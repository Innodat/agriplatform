# ADR-0098: Availability-Method Changes at Leave-Period Boundaries

**Status:** Accepted  
**Date:** 2026-09-22  
**Scope:** MVP transitions between daily, monthly and upfront availability

## Decision

Switch an employee between daily earning, monthly instalments and upfront
availability only at the start of their next leave period. Complete the current
period under its existing method; apply the new method from the next boundary.
Use the employee's applicable calendar-year or anniversary period, not a universal
1 January date. Do not introduce midperiod conversion or remainder-grant rules.

Preserve carry-over, protected reservations, submitted snapshots and impact-review
safeguards. Existing future requests affected by the planned switch require the
existing review/acknowledgement treatment rather than silent funding changes.
A common policy change may consequently have different effective boundaries for
employees with different anniversary periods; preview those dates explicitly.

This restriction concerns the availability method. A prospective change in the
annual amount within a daily policy still follows
[ADR-0096](./0096-daily-earning-across-policy-versions.md).
Individual recurring overrides retain their separate boundary rule under
[ADR-0083](./0083-recurring-entitlement-period-boundaries.md).
Follow [availability modes](./0090-annual-entitlement-availability-options.md) and
[leave periods](./0042-entitlement-period-basis.md).
Changes of leave-period basis and transitions to/from manual-only or untracked
balance policies remain separate decisions, not implicitly authorized here.

## Consequences

- Acceptance: calendar and anniversary method changes, no midperiod switch,
  retained current-period rules and reviewed effects on existing future requests.
- Scaffold/shared UI: Leave policy effective-date validation and impact preview.
- Agent context: existing versioning/history rules suffice.
- Documentation: requirements, tracker and UX contract updated.
- ADR impact: additive restriction on method changes; accepted records unchanged.
- Planning only; no actual policy assignment or calculation changed.
