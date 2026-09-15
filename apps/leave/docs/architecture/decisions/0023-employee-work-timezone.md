# ADR-0023: Employee Work Timezone Defines Leave Day Boundaries

**Status:** Accepted  
**Date:** 2026-09-14  
**Scope:** Timezone for leave dates, accrual, and expiry

## Context

The user approved using the employee's configured work timezone for leave dates,
accrual, and expiry. A viewer or approver travelling overseas must receive the
same entitlement outcome.

## Decision

Define leave dates and accrual/expiry day boundaries in the employee's configured
work timezone. Do not derive these boundaries from the viewer's or approver's
timezone. Viewing or approving the same request from another timezone must not
change its leave dates, calculated duration, or entitlement outcome.

Apply [start-of-effective-date accrual](./0022-accrual-effective-date-availability.md)
and [inclusive expiry](./0021-inclusive-entitlement-expiry-date.md) in that work
timezone within [date-by-date projection](./0019-date-by-date-future-balance.md).
Preserve existing [schedule and calculation snapshots](./0003-working-time-in-minutes.md)
and [historical policy rules](./0002-versioned-leave-policies.md).
Implementation follows the platform's
[API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md).

## Alternatives considered

- Use the viewer's or approver's timezone: rejected because entitlement outcomes
  would vary with who opens the request or where they are located.
- Use one fixed global timezone for business dates: the user selected each
  employee's configured work timezone.

## Consequences

- The specification includes an overseas-approver acceptance example for later
  executable tests of dates, accrual, and expiry.
- Changes to an employee's work timezone and daylight-saving schedule calculations
  still need deterministic treatment before affected stories pass readiness;
  this decision does not authorize rewriting historical calculations.
- Scaffold impact: no scaffold change — application-specific calculation policy.
- Shared-UI impact: none; no reusable implementation is introduced.
- Agent-context impact: existing deterministic calculation and ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: additive timezone clarification; accepted ADRs remain unchanged.
- Planning only; Phase 1 readiness and failing acceptance tests precede implementation.
