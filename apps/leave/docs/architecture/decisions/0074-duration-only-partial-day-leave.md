# ADR-0074: Duration-Only Partial-Day Leave and Daily Capacity Checks

**Status:** Accepted  
**Date:** 2026-09-15  
**Scope:** Partial-day input, calendar presentation, and request conflicts  
**Supersedes in part:** ADR-0052's exact-interval overlap rule and ADR-0011's label for partial-day colleague entries

## Context and decision

The user selected simpler partial-day requests until an exact-time requirement
arises. Half day selects a date and consumes exactly 50% of that day's scheduled
working hours, without first/second-half selection. Hours selects a date and a
duration in 30-minute increments, without start/end times. An optional note can
describe arrangements agreed with the supervisor. Full-day ranges remain unchanged.

Warn when another submitted, in-approval, or approved request exists for the same
employee, NGO, and date. Allow combined durations within the scheduled hours for
that day, but block totals exceeding them, across leave types and concurrent
submissions. Exclude draft, rejected, withdrawn, and cancelled requests from the
total. Other eligibility and approval rules continue to apply. This replaces only
the exact-interval conflict behavior in
[ADR-0052](./0052-overlaps-and-administrative-corrections.md).

Calendar entries identify dates with leave without inventing time intervals.
Permitted views show Half day or requested hours; colleague views show Part-day
absence without type, notes, or document information. This refines the partial-day
label in [ADR-0011](./0011-colleague-absence-privacy.md), retaining its field privacy
and Unavailable for full days. Deduct only requested duration under
[canonical minute rules](./0003-working-time-in-minutes.md).
Use the platform's [API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md).

## Consequences

- The specification records two two-hour requests on an eight-hour day, full-day
  plus partial-day denial, calendar privacy, and concurrent daily-total checks.
- Exact-time availability is intentionally not provided by partial-day requests;
  employees and supervisors arrange timing.
- Scaffold impact: no scaffold change — application-specific duration semantics.
- Shared-UI impact: generic calendar/input primitives may be reused, with Leave
  conflict rules and privacy transforms in the application.
- Agent-context impact: existing authorization and ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and UX log.
- ADR impact: scoped supersessions; accepted original records remain unchanged.
- Planning only; Phase 1 readiness precedes implementation.
