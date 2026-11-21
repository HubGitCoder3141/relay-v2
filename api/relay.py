"""Protected Vercel preview entry point for Relay."""
import os
import re
from contextlib import closing
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

import psycopg
from psycopg.rows import dict_row

from relay_auth import SupabaseAuth, account_cookie, session_token
from server import MIGRATIONS, Problem, RelayHandler, field

SCHEMA_FILE = Path(__file__).resolve().parent.parent / "supabase" / "relay_preview.sql"
PREVIEW_PROJECT = "qemqfiofozmxesdiikxv"
PRODUCTION_PROJECT = "tryyihbuzexsgvrfeuwn"

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

    def serve(self, post):
        url = urlsplit(self.path)
        if url.path in ("/api/relay", "/api/relay.py"):
            route = parse_qs(url.query, keep_blank_values=True).get("relay_path", [""])[0]
            self.path = "/" + route.lstrip("/")
        super().serve(post)

    def check_request(self):
        if os.environ.get("VERCEL_ENV") != "preview" and not (
                self.production and os.environ.get("RELAY_PRODUCTION_ENABLED") == "1"):
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
        if actual != MIGRATIONS[-1][0]:
            raise Problem(503, "The preview database schema needs an update.")
        return {"status": "ok", "database": "postgres", "schemaVersion": actual}

    def auth(self):
        return SupabaseAuth(PRODUCTION_PROJECT, os.environ.get("SUPABASE_PUBLISHABLE_KEY"))

    def api(self, path, post):
        if not self.production:
            return super().api(path, post)
        if path == "/api/auth" and post:
            return self.account_action()
        if path != "/api/health":
            self.account_id = self.auth().identity(session_token(self.headers))
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
        viewer, headers = super().household(db, allow_create)
        if self.production and allow_create:
            self.bind_account(db, viewer)
        return viewer, headers

    def join(self, db, data):
        viewer, headers = super().join(db, data)
        if self.production:
            self.bind_account(db, viewer)
        return viewer, headers

    def demo_enabled(self):
        return False

    def decorate_state(self, state):
        if self.production:
            state["accountMode"] = True
        return state

    @property
    def cookie_name(self):
        return "__Host-relay_preview"

    def session_headers(self, token):
        if self.production:
            return {}
        return {"Set-Cookie": f"{self.cookie_name}={token}; Secure; HttpOnly; SameSite=Strict; Path=/; Max-Age=86400"}
