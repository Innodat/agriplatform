# ADR-0106: On-Demand Accrual with Decision Evidence

**Status:** Accepted  
**Date:** 2026-09-22  
**Confirms and refines:** ADR-0090  
**Supersedes in part:** ADR-0001 only where a posted accrual entry is required to derive automatic entitlement

## Decision

Choose authoritative backend calculation on demand for automatic entitlement,
rather than daily accrual transactions. Availability must not depend on a scheduled
posting job. Store effective-dated policy and employment history, immutable actual
balance events (including leave deductions, adjustments and corrections), and
calculation snapshots at consequential submissions, approvals and confirmed changes.
A routine balance read does not require an accrual transaction or decision snapshot.

Calculate earned entitlement for the requested date from the recorded history.
Apply caps, expiry, reservations and corrections in their historical order; a simple
annual-rate multiplication cannot replace the established rules. The same recorded
inputs and calculation rules must reproduce the same result. Snapshots preserve the
evidence used in a decision; they do not authorize a later mutation using stale data.
Existing fresh-data and concurrency requirements still apply at confirmation.

The employee sees a simple balance with an expandable explanation. An illustrative
breakdown is 9 days earned, 3 deducted for approved leave, 2 reserved for pending
requests, and 4 available. Keep reservations and deductions distinct.

Any future cache or materialized projection remains subordinate to the calculation;
never count a derived earning portion and its projection as separate entitlements.
This decision does not remove workers used for notifications or other scheduled work.

## Impact and verification

- Acceptance: repeat reads without duplicate earning; deterministic historical replay;
  correct cap/expiry handling; preserved decision evidence; fresh mutation validation.
- Scaffold/shared UI: calculation is Leave-specific; reuse existing disclosure controls.
- Agent context: no additional instruction needed.
- Documentation: requirements/tracker synchronized; physical event/snapshot schema,
  replay ordering details and bounded calculation cost remain readiness work.
- ADR: accepted originals retained; scoped refinement of ADR-0090/ADR-0001.
- Planning only; no runtime implementation or daily worker removal performed.
