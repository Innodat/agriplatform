# ADR-0154: Reassess Finalization When a Blocking Condition Resolves

**Status:** Accepted  
**Date:** 2026-10-22  
**Scope:** Pending requests whose approval decisions are already recorded  
**Complements:** [ADR-0007](./0007-required-approval-and-automatic-decisions.md),
[ADR-0078](./0078-approval-coverage-before-final-approval.md),
[ADR-0088](./0088-employee-acknowledgement-for-on-behalf-unpaid-leave.md)
and [ADR-0151](./0151-notify-pending-unpaid-changes-without-renewed-acknowledgement.md).

## Decision

When required approval decisions are already recorded, resolving a previously blocking
condition triggers a fresh finalization check automatically. If every current condition
passes, complete the request and consume applicable reserved allocation exactly once.
Otherwise retain pending status with the outstanding reason. Do not require repeated
valid approval or a separate manual completion button.

This includes arranging valid required approval cover and receiving an outstanding
initial unpaid on-behalf employee response. A manager's authorized coverage exception
can resolve that gate without claiming actual cover exists; other conditions remain.
This is completion using existing decisions, not an automatic decision for another
person. Recheck all independent gates, current authority and consequential input
consistency; preserve actual approver attribution. Merely opening or reading a request
or notification never triggers approval. L-0151 remains: later pending funding changes
do not introduce renewed employee acknowledgement.

## Contracts and verification still required

Bind an explicit trigger-to-owner map for relevant condition-resolving commands and
necessary scheduled/recovery consumers before readiness. Do not infer arbitrary periodic
approval, unspecified cross-owner callbacks or universal finalization on any write.
Define how required reassessment survives interrupted processing, unavailable checks,
concurrent changes and unknown outcomes. A successful cover arrangement is not proof
that request finalization succeeded. UI must show actual committed request status.
Keep short transactions/external waits outside locks and existing atomic domain/audit/
notification effects. Worker execution records initiator/executor appropriately without
inventing a human approval decision. Exact contracts, trigger enumeration and tests
remain open.

Verify all decisions plus last coverage/initial-response gate resolution, another gate
still blocked, stale/ineligible authority, unavailable check, race with withdrawal and
duplicate reassessment; check one-time effects and truthful status across real consumers.
Reuse existing operation/finalization/outbox/queue patterns; no generic workflow engine
or new UI approval flow. Update features, spine, UX, Story 5.10 and affected consumer
traceability, tracker/handoff and index. Existing agent rules suffice; accepted ADRs
unchanged. No code, runtime tests, migrations, grants, deployment or readiness approval.
