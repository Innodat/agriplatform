# ADR-0018: Approval History Is Visible to Employees and Assigned Approvers

**Status:** Accepted  
**Date:** 2026-09-14  
**Scope:** Approval history and comments

## Context

The user approved employees seeing decisions, approver names, timestamps, and
approval/rejection comments on their own requests. Assigned approvers may see the
same history for requests they handle. MVP has no private approver-only comments.

## Decision

Expose decisions, approver names, decision timestamps, and approval/rejection
comments to the request owner and assigned approvers within their authorized active
NGO/resource scope. Enforce the same visibility in request views and API responses.
MVP supports no private approver-only comments; approval and rejection comments
are visible to the employee whose request they concern.

This completes those history fields for the approver role alongside
[ADR-0012](./0012-assigned-approver-field-visibility.md). Leave Manager history access
remains as approved in [ADR-0013](./0013-leave-manager-field-visibility.md).
It does not grant unrelated actors access or expand
[colleague visibility](./0011-colleague-absence-privacy.md),
[email content](./0014-email-notification-privacy.md), or
[in-app notification content](./0015-in-app-notification-privacy.md).
Medical documents retain [separate authorization](./0006-sensitive-attachment-access.md).
Business-data access follows the platform's
[API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md).

## Alternatives considered

- Private approver-only comments: excluded from MVP by the user's decision.
- Show the employee only the outcome: the user selected full decision attribution,
  timestamps, and approval/rejection comments.

## Consequences

- The specification includes employee and assigned-approver history visibility,
  denied out-of-scope access, and continued notification exclusions as acceptance
  examples for later executable tests.
- Scaffold impact: no scaffold change — application-specific visibility policy.
- Shared-UI impact: none; no reusable implementation is introduced.
- Agent-context impact: existing authorization and test-first rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: additive history clarification; accepted ADRs remain unchanged.
- This resolves approval-history visibility, not a fresh validation of the entire
  privacy matrix. Planning only; Phase 1 readiness still precedes implementation.
