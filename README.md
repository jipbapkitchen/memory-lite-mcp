# Memory Lite — free local memory for Claude & Cursor (MCP)

<!-- mcp-name: io.github.jipbapkitchen/memory-lite -->

A tiny **Model Context Protocol** server that gives your AI assistant a memory that lives
**only on your computer** (one SQLite file). No cloud, no API keys, **zero dependencies**
(Python 3.9+ standard library). MIT licensed. Made by **Jipbap Kitchen**.

| Tool | What it does |
|---|---|
| `remember` | save a fact / preference / decision (optional tags) |
| `recall` | keyword match (any word), newest first, max 10 results |
| `forget` | delete a memory by id |

Data file: `~/.memory-lite/memory.db` (override with `MEMORY_LITE_DB`).

## Install

With [uv](https://docs.astral.sh/uv/) (recommended): nothing to install, the client runs `uvx memory-lite-mcp`.
Or: `pip install memory-lite-mcp`, or clone this repo and run `python -m memory_lite_mcp` with `PYTHONPATH=src`.

Check it works: `uvx memory-lite-mcp doctor`

### Claude Desktop
Edit `claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{ "mcpServers": { "memory-lite": { "command": "uvx", "args": ["memory-lite-mcp"] } } }
```
Fully quit and reopen Claude Desktop.

### Cursor
`~/.cursor/mcp.json` (all projects) or `.cursor/mcp.json` (one project) — same JSON as above.

### Claude Code
`claude mcp add memory-lite -- uvx memory-lite-mcp`

## Lite vs. full edition

| | Memory Lite (free, MIT) | **AI Memory Bible** (paid) |
|---|---|---|
| remember / recall / forget | ✅ | ✅ |
| Search | keyword match, newest first, max 10 | **SQLite FTS5 BM25 ranking** + highlighted snippets |
| Projects & tag filters | – | ✅ |
| update, list, briefing (session-start summary) | – | ✅ |
| JSON export / import (backup, move PCs) | – | ✅ |
| One-command installers (Windows / macOS / Linux) + auto config with backup | – | ✅ |
| `doctor` self-check + illustrated PDF setup guide & FAQ | basic doctor | ✅ |

**Get the full edition:** https://bamsuni.com/ai-shop/en/ &nbsp;·&nbsp; Payhip: https://payhip.com/b/Jl3Tm

## Privacy
Everything stays in a local SQLite file. The server makes no network requests. Don't store passwords or API keys.

## License
MIT © 2026 Jipbap Kitchen
