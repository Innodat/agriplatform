# ADR-0093: Daily Cap and Prospective Resumption

**Status:** Accepted  
**Date:** 2026-09-22  
**Scope:** Daily earning at an accumulated balance cap

## Decision

Apply the optional accumulated cap to daily earning in effective-date order.
At the start of an eligible day, add only earning that fits. Earning excluded
because of the cap is not automatically recovered when room later opens.
A balance reduction after that day's accrual boundary does not trigger another
grant for that day; normal earning resumes at the next eligible day's start.

Example: Ana starts Monday at her 20-day cap, so Monday adds nothing. An authorized
deduction later Monday creates room. Tuesday's portion becomes available at the
start of Tuesday, subject to remaining capacity. Monday's excluded portion is not
restored. This example concerns a current-effective deduction, not a backdated
correction, which requires historical recalculation.

Preserve existing rules: already-earned pending reservations count toward the cap;
future accrual is not today's accumulated balance. Final approval's consumption
and cancellation recalculation retain their agreed effects. Cancellation must not
manufacture extra entitlement through temporary cap headroom.

Compute the capped result on demand from effective-dated inputs and immutable
actual events. Retain reproducible explanations of excluded earning; no daily
worker or separate daily ledger row is required. Do not approximate the result
by taking the minimum of today's cap and an otherwise uncapped annual formula.
Preserve audit snapshots and correction history rather than rewriting decisions.

This extends [daily availability](./0091-start-of-day-daily-entitlement.md) and
[cumulative precision](./0092-cumulative-daily-entitlement-precision.md), retaining
[cap rules](./0033-optional-accumulated-balance-cap.md),
[no automatic catch-up](./0034-accrual-resumption-after-cap.md),
[earned reservations](./0037-earned-reservations-count-toward-cap.md) and
[cancellation recalculation](./0038-cancellation-accrual-recalculation.md).
Fractional capacity at a cap boundary, changes effective at the same daily boundary,
and exact historical replay representation still require deterministic examples.

## Consequences

- Acceptance: reproduce Monday/Tuesday behavior, no recovery of excluded earning,
  pending-reservation cap treatment and cancellation anti-manipulation outcomes.
- Scaffold/shared UI: domain-specific calculation; existing balance explanations apply.
- Agent context: existing immutable-history and calculation rules suffice.
- Documentation: requirements and implementation tracker reference the rule.
- ADR impact: additive daily refinement; accepted records remain unchanged.
- Planning only; no runtime calculation or scheduled job implemented.
