# ADR-0145: Reconcile Start-Available Monthly Coverage Changes

**Status:** Accepted  
**Date:** 2026-10-15  
**Scope:** Monthly instalment already available before assignment coverage is shortened

## Decision

Apply the existing partial-period choice when reviewing an assignment-ending change
that shortens a monthly instalment whose amount is already available. With adjustment,
recalculate from actual covered days; with full-period allowance, retain one nominal
instalment. This completes the start-available case left open by ADR-0142/0144.

Example: 1.5 days available on 1 April and proposed assignment ending on 15 April gives
0.75 days under adjusted 15/30 coverage, or retains 1.5 days under full-period allowance.
Show balance difference and affected requests before confirmation. The reviewed assignment
change owns this calculation consequence; do not require a separately calculated manual
deduction merely to implement the policy's formula.

Preserve original decision/calculation evidence, immutable actual events and current
authorization. Apply ADR-0128 safeguards to reserved/consumed amounts, including approved-
request pre-change resolution for discretionary changes. Do not silently cancel requests
or convert approved paid leave to unpaid. Necessary factual correction follows its own
reviewed workflow. Do not silently broaden assignment permission into funding-remedy authority.

This is monthly partial-period reconciliation. ADR-0137's retention of an annual upfront
grant on assignment ending remains separate. Normal adjustments remain available under
their own authority; do not duplicate derived reconciliation with an extra posted deduction.

## Consequences and verification

Bind original/proposed coverage, calculation versions, difference representation, effect/
recorded dates, precision/caps/expiry, existing request coordination and atomic assignment/
evidence/audit/notification intent. Repeated changes/resumption use the applicable union
of covered dates, not duplicate nominal instalments. Never rewrite original snapshots.

Verify adjusted/full April examples, unchanged prior periods, reviewed balance/request
impact, reserved/consumed safeguards, rejected stale review, no duplicate actual/derived
effect, attribution/retry recovery and privacy-appropriate existing notices. Actual E5/E6
consumers must integrate before activation. Exact tests/final sizing/readiness remain open.

Update requirements, spine, written review UX, affected earning/assignment story obligations
and tracker/handoff. Reuse review/version/coordination/evidence/outbox scaffold/UI patterns;
Leave owns reconciliation semantics. Existing agent context suffices; accepted predecessors
unchanged. No runtime tests/code or implementation/readiness authorization.
