# ADR-0155: Recurring Reminders and Single Escalation

**Status:** Accepted  
**Date:** 2026-10-22  
**Scope:** Repetition of unanswered approval reminders and escalation  
**Complements:** [ADR-0057](./0057-approval-reminder-interval.md) and
[ADR-0058](./0058-unanswered-approval-escalation.md).

## Decision

Remind the currently responsible approver every policy-configured reminder interval
while their action remains outstanding. The default is every three calendar days.
Notify the authorized Leave Manager once at the policy-configured escalation threshold,
default seven calendar days. Keep unresolved escalation visible in Needs attention;
continue approver reminders without repeatedly notifying the manager for that same
outstanding approval. Reminder interval and escalation threshold remain configurable.

Current-action selection, stopped/omitted steps, current scope/recipient authorization,
privacy, continued timers while waiting for supervisor return, and unchanged assignment/
outcomes retain their accepted rules. Escalation remains notification, not a new grant
or transfer. Use original event identity for delivery retries; a new scheduled reminder
occurrence differs from a retry of an existing occurrence.

## Remaining contracts and verification

Exact calendar-day anchor/timezone, waiting-time behavior across reassignment, new
step/cycle identity, policy-version applicability, delayed-run catch-up and occurrence
identity/discovery remain explicit open contracts. Do not infer a missed-message burst,
reset rule or new configuration option beyond the agreed interval and threshold.
Verify repeated due reminders and one escalation per outstanding approval using actual
owner worker/outbox/delivery integration, continuing reminders after escalation and
stopping when action no longer required. Reuse existing E3 recovery/relevance/privacy
suite evidence; no new notification transport or workflow engine.

Update features, UX, spine, Stories 5.26/5.27, tracker/handoff and ADR index. Shared
scaffold/UI consume proven scheduling/attention patterns; promote generic gaps with
first consumer. Existing agent instructions suffice. Accepted predecessors unchanged.
Contracts, final coverage/order/sizing/readiness remain open. No code, runtime tests,
migrations, grants, deployment or implementation authorization.
