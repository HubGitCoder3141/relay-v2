"""Integration checks against the loopback HTTP application and a temporary SQLite file."""
import http.client
import json
import sqlite3
import tempfile
import threading
import unittest
from contextlib import closing
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
        self.server = create_server(self.database, port=port, demo=True)
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

    def test_conflicting_labels_are_left_open_with_source_evidence(self):
        state = self.post("intake", {"text": "Date: 2026-12-04\nDate: 2026-12-05\nTime: 16:15\nFor: Sam and Alex"})
        source = state["sources"][0]
        self.assertEqual((source["date"], source["time"], source["person"]), ("", "", ""))
        self.assertEqual(source["extraction"]["date"], {
            "status": "conflicting",
            "evidence": [{"line": 1, "value": "2026-12-04"}, {"line": 2, "value": "2026-12-05"}],
        })
        self.assertEqual(source["extraction"]["person"]["status"], "invalid")

    def test_preparation_and_instructions_follow_approved_versions(self):
        old = self.state["plans"][0]
        draft = self.post("intake", {"text": "Bring: Cleats\nInstructions: Use the east gate"})["sources"][0]
        self.assertEqual(draft["preparation"], "Cleats")
        self.assertEqual(draft["instructions"], "Use the east gate")
        payload = {"id": draft["id"], "decision": "approve", "target": old["id"]}
        self.post("review", payload, 409)
        state = self.post("review", {**payload, "expectedSourceId": old["sourceId"], "preparation": "Cleats and water"})
        plan = next(plan for plan in state["plans"] if plan["id"] == old["id"])
        self.assertEqual((plan["preparation"], plan["instructions"]), ("Cleats and water", "Use the east gate"))
        self.assertEqual(plan["history"][0]["preparation"], "")
        self.assertEqual(state["sources"][0]["extraction"]["preparation"]["evidence"][0]["value"], "Cleats")

    def test_default_workspace_starts_without_sample_records(self):
        with create_server(self.database, port=0) as server:
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            previous = self.server
            self.server = server
            try:
                state, _ = self.new_household()
                self.assertEqual((state["sources"], state["plans"], state["tasks"]), ([], [], []))
                self.assertEqual(state["members"], [])
            finally:
                self.server = previous
                server.shutdown()
                thread.join()

    def test_roster_addition_is_household_scoped_and_used_for_intake(self):
        state = self.post("members", {"name": "Morgan"})
        self.assertIn("Morgan", state["members"])
        self.post("members", {"name": "morgan"}, 409)
        draft = self.post("intake", {"text": "For: MORGAN"})["sources"][0]
        self.assertEqual(draft["person"], "Morgan")
        other, _ = self.new_household()
        self.assertNotIn("Morgan", other["members"])
        self.assertIn("Morgan", self.request("GET", "/api/export", self.cookie)[1]["members"])
        self.assertEqual(self.post("reset", {})["members"], [])

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
        self.assertEqual((status, body["status"], body["schemaVersion"]), (200, "ok", 5))
        db = sqlite3.connect(self.database)
        try:
            self.assertEqual(db.execute("SELECT version FROM schema_migrations ORDER BY version").fetchall(), [(1,), (2,), (3,), (4,), (5,)])
        finally:
            db.close()

    def test_competing_plan_revisions_return_scoped_recovery_metadata(self):
        base = self.state["plans"][0]
        drafts = [self.post("intake", {"title": title, "text": title})["sources"][0]["id"]
                  for title in ("Move pickup", "Bring water")]
        common = {"decision": "approve", "target": base["id"], "expectedSourceId": base["sourceId"]}
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda sid: self.request("POST", "/api/review", self.cookie, {**common, "id": sid}), drafts))
        self.assertEqual(sorted(result[0] for result in results), [200, 409])
        winner = next(i for i, result in enumerate(results) if result[0] == 200)
        conflict = results[1-winner][1]
        self.assertEqual(conflict["code"], "plan_changed")
        self.assertEqual(conflict["currentSourceId"], drafts[winner])
        state = self.post("review", {**common, "id": drafts[1-winner], "expectedSourceId": drafts[winner]})
        plan = next(plan for plan in state["plans"] if plan["id"] == base["id"])
        self.assertEqual([version["sourceId"] for version in plan["history"]], [base["sourceId"], drafts[winner]])

    def test_family_email_chunks_preserve_evidence_and_plan_logistics(self):
        text = ("Subject: Winter concert\r\nWhen: Saturday, December 5, 2026 at 6:30 p.m.\r\n"
                "Where: East auditorium\r\nFor: Sam\r\nResponsible: Alex\r\n"
                "RSVP by: December 1, 2026\r\nPlease bring a music folder.\r\n"
                "Instructions: Enter through the side door.")
        response = self.post("intake", {"text": text})
        draft = next(source for source in response["sources"] if source["id"] == response["createdSourceId"])
        self.assertEqual(draft["text"], text)
        expected = {"title":"Winter concert", "date":"2026-12-05", "time":"18:30", "location":"East auditorium",
                    "person":"Sam", "responsibility":"Alex", "deadline":"2026-12-01",
                    "preparation":"a music folder", "instructions":"Enter through the side door."}
        self.assertEqual({key:draft[key] for key in expected}, expected)
        self.assertEqual(draft["extraction"]["time"]["evidence"], [{"line":2,"value":"6:30 p.m."}])
        revised = self.post("review", {"id":draft["id"],"decision":"approve","location":"Main auditorium"})
        approved = next(plan for plan in revised["plans"] if plan["sourceId"] == draft["id"])
        self.assertEqual({key:approved[key] for key in expected},{**expected,"location":"Main auditorium"})
        self.assertEqual(revised["sources"][0]["extraction"]["location"]["evidence"][0]["value"],"East auditorium")

    def test_schedule_and_responsibility_abstain_on_ambiguous_values(self):
        draft = self.post("intake", {"text":"Event: Practice\nWhen: Friday at 4\nDate: 12/04/2026\n"
                                          "Due: tomorrow\nResponsible: Alex or Sam"})["sources"][0]
        for key in ("date","time","deadline","responsibility"):
            self.assertEqual(draft[key], "")
        self.assertEqual(draft["extraction"]["deadline"]["status"], "invalid")
        self.assertEqual(draft["extraction"]["responsibility"]["status"], "invalid")

    def test_invite_redeem_promote_remove_and_scope(self):
        invite = self.post("access", {"action": "invite", "name": "Jordan"})
        _, foreign = self.new_household()
        self.assertEqual(self.request("POST", "/api/join", foreign, {"code": invite["inviteCode"]})[0], 409)
        status, joined, headers = self.request("POST", "/api/join", data={"code": invite["inviteCode"]})
        self.assertEqual(status, 200)
        guest = headers["Set-Cookie"].split(";")[0]
        member_id = joined["access"]["viewer"]["id"]
        self.assertEqual(joined["access"]["viewer"]["role"], "member")
        self.assertEqual(joined["plans"], self.state["plans"])
        self.assertEqual(self.request("POST", "/api/join", data={"code": invite["inviteCode"]})[0], 404)
        self.assertEqual(self.request("GET", "/api/export", guest)[0], 403)
        self.assertEqual(self.request("POST", "/api/reset", guest, {})[0], 403)
        edit = {"action": "role", "id": member_id, "role": "admin"}
        self.assertEqual(self.request("POST", "/api/access", foreign, edit)[0], 404)
        self.assertEqual(self.request("POST", "/api/access", guest, edit)[0], 403)
        self.post("access", edit)
        self.assertEqual(self.request("GET", "/api/state", guest)[1]["access"]["viewer"]["role"], "admin")
        self.assertEqual(self.request("POST", "/api/access", guest, {"action": "invite", "name": "Taylor"})[0], 200)
        self.post("access", {"action": "remove", "id": member_id})
        self.assertEqual(self.request("GET", "/api/state", guest)[0], 401)

    def test_invitation_can_only_be_redeemed_once_under_concurrency(self):
        code = self.post("access", {"action": "invite", "name": "Robin"})["inviteCode"]
        with ThreadPoolExecutor(max_workers=2) as pool:
            statuses = list(pool.map(lambda _: self.request("POST", "/api/join", data={"code": code})[0], range(2)))
        self.assertEqual(sorted(statuses), [200, 404])

    def test_invitation_revocation_and_expiration_prevent_join(self):
        created = self.post("access", {"action": "invite", "name": "Robin"})
        invite_id = created["access"]["invites"][0]["id"]
        self.post("access", {"action": "revoke", "id": invite_id})
        self.assertEqual(self.request("POST", "/api/join", data={"code": created["inviteCode"]})[0], 404)
        created = self.post("access", {"action": "invite", "name": "Robin"})
        with closing(sqlite3.connect(self.database)) as db, db:
            db.execute("UPDATE household_invites SET expires=0")
        self.assertEqual(self.request("POST", "/api/join", data={"code": created["inviteCode"]})[0], 404)

