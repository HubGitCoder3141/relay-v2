"""Protected Vercel preview entry point for Relay."""
import os
import re
from contextlib import closing
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

import psycopg
from psycopg.rows import dict_row

from server import MIGRATIONS, Problem, RelayHandler

SCHEMA_FILE = Path(__file__).resolve().parent.parent / "supabase" / "relay_preview.sql"
PREVIEW_PROJECT = "qemqfiofozmxesdiikxv"

class PostgresSession:
    def __init__(self, url):
        address = urlsplit(url)
        if (address.scheme not in ("postgres", "postgresql") or not address.hostname
                or not address.username or not address.password or not address.path):
            raise Problem(503, "The preview database configuration is incomplete.")
        username = unquote(address.username)
        if not (username.endswith("." + PREVIEW_PROJECT) and address.hostname.endswith(".pooler.supabase.com")
                or address.hostname == f"db.{PREVIEW_PROJECT}.supabase.co"):
            raise Problem(503, "The database does not match Relay’s preview resource.")
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

    def serve(self, post):
        url = urlsplit(self.path)
        if url.path in ("/api/relay", "/api/relay.py"):
            route = parse_qs(url.query, keep_blank_values=True).get("relay_path", [""])[0]
            self.path = "/" + route.lstrip("/")
        super().serve(post)

    def check_request(self):
        if os.environ.get("VERCEL_ENV") != "preview":
            raise Problem(503, "Relay is available only in its protected preview.")
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
        return PostgresSession(url)

    def begin_database(self, db, write):
        db.execute("SET LOCAL search_path = relay_preview, pg_catalog")
        db.execute("SET LOCAL statement_timeout = '5s'")
        # Preserve SQLite's single-writer invariants across preview function instances.
        if write:
            db.execute("SELECT pg_advisory_xact_lock(219553, 5)")

    def health_status(self):
        with closing(self.open_database()) as db, db:
            self.begin_database(db, True)
            missing = db.execute("SELECT to_regnamespace('relay_preview') IS NULL AS missing").fetchone()["missing"]
            if missing:
                # Idempotent first initialization on this protected, pinned preview database.
                for statement in SCHEMA_FILE.read_text(encoding="utf-8").split(";"):
                    if statement.strip():
                        db.execute(statement)
            actual = db.execute("SELECT MAX(version) AS version FROM schema_version").fetchone()["version"]
        if actual != MIGRATIONS[-1][0]:
            raise Problem(503, "The preview database schema needs an update.")
        return {"status": "ok", "database": "postgres", "schemaVersion": actual}

    def demo_enabled(self):
        return False

    @property
    def cookie_name(self):
        return "__Host-relay_preview"

    def session_headers(self, token):
        return {"Set-Cookie": f"{self.cookie_name}={token}; Secure; HttpOnly; SameSite=Strict; Path=/; Max-Age=86400"}
