# ADR-0139: Scheduled-Policy Amendment Cutoff

**Status:** Accepted  
**Date:** 2026-10-15  
**Scope:** Policy schedules with different employee effective boundaries

## Decision

For MVP, permit Amend scheduled change and Cancel scheduled change only before the
change takes effect for any affected employee. After the first effect starts, use the
normal new-policy-version flow under [ADR-0002](./0002-versioned-leave-policies.md).
Do not partly roll back already-effective changes while cancelling still-future effects.

Example: an 18-to-24-day change applies to Ana on 1 July and Ben on 1 October.
In August, the original change is no longer amendable/cancellable through the scheduled
actions. Review a new prospective policy version and resulting employee-specific dates
instead. Preserve already-earned/granted entitlement and original decision evidence.
The new-version flow is not an immediate undo of Ana's grant or an assumed cancellation
of Ben's scheduled effect; show actual resulting future changes and permitted timing.

Notify actually affected employees under [ADR-0101](./0101-monthly-rate-changes-and-effective-date-notifications.md)
and [ADR-0102](./0102-upfront-entitlement-changes-next-period.md), retaining original
notices/history and minimal sensitive content. Actual mistakes still use their authorized
correction workflows; [ADR-0128](./0128-accountable-request-impacts-of-administrative-changes.md)
request-impact safeguards remain binding.

## Consequences and verification

Bind how the earliest effective boundary is determined and protected for the complete
affected set, including non-allowance fields, changed assignments, timezones and concurrent
boundary crossing. Use effectiveness, not first usable earning date, notification delivery
or execution of a worker. Do not infer still-future status from a global Scheduled label.
Exact overlap/supersession/version interpretation and source/test mapping remain contracts.

Story 3.35 rejects stale amend/cancel at the cutoff; Story 3.34 reviews new prospective
versions with preserved original effects. Verify all-future changes, the Ana/Ben example,
boundary race, renewed review, preserved history/grants, accurate resulting dates and
duplicate-safe notifications/recovery. Real E5/E6 integrations precede affected activation.

Update requirements, spine, written UX, story obligations and tracker/handoff. Reuse guarded
version/review/action-availability scaffold/UI patterns; Leave owns effective-boundary
semantics. Existing agent context suffices. Accepted predecessors unchanged; no runtime
tests, code, final sizing/readiness PASS or implementation authorization.
