# ADR-0144: Monthly Availability After Assignment Coverage Ends

**Status:** Accepted  
**Date:** 2026-10-15  
**Scope:** Monthly covered portion with later scheduled availability

## Decision

Preserve the calculated portion for covered dates when assignment coverage ends before
the monthly instalment's scheduled availability. Keep the original availability date;
do not accelerate it to assignment ending or discard the portion solely because coverage
has ended. Earn nothing for uncovered dates. This clarifies the cutoff contract left open
by ADR-0137/0141/0142, separating covered dates from availability timing.

Example: 1–15 April coverage produces a 0.75-day adjusted portion under a month-end
policy. It becomes available on 30 April, not 15 April. No earning for 16–30 April is
implied. Use actual aligned instalment boundaries, not universal calendar-month assumptions.

Retained entitlement does not independently authorize a new request outside assignment
coverage. Preserve prior portions/provenance/expiry, current authority and existing-request
impact review. Assignment ending is not employment departure; other factual correction/
employment/proration rules remain under their own contracts. No worker-posted earning.

## Consequences and verification

Bind coverage and scheduled-availability references, governing policy/version, historical
rate/cap/expiry/cumulative precision, period-boundary interactions and actual request
consumer behavior. Show pending scheduled availability truthfully rather than counting it
as today's usable balance. Existing expiry/leave-date funding rules still apply.

Test the April example before/on 30 April, aligned anniversary periods, zero coverage,
no accelerated or lost covered portion, no uncovered earning, no duplicate actual/derived
amount and no new-request authority merely from retained balance. Existing readers/writers
and actual E5/E6 consumers integrate before affected activation. Exact tests, final sizing
and readiness remain open; no runtime tests executed here.

Update requirements, spine, written calculation explanation, affected E3 story contracts
and tracker/handoff. Reuse typed effective/usable-date/review/status scaffold/UI patterns;
Leave owns earning semantics. Existing agent context suffices; accepted predecessors
unchanged. No code or implementation/readiness authorization.
