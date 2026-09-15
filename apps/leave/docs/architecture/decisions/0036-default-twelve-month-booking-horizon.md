# ADR-0036: Default Advance-Booking Horizon Is Twelve Months

**Status:** Accepted  
**Date:** 2026-09-14  
**Scope:** Default booking window

## Context

The user approved a 12-month advance-booking default, configurable per policy,
with every requested leave date inside the window. This controls booking distance
without restricting valid carry-over.

## Decision

Default the maximum advance-booking horizon to 12 months ahead of submission.
Allow each policy to configure its horizon. Require every requested leave date
to be within the permitted window, including the last date; checking only the
first date is insufficient. The cutoff date is included in the window.

Apply the [submission validation](./0035-leave-date-funding-and-booking-horizon.md)
and [employee work timezone](./0023-employee-work-timezone.md) rules. This window
does not shorten entitlement validity or replace
[carry-over rules](./0028-policy-carry-over-options.md). Keep configuration in
[versioned policies](./0002-versioned-leave-policies.md). The platform's
[API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md)
continues to apply.

## Alternatives considered

- A fixed horizon for every policy: the user approved a configurable default.
- Validate only the first leave date: rejected; all requested dates must fit.
- Restrict carry-over validity to the booking horizon: not the approved behavior.

## Consequences

- The specification includes a 14 September 2026 submission with a 14 September
  2027 cutoff and denial of an otherwise funded request ending the following day.
- Calendar arithmetic for cutoff dates absent from the target month/year must be
  deterministic before the booking-validation story passes readiness; accrual-date
  fallback is a separate existing decision.
- Scaffold impact: no scaffold change — application-specific booking policy.
- Shared-UI impact: none; no reusable implementation is introduced.
- Agent-context impact: existing deterministic calculation and ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: additive default selection; accepted ADRs remain unchanged.
- Planning only; Phase 1 readiness and failing acceptance tests precede implementation.
