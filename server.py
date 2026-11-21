"""Relay's loopback-only, single-operator family workspace."""
import argparse
import hashlib
import json
import re
import secrets
import sqlite3
from contextlib import closing
from datetime import date, timedelta
from time import time
from http.cookies import CookieError, SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from relay_intake import DETAIL_LIMIT, extract, valid_date, valid_time

ROOT = Path(__file__).resolve().parent
MEMBERS = ("Alex", "Sam")
FIELDS = ("title", "date", "time", "person", "preparation", "instructions", "location", "responsibility", "deadline")
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
MIGRATIONS = (
    (1, SCHEMA),
    (2, """
        ALTER TABLE sources ADD COLUMN preparation TEXT NOT NULL DEFAULT '';
        ALTER TABLE sources ADD COLUMN instructions TEXT NOT NULL DEFAULT '';
        ALTER TABLE sources ADD COLUMN extraction TEXT NOT NULL DEFAULT '{}';
    """),
    (3, """
        CREATE TABLE IF NOT EXISTS members (
            household INTEGER NOT NULL REFERENCES households(id), name TEXT NOT NULL,
            normalized TEXT NOT NULL, PRIMARY KEY(household,normalized)
        );
        INSERT INTO members SELECT id,'Alex','alex' FROM households
            WHERE id IN (SELECT household FROM sources UNION SELECT household FROM tasks);
        INSERT INTO members SELECT id,'Sam','sam' FROM households
            WHERE id IN (SELECT household FROM sources UNION SELECT household FROM tasks);
    """),
    (4, """
        CREATE TABLE household_access (
            id TEXT PRIMARY KEY, household INTEGER NOT NULL REFERENCES households(id),
            name TEXT NOT NULL, token_hash TEXT NOT NULL UNIQUE,
            role TEXT NOT NULL CHECK(role IN ('owner','admin','member')),
            active INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0,1))
        );
        CREATE INDEX access_household ON household_access(household,active);
        INSERT INTO household_access (id,household,name,token_hash,role)
            SELECT lower(hex(randomblob(16))),id,'Workspace owner',session_hash,'owner' FROM households;
        CREATE TABLE household_invites (
            id TEXT PRIMARY KEY, household INTEGER NOT NULL REFERENCES households(id),
            name TEXT NOT NULL, code_hash TEXT NOT NULL UNIQUE, expires INTEGER NOT NULL
        );
        CREATE INDEX invites_household ON household_invites(household,expires);
    """),
    (5, """
        ALTER TABLE sources ADD COLUMN location TEXT NOT NULL DEFAULT '';
        ALTER TABLE sources ADD COLUMN responsibility TEXT NOT NULL DEFAULT '';
        ALTER TABLE sources ADD COLUMN deadline TEXT NOT NULL DEFAULT '';
    """),
)


class Problem(Exception):
    def __init__(self, status, message, **details):
        super().__init__(message)
        self.status = status
        self.details = details


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


def validate_details(payload, source, members):
    title = field(payload, "title", 160, source["title"], required=True)
    day = field(payload, "date", 10, source["date"])
    hour = field(payload, "time", 5, source["time"])
    person = field(payload, "person", 80, source["person"])
    if day and not valid_date(day):
        raise Problem(400, "Enter a valid date in YYYY-MM-DD format.")
    if hour and not valid_time(hour):
        raise Problem(400, "Enter a valid 24-hour time in HH:MM format.")
    if hour and not day:
        raise Problem(400, "Choose a date for this time.")
    responsible = field(payload, "responsibility", 80, source["responsibility"])
    if any(name and name not in members for name in (person, responsible)):
        raise Problem(400, "Choose a member of this household.")
    preparation = field(payload, "preparation", DETAIL_LIMIT, source["preparation"])
    instructions = field(payload, "instructions", DETAIL_LIMIT, source["instructions"])
    location = field(payload, "location", 160, source["location"])
    deadline = field(payload, "deadline", 10, source["deadline"])
    if deadline and not valid_date(deadline):
        raise Problem(400, "Enter a valid deadline in YYYY-MM-DD format.")
    return title, day, hour, person, preparation, instructions, location, responsible, deadline


def add_source(db, household, content, status, details, target="", evidence=None):
    source_id = identifier()
    columns = ("household", "id", "text", "status", "target", "extraction", *FIELDS)
    query = f"INSERT INTO sources ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})"
    db.execute(query, (household, source_id, content, status, target,
                       json.dumps(evidence or {}, ensure_ascii=False), *details))
    return source_id


def seed(db, household):
    for name in MEMBERS:
        add_member(db, household, {"name": name})
    today = date.today()
    tomorrow = (today + timedelta(days=1)).isoformat()
    entries = [
        ("Soccer pickup", today.isoformat(), "16:00", "Alex", "Alex will collect the team from the east gate at 4 pm."),
        ("Library books", tomorrow, "08:30", "Sam", "Please return the library books before morning class."),
        ("Music lesson", tomorrow, "15:30", "Alex", "The music lesson starts at 3:30 pm in the practice room."),
    ]
    for title, day, hour, person, notice in entries:
        plan = identifier()
        source = add_source(db, household, notice, "approved", (title, day, hour, person, "", "", "", "", ""))
        db.execute("INSERT INTO versions VALUES (?,?,?)", (household, plan, source))
        if title == "Soccer pickup":
            soccer = plan
    add_source(db, household, "Practice will run 30 minutes later today. Please meet us at the east gate at 4:30 pm.",
               "pending", ("Soccer pickup", today.isoformat(), "16:30", "Alex", "", "", "", "", ""), soccer)


def member_names(db, household):
    return [row["name"] for row in db.execute(
        "SELECT name FROM members WHERE household=? ORDER BY normalized", (household,)
    )]


def access_snapshot(db, viewer):
    household = viewer["household"]
    profile = {key: viewer[key] for key in ("id", "name", "role")}
    people = [dict(row) for row in db.execute(
        """SELECT id,name,role FROM household_access WHERE household=? AND active=1
           ORDER BY CASE role WHEN 'owner' THEN 0 WHEN 'admin' THEN 1 ELSE 2 END,name,id""",
        (household,),
    )]
    invites = []
    if viewer["role"] in ("owner", "admin"):
        invites = [dict(row) for row in db.execute(
            "SELECT id,name,expires FROM household_invites WHERE household=? AND expires>? ORDER BY expires,id",
            (household, int(time())),
        )]
    return {"viewer": profile, "people": people, "invites": invites}


def require_role(viewer, *roles):
    if viewer["role"] not in roles:
        raise Problem(403, "Your household role does not allow this action.")


def change_access(db, viewer, payload):
    require_role(viewer, "owner", "admin")
    household = viewer["household"]
    action = field(payload, "action", 16, required=True)
    if action == "invite":
        name = " ".join(field(payload, "name", 80, required=True).split())
        code = secrets.token_urlsafe(24)
        db.execute("DELETE FROM household_invites WHERE household=? AND expires<=?", (household, int(time())))
        db.execute("INSERT INTO household_invites VALUES (?,?,?,?,?)",
                   (identifier(), household, name, session_hash(code), int(time()) + 86400))
        return code
    person_id = field(payload, "id", 80, required=True)
    if action == "revoke":
        result = db.execute("DELETE FROM household_invites WHERE household=? AND id=?", (household, person_id))
        if not result.rowcount:
            raise Problem(404, "That invitation is unavailable.")
        return None
    require_role(viewer, "owner")
    if action not in ("role", "remove"):
        raise Problem(400, "Choose a household access action.")
    person = db.execute(
        "SELECT role FROM household_access WHERE household=? AND id=? AND active=1", (household, person_id)
    ).fetchone()
    if person is None:
        raise Problem(404, "That household member is unavailable.")
    if person["role"] == "owner":
        raise Problem(403, "The workspace owner cannot be changed or removed.")
    if action == "remove":
        db.execute("UPDATE household_access SET active=0 WHERE household=? AND id=?", (household, person_id))
    else:
        role = field(payload, "role", 8, required=True)
        if role not in ("admin", "member"):
            raise Problem(400, "Choose admin or adult member.")
        db.execute("UPDATE household_access SET role=? WHERE household=? AND id=?", (role, household, person_id))
    return None


def add_member(db, household, payload):
    name = " ".join(field(payload, "name", 80, required=True).split())
    normalized = name.casefold()
    cursor = db.execute(
        "INSERT INTO members VALUES (?,?,?) ON CONFLICT(household,normalized) DO NOTHING",
        (household, name, normalized),
    )
    if not cursor.rowcount:
        raise Problem(409, "That name is already in the household.")


def snapshot(db, household):
    rows = db.execute("""SELECT id,text,title,status,date,time,person,target,preparation,instructions,
                                location,responsibility,deadline,extraction
                         FROM sources WHERE household=? ORDER BY rowid DESC""",
                      (household,))
    sources = [{**dict(row), "extraction": json.loads(row["extraction"])} for row in rows]
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
    return {"members": member_names(db, household), "sources": sources, "plans": list(plans.values()), "tasks": tasks,
            "schemaVersion": MIGRATIONS[-1][0]}


def apply_review(db, household, payload):
    sid = field(payload, "id", 80, required=True)
    source = db.execute("SELECT * FROM sources WHERE household=? AND id=?", (household, sid)).fetchone()
    if source is None:
        raise Problem(404, "This source is unavailable.")
    if source["status"] != "pending":
        raise Problem(409, "This source has already been reviewed.", code="suggestion_reviewed")
    decision = field(payload, "decision", 10)
    if decision == "reject":
        db.execute("UPDATE sources SET status='rejected' WHERE household=? AND id=?", (household, sid))
        return
    if decision != "approve":
        raise Problem(400, "Choose approve or reject.")
    details = validate_details(payload, source, member_names(db, household))
    target = field(payload, "target", 80, source["target"])
    if target:
        latest = db.execute("SELECT source FROM versions WHERE household=? AND plan=? ORDER BY rowid DESC LIMIT 1",
                            (household, target)).fetchone()
        if latest is None:
            raise Problem(404, "This plan is unavailable.")
        if field(payload, "expectedSourceId", 80) != latest["source"]:
            raise Problem(409, "Another review updated this plan.", code="plan_changed",
                          currentSourceId=latest["source"])
    assignments = ",".join(f"{key}=?" for key in FIELDS)
    db.execute(f"UPDATE sources SET status='approved',{assignments},target=? WHERE household=? AND id=?",
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
    if person and person not in member_names(db, household):
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
        for version, script in MIGRATIONS:
            db.execute("BEGIN IMMEDIATE")
            if db.execute("SELECT 1 FROM schema_migrations WHERE version=?", (version,)).fetchone() is None:
                for statement in script.split(";"):
                    if statement.strip():
                        db.execute(statement)
                db.execute("INSERT INTO schema_migrations(version) VALUES (?)", (version,))
            db.commit()


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

    @property
    def cookie_name(self):
        return f"relay_session_{self.server.server_port}"

    def session(self, db):
        jar = SimpleCookie()
        try:
            jar.load(self.headers.get("Cookie", ""))
        except CookieError:
            pass
        if self.cookie_name in jar:
            return db.execute("SELECT * FROM household_access WHERE token_hash=?",
                              (session_hash(jar[self.cookie_name].value),)).fetchone()
        return None

    def session_headers(self, token):
        return {"Set-Cookie": f"{self.cookie_name}={token}; HttpOnly; SameSite=Strict; Path=/api/; Max-Age=31536000"}

    def household(self, db, allow_create):
        record = self.session(db)
        if record:
            if not record["active"]:
                raise Problem(401, "Access to this household was removed.", code="access_removed")
            return record, {}
        if not allow_create:
            raise Problem(401, "Open the household overview to start a local session.")
        token = secrets.token_urlsafe(32)
        token_hash = session_hash(token)
        household = db.execute("INSERT INTO households(session_hash) VALUES (?)", (token_hash,)).lastrowid
        person_id = identifier()
        db.execute("INSERT INTO household_access VALUES (?,?,?,?,?,1)",
                   (person_id, household, "Workspace owner", token_hash, "owner"))
        if self.server.demo:
            seed(db, household)
        return db.execute("SELECT * FROM household_access WHERE id=?", (person_id,)).fetchone(), self.session_headers(token)

    def join(self, db, data):
        code = field(data, "code", 80, required=True)
        invite = db.execute("SELECT * FROM household_invites WHERE code_hash=? AND expires>?",
                            (session_hash(code), int(time()))).fetchone()
        if invite is None:
            raise Problem(404, "This invitation is invalid, expired, or already used.")
        old = self.session(db)
        if old and old["active"]:
            scope = old["household"]
            has_records = any(db.execute(f"SELECT 1 FROM {table} WHERE household=? LIMIT 1", (scope,)).fetchone()
                              for table in ("sources", "tasks", "members", "household_invites"))
            has_other_access = db.execute(
                "SELECT 1 FROM household_access WHERE household=? AND id<>? AND active=1", (scope, old["id"])
            ).fetchone()
            if old["role"] != "owner" or has_records or has_other_access or scope == invite["household"]:
                raise Problem(409, "Open the invitation in a fresh browser profile to keep this workspace.")
            db.execute("UPDATE household_access SET active=0 WHERE id=?", (old["id"],))
        token, person_id = secrets.token_urlsafe(32), identifier()
        db.execute("INSERT INTO household_access VALUES (?,?,?,?,?,1)",
                   (person_id, invite["household"], invite["name"], session_hash(token), "member"))
        db.execute("DELETE FROM household_invites WHERE id=?", (invite["id"],))
        return db.execute("SELECT * FROM household_access WHERE id=?", (person_id,)).fetchone(), self.session_headers(token)

    def api(self, path, post):
        allowed = {"/api/intake", "/api/review", "/api/tasks", "/api/reset", "/api/members", "/api/access", "/api/join"} if post else {"/api/state", "/api/export", "/api/health"}
        if path not in allowed:
            raise Problem(404, "Unknown endpoint.")
        if path == "/api/health":
            self.json_response(200, {"status": "ok", "schemaVersion": MIGRATIONS[-1][0]})
            return
        data = self.read_json() if post else {}
        with closing(connect(self.server.database)) as db, db:
            db.execute("BEGIN IMMEDIATE" if post or path == "/api/state" else "BEGIN")
            viewer, headers = self.join(db, data) if path == "/api/join" else self.household(db, path == "/api/state")
            household = viewer["household"]
            invite_code = None
            created_source = None
            if path == "/api/intake":
                content = field(data, "text", 12000, required=True, preserve=True)
                values, evidence = extract(content, member_names(db, household))
                first_line = content.strip().splitlines()[0]
                title = field(data, "title", 160) or values.get("title")
                if not title:
                    title = first_line if len(first_line) <= 72 and ":" not in first_line else "Untitled plan"
                details = (title, *(values.get(key, "") for key in FIELDS[1:]))
                created_source = add_source(db, household, content, "pending", details, evidence=evidence)
            elif path == "/api/review":
                apply_review(db, household, data)
            elif path == "/api/tasks":
                apply_task(db, household, data)
            elif path == "/api/members":
                require_role(viewer, "owner", "admin")
                add_member(db, household, data)
            elif path == "/api/access":
                invite_code = change_access(db, viewer, data)
            elif path == "/api/reset":
                require_role(viewer, "owner")
                db.execute("DELETE FROM tasks WHERE household=?", (household,))
                db.execute("DELETE FROM versions WHERE household=?", (household,))
                db.execute("DELETE FROM sources WHERE household=?", (household,))
                db.execute("DELETE FROM members WHERE household=?", (household,))
                db.execute("DELETE FROM household_invites WHERE household=?", (household,))
            elif path == "/api/export":
                require_role(viewer, "owner")
                headers["Content-Disposition"] = 'attachment; filename="relay-household.json"'
            state = snapshot(db, household)
            state["access"] = access_snapshot(db, viewer)
            if invite_code:
                state["inviteCode"] = invite_code
            if created_source:
                state["createdSourceId"] = created_source
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
            self.json_response(err.status, {"error": str(err), **err.details})
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


def create_server(database, port=4173, *, demo=False):
    database = Path(database)
    database.parent.mkdir(parents=True, exist_ok=True)
    migrate(database)
    server = ThreadingHTTPServer(("127.0.0.1", port), RelayHandler)
    server.database = database
    server.demo = demo
    return server


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=4173)
    parser.add_argument("--database", type=Path, default=ROOT / ".relay" / "households.sqlite3")
    parser.add_argument("--demo", action="store_true", help="Seed fictional plans for new workspaces.")
    args = parser.parse_args()
    with create_server(args.database, args.port, demo=args.demo) as app:
        print(f"Relay is running at http://127.0.0.1:{app.server_port}", flush=True)
        try:
            app.serve_forever()
        except KeyboardInterrupt:
            pass
