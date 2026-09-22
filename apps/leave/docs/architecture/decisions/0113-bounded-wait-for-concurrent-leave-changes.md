# ADR-0113: Bounded Wait for Concurrent Leave Changes

**Status:** Accepted  
**Date:** 2026-09-22  
**Complements:** Existing employee coordination, operation identity and confirmation safeguards

## Decision

When another operation holds the employee/NGO coordination lock, wait briefly within
a bounded timeout. After acquiring coordination, load and validate the updated inputs
before proceeding. Do not calculate from stale pre-wait mutable state.

If coordination cannot be obtained within the bound, end the attempt without its
business effects and preserve the user's form. Show: **Another change is being
completed for this employee. Please try again.** Do not leave an indefinite spinner
or expose database locking details. Set and test the concrete timeout during the
affected implementation story; no numerical timeout is established by this decision.

Retry through the existing duplicate-safe operation contract. A retry must not create
a second business effect. If prior changes alter consequential reviewed information,
show the updated result and obtain confirmation under ADR-0112. Follow the existing
operation-identity rules when changed input becomes a genuinely new operation.

Use the busy response only when the attempted change is known not to have committed.
An uncertain network outcome still requires the existing operation-status resolution;
do not misrepresent it as a definite failed attempt or blindly create another action.
Release coordination on transaction completion or rollback, never across human review.

## Impact and verification

- Acceptance: brief contention proceeds using fresh inputs; timeout has no business
  effects and retains form values; subsequent retry is duplicate-safe; changed
  results require confirmation; uncertain outcomes retain their recovery flow.
- Scaffold/shared UI: reuse existing error/form and operation-recovery patterns;
  no new shared component or administrator setting.
- Agent context: existing transaction and idempotency guidance suffices.
- Documentation: requirements, tracker and UX synchronized.
- ADR: additive; accepted predecessors unchanged.
- Planning only; no runtime locking, timeouts or retry code implemented.
