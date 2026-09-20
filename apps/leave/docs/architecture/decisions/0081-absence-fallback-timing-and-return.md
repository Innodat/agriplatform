# ADR-0081: Absence Fallback Timing and Supervisor Return

**Status:** Accepted  
**Date:** 2026-09-17  
**Scope:** Pending requests under directional absence policy

## Decision

Evaluate approver absence when approval is needed, not during the applicant's
requested leave dates. The applicant's own coverage requirement still considers
their planned absence period.

A temporary approver or final approver using the absence fallback may wait for the
supervisor to return when appropriate. Keep the request pending and visible, allow
an explanatory comment under normal comment visibility rules, and continue normal
reminders/escalation. Waiting does not create an implicit deadline extension.

Under the configured final-approver fallback, restore the outstanding supervisor
step when the supervisor returns if no final decision has been made, and record
the transition in history. A completed final-approver decision stays valid.
Temporary assignments retain the separate expiry/return rules in
[ADR-0077](./0077-scheduled-return-of-temporary-approvals.md).

This resolves pending-return behavior in
[ADR-0080](./0080-directional-absence-approval-policy.md) and partially supersedes
its requirement for explicit intervention for this particular transition. The
return is an execution of the snapshotted absence policy, not a policy replacement
or general permission for silent directory-driven rerouting. Do not erase recorded
decisions. Concurrent return/decision handling requires implementation design.

## Consequences

- Acceptance scenarios: December approval of February leave uses December approver
  availability; waiting retains reminders; supervisor return restores outstanding
  work before finalization; completed fallback approval is not reopened.
- Shared UI/scaffold: use current queue/history/comment patterns, no changes now.
- Agent context: unchanged.
- Documentation: product, UX, tracker, index, and decision log updated.
- ADR impact: timing refinement and narrow partial supersession above.
- Planning only; runtime scheduling and concurrency are not implemented.
