import unittest
from unittest.mock import patch

from relay_auth import SupabaseAuth, account_cookie, session_token
from server import Problem


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
