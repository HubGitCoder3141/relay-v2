"""Supabase email-code authentication for the hosted production application."""
import json
from http.cookies import CookieError, SimpleCookie
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener
from uuid import UUID

from server import Problem

AUTH_COOKIE = "__Host-relay_account"


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def account_cookie(token, age):
    return {"Set-Cookie": f"{AUTH_COOKIE}={token}; Secure; HttpOnly; SameSite=Strict; Path=/; Max-Age={age}"}


def session_token(headers):
    jar = SimpleCookie()
    try:
        jar.load(headers.get("Cookie", ""))
    except CookieError:
        return ""
    return jar[AUTH_COOKIE].value if AUTH_COOKIE in jar else ""


class SupabaseAuth:
    def __init__(self, project, key):
        if not key:
            raise Problem(503, "Relay sign-in is not configured.")
        self.base_url = f"https://{project}.supabase.co/auth/v1"
        self.key = key

    def request(self, path, body=None, token=""):
        headers = {"apikey": self.key, "Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        request = Request(self.base_url + path, None if body is None else json.dumps(body).encode(),
                          headers=headers)
        try:
            with build_opener(NoRedirect()).open(request, timeout=8) as response:
                raw = response.read(65536)
                return json.loads(raw) if raw else {}
        except HTTPError as error:
            if error.code == 429:
                raise Problem(429, "Too many sign-in attempts. Wait a little and try again.") from None
            if error.code >= 500:
                raise Problem(503, "Sign-in is temporarily unavailable.") from None
            raise Problem(401, "Sign-in could not be verified. Request a new email code.", code="sign_in_required") from None
        except (URLError, OSError, ValueError):
            raise Problem(503, "Sign-in is temporarily unavailable.") from None

    def identity(self, token):
        if not token:
            raise Problem(401, "Sign in to open your household.", code="sign_in_required")
        user = self.request("/user", token=token)
        try:
            uid = str(UUID(user.get("id", "")))
        except (AttributeError, ValueError, TypeError):
            raise Problem(401, "Sign in to open your household.", code="sign_in_required") from None
        if not user.get("email_confirmed_at"):
            raise Problem(401, "Verify your email before signing in.", code="sign_in_required")
        return uid
