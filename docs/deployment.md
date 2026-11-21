# Deployment readiness

## Current supported topology

Relay V2 is a loopback-only Python HTTP service with SQLite. Run it on one trusted device:

```powershell
python server.py --port 4173
```

It is intentionally not deployable on GitHub Pages: the product needs a Python service, transactional persistence, and session authorization. GitHub Pages can only serve static files.

## Required architecture before an internet-facing deployment

1. Run the Python service behind a managed HTTPS reverse proxy.
2. Replace local synthetic-session creation with account authentication and a verified household membership/role model.
3. Move SQLite to a managed, encrypted relational database with backups, migration execution, retention/deletion jobs, and recovery testing.
4. Store secrets in the host’s secret manager; never commit them or place them in browser code.
5. Add rate limits, structured privacy-safe logging, monitoring, audit events, CSRF/session lifecycle controls, and an incident-response process.
6. Complete a privacy review, consent/deletion model, terms, and real-family security testing before holding non-synthetic data.

Suitable low-cost future shapes include a Python-capable container host plus managed Postgres. Selecting a provider, creating accounts, exposing a URL, or paying for services requires separate authorization.
