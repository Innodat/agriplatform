# ADR-0020: Allocate Eligible Entitlement by Earliest Expiry

**Status:** Accepted  
**Date:** 2026-09-14  
**Scope:** Allocation within a selected leave balance

## Context

An employee may have carried-over and newly accrued entitlement with different
expiry dates. The user approved using eligible entitlement that expires soonest
first, with non-expiring entitlement last, within the selected leave balance.
Using another leave type still requires the agreed override.

## Decision

Allocate eligible entitlement within the selected balance in ascending expiry
order. Allocate non-expiring entitlement only after eligible expiring portions.
Determine eligibility using the requested date and existing accrual, expiry, and
reservation rules in [ADR-0019](./0019-date-by-date-future-balance.md). Ordering does
not make expired, not-yet-earned, or already-reserved entitlement available.

Do not automatically draw from another leave type. Cross-type use remains subject
to the existing authorized override and explicit allocation rules in the
[feature specification](../../features.md#9-insufficient-balance-override).
Preserve [immutable ledger allocations](./0001-immutable-balance-ledger.md),
[policy snapshots](./0002-versioned-leave-policies.md), and
[canonical minutes](./0003-working-time-in-minutes.md). The platform's
[API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md)
continues to govern the Leave calculation service boundary.

## Alternatives considered

- Use newly accrued entitlement before earlier-expiring carry-over: not the
  selected rule; eligible entitlement expiring soonest takes priority.
- Automatically use another leave type when the selected balance is insufficient:
  rejected; the existing override remains required.

## Consequences

- The specification includes a worked allocation example and a cross-type denial
  example for later executable acceptance tests.
- This resolves expiry priority from R3. Same-expiry tie-breaking must be
  deterministic before the allocation story passes readiness; proration, rounding,
  supported calculation options, and same-date event ordering remain unresolved.
- Scaffold impact: no scaffold change — application-specific allocation rules.
- Shared-UI impact: none; no reusable implementation is introduced.
- Agent-context impact: existing deterministic calculation and ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: additive resolution of ADR-0019's open allocation priority; accepted
  ADRs remain unchanged.
- Planning only; Phase 1 readiness and failing acceptance tests precede implementation.
