# ADR-0068: Save in the Original NGO Before Switching

**Status:** Accepted  
**Date:** 2026-09-15  
**Scope:** NGO switching during request editing

## Decision

The user approved saving the current draft in its original NGO before switching
and opening My Leave in the selected NGO. Never move the draft or unsaved data
between NGOs. If saving fails, remain on the request and offer Retry, Stay, or
Discard unsaved changes and switch. Discard applies only to unsaved changes;
preserve any previously saved draft in its original NGO.

Apply [draft saving](./0067-automatic-draft-saving.md),
[role navigation](./0066-role-sections-and-action-badges.md), and current membership
authorization through the platform's
[API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md).

## Consequences

- The specification includes successful save/switch, failed-save choices,
  preservation of the last saved draft, and cross-NGO data isolation expectations.
- A successful save does not itself authorize access to the destination NGO;
  existing membership and switching checks still apply.
- Scaffold impact: generic switch/save coordination may be promoted when proven;
  no implementation now.
- Shared-UI impact: reusable selector and unsaved-change dialog may host these
  controls; Leave draft persistence stays application-owned.
- Agent-context impact: existing authorization, data-preservation, and ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: additive switching behavior; accepted ADRs remain unchanged.
- Planning only; Phase 1 readiness precedes implementation.
