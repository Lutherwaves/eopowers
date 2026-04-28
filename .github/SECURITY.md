# Security policy

## Supported versions

eopowers is a Claude Code plugin distributed from `main`. Only the latest commit on `main` is supported.

## Reporting a vulnerability

Please **do not** open public issues for security problems.

Report privately via GitHub's [Private vulnerability reporting](https://github.com/Lutherwaves/eopowers/security/advisories/new), or email **martin@yankovs.com**.

Include:
- A description of the issue and its impact
- Steps to reproduce (sample order ID, command sequence, or PoC)
- Affected version / commit

You should receive an acknowledgment within **5 business days**. We aim to ship a fix or mitigation within **30 days** for confirmed issues, faster for anything that exposes client procurement data.

## Scope

In scope:
- Code execution, path traversal, or arbitrary write through any `/eop-*` skill
- Leakage of client data (pricing, фирмени данни) outside the workspace
- Supply-chain issues in skills, hooks, or agent prompts (prompt injection that escalates privileges)

Out of scope:
- Social engineering of plugin users
- Issues in eop.bg itself — report those to the platform operators
- Bugs in third-party MCP servers
