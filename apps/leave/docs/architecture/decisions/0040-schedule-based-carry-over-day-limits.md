# ADR-0040: Convert Carry-Over Day Limits Using the Effective Standard Day

**Status:** Accepted  
**Date:** 2026-09-14  
**Scope:** Conversion of day-denominated carry-over limits

## Context

The user approved converting day limits using the employee's configured standard
working-day duration effective at rollover, recording the conversion, and retaining
the carried amount when the employee's schedule later changes.

## Decision

Multiply the configured carry-over day limit by the employee's configured standard
working-day duration effective at rollover to obtain the canonical-minute limit.
Save the day limit, standard-day duration, effective schedule context, and converted
minute limit in the audit record. Apply the limit to unused eligible entitlement;
it is not a new entitlement grant. Later schedule changes do not rewrite that
rollover's carried amount.

Apply [carry-over options](./0028-policy-carry-over-options.md),
[canonical minutes and schedule snapshots](./0003-working-time-in-minutes.md),
[immutable history](./0001-immutable-balance-ledger.md), and
[versioned policies](./0002-versioned-leave-policies.md).
The platform's [API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md)
continues to apply.

## Alternatives considered

- Assume eight hours for every employee: rejected; use the employee's configuration.
- Recalculate historical carry-over after schedule changes: rejected; retain the
  conversion effective at rollover.

## Consequences

- The specification includes five-day limits of 2,400 minutes for an eight-hour
  standard day and 1,800 minutes for a six-hour standard day, plus snapshot checks.
- How to configure the standard-day value for variable-length schedules still
  needs definition before affected stories pass readiness.
- Scaffold impact: no scaffold change — application-specific entitlement conversion.
- Shared-UI impact: none; no reusable implementation is introduced.
- Agent-context impact: existing deterministic calculation and ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: additive day-limit conversion; accepted ADRs remain unchanged.
- Planning only; Phase 1 readiness and failing acceptance tests precede implementation.
