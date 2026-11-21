"""Relay's loopback-only, single-operator family workspace."""
import argparse
import hashlib
import json
import re
import secrets
import sqlite3
from contextlib import closing
from datetime import date, timedelta
from http.cookies import CookieError, SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
MEMBERS = ("Alex", "Sam")
FIELDS = ("title", "date", "time", "person")
SCHEMA = """
CREATE TABLE IF NOT EXISTS households (
    id INTEGER PRIMARY KEY, session_hash TEXT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS sources (
    household INTEGER NOT NULL REFERENCES households(id), id TEXT NOT NULL,
    text TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN ('pending','approved','rejected')),
    title TEXT NOT NULL, date TEXT NOT NULL, time TEXT NOT NULL,
    person TEXT NOT NULL, target TEXT NOT NULL,
    PRIMARY KEY(household,id)
);
CREATE TABLE IF NOT EXISTS versions (
    household INTEGER NOT NULL, plan TEXT NOT NULL, source TEXT NOT NULL,
    PRIMARY KEY(household,source),
    FOREIGN KEY(household,source) REFERENCES sources(household,id)
);
CREATE INDEX IF NOT EXISTS plan_versions ON versions(household,plan);
CREATE TABLE IF NOT EXISTS tasks (
    household INTEGER NOT NULL REFERENCES households(id), id TEXT NOT NULL,
    title TEXT NOT NULL, plan TEXT NOT NULL, person TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('open','done')),
    PRIMARY KEY(household,id)
);
CREATE INDEX IF NOT EXISTS household_tasks ON tasks(household, status, plan);
"""
MIGRATIONS = ((1, SCHEMA),)


class Problem(Exception):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status


def identifier():
    return secrets.token_urlsafe(16)


def session_hash(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def field(payload, key, limit, default="", required=False, preserve=False):
    value = payload.get(key, default)
    if not isinstance(value, str) or len(value) > limit or any(
        ord(ch) < 32 and ch not in "\r\n\t" or 0xD800 <= ord(ch) <= 0xDFFF for ch in value
    ):
        raise Problem(400, f"Check the {key} field (maximum {limit} characters).")
    if required and not value.strip():
        raise Problem(400, f"Enter a {key}.")
    return value if preserve else value.strip()


def validate_details(payload, source):
    title = field(payload, "title", 160, source["title"], required=True)
    day = field(payload, "date", 10, source["date"])
    hour = field(payload, "time", 5, source["time"])
    person = field(payload, "person", 80, source["person"])
    if day:
        try:
            if date.fromisoformat(day).isoformat() != day:
                raise ValueError()
        except ValueError:
            raise Problem(400, "Enter a valid date in YYYY-MM-DD format.") from None
    if hour and not re.fullmatch(r"(?:[01][0-9]|2[0-3]):[0-5][0-9]", hour):
        raise Problem(400, "Enter a valid 24-hour time in HH:MM format.")
    if hour and not day:
        raise Problem(400, "Choose a date for this time.")
    if person and person not in MEMBERS:
        raise Problem(400, "Choose a member of this household.")
    return title, day, hour, person


def deterministic_suggestion(text, title):
    """Extract only explicit, locale-independent fields from untrusted source text.

    Natural-language interpretation belongs behind the unavailable model boundary.
    This helper deliberately abstains from relative dates, ambiguous numeric dates,
    and names that are not known household members.
    """
    day_match = re.search(r"\bDate\s*:\s*(\d{4}-\d{2}-\d{2})\b", text, re.I)
    time_match = re.search(r"\bTime\s*:\s*((?:[01]\d|2[0-3]):[0-5]\d)\b", text, re.I)
    person_match = re.search(r"\b(?:For|Affected person)\s*:\s*(Alex|Sam)\b", text, re.I)
    day = day_match.group(1) if day_match else ""
    if day:
        try:
            if date.fromisoformat(day).isoformat() != day:
                day = ""
        except ValueError:
            day = ""
    return title, day, time_match.group(1) if time_match and day else "", person_match.group(1).title() if person_match else ""


def add_source(db, household, content, status, details, target=""):
    source_id = identifier()
    db.execute("INSERT INTO sources VALUES (?,?,?,?,?,?,?,?,?)",
               (household, source_id, content, status, *details, target))
    return source_id


def seed(db, household):
    today = date.today()
    tomorrow = (today + timedelta(days=1)).isoformat()
    entries = [
        ("Soccer pickup", today.isoformat(), "16:00", "Alex", "Alex will collect the team from the east gate at 4 pm."),
        ("Library books", tomorrow, "08:30", "Sam", "Please return the library books before morning class."),
        ("Music lesson", tomorrow, "15:30", "Alex", "The music lesson starts at 3:30 pm in the practice room."),
    ]
    for title, day, hour, person, notice in entries:
        plan = identifier()
        source = add_source(db, household, notice, "approved", (title, day, hour, person))
        db.execute("INSERT INTO versions VALUES (?,?,?)", (household, plan, source))
        if title == "Soccer pickup":
            soccer = plan
    add_source(db, household, "Practice will run 30 minutes later today. Please meet us at the east gate at 4:30 pm.",
               "pending", ("Soccer pickup", today.isoformat(), "16:30", "Alex"), soccer)


def snapshot(db, household):
    rows = db.execute("SELECT id,text,title,status,date,time,person,target FROM sources WHERE household=? ORDER BY rowid DESC",
                      (household,))
    sources = [dict(row) for row in rows]
    source_by_id = {s["id"]: s for s in sources}
    plans = {}
    for row in db.execute("SELECT plan,source FROM versions WHERE household=? ORDER BY rowid", (household,)):
        plan_id, source_id = row
        details = {k: source_by_id[source_id][k] for k in FIELDS}
        old = plans.get(plan_id)
        history = old["history"] + [{k: old[k] for k in (*FIELDS, "sourceId")}] if old else []
        plans[plan_id] = {"id": plan_id, **details, "sourceId": source_id, "history": history}
    tasks = [dict(row) for row in db.execute(
        "SELECT id,title,plan,person,status FROM tasks WHERE household=? ORDER BY rowid DESC", (household,)
    )]
    return {"members": list(MEMBERS), "sources": sources, "plans": list(plans.values()), "tasks": tasks}


def apply_review(db, household, payload):
    sid = field(payload, "id", 80, required=True)
    source = db.execute("SELECT * FROM sources WHERE household=? AND id=?", (household, sid)).fetchone()
    if source is None:
        raise Problem(404, "This source is unavailable.")
    if source["status"] != "pending":
        raise Problem(409, "This source has already been reviewed. Refresh to see the decision.")
    decision = field(payload, "decision", 10)
    if decision == "reject":
        db.execute("UPDATE sources SET status='rejected' WHERE household=? AND id=?", (household, sid))
        return
    if decision != "approve":
        raise Problem(400, "Choose approve or reject.")
    details = validate_details(payload, source)
    target = field(payload, "target", 80, source["target"])
    if target:
        latest = db.execute("SELECT source FROM versions WHERE household=? AND plan=? ORDER BY rowid DESC LIMIT 1",
                            (household, target)).fetchone()
        if latest is None:
            raise Problem(404, "This plan is unavailable.")
        if "expectedSourceId" in payload and field(payload, "expectedSourceId", 80) != latest["source"]:
            raise Problem(409, "This plan changed during review. Refresh and check the current version.")
    db.execute("UPDATE sources SET status='approved',title=?,date=?,time=?,person=?,target=? WHERE household=? AND id=?",
               (*details, target, household, sid))
    db.execute("INSERT INTO versions VALUES (?,?,?)", (household, target or identifier(), sid))


def apply_task(db, household, payload):
    action = field(payload, "action", 10, required=True)
    if action == "toggle":
        task_id = field(payload, "id", 80, required=True)
        task = db.execute("SELECT status FROM tasks WHERE household=? AND id=?", (household, task_id)).fetchone()
        if task is None:
            raise Problem(404, "This follow-through action is unavailable.")
        status = "done" if task["status"] == "open" else "open"
        db.execute("UPDATE tasks SET status=? WHERE household=? AND id=?", (status, household, task_id))
        return
    if action != "create":
        raise Problem(400, "Choose a follow-through action.")
    title = field(payload, "title", 160, required=True)
    person = field(payload, "person", 80)
    if person and person not in MEMBERS:
        raise Problem(400, "Choose a member of this household.")
    plan = field(payload, "plan", 80)
    if plan and db.execute("SELECT 1 FROM versions WHERE household=? AND plan=?", (household, plan)).fetchone() is None:
        raise Problem(404, "This plan is unavailable.")
    db.execute("INSERT INTO tasks VALUES (?,?,?,?,?,?)", (household, identifier(), title, plan, person, "open"))


def connect(database):
    db = sqlite3.connect(database, timeout=10)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    db.execute("PRAGMA secure_delete=ON")
    return db


def migrate(database):
    """Apply ordered, idempotent schema migrations before accepting requests."""
    with closing(connect(database)) as db, db:
        db.execute("CREATE TABLE IF NOT EXISTS schema_migrations (version INTEGER PRIMARY KEY)")
        applied = {row[0] for row in db.execute("SELECT version FROM schema_migrations")}
        for version, script in MIGRATIONS:
            if version not in applied:
                db.executescript(script)
                db.execute("INSERT INTO schema_migrations(version) VALUES (?)", (version,))


class RelayHandler(BaseHTTPRequestHandler):
    server_version = "Relay"
    sys_version = ""

    def log_message(self, fmt, *args):
        # The default access log includes paths and untrusted request data.
        pass

    def respond(self, status, body, mime, extra=None):
        self.send_response(status)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'")
        for name, value in (extra or {}).items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def json_response(self, status, value, headers=None):
        self.respond(status, json.dumps(value, ensure_ascii=False).encode("utf-8"),
                     "application/json; charset=utf-8", headers)

    def check_request(self):
        port = self.server.server_port
        hosts = {f"127.0.0.1:{port}", f"localhost:{port}"}
        if port == 80:
            hosts.update(("127.0.0.1", "localhost"))
        host = self.headers.get("Host", "").lower()
        if host not in hosts:
            raise Problem(403, "Use the local Relay address.")
        if self.headers.get("Sec-Fetch-Site") == "cross-site":
            raise Problem(403, "Open Relay directly on this device.")
        origin = self.headers.get("Origin")
        if origin is not None and origin != f"http://{host}":
            raise Problem(403, "Open Relay directly on this device.")

    def read_json(self):
        if self.headers.get_content_type() != "application/json":
            raise Problem(415, "Send JSON for this request.")
        length = self.headers.get("Content-Length", "")
        if not re.fullmatch(r"[0-9]{1,9}", length) or int(length) > 65536:
            raise Problem(413, "Use a shorter source.")
        try:
            data = json.loads(self.rfile.read(int(length)).decode("utf-8"))
        except (ValueError, RecursionError):
            raise Problem(400, "The request could not be read.") from None
        if not isinstance(data, dict):
            raise Problem(400, "Expected a JSON object.")
        return data

    def household(self, db, allow_create):
        cookie_name = f"relay_session_{self.server.server_port}"
        jar = SimpleCookie()
        try:
            jar.load(self.headers.get("Cookie", ""))
        except CookieError:
            pass
        if cookie_name in jar:
            record = db.execute("SELECT id FROM households WHERE session_hash=?",
                                (session_hash(jar[cookie_name].value),)).fetchone()
            if record:
                return record["id"], {}
        if not allow_create:
            raise Problem(401, "Open the household overview to start a local session.")
        token = secrets.token_urlsafe(32)
        household = db.execute("INSERT INTO households(session_hash) VALUES (?)", (session_hash(token),)).lastrowid
        seed(db, household)
        return household, {"Set-Cookie": f"{cookie_name}={token}; HttpOnly; SameSite=Strict; Path=/api/; Max-Age=31536000"}

    def api(self, path, post):
        allowed = {"/api/intake", "/api/review", "/api/tasks", "/api/reset"} if post else {"/api/state", "/api/export", "/api/health"}
        if path not in allowed:
            raise Problem(404, "Unknown endpoint.")
        if path == "/api/health":
            self.json_response(200, {"status": "ok", "schemaVersion": MIGRATIONS[-1][0]})
            return
        data = self.read_json() if post else {}
        with closing(connect(self.server.database)) as db, db:
            db.execute("BEGIN IMMEDIATE" if post or path == "/api/state" else "BEGIN")
            household, headers = self.household(db, path == "/api/state")
            if path == "/api/intake":
                content = field(data, "text", 12000, required=True, preserve=True)
                title = field(data, "title", 160) or content.strip().splitlines()[0][:160]
                add_source(db, household, content, "pending", deterministic_suggestion(content, title))
            elif path == "/api/review":
                apply_review(db, household, data)
            elif path == "/api/tasks":
                apply_task(db, household, data)
            elif path == "/api/reset":
                db.execute("DELETE FROM tasks WHERE household=?", (household,))
                db.execute("DELETE FROM versions WHERE household=?", (household,))
                db.execute("DELETE FROM sources WHERE household=?", (household,))
            elif path == "/api/export":
                headers["Content-Disposition"] = 'attachment; filename="relay-household.json"'
            state = snapshot(db, household)
        self.json_response(200, state, headers)

    def serve(self, post):
        try:
            self.check_request()
            path = urlsplit(self.path).path
            if post or path.startswith("/api/"):
                self.api(path, post)
                return
            if path in ("/", "/index.html"):
                name, mime = "index.html", "text/html"
            elif path == "/styles.css":
                name, mime = "styles.css", "text/css"
            elif re.fullmatch(r"/src/[A-Za-z0-9_-]+\.mjs", path):
                name, mime = path[1:], "text/javascript"
            else:
                raise Problem(404, "Page unavailable.")
            file = (ROOT / name).resolve()
            if not file.is_relative_to(ROOT) or not file.is_file():
                raise Problem(404, "Page unavailable.")
            self.respond(200, file.read_bytes(), mime + "; charset=utf-8")
        except Problem as err:
            self.json_response(err.status, {"error": str(err)})
        except (sqlite3.Error, OSError) as error:
            # Keep sensitive request content out of logs while preserving the
            # storage failure needed to diagnose a local startup problem.
            print(f"Relay storage error: {type(error).__name__}: {error}", flush=True)
            self.json_response(503, {"error": "Relay could not access local storage. Try again."})
        except ValueError:
            self.json_response(400, {"error": "Invalid request."})

    def do_GET(self):
        self.serve(False)

    def do_POST(self):
        self.serve(True)


def create_server(database, port=4173):
    database = Path(database)
    database.parent.mkdir(parents=True, exist_ok=True)
    migrate(database)
    server = ThreadingHTTPServer(("127.0.0.1", port), RelayHandler)
    server.database = database
    return server


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=4173)
    parser.add_argument("--database", type=Path, default=ROOT / ".relay" / "households.sqlite3")
    args = parser.parse_args()
    with create_server(args.database, args.port) as app:
        print(f"Relay is running at http://127.0.0.1:{app.server_port}", flush=True)
        try:
            app.serve_forever()
        except KeyboardInterrupt:
            pass
