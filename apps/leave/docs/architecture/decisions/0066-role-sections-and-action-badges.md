# ADR-0066: Role Sections Share One Application and Active NGO

**Status:** Accepted  
**Date:** 2026-09-15  
**Scope:** Navigation for users with multiple roles

## Decision

The user approved one application with My Leave, Approvals, and Manage Leave
sections shown according to permissions. Everyone starts on My Leave; section
switching requires neither sign-out nor an NGO change.

Show section badges for work requiring the user's attention. Keep those counts
separate from unread notifications: marking notifications read does not resolve
approval, acknowledgement, or administrative work. Scope sections and badge data
to the user's active NGO and permissions; enforce direct-route/API access too.

Use the approved [employee](./0063-employee-home-screen.md),
[approver](./0064-approver-home-screen.md), and
[Leave Manager](./0065-leave-manager-home-and-ngo-wide-scope.md) experiences, and
retain [notification read-state separation](./0056-notification-read-state.md).
The platform's [API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md)
continues to apply.

## Consequences

- The specification includes multi-role navigation, unauthorized section/count
  denial, and unchanged work badges after marking notifications read.
- Scaffold impact: incorporate proven generic shell navigation hooks during delivery;
  no runtime code is introduced now.
- Shared-UI impact: navigation/badge primitives may be shared; Leave section names,
  work-count semantics, and permissions stay application-owned.
- Agent-context impact: existing authorization, accessibility, and ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: additive navigation decision; accepted ADRs remain unchanged.
- Planning only; Phase 1 readiness precedes implementation.
