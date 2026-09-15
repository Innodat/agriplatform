# ADR-0026: Round Prorated Grants Once Using the Policy's Rule

**Status:** Accepted  
**Date:** 2026-09-14  
**Scope:** Fractional-minute rounding of prorated entitlement grants

## Context

The user approved per-policy rounding down, to nearest, or up to a whole minute,
applied once to the final calculated grant. For nearest, exactly half a minute
rounds up. Hourly request increments and exact half-day consumption stay unchanged.

## Decision

Each policy selects down, nearest, or up to a whole minute for prorated grants.
Calculate the grant before rounding; do not round intermediate calculation steps.
Apply the selected rule once to the final calculated amount. Under nearest-minute
rounding, a half-minute tie rounds up.

Apply this rule to [calendar-day proration](./0025-per-policy-calendar-day-proration.md)
within [versioned policies](./0002-versioned-leave-policies.md). Preserve the
calculation and rounding choice in the grant's audit explanation under
[immutable ledger rules](./0001-immutable-balance-ledger.md).

This decision concerns entitlement grants, not request duration: preserve
[30-minute hourly increments and exact 50% half days](./0003-working-time-in-minutes.md).
It does not define a new rule for negative adjustments or cancellation reversals.
The platform's [API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md)
continues to apply.

## Alternatives considered

- Apply one universal rounding mode: the user selected a policy-level choice.
- Round intermediate steps: rejected; rounding occurs once on the final grant.
- Use half-to-even for nearest: the user selected half-minute ties rounding up.

## Consequences

- The specification includes a 481-minute grant prorated by 15/30, producing
  240.5 minutes: down yields 240, nearest and up yield 241. A 240.4-minute example
  distinguishes nearest from up.
- Later tests must verify the selected rule and absence of intermediate rounding.
- Scaffold impact: no scaffold change — application-specific calculation policy.
- Shared-UI impact: none; no reusable implementation is introduced.
- Agent-context impact: existing deterministic calculation and ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: additive rounding clarification; accepted ADRs remain unchanged.
- Planning only; remaining calculation questions and Phase 1 readiness must be
  addressed before implementation, with failing acceptance tests first.
