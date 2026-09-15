# ADR-0049: Leave Cannot Extend Beyond a Known Employment End Date

**Status:** Accepted  
**Date:** 2026-09-15  
**Scope:** Leave-date eligibility at employment end

## Context

The user approved blocking new submission and final approval when requested dates
extend beyond a known employment end date. Existing affected requests are flagged
with the administrator's explanation for correction or cancellation, without silent
date changes. Leave on the final employment date remains eligible under normal rules.

## Decision

At submission and final approval, reject any request containing a leave date after
the recorded employment end date. Include the last employment date in eligibility,
subject to all other rules. Evaluate dates in the
[employee work timezone](./0023-employee-work-timezone.md).

When an authorized employment end-date change affects an existing request, flag
it for correction or cancellation and show the administrator's explanation.
Preserve its dates and history until an authorized action occurs; do not silently
trim or cancel it. Use existing
[correction and cancellation permissions](./0010-cancel-and-replace-approved-leave.md)
and [explained change controls](./0032-protected-reservations-and-explained-changes.md).
This grants no new correction authority to approvers. Approved-request date changes
continue to require cancellation and replacement rather than in-place editing.

Preserve [immutable history](./0001-immutable-balance-ledger.md) and the platform's
[API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md).

## Alternatives considered

- Allow leave after recorded employment ends: rejected.
- Automatically trim or cancel affected requests: rejected; flag for authorized
  action with an explanation.
- Exclude the last employment date: rejected; it remains eligible under normal rules.

## Consequences

- The specification includes a 30 June employment end with 1 July submission and
  final-approval denial, plus an explained existing-request flag.
- The flag is an eligibility issue, not a new application lifecycle state.
- Scaffold impact: no scaffold change — application-specific eligibility rules.
- Shared-UI impact: none now; eligibility explanations belong in Leave.
- Agent-context impact: existing authorization, audit, and ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: additive employment-date rule; accepted ADRs remain unchanged.
- Planning only; Phase 1 readiness and failing acceptance tests precede implementation.
