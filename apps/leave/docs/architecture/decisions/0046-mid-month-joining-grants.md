# ADR-0046: Initial Monthly Grants for Mid-Month Joiners

**Status:** Accepted  
**Date:** 2026-09-14  
**Scope:** First grant under monthly accrual policies

## Context

The user approved an employment-start grant for employees joining after an upfront
monthly grant date, with normal grants resuming on subsequent month starts.
Month-end policies wait until month-end for the initial grant.

## Decision

Under a start-of-month policy, issue the initial grant on the employment start date
when an employee joins after that month's grant date. Use the policy's agreed
partial-month proration and rounding rules. Resume normal grants on the first of
each following month. Under an end-of-month policy, issue the initial grant at
month-end using the applicable partial-month rules.

Apply [monthly timing](./0045-monthly-grant-start-or-end.md),
[policy proration](./0025-per-policy-calendar-day-proration.md),
[grant rounding](./0026-prorated-grant-rounding.md), and
[cap rules](./0033-optional-accumulated-balance-cap.md). Preserve
[idempotent ledger history](./0001-immutable-balance-ledger.md) and existing eligibility.
The platform's [API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md)
continues to apply.

## Alternatives considered

- Delay an upfront-policy joiner's first grant until the following month: the user
  selected an employment-start grant.
- Grant immediately for month-end policies too: rejected; these wait until month-end.

## Consequences

- The specification includes a 16 April joiner receiving 240 of 480 minutes under
  calendar-day proration, with initial and subsequent dates for both policy modes.
- The joining grant must not duplicate the regular grant for that employment month.
- Scaffold impact: no scaffold change — application-specific accrual policy.
- Shared-UI impact: none; no reusable implementation is introduced.
- Agent-context impact: existing deterministic calculation and ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: additive joining-grant detail; accepted ADRs remain unchanged.
- Planning only; Phase 1 readiness and failing acceptance tests precede implementation.
