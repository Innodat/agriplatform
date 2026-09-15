# ADR-0027: Missing Accrual Dates Use the Month's Last Valid Day

**Status:** Accepted  
**Date:** 2026-09-14  
**Scope:** Calendar fallback for configured accrual dates

## Context

The user approved using the last valid day of the month when a configured accrual
date does not exist, while keeping the configured date unchanged for future periods.

## Decision

For an accrual occurrence whose configured date is absent from that month or year,
use the last valid day of that month. A monthly grant on the 31st therefore falls
on 30 April or 28/29 February. An annual grant on 29 February falls on 28 February
in non-leap years.

Keep the original configuration: later periods resolve independently from it.
An April fallback to the 30th must not move May's configured 31st grant to the 30th.
Apply the resolved date using [effective-date availability](./0022-accrual-effective-date-availability.md)
and the [employee work timezone](./0023-employee-work-timezone.md).
Preserve [idempotent grants](./0001-immutable-balance-ledger.md) and
[versioned policies](./0002-versioned-leave-policies.md) for the
[supported schedules](./0024-mvp-accrual-schedules.md).
The platform's [API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md)
continues to apply.

## Alternatives considered

- Skip the grant or move it into the following month: the user selected the last
  valid day within the intended month.
- Permanently change the configured date after a fallback: rejected; later periods
  must retain the original schedule.

## Consequences

- The specification includes short-month, leap-year, subsequent-period, and retry
  acceptance examples for later executable tests.
- Scaffold impact: no scaffold change — application-specific scheduling policy.
- Shared-UI impact: none; no reusable implementation is introduced.
- Agent-context impact: existing deterministic calculation and ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: additive calendar clarification; accepted ADRs remain unchanged.
- Planning only; this resolves configured-date fallback, not the full readiness gate.
