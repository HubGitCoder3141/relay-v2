# Relay V1 technical architecture

## Runtime shape

`server.py` runs one loopback-only HTTP process at `127.0.0.1`. Browser modules call its same-origin JSON API. SQLite persists source records and plan version links. The current build has no external service, identity provider, model provider, background worker, or real-time channel.

```mermaid
flowchart LR
  Browser[Browser UI] -->|same-origin JSON| Server[Python service]
  Server -->|transactional records| Database[(SQLite)]
  Browser -->|read-only snapshot| Reasoning[Briefing and lookup module]
  Reasoning -->|source and plan references| Browser
```

## Data model

| Record | Fields | Role |
| --- | --- | --- |
| Household | internal ID, session token hash | Isolates a browser-local synthetic workspace. |
| Source | ID, original wording, review status, title, date, time, affected person, target plan | Retains untrusted input and its reviewed structured values. |
| Plan version link | household, plan ID, source ID | Creates an ordered, source-linked history for a plan. |
| Plan projection | current source values and earlier linked source values | Built from version links for the UI and reasoning module. |
| Follow-through action | household, action ID, plan ID, assigned person, open/done state | Tracks a practical local action without claiming external completion. |
| Migration ledger | ordered schema versions | Applies idempotent SQLite migrations before the server accepts requests. |

The session token never enters SQLite in readable form. A request cookie is HttpOnly and SameSite=Strict with an `/api/` path. A browser with no valid session gets a new synthetic household only through `GET /api/state`.

## API boundary

| Endpoint | Method | Operation |
| --- | --- | --- |
| `/api/state` | GET | Return the authorized household snapshot, creating a synthetic workspace when needed. |
| `/api/intake` | POST | Preserve pasted text and create a pending source. |
| `/api/review` | POST | Approve or reject a pending source. Approval adds a plan or a new plan version. |
| `/api/export` | GET | Return the authorized snapshot as JSON. |
| `/api/reset` | POST | Remove plans and sources from the authorized local household. |
| `/api/tasks` | POST | Create or toggle an authorized plan-specific follow-through action. |
| `/api/health` | GET | Return the local service and schema-migration status without reading household data. |

All mutations validate JSON size and field types, operate in a SQLite transaction, and return the resulting snapshot. Review accepts an `expectedSourceId` for a target plan, preventing a stale reviewer from silently adding a revision after another review changed that plan.

## Security boundaries

The service binds only to loopback, checks the `Host`, rejects cross-site fetch metadata and foreign origins, and serves a fixed allowlist of runtime files. Source text is treated as data and rendered with HTML escaping. The server sets content security, no-sniff, referrer, and no-store headers. Default HTTP logging is disabled because request paths and source content can be sensitive.

This protects the local evaluation scope. Network deployment needs production authentication, password policy or passkey design, family membership authorization, encrypted transport, secure secret management, file scanning, abuse protection, audit trails, backups, monitoring, privacy review, and incident response.

## Intelligence boundary

The browser reasoning module receives a snapshot and has no write or network capability. It uses deterministic rules for date ordering, version comparison, exact collision detection, duplicate wording, and a bounded question grammar. `interpretSource` is an explicit unavailable interface. A future model adapter should create review candidates with source spans and schema validation before a human-approved server transition.
