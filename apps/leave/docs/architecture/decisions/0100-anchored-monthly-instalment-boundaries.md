# ADR-0100: Anchored Monthly Instalment Boundaries

**Status:** Accepted  
**Date:** 2026-09-22  
**Scope:** Monthly boundaries for anniversary-aligned instalments

## Decision

Calculate every monthly boundary independently from the original anniversary
month/day and its month offset. If the destination month lacks that day, use its
last calendar day for that boundary. Preserve the original day for later months;
do not add a month repeatedly to an already-clamped date.

A 31 January anniversary produces boundaries on 31 January, 28 February (29 in a
leap year), 31 March, 30 April and 31 May. Each instalment ends on the day before
the next starts. The twelve instalments cover the leave year exactly without gaps
or overlaps; the final boundary is the next annual period start. Retain the
original leap-day anniversary and the existing non-leap fallback when resolving
annual starts, rather than permanently replacing it with 28 February.

Policy-selected start/end availability refers to these resolved instalment periods
under [ADR-0099](./0099-monthly-instalments-aligned-to-leave-year.md). Use actual
instalment length for partial-employment proration. Continue applying employee
work timezone and start-of-effective-date availability.

This is a boundary calculation. It does not change the distinct inclusive carry-over
expiry arithmetic in [ADR-0089](./0089-carry-over-month-boundary-expiry.md).
For example, a Jan31-to-Feb28 boundary interval ends Feb27; the separate one-month
carry-over expiry example from Jan31 remains usable through Feb28.

## Consequences

- Acceptance: test original days 29/30/31, February in leap/non-leap years, no drift,
  twelve contiguous intervals and consistency with the next annual start.
- Scaffold/shared UI: Leave-specific date arithmetic and policy-preview examples.
- Agent context: existing deterministic-date rules suffice.
- Documentation: requirements, tracker and UX reference resolved boundaries.
- ADR impact: additive refinement of ADR-0099; accepted originals unchanged.
- Planning only; no runtime implementation or changed employee policy data.
