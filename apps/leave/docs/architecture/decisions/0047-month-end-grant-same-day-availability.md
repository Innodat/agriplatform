# ADR-0047: Month-End Grants Are Usable on Their Grant Date

**Status:** Accepted  
**Date:** 2026-09-14  
**Scope:** Availability of monthly end-of-month accrual

## Context

The user selected availability from the start of the month-end grant date, keeping
the existing effective-date rule rather than waiting until the following month.

## Decision

Make month-end grants available from the start of their grant date in the employee's
configured work timezone. A grant dated 30 April may fund eligible 30 April leave;
it cannot fund earlier leave and need not wait until 1 May to become available.

This confirms [effective-date availability](./0022-accrual-effective-date-availability.md)
for [month-end schedules](./0045-monthly-grant-start-or-end.md), using the
[employee work timezone](./0023-employee-work-timezone.md). Existing cap, expiry,
reservation, and eligibility rules still apply. Preserve
[idempotent ledger history](./0001-immutable-balance-ledger.md) and the platform's
[API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md).

## Alternatives considered

- Make month-end accrual available only on the following month's first day: the
  user selected same-date availability consistent with other effective grants.

## Consequences

- The specification includes a 30 April allowed/29 April denied example and
  explicitly excludes automatic deferral to 1 May.
- Scaffold impact: no scaffold change — application-specific availability policy.
- Shared-UI impact: none; no reusable implementation is introduced.
- Agent-context impact: existing deterministic calculation and ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: additive clarification; accepted ADRs remain unchanged.
- Planning only; Phase 1 readiness and failing acceptance tests precede implementation.
