# ADR-0017: Leave Manager Medical-Document Metadata Visibility

**Status:** Accepted  
**Date:** 2026-09-14  
**Scope:** Medical-document metadata shown to Leave Managers

## Context

The user approved applying the assigned-approver medical-document metadata rule
to Leave Managers: without document permission, show only provision and
verification status. Filenames, previews, and downloads require separate permission.

## Decision

Within their authorized active NGO/resource scope, Leave Managers without
`leave.document.sensitive.read` may see only whether the required medical document
was provided and its verification status. Status text must not disclose document
contents or revealing diagnostics. Apply this limit in rendered views, API
responses, and direct metadata access.

Filenames, previews, and downloads require the separate permission, request-level
document authorization, and applicable content-safety checks under
[ADR-0006](./0006-sensitive-attachment-access.md). Neither Leave Manager status nor
the document permission grants access outside authorized NGO/resource scope.

This adds the Leave Manager counterpart of
[ADR-0016](./0016-approver-medical-document-metadata.md) and clarifies document
metadata alongside [ADR-0013](./0013-leave-manager-field-visibility.md)'s request
field rules. Employee access and other roles' permissions remain governed by
existing decisions. The platform's
[API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md)
continues to govern business-data authorization.

## Alternatives considered

- Show filenames and previews through the Leave Manager role alone: the user
  selected the same separate permission boundary as for approvers.
- Hide provision and verification status: the user approved these limited facts
  for in-scope administration.

## Consequences

- The specification records allowed status and denied metadata/access examples,
  including cross-NGO denial, for later executable acceptance tests.
- Scaffold impact: no scaffold change — application-specific visibility policy.
- Shared-UI impact: none; no reusable implementation is introduced.
- Agent-context impact: existing authorization and test-first rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: additive clarification; accepted ADRs remain unchanged.
- This closes the Leave Manager medical-document metadata question, not the full
  R5 finding. Planning only; Phase 1 readiness remains required for implementation.
