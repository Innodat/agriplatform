# ADR-0041: Explicit Standard Day for Variable-Length Schedules

**Status:** Accepted  
**Date:** 2026-09-14  
**Scope:** Entitlement conversions for employees with different-length working days

## Context

The user approved an explicitly configured standard day in the employee's schedule
for entitlement conversions. Actual leave continues to use the working hours
scheduled on the requested date.

## Decision

Include an explicit standard-day duration in employee schedule configuration for
entitlement conversions. Apply it to conversions such as
[carry-over day limits](./0040-schedule-based-carry-over-day-limits.md), even when
individual working days differ in length.

Do not substitute this value for actual date-specific working time when calculating
leave consumption. Full-day leave consumes the scheduled working time on that
date; half-day leave consumes exactly 50% of that time. Preserve existing hourly
increment and schedule rules under
[ADR-0003](./0003-working-time-in-minutes.md), together with effective schedule and
calculation snapshots. Preserve [immutable history](./0001-immutable-balance-ledger.md).
The platform's [API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md)
continues to apply.

## Alternatives considered

- Assume the same duration for every working day: rejected; actual leave follows
  the schedule for the requested date.
- Infer the conversion duration from a particular requested day: the user selected
  an explicit standard-day configuration.

## Consequences

- The specification includes an eight-hour standard day with a six-hour Friday:
  five conversion days equal 40 hours, Friday leave consumes six hours, and a
  half-day Friday consumes three hours.
- Configuration and calculation UI must distinguish the entitlement conversion
  value from the working time used for a particular absence.
- Scaffold impact: no scaffold change — application-specific schedule semantics.
- Shared-UI impact: none now; this configuration belongs in Leave.
- Agent-context impact: existing deterministic calculation and ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: additive resolution of variable-schedule conversion; accepted ADRs
  remain unchanged.
- Planning only; Phase 1 readiness and failing acceptance tests precede implementation.
