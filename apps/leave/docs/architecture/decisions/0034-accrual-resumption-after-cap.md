# ADR-0034: Resume Scheduled Accrual Without Automatic Catch-Up

**Status:** Accepted  
**Date:** 2026-09-14  
**Scope:** Accrual after a balance drops below its cap

## Context

The user approved normal accrual resuming on the next scheduled date when the
balance falls below the cap, granting only what fits. Previously excluded amounts
are not automatically restored.

## Decision

A balance reduction below the cap does not itself trigger a grant. On the next
scheduled effective date, calculate the normal eligible grant and apply the
[balance cap](./0033-optional-accumulated-balance-cap.md). Do not automatically add
amounts excluded on previous scheduled dates because of the cap.

Preserve the history and explanation of excluded amounts under
[immutable ledger rules](./0001-immutable-balance-ledger.md). Continue using the
policy's [grant schedule](./0024-mvp-accrual-schedules.md) and
[effective-date availability](./0022-accrual-effective-date-availability.md).
This does not introduce a new rule for authorized manual adjustments. The
platform's [API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md)
continues to apply.

## Alternatives considered

- Grant immediately when the balance drops: the user selected the next scheduled date.
- Automatically restore earlier excluded accrual: rejected; normal accrual resumes
  without automatic catch-up.

## Consequences

- The specification includes next-date, no-immediate-grant, no-catch-up, and
  partial-capacity examples for later executable tests.
- Reservation treatment in cap measurement remains open before affected stories
  pass readiness.
- Scaffold impact: no scaffold change — application-specific entitlement policy.
- Shared-UI impact: none; no reusable implementation is introduced.
- Agent-context impact: existing deterministic calculation and ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: additive resumption decision; accepted ADRs remain unchanged.
- Planning only; Phase 1 readiness and failing acceptance tests precede implementation.
