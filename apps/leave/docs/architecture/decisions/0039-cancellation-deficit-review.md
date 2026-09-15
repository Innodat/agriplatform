# ADR-0039: Authorized Leave Managers Review Cancellation Deficits

**Status:** Accepted  
**Date:** 2026-09-14  
**Scope:** Review of deficits resulting from cancellation recalculation

## Context

The user approved a Leave Manager with balance-adjustment permission reviewing a
cancellation deficit, recording a mandatory reason, and explaining the outcome to
the employee. Additional paid entitlement requires an explicit audited grant;
previously approved leave is never automatically changed to unpaid.

## Decision

Assign review of [cancellation-recalculation deficits](./0038-cancellation-accrual-recalculation.md)
to a Leave Manager with `leave.balance.adjust` within the authorized active NGO and
resource scope. Require a reason for the review outcome and an employee-visible
explanation. Preserve the actor, outcome, and reason in audit history.

Additional paid entitlement must be an explicit audited grant under existing
authorization and [immutable ledger rules](./0001-immutable-balance-ledger.md).
Resolving the review alone does not create entitlement. Do not automatically
convert previously approved leave to unpaid leave. This review does not add an
approval gate to cancellation itself or broaden on-behalf permissions.
The platform's [API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md)
continues to apply.

## Alternatives considered

- Let any approver resolve a balance deficit: the user selected a Leave Manager
  with balance-adjustment permission.
- Resolve without a reason or employee explanation: rejected.
- Silently grant entitlement or convert approved leave to unpaid: rejected;
  paid grants must be explicit and audited.

## Consequences

- The specification includes permission/scope denial, mandatory-reason, explicit
  grant, employee-explanation, and no-automatic-unpaid expectations for later tests.
- This identifies the reviewer and controls, without inventing debt recovery,
  payroll deduction, or other unspecified deficit-resolution mechanisms.
- Scaffold impact: no scaffold change — application-specific review behavior.
- Shared-UI impact: keep the review and explanation in Leave; no shared component now.
- Agent-context impact: existing authorization, audit, and ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: additive review responsibility; accepted ADRs remain unchanged.
- Planning only; Phase 1 readiness and failing acceptance tests precede implementation.
