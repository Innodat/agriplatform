# ADR-0064: Approver Home Prioritizes Required Decisions and Availability

**Status:** Accepted  
**Date:** 2026-09-15  
**Scope:** Supervisor and final approver landing experience

## Decision

The user approved the approver home screen prioritizing:

- Requests currently awaiting the approver's decision.
- Flags for short notice, backdating, balance overrides, and overdue requests.
- Team availability alongside the queue.
- Access to the approver's own employee workspace.

Opening a request shows its duration, balance effect, employee explanation, and
approval history under the agreed permissions. Respect active NGO/resource scope;
the layout grants no additional team or document visibility. Only currently
required actions appear as actionable tasks, respecting already-recorded decisions.

Apply [approver field visibility](./0012-assigned-approver-field-visibility.md),
[approval history](./0018-approval-history-visibility.md),
[document permissions](./0016-approver-medical-document-metadata.md), and
[colleague privacy](./0011-colleague-absence-privacy.md). Data access follows the
platform's [API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md).

## Consequences

- The specification records actionable queue, flags, scoped availability,
  request details, and employee-workspace navigation expectations for later tests.
- Scaffold impact: no implementation now; promote proven generic layout patterns
  during delivery when appropriate.
- Shared-UI impact: generic queue/layout primitives may be shared; approval flags,
  decisions, and Leave availability privacy remain application-specific.
- Agent-context impact: existing authorization, accessibility, and ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog;
  elaborate responsive layouts during UX planning.
- ADR impact: additive home-screen decision; accepted ADRs remain unchanged.
- Planning only; Phase 1 readiness precedes implementation.
