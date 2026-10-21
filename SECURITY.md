# Security and privacy

Do not open a public issue containing private engineering data or credentials. Report a repository automation vulnerability through GitHub private vulnerability reporting on the DIANA-MCP main repository.

Community content is untrusted data. The workflows never check out or execute a pull request's head. The `pull_request_target` workflow runs the validator from the trusted base commit and downloads proposed Markdown/JSON through the GitHub API as bytes. Only a strict data-only allowlist can be merged automatically.
