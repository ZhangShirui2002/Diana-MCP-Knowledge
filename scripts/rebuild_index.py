#!/usr/bin/env python3
"""Build effective community trust from immutable candidate data and independent confirmations."""
from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def field(text: str, name: str, default: str = "") -> str:
    match = re.search(rf"(?m)^{re.escape(name)}:\s*(.*?)\s*$", text)
    if not match:
        return default
    value = match.group(1).strip()
    if value.startswith('"'):
        try:
            return str(json.loads(value))
        except ValueError:
            return default
    return value


def main() -> int:
    entries = {}
    for path in sorted((ROOT / "experiences").glob("*/*.md")):
        text = path.read_text(encoding="utf-8")
        entry_id = field(text, "id")
        if entry_id:
            entries[entry_id] = {"declared_status": field(text, "community_status", path.parent.name)}
    reports = defaultdict(list)
    for path in sorted((ROOT / "confirmations").glob("*.json")):
        try:
            item = json.loads(path.read_text(encoding="utf-8"))
        except ValueError:
            continue
        if item.get("entry_id") in entries and item.get("outcome") in ("success", "failure"):
            reports[item["entry_id"]].append(item)
    index = {}
    for entry_id, base in sorted(entries.items()):
        items = reports[entry_id]
        unique = {}
        for item in items:
            key = (str(item.get("contributor", "")).lower(), item.get("environment_fingerprint"))
            unique[key] = item  # latest deterministic file order wins for the same contributor/environment
        successes = [item for item in unique.values() if item["outcome"] == "success"]
        failures = [item for item in unique.values() if item["outcome"] == "failure"]
        declared = base["declared_status"]
        if declared in ("obsolete", "reproducibly-verified"):
            effective = declared
        elif successes and failures:
            effective = "disputed"
        elif len(failures) >= 2:
            effective = "disputed"
        elif len(successes) >= 3 and len({i["contributor"].lower() for i in successes}) >= 3 and not failures:
            effective = "community-confirmed"
        else:
            effective = "candidate"
        confidence = 0.10 + min(len(successes), 4) * 0.18 - min(len(failures), 3) * 0.22
        if effective == "community-confirmed":
            confidence = max(confidence, 0.70)
        elif effective == "reproducibly-verified":
            confidence = max(confidence, 0.90)
        elif effective == "disputed":
            confidence = min(confidence, 0.20)
        dates = [str(item.get("date", "")) for item in unique.values() if item.get("date")]
        index[entry_id] = {
            "effective_status": effective,
            "confidence": round(max(0.0, min(1.0, confidence)), 2),
            "successful_confirmations": len(successes),
            "failed_confirmations": len(failures),
            "last_confirmed": max(dates) if dates else None,
        }
    output = {"format": 1, "generated_at": datetime.now(timezone.utc).isoformat(), "entries": index}
    (ROOT / "index.json").write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"indexed {len(index)} entries and {sum(len(v) for v in reports.values())} confirmations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
