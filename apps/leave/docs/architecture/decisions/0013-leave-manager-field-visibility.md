# ADR-0013: Leave Manager Request-Field Visibility

**Status:** Accepted  
**Date:** 2026-09-14  
**Scope:** Leave Manager request-field visibility

## Context

The user confirmed that Leave Managers may see leave types, employee notes, and
approval history within their authorized NGO scope, while medical documents still
require a separate permission.

## Decision

Through their Leave Manager role, actors may read leave types (including sensitive
types), employee notes, and approval history within their authorized active NGO
and resource scope. Enforce this scope in request views and API responses.

Medical documents remain subject to `leave.document.sensitive.read`, request-level
document authorization, and Content Service protections under
[ADR-0006](./0006-sensitive-attachment-access.md). Leave Manager status alone does
not grant document access or access to another NGO or out-of-scope requests.

This adds the Leave Manager visibility rule left open by
[ADR-0011](./0011-colleague-absence-privacy.md) and
[ADR-0012](./0012-assigned-approver-field-visibility.md). It does not expand
Organization Administrator or Platform Administrator permissions. The platform
[API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md)
continues to govern business-data authorization.

## Alternatives considered

- Require another permission for these request fields: the user approved access
  through the Leave Manager role within its authorized scope.
- Include medical documents in role access: rejected; separate authorization stays.

## Consequences

- The specification includes an allowed-field example and document/out-of-scope
  denial examples for later executable acceptance tests.
- Other unspecified fields and delivery channels in review finding R5 remain open;
  this decision does not determine attachment metadata or notification payloads.
- Scaffold impact: no scaffold change — application-specific authorization rules.
- Shared-UI impact: none; no reusable implementation is introduced.
- Agent-context impact: existing authorization and test-first rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: additive clarification; accepted ADRs remain unchanged.
- Planning only; Phase 1 readiness remains required before implementation.
