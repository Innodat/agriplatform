# ADR-0042: Calendar-Year or Employment-Anniversary Entitlement Periods

**Status:** Accepted  
**Date:** 2026-09-14  
**Scope:** Policy entitlement-period basis

## Context

The user approved each policy choosing a calendar year or an employee's
employment-anniversary year. Accrual frequency remains a separate setting.

## Decision

Support calendar-year periods from 1 January through 31 December and
employment-anniversary periods from the employee's anniversary through the day
before the next anniversary. Either basis can use monthly or annual upfront
grants under the [supported schedules](./0024-mvp-accrual-schedules.md).

Use the applicable period in [proration](./0025-per-policy-calendar-day-proration.md)
and [carry-over](./0028-policy-carry-over-options.md); do not infer period basis
from grant frequency. Preserve [versioned policies](./0002-versioned-leave-policies.md)
and [employee work timezone](./0023-employee-work-timezone.md) rules.
The platform's [API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md)
continues to apply.

## Alternatives considered

- Require calendar-year periods for all policies: the user approved an anniversary
  option too.
- Couple period basis to grant frequency: rejected; they are separate settings.

## Consequences

- The specification includes a 1 July employment start with a 1 July–30 June
  anniversary period, contrasted with a calendar-year period.
- Annual grant alignment with period boundaries and leap-day anniversary behavior
  still need deterministic treatment before affected stories pass readiness.
- Scaffold impact: no scaffold change — application-specific entitlement periods.
- Shared-UI impact: none; no reusable implementation is introduced.
- Agent-context impact: existing deterministic calculation and ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: additive period selection; accepted ADRs remain unchanged.
- Planning only; Phase 1 readiness and failing acceptance tests precede implementation.
