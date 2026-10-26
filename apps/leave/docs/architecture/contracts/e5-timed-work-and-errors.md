# E5 timed business work, occurrence identity and safe errors

**Status:** Selected G5 technical contract; runtime and G6/C6 readiness remain open.  
**Date:** 2026-10-25  
**Owners:** Actual Leave timed-work/notification producers and E3 worker infrastructure

Product policy stays in Features and L-0155/0156/0157/0160/0163. This binds their owner
interfaces, not a workflow engine or a new worker service. Leave API and worker share
the Leave release/code owner and run separately under restricted identities. E3 3.23/24
owns actual outbox/handover; 5.23/25/26/27 own their first real timed domain consumers.
No implemented generic worker or notification runtime was found in the inspected service/
builder inventory; referenced owner designs are not proof of running delivery.

## Closed due-work variants

Use one Leave-owned `leave.due_work` representation, introduced only with the first real
expiry consumer 5.23-A and extended by subsequent producers. Fields: UUID id/org/causal_id,
`work_type`, positive `payload_version` initially 1, `due_at` UTC, immutable typed payload,
mutable state pending/claimed/completed/superseded/needs_attention, attempt count,
next_attempt_at, nullable claim token/worker actor/until, last safe outcome code,
creation/update attribution. Payload branch structural checks and scoped actual local
FKs are introduced by the real branch owner. No client-defined work type, arbitrary URL,
SQL, callable name or credentials. Unsupported versions remain retained/flagged, not
marked completed by a new binary that cannot interpret them.

| Work type | Closed v1 payload / actual owner |
| --- | --- |
| `appointment.start` | appointment UUID/revision and exact retained selection/return evidence ref; 5.21-A |
| `appointment.expire` | appointment UUID/revision and exact retained return evidence ref; 5.23-A first, actual 5.21 producer integration |
| `supervisor.return` | request/cycle/step UUIDs, actual absence-source/effective-boundary ref and responsibility/principal binding; 5.25-A |
| `approval.reminder` | request/cycle/step UUIDs and action-clock UUID; 5.26-A |
| `approval.escalate` | request/cycle/step UUIDs and action-clock UUID; 5.27-A |

No standalone appointment-return work type: start/expire owns its reviewed selected work/
conditional return, early end applies its own protected current command. Unique producer
binding is `(org_id,work_type,causal_id)`; exact matching immutable input returns existing
work, changed input is integrity conflict. Appointment causal identity is its stable ID
plus recorded revision/kind represented by a retained producer UUID. Reminder/escalation
causal identity is the actual action clock. Existing per-item selection progress belongs
to the appointment producer; no server-wide batch engine or new task dashboard.

Reminder work may advance next due/state under the same row while payload/clock remains
unchanged; each notification occurrence below has its own durable identity. A superseding
appointment revision records a new retained due-work identity and fences old revision
work; it does not mutate an old immutable payload into another command.

## Claim, execution and recovery baseline

Restricted discovery returns only bounded due item IDs/verified org hints, never a global
business read or arbitrary payload-selected org context. Claim at most 25 items per poll,
with at most one executing per worker initially, ordered due_at then UUID. Establish each
item's authoritative org scope before reading business data, and clear pooled context
between items. Claim transaction uses row contention/skip-locked, creates a fresh claim
token and lease, then commits before remote calls. Discovery/claim credentials cannot
impersonate all organization users or read another owner's tables.

Select initial 30-second maximum idle polling interval and 60-second claim lease; one
attempt is capped at the existing 20-second E5 recovery budget including required remote
reads/current local work, with existing 3-second fact reads and 5-second local transaction
cap. These are initial bounded technical settings, not measured latency/SLA. No lease
extension is needed for an attempt within that budget; exhausted work releases/reschedules
rather than running indefinitely. A claim is not business authority or a long-held DB lock.

At each effect transaction recheck current claim token/unexpired lease and actual target/
revision/lifecycle/authority/source precedence. Use the existing dependency/employee/domain
lock order; no HTTP under those locks. Commit actual domain changes, required local
accounting/evidence/audit/outbound intent and progress/completion together. A stale holder
cannot finalize after another claim, even if its remote read eventually succeeds. A lost
commit response is recovered from actual causal progress/state; it is not an instruction
to repeat previously completed domain effects.

Retry transient failure using existing 30/60/120-second backoff capped at five minutes
with jitter, preserving payload/causal/item identity. Recover expired claims; no delete/
recreate. Definitively obsolete work becomes superseded with safe reason. A genuine no-
destination/coverage issue becomes current attention as its domain owner requires, without
claiming success or extending approval authority. Technical unknown remains recoverable,
not a business rejection. Graceful worker drain is bounded at 30 seconds; stop claims,
finish/rollback bounded active work, preserve supervisor forced-termination evidence and
recover any remaining lease. None of this relaxes current approval checks during worker lag.

## Action clock, recurrence and occurrence identity

Actual first actionable step establishes immutable `action_clock_id`, waiting_since UTC,
clock timezone from the submitted cycle's employee work timezone, and retained cadence/
escalation configuration evidence. Do not require the approver to have employment or a
work timezone. Preserve already calculated due UTC values and their normalization evidence;
a tzdb upgrade must not silently rewrite recorded occurrence history.

Calendar-day interval N is positive whole days. Compute each slot from waiting_since in
that retained timezone plus N local calendar dates at its local time, not N working days
or blindly N times 24 hours. Resolve repeated local time to its earlier instant and a gap
to the first valid instant at/after the intended local time, retaining the resulting UTC
instant; never move the clock to the browser/worker timezone. Enumerate slots by positive
integer `slot_number`, not arrival/order of worker attempts. Escalation has its one original
threshold slot. Source configuration changes use actual reviewed source/cadence rules;
this contract supplies no new UI to silently reschedule an outstanding action.

Same unfinished step transferred, temporarily reassigned or restored retains its established
clock, escalation occurrence and cadence under L-0156. If a restored step has never been
actionable, establish its clock when it first becomes actionable. A different actionable
step has its own clock. Wait for return is no new command/state and does not pause timing.
Completed step clocks are not resurrected when another cycle is explicitly submitted.

Select `leave.approval_occurrence` with scoped UUID id, action_clock/step/cycle/request refs,
kind reminder/escalation, slot number, intended due instant, actual created_at,
actual recipient binding refs and outbound event refs. Unique
`(org_id,action_clock_id,kind,slot_number)` prevents duplicate generation; escalation always
uses slot 1. Claim generation/progress and occurrence/outbox creation in one local protected
transaction, leaving no generated checkpoint without its required intent. No fake human
approval/employee acknowledgement in these records.

When several reminder slots were missed, choose only the latest due slot not already
represented and advance the processed slot checkpoint past earlier slots. Existing pending/
accepted/uncertain occurrence/outbox records remain; skip safely obsolete unhanded items
with retained reason, not deletion. A retry of an existing slot reuses its immutable event,
never a newly dated copy. Do not generate a catch-up if the actual outstanding schedule
already has equivalent recoverable intent. New later scheduled slots are new occurrences;
expired old notification intent is never rejuvenated under its original identity. Single
escalation remains one occurrence per clock, not one per assignee or delivery retry.

Assignment transfer emits its actual assignment notice independently and preserves timing.
It does not retarget an immutable old-recipient reminder under the same event ID or create
another escalation. Leave rechecks current required action/recipient/relevance before
handover; definitive stale unhanded reminder can be skipped, while uncertain/accepted
remote effects cannot be locally recalled. Shared notification delivery does no Leave
workflow calculation. Notification read state changes no clock/assignment/funding/outcome.

## Stable coverage-gap attention identity

5.3 first emits structured actual responsibility/principal/uncovered interval evidence;
5.28-A composes actual live source evidence. Introduce a retained gap identity with its
first real mutation/attention producer, not a bulk E5 schema upfront. One active issue per
`(org_id, responsibility_id, principal_actor_id, absence_source_id)`; keep a UUID identity
while uncovered intervals/appointment references/waiting requests change. `absence_source_id`
is the actual request/cycle or other already supported recorded absence source UUID, not
an invented external person lookup. Exact scoped actual source FK uses its closed branch.
A resolved issue retains historical identity; a new distinct absence/source creates its
own issue. No waiting request or authorized exception alone resolves the same gap.

Gap record/projection exposes actual current source revision/segments, not a permanent
claim from one old scan. Actual source/appointment/member/return changes trigger existing
protected refresh; read failure cannot erase a known gap. No polling view mutation or
separate history/task service. Current owner proof must include gap without waiting work,
partial cover, sequential cover, replacement and source supersession.

## Safe errors and owner result unions

Reuse platform API error/recovery envelope: `error_id` machine discriminator, safe fallback
`error`, optional allowlisted details/operation_id/trace_id. Existing Access/Content legacy
wire stays compatible through actual service adapter mapping, not parsing their English.
No stack traces, raw input/medical notes, service keys, provider URLs or other-owner IDs.
Only include current resource details after actual current resource authorization.

| Existing E5 error family | Closed safe detail fields |
| --- | --- |
| request revision / changed approval steps | request_id UUID, current_revision positive decimal string |
| request not pending | request_id UUID, request_status actual supported lifecycle discriminator |
| correction revision / closed | request_id UUID, correction_id UUID, current_revision positive decimal string and actual correction lifecycle where relevant |
| appointment revision / review changed | appointment_id UUID, current_revision positive decimal string; create review change has no fabricated appointment ID |
| funding / coverage / transfer review changed | request_id UUID and current_revision; changed details are fetched through authorized fresh review, not dumped into an error |
| preference revision | current view calendar/list and current nonnegative decimal-string revision only |
| invalid query/cursor/body | bounded array of allowed field paths plus stable validation codes, never rejected input values |
| auth/denial/not-found/dependency/internal | No business details; existing safe operation/trace refs where applicable |

Existing command contract owns exact identifiers and HTTP mappings; this table constrains
payload details rather than renaming codes. Internal worker outcomes are closed
`applied`, `already_applied`, `superseded`, `retryable`, `needs_attention`,
`unsupported_version`; they are not public request statuses or human decisions. Internal
unsupported work is retained/flagged. Unresolved mutation receipt stays the original
committed/unresolved union; a 500/503/timeout alone never proves noncommit.

## Verification allocation and G5 closure limits

5.23 actual first due worker proves claim expiry/fencing, current authority despite lag,
exact conditional return and transaction/remote separation. 5.21/22 prove real producer
and revision supersession; 5.25 actual ended-absence return; 5.26 slot recurrence/coalescing;
5.27 one escalation/attention; 5.28 live gap projection; E3 3.22–26 actual organization
notification acceptance/handover/delivery/inbox. Reuse core/owner tests, add actual producer
integration rather than repeat the whole suite for every story.

Oracles: crash between occurrence and intent rolls both back; lost receiver response
reuses original immutable event; transfer after six days keeps seventh-day escalation;
three missed reminders yield one latest catch-up, not three; restored established step
does not reset waiting; expired/superseded appointee cannot act before worker cleanup;
stale worker cannot finalize after reclaim; unsupported payload survives release/retry;
known gap with failed facts remains recoverable, not resolved. These are planned tests,
not runtime PASS. G5 design bound together with the explicit shared Leave notification
variant; actual storage/wire/error adapter artifacts and C6 final coverage/order/size remain.
No Leave implementation, runtime tests, migrations, grants or readiness authorization.

## First-use gap representation ownership adopted — 2026-10-25

Accepted 5.28-C now owns the first actual stable gap representation/projection/update
interface and minimum manager visibility. This makes the earlier generic first-producer
allocation explicit. Actual 5.11/12/20/21/22/23/24/25 and relevant source writers retain
protected real gap effect/current-clear/known-unknown evidence and their producer tests.
5.28-A/B only enrich residual actual-source/action composition. Due-work identity/claim/
clock/notification contracts unchanged; no new worker or automatic resolution on GET.
