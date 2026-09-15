# ADR-0032: Protect Reservations and Explain Increased Unpaid Amounts

**Status:** Accepted  
**Date:** 2026-09-14  
**Scope:** Reservation priority and acknowledgement after authorized funding changes

## Context

The user selected protection of existing reservations rather than displacement by
new requests with earlier leave dates. They also confirmed that renewed employee
acknowledgement should include an explanation from the actor responsible for the
correction, authorized change, or employment termination.

## Decision

New requests use remaining eligible entitlement; they cannot take entitlement
allocated to existing reservations. Any shortfall belongs to the new request,
even if its leave dates precede those of an existing request.

Include expected expiry, carry-over limits, and accrual in original projections.
Routine passage across a period boundary alone must not unexpectedly increase
unpaid amounts. Existing reservations still do not extend entitlement validity
under [ADR-0031](./0031-pending-request-rollover-shortfalls.md).

When an authorized balance correction, entitlement change, or employment update
increases a pending request's unpaid amount, require an employee-visible reason
from the actor making the change. Show the actor, explanation, previous amount,
and revised amount. Require acknowledgement of the revised amount before final
approval. Preserve the explanation, acknowledgement, and prior decisions in audit
history. Scheduled reconciliation carries through the underlying change's reason.
Acknowledgement does not substitute for required approval or authorize a balance
override. This decision concerns pending requests, not reopening approved leave.

Preserve [immutable ledger history](./0001-immutable-balance-ledger.md),
[required approvals](./0007-required-approval-and-automatic-decisions.md), and
[date-by-date availability](./0019-date-by-date-future-balance.md). Business-data
authorization follows the platform's
[API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md).

## Alternatives considered

- Give new earlier-dated requests priority over existing reservations: rejected
  by the user in favor of protection of existing allocations.
- Ask for acknowledgement without an explanation: rejected; the employee needs
  attribution, reason, and the exact change in unpaid amount.

## Consequences

- The specification includes competing-request and explained-correction examples
  for later acceptance tests, including final-approval acknowledgement gating.
- UI and API must tie acknowledgement to the revised amount, preserving history.
- Scaffold impact: no scaffold change — application-specific reservation behavior.
- Shared-UI impact: none now; request warnings and explanations belong in Leave.
- Agent-context impact: existing authorization, audit, and ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: additive priority and acknowledgement decision; accepted ADRs unchanged.
- Planning only; Phase 1 readiness and failing acceptance tests precede implementation.
