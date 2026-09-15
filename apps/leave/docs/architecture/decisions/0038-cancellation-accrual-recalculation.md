# ADR-0038: Recalculate Accrual Enabled by Cancelled Approved Leave

**Status:** Accepted  
**Date:** 2026-09-14  
**Scope:** Cancellation of approved leave that affected capped accrual

## Context

The user identified a cap-manipulation risk: approved future leave creates room
for accrual, which may remain after cancellation even if restoration is capped.
They approved recalculating affected accrual, presenting the resulting balance,
and referring spent-entitlement deficits for authorized review.

## Decision

On approved cancellation, calculate what would have accrued had the cancelled
request never consumed entitlement, preserving other actual leave and transactions.
Restore the cancelled consumption and reverse only the extra accrual it enabled.
Use new auditable correction entries; do not rewrite history. Preserve original
entitlement expiry dates.

Before cancellation, show restored entitlement, extra-accrual reversal, applicable
expiry effects, and the resulting balance. Apply
[explanation and renewed acknowledgement](./0032-protected-reservations-and-explained-changes.md)
when the correction affects other pending requests' unpaid amounts. If the extra
entitlement has already been spent, flag the resulting deficit for authorized
review rather than silently converting previously approved leave to unpaid leave.
The deficit review is not a new cancellation approval gate.

Preserve [immutable ledger history](./0001-immutable-balance-ledger.md),
[historical policy versions](./0002-versioned-leave-policies.md),
[cancellation rights](./0010-cancel-and-replace-approved-leave.md), and
[cap rules](./0033-optional-accumulated-balance-cap.md). Implement within the
platform's [API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md).

## Alternatives considered

- Restore everything without recalculation: retains accrual enabled by a cancelled
  booking and may exceed the cap.
- Cap restoration alone: still retains extra accrual if other leave has created
  room before cancellation.
- Rewrite past ledger entries or silently make approved leave unpaid: rejected;
  use auditable corrections and authorized deficit review.

## Consequences

- The specification records the 13 + 5 restored - 2 extra accrual = 16 example,
  retaining actual leave and testing retry-safe correction effects later.
- Implementation must identify the affected accrual and preserve historical
  calculation inputs; chronology and concurrent corrections need deterministic
  acceptance coverage before the affected story passes readiness.
- Earlier conversational restoration-cap and work-related-exception proposals
  were not accepted rules; this decision adopts recalculation instead.
- Scaffold impact: no scaffold change — application-specific balance reconciliation.
- Shared-UI impact: keep the cancellation breakdown in Leave; no shared component now.
- Agent-context impact: existing characterization, audit, and ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: additive cancellation detail; accepted ADRs remain unchanged.
- Planning only; Phase 1 readiness and failing acceptance tests precede implementation.
