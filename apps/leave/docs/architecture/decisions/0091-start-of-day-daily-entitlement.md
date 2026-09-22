# ADR-0091: Start-of-Day Daily Entitlement Availability

**Status:** Accepted  
**Date:** 2026-09-21  
**Scope:** Daily availability boundary under ADR-0090

## Decision

For daily earning, include the current eligible calendar day from its start in
the employee's configured work timezone. The day's portion is usable on that date;
it does not require completing the day or waiting for a midnight worker.
Authoritative on-demand calculations determine the applicable local date.

For an unchanged 18-day entitlement and an eligible full 365-day calendar year,
1 January includes one daily portion, 2 January includes two, and 31 December
includes all 365 portions, reaching 18 days before caps, use and other effects.
Use the actual leave-year length, including leap years. These are timing examples,
not new defaults or permission to ignore employment eligibility or policy versions.

This resolves the daily boundary in
[ADR-0090](./0090-annual-entitlement-availability-options.md), consistent with
[effective-date availability](./0022-accrual-effective-date-availability.md) and
[employee work timezone](./0023-employee-work-timezone.md).
Rounding/precision, partial-employment examples, policy transitions and historical
cap/reservation replay still require deterministic definitions before readiness.

## Consequences

- Acceptance: test just before/at local midnight, current-day inclusion, calendar
  and anniversary periods, leap-year length, and worker-independent availability.
- Scaffold/shared UI: domain-specific calculation; no new generic component.
- Agent context: existing date/time and deterministic-testing rules suffice.
- Documentation: requirements and policy UX reflect the daily boundary.
- ADR impact: additive refinement of ADR-0090; accepted originals unchanged.
- Planning only; no code or midnight job implemented.
