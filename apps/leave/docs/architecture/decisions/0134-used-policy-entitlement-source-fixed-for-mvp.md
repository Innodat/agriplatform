# ADR-0134: Used-Policy Entitlement Source Fixed for MVP

**Status:** Accepted  
**Date:** 2026-10-15  
**Scope:** Transitions between automatic entitlement and manual-only grants

## Decision

Allow automatic annual entitlement or manual-only grants at initial policy setup under
[ADR-0090](./0090-annual-entitlement-availability-options.md). Once a policy is in use,
keep that category fixed for MVP. Defer ordinary conversion between automatic entitlement
and manual-only grants until transition effects are designed. This resolves that open
question in [ADR-0098](./0098-availability-method-changes-at-period-boundaries.md);
accepted predecessors remain unchanged.

Retain supported daily/monthly/upfront changes within automatic policies at their agreed
boundaries. Retain normal authorized one-off adjustments, including additional grants to
automatic policies. An adjustment is not a category conversion and does not resolve when
automatic earning starts/stops or how previously earned entitlement survives conversion.

Enforce the restriction across applicable configuration and replacement-assignment paths;
creating a new type does not migrate existing entitlement between categories. This does
not prohibit independent new types or initial assignments with no migrated entitlement.
Types without a tracked balance are a separate concept whose MVP behavior remains open;
do not infer their behavior or exclude them from this decision about automatic/manual-only.

## Consequences and verification

Define/protect in-use detection and concurrency before implementation. Explain the fixed
category in used-policy editing; reject unsupported conversion through direct API and
replacement paths. Prove initial category selection, unchanged historical entitlement,
allowed automatic-method changes and authorized one-off adjustments with no category
change. Update features, spine, written UX, E3 contract obligations and tracker/handoff.
Reuse generic guarded configuration/review/typed errors in scaffold/UI; Leave owns earning
semantics. Existing agent instructions suffice. Exact source/test mapping, final sizing
and readiness remain open. No application code or implementation authorization.
