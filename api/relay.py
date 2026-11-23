"""Protected Vercel preview entry point for Relay."""
import os
import re
from contextlib import closing
from hmac import compare_digest
from pathlib import Path
from secrets import token_urlsafe
from time import time
from urllib.parse import parse_qs, unquote, urlsplit

import psycopg
from psycopg.rows import dict_row

from relay_auth import SupabaseAuth, account_cookie, session_token
from relay_interpretation import active_notice_model
from server import MIGRATIONS, Problem, RelayHandler, field, session_hash

SCHEMA_FILE = Path(__file__).resolve().parent.parent / "supabase" / "relay_preview.sql"
PREVIEW_PROJECT = "qemqfiofozmxesdiikxv"
PRODUCTION_PROJECT = "tryyihbuzexsgvrfeuwn"
FAMILY_OWNER_ID = "relay-family-owner"
FAMILY_HOUSEHOLD_HASH = session_hash("relay-private-family-household")
OWNER_SESSION_SECONDS = 30 * 86400

class PostgresSession:
    def __init__(self, url, project):
        address = urlsplit(url)
        if (address.scheme not in ("postgres", "postgresql") or not address.hostname
                or not address.username or not address.password or not address.path):
            raise Problem(503, "The preview database configuration is incomplete.")
        username = unquote(address.username)
        if not (username.endswith("." + project) and address.hostname.endswith(".pooler.supabase.com")
                or address.hostname == f"db.{project}.supabase.co"):
            raise Problem(503, "The database does not match Relay’s configured environment.")
        # Supabase transaction pooling cannot retain server-side prepared statements.
        # Marketplace URLs may carry client-specific query keys that libpq does not accept.
        self.connection = psycopg.connect(host=address.hostname, port=address.port or 5432,
                                           dbname=unquote(address.path[1:]), user=username,
                                           password=unquote(address.password), sslmode="require", connect_timeout=6,
                                           prepare_threshold=None, row_factory=dict_row)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        if exc_type:
            self.connection.rollback()
        else:
            self.connection.commit()

    def close(self):
        self.connection.close()

    def execute(self, statement, values=()):
        return self.connection.execute(statement.replace("?", "%s"), values)


class handler(RelayHandler):
    storage_errors = (*RelayHandler.storage_errors, psycopg.Error)

    @property
    def production(self):
        return os.environ.get("VERCEL_ENV") == "production"

    @property
    def family_mode(self):
        return self.production and os.environ.get("RELAY_ACCESS_MODE") == "family"

    @property
    def accounts_mode(self):
        return self.production and os.environ.get("RELAY_ACCESS_MODE") == "accounts"

    def family_owner_key(self):
        key = os.environ.get("RELAY_FAMILY_OWNER_KEY", "")
        if not re.fullmatch(r"[A-Za-z0-9_-]{43,64}", key):
            raise Problem(503, "The private household has not been configured.")
        return key

    def family_key_hash(self):
        return session_hash("relay-family-key:" + self.family_owner_key())

    def family_token(self):
        return session_token(self.headers, self.cookie_name)

    def serve(self, post):
        url = urlsplit(self.path)
        if url.path in ("/api/relay", "/api/relay.py"):
            route = parse_qs(url.query, keep_blank_values=True).get("relay_path", [""])[0]
            self.path = "/" + route.lstrip("/")
        super().serve(post)

    def check_request(self):
        if os.environ.get("VERCEL_ENV") != "preview" and not (
                (self.family_mode or self.accounts_mode) and os.environ.get("RELAY_PRODUCTION_ENABLED") == "1"):
            raise Problem(503, "Relay production is not configured.")
        host = self.headers.get("Host", "").lower()
        if not re.fullmatch(r"[a-z0-9-]+\.vercel\.app", host):
            raise Problem(403, "Open the protected Relay preview directly.")
        origin = self.headers.get("Origin")
        if self.headers.get("Sec-Fetch-Site") == "cross-site" or (origin is not None and origin != f"https://{host}"):
            raise Problem(403, "Open the protected Relay preview directly.")

    def open_database(self):
        url = os.environ.get("POSTGRES_URL")
        if not url:
            raise Problem(503, "The preview database is not configured.")
        return PostgresSession(url, PRODUCTION_PROJECT if self.production else PREVIEW_PROJECT)

    def begin_database(self, db, write):
        if self.family_mode and urlsplit(self.path).path in ("/api/state", "/api/export", "/api/health"):
            db.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ, READ ONLY")
            write = False
        db.execute("SET LOCAL search_path = relay_production, pg_catalog" if self.production
                   else "SET LOCAL search_path = relay_preview, pg_catalog")
        db.execute("SET LOCAL statement_timeout = '5s'")
        # Preserve SQLite's single-writer invariants across preview function instances.
        if write:
            db.execute("SELECT pg_advisory_xact_lock(219553, 6)" if self.production
                       else "SELECT pg_advisory_xact_lock(219553, 5)")

    def health_status(self):
        with closing(self.open_database()) as db, db:
            self.begin_database(db, True)
            if not self.production and db.execute(
                    "SELECT to_regnamespace('relay_preview') IS NULL AS missing").fetchone()["missing"]:
                # Idempotent first initialization on this protected, pinned preview database.
                for statement in SCHEMA_FILE.read_text(encoding="utf-8").split(";"):
                    if statement.strip():
                        db.execute(statement)
            actual = db.execute("SELECT MAX(version) AS version FROM schema_version").fetchone()["version"]
            if not self.production and actual == 5:
                # The isolated Marketplace preview uses a separate project and self-initializes.
                db.execute("ALTER TABLE tasks ADD COLUMN IF NOT EXISTS due text NOT NULL DEFAULT ''")
                db.execute("INSERT INTO schema_version (version) VALUES (6) ON CONFLICT DO NOTHING")
                actual = 6
            if self.family_mode:
                db.execute("SELECT 1 FROM family_owner_sessions LIMIT 1").fetchone()
        if actual != MIGRATIONS[-1][0]:
            raise Problem(503, "The Relay database schema needs an update.")
        return {"status": "ok", "database": "postgres", "schemaVersion": actual,
                "noticeModelAvailable": active_notice_model() is not None}

    def auth(self):
        return SupabaseAuth(PRODUCTION_PROJECT, os.environ.get("SUPABASE_PUBLISHABLE_KEY"))

    def api(self, path, post):
        if not self.production:
            return super().api(path, post)
        if self.family_mode:
            self.family_owner_key()
            if path == "/api/auth" and post:
                if self.read_json().get("action") != "signout":
                    raise Problem(400, "Unknown sign-in action.")
                if self.family_token():
                    with closing(self.open_database()) as db, db:
                        self.begin_database(db, True)
                        self.revoke_family_session(db)
                self.json_response(200, {"stage": "family"}, self.session_headers(""))
                return
            if path not in ("/api/health", "/api/join") and not self.family_token():
                raise Problem(401, "Enter your private Relay code.", code="family_sign_in_required")
            return super().api(path, post)
        if path == "/api/auth" and post:
            return self.account_action()
        if path != "/api/health":
            self.account_id = self.auth().identity(session_token(self.headers))
        if path == "/api/onboard" and post:
            self.read_json()
            with closing(self.open_database()) as db, db:
                self.begin_database(db, True)
                self.create_account_household(db)
            self.json_response(200, {"stage": "ready"})
            return
        return super().api(path, post)

    def account_action(self):
        data = self.read_json()
        action = field(data, "action", 12, required=True)
        auth = self.auth()
        if action == "signout":
            token = session_token(self.headers)
            if token:
                try:
                    auth.request("/logout?scope=local", {}, token=token)
                except Problem as error:
                    if error.status != 401:
                        raise
            self.json_response(200, {"stage": "email"}, account_cookie("", 0))
            return
        email = field(data, "email", 254, required=True).lower()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            raise Problem(400, "Enter a valid email address.")
        if action == "request":
            auth.request("/otp", {"email": email, "create_user": True})
            self.json_response(200, {"stage": "code"})
            return
        if action != "verify":
            raise Problem(400, "Unknown sign-in action.")
        code = field(data, "code", 8, required=True)
        if not re.fullmatch(r"[0-9]{6,8}", code):
            raise Problem(400, "Enter the code from your email.")
        result = auth.request("/verify", {"type": "email", "email": email, "token": code})
        token = result.get("access_token", "")
        if not re.fullmatch(r"[A-Za-z0-9_.-]{20,3500}", token):
            raise Problem(503, "Sign-in did not return a usable session.")
        auth.identity(token)
        self.json_response(200, {"stage": "signed_in"}, account_cookie(token, 3600))

    def session(self, db):
        if self.family_mode:
            token = self.family_token()
            if not token:
                return None
            if re.fullmatch(r"owner_[A-Za-z0-9_-]{43}", token):
                return db.execute("""SELECT a.* FROM household_access a
                    WHERE a.id=? AND EXISTS (SELECT 1 FROM family_owner_sessions
                    WHERE token_hash=? AND key_hash=? AND expires>?)""",
                    (FAMILY_OWNER_ID, session_hash(token), self.family_key_hash(), int(time()))).fetchone()
            viewer = super().session(db)
            if viewer and not db.execute("SELECT 1 FROM households WHERE id=? AND session_hash=?",
                                         (viewer["household"], FAMILY_HOUSEHOLD_HASH)).fetchone():
                return None
            if viewer and viewer["role"] == "owner":
                return None
            return viewer
        if not self.production:
            return super().session(db)
        return db.execute(
            """SELECT a.* FROM household_access a
               JOIN identities i ON i.access_id = a.id WHERE i.user_id = CAST(? AS uuid)""",
            (self.account_id,),
        ).fetchone()

    def bind_account(self, db, viewer):
        db.execute(
            """INSERT INTO identities (user_id, access_id) VALUES (CAST(? AS uuid),?)
               ON CONFLICT(user_id) DO UPDATE SET access_id=excluded.access_id""",
            (self.account_id, viewer["id"]),
        )

    def household(self, db, allow_create):
        if self.family_mode:
            viewer = self.session(db)
            if not viewer:
                raise Problem(401, "Enter your private Relay code.", code="family_sign_in_required")
            if not viewer["active"]:
                raise Problem(401, "Access to this household was removed.", code="access_removed")
            return viewer, {}
        if self.accounts_mode and not self.session(db):
            raise Problem(409, "Create or join a household to continue.", code="household_setup_required")
        return super().household(db, allow_create)

    def create_account_household(self, db):
        viewer, _ = super().household(db, True)
        self.bind_account(db, viewer)

    def join(self, db, data):
        if self.family_mode:
            code = field(data, "code", 80, required=True)
            if code.isascii() and compare_digest(code, self.family_owner_key()):
                return self.join_family_owner(db)
            if not db.execute("""SELECT 1 FROM household_invites i JOIN households h ON i.household=h.id
                                 WHERE i.code_hash=? AND h.session_hash=?""",
                              (session_hash(code), FAMILY_HOUSEHOLD_HASH)).fetchone():
                raise Problem(404, "This invitation is invalid, expired, or already used.")
            return super().join(db, data)
        viewer, headers = super().join(db, data)
        if self.production:
            self.bind_account(db, viewer)
        return viewer, headers

    def join_family_owner(self, db):
        viewer = db.execute("SELECT * FROM household_access WHERE id=?", (FAMILY_OWNER_ID,)).fetchone()
        if viewer is None:
            household = db.execute("INSERT INTO households(session_hash) VALUES (?) RETURNING id",
                                   (FAMILY_HOUSEHOLD_HASH,)).fetchone()["id"]
            db.execute("INSERT INTO household_access VALUES (?,?,?,?,?,1)",
                       (FAMILY_OWNER_ID, household, "Workspace owner", session_hash(token_urlsafe(32)), "owner"))
            viewer = db.execute("SELECT * FROM household_access WHERE id=?", (FAMILY_OWNER_ID,)).fetchone()
        token = "owner_" + token_urlsafe(32)
        now = int(time())
        key_hash = self.family_key_hash()
        db.execute("DELETE FROM family_owner_sessions WHERE expires<=? OR key_hash<>?", (now, key_hash))
        db.execute("INSERT INTO family_owner_sessions VALUES (?,?,?)",
                   (session_hash(token), key_hash, now + OWNER_SESSION_SECONDS))
        return viewer, self.session_headers(token)

    def revoke_family_session(self, db):
        viewer = self.session(db)
        if viewer and viewer["role"] == "owner":
            db.execute("DELETE FROM family_owner_sessions WHERE token_hash=?", (session_hash(self.family_token()),))
        elif viewer and viewer["active"]:
            db.execute("UPDATE household_access SET active=0 WHERE id=?", (viewer["id"],))

    def demo_enabled(self):
        return False

    def decorate_state(self, state):
        if self.production:
            state["accountMode"] = True
            if self.family_mode:
                state["familyMode"] = True
        return state

    @property
    def cookie_name(self):
        if self.family_mode:
            return "__Host-relay_family"
        return "__Host-relay_preview"

    def session_headers(self, token):
        if self.family_mode:
            lifetime = (OWNER_SESSION_SECONDS if token.startswith("owner_") else 31536000) if token else 0
            return {"Set-Cookie": f"{self.cookie_name}={token}; Secure; HttpOnly; SameSite=Strict; Path=/; Max-Age={lifetime}"}
        if self.production:
            return {}
        return {"Set-Cookie": f"{self.cookie_name}={token}; Secure; HttpOnly; SameSite=Strict; Path=/; Max-Age=86400"}
