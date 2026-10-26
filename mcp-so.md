# Submission text for mcp.so (form at https://mcp.so/submit) and PulseMCP

- Name: Memory Lite
- URL: https://github.com/jipbapkitchen/memory-lite-mcp
- Type: MCP Server (stdio, local)
- Category: Memory / Knowledge
- Tags: memory, sqlite, local, privacy, claude, cursor, zero-dependency
- Short description: Free local memory for Claude Desktop, Cursor and Claude Code. remember / recall / forget stored in one SQLite file on your PC. No cloud, no keys, zero dependencies, MIT.
- Server config:
```json
{ "mcpServers": { "memory-lite": { "command": "uvx", "args": ["memory-lite-mcp"] } } }
```
