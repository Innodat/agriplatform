# ADR-0156: Preserve Approval Waiting Clock on Transfer

**Status:** Accepted  
**Date:** 2026-10-22  
**Scope:** Waiting time for an unfinished approval step  
**Complements:** [ADR-0057](./0057-approval-reminder-interval.md),
[ADR-0058](./0058-unanswered-approval-escalation.md),
[ADR-0147](./0147-current-supervisor-routing-and-concise-decision-attribution.md)
and [ADR-0155](./0155-recurring-reminders-and-single-escalation.md).

## Decision

Reassignment preserves the original waiting clock for the same unfinished approval
step. The receiving approver gets an assignment notification immediately through the
existing notification mechanism. The reminder/escalation schedule does not restart.

Example: work transfers after six calendar days unanswered. Notify the new assignee
of the assignment; default seven-day escalation remains due the next day. An already
issued escalation remains visible through reassignment, with current assignment,
without another escalation notice solely because the approver changed.

A different step becoming actionable starts its own clock. This decision concerns
identity of the unfinished required action, not one clock for the entire request.
Preserve completed decisions and fresh-cycle rules. Apply the same principle when
that same unfinished step transfers by authorized manual change, effective supervisor
replacement or temporary return; bind concrete identity transitions before readiness.

## Remaining contracts and impacts

Define exact actionable-start evidence, calendar-day/timezone boundaries, step/cycle
identity and due-work coordination. Absence-policy omission/restoration transitions
and delayed-run catch-up need explicit mapping rather than invented resets. Current
recipient authorization/relevance and L-0155 recurrence remain; notification intent
being created immediately does not promise immediate external delivery.

Verify day-six transfer/day-seven escalation, current receiving approver notifications,
already-escalated transfer without new escalation, and independent next-step clock.
Reference existing worker/retry/transfer suites; no new scheduler or UI control. Update
features, spine, UX, affected Stories 5.24/5.26/5.27 and tracker/handoff/index. Reuse proven
scheduling/notification/activity patterns; promote generic gaps with first consumer.
Existing agent instructions suffice. Accepted predecessors unchanged. Contracts, final
coverage/order/sizing/readiness remain open. No code, runtime tests, migrations, grants,
deployment or implementation authorization.
