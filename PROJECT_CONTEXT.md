# Relay project context

Relay helps adults coordinate household logistics by turning fragmented information into a reviewed current plan with traceable changes. Families with school-age children and multiple caregivers are the proposed first audience. Market adoption and willingness to pay remain unvalidated.

The V3 development build uses a loopback-only Python HTTP server, SQLite, and native browser ES modules. Pasted source text enters an inbox. A bounded parser identifies explicit labels, saves line evidence, flags contradictions, and leaves approval to household reviewers. Approved versions feed the plan, interactive week briefing, and read-only lookup. A person in the plan roster supports name resolution. Separately, household access is issued to adult browser sessions.

Run `python server.py --port 4173` from the repository root. Use the README for synthetic demo and test commands. The GitHub repository remains private.

The directive prohibits external AI requests, model installation, provider credentials, paid services, and unauthorized deployment. Cookie-backed owner, administrator and adult member sessions share a household through expiring one-time invites. Owners can change roles and remove access. A networked pilot requires verified accounts, production operations, and a separate privacy and security review.

Read [the V3 scope and audit](docs/v3-delivery.md) for the active implementation checklist, [SaaS readiness](docs/saas-readiness.md) for the pilot roadmap, and [master-handoff.md](master-handoff.md) for historical research.
