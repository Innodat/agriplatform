# ADR-0085: Period-Relative Carry-Over Expiry

**Status:** Accepted  
**Date:** 2026-09-20  
**Scope:** Carry-over expiry configuration

## Decision

For enabled carry-over, offer Does not expire or Expires after a configured number
of months from the new leave-period start. Show the resulting last usable date.
A three-month window from 1 January is usable through 31 March; from 1 July,
through 30 September. Three months is illustrative, not a default.

Use the applicable calendar-year or employment-anniversary period rather than an
annually maintained fixed date. Preserve inclusive expiry and the rule that
repeated carry-over never extends an existing expiry. This refines the input for
[ADR-0028](./0028-policy-carry-over-options.md), retaining
[ADR-0029](./0029-repeated-carry-over.md) and
[ADR-0042](./0042-entitlement-period-basis.md).

## Consequences

- Month-end and leap-day anniversary arithmetic need explicit deterministic
  examples before implementation readiness; the two first-of-month examples do
  not settle those edge cases.
- Scaffold/shared-UI impact: no implementation; domain-specific policy input.
- Documentation impact: synchronize policy UX, product truth, tracker and memlog.
- Agent-context impact: existing deterministic-calculation instructions suffice.
- ADR impact: additive refinement; accepted ADR text remains unchanged.
- Planning only; no runtime changes or readiness completion.
