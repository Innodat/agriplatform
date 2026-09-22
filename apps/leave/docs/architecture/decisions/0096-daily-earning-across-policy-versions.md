# ADR-0096: Daily Earning Across Policy Versions

**Status:** Accepted  
**Date:** 2026-09-22  
**Scope:** Prospective annual-entitlement changes in daily policies

## Decision

Calculate each eligible date using the policy annual-entitlement rate effective
on that date. Preserve entitlement already earned under earlier versions. A new
policy version must not silently apply its rate to earlier dates.

Example: annual entitlement rises from 18 to 24 days effective 1 July. Eligible
dates before 1 July use the 18-day annual rate; 1 July and later dates use the
24-day rate. For an unchanged 365-day calendar period with full-year employment
and constant standard-day conversion, the uncapped earned amount is
18 × 181 / 365 + 24 × 184 / 365 days, before usable-minute rounding.
The denominator remains the full applicable leave-year length, not the length of
each policy segment. Rate changes do not themselves start a new entitlement period.

Keep fractional precision across the applicable earning segments; combine before
whole-minute usability rounding. Apply cap/expiry and other balance events in
historical order. Segmentation must not erase excluded accrual or revive expired
entitlement. The simple example assumes no such intervening effects.

This implements [effective-dated policies](./0002-versioned-leave-policies.md) for
[daily earning](./0090-annual-entitlement-availability-options.md) with
[cumulative precision](./0092-cumulative-daily-entitlement-precision.md).
Individual recurring employee overrides remain restricted to leave-period
boundaries under [ADR-0083](./0083-recurring-entitlement-period-boundaries.md);
one-off adjustments remain the means of immediate individual balance changes.

Existing requests retain their calculation snapshots. Changes affecting protected
reservations or unpaid amounts use existing impact review and acknowledgement
safeguards. Deliberate backdated correction is separate from prospective publication.
This decision does not settle a change of earning mode or leave-period basis.

## Consequences

- Acceptance: verify the effective date, two-rate calculation, no segment rounding
  loss, no retroactive rate replacement and protected request handling.
- Scaffold/shared UI: Leave-specific policy calculation; existing version review applies.
- Agent context: existing effective-date and history rules suffice.
- Documentation: requirements and tracker synchronized.
- ADR impact: additive refinement; accepted records unchanged.
- Planning only; no policy data or calculation code changed.
