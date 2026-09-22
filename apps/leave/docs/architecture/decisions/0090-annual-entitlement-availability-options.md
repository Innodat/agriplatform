# ADR-0090: Annual Entitlement and Availability Options

**Status:** Accepted  
**Date:** 2026-09-21  
**Scope:** MVP entitlement policy and calculation direction  
**Supersedes in part:** ADR-0024's three-mode MVP scope; ADR-0001 only insofar as automatic earned entitlement requires separately posted accrual entries

## Decision

Configure an annual entitlement for automatically accruing policies and choose
when it becomes available:

- Earned daily: earn the annual amount proportionally across eligible calendar days
  of the leave year, using its actual length. No second-by-second earning.
- Available upfront: available at the leave-period start, retaining applicable
  joining/leaving proration rules.
- Monthly instalments: release portions of the annual amount at the policy-selected
  start or end of each calendar month. An 18-day annual amount gives 1.5 days per
  complete monthly instalment before other applicable rules.

Retain manual-only authorized grants separately. Types without a tracked balance
are a distinct concept, not a manual grant schedule. Defer actual-hours-worked,
weekly/payroll-cycle and second-level accrual until demonstrated client need.

The backend calculates entitlement authoritatively on demand for the relevant date.
Availability does not depend on a worker having posted periodic accrual entries.
Keep immutable actual balance events, versioned calculation inputs and recorded
request/decision snapshots so historical results remain explainable. Do not create
a competing frontend policy calculator. Automatic entitlement may be derived;
posting it as well must never count it twice. Any cached/materialized projection
is subordinate to the authoritative calculation.

Retain [immutable history](./0001-immutable-balance-ledger.md),
[policy versions](./0002-versioned-leave-policies.md),
[monthly timing](./0045-monthly-grant-start-or-end.md), existing caps, expiry,
protected reservations and cancellation-recalculation safeguards. A simple annual
amount times elapsed fraction is insufficient when these historical events apply.
No protected reservation or recorded approval is silently rewritten.

## Remaining decisions before affected story readiness

- Daily effective boundary, joining/leaving inclusivity and work-timezone examples.
- Fractional-minute precision and cumulative rounding without daily loss or annual
  drift; reconcile existing final-grant rounding with derived accrual.
- Monthly instalments for anniversary periods and changes in annual entitlement.
- Deterministic cap/expiry/reservation replay and historical correction behavior.
- Concrete event/snapshot/projection representation and bounded calculation cost.

## Consequences

- Scaffold/shared UI: application-specific calculation and policy editor changes;
  existing platform primitives suffice, no shared accrual engine.
- Agent context: existing deterministic calculation and history rules suffice.
- Documentation: requirements, tracker and UX contract updated; existing visual
  examples require follow-up for the added daily choice and annual-amount wording.
- ADR impact: scoped supersession; accepted originals remain unchanged.
- Planning only; calculation readiness remains pending and no worker removed.
