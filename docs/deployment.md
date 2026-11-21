# Deployment readiness

## Current supported topology

Local Relay runs as a loopback-only Python HTTP service with SQLite. Run it on one trusted device:

```powershell
python server.py --port 4173
```

Relay also has a Vercel-protected preview function in `api/relay.py`. Preview uses the Supabase Marketplace `POSTGRES_URL` and a private `relay_preview` schema. The health endpoint initializes that schema on the pinned preview resource if missing, then checks its version. The function rejects Production requests and does not fall back to SQLite. Vercel authentication must remain enabled for this preview. Use synthetic data. The local and hosted stores are separate.

The product needs a Python service, transactional persistence, and session authorization. GitHub Pages can only serve static files.

## Preparing Production

Production expects the separate Supabase project `relay`. The existing Preview credentials remain scoped to Preview.

1. Add the Production project's **Transaction pooler** connection string to Vercel as `POSTGRES_URL`, scoped to **Production**. Store it in Vercel's secret manager.
2. Set `SUPABASE_PUBLISHABLE_KEY` to the same project's publishable key in Production. Use a custom SMTP sender in Supabase Auth that can deliver to external users. Configure the email OTP template to include `{{ .Token }}`.
3. Apply `supabase/relay_preview.sql` with its schema name replaced by `relay_production`, then apply `supabase/production_identities.sql`. This gives hosted users durable identity-to-membership links without exposing the tables to Supabase Data API roles.
4. After configuration, set `RELAY_PRODUCTION_ENABLED=1` for a protected Production candidate. Verify an external email signup, logout, token expiry, invite and competing revision workflows before assigning the public URL.

The browser receives a Secure, HttpOnly account cookie. Supabase confirms the identity on each protected API request. Accounts return to their bound household. Expired access requires a fresh email code.

## Required architecture before an internet-facing deployment

1. Run the Python service behind a managed HTTPS reverse proxy.
2. Replace local synthetic-session creation with account authentication and a verified household membership/role model.
3. Move SQLite to a managed, encrypted relational database with backups, migration execution, retention/deletion jobs, and recovery testing.
4. Store secrets in the host’s secret manager; never commit them or place them in browser code.
5. Add rate limits, structured privacy-safe logging, monitoring, audit events, CSRF/session lifecycle controls, and an incident-response process.
6. Complete a privacy review, consent/deletion model, terms, and real-family security testing before holding non-synthetic data.

Suitable low-cost future shapes include a Python-capable container host plus managed Postgres. Selecting a provider, creating accounts, exposing a URL, or paying for services requires separate authorization.
