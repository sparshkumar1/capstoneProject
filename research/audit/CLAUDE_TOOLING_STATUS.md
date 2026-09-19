# Claude Code Tooling Status (audit session, 2026-09-19)

## Serena
- **Root cause:** the Serena MCP process was launched without `~/.local/bin` on `PATH`, so its Python language server (started through `uv`/`uvx`) could not be found.
- **Change made (user-level only):** local-scope MCP registration for `serena` re-created with `PATH=C:\Users\spars\.local\bin;<existing PATH>` in its `env`. Command is still the full path to `serena.exe start-mcp-server --context claude-code --project <repo>`; backend remains LSP. Backup of `~/.claude.json` saved as `~/.claude.json.bak-pre-serena-path-fix`. (A first `claude mcp add-json` attempt failed on shell quoting after the old entry was removed; the entry was re-added with `claude mcp add -e PATH=...` within the same session.)
- **Evidence the fix works:** a fresh `serena project health-check` with that PATH started Pyright 1.1.403 in ~5 s and passed symbols-overview, find-symbol and find-references.
- **Live-session status:** the MCP process attached to this audit session was still the pre-fix process (log `mcp_20260919-183938_21036.txt`); `get_symbols_overview` on `rl/guardrails.py` **still failed inside this session**. Audit inspection therefore used Read/Grep/Bash instead of Serena. A restart of the session/MCP server is required for the live call to succeed.

## Other tools
| Tool | Status | Evidence |
|---|---|---|
| Context7 | OK | `/dlr-rm/stable-baselines3` resolved and queried (BaseCallback docs) |
| Zotero MCP | OK, read-only | connected; library has 1 item; no writes attempted; no writes authorised |
| Superpowers | OK | v6.3.0 enabled (not needed for this audit) |
| claude-md-management | OK | v1.0.0 enabled; not run (CLAUDE.md is stale but was not edited) |
| W&B / Stable-Baselines3 | OK | wandb 0.30.0, stable-baselines3 2.7.1, gymnasium 0.29.1 import; login state not checked; not used |

## Project artifacts
- No repository source, `research/` frozen artifact, human data, benchmark, checkpoint or database was modified.
- Only additions in the repository: the five `research/audit/CLAUDE_*` files created by this audit.
- Read-only side effects outside the repo: audit replay scripts and outputs in the session scratchpad; a Serena health-check log inside the already-untracked `.serena/` folder.
- Note: the audit replayed Paper 3 *evaluation* (no training) from frozen checkpoints in the scratchpad to verify reported numbers; env logging was redirected to the scratchpad and `git status` was identical before and after.
