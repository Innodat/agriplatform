# ADR-0063: Employee Home Screen Prioritizes Applying and Required Actions

**Status:** Accepted  
**Date:** 2026-09-15  
**Scope:** Employee landing experience

## Decision

The user approved an employee home screen containing:

- An obvious Apply for leave action.
- Balance summaries by leave type.
- Pending requests and anything needing the employee's response.
- Upcoming approved leave.
- A link to the year calendar and full history.

Scope the content to the employee's active NGO and existing permissions. Use
[history and balance views](./0062-employee-history-and-balance-views.md) and retain
the distinction between [notification reading and business actions](./0056-notification-read-state.md).
Data access follows the platform's
[API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md).

## Consequences

- The specification includes a home-screen navigation and required-action example
  for UX planning and later acceptance testing.
- Scaffold impact: no implementation now; promote proven generic layout patterns
  in the same delivery item when appropriate.
- Shared-UI impact: generic shell/cards may be shared; Leave balances and required
  actions remain application-specific.
- Agent-context impact: existing authorization, accessibility, and ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog;
  elaborate responsive layouts during UX planning.
- ADR impact: additive home-screen decision; accepted ADRs remain unchanged.
- Planning only; Phase 1 readiness precedes implementation.
