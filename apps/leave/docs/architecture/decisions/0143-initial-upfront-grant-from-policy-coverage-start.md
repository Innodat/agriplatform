# ADR-0143: Initial Upfront Grant from Policy Coverage Start

**Status:** Accepted  
**Date:** 2026-10-15  
**Scope:** First upfront entitlement when initial policy assignment starts midyear

## Decision

Use the existing upfront partial-period proration choice for initial policy coverage.
Coverage starts at the later of employment start and assignment start. With adjustment,
grant the proportion for remaining eligible calendar days in the applicable leave year;
with Give the full period allowance, grant the full annual amount once. Add no policy
switch. Explain employment and assignment dates in the existing partial-period help.

Example: first coverage on 1 July 2026 for an 18-day calendar-year policy gives
18 × 184/365 before applicable conversion/whole-minute rounding with adjustment, or
18 days once under the full-period choice. Known employment end and other applicable
employment/proration/cap rules still apply; this example assumes employment through year end.

This is initial entitlement, not ending/restarting coverage after an upfront grant.
ADR-0141 prohibits another annual grant merely from resumption. Preserve original
portions/expiry/history and ADR-0136 replacement/ADR-0137 ending safeguards. No retrospective
grant for pre-coverage dates or duplicate grant through replacement/reassignment.

## Consequences and verification

Bind original policy/type/period provenance and proof of initial versus previously granted
entitlement, employment/assignment date intersection, anniversary/leap boundaries, rate/
conversion/cap/rounding, known employment end and concurrent assignment guards. Do not
silently extend employment-departure clawback to assignment ending. Availability follows
accepted effective-date rules; no worker-posting or duplicate actual/derived earning.

Verify later employment/assignment start, the July example, adjusted/full choices,
anniversary/leap periods, existing previous grants, resumption/replacement without
duplication, current scope, evidence and review. Exact tests/final sizing/readiness remain
open; no runtime tests or code. Update requirements, spine, written help, relevant E3
calculation/assignment contracts and tracker/handoff. Reuse generic review/typed-result/
evidence scaffold/UI patterns; Leave owns entitlement semantics. Existing agent context
suffices. Accepted predecessors unchanged; no implementation authorization.
