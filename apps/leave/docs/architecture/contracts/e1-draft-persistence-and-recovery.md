# E1 draft persistence and recovery — discussion contract

**Status:** Product behavior agreed; consolidated technical baseline 2026-10-01; listed contract/verification gates open; not story-ready
**Date:** 2026-09-23  
**Owners:** Leave lead and Platform API owner

This discussion fills implementation choices beneath the existing
[feature specification §7](../../features.md#7-leave-application-experience), spine
AD-4/8/12 and the accepted platform operation/revision/draft rules. It is not a new
feature specification. The approved first journey remains sign in → select
organization → create/resume → autosave → close → reopen.

Terminology clarification, 2026-10-01: an **operation outcome record** (called an
operation receipt in the technical schema below) is internal retry evidence, unrelated
to Expense/Receipts. Leave has no historical operation records to migrate. Version handling concerns
records created after this implementation is delivered;
initial delivery supports only its first version and must fail safely on unsupported
versions. No legacy Expense-data migration is required under platform ADR-0045.

## Proposed storage and command boundaries

| Concern | Proposed E1 contract |
| --- | --- |
| Owner | Leave owns draft content and operation outcomes; shared employment is referenced through its HTTP contract. No platform-wide draft table. |
| Identity | Separate UUID draft and operation IDs; server-managed integer revision starts at 1 and increments on each accepted mutation. Actor identity is distinct from employee ownership. |
| Uniqueness | One active employee draft for `(org_id, employment_id)`, enforced by a partial unique database constraint. The enduring employment identity follows platform ADR-0042; period/eligibility rules remain separate. |
| Start | Create-or-resume command with an operation ID; server derives authorized ownership. Create an empty draft or return the existing one unchanged. Initial user input goes through revision-checked saving rather than a competing creation payload. |
| Read | Return authorized current persisted state and revision. An old successful operation outcome does not assert that the draft is still active or still at that revision. |
| Save | Supply draft ID, expected revision, operation ID and a bounded draft-input payload. Check revision and active lifecycle atomically; no upsert. Record the successful outcome in the same transaction. |
| Close | A client navigation action, not a terminal draft state. Wait for pending saves; retain the saved draft on closure. Apply existing failed-save choices to Close, Escape and mobile Back. |
| Discard | Explicit confirmed command with revision and operation ID. Close the lifecycle atomically. Preserve minimal closure/replay evidence so late writes and old start retries cannot resurrect it. Remove editable contents under the agreed retention policy below. |
| Later submission | E5 adds the submitted closure transition atomically with request/reservation/audit/outbox effects. E1 does not expose submission or simulate its success. |

The 2026-10-01 consolidation below selects physical names, route/counter representation
and coordination for validation. Constraint SQL, canonicalization/key management and
verification remain pending; this is design, not a migration.

## What a saved draft means

Recommend accepting incomplete form data without treating it as a valid request.
Keep selected leave type, duration mode, dates/duration and optional employee note as
draft input. Exact field schemas, bounds and reference validation must be settled
before the mutation story; reject malformed or unauthorized references safely.
Preserve entered values when eligibility/configuration changes rather than silently
replacing them. Attachments join through E4's separate association contract.

Draft saving reserves no entitlement and does not confirm policy eligibility,
approval routing, document completeness or a paid/unpaid allocation. E3 provides
authoritative calculation previews and E5 revalidates on submission. E1 may use
authorized minimal configuration fixtures; it must not display invented balances,
duration calculations, successful validation or working submission controls.

The Saved indicator must cover the input actually acknowledged by the server. Resolve
how partially typed/invalid date text is represented before the UI story; it must
not disappear on reopening after the UI claimed it was saved. No default leave type
is selected. Under the 2026-10-04 agreement, the UI initializes Full days when first
choosing a type in a new request if permitted; otherwise no mode is selected. This
is an ordinary form input change, saved through normal revision/operation handling.
Reads, autosave and restoration never fill defaults into saved null selections.
Later type changes never select a replacement automatically; a definitively disallowed
mode may be cleared with a brief notice under ADR-0122.

## Agreed draft input preservation

Agreed 2026-09-24: keep draft-input validation separate from request/submission
validation. Autosave preserves bounded, partially entered form values, not only already-valid
dates and durations. E1 acceptance should demonstrate the following distinctions:

| Input | Agreed save/reopen behavior |
| --- | --- |
| No leave type or duration mode selected | Save an unfinished draft without adding a default or forcing a selection just to close. |
| Start date entered, end date blank | Preserve the start and blank end; show neither a zero duration nor successful request validation. |
| Partially typed date such as `24/09/` | Preserve the exact in-progress text after acknowledgement and reopening; ask the employee to complete it before calculations/submission. Do not substitute today's date or erase it after claiming Saved. |
| End date earlier than start | Preserve both entries and explain the ordering issue at the agreed validation point; never swap dates automatically. |
| Invalid/incomplete hours text | Preserve bounded input as draft text; require a valid duration in the accepted 30-minute increments before calculation/submission. No exact start/end times. |
| Optional note | Preserve as plain text. Exclude it from diagnostics and replay snapshots; remove it with discarded form contents. |
| Previously selected type becomes unavailable | Preserve the reference for authorized explanation; require a new eligible selection where necessary. A new arbitrary/cross-organization reference is still rejected. |

The concrete payload should represent in-progress text separately from interpreted
values. Record its input-format context so changing language cannot silently reinterpret
an ambiguous date or decimal. Unambiguous valid dates use a canonical date-only value;
do not round-trip through UTC timestamps or make timezone conversion change the date.
The server owns interpretation for domain calculation; raw text alone is never a
validated request. Render input as text, never executable markup.

Bound field lengths and total payload size in the shared API contract, with safe
field-specific errors. Do not silently truncate input and label the whole form Saved.
The exact bounds, payload discriminators, supported input formats and mode-switch
handling must be finalized before the autosave story. This proposal requires no
frontend-only durable store or promise to recover changes never acknowledged by the
server. Local changes newer than an acknowledgement remain unsaved.

Sources: feature specification §7, platform EXPERIENCE Date inputs, Leave EXPERIENCE
Apply for leave, and Leave ADR-0118. Promote proven input-state/serialization controls
through shared UI/scaffolding, retaining Leave's type, schedule and policy validation.
These agreed behaviors inform acceptance coverage; they are not finalized stories or
a completed UX/requirements inventory.

## Retry, concurrency and error behavior

The [shared error/recovery wire proposal](../../../../../platform/docs/architecture/contracts/api-errors-and-operation-recovery.md)
owns the envelope, legacy numeric-code compatibility and committed/unresolved outcome
representations. Leave owns these proposed domain mappings:

| HTTP / identifier | Leave behavior |
| --- | --- |
| 409 / `leave.draft_revision_conflict` | Stop saving, preserve local edits and offer Review saved draft after current authorization. A returned revision is information, not permission to silently retry with it. |
| 409 / `leave.draft_discarded` | Stop saving; show the accepted discarded-elsewhere message and Back to My Leave. No automatic new draft. |
| 409 / `leave.draft_submitted` | E5 adds the submitted-elsewhere message and authorized View request. E1 does not implement submission. |
| 409 / `leave.draft_start_outdated` | A proposed scope-generation check failed. Return to current authorized draft context and require an explicit new start/resume action; preserve local input where practical. |
| 403 / `leave.draft_read_only` | Current permissions permit reading but the agreed ended-employment rule prevents starting/editing. Explain read-only employment status without suggesting repeated save retries. |

Resource disclosure checks precede domain-specific details. E1 cannot rely on English
messages to distinguish these outcomes. Concrete route/payload models and timeout
budgets remain pre-story work.

- Resolve a committed matching operation before attempting its mutation again;
  recheck current access before returning the outcome. Different payload with the
  same operation ID is rejected. Concurrent identical operations commit once.
- Serialize/coalesce saves within a tab; do not replace newer typing with older
  acknowledgements. Resolve an uncertain save before sending a fresh save operation.
- A stale revision pauses saving and offers the accepted review-saved-draft flow;
  never automatically replace the expected revision and overwrite current data.
- Closed-draft errors distinguish discarded from submitted after authorization.
  Neither stale save nor old create retry may attach to a later unrelated draft.
- Propose adding a stable string `error_id` alongside the existing optional numeric
  `code` and safe message/details fields. Preserve numeric-code compatibility;
  finalize the shared Pydantic/OpenAPI/adapters/generated-client contract together.
  This field choice is proposed platform API work, not a Leave-only alternate format.

No retry window is assumed. Before readiness, specify outcome retention, minimum
lifecycle evidence, cleanup and how expired/unknown operation IDs are prevented from
executing an old start as a new action. A missing outcome is not evidence of failure
or permission to generate a fresh operation ID. Do not borrow notification retention
windows for employee commands without a separate rationale.

## Agreed recovery evidence and retention policy for E1

The user approved the following retention behavior on 2026-09-24. Concrete storage,
wire and concurrency design still require verification. Keep three lifecycles separate:

| Data | Agreed initial policy |
| --- | --- |
| Active draft input | Retain until explicit discard or successful submission; neither the selected end date passing nor a session expiring removes it. No inactivity-based expiry in E1. Organization/person deletion and any future retention policy require their own owned process. |
| Discarded draft input | Remove the editable form payload in the discard transaction. Retain minimal closed-draft identity/state, revision and attribution so old views receive safe lifecycle recovery. No recover-discarded-draft UI. Backup expiry is a separate operations policy; do not promise immediate erasure from backups. |
| Command/replay evidence | Initially retain compact operation receipts without automatic expiry. Store scope/caller, command identity, target, input fingerprint, committed revision/result reference and timestamps; do not duplicate employee notes or whole form payloads in every autosave receipt. No automatic cleanup until a bounded rejection/expiry contract is designed and verified. |

Reconfirmed 2026-10-02: retain the compact closed draft row for simpler lifecycle and
retry checks. Clear editable contents on discard; E5 submission clears draft contents
atomically after the permanent request and required effects are recorded. No separate
archive database or restore UI. Closed-draft cleanup is deferred until an age threshold,
operation-outcome expiry/rejection rules, reference handling and longer-lived audit
retention are specified and verified together. No X-day purge is selected for E1.
This agreement supersedes the conversational suggestion to immediately delete closed
draft rows; the existing closed-row/foreign-key design remains the current baseline.

This chooses storage of compact evidence over an arbitrary short replay window for
E1. It does not establish permanent retention of all application data. Measure receipt
volume and define a safe compaction/expiry policy before introducing cleanup; never
silently prune evidence and reinterpret an old operation as a fresh action. A plain SHA-256
fingerprint distinguishes payload reuse without storing another full input snapshot.
It is not confidentiality protection: predictable sensitive input may be guessed.
Keyed fingerprints are a logged security enhancement, subject to application threat
assessment; the current E1 design has no fingerprint secret or key rotation.

A receipt proves a command's committed outcome, not the current draft contents. A
save receipt can report that revision 4 committed even if the current revision is 7.
The client then reads authorized current state and follows conflict/lifecycle rules;
it must not replace newer local input with an old snapshot. An uncertain discard
checks its existing operation before offering a new action.

### Database placement and platform reuse

Recovery evidence is authoritative in the owning application's PostgreSQL database,
not only in the browser. Under
[platform ADR-0012](../../../../../platform/docs/architecture/decisions/0012-operation-identity-idempotency-and-tracing.md),
operation outcomes commit atomically with the business change. A separate central
recovery service would break that local atomicity and is not proposed.

Proposed physical division (illustrative table names, not implemented schemas):

| Record | Location and purpose |
| --- | --- |
| Draft lifecycle | `leave.draft`: retain ID, organization/employment scope, closed state, revision and attribution after discard; remove the form payload. This small retained row explains why an old draft can no longer be edited. |
| Operation receipt | `leave.operation_receipt`: one record per committed operation, containing caller/scope, operation ID, command, versioned input fingerprint, target ID and compact outcome. Multiple saves cannot be represented by only a last-operation field on the draft. No notes or whole draft snapshots in receipts. |
| Draft-scope generation | A Leave-owned employee/organization scope row, separate from any one draft; supports the proposed delayed-start guard below across draft closure and replacement. |

Discard, payload removal, lifecycle closure, generation change (if this design is
selected) and the discard receipt commit in one local transaction. No successful
receipt may exist without its corresponding committed effect. Current authorization
protects reads of all these records, including outcome lookups.

The browser keeps in-flight operation IDs, expected revisions and recoverable local
edits under the existing session rules. Browser state is not the durable deduplication
record; browser loss or backend restart must not erase the database evidence. This
adds no promise of sensitive form persistence in localStorage or recovery of unsaved
text after closing a tab.

Treat implementation as a shared-platform enabling delivery item linked to E1's first
consumer: prove revision/operation handling and safe save/close recovery, then update
owning templates, reusable clients/UI and disposable generated-app tests in the same
item. The builder remains a placeholder until that work is delivered. Future apps
adopt this proven pattern rather than independently redesigning it. Each app still
owns its local tables, migrations and business transaction; upgrades to generated
code require explicit adoption and compatibility tests.

Applications define draft cardinality, states, authorization, payload and retention.
One active draft per employee/organization is Leave-specific and opt-in elsewhere.
An app without drafts need not adopt a draft table, although retriable commands still
follow platform ADR-0012. There is no universal platform draft workflow or requirement
that every app use Leave's discard/retention policy.

### Unseen or delayed starts

Retaining completed operations alone does not protect a start request that was delayed
before its first arrival. Propose a Leave-owned draft-scope generation for each employee/
organization scope. The authorized context read supplies the generation; new start
commands submit that expected generation. Atomically coordinate generation, active-draft
uniqueness and the operation receipt; advance the generation when a draft closes.
A never-before-seen start from an older generation is rejected, even if another draft
now exists. A recorded matching start retry returns its original result reference,
never the newer draft. Concurrent starts in the current generation converge on the
same active draft without overwriting it. This is a domain guard, not a generic workflow
engine or a new user-visible step. Generation/lock schema remains pre-story design.

### Recovery outcomes

- Committed: return the recorded result after current authorization; no repeat effects.
- No receipt yet: treat as not resolved, not proof of failure. Retry the identical
  operation and payload under concurrency protection; late first attempts and retries
  must serialize safely. Do not create a fresh operation automatically.
- Same operation with different input: reject without changing the draft.
- Stale revision or scope generation: preserve local input and require explicit
  current-state review or a new user start action; do not silently update guards.
- Missing/closed target: saves never create it. For authorized closed targets, use the
  accepted discarded/submitted recovery; otherwise return a safe non-disclosing result.

Attachment data will follow E4 association/recovery rules; discarding the form must
not issue uncontrolled deletes to the Content owner. E1 has no uploaded attachments.
Prove discard/save races, unknown delayed starts, new draft after discard and replays
across process restart with the real restricted runtime role before accepting this
contract. No implementation or retention gate is completed by this proposal.

## Remaining gates and evidence

The accepted identity direction does not close its remaining wire, service-caller,
membership/role migration, actor mapping, timeout or employment-freshness gates.
Agreed on 2026-09-23: allow employees with current or future employment to prepare drafts once
explicitly granted Leave access. For ended employment, preserve the draft but allow
only authorized reading, not new starts/edits; membership revocation still denies
access entirely. On rehire, resume the same retained draft with refreshed context and
explicit warnings for invalid inputs rather than copying it or silently deleting it.
The selected leave end date passing does not close or delete a draft. On reopening,
retain input and apply current backdating/eligibility rules; explain invalid dates and
block submission until corrected where required. No automatic expiry follows from
the requested dates. Department,
location and supervisor may be unassigned without blocking drafts under ADR-0041.

Verify simultaneous start, two-tab saves, delayed acknowledgements, uncertain commit,
discard/save/start-retry races, expired replay evidence and authorization loss using
the actual restricted database role and API contract. Browser evidence covers the
first journey, failed close, organization switch and same-user session return.
Use the recommended Playwright Test in TypeScript browser-testing direction, with
pytest for backend/domain/database tests and focused Vitest/React Testing Library
tests where useful; package/version/environment verification remains pending.

Scaffold impact: prove conditional writes, operation recovery and error adapters in
the owning item and update generator/disposable-sample tests. Shared UI impact: save,
close, conflict and safe recovery primitives; Leave owns the draft fields/lifecycle.
Agent-context impact: existing rules suffice. Documentation impact: this contract,
authoritative source links and tracker. ADR impact: existing accepted rules govern;
no superseding decision or new implementation authority is created here.

## Consolidated E1 technical baseline — 2026-10-01

The following supplies concrete design values for contract validation. It is a
working technical baseline, not approval of implementation readiness or a claim of
measured performance. It refines the earlier proposals; agreed product behavior and
accepted ADRs still govern. Product-visible new defaults are called out below.

### Routes and request identity

Use `/api/v1/organizations/{org_id}` as Leave's authenticated business API prefix.
Resolve employee ownership from the verified caller and People contract; none of
these own-draft routes accepts an arbitrary employee owner in its payload.

| Method / suffix | Contract |
| --- | --- |
| GET `/me/draft-context` | Current authorized employment/editability, decimal-string `scope_generation`, and active-draft summary if present. Does not create a draft. |
| POST `/me/draft/start` | UUID `operation_id`, decimal-string `expected_scope_generation`; no initial form payload. Return a compact committed acknowledgement with original draft ID. Read the current draft separately. |
| GET `/drafts/{draft_id}` | Current authorized draft lifecycle, revision and active input. Discarded payload is absent. Never return another employee's protected data. |
| PUT `/drafts/{draft_id}/input` | UUID `operation_id`, decimal-string `expected_revision`, complete versioned `input` envelope. Replace only the allowlisted input aggregate, never owner/lifecycle/attribution. |
| POST `/drafts/{draft_id}/discard` | UUID `operation_id`, decimal-string `expected_revision`; clear input and close atomically. |
| GET `/operations/{operation_id}` | Current caller/organization-scoped `committed` receipt or `unresolved`; current access required, no employee input in the response. |

Use UUID v4 values for draft and operation identities. Keep integer revisions and
scope generations as PostgreSQL bigint; serialize unsigned decimal strings on the
wire, accepting only positive revisions and nonnegative generations within signed
bigint range. Treat IDs/counters as opaque outside their explicitly defined contract.
Scope generation begins at 0; draft revision begins at 1. Replies carry a response
schema version through the versioned API contract. Do not add a fake Submit endpoint.

### Input envelope and product-visible limits

Use `input_version: 1`, nullable `leave_type_id`, nullable duration mode
`full_days | half_day | hours`, plain-text `note`, and separate input groups for each
mode. Full days retain start/end date entries; half day retains one date; hours retains
one date and duration text. Keep inactive-mode values when switching modes so switching
back restores prior typing; calculations/submission consider only the selected mode.
Changing leave type preserves independent input but clears a now-disallowed selection
with a brief notice under ADR-0122; do not silently select a replacement. This preservation behavior was approved on 2026-10-01.

Represent date entry as raw `text` plus an explicit input-format identifier, initially
`dmy_numeric_v1` for English typed day/month/four-digit-year entry. Calendar selection
populates the same entry model. The server derives a canonical date-only value or an
incomplete/invalid status; never accept a client-derived canonical value as authority.
Do not store two independently editable date truths. Persist the format identifier
with incomplete text; later locale changes must not reinterpret it. Domain validation
remains separate. Format identifiers can be extended compatibly for Portuguese.

Working bounds: 64 Unicode code points per date entry, 32 per duration entry, 4,000
per note, and 32 KiB UTF-8 for the complete mutation body. Count code points consistently
across Python and TypeScript; do not use JavaScript UTF-16 length as an equivalent.
Reject unknown envelope keys, unsupported versions/modes/formats and oversized bodies;
return safe field errors without echoing values. Never truncate silently. Empty text
is permitted. Duration text uses a recorded decimal-format identifier; canonical minutes
are derived only from valid positive hours in half-hour increments. Exact accepted
lexical grammar and mode-switch UX examples must be included in the schema fixtures.
The 4,000-character note cap and mode-switch preservation were approved on 2026-10-01; the byte/field bounds
are testable technical limits, not measured capacity claims.

### Timing baseline

Shared-input race semantics follow accepted
[platform ADR-0044](../../../../../platform/docs/architecture/decisions/0044-bounded-shared-input-observations-for-draft-saves.md).
The ten-second total E1 execution limit is approved; lower-level timing/cancellation
mechanisms still require verification. Other applications define their own limits.

| Boundary | Initial design value and behavior |
| --- | --- |
| Autosave | Start after 1 second without input; under continuous typing request a save at least every 5 seconds when no save/recovery is in flight. Coalesce to the latest snapshot. Close/switch flushes pending input immediately. |
| Protected backend request | 10-second total execution deadline, including dependency calls, connection acquisition, coordination, commit and response preparation. Never reuse authorization past this execution budget. |
| Shared access and employment calls | Up to 3 seconds each within the remaining request budget; no internal automatic network retry inside the protected mutation. These are new Leave/v2 budgets, not unverified replacements for existing v1 clients. |
| Database | At most 1 second waiting for a coordination lock and 2 seconds for the local business transaction including commit, always within the remaining request deadline. No external HTTP while locks are held. |
| Browser mutation response | 12-second client timeout, leaving margin above the backend deadline. Timeout/cancellation never proves rollback. |
| Automatic uncertainty recovery | At most 15 additional seconds, no more than 3 outcome lookups and 1 identical mutation retry, all serialized and capped by the remaining recovery deadline. Stop immediately on known denial/validation/conflict/lifecycle outcomes. |
| Recovery exhausted | Show not-yet-confirmed with Retry, retain input and original operation/payload; no endless background loop or competing fresh save. |

Retry begins with an outcome lookup; retry the identical mutation only while unresolved
and enough budget remains. A lookup after a retry may resolve a lost response. Skip
work that cannot fit; deadlines count elapsed wall time and are not reset by each
attempt. User Retry starts a new bounded recovery cycle for the same operation. Backend
commit uncertainty still follows receipt lookup. These timeout values require tests
for cancellation/transaction cleanup and actual latency before readiness; an HTTP
library timeout alone is not proof of the total deadline.

### Persistence, coordination and receipt contents

Select `leave.draft_scope`, `leave.draft` and `leave.operation_receipt` as the physical
design names. All are Leave-owned, tenant-scoped and protected by restricted runtime
RLS with transaction-local verified organization/actor context. No cross-owner foreign
keys to People tables. Enforce local compound references to keep draft, scope and
operation targets in the same organization. Retain platform ADR-0025 attribution.

`draft_scope` has one row per `(org_id, employment_id)` with bigint generation. Create
this row atomically on the first authorized start if absent; reading absent context
returns generation 0. `draft` holds UUID identity, scope, lifecycle, bigint revision,
versioned input and attribution/closure fields. Enforce a partial unique constraint
on scope while active; a closed draft must have no editable payload. E1 supports
active/discarded only; E5's migration adds submitted lifecycle and request linkage.

For all E1 draft mutations, after current external checks, establish local transaction
scope and lock the employee's `draft_scope` row. This serializes that employee's draft
commands without locking other employees or holding locks during user editing. Under
that guard, resolve an existing operation receipt before testing new-write revision/
generation guards; then lock the target draft if needed. All paths use this order.
Read-only outcome lookups need not lock; absence while a transaction runs is unresolved.
Verify the first-scope-row insertion race explicitly; a prior unprotected read is not
sufficient. Unique operation keys remain a database backstop.

Receipts are uniquely keyed by `(org_id, actor_id, operation_id)` and store command
kind/version, target employment/draft IDs, fingerprint/algorithm version, committed
revision, compact result reference and creation attribution/time. A different command
using the same scoped operation key is a mismatch. Preserve canonicalization of the
full validated command, including expected revision/generation and raw input; object
key order is irrelevant, while omitted/null/empty handling must be explicit. Do not
normalize away distinct user text before fingerprint comparison. Preserve canonicalization and
algorithm-version support while receipts remain usable. E1 needs no fingerprint key
provisioning; a stronger algorithm requires an explicit compatible evolution design.

A save commits one revision increment, input update, attribution and receipt together;
an identical replay increments nothing. A discard commits input removal, lifecycle/
revision update, scope-generation advance, audit evidence and receipt together. New
start creates/resumes without changing existing payload and stores its receipt in the
same transaction. Never log or snapshot note/date payload into receipts or operational
logs. Trace each race in E1-AC-02/04/05/06/10/11/15; no test has run for this baseline.

### Gates still open after this consolidation

- Input v1 shape and lexical examples are now specified below; translate them into
  declared API schemas/fixtures during delivery. The 4,000-character note limit and
  preservation across duration-mode switching are approved.
- Shared person/account/service actor mapping, v2 schemas and legacy Access grant
  compatibility; effective-date timezone and shared employment freshness through commit.
- Dependency pins and isolated development/test topology; initial browser matrix;
  migration adoption/rollback evidence and real deadline/cancellation behavior.
- Structural key/RLS and fingerprint/version lifecycle design is specified below. Reviewed
  DDL, executable compatibility/concurrency evidence and
  the missing builder/generation tests remain delivery work.

These are owned contract/verification tasks, not a new lifecycle or permission to
implement Leave. Reuse existing Access/Content/deployment work where it meets the
accepted contracts, and preserve current consumers. Keep the first slice unchanged.

### E1 input version 1: exact shape and interpretation

Design completion, 2026-10-01: the following fills the input-shape/lexical gap in the
baseline above. It is a contract specification, not generated schema or application
code. Dates/duration validity are derived from this one stored input representation.

```json
{
  "input_version": 1,
  "leave_type_id": null,
  "duration_mode": null,
  "full_days": {
    "start": { "text": "", "format": "dmy_numeric_v1" },
    "end": { "text": "", "format": "dmy_numeric_v1" }
  },
  "half_day": {
    "date": { "text": "", "format": "dmy_numeric_v1" }
  },
  "hours": {
    "date": { "text": "", "format": "dmy_numeric_v1" },
    "duration": { "text": "", "format": "decimal_hours_dot_v1" }
  },
  "note": ""
}
```

All keys above are required in a full input replacement, with no unknown keys.
`leave_type_id` is a UUID or null; `duration_mode` is null or one of the three baseline
values. Text leaves are strings, including empty strings, not null. Never interpret
omitted fields as instructions to erase existing values; reject an incomplete envelope.
The server creates this empty shape on a new draft; no type/mode choice is defaulted.
All three mode groups persist, but only the selected group is interpreted for the
request. No client-controlled calculated amounts, eligibility, actor, owner, revision
or lifecycle fields belong inside `input`.

Store raw text exactly, without Unicode normalization, whitespace trimming or automatic
correction. Reject U+0000 and oversized/structurally malformed input with safe field
errors; PostgreSQL storage restrictions must not become an unexplained save failure.
Such rejected input remains visibly unsaved. The limits above apply to raw text.
Interpretation may ignore leading/trailing ASCII spaces without rewriting stored text.
Render preserved input as text, not HTML.

For `dmy_numeric_v1`, a complete date has one or two ASCII digits for day/month and
exactly four for year, separated by `/`, and must be a real Gregorian date in years
0001–9999. ISO date-only values returned for valid interpretation are server-derived.
Blank is unset; a syntactically extendable prefix is incomplete; an impossible or
otherwise malformed value is invalid. Both incomplete and invalid bounded strings
are still saveable drafts. Errors are presented at the agreed interaction point,
not as a blocking message on every keystroke. Calendar selection writes a complete
zero-padded `DD/MM/YYYY` entry. Display formatting outside the editor remains governed
by the approved UX; adding another typed grammar requires a new explicit format ID.

For `decimal_hours_dot_v1`, a complete amount contains ASCII digits, optionally one
`.` followed by digits; no signs, exponent, grouping separators or unit suffixes.
Parse decimal arithmetic exactly, never binary floating point. A valid amount is
positive and exactly divisible by 0.5 hours; convert to whole minutes only then.
A bare decimal suffix such as `1.` is incomplete. Bounded other text remains a saved
invalid entry until corrected. Later Portuguese input gets its own format ID;
changing locale does not reinterpret a stored dot-format entry as comma-format text.
Scheduled-day maximums and other eligibility are later domain validation, not reasons
to lose draft input. Half-day duration is derived from the schedule, never an entered
morning/afternoon choice or exact clock range.

Contract examples to bind E1-AC-03/04:

| Raw input or action | Save/reopen | Interpretation |
| --- | --- | --- |
| `24/09/` | Preserve exactly | Incomplete; no date/calculation value |
| `1/10/2026` | Preserve exactly | Date-only `2026-10-01` |
| `31/02/2026` | Preserve exactly | Invalid calendar date |
| `02/10/2026` through `01/10/2026` | Preserve both | Individually valid dates; invalid ordered range, never swapped |
| Hours `1.50` | Preserve exactly | 90 minutes |
| Hours `1.25` | Preserve exactly | Invalid 30-minute increment |
| Hours `1.` | Preserve exactly | Incomplete |
| Hours `1,5` in dot format | Preserve exactly | Invalid under this format; never silently reinterpret |
| 4,000-code-point note | Preserve exactly | Within limit regardless of UTF-16 code-unit count |
| 4,001-code-point note | Reject save, preserve local edit | Field limit error; previously saved note unchanged |
| Switch full days → hours → full days | Preserve each mode group | Only active mode contributes to later calculations/submission |
| Missing `hours` group in PUT payload | Reject save | Incomplete envelope, not a request to delete saved hours |

The exact server parse/interpretation representation must be reflected in the generated
API schema and exercised by shared client fixtures during delivery; this document
settles behavior but does not claim those artifacts exist. No application tests ran.

### Structural database contract — 2026-10-01

This completes the design-level key/constraint mapping for E1. Reviewed Alembic/SQLAlchemy
DDL, restricted-role verification and deployed migration evidence remain delivery work.
Do not create these tables or run migrations as part of this planning document.

| Table | Required structural constraints and write authority |
| --- | --- |
| `draft_scope` | Primary key `(org_id, employment_id)`, both UUID/non-null; nonnegative bigint generation; server-managed creation/update actor UUIDs and UTC timestamps. Runtime may select/insert/update for authorized commands, never delete/rekey a scope. |
| `draft` | UUID ID primary key; non-null organization/employment; composite FK to its local scope with deletion restricted; unique `(org_id, employment_id, id)` for receipt linkage; positive bigint revision; E1 lifecycle limited to active/discarded. Partial unique `(org_id, employment_id)` where active. Scope/identity/creation attribution immutable. |
| `operation_receipt` | Primary key `(org_id, actor_id, operation_id)`; non-null employment/draft IDs with composite FK `(org_id, employment_id, draft_id)` to draft; command enum start/save/discard plus positive command/fingerprint versions; fixed 32-byte digest and supported algorithm/version identifier; positive committed revision; immutable compact result and creation attribution. Runtime select/insert only; no update/delete. |

Active drafts require a non-null JSON object payload, input version 1 and null closure
fields. Discarded drafts require SQL NULL payload, non-null closure actor/time, and
no result-request linkage in E1. No form payload in closure audit or receipts. Submission
support is an E5 migration, not an unused permissive E1 state. Enforce nullability with
explicit checks: a SQL NULL result must not accidentally satisfy a shape check.

For the input JSON, database checks cover version, required containers/types, permitted
mode/format identifiers and declared text limits; detailed date/hour interpretation and
policy eligibility stay in the application. Map named constraint failures explicitly:
recognized concurrency collisions take their authorized conflict path, malformed input
has a safe validation response, and unexpected integrity failures roll back without
exposing SQL. Never map every integrity exception to duplicate-draft success.

Use server-side triggers or equivalently enforced owned write paths to preserve creation
fields, derive update attribution and reject terminal-to-active transitions. Every accepted
save changes revision by exactly one; no-op receipt replay changes none. Runtime grants
alone must not allow alternate paths to rewrite immutable receipt evidence. Evidence of
atomic mutation-plus-receipt belongs to the transaction tests; a foreign key alone does
not prove the command and its receipt committed correctly.

RLS uses transaction-local `app.org_id` from verified server context for SELECT/INSERT/
UPDATE, with both read and new-row scope checks. Missing/invalid scope must expose no
rows and allow no writes; guard invalid settings without leaking cast/database details.
Enable and force RLS on all three tables; the runtime role is neither owner nor superuser
and has no BYPASSRLS or migration privileges. Per-employee access is enforced by the
protected API in addition to tenant RLS; trusted backend context is not proof against a
compromised backend. No cross-owner FK or implicit access to identity/People tables.
PostgreSQL's owner/bypass behavior makes the runtime-role distinction essential; see
[Row Security Policies](https://www.postgresql.org/docs/current/ddl-rowsecurity.html).

Receipt inserts also hold the same employee scope guard as the mutation; a unique
operation-key collision from an unrelated scope is a rejected mismatch after rollback,
never a way to disclose another employee's result. Record a successful create/resume
receipt even if no draft input changed. Discard advances generation and revision only
once, records consequential audit and clears input in the same transaction. Preserve
closed rows while referenced by retained receipts. No cascade deletion removes evidence.

On a lock/deadline conflict, roll back the entire transaction and return safe unresolved/
busy recovery as appropriate; an HTTP response failure after commit still resolves via
the original receipt. Do not emit a committed acknowledgement before database commit.
Counter overflow fails safely rather than wrapping or resetting identifiers; never reuse
scope generations or draft revisions. Both normal and alternate supported writer paths
must satisfy these invariants and the existing fixed lock order.

### Operation fingerprint contract — simplified 2026-10-01

Select plain SHA-256 over a versioned canonical command envelope for E1, replacing
the earlier HMAC proposal after the user's complexity discussion. Canonical JSON uses
[RFC 8785 JCS](https://www.rfc-editor.org/rfc/rfc8785), rejecting duplicate keys and invalid
Unicode while preserving decoded text without normalization. Use maintained hash and
canonicalization libraries. This fingerprint checks consistency, not confidentiality.

The canonical envelope contains: a fixed `leave.draft.command` purpose tag;
fingerprint/command versions; organization, actor and employment UUIDs; operation UUID;
command kind; target draft UUID for save/discard (null for start); submitted expected
revision or generation; and the full validated input for save (null for start/discard).
Canonical UUID strings are lowercase/hyphenated. Revisions/generations use canonical
decimal strings without leading zeros (except generation `0`). Envelope fields are
explicit, not omitted or default-filled during comparison.

Include only stable action inputs, not authorization timestamps, observed employment
revisions, current lifecycle, computed dates/minutes or other changeable server reads.
Those observations belong in committed evidence; including them in the fingerprint
would incorrectly make an identical retry appear to have changed its payload. The
same parsed command with different JSON whitespace/object-key order has the same
fingerprint; a changed note, raw date, inactive-mode entry, mode, format or expected
revision has a different one. JSON escaping differences that decode to the same string
are transport differences, not changes to the stored text. Unsupported versions and
noncanonical counter strings fail validation, never silently downgrade.

Only the backend computes the fingerprint; the browser supplies no trusted digest.
Persist the 32-byte digest and `sha256-jcs-v1` identifier, not canonical command bytes
or draft snapshots. Do not log the canonical envelope. An unkeyed digest may reveal
predictable sensitive values through candidate guessing; neither unique IDs included
in the envelope nor deleting the draft payload makes that risk disappear when the
attacker has those IDs. Treat outcome records as protected business metadata.

There is no HMAC key, key-version column, keyring, rotation or key-recovery gate in E1.
Keep support for the selected canonicalization/fingerprint version while its outcomes
remain retryable. Unsupported versions fail safely; never execute as a fresh operation.
A later algorithm change requires compatible recognition and explicit retained-record
handling, not an automatic rehash from missing original payloads.

The [platform security enhancement candidate](../../../../../platform/docs/architecture/contracts/operation-fingerprint-security-evolution.md)
logs HMAC-SHA-256 for applications whose sensitive-data threat model warrants it.
Leave's pilot security assessment must consider candidate-guessing exposure, including
medical/type data and long-lived outcomes, and adopt stronger protection before that
exposure if required. The simpler E1 design is not a platform-wide ban on keyed hashing.

### Required structural and fingerprint fixtures

- Actual runtime role: missing/malformed/cross-organization context, pooled connection
  reuse after commit/rollback, cross-scope local FK and immutable receipt writes.
- Simultaneous first start, save/discard collision, receipt uniqueness across mismatched
  employee/command inputs, rollback after each mutation step and commit-response loss.
- Payload-null/lifecycle invariants, immutable creation fields, counter overflow and
  allowed alternate writes; no copied note in audit/receipt/log fixtures.
- Canonicalization reference vectors, reordered keys/escaped strings, Unicode scalar
  and surrogate cases, raw whitespace/text changes, mode/format/revision changes and
  duplicate JSON property rejection before model coercion.
- Identical replay after restart/restore, supported fingerprint versions and safe
  failure on unsupported versions. Assert no repeated business effect or leaked payload.
  Key rotation/missing-key cases belong to the deferred HMAC enhancement, not E1.

The pattern is reusable through first-consumer scaffold work; table ownership,
command input and allowed effects remain application-specific. Existing ADRs govern;
no new ADR or application implementation is needed to record this design. Dependency
selection/pinning, actual DDL/adapter artifacts and executable fixture
results remain explicit delivery/readiness evidence, not assumed complete here.


### Mutation acknowledgements and error details — 2026-10-01 proposal

All three mutation endpoints return HTTP 200 only after commit, using the same
shape as a committed outcome lookup: `operation_id` (UUID), `status: committed`,
and `result` (the compact typed object below). Start uses the same status for creation
and resumption; its explicit result distinguishes them. A matching replay returns the
original acknowledgement, not a fresh snapshot of the draft. Responses are private
and no-store. No note, raw date input or whole form snapshot belongs in the outcome.

| Required result field | Type and meaning |
| --- | --- |
| `command` | `start`, `save` or `discard`. |
| `draft_id` | Original target UUID. |
| `revision` | Positive bigint decimal string at this command's commit. |
| `scope_generation` | Nonnegative bigint decimal string at this command's commit. |
| `disposition` | For start: `created` or `resumed`; for save: `saved`; for discard: `discarded`. |

`result` is a discriminated union on `command`; incompatible dispositions and unknown
fields are invalid. Store this acknowledgement with the atomic outcome record.
Replaying start/save after a later discard still identifies that original operation's
commit. It does not say the draft remains active or return discarded input. Resolve
current lifecycle through the authorized draft read before presenting it as editable.
Never redirect an old start result to a newer draft. A resumed start records the
observed revision without rewriting the input or incrementing its revision merely
because the draft was resumed.

An authorized outcome lookup with no visible record returns exactly `operation_id`
and `status: unresolved`; it has no `result`, revision or claim that execution failed.
Current authorization failures remain errors. The client associates acknowledgements
with its sent snapshot and operation ID: an older successful save cannot mark newer
local edits Saved. Revision advancement follows the existing mutation contract.

Refine the shared error envelope with these allowlisted domain details. All counters
are decimal strings, including error responses. No protected details are returned
until organization, caller and resource ownership have been verified.

| HTTP / `error_id` | `details` |
| --- | --- |
| 409 / `leave.draft_revision_conflict` | `{current_revision}`; never the other tab's form values. |
| 409 / `leave.draft_start_outdated` | `{current_scope_generation}`; refresh context, no automatic new action. |
| 409 / `leave.draft_discarded` | `{draft_id}` for the authorized requested draft; no input. |
| 403 / `leave.draft_read_only` | `{reason: employment_ended}` for the existing employment rule. |
| 409 / `leave.setup_required` | `{reason}` from `employment_missing`, `employment_periods_missing`; preserve any authorized saved draft. Missing/invalid timezone is a nonblocking notice, not this mutation error. |
| 413 / `request_too_large` | `{max_bytes: 32768}`; reject without truncation or success acknowledgement. |
| 422 / `validation_failed` | `{fields: [{path, rule}]}`; paths are declared request-field paths and rules are stable allowlisted identifiers; never raw input or exception context. |

Shared authentication/access/dependency and operation-mismatch/busy identifiers retain
their shared meanings. A missing or inaccessible target uses safe 404
`resource_not_found`. E5's submitted error remains future work. Framework and proxy
413 responses need safe client fallback when the common envelope is unavailable; an
unexpected transport/error response never proves a mutation did not commit.

Incomplete or domain-invalid dates/hours remain saveable input under the agreed input
contract; 422 is for structural/format-version/bounds violations, not a new requirement
that a draft be ready to submit. An error's current revision/generation is information,
not permission to silently overwrite or retry with changed guards.

Traceability: E1-AC-03/04/06/07/10/11/14/17, platform ADR-0012/0031/0033/0034
and Leave ADR-0118. Required fixtures cover each discriminated result, matching replay
after closure, stale acknowledgement with newer typing, decimal counters, safe error
details, oversized bodies and malformed/unknown responses. Shared scaffold owns the
generic outcome/error transport; Leave owns dispositions and domain details. Shared UI
uses existing Saved/setup/conflict recovery states. Existing agent guidance suffices;
no accepted ADR changes. Read-response schemas are proposed in the following section. No API,
test or migration is implemented by this wire proposal.

### Draft context and read responses — 2026-10-01 proposal

The user agreed to retain uniqueness, revision, retry-identity and lifecycle protection.
A new intentional save may contain unchanged values; E1 does not compare all drafts for
content duplicates. Retrying an existing operation remains distinct from a new save.

Both reads require current own-read authority and verified organization/employee
ownership. Return private, no-store responses. A read never creates a scope/draft,
advances revision, saves local input or resumes a mutation. UUIDs and bigint decimal
strings retain the preceding wire conventions. These response shapes describe current
observations, not grants that can be reused for a later mutation.

`GET /me/draft-context` returns HTTP 200 with one of these typed variants:

| `status` | Required fields in addition to status |
| --- | --- |
| `ready` | `org_id`, `employment_id`, `scope_generation`, `active_draft`, `editability`, `setup_notices`. |
| `setup_required` | `org_id`, `reason` from `employment_missing`, `identity_person_link_required`, `identity_actor_setup_required`; no invented employment reference, generation or draft-existence claim. |

For `ready`, `active_draft` is null or `{draft_id, revision}`. A null means no active
draft in the verified scope at this read, not a promise that another tab cannot start
one. A valid relationship whose scope row has never been created has generation `"0"`.
Read scope generation and active-draft summary from one consistent local snapshot;
never combine a pre-discard generation with a post-discard draft result. Opening the
summary's draft is a separate authorized read and may observe a later lifecycle.

`editability` is a discriminated object: `{status: editable}` or
`{status: read_only, reason}`. Reasons are `permission_missing`, `employment_ended`,
`employment_periods_missing`. Missing/invalid timezone is a nonblocking setup notice
for draft preservation under Leave ADR-0122, not a read-only reason.
`setup_notices` is an array of safe typed objects `{code}`; E1 codes are
`work_timezone_missing` and `work_timezone_invalid`. Empty means no such known notice,
not proof of complete business setup. No configuration payload or administrator-contact
requirement accompanies it. Notices do not change editable to read_only. They may be
shown near a dependent preview; successful draft saving still reports Saved truthfully.

Here `ready` means the draft scope can be resolved, not that the form is valid or
editable. Missing periods/timezone need not hide an already-owned draft. Resolve
permission restriction before setup/employment reasons; when management is permitted,
resolve timezone setup before date-based employment interpretation. Do not invent an
ended/current state without the work timezone. These checks fit the existing total
deadline and happen outside business locks.

Own-read without own-manage returns readable context with `permission_missing`.
A confirmed management denial is different from an unavailable authorization check:
unavailability returns the shared error and cannot be rendered as a confirmed read-only
permission decision. Service-credential rejection follows the integration-error mapping.
No own-read means access denial, not a successful context containing draft references.

`GET /drafts/{draft_id}` returns HTTP 200 with common required fields `org_id`,
`draft_id`, `revision`, and `state`, plus fields defined by state:

- `state: active`: required `input` (the exact stored input-v1 envelope), `editability`
  as above, `setup_notices`, and server-managed `updated_at` (UTC RFC 3339). Input and revision come
  from the same local snapshot. This read restores stored text, never normalized or
  reparsed replacements. No E3 entitlement/eligibility result is implied.
- `state: discarded`: required `discarded_at` (UTC RFC 3339); no `input` or editability
  field. This is a lifecycle observation, not a form with empty editable values.

Only return either variant after verifying ownership; unknown or inaccessible targets
use safe 404 without cross-employee existence disclosure. Preserve existing drafts
through setup changes, but if person/employment mapping cannot establish ownership,
return safe setup/error handling rather than guessing ownership from supplied IDs,
email or an old browser session. The preservation rule is not an access bypass.
No submitted variant is implemented before E5 defines it.

On ordinary reopening, display the retrieved saved input; it may be incomplete or have
past dates. With newer unsaved local edits, a background/context refresh must not
silently replace the form. Use the agreed conflict/recovery action to review stored
content. A discarded response shows the existing discarded-elsewhere recovery; it
cannot start another draft automatically. A read-only response preserves visible
saved content and explains the restriction without suggesting it was deleted.

Required evidence: E1-AC-01/03/05/09/10/12/13/14/15/17 cover null active scope,
concurrent start/discard between reads, coherent input/revision, current read-only
permissions versus outage, missing setup, ended/future employment, revoked access,
closed payload absence, account change and preserved newer local edits. Generated
clients must distinguish variants and reject malformed/unsupported responses safely.
Scaffold: typed private/no-store reads and state handling; Leave owns draft states and
editability reasons. Shared UI uses existing recovery/read-only presentations. Agent
context/ADRs unchanged. Wire shapes are now proposed for mutations and reads; formal
OpenAPI declarations, schema/constraint mapping and executable evidence remain open.


Audit integration, 2026-10-02: the user approved owner-local required evidence before
effects/content release and nonblocking remote diagnostic export. The
[selection/read-event contract](../../../../../platform/docs/architecture/contracts/e1-security-audit-ownership.md#e1-selection-and-read-event-wire-design--2026-10-02)
defines context acknowledgement separately from employee/draft operation records.
Save/resolve source edits before target selection; a failed target selection never
undoes the acknowledged source draft. The later user-approved simplification removes separate audit writes for ordinary
own-draft GETs; current authorization and consistent input/revision remain required. These add acceptance
fixtures, not new employee confirmation prompts or completed runtime evidence.


Draft attribution clarification — approved 2026-10-02: `created_by`, `created_at`,
`updated_by`, `updated_at` are server-managed fields on the draft itself. Creation and
ordinary autosaves need no separate duplicate audit rows. Retain revision and compact
atomic operation outcomes, plus minimal consequential discard evidence. No separate
audit event is required for opening one's own draft. This refines the earlier
audit integration proposal; accepted ADR-0025 remains unchanged. No full-content edit
history or further sensitive payload retention is introduced.


## Interactive sign-in recovery — simplified 2026-10-05

The user approved ordinary authentication return navigation and recovery of the current
server-saved draft. This replaces the previously agreed custom per-tab recovery carrier
and its proposed v1 schema/30-minute lifetime. See the current contract below.

## Current simple draft failure exits — 2026-10-05

Follow [platform ADR-0050](../../../../../platform/docs/architecture/decisions/0050-inline-draft-save-failure-and-exit-confirmation.md)
and [Leave ADR-0123](../decisions/0123-inline-draft-save-failure-and-exit-confirmation.md).
After bounded recovery cannot confirm saving while editing, show inline Changes not saved
with Retry; typing remains possible without a Keep editing button. Close saved input
immediately. When exit cannot finish saving within the existing bounds, ask Your latest
changes may not be saved. Close anyway? and offer Stay / Close anyway. Switching uses
Stay / Switch anyway. Staying returns to the editor and its inline Retry. Fresh typing
cannot bypass an unresolved save; keep revision/operation safeguards internal.
Leaving abandons unsent local input without deleting saved state or promising rollback
of an in-flight save. Reopen current authorized values; no automatic lost-write replay.
This supersedes the earlier three-choice presentation, not submission safeguards.


The [minimum work-timezone configuration contract](./e1-work-timezone-configuration.md)
now owns E1-CONTEXT's profile/default/override precedence and version-source evidence.
Its effective-boundary and commit-guard details apply only to consumers actually relying
on a dated interpretation, not as a universal prerequisite for draft preservation.


## Draft simplicity amendment — 2026-10-04

[ADR-0122](../decisions/0122-lightweight-draft-compatibility-and-setup.md) supersedes
this contract's earlier timezone-required draft mutation and always-retained obsolete
selection rules. Missing/invalid timezone is nonblocking for authorized input preservation;
it is not a `leave.setup_required` save error or read-only reason. Required identity/
employment ownership and current access still fail closed. Definitively ended employment
retains its read-only rule; absent timezone must not fabricate such an interpretation.

Complete effective-profile/date guarding is required where an action actually relies
on that interpretation, not merely for storing bounded dates/notes. E1-CONTEXT/D1/D2
must reconcile the response/setup-notice and optional dated-observation schemas before
readiness. Existing consequential calculation/submission gates remain unchanged.

Definitively obsolete type/mode choices may be cleared with a brief field notice; preserve
independent values and do not clear on dependency failure. Treat clearing as a normal
input change, using revision/lifecycle checks and truthful save feedback. No GET mutates
stored input, no new default is forced, and no draft is wholly discarded automatically.

Platform authority: [ADR-0049](../../../../../platform/docs/architecture/decisions/0049-lightweight-draft-preservation-and-compatibility.md) generalizes the lightweight preservation approach. Leave ADR-0122 retains the application-specific timezone and obsolete-choice rules; existing accepted ADR text is unchanged.


### Active contract reconciliation — 2026-10-04

The active context/read contract now carries nonblocking setup_notices and no longer
returns a timezone-only draft mutation rejection. A missing timezone uses authorized
People discovery/ownership without fabricating as_of_date or effective eligibility.
Observation evidence distinguishes undated discovery from dated interpretation: omit
an effective date when none was established; never store a fake date merely to satisfy
an earlier receipt shape. Internal evidence schemas must represent both observations
before the corresponding endpoint is ready.

Where a current dated interpretation is actually used to enforce a confirmed employment
restriction, its freshness remains meaningful. Do not make full profile-version machinery
mandatory on the undated preservation path. Existing no-employment/no-period setup and
confirmed ended-employment rules have not been waived by the timezone amendment. The
People discovery contract must provide sufficient authorized period-presence evidence
before using that rule without a dated lookup; do not guess it from a missing date.
This narrow schema integration is still a readiness item, not a new user decision.

Obsolete selection reset is a normal input change: show a brief field notice, set only
the definitively obsolete selected ID/mode to null, retain independent inputs and use
normal autosave. Do not clear an ID just because a paginated list did not contain it;
absence must be definitive under the authorized choice-resolution contract. If clearing
a type makes mode applicability unknown, leave the mode unconfirmed until explicit
selection/resolution; never infer permitted units from a stale catalogue or submit.
No GET rewrites the row, no automatic whole-draft cleanup, and dependency outages do
not erase input. Submission validity is independently enforced in its later contract.


## Undated evidence and definitive draft choices — 2026-10-05

People's discovery `found` response includes required `has_periods`. This answers
whether employment setup has periods without calculating a timezone-dependent status.
No periods retains its agreed setup restriction; periods present plus missing/invalid
timezone permits otherwise authorized preservation under ADR-0122. No effective date
or current/ended claim is invented. Required shared authority/ownership failure still
fails closed; a service outage is never represented as absent periods.

Internal committed observation evidence is a tagged union, separate from the stable
command fingerprint and not returned as a browser authorization token:

- `kind: discovery`: organization/person/employment UUIDs, positive decimal-string
  relationship revision, UTC observed_at and boolean has_periods. No as_of_date,
  employment_state or fabricated timezone/version fields.
- `kind: effective`: the same identities/revision/observed_at plus actual as_of_date,
  employment_state and the period identity from the effective read; include the actual
  Leave timezone/settings source evidence used for that interpretation.

Both retain the authorization decision reference and the existing bounded execution
rules. An identical operation's retry may obtain fresh observations without changing
its command fingerprint. Never add a date merely to satisfy an old evidence shape.
Declared receipt/evidence schemas and tests must support both variants before delivery.
The [draft-choice read contract](./e1-draft-choice-resolution.md) now owns definitive
selected-type resolution; list pagination never proves an existing choice obsolete.

## Saved-draft sign-in return — agreed 2026-10-05

Use the existing supported authentication flow and a validated internal return target.
Do not build the proposed `leave.auth_return.v1` record, custom 30-minute navigation
lifetime, pending-operation persistence or separate recovery protocol. Normal session
renewal comes first; a routine application release must not itself require sign-in.
Returning the next day uses ordinary session handling and authorized draft discovery.
Interactive authentication frequency depends on provider and application session policy;
Microsoft authentication and the resulting Supabase session are separate boundaries.
Actual revocation/reauthentication propagation must be verified for the configured flow.

When interactive sign-in is necessary, stop new saves, use supported auth-adapter return
context and preserve only the minimum validated destination and account binding needed
for identity-safe navigation. Do not replace OAuth/PKCE/state validation or add a second
protocol. Recheck the authenticated account and current organization/resource access
before reopening the current server-saved draft. Different-account return clears prior
protected local context and uses fresh authorized navigation. Missing or invalid return
context also falls back to ordinary authorized navigation. No arbitrary external redirect,
sensitive form contents in URLs, persisted form payload or automatic consequential action.

Unsaved typing is not guaranteed across full-page sign-in. Explain when only saved values
were recovered; do not present an old operation result as the current draft. This is an
application of platform ADR-0032, whose accepted decision remains unchanged.

### Existing write protection remains binding

While the editor and an original operation reference survive, use the existing bounded
outcome/retry flow under current authority. Do not recreate an uncertain request from
missing input or automatically replay writes after a full-page authentication return.
Reload current saved state with its revision/editability. Normal subsequent user edits
use the existing revision/lifecycle checks; concurrent delayed saves must conflict safely
rather than silently overwrite a newer acknowledged revision or reopen a closed draft.
A read, lost reference or elapsed time does not prove an earlier request rolled back.

The delayed-save/reopened-editor ordering case remains a backend concurrency verification
obligation for D2/WRITE, not a reason to require durable browser recovery records. Define
and validate this ordering before the affected story is ready; implementation must test
both possible commit orders. Consequential actions retain their stronger original-operation
recovery and explicit-confirmation requirements. The removal of this browser carrier
neither removes server operation outcomes nor changes execution deadlines.

### Acceptance and reusable impacts

A1/D5 and E1-AC-12/13/15/17 cover silent renewal; actual interactive callback returning
the same account to its permitted saved draft; different account; revoked access; missing
or malicious destination; provider unavailability; honest loss of unsaved typing; and no
automatic write/submit/discard. D2/WRITE also test a delayed save against edits after return,
revision conflict, and closed-draft protection. No custom TTL/4 KiB record tests remain.

Prove the generic renewal, validated destination and identity-safe callback in the shared
shell/generated reference app. Leave supplies its routes, saved-draft loading and lifecycle
presentation. Shared UI, scaffold, acceptance map, UX and tracker follow the same rule;
AGENTS already links ADR-0032 and needs no new policy. No new ADR is needed because
ADR-0032 explicitly permits saved-only recovery and does not mandate a storage mechanism.
Auth-adapter feasibility and actual provider behavior remain evidence requirements;
no application code, credentials, provider settings or runtime storage were changed.


Draft failure presentation update — accepted 2026-10-05: platform ADR-0050 partially
supersedes ADR-0048; Leave ADR-0123 adopts it. Use inline Changes not saved with Retry
while editing; no Keep editing button. Prompt Stay / Close anyway only on exit when
bounded saving cannot be confirmed; switching uses Stay / Switch anyway. Confirmed saved
input closes immediately. Existing revision/lifecycle/retry and access protections stay
binding; no rollback or unsent-input survival promise. D2-B/D3 and shared scaffold/UI
fixtures must prove these cases. Earlier three-choice wording is superseded. This does
not decide whether a workflow needs a draft or change accepted draft scope.


Saving convention — 2026-10-05: Under platform ADR-0051/Leave ADR-0124, E1 retains the autosaved unfinished request. Draft saved denotes input preservation only; Submit request is an E5 consequential action. No redundant Save control or universal draft mechanism. Explicit business-form saving and immediate personal preferences are separate workflows.
