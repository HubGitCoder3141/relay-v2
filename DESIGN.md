---
version: v3
name: Relay
description: Modern Family Home, a shared space for household plans and decisions.
---

# Relay design system

## Product register

Relay is a household coordination assistant for adults sharing family logistics. It is an operating product rather than a chat surface. The interface shows the family briefing, current plan, review queue, source history, and bounded household lookup. It never represents a suggestion as an approved fact.

## Visual direction

Modern Family Home sets the identity and keeps the first view welcoming through real dates, people and plans. A Contemporary Family Journal would give the source history more character, but chronology alone would bury today's schedule. A Premium Family Command Center would be efficient for high volumes, but uniform panels and metrics would shift attention away from the family. Relay uses Home for arrival and people, Journal for the dated plan and history, and the more structured approach for source review and access.

The supplied references informed the contrast between deep and soft surfaces, the rounded date controls, and the visible presence of people. Relay expresses those ideas through forest and clay arrival panels, a buttery date marker, and color-coded initials generated from household names. Plum identifies Ask Relay. The palette includes paper `#f5eee2`, surface `#fffaef`, forest `#233d34`, clay `#f1c3ad`, sage `#e1eadb`, butter `#f2d681`, and plum `#49334d`. Palatino and Georgia provide editorial headings. Aptos and platform sans-serif support forms and dates. Color reinforces visible labels and controls.

## Layout and responsive behavior

Desktop uses a 1260px composition. The briefing begins with the date and people, then places the week and the review and preparation sections next to one another. At 760px, navigation moves to its own row, sections stack, and the evidence breakdown starts collapsed. Timeline rows keep the person's name at phone widths. Review places the source and decision side by side at larger widths and stacks them at narrower widths.

Date buttons show the plan count in text and use a visible pressed state. Selecting a date filters the agenda and retains keyboard focus. Selecting a person opens their filtered plan timeline. The preparation section uses confirmed plans for the visible forward week and opens the original plan detail. Reconciliation compares previous, confirmed and draft values in reading order, using three columns on larger screens and a stack on phones.

## Interaction rules

Motion follows the change. Week navigation moves the date strip and agenda in the chosen direction. Date and person filters settle only their changed results. New routes introduce the heading, and confirmed actions draw a check beside the status message. These effects run once for roughly 200–320 ms. Reduced motion keeps focus, selection and confirmation cues with immediate updates.

- Original source wording remains visible before approving a plan.
- Pending, approved, and rejected sources use text labels and color.
- A reviewer sees the current confirmed values when a suggestion updates an existing plan.
- Source history is accessible from a plan detail view.
- Destructive local deletion has a confirmation step and export is available first.
- Forms use visible labels, native date/time controls, inline errors, dialog focus restoration, and Escape handling.
- Reduced motion removes transitions.
- Follow-through actions can stand alone or attach to a plan. The Actions view uses labeled date groups with a single ruled column on phones, followed by a disclosure for completed work. The same row also appears on the briefing and in plan detail. Keep the title and check control separate for editing and completion. A checkmark records the family's update.

## Runtime owners

`styles.css` owns tokens and responsive behavior. `src/app.mjs` owns navigation and the shared dialog pattern. `src/intelligence.mjs` owns read-only projections and lookup. `server.py` owns persistent transitions, source access, and household session authorization.
