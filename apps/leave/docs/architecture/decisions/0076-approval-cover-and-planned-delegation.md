# ADR-0076: Planned Approval Delegation and Administrative Cover

**Status:** Accepted  
**Date:** 2026-09-16  
**Scope:** MVP approval availability and cover

## Decision

Support dated, authorized delegation for each required approval step, including
final approval, and permissioned reassignment for unexpected absence. Check the
substitute's NGO membership, step eligibility, known absence, and self-approval
conflicts. Delegation does not independently grant approval authority.

Flag approved absence as a coverage concern without waiting for the ordinary
seven-day escalation. Do not infer substitutes from the organization chart.
Support multiple Leave Managers with separately authorized reassignment rights.
When no eligible cover exists, preserve pending work and surface the issue rather
than skipping or automatically approving a required step.

Preserve existing workflow snapshots and completed decisions. Already assigned
outstanding steps require explicit authorized rerouting with actor/reason history;
delegation must not silently rewrite assignments. Activation and expiry treatment
of outstanding work remains a planning detail to resolve before implementation.

This extends the existing acting-approver requirement and complements
[ADR-0058](./0058-unanswered-approval-escalation.md), without superseding its
permissioned rerouting rule. Preserve required approvals under
[ADR-0007](./0007-required-approval-and-automatic-decisions.md) and the platform
[API authorization boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md).

## Consequences

- Product specification and tracker include coverage acceptance scenarios.
- Scaffold impact: none now; evaluate generic delegation needs during delivery.
- Shared-UI impact: existing person/date controls may be reused; Leave owns step eligibility.
- Agent-context impact: existing planning and authorization instructions suffice.
- Documentation impact: update feature requirements, tracker, UX, index, and decision log.
- ADR impact: additive; no accepted decision is superseded.
- Planning only; no runtime implementation or executable verification is claimed.
