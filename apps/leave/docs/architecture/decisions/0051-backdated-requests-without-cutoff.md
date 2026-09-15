# ADR-0051: Backdated Requests Have No Fixed Cutoff

**Status:** Accepted  
**Date:** 2026-09-15  
**Scope:** Backdated leave submission

## Context

The user questioned the need for a fixed backdating window when approvers already
review requests. They approved unrestricted backdating by age, with a reason,
visible lateness, normal approval, and historical calculation protections.

## Decision

Permit backdated requests without a fixed cutoff. Require an employee reason and
show the assigned approver how late the submission is. Apply all existing
employment-date, overlap, and balance checks and the normal approval workflow.
Do not require a separate administrative route solely because a request is old.

Use the schedule and policy applicable to the historical leave dates, and explain
any resulting balance corrections using new auditable entries. Preserve
[historical policies](./0002-versioned-leave-policies.md),
[schedule-based calculations](./0003-working-time-in-minutes.md),
[immutable ledger history](./0001-immutable-balance-ledger.md), and
[required approvals](./0007-required-approval-and-automatic-decisions.md).
Use the [employee work timezone](./0023-employee-work-timezone.md) for date-based
lateness. The platform's [API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md)
continues to apply.

## Alternatives considered

- A configurable fixed cutoff with an administrative route beyond it: proposed
  during discussion but not adopted; normal review evaluates late requests.
- Allow backdating without reasons or historical calculation checks: rejected.

## Consequences

- The specification includes five-day and fourteen-day late submissions,
  missing-reason denial, and historical calculation expectations for later tests.
- This does not bypass other authorization or turn a request into automatic approval.
- Closed payroll/reporting periods are not introduced here; future adoption could
  require a linked decision on restrictions.
- Scaffold impact: no scaffold change — application-specific submission rules.
- Shared-UI impact: none now; lateness and correction explanations belong in Leave.
- Agent-context impact: existing authorization, audit, and ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: additive backdating decision; accepted ADRs remain unchanged.
- Planning only; Phase 1 readiness and failing acceptance tests precede implementation.
