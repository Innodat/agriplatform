# ADR-0109: Expiry and Rollover Before New Earning

**Status:** Accepted  
**Date:** 2026-09-22  
**Complements:** ADR-0091, ADR-0093 and existing inclusive expiry/carry-over rules

## Decision

At a local date boundary, resolve entitlement expiry before calculating new earning
available on that date. At a leave-year boundary, resolve carry-over and expiry of
prior-period amounts before adding new-period entitlement. Determine cap headroom
from the resulting eligible balance, preserving established reservation/cap rules.
This ordering is fixed, not an administrator setting.

An inclusive expiry date remains usable through that date; the amount becomes
ineligible on the following date. Example: Ana has 20 days, equal to her cap. Two
days expire at the end of 31 March. On 1 April, remove those two days first, then
calculate that day's earning against the resulting 18-day balance. Do not discard
new earning by testing it against the pre-expiry 20-day balance.

Retain existing carry-over limits, expiry dates, earliest-expiry allocation and
protected-request safeguards. Reservations do not extend expiry. This rule does not
restore previously capped-out earning. Later same-day consumption follows the
already-agreed start-of-day earning rule; it cannot retroactively create headroom
for that day's excluded earning.

Apply the same boundary ordering to on-demand calculation, historical replay and
any future derived projection. Automatic earning does not wait for a worker posting
expiry or rollover records; retain existing auditable effect and idempotency rules
without counting a derived effect and its recorded representation twice.

## Impact and verification

- Acceptance: inclusive last expiry date; first ineligible date; cap headroom after
  expiry; year-end carry-over/expiry before new entitlement; repeat-read consistency.
- Scaffold/shared UI: domain-specific ordering; no new shared primitive or control.
- Agent context: existing deterministic calculation guidance suffices.
- Documentation: requirements and implementation tracker synchronized.
- ADR: additive ordering rule; accepted predecessor decisions unchanged.
- Planning only; no runtime implementation or event processing performed.
