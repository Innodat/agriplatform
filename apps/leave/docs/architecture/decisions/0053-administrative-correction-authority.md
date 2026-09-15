# ADR-0053: Administrative Corrections Require Scoped Leave Manager Authority

**Status:** Accepted  
**Date:** 2026-09-15  
**Scope:** Role and permission for administrative leave corrections

## Context

The user confirmed that the administrator who corrects past, current, and future
leave is a Leave Manager with separate on-behalf permission within authorized NGO
and employee scope. Organization Administrator status alone grants no correction
authority. Reasons, history, and approved cancellation/replacement rules remain.

## Decision

Require the Leave Manager role and `leave.admin.on_behalf` permission within the
active NGO and authorized employee scope for administrative leave corrections.
Organization Administrator status alone is insufficient. Require a reason and
retain full correction history.

This resolves the role assignment left open by
[ADR-0052](./0052-overlaps-and-administrative-corrections.md). Preserve existing
[approved cancellation/replacement and separate approval rights](./0010-cancel-and-replace-approved-leave.md),
[immutable balance history](./0001-immutable-balance-ledger.md), and
[required approvals](./0007-required-approval-and-automatic-decisions.md).
Correction authority does not itself grant approval authority. The platform's
[API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md)
continues to apply.

## Alternatives considered

- Permit Organization Administrators by role alone: rejected.
- Permit any Leave Manager without separate on-behalf permission: rejected.

## Consequences

- The specification records allowed scoped correction and denied missing-permission,
  out-of-scope, and Organization-Administrator-only cases for later tests.
- This does not broaden document access or authorize silent changes to history.
- Scaffold impact: no scaffold change — application-specific correction authority.
- Shared-UI impact: none now; correction actions belong in Leave.
- Agent-context impact: existing authorization, audit, and ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: additive role clarification; accepted ADRs remain unchanged.
- Planning only; Phase 1 readiness and failing acceptance tests precede implementation.
