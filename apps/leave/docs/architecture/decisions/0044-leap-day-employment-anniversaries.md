# ADR-0044: Leap-Day Anniversaries Fall on February 28 in Non-Leap Years

**Status:** Accepted  
**Date:** 2026-09-14  
**Scope:** Employment-anniversary entitlement periods

## Context

The user approved using 28 February in non-leap years for an employee who started
on 29 February, returning to 29 February in leap years. That date starts the new
entitlement period and triggers any annual upfront grant.

## Decision

Resolve a 29 February employment anniversary to 28 February in non-leap years and
29 February in leap years. Preserve the original employment start date and derive
each year's anniversary independently. The resolved anniversary starts the new
period; the preceding period ends the day before it, without gaps or overlaps.

Apply [period definitions](./0042-entitlement-period-basis.md),
[annual period-start grants](./0043-annual-grants-at-period-start.md), and
[employee work timezone](./0023-employee-work-timezone.md) rules.
Preserve [idempotent grant history](./0001-immutable-balance-ledger.md) and use the
platform's [API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md).

## Alternatives considered

- Use 1 March in non-leap years: the user selected 28 February.
- Permanently move anniversaries to 28 February: rejected; leap years return to
  the original 29 February date.

## Consequences

- The specification includes the 2025 fallback and a 28 February 2027 through
  28 February 2028 period followed by a 29 February 2028 start.
- Test period continuity and one annual grant per resolved period start.
- Scaffold impact: no scaffold change — application-specific period policy.
- Shared-UI impact: none; no reusable implementation is introduced.
- Agent-context impact: existing deterministic calculation and ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: additive anniversary clarification; accepted ADRs remain unchanged.
- Planning only; Phase 1 readiness and failing acceptance tests precede implementation.
