# Relay V2

Relay is a local family-coordination evaluation build. It preserves an original message, creates a reviewable suggestion, records an approved family plan or revision, retains source history, tracks plan-specific follow-through actions, detects exact schedule overlaps, and answers a bounded set of questions from approved household records.

## Run locally

```powershell
python server.py --port 4173
```

Open [http://127.0.0.1:4173](http://127.0.0.1:4173). Relay creates one synthetic household per browser session and stores it in `.relay/households.sqlite3`. Use the Household menu to export or delete that local workspace.

If the page says **“Briefing unavailable”**, close any earlier Relay terminal windows, run the command above once, and refresh this exact `127.0.0.1` address. Opening `index.html` directly or through a static preview cannot start the local API.

## V2 capabilities

- A source-backed intake → review → approval/rejection journey with immutable plan version history.
- Household-scoped SQLite persistence, hashed session tokens, transactional writes, schema migrations, health endpoint, export, and permanent local reset.
- Plan-specific follow-through actions with household validation and open/done state.
- Deterministic briefing, source duplicate detection, exact schedule collision detection, field-change history, and bounded evidence-linked lookup.

## Capability boundary

No AI provider, API key, model, external integration, email connection, file processing, account system, or real household sharing is configured. The intake screen accepts pasted text. It can prefill only explicitly labelled ISO fields such as `Date: 2026-12-04`, `Time: 16:15`, and `For: Sam`. Everything else requires a reviewer to fill or correct before it becomes an approved plan.

Ask Relay supports current records for today, tomorrow, changes, exact-time conflicts, sources awaiting review, and a person listed on a matching plan title. Each answer links to supporting household records. Open-ended questions return an explicit unavailable response.

## Tests

```powershell
node --test tests/*.test.mjs
python -m unittest discover -s tests -v
```

The Python suite opens temporary loopback sockets. In a restricted shell, run it with the environment’s approved local-loopback permission.

Read [V1 product scope](/C:/Users/Robot/Relay/docs/v1-product.md), [technical architecture](/C:/Users/Robot/Relay/docs/technical-architecture.md), [technology decisions](/C:/Users/Robot/Relay/docs/technology-decisions.md), and [Relay intelligence architecture](/C:/Users/Robot/Relay/docs/relay-intelligence-architecture.md) before extending the build.

## Development and release checks

```powershell
node --test tests/*.test.mjs
python -m unittest discover -s tests -v
node --check src/app.mjs
python -m py_compile server.py
python tools/package_local.py
```

See [deployment readiness](/C:/Users/Robot/Relay/docs/deployment.md) for the required architecture before a networked release. GitHub Pages cannot host this application because it requires the Python service and database.
