# ADR-0015: In-App Notifications Use Minimal Request Content

**Status:** Accepted  
**Date:** 2026-09-14  
**Scope:** Leave in-app notification content

## Context

The user approved using the email content limit for in-app notifications: employee
name, dates, status, and a request link. Opening the request shows the details
permitted by the recipient's role.

## Decision

Limit request-specific in-app notification content to employee name, absence
dates, request status, and a request link. Exclude leave types, employee notes,
approval comments, and document details from lists, banners, previews, API payloads,
and links. This matches the content boundary in
[ADR-0014](./0014-email-notification-privacy.md).

Notifications are exposed only to authorized recipients within their active NGO
and resource scope. Opening a request rechecks current authentication, membership,
and resource permissions; an earlier notification grants no continuing access.
The request view follows the recipient's role permissions, including
[approver](./0012-assigned-approver-field-visibility.md) and
[Leave Manager](./0013-leave-manager-field-visibility.md) rules. Medical documents
retain [separate authorization](./0006-sensitive-attachment-access.md).

This does not expand recipient audiences or weaken the
[colleague privacy rule](./0011-colleague-absence-privacy.md). Enforce the boundary
through the platform's
[FastAPI API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md),
not just rendered notification text.

## Alternatives considered

- Include role-permitted request details directly in notifications: the user
  selected minimal notifications with details available on opening the request.
- Hide details visually but include them in notification payloads: inconsistent
  with the approved content limit.

## Consequences

- The specification records notification payload and request-access acceptance
  examples, including access changes after notification delivery.
- Scaffold impact: no scaffold change — application-specific content policy.
- Shared-UI impact: none; no reusable implementation is introduced.
- Agent-context impact: existing authorization and test-first rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: additive resolution of the in-app channel left open by ADR-0014;
  accepted ADRs remain unchanged.
- Other unspecified R5 fields remain open. This is planning only; Phase 1 readiness
  remains required before implementation and executable acceptance testing.
