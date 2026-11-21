# Relay V3 development build

Relay is a local family-coordination evaluation build. It preserves an original message, creates a reviewable suggestion, records an approved family plan or revision, retains source history, tracks plan-specific follow-through actions, detects exact schedule overlaps, and answers a bounded set of questions from approved household records.

## Run locally

```powershell
python server.py --port 4173
```

Open [http://127.0.0.1:4173](http://127.0.0.1:4173). New browser sessions start with an empty workspace. Add family names in Household, then paste a message under Add information. The workspace lives in `.relay/households.sqlite3`. Household also offers export and deletion.

To try fictional sample data in a separate workspace, run `python server.py --port 4174 --demo --database .relay/demo.sqlite3`.

If the page says **“Briefing unavailable”**, close any earlier Relay terminal windows, run the command above once, and refresh this exact `127.0.0.1` address. Opening `index.html` directly or through a static preview cannot start the local API.

## Current capabilities

- A source-backed intake → review → approval/rejection journey with immutable plan version history.
- Household-scoped SQLite persistence, hashed session tokens, transactional writes, schema migrations, health endpoint, export, and permanent local reset.
- Plan-specific follow-through actions with household validation and open/done state.
- Deterministic briefing, source duplicate detection, exact schedule collision detection, field-change history, and bounded evidence-linked lookup.
- A persistent household roster, source-line evidence, explicit ambiguity states, and approved preparation and instructions in plan detail and history.
- A seven-day briefing board, version comparison that preserves the active draft, and local adult access with one-time invitations and server-enforced roles.

To try local collaboration, open **Household → Household access** and create an adult invitation. On the same computer, open Relay in a fresh browser profile, choose **Join another household**, and paste the code. The owner can promote, demote, or remove that browser's access. The code expires after 24 hours and works once.

## Capability boundary

Relay uses local browser access. Verified accounts, cross-device sharing, external integrations, email connections, file processing and model inference remain future work. Intake accepts pasted text. The deterministic parser recognizes separate lines such as:

```text
Subject: Winter concert
When: Saturday, December 5, 2026 at 6:30 p.m.
Where: East auditorium
For: Sam
Responsible: Alex
RSVP by: December 1, 2026
Please bring a music folder.
Instructions: Enter through the side door.
```

People must match the plan roster. Relative dates, ambiguous numeric dates, unmarked times and contradictory values stay open for review. The source and the exact evidence lines remain available after approval.

Ask Relay looks up today, tomorrow, the next seven days, preparation, changes, exact-time conflicts, sources awaiting review, and a person listed on a matching plan title. Answers cite the supporting records.

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
