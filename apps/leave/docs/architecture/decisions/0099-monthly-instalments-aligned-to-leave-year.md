# ADR-0099: Monthly Instalments Aligned to the Leave Year

**Status:** Accepted  
**Date:** 2026-09-22  
**Scope:** Monthly availability for calendar and anniversary leave periods  
**Supersedes in part:** ADR-0045's universal calendar-month timing

## Decision

Divide the employee's leave year into twelve monthly instalment periods aligned
to its start. The policy selects availability at the start or end of each
instalment period. Calendar-year policies continue using ordinary calendar months;
anniversary policies use anniversary-aligned monthly periods.

Example: a leave year from 15 July through 14 July has its first monthly period
15 July–14 August, second 15 August–14 September, and so on. Under an unchanged
18-day annual amount, each of the twelve complete instalments has a nominal
1.5-day portion, subject to existing precision, cap and eligibility rules.

This refines [ADR-0045](./0045-monthly-grant-start-or-end.md). Preserve start-of-day
availability on the selected grant date under
[ADR-0047](./0047-month-end-grant-same-day-availability.md) and cumulative complete
instalment rounding under [ADR-0097](./0097-cumulative-monthly-instalment-rounding.md).
An end-of-instalment grant is usable on that period's final date, not the next day.

Apply partial-employment proration to the applicable aligned instalment period,
not an unrelated calendar month. Existing joining-grant behavior for upfront
monthly policies remains, relative to that instalment's start. Existing final
prorated-grant rounding remains separate from full-instalment cumulative rounding.

Missing matching dates for 29th/30th/31st anniversaries and leap-year transitions
need a deterministic boundary rule next. Do not infer repeated clamping or a new
carry-over expiry rule; expiry arithmetic remains governed separately.

## Consequences

- Acceptance: twelve contiguous instalment periods, 15-July example, calendar-year
  equivalence and start/end availability including the period's final date.
- Scaffold/shared UI: policy labels say start/end of instalment period and show
  employee-specific examples; no shared runtime accrual capability.
- Agent context: existing deterministic-date rules suffice.
- Documentation: product truth, tracker and UX contract updated; older policy
  preview is explicitly pending refresh under the existing accrual follow-up.
- ADR impact: partial supersession of ADR-0045; accepted original unchanged.
- Planning only; no policy records or calculation implementation changed.
