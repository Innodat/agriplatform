# ADR-0107: Corrected Balances Preserve Decision Evidence

**Status:** Accepted  
**Date:** 2026-09-22  
**Complements:** ADR-0106 and existing historical-correction safeguards

## Decision

When authorized historical information is corrected, preserve the original approval
and its calculation snapshot. Recalculate the affected balance using the corrected
information without rewriting evidence of what the approver knew. Record the actor,
explanation and consequences of the correction. Apply existing affected-request
safeguards, including renewed acknowledgement where unpaid leave increases; this
does not silently rewrite protected reservations or approve a changed allocation.

Ordinary balance views show the corrected result. The original calculation remains
accessible in request history as **Balance at approval**, distinguished from any
later recalculation. Use the equivalent decision-specific label for other snapshots.
The correction record links the corrected information and resulting effects to the
original evidence so both are explainable. Existing preview/confirmation and fresh
validation rules remain binding.

Example: an approval recorded 10 days available. A later employment-start-date
correction reveals that 9 days should have been available at that point. Retain the
10-day approval snapshot and explain the revised 9-day historical calculation.
The current balance is recalculated with all subsequent events, not simply set to 9.

## Impact and verification

- Acceptance: original approval evidence survives correction; corrected balance
  accounts for subsequent events; actor/reason and affected-request safeguards remain.
- Scaffold/shared UI: existing history/disclosure patterns suffice; no new component.
- Agent context: existing immutability and correction instructions suffice.
- Documentation: requirements, tracker and UX synchronized.
- ADR: additive clarification of ADR-0106; accepted originals unchanged.
- Planning only; no runtime or production data changes.
