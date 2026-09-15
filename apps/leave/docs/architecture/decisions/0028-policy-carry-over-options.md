# ADR-0028: Policies Configure Carry-Over Limits and Expiry

**Status:** Accepted  
**Date:** 2026-09-14  
**Scope:** Carry-over between entitlement periods

## Context

The user approved policy choices of no carry-over, all unused eligible entitlement,
or carry-over up to a configured limit. Each policy also determines whether carried
entitlement expires and, if so, when.

## Decision

Support those three carry-over options per policy and configurable expiry for
carried entitlement. Apply [inclusive expiry](./0021-inclusive-entitlement-expiry-date.md)
and [earliest-expiry allocation](./0020-earliest-expiry-entitlement-allocation.md)
to carried portions. Preserve [versioned policies](./0002-versioned-leave-policies.md),
[immutable ledger history](./0001-immutable-balance-ledger.md), and
[schedule-aware canonical minutes](./0003-working-time-in-minutes.md).
Carry-over must not duplicate entitlement. A day-based limit must not assume a
universal eight-hour day.

The example of five days expiring on 31 March illustrates a possible configuration;
it is not a mandatory default. The platform's
[API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md)
continues to apply.

## Alternatives considered

- One universal carry-over rule: the user selected per-policy configuration.
- Require every carried portion to expire: the user approved optional expiry.

## Consequences

- The specification includes no/all/capped carry-over and expiry acceptance
  examples for later executable tests.
- Outstanding reservations at rollover, repeated carry-over of earlier carried
  portions, and conversion of day limits still require explicit rules before
  affected stories pass readiness.
- Scaffold impact: no scaffold change — application-specific entitlement policy.
- Shared-UI impact: none; no reusable implementation is introduced.
- Agent-context impact: existing deterministic calculation and ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: additive carry-over decision; accepted ADRs remain unchanged.
- Planning only; this resolves carry-over options, not the full readiness gate.
