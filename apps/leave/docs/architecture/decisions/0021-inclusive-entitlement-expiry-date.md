# ADR-0021: Entitlement Expiry Date Is the Last Usable Leave Date

**Status:** Accepted  
**Date:** 2026-09-14  
**Scope:** Entitlement expiry-date semantics

## Context

The user approved entitlement remaining usable for leave taken on its expiry date
and becoming unavailable the following day. Earlier submission does not allow
expired entitlement to fund later leave.

## Decision

Treat the expiry date as inclusive: entitlement can fund eligible leave taken on
that date, subject to availability and existing reservations. It cannot fund leave
taken from the next date onward. Evaluate expiry against the leave date, not the
submission date; early submission does not extend validity.

Apply this rule to each date under
[ADR-0019](./0019-date-by-date-future-balance.md), then allocate eligible portions
under [ADR-0020](./0020-earliest-expiry-entitlement-allocation.md). Existing shortfall
and override rules apply when remaining eligible entitlement is insufficient.
Preserve [immutable history](./0001-immutable-balance-ledger.md) and
[policy snapshots](./0002-versioned-leave-policies.md). Implementation follows the
platform's [API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md).

## Alternatives considered

- Make entitlement unavailable on its stated expiry date: the user selected that
  date as the last usable day.
- Preserve validity for later leave when submitted before expiry: rejected;
  eligibility follows when leave is taken.

## Consequences

- The specification includes 31 December/1 January and spanning-request acceptance
  examples for later executable tests.
- This resolves inclusive expiry-date meaning. Same-date accrual timing, applicable
  timezone boundaries, proration, and rounding still need sufficient detail before
  affected calculation stories pass readiness.
- Scaffold impact: no scaffold change — application-specific calculation policy.
- Shared-UI impact: none; no reusable implementation is introduced.
- Agent-context impact: existing deterministic calculation and ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: additive clarification; accepted ADRs remain unchanged.
- Planning only; Phase 1 readiness and failing acceptance tests precede implementation.
