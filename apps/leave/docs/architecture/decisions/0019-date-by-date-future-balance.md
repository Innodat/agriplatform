# ADR-0019: Assess Future Leave Balances on Each Requested Date

**Status:** Accepted  
**Date:** 2026-09-14  
**Scope:** Future-request balance projection

## Context

The user approved checking availability on each requested leave date, accounting
for accrual earned by then, entitlement expiring before then, and existing
reservations. A multi-date request must remain affordable throughout; shortfalls
follow the agreed override and unpaid-leave rules.

## Decision

Project availability for every requested leave date. Include accrual earned by
that date, exclude entitlement expired before that date, and account for other
requests' reservations. Carry forward the candidate's earlier-date consumption
inside the projection; do not reuse the same entitlement across its dates.

Do not treat a request as fully funded solely because it is affordable on its
first date. Later accrual cannot retrospectively fund an earlier shortfall.
Apply the existing insufficient-balance override and unpaid-allocation rules to
any shortfall; this decision does not introduce an unconditional submission block
or a new approval permission.

Preserve [immutable ledger history](./0001-immutable-balance-ledger.md),
[versioned policy snapshots](./0002-versioned-leave-policies.md), and
[canonical minutes](./0003-working-time-in-minutes.md). This is a Leave-domain
calculation decision, implemented within the platform's
[API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md).

## Alternatives considered

- Check only the first leave date: misses expiry and funding changes during a
  multi-date request.
- Use accrual earned after a requested date to fund that earlier date: conflicts
  with availability as of each leave date.
- Ignore pending reservations: permits competing requests to spend the same
  entitlement.

## Consequences

- The specification includes worked accrual, expiry, and competing-reservation
  examples, with shortfalls expressed in minutes for later acceptance tests.
- R3 is partially resolved. Supported accrual/proration/rounding options,
  entitlement allocation priority, and same-date accrual/expiry ordering remain
  unresolved before affected calculation stories pass readiness.
- Scaffold impact: no scaffold change — application-specific calculation rules.
- Shared-UI impact: none; no reusable implementation is introduced.
- Agent-context impact: existing deterministic calculation and ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: additive projection decision; accepted ADRs remain unchanged.
- Planning only; Phase 1 readiness and failing acceptance tests must precede
  implementation of the affected behavior.
