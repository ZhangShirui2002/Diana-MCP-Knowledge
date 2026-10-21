# Contributing data safely

Contributions must be reusable engineering knowledge that you are entitled to publish. Never submit client names, project identifiers, model geometry, proprietary material data, loads, measurements, screenshots, original `.dat/.dcf/.out/.tb/.dnb/.ff/.dpf` files, DIANA manual text, credentials, license-server details, private paths, IP addresses, emails, or host/user names.

The preferred route is DIANA-MCP's local redact → preview → contribute workflow. It creates only `candidate` entries and requires an exact human confirmation immediately before upload.

Automated acceptance is deliberately narrow:

- candidate additions: `experiences/candidate/<id>.md`;
- reproduction reports: `confirmations/<entry-id>-<unique-id>.json`;
- no deletion, rename, symlink, binary, workflow, script, fixture, or executable change;
- at most 20 files and 256 KiB total per pull request;
- no executable code fences or `验证脚本` section;
- every commit has a `Signed-off-by:` line (Developer Certificate of Origin).

Use `git commit -s` to add the sign-off. Passing automation means only that the data shape and safety checks passed. It is not an endorsement of technical correctness.

Confirmation JSON follows [schema/confirmation.schema.json](schema/confirmation.schema.json). `contributor` must equal the pull-request author's GitHub login. Environment fingerprints should be stable hashes, not host names or paths.
