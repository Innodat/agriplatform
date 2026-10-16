# ADR-0142: Monthly Instalments for Partial Assignment Coverage

**Status:** Accepted  
**Date:** 2026-10-15  
**Scope:** Monthly entitlement when an instalment has partial assignment coverage

## Decision

Extend the existing monthly partial-period choice under ADR-0104 to policy-assignment
coverage as well as employment. Eligible dates are the intersection of employment and
applicable assignment coverage; count overlapping/repeated intervals only once.

With adjustment enabled, multiply the nominal instalment by eligible covered calendar
days divided by all calendar days in the actual leave-year-aligned instalment. With Give
the full period allowance, provide at most one nominal instalment for a period with
eligible coverage. No coverage means no instalment. Repeated assignments within one
instalment do not each produce another full portion.

Example: a nominal 1.5-day instalment and 15 covered days in a 30-day period yields
0.75 days with adjustment, or 1.5 days once with full-period allowance. Explain partial
coverage as employment or assignment dates; add no second configuration setting. Retain
the existing default to adjustment, accepted cumulative precision and historical rate/
cap/expiry rules. A configured full-period allowance is not daily gap catch-up earning.

## Consequences and verification

This extends partial-employment scope without changing accepted predecessor records.
ADR-0141's no-coverage/no-duplicate principles remain. Bind exact start/end availability,
cutoff, already-available instalment and correction/replay examples before readiness;
the formula does not introduce a new grant date, automatic clawback or snapshot rewrite.
Preserve assignment-ending and request-impact safeguards under ADR-0137/0128.

Verify 15/30 and no-coverage examples, employment/assignment intersection, repeated and
overlapping intervals without double counting, full-period maximum once, anniversary/
month-end/leap periods, historical rate segments and cumulative fractional precision.
Real API/calculation/writer integration and exact source/test mapping remain required.

Update requirements, spine, written policy help, earning/assignment story obligations and
tracker/handoff. Reuse generic conditional form/help/version/test scaffold and UI patterns;
Leave owns calendar/earning semantics. Existing agent context suffices. Final sizing and
readiness remain open; no code, runtime tests or implementation authorization.
