---
id: SPEC-kdg-historical-actor-display
status: owner-repaired-composition-planned
companions:
  - ../../../services/access/HISTORICAL-ACTOR-DISPLAY.md
  - ../../../apps/kdg-capture/docs/audit-display-composition.md
  - ../../../apps/kdg-capture/docs/contracts.md
  - ../../../apps/kdg-capture/docs/epics.md
sources: []
---

# Historical actor display for KDG audit

## Why

KDG administrator audit metadata retains durable actor IDs but cannot yet present
permitted names for original capturers and actual modifiers. Identity owns label
resolution; KDG owns current record authorization, composition and presentation.

## Capabilities

- **CAP-1**
  - **intent:** Authorized KDG administrators can identify the actors behind the permitted record's attribution.
  - **success:** HD-1–HD-7 and KDG KC-1–KC-9 prove retained labels, original executor/initiator identity, scoped disclosure, safe dependency failure and current-authority publication.

## Constraints

- Adopted repository-owned contracts and Story 3.1 remain authoritative; API details and acceptance traceability live there.
- Actor existence, employment and membership history confer no current access. KDG selects permitted record actors; Identity owns labels and retention.
- Preserve the repaired private-outcome diagnostic boundary, cancellation ownership and original execution budgets in consuming implementation.
- Preserve all handoff exclusions and concurrent work. Backend and later inert web consumers need separate proof; synthetic checks do not qualify native retention or live authority.

## Non-goals

- General actor directory, event-time names, actor management, UI mounting, database/privilege changes, live activation or full Story 3.1 completion.

## Success signal

The isolated owner HTTP candidate exists, and the KDG combined contract now defines
the selected page/label envelope, bounds, final authorization and publication rules.
The owner cancellation-diagnostic repair now has four actual RED/GREEN regressions
and independent review. Next select the bounded synthetic backend consumer against
KC-1–KC-9. Passing owner suites do not establish unimplemented consuming behavior.

## Assumptions

- The separate audit-details path, label-status union, phase reserves and backend-first delivery are selected planning defaults for consuming Build; they do not activate a runtime surface.

## Deferred qualification

- Native projection/privileges, actual retention, real credential provisioning/rotation and release activation require separate qualification.
- The later inert client must prove account/org/page/session invalidation and generated/runtime response validation before named presentation.
