# ADR-0094: Daily Earning at Employment Boundaries

**Status:** Accepted  
**Date:** 2026-09-22  
**Scope:** Partial employment under daily earning

## Decision

Count employment start and end dates as eligible dates for daily earning, subject
to other applicable policy conditions. Earn nothing before employment begins or
after employment ends. The final employment day's portion is available from its
start under [ADR-0091](./0091-start-of-day-daily-entitlement.md).

Use the full applicable leave year's actual length as the denominator, not the
remaining employment duration. For an unchanged 18-day annual entitlement and
100 eligible employment dates in a 365-day leave year, earning is 18 × 100 / 365
days before applicable balance effects and conversion/rounding. Joining late or
having a known departure date must not accelerate earning to the annual total.
For anniversary periods use the actual period boundaries and length, retaining
existing anniversary/leap-date rules.

Do not apply an additional partial-year proration to an annual amount already
multiplied by eligible employment days: this would reduce daily earning twice.
Upfront and monthly policies keep their separately defined joining/leaving rules.
A one-date employment interval includes one eligible day, not zero or two.

Retain [annual availability modes](./0090-annual-entitlement-availability-options.md),
[cumulative precision](./0092-cumulative-daily-entitlement-precision.md),
[entitlement periods](./0042-entitlement-period-basis.md),
[leap-day anniversaries](./0044-leap-day-employment-anniversaries.md) and
[employment-end eligibility](./0049-leave-after-employment-end.md).
Backdated employment corrections still require recalculation and existing
reservation/acknowledgement safeguards; this decision does not silently rewrite history.

## Consequences

- Acceptance: include same-day employment, midyear join/departure, dates outside
  employment, leap-year denominators and no double proration or acceleration.
- Scaffold/shared UI: Leave-specific rules; existing employment inputs suffice.
- Agent context: existing deterministic-date and audit rules suffice.
- Documentation: requirements and tracker reference the daily employment rule.
- ADR impact: additive; accepted upfront/monthly decisions unchanged.
- Planning only; no runtime calculation implemented.
