# ADR-0097: Cumulative Rounding of Complete Monthly Instalments

**Status:** Accepted  
**Date:** 2026-09-22  
**Scope:** Complete monthly instalments of unchanged annual entitlement

## Decision

For complete monthly instalments under an unchanged annual entitlement, calculate
the cumulative scheduled entitlement and floor it to whole minutes. The current
instalment is the difference between this cumulative amount and the previous
cumulative scheduled amount, not a separately rounded annual amount divided by 12.

Example: 19 standard days at 450 minutes gives 8,550 annual minutes. The cumulative
amount after one complete instalment is floor(8,550/12) = 712 minutes. After two
it is 1,425 minutes, so the second instalment contributes 713. After twelve complete
instalments the cumulative scheduled entitlement is exactly 8,550 minutes.

Calculate nominal instalments independently of cap exclusions, consumption and
other balance effects. Apply those effects afterwards in their proper historical
order. Never subtract actual granted/remaining balance from the cumulative nominal
amount to compute the next instalment: doing so could restore capped-out earning
or used leave. Amounts previously excluded by the cap remain excluded.

Partial employment months retain their separate proration rules under
[ADR-0025](./0025-per-policy-calendar-day-proration.md) and final-grant rounding under
[ADR-0026](./0026-prorated-grant-rounding.md). This decision settles twelve complete
instalments with unchanged entitlement; partial-month integration, annual-rate
changes and anniversary-year monthly boundaries remain explicit readiness work.

Apply [annual availability options](./0090-annual-entitlement-availability-options.md)
and preserve [no cap catch-up](./0034-accrual-resumption-after-cap.md).
No worker processing is required to make the cumulative calculation authoritative.

## Consequences

- Acceptance: verify alternating 712/713-minute portions, full 8,550-minute total,
  repeated calculations, and no restoration of cap exclusions or consumed amounts.
- Scaffold/shared UI: Leave-specific calculation; existing policy controls suffice.
- Agent context: existing deterministic calculation and cap rules suffice.
- Documentation: requirements and implementation tracker reference the rule.
- ADR impact: additive; does not replace partial-employment grant rounding.
- Planning only; no calculation implementation or migration.
