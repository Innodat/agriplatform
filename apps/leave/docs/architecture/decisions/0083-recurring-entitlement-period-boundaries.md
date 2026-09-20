# ADR-0083: Recurring Entitlement Changes at Leave-Period Boundaries

**Status:** Accepted  
**Date:** 2026-09-19  
**Scope:** MVP employee recurring entitlement overrides

## Decision

Creating, changing or ending a recurring employee entitlement override, including
returning to policy entitlement, takes effect only at a leave-period boundary.
Default to the next boundary under the applicable policy. Calendar-year and
employment-anniversary periods follow [ADR-0042](./0042-entitlement-period-basis.md);
monthly accrual does not turn each month into a leave-period boundary.

Overrides continue until explicitly changed, with no automatic end date in MVP.
For an immediate balance change, use a separately authorized one-off adjustment
with reason, impact review and existing acknowledgement safeguards. Do not reset
current balance to a recurring allowance or silently recalculate historical grants.

Example: changing a calendar-year recurring allowance from 20 to 25 days in
September takes effect next January. An immediate additional allocation requires
an explicit adjustment; that adjustment does not change recurring entitlement.

## Consequences and alternatives

Allowing arbitrary midperiod recurring dates was considered and deferred because
it needs additional prospective accrual and proration rules. An immediate
contractual change may therefore require both an adjustment and a scheduled
recurring change. Period boundaries follow the policy, not a universal January date.

- Scaffold/shared-UI impact: no implementation change; this date constraint belongs to Leave.
- Agent-context impact: existing planning and deterministic-calculation rules suffice.
- Documentation impact: synchronize product truth, tracker, UX and decision log.
- ADR impact: additive constraint referencing ADR-0042; accepted ADR text remains unchanged.
- Planning only; this decision does not authorize implementation or close readiness.
