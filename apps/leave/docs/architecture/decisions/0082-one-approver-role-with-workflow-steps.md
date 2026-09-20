# ADR-0082: One Approver Role with Workflow-Assigned Steps

**Status:** Accepted  
**Date:** 2026-09-17  
**Scope:** Leave approval role and workflow configuration

## Decision

Expose one Approver role rather than separate Supervisor and Final approver roles.
The role permits decisions on assigned approval steps; workflow configuration
determines the step and person. A supervisor relationship can resolve an assignment
but is not a separate approval role. Final approver describes workflow position,
not a permanent role or a universal override power.

Retain the one-/two-step MVP presets, required-step completion, authorized automatic
decisions, self-approval restrictions, and separate sensitive-document access.
Directional absence and temporary appointment rules remain attached to assigned
responsibilities. A temporary appointment still grants bounded authority without
requiring a permanent Approver role.

Use a unified approval capability with workflow-step/resource scope in the catalog;
reconcile the earlier supervisor/final permission entries during contract design.
Do not implement this by broadening permission to all requests.

This refines Leave's role catalog under
[platform ADR-0011](../../../../../platform/docs/architecture/decisions/0011-application-roles-and-business-permissions.md).
It does not remove the required steps in [ADR-0007](./0007-required-approval-and-automatic-decisions.md)
or the configured directional behavior in [ADR-0080](./0080-directional-absence-approval-policy.md).

## Consequences

- Verify the same role can act on different assigned positions but never unassigned requests.
- Shared UI/scaffold: reuse shared role controls; update application catalog examples when implemented.
- Agent context: unchanged.
- Documentation: product roles, permission families, tracker, UX, and mock updated.
- ADR impact: role-catalog refinement; historical terminology remains in immutable records.
- No runtime role assignments or access grants changed.
