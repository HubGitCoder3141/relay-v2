# Relay V1 product specification

Relay helps an adult answer “What changed for our family, and what do we need to do about it?” The initial audience is families coordinating through two or more caregivers. The founder chose family coordination as the product direction. Demand, payment and the advantage over existing assistants still need field research.

## First journey

A caregiver receives a message changing an activity. They paste the message into Relay. The original enters a review queue. The caregiver checks the proposed information against the wording, corrects the date, chooses the affected person and identifies the existing plan if this is a change. Approval creates a current plan or a revision. Rejection closes the suggestion without changing the plan. The family briefing draws from these records and the assistant answers supported questions with access to the underlying sources.

## Screens and decisions

| Surface | Job | Trust requirement |
| --- | --- | --- |
| Briefing | Find the next important event, decision or possible collision. | Pending information must be distinguishable from approved plans. |
| Intake and review | Capture the original wording and resolve what it means. | Verify fields and link a revision to the correct plan before approval. |
| Family plan | See who is affected and open a source or earlier version. | Retain the source behind each version. A recorded plan does not establish real-world completion. |
| Ask Relay | Retrieve relevant household records for supported questions. | Unsupported questions need a clear capability boundary. |
| Household data | Inspect the people in the example, export records and clear the local workspace. | Authorize against the session on the server. |

## Scope for this phase

Use synthetic family data on a single computer. Accept pasted email or message text. Use explicit structured fields and deterministic checks where available. Defer open-ended interpretation, OCR, file processing and actions in other services. Source text is untrusted data. One person can evaluate how a household plan would change before multi-adult invitations or production identity are introduced.

## Success criteria

Reviewing a change should require less effort than rereading both messages and maintaining a separate calendar. A user should be able to identify the previous plan, explain why the new one is current, and discover a scheduling collision. The first family interviews should measure corrections, missed changes, time saved and actual participation by the second adult. No field results exist yet.
