# ADR-0104: Monthly Partial-Employment Default

**Status:** Accepted  
**Date:** 2026-09-22  
**Complements:** ADR-0025, ADR-0099, ADR-0100 and ADR-0103

## Decision

For new monthly policies, default the partial-employment choice to **Adjust for
time employed**. Keep **Give the full period allowance** as the alternative.
Do not change existing policy selections when applying this default.

Adjustment uses the annual allowance divided by twelve, multiplied by calendar
days employed within the applicable instalment period divided by all calendar
days in that period. Count employment start and end dates inclusively. Use the
leave-year-aligned instalment boundaries, including anniversary periods.

At 18 days per year, a complete instalment is 1.5 days. Employment covering 15 of
a 30-day instalment gives 0.75 days with adjustment, or 1.5 days with the full-period
choice. Show this as an illustrative explanation beside the setting.

Existing start/end availability and joining/leaving correction rules still apply;
this decision does not introduce a new grant date or rounding choice. Daily earning
already accounts for eligible employment dates and does not expose this selector.
Fractional integration across partial instalments and rate changes remains a
separate calculation-readiness decision.

## Impact

- Requirements and UX: record the new-policy default and visible example.
- Scaffold/shared UI: existing field help suffices; no new shared component.
- Agent context: no change needed.
- ADR: complements accepted rules without changing historical selections.
- Verification: 18 / 12 × 15 / 30 = 0.75; full-period option = 1.5 days.
- Planning only; no application implementation or production data changes.
