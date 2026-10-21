#!/usr/bin/env python3
"""Validate community contributions as inert data.

In pull_request_target this file is loaded from the trusted base commit. It never checks out, imports, or executes
the pull request head. Proposed files are downloaded through the GitHub API and parsed in memory.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

MAX_FILES = 20
MAX_TOTAL = 256 * 1024
MAX_FILE = 64 * 1024
ALLOWED_TYPES = {"error-fix", "modeling-pitfall", "api-usage", "convergence", "parameter",
                 "result-interpretation", "workflow"}
PRIVATE = [
    ("email", re.compile(rb"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")),
    ("IPv4", re.compile(rb"(?<![\d.])(?:25[0-5]|2[0-4]\d|1?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|1?\d?\d)){3}(?![\d.])")),
    ("Windows path", re.compile(rb"(?i)(?<![A-Z0-9_])[A-Z]:[\\/][^\s<>\"|]+")),
    ("UNC path", re.compile(rb"\\\\[^\\\s]+\\[^\s<>\"|]+")),
    ("home path", re.compile(rb"(?i)/(?:home|users|mnt|work|tmp|var/tmp)/[^\s<>\"']+")),
    ("private key", re.compile(rb"-----BEGIN (?:OPENSSH |RSA |EC )?PRIVATE KEY-----")),
    ("credential", re.compile(rb"(?i)\b(?:api[_-]?key|access[_-]?token|bridge[_-]?token|password)\s*[:=]\s*[^\s<]{8,}")),
]
PROMPT_INJECTION = re.compile(
    r"(?i)(ignore (?:all |the )?(?:previous|prior) instructions|system prompt|developer message|"
    r"you are (?:chatgpt|an ai|the assistant)|tool[_ -]?call|<\|(?:system|assistant|user)\|>)"
)
EXECUTABLE_FENCE = re.compile(r"```\s*(?:python|py|bash|sh|powershell|ps1|cmd|bat|javascript|js|ruby|perl)\b", re.I)
ID = re.compile(r"^[a-z0-9][a-z0-9-]{2,79}$")


class Rejected(ValueError):
    pass


def request_json(url: str, token: str, method: str = "GET", body: dict | None = None):
    data = json.dumps(body).encode() if body is not None else None
    request = urllib.request.Request(url, data=data, method=method, headers={
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "diana-mcp-community-validator",
        **({"Content-Type": "application/json"} if data else {}),
    })
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:1000]
        raise Rejected(f"GitHub API {exc.code}: {detail}") from exc


def parse_front_matter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise Rejected("candidate must start with YAML front matter")
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration as exc:
        raise Rejected("candidate has no closing front-matter fence") from exc
    fields: dict[str, str] = {}
    for line in lines[1:end]:
        if not line or line[:1].isspace() or line.lstrip().startswith("#"):
            continue
        match = re.match(r"^([A-Za-z_][\w-]*):(?:\s*(.*))?$", line)
        if not match:
            raise Rejected(f"invalid front-matter line: {line[:120]}")
        key, value = match.group(1), (match.group(2) or "").strip()
        if key in fields:
            raise Rejected(f"duplicate front-matter field: {key}")
        if value.startswith('"'):
            try:
                value = str(json.loads(value))
            except ValueError as exc:
                raise Rejected(f"invalid quoted value for {key}") from exc
        fields[key] = value
    return fields


def privacy_scan(data: bytes) -> None:
    for label, pattern in PRIVATE:
        if pattern.search(data):
            raise Rejected(f"privacy scan found {label}; use a neutral placeholder")
    text = data.decode("utf-8", "strict")
    if PROMPT_INJECTION.search(text):
        raise Rejected("content resembles prompt injection")


def validate_candidate(path: str, data: bytes) -> None:
    privacy_scan(data)
    text = data.decode("utf-8")
    if EXECUTABLE_FENCE.search(text) or re.search(r"(?m)^##\s+验证脚本\s*$", text):
        raise Rejected("executable verification scripts are not accepted in community candidates")
    fields = parse_front_matter(text)
    required = {
        "status": "draft", "community_status": "candidate", "license": "Apache-2.0",
        "requires_human_review": "true",
    }
    for key, expected in required.items():
        if fields.get(key) != expected:
            raise Rejected(f"{key} must be {expected!r}")
    entry_id = fields.get("id", "")
    if not ID.fullmatch(entry_id) or Path(path).stem != entry_id:
        raise Rejected("id must be a safe slug and match the file name")
    if fields.get("type") not in ALLOWED_TYPES:
        raise Rejected("unknown experience type")
    if not 3 <= len(fields.get("title", "")) <= 200:
        raise Rejected("title must contain 3-200 characters")
    try:
        confidence = float(fields.get("confidence", "0"))
    except ValueError as exc:
        raise Rejected("confidence must be numeric") from exc
    if not 0 <= confidence <= 0.2:
        raise Rejected("a candidate may not claim confidence above 0.2")
    if fields.get("evidence") not in ("", "[]"):
        raise Rejected("private evidence does not belong in a candidate; describe public reproduction separately")
    for heading in ("现象", "原因", "解决", "验证"):
        if not re.search(rf"(?m)^##\s+{heading}\s*$", text):
            raise Rejected(f"missing section: {heading}")


def validate_confirmation(path: str, data: bytes, author: str, candidate_ids: set[str]) -> None:
    privacy_scan(data)
    try:
        item = json.loads(data)
    except ValueError as exc:
        raise Rejected("confirmation must be valid JSON") from exc
    keys = {"format", "entry_id", "outcome", "date", "diana_version", "environment_fingerprint",
            "evidence_summary", "contributor"}
    if set(item) != keys:
        raise Rejected(f"confirmation keys must be exactly {sorted(keys)}")
    if item["format"] != 1 or item["outcome"] not in ("success", "failure"):
        raise Rejected("invalid confirmation format or outcome")
    if not re.fullmatch(r"20\d\d-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01])", str(item["date"])):
        raise Rejected("date must use YYYY-MM-DD")
    if item["contributor"].lower() != author.lower():
        raise Rejected("confirmation contributor must equal the pull-request author")
    if item["entry_id"] not in candidate_ids:
        raise Rejected("confirmation references an unknown entry")
    if not re.fullmatch(r"sha256:[a-f0-9]{16,64}", str(item["environment_fingerprint"])):
        raise Rejected("environment_fingerprint must be an irreversible sha256 prefix")
    if not 1 <= len(str(item["diana_version"])) <= 40:
        raise Rejected("invalid diana_version")
    if not 10 <= len(str(item["evidence_summary"])) <= 2000:
        raise Rejected("evidence_summary must contain 10-2000 characters")
    if not Path(path).stem.startswith(item["entry_id"] + "-"):
        raise Rejected("confirmation file name must start with <entry_id>-")


def existing_candidates(repository: str, ref: str, token: str) -> set[str]:
    query = urllib.parse.quote("experiences/candidate", safe="/")
    try:
        items = request_json(f"https://api.github.com/repos/{repository}/contents/{query}?ref={ref}", token)
    except Rejected:
        return set()
    return {Path(item["name"]).stem for item in items if item.get("type") == "file" and item["name"].endswith(".md")}


def pull_request_files(repository: str, number: int, token: str) -> tuple[dict, list[tuple[str, bytes]]]:
    api = f"https://api.github.com/repos/{repository}"
    pr = request_json(f"{api}/pulls/{number}", token)
    changed = request_json(f"{api}/pulls/{number}/files?per_page=100", token)
    if not 1 <= len(changed) <= MAX_FILES:
        raise Rejected(f"a contribution must change 1-{MAX_FILES} files")
    total = sum(int(item.get("changes", 0)) for item in changed)
    if total > 10000:
        raise Rejected("pull request is too large")
    files = []
    total_bytes = 0
    for item in changed:
        path = item["filename"]
        if item["status"] not in ("added",):
            raise Rejected(f"only new files are accepted automatically: {path}")
        allowed = (re.fullmatch(r"experiences/candidate/[a-z0-9][a-z0-9-]{2,79}\.md", path) or
                   re.fullmatch(r"confirmations/[a-z0-9][a-z0-9-]{2,159}\.json", path))
        if not allowed:
            raise Rejected(f"path is outside the data-only allowlist: {path}")
        encoded = urllib.parse.quote(path, safe="/")
        content = request_json(f"{api}/contents/{encoded}?ref={pr['head']['sha']}", token)
        if content.get("type") != "file" or content.get("encoding") != "base64":
            raise Rejected(f"not a regular base64 file: {path}")
        data = base64.b64decode(content["content"], validate=True)
        if len(data) > MAX_FILE:
            raise Rejected(f"file exceeds {MAX_FILE} bytes: {path}")
        total_bytes += len(data)
        files.append((path, data))
    if total_bytes > MAX_TOTAL:
        raise Rejected(f"contribution exceeds {MAX_TOTAL} bytes")
    commits = request_json(f"{api}/pulls/{number}/commits?per_page=100", token)
    for commit in commits:
        message = commit["commit"]["message"]
        if not re.search(r"(?im)^Signed-off-by:\s+.+\s+<[^<>]+>$", message):
            raise Rejected(f"commit {commit['sha'][:8]} lacks a Signed-off-by line")
    return pr, files


def validate_pull_request(repository: str, number: int, token: str, merge: bool) -> dict:
    pr, files = pull_request_files(repository, number, token)
    author = pr["user"]["login"]
    candidates = existing_candidates(repository, pr["base"]["sha"], token)
    candidates.update(Path(path).stem for path, _ in files if path.startswith("experiences/candidate/"))
    for path, data in files:
        if path.startswith("experiences/candidate/"):
            validate_candidate(path, data)
        else:
            validate_confirmation(path, data, author, candidates)
    result = {"accepted_as_data": True, "files": len(files), "bytes": sum(len(d) for _, d in files),
              "head": pr["head"]["sha"], "merged": False}
    if merge:
        merged = request_json(f"https://api.github.com/repos/{repository}/pulls/{number}/merge", token, "PUT", {
            "sha": pr["head"]["sha"], "merge_method": "squash",
            "commit_title": f"knowledge: accept data-only contribution #{number}",
        })
        if not merged.get("merged"):
            raise Rejected(f"validated but GitHub did not merge: {merged.get('message')}")
        result["merged"] = True
    return result


def validate_local(root: Path) -> dict:
    files = sorted((root / "experiences" / "candidate").glob("*.md"))
    for path in files:
        validate_candidate(path.relative_to(root).as_posix(), path.read_bytes())
    candidate_ids = {p.stem for p in files}
    confirmations = sorted((root / "confirmations").glob("*.json"))
    for path in confirmations:
        item = json.loads(path.read_text(encoding="utf-8"))
        validate_confirmation(path.relative_to(root).as_posix(), path.read_bytes(), item.get("contributor", ""),
                              candidate_ids)
    return {"accepted_as_data": True, "candidates": len(files), "confirmations": len(confirmations)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pull-request", type=int)
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY"))
    parser.add_argument("--token", default=os.environ.get("GITHUB_TOKEN"))
    parser.add_argument("--merge", action="store_true")
    parser.add_argument("--local-root", type=Path)
    args = parser.parse_args()
    try:
        if args.local_root:
            report = validate_local(args.local_root)
        else:
            if not args.pull_request or not args.repository or not args.token:
                raise Rejected("pull-request mode requires --pull-request, --repository and a token")
            report = validate_pull_request(args.repository, args.pull_request, args.token, args.merge)
    except (Rejected, UnicodeDecodeError, ValueError) as exc:
        print(f"REJECTED: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
