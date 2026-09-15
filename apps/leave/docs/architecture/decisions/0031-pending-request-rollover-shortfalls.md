# ADR-0031: Pending Rollover Shortfalls Warn of Requested Unpaid Leave

**Status:** Accepted  
**Date:** 2026-09-14  
**Scope:** Pending request reservations across entitlement periods

## Context

The user approved reservations not bypassing carry-over limits or extending expiry.
Pending requests with a rollover shortfall stay pending and enter the existing
override/unpaid process. The user additionally requires a UI warning showing the
exact amount that will be requested as unpaid leave.

## Decision

Fund pending new-period requests only from entitlement valid on their leave dates.
Reservations do not override carry-over limits or extend expiry. If rollover
creates a shortfall, retain the request's pending lifecycle state and flag it for
the existing override/unpaid process. Do not silently approve, reject, or cancel it.

Show the employee the exact shortfall as requested unpaid leave, separate from the
funded portion. Use schedule-aware units backed by canonical minutes. For example,
a 120-minute shortfall produces “2 hours will be requested as unpaid leave.” Make
clear this is requested allocation, not a completed approval. Show the warning
when the shortfall is known and update the pending request when rollover changes
funding. Approvers see the same shortfall in existing override review; an authorized
alternative allocation updates the displayed amounts.

Apply [date-by-date availability](./0019-date-by-date-future-balance.md),
[carry-over limits](./0028-policy-carry-over-options.md), and
[expiry of non-carried amounts](./0030-non-carried-entitlement-expiry.md).
Preserve [ledger history](./0001-immutable-balance-ledger.md),
[schedule-aware minutes](./0003-working-time-in-minutes.md), and
[required approval](./0007-required-approval-and-automatic-decisions.md).
The platform's [API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md)
continues to apply.

## Alternatives considered

- Preserve expired or excess entitlement through reservations: rejected.
- Automatically cancel or finalize a shortfall request: rejected; it stays pending.
- Show only a generic insufficient-balance warning: insufficient; the user requires
  the exact amount that will be requested as unpaid leave.

## Consequences

- The specification records a 480-minute request with 360 funded and 120 requested
  unpaid minutes, retaining pending state and showing matching approver amounts.
- Rollover reconciliation must preserve reservation and ledger integrity without
  duplicate effects or automatic final consumption.
- Scaffold impact: no scaffold change — application-specific allocation behavior.
- Shared-UI impact: keep the Leave-specific warning in the application; no shared
  component is introduced by this planning change.
- Agent-context impact: existing authorization, deterministic calculation, and
  ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: additive resolution of pending rollover reservations; accepted ADRs
  remain unchanged. No new application lifecycle state is introduced.
- Planning only; Phase 1 readiness and failing acceptance tests precede implementation.
