# ADR-0045: Monthly Policies Choose Start-of-Month or End-of-Month Grants

**Status:** Accepted  
**Date:** 2026-09-14  
**Scope:** Monthly grant timing  
**Supersedes in part:** ADR-0024's freely configured monthly date and ADR-0027's monthly configured-date fallback

## Context

The user approved start-of-month or end-of-month timing per policy, replacing a
freely configured monthly grant date. Partial employment months use the agreed
proration rule.

## Decision

Each monthly policy selects the first or last calendar day of the month for its
grant. Use the employee's configured work timezone and apply the policy's
no-proration or calendar-day-proration choice to partial employment months,
including the agreed final-grant rounding rule.

This supersedes independent monthly dates in
[ADR-0024](./0024-mvp-accrual-schedules.md) and their fallback mechanism in
[ADR-0027](./0027-accrual-date-calendar-fallback.md). Other schedule choices and
historical accepted records remain intact. Annual timing follows
[ADR-0043](./0043-annual-grants-at-period-start.md).
Apply [proration](./0025-per-policy-calendar-day-proration.md),
[rounding](./0026-prorated-grant-rounding.md), and
[idempotent ledger rules](./0001-immutable-balance-ledger.md).
The platform's [API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md)
continues to apply.

## Alternatives considered

- Keep a freely configured monthly date: replaced by start/end choices.
- Require one timing for every policy: the user selected policy configuration.

## Consequences

- The specification includes April/May/February dates, partial-month calculation,
  and retry examples for later executable tests.
- Exact availability during the final calendar day and posting a partial grant
  when employment begins after an upfront grant date still need definition before
  affected stories pass readiness; this decision does not silently alter prior
  effective-date availability rules.
- Scaffold impact: no scaffold change — application-specific accrual timing.
- Shared-UI impact: none now; policy configuration remains in Leave.
- Agent-context impact: existing deterministic calculation and ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: scoped supersession of monthly timing/fallback; accepted originals
  remain unchanged.
- Planning only; Phase 1 readiness and failing acceptance tests precede implementation.
