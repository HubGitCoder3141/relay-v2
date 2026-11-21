---
version: v2
name: Relay
description: A high-density household signal ledger for source-backed coordination.
---

# Relay design system

## Product register

Relay is a household coordination assistant for adults sharing family logistics. It is an operating product rather than a chat surface. The interface shows the family briefing, current plan, review queue, source history, and bounded household lookup. It never represents a suggestion as an approved fact.

## Visual direction

Relay is a household signal ledger: a calm, technical paper field with black rules, fog-grey stock, and a reserved vermilion signal for attention and action. It deliberately abandons the illustrated-home hero and rounded-SaaS-card language. Information is organized in a ruled ledger, not decorative panels: a narrow navigation mast, headline/decision band, quantitative signal strip, and dense paired plan/review rails.

Iowan Old Style/Baskerville-like editorial type carries decisive headings; Aptos/system sans carries compact operational data. Rectangular controls, one-pixel rules, tabular dates, and an explicit task check provide the product's visual grammar. Vermilion communicates unresolved signal, current navigation, and the one decisive pathway; it is never used as soft decoration.

## Layout and responsive behavior

Desktop uses a 1320px ruled composition. The briefing begins with the actual household state and moves directly into the plan plus decision rail; the page has no generic dashboard card grid. At 760px, the mast collapses, counts retain priority, and the two ledger rails stack while preserving reading order. The action band becomes full width and touch targets stay at least 42px.

## Interaction rules

- Original source wording remains visible before approving a plan.
- Pending, approved, and rejected sources use text labels and color.
- A reviewer sees the current confirmed values when a suggestion updates an existing plan.
- Source history is accessible from a plan detail view.
- Destructive local deletion has a confirmation step and export is available first.
- Forms use visible labels, native date/time controls, inline errors, dialog focus restoration, and Escape handling.
- Reduced motion removes transitions.
- Follow-through actions are attached to a plan, assigned to a household member where known, and explicitly toggled open/done. A checkmark is not evidence of an external action.

## Runtime owners

`styles.css` owns tokens and responsive behavior. `src/app.mjs` owns navigation and the shared dialog pattern. `src/intelligence.mjs` owns read-only projections and lookup. `server.py` owns persistent transitions, source access, and household session authorization.
