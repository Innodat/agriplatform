# ADR-0138: Simple Leave-Type Deactivation and Employee Explanations

**Status:** Accepted  
**Date:** 2026-10-15  
**Scope:** Resolution of leave-type retirement dependencies and communication

## Decision

Retain the existing Deactivate action and dependency review under
[ADR-0132](./0132-leave-type-deactivation-dependency-guards.md). Resolve dependencies
through existing authorized assignment changes, adjustments and request/correction
actions. Defer a separate Close to new requests/Disable control and a combined retirement
workflow. The intervening conversational proposals for these controls were not adopted.

In addition to current/scheduled assignments, block deactivation while unexpired remaining
entitlement, pending requests, approved leave not yet finished, or unresolved funding/
correction issues still depend on the type. Historical-only references do not block.
Define exact date/status/amount predicates and supported write guards before readiness.
Show authorized links to normal resolution actions; no bulk zero-balance or automatic
request cancellation shortcut. Waiting for expiry is possible where consistent with the
existing policy. Do not deduct balances merely to tidy the catalogue.

The organization determines the permitted treatment of existing entitlement; administrators
review consequences through the applicable existing workflows. Preserve immutable history,
approved funding and [ADR-0128](./0128-accountable-request-impacts-of-administrative-changes.md).
Ending assignment still follows [ADR-0137](./0137-ending-policy-assignment-preserves-earned-entitlement.md).
No action/message bypasses unsupported basis/category/cross-type entitlement migration.

Use existing standard notifications and authorized detail views with clear employee-facing
reasons describing the real change. The existing adjustment reason supplies the explanation;
do not add a custom message composer, notification bundling or a new communication workflow.
An explanation may mention the appropriate new leave type where relevant and authorized,
without implying unsupported transfer. Preserve sensitive-type minimal notices/authorized
details; do not place private reasons into email or generic notification payloads.

## Consequences and verification

Extend Story 3.37's checks for the listed operational dependencies, without altering
historical-only access or valid retirement of resolved types. Verify current observations,
concurrent new dependencies, failed reads, authorized resolution navigation, no automatic
confiscation/cancellation and retained history. Existing adjustment/assignment notification
tests prove correct event/reason/date/amount/privacy; no extra retirement message engine.

Update requirements, spine, written UX, story obligations and tracker/handoff. Reuse guarded
dependency review/related-record/notification scaffold/UI patterns; Leave owns predicates
and business communication. Existing agent instructions suffice. Accepted predecessors
unchanged; exact contracts/tests/final sizing/readiness remain open. Planning only.
