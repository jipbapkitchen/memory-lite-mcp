"""Memory Lite - a tiny, free, local memory MCP server (MIT). By Jipbap Kitchen.

Tools: remember, recall, forget. Storage: one SQLite file on your own computer.
Zero third-party dependencies (Python 3.9+ standard library only).
Need projects, tags filters, ranked full-text search, briefing, update, export/import
and one-command installers? See AI Memory Bible: https://bamsuni.com/ai-shop/en/
"""
import json, os, sqlite3, sys, time
from pathlib import Path

__version__ = "1.0.0"
UPGRADE_URL = "https://bamsuni.com/ai-shop/en/"
PROTOCOLS = ["2025-06-18", "2025-03-26", "2024-11-05"]
MAX_RESULTS = 10

def db_path():
    return Path(os.environ.get("MEMORY_LITE_DB") or (Path.home() / ".memory-lite" / "memory.db")).expanduser()

class LiteStore:
    def __init__(self, path=None):
        p = str(path or db_path())
        if p != ":memory:":
            Path(p).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(p)
        self.db.execute("CREATE TABLE IF NOT EXISTS memories(id INTEGER PRIMARY KEY AUTOINCREMENT, "
                        "content TEXT NOT NULL, tags TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL)")
        self.db.commit()

    def remember(self, content, tags=None):
        content = (content or "").strip()
        if not content:
            raise ValueError("content must not be empty")
        if isinstance(tags, str):
            tags = tags.split(",")
        tags = ",".join(t.strip().lower() for t in (tags or []) if t.strip())
        cur = self.db.execute("INSERT INTO memories(content,tags,created_at) VALUES(?,?,?)",
                              (content, tags, time.strftime("%Y-%m-%dT%H:%M:%S%z")))
        self.db.commit()
        return {"id": cur.lastrowid, "content": content, "tags": [t for t in tags.split(",") if t]}

    def recall(self, query=""):
        """Simple keyword match (any word, case-insensitive), newest first, max 10. No ranking."""
        words = [w for w in str(query).lower().split() if len(w) > 1][:8]
        sql, args = "SELECT id,content,tags,created_at FROM memories", []
        if words:
            sql += " WHERE " + " OR ".join(["lower(content||' '||tags) LIKE ?"] * len(words))
            args = [f"%{w}%" for w in words]
        sql += " ORDER BY id DESC LIMIT ?"
        rows = self.db.execute(sql, args + [MAX_RESULTS]).fetchall()
        return [{"id": r[0], "content": r[1], "tags": [t for t in r[2].split(",") if t], "created_at": r[3]} for r in rows]

    def forget(self, mid):
        n = self.db.execute("DELETE FROM memories WHERE id=?", (int(mid),)).rowcount
        self.db.commit()
        return n > 0

TOOLS = [
    {"name": "remember", "description": "Save a fact, preference or decision to local memory.",
     "inputSchema": {"type": "object", "properties": {"content": {"type": "string"},
                     "tags": {"type": "array", "items": {"type": "string"}}}, "required": ["content"]},
     "annotations": {"readOnlyHint": False, "destructiveHint": False, "openWorldHint": False}},
    {"name": "recall", "description": "Find saved memories containing any of the given keywords (newest first, max 10). Use before saying you don't know something about the user.",
     "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": []},
     "annotations": {"readOnlyHint": True, "openWorldHint": False}},
    {"name": "forget", "description": "Delete a memory by id.",
     "inputSchema": {"type": "object", "properties": {"id": {"type": "integer"}}, "required": ["id"]},
     "annotations": {"readOnlyHint": False, "destructiveHint": True, "openWorldHint": False}},
]

def handle(store, msg):
    if not isinstance(msg, dict) or "method" not in msg:
        return None
    mid, method, params = msg.get("id"), msg["method"], msg.get("params") or {}
    note = "id" not in msg
    def ok(result):
        return None if note else {"jsonrpc": "2.0", "id": mid, "result": result}
    if method == "initialize":
        v = params.get("protocolVersion")
        return ok({"protocolVersion": v if v in PROTOCOLS else PROTOCOLS[0],
                   "capabilities": {"tools": {"listChanged": False}},
                   "serverInfo": {"name": "memory-lite", "version": __version__},
                   "instructions": "Local memory on the user's computer. Call recall before saying you don't know something about the user; call remember for durable facts. Never store secrets."})
    if method == "ping":
        return ok({})
    if method == "tools/list":
        return ok({"tools": TOOLS})
    if method == "tools/call":
        name, a = params.get("name"), params.get("arguments") or {}
        try:
            if name == "remember":
                out = {"saved": store.remember(a.get("content"), a.get("tags"))}
            elif name == "recall":
                res = store.recall(a.get("query", ""))
                out = {"count": len(res), "memories": res}
            elif name == "forget":
                if not store.forget(a.get("id")):
                    raise ValueError(f"memory {a.get('id')} not found")
                out = {"deleted": int(a["id"])}
            else:
                return None if note else {"jsonrpc": "2.0", "id": mid, "error": {"code": -32602, "message": f"Unknown tool: {name}"}}
            return ok({"content": [{"type": "text", "text": json.dumps(out, ensure_ascii=False, indent=2)}], "isError": False})
        except (ValueError, TypeError, KeyError) as e:
            return ok({"content": [{"type": "text", "text": f"Error: {e}"}], "isError": True})
    if note:
        return None
    return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": f"Method not found: {method}"}}

def serve(store=None):
    store = store or LiteStore()
    try:
        sys.stdin.reconfigure(encoding="utf-8"); sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            resp = handle(store, json.loads(line))
        except json.JSONDecodeError:
            resp = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}}
        if resp is not None:
            sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n"); sys.stdout.flush()

def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    cmd = argv[0] if argv else "serve"
    if cmd in ("-h", "--help", "help"):
        print("memory-lite-mcp [serve|doctor|version]\nFree MIT edition. Full edition: " + UPGRADE_URL); return 0
    if cmd == "version":
        print(f"memory-lite-mcp {__version__} (MIT, Jipbap Kitchen). Full edition: {UPGRADE_URL}"); return 0
    if cmd == "doctor":
        s = LiteStore(); s.remember("doctor check"); r = s.recall("doctor"); s.forget(r[0]["id"])
        print(f"[ok] Python {sys.version.split()[0]}, SQLite {sqlite3.sqlite_version}, DB {db_path()}")
        print(json.dumps({"mcpServers": {"memory-lite": {"command": "uvx", "args": ["memory-lite-mcp"]}}}, indent=2))
        print("Want projects, ranked full-text search, briefing, export/import and installers? " + UPGRADE_URL)
        return 0
    serve(); return 0

if __name__ == "__main__":
    raise SystemExit(main())
