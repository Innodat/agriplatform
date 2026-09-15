# ADR-0016: Approver Visibility of Medical-Document Metadata

**Status:** Accepted  
**Date:** 2026-09-14  
**Scope:** Medical-document metadata shown to assigned approvers

## Context

The user approved showing approvers without document permission only whether a
required document was provided and its verification status. Filenames and previews
can disclose sensitive information without opening a file.

## Decision

For in-scope requests, assigned approvers without
`leave.document.sensitive.read` may see only whether the required medical document
was provided and its verification status. Status text must not expose document
contents or revealing diagnostics.

Filenames, previews, and downloads require the separate document permission and
request-level document authorization under
[ADR-0006](./0006-sensitive-attachment-access.md), with applicable content-safety
checks. Enforce this restriction in API responses and direct metadata, preview,
and download access, not only in the rendered request view.

Employees retain access to their own permitted documents under existing ownership
and authorization rules. This decision does not add an approver permission
requirement to employee access or change other roles' metadata visibility.

This resolves the assigned-approver medical-document metadata question left open
by [ADR-0012](./0012-assigned-approver-field-visibility.md). It does not expand
[email](./0014-email-notification-privacy.md) or
[in-app notification](./0015-in-app-notification-privacy.md) content. Business-data
checks follow the platform's
[API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md).

## Alternatives considered

- Show filenames and previews to every assigned approver: rejected because those
  fields can reveal sensitive information without a download.
- Hide all document-presence information: the user approved a minimal provision
  indicator and verification status to support approval decisions.

## Consequences

- The specification records permitted status, denied metadata/access, and retained
  employee-access acceptance examples for later executable tests.
- Scaffold impact: no scaffold change — application-specific visibility policy.
- Shared-UI impact: none; no reusable implementation is introduced.
- Agent-context impact: existing authorization and test-first rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: additive metadata clarification; accepted ADRs remain unchanged.
- Other unspecified R5 fields and roles remain open. This is planning only;
  Phase 1 readiness remains required before implementation.
