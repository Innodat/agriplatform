# ADR-0029: Notification Retry Expiry and Retention

**Status:** Accepted  
**Date:** 2026-09-22  
**Scope:** Notification delivery only, not general business-command idempotency

## Decision

Permit retries of the original notification event for 90 days from its original
server-recorded creation instant. Preserve this instant across handovers and retries;
retrying must not reset the deadline. At the deadline, stop further delivery attempts
and mark unresolved delivery expired, with a reason and retained investigation history.
This maximum recovery window is not a requirement to retry automatically for 90 days;
shorter bounded automatic retry policies and correction-required failures still apply.
Relevance, permissions and current-state checks can stop a notification earlier.

Keep completed, skipped or expired outbox details and attempt history for 90 days
after the terminal transition. Completion means the owning stage finished (for the
producer, confirmed handover), not proof that email was received or read. Expiry is
an explicit terminal delivery outcome, not successful delivery or resolution of the
underlying business issue. Qualify ADR-0024 retained-failure rules for notifications:
expiry may close delivery processing while preserving the evidence for this period.

Retain receiver duplicate-prevention records for at least 90 days after original
acceptance, and longer while associated processing remains unresolved. Delete only
after that period and completed processing. Receivers enforce the original event-age
deadline independently of whether a duplicate record still exists; expired events must
never be treated as fresh work after cleanup. Validate immutable origin/expiry metadata
through the authenticated producer contract. A retry with altered origin metadata must
not bypass duplicate-payload checks. Use UTC instants and consistent boundary tests.
Do not start another outbound attempt after expiry; an already-started remote effect
cannot be assumed recalled merely because the deadline passes.

An exceptional later need is a newly authorized notification based on current state,
with a new event identifier, an explanation and a reference to the original event ID.
Preserve that reference as audit context even if old operational details have expired;
do not require the deleted payload to be retained to create the reference. Check any
available delivery evidence when deciding whether another message is appropriate.
Never repeat the underlying leave or other business action to recreate a notification.

Do not apply these durations automatically to payments, general business-operation
idempotency, business audit, leave history or decision snapshots. Those follow their
own contracts. Delivery expiry/cleanup is routine operational processing; no new
administrator screen or cross-service cleanup coordinator is required.

## Impact and verification

- Acceptance: retry just before/at expiry, unchanged deadline across retries, older
  replay after receiver cleanup rejected, active processing prevents premature cleanup,
  terminal-plus-90-day cleanup, and authorized replacement without repeated domain effects.
- Scaffold: notification-specific configurable defaults and envelope validation where
  proven; do not bake this window into every outbox or generic idempotency helper.
- Shared UI: no new business control; existing delivery/support reporting suffices.
- Agent context: existing identity, audit and delivery safeguards suffice.
- Documentation: shared builder guidance and Leave requirements/tracker synchronized.
- ADR: refines notification failure lifecycle under
  [0024](./0024-durable-delivery-retries-and-audited-recovery.md), retaining
  [0012](./0012-operation-identity-idempotency-and-tracing.md) identity semantics.
- Planning only; no retention jobs, data deletion or notifications executed.
