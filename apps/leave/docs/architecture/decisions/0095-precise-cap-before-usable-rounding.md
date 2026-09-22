# ADR-0095: Apply Daily Cap Before Usable-Minute Rounding

**Status:** Accepted  
**Date:** 2026-09-22  
**Scope:** Fractional daily earning at an accumulated balance cap

## Decision

Apply the accumulated cap to precise calculated entitlement before rounding the
usable amount down to whole minutes. Retain fractions earned below the cap in the
calculation. Permanently exclude only the portion that cannot fit; do not retain
that excluded excess as a hidden balance that reappears after a deduction.

Example: with a 120-minute cap, precise accumulated entitlement of 119.8 minutes
and a new eligible daily portion of 0.5 minutes, accept 0.2 minutes and exclude
0.3 minutes. Accumulated entitlement reaches exactly 120 minutes. The 0.3 minutes
is not recoverable through ordinary later earning. Values are illustrative.

Combine this rule with [cumulative precision](./0092-cumulative-daily-entitlement-precision.md),
[daily cap/resumption](./0093-daily-cap-and-prospective-resumption.md),
[earned-reservation cap treatment](./0037-earned-reservations-count-toward-cap.md)
and [historical cancellation recalculation](./0038-cancellation-accrual-recalculation.md).
Authorized historical corrections can change the reconstructed circumstances;
no-catch-up does not prohibit required correction of erroneous historical inputs.
Do not rewrite recorded transactions or silently revise protected reservations.

## Consequences

- Acceptance: test partial capacity, exact capacity, above-cap existing entitlement,
  preserved fractions below cap and no recovery of excluded fractions after deduction.
- Scaffold/shared UI: Leave calculation; existing explanation patterns suffice.
- Agent context: existing precision, history and deterministic-testing rules suffice.
- Documentation: requirements and tracker updated.
- ADR impact: additive refinement of ADR-0092/0093; accepted records unchanged.
- Planning only; no production arithmetic or ledger schema implemented.
