# ADR-0025: Policies Choose Calendar-Day Proration or No Proration

**Status:** Accepted  
**Date:** 2026-09-14  
**Scope:** Partial employment periods

## Context

The user approved each policy choosing no proration or calendar-day proration for
employees joining or leaving partway through a period, including first and last
employment dates. Manual-only grants remain explicit amounts. Different leave
types can have different versioned policies.

## Decision

For scheduled entitlement, each policy selects no proration or calendar-day
proration. For the latter, multiply the configured period entitlement by calendar
days employed within the period divided by total calendar days in that period.
Count first and last employment dates inclusively, limited to the period.
No-proration policies retain the configured period amount for otherwise eligible
employees. Manual-only grants remain explicit authorized amounts.

Apply these choices within [versioned policies](./0002-versioned-leave-policies.md)
and the [MVP grant schedules](./0024-mvp-accrual-schedules.md), preserving
[immutable history](./0001-immutable-balance-ledger.md) and
[canonical minutes](./0003-working-time-in-minutes.md). This does not change
eligibility or authorize silent reversal of past grants. The platform's
[API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md)
continues to apply.

## Alternatives considered

- One universal proration rule: the user selected per-policy configuration.
- Prorate by working days: calendar days were selected for this calculation.
- Automatically prorate manual grants: explicit amounts were retained.

## Consequences

- The specification includes a 15-of-30-day example with a 480-minute grant,
  yielding 240 minutes when prorated and 480 without proration.
- Fractional-minute rounding and reconciliation when employment dates change after
  a grant still need definition before affected stories pass readiness.
- Scaffold impact: no scaffold change — application-specific calculation policy.
- Shared-UI impact: none; no reusable implementation is introduced.
- Agent-context impact: existing deterministic calculation and ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: additive resolution of proration; accepted ADRs remain unchanged.
- Planning only; Phase 1 readiness and failing acceptance tests precede implementation.
