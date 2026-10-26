import json, os, subprocess, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import memory_lite_mcp as L

class T(unittest.TestCase):
    def test_store(self):
        s = L.LiteStore(":memory:")
        m = s.remember("Stack is FastAPI and Postgres", ["stack"])
        self.assertEqual(s.recall("postgres")[0]["id"], m["id"])
        self.assertEqual(s.recall("nothinghere"), [])
        self.assertTrue(s.forget(m["id"])); self.assertFalse(s.forget(m["id"]))
    def test_protocol_subprocess(self):
        env = dict(os.environ, MEMORY_LITE_DB=":memory:", PYTHONPATH=str(ROOT / "src"))
        msgs = [{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"t","version":"1"}}},
                {"jsonrpc":"2.0","method":"notifications/initialized"},
                {"jsonrpc":"2.0","id":2,"method":"tools/list"},
                {"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"remember","arguments":{"content":"likes tea"}}},
                {"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"recall","arguments":{"query":"tea"}}},
                {"jsonrpc":"2.0","id":5,"method":"bogus"}]
        p = subprocess.run([sys.executable, "-m", "memory_lite_mcp"], input="\n".join(json.dumps(m) for m in msgs)+"\n",
                           capture_output=True, text=True, env=env, timeout=20)
        out = [json.loads(l) for l in p.stdout.splitlines()]
        self.assertEqual([o["id"] for o in out], [1,2,3,4,5])
        self.assertEqual({t["name"] for t in out[1]["result"]["tools"]}, {"remember","recall","forget"})
        self.assertIn("likes tea", out[3]["result"]["content"][0]["text"])
        self.assertEqual(out[4]["error"]["code"], -32601)

if __name__ == "__main__":
    unittest.main()
