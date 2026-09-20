# ADR-0089: Carry-Over Month-Boundary Expiry

**Status:** Accepted  
**Date:** 2026-09-20  
**Scope:** Deterministic carry-over expiry arithmetic

## Decision

Resolve the arithmetic left open by [ADR-0085](./0085-period-relative-carry-over-expiry.md).
Starting from the actual new leave-period start, add the configured whole number
of calendar months once to identify the destination year and month. If its matching
day exists, the inclusive last usable date is the day before that date. If the
matching day does not exist, use the destination month's final day directly;
do not subtract another day. Do not calculate through repeated one-month additions.

| Period starts | Months | Inclusive last usable date |
|---|---|---|
| 1 January 2026 | 3 | 31 March 2026 |
| 15 January 2026 | 1 | 14 February 2026 |
| 31 January 2026 | 1 | 28 February 2026 |
| 31 January 2028 | 1 | 29 February 2028 |
| 29 February 2028 | 12 | 28 February 2029 |

The policy editor shows the calculated last usable date. Preserve any existing
earlier expiry: repeated carry-over never extends it. A portion is usable on its
last usable date, but not the following day. Resolve the actual period start under
[ADR-0044](./0044-leap-day-employment-anniversaries.md) before this calculation.

## Consequences

- Delivery must cover these examples, direct multi-month arithmetic, inclusive
  eligibility and preservation of an existing earlier expiry in calculation tests.
- Scaffold/shared-UI impact: none; this is a Leave calculation and preview rule.
- Agent-context impact: existing deterministic-calculation instructions suffice.
- Documentation impact: product truth, tracker, UX and review resolution updated.
- ADR impact: additive refinement of ADR-0085; accepted text remains unchanged.
- Planning only; no runtime implementation or readiness completion.
