# Relay V3 scope and audit

The primary journey is capture → inspect source → edit suggested details → approve or reject → inspect current plan and earlier versions → prepare and follow through. Relay's value hypothesis is that evidence and clear handling of changes reduce the work of coordinating a household. Retain local Python and SQLite for this iteration to protect existing records, keep the build dependency-free, and test that hypothesis before introducing framework or hosting costs.

| V2 finding | V3 response | Remaining work |
|---|---|---|
| Every workspace mixed in fictional plans and two fixed names | Empty start by default, explicit demo flag, scoped persistent roster, and separate browser access with roles and invitations | Person edits, relationships, verified identities and per-record permissions |
| Parser accepted the first matching date or partial name | Whole-line parsing with stored per-field evidence and abstention | Unstructured dates, multiple events, document and image intake |
| Version check was optional, and current values appeared only for a preselected plan | All existing-plan approvals require the previous source ID. Stale reviews preserve the draft and compare old, newly confirmed and draft values before resubmission. | Persist protected drafts across reload and add reviewer attribution |
| Preparation and venue instructions disappeared from structured history | Versioned preparation and instructions, visible details and cited weekly lookup | Deadlines, responsibility acceptance, duration and travel-aware conflicts |
| Mobile mast hid all navigation, and toasts lacked their styling class | Visible responsive tabs, restored feedback, evidence disclosure on mobile and a side-by-side source review on desktop | Assistive-technology walkthrough, broader device testing, visual regression baselines |
| Snapshot sends the entire household, and the browser builds all views from it | Retained for the local workload, with the per-field evidence computed once at intake | Bounded views and load measurement before network deployment |

## Trust and infrastructure

Migration 2 adds source fields and evidence with backward-compatible defaults. Migration 3 adds a normalized unique name per household and restores the two previously available labels in existing households with records. DDL and migration ledger updates share a write transaction. Export includes members, source reports, plans and prior versions. Reset deletes members and all coordination records. The original text and captured extraction are kept when the reviewer corrects a value.

Supported screens are Briefing, Family plan, Inbox, Ask Relay, and the intake, review, plan detail, and household dialogs. Search is bounded to supported questions. Conflict checks require an exact date, time, and named affected person. Source text is untrusted data and the lookup layer has no execution authority. The local session model is insufficient for public access.

## Verification

Run the Node and Python suites from the README. To regenerate the Edge captures, run `node tools/browser_check.mjs` with an existing Playwright install and Edge available. Set `RELAY_PLAYWRIGHT` to the installed Playwright package directory if it is outside this repository. The browser check creates an isolated local test database and captures the primary surfaces at 390 and 1440 pixels. It also checks input validation, review evidence, approval, preparation lookup, persistence after reload and completing a follow-through action.

## Next milestones

1. Evaluate the new comparison flow with contradictory real-world-style notices. Add protected draft recovery across reload and decision attribution.
2. Extend the authorized family context model with stable person IDs, explicit responsibilities, and schedules with durations. Define acceptance and per-record visibility before network sharing.
3. Introduce bounded file processing and identity only once the applicable privacy, retention, and deployment requirements are settled.
4. Evaluate the local flow with synthetic scenarios and prospective adult users. Measure missed obligations, wrong details, stale answers, unnecessary flags, and correction effort before funding a model or integrations.
