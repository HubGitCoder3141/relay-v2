# Relay UX contract

Relay is an operating interface, not a chat surface. This contract records observable UI behavior; domain rules remain in `server.py` and the technical architecture document.

| Capability | Canonical owner | Contract |
| --- | --- | --- |
| Forms | `src/app.mjs` form handler | Native inputs, visible labels, first invalid field receives focus, inline error is announced, and duplicate submission is disabled while saving. |
| Toast feedback | `notify()` in `src/app.mjs` | A short status message confirms successful local mutations; persistent failures remain next to the action. |
| Dialog | `openPanel()` / `closePanel()` | Review, source, plan, and household tasks use the single accessible dialog; Escape and close restore focus. |
| CRUD service | `/api/*` in `server.py` | Every mutation validates and returns the authoritative household snapshot. Browser state is replaced only by that snapshot. |
| Date/time fields | Native HTML controls | Browser-owned locale picker behavior is accepted for this local English evaluation build. The API validates canonical ISO date and 24-hour time strings. |
| Destructive reset | Household dialog + `/api/reset` | Explicit confirmation appears before permanent local data deletion; export is adjacent. |

Loading starts with an app-owned status message. Empty states explain what will appear and the next real action. The server response is the sole source of mutation success or error; no optimistic household writes occur.
