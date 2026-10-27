---
id: SPEC-kdg-historical-actor-display
status: ready-for-isolated-synthetic-owner
companions:
  - ../../../services/access/HISTORICAL-ACTOR-DISPLAY.md
  - ../../../apps/kdg-capture/docs/contracts.md
  - ../../../apps/kdg-capture/docs/epics.md
sources: []
---

# Historical actor display for KDG audit

## Why

KDG administrator audit metadata retains durable actor IDs but cannot yet present
permitted names for original capturers and actual modifiers. Identity owns the
missing display contract; current-account and assignment discovery cannot supply it.

## Capabilities

- **CAP-1**
  - **intent:** Authorized KDG administrators can identify the actors behind the permitted record's attribution.
  - **success:** Owner/consumer cases HD-1–HD-7 in the adopted Identity contract prove retained labels, original executor/initiator identity, scoped disclosure and safe lookup failure.

## Constraints

- Repository-owned contracts and Story 3.1 remain authoritative; wire details and acceptance traceability live in the adopted owner contract.
- Actor existence, employment and membership history confer no current access; KDG authorizes and selects actors, Identity owns labels and retention.
- Preserve every current handoff exclusion, concurrent work and prior evidence. The selected implementation is an isolated synthetic owner candidate; native changes, active app wiring and KDG composition remain gated.

## Non-goals

- General actor directory, event-time name snapshots, actor management, UI mounting, database changes, real authority qualification or full Story 3.1 completion.

## Success signal

The owner contract fixes label, caller/selection, wire, failure and execution
semantics. The selected owner candidate must observe HTTP acceptance RED, then prove
HD-1–HD-5 and owner HD-7 without activating a service. HD-6 and consuming HD-7 remain
later work. This readiness pass executes documentation checks only.

## Deferred qualification

- Native projection migration/privileges and actual retention need separately scoped database proof; real credential provisioning/rotation and runtime activation remain outside this slice.
- KDG composition still needs a complete aggregate DTO/byte bound, current authorization and session/publication proof before named presentation.
