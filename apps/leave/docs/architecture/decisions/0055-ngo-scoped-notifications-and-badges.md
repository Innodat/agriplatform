# ADR-0055: Active-NGO Inbox with Per-NGO Unread Badges

**Status:** Accepted  
**Date:** 2026-09-15  
**Scope:** Notification display and NGO switching

## Context

The user approved active-NGO notification display and proposed unread badges on
individual NGO selector entries. They agreed to counts only for active memberships,
with details loaded after selecting the NGO.

## Decision

Show only the active NGO's notifications and unread count in the main bell and
inbox. Switching NGOs loads the selected NGO's inbox. Recheck current membership
and request permissions when opening notifications.

Show each NGO's unread count in the selector only while the user has active
membership there. This is a limited cross-NGO count summary, not access to other
NGOs' notification details. Do not include previews or request information in
selector badges or their count payloads. Selecting an NGO loads its authorized inbox.

Use [minimal notification content](./0015-in-app-notification-privacy.md) and the
platform's [common notification capability](../../../../../platform/docs/architecture/decisions/0006-common-notification-capability.md).
Authorization remains server-enforced under the
[API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md).

## Alternatives considered

- Merge all NGO notification details into the active inbox: rejected in favor of
  active-NGO detail with separate count-only awareness.
- Hide all awareness of other NGO unread items: the user requested selector badges.

## Consequences

- The specification includes two-NGO counts, switching, and revoked-membership
  denial examples for later executable tests, including count payload privacy.
- Scaffold impact: update shared notification client and NGO switching integration
  when proven in implementation; no runtime code is added now.
- Shared-UI impact: reusable selector badges and active-NGO bell/inbox belong in
  shared UI when proven, while Leave detail views remain application-specific.
- Agent-context impact: existing tenant authorization and ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: additive application requirement; reusable cross-app contracts should
  be recorded in platform architecture during planning without copying decisions.
- Planning only; Phase 1 readiness and failing acceptance tests precede implementation.
