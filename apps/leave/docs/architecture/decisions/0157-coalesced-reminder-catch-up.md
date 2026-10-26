# ADR-0157: Coalesced Reminder Catch-Up

**Status:** Accepted  
**Date:** 2026-10-22  
**Scope:** Recovery of timed approval reminders after technical interruption  
**Complements:** [ADR-0116](./0116-owned-outbox-and-obsolete-notification-intent.md),
[ADR-0155](./0155-recurring-reminders-and-single-escalation.md) and
[ADR-0156](./0156-preserve-approval-waiting-clock-on-transfer.md).

## Decision

After technical interruption, produce at most one catch-up reminder per outstanding
approval instead of a notification for every missed reminder interval. Resume the normal
schedule. If the single escalation threshold was also missed, generate its authorized
manager notice once. Completed or obsolete work receives neither under existing rules.
Example: missed day-three/six/nine occurrences recover on day ten as one approver
reminder, plus the previously missed manager escalation if still applicable.

Business-change notifications remain atomic with their originating change. Timed
reminders can become due without a request change. Their due-work discovery/scheduling
must be durable, but the exact durable representation/generation transaction is an open
contract, not a presumption that all future recurring notifications are precreated on
submission. Recording a business change without its required notification intent is
not authorized by this decision.

Retain the outbox and existing event identities; never clear/recreate it for catch-up.
The Leave-owned worker applies Leave relevance/current-assignment checks before handover
to shared delivery. Shared delivery owns transport, not Leave workflow interpretation.
Already generated items use existing records and identity. Safely superseded unhanded
reminders may be marked skipped with reason/history retained. Coordinate generation
and existing outbox work so recovery does not add a catch-up duplicate to pending work.
Uncertain or accepted handover is not definitely unsent and cannot be recalled locally.
This reduces obsolete notifications; it does not guarantee recall or eliminate races.

## Remaining contracts and impacts

Bind due discovery, occurrence identity/checkpoint, missed-run coalescing against existing
outbox/claims, next due schedule, original waiting clock and accepted/uncertain handover
outcomes. Do not silently discard factual business notices. Verify delayed generation,
already-generated pending reminders, due escalation, completed/transferred work and
concurrent recovery using actual E3 notification/Leave scheduling integration. Generic
transport retries remain owned by E3; catch-up is not a new delivery engine.

Update features/spine/UX/Stories 5.26/5.27, tracker/handoff/index. Reuse proven owner worker/
outbox/notification patterns, promoting generic gaps with first consumer. Existing agent
instructions suffice. Accepted predecessors unchanged. Contracts, final source/test coverage,
dependency order, sizing/readiness remain open. No code, runtime tests, migrations,
grants, deployment or implementation authorization.
