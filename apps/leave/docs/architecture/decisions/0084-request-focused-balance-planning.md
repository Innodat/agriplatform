# ADR-0084: Request-Focused Balance Planning for MVP

**Status:** Accepted  
**Date:** 2026-09-19  
**Scope:** Employee balance-planning presentation  
**Supersedes in part:** [ADR-0062](./0062-employee-history-and-balance-views.md), only the standalone future-date balance selector

## Decision

My Leave shows current available and reserved balances with expandable explanations.
Future calculations appear automatically in Apply for the selected leave dates,
showing paid/unpaid allocation and resulting balance. Exploring dates in a draft
neither submits leave nor reserves entitlement. Defer a separate future-date
calculator and balance-over-time graph until demonstrated employee need.

Explain the actual policy consequence of a shortfall: requested unpaid amount
with required acknowledgement, authorized future-entitlement use, or insufficient
leave when the policy disallows the request. A generic negative-balance warning
alone is insufficient. This introduces no new borrowing or override permission.

Retain date-by-date projection under [ADR-0019](./0019-date-by-date-future-balance.md),
reservation protection, expandable calculations, history, and privacy. Calculation
requirements remain; only the standalone planning interface is deferred.

## Consequences

Employees comparing dates change them in their draft. This favors the primary
application task over a separate exploratory interface. Revisit a dedicated
calculator if user research demonstrates a recurring need.

- Scaffold/shared-UI impact: no implementation change; request balance composition belongs to Leave.
- Agent-context impact: no new agent instruction is needed.
- Documentation impact: update feature catalogue, delivery tracker, UX and memlog.
- ADR impact: partially supersedes ADR-0062; its accepted text remains unchanged.
- Planning only; no implementation or readiness completion is authorized.
