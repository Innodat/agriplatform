# ADR-0037: Already-Earned Reserved Entitlement Counts Toward the Cap

**Status:** Accepted  
**Date:** 2026-09-14  
**Scope:** Reservation treatment in accumulated-balance cap measurement

## Context

The user approved already-earned reserved entitlement continuing to count toward
the accumulated-balance cap until final approval consumes it. Reservations against
future accrual remain separate from today's accumulated balance.

## Decision

Include already-earned reserved entitlement in the accumulated balance used for
cap measurement. Reserving it for a pending request does not create cap headroom.
Final approval converts the reservation to consumption, reducing that balance and
creating room for later scheduled accrual. Withdrawing a pending request releases
the reservation without reducing accumulated entitlement or creating headroom.

Future-accrual reservations do not change today's accumulated balance, as clarified
in [ADR-0035](./0035-leave-date-funding-and-booking-horizon.md). Apply
[cap rules](./0033-optional-accumulated-balance-cap.md),
[scheduled resumption without catch-up](./0034-accrual-resumption-after-cap.md),
[final-approval consumption](./0007-required-approval-and-automatic-decisions.md),
and [immutable ledger history](./0001-immutable-balance-ledger.md).
The platform's [API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md)
continues to apply.

## Alternatives considered

- Deduct pending reservations from the cap measurement: rejected; already-earned
  entitlement remains accumulated until consumption.
- Count future accrual as today's accumulated entitlement: rejected; keep those
  funding sources distinct.

## Consequences

- The specification includes pending, final-approval, withdrawal, and future-accrual
  examples for later executable acceptance tests.
- This resolves reservation treatment in cap measurement. Cancellation after
  consumption still follows existing reversal rules and needs cap interaction
  detail before affected stories pass readiness.
- Scaffold impact: no scaffold change — application-specific balance policy.
- Shared-UI impact: none; no reusable implementation is introduced.
- Agent-context impact: existing deterministic calculation and ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: additive resolution of cap measurement; accepted ADRs unchanged.
- Planning only; Phase 1 readiness and failing acceptance tests precede implementation.
