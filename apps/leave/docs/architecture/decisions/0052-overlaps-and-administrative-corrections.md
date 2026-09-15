# ADR-0052: Prevent Overlaps and Support Authorized Historical Corrections

**Status:** Accepted  
**Date:** 2026-09-15  
**Scope:** Overlapping leave and administrative correction across time

## Context

The user accepted preventing overlapping working-time intervals in the same NGO
and added that an administrator may correct past, current, and future leave to
match what actually happened.

## Decision

For the same employee and NGO, submitted, in-approval, and approved requests block
overlapping working-time intervals, even across leave types. Draft, rejected,
withdrawn, and cancelled requests do not block submission. Adjacent non-overlapping
hourly or half-day requests remain allowed under their schedule rules. Concurrent
submissions must preserve this invariant.

Support authorized administrative corrections for past, current, and future leave.
Preserve actor, reason, original history, and balance effects. This is not a general
overlap bypass or a grant of access based solely on an administrator title.
The exact administrative role assignment remains to be confirmed; existing scoped
on-behalf authorization continues to control access.

Preserve [approved cancellation and replacement](./0010-cancel-and-replace-approved-leave.md),
[immutable balance history](./0001-immutable-balance-ledger.md), and
[backdated-request rules](./0051-backdated-requests-without-cutoff.md). No approval
bypass or in-place rewrite of approved history was authorized by this decision.
The platform's [API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md)
continues to apply.

## Alternatives considered

- Permit overlapping requests for different leave types: rejected.
- Let drafts or rejected/withdrawn/cancelled requests block working intervals:
  rejected; only the specified active states block them.
- Restrict corrections to future leave: the user explicitly includes past and current.

## Consequences

- The specification records overlapping and adjacent intervals, state exclusions,
  concurrent submissions, and auditable administrative corrections for later tests.
- Role assignment for correction remains open; existing permissions are not broadened.
- Scaffold impact: no scaffold change — application-specific request invariants.
- Shared-UI impact: none now; correction and overlap explanations belong in Leave.
- Agent-context impact: existing authorization, audit, and ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: additive overlap/correction scope; accepted ADRs remain unchanged.
- Planning only; Phase 1 readiness and failing acceptance tests precede implementation.
