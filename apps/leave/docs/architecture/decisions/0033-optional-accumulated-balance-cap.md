# ADR-0033: Policies May Cap Accumulated Balances

**Status:** Accepted  
**Date:** 2026-09-14  
**Scope:** Scheduled accrual at a maximum accumulated balance

## Context

The user approved each policy choosing a maximum accumulated balance or remaining
uncapped. Scheduled accrual grants only what fits; excess is recorded as not
granted with an explanation. Existing entitlement is not removed.

## Decision

Support an optional accumulated balance cap per policy, separate from carry-over
limits. On scheduled accrual, grant only the amount that fits under the cap and
record the excluded amount as not granted because of the cap. Explain both the
granted and excluded amounts in balance history. At or above the cap, grant zero
without removing existing entitlement. Uncapped policies grant the otherwise
eligible scheduled amount.

Preserve [immutable ledger and audit history](./0001-immutable-balance-ledger.md),
[versioned policies](./0002-versioned-leave-policies.md), and
[scheduled-grant rules](./0024-mvp-accrual-schedules.md). This decision does not
replace [carry-over limits](./0028-policy-carry-over-options.md) or introduce an
automatic deduction. The platform's
[API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md)
continues to apply.

## Alternatives considered

- Require every policy to have a cap: the user selected an optional cap.
- Remove existing entitlement when applying a cap: rejected.
- Silently omit excess scheduled accrual: rejected; record and explain it.

## Consequences

- The specification includes partial-grant, at/above-cap, and uncapped examples
  for later executable acceptance tests.
- Reservation treatment in cap measurement and recovery of excluded accrual remain
  to be resolved before affected stories pass readiness. This decision does not
  define how caps affect manual grants or authorized exceptions.
- Scaffold impact: no scaffold change — application-specific entitlement policy.
- Shared-UI impact: none; no reusable implementation is introduced.
- Agent-context impact: existing deterministic calculation and ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: additive cap decision; accepted ADRs remain unchanged.
- Planning only; Phase 1 readiness and failing acceptance tests precede implementation.
