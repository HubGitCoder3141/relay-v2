import importlib.util
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from types import ModuleType
from unittest.mock import patch

from relay_auth import SupabaseAuth, account_cookie, session_token
from server import Problem, change_access, connect, migrate


class HostedIdentityTests(unittest.TestCase):
    def setUp(self):
        self.auth = SupabaseAuth("test-project", "test-key")

    def test_identity_requires_a_verified_session_and_email(self):
        with self.assertRaises(Problem) as missing:
            self.auth.identity("")
        self.assertEqual(missing.exception.details["code"], "sign_in_required")
        uid = "d5a76f7c-6f00-4ae8-87b8-a5ad53a7e35b"
        with patch.object(self.auth, "request", return_value={"id": uid}):
            with self.assertRaises(Problem):
                self.auth.identity("unverified-cookie")
        with patch.object(self.auth, "request", return_value={
                "id": uid, "email_confirmed_at": "2026-11-21T00:00:00Z"
        }) as request:
            self.assertEqual(self.auth.identity("verified-cookie"), uid)
            request.assert_called_once_with("/user", token="verified-cookie")

    def test_account_cookie_is_separate_from_preview_cookie_and_http_only(self):
        header = account_cookie("abc.def.ghi", 3600)["Set-Cookie"]
        for part in ("Secure", "HttpOnly", "SameSite=Strict", "Path=/"):
            self.assertIn(part, header)
        self.assertEqual(session_token({"Cookie": header.split(";")[0]}), "abc.def.ghi")
        self.assertEqual(session_token({"Cookie": "__Host-relay_preview=some-local-token"}), "")


class FamilyAccessTests(unittest.TestCase):
    def test_owner_key_and_single_use_invite_share_one_private_household(self):
        # This checks the hosted handler's access logic using the loopback SQL store.
        driver = ModuleType("psycopg")
        driver.Error = Exception
        rows = ModuleType("psycopg.rows")
        rows.dict_row = None
        spec = importlib.util.spec_from_file_location("relay_hosted_test", Path(__file__).resolve().parents[1] / "api/relay.py")
        hosted = importlib.util.module_from_spec(spec)
        with patch.dict("sys.modules", {"psycopg": driver, "psycopg.rows": rows}):
            spec.loader.exec_module(hosted)

        app = object.__new__(hosted.handler)
        app.headers = {}
        owner_key = "A" * 43
        env = {"VERCEL_ENV": "production", "RELAY_ACCESS_MODE": "family", "RELAY_FAMILY_OWNER_KEY": owner_key}
        with tempfile.TemporaryDirectory() as temp, patch.dict("os.environ", env):
            database = Path(temp) / "family.db"
            migrate(database)
            with closing(connect(database)) as db, db:
                db.execute("CREATE TABLE family_owner_sessions (token_hash TEXT PRIMARY KEY, key_hash TEXT, expires INTEGER)")
                with self.assertRaises(Problem) as missing:
                    app.household(db, True)
                self.assertEqual(missing.exception.details["code"], "family_sign_in_required")
                with self.assertRaises(Problem):
                    app.join(db, {"code": "incorrect"})
                self.assertEqual(db.execute("SELECT count(*) FROM households").fetchone()[0], 0)

                owner, headers = app.join(db, {"code": owner_key})
                self.assertEqual(owner["role"], "owner")
                self.assertIn("Secure; HttpOnly; SameSite=Strict", headers["Set-Cookie"])
                original_cookie = headers["Set-Cookie"].split(";")[0]
                app.headers = {"Cookie": original_cookie}
                self.assertEqual(app.household(db, False)[0]["id"], owner["id"])
                _, second_session = app.join(db, {"code": owner_key})
                second_cookie = second_session["Set-Cookie"].split(";")[0]
                self.assertNotEqual(second_cookie, original_cookie)
                app.revoke_family_session(db)
                self.assertIsNone(app.session(db))
                app.headers = {"Cookie": second_cookie}
                self.assertEqual(app.session(db)["id"], owner["id"])
                invite = change_access(db, owner, {"action": "invite", "name": "Family member"})
                app.headers = {}
                member, member_headers = app.join(db, {"code": invite})
                self.assertEqual(member["household"], owner["household"])
                self.assertEqual(member["role"], "member")
                with self.assertRaises(Problem):
                    app.join(db, {"code": invite})

                with patch.dict("os.environ", {"RELAY_FAMILY_OWNER_KEY": "B" * 43}):
                    app.headers = {"Cookie": second_cookie}
                    self.assertIsNone(app.session(db))
                    rotated, _ = app.join(db, {"code": "B" * 43})
                    self.assertEqual(rotated["household"], owner["household"])
                    app.headers = {"Cookie": member_headers["Set-Cookie"].split(";")[0]}
                    self.assertEqual(app.session(db)["id"], member["id"])
                    change_access(db, rotated, {"action": "remove", "id": member["id"]})
                    with self.assertRaises(Problem) as revoked:
                        app.household(db, False)
                    self.assertEqual(revoked.exception.details["code"], "access_removed")
