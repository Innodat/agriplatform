# ADR-0024: MVP Supports Annual, Monthly, and Manual-Only Grants

**Status:** Accepted  
**Date:** 2026-09-14  
**Scope:** Supported MVP entitlement-grant schedules

## Context

The user confirmed that annual upfront, monthly, and manual-only options cover
the NGOs' MVP needs. Joining or leaving partway through a period requires a
separate proration rule.

## Decision

Each leave policy can choose:

- Annual upfront: grant configured entitlement on a configured annual date.
- Monthly: grant a configured portion each month.
- Manual only: authorized staff grant entitlement with an audited reason; no
  automatic scheduled grants.

Apply existing balance-adjustment authorization and mandatory reasons to manual
grants. All grants preserve [immutable, idempotent ledger behavior](./0001-immutable-balance-ledger.md)
and [versioned policy configuration](./0002-versioned-leave-policies.md).
Scheduled entitlement becomes usable under
[effective-date availability](./0022-accrual-effective-date-availability.md) and
[employee work timezone](./0023-employee-work-timezone.md) rules.
The platform's [API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md)
continues to govern business-data authorization.

## Alternatives considered

- Require one universal accrual schedule: the user confirmed policy-level choice
  among these three options.
- Add more schedule types now: these three cover the confirmed MVP needs.

## Consequences

- The specification records each schedule's behavior, retry deduplication, and
  manual-grant authorization/reason acceptance examples for later executable tests.
- This resolves the MVP schedule set. Proration for partial periods, rounding, and
  calendar edge cases for configured grant dates still need sufficient definition
  before affected calculation stories pass readiness.
- Scaffold impact: no scaffold change — application-specific entitlement policy.
- Shared-UI impact: none; no reusable implementation is introduced.
- Agent-context impact: existing deterministic calculation and ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: additive resolution of supported schedules; accepted ADRs unchanged.
- Planning only; Phase 1 readiness and failing acceptance tests precede implementation.
