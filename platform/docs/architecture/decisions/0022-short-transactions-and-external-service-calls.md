# ADR-0022: Short Transactions and External Service Calls

**Status:** Accepted  
**Date:** 2026-09-22  
**Scope:** Platform-wide application and shared-service transaction design

## Decision

Keep database transactions short. By default, do not hold business coordination or
write locks while waiting for external service calls. This applies to applications
and shared services, including services deployed on the same machine.

Perform current authentication and shared authorization checks before entering the
protected business transaction. Inside it, load and validate current domain state,
check domain-specific eligibility, and atomically save business changes, required
audit/evidence and durable outbound intent. Release locks before delivering external
side effects. Use the existing transactional outbox and duplicate-safe delivery
patterns when the external effect must survive a process failure; a best-effort call
after commit alone is insufficient for required delivery.

Notification failures do not undo a committed business action. An action that requires
an external business outcome must represent that outcome honestly (for example as
pending), rather than claim completion before it exists. Use explicit workflow and
recovery semantics where multiple owners participate; a local transaction cannot
roll back a completed remote action.

Moving a call before a transaction does not guarantee its result stays current.
Preserve ADR-0019/0021 authorization boundaries, including fresh authorization for
new execution after delay. For other consequential external inputs, specify validity
and consistency guarantees. Do not replace protected local checks with stale remote
preflight results or bypass the HTTP ownership boundary through cross-service tables.

Exceptions are allowed where the workflow genuinely requires a different arrangement.
Document the concrete need, bounded call/transaction timeouts, concurrency impact,
failure/retry behavior and treatment of external side effects in the owning design.
Use the normal design/delivery review; this principle adds no separate user approval
flow or exception administration UI.

## Impact and verification

- Acceptance: slow/unavailable delivery does not retain business locks; rollback
  cannot produce orphan notification intent; committed intent survives interruption;
  retries are duplicate-safe; required remote outcomes and exceptions are tested.
- Scaffold: promote a proven short-transaction/outbox pattern when delivery implements
  it; do not add network calls to generic transaction helpers or claim current support.
- Shared UI: reuse existing pending/failure/retry patterns; no new control required.
- Agent context: link this platform-wide default in repository instructions.
- Documentation: scaffold guidance and Leave requirements/tracker link this decision.
- ADR: complements 0006, 0012, 0014, 0019 and 0021; accepted originals unchanged.
- Planning only; no runtime, shared service or scaffold implementation changed.
