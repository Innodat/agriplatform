# KDG technical contracts — proposal for readiness

Current KDG retry decision, 2026-10-22: [ADR-0061](../../../platform/docs/architecture/decisions/0061-kdg-first-committed-operation-wins.md) selects first committed request wins for capture.create/edit. It supersedes earlier fingerprint/HMAC prerequisites; other owner contracts retain their choices. No runtime conversion is implemented.

App-owned design, reconciled with the selected [shared readiness addendum](../../../platform/docs/architecture/contracts/kdg-shared-readiness.md).
Does not implement the shared Access union, register capabilities,
create DDL/OpenAPI models, or imply that provisioning commands exist. Shared owner
agreement, concrete schema validation and story readiness precede implementation.

## Access integration and roles

Request the canonical Access v2 endpoint using end-user bearer plus KDG service
credential, one exact permission and `authorization_scope: {kind: organization, org_id}`.
Required success evidence: exact permission/scope/account/actor, positive membership ID,
decision_id and checked_at. Proposed KDG resource_scope variants:
`{kind: own_account, account_id}` or `{kind: organization, org_id}`. These are deliberately
different from Leave's own-person variant. The shared addendum defines its closed union,
caller allowlist and exact registry extension; owners deliver constraints/consumers together. KDG cannot invent
that shape at runtime or read Identity/Access tables.

Exact capability IDs selected in the shared owner planning baseline (registration not implemented):

| Capability | Capturer | Questionnaire administrator | KDG domain check |
| --- | --- | --- | --- |
| kdg_capture.capture.create.assigned | Yes | Yes | Current child assignment; active child for fresh choices, or verified prior eligibility for pending inactive-child sync |
| kdg_capture.capture.create.all | No | Yes | Exact Khula scope; active child for fresh choices, or verified prior eligibility for pending inactive-child sync |
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

Server uses current Access verification before the DB transaction. Selected authorization
request limit 3 seconds, total executing request 10 seconds, DB lock wait 2 seconds,
statement timeout 5 seconds; start local execution within 1 second of the observation
or recheck. No network wait
under business locks. Record decision/action timing safely. Local assignment/child state
is checked under the same transaction serialization boundary as capture create. A queued
command submitted after removal is refused; no old local observation authorizes sync.

### Entry capability and context proposal

For the two maintained default KDG roles, use capture.read.own as the proposed entry
capability: both roles explicitly hold `kdg_capture.capture.read.own`. The shared addendum
selects registration/caller binding; runtime registration remains prerequisite delivery.
Entry establishes current account/actor/Khula membership/admission only, grants no
additional action, and does not renew cached create/admin/assignment authority.
The selector-free `/context` endpoint is independently deliverable before `/provision`;
its exact draft fields/negative cases are in approved Story 1.1 in epics.md. Existing/revoked child
assignments are not an entry prerequisite; current capturers may retain own history.

## Questionnaire documents

Definition `schema_version: 1`, `questions` ordered array. Each question has UUID `id`,
type `rating | boolean | text`, label, required boolean and type-specific configuration.
MVP rating uses integers 1–5 (1 = Goed, 5 = Nie goed nie); reject 0, 6 and fractions.
Intermediate descriptions
remain absent until Khula supplies them. Boolean supports details_enabled and details_label;
initial seed uses default false (Nee). Text has plain multiline content, no rich HTML.
No executable expressions/markup, arbitrary branching or external form schema engine.

Selected KDG bounds for delivery review: 50 questions/version, label 500 characters, details/text
5000 characters, total command 128 KiB UTF-8. Empty required text fails after whitespace
normalization; preserve original entered content when valid. UUID question keys must be
unique in each version and stable across compatible edits. Reject unknown types, keys,
duplicate JSON keys and answers outside the pinned definition; do not silently drop data.
Use identical bounds in editor/API fixtures; implementation proves enforcement.

Answer map keys are question UUIDs. Rating answer `{value: integer}`; boolean
`{value: boolean, details?: string}` (details permitted only for true when enabled);
text `{value: string}`. False excludes details completely. Optional unanswered question
may be absent; required rating starts unanswered rather than defaulting to 1. Unsaved forms may be incomplete and hold temporary hidden-details buffers in memory
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
- Operation outcome: unique org/caller/command/operation identity, supported command/result
  versions, compact committed result and executor/time. No command fingerprint metadata
  is required for current capture.create/edit; no plain-text answer in receipt.

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
| GET /operations/{id}?command_type={type} | Required closed command discriminator; caller/command-scoped committed compact receipt or unresolved; current access required |
| Admin questionnaire draft/save/publish | Explicit expected revision + operation identity; publish stores immutable version atomically |
| Admin child/assignment save | Exact account/child, expected revision/operation ID, current admin authority and scoped eligibility |

Selected 100 rows/page maximum and opaque scoped pagination cursor; page results are not
server authorization for cached data. Initial default download: last 30 days (approved PRD A-5),
own observations for either role in the PWA; all-organization portal reads stay online. Retain all pending captures/conflicts/
referenced versions regardless of history window. Fetch older history explicitly online;
no requirement to download an entire organization. Downloads update server baselines, never overwrite pending
local overlays, base snapshots or conflicts; status reflects the latest local sequence. Refresh every record's current revision
from permitted server reads when processing conflict, not from a cached list.

Use platform [error/outcome contract](../../../platform/docs/architecture/contracts/api-errors-and-operation-recovery.md).
401 authentication_required; 403 access_denied; 404 resource_not_found (inaccessible
records disclose no existence); 409 operation_busy or
kdg_capture.capture_revision_conflict with current_revision; 422 validation_failed with
safe paths/codes only; 503 authorization_unavailable/dependency_unavailable; 500 internal_error.
Additional safe attention IDs: assignment_unavailable, child_inactive,
questionnaire_version_unavailable, unsupported_command_version. Labels never drive branches.
Server conflict returns no unauthorized answer snapshot; fetch current details under permission.

Success/outcome: `{operation_id,status: committed,result:{capture_id,revision}}`. A replay
returns original receipt even if current record is newer. `status: unresolved` permits
retry of the frozen submitted snapshot, not a claim of no commit. No synced feedback without a matching receipt
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
Administrators use own-capture/read/edit offline in the PWA. Organization-wide reads,
edits and audit require online portal access; do not issue offline all-read/all-edit
observations or persist another author's records on the phone.

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

Concrete create/outcome/read DTOs, outcome retention and restricted DB fixtures
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

## Administrator read/audit increment — approved surface split

[Approved Story 3.1](epics.md#story-31-view-authorized-khula-observations-and-administrator-audit-details)
extends online record/history reads with explicitly checked read.all. No offline
read.all observation, organization-wide download or IndexedDB/service-worker cache.
The PWA remains own-only for both roles. Compact Audit details is an online administrator
surface over record-owned evidence with current all-read and safe actor display.
No revision archive/restore or new audit service; no all-edit authority minted here.

## Online administrator edit increment — approved

[Approved Story 3.2](epics.md#story-32-correct-authorized-observations-online-without-overwriting-another-editor)
adds online all-edit/context/operation recovery with preserved original owner and actual
editor. No offline all-edit observation or other-author local cache. Reuse conditional
writes and explicit comparison; keep administrator attempted answers/reviewed base in
memory while the form remains open. No server conflict-input store, draft, autosave or
proposal retrieval endpoint. Closing/reloading may discard uncommitted answers.
Successful edits commit required audit and compact operation receipt; unknown outcomes
resolve the original operation before competing writes. A rejected conflict is not a
committed edit. Exact all-edit/context/conflict/outcome contracts gate Build. Capturer
explicitly saved offline edits/conflicts remain durable under E2; no phone-input intake.

## Questionnaire draft editor increment — approved scope

[Approved Story 4.1](epics.md#story-41-edit-and-save-a-questionnaire-draft-online) adds app-owned
working-draft start/read/whole-form Save/Cancel under current questionnaire.manage.
Published definitions remain unchanged. Stable IDs survive compatible wording/order
changes; new/incompatible question types get new IDs. One working draft per
questionnaire is approved with explicit atomic create/resume (ADR-0034 opt-in), not a
general autosave mandate. Draft lifecycle/start/conditional-write/outcome DTOs and
validation limits gate Build. Publish is the next independent increment.

## Questionnaire publication increment — approved scope

[Approved Story 4.2](epics.md#story-42-publish-a-questionnaire-without-changing-older-observations) publishes
the exact saved working copy with current manage authority and guarded draft/current
publication state. Immutable version, live pointer, draft closure, evidence and receipt
commit atomically. New working copy requires explicit start; stale saves cannot reopen
a published draft. Old-version creates/edits remain valid; open entries stay pinned
and only subsequent new captures adopt a successfully downloaded newer definition.
Actual editor/publication plus installed Android/iPhone scenarios prove compatibility.

## Child-management increment — approved scope

[Approved Story 5.1](epics.md#story-51-manage-children-online-without-losing-their-observations)
adds online child.manage list/create/update with explicit Save/Cancel, stable child UUID,
display name and active status. Ordinary deactivation removes refreshed new choices but
does not reject pending offline observations solely for inactive status: verify prior
provisioned child eligibility and current membership/app/create/assignment authority.
Retain historical own/all correction under current rights. Fresh inactive-child creation
is not enabled. Client pending flags/dates cannot prove eligibility or pre-deactivation
Save timing; concrete issued/stored eligibility reference and compatible create/provision
DTOs gate Build. Do not relax current server access checks. Privacy restriction/deletion
is separate from ordinary child availability and needs Khula retention/processing policy.

Reactivation restores only valid assignment/create eligibility, never platform grants.
No child deletion or People master. Name/status/revision/outcome and coordinated-create
fixtures gate Build.

## Facilitator-assignment increment — approved scope

[Approved Story 5.2](epics.md#story-52-assign-children-to-verified-facilitators-online) adds explicit online
assignment Save/Cancel using verified target account/Khula membership/current capture
authority from existing shared-owner contracts. No account/grant/People generator or
email-only target binding. Unassignment stops new assigned captures but preserves own
historical access under current rights. User-approved membership-instance renewal prevents
retirement/rejoin silently resurrecting old assignment eligibility; same-membership
grant recovery alone does not require renewal. Trusted target-list/evidence and lifecycle
contracts plus concrete bounded write/outcome fixtures remain shared-owner Build gates.

## Storage/update reliability completion — approved scope

[Approved Story 5.3](epics.md#story-53-protect-saved-observations-through-storage-failures-and-app-updates) proves bounded
quota/transaction recovery, non-destructive supported local-schema upgrades, deferred
shell activation and old queue/version compatibility. Protected saved/unknown/conflict
work is never disposable cache. Existing platform owners provide proven neutral
transaction/migration/claim/queue/update fixtures; KDG owns schemas/definitions. No
autosave, universal history engine, forced reload/reset or browser-storage guarantee.
Concrete schema/build/payload upgrade pairs and automated/physical evidence gate delivery.

Update-first default approved: no preliminary sync requirement; protect pending edits/
conflicts and sync after update. Settle executing local writes/requests safely with
bounded handling and wait for unsaved-form Save/Cancel before reload. Unknown operation
identities remain recoverable; updates do not wait indefinitely for successful sync.
No mandatory adapter pattern: add migrations/version handlers only for concrete changed
formats. Behavioral compatibility and prior-release supported payload tests are binding.

[Approved Story 5.4](epics.md#story-54-verify-the-complete-workflow-and-prepare-a-controlled-khula-pilot) closes integrated
session/device/release evidence and named Khula retention/device/processing policies
before a real-data pilot. Seven-day access and 30-day own download windows are not
retention policies. Genuinely denied saved work needs owner-approved bounded retention/
disposal; no bypass upload, new export/intake or indefinite retention claim.

## KDG request and recovery contract — engineering closure

2026-10-14. These are app-owned build inputs within approved behavior, not generated
OpenAPI or evidence of implemented handlers. Shared capability/actor/membership fields
are selected in the shared addendum; physical owner schema/privilege inputs remain
gates. This section defines no duplicate shared endpoint/service.

### Wire values and validation

UUIDs serialize as lowercase hyphenated strings. Reject malformed or nil domain IDs.
Server revisions are decimal strings matching `[1-9][0-9]*`, bounded to positive signed
64-bit integers; never send large revisions as JavaScript numbers. Command/definition
versions are small positive integers, initially 1. Dates are validated `YYYY-MM-DD`
calendar dates; observation date is explicit and not inferred from server receipt time.
Device `captured_at` is an RFC3339 UTC string, preserved as untrusted device time.
Server attribution/times come solely from verified execution.

Reject unknown fields/duplicate JSON keys, non-finite numbers, invalid Unicode, U+0000 NUL anywhere in persisted text and
caller-controlled owner/org/actor/audit fields. Initial rating is integer 1–5 and
initially unanswered. Reject 0/6/fractions; boolean false is a valid required answer.
False details must be absent, not retained secretly on the server. Required text needs
non-whitespace content; optional unanswered text is omitted. Preserve entered Unicode/
whitespace in valid text; do not silently normalize answer content.

Definition bounds: 50 active questions; label/details-label/endpoint-label 500 Unicode
code points, each answer/details text 5000 code points, command body 131072 UTF-8 bytes.
Names for child display are nonblank, at most 200 code points; do not infer uniqueness
or identity from spelling. These are resource bounds, not clinical/content rules.

### Capture commands

| Action | Exact submitted fields | Immutable server facts |
| --- | --- | --- |
| Create (`capture.create`, v1) | operation_id, command_version, capture_id, child_id, questionnaire_version_id, observation_date, answers, captured_at, child_eligibility_ref | Fixed configured org, verified original account/actor, created/updated server time, original child/version; server revision initially 1 |
| Edit (`capture.edit`, v1) | operation_id, command_version, expected_revision, observation_date, answers; capture ID in path | Original owner/creation, child and questionnaire version unchanged; current editor/time recorded only on changed successful write |

The initial published questionnaire identity is determined by its version reference,
not a client-supplied name/position. Create requires current create.assigned + active
app assignment, or current create.all for the author's own capture. Own/edit and online
all/edit use their corresponding current read/edit capabilities, never a client role.
Do not materialize edit expected_revision until that action's own predecessor resolves;
then freeze it and the complete wire payload. Unrelated server changes require conflict
review, not substitution of the downloaded latest revision.

### Prior child eligibility

Use an opaque KDG-owned eligibility reference per provisioned child, returned by the
existing `/provision` path and retained with each saved create. Its authoritative
record binds org, account, membership instance, child, observed active-child state,
appropriate own-create/assignment context and server issuance time. It contains no
answers and grants no rights. No token-secret/parallel authorization service is needed:
resolve the opaque reference through the app's protected persistence.

On sync check current admission/membership/create permission and applicable current
assignment, then verify the reference belongs to this caller/child/context. A foreign/
missing reference cannot claim inactive-child compatibility. Ordinary inactivity may
accept the previously provisioned child; a fresh request for an inactive child does
not receive new eligibility setup. A phone date/flag proves neither eligibility nor
pre-deactivation Save. This deliberately supports stale offline setup, not a provable
time cutoff. Explicit privacy restriction is a separate current processing boundary.

The shared addendum binds membership instance to Identity's existing new membership
ID on rejoin, and selects current target evidence. Reference retention must support delayed saved work; no arbitrary
expiry/purge is introduced before Khula's retention decision. Define the owned reference
table in 1.4, bind local/create DTOs in 1.5/1.6, and prove 5.1 inactivity behavior with
that evidence. This is a refinement of the approved provisioning/create path, not a new
user step or a proof that these contracts have passed shared owner review.

### Compact successful receipt and unknown outcome

Persist unique `(org_id, executor_account_id, command_type, operation_id)` with business
effects, required immutable evidence, trusted attribution and compact result in one owner
transaction. The server derives capture.create/capture.edit from the handler, never an
arbitrary action field. No command fingerprint metadata or payload comparison is required.
A successful create/edit receipt contains operation_id,
command_type, command_version, status `committed` and result `{capture_id, revision}`.
Revision is the string recorded for that operation, even if the capture later changes.
No answer/child-name/definition dumps are exposed by receipt lookup.

An authorized no-op edit records its receipt with unchanged revision and no fake audit
event. A committed duplicate returns the original receipt including its original target
and revision even if incoming content differs. Privately resolve the stored target and
recheck current authority on that actual stored resource/command; supplied target/action
never authorizes replay. Before lookup, strictly parse structural shape, typed IDs/bounds
and supported incoming command versions; unsupported versions fail safely. On committed
replay return the original supported command/receipt version even when a different
supported incoming version was supplied. Only after finding no committed outcome apply
fresh-action domain/eligibility/expected-revision/lifecycle validation; later resource
changes do not invalidate an otherwise currently authorized original receipt.
New intended actions/changed input use a new operation ID. Concurrent duplicates serialize
and cannot both commit effects; failed/uncommitted actions have no successful receipt.
No automatic outcome expiry/deletion is introduced.

Unknown lookup returns status `unresolved` only when scoped verification/read succeeds
and no committed receipt is observed. It is not proof a competing transaction cannot
still commit. Bounded identical retry is allowed; deny/unavailable/authentication errors
are separate HTTP/error outcomes. Foreign operation identity never reveals existence.
Lookup requires the supported `command_type` query discriminator, since an operation UUID
may exist under different command types. Resolve only the authenticated org/caller/type/
ID key; never return an arbitrary first row. Reject unsupported types, recheck the
permission for the stored resource/command, and do not infer that permission from the
query discriminator. The first capture consumer supports capture.create/capture.edit;
other app command recovery registers explicit handlers with its consuming DTOs.
A fresh stale edit with no committed outcome returns 409 kdg_capture.capture_revision_conflict with safe current_revision metadata,
not an answer snapshot. No server conflict-input draft is stored; current record is
fetched through current authorized reads for in-memory portal review.

### Frozen submitted snapshot and first committed outcome

The client freezes the complete queued command and expected revision when eligible to
send. Snapshot confirmation relies on the client binding that frozen input uniquely to
its operation; the server receipt does not attest equality with the incoming body. For
edit acknowledgement, the receipt capture_id must match the queued capture target as
well as its operation/command binding. On mismatch preserve local input, block descendants
and require reconciliation; never mark other local content Synced. Late acknowledgements
do not confirm newer local input. Pending predecessors block later sends, and unknown outcomes
never automatically allocate a fresh operation. Strict typed shape/UUID/date/revision/
answer validation remains; no canonical command envelope, SHA/JCS command digest, HMAC,
fingerprint metadata, fingerprint secret files or associated key backup/restore is a
current KDG delivery gate. This is the selected [ADR-0061](../../../platform/docs/architecture/decisions/0061-kdg-first-committed-operation-wins.md) model,
not an algorithm fallback. Earlier HMAC selection is retained as superseded history in
the [security candidate](../../../platform/docs/architecture/contracts/operation-fingerprint-security-evolution.md#kdg-initial-fingerprint-disposition--2026-10-14).
Ordinary business-data backup/recovery and child privacy gates still apply.

### Pagination and updates

Page size defaults to 30, max 100. Cursors are opaque app-owned references scoped to
account/org/read mode/query; validate scope/filter integrity, and always recheck current
permission. Order capture history by immutable `(server_created_at,capture_id)`, not
editable observation date; the 30-observation-day window is an explicit query filter.
Pages are not snapshot-isolated across a long scan: updates/late sync may need refresh;
absence is never evidence of deletion/revocation. Only own responses are persisted.

Initial local schema/queue/definition versions are 1, declared independently. The first
release has no existing KDG store to migrate; include a synthetic v1→next-version fixture
when proving the shared migration/update helper. Do not invent an adapter per release.
A changed local schema or payload adds its exact supported handler/migration and tests
in that release; unchanged formats reuse current behavior. Activation settles active
Save/request work under the existing bounded request handling, preserves unknown action
IDs and waits for unsaved-form Save/Cancel; pending/attention queues do not block update.
Sync follows activation. Unsupported bytes/commands stay protected, never reset/drop.

### Enforcement evidence

Extend A05 bounds/rating/false-details, A09 first-commit-wins/changed-body replay/no-op/concurrent receipt,
A14 foreign operation/reference/cursor, A16 prior-eligibility/current-access, A18 page
refresh and A17 schema/update fixtures. Actual OpenAPI/Pydantic and generated TypeScript
become model authority during Build; this planning contract seeds rather than duplicates
their future implementation. No runnable test command is invented before scaffold delivery.

## Implemented definition candidate — 2026-10-23

The inert [Pydantic definition model](../api/questionnaire.py) now closes this small
Story1.2 prerequisite; its database, operator command and read API remain undelivered.
This is not a new HTTP wire contract or permission to bypass the story's shared gates.

Definition fields: schema_version=1 and ordered questions (1–50 unique canonical,
nonzero UUID IDs). Common question fields are id, type, label and strict required.
Rating configuration explicitly carries minimum=1, maximum=5, minimum_label=Goed and
maximum_label=Nie goed nie; no default or intermediate descriptions. Boolean carries
strict default=false, details_enabled and details_label (required when enabled, absent/
null when disabled). Text has only the common fields. Extra/answer/expression fields
are refused. Nonblank labels keep their exact content/order, max500 Unicode code points;
NUL and invalid Unicode are refused. These are definition checks, not answer validation.

parse_definition bounds raw UTF-8 JSON to the existing128KiB command ceiling and rejects
duplicate JSON keys, nonfinite constants, duplicate question IDs and coercion. Complete
future command/HTTP envelopes need their own total-byte enforcement. Public domain
failure is the fixed identifier kdg_capture.invalid_questionnaire_definition; raw input/
validation context is never returned by that boundary. Field-path presentation belongs
to the consuming API. initial_definition requires four supplied IDs and creates only
inert exact initial content, no version/organization/actor identity or stored publication.

## Implemented private outcome storage candidate — 2026-10-23

The [KDG-owned adapter](../write-candidate/operation_outcomes.py) validates closed v1
capture.create/edit receipts and stored rows, performs exact org/executor-account/
handler-command/operation lookup and plain server-attributed INSERT in a caller-owned
write transaction. Read [synthetic evidence](OUTCOME_STORAGE_CANDIDATE_EVIDENCE.md).
No mounted API, migration or persisted capture/history/outcome implementation follows.
Current stored-resource authority, atomic linked writes and native/release qualification
remain consuming gates. GET recovery and POST retry retain their different authority
requirements above. Private None is not public unresolved or rollback proof.

## Implemented capture input boundary — 2026-10-23

The [app-owned models/parsers](../api/capture_commands.py) implement the exact create/edit
v1 shapes above, strict envelope/scalar/bounds checks and fresh-action answer validation
against an explicitly supplied original QuestionnaireDefinition. Read [evidence](CAPTURE_COMMAND_VALIDATION_EVIDENCE.md).
parse_create/parse_edit precede outcome lookup; validate_answers belongs only after
confirmed outcome absence. No current authority, pinned-version persistence/lookup,
replay, HTTP route or atomic write is implemented by these pure functions. Eligibility
reference stays opaque nonblank text; it proves no authority. Supplied blank text is
invalid; optional unanswered text is omitted. Safe failures expose validation_failed or
unsupported_command_version only. Public OpenAPI/client exports remain unchanged until
an actual consuming HTTP slice mounts these contracts.

## Linked storage schema candidate — 2026-10-23

The unapplied [owner revision](../migrations/candidates/0002_capture_storage.py) declares
supporting questionnaire/version/child/assignment/eligibility and linked capture/outcome/
revision storage together. Read [offline evidence](LINKED_STORAGE_SCHEMA_EVIDENCE.md).
It remains outside active Alembic versions. Composite same-org/owner/executor/operation
links, deferred snapshot completeness, server capture attribution and FORCE RLS are
DDL candidates, not actual PostgreSQL or authorized writer qualification. Generated
outcome target/revision columns preserve the existing private adapter interface. Issued
opaque eligibility references are nonblank text <=200 codepoints; retained observations
do not confer current authority. Parent mutation commands/grants remain gated. Native
constraint/RLS/atomicity/current authority and release recovery precede promotion.

## Rollback-only native storage evidence — 2026-10-24

The [native suite](../migrations/tests/qualify_capture_storage.py) now executes actual
candidate DDL, constraints/triggers/RLS and concrete capture/outcome/history SQL inside
rollback-only transactions. See [evidence](NATIVE_STORAGE_ROLLBACK_EVIDENCE.md). Candidate
tables use the runtime current role within a fixture-admin session; actual restricted
logins are separately inspected. No durable commit, concurrent replay, current Access
or protected writer API is implied, and no active migration is installed. The unresolved
historical global hash difference remains recorded; fresh fixture/current preservation
checks establish this run's rollback only. Promotion/release gates remain binding.


### Unmounted own-read recovery consumer — 2026-10-25

`write-candidate/operation_recovery.py` implements the callable behind the planned
GET operation lookup, without mounting an HTTP route. `RecoveryHandler.execute`
takes an exclusive fresh connection, canonical operation UUID, required closed
`capture.create` / `capture.edit` discriminator and bearer authorization. Organization
is configured; account and durable actor come from current protected Access read.own
evidence, including current membership and own-account resource scope. Caller-selected
account, organization or target parameters are not accepted.

It reads the private exact scoped outcome and separately verifies the actual stored
capture's org/owner before disclosing the original v1 compact receipt. It does not
require current create authority, assignment or child eligibility and takes no business
or operation locks. Successful absence returns exactly
`{operation_id,command_type,status: "unresolved"}`; this permits a concurrent later
commit. Stored-target or storage verification failure yields safe
`503 operation_verification_unavailable`, never unresolved. Existing authentication,
Access denial/setup and bounded execution errors remain machine-readable.

The total ten-second budget covers current Access (at most three seconds), worker
admission, fresh observation entry, SQL and completion. Cancellation retains connection
ownership until the worker finishes. Future HTTP adaptation must preserve validated
single-valued query/header inputs, bounded acquisition and no-store/error conventions;
no route, release activation or new edit writer follows from this callable.
[Implementation and qualification evidence](OPERATION_RECOVERY_EVIDENCE.md) records
the exact native/synthetic coverage and remaining gates.


### Candidate-only recovery HTTP embedding — 2026-10-25

`write-candidate/recovery_http.py:create_candidate` constructs the candidate GET
`/api/v1/operations/{operation_id}` with exactly one required `command_type` item,
canonical operation UUID, a single valid bearer token and empty bounded body. Unknown
or duplicate query selectors return422; invalid/multiple bearer headers return401 with
challenge. Committed/unresolved DTOs retain the preceding callable contract; known
safe errors are allowlisted and all responses are private/no-store, including routing
and unexpected failures. No module app or active startup import is added.

One original Budget covers body receipt, current Access, bounded pool/driver checkout,
SQL and release. Acquisition follows Access; slow acquisition cannot refresh evidence.
The existing retained worker owns checkout through release on cancellation/expiry.
Ordinary fixed pool/driver timeouts bound phases; response completion may await unwind,
never abandon ownership or report late success. The lazy engine uses a single numeric
PostgreSQL host, an explicit port (default5432), no URL query overrides, pool timeout0.25s,
connect timeout3s, no overflow/pre-ping/recycle and read-only defaults. Standard FastAPI
lifespan disposes the owned engine after the ASGI host drains requests.

[HTTP qualification evidence](RECOVERY_HTTP_EVIDENCE.md) records synthetic coverage and
remaining native, schema/client, startup and release gates. Active context API and
approved dependency manifests remain unchanged; constructing a candidate is no release
authorization or provisioning action.


### Candidate recovery OpenAPI and client types — 2026-10-25

The candidate's custom OpenAPI metadata now describes its manually validated inputs
and actual serialized output. [Candidate OpenAPI](../write-candidate/recovery-openapi.json)
is exported deterministically with no engine/authority construction or network/SQL.
It declares required command_type, canonical nonnil UUID, Bearer authentication,
required committed/unresolved status, v1 receipt and decimal-string signed-bigint
revision bounds. Error schemas have closed shapes and status-specific identifier enums;
private/no-store and401 Bearer challenge are documented and wire-validated.

Existing platform generation produces separate types in contracts/recovery-generated;
active context schema/client and startup remain unchanged. These types are compile-time
contracts, not a runtime SDK, token supplier, UUID validator or browser integration.
The existing manual boundary still rejects unknown/duplicate selectors; OpenAPI
parameter declarations alone cannot express all query multiplicity constraints.
[Evidence](RECOVERY_CONTRACT_EVIDENCE.md) records actual schema-to-wire, TypeScript and
fresh-import export checks. Historical native evidence remains bound to its original
source versions; this metadata delivery makes no new native or release claim.


### Candidate recovery request adapter — 2026-10-25

`web/src/recovery.ts:recoverOperation(session,pending,options)` consumes generated types
and validates unknown wire data. Pending scope pins account/org/original operation and
command; edit also requires its queued capture target. One fixed relative GET sends
only bearer and required discriminator. Required caller `{signal,isCurrent}` represents
its existing generation plus account/org observation; cancellation or stale execution
cannot return a receipt or denial for publication. This is a local fence; server checks
current own-read authority. Actual Auth/entry wiring remains a consuming gate.

A total at-most10-second deadline covers headers/body even if transport ignores abort.
Per-read monotonic checks prevent empty-chunk timer starvation;16KiB cumulative UTF-8
bytes, exact decoded shape/identity/version/revision/error status families and duplicate
keys are checked. Responses must be JSON/private/no-store. Safe frozen results preserve
original compact receipt or verified unresolved, with no raw upstream messages. Edit
mismatch refuses acknowledgement; create keeps first committed target under ADR-0061.

No retry, refresh, new operation ID, write, queue/storage mutation or Synced feedback is
performed. Unresolved remains compatible with a later commit. The candidate is not
imported by active startup; [evidence](RECOVERY_ADAPTER_EVIDENCE.md) records synthetic
transport/type verification and the required future Auth integration boundary.


### Candidate recovery consuming Auth entry — 2026-10-25

`web/src/recovery-entry.ts:createRecoveryEntry` owns recovery within the existing
fixed-organization Auth entry. `recover(pending)` requires current admission and matching
pending/session/context account and organization, then passes the pinned bearer and
existing lifecycle execution signal/predicate to recoverOperation. Unadmitted or
superseded execution returns `superseded`; mismatched/malformed input returns
`invalid_request` without transport. Current results preserve the recovery wire contract.
Refresh, account replacement, retry/sign-in, logout, password recovery and disposal abort
in-flight reads; late receipts/errors cannot escape. Every result releases its own lease.
No automatic Auth recovery, write, queue mutation, new operation or Synced feedback occurs.
The trusted generic lease is never published and is hidden by this consuming wrapper.
Organization replacement disposes the old entry owner. Server access is checked per call;
a returned observation grants no later write authority. Candidate remains unconnected to
browser/editor and active API startup. See [qualification](RECOVERY_ENTRY_EVIDENCE.md).


### Native stored-edit recovery fixture — 2026-10-25

The [retained-only qualifier](../migrations/tests/qualify_edit_recovery_http.py) creates
one fresh synthetic capture through the actual runtime create handler, then commits two
explicitly test-only edits under the restricted runtime login. Independent read-only
storage checks and unchanged candidate HTTP recover the original edit at revision2
before and after revision3 exists; original create remains revision1. Exact scope,
current own-read denial before checkout and lease release are verified natively.

[Evidence](NATIVE_EDIT_RECOVERY_EVIDENCE.md) records journal-before-write identities,
complete prior-row preservation, exact parent/capture/outcome/history deltas and source
receipts. This qualifies stored-edit recovery only. It supplies no edit API/domain
authorization, real Access, browser/queue/editor integration or release activation.
Historical native reports retain their original source claims and limitations.


### Inert fresh own-edit transaction body — 2026-10-25

`write-candidate/capture_edit.py:edit_in_transaction` now consumes a trusted current
own_write context/original Budget, path capture UUID, EditCommand and exact own-edit
permission. The caller owns current admission/membership, durable actor and required
read/edit authority before entering the transaction. No new Auth/HTTP boundary exists.

The scoped operation lock/private lookup precedes SELECT FOR UPDATE on the exact own
capture. Existing outcome stops privately for later stored-target-authorized replay.
Fresh answers use the stored original definition. Unassignment/ordinary child inactivity
do not remove historical own-edit rights. Stale expected revision raises a safe local
RevisionConflict with only current_revision metadata, including when values are unchanged.
Changed writes conditionally increment once and append linked outcome/history; no-op
appends only its receipt. The original owner/child/version/device/creation facts remain
immutable. This body returns only a provisional receipt; acknowledgement requires the
outer durable commit. Native behavior and eventual HTTP409/error mapping are unqualified.
See [own-edit evidence](OWN_EDIT_BODY_EVIDENCE.md); no active API/client wiring changes.


### Native own-edit body qualification — 2026-10-25

The actual inert fresh-only `edit_in_transaction` body is now qualified against retained
PostgreSQL using actual restricted runtime writers and independent restricted read-only
sessions after writer disposal. Answers-only/date-only writes preserve original facts;
no-op adds only a revision3 receipt and preserves exact capture/timestamps/history.
Stale unchanged input conflicts; invalid original-version answers and foreign scopes
leave no writes. A native23514 after update/outcome and before history fully rolls back;
explicit original-command retry commits revision4. A committed duplicate stops privately
without replay/disclosure. The existing body/schema are unchanged.

[Native evidence](NATIVE_OWN_EDIT_EVIDENCE.md) records exact five-outcome/four-revision
proof, original-row/sentinel/ledger preservation, safe failure receipts and source bindings. The reviewed fault verifies the original
uncommitted outcome inside the same transaction/original Budget before injection;
already observed execution results survive a later independent-read failure. Two
successful datasets remain retained; current claims bind to the reviewed-source report.
Context/Access and differentiated editor actors are synthetic: real Identity binding,
current HTTP admission/Auth/replay, conflict wire mapping, native contention/cancellation,
active startup/browser/editor/queue/UI and ADR-0020 release gates remain unqualified.


### Candidate current-access own-edit API and replay — 2026-10-25

`write-candidate/edit_http.py:create_candidate` explicitly constructs an unmounted
PUT /api/v1/captures/{capture_id}. Both current own-read and own-edit checks precede
acquisition, with matching account/actor/membership and fixed org/own-account scope.
One original10-second Budget covers streaming through commit/release acknowledgement;
both Access checks share3 seconds, using the older observation for existing freshness.
A duplicate returns its original receipt only after current stored-target ownership
verification; incoming path/content/revision never authorize that target. Fresh actions
use the unchanged qualified body. No create/assignment/active-child prerequisite is added.

Fresh conflicts return409 `kdg_capture.capture_revision_conflict` with top-level string
`current_revision` in the compatible safe error envelope; no snapshot. Fresh missing or
foreign captures return404 `capture_unavailable`. Strict bounded JSON, single Bearer and application/json Content-Type,
closed query, private no-store and safe errors apply. Worker cancellation retains
connection ownership until unwind; no late/provisional success acknowledgement.
[Evidence](OWN_EDIT_HTTP_EVIDENCE.md) and candidate edit-openapi/generated types record
synthetic behavior and exact limits. Active API/browser/editor/queue wiring, native
qualification of this new boundary, real Identity/Access and release gates remain open.


### Native candidate own-edit HTTP qualification — 2026-10-25

The actual candidate PUT orchestration and stored-target replay now pass retained
PostgreSQL qualification with mocked current Access and actual restricted runtime
sessions. Actual create establishes1; answers/date PUTs commit2/3; receipt-only no-op
preserves complete capture/timestamps/history. A changed valid incoming path, stale
revision and domain-invalid answers replay the original edit receipt at2 while storage
remains3. Fresh stale/invalid, foreign scopes, either denied capability and malformed
HTTP return safe expected outcomes without writes. Reviewed checks include committed-replay
denial for each capability, exact Access-check sequences and original-account replay on
the same pool immediately after foreign-account refusal. Native23514 after UPDATE/outcome
and before history fully rolls back; original-command retry commits4 once, duplicate
returns the original receipt. Released leases precede every independent restricted
read; all observed physical application connections are disposed at lifespan end.

[Native evidence](NATIVE_EDIT_HTTP_EVIDENCE.md) and its [source-bound record](evidence/native-edit-http-20261025.json)
retain journaled inputs, executed dependencies, observed responses before oracles,
exact deltas and complete prior-row/sentinel/ledger preservation. The reviewed33-source report records20 create/PUT checks and totals16/36/32 with
eight of each parent. The first32-source proof at15/31/28 remains historical evidence. Body/schema/API, scaffold/shared UI/context/ADR
remain unchanged. ASGI/mocked Access prove no real network or Identity/Access authority;
native contention/cancellation/TCP drain, active API/browser/editor/queue/UI and ADR-0020
release gates remain open. No migration, provisioning, privilege expansion or cleanup.


### Candidate unconnected own-edit request adapter — 2026-10-26

`web/src/edit.ts:editCapture(session,pending,options)` consumes generated edit types.
Pending input pins account/org/capture and its original EditCommand. Before any await,
it snapshots bearer, identity primitives and the complete serialized nested command.
One selector-free same-origin PUT uses JSON, no-store and redirect refusal with a131072
UTF-8 byte request ceiling. Backend retains original-definition/domain validation.

Only an exact closed v1 capture.edit committed receipt matching original operation and
capture acknowledges success. Canonical signed-bigint revision strings stay exact.
Generated safe status/error pairs expose required current_revision only for409 revision
conflict, without upstream text/snapshot. Caller-owned cancellation/generation fencing
and one at-most10-second deadline cover preflight, headers/body and publication, with
16384-byte strict JSON/Unicode/duplicate-key response validation and best-effort disposal.
Stale/throwing fences suppress late receipts/errors. Cancellation after dispatch may
still commit; failure never implies unresolved, rollback or safe new identity.

No retry/recovery/refresh, saved-input/store mutation or Synced feedback occurs.
Candidate remains unconnected to browser/editor/queue/Auth and active startup.
[Evidence](EDIT_ADAPTER_EVIDENCE.md) records54 edit and41 recovery cases passing after
review corrections; root final verification passes124 affected tests, both strict
TypeScript7.0.2 configurations and all three scaffold parity checks. Three review layers
completed, nine findings addressed, none deferred. Companion app-owned recovery now shares the demonstrated small predicate-before-
final-signal correction, with dispatch/publication characterization tests. Initial rejected
edit leases skip payload getters/toJSON. Direct undefined answer entries refuse without
dropping input; legitimate omitted optional fields remain valid. Synchronous JSON preflight
cannot be preempted or heap-bounded: the byte check follows serialization and an elapsed
deadline prevents transport. Actual Auth integration, real Access, browser/native and
release activation remain separate gates.


## Candidate own-edit entry — 2026-10-26

`createEditEntry` binds the original generated edit command to the existing current
Auth execution lease. The wrapper hides raw acquisition, pins fixed organization and
configuration, checks pending account/org against admission and delegates synchronous
nested snapshot/PUT/response semantics to editCapture. The adapter budget starts after
the wrapper pending spread; synchronous wrapper capture and serialization cannot be
preempted. Its maximum 10-second deadline is not an end-to-end wall-clock bound. Every acquired execution releases
in finally; stale completions return superseded, including ready results. Operation
results never change admission, publications or caller input. Offline uses disposed prior
owner plus an online:false replacement; organization changes replace the owner.
[Evidence](EDIT_ENTRY_EVIDENCE.md) retains historical pre-review results of 31 consumer
and 230 full synthetic Auth tests, 124 direct regressions, strict TS7 and four parity checks.
Post-review focused proof executes all 38 edit-entry cases with combined edit-only and
acceptance-only flags. Root final verification passes237 compiled Auth cases,124 direct
regressions, strict TypeScript7.0.2 and four scaffold parity checks; seven review findings
addressed, none deferred. This separately imported
candidate is unconnected to browser/editor/startup and creates no new session lifecycle,
retry/recovery, queue mutation or Synced feedback. Results observe completion only;
cancellation/deadline does not prove rollback or absence. Real Auth/Access, backend/native,
browser and release activation remain unqualified.


## Candidate create/edit/recovery HTTP path — 2026-10-26

`write-candidate/create_http.py:create_candidate` adds explicit POST with one original
body/Access/checkout/transaction/release budget and current create-all or assigned
authority before acquisition. Existing transaction/replay handlers own original receipts
and stored-child checks; worker ownership remains through cancellation and unwind.
Offline create OpenAPI/owner-generated types describe the safe wire. `createCapture`
and `createCreateEntry` add the pinned client/current-Auth consumer alongside edit/recovery.
Synchronous capture/serialization is not preemptible; cancellation may still commit.
No automatic retry, new identity, refresh or saved-state effect follows from a result.

[Evidence](PERSISTENCE_HTTP_PATH_EVIDENCE.md) records21 HTTP/4 contract/90 client cases,
199 synthetic backend regressions,327 compiled Auth/client and124 direct regressions,
strict TS7.0.2, four scaffold checks and seven loopback requirement groups. Real handlers
execute against synthetic authority/storage: create1/edit2, original receipt recovery,
replay/no-op/conflict and fresh release-failure recovery. This proves wire/control-flow
agreement, not native permissions/rollback or TCP drain. No browser/editor/queue/default
startup activation. Historical native evidence and ADR-0020 release gates remain binding.

Review: ten addressed, one rejected with evidence, none deferred. Three proof-process
controls and two strict synthetic fixture cases pass. Sibling edit schema Unicode
constraints and shared schema test-tool calendar checking are synchronized.


## Candidate current own-capture detail — 2026-10-26

`GET /api/v1/captures/{capture_id}` is an explicitly constructed candidate own-read
boundary, without query selectors or a nonempty body. One bearer and current
`kdg_capture.capture.read.own` authorization bind verified account/durable actor to the
fixed organization before checkout. Its read-only transaction uses explicit capture,
organization and original owner account predicates and returns the current saved
capture, the permitted current child label and the original questionnaire definition.
Unassignment/inactivation does not create a new read prerequisite. Missing and foreign
captures return the same safe 404 `capture_unavailable`.

`CaptureDetail` carries capture/org/original owner account/actor and child IDs,
`child_label`, original questionnaire/version IDs and positive decimal
`questionnaire_version`, original `definition`, current positive decimal `revision`,
`observation_date`, `answers`, original untrusted device `captured_at`, and stored
`created_by`/`created_at`/`updated_by`/`updated_at` attribution. No actor display-name
lookup is implied. Creation membership/eligibility references, operation outcomes and
revision archive are excluded. Date-only observations remain date-only; server times
remain distinct from original device time.

The bounded response limit is 512 KiB. Invalid required stored evidence fails safely
as 503 `capture_read_unavailable`; current authentication/admission/setup, observation
expiry, deadline and internal errors retain stable safe identifiers. Every response is
private/no-store. One original execution budget covers authority, acquisition, SQL and
release; cancellation retains worker ownership through unwind and never publishes late
success. No external wait occurs inside the read transaction.

The generated read contract supplies the isolated transport and Auth consumer. Each
read pins account/org/capture and respects caller cancellation/current-generation
fences; a stale response cannot populate a replacement account's state. A read result
never acknowledges an uncertain operation, marks content Synced, updates an offline
read observation, grants later write authority or automatically retries. Operation
recovery still returns the original receipt even when detail now has a later revision.
Listing, pagination, offline cache integration and activation remain separate consuming
work. See [readback evidence](OWN_CAPTURE_READBACK_EVIDENCE.md).


## Candidate own-history pagination — 2026-10-26

`GET /api/v1/captures` is an explicitly constructed own-history candidate. Every page
requires current fixed-org `kdg_capture.capture.read.own` and verified account/actor
before checkout. Inclusive `from_date` and `to_date` are explicit date-only filters;
`limit` defaults to 30 and is bounded to 1–100. The caller fixes the dates for a download;
the eventual phone host calculates today plus previous 29 days. Unknown/duplicate
query keys, account/org selectors, malformed bounds/limit/cursor and nonempty bodies
are refused safely. Child assignment, active status and create/edit grants do not
filter already-owned readable history.

Ordering and continuation use descending immutable `(created_at,capture_id)`; current
observation dates filter independently. Full records carry current answers/revision,
permitted child label, original questionnaire definition/version and stored provenance
under the existing detail contract. A page echoes its verified account/org and query
binding, includes items and a nullable next_cursor. Empty is a verified current query
result, never an inference about deletion. Pages are separate reads; concurrent edits
or late synchronization may require refresh.

Cursor bytes are closed, versioned canonical base64url JSON, bounded and strictly
decoded. Compare account/org/own-read mode/date/limit binding with the current verified
request and reject mismatches. The tuple is untrusted navigation; SQL always applies
current org/owner/date predicates independently. This is intentionally unsigned and
not tamper-evident: a caller choosing another valid position can only navigate their
currently authorized query. No opaque value substitutes for authority, and there is
no server cursor registry, expiry/worker-affinity mechanism, new service or signing
key. This clarifies the earlier scope/filter-binding seed; it does not introduce HMAC.

The server selects at most limit+1 rows and returns at most 100 full records, each
subject to the existing 512 KiB detail bound. A separate 2 MiB actual UTF8 page bound may
reduce the count; continuation follows the last included tuple, preserving the first
omitted row for the next page. No partial item or invalid required stored evidence
becomes success. Every response is private/no-store; existing current authorization,
safe errors, one bounded read-only execution/worker ownership and final response
serialization safeguards apply. No network-completion deadline is promised.

The isolated one-page client/Auth consumer pins account/org/query and rejects an
invalid whole page, stale Auth result, duplicate/out-of-order record or inconsistent
continuation. It neither walks pages automatically nor changes cache, queue, saved
status, uncertain-operation receipts or offline observations. Offline merging,
read-observation renewal, history UI and activation remain later consuming work.
See [history-page evidence](OWN_HISTORY_PAGES_EVIDENCE.md).


## Candidate offline own-history consumption — 2026-10-26

This increment extends the candidate history response with required `observation`.
It supersedes the preceding candidate's no-observation-renewal limitation only for
this exact successful own-history read. `/context`, own-detail reads, write receipts
and unrelated successes still mint no new offline capability. The closed observation
contains verified account_id, actor_id, membership_id, authorization_scope organization,
resource_scope own_account, literal `kdg_capture.capture.read.own`, decision_id,
checked_at and expires_at exactly seven days later, derived from the same Access check.
A cursor or local clock never provides authority. Current per-page checks and request
budgets are unchanged; fingerprints/HMAC remain deferred.

The isolated KDG IndexedDB version1 candidate atomically imports validated full pages,
original immutable definitions, server baselines, progress and that exact observation.
Records/definitions/progress are account/org partitioned. Higher revisions replace
older server baselines; contradictory immutable facts or equal-revision content refuse
an entire import. Pending local fields, base snapshots, conflict evidence and original
operation IDs remain untouched, including pending-only rows first gaining a baseline.
Imported existence is not an uncertain-operation receipt. Missing rows never delete
records; restart/refresh does not promise a database snapshot.

`downloadOwnHistory` explicitly follows cursors under fixed bounds and fresh current
scope. Network waits stay outside the local transaction. `openHistoryStore` owns its
handle; ordinary close preserves valid offline reopening, while deny/logout persist
an account/org lock and invalidate late generations. Restoration is explicit and uses
fresh same-account own-read evidence; old or foreign callbacks cannot restore it.
Local read checks stored expiry, a persisted wall watermark and process-local monotonic
elapsed time. A clock anomaly requires fresh online restoration, including after a
new JavaScript realm opens. These are managed-device policy checks, not tamperproof
server authorization. Failed lock writes return unavailable and retain the current
process lock; no persistence claim follows refused storage writes.

Local reads use bounded prefix keyset/count reads, default30/max100, with `next_key`
and separate `progress_next_key` continuation. This does not introduce automatic
retention or prune locally authored records, pending work or referenced definitions.
A completed local transaction confirms that page only; interrupted downloads retain
prior committed data and partial progress, with outage distinct from known denial.

Generic IndexedDB request/transaction completion helpers and generated tests now come
from the builder template under `web/offline-tools`, checked through
`platform/builder-cli/scripts/sync-kdg-offline.mjs`. KDG owns cache schema, observations,
merge and retention policy; there is no generic offline history runtime engine.
No UI/service-worker/default-startup activation or physical-device durability claim
is included. See [offline history evidence](OFFLINE_HISTORY_EVIDENCE.md).


## Candidate protected own-edit context — 2026-10-26

`GET /api/v1/captures/{capture_id}/edit-context` now has an isolated candidate
implementation, generated contract and strict transport/Auth consumer. It checks current
own-read and own-edit independently before checkout, requiring the same verified
organization, account, durable actor and membership. Missing and foreign captures
share safe404. Historical own editing needs neither create permission nor current
child assignment/active status.

The closed response contains current original-owner `capture` with its original
questionnaire, exact `editable_fields` (`observation_date`, `answers`),
`read_observation` and `edit_observation`. Each observation retains its own actual
Access decision ID and checked_at; expires_at is exactly seven days later. It grants
no create/all-record authority. This supersedes earlier no-edit-context limitations
only for this explicit current read/edit check. Ordinary reads/history/receipts cannot
mint own-edit evidence. No local observation is persisted by this consumer.

The existing short read-only transaction and exclusive worker ownership use one
original ten-second budget through final serialization/release. Detail has an
independent512KiB UTF8 limit; the entire context has a544KiB limit. Current safe typed
errors and private/no-store behavior apply. Client whole-envelope validation and
Auth leases prevent malformed, foreign, late or replaced-session publication.
No command, receipt, saved overlay or queue mutation occurs.

Observation metadata is generated from owning schemas, with strict identifiers,
positive membership IDs and canonical UTC-Z timestamps. Context and history share
only their local exact observation metadata/validator. Existing PUT authorization
retains its behavior through a small shared pair-check implementation.

This remains unmounted synthetic code. Actual PostgreSQL permissions, joins,
read-only effects and native cancellation/drain qualification remain activation
prerequisites. No local Save/UI/worker activation is included. See
[own-edit context evidence](OWN_EDIT_CONTEXT_EVIDENCE.md) and its machine record.


## Candidate local explicit edit Save — 2026-10-26

For server-backed own captures, the isolated IndexedDB owner now consumes verified
edit-context through `importEditContext`, opens immutable reviewed tokens through
`openEdit`, and commits explicit completed changes through `saveEdit`. This extends
the earlier history-only store; the database name is unchanged and local schema v2
adds `edit_actions` while retaining v1 data and opaque pending/conflict fields.

The original questionnaire, owner/child/version and server provenance remain fixed.
Saved overlays and immutable action snapshots remain separate from the latest server
baseline. Typing and Cancel cause no edit/action write. Whole-form validation supports
rating1 and false, excludes hidden false-answer details from durable changes/identity,
rejects invalid wire characters and respects the existing131072-byte PUT limit with
maximum expected-revision overhead. Caller objects are copied before the first await.

Each explicit action uses its caller-supplied stable UUID, literal type `capture.edit`
and version1. It retains reviewed base, normalized changes, exact observations,
predecessor and local outcome. Identical retry recovers the same local result; changed
content under the same ID refuses. A first eligible action retains its reviewed
revision; successors have no guessed revision. These are local intents, not ready
wire payloads or server receipts. Future materialization/delivery remains separate.

Eligible Save commits intent and overlay together. A stale local head or unrelated
newer baseline retains a separate Needs attention proposal without replacing newer
saved changes. Existing unresolved pending/conflict work likewise prevents an ordinary
overlay replacement. `readEditActions` retrieves retained actions/proposals under
current valid own-read, default30/max100 with namespace-bound key continuation.
Nothing prunes, deletes or automatically resolves those proposals.

Known edit denial has an independent durable generation, preserving current own-read.
Read-only history restoration cannot revive old edit evidence. Explicit restoration
requires newer verified edit-context; old reviewed tokens remain invalidated. The
process keeps known denial when its durable write fails, without claiming persistence
across a destroyed JavaScript process. Denial/restoration across tabs and reopening
must preserve the same authority boundary. Expired observations return `expired`,
known denial returns `denied`, transient execution/storage/clock failures return
`unavailable`; no English-message branching is required.

Successful results are `saved_locally` or `needs_attention` after commit/publication
checks. Completion-boundary cancellation or expiry may suppress success after work
committed. Retain original action ID/input and inspect/retry that identity after valid
recovery; never infer rollback, generate a replacement ID or label it Synced. New
work needs a fresh handle-issued reviewed token. No sender, claim, receipt application,
pending-create editing, unfinished-input autosave, editor UI or startup activation is
implemented here. See [local edit Save evidence](LOCAL_EDIT_SAVE_EVIDENCE.md).


## Candidate ordered local edit reconciliation — 2026-10-26

The isolated v2 store now exposes `prepareEdit(action_id, execution)`,
`consumeEditReceipt(pending, outcome, execution)` and
`consumeEditConflict(pending, outcome, execution)`. This supersedes earlier
materialization/receipt-application omissions only for server-backed own-edit local
storage. No sender, claim, retry schedule or queue activation is implied.

Preparation atomically retains a version1 delivery envelope containing the exact
`PendingEdit`-compatible command and its serialized bytes, separate from immutable
saved intent/base/input. A first action uses its reviewed revision. A successor waits
for its exact predecessor's committed receipt; no-op results can retain the same
revision. Repeated or competing preparation preserves bytes and original operation ID.
An unresolved lookup/read cannot become a receipt. Already frozen commands stay
recoverable under that same identity despite newer readback; an unprepared action
facing known unrelated progress is blocked for attention without a fake server409.

Receipt consumption accepts the existing adapter's closed `{kind: committed, receipt}`
result, bound to the frozen organization/account/action/type/version/target and a
result revision equal to expected or expected+1. Conflict consumption accepts the
closed typed409 revision-conflict result. Retained delivery outcomes are validated
before later use; unsupported or contradictory metadata remains retained and cannot
advance descendants or confirmation. Identical repeated consumption is harmless.

Readback never acknowledges an operation by itself. With its matched receipt already
retained, actual authorized original-owner detail can retire only that same latest
saved overlay. At the receipt revision, date/answers must match; newer server detail
can display later content while confirming the older action completed. Attribution
and timestamps come only from validated detail. Late receipts/readbacks preserve
newer overlays, immutable reviewed bases and operation identities. Newly opened forms
work after acknowledged readback; existing descendants may follow only their own
verified predecessor progress, without rebasing onto unrelated changes.

Conflicts retain frozen attempted command, reviewed base/proposal and safe current
revision. Descendants remain blocked and readable; import cannot resolve the conflict
or delete pending work. Current own-read governs outcome consumption; preparation also
requires valid own-edit. Edit-only denial/expiry can therefore block preparation while
allowing read-authorized receipt retention. No operation renews a permission through
an unrelated success. Existing account/epoch/clock/session and transaction safeguards
apply, including original-ID recovery when failure follows transaction completion.

New results are `prepared` (stored bytes only), `blocked`, `invalid` and `reconciled`,
with existing `expired`, `denied` and `unavailable` failures. Callers consume only
validated transport/recovery results with the same scoped execution fence. No active
Auth-to-sender coordinator, pending-create consumer or complete Story2.2 claim is made.
See [ordered reconciliation evidence](EDIT_RECONCILIATION_EVIDENCE.md).

## Explicit saved-edit delivery and recovery — 2026-10-26

An unmounted consumer coordinates one selected saved edit under one Auth execution
lease. It recovers the original operation outcome before sending; only an unresolved
outcome plus current own-edit authority permits one PUT in that invocation. Retained
preparation, receipt recovery and readback require own-read independently of edit.
Original command bytes, action/operation identity and reviewed revision remain stable.

The original total deadline includes storage, HTTP and publication (default/maximum
30 seconds; each HTTP phase at most 10 seconds). Session replacement, abort or deadline
suppresses success and dependent work. Storage completes before network waits; no
business transaction is held across HTTP. Unavailable, malformed or authentication
failures do not acknowledge work or establish permission denial.

A matched committed outcome is consumed durably before current detail is imported.
Acknowledgement describes that operation only: it does not promise that newer local
changes are Synced. Readback failure preserves a known durable receipt and leaves
readback pending. Exact revision conflicts retain Needs attention without implicit
rebase. Detail import renews neither read nor edit observations.

Recovery/read access denial locks the partition. An ambiguous PUT denial first latches edit denial, then checks
current own-detail: success preserves own-read; read denial or an unverifiable probe
conservatively locks the partition within the execution fence. A deadline/session
change stops further writes while retaining an already-latched edit denial. Existing fresh restoration
contracts remain the way to restore authority. Original pending input is retained.

Simultaneous explicit calls may submit the identical operation; existing server
idempotency prevents duplicate effects. This consumer introduces no exclusive sender
claim, scheduling, automatic retry or startup integration. Durable claims and active
queue delivery remain separate prerequisites; this is not a production release gate.

## Candidate protected setup contract — 2026-10-26

The unmounted selector-free `GET /api/v1/provision` composes exact current own-read,
own-edit, create-all and create-assigned checks before checkout. Positive evidence
must agree on verified organization/account/durable actor/membership and retains each
actual decision plus exact seven-day expiry. Own-read is required; known edit/create
denial produces null positive slots, while verification unavailability fails the whole
request. Read/create success never mints edit authority.

Closed `Provision` contains schema_version1, org_id/account_id/actor_id/membership_id,
read_observation, nullable edit_observation/create_all_observation/
create_assigned_observation, create_state, children and nullable questionnaire.
Questionnaire contains questionnaire_id/questionnaire_version_id/questionnaire_version
and original definition. Latest published display version belongs to an explicitly
configured questionnaire; no browser questionnaire selector or arbitrary cross-catalog
latest choice is introduced.

Each child contains child_id/child_label/child_revision, child_eligibility_ref,
create_permission, nullable assignment (assignment_id/assignment_revision) and independent
checked_at/expires_at. All-create requires no assignment. Assigned creation requires a
current same-account/membership assignment. Child locks and current rechecks precede
atomic issuance of immutable references with trusted actor attribution. New references
are43 URL-safe opaque characters, grant no rights, and introduce no expiry or purge of stored eligibility
records. Existing general create references remain opaque text≤200 code points.

Creation state precedence is not_permitted (no children/positive create observation),
no_published_questionnaire, no_eligible_children, then ready. Bounds:1000 complete
children,1MiB UTF8 response and existing128KiB definition. Overflow is safe unavailable,
not partial setup. Response publication follows commit/release/final validation under
one original ten-second budget; release failure can leave committed references.
No capture, outcome or history writes, pruning or authority renewal from unverified data.

Strict generated types, transport and explicit Auth consumer validate the entire
closed response, evidence relationships, original definition, safe typed errors and
request/session/deadline fences. No setup/local capture persistence, PWA readiness or
startup activation is implied. Current runtime grants deliberately lack eligibility
INSERT: controlled narrow authorization and actual PostgreSQL qualification, including
latest-version query ordering and rollback, remain pre-activation requirements.
See [setup evidence](PROVISION_CONTRACT_EVIDENCE.md).


## Atomic local completed-create persistence — 2026-10-26

The isolated schema3 store implements `beginSetupRefresh` → exact
`importProvision`, pinned `openCreate`, atomic `saveCreate`, bounded
`readCreateActions` and local content through `read`. The request ticket is minted
before HTTP, durable, scoped and one-use; older responses cannot publish over a newer
request/known denial. `createSetupEntry.refresh` explicitly composes Auth, request and
import within one total deadline and lease. HTTP denial publication compares the
same current ticket before locking. Stale denials return superseded. After a current
partition denial, reopen the store and construct a fresh entry for explicit verified
restoration; invalidated handles are never revived. The consumer is unmounted.

Completed local content uses `local_capture` and pending create status, separate from
actual server `baseline`. Capture/operation IDs are distinct and stable for one Save;
immutable generated create bytes survive reopening and exact retries. Existing exact
committed-result recovery requires current own-read, independently of expired original
creation evidence; new writes retain all creation checks. Initial Save
checks read/selected-create/child and original pinned expiry independently, without
requiring own-edit. Hidden false details are excluded before durable identity; whole
original answers and the131072-byte UTF8 command limit apply. Multiple same-day
records are allowed. No unfinished typing, guessed server revision/audit or Synced
claim is introduced. Pending-only creates cannot enter server-backed edit APIs.

Supported v1/v2 storage upgrades retain populated/opaque rows; stale connections
refuse safely and unknown newer storage is retained. Schema3 browser update and
connection coordination remains a release prerequisite, alongside existing native
setup issuance qualification. See [local create Save evidence](LOCAL_CREATE_SAVE_EVIDENCE.md)
and its [source-bound record](evidence/local-create-save-20261026.json).


## Explicit saved-create delivery/recovery — 2026-10-26

`createCreateDeliveryEntry.deliver({account_id,org_id,action_id})` explicitly consumes
a saved create through original GET recovery, at most one unchanged POST, durable
receipt and current readback. The original total30second maximum/default covers one
Auth lease, storage, HTTP and final publication; each HTTP phase gets at most10seconds
and remaining time. No sender/claim/scheduling or startup is activated.

Version1 delivery metadata is separate from immutable pending/serialized/content.
Matching receipt recovery remains own-read-only after creation expiry/denial. POST
checks current authority; known local create denial requires explicit newer positive
verification of either capability. Original cache expiry/absence from today's child
list does not invalidate prior eligible saved work; preserve original reference.

Only receipt-bound actual detail marks that create Synced, without inventing audit.
Equal-revision content matches original date/answers; newer current detail may differ
while retaining create receipt revision1. Preserve original local_capture and newer
edit work. Known rejection retains selected Needs attention; unavailable outcomes
retain original retryable IDs/bytes. Creation-only denial and read denial remain
independent. See [owner evidence](CREATE_DELIVERY_EVIDENCE.md) and its machine record.


## Pending-create own-edit persistence — 2026-10-26

The unmounted store extends `openEdit`/`saveEdit` to completed locally saved creates
without inventing server facts. Version2 `local_create` reviews/actions carry an
explicit typed create/edit predecessor and a local base without server revision or
creation/update audit fields. Existing version1 server-backed edits remain supported;
unknown versions are retained and blocked. Each completed Save atomically retains its
separate immutable proposal and latest overlay; original create pending, serialized,
content, eligibility reference and local_capture remain unchanged. Whole-form original
validation and hidden false-detail exclusion apply. No typing/autosave is introduced.

Current exact setup own-read/own-edit observations authorize pending local editing;
create permission, current child eligibility/assignment/activity and latest questionnaire
are independent. Negative edit evidence invalidates old reviewed handles. Explicit
newer positive setup restoration can authorize a future review and does not restore
old generations. Process and durable denial must survive storage failures/reopen.

`prepareEdit` resolves the first predecessor from its matching validated durable create
receipt, including when server readback is unavailable. Later edits use their matching
edit receipts. Neither history existence nor current baseline supplies a replacement
expected revision. Unrelated server progress and stale local proposals are retained
for attention; late create/readback or earlier edit acknowledgement preserves newer
saved overlays. Existing explicit create/edit delivery and server checks are reused.
No new HTTP contract, local schema reset, sender or runtime activation is introduced.

See [pending-create edit evidence](PENDING_CREATE_EDIT_EVIDENCE.md) and its
[machine record](evidence/pending-create-edit-20261026.json) for exact qualification,
review, requirement-to-test mapping and limits. Ordinary release compatibility,
controlled migrations before activation and explicit recovery remain binding.


## Explicit confirmed-server own conflict decisions — 2026-10-26

The unmounted `createConflictResolutionEntry` offers `review(pin, mode)`,
`useCurrent(reviewed, decision_id)` and `saveReplacement(reviewed, decision_id,
action_id, changes)`. Pin account/org/capture/source_action_id. Current review fetches
actual authorized detail; replacement review fetches current exact own-edit context.
Decision invocation owns a new bounded Auth lease and rechecks actual current state.
No transaction or execution lease spans human review. Total30seconds default/max;
each HTTP phase gets at most10seconds/remaining, including final publication/release.

The store provides `openConflict`, `lookupResolution`, `useCurrent`,
`saveConflictReplacement` and bounded `readResolutions`. This subset requires a known server-backed v1 edit409, the active
head within its branch and fully interpreted capture actions. Any unknown prepared
outcome blocks competing decisions; unresolved lookup cannot prove no in-flight commit.
Known off-head proposals remain retained. Original content/status/command bytes,
predecessors, receipts and create intent are immutable. Derived descendant dispositions
are separate local metadata; descendants are paused, never silently replayed/included.

Use-current requires own-read only and creates no server write/revision. Replacement
validates the complete original-version result, creates a new operation pinned to the
reviewed server revision and uses ordinary edit delivery/recovery/readback. Fresh
current context cannot renew the original review's expiry. Neither detail nor entry
context fabricates a seven-day offline observation; retain valid existing own-read or
use the existing setup/history refresh. Decision/action/overlay/dispositions commit
atomically under current head/baseline/generation CAS. Exact decision retry is idempotent;
changed identity/content is rejected. Unknown/malformed decisions remain retained and
blocked. Late old outcomes cannot revive resolved branches or clear newer proposals.

The coordinator performs own-read `lookupResolution` before HTTP or authority required
for a new replacement. Immutable identity uses the original reviewed decision and
normalized complete input, excluding newly fetched detail/permission timestamps.
A committed decision remains recoverable after server/baseline progress, edit denial
and reopen; recovery verifies retained source, linked replacement, dispositions and
generation. Missing or contradictory effects refuse success. New decisions still
require fresh current-state checks, branding and CAS. An unavailable own-read probe
after edit403 does not prove read denial; only actual applicable read403 locks it.

Isolated local schema4 adds immutable `resolutions` and capture indexes without
resetting existing/opaque rows. Older connections close and schema3 code refuses4,
preventing bypass of new disposition fences. Activation requires coordinated browser
update/compatibility/recovery qualification; no default-startup upgrade or release
readiness is claimed. Conflict review and decision recovery refuse captures with
over100 retained actions or unsupported/incomplete state, without partial decisions
or deleting history. Same-phone unprepared and
pending-create conflict decisions are the next technical subset.

See [conflict-resolution evidence](CONFLICT_RESOLUTION_EVIDENCE.md) and its
[machine record](evidence/conflict-resolution-20261026.json). Existing API/DB release
safeguards remain binding; no new endpoint or conflict/override service is introduced.

## Same-phone unprepared conflict decisions — 2026-10-26

The unmounted schema4 store adds `openLocalConflict(pin, mode, execution?)`,
`useLocalCurrent(reviewed, decision_id, execution?)`,
`saveLocalConflictReplacement(reviewed, decision_id, action_id, changes, execution?)`
and `lookupLocalResolution(selection, execution?)`. These are pure local transactions,
with the same caller-owned execution/session lifetime as ordinary Save. They issue no
HTTP and add no server endpoint, Auth provider or generic merge service.

The source is an undisposed off-head Needs attention v1/v2 edit with no delivery
payload. Reviews identify actual saved current content, current head/create, nullable
baseline, generation and applicable authority. A synchronized baseline takes precedence
over retained original-create evidence when no newer overlay exists. Source retirement,
paused descendants, decision and new intent/overlay commit atomically under CAS.
Original proposals/create bytes and predecessor relationships remain immutable.

Use-current needs valid own-read and preserves existing chosen state/status. It never
claims server acknowledgement or sets Synced. Replacement needs independent valid
own-edit, original-version validation and a fresh ordinary v1/v2 action, based on the
actual current predecessor. Known create rejection is not a new editing prerequisite;
original creation validation still applies when delivery retries. Unresolved chosen
ancestors stay unchanged and replacement revision waits for their actual matching
receipts; uncertain independent prepared work refuses competing resolution.

Version2 local decisions coexist with version1 confirmed-server decisions. Own-read
exact recovery checks original normalized selection and retained effects before edit
checks, allowing reopen, edit loss, actual receipt progress, later server resolution
and reference-only child-label refresh. Missing/contradictory effects and changed retry
input refuse success. Lookup identity is captured before awaiting. New decisions still
require branded reviews, current scope/expiry and unchanged local snapshot/generations.
Abort/quota/completion ambiguity never implies rollback or success without evidence.

Existing conditional PUT/recovery/readback still owns server mutation. A later unrelated
server change produces ordinary409 and retains the replacement. Known own-read denial
blocks protected local history and recovery while retaining data. Review/recovery refuse
unsupported/incomplete or over100-action capture graphs without deleting history.
No complete Story2.3, browser update/device or release qualification is claimed. Confirmed
v2 server409, active unprepared heads stale from server progress and re-review of already
paused descendants are subsequent subsets. See [local evidence](LOCAL_CONFLICT_RESOLUTION_EVIDENCE.md).

Post-review qualification: original current-review own-read evidence remains privately
pinned for new decisions even after partition refresh; committed recovery needs current
own-read, without renewed original edit authority. Replacement refuses insertion above
the100-action graph bound before writes. Recovery validates chosen active ancestry or
actual receipt/subsequent validated decision evidence, and refused corrupt/disposed
ancestry remains retained. Focused883/HTTP71 checks and24 affected commands pass; all13
review findings addressed. No public API, schema or activation expansion.

## Remaining retained own-proposal decisions — 2026-10-26

Existing `openConflict`/`useCurrent`/`saveConflictReplacement`/`lookupResolution` and
unmounted Auth coordinator/entry signatures remain compatible. Validated classifications
add confirmed pending-create v2 edit409, active unprepared stale v1/v2 work and explicitly
selected paused proposals. Server-current choices use actual authorized detail/context;
new replacements remain ordinary v1 edits at the reviewed current revision. Actual
original create/ancestor receipts establish v2 origin; missing creation audit is never
invented. Own receipt progress alone does not establish unrelated server staleness.

Existing local choice/lookup methods also support explicitly reconsidered paused work
against the actual chosen phone state. These choices issue no HTTP. Replacements use
its actual current typed predecessor and wait for matching real receipts before command
materialization. Earlier pending chosen work remains distinct from confirmed server state.

New server/local retained decisions use versions3/4 in the existing schema4 resolutions
store. Legacy1/2 interpretation remains strict. Original actions, wire bytes, proposals,
predecessors and earlier decisions/dispositions stay immutable. A reconsideration keeps
its original paused action blocked and links the earlier exact pause/generation. Only
fresh explicitly selected actions may deliver. Server-current choices atomically cover
the reviewed active unsent branch and descendants; unresolved unknown outcomes block
competing decisions. Existing local choices may preserve chosen uncertain ancestors
because new dependent work still waits for their actual matching receipts.

Recovery verifies source, complete selected intent, active lineage or actual receipt/
validated later dispositions, current baseline and historical effects. Linked decision
validation is finite within one transaction; any failed member refuses the result.
Missing/corrupt effects cannot be justified solely by another link. Current own-read
recovers committed choices before fresh write checks/HTTP, including after edit loss,
original review expiry, reopen and legitimate progress. A new current review privately
pins its original own-read evidence; independent refresh never renews that review.

New choices use snapshot/head/baseline/generation CAS and ordinary IDB completion.
The100-action and100-decision qualification bounds include the proposed insertion;
combined100/100 review and exact recovery meet explicit30-second execution fences;
refusal preserves history and prior recoveries. These are local qualification bounds,
not a universal server-history policy. Deadline/cancellation, denial and safe error
contracts remain. No endpoint/OpenAPI/command/schema upgrade or activation is added.

See [retained-proposal evidence](RETAINED_PROPOSAL_RESOLUTION_EVIDENCE.md). Qualification
and review status is recorded there; no full Story2.3/UI, physical-device/browser update,
native permissions/rollback or release readiness is implied.

## Online organization read API subset — 2026-10-26

The separately constructed `admin_http` candidate owns
`GET /api/v1/admin/captures` and `GET /api/v1/admin/captures/{capture_id}`.
Every request, including continuation, checks current fixed-organization
`kdg_capture.capture.read.all`, verified account/durable actor/membership and exact
organization authorization/resource scope before checkout. No client selector, role
name, own-read grant or offline observation confers all-read authority. Denial has no
own fallback. Server transaction mode is `all_read`; organization predicates and
original child/questionnaire joins apply independently of the cursor. Existing own
endpoints and offline observation remain unchanged.

Detail returns the existing complete `CaptureDetail`, including immutable owner/actor,
original questionnaire definition and stored creation/update provenance. It adds no
actor names, audit events, revision archive, write acknowledgement or edit authority.
Missing/foreign organization detail remains the same safe 404; invalid required stored
evidence fails safely without partial results. Historical reading does not depend on
current child activity or assignment.

History requires explicit inclusive `from_date`/`to_date`, default `limit=30`, maximum
100, optional canonical base64url cursor of at most 2048 bytes. Closed navigation binds
current account/org/read.all/date/limit and descending immutable `(created_at,id)`.
Own/all cursors are incompatible. Current authority and independent SQL filters remain
required for any valid cursor position; no HMAC, cursor registry or implied snapshot.
The closed page contains `org_id`, `account_id`, dates, limit, complete items and nullable
`next_cursor`, with no observation, expiry or offline lease. Row selection is limit+1;
actual UTF8 limits remain 512 KiB per detail and 2 MiB per page. Byte-limited continuation
starts after the last included item without skipping omitted valid rows.

One original ten-second budget covers authorization, bounded acquisition, worker-owned
read-only transaction/release and final response construction. Access has at most three
seconds and SQL entry requires the original one-second-fresh observation. Cancellation
awaits worker unwind. All responses/errors are private/no-store with stable safe typed
errors. Nothing mounts these routes or sends all-record data to browser persistence.

Owner-exported `admin-openapi.json` and `contracts/admin-generated/` describe this subset;
[online read evidence](ONLINE_ADMIN_READ_EVIDENCE.md) records current qualification.
Actor-display mapping, audit DTO/routes, online portal/session UI, actual restricted-role
SQL and activation are not established by this API subset. No complete Story 3.1 claim.

## Bounded online audit metadata API subset — 2026-10-26

The separately constructed `audit_http` candidate exposes
`GET /api/v1/admin/captures/{capture_id}/events`. Every page requires the same current
fixed-org capture.read.all account/actor/membership and organization resource scope
as the administrator read API. No own fallback, offline observation or stored authority.

The closed page has org_id, account_id (verified reader), capture_id, original
owner_account_id/owner_actor_id, created_by/created_at, updated_by/updated_at,
current_revision, limit, events and next_cursor. Each event contains revision,
command_type (capture.create/edit), executor_actor_id, nullable initiator_actor_id and
recorded_at. IDs represent durable actors; actor-name resolution remains a separate
Identity-owned HTTP contract and is not supplied by assignment-target discovery.
Creation/update stamps and revision recorded_at are independent server statement times,
not exact commit instants. Preserve actual executor/initiator and original ownership.

Read immutable capture_revision metadata directly, without executor-private outcomes,
answer snapshots, definitions, receipt/operation/outcome IDs or operational logs. One
bounded SELECT observes the parent and lateral event selection coherently. No-op/retry
receipts add no event. Validate after the short read-only all_read transaction; release
and final serialization remain inside the original 10-second budget, with owned unwind.

Closed query accepts only limit (default 30/max 100) and cursor (maximum 2,048 bytes).
Numeric revision DESC and strict revision < last define navigation. A canonical closed
cursor binds version, verified caller/org/capture/read.all/limit/last revision. SQL scope
remains independently checked; cursor positions confer no authority. Limit+1 determines
continuation; actual UTF8 response is at most 64 KiB. No cross-request snapshot promise.
Newer events are available on refresh. Missing/foreign records share private 404; invalid
stored evidence returns a safe unavailable error, never partial audit data.

Owner-generated audit OpenAPI/client and [audit evidence](ONLINE_AUDIT_READ_EVIDENCE.md)
record this technical subset. Historical display names, portal/UI, actual native SQL/RLS
and full Story 3.1 remain outstanding; no migration or activation is performed.

## Online administrator edit-context API subset — 2026-10-26

The separate `admin_edit_context_http` candidate exposes
`GET /api/v1/admin/captures/{capture_id}/edit-context`. Success requires current fixed-org
capture.read.all AND capture.edit.all before checkout. Independently verified organization
resource/admission scopes and current account/durable actor/membership must agree across
the ordered pair. Denial never falls back to own permissions. The pair shares one
three-second Access deadline inside the original ten-second request budget.

The first read check's monotonic observation remains the SQL-entry freshness reference;
the second decision and acquisition cannot refresh it. Use read-only all_read, existing
organization-bound original detail retrieval and post-commit validation. Release and
final serialization remain in the original budget; cancellation awaits owned unwind.

Closed `AdminEditContext` contains only `capture: CaptureDetail` and exact ordered
`editable_fields: ["observation_date", "answers"]`. It preserves displayed revision,
original definition/version, child, owner/actor and stored provenance. The current
administrator need not be the original owner/actor. Historical context does not require
current child activity, assignment or new-create eligibility. Detail stays at most512KiB;
whole response at most544KiB actual UTF8. Missing/foreign targets share private404;
malformed evidence/execution fails safely without a partial capture.

Any query selector or nonempty body is refused. No observations, expiry/offline leases,
actor names, command/receipt/outcome fields or write authority are returned. Responses
remain private/no-store and no browser cache or startup route is activated. Existing
own-only context and offline observations remain unchanged. Future Save/recovery/conflict
contracts must close separately and recheck authority at their own action boundary.

See [administrator context evidence](ONLINE_ADMIN_EDIT_CONTEXT_EVIDENCE.md) and owner
OpenAPI/generated client. No schema change, native/driver qualification, named portal
presentation or complete Story3.1/3.2 claim is made.


## Online administrator conditional edit and recovery candidate — 2026-10-27

The inert PUT `/api/v1/admin/captures/{capture_id}` consumes existing EditCommand
(operation_id, command_version=1, expected_revision, observation_date, answers) and
returns the existing compact committed CaptureReceipt. Current organization read.all
then edit.all must match verified account/durable actor/membership before checkout.
Use actual executor all_write; never impersonate the original owner or fall back to own.
The first read observation remains one-second fresh at SQL entry, under one three-second
Access-pair and original ten-second total budget. Original-version validation and row
locking/conditional revision apply; original owner/child/questionnaire/creation/device
facts remain unchanged. Changed capture, private operation receipt and revision evidence
commit together. No-op records a receipt without an update/history event; stale no-op
still conflicts. Conflict409 carries only stable error_id and current_revision.

GET `/api/v1/admin/operations/{operation_id}?command_type=capture.edit` requires exactly
that query item and current read.all under all_read, without edit.all, body or selectors.
Receipt lookup remains organization/current-executor/command/operation private. Authorize
the actual stored target before replay/recovery, even when retry path/answers differ;
return the original receipt/revision without another effect. A private missing operation
returns unresolved, which never proves in-flight work cannot commit later. Invalid or
unavailable stored target yields safe503 operation_verification_unavailable. Existing
receipts have no own/admin surface discriminator; this route asserts current all-read,
not invented provenance. All responses/errors private/no-store; final serialization and
owned release remain within the original execution budget.

No proposal store, force overwrite, draft, offline all-edit observation or schema change.
The candidate is not mounted or released. See [qualified evidence](ONLINE_ADMIN_EDIT_EVIDENCE.md)
and [generated contract](../contracts/admin-edit-generated/index.ts). Full portal conflict
comparison, session rendering, native SQL/RLS/driver and release qualification remain.
