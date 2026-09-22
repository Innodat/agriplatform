# ADR-0105: Monthly Precision Across Partial Periods and Rate Changes

**Status:** Accepted  
**Date:** 2026-09-22  
**Extends:** ADR-0097 and ADR-0103  
**Supersedes in part:** ADR-0097 treatment of partial monthly portions as separately rounded grants

## Decision

Within a leave year, maintain full precision across related monthly entitlement
portions, including partial employment periods and changes in annual allowance.
Each portion uses its applicable effective-dated annual allowance and the approved
employment-day ratio (or full-period choice). Rate changes retain ADR-0101 timing.
Do not reset earned fractional precision when the annual allowance changes.
Floor final usable entitlement to whole minutes; never independently truncate each
monthly portion. In an uncapped example, exact portions of 712.5 and 952.5 minutes
give 712 usable minutes initially and 1,665 cumulatively, a further 953 minutes.
An exact partial portion of 240.5 followed by 481 gives 721 usable minutes, with
0.5 retained in the precise calculation rather than discarded.

Replay entitlement and balance events in effective order. Preserve earned fractions
allowed by the cap, but discard amounts excluded by it: fractions are not a route
to recover capped-out entitlement. Never compute a future instalment by subtracting
actual grants, reservations or consumed balance from cumulative nominal entitlement.
Consumption, expiry and cap effects remain separately governed historical events.
A standalone grant still follows ADR-0103; a related monthly partial portion is
part of the cumulative calculation, not a standalone grant for rounding purposes.

This adds no user setting and does not change request increments, availability dates,
existing correction safeguards or year-end carry-over policy. Historical snapshots
remain immutable. This decision does not authorize cross-year fractional carry-over.

## Impact and verification

- Requirements/tracker: close partial-period and changed-rate precision integration.
- Acceptance: exact cumulative examples, repeated reads, changed rates, partial
  periods, and no recovery of cap exclusions or consumed leave.
- Scaffold/shared UI: Leave-specific calculation; no new control or shared component.
- Agent context: existing deterministic calculation guidance suffices.
- Documentation/ADR: current requirements link here; accepted predecessors unchanged.
- Planning only; no runtime implementation or historical balance rewrites.
