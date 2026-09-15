# ADR-0003: Canonical Working Time in Minutes

**Status:** Accepted  
**Date:** 2026-09-01  
**Scope:** Leave duration and balance consumption

## Context

Employees may have different schedules, breaks, timezones, working days, and hours
per day. The product supports full-day, half-day, and hourly leave. A global
days-to-hours conversion would produce incorrect results when schedules differ or
change.

## Decision

Store calculated consumption canonically in minutes, together with the effective
schedule, calendar, timezone, and policy-version snapshot. Hourly requests use
30-minute increments. A half day consumes exactly 50% of that employee's configured
scheduled hours for the selected day. UI and reports convert minutes to the policy's
preferred display unit.

## Alternatives considered

- Store fractional days only
- Assume every workday is eight hours
- Recalculate historical duration from the current schedule

## Consequences

- Non-standard schedules and multi-country calendars are supported consistently.
- Rounding and display conversion must be policy-defined and tested.
- Submitted calculations do not change when schedules or holidays are later edited.
- Timezone and effective-date test coverage is required.

