# KDG technical contracts — proposal for readiness

App-owned design only. Does not change the shared Access union, register capabilities,
create DDL/OpenAPI models, or imply that provisioning commands exist. Shared owner
agreement, concrete schema validation and story readiness precede implementation.

## Access integration and roles

Request the canonical Access v2 endpoint using end-user bearer plus KDG service
credential, one exact permission and `authorization_scope: {kind: organization, org_id}`.
Required success evidence: exact permission/scope/account/actor, positive membership ID,
decision_id and checked_at. Proposed KDG resource_scope variants:
`{kind: own_account, account_id}` or `{kind: organization, org_id}`. These are deliberately
different from Leave's own-person variant. Access owner must define its closed union,
caller allowlist, registry/schema constraints and consumers together; KDG cannot invent
that shape at runtime or read Identity/Access tables.

Proposed exact capabilities (final registry IDs are an owner gate):

| Capability | Capturer | Questionnaire administrator | KDG domain check |
| --- | --- | --- | --- |
| kdg_capture.capture.create.assigned | Yes | Yes | Current child assignment and active child |
| kdg_capture.capture.create.all | No | Yes | Any active child in the exact authorized Khula organization |
| kdg_capture.capture.read.own | Yes | Yes | Original capture owner account equals caller |
| kdg_capture.capture.edit.own | Yes | Yes | Original capture owner equals caller; original version validation |
| kdg_capture.capture.read.all | No | Yes | Exact authorized Khula organization |
| kdg_capture.capture.edit.all | No | Yes | Exact authorized Khula organization; preserve owner |
| kdg_capture.questionnaire.manage | No | Yes | Draft/publish rules |
| kdg_capture.child.manage | No | Yes | Active/inactive child management within Khula |
| kdg_capture.assignment.manage | No | Yes | Verified active member with application capture access; app assignment only |

PRD A-1 is user-approved: administrator create-all is required, with no assignment
prerequisite for that capability. Capturer create-assigned still checks current local
domain assignment. Provision eligible active children for each scope; do not use an
administrator capability to upload another user's pending work. No role grants all
future permissions via wildcard. Access role assignment is platform organization authority, not conferred by
questionnaire-administrator. KDG facilitator screen can select eligible accounts for
child assignment and link shared onboarding/access screens when available; it does not
create Auth accounts, employment or grants itself.

Server uses current Access verification before the DB transaction. Proposed authorization
request limit 5 seconds, total executing request 10 seconds, DB lock wait 2 seconds;
if execution has not started promptly after authority check, recheck. No network wait
under business locks. Record decision/action timing safely. Local assignment/child state
is checked under the same transaction serialization boundary as capture create. A queued
command submitted after removal is refused; no old local observation authorizes sync.

### Entry capability and context proposal

For the two maintained default KDG roles, use capture.read.own as the proposed entry
capability: both roles explicitly hold `kdg_capture.capture.read.own`. Access owner
must finalize that registration/caller binding; no new shared contract is changed here.
Entry establishes current account/actor/Khula membership/admission only, grants no
additional action, and does not renew cached create/admin/assignment authority.
The selector-free `/context` endpoint is independently deliverable before `/provision`;
its exact draft fields/negative cases are in approved Story 1.1 in epics.md. Existing/revoked child
assignments are not an entry prerequisite; current capturers may retain own history.

## Questionnaire documents

Definition `schema_version: 1`, `questions` ordered array. Each question has UUID `id`,
type `rating | boolean | text`, label, required boolean and type-specific configuration.
MVP rating uses integers 0–5 and explicit endpoint labels; intermediate descriptions
remain absent until Khula supplies them. Boolean supports details_enabled and details_label;
initial seed uses default false (Nee). Text has plain multiline content, no rich HTML.
No executable expressions/markup, arbitrary branching or external form schema engine.

Proposed validation bounds: 50 questions/version, label 500 characters, details/text
5000 characters, total command 128 KiB UTF-8. Empty required text fails after whitespace
normalization; preserve original entered content when valid. UUID question keys must be
unique in each version and stable across compatible edits. Reject unknown types, keys,
duplicate JSON keys and answers outside the pinned definition; do not silently drop data.
Bounds are architecture proposals to validate/approve before editor story readiness.

Answer map keys are question UUIDs. Rating answer `{value: integer}`; boolean
`{value: boolean, details?: string}` (details permitted only for true when enabled);
text `{value: string}`. False excludes details completely. Optional unanswered question
may be absent; required rating cannot default to zero. Unsaved forms may be incomplete and hold temporary hidden-details buffers in memory
only; completion requires required answers. No observation draft store is used.

Relational version identity `(org_id, questionnaire_id, version_id)` is referenced by
capture. Publish allocates increasing display version and immutable definition/hash.
History references exact definition, not latest labels. Retiring a question removes it
from future published versions only. Old published versions are retained indefinitely
until an explicitly reviewed retention/support policy; no release disables old queued
captures merely because a new questionnaire was published.

## Persistence and attribution seed

KDG owns schema `kdg_capture`, independent Alembic history/version table and runtime
identity. Exact DDL and privileges belong to the consuming story. Proposed records:

- Questionnaire and version: stable identity, org scope, draft revision or published
  immutable version, validated definition, creation/publication actor/time.
- Child: UUID, org_id, display name, active/inactive, revision, attribution. No shared
  People record or identity account for a child.
- Assignment: org/child/account identifiers, active state, revision, actor/time and
  history. Same-org child reference; account eligibility checked over HTTP before short
  local write, with bounded execution and no invented shared-table FK.
- Capture: device UUID, org_id, child_id, questionnaire/version IDs, observation_date,
  answers JSONB, immutable owner account + actor, untrusted local captured_at,
  server created_at/created_by/updated_at/updated_by and integer server revision.
- Capture revision: immutable authorized domain snapshot and change provenance per
  server revision, original owner plus actual editor. Sensitive answers belong only
  here and capture, never generic operational logs. No separate duplicate audit table
  copying every snapshot; compact publish/assignment evidence uses owner-local events.
- Operation outcome: unique org/caller/command/operation identity, fingerprint version,
  compact committed result and executor/time. HMAC-vs-SHA fingerprint selection is an
  explicit sensitivity review before schema readiness; no plain-text answer in receipt.

Tenant-aware local FKs prevent capture/version/child cross-org references; immutable
history includes same-org capture reference and unique `(org_id,capture_id,revision)`.
No unique child/date constraint. All writes participate in revision/attribution checks,
including operator setup; alternate-writer and restricted-role tests prove enforcement.
Shared actor IDs are resolved/retained through Identity policy; account deletion never
deletes original capture or actor history. Client cannot set author/audit timestamps.

Device recorded time remains visible as recorded on phone; server creation time means
first verified server commit. Preserve both rather than pretending offline device time
is a trusted audit timestamp. Pending local revisions have local sequence and device time;
they become server revisions only after acknowledgement.

## Proposed API routes and safe outcomes

All business routes under `/api/v1`, authenticated, fixed-org policy enforced server-side,
private/no-store. Pydantic/OpenAPI is the authoritative future schema; generate/validate
TypeScript, do not derive client models from DB tables.

| Route | Contract seed |
| --- | --- |
| GET /context | Online current KDG entry evidence: bearer-derived account/actor, current membership, exact Khula organization entry permission, decision ID/time; no domain provisioning or offline lease |
| GET /children | Current account capture-eligible active children: create-all grants all within Khula; create-assigned grants own assignments; no account/org selector or offline lease |
| GET /provision | Initial setup schema: verified account/actor/membership, exact scoped seven-day observations, eligible children and immutable latest published definition; capture history downloads remain a separate paginated read |
| GET /questionnaire-versions/{id} | Exact authorized original version, including historical retained versions |
| POST /captures | UUID capture_id, operation_id, command_version, child_id, questionnaire_version_id, observation_date, answers, local captured_at; owner derived from bearer, no supplied owner |
| GET /captures/{id}/edit-context | Current own-read/edit scope, record/revision/original definition and scoped observation; no new-create/assignment requirement |
| PUT /captures/{id} | operation_id, command_version, expected_revision decimal string, editable date/answers; immutable child/version/owner |
| GET /captures and /captures/{id} | Keyset page / full record with revision and source version, own/all-permitted filter |
| GET /operations/{id} | Caller/command-scoped committed compact receipt or unresolved; current access required |
| Admin questionnaire draft/save/publish | Explicit expected revision + operation identity; publish stores immutable version atomically |
| Admin child/assignment save | Exact account/child, expected revision/operation ID, current admin authority and scoped eligibility |

Proposed 100 rows/page maximum and opaque scoped pagination cursor; page results are not
server authorization for cached data. Initial default download: last 30 days (approved PRD A-5),
own for capturer/all permitted for administrator. Retain all pending captures/conflicts/
referenced versions regardless of history window. Fetch older history explicitly online;
no requirement to download an entire organization. Downloads update server baselines, never overwrite pending
local overlays, base snapshots or conflicts; status reflects the latest local sequence. Refresh every record's current revision
from permitted server reads when processing conflict, not from a cached list.

Use platform [error/outcome contract](../../../platform/docs/architecture/contracts/api-errors-and-operation-recovery.md).
401 authentication_required; 403 access_denied; 404 resource_not_found (inaccessible
records disclose no existence); 409 operation_payload_mismatch or
kdg_capture.capture_revision_conflict with current_revision; 422 validation_failed with
safe paths/codes only; 503 authorization_unavailable/dependency_unavailable; 500 internal_error.
Additional safe attention IDs: assignment_unavailable, child_inactive,
questionnaire_version_unavailable, unsupported_command_version. Labels never drive branches.
Server conflict returns no unauthorized answer snapshot; fetch current details under permission.

Success/outcome: `{operation_id,status: committed,result:{capture_id,revision}}`. A replay
returns original receipt even if current record is newer. `status: unresolved` permits
same-payload retry, not a claim of no commit. No synced feedback without a matching receipt
and current local sequence. Compatibility tests cover both legacy shared error families.

## Local persistence, queue and reconciliation

Account/org namespace contains versions, children/assignment observations, downloaded
captures, pending capture revisions, queued actions, conflicts,
schema metadata and last verified local-use context. Service worker caches only revisioned
shell assets and offline navigation; auth/provider/API routes are network-only. Store
access tokens through existing app-specific auth boundary, never in command payloads.

Entry: in-memory editing → explicit Save → atomic completed local capture plus pending
create operation. No automatic unfinished-input write/resume or active-draft constraint.
Allow several completed captures per child/date; use a fresh resource/operation identity
for each distinct observation. Resolve one uncertain attempted Save under its original
IDs/immutable input before a changed attempt; repeat clicks cannot duplicate it.
Temporary hidden detail text exists only while editing and is excluded from false answers.

Queue per record: pending → in_flight → committed, or attention with durable cause.
An in_flight claim has a recoverable attempt identity/expiry; crashes return to uncertain
outcome resolution. Multiple tabs serialize claims with IndexedDB transactions; a lease
may prevent excess calls but server operation uniqueness remains the safety guarantee.

Each Save creates a stable durable action ID and local snapshot. Once eligible to send,
materialize/freeze its wire payload (including predecessor's acknowledged expected revision).
A second offline Save is persisted as a dependent action; do not mutate the earlier
in_flight payload or submit the later action against guessed server revision. Creates
precede edits. Response arriving after a newer local Save acknowledges only its local
sequence; the newer content remains Saved on this phone. Never replace local edits
with the older acknowledged server snapshot.

Foreground triggers: open, pageshow/resume/visible, online event and Sync now. A network
event starts an attempt, not proof of reachability. Proposed 30-second cycle, 10-second
request maximum, exponential delays 1/2/4 seconds with jitter for transient failures,
at most three sends per operation/cycle, then pending Retry/Sync now. Process independent
records even if another record needs attention. No perpetual spinner or exclusive reliance
on background sync. Recheck current authorization on every request, including retry/outcome.

Conflict retains base, local proposal and safely fetched current state. Resolution is
explicit complete-answer selection (field-by-field comparison can guide it, no automatic
merge); use-server resolves local branch with explicit warning, keeping prior conflicted
proposal as protected resolution evidence until retention policy. Save reviewed changes
issues a new operation against current revision. Dependent unsent edits remain preserved
for re-review; do not automatically replay them over resolution. Original author never changes.

Known online denial locks/removes affected downloaded display cache and invalidates local
authority; preserve pending work in a locked partition. Assignment denial stops new create
but does not automatically delete own history; user-approved history policy is PRD A-2; deactivated-child historical editing is user-approved in PRD A-6.
Never upload rejected work as an administrator or reassigned child on behalf of author.
Recovery requires regained same-user authority or separately authorized domain handling;
there is no export/impersonation feature in MVP.

## Offline window, logout, storage and upgrades

Last successful online authorization records server checked_at and expires_at seven days
later for each local account/Khula capability observation. Capabilities not refreshed do
not inherit a refreshed lease from unrelated success. Use pinned account identity and
monotonic elapsed time within a process; clock rollback or implausible time locks until
online verification. Across restarts browser clock is not tamperproof; this is managed
application behavior, never trusted server evidence or protection against same-origin JS.
Offline admin permits downloaded history/edit only, not configuration administration.

Logout immediately cancels background attempts and closes visible partition. A response
after logout may be recorded only in its original partition, never rendered elsewhere;
do not delete uncertain operation IDs. A returning identical verified account rechecks
access before unlocking; another account cannot claim work. Retaining locked data is not
encryption against someone controlling the phone/browser origin. Shared-device/at-rest
requirements and retention require Khula review before a real child-data pilot.

Request persistent storage where supported and inspect quota estimates; lack of permission
is not a guarantee of failure, grant is not a backup. Evict only re-downloadable acknowledged
history, never pending actions/conflicts/referenced versions. Handle transaction
abort/quota failures before feedback. Private browsing is not a supported durable setup.
No promise against user clearing data, uninstall/OS deletion or storage eviction.

Quota recovery may reclaim only verified disposable/re-downloadable cache, followed by
one bounded retry; repeated quota failure stops automatic attempts and keeps current
input on screen with plain guidance. Do not intentionally crash or reset the database;
restart is not a remedy for quota and can lose input still in memory. The proposed
unfinished-form recovery option was rejected on 2026-10-13. Explicit Save and completed-
capture persistence remain; no draft list, local-draft merge or unfinished-form store.

Local migration uses IndexedDB versionchange transaction, old-to-new fixtures, closed
connections and version compatibility. Failed upgrade leaves prior data intact and blocks
new writes with Retry; never deleteDatabase as recovery. Shell update is prompt-based;
defer activation until open input is explicitly saved or deliberately abandoned, then
stop sync and wait/close other versioned connections before activation. No unfinished
form checkpoint is created to enable an update.
An unsupported queue schema is retained as attention; ordinary API release supports
previous running client/queue versions. Publication never silently migrates an open entry or saved capture.

## Initial questionnaire setup increment

Approved Story 1.2 supplies `questionnaire.bootstrap_initial` through the existing
owner-local operator tooling. Its typed organization-scoped command creates the exact
initial immutable version and operation/change evidence in one KDG transaction;
`GET /api/v1/questionnaire-versions/{version_id}` proves current authorized retrieval.
Read requires current `kdg_capture.capture.read.own` entry capability for both default
roles, but grants no create/edit/admin power. Child/assignment records and `/provision`
are subsequent consumers, so this increment has no forward dependency on them.

Explicit fixed questionnaire/version/question UUIDs, expected absence, reason/evidence
and definition bind the initial command. Identical operation replay returns the original
receipt; different input conflicts; fresh expected-absence setup cannot overwrite an
existing version. Executor/time derive from trusted operator context. Only synthetic
fixtures are used in eventual delivery acceptance; this planning package executes no
command or live setup. See [approved Story 1.2](epics.md#story-12-provision-and-retrieve-the-initial-published-questionnaire)
for exact criteria, ownership and prereadiness contracts.

## Initial child/assignment setup increment

Approved Story 1.3 adds KDG-owned `child.bootstrap_initial` and `GET /api/v1/children`.
The command binds exact child/assignment/account IDs and expected absence, writes only
KDG state and never grants membership/access. Ordinary API reads use current bearer,
fixed Khula and exact same-organization create-all/create-assigned authority. Capturers
see active assigned children; administrators see all active children, independent of
assignments. Entry-only users receive an explicit no-create state, not another user's
choices. Verification outage is distinct from a confirmed empty/no-permission result.

Existing Identity/Access owners must define trusted operator verification of the exact
assignment target's current account/membership/capability before this story's Build gate.
Their user-bearer `/v2/check` cannot check another account through a selector; operator
bearer identity is not the target identity. No new public/shared endpoint is asserted
here. Bound observed target evidence and executing write freshness; remote verification
stays outside local business locks. Current target verification and ordinary consumer
checks separately prove setup, rather than treating old receipts as current authority.

Assignment identity is account-bound within org/child scope with server revision and
attribution. Later membership-rejoin handling for old assignments is an explicit E5
lifecycle decision; no missing current app grant can be resurrected by an assignment.
See [approved Story 1.3](epics.md#story-13-provision-the-initial-child-and-facilitator-assignment).

## Initial offline phone setup increment

Approved Story 1.4 composes the approved entry/child/version domains into the
selector-free `/provision` setup read. Its initial schema contains no capture/history
payload or dependency. Current exact capabilities and account/actor/membership/scope
must agree; include verified permission/resource checked_at and expires_at (seven days),
plus observed eligible child/assignment revision evidence. Administrator create-all
requires no fabricated assignment. Missing/denied capabilities mint no positive local
observation; unavailable checks are not confirmed denial or an empty successful result.

The browser downloads shell assets outside local data transactions and commits complete
setup plus active snapshot metadata atomically in its account/Khula IndexedDB partition.
Only acknowledge offline setup once both shell readiness and local snapshot are verified;
Cache Storage and IndexedDB are not one atomic transaction. Known denial invalidates its
corresponding local authority, account/entry denial locks the partition, and stale session
callbacks cannot publish a snapshot after logout/account change. Exact-scope observation
renewal never extends stronger unobserved rights. This is device-local policy only.

Manifest/service worker caches public versioned shell assets, not protected API/Auth
responses. Offline setup UI reads IndexedDB directly under the valid local window;
private local bytes are not a generic HTTP-cache fallback. Keep initial stores limited
to setup metadata, observations, eligible child snapshots and immutable versions. No
future capture/queue store is required to prove installed offline setup reopening.
Future version refresh updates only new-entry selection, preserves immutable definitions
and later pinned open-entry/capture references. Do not delete a failed/unsupported local schema.
See [approved Story 1.4](epics.md#story-14-install-kdg-capture-and-provision-authorized-setup-for-offline-opening) for acceptance/device scope.

## Explicit observation Save increment

Approved revised Story 1.5 renders the initial form and stores a completed local capture plus
pending create command atomically only on Save observation. Current required local
creation/child scope, complete answers and account/actor/version binding are validated.
An open entry pins its questionnaire in memory; no auto-checkpoint, draft/recovery store,
active-draft uniqueness, draft list or unfinished-form merge is required.

A capture UUID and distinct operation UUID freeze one attempted Save. Resolve uncertain
local results before changed input/new attempts; success follows commit only. Multiple
same-day captures remain valid. Completed local records have minimal own-partition list/
details/reopen and pending status; server upload follows in its own story.

Hidden-details buffers remain in memory and are excluded from saved false answers.
Before-Save closure/restart may lose typing; app-controlled exit uses ordinary unsaved-
change confirmation, not a draft flush. See [approved 1.5](epics.md#story-15-explicitly-save-an-observation-on-this-phone)
and proposed [application rationale](architecture/decisions/0001-explicit-observation-save.md).
Storage failures still retain visible input with bounded safe recovery/plain guidance;
removing autosave does not remove failures at explicit Save.

## Create synchronization increment

Approved Story 1.6 consumes completed local captures/pending commands through the current-
authorized create API, original-caller outcome lookup and own single-record read.
Current author/Khula/child and exact original published version are verified before
capture, initial revision and compact receipt commit atomically. Frozen IDs/content
survive lost responses and repeated attempts; unknown outcome never creates a new action.

Operation lookup uses current own-read and original caller/capture-create command scope;
it may recover a committed receipt after create permission is removed, but authorizes
no new write. POST retries still need current creation authority. Pending input from a
different account cannot be sent under an administrator or replacement account.
Foreground open/resume/reconnect/Sync now uses bounded claims/recovery/retries. Only a
matching acknowledged snapshot becomes Synced; late/out-of-order callbacks retain newer
local work. Known rejection keeps local capture/intent with scoped attention/lock states;
verification unavailability differs from denial. Ordinary releases preserve queued versions.

Concrete create/outcome/read DTOs, capture fingerprint/retention and restricted DB fixtures
remain before Build; no new universal sync service or worker is required. See
[approved Story 1.6](epics.md#story-16-synchronize-a-saved-capture-and-view-its-server-backed-record). Server history pagination/editing and
organization-wide administrative reads remain subsequent consuming epics.

## Own-history download increment

Approved Story 2.1 extends own-current-read with paginated history and original definitions,
using phone-date/previous-29-day observation bounds fixed during a download. Older
ranges are available online. Each page rechecks exact own-read; no account/org selector,
creation/assignment requirement or all-record permission is inferred. Backend returns
only original-owner records, with their permitted child labels even after unassignment.

Scope/filter-bound cursor pagination uses immutable server creation time/ID, not mutable
observation dates/answers; it does not imply a cross-request database snapshot. Merge
permitted full pages/needed versions and progress atomically. Retain pending local
snapshots/operations/base references; downloaded existence alone is not an uncertain-
operation acknowledgement. Older responses cannot replace newer server baseline, and
missing rows never prove deletion or permission loss. Label partial/unavailable vs empty.

Successful history requests renew only their exact scoped read observation. Default
window does not delete pending data or locally authored captures outside that window;
MVP does not auto-prune locally authored records. Only re-downloadable acknowledged
cache can be reclaimed; concrete authored-record retention remains E5/pilot policy.
See [approved Story 2.1](epics.md#story-21-browse-my-capture-history-online-and-offline). This story does not require
edit API, revision-list presentation, editor publication or all-history administration.

## Own-capture editing increment

Approved Story 2.2 consumes own history with explicit Save/Cancel, original questionnaire
and immutable owner/child/version. Offline Save atomically stores saved overlay/edit
intent; no unfinished typing is persisted. Extend setup/edit-context with exact own-edit
observations, independently checked. Unassignment does not remove historical own-edit
rights; user-approved A-6 likewise preserves historical editing for inactive children.

PUT uses expected server revision, immutable operation identity and date/answers only.
Current own-edit/ownership/original validation precedes atomic conditional mutation,
immutable revision evidence, trusted update attribution and receipt. Unchanged authorized
saves produce no fictitious history/revision. Per-record predecessors define eligible
command materialization; forms pin the actually reviewed base. Conflicts preserve saved
proposals and pause descendants without auto-rebase; resolution UI follows separately.

Extend current own-outcome lookup for capture.edit without permitting another owner's
receipt/resource. Read-only/create successes do not renew edit scope. Same-owner pending
creates may be edited locally under current own-edit observations; send only after the
create receipt resolves the server base. See [approved Story 2.2](epics.md#story-22-edit-my-captures-offline-and-synchronize-explicit-changes-safely).
No administrator all-edit API or live new questionnaire producer is needed here.

## Own-conflict resolution increment

[Approved Story 2.3](epics.md#story-23-review-and-explicitly-resolve-conflicting-saved-changes) compares retained
explicitly saved changes and current authorized state, then offers use-current or a
reviewed replacement. Reuse current read/edit-context and revision-checked PUT; no new
conflict service or override endpoint. Replacement pins the revision actually reviewed
and gets a new operation identity. Unknown outcomes resolve before competing writes.

Commit local resolution metadata, selected complete result and descendant dispositions
atomically. Later queued edits remain paused for explicit review or explicit inclusion;
never automatically replay them over the chosen result. Preserve former saved proposals
under the same account/organization retention rules. Unsaved review typing stays in
memory; retained local conflict work is not a server-backup promise. Repeated concurrent
change requires review again. Offline comparison uses permitted retained snapshots;
server replacement requires current authorized state and checked delivery.

## Simple offline history boundary — revised 2026-10-14

[Approved Story 2.4](epics.md#story-24-prove-simple-offline-capture-history-and-editing) proves
simple current-observation history/details and E2 editing. No revision-browser API,
revision downloads or local revision archive. Show observation date and answers with compact capture status; audit
attribution is stored internally and presented on authorized administrator surfaces.

Persist current captures and required original questionnaire definitions, pending
commands/reviewed bases and conflict proposals. Original definitions are necessary to
render/edit old captures; they are not a user-managed version history. Internal server
revision tokens and immutable business evidence remain as previously agreed, without
requiring a user interface or copying the audit archive to phones.

Common local transaction/migration, partition, queue/retry/idempotency, conditional
revision/conflict, sync-status and app-update/test primitives belong with existing
platform scaffold/UI owners when proven domain-neutral. Keep KDG semantics and APIs
application-owned; no new offline service or generic history engine. Shared changes
remain gated on coordinator/Leave ownership handoff.

## Initial provisioning and operational envelope

Use the accepted [controlled provisioning design](../../../platform/docs/architecture/contracts/e1-controlled-provisioning-and-evidence.md):
explicit environment target, verified operator identity, owner-specific authority,
operation IDs, expected state, atomic owner-local outcome/evidence. Not raw SQL in app
startup, browser seeding or migration inserting Auth accounts.

Sequence after approved implementation: Identity verifies/creates only authorized profile/
actor/membership through supported ownership; Access configures KDG admission and Louwnique's
explicit capabilities; KDG owner command creates initial child/assignment and validated
published version. Synthetic equivalents serve local/CI/device proof. Replays/partial
cross-owner failure resume from known receipts. The command adapter/trust/privileges are
not installed yet; exact invocation is a readiness input. Normal admin portal follows later.

Existing release tooling registers KDG owner and dependencies, uses isolated credentials,
coordinates migrations before activation, and verifies old API/queue compatibility under
ADR-0020. No Content/People/notification worker is necessary. Structured diagnostics expose
safe IDs/categories, no observation payloads. Domain revision histories are separately
authorized. Select deployment hostname/TLS/callback/CORS, backup recovery and operational
retention before pilot release, not during initial planning execution.

## Approved presentation and conflict responsibility — 2026-10-14

User-approved with C: routine capturer details show observation date/answers and
compact save/sync feedback; audit creation/modification actors/timestamps stay stored
and are exposed to authorized administrator audit presentation in E3. Observation
date is the editable day observed, not server creation time (which may be delayed by
offline sync). No new always-visible audit panel in the capture interface.

The editor/device holding a conflicting saved proposal resolves that
proposal: capturer for own pending edits, administrator for their own pending edits
to authorized records. Reading first does not claim resolution rights or remove
another device's pending work. Conditional server writes still arbitrate concurrent
resolutions. Administrator reads cannot discover proposals never synchronized from
a facilitator phone; central conflict intake/delegation is outside MVP. Existing
own/all permissions apply; no separate supervisor, impersonation or local partition
access is granted. This approved presentation clarification supersedes earlier
routine attribution-display wording; stored provenance and conditional writes remain.

## Administrator read/audit increment

[Candidate Story 3.1](story-candidates/3-1-administrator-history.md) extends existing
record/history reads with explicitly checked read.all and exact local all-read
observations. Backend filtering and local rendering never infer all scope from
membership, platform admin or own-read. Same 30-day default and safe-cache rules apply.
Compact Audit details is an online administrator surface over record-owned committed
evidence with current all-read, bounded pages and safe actor display. No revision
archive download/restore or new audit service; no all-edit authority is minted.
