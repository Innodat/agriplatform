# ADR-0043: Annual Upfront Grants Align with Entitlement-Period Start

**Status:** Accepted  
**Date:** 2026-09-14  
**Scope:** Annual upfront grant timing  
**Supersedes in part:** ADR-0024's freely configured annual grant date

## Context

The user approved replacing a freely configured annual grant date with grants at
the start of the entitlement period. A mid-calendar-year joiner receives a grant
on their employment start date using the policy's agreed proration rule.

## Decision

For annual upfront policies, grant on the first day of each entitlement period:
1 January for calendar-year periods and the employee's anniversary for
employment-anniversary periods. For employment beginning partway through a
calendar-year period, issue a joining grant effective on the employment start date,
using the configured no-proration or calendar-day-proration rule and grant rounding.

This replaces only the freely configured annual date in
[ADR-0024](./0024-mvp-accrual-schedules.md). Its monthly and manual-only choices remain.
Use [period definitions](./0042-entitlement-period-basis.md),
[proration](./0025-per-policy-calendar-day-proration.md),
[rounding](./0026-prorated-grant-rounding.md), and
[effective-date availability](./0022-accrual-effective-date-availability.md).
Preserve [versioned policies](./0002-versioned-leave-policies.md) and
[idempotent ledger entries](./0001-immutable-balance-ledger.md).
The platform's [API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md)
continues to apply.

## Alternatives considered

- Retain an independently configured annual date: superseded by period-start grants.
- Delay a mid-year joiner's initial grant until January: the user approved an
  employment-start grant using the chosen proration rule.

## Consequences

- The specification includes calendar-year, July joining, anniversary-year, and
  retry examples for later executable tests.
- Annual-date configuration follows period basis rather than an independent field.
- Leap-day anniversary boundaries still require definition before affected stories
  pass readiness. Historical configured-date examples remain in accepted ADRs.
- Scaffold impact: no scaffold change — application-specific entitlement policy.
- Shared-UI impact: none now; policy configuration stays in Leave.
- Agent-context impact: existing deterministic calculation and ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: scoped supersession of ADR-0024; accepted originals remain unchanged.
- Planning only; Phase 1 readiness and failing acceptance tests precede implementation.
