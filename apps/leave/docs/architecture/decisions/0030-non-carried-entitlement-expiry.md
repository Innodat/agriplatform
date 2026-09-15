# ADR-0030: Unused Entitlement That Cannot Carry Over Expires

**Status:** Accepted  
**Date:** 2026-09-14  
**Scope:** Disposition of unused entitlement excluded from carry-over

## Context

The user approved expiry at the period boundary for unused entitlement that cannot
carry over, with an auditable ledger entry and a clear employee balance-history
explanation. It is not automatically paid out or moved to another leave type.

## Decision

Expire unused entitlement excluded from carry-over because the policy disables
carry-over, a configured limit is exceeded, or further transfer is prohibited.
Record the amount and reason in an auditable expiry ledger entry and explain them
in the employee's balance history. Preserve prior entries and prevent duplicate
effects on retry. Create no automatic payout or cross-type transfer.

Apply [carry-over options](./0028-policy-carry-over-options.md) and
[repeat-transfer rules](./0029-repeated-carry-over.md) while preserving
[immutable ledger history](./0001-immutable-balance-ledger.md) and
[versioned policies](./0002-versioned-leave-policies.md). This adds a period-boundary
disposition for non-transferred amounts; it does not extend any existing expiry.
The platform's [API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md)
continues to apply.

## Alternatives considered

- Automatically pay out excluded entitlement: not the approved product behavior.
- Move excluded amounts to another leave type: rejected as an automatic action.
- Remove balances without history: rejected; expiry must be auditable and explained.

## Consequences

- The specification includes capped, disabled, and prohibited-repeat examples,
  plus no-payout/no-cross-type-transfer and retry expectations for later tests.
- Outstanding reservations at rollover remain unresolved; this decision does not
  settle their treatment or cancel pending requests.
- Scaffold impact: no scaffold change — application-specific entitlement policy.
- Shared-UI impact: none; no reusable implementation is introduced.
- Agent-context impact: existing deterministic calculation and ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: additive resolution of non-transferred amounts; accepted ADRs unchanged.
- Planning only; Phase 1 readiness and failing acceptance tests precede implementation.
