# Relay SaaS readiness

The local evaluation build supports separate browser sessions sharing a household by invitation. It exercises role enforcement and concurrent approvals on one loopback server. A hosted pilot requires a separate identity, privacy and operations milestone.

| Area | Current implementation | Before a hosted pilot |
|---|---|---|
| Identity and accounts | Bearer cookies identify local browser sessions. An owner or administrator creates an expiring adult invitation. | Verified adult identity, durable accounts, recovery, session expiry and rotation, sign-out, and an audit trail for membership changes. Add household switching after one account can safely hold multiple memberships. |
| Tenancy and persistence | SQLite write transactions, scoped queries, atomic migrations, and composite keys on source records. | Centralize tenant policy and add production lifecycle tests. Retain SQLite for a single instance if measured load permits. Consider managed PostgreSQL when concurrent worker writes or operational requirements justify it. Evaluate row policies as a second layer, with explicit coverage for privileged workers and backups. [PostgreSQL row security](https://www.postgresql.org/docs/current/ddl-rowsecurity.html) |
| Deployment | Loopback Python HTTP process. GitHub hosts private source code. | Production HTTP server, HTTPS, secure cookies, origin checks, request quotas, deployment rollback and tested configuration. Establish a retention policy and run a security review before opening network access. |
| Files, documents and email | Pasted text with original wording and line evidence. | Scoped private object storage, retention and deletion, file validation and bounded parsing. Start with explicit user-uploaded documents. Email forwarding needs verified addresses, deduplication and abuse controls. |
| Background processing | Intake and review are synchronous. | Add a durable jobs table for parsing or mail when those workflows ship. Require idempotency, retry bounds and a visible failed state. Add separate workers only where workloads justify them. |
| Cross-device sync | Local browser sessions read snapshots. Revisions check the latest source in the write transaction. | Add version-aware refresh and reauthorization across devices before evaluating push. Send only household-scoped updates and recheck authorization on reconnect. |
| Monitoring | Local health response and limited error output. | Collect latency, error rates and queue health without source messages, invite codes or household names. Add incident ownership and alert thresholds. |
| Portability and deletion | Owners can export and reset household content. Removed browser access is denied by the server. | Define household closure, account deletion, retention and backup expiry. Test full deletion and export completeness across all stores and jobs. |
| Backup and recovery | Local database file and JSON export. | Design encrypted backups and perform restore drills. Measure recovery time and acceptable data loss. Validate a restored release before use. |
| Billing | Research only. | Keep one billing owner per household and a server-side entitlement separate from household roles. Keep privacy controls and data export available through billing lifecycle transitions. |

## Billing options under consideration

Stripe Billing exposes subscription lifecycle events and supports verifying their origin. It is a candidate if Relay needs direct control of checkout and subscription operations. Confirm taxes, refunds, eligibility and support obligations before selection. [Stripe subscription webhooks](https://docs.stripe.com/billing/subscriptions/webhooks)

Paddle Billing offers a merchant-of-record model and webhook delivery. It is a candidate if outsourcing merchant-of-record obligations fits Relay's eligibility and unit economics. Verify onboarding and contractual terms before committing. [Paddle Billing](https://developer.paddle.com/migrate/) and [Paddle webhooks](https://developer.paddle.com/webhooks/)

Either path needs authenticated event processing, durable event IDs for deduplication, out-of-order event handling, reconciliation with provider state, and owner-only billing changes. Keep checkout, plan IDs and provider credentials out of the local evaluation build. Authorize provider signup and implementation only after value and willingness to pay are validated.
