# ADR-0062: Employee Year Calendar, History List, and Balances

**Status:** Accepted  
**Date:** 2026-09-15  
**Scope:** Employee history and balance experience

## Context and decision

The user requested leave-taken history and remaining balances per leave type, and
approved a year calendar with a companion list. Show dates, type, duration, and
status in an accessible list, with year selection for historical leave. Distinguish
leave already taken, approved future leave, and pending requests without relying
on colour alone. These are presentation categories, not new lifecycle states.

Show currently available and reserved balances per leave type, plus projected
balance for a selected future date. Let employees open explanations of grants,
leave used, expiry, and adjustments under
[immutable ledger rules](./0001-immutable-balance-ledger.md) and
[date-by-date projection](./0019-date-by-date-future-balance.md).
Keep the existing own-request authorization and
[colleague privacy boundary](./0011-colleague-absence-privacy.md).

Pilot tasks include finding last year's leave taken and identifying available
balances for each leave type. Design and implement the experience before pilot
testing, then refine and retest when observations expose confusion. This does not
claim a full pilot rubric or implementation-readiness pass.

## Consequences

- The specification records historical navigation, accessible details, balance
  projections/explanations, and authorization acceptance examples for later tests.
- Scaffold impact: no implementation now; promote reusable layout/calendar patterns
  only when proven during delivery.
- Shared-UI impact: generic calendar/list primitives may be shared; Leave statuses,
  balances, and calculation explanations remain application-specific.
- Agent-context impact: existing accessibility, authorization, and ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog;
  elaborate layouts and pilot observations during UX planning.
- ADR impact: additive employee-view decision; accepted ADRs remain unchanged.
- Platform alignment: business data stays behind the
  [FastAPI boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md).
- Planning only; Phase 1 readiness precedes implementation.
