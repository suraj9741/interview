# AWS notes

Notes written while studying for the **AWS Certified Solutions Architect – Associate (SAA-C03)** exam, kept interview-ready. One file per course section; each starts with a diagram and ends with a from-memory drill and a 30-second spoken answer.

| # | Note | Covers |
|---|---|---|
| 01 | [IAM cheat sheet](01-iam-cheat-sheet.md) | Users, groups, policies (JSON, identity vs resource-based, inline vs managed, explicit deny), MFA, password policy, access keys, CLI on Ubuntu, CloudShell, roles and STS, credential report, access advisor, shared responsibility, best practices, 29 exam traps |

Diagrams live in [diagrams/](diagrams/) as `.drawio.svg` (open them in draw.io to edit). They are generated once by `python3 tools/diagrams_aws.py`; existing files are skipped unless you pass `--force`.
