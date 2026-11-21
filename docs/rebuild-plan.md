# Relay prototype reconstruction — 2026-11-21

## Product understanding

Relay helps school-age families keep a dependable record of what a notice asks, who will handle it, and what happened. The commitment focus is a provisional research direction. This prototype tests that workflow; it does not claim AI extraction, shared accounts, notifications, or verified completion.

## Experience

- **Today:** decisions awaiting a clear yes and accepted work due soon.
- **Plan:** the complete, filterable record of family commitments.
- **Changes:** a readable chronology of plan revisions, acceptance, and completion.
- **Detail:** each item keeps the current notice, person, due date, next action, completion note, and prior wording together.
- **Capture:** manually enter a notice and its action. Changing the date, person, or notice reopens acceptance.

The primary journey is notice → named person → recorded acceptance → recorded completion. A revised plan returns to acceptance and preserves its history. All records remain in one browser.

## Design direction

The visual reference is a family correspondence folder, translated into a crisp modern tool. Ink navy `#1C3044`, paper `#F7F8F6`, white `#FFFFFF`, vivid blue `#315FC2`, marigold `#D59B4D`, and pine `#287466` give each state a purpose. A narrow colored thread alongside each commitment, and a three-step detail rail, make source → responsibility → outcome the recognizable signature. Display headings use Georgia with restrained size; body and controls use system sans. The serif gives the family voice warmth while the operating UI stays precise.

## Implementation

Replace the current presentation and interaction layer with a new semantic HTML shell, responsive CSS system, and modular browser application. Retain the small tested commitment state module, since its transitions and history match the product hypothesis. Migrate the earlier browser storage key on first load so locally entered records survive. Use no external dependencies or network services. Add tests for new view projections and migration behavior, then run browser flows at desktop and phone widths.

## Boundaries

The sample household is clearly marked as an example. A recorded yes or completion is a manual local note, never a claim that another caregiver saw or confirmed it. No backend, credentials, or infrastructure exist to migrate.
