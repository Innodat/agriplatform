# ADR-0022: Accrual Is Available from the Start of Its Effective Date

**Status:** Accepted  
**Date:** 2026-09-14  
**Scope:** Newly accrued entitlement availability

## Context

The user approved newly accrued entitlement becoming available from the start of
its configured effective date. Each policy still determines its accrual schedule
and effective dates.

## Decision

Include accrual in availability from the start of its configured effective date.
It may fund eligible leave on that date or later, subject to expiry, reservations,
and allocation rules. It cannot fund leave taken before its effective date.
Do not impose a universal monthly schedule or first-of-month effective date;
these remain policy configuration.

Apply this rule within
[date-by-date projection](./0019-date-by-date-future-balance.md),
[earliest-expiry allocation](./0020-earliest-expiry-entitlement-allocation.md), and
[inclusive expiry](./0021-inclusive-entitlement-expiry-date.md).
Preserve [idempotent immutable ledger entries](./0001-immutable-balance-ledger.md)
and [effective-dated policies](./0002-versioned-leave-policies.md).
Implementation follows the platform's
[API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md).

## Alternatives considered

- Make accrual usable only after its effective date: the user selected availability
  from the start of that date.
- Allow new accrual to fund earlier leave: inconsistent with the accepted
  date-by-date projection rule.

## Consequences

- The specification includes a 1 February versus 31 January acceptance example
  for later executable calculation tests.
- This resolves availability on the accrual effective date. Supported accrual
  schedules, timezone boundaries, proration, rounding, and other pending calculation
  details still need sufficient definition before affected stories pass readiness.
- Scaffold impact: no scaffold change — application-specific calculation policy.
- Shared-UI impact: none; no reusable implementation is introduced.
- Agent-context impact: existing deterministic calculation and ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: additive clarification; accepted ADRs remain unchanged.
- Planning only; Phase 1 readiness and failing acceptance tests precede implementation.
