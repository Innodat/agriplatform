# ADR-0035: Reserve Leave-Date Entitlement Within a Policy Booking Horizon

**Status:** Accepted  
**Date:** 2026-09-14  
**Scope:** Future reservation funding and advance booking

## Context

The user questioned whether booking three years ahead could preserve today's
entitlement and accumulate 60 days. They authorized clarifying that funding follows
the leave dates, with earlier entitlement contributing only through valid permitted
carry-over, and adding a maximum advance-booking horizon per policy.

## Decision

Allocate reservations from entitlement valid on each leave date. Requests for
year 3 may use projected year-3 accrual and valid permitted carry-over; they cannot
preserve otherwise expired year-1 or year-2 entitlement through early submission.
A reservation against future accrual is not current accumulated entitlement and
does not consume today's balance simply because it is submitted today.

Protect existing valid reservations under
[ADR-0032](./0032-protected-reservations-and-explained-changes.md), applying
[date-by-date availability](./0019-date-by-date-future-balance.md),
[carry-over limits](./0028-policy-carry-over-options.md), and
[repeat-transfer rules](./0029-repeated-carry-over.md). A large future request is
funded only if those rules and the employee's schedule support the full amount.

Each policy configures a maximum advance-booking horizon. Check requested dates
against it at submission and reject out-of-window dates with a clear explanation,
even if projected funding is sufficient. The default horizon is not yet selected.
Use [versioned policies](./0002-versioned-leave-policies.md) and the platform's
[API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md).

## Alternatives considered

- Fund every future request from today's balance: rejected; eligibility follows
  when leave is taken.
- Allow early submission to preserve expired entitlement: rejected.
- Permit arbitrarily distant requests based solely on projected balances: use the
  policy's booking horizon as an additional condition.

## Consequences

- The specification includes year-3 funding, a conditional 60-day example, and
  booking-window denial acceptance examples for later executable tests.
- The previously proposed cap treatment of already-earned reserved entitlement
  was not approved by this clarification and remains open. Future-accrual
  reservations must not be confused with current accumulated entitlement.
- Scaffold impact: no scaffold change — application-specific reservation policy.
- Shared-UI impact: none now; booking-limit explanations belong in Leave.
- Agent-context impact: existing deterministic calculation and ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: additive clarification; accepted ADRs remain unchanged.
- Planning only; Phase 1 readiness and failing acceptance tests precede implementation.
