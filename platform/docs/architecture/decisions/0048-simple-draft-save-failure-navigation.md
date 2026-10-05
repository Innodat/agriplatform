# ADR-0048: Simple Draft Save-Failure Navigation

**Status:** Accepted  
**Date:** 2026-10-04  
**Scope:** Platform autosaved, non-consequential draft editing

## Decision

Keep draft save-failure navigation simple. Close normally flushes pending changes and
waits for bounded save/recovery. If saving cannot be confirmed, show “Your latest changes
may not be saved.” Offer Try again, Keep editing and Close anyway. For context switching,
use Stay and Switch anyway. Do not expose operation IDs, commit uncertainty explanations
or a second technical confirmation to the user. Known failures may use “Your latest
changes were not saved.” Never claim Saved without acknowledgement.

Try again uses safe existing operation recovery. Staying retains local input; fresh
writes remain subject to unresolved-operation and revision safeguards. Leaving abandons
local unsent edits without deleting the draft or promising rollback of an in-flight
save. On return, load current authorized saved state and handle outstanding recovery
internally. Late responses cannot overwrite another context or initiate stale navigation.
Retain scoped recovery references under the owning retention contract; missing/expired
references do not prove rollback. Do not promise unsaved recovery after leaving.

This is shared UX for non-consequential draft preservation, not submission, approval,
payment, deliberate draft discard or other consequential commands. Those retain their
own confirmation and outcome-resolution rules. Authorization, revision, operation
identity and lifecycle protections remain required under ADR-0012/0013/0032/0033.
Applications own draft states and destinations; do not impose a universal draft model.

## Impacts and verification

- Scaffold/shared UI: prove reusable save/status/navigation handling with the first
  consumer, then update owning templates, fixtures and documentation in the same item.
- Acceptance: successful close, failed/unknown save, retry, staying, leaving, lost
  response after commit, late response after context switch and authorized reopening.
  Verify no false Saved feedback, duplicate effects or cross-context disclosure.
- Agent context: apply this UX to draft-preservation stories; keep technical safeguards
  internal and consequential commands distinct.
- Documentation: platform EXPERIENCE and Leave adoption reference this decision.
- ADR: additive platform convention; accepted prior platform ADRs remain unchanged.
- Planning only; readiness and failing acceptance evidence still precede implementation.
