# ADR-0056: Notification Read State Is Separate from Business Actions

**Status:** Accepted  
**Date:** 2026-09-15  
**Scope:** Notification read behavior

## Context

The user approved marking notifications read on opening and providing “Mark all
as read” for the active NGO only. Reading is not approval or unpaid-amount
acknowledgement.

## Decision

Mark a user's notification read when they open it. Provide an action to mark that
user's notifications read within the active NGO only. Update the corresponding
unread counts; do not modify another NGO's or another user's read state.

These actions do not approve leave or acknowledge an increased unpaid amount.
Retain explicit authorized approval and acknowledgement actions under
[ADR-0007](./0007-required-approval-and-automatic-decisions.md) and
[ADR-0032](./0032-protected-reservations-and-explained-changes.md).
Apply [NGO-scoped display and membership checks](./0055-ngo-scoped-notifications-and-badges.md)
using the platform's
[common notification capability](../../../../../platform/docs/architecture/decisions/0006-common-notification-capability.md)
and [API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md).

## Alternatives considered

- Mark every NGO's notifications read together: rejected; bulk action is active-NGO only.
- Treat reading as approval or acknowledgement: rejected; business actions remain explicit.

## Consequences

- The specification includes per-user, two-NGO read/count behavior and unchanged
  approval/acknowledgement expectations for later executable tests.
- Scaffold impact: integrate the shared read-state client when proven during delivery;
  no runtime code is added now.
- Shared-UI impact: read and bulk-read controls belong with the reusable notification
  display; Leave approval and acknowledgement remain domain actions.
- Agent-context impact: existing authorization and ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: additive read-state requirement; accepted ADRs remain unchanged.
- Planning only; Phase 1 readiness and failing acceptance tests precede implementation.
