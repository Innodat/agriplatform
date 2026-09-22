# ADR-0092: Cumulative Daily Entitlement Precision

**Status:** Accepted  
**Date:** 2026-09-21  
**Scope:** Rounding daily earning under ADR-0090/0091

## Decision

Calculate daily earned entitlement cumulatively from the applicable annual amount
and eligible dates. For unchanged entitlement and uninterrupted eligibility:

    earned minutes = annual entitlement minutes × eligible days / leave-year days

Include the current eligible date under
[ADR-0091](./0091-start-of-day-daily-entitlement.md). Use actual leave-year length.
Round the resulting usable earned entitlement down to a whole minute. Preserve
fractional precision in the underlying calculation; never truncate each day's
portion or use yesterday's rounded balance as the input for today's accrual.
Use exact rational or sufficient decimal arithmetic with a defined rounding
boundary, not binary floating-point approximation that can lose a whole minute.

Example: 18 days at an unchanged 480-minute standard day gives 8,640 annual minutes.
After 100 of 365 eligible days, exact earned entitlement is 864,000/365 minutes;
2,367 whole minutes are usable before other applicable balance effects. At 365
eligible days, the result is exactly 8,640 minutes. Fractions contribute to later
whole minutes without requiring daily ledger entries or worker execution.

This is specific to daily earning. Existing final-grant rounding for prorated
upfront/monthly grants remains governed by
[ADR-0026](./0026-prorated-grant-rounding.md). Hourly input increments remain
30 minutes; schedule-based full/half days retain their actual durations.

The simple formula is an example for unchanged inputs. Historical policy or
schedule changes, caps, expiry and reservations still require the deterministic
replay design identified in [ADR-0090](./0090-annual-entitlement-availability-options.md).
Do not sum independently rounded intervals or carry fractional entitlement across
expiry merely because it simplifies arithmetic. Exact interval/bucket treatment
must preserve applicable eligibility and expiry, and remains readiness work.

## Consequences

- Acceptance: verify day-100 and full-year examples, leap-year totals, retained
  fractions across repeated reads, and no dependency on prior rounded results.
- Scaffold/shared UI: application-specific calculation; no shared accrual engine.
- Agent context: existing deterministic-calculation rules suffice.
- Documentation: requirements, tracker and UX updated; daily visual follow-up remains.
- ADR impact: additive precision rule; existing accepted records unchanged.
- Planning only; no runtime implementation or completed calculation readiness.
