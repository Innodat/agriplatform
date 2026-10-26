# E3 request accounting interface consumed by E5

E6 consumer proposal, 2026-10-25: the
[E6 correction contract](e6-corrections-and-consequences.md) allocates a distinct
approved-cancellation reversal adapter/event and atomic linked replacement. E3 remains
the owner of replay, source provenance, event ordering and immutable evidence. Consumed
commitments are never reset to active/released. The E6 extension awaits package review;
no implemented event type or accepted E5 boundary is changed by this reference.

**Status:** Concrete planning baseline; no runtime schema or readiness claim  
**Date:** 2026-10-23  
**Owners:** Leave E3 accounting/allocation owner and E5 commitment consumer

Refines E3 3.9/3.17-A/3.18 and accepted E5 5.8-A. Product rules remain in Features,
L-0001/0106/0110/0111/0129 and the spine. The [E5 contract](e5-request-command-and-finalization.md)
owns command/guard/lifecycle composition. This is one narrow owner interface, not a second
ledger, feature specification or runtime service. Names below are selected design names;
no existing Leave tables are claimed.

## Immutable request effects in the existing ledger design

Use E3's `leave.balance_event` and `leave.balance_event_line` design for immutable actual
accounting. E3 3.9 creates only its needed original event representation; 5.8-A adds the
request-specific columns/types/references when actual request state exists. Do not require
E3 to depend on future E5 request tables or pre-create request entities in E3.

| Request effect event field | Required representation / constraint |
| --- | --- |
| `id`, `org_id`, `employment_id`, `leave_type_id` | UUIDs; actual scoped source/type identities, creation attribution under P-0025 |
| `sequence` | Positive bigint, allocated by E3's serialized employee event order, not client time |
| `event_kind`, `payload_version` | Closed request branch: `request.reserve`, `request.consume`, `request.release`; payload version 1 |
| `request_id`, `cycle_id`, `commitment_id` | Non-null UUIDs for this branch, scoped FK to actual E5 commitment/cycle when the request extension activates |
| `causal_id` | Original parent operation or stable durable-work UUID; identity of actual execution, not an arbitrary fresh retry UUID |
| `allocation_evidence_id` | Scoped retained immutable calculation/allocation evidence under L-0111; no raw request note/reason copied here |
| `effective_date`, server recorded UTC time | Distinct E3 business ordering/date basis and actual recording time; affected leave dates are preserved on lines |

Use unique `(org_id,commitment_id,causal_id,event_kind)` for the request effect branch,
plus unique `(org_id,employment_id,sequence)` in the E3 event order. Actual request/cycle/
employment consistency is enforced through scoped local references. Generic source branches
retain their own typed shapes; nullable request columns cannot accidentally satisfy the
request-branch check. Do not add a separate transition/effect journal beside these events.

Each `balance_event_line` has `id` UUID, scoped `event_id`, positive `ordinal`, `leave_date`,
`source_leave_type_id`, `portion_key` and positive `minutes` bigint. Unique scoped event/
ordinal and event/date/source-type/portion keys reject duplicate contributions. Preserve
E3's original source-period provenance and retained input versions in the linked immutable
allocation evidence. `portion_key` is the allocator's opaque stable canonical identity,
nonempty and at most 512 UTF-8 bytes; not a mutable label or newly generated ID on replay.
E3 3.18 owns its deterministic construction and tie ordering; that allocator interface
must be delivered before this consumer. A client cannot submit a trusted portion key.

One request effect event may contain multiple dates/portions. Settle the exact active
allocation lines rather than silently calculating a different plan. Only real paid
entitlement contributions create positive amount lines. An entirely unpaid tracked request
has zero amount lines; its real lifecycle/evidence remains explicit. Untracked policies
create no entitlement event/commitment. Actual usage/classification evidence remains with
the owning request workflow rather than fictitious paid accounting.

## Current commitment head and settlement invariants

5.8-A introduces `leave.request_commitment`: UUID `id`, organization/employment/request/
cycle/type UUIDs, positive bigint `revision`, `state` active/consumed/released, current
`allocation_evidence_id`, and server creation/update attribution. Enforce unique
`(org_id,request_id,cycle_id)` plus a scoped unique key including employment/id for event
references. Cycle reference belongs to its actual request; type/evidence links use the
actual local predecessor keys. No mutable balance total is authoritative history.

Reserve inserts the head, immutable reserve event and lines together. Consume/release
condition the head transition on active state and expected revision, append their actual
immutable event and apply E3 accounting semantics atomically. Reserve reduces available
funding without consumption; consume removes that reservation and records one actual
paid deduction; release frees the reservation without a paid grant. Never sum reserve
and consume as two deductions. Current head state can accelerate coordination, but balance
replay remains reproducible from immutable events and retained policy/allocation history.

A settled head cannot return to active. Same causal effect returns its original outcome;
a different causal identity cannot settle it again. Existing actual reallocation writers
later append their own reviewed allocation/evidence effects to the same representation;
they do not edit prior event lines. Approved cancellation is a distinct E6 reversal,
not a permitted consumed-to-released update.

Runtime uses forced org RLS and verified API domain scope, immutable event/line protection,
controlled attribution and safe named-constraint mapping. One caller transaction contains
head/event/line/calculation/audit/outcome/intent and the request's promised state changes.
Actual source portion validity, allocator conservation and event/head correspondence are
protected owner-write invariants; foreign keys alone do not establish them. Duplicate
uniqueness failure rolls back the complete losing transaction before permitted recovery.

## Sizing and verification inputs

This closes the request-side field/line/effect uniqueness shape. The E3 allocator's opaque
portion construction and retained evidence physical schema remain explicit predecessor
interfaces; 5.8-A must not design another allocator to compensate for missing delivery.
All request-side amounts are integer minutes; JSON serializes bigint counters/minutes as
canonical decimal strings. Dates are ISO date-only; timestamps are UTC RFC3339. No float
rounding or localized text matching.

5.8-A verifies reserve/consume/release, immediate reserve+consume, exact/different causal
retries, both competing settlement orders, wrong scope/cycle/portion, tracked zero/untracked,
rollback after each effect stage, immutability, event-order/line uniqueness and actual guard
contention/restart. E3 independently verifies replay/no-double-count and portion construction;
actual submit/finalization/withdrawal producers verify their real domain envelopes. These
are planned oracles, not existing tests/commands/PASS. Exact migration/constraint identifiers,
fixture paths and runtime commands bind with the actual package rather than fabricated files.

No duplicate UI/service/agent policy or accepted ADR change. Scaffold reuses actual E3/C
owner transaction/evidence primitives; no generic accounting engine. Planning only: no code,
tests, grants, migrations or deployment. Final coverage and readiness remain open.


## Later exceptional-allocation consumer extension — 2026-10-23

Actual 5.13-A owns the [C5 reviewed replacement/grant extension](e5-capabilities-and-commands.md#exceptional-allocation-and-combined-approval-command-models--2026-10-23).
It appends request.reallocate with previous/revised allocation evidence and explicit
release/reserve contribution roles, preserving positive line amounts and immutable prior
history. Request-specific discretionary grant is an actual E3 source/effect under its
original causal identity. One current commitment head remains; no consumed-to-active reset,
second ledger or silent addition to 5.8-A's three-effect foundation. Exact E3 type/model/
constraint adapters evolve with this real consumer and its conservation/rollback tests.
No runtime schema or migration was changed in planning.

## Deterministic portion and retained calculation interface — 2026-10-25

This is the E3-owned completion of the G3 allocation/evidence projection consumed by
5.8-A/5.13-A and source-impact writers. It refines 3.9/3.17-A/3.18 and L-0106/0110/0111/
0129, not their product rules. Names are selected planning models, not existing tables.
No daily earning posting or second ledger is introduced.

### Portion provenance and identity

A portion projection contains `portion_key`, `source_leave_type_id`, `original_period`
(inclusive `start_date`, `end_date`), `available_from` (civil date), nullable inclusive
`expires_on`, original entitlement minutes, current valid reserved/consumed minutes and
remaining eligible minutes, plus typed immutable source provenance. Values are integer
minutes represented by nonnegative canonical decimal strings; allocation contribution
lines require strictly positive minutes. Original period is retained through carry-over;
a carry-over date is not a new original earning period or a second entitlement.

Select two closed provenance branches:

- `automatic`: actual employment/type and policy-assignment UUID, immutable governing
  policy version UUID, immutable rate-source reference (kind policy_version or
  employee_entitlement_version and its actual UUID), original period start/end and
  earning occurrence civil date. The occurrence is calculated under E3's accepted earning
  schedule; no per-day transaction or synthetic source event is required.
- `event`: actual immutable source balance-event UUID and positive source-line ordinal,
  original period start/end and actual source type. The actual source/grant owner supplies
  those references; a request reservation/consumption is not a fresh grant origin.

Construct `portion_key` as `p1:` plus lowercase SHA-256 of UTF-8 RFC-8785 canonical JSON
of `{version:1, org_id, employment_id, source_leave_type_id, origin}`. `origin` is exactly
one of the above closed branches; canonical UUIDs/dates/string counters are required.
No label, request ID, replay timestamp, current expiry, mutable amount or calculation
build identifier enters identity. Distinct immutable source versions/origins remain
separate even if amounts coincide. Unsupported origin version fails safely; never mint a
random replacement key on replay. Digest collision/inconsistent origin binding is an
integrity error, not permission to merge two entitlements. Retain the full typed provenance
with evidence so the digest is not the sole explanation.

A retained unchanged origin keeps its key across replay and carry-over. Corrections that
change an immutable earning basis yield a revised origin/evidence and follow actual
protected impact/remedy rules; do not silently retarget a prior reservation to the new
key. A corrected amount/validity for the same origin is explained in revised calculation
evidence without fabricating another earning source. E3 owns derivation of eligible
amounts, cap/expiry/correction ordering and deterministic reconstruction from its actual
history; the key is not an extra allocation rule.

### Allocation input/output

The owner allocator accepts the actual normalized per-date duration, effective policy/
work/employment history, actual source event history and active other-request commitments.
For replacement/reassessment pass the exact current commitment identity to exclude its
own reservation from *candidate* available calculation, retaining it protected until the
reviewed atomic replacement. Never exclude another commitment or drop the original before
knowing the replacement can be applied. Order requests/affected sets under existing owner
coordination; an earlier requested date never displaces an existing valid reservation.

Evaluate candidate dates ascending. On each date discard unavailable/expired portions,
account for protected valid prior reservations and candidate usage on earlier dates,
then allocate by `(expires_on with null last, original_period.start_date,
original_period.end_date, portion_key)` ascending. Period boundaries are the actual owning
periods, not new rollover periods. Equal-expiry oldest-source priority remains L-0129;
full period boundaries make the original period comparison explicit before final identity.
Later earning cannot repair an earlier shortfall. Do not borrow across source types except
through the actual reviewed exceptional-allocation rules.

Result has `tracking` tracked/untracked, `calculation_version`, normalized duration,
ordered date entries and totals. Each date entry contains `leave_date`, `requested_minutes`,
`funded_minutes`, `shortfall_minutes` and ordered positive contributions
`{source_leave_type_id, portion_key, minutes}`. For tracked calculations, funded plus
shortfall equals requested per date and in totals; no portion exceeds its valid available
amount across dates. Shortfall is a calculation result, not automatically unpaid leave,
a discretionary grant or negative balance. Actual submission/exception policy turns the
reviewed result into paid/unpaid classification. Untracked returns its actual usage
classification and no fictitious entitlement contributions/commitment; no hidden tracked
zero balance. The normalized summary remains the command contract's public projection.

### Immutable evidence storage

Select E3 `leave.calculation_evidence`: UUID `id`, `org_id`, `employment_id`, `leave_type_id`,
`causal_id`, bounded server-generated `evidence_key`, `calculation_version`, positive
`payload_version` (initially 1), `basis_date`, `input_evidence`/`result_evidence` JSON objects,
creation actor ID and UTC time. Scoped unique `(org_id,employment_id,id)` supports actual
owner references; unique `(org_id,causal_id,evidence_key)` prevents duplicate evidence for
one actual purpose. Runtime cannot update/delete immutable evidence. Apply actual org
RLS/actor provenance and current domain field authorization, not browser access to the table.

`evidence_key` is selected by the owning closed command adapter, not arbitrary client input:
`primary` for its one primary calculation, or `request:<request UUID>:cycle:<cycle UUID>:after`
for an affected request. At most 160 UTF-8 bytes. Before evidence reuses actual retained
previous evidence where adequate; if a new before observation is needed use the same
request/cycle form with `before`. Request-specific keys/references are introduced only by
actual E5 consumers; original E3 source actions need no future request-table dependency.
Owning request/cycle/event references enforce their actual scoped link when those models
exist. The evidence key is not a general business object resolver or audit service.

`input_evidence` v1 contains normalized requested dates/minutes, actual policy/assignment/
rate/work/calendar/employment values or retained immutable version references, current
source-event ordering boundary, relevant actual commitment/allocation references and
complete typed provenance for used portions. Mutable row ID/revision alone is insufficient:
preserve its relevant value or an immutable version whose retention is protected.
`result_evidence` v1 contains the exact ordered allocation result above plus actual
paid/unpaid/tracking classification when known by the caller. No note, medical content,
private document metadata or credential payload is copied into calculation evidence.

The calculation version identifies actual rules/code independently of policy version.
Do not require execution of obsolete code: evidence explains the original result, and a
new calculation can be compared without rewriting it. Routine preview/balance reads do
not create this record. Actual consequential action and evidence commit/rollback in the
same short owner transaction, with its state/ledger/receipt/required intent. No independent
evidence service transaction or second snapshot framework.

### Planned verification allocation

3.18 owns repeatable keys/provenance, automatic versus actual-event sources, no duplicate
carry-over/earning, earliest-expiry/oldest-period/final ties, future earning/date shortfalls
and existing reservation priority. 3.9/3.17-A own event ordering/replay; first consequential
E3 consumer owns actual immutable evidence/schema/permissions/rollback. 5.8-A proves real
allocation/evidence references in commitment effects; 5.13-A proves reviewed replacement
without dropping prior protection. 5.15 source owners prove actual changed-history effects.
Oracles include two same-amount distinct origins staying distinct, equal expiry using
older original period, a carry-over retaining its original key, repeated preview with no
writes, and later changed policy/calculation not altering saved evidence. No runtime tests
executed; exact package/constraint/generated artifacts remain G6/C6 owner work.

## Exact work/calendar precision binding — planning candidate 2026-10-26

The [work/calendar and minute contract](work-calendar-and-minute-precision.md) owns the
selected closure shapes, nominal local-clock DST quotas, effective-date interpretation
and exact half-minute consumption. Its MinuteAmount mapping supersedes integer-only
amount wording in this technical candidate; integer counts/revisions and entitlement
floor rules remain. Existing accepted ADRs and original acceptance criteria are unchanged.
Actual writer/consumer fixtures must use that contract before this interface is delivered.

## Consolidated adoption — accepted 2026-10-26

The user explicitly approved the completed consolidated planning package. The reviewed
choices and bounds in this contract are adopted under [the acceptance decision](../decisions/0171-work-calendar-precision-and-retention.md).
Earlier candidate/pending-review wording is historical and superseded for these choices.
Actual implementation and provider/database/browser/recovery proof remain delivery work.
The user requires a new Codex session before implementation; no runtime action here.
