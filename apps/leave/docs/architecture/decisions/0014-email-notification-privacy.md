# ADR-0014: Email Notifications Keep Request Details in the Application

**Status:** Accepted  
**Date:** 2026-09-14  
**Scope:** Leave email notification content

## Context

The user approved email notifications containing only the employee's name, dates,
request status, and a secure link. Leave types, employee notes, approval comments,
and document details stay in the application, where permissions are checked.

## Decision

Limit request-specific email content to employee name, absence dates, request
status, and a secure application link. Exclude all leave types, employee notes,
approval comments, and document details from subjects, bodies, previews, and link
text/parameters. Do not attach supporting documents or use direct document links.

Following the application link requires authentication and active NGO/resource
authorization before request details are disclosed. Possession of a link grants
no access. Medical documents retain the separate permission and domain checks in
[ADR-0006](./0006-sensitive-attachment-access.md).

This is a content limit for authorized recipients, not permission to notify new
audiences or expose request status to ordinary colleagues. Preserve
[ADR-0011](./0011-colleague-absence-privacy.md)'s colleague boundary. In-application
field visibility follows the existing role rules, including
[ADR-0012](./0012-assigned-approver-field-visibility.md) and
[ADR-0013](./0013-leave-manager-field-visibility.md). This decision does not define
in-app notification payloads. Business-data authorization follows the platform
[API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md).

## Alternatives considered

- Include detailed request information in approval emails: not the selected rule;
  authorized users follow the link to the application for those details.
- Include documents or storage read links: rejected; document authorization remains
  inside the application flow.

## Consequences

- Email templates must enforce the same exclusions across ordinary and sensitive
  leave types, including subjects, previews, and links.
- The specification records content and link-access acceptance examples for later
  executable notification and authorization tests.
- Scaffold impact: no scaffold change — application-specific content policy.
- Shared-UI impact: none; no UI implementation is introduced.
- Agent-context impact: existing authorization and test-first rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: additive email-content decision; accepted ADRs remain unchanged.
- Other unspecified R5 fields/channels remain open. Phase 1 readiness is still
  required before implementation; this record changes planning documents only.
