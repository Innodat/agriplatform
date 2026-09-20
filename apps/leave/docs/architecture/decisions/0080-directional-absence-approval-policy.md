# ADR-0080: Directional Approval Reduction During Absence

**Status:** Accepted  
**Date:** 2026-09-17  
**Scope:** Optional two-step approval policy

## Decision

Keep all configured steps required by default. Offer an explicit two-step policy
alternative: when the supervisor is absent, the configured final approver (the CEO
in the agreed example) may approve alone. When the final approver is absent, the
supervisor cannot decide alone; appoint a temporary final approver.

Use recorded applicable absence, not elapsed response time, as the condition.
Record the omitted supervisor step as Not required under absence policy rather
than Approved. Preserve the actual decision-maker and policy basis in history.
Require at least one valid approval, retain self-approval restrictions and current
authorization checks, and do not bypass unpaid acknowledgement or other finalization
conditions. If both configured approvers are absent, temporary approval is required.

This partially supersedes the unconditional all-configured-steps requirement in
[ADR-0007](./0007-required-approval-and-automatic-decisions.md) and
[ADR-0008](./0008-later-step-acceptance-on-submission.md) only for the explicitly enabled
absence policy. It does not supersede the default or grant general override powers.
Follow the platform [API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md).

## Planning dependencies

Preserve snapshotted policy and completed decisions. Before implementation, define
when absence eligibility is evaluated for pending steps and how subsequent changes
are explicitly recorded. Do not infer permission to silently rewrite an in-flight
workflow. Define how valid final-approver fallback is recognized in the coverage
check from [ADR-0078](./0078-approval-coverage-before-final-approval.md), including
responsibilities governed by other policies. Resolve the both-absent combination
without assuming every temporary final approver inherits the CEO's step-reduction
authority. These mechanics remain open; the directional policy choice is accepted.

## Consequences

- Delivery scenarios: default requires both steps; enabled rule permits CEO-only
  approval for absent supervisor; CEO absence does not permit supervisor-only
  approval; self-approval conflicts and both-absent cases remain controlled.
- Shared UI/scaffold: no change now; policy and review use existing planned controls.
- Agent context: unchanged.
- Documentation: synchronize specification, tracker, UX, index, and decision log.
- ADR impact: partial supersession above; historical text remains immutable.
- Planning only; no runtime or approval state changed.
