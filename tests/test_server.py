"""Integration checks against the loopback HTTP application and a temporary SQLite file."""
import http.client
import json
import sqlite3
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from server import create_server


class HouseholdAPI(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.database = Path(self.temp.name) / "relay.db"
        self.start()
        self.addCleanup(self.stop)
        self.state, self.cookie = self.new_household()

    def start(self, port=0):
        self.server = create_server(self.database, port=port)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def stop(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def request(self, method, path, cookie="", data=None, headers=None):
        conn = http.client.HTTPConnection(*self.server.server_address, timeout=5)
        try:
            headers = {"Cookie": cookie, "Content-Type": "application/json", **(headers or {})}
            body = json.dumps(data) if data is not None else None
            conn.request(method, path, body, headers)
            response = conn.getresponse()
            raw = response.read()
            value = json.loads(raw) if response.getheader("Content-Type", "").startswith("application/json") else raw
            return response.status, value, dict(response.getheaders())
        finally:
            conn.close()

    def new_household(self):
        status, state, headers = self.request("GET", "/api/state")
        self.assertEqual(status, 200)
        self.assertIn("HttpOnly", headers["Set-Cookie"])
        self.assertIn("SameSite=Strict", headers["Set-Cookie"])
        return state, headers["Set-Cookie"].split(";")[0]

    def post(self, path, payload, status=200, **kwargs):
        got, state, _ = self.request("POST", "/api/" + path, self.cookie, payload, **kwargs)
        self.assertEqual(got, status, state)
        return state

    def test_intake_review_history_export_restart_delete(self):
        original = "  Library books due on Friday.\nKeep this exact wording.  "
        state = self.post("intake", {"text": original, "title": "Library books"})
        draft = state["sources"][0]
        self.assertEqual(draft["text"], original)
        self.assertEqual(draft["date"], "")
        self.assertEqual(state["plans"], self.state["plans"])
        self.post("review", {"id": draft["id"], "decision": "reject"})
        change = next(s for s in self.state["sources"] if s["status"] == "pending")
        old = next(p for p in self.state["plans"] if p["id"] == change["target"])
        payload = {**{k: change[k] for k in ("id", "date", "time", "title", "person", "target")},
                   "decision": "approve", "expectedSourceId": old["sourceId"]}
        current = self.post("review", payload)
        revised = next(p for p in current["plans"] if p["id"] == old["id"])
        self.assertEqual(revised["sourceId"], change["id"])
        self.assertEqual(revised["history"][0]["sourceId"], old["sourceId"])
        self.assertEqual(revised["history"][0]["time"], old["time"])
        self.post("review", payload, 409)
        port = self.server.server_port
        self.stop()
        self.start(port)
        self.assertEqual(self.request("GET", "/api/export", self.cookie)[1], current)
        emptied = self.post("reset", {})
        self.assertEqual((emptied["sources"], emptied["plans"]), ([], []))
        self.assertEqual(self.request("GET", "/api/state", self.cookie)[1], emptied)

    def test_cross_household_and_validation(self):
        other, _ = self.new_household()
        own = self.state["sources"][0]
        foreign = other["sources"][0]
        self.post("review", {"id": foreign["id"], "decision": "reject"}, 404)
        base = {"id": own["id"], "decision": "approve", "title": "Pickup"}
        self.post("review", {**base, "target": other["plans"][0]["id"]}, 404)
        self.post("review", {**base, "date": "2026-02-30"}, 400)
        self.post("review", {**base, "person": "Stranger"}, 400)
        self.post("review", {**base, "time": "26:60"}, 400)
        self.post("review", {**base, "expectedSourceId": "stale"}, 409)
        self.post("intake", {"text": "  "}, 400)
        self.post("reset", {}, 403, headers={"Origin": "http://example.org"})
        self.assertEqual(self.request("POST", "/api/reset", data={})[0], 401)
        self.assertEqual(self.request("GET", "/api/state", self.cookie, headers={"Host": "example.org"})[0], 403)
        self.assertEqual(self.request("GET", "/master-handoff.md")[0], 404)
        self.assertEqual(self.request("GET", "/api/state", self.cookie)[1], self.state)

    def test_concurrent_approval_only_creates_one_version(self):
        state = self.post("intake", {"text": "Meet at the office.", "title": "Office"})
        review = {"decision": "approve", "id": state["sources"][0]["id"]}
        with ThreadPoolExecutor(max_workers=2) as pool:
            statuses = list(pool.map(lambda _: self.request("POST", "/api/review", self.cookie, review)[0], range(2)))
        self.assertEqual(sorted(statuses), [200, 409])
        self.assertEqual(len(self.request("GET", "/api/state", self.cookie)[1]["plans"]), len(self.state["plans"]) + 1)

    def test_intake_only_extracts_explicit_iso_fields(self):
        state = self.post("intake", {
            "title": "Museum visit",
            "text": "Date: 2026-12-04\nTime: 16:15\nFor: Sam\nBring a packed lunch.",
        })
        source = state["sources"][0]
        self.assertEqual((source["date"], source["time"], source["person"]), ("2026-12-04", "16:15", "Sam"))
        state = self.post("intake", {"title": "Ambiguous", "text": "Meet Friday at 4."})
        source = state["sources"][0]
        self.assertEqual((source["date"], source["time"], source["person"]), ("", "", ""))

    def test_follow_through_actions_are_scoped_persistent_and_toggleable(self):
        plan = self.state["plans"][0]
        state = self.post("tasks", {"action": "create", "title": "Pack shin guards", "plan": plan["id"], "person": "Alex"})
        task = state["tasks"][0]
        self.assertEqual((task["title"], task["plan"], task["person"], task["status"]),
                         ("Pack shin guards", plan["id"], "Alex", "open"))
        state = self.post("tasks", {"action": "toggle", "id": task["id"]})
        self.assertEqual(state["tasks"][0]["status"], "done")
        self.assertEqual(self.request("GET", "/api/export", self.cookie)[1]["tasks"][0]["status"], "done")
        other, other_cookie = self.new_household()
        self.assertEqual(self.request("POST", "/api/tasks", other_cookie, {"action": "toggle", "id": task["id"]})[0], 404)
        self.post("tasks", {"action": "create", "title": "x", "plan": other["plans"][0]["id"]}, 404)
        self.post("tasks", {"action": "create", "title": "x", "person": "Stranger"}, 400)

    def test_database_migration_ledger_and_health_endpoint(self):
        status, body, _ = self.request("GET", "/api/health")
        self.assertEqual((status, body["status"], body["schemaVersion"]), (200, "ok", 1))
        db = sqlite3.connect(self.database)
        try:
            self.assertEqual(db.execute("SELECT version FROM schema_migrations").fetchall(), [(1,)])
        finally:
            db.close()

