# People–Leave consequential change coordination

**Status:** Planning baseline adopted by user on 2026-10-23 under
[ADR-0062](../decisions/0062-people-leave-prepared-source-change-coordination.md);
implementation/runtime verification and overall readiness remain pending  
**Date:** 2026-10-23  
**Owners:** People source owner and Leave request-consequence owner

Sources: platform ADR-0020/0022/0025/0026/0028/0031/0040/0041/0042/0060; Leave
ADR-0147/0154/0160/0163. Earlier candidate analysis remains in
[identity/employment](identity-access-employment-e1.md#consequential-people-change-attempts-and-cancellation-fence--e5-candidate-2026-10-23).
This document consolidates its minimum wire/state contract; it does not create another
employee master, grant service, workflow engine or customer configuration feature.

## Ownership and protocol identities

People alone writes employment/period/supervisor facts and its registered/committed/
cancelled attempt. Leave alone writes preparation gates, request consequences and current
approval authority. Communication is authenticated HTTP, never cross-owner database access.
Service caller/consumer/environment scope follows the restricted caller matrix; human
source authority remains separate from narrow service recovery.

All identifiers are UUIDs; revision counters are canonical positive bigint decimal strings.
Dates are ISO date-only; effective instants/server times are UTC RFC3339. Each message uses
`protocol_version: 1`. Original human `operation_id`, People `source_attempt_id`, selected
item identity, Leave `preparation_id`, request identity and service work identity are distinct.
The source attempt binds immutable canonical input and exact source/expected revision.
`change_digest` is its backend SHA-256 canonical-input digest, lowercase 64 hexadecimal
characters; not a browser credential or substitute for source/consumer authorization.

Each source variant carries one exact employment relationship/item:

| `change_kind` | Closed proposed-change branch |
| --- | --- |
| `supervisor_change` | Employment ID, supervisor employment UUID or explicit null, closed effective intent: on_commit or at an explicit UTC instant |
| `employment_period_add` | Employment ID, stable new period ID, inclusive start date and nullable inclusive end date |
| `employment_period_end` | Employment ID, existing period ID and inclusive end date |

Shared source validation still rejects self/cross-org supervisor, invalid/overlapping periods
and stale revisions. A selected batch uses actual identified per-item outcomes; its parent
cannot claim all items changed from one accepted request. Additional corrections need an
explicit source variant before activation. These source branches do not authorize arbitrary
employment patches. Supervisor date-only UI normalization must bind a declared timezone
before planned-date activation; this contract accepts normalized effective instants and
does not invent a new organization timezone setting.

## Restricted internal HTTP operations

These routes are selected design names, not existing deployed endpoints. Unknown fields,
wrong source variants and unsupported request versions fail the shared safe validation
contract. Do not expose them as browser commands.

| Owner / method and suffix under `/internal/v1/organizations/{org_id}` | Required request / response contract |
| --- | --- |
| Leave POST `/people-change-preparations` | Request: protocol version, registered source attempt ID, consumer `leave`, source revision, change digest, exact typed proposed change and source-reviewed consequence evidence. Response: preparation ID, source attempt ID, protocol version, `state: prepared`, bound source revision/digest. Actual source-review evidence schema must be closed with the source command |
| Leave GET `/people-change-preparations/{preparation_id}` | Current permitted preparation identity/source binding and state prepared/reconciled/cancelled; no employee request export or sensitive review payload |
| People GET `/change-attempts/{source_attempt_id}` | Exact bound consumer/organization only; response protocol/attempt/digest/source identity, state registered/committed/cancelled. Committed adds actual committed source revision and outcome reference; cancelled adds definitive cancellation reference. Registered does not imply source success |
| People POST `/change-attempts/{source_attempt_id}/cancel` | Request protocol version, recovery operation ID, exact bound consumer/preparation ID. Atomic registered-to-cancelled or original already-terminal outcome. Never alter proposed facts or reverse committed source change |
| Leave POST `/people-change-preparations/{preparation_id}/reconcile` | Request protocol version and original source attempt ID; authoritative source outcome verified outside locks before protected local consequence/release. Response current preparation state and safe outcome reference, not human approval |

The actual human People source command registers/commits through its owning source API;
these internal routes do not supply a generic service-only fact-commit bypass. Current
People facts/effective observations use the owning read contract, not preparation GET.
Outcome lookup stays compact: it does not expose the whole registered input to another app.
A preparation's typed proposal comes from the authenticated People producer and must match
the attempt binding before People can use it for commit.

## State and execution sequence

1. People verifies the current human source command, registers its exact immutable attempt
   and obtains Leave preparation after review. No gate/DB lock during human review.
2. Leave verifies producer/scope/current source observations outside locks. Under its local
   dependency/employee protocol, re-enumerate affected work and review consequences; record
   one prepared gate on the actual protected source subjects. Conflicting active preparation
   returns bounded busy; no unguarded second change. Material changed review rejects with
   renewed source confirmation before any source mutation.
3. People binds preparation ID/digest/revision to that attempt. In one owner transaction,
   require registered state and expected source revision, then commit source facts/history/
   revision/original outcome/consequence intent and committed attempt state. No HTTP wait
   under locks. Cancel competes on that same attempt; cancelled cannot commit later.
4. Leave resolves the exact authoritative outcome via People HTTP. Registered/unknown keeps
   the gate; cancelled permits local cancelled release. Committed version drives actual
   protected consequences/evidence/intent then reconciled release. Superseded messages cannot
   overwrite later local source observations or unfinished assignment precedence.
5. Record/recover each owner's outcome independently. A reconciliation failure after People
   commit is recoverable pending consequence, not source rollback or whole-operation success.

Matching prepare retries reuse the same stored binding; a digest/target/revision mismatch
cannot reuse it. A duplicate reconcile/cancel returns current original causal progress,
not repeated effect. Late preparation after source cancellation reconciles to cancelled;
it cannot revive commit rights. Source attempt terminal evidence and supported message
versions remain retained under the owning compatibility/retry policy.

No timer by itself releases prepared gates. A deadline may trigger exact-attempt cancel or
reconciliation; only authoritative cancellation or reconciled committed consequences
makes release safe. People unavailability is distinct from cancellation. Source outcome
lookup absence is not proof that a delayed execution cannot commit.

## Future facts, current authority and access lifetime

Recording a scheduled change participates now and installs sufficient source revision/
effective-boundary evidence before preparation release; future authority does not start
early and the gate is not retained until that date. At a known boundary, current checks
invalidate old observations even if workers lag. Leave ADR-0163's final protected authority
instant governs short bounded supervisor transactions; restarted checks need current facts.
Completed/final steps and L-0160's superseded temporary-responsibility rules remain binding.

Source participation cutover precedes initial authoritative baseline/reconciliation and
consequential admission. Access disable blocks user actions but does not unregister source
participation or cancel existing work. Narrow recovery survives without reviving user rights.
No automatic retirement/customer registry; technical decommission requires safe fencing/
reconciliation and queued-version compatibility. Actual cutover implementation is an explicit
source/release prerequisite, not a claimed existing runtime registry.

## Remaining acceptance inputs and verification

The caller matrix, source-attempt fence, local guard protocol, state/operation interfaces
and ownership are consolidated here. Remaining C4 contract gates are exact reviewed-
consequence evidence per source command, planned-date timezone normalization, People physical
attempt storage/row order, actual consumer cutover/credential transport and numerical
execution/recovery/outage limits. Whole-protocol architecture adoption still requires
those bounded choices and owner verification planning; accepted predecessor ADRs are unchanged.
Do not reopen already agreed People/Leave ownership or add another UI flow to answer them.

Real People/Leave suites must exercise both commit/cancel orders, old-read-before-prepare,
intervening new request/membership, late preparation, lost source/cancel responses, failed/
resumed consequence, exact selected item outcomes, effective boundary with worker lag,
current old/new/temp eligibility, wrong service/consumer/scope/version and Access disable.
E5-WRITER-02/AUTH-01 link owner evidence; 5.32 adds only missing composition. Recovery uses
actual owner commands/durable consequence intent, not notification transport impersonating
business authorization. No numerical SLA, implementation, tests, grants or migrations exist
from this planning pass. C5/C6 still own closed consumer schema and final test/order/size.


## Initial execution and recovery budgets — 2026-10-23

**Selected technical design values to verify, not measured performance/SLA or a promise
that the validation workload fits them.** Applies to consequential E5/source-coordination
executions; E1 lightweight draft deadlines remain unchanged. Use monotonic elapsed time
for deadlines and UTC/domain time for business effective instants. All nested work shares
the remaining outer deadline; a hop/restart never resets it.

| Boundary | Initial value / required behavior |
| --- | --- |
| Human consequential backend execution | 30 seconds total from accepted execution through connection acquisition, owner calls, preparation, protected transaction, commit and response preparation |
| Access / People current fact or exact outcome read | At most 3 seconds per call within remaining execution budget; no hidden automatic transport retries |
| Internal prepare/reconcile HTTP step | At most 20 seconds within remaining outer deadline, leaving required local completion work budget; do not initiate a step that cannot safely fit. A timed-out remote step is unresolved, not rolled back |
| Coordination lock wait | At most 1 second per acquisition and always within the 5-second total local transaction budget; cumulative waits never extend that total |
| Owning local business transaction | At most 5 seconds including commit/rollback path, clipped to remaining execution time. No external HTTP or notification delivery under its locks |
| Protected supervisor authority instant | Final current check under protection; at most the remaining 5-second local transaction budget afterward. This operational bound implements L-0163, not a five-second grace period for checks after the boundary |
| Browser mutation wait | 35 seconds initial timeout. Disconnect/cancellation never proves rollback; retain original operation/payload |
| Automatic uncertainty observation | At most 15 additional seconds, at most 3 serialized outcome lookups. No automatic consequential mutation reissue in this observation cycle; explicit user Retry resolves the original identity first |
| Durable reconciliation attempt | 20-second total step budget, same 3-second observation/5-second local transaction caps; no overlapping attempts for the same causal work |

Total deadlines include discovery/calculation and any local guard-set restart. On restart,
freshen required observations/authority and spend only remaining time. A command cannot
continue a fresh human mutation as a worker just because its deadline expired. A committed
source may still require its separately owned durable consequence recovery; that is actual
reconciliation, not extension of the original human authority window.

Driver/statement/lock timeouts, bounded connection acquisition and cancellation cleanup
must actually enforce the outer deadlines. Merely configuring one HTTP client timeout is
insufficient, and a commit deadline failure can leave an unknown outcome. Preserve original
operation and resolve its receipt/source attempt; never classify an uncertain commit as
safe to execute with a new identity. Actual implementations test the server, proxy and
browser timeout interaction against these values.

Explicit user Retry begins with original outcome lookup. A definitively uncommitted action
may execute the same frozen command under a fresh bounded current-authority execution; a
changed review needs a distinct new confirmation only after no-commit is established.
Known denial/conflict/validation stops automatic observation. After bounded observation,
show the existing unconfirmed/Retry behavior, not endless polling or a new technical screen.
E1's own autosave retry cadence is not changed by this consequential-command choice.

### Long outage and durable retry

Use the actual owner's durable causal work, no duplicate notification queue or universal
reconciliation service. Initially retry failed reconciliation after 30 seconds, then
60/120 seconds, capped at 5 minutes, with bounded jitter and one claimed execution per
causal item. Retain original identities and supported versions; successful/terminal
resolution stops retry. Persist next-attempt state so restarts do not duplicate effects
or replay every missed retry. Exact worker claim/storage uses its owning delivery contract.

At 5 minutes of continuously unresolved coordination, emit one grouped technical incident
under P-0037 with safe operation/trace/age metadata. Fresh evidence determines resolution;
a timer or empty queue cannot claim recovery. This threshold is technical configuration,
not an employee notification/approval escalation or a promise to restore service in five
minutes. Reconciliation remains bounded per attempt through longer outages.

No elapsed duration alone releases a Leave preparation gate or deletes a source attempt.
If cancel is required, People must durably establish cancelled state; committed source
changes reconcile to their actual consequences. Unrelated independently protected work
remains available. No automatic source rollback, user administrator-chase flow or indefinite
spinner is added. Existing support/recovery tooling handles an unresolved technical incident.

### Workload and change control

Validate representative current-client load below 100 employees and the agreed 1,000-
employee safety-factor workload, with historical/future requests and concurrent ordinary
use. Measure total/calculation/dependency/lock/transaction phases plus timeout cleanup.
Initial local shared-setting changes remain synchronous; calculate/prepare outside locks,
then protected current checks and writes. These values are execution caps, not evidence
that a 1,000-request write set completes in five seconds. Failure to fit requires measured
query/batching/transaction design review before release; it does not silently authorize
the withdrawn background-impact-worker/progress-screen proposal.

C4 numerical execution/recovery/outage values are now bound at design level. Runtime
verification and performance acceptance remain actual owner delivery evidence. The exact
source schema/normalization/storage/cutover/transport gates listed above remain open;
these budget choices do not establish whole-protocol acceptance or implementation readiness.
No code, settings, credentials, tests, benchmark, migration or deployment changed.


## Source fields and effective-intent binding — 2026-10-23

**Technical binding of already scoped current versus planned source changes.** Every
registered change has `change_kind`, `employment_id`, expected `source_revision` and its
closed source branch below. Source revision must cover every source fact used by that
command/read; People locks/checks its actual owning row and advances it once with the
accepted source change. A source adapter cannot compare only an unrelated profile revision.
Body organization/actor selectors cannot override verified caller/stored attempt context.

| Source branch | Exact additional input fields |
| --- | --- |
| `supervisor_change` | `supervisor_employment_id` (UUID or explicit null), `effective` union below |
| `employment_period_add` | Stable server-assigned `period_id`, `start_date` (date), `end_date` (date or explicit null) |
| `employment_period_end` | Existing `period_id`, `end_date` (date); no employee-master replacement or period deletion |

The `effective` union is either `{kind: on_commit}` or
`{kind: at, effective_at: <UTC RFC3339 instant>}`. Closed source models reject unknown fields
and incompatible variants. IDs generated when the original source intent is registered
are retained on retries; never regenerate a period/attempt ID and call it the same change.
Actual user input fingerprinting excludes subsequently generated commit timestamps.

### Immediate supervisor changes

Single current edit and immediate selected replacement use `on_commit`: People assigns the
effective UTC instant from its server clock in the final source-write transaction, after
Leave preparation. It is not request arrival, review, attempt registration or browser time.
Store the actual resulting instant in source history/outcome and carry it into Leave
consequence evidence. Matching replay returns the original actual instant, not a new now.

Preparation previews old/new responsibility consequences without needing to predict that
future commit timestamp. The canonical proposed change binds on_commit intent; People
verifies that intent/digest/preparation before resolving the instant. This closes the race
where an immediate change was accidentally backdated to before preparation and old valid
decisions were reinterpreted as unauthorized. Earlier completed decisions remain preserved.

### Planned supervisor dates

The People wire fact is an explicit instant. A Leave source editor offering an effective
calendar date normalizes it on the backend for each selected employee using the declared
employee work timezone observation already owned by Leave. Review shows each actual local
date/zone and normalized instant where needed to distinguish selected employees; differing
zones may produce differing UTC instants. No browser/server default timezone or new shared
organization-timezone setting is introduced. Other authorized People clients must likewise
supply their own explicitly interpreted instant; People does not query Leave tables.

Retain normalization evidence with the source review/preparation: input civil date, IANA
zone name, timezone database version, actual work-setting/source revision and normalized
UTC instant. Resolve the setting applicable before the proposed change; do not select the
new version by asking it which timezone makes itself effective. Protect/recheck the relevant
Leave work-setting versions at confirmation. A changed normalization result requires renewed
review, not silently reinterpreted date. Missing timezone blocks only that date-based Leave
editor's calculation; ordinary People current edit still accepts on_commit without a Leave
work profile. No automatic UTC fallback is supplied.

Interpret start of the chosen local date as its earliest valid instant. If midnight repeats,
use its earliest occurrence; if midnight does not exist, use the first valid instant still
within that date. A wholly nonexistent civil date is invalid and preserves input; never
silently switch to a different date. Verify these cases with the selected maintained timezone
library and retain the chosen instant so later timezone-data changes do not rewrite the
stored schedule. Existing scheduled amendment/cancellation is a new reviewed source action.

Planned mode is for a still-future intended change. If it has become due before the source
change can be committed, require refreshed source review rather than silently converting it
to on_commit or inserting a retroactive supervisor fact. This does not invent a historical
supervisor-correction workflow. A schedule already committed earlier retains its actual
boundary and is enforced when due even if workers lag.

### Employment periods are dates

Period start/end stay literal date-only inclusive source facts; do not convert them into
supervisor instants or truncate them using the approver/browser timezone. E3 evaluates
requested Leave work dates against those periods, preserving gaps and inclusive end date.
Period-add is not automatic app admission, policy assignment, balance reset or continuous
service. Bound source and resulting People revision/period identity are sufficient for
Leave's exact dated read and reconciliation; whole employee payload copies are forbidden.

### Verification and remaining C4 gates

Actual producer tests cover on_commit clock assigned after preparation, replay preserving
instant, future planned date per selected zone, changed work-setting observation, missing
zone with usable current edit, midnight repeat/gap/nonexistent date, planned date becoming
due before commit, committed schedule with delayed worker and period end/add/gap boundaries.
Keep final authority-instant checks under L-0163; normalization is not authority.

Source branches and normalization are now selected design baseline, not implementation or
whole-protocol acceptance. Exact source reviewed-consequence projection, People attempt
storage/row order and concrete cutover/credential transport remain finite C4 closure items.
Numerical budgets already bound above apply. Existing source APIs/UI own validation and
review handling; no new source feature, date picker or employee permission is introduced.
No code, tests, migration, settings or deployment changed.


## Source review evidence and People attempt persistence — 2026-10-23

**Concrete contract binding within existing review/accountability rules.** Reuse the
existing source Review/Confirm and immutable consequential calculation evidence. There is
no separately editable review workflow, signed browser token or new review-record service.

### Closed preparation review evidence

`source_review` contains exactly `schema_version: 1`, `source_revision`, `change_digest`,
`consequence_digest` and `normalization` (null or the closed planned-date object). Both
digests are lowercase 64-character SHA-256 hex over the backend's versioned canonical
projection. `normalization` contains `civil_date`, `zone`, `tzdb_version`,
`work_settings_revision` and `effective_at`; source-specific actual setting/version
references are retained in the linked owning calculation evidence. On-commit source intent
uses null normalization and resolves its actual instant later in People.

The change projection contains the exact source branch/expected revision and selected
item, not a later filter evaluation. The consequence projection contains a deterministic
ordered set of actual affected request identities/current cycles/revisions and these
source-appropriate results:

| Source family | Consequential reviewed fields |
| --- | --- |
| Supervisor change | Actual affected unfinished supervisor responsibility/step, old/proposed effective assignee or pending eligibility/attention result; temporary supersession scope, completed/final-step preservation; effective intent/date |
| Period end/add | Actual relevant requested-date eligibility before/after; previous/revised paid/unpaid/duration allocation where changed under E3; outstanding validity/coverage/response applicability and required approved-request protection/attention |

Use canonical codes/UUIDs/ISO dates/integer-minute decimal strings, not display labels,
mutable actor names, check timestamps or notification-delivery status. Reuse E3 normalized
allocation projections. Compare actual consequential changes, not every metadata/source
revision with no meaningful effect. Display exact required before/after consequences
through the already authorized source review. L-0151/0162 govern later unpaid notice/
initial response closure; an obsolete earlier acknowledgement rule is not revived.

The browser echoes the reviewed digest/evidence, but this grants no authority. Leave
recalculates the projection under protected source/membership/current-input observation
at preparation. Changed consequence returns existing renewed-review behavior before a
gate/source commit; do not silently expand an exact selected set. A matching digest does
not excuse stale source revision or invalid authority. The immutable actual calculation/
review reference and responsible actor are retained with the owning source/consequence
mutation; no full private Leave projection is copied into People attempt metadata.

Service credential or People employment-management authority alone grants no general
Leave request-detail read. The source integration checks the actual required scoped
source/consequence access before returning private affected-request/funding data. If it
cannot provide a mandatory authorized impact review, it must not substitute a redacted
count and claim the review completed. Bind these checks to existing source/Leave action
capability catalog in C5; no new role, default document permission or permission-transfer
workflow is introduced. Medical content remains excluded even from this source projection.

### People-owned attempt relation

Select `people.change_attempt` for the later source writer's durable fence. E1 read-only
People foundation does not pre-create it. The consuming 5.15-K/5.24 source integration adds
only the source variants and storage actually needed then.

| Field group | Concrete structure / invariant |
| --- | --- |
| Identity | UUID `id`, `org_id`, `employment_id`, executor `actor_id`, original `operation_id`; optional original `initiator_actor_id` where executor differs. PK id; unique `(org_id,actor_id,operation_id)` for per-source command; scoped unique `(org_id,employment_id,id)` |
| Immutable proposed action | `protocol_version`, closed `change_kind`, positive bigint expected `source_revision`, canonical input version/digest, closed typed proposed-change payload and source review evidence above; no generic employee JSON |
| Binding | Consumer `leave`, nullable `preparation_id` until obtained; bind once to exact attempt/digest/revision, never substitute another preparation after source commit |
| State | registered/committed/cancelled with positive attempt revision; server-managed creation/update actor/time. All original identity/input/digest fields immutable |
| Committed branch | Non-null resulting source revision and actual immutable People change/outcome references, commit timestamp/effective instant where applicable; cancellation fields null |
| Cancelled branch | Non-null cancellation operation/actor/time and retained definitive cancellation outcome; committed-source/change fields null |
| Registered branch | Both terminal branch fields null; no successful source receipt or source fact change implied |

Use scoped FK to actual `people.employment`, positive counters, explicit non-null union
checks, immutable-input/terminal-state enforcement and indexes `(org_id,state,updated_at,id)`
for narrow recovery plus `(org_id,employment_id,id)` for exact source lookup. Actual
committed history/revision linkage uses the People-owned keys of `employment_change` and
owner outcome storage. No FK into Leave/Access/Identity databases. Attempts are protected
business metadata: force org RLS, restricted non-owner runtime roles and scoped service
operation policy. No runtime delete, rekey, input rewrite or terminal resurrection.

Selected bulk replacement registers independent per-item attempts/operation identities
and retains parent/item correlation under its actual partial-outcome contract. Do not
reuse one operation unique key for several employee attempts or pretend a multi-item
People change is one all-or-nothing cross-owner commit.

### Source write order and atomic terminal transition

All People attempt mutations acquire attempt rows in UUID order first, then applicable
employment/source rows in stable employment UUID order, then source child/history rows
in their declared key order. Cancel needs the attempt row only and never later takes
source locks in reverse order. Binding registration/preparation is a separate short local
transaction; no People source lock is retained during Leave HTTP.

Commit rechecks registered state, exact one-time preparation binding, expected source
revision and current human authority/effective intent, then performs fact/history/revision/
source receipt/consequence intent/attempt-committed update in the same transaction.
Cancel changes registered to cancelled on the same locked attempt. Terminal repeat returns
the original state; a conflicting terminal action cannot be overwritten. Actual source
facts cannot be changed by a maintenance/import/alternate path bypassing participation.
No global People lock or configurable platform transaction engine is introduced.

### Closure status and proof

Source-review and People attempt-storage/row-order decisions are now specified. Actual
People migration/constraint names, typed implementation and runtime tests follow delivery;
capability catalog binding is C5, exact package/test evidence C6. The remaining C4 design
items are concrete credential transport and source-side consumer cutover before protocol
adoption. Existing numerical execution/recovery bounds apply to these transactions.

Owner tests verify digest/input mismatch, intervening changed request, authorized versus
inaccessible impact detail, no medical leak, invalid state unions, immutable input,
per-item identity and both terminal race orders under real roles. No test PASS, code,
migration, credential or grant changed in this planning. Final coverage/order/readiness
and whole-protocol adoption remain open.


## Caller transport and source participation cutover — 2026-10-23

**Final two C4 design bindings; adoption recommendation, not a live change.** Inspected
current `services/access/organization_check.py` and `studies_access.py`: owner-specific
X-Service-Key caller admission and constant-time comparison already exist. This is a
transport reuse source, not proof that People/Leave coordination endpoints are implemented.
No key values, environment files or live settings were read.

### Internal caller transport

Use `X-Service-Key` with distinct environment/owner/caller-policy credentials for People
producer -> Leave, Leave API -> People and Leave recovery -> People. Receiver policy maps
the authenticated credential to allowed operations/consumer, not an untrusted caller name
or role header. Recovery may observe/cancel its bound attempts, never invoke a human source
commit. Missing/invalid/disallowed service identity returns safe service_access_denied;
provider/authority unavailability is not misreported as denial. Compare secrets with the
maintained constant-time primitive and reject absent/duplicate/malformed credential headers.

Use HTTPS with certificate/host verification for non-loopback service transport; explicit
local loopback development transport is configuration, not a production exception. Keep
credentials out of browser bundles, URLs, request/response dumps and trace fields. Deployment
configuration contains secret references, not plaintext keys in scaffold JSON/source docs.
No mTLS infrastructure, new token broker, universal platform credential or per-org keys.

Human-initiated source commands retain end-user bearer propagation/current authorization
through the actual source API. Internal producer preparation carries the verified initiating
context bound to its original source attempt; caller credential alone cannot select an
arbitrary human actor. Durable recovery uses its own actor and stored initiator link, no
retained user bearer required for finishing already committed consequences. Endpoint and
attempt scope checks from the caller matrix still apply in both cases.

Rotate credentials through deployment-controlled bounded overlap of explicitly allowed
old/new caller entries; remove old admission only after actual producer/consumer rollout
verification. Queued work stores causal identity, not credentials; it authenticates with
current permitted service identity when executed. Rotation does not delete work or imply
source-operation expiry. Exact secret provisioning remains the existing owner deployment
mechanism to implement/prove, not another application service.

### Concrete People-side participation barrier

Use one small People-owned `people.consumer_participation` relation with primary key
`(org_id,consumer)` where this protocol permits only consumer `leave`, state inactive/active,
protocol version 1, positive revision and server attribution. This row is source coordination
metadata, not Access app enablement, an employee permission, general subscription catalogue
or new customer control. It remains after Access disable and is not deleted/recreated.

Ensure the stable row before a relevant source execution enters its business transaction,
using a short bounded People-owned preflight with no source locks held. Existing organizations
receive rows during controlled expansion; missing required row is not an unlocked inactive
state. Only controlled owner deployment/adoption may activate it; ordinary runtime source
writers cannot disable/retire/rekey it. Enforce org RLS and actual role/trigger/owned-write
controls, including the narrow UPDATE privilege required for locking SELECT without granting
runtime permission to change participation. No cross-owner database access is used.

Every relevant People fact writer reads the participation row under **FOR SHARE before
attempt/employment/source locks**, within its final local transaction. Actual attempt order
therefore becomes participation -> attempt -> employment -> child/history. Source flow
observes participation before external preparation, then rechecks it under this lock. If
inactive became active and no exact Leave preparation was obtained, roll back and reprepare
outside locks; it cannot commit using its earlier observation. Existing active preparations
and exact source revision checks remain required. Shared reads do not serialize unrelated
employees' source writes against each other.

Activation takes **FOR UPDATE** on that same row, changes inactive to active atomically
and commits before the authoritative Leave baseline is installed. It waits for earlier
shared-guard source transactions to finish; later source transactions see active and
must participate. This creates the missing cutover boundary without holding a lock during
HTTP or scanning/locking the whole employee population. Registered attempts that have not
committed also recheck participation at their final source write.

### Controlled activation and recovery order

1. Migrate People/Leave schemas through their own coordinated histories; install compatible
   restricted caller policy and protocol-aware source/consequence implementations. Keep
   consequential Leave admission blocked. No API startup migration.
2. Verify every supported source/alternate writer obeys the participation barrier and old
   incompatible writers are drained/blocked. Activate People participation through its
   protected owner deployment operation.
3. Outside that transaction, install current source/history/future-boundary observations
   into Leave and reconcile gated concurrent changes. Changes since cutover either have
   required preparation or fail their source commit, so a bare snapshot is not the barrier.
4. Verify source versions/gates/protocol readiness, then allow consequential Leave actions
   subject to independent Access admission/membership/capabilities. Preserve draft and
   independently authorized read behavior; protocol readiness never grants Access rights.

If any step fails, stop dependent activation and report exact owner progress; do not
unconditionally set participation inactive or reverse applied migrations. An active source
with Leave unavailable fails/retries its affected protected action; it cannot silently bypass
the consumer. Unknown attempts resolve through the original fence. Compatible recovery
may restore a supported protocol-aware binary; an older writer that ignores participation
is not a safe rollback. Plan the P-0020 maintenance/recovery path when previous-version
compatibility cannot be preserved. Technical decommission remains explicit, outside MVP
access toggling, with retained work/version evidence.

### C4 adoption checkpoint

The finite C4 design list is now specified: source wire/review/normalization, attempt
storage/row order, caller policy/transport, participation cutover and execution/recovery
bounds. **Recommend adopting this consolidated protocol baseline.** Formal shared adoption
is still pending the user's checkpoint; this statement does not silently accept an ADR.
C5 actual capability/consumer schema bindings and C6 exact acceptance/test/package/order/
sizing remain open, as do runtime delivery proof and overall implementation readiness.

Actual suites verify wrong credentials/scope, non-loopback transport policy, rotation with
queued work, first-row creation, both source-write/activation orderings, registered attempt
crossing activation, incompatible old writer refusal, failed baseline/activation stop and
Access disable with retained participation. Inspect real owner transactions/outcomes.
No code, keys, grants, migrations, network settings, live app toggles or tests changed.


## Protocol adoption recorded — 2026-10-23

User explicitly agreed to adopt this consolidated baseline. Platform ADR-0062 records
acceptance without modifying predecessors. This supersedes earlier pending-adoption or
candidate language for the specified protocol design, not claims about runtime delivery.
C4's finite design items are complete at planning level. Exact C5 consuming capabilities/
closed endpoint models and C6 source-to-test/package/order/size/overall readiness remain
open. Actual producer/worker/migration/transport/concurrency proof is delivery acceptance.
Do not restart the agreed owner/coordination design or treat adoption as implementation
permission. Existing scoped story boundaries remain 80.
