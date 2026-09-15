# ADR-0029: Policies Choose Once-Only or Repeated Carry-Over

**Status:** Accepted  
**Date:** 2026-09-14  
**Scope:** Further rollover of carried entitlement

## Context

The user approved per-policy once-only or repeated carry-over. Existing expiry
dates stay unchanged in both cases; rolling over never extends them.

## Decision

Each policy chooses once-only or repeated carry-over. Under once-only, a portion
already carried into one period cannot transfer into another. Under repeated
carry-over, eligible unused carried entitlement may transfer again, subject to
the policy's carry-over limit. Preserve any existing expiry date on transferred
entitlement; further rollover does not restart its validity.

Apply the [carry-over options and limits](./0028-policy-carry-over-options.md),
[inclusive expiry](./0021-inclusive-entitlement-expiry-date.md), and
[earliest-expiry allocation](./0020-earliest-expiry-entitlement-allocation.md).
Preserve [immutable ledger history](./0001-immutable-balance-ledger.md) and
[versioned policies](./0002-versioned-leave-policies.md). The platform's
[API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md)
continues to apply.

## Alternatives considered

- Always prohibit or always permit further carry-over: the user selected a
  policy-level choice.
- Extend expiry whenever entitlement rolls over: rejected; existing expiry stays.

## Consequences

- Track carried-portion provenance so once-only policies can exclude previously
  carried entitlement from further transfer without rewriting history.
- The specification includes once-only, repeated, limit, and unchanged-expiry
  acceptance examples for later executable tests.
- Outstanding reservations and disposition of non-transferred portions still need
  sufficient definition before affected rollover stories pass readiness.
- Scaffold impact: no scaffold change — application-specific entitlement policy.
- Shared-UI impact: none; no reusable implementation is introduced.
- Agent-context impact: existing deterministic calculation and ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: additive resolution of repeated carry-over; accepted ADRs unchanged.
- Planning only; this decision does not pass the full readiness gate.
