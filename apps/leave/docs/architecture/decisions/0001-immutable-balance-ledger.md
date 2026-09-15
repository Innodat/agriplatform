# ADR-0001: Immutable Leave Balance Ledger

**Status:** Accepted  
**Date:** 2026-09-01  
**Scope:** Leave domain

## Context

Accrual, reservations, approval, rejection, cancellation, expiry, manual changes,
unpaid leave, and exceptional paid grants all affect balances. A mutable balance
column cannot explain its history reliably and is vulnerable to retry/concurrency
errors.

## Decision

Derive balances from immutable, tenant-scoped ledger entries. Corrections and
reversals create compensating entries rather than editing history. Scheduled jobs
and commands use idempotency keys. Current, reserved, used, and projected balances
are reproducible from ledger entries and effective-dated policy data.

Exceptional requests use explicit allocation lines, allowing duration to be split
across an ordinary balance, a discretionary paid grant, another eligible paid leave
balance, and unpaid leave.

## Alternatives considered

- Store and update one balance total per employee/type
- Recalculate exclusively from approved applications
- Edit historical transactions when policies change

## Consequences

- Complete balance explanations and point-in-time reporting are possible.
- Reversal, reconciliation, and invariant tests are mandatory.
- Ledger volume and query projections require appropriate indexes/read models.
- Employee entitlement overrides cause explicit adjustments, never silent history edits.

## Related platform decisions

- [FastAPI/OpenAPI boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md)

