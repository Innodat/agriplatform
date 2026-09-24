# E1 draft persistence and recovery — discussion contract

**Status:** Draft behavior, employment eligibility and discard/retention policy agreed; physical recovery design pending; not story-ready  
**Date:** 2026-09-23  
**Owners:** Leave lead and Platform API owner

This discussion fills implementation choices beneath the existing
[feature specification §7](../../features.md#7-leave-application-experience), spine
AD-4/8/12 and the accepted platform operation/revision/draft rules. It is not a new
feature specification. The approved first journey remains sign in → select
organization → create/resume → autosave → close → reopen.

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

Physical table names, constraint SQL, operation key/fingerprint representation and
cleanup policy remain delivery design; the table above is a proposal, not a migration.

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
or duration mode is introduced by this proposal.

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

This chooses storage of compact evidence over an arbitrary short replay window for
E1. It does not establish permanent retention of all application data. Measure receipt
volume and define a safe compaction/expiry policy before introducing cleanup; never
silently prune evidence and reinterpret an old operation as a fresh action. A keyed
fingerprint over canonical inputs must distinguish payload reuse without making short
sensitive fields guessable from an unkeyed hash; canonicalization, key ownership and
rotation are part of the concrete API/storage contract.

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
| Operation receipt | `leave.operation_receipt`: one record per committed operation, containing caller/scope, operation ID, command, protected input fingerprint, target ID and compact outcome. Multiple saves cannot be represented by only a last-operation field on the draft. No notes or whole draft snapshots in receipts. |
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
