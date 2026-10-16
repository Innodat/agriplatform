# ADR-0137: Ending Policy Assignment Preserves Earned Entitlement

**Status:** Accepted  
**Date:** 2026-10-15  
**Scope:** Ending an employee's policy assignment without replacement

## Decision

Stop automatic earning from the effective assignment end. New requests cannot include
leave dates outside applicable assignment coverage. Preserve already-earned entitlement,
its existing expiry and historical meaning. Ending the assignment does not itself erase
the remaining balance or reclaim an upfront grant already provided.

Retained entitlement remains visible to authorized users; it does not independently
authorize new requests without applicable policy coverage. Preserve existing requests
and review their consequences before confirmation under
[ADR-0128](./0128-accountable-request-impacts-of-administrative-changes.md), including
approved-request safeguards and any increased-unpaid acknowledgement obligations.
Do not silently cancel requests, release reservations or rewrite approved funding.

Assignment ending is distinct from ending employment. Factual employment departure and
its authorized proration/correction rules, including ADR-0048, remain unchanged. Do not
use assignment-ending behavior to bypass necessary factual correction or to imply that
the ordinary departure workflow has been executed. Existing events/evidence stay immutable.

## Consequences and verification

Bind precise inclusive/exclusive end-date representation, employee-local interpretation,
scheduled earning at the cutoff, existing request validity/funding treatment and review/
coordination before readiness. Existing expiry/carry-over provenance is not reset; exact
subsequent rollover/expiry interpretation must preserve applicable historical rules.
Ending coverage cannot bypass basis/category migration restrictions or authorize later
double earning through reassignment. Detailed resumption/overlap contracts remain gates.

Verify earning cutoff, request-date coverage, retained five-day balance without implied
new-request authority, no upfront clawback merely from assignment ending, original expiry/
history, actual request-impact safeguards and separation from employment departure.
Pair direct API/database/concurrency/recovery and UI review tests with actual E5/E6
integration before affected activation; exact tests and final sizing remain open.

Update Features §4/6, spine, written review UX, Story 3.36 contracts and tracker/handoff.
Reuse guarded effective-dated review/evidence/notification scaffold and UI patterns;
Leave owns earning/coverage meaning. Existing agent context suffices. Accepted predecessors
unchanged. Planning only; no code, runtime tests, readiness PASS or implementation authority.
