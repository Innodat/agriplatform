# ADR-0012: Assigned Approvers Can Read Sensitive Types and Employee Notes

**Status:** Accepted  
**Date:** 2026-09-14  
**Scope:** Assigned approver request-field visibility

## Context

The user confirmed that approvers should see sensitive leave types and employee
notes through their normal approval role, while medical documents require a
separate permission. ADR-0011 left approver field visibility open.

## Decision

An assigned supervisor or final approver may read the leave type, including
sensitive types, and employee note for requests within their approval scope and
active NGO. These fields require no additional sensitive-field permission.
Enforce the same resource scope in request views and their API responses.

Approval authority alone grants no medical-document access. Such reads require
`leave.document.sensitive.read`, Leave request-level document authorization, and
the existing Content Service protections under
[ADR-0006](./0006-sensitive-attachment-access.md).

This decision grants no access to unrelated requests or other NGOs and does not
broaden administrative visibility. Ordinary colleague views retain
[ADR-0011](./0011-colleague-absence-privacy.md)'s Unavailable rule. Platform
[API authorization boundaries](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md)
continue to apply.

## Alternatives considered

- Require another permission for sensitive type labels and employee notes: the
  user selected access through the normal approval role.
- Include medical documents in approval access: rejected in favor of the separate
  document permission and resource authorization.

## Consequences

- The feature specification records allowed field access and denied document and
  out-of-scope access as acceptance examples.
- Administrative field visibility and other unresolved R5 details remain open;
  this decision does not settle attachment metadata or notification payloads.
- Scaffold impact: no scaffold change — application-specific authorization rules.
- Shared-UI impact: none; no reusable UI pattern is implemented here.
- Agent-context impact: existing tenant and resource authorization rules suffice.
- Documentation impact: synchronize the specification, tracker, index, and memlog.
- ADR impact: additive resolution of ADR-0011's open approver fields; accepted
  ADRs remain unchanged.
- This is a planning decision. Implementation still requires Phase 1 readiness;
  executable acceptance tests will be added before the affected behavior.
