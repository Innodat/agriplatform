# ADR-0088: Employee Acknowledgement for On-Behalf Unpaid Leave

**Status:** Accepted  
**Date:** 2026-09-20  
**Scope:** Initial unpaid amount in an authorized on-behalf request  
**Supersedes in part:** [ADR-0069](./0069-submission-summary-and-unpaid-acknowledgement.md), only acknowledgement timing for on-behalf submission

## Context and decision

Ordinary employees acknowledge an exact unpaid amount before submitting their own
request. An authorized manager entering that request for them needs a way to hand
off acknowledgement without acting as the employee or modifying their saved draft.

Allow the authorized manager to submit the request with the required reason and
paid/unpaid allocation. Notify the employee through the existing minimal notification
flow and show Your response is needed on My Leave, linked to the submitted request.
Only the employee may acknowledge its current unpaid amount. On-behalf permission
does not authorize that acknowledgement. Keep the manager, employee and each actor’s
actions separately attributed in history.

Final approval remains blocked until the employee’s acknowledgement is valid for
the current unpaid amount. Otherwise-authorized intermediate approval steps may
proceed. A submitting approver’s own assigned step may be recorded as approved under
[ADR-0007](./0007-required-approval-and-automatic-decisions.md) and
[ADR-0008](./0008-later-step-acceptance-on-submission.md), including when it is
the sole step; the overall request still cannot finalize until acknowledgement and
all other existing finalization gates pass. Keep entitlement reserved until valid
final approval and consume it once. Do not require a repeated approval solely
because employee acknowledgement arrives later.

Recheck the current request and exact unpaid amount when the employee responds.
A stale checkbox cannot acknowledge a different amount. Changes retain the actor,
reason and prior decisions under
[ADR-0032](./0032-protected-reservations-and-explained-changes.md). Existing eligible
withdrawal remains available. This response is part of the submitted request,
not a second employee draft, and leaves any employee-owned draft untouched.

Ordinary self-service submission still requires exact-amount acknowledgement before
submission. This exception changes only the on-behalf handoff, not approval authority,
funding permissions, notification privacy or the employee’s identity.
The platform [API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md)
continues to apply.

## Consequences and impacts

- Acceptance examples cover submission by a manager with and without an assigned
  approval step, sole-approver finalization waiting for the employee, changed amounts
  before response, denied manager acknowledgement and an untouched employee draft.
- Scaffold/shared UI: no implementation; reuse the existing request-response surface
  and generic notification primitives when delivered. The consent gate is Leave-specific.
- Agent context: no change.
- Documentation: synchronize requirements, UX, delivery tracker, ADR index and logs.
- ADR: preserve all accepted files; refine ADR-0069 only for on-behalf timing and retain
  ADR-0071’s concise summary refinement.
- Planning only; no implementation readiness approval.
