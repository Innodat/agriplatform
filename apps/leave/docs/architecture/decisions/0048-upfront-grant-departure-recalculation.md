# ADR-0048: Recalculate Upfront Grants When Employment Ends

**Status:** Accepted  
**Date:** 2026-09-14  
**Scope:** Partial-period employment departure after upfront grants

## Context

The user approved recalculating a period's upfront grant using its policy proration
rule and employment end date. Corrections require explanations; spent-entitlement
deficits go to authorized Leave Manager review without automatically making
approved leave unpaid. No-proration policies retain their full eligible grant.

## Decision

Recalculate the affected upfront period grant using the recorded employment end
date and [policy proration](./0025-per-policy-calendar-day-proration.md), including
[final-grant rounding](./0026-prorated-grant-rounding.md). Record corrections as new
auditable entries with an employee-visible explanation. Under no proration, retain
the full otherwise eligible period grant.

If the excess was already spent, refer the deficit to an in-scope Leave Manager
with balance-adjustment permission, using the reason and employee-explanation
controls established for [deficit review](./0039-cancellation-deficit-review.md).
Do not automatically convert previously approved leave to unpaid. Apply
[explained renewed acknowledgement](./0032-protected-reservations-and-explained-changes.md)
when a pending request's unpaid amount increases.

Preserve [immutable history and idempotency](./0001-immutable-balance-ledger.md),
[historical policy versions](./0002-versioned-leave-policies.md), and existing
employment-update authorization. This does not introduce payroll deductions or
debt-recovery rules. The platform's
[API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md)
continues to apply.

## Alternatives considered

- Retain every upfront grant irrespective of the chosen proration rule: rejected.
- Prorate a no-proration policy: rejected; retain the full eligible grant.
- Silently rewrite history or make approved leave unpaid: rejected; use corrections
  and authorized deficit review.

## Consequences

- The specification includes a 480-minute April grant corrected to 240 minutes for
  a 15 April end date, plus no-proration, spent-deficit, and retry expectations.
- Scaffold impact: no scaffold change — application-specific grant reconciliation.
- Shared-UI impact: none now; employment-change explanations belong in Leave.
- Agent-context impact: existing authorization, audit, and ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: additive departure rule; accepted ADRs remain unchanged.
- Planning only; Phase 1 readiness and failing acceptance tests precede implementation.
