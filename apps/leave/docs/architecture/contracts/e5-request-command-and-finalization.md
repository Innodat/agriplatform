# E5 request commands and finalization — discussion contract

**Status:** Core boundary, app-owned operation-record/scaffold reuse, narrow local coordination and prepared People-change coordination directions approved; concrete protocols and evidence remain open  
**Date:** 2026-10-23  
**Owners:** Leave lead, Platform API owner and affected source-service owners

This refines the approved 5.10-A extraction and consequential consumers in the BMAD
epics. Product rules remain in [features](../../features.md), accepted decisions and
the [spine](../ARCHITECTURE-SPINE.md). It is not a replacement feature specification,
a new workflow engine, implementation permission or completed readiness evidence.

Sources: platform ADR-0012/0013/0022/0025/0031/0035/0056; Leave ADR-0112/0113/0148/
0151/0154; the [E1 persistence contract](e1-draft-persistence-and-recovery.md) and
[shared error/recovery contract](../../../../../platform/docs/architecture/contracts/api-errors-and-operation-recovery.md).

## Proposed command identity and targeting

**Reuse direction approved — 2026-10-23:** Leave owns its operation records alongside
business data; platform conventions and proven scaffold helpers/tests supply common
mechanics. Extend the existing logical Leave recovery model for Leave-specific request
commands rather than introduce a central operation service or duplicate recovery mechanism.
Prove a real consumer before promoting generic scaffolding and verify each app integration.
This approval does not select the exact target DDL, all wire fields or remaining protocols.

| Concern | Proposed E5 contract |
| --- | --- |
| Identities | Request, cycle, step, operation, event and diagnostic trace IDs have distinct meanings. Use UUID resource/operation identities and server-managed positive bigint revisions encoded as decimal strings, consistent with E1. |
| Actor/scope | Server derives current organization, executor actor and permitted employment/request context. A payload, receipt or existing actor ID grants no authority. Preserve human initiator separately for later service execution. |
| Retry identity | Retain `(org_id, actor_id, operation_id)` duplicate scope and command/version/target/input comparison. Same operation with changed command, target or submitted input conflicts; Leave does not inherit KDG's special first-committed-input policy. |
| Expected state | Human reviewed commands include target identity and expected aggregate revision plus bounded command-specific input. Required related-input evidence is checked separately; request revision alone cannot establish its freshness. |
| Canonical input | Extend E1's versioned backend canonicalization/fingerprint contract to each supported request command. Include submitted expected revision and actual command input; exclude changing server observations and timestamps. Retain digest/version, not whole notes/reasons/documents in receipt copies. |
| Current read | Read returns actual permitted current state/revision. An old receipt reports its original compact acknowledgement, not a claim the request still has that status/revision. Neither read nor receipt lookup finalizes. |

E1's selected `leave.operation_receipt` currently requires a draft foreign key and
start/save/discard command enumeration. Request commands cannot simply write arbitrary
request IDs into that draft field or create synthetic drafts to satisfy it.

Propose extending that existing owner-local receipt structure with explicitly typed,
constrained draft/request targets and supported command versions. Preserve existing
draft rows and wire responses. Draft-target commands retain their scoped draft FK;
request-target commands require a scoped request FK. Exactly the allowed target shape
must hold for each command; no unconstrained polymorphic `target_id`. A submission may
remain draft-targeted while its compact result links the created request. Source writes
whose primary target is an adjustment/profile/other source retain that owner's bounded
target contract; this document does not invent all their table shapes.

Keep one logical application-local retry model; no parallel central outcome service.
Exact DDL/target shape, canonical command versions, FK/constraint names and compatible
transition remain required design work. Existing E1 receipt retention/immutability and
supported fingerprint versions stay binding. Follow coordinated compatible schema
changes under platform ADR-0020; an empty new-application database is not an assumed
deployment condition by the time E5 consumes E1.

## Proposed protected effect and outcome envelope

1. Authenticate and obtain owner-authorized inputs outside local business locks under
   explicit validity/consistency contracts. A fresh preflight or draft-save observation
   deadline is insufficient for consequential actions.
2. Enter bounded local coordination for the actual affected scope, resolve an existing
   matching committed receipt, then check current local lifecycle/review revisions and
   protected dependency evidence. Replay does not execute against a newer revision.
3. Invoke one shared request/finalization kernel for the actual command. A parent
   command calling the kernel in its transaction does not create a competing second
   user operation or duplicate parent receipt.
4. Commit required local request/cycle/step and allocation/ledger effects, consequential
   evidence/audit, original operation acknowledgement and outbound/reassessment intent
   together. No visible success before this local envelope commits; rollback leaves
   none of that envelope's effects. Reuse E3-owned models inside permitted Leave ownership;
   do not infer cross-service database transactions.
5. Release local business coordination before external delivery. Required external
   business outcomes remain honestly pending/recoverable until completed by their owner.

Shared configuration protection, employee/cross-employee coverage lock scope, order,
timeouts, related revisions and cross-owner HTTP consistency are **not selected by
these steps**. Those are blocking contracts below; this outline cannot substitute for
an actual algorithm preventing a change between verification and commit.

| Outcome fact | Required distinction |
| --- | --- |
| `status: committed` operation | Its command's local effects/outcome committed. It does not mean the leave request is Approved. |
| Request remains pending | Valid decisions/reservations survive with current outstanding reason. A recorded response/cover/exception can commit while another gate blocks. |
| Request Approved | Actual all-gate finalization and applicable consumption/evidence/intent committed once. Untracked usage has no fictional entitlement effects. |
| Replay acknowledgement | Original operation/result reference and committed revision. Obtain current request state through the authorized current read. |
| Lookup `unresolved` | No authorized committed result is established; absence of a receipt is not proof of failure or permission for a fresh operation. |
| Known local contention timeout | No effects from this attempt; safe busy feedback under L-0113. Distinguish from another matching in-flight attempt or uncertain commit. |
| Changed consequential review | No stale new command commit; preserve input and require current review. Never silently replace expected revision. |
| Lost response/unexpected error | Resolve original identity/outcome; confirmed mutation with failed refresh retries only the read. |

Use the shared `error_id` and safe typed details while preserving supported legacy
response families through explicit adapters. Exact request routes, result models and
error IDs/HTTP mappings remain open; do not copy draft-specific identifiers onto request
actions or branch on English text.

## Proposed condition-resolution recovery ownership

The real resolving command owns triggering reassessment under L-0154. If it cannot
complete required reassessment as part of its permitted current execution, record the
required durable scoped intent with its accepted local action. No best-effort callback,
request-read trigger or universal periodic approval is sufficient.

A resumed worker has a stable scoped work identity, originating command/trigger link,
current request/cycle context and actual service executor. If it makes a later separate
commit, retain its own effect/operation identity and causal link; never rewrite the
original immutable receipt to pretend later finalization happened in the first command.
Recheck current lifecycle, decisions and every gate. Duplicate/stale work cannot consume
twice, invent a human decision or resurrect closed requests. Exact identity, current-
revision handling, claim/fencing/version/retention and retry bounds remain to be bound
against actual E3 worker contracts and each resolving producer.

## Verification and remaining gates

| Gate | Required actual evidence / owner |
| --- | --- |
| Receipt structural evolution | E1 draft receipts still valid; request receipts enforce actual request/organization scope; command/target mismatch rejected; immutable replay and compatible upgrade. Core owns extension; source writers prove their own target shapes. |
| Atomic local envelope | Actual request/ledger/audit/receipt/outbox rollback and one-time concurrent effects under restricted runtime roles; no remote owner stand-in success. Core plus actual command consumers. |
| Fresh local mutable inputs | Concrete related configuration/employee/cross-employee coordination and every relevant local writer; no employee-only lock claim. Leave core/source owners. |
| People employment/supervisor inputs | Concrete through-commit validity and affected-request coordination over HTTP, including change/race/partial recovery. People and actual Leave source consumers. Open. |
| Access input | Current admission/capability and bounded in-flight authority under P-0019/0021; reauthorize delayed/new execution. Access and each real consumer. No draft-save TTL borrowed. |
| Content evidence | E4 owns confirmed association/verified bytes/reference-cleanup protocol and its remaining concrete contract work. E5 5.9/core/actual commands consume it for required-document checks and submitted-reference continuity; bind only actual consumer integration, not a second Content protocol. |
| Trigger/recovery | Actual last-gate command, another gate blocked, unavailable check, interrupted handoff, duplicate worker and terminal race; inspect initiator/executor and one-time effects. Resolving producer plus core/worker. |
| Browser and wire | Committed command versus current request status, unknown original Retry, changed review, confirmed write/read failure and safe error adapters/generated types. Actual browser/API consumers. |

No exact test paths/commands/results, complete event schema, timeout constants or final
source-to-test coverage are claimed. Bind these before affected story readiness and
single-agent sizing. Controlled valid persisted requests establish core/consumer behavior;
actual source and submission producers still prove their real integrations.

Impacts: prove/reuse owner-local outcome, typed error, short transaction and durable intent
patterns; promote generic scaffold/shared-UI gaps only with actual consumers. Existing
agent instructions suffice. This contract and BMAD ownership/evidence links are technical
documentation; no new product rule or accepted ADR alteration. No code, tests, migrations,
live grants, deployment or implementation authorization.

## Local mutable-input coordination direction — approved 2026-10-23

**Narrow scoped shared/exclusive dependency and employee coordination direction approved.**
Concrete SQL/schema, full ordering/dynamic-reference algorithm and verification remain open.
This concerns Leave-owned records only. People employment/supervisor, Access authority and
Content readiness retain separate current-evidence contracts; no local guard locks another
service's facts or permits cross-service tables.

Use persistent, narrowly scoped coordination identities for relevant local dependencies
and the employee within the organization. A request command protects the dependencies it
uses against incompatible changes and serializes its affected employee mutations across
leave types. A configuration writer takes incompatible-change protection on the actual
source and coordinates affected employees/request effects under the same protocol. Use
shared protection for readers and exclusive protection for relevant writers so unrelated
employees reading the same unchanged policy are not all serialized together.

The following are requirements on the proposed protocol, not a claim that a list of locks
alone solves dynamic dependency changes:

1. Discover candidate source/reference and affected-employee sets before taking business
   locks; do external owner waits outside them. Derive scoped identities from actual
   authorized records, not arbitrary client-selected lock keys.
2. Acquire dependency protection in a single deterministic namespace/order, then affected
   employee coordination in stable order. Resolve command scope/payload comparison and
   immutable committed receipt under its own declared duplicate-protection mechanism;
   exact global order including receipt/draft lifecycle guards remains a contract gate.
3. Reload local source references, dependency membership, request/cycle revisions and
   mutable accounting state under protection. If the actual required set differs from
   the protected set, release/restart with a fresh complete set and current observations;
   never proceed with an uncovered dependency or acquire additional locks out of order.
4. Protect creation/removal of dependency references as well as updates to existing
   values. New request/assignment/default/cover relationships cannot appear unnoticed
   while a source writer enumerates affected work. Define each writer's protected index/
   association guard or equivalent concrete protocol; a precomputed list is insufficient.
5. Apply current domain checks and atomic local effects through commit. Release all
   business coordination on commit/rollback, before delivery or waiting on other services.
   Never hold it while the user reviews or edits.
6. Bound contention and complete execution/restart budgets. Known uncommitted contention
   preserves input with existing busy/Retry behavior; an uncertain outcome follows original
   operation recovery. Do not choose a numerical timeout or indefinite retry loop here.

Actual coverage/absence can depend on another employee's responsibility or request. Its
source-changing writer must participate in the same protected dependency protocol; locking
only the applicant cannot establish full coverage. Bind cross-employee discovery and
membership/change protection explicitly before claiming that contract complete. No global
organization lock or unrelated-employee serialization is proposed as a shortcut.

Required concrete work: scoped guard schema or equivalent existing rows, lock mode/SQL,
complete participating writer/reference catalogue, exact ordering including E1 draft
submission, dynamic-set/phantom protection, bounded wait/execution limits and verification
under real roles/concurrency. Select with actual persistence and prove changed policy/
calendar/profile/type/assignment, same-date capacity, two requests funding together,
source assignment arriving during affected-set discovery and cross-employee cover races.
Source-read observations from another owner cannot be made safe by these local guards;
those protocols remain open. No test run, readiness PASS or runtime implementation.

## People change coordination direction — approved 2026-10-23

**Prepare-before-source-commit, separate owner outcomes and recoverable consequence direction approved.**
Concrete shared-service protocol/architecture, deadlines and verification are not yet approved or complete.
Applicable sources are actual employment/period and supervisor changes under P-0040/
0041/0042/0060, including every consequential alternate writer. The shared owner must
agree its write/observation protocol; Leave cannot impose a second employee master.

Propose a durable narrowly scoped change handshake before source commitment, using the
existing owner operation/review/outbox mechanisms rather than a distributed database
transaction. It temporarily prevents conflicting Leave consequential commits across the
source-change window. Draft preservation and unrelated scopes remain independent.

| Phase | Candidate responsibility |
| --- | --- |
| Review | Existing authorized source UI/API reviews exact source change and Leave consequences. No durable business gate or database lock is held during human review. |
| Prepare after confirmation | The real writer obtains a Leave-issued scoped preparation for the exact source operation/expected revision. Under short local coordination, Leave checks current affected requests/review and records a durable pending-change gate for the relevant dependency. Earlier Leave commits are included; later conflicting commits see the gate. If material review changed, abort preparation and return for renewed review before source mutation. |
| Commit source | People verifies the current prepared operation/fence and expected relationship state, then commits its owned fact/history/outcome and required consequence intent locally. Every relevant writer participates; a bare People update bypass cannot be considered safe. No remote wait under People write locks. |
| Apply consequence | Leave verifies actual authoritative source outcome/version outside local locks, then applies current request/authority/funding effects through its protected local writer. Preserve completed decisions and expose eligible transfer or pending attention under existing rules. Source-save success is not consequence completion. |
| Finish | Release the durable pending-change gate only after required consequences are reconciled or authoritative cancellation establishes that the source operation can no longer commit. Each owner retains actual operation/history/causal links; do not roll back another owner's committed fact. |

An execution that read People before gate preparation must still check the relevant gate
inside its protected Leave commit. Preparation uses the same local dependency protocol,
so it either observes the completed Leave mutation or precedes and blocks that mutation;
there is no unchecked old-read window. Source edits must not commit before this participation
is established. This is a proposed proof obligation, not evidence all writers already comply.

Pending change is a durable business-coordination state, not a database lock retained
during HTTP calls. Use bounded execution/deadlines, durable retry and reconciliation.
A gate cannot simply expire and let a delayed old source attempt commit afterwards:
source-operation fencing/cancellation must first prove that attempt cannot still commit.
Committed source changes recover to current consequences; unknown outcomes stay truthful
and use original-operation recovery. Define operational recovery/alerts with existing
support tooling; no business-admin approval queue or indefinite spinner is introduced.
Exact deadline, reconciliation and exceptional-outage bounds remain an unresolved contract,
not a promise that arbitrary network partition preserves both availability and consistency.

Scope includes only dependencies genuinely used by the affected Leave workflows. Define
who may prepare/cancel/observe, active consumer registration/adoption, source revision and
fence transitions, fan-out/affected set, conflict/reconfirmation, expiry/recovery and restart
behavior before acceptance. Existing effective/future-dated employment/supervisor semantics
must remain correct at boundaries even if workers lag; do not delay a fact's effective
meaning or permit stale decisions by introducing a new preparation mechanism. Those
boundary/observation details remain open and may require refining this candidate.

Required tests use actual People/Leave operations and restricted identities: Leave commit
before preparation, old read before gate then commit attempt, changed affected set, source
commit/response loss, failed consequence, cancelled prepare with delayed old source attempt,
concurrent writers, effective-date boundary/worker lag and recovery. Inspect separate owner
outcomes and preserved actual authority/decisions. No selected HTTP routes/schema/lease
constants, architecture acceptance, full proof, runtime tests or readiness claim.

If selected, record the actual shared People participation in its owning platform contract
and determine whether a new linked ADR is needed; do not amend immutable accepted ADRs.
Access bounded in-flight authorization and Content association/readiness are separate
contracts, not automatically covered by this handshake.

## Effective-boundary and authority reconciliation — 2026-10-23

This maps the approved People-change direction to existing source semantics. It does not
select the remaining wire/state/fencing algorithm or assert shared-owner implementation.

| Source situation | Consequential consumer obligation |
| --- | --- |
| Current effective employment/supervisor edit | Prepare relevant Leave dependency before source commit, then reconcile actual new source revision and required local effects before releasing safe participation. Return actual per-owner outcome. |
| Future effective source change recorded now | Recording the new schedule/period is a real source mutation and participates now. Leave keeps only subordinate version/effective-boundary/consequence evidence needed by its workflow, not an editable copy of the employment master. Dates are not treated as current merely because the source save succeeded. |
| Scheduled boundary becomes due | Actual current eligibility/approval checks respect effective facts and known boundaries even while queue/transfer worker processing lags. Gate/revision protocol must cover activation or prevent stale consequential commits; a delayed worker cannot preserve former authority. Exact boundary discovery/date/timezone/fencing algorithm remains open. |
| Scheduled source amendment/cancellation or timezone-dependent boundary changes | Recheck actual owner version and affected Leave dependency evidence. Stale due work cannot apply superseded arrangements; relevant local settings changes participate too. No new universal polling/approval loop. |
| Unavailable or uncertain source after preparation | Original owner operation and durable reconciliation determine committed/cancelled outcome. Do not automatically release only because wall-clock deadline passed; cancel/fence any possible delayed source commit first. Concrete exceptional-outage limits remain open. |

Release a coordination gate when facts/consequences are correctly reconciled, not only
when a replacement approver exists or a leave request becomes Approved. An ineligible
replacement can produce a completed source consequence of truthful pending/coverage
attention with no stale deciding rights; that business condition must not retain an
otherwise completed technical change gate indefinitely. Temporary verification failure
and unknown coordination still need explicit recoverable protocol treatment.

### Access uses its existing bounded in-flight contract

P-0019/0021 already define the authority ordering; the People fact-change handshake does
not extend automatically to grant/membership edits. Each new protected execution checks
current app admission, membership and exact capability through Access, with authenticated
account/actor and typed organization/resource scope. Opening a form, queued work, an old
receipt or a JWT role is not current authority.

A short already-authorized executing command may finish when permission is revoked after
its check, within its explicit execution budget. New, delayed or restarted execution
reauthorizes; receipt access also rechecks current authorization. Service-owned durable
work uses its actual narrow service authority and current domain checks, not relabelled
queued human work. Local assignment/temporary interval/required-step checks still bind;
bounded in-flight capability permission does not keep an expired or superseded assignment
valid. No positive permission cache across requests and no borrowed 10-second draft-save
employment allowance.

Extend the existing canonical Access `/v2/check` contract only for actual E5 resource
scopes/capabilities needed by own/assigned/manager actions; do not assume its current E1
own-person response authorizes all manager records. Bind exact capability catalog/default/
custom role mapping, closed typed resource variants, current verification evidence,
execution/queue deadlines and API/worker recovery tests before readiness. Record this in
the owning shared Access contract when concrete models are selected; no new grant protocol
or accepted-ADR change is required just to reuse existing in-flight ordering.

Required evidence: revoke before confirmation denies; revoke after bounded execution
begins follows existing ordering; delayed/restarted action rechecks; outcome lookup cannot
leak after access loss; Access outage differs from denial; temporary expiry/permanent
replacement invalidates old domain authority independently. Exact tests/commands and
numerical execution budget remain open; no runtime evidence claimed.

## E4 ownership correction — 2026-10-23

The user questioned whether Content work was being repeated. Actual E4 4.4 explicitly
owns association/readiness/reference/cleanup coordination and bounded recovery; 4.13 owns
integrated attachment proof. Their detailed protocol/sizing/test evidence may still be
open, but that work remains in E4. Do not reopen its product review or move those mechanisms
into E5 merely because the consequential consumer is now being reconciled.

E5 owns only its real Leave consumer obligations: 5.9 applies the policy-required-document
condition at submission/final approval; 5.10-A/5.11-A and later producers preserve actual
confirmed references through request/draft lifecycle and check current owner evidence under
E4's protocol. Link E4's contract and tests for bytes, metadata permissions, cleanup,
retention/download and generic association recovery. 5.32-H contributes only demonstrated
request-workflow composition gaps and linked existing evidence; it does not requalify the
whole attachment service or rebuild authorized reads.

No new Content design discussion or delivery boundary follows from this checkpoint.
If mapping identifies a concrete missing E4 contract or producer interaction, record its
exact owner and evidence gap there rather than silently creating another handshake in
this E5 document. E4 is planned, not claimed implemented/ready. Cross-service observation
validity must actually be supplied by that owning contract before dependent E5 readiness;
referencing it alone is not runtime proof or a waiver.

## Core persistence responsibilities and sizing assessment — 2026-10-23

**Proposed contract-bound allocation; not final schema, size PASS or approved split.**
Sources checked: Features request lifecycle/state models; L-0007 with L-0147/0158
supersessions, L-0111 calculation evidence, E1 receipt structural contract and actual
E3 3.17-A composition inputs. Do not reinterpret historical frozen-assignee wording or
introduce new visible states from a persistence design.

| Record responsibility | Minimum required protection/read meaning | Existing owner / proposed core allocation |
| --- | --- | --- |
| Request head | Stable request/organization/employment identity, actual allowed lifecycle, server revision/attribution and current cycle reference; cycle references cannot cross request/organization | Core state/read. Permanent request remains separate from E1 draft; draft closure/create occurs in actual submission producer |
| Submission cycle evidence | Preserve submitted values, applicable policy/calculation/route requirements and initiator; new resubmission creates a distinct cycle under same request; old submitted evidence remains immutable | Core read representation; actual submission/resubmission creates it. Do not put autosaved rejected corrections into immutable submitted evidence |
| Required step instances | Ordered required responsibilities with actual current assignment/revision and accepted omission state; preserve selected final and completed decisions during permitted supervisor transfer | Core state/read contracts; actual assignment/transfer/decision writers own mutations and source evidence |
| Formal decision evidence | Actual actor/authority/acting-for/time/comment and responsibilities satisfied, immutable prior decisions and distinct intermediate versus final outcome | Core read representation; actual 5.18-A/submitting actor commands create evidence. A worker never invents human approval |
| Funding and calculation evidence | Request/cycle linkage and current authoritative allocation inputs; immutable consequential calculation explanation/version under L-0111 | Reuse E3 allocation/accounting and modest calculation evidence. No second ledger, cached authoritative balance or universal snapshot framework |
| Command outcome | Existing Leave operation receipt extended for valid target/command shapes, preserved immutable E1 receipts and supported canonical-input comparison | State/read/recovery support; exact FK/check/version/compatible migration contract required |
| Finalization effects | Current all-gate checks, valid decisions retained or Approved and one-time consumption, audit/evidence/outcome/intent local envelope | Separate protected finalization responsibility using the state/read and E3 contracts |

Structurally enforce local scoped request/cycle/step links, positive revisions, valid
supported states and immutable evidence/write permissions with actual restricted owner
roles. Use existing actor-registry and external reference contracts; do not add cross-owner
FKs or invent employee masters. Exact columns, keys, cycle/head insertion ordering,
index/access paths, mutable pending projections versus immutable submission fields and
safe constraint-error models remain concrete design work.

Two independently testable delivery responsibilities are now visible:

- State/read/recovery support: request/cycle/step evidence interpretation and scope,
  immutable versus mutable fields, actual authorized current read, structural integrity,
  existing receipt extension, E1 compatibility and original-outcome lookup.
- Protected finalization: real current-input/dependency coordination, independent gate
  matrix, tracked/untracked accounting, atomic consequential effects and recovery/terminal
  races through actual owner contracts.

Recommendation: refine approved 5.10-A to the first responsibility and introduce 5.10-B
for the second. Both remain before actual consequential source consumers; B consumes A,
actual source writers consume the relevant A/B contracts, and real submission later proves
its produced records. Do not permit a source mutation needing finalization to rely on A
alone. This is a proposed scope refinement, not an assertion that exact implementation
size is known or that the narrower halves need no further assessment.

A is useful/testable on actual controlled valid owner records and current-read/outcome
interfaces without a future finalizer; it does not expose a fake Submit/Approve action or
claim creation producer proof. B must demonstrate all finalization behavior on actual
storage and E3 effects before consumers rely on it. Existing source/producer tests remain
required; splitting does not move first-use safety into a later optional proof story.

If approved, revise original 5.10-A acceptance/ownership and graph edges explicitly;
retain history of its approved combined intent for traceability. Do not append B as an
approved story, increment agreed boundary count, or mark the split accepted before user
input. No extra UI/permission, new product rule, implementation or readiness authorization.

## Core refinement approved — 2026-10-23

User approved A request state/current reads/operation recovery then B protected finalization.
This supersedes the proposed split wording above: refined 5.10-A owns the first surface,
approved 5.10-B the second. Both remain before actual finalizing source/submit consumers;
there is one state model and one finalizer. The exact record/schema/target/coordination/
recovery contracts and sizes are still open; direction approval is not full contract or
readiness acceptance. The BMAD epics contain current detailed AC ownership and updated
candidate dependency graph; no duplicate specification or implementation is introduced.

## On-behalf/initial-response responsibility assessment — 2026-10-23

**Analysis and one unresolved product proposal; no new split approved.** Read actual
5.12-A ACs and original 5.12/5.14 ownership, Features on-behalf handoff, accepted L-0088/
0151 and extracted A/B core. The existing combined API contains two separately executed
commands, not a single transaction spanning two people:

| Responsibility | Actual writer/read and prerequisites | Scope retained |
| --- | --- | --- |
| On-behalf submission | Own actual submitting capability/target lookup/reason, employee context, 5.11 submission reuse and 5.10-A/B state/finalizer | Real request/cycle/paid reservation, actual permitted own decisions, initiator-versus-employee attribution, outstanding initial response/notice if unpaid, ordinary employee draft untouched |
| Employee response | Actual employee-only access/current amount+revision check and response mutation, 5.19-A terminal protection, 5.10-B reassessment | No proxy, notification-read consent or new approval decision; one response outcome and current finalization or pending reasons |
| Later allocation change | Actual 5.13/5.15 source writer; response applicability/current allocation and L-0151 notice | No renewed response after satisfied/otherwise legitimately closed requirement; preserve initial history and independent gates |
| Browser | Existing 5.12-B uses completed commands and genuine 5.19-B withdrawal | Actor entry and employee detail/action; no second response draft or redesigned workspace |

The extracted core removes duplicate accounting/finalization work from 5.12-A. Two commands
alone do not prove the remaining actual handoff scope is too large; do not split simply
because two actors exist. Concrete payload/current-amount/response-closure contracts and
fixtures must be bound before final single-agent assessment. Keep existing approved combined
boundary until evidence justifies changing it. An independent response consumer before
submission producer is possible with valid controlled records, but is not selected here.

### Open zero-unpaid case: proposal for user decision

L-0151 explicitly leaves zero-unpaid applicability and concurrent initial response/allocation
changes open. For a request initially submitted on behalf with unpaid leave and still
awaiting the employee response, propose: if an authorized real allocation change reduces
current requested unpaid amount to zero, close the response requirement because no unpaid
amount remains. Preserve original handoff/current change/history; do not fabricate an
employee acknowledgement. The actual resolving writer triggers current all-gate reassessment
under L-0154, finalizing only when every other condition passes.

Under this proposal later introduction/increase of unpaid allocation in the same cycle
uses existing L-0151 notice/reason/prior-revised amounts without reopening the closed response.
A fresh resubmission/replacement cycle still applies its own initial rules. Allocation-change
and employee-confirmation races must resolve against actual current evidence under one
protected lifecycle: no stale positive-amount acknowledgement is applied after zero closure,
and no closed request is reopened. Exact harmless stale-result versus conflict presentation
and outcome fields remain technical contract work after the product decision.

**Not approved yet:** This proposal resolves a named open product case; do not implement
it, mark it accepted or rewrite immutable ADR-0151. If accepted, record a linked narrow
ADR resolving that gate, align Features/UX/source/test owners and update actual response/
allocation writer traceability. Other initial employee-only, exact-amount and no-renewal
rules stay unchanged. No new permission, user-visible request state, notice subsystem or
extra manual completion action.

## Zero-unpaid initial-response resolution — approved 2026-10-23

The user accepted the zero-unpaid proposal above. Accepted L-0162 now resolves the named
L-0151 product gate; previous not-approved wording above is historical. Actual allocation
writer closes an outstanding initial response at current zero with change actor/reason,
not employee consent, and invokes 5.10-B fresh finalization or durable recovery. Later
same-cycle unpaid changes notify only; fresh cycles apply initial rules. No new boundary.

Required actual allocation/response contract cases:

| Current initial obligation / allocation | Required writer/response behavior |
| --- | --- |
| Initially fully paid; later unpaid positive | No initial response created; current notice/reason per L-0151 |
| Awaiting initial response; current unpaid positive | Only employee may acknowledge exact current amount/revision |
| Awaiting initial response; authorized allocation becomes zero | Allocation writer closes requirement with linked zero-unpaid reason/history and reassessment; no synthetic acknowledgement |
| Previously acknowledged or closed at zero; later same-cycle unpaid positive | Notice only; no reopened response |
| Employee sends stale positive-amount response after zero closure | No new acknowledgement/finalization based on stale input; return truthful current authorized state through typed conflict/no-action handling |
| New rejected-resubmission/replacement cycle | Evaluate that cycle's initial rules; prior response/closure does not satisfy it |

Bind source allocation, current response applicability and request revision in the actual
protected mutation, with original command outcome and required closure/effect/notice intent.
No separate asynchronous gap may let the request finalize using contradictory allocation/
response state. Do not modify the original immutable acknowledgement/receipt to manufacture
consent. Exact response/action result/error models and how pending recovery stores evidence
remain technical contracts, not an additional product question. Actual 5.12-A/5.13-A/5.15
writers own producer race tests; 5.12-B/5.30/5.31 consume actual required-action status.

## Multi-employee source consequence processing — proposal 2026-10-23

**Superseded recommendation — 2026-10-23:** The user challenged the added complexity. The assistant withdraws background request-impact processing as the default recommendation pending workload evidence; revised synchronous-first proposal follows. This earlier candidate was never approved.

Actual 5.15-Q/S/U source changes may affect many employees/requests. Recommend a protected
source revision and durable affected-work/coordination handoff followed by bounded owner
processing through actual 5.10-A/B contracts, with separate source-saved versus consequence-
complete outcomes. This does not select a generic saga engine or publish-and-forget behavior.

Each actual family must bind its exact reviewed affected scope, changing reference membership,
local source/request version guards and prevention of stale dependent commits before safe
handoff. Required per-item accounting/history/outcome/notice effects are atomic locally;
source success alone cannot assert all impacts applied. Actual unchanged/changed/unavailable/
material-review conflicts and interrupted stale-version recovery need explicit contracts.
Technical gates release after truthful reconciliation, not only after business approval.

Direction remains proposed pending user discussion; exact request-impact worker/manifest/
source commit schema, bounds and source-versus-executor delivery split are not selected.
Use existing worker mechanics with actual source-specific eligibility/calculation semantics;
no policy activation/accrual worker, new administrative review queue, unchecked partial
source save or first-use safety waiver. No runtime tests or readiness claim.

## Synchronous-first local source changes — revised recommendation 2026-10-23

The previous worker/manifest/per-employee gate proposal adds real domain orchestration,
not merely reuse of notification transport. Workload/latency/transaction measurements do
not yet justify it. Withdraw it as default recommendation; do not create worker stories,
new progress states, tables or guard-manifest machinery from that unapproved candidate.

For Leave-owned default/profile/calendar source changes, recommend the existing API
Save/Review/Confirm path completes the required protected source and pending-request
consequences before returning completed success. Prepare expensive review/calculation and
external checks outside business locks; under the concrete local consistency contract,
reload/revalidate protected inputs and commit required source/request/accounting/evidence/
outcome/notification-intent effects together in a short bounded local transaction.
Actual notifications remain delivered afterwards by existing E3 workers. Scheduled approval
reminders/appointment expiry remain their already owned worker responsibilities.

Ordinary UI retains explicit confirmation, saving feedback, success/field or changed-review
handling and original-operation Retry. It does not need a new background-impact progress
screen when the API returns only after the required local effects commit. A timeout or lost
response still resolves the original operation; it is not automatic permission to repeat
Save or claim rollback. Known uncommitted busy failure preserves current input.

Before readiness, use representative supported organization sizes, affected pending-request
counts and dependency fan-out to set/test request/coordination/transaction budgets. Show
actual authoritative calculation/revalidation and row/effect cost; do not size solely by
employee count or solve a broad workload with one long lock-held transaction. If realistic
work does not fit the short synchronous path, bring back the concrete evidence and choose
an explicitly bounded alternative with its actual UI/outcome/atomicity implications. Do
not silently truncate affected sets, impose a new product limit or switch to a worker.

For clarity about the withdrawn alternative: the API would record accepted source/impact
work and a backend worker would claim bounded batches, persist outcomes and resume them
after failure. Bounds would need concrete item/time/claim/retry/total-recovery contracts.
Because saved source and completed consequences could differ, the UI would need truthful
saved/updating/failed-result feedback even if there were no additional user action or
new dedicated screen. Therefore that alternative cannot be described as having no UI
impact. None of those mechanics is currently implemented or selected.

This revision applies only to the proposed many-employee local request-impact mechanism;
it does not reverse the approved People cross-owner preparation direction or existing
notification/timed workers. Those separate boundaries retain their recovery obligations.
Revised direction remains a recommendation for collaborative confirmation; exact workload/
consistency/transaction contracts, atomic evidence, sizing/readiness remain open.

## Workload scale and illustrative cost model — 2026-10-23

**User-selected scale:** 100 employees expected; use 1,000 employees for estimates and
representative validation as a safety factor. This is not a product maximum, measured
capacity or approval of the withdrawn background-impact design. Current synchronous-first
recommendation remains subject to actual workload/transaction measurements under L-0108.

Employee count alone does not determine cost. For a change affecting 1,000 employees,
measure dependency discovery/current-data fetch, per-employee context/earning work,
affected pending-request calculation and row/effect/notice writes separately. Efficient
bulk input fetching must not become a network/database call per employee/date. Reuse
current direct authoritative calculations; do not introduce caches/checkpoints or worker
orchestration merely from this estimate.

**Illustrative arithmetic, not benchmark or predicted duration:** if the actual affected-
request recalculation portion costs 5–20 ms per request when processed serially, it alone
would take approximately:

| Affected pending requests in a 1,000-employee fixture | Recalculation-only sensitivity |
| --- | --- |
| 100 | 0.5–2 seconds |
| 1,000 | 5–20 seconds |
| 5,000 | 25–100 seconds |

The assumed 5–20 ms is unmeasured and not a factual performance range for Leave. Employee
context/history evaluation, data fetching, writes, protected revalidation and contention
are additional, potentially dominant costs. Actual calculation may be faster or slower;
this model identifies what to measure, not an SLA or a reason by itself to add workers.

Candidate verification fixture dimensions (not user-selected product limits): 1,000
employees, several years of retained history, normal/light and one-pending-per-employee
shared changes, a deliberately larger pending-request stress case and concurrent ordinary
browse/submit/approve activity. If using 20 requests per employee per year over five years,
that produces 100,000 historical requests; this is a test assumption, not an observed user
pattern. Record actual policy/portion/date distribution and deployment CPU/memory/database
pool/query plans with results; organization size is not simultaneous-user count.

Proposed planning budgets, still for confirmation/measurement: aim for ordinary
confirmation in a few seconds and the protected write transaction around one second or
less under representative load, with known-safe bounded contention/retry. Heavy preparation
may take longer outside locks, but revalidation/commit must retain through-commit safety;
no stale preflight substitution. Final numeric latency percentiles, execution/lock/recovery
bounds and permitted workload remain readiness gates. Failure to meet them first triggers
query/calculation/transaction design analysis; only measured need justifies architectural
complexity. Notifications remain existing post-commit worker delivery.

FastAPI can serve concurrent requests with correctly used async I/O or its synchronous
endpoint thread pool; CPU-heavy/blocking code in an event-loop handler can still stall that
process. Database connections and conflicting domain locks can constrain concurrency even
when the event loop is free. Test the actual deployment while shared changes run; a separate
worker is not a substitute for efficient calculations or short database transactions.
References checked 2026-10-23: [FastAPI concurrency](https://fastapi.tiangolo.com/async/),
[deployment concurrency](https://fastapi.tiangolo.com/deployment/concepts/) and
[PostgreSQL row locking](https://www.postgresql.org/docs/17/explicit-locking.html).
No runtime benchmark performed or capacity/latency PASS claimed.

## Current scale and endpoint measurement — agreed 2026-10-23

User clarified two current clients together have fewer than 100 employees and explicitly
endorsed endpoint performance metrics to inform decisions as load increases. Adopt the
synchronous-first initial direction for the proposed Leave-owned many-employee source
changes; keep 1,000 employees as the agreed representative validation safety factor.
The withdrawn worker/manifest/progress candidate is not an initial delivery requirement.
No new guarantee that any employee count fits a given transaction is inferred.

Use existing spine AD-13 basic backend OpenTelemetry/structured diagnostics and L-0108
measure-before-performance-machinery. Required measurement allocation:

| Measure | Purpose / existing delivery owner |
| --- | --- |
| Endpoint duration distributions, volume, in-flight work and status/error totals | See latency percentiles and error/timeout changes as usage grows; first API/scaffold consumer proves reusable instrumentation, real E5 routes retain consumer checks |
| Calculation/input preparation, database work, protected transaction and coordination wait durations | Distinguish computation, external wait and lock-held cost; core 5.10-A/B, submission and each real source family supply actual phase evidence |
| Affected employee/request counts and historical workload shape | Relate slow changes to real amount of work; record bounded numerical observations, not employee identity as metric labels |
| Concurrent ordinary route latency during shared setting changes | Validate API remains usable while source review/confirmation executes; representative acceptance/performance fixtures and operational monitoring |

Use route templates/method/result classes and bounded low-cardinality operation categories,
not per-request UUID/raw URLs/employee/organization IDs as metric dimensions. Follow P-0023:
no note/reason/document/payload content in metrics, traces or diagnostic dumps. Safe trace/
operation references remain in their existing authorized diagnostic/evidence contexts.
Export telemetry asynchronously with bounded resource use; collector failure must not
become a business lock wait or invalidate a committed command. Reuse proven instrumentation,
not another telemetry transport or business-admin performance screen.

Observe p50/p95/p99 as appropriate to available sample counts, retaining counts and workload
context; low traffic is not evidence of stable tail latency. Exact instrument names,
buckets, sampling, retention, alerts and production thresholds are delivery inputs under
existing observability owners. The few-second confirmation/roughly one-second transaction
figures above remain proposed objectives, not user-approved SLA or measured results.

Record actual benchmark deployment/data/concurrency, endpoint and phase timings alongside
owner tests; monitor after release using the same measures. A measured problem first
prompts query/data-access/calculation/transaction analysis. Only demonstrated need changes
the architecture or UI. No early worker implementation, new story or size/readiness PASS.

## Core state/read design baseline for validation — 2026-10-23

**Technical design proposal within approved 5.10-A; no new product decision, final DDL,
implementation or readiness PASS.** This makes ownership/constraints specific enough for
schema and command sizing without recreating E3 accounting/E4 attachment mechanisms.

| Proposed Leave record | Minimum state / references | Mutation responsibility |
| --- | --- | --- |
| `request` | UUID identity; org/employment/type references; current cycle; supported actual non-draft lifecycle; positive bigint review revision; server creation/update attribution | Actual submission creates it; accepted request-level changes update its current revision; original identity never changes on resubmission |
| `request_cycle` | UUID identity plus request/org and stable cycle order; immutable submitted values, applicable policy/required responsibility definitions and consequential evidence references | Actual initial/resubmission producer inserts the new submitted evidence; current allocation/assignment changes are not permission to rewrite prior submitted values |
| `approval_step` | UUID identity within request/cycle/org; fixed responsibility/order, current assignment/authority-reference state and revision; optional accepted decision reference | Actual approved transfer changes only unfinished applicable assignment; actual decision binds final evidence; temporary/fallback handling respects existing semantics |
| `approval_decision` | UUID identity within request/cycle/org; actual actor, outcome/comment/time, operation/authority evidence and fixed responsibilities covered | Immutable actual submitting/approving/rejecting command evidence; no worker-generated human decision or later expansion of what the decision covered |
| Existing `operation_receipt` | Existing owner/caller/operation key, supported typed command/target/fingerprint and compact immutable result | Actual caller command commits receipt with its effects; extend E1 compatibly rather than create another recovery mechanism |

These are proposed physical names/ownership to validate, not instructions to create every
future E5 entity. Actual later response/appointment/coverage-exception/correction storage
is introduced by its consuming item. Existing E3 allocation/ledger/calculation evidence
and E4 associations remain referenced through their actual owner contracts, not copied
into a new generic core store.

### One decision can satisfy multiple required responsibilities

Use an optional scoped `decision_id` on each approval step that has an actual accepted
decision. Multiple steps may reference the same immutable decision when L-0158 permits
one confirmation for both; a separate decision-step join table is not needed merely for
this MVP case. The decision's immutable typed responsibility/authority evidence records
which fixed step identities it satisfied. Assignment/responsibility meaning cannot later
be altered to expand that accepted decision. Current step-to-decision association is
write-once once accepted, except explicit future separately authorized correction policy;
no such correction is introduced by this contract.

Enforce matching org/request/cycle in local references. A scoped decision FK is structural
protection; actual same actor/authority/outcome/covered-step validity is checked by the
protected command, with permitted alternate writes also guarded. Configured distinct-person
policy still rejects same-person completion; storage representation is not an authority
exception. A genuine two-step confirmation can reuse one evidence record without making
the supervisor's omitted step Approved or duplicating comments into fake decisions.

### Review revisions and current reads

A committed request/cycle/step change that alters current reviewed consequences advances
the request review revision once for its owning command; applicable step assignment/state
revisions advance as defined by that command. Original-operation replay and reads do not
advance revisions. Related policy/calendar/employment/access facts retain their independent
protection; bumping request revision is not a substitute for their consistency protocol.

Core current read returns request identity, actual revision/status/current-cycle identity
and the minimum allowed current values/outstanding evidence required by its authorized
consumer. Own, assigned-review and administrative scopes require their actual current
capability plus domain relationship; a manager source consumer cannot use an employee-only
permission. Routine absence/cover and sensitive-document metadata stay excluded unless
that specific view is currently authorized for them. Raw ORM rows are not response models.

Current read is not full paginated formal history: broader 5.30-A owns that residual query.
Core history identity/immutable source evidence still supports actual minimum earlier
views. Reuse E1 UUID and decimal-string bigint representations, server-managed attribution
and typed safe error/outcome conventions; exact OpenAPI routes/models remain bound to each
first consumer rather than prebuilding every future endpoint.

Required schema validation before sizing: current-cycle pointer belongs to its request;
cycle order unique per request; step responsibility/order unique under applicable contract;
no cross-org/cross-cycle decision linkage; valid actual lifecycle and no closed resurrection;
immutable submitted/decision evidence; matching request/draft outcome targets; actor/external
references under existing owner rules; insertion order/deferred-reference technique and
compatible migration/RLS/index/error mapping. Exact SQL/constraint/index names and lifecycle
transition matrix are still delivery contract work, not an implemented schema claim.

### Atomic-effect ownership check

A writes no consumption and decides no approval. B validates this actual current state and
its real current-input/response/coverage contracts, then owns its protected all-gate effect
envelope. Actual 5.11/5.12/5.18/5.19/5.20/5.24 and source writers own the source of their
changes/decisions and prove real integration. Replays return immutable acknowledgement
before new-state mutation checks but still require current permitted outcome access.
Rejected correction autosave is separate mutable input and cannot update submitted cycles;
no future correction or response handler is needed to verify A's real read/structural cases.

This baseline reduces unresolved representation choices but does not establish single-agent
fit: compatible receipt migration, actual restricted-role/reference constraints/current-read
models and fixtures still need concrete size/evidence. Keep 5.10-A/B boundaries unchanged;
no extra table, worker, user-visible state or product approval round solely from this pass.

## Request lifecycle and writer participation baseline — 2026-10-23

**Technical allocation of accepted behavior; no new visible states or lifecycle policy.**
Use the source model's submitted/in_approval as pending states for eligibility checks;
Approved, Rejected, Withdrawn and Cancelled retain their distinct meanings. Rejected is
closed for decision/finalization but explicitly eligible for its separate correction/
resubmission workflow. A generic terminal flag cannot disable that approved exception.
Ordinary draft active/discarded/submitted-closure belongs to E1 plus submission, not a
permanent request-head Draft record or an employee withdrawal of saved draft input.
Exact initial submitted/in_approval persistence timing belongs to actual submission's
bound transition/result model; do not invent an extra queued-routing stage to use both.

| Actual writer/read | Admissible current context | Request/cycle consequence and protected participation |
| --- | --- | --- |
| 5.11-A own submission | Editable current ordinary draft; new request, no reused closed-draft create | Create one request/cycle/required steps, record permitted own decisions, close draft/reserve or finalize via B in same local envelope; include employee/date/funding/dependency and draft/outcome guards |
| 5.12-A on-behalf submission | Current actor capability/target context, no employee draft mutation | Create actual request/cycle/initial obligation if unpaid, own decisions only if authorized, reserve or B completion; leave employee's draft intact |
| 5.18-A approve | Current actionable assigned unfinished step in pending request/current cycle | Immutable actual decision/covered steps, pending or B completion; no employee response or funding override inferred |
| 5.18-A reject | Current authorized assigned step and pending request | Rejected with visible reason and one release/unfinished task-response closure; preserve earlier decisions/current cycle history |
| 5.19-A withdraw | Current employee own pending request, including on-behalf origin | Withdrawn, one release/task-response closure, no draft/correction reopening; race with finalization shares protected request/accounting boundary |
| 5.20-A save corrections | Employee's rejected request and open correction revision | Request remains Rejected; no reservation/new cycle/approval and no submitted-history overwrite; ordinary draft independent |
| 5.20-A resubmit | Current rejected request plus explicit current reviewed corrections | Same request/new current cycle and validated fresh allocation/initial rules; close correction editability; preserve old evidence/decisions without carry-forward |
| 5.12-A employee response | Current pending cycle with genuinely outstanding positive initial unpaid requirement | Record employee-only current evidence then B, or current pending; reject stale/proxy/closed confirmation and preserve ordinary draft |
| Actual 5.13/5.15 allocation writer | Pending request and its permitted reviewed current source/action | Protected prior/revised allocation/evidence/notice; L-0162 zero closes initial obligation without consent, later same-cycle increases do not reopen it; B reassessment under actual resolving trigger |
| 5.13-A funding-only | Current exceptional-allocation capability/reason/source rules | No human approval recorded; current B reassessment may complete from previously valid decisions under all gates |
| 5.13-A combined action | Both current funding and assigned-approval authority on pending request | Allocation and actual decision are distinct evidence/effects in one atomic local envelope, then B; no partial combined success |
| 5.5-A exception | Current bounded applicant gap and exception capability/reason | Record actual exception/unchanged gap; B checks all other conditions, no implied manager approval |
| 5.24-A manual transfer | Current eligible authorized target and selected unfinished steps | Only current assignment/step revisions change; prior completed decisions/final steps/clock remain; B only if a bound applicant gate is genuinely resolved |
| 5.24-C/E People effective supervisor change | Prepared authorized current source/item/fence and affected unfinished work | Apply eligible current responsibility or safe pending attention, preserve completed/final work; no stale former supervisor decision while effect processing lags |
| 5.21-A/5.22/5.23 temporary lifecycle | Actual bounded appointment/current revisions/source precedence | Update scoped authority/unfinished work or pending cover, never reopen closed request/extend expired right; preserve valid decision attribution and clock |
| 5.25-A supervisor return | Pending fallback request and current recorded absence/source evidence | Restore required unfinished supervisor step/authority under policy, no reopened valid completed fallback approval; stale fallback cannot finalize alone |
| Source setting change on approved request | Existing approved-request protection, E6 correction rules where relevant | No direct overwrite/conversion/cancellation under pending-only E5 integration; required deficit/coverage attention and factual source history remain owned |
| Reassessment worker | Declared valid trigger and current pending request, own service authority | B uses current gates and actual decisions; no fake human action, repeated consumption or terminal resurrection |
| Reminder/escalation/send/read | Existing current required-action eligibility | Notification/attention state only; no request approval, response satisfaction, funding change or business finalization |
| Current read/operation lookup | Current permitted own/assigned/admin scope | No mutation/revision advance or trigger; original immutable result distinct from current status |
| Approved cancellation/replacement | Actual E6 authority/lifecycle | Not implemented by E5 core/withdrawal/source commands; E6 owns cancellation/reversal/new replacement cycle |

### Local atomic effect obligations by writer family

Request lifecycle, step state and immutable decisions are not independent commits when one
command promises their combined change. Its required allocation/reservation/release or
consumption, calculation/history/audit, compact outcome and notification intent share the
owning local commit. Ordinary concurrent reads see a consistent committed representation;
read projections still recheck current access. Record optimistic revision/related-input
checks under actual coordination; a read-before-write check alone does not suffice.

A no-op receipt replay changes no current revision/effect. Distinct accepted commands
retain their own effects; one matching original operation cannot create another cycle,
response or grant. An automatic worker has separate causal identity, not permission to
update a prior immutable receipt. Changed reviewed consequence requires the actual user's
new current confirmation, never a silently substituted expected revision. Already accepted
condition resolution retains its own declared recovery semantics under current gates.

Unfinished assignment changes may advance current request review/step revisions, but
cannot edit prior accepted decision-to-step evidence. A decision cannot satisfy a later
new responsibility or fresh cycle merely because the actor/name matches. L-0158 shared
same-person decision is limited to the original currently authorized covered responsibilities.

### Planned acceptance-case identities for core and real consumers

These IDs designate planned evidence ownership, not implemented tests or a test-pass claim.
Exact repository test paths/commands will bind to actual packages when delivery is ready;
do not fabricate executable test locations now.

| Planned case | Independent oracle / ownership |
| --- | --- |
| E5-STATE-01 scoped local references | Actual restricted DB/API rejects cross-org/request/cycle linkage; valid linked records read correctly. A owns structural/reference case |
| E5-STATE-02 immutable history | Actual submitted/decision evidence remains unchanged after supported current assignment change; A plus actual transfer writer |
| E5-STATE-03 original versus current | Immutable receipt shows original commit while current authorized read shows later revision/status; replay mutates neither. A plus actual command |
| E5-STATE-04 same-person step coverage | One immutable decision covers exactly original permitted step set; missing authority/distinct-person setting denies; later route change cannot expand it. A structure plus actual decision/submission writers |
| E5-FINAL-01 independent blocked gate | Hold each required gate unsatisfied with valid decisions; actual request remains pending/reserved, no consumption. B with real owner inputs |
| E5-FINAL-02 one-time complete/rollback | Inspect real request, ledger/allocation, audit/outcome and outbox across successful, duplicate and induced local failure; all required effects once or none. B plus each command envelope |
| E5-LIFE-01 approve versus withdraw/reject | Actual competing commands produce one valid closed result and correct one-time accounting, preserved original decisions. Actual 5.18/5.19 plus B |
| E5-LIFE-02 rejected correction/save/resubmit | Same identity/new cycle, immutable old evidence, no pre-resubmit reservation, late save refused and ordinary draft intact. Actual 5.20 |
| E5-RESP-01 response/current allocation | Actual positive/current employee response, zero closure without consent, later notice-only and concurrent/stale outcome compared to response/history/ledger. Actual 5.12/5.13/5.15 plus B |
| E5-WRITER-01 changed local dependencies | Real calendar/profile/policy/assignment/date-capacity writers cannot slip between protected read and commit; actual affected-set membership changes covered. Each actual local source family/core protocol |
| E5-WRITER-02 changed People source | Actual prepare/source/Leave-consequence order, old-read race, unknown/late cancelled attempt and due boundary respect current authority. People and actual 5.15-K/5.24 consumers |
| E5-AUTH-01 changed access/domain authority | Current revocation/new execution and bounded in-flight ordering, unavailable versus denied, expired/changed assignment independent of permission. Access and actual commands |
| E5-OBS-01 usable measurement under concurrent change | Real route/phase/counter evidence, no payload/identity cardinality leakage, bounded exporter and unrelated request responsiveness. Existing observability owner plus actual core/source consumers |

No planned case replaces its owner's failing-first acceptance or establishes all source
variants. 5.32 links these real owner cases and adds only missing composition evidence.
Remaining concrete design includes state/target DDL and write permissions, exact initial
pending result mapping, actual lock/reference/fence protocol, typed payload/error details,
execution budgets and consumer-specific scenario/source mapping. No further story or new
product decision follows from this allocation; final sizing/readiness remain open.


## Minimum request read and recovery wire baseline — 2026-10-23

**Technical baseline for 5.10-A and its first consumers; not a completed OpenAPI schema.**
Reuse E1's authenticated `/api/v1/organizations/{org_id}` prefix and existing
`GET /operations/{operation_id}`. The verified path organization must match current
admission and permitted resource scope; it is not trusted merely because the client
selected it. Add `GET /requests/{request_id}` for minimum authorized current detail.
Do not add a second request-operation lookup, a mutation on GET or early endpoints
for later history/calendar/queue features. Both reads are private and no-store.

### Current request response: required common fragment

| Field | Wire representation / meaning |
| --- | --- |
| `request_id` | UUID of the actual stable request, not a draft or operation ID |
| `current_cycle_id` | UUID of its current submitted cycle; no synthetic cycle for unsent corrections |
| `revision` | Positive decimal-string bigint request review revision; opaque optimistic concurrency value, not a timestamp |
| `status` | Actual current lifecycle discriminator from the bound request state model; `committed` is never a request lifecycle value |

Read this fragment and its permitted detail from one consistent committed local view.
Actual submitted dates/duration/type, current allocation and other presentation fields
are typed extensions bound by their first consuming story to E3/E5 owner contracts;
this fragment alone is not a sufficient leave-details screen or finalization input.
The initial submitted/in_approval transition remains a submission-contract decision;
no new status or inferred final outcome is introduced here.

Use one allowlisted response model per supported audience projection. Own detail shows
the employee's approved product detail and concise current required action; it does not
expose internal approver absence, workflow diagnosis or temporary-coverage reasoning.
Assigned-approver and manager detail require their current domain scope and reveal only
the fields needed by that authorized surface. A client-supplied role/projection value
cannot obtain additional fields. Formal decision history is the later 5.30-A extension,
not a second implementation inside the core. Document readiness may be projected safely;
medical metadata/bytes still need the separate permission and E4-owned routes.

### Original committed request result

Preserve E1's outer union exactly: HTTP 200 with `operation_id`, `status: committed`
and typed `result`, or authorized lookup with exactly `operation_id` and
`status: unresolved`. Preserve the existing draft result branch without renaming its
fields or command values. Add request-target result branches with the required fragment:

| Result field | Wire representation / meaning |
| --- | --- |
| `command` | Versioned contract's closed command discriminator; each real consumer binds its actual value and allowed result shape |
| `request_id` | Original affected request UUID |
| `cycle_id` | Cycle affected by that original command, even after a later resubmission |
| `revision` | Request review revision at that command's commit, not the latest read |
| `request_status` | Actual request lifecycle at that commit, distinct from outer `committed` |

Command-specific disposition/decision references are added only where the actual action
needs them. Do not put employee input, reasons, allocation snapshots, document metadata,
full workflow details or current authorization claims in the compact receipt. A source
command affecting many requests retains its source-target acknowledgement; it does not
serialize this fragment once per request into an unbounded outcome.

For example, an original decision result can identify revision `7` and a pending status,
while a separate current read shows revision `9` and Approved. Both are truthful. Retry
must not overwrite the receipt with revision `9`, repeat the decision or automatically
confirm a new action. If the original result is known but current detail cannot load,
retain the confirmed outcome and retry the read only. Current authorization is required
for recovery; a previously valid receipt is not ongoing permission to read its target.

### Error and recovery binding

Reuse the shared machine-readable envelope and its authentication, access, not-found,
payload-mismatch, busy, validation and dependency identifiers. Add request optimistic
conflict HTTP 409 / `leave.request_revision_conflict` with only
`details: {current_revision}` (positive decimal string), after current resource access
is established. Never return someone else's values or silently substitute that revision
into the user's confirmation. Exact command-specific changed-input/gate errors remain
with their consuming command and safe typed detail schema.

An inaccessible/missing request uses the established non-disclosing resource error;
failed authorization verification remains `authorization_unavailable`, not empty data
or a fabricated denial. A timeout/500/busy response or unresolved lookup cannot prove
that mutation failed. Retain the original operation and frozen command input; use the
bounded original-operation recovery contract. No new operation ID, advanced expected
revision or automatic resubmission follows from an uncertain response.

### Verification allocation and remaining wire work

5.10-A owns planned E5-STATE-03 plus current-authority and projection contract cases:
original result versus later current state, unchanged E1 draft branch, unknown outcome,
no cross-organization enumeration, sensitive-field absence and no read-side mutation.
Actual command stories own their closed discriminator, input/result/validation schemas
and real commit/retry integration. Backend OpenAPI, generated frontend union types,
localized error handling and fixture assertions must agree; no generated files are
hand-edited. No runtime tests or schema generation occurred in this planning pass.

This binds the common route, identity/counter representation, original/current result
separation and one safe conflict shape. Full field schemas, concrete receipt/target DDL,
command catalog, disclosure fixtures, execution budgets and source coordination still
need binding before sizing/readiness. No new story boundary or product rule is added.


## Receipt target constraints and first request-command branches — 2026-10-23

**Concrete design baseline for validation, not applied DDL or proof of compatibility.**
Keep one Leave-owned `operation_receipt` and its primary key
`(org_id, actor_id, operation_id)`. Keep E1's existing fields, immutable creation
attribution, digest/version support and runtime select/insert-only policy. Extend with
an explicit `target_kind` discriminator and nullable `request_id`; permit nullable
`draft_id` only under the following checked union. Keep `employment_id` non-null for
both branches. Never change old draft fingerprint bytes or reinterpret old results.

| Receipt target branch | Required database shape |
| --- | --- |
| `draft` | `draft_id IS NOT NULL`, `request_id IS NULL`; existing composite FK `(org_id, employment_id, draft_id)` remains enforced |
| `request` | `request_id IS NOT NULL`, `draft_id IS NULL`; composite FK `(org_id, employment_id, request_id)` references the actual local request's unique scoped key |

Use explicit non-null discriminator/check predicates so SQL NULL cannot bypass the
union. Restrict target deletion; never cascade retained receipts away. Organization,
actor, employment, command/version, target, digest and result remain immutable after
insert. A scoped FK prevents wrong-organization/employment linkage but does not grant
that actor authority: API checks and restricted database access remain necessary.

The command/target allowlist initially preserves `start`/`save`/`discard` as draft-only
and adds `approve`/`reject`/`withdraw` as request-only, each request command version 1.
Do not make every command legal on every branch. Submission, resubmission, employee
response and source-change commands extend the closed allowlist in their actual
consuming item, with their own explicit target/effect contracts. No unused command
handler is part of 5.10-A merely to demonstrate a discriminator.

For a request branch, existing `committed_revision` denotes the original request review
revision and must agree with its typed compact result. For existing draft branches it
continues to denote the original draft revision. Positive bigint checks remain. Source
writers with their own primary entities still need explicit scoped target branches;
these two shapes do not authorize arbitrary source IDs in a request/draft FK.

### First real request results and input comparison

Bind 5.18-A `approve`/`reject` and 5.19-A `withdraw` to the preceding common compact
result fields: `command`, `request_id`, `cycle_id`, `revision`, `request_status`.
`approve` may leave the request pending or complete it through 5.10-B; outer committed
means the decision committed, not necessarily that leave is Approved. `reject` and
`withdraw` identify their respective closed lifecycle outcomes. Use actual persisted
lifecycle codes from the bound state schema, not a second set of display labels.
The immutable actual decision is independently available through its authorized domain
read/history; the recovery result need not duplicate decision comments or workflow state.

For those request commands, use purpose `leave.request.command`, command version 1
and E1's `sha256-jcs-v1` digest/canonicalization mechanics. The canonical envelope
contains explicit organization/actor/employment/operation identity, command/version,
request/cycle identity, submitted expected request revision and the full validated
command input, including any submitted step identities/revisions or reason/comment.
Each real command's schema specifies null versus empty/omitted values and field limits;
this list does not invent optional fields or permit undeclared input. Include submitted
review evidence when it is part of the actual command, but exclude newly observed
server facts, calculated allocation, authorization times and generated decision IDs.
Backend comparison, not a client digest, decides an identical retry.

Resolved persistence targets and original command input are distinct. E1 start already
fingerprints a null input target but stores the created/resumed draft. Similarly, a later
create/submission command may fingerprint a draft or explicit create intent and store
its actual committed target/result. Never recompute the original input digest from a
newly generated request ID or latest state. The submission item must bind draft closure,
created request linkage and both relevant revisions without changing the meaning of
E1's draft revision field. That cross-link schema is still open, not hidden in JSON
without required structural protection.

### Compatible migration and evidence responsibilities

Use a controlled expand migration before new API activation: add the discriminator with
the draft default/backfill for existing rows, add nullable request target and scoped FK,
then replace the old unconditional draft-not-null/command restriction with the explicit
checked union/allowlist. Preserve old E1 columns and result payloads so the previous API
can still insert/read draft receipts. The old E1 lookup contract must handle the expanded
result union compatibly before any producer writes request results: coordinate that
consumer change or keep request-command activation disabled. A database-expand migration
alone cannot prove old binary/response-validator compatibility. No startup migrations,
receipt rewrites, dropped immutable evidence or automatic down migration after failure.

5.10-A owns structural target-union/reference/immutability and migration compatibility
fixtures; actual 5.18-A/5.19-A own real command result/digest/commit integration. Planned
cases include invalid both/neither targets, cross-employment target, command/target mismatch,
old E1 insert and lookup, changed-input replay, request revision changed after original
commit and injected rollback. Verify under actual restricted roles; test-only seeded
request records establish core behavior without fake business handlers. SQL constraint
names, enum-versus-check migration implementation, request/cycle/result linkage enforcement,
all new producer schemas and concrete rollout evidence remain delivery gates.

No new product permission, workflow step, service, table family or story split follows.
Scaffold impact is the existing proven owner-local recovery adapter plus typed result
extension; shared UI needs no new surface. Agent context/accepted ADRs are unchanged;
this owning contract and BMAD checkpoint carry the documentation refinement. No runtime
code, migration or tests were executed.


## Own submission closure, linkage and revision baseline — 2026-10-23

**Technical refinement of approved 5.11-A; E1's agreed retention remains binding.**
Use `POST /api/v1/organizations/{org_id}/drafts/{draft_id}/submit` with UUID
`operation_id`, positive decimal-string `expected_revision` for the saved draft,
and the command's typed `review` evidence. The employee is derived from current
caller/employment ownership. Do not accept another employee ID or a second full form
payload as an alternate submission source. Persist outstanding edits first, review that
saved revision, then submit it. Exact review consequence/acknowledgement fields and
freshness protocol remain to be bound; a draft revision alone is not sufficient evidence
of unchanged funding, route, coverage or external inputs.

Under actual current-input coordination, verify the saved draft revision and editability
together, and read its persisted input. Create the actual request/cycle/steps, accepted
own decisions and reservation or immediate finalization effects; close the draft and
store one original outcome in the same local transaction. E4 continues to own document
association mechanisms; use its actual continuity contract rather than duplicating it.
No success is returned before commit and no HTTP wait is held under business locks.

### Closed draft structure and invariants

Add `submitted` to the E1 lifecycle only with this consumer. Extend `leave.draft` with
nullable `submitted_request_id` and `submitted_cycle_id`, constrained as follows:

| Lifecycle | Payload / closure / submitted linkage |
| --- | --- |
| `active` | Existing versioned input present; closure fields and both submitted IDs NULL |
| `discarded` | SQL NULL editable input; closure actor/time present; both submitted IDs NULL |
| `submitted` | SQL NULL editable input; closure actor/time and both submitted IDs non-null |

Use composite FK `(org_id, employment_id, submitted_request_id)` to the actual local
request, plus `(org_id, submitted_request_id, submitted_cycle_id)` to its actual cycle's
scoped unique key. Restrict deletion. A partial unique key on `(org_id, submitted_request_id)`
for submitted rows prevents multiple ordinary drafts claiming the same initial request.
This does not require every request to have a draft: on-behalf creation is separate.
Retain the compact closed draft under the agreed E1 policy. Neither submission nor later
correction/resubmission can reopen it or restore its removed editable payload.

The two links identify the original request and initial cycle permanently. A later
rejected-request resubmission changes the request's current cycle, not the closed draft's
original link. Actual draft writes must enforce immutable submitted linkage; a foreign
key alone does not prevent a valid but incorrect relink. Do not add a reverse request-to-
draft FK or require a synthetic draft for on-behalf requests merely to make this relation
bidirectional. Exact constraints/owned write paths must prove valid insert order without
disabling integrity for runtime callers.

### Distinct counters and submission result

Successful submission advances the existing draft revision exactly once and its employee
scope generation exactly once, closes the draft, and frees the one-active-draft scope.
The newly created request starts at review revision `1`; initial steps/own decisions and
immediate all-gate completion are part of that one creation command, not extra fictitious
request revisions. The first cycle's identity is independent of these counters. Subsequent
accepted request commands use the existing once-per-command revision rule. Replay advances
none of them. Counters remain bigint decimal strings on the wire.

Add `submit` version 1 as a **draft-target** receipt command. Keep `committed_revision`
as the closed draft revision, preserving the meaning of that column for draft targets.
Its compact typed `result` contains exactly:

| Field | Meaning |
| --- | --- |
| `command` | `submit` |
| `draft_id`, `revision`, `scope_generation` | Original draft and its closed revision / resulting scope generation |
| `request_id`, `cycle_id` | Actual original request and initial cycle |
| `request_revision`, `request_status` | Request's revision and actual lifecycle at this submission commit |

This is an explicit submission branch, not the request-target result fragment whose
`revision` denotes a request revision. Generated unions must discriminate correctly.
Use the existing draft-command fingerprint purpose with new command version/allowlist
support; canonical input includes original draft identity, submitted expected revision
and complete validated `review` evidence. Do not inject the generated request/cycle IDs,
current calculation or later draft values into the original input digest. Store the
committed linkage on the closed draft and enforce result/link/revision agreement through
the protected receipt-insert path; mere JSON presence is not referential integrity.

### Duplicate, late-save and recovery behavior

A matching committed operation returns that original result after current permitted
outcome checks, before testing whether the draft is now closed. A different operation
against the submitted draft cannot create another request: use existing authorized
`leave.draft_submitted` recovery with `request_id` only after verifying current access to
the linked request. It must not masquerade as that different operation having committed.
Late save/discard, concurrent submission and delayed start retain E1's lifecycle/revision/
scope guards. No stale input can replace submitted values or be copied to a new draft.
A newly requested draft requires an explicit new start action with current scope state.

For a lost response, Retry resolves the original operation and navigates to its actual
request. If request detail is temporarily unavailable after confirmed commit, retry only
the detail read. Later cycle/status changes remain visible through current request read;
the original receipt and submitted draft link are not rewritten. Unknown outcome retains
the original frozen command and operation under L-0148; absence of a receipt alone does
not establish failure. Initial own unpaid acknowledgement still must match exact current
consequences on any execution that has not already committed.

### Evidence and remaining bindings

5.11-A owns actual submission atomicity and linkage tests: successful pending/immediate
completion, induced rollback, one request from competing submissions, once-only counters,
submitted versus discarded shape, invalid cross-scope/cycle references, immutable original
link after real resubmission, late save/start and commit-then-lost-response recovery.
Use actual E1/core/E3/E4 consumers; 5.32-L adds missing browser composition only. Do not
implement a second receipt or bypass real source-writer coordination to pass fixtures.

This binds submission identity, draft lifecycle, reference structure and distinct result
counters. Exact `review` schema/current-input protocol, initial pending lifecycle code,
protected global lock order, receipt insertion enforcement and rollout/SQL evidence remain
open before sizing/readiness. Scaffold reuses draft lifecycle/recovery and current typed
API generation; no new shared UI surface, agent-context rule or ADR change is introduced.
No code, migration, runtime test or implementation authorization follows.


## Reviewed consequence comparison for own submission — 2026-10-23

**Technical allocation of Features' existing current-input confirmation rule and L-0069;
no new approval round or stored review workflow.**
Use an allowlisted, versioned summary comparison inside the already defined `review`
command input. The browser echoes the normalized consequences displayed by the backend's
existing calculation/preview consumer. At submission the backend independently reloads,
recalculates and compares the current protected result; client values never determine
eligibility, accounting or authority. This needs neither a new review-record table nor
a signed preview token/key lifecycle. It is evidence of the submitted confirmation,
not proof of what a human actually read.

### Review input and comparison ownership

| Field | Binding |
| --- | --- |
| `schema_version` | Closed review schema version `1`; unknown versions fail validation |
| `summary` | Typed normalized own-submission summary: selected type, interpreted requested dates/mode, calculated duration and applicable paid/unpaid consequences. Bind exact units/amount/date representations to the existing E3 calculation contract, not a second calculator or localized display text |
| `unpaid_acknowledgement` | Null when none is required; otherwise a typed exact amount/unit matching the current requested unpaid consequence under L-0069. It cannot stand for approval or exceptional-funding authority |

The actual generated model must close the summary/amount unions, reject unknown fields
and distinguish untracked policies without invented entitlement amounts. Do not use
arbitrary JSON, floats or translated labels for comparison. E3 owns normalized funding
and duration representations; final field/schema binding remains explicit work there.
The saved draft revision protects the source input (including note/type/mode/date edits).
Summary equality alone cannot permit submission of a different saved revision.

Use the same pure projection of calculated results for preview and protected confirmation,
with an explicit field comparator. Compare the consequences shown for confirmation,
including applicable date-specific allocation when presented, not entire calculation
snapshots, balances or internal routing observations. A changed total duration, paid/unpaid
consequence or another consequential reviewed detail requires renewed confirmation.
Newly invalid input or failed eligibility follows the corresponding validation/gate error;
it is not accepted merely because summary fields match.

Changed source revision/time, internal eligible approver assignment or an entitlement
source selection with no changed consequential reviewed detail need not cause renewed
review. Current authority, date-by-date funding and all independent gates still pass.
Never include approver absence, medical metadata or private coverage reasoning in the
employee summary just to make change detection easier. There is no preview age alone
that grants validity or forces a new confirmation: protected current checks decide.

### Changed review and retry behavior

After current access/resource checks, a valid new execution with changed consequential
review returns HTTP 409 / `leave.submission_review_changed`, with safe typed detail
`{draft_id, current_revision}`. It commits no request, draft closure, reservation or
successful receipt. The client preserves the draft, refreshes its current summary and
clears any acknowledgement that no longer matches. Show the revised existing summary;
the employee explicitly submits it again. Do not add a technical error/status screen,
submit changed consequences automatically or treat the first click as blanket consent.

A revised confirmation uses a new operation ID because its reviewed input changed.
This is allowed only after the previous action is definitively rejected/uncommitted;
unknown outcomes retain the original frozen input and operation under L-0148. A matching
committed retry resolves the receipt before performing a new comparison: later policy or
balance changes cannot turn its original successful submission into a new review error.
This preserves the distinction between retrying an original action and confirming a new
reviewed action. Backend coordination must make the no-commit conflict versus concurrent
commit ordering truthful; a missing receipt lookup alone cannot establish that ordering.

5.11-A owns backend acceptance evidence: changed duration, paid/unpaid amount, changed
nonconsequential source revision, saved-draft conflict, invalid current gate, stale unpaid
acknowledgement, commit-then-lost-response and changed-input operation mismatch. 5.11-B
owns refresh/preserved input/cleared stale acknowledgement and explicit new confirmation
without duplicate creation. E3 owns calculation/projection correctness; 5.32 references
those cases and adds only missing composition proof.

Scaffold/shared UI reuse versioned typed errors and the existing summary/confirmation;
Leave owns consequence fields. Existing agent and accepted ADR rules suffice. Exact E3
summary/amount schemas, comparator fixture table, protected writer order and recovery
execution budgets remain open before readiness; no code or tests were run. No story
boundary or product policy changes in this pass.


## Local lock ordering and duplicate coordination baseline — 2026-10-23

**Refines the approved narrow local coordination direction; actual writer mapping and
concurrency proof remain open.** Use persistent Leave-local guard rows with verified
organization scope and stable typed dependency identities. Read dependencies with row
`FOR SHARE`; a relevant source/reference change takes `FOR UPDATE` on that dependency's
guard. Employee mutation guards use `FOR UPDATE` across leave types. Do not substitute
`FOR KEY SHARE` for protection against non-key source changes. PostgreSQL documents the
row-mode conflicts and recommends consistent acquisition order and strongest required
mode first: [PostgreSQL 17 explicit locking](https://www.postgresql.org/docs/17/explicit-locking.html).
This is design reference, not verification of installed runtime/database behavior.

### Global phase order

| Phase | Required order and behavior |
| --- | --- |
| 0: preparation | Current external checks and candidate dependency/employee discovery outside business locks; no authority from client-selected guard IDs |
| 1: draft scope if needed | Existing E1 `draft_scope FOR UPDATE`, sorted by scoped employment UUID if more than one; only workflows actually touching that draft lifecycle take it |
| 2: local dependencies | Complete candidate guard set ordered by closed dependency-kind ordinal then UUID bytes within the verified organization; strongest required shared/exclusive mode selected before acquisition |
| 3: employee mutations | Complete affected employee guard set ordered by employment UUID bytes, exclusively across leave types |
| 4: actual domain rows | Reload/revalidate, then lock/update actual request/cycle/step/accounting/source rows using one declared table/key order; receipt and required effects commit together |

Every command follows the phases it needs, never acquiring an earlier-phase guard after
a later one. Submission takes draft scope before dependencies/employees; an E1 save keeps
its existing draft-scope-only protocol and does not acquire business eligibility guards.
A source writer cannot decide late to edit a draft while holding business locks. 5.10-B
runs within the caller's complete protected set, not by starting a nested independent
transaction or taking an undeclared new guard. No same-object shared-to-exclusive upgrade;
if the stronger need or another identity is discovered, roll back and restart discovery.

The dependency-kind registry, guard creation owner and actual domain-table/key order must
be enumerated from real E2/E3/E5 writers before protocol completion. Guard existence is
not authority and guards cannot be dropped while live references can use them. Missing
required guard protection fails/restarts through the defined owner path; selecting zero
rows is never equivalent to acquiring a lock on an absent default/reference slot.
An empty organization-default slot needs its own narrowly scoped setting identity, not
an organization-wide lock covering unrelated settings or employees.

### Dynamic references and affected membership

Reference creation, removal and reassignment take shared protection on every relevant
old/new dependency guard, plus the affected employee guard. Source mutation takes exclusive
protection on the source guard. Once that exclusive protection is held, re-enumerate its
current affected references/requests; concurrent new attachment to that source cannot pass
its own shared guard. This includes indirect references such as default-profile followers,
not only rows with a directly stored profile ID.

After the entire planned set is acquired, reload actual references, affected membership,
revisions and mutable inputs. A changed set requiring any additional dependency or employee
causes whole-transaction rollback/restart with fresh discovery. No late unordered guard,
partial affected-set processing or silently omitted new member. Repeat only within the
single total execution budget; contention/dynamic churn must eventually return existing
busy/Retry behavior. All relevant reference writers must participate; a guard row cannot
protect a bypassing writer or prove cross-employee coverage by itself.

### Duplicate protection without another operation-lock facility

Keep the existing receipt unique key and owning mutation scope protection. For a matching
command, the same target employee/draft guards serialize the execution; recheck the receipt
under that protection before applying any new effects or rejecting stale lifecycle/revision.
An optional earlier authorized receipt read may fast-return immutable success, but absence
outside the protected path never authorizes duplicate execution. E1's receipt-under-draft-
scope behavior is preserved; request commands use their protected employee boundary.

A changed-command/target operation reuse can reach a different scope. The receipt unique
constraint remains the cross-scope backstop: the losing transaction rolls back *all* local
effects. Only after rollback, inspect the original receipt through current permitted scope
and canonical-input comparison; return mismatch without exposing the other target. An
unresolved unique collision/lock timeout is not committed success. Do not catch an integrity
error inside a failed transaction and continue business writes or blindly return the winner.
No new advisory operation lock, lock table per operation or central outcome service is needed.

Keep current authorization checks before protected new execution; matching receipts do
not bypass current permitted outcome access. E1's known execution budgets remain draft-only;
E5 numerical phase/transaction/restart budgets still need binding to actual workload and
1,000-employee validation. Configure bounded waits/statement execution and rollback cleanup;
no HTTP retry, delivery or user review occurs while the transaction holds these guards.

### Evidence and completion limits

Extend planned E5-WRITER-01/LIFE-01/STATE-03 with real concurrent traces: save versus submit,
submit versus changed default/reference membership, source change versus new association,
two same-day/funding mutations, identical operation against one target, changed-target
operation collision and rollback, uncovered cross-employee absence dependency, and guard-
set restart exhaustion. Measure guard/transaction phases under E5-OBS-01. Actual source
owners prove their writer and reference paths; 5.32 references existing evidence.

This selects phase order, row modes, membership re-enumeration and duplicate backstop
without changing E1's lock semantics. Concrete guard DDL/closed kind catalogue, exhaustive
writer/reference mapping, domain-row order, cancellation/budget values and measured
concurrency evidence remain required before claiming readiness or final agent sizing.
No implementation, new user flow, shared service or ADR amendment is introduced. Scaffold
may promote the proven transaction/retry primitives with first consumers; domain guard
identities stay Leave-owned. Existing shared UI and agent context remain sufficient.


## Initial submission dependency and reference-writer register — 2026-10-23

**Concrete identity/owner allocation, not proof every source path participates.**
The following closed dependency kinds supply the phase-2 registry in ordinal order.
Use `(org_id, kind, subject_id)` as the stable local guard identity; subject IDs below
are verified source identities, not arbitrary client inputs. Guard rows survive changes
between an empty and populated setting. Existing employee coordination is phase 3 and
is distinct from these dependency guards. Application-local guard facts do not copy or
lock another service's source tables.

| Kind / subject identity | Protected facts and reference membership | Actual participating writers / evidence owners |
| --- | --- | --- |
| 01 `leave_type` / type UUID | Current type admission, permitted modes and policy selection references; preserved submitted type evidence remains separate | E3 3.1/3.37/3.38/3.39, actual policy-assignment writers and new submission/resubmission |
| 02 `policy` / policy UUID | Used policy publication, scheduled version changes and associated employee/type selection | 3.34/3.35 through 5.15-E/G; actual first policy creation and assignment paths |
| 03 `employee_policy` / employment UUID | Employee's complete policy assignment/override timeline, including an initially empty assignment set | 3.28 initial assignment, 3.36 through 5.15-I, recurring overrides 3.30 through 5.15-C; effective-date owner processing when it mutates this source |
| 04 `employee_work` / employment UUID | Explicit/default profile selection and override timeline, including reset to inheritance | 2.20/2.22 through 5.15-O/M; new/replacement assignments protect old/new referenced dependencies |
| 05 `default_profile` / organization UUID | Default selection and membership of employees relying on it, including empty default slot | 2.21 through 5.15-Q and every employee explicit/default selection/reset writer; one setting guard, not a global organization lock |
| 06 `work_profile` / profile UUID | Calculation version and explicit/default/future holders; immutable historical versions stay readable | 2.19/2.23/2.24 and 5.15-S plus 2.20/2.21 reference writers; unused create/archive owners prove their no-holder preconditions |
| 07 `calendar` / calendar UUID | Holiday/full/partial closure calculation and employee/profile/default references to that calendar | 2.18 through 5.15-U plus actual work-setting/profile/default reference writers; protect absence of an entry using the calendar identity, not a nonexistent date row |
| 08 `approval_configuration` / actual owning configuration UUID | Ordered responsibilities, configured final approver and fallback/self/distinct-person settings | Actual policy/approval-setting publisher and route-reference writers; if policy owns the same configuration row, use its 02 guard instead of adding a duplicate lock identity |
| 09 `approval_subject` / employment UUID | Leave-local absence/appointment/responsibility/unfinished assignment inputs relevant to that person's coverage and route | Actual request lifecycle writers 5.11/12/18/19/20, appointment 5.21/22/23, transfer 5.24, return 5.25 and exception 5.5 where their mutation changes those facts |

The phase-3 employee guard protects same-date capacity, allocation/reservation/ledger and
current request state across leave types. Actual 5.13 and 5.15-A balance adjustments,
E3 earning/expiry/carry-over mutation owners and all request accounting writers share that
boundary; no second per-leave-type employee lock substitutes for it. Current date-dependent
calculation is still required even if no worker or administrator has written a new row.

### Reference membership rules for the register

Readers take shared protection on relevant dependency guards. A writer of that dependency's
facts takes exclusive protection; a reference writer also protects every old/new referenced
dependency before changing membership. In particular, employee-policy/work timeline changes
are exclusive on their employee-specific dependency identity, and shared on the old/new
policy/profile/default/calendar identities whose membership changes. A source publisher's
exclusive source guard then prevents a new holder entering unnoticed during re-enumeration.
The earlier general shared reference rule does not make mutation of the employee-specific
selection timeline a shared read.

A source and employee selection may both change: declare all necessary identities and
strongest modes up front. If references resolve to a different profile/calendar/policy or
employee set after protection, restart the whole protected execution. The same applies to
cross-employee approval-subject dependencies; deduplicate overlapping identities and choose
exclusive mode wherever the command changes a fact another finalization reads. Do not lock
only the applicant and assume other people's absence/appointment facts are stable.

Configured responsibility membership includes future work that may arrive, not merely
existing pending steps. A People supervisor change that alters those responsibilities must
update the relevant Leave projection/gate under the approved prepared-change protocol.
The exact People-to-Leave affected-subject discovery/fence is an external coordination
binding; this local register alone does not solve that boundary. Applicant coverage can
remain incomplete on submission and block finalization, as already approved in 5.3.

### Other-owner inputs and remaining reachability decisions

| Input | Owning protection / concrete outstanding binding |
| --- | --- |
| Employment periods, initial employment and rehire | People current-input/prepared-change protocol; 5.15-K covers employment end, not automatic proof of period creation/rehire participation. 2.11 proves genuinely new identity; 2.13 needs positive reachable period-addition evidence |
| Supervisor relationships and effective changes | People plus actual 5.24-C/E preparation/consequence/fence; no local guard can preserve stale authority while source changes are undisclosed |
| Admission, membership, grants and app availability | Access bounded in-flight/current-check contract; employment/guard existence never grants rights |
| Document identity, readiness and associations | E4-owned actual contracts and 5.9 producer/finalizer composition; no repeated Content mechanism or local cross-owner lock |

Actual 3.28 initial policy assignment and 2.13 rehire remain explicit positive-integration
obligations. Bind them into their source owners and the existing protected integration
where behavior fits; do not label them covered merely because change/end writers exist,
or add new boundaries before reachable effects and size justify one. Department/location
facts remain descriptive/grouping inputs unless an accepted rule actually consumes them;
do not automatically expand this into policy/profile authorization.

### Completion evidence and impacts

The register gives concrete guard identities and accountable source families for planned
E5-WRITER-01/02. Remaining protocol work is physical guard schema/creation lifecycle,
exact publisher/selection paths, approval configuration's actual owner key, indirect
membership queries/indexes, domain-row order and external prepare/fence payloads. Each
real source tests its own new/changed/removed references and bypass paths; no runtime
coverage PASS follows from a table entry. Final allocation includes every source variant,
not only one representative successful change per kind.

No new product decision or story boundary. Generic guard/transaction helpers are scaffold
candidates only after actual consumer proof; the dependency taxonomy is Leave-specific.
No shared UI/agent-context/ADR change is needed. This contract is the owning technical
register; epics and checkpoint link it rather than duplicate its full catalogue. No code,
SQL migrations, tests or benchmark ran; coverage, sizing and readiness remain open.


## Guard storage, creation and retention baseline — 2026-10-23

**Physical design baseline for the approved local protocol; not applied SQL.**
Use one small Leave-owned `leave.coordination_guard` relation for both the registered
dependency guards and the phase-3 employee mutation guard. It contains no source payload,
copy of employment facts, lease, worker claim, permission or review snapshot.

| Column / invariant | Concrete baseline |
| --- | --- |
| `org_id` | Verified organization UUID, non-null |
| `kind` | Non-null closed discriminator for the nine registered dependency kinds plus `employee_mutation`; fixed ordinal mapping in the owning code/schema |
| `subject_id` | Non-null UUID interpreted only by that closed kind: the exact source/setting/employment identity in the preceding register |
| Primary key | `(org_id, kind, subject_id)`; no surrogate identity required for locking |
| Attribution | Immutable server creation actor UUID and UTC timestamp under platform ADR-0025; no update fields because the guard row itself never changes |
| Scope safety | For organization-default setting identity, require `subject_id = org_id`; no arbitrary names, client-selected lock namespaces or cross-owner foreign keys |

Its subject is a coordination identity, not a generic business-record reference or receipt
target. Actual source records retain their real scoped references/constraints. A guard
cannot prove that its subject exists, is eligible or belongs to an authorized employee;
only verified owning-source resolution can establish those facts. Do not infer authority
from a successful lock or guard lookup. One relation avoids separate guard tables for each
kind and an unnecessary per-operation guard store.

### Creation before use

Local source creation creates its guard in the same local commit before that source can
be referenced by another command. Existing source rows receive guards in the controlled
migration before the protected writers activate. Create the organization-default slot
when that setting scope is initialized, even when no default is selected. Its identity
persists across setting/unsetting. Profile/calendar/policy publishers reuse their stable
identity guard across versions; do not create a fresh guard that old readers fail to lock.

Employee-scoped guards and other legitimately absent stable scopes may be ensured in a
short **separate preflight transaction**, after current verified scope/source resolution
and before acquiring any draft/dependency/employee business locks. Use idempotent insert
with primary-key conflict handling, then finish that transaction. This creates only empty
coordination identity, not an employee, draft, assignment, request or consequential result.
A later rejected business command may leave that harmless guard row. This is why creation
need not be coupled to successful submission or represented as an application operation.

Concurrent first creation must remain bounded by the total execution deadline; conflict
handling can wait on another insertion and must be measured. Never insert/ensure a guard
late while holding phase-2/3 business locks: an insert's unique-index wait would add an
undeclared acquisition order. After preflight, acquire the existing rows in the established
phase order and require every planned guard to be returned. Missing guard rows fail safely
and restart the preflight path; locking an empty SELECT result is not protection.

The dependency and employee guards for an employee remain different rows: a policy
selection writer may need exclusive `employee_policy` while all same-day/accounting
mutations serialize on `employee_mutation`. Neither substitutes for the other. Preflight
may create only identities derived by the authorized workflow, not a caller-supplied bulk
list of arbitrary subjects. It creates no approval appointment or future source mutation.

### Access, retention and rollout

Enable/force organization RLS with transaction-local verified organization context and
use a non-owner runtime role without BYPASSRLS/migration privileges. Grant SELECT/INSERT
and the narrow column UPDATE privilege required for row-locking SELECT (on `subject_id`),
with organization-scoped SELECT/INSERT/UPDATE policies. Enforce an unconditional rejecting
UPDATE trigger on this immutable relation; deny DELETE and runtime trigger/DDL control.
The narrow privilege enables locking, not successful key updates, including no-op UPDATE.
PostgreSQL requires UPDATE privilege on at least one column for locking SELECTs: see
[SELECT privileges](https://www.postgresql.org/docs/17/sql-select.html). A SELECT/INSERT-only
grant would therefore be insufficient. Test actual lock success and attempted update
rejection under the same runtime role. Locking uses the existing row, not a touch/version
update. Server-managed creation attribution must reject caller-forged values through the
actual owned insert path. Employee-level domain authorization still belongs to the
protected API; tenant RLS is not sufficient by itself.

Retain guards while sources/references or supported delayed commands may use their identities.
No runtime cleanup, inactivity expiry or delete/recreate is selected. Archiving a work
profile or deactivating a type does not remove its guard; empty/default reset scopes keep
the same identity. Future organization erasure/retention needs an owner-controlled process
with references and delayed execution considered, not cascade cleanup from a source row.

A schema/backfill deployment alone is insufficient: all relevant writer/reference paths
must adopt the protocol before consequential consumers activate. Preserve E1's independent
lightweight draft writes and existing runtime release compatibility. Actual Alembic/SQL,
RLS/grant/attribution enforcement and deployment ordering remain delivery evidence under
platform ADR-0020; no migrations run during this planning.

### Focused evidence allocation and remaining protocol work

Core/first source consumers own restricted-role cases for: valid/invalid kind and setting
scope, duplicate first creation, wrong organization, missing preflight guard, immutable
row/key/attribution, archive retaining identity and shared-read versus exclusive-source
contention. Actual source reference tests prove zero-to-one holders and default reset
cannot escape the registered membership guard. Record phase timing and rollback/connection
cleanup, not sensitive source values. These are planned cases, not executed tests.

This closes the local guard physical shape and first-creation/empty-slot/retention choices
at design level. Exact source initialization paths, domain-row write order, numerical
budgets and measured concurrency remain open. People prepare/fence and Content/Access
protocols remain separately owned; this guard table does not resolve external freshness.
No new product rule, user screen, service or story split. Scaffold may reuse proven scoped
lock/preflight helpers; the registry stays Leave-owned. Existing shared UI/agent context and
accepted ADRs need no change. Final atomic coverage, sizing and readiness remain open.


## People cancellation-fence candidate allocation — 2026-10-23

The shared owner now carries the [source attempt/cancel fence candidate](../../../../../platform/docs/architecture/contracts/identity-access-employment-e1.md#consequential-people-change-attempts-and-cancellation-fence--e5-candidate-2026-10-23).
It proposes one immutable-input-bound People attempt with registered/committed/cancelled
state, atomic commit-versus-cancel, retained terminal identity and no gate release from
wall-clock expiry alone. Leave owns its separate preparation/consequence state and releases
only on authoritative cancellation or reconciled committed consequences. Delayed source
commit after cancellation cannot revive the attempt; late preparation reconciles against
that terminal state. No distributed transaction or another-owner rollback.

This refines the approved direction without claiming shared architecture acceptance.
Actual schemas/service authority/registration/affected subjects/future boundary protocol,
owner lock order, deadlines, adoption decision and real E5-WRITER-02 evidence remain open.
5.15-K/5.24 actual source producers consume the owning contract; no duplicate employee
master, operation service, story boundary or user cancellation workflow is added.


## Affected-source and future-boundary candidate allocation — 2026-10-23

The [shared owner candidate](../../../../../platform/docs/architecture/contracts/identity-access-employment-e1.md#affected-subjects-and-future-effective-observations--e5-candidate-2026-10-23)
now maps exact selected relationship scope to Leave's dynamically discovered unfinished
work/coverage subjects. Future changes install revision/effective-boundary evidence now,
release the technical gate after reconciliation, and do not activate future authority early.
Current consequential checks invalidate observations at known boundaries even if workers
lag; stale assignments cannot authorize a decision. Employment requested-date semantics
remain inclusive and separate from supervisor effective-instant normalization.

One material boundary remains explicitly proposed: use the protected final authorization
check as the action's authorization instant and allow its short bounded transaction to
finish across an effective boundary. Any final check at/after the boundary needs new facts.
This People-domain in-flight rule is not inferred from Access and is not approved merely
by recording the candidate. Exact duration, timezone/source response, registration, source
scope discovery, shared adoption and actual race evidence remain open. Actual 5.15-K/5.24/
5.21–25 owners consume this candidate; no new story boundary or UI workflow is added.


## Supervisor-boundary authority rule accepted — 2026-10-23

User agreement resolves the preceding specific in-flight proposal under
[ADR-0163](../decisions/0163-protected-authority-check-at-supervisor-boundaries.md).
Use the final protected check as the authority instant; its short bounded transaction
may finish after a permanent-supervisor boundary when checked before it. Checks at/after
need new facts, worker lag gives no rights, and restarted execution rechecks. Existing
decision authority evidence records the evaluation instant/source basis. This is not
acceptance of the full People protocol or another authority's grace period.

Exact numerical bounds, effective-instant/timezone schemas, source preparation/fence,
service registration/authority and actual race evidence remain open. 5.18-A/5.24-C/E and
5.21–25 consumers bind actual decision/source/temporary interaction cases, with 5.32-J
referencing composition evidence. No new boundary, UI step or duplicate authority log.


## Restricted coordination caller allocation — 2026-10-23

The user clarified and agreed that Leave consumes People facts via authorized HTTP, never
People tables. The shared [caller-policy candidate](../../../../../platform/docs/architecture/contracts/identity-access-employment-e1.md#restricted-peopleleave-coordination-callers--e5-candidate-2026-10-23)
now allocates People-to-Leave prepare/notice and Leave-to-People fact/outcome/consumer-bound
cancel authority. Only People commits/cancels its source attempt; only Leave applies its
request consequences. Worker recovery cannot impersonate human approval or revive an
unauthorized source command. No new employee role, universal credential or runtime registry.
Deployment-owned caller admission and narrow pending-work recovery survive browser disable
without granting user access; exact activation/retirement handshake remains open.

Actual source/core/reconciliation consumers own positive and confused-deputy/revocation/
protocol tests under E5-WRITER-02/AUTH-01. Full route/schema/transport/budget/consumer lifecycle
and shared architecture adoption remain open before sizing/readiness. No implementation,
credentials/grants or story boundary changed.


## Access disable and source participation allocation — 2026-10-23

User agreement clarified organization-wide Leave enablement versus individual membership/
grants. The [shared participation baseline](../../../../../platform/docs/architecture/contracts/identity-access-employment-e1.md#leave-participation-across-access-disablere-enable--e5-baseline-2026-10-23)
keeps required source participation through Access disable/re-enable, resolves original
prepared/committed work under narrow recovery and gates unsafe consequential commands
without new user flows. No automatic retirement or new customer integration registry is
part of MVP; later technical decommission requires safe draining/fencing and compatibility.
Initial source-side cutover precedes baseline reconciliation and consequential admission;
the actual implementation/release cutover proof remains open. Access owns admission, People
facts and Leave consequences remain separate. Planned disable/adoption cases reference
real owner tests under E5-WRITER-02/AUTH-01; no new boundary or implementation.


## Remaining contract closure packages and sizing checkpoint — 2026-10-23

**Current closure register, superseding scattered historical next-step notes; not six new
stories or a competing delivery workflow.** Keep 78 approved suffixed boundaries and the
32 original scopes. Allocate the remaining design work to these existing owners; do not
restart product discussion or add speculative lifecycle/features to fill a contract gap.

| Package / owner | Bounded planning deliverable and closure condition | Existing delivery consumers |
| --- | --- | --- |
| C1 request state/recovery — Leave core plus E1 outcome owner | One record/column/key/index/immutability/runtime-role matrix for the four core state records, guard relation and receipt extension; closed minimum read/result/error schemas, original/current distinction and compatible activation. No future domain entities or fake mutation handlers | 5.10-A; actual producers prove their own insert/effect/linkage integration |
| C2 rule/finalization composition — Leave rule owners plus E3 | Bind 5.1–4/5.6–9 runtime responsibility to executable predecessors, exact current evidence/gate result types and E3 allocation/reservation/consume/release/evidence/intent interfaces; kernel atomic effects and numerical execution/recovery budgets. No duplicate calculator/ledger/Content mechanism | 5.10-B and actual decision/response/exception/submission/source resolvers |
| C3 local source participation — actual E2/E3/E5 writers | Register each real source/reference path against the closed dependency kinds, physical initialization and actual domain-row order; affected membership queries/indexes, new/removal/default/alternate writers and independent concurrency oracles. Resolve 3.28 initial assignment reachability positively | 5.15 local families, 5.13/5.18/5.19/5.20–25, type/profile/archive source owners |
| C4 People protocol — People owner plus Leave integration | Consolidate attempt/gate wire/storage states, prepare/outcome/cancel/consequence payloads, exact service policy/consumer cutover, source/boundary/timezone evidence and numerical recovery bounds; decide shared architecture adoption. Include 2.13 rehire reachability and L-0163 authority instant | 5.15-K, 5.24-C/E and employment/temporary authority consumers; no new human roles or source master |
| C5 actual command/browser schemas — each consuming story | Close its canonical input/result/validation union and review projection with E3 representations, actual target/linkage/initial pending code, explicit actor scope and browser recovery. Each command owns new data/effects only when consumed | 5.11/12/13/18/19/20 and later actual sources/appointment APIs plus their browser partners; 5.30 extends history once |
| C6 coverage/order/size — BMAD epic owner with source owners | Complete atomic original requirement/AC-to-consumer/planned-test mapping, real package/test-command strategy, external predecessor and executable foundation allocation, final topological order and per-boundary single-agent assessment. Link owner tests; 5.32 fills composition gaps only | Entire E5; final epic completion/readiness gates stay open |

A package is closed by a concrete reviewable contract/mapping, not a statement that an
owner will figure it out later. Changes to product/security/ownership policy return for
user discussion; routine technical choices within accepted constraints need no repeat
product approval. Shared protocol candidates are not converted to accepted architecture
merely by appearing in this register. Preserve accepted ADRs and scoped owner contracts.

### Planning versus delivery evidence

Do not create a circular gate that requires Leave implementation/tests before planning
can authorize implementation. At planning completion, contracts and ACs must specify the
actual acceptance oracles, predecessor mechanisms, relevant package/test locations and
verification commands or explicitly owned prerequisite tooling work. An absent planned
package is not permission to invent a working command or mark a scaffold available.

During authorized delivery, observe the acceptance failure before implementing behavior,
then run the actual restricted-role/concurrency/contract/browser evidence required by the
story. Required earlier owner implementations must be proven before a later dependent
consumer can pass. Benchmark results, migration execution and runtime PASS do not exist
from this planning session and are not manufactured as pre-planning achievements.

### Resumed sizing: current boundary assessment

| Boundary | Concrete envelope now visible | Current sizing disposition |
| --- | --- | --- |
| 5.10-A | Four core state records, one guard relation, compatible receipt extension, minimum current GET plus existing outcome GET and restricted structural/read fixtures | Retain provisionally; C1 schema/projection/compatibility detail is the immediate remaining size input. No accounting, submission/finalization/transfer implementation added |
| 5.10-B | Compose actual predecessor rules and E3 effects under protected current inputs; no new human decision or public completion endpoint | Retain provisionally; C2 executable foundation allocation/interface and budget closure required before single-agent judgment |
| 5.11-A | Actual saved-draft submission/closure/linkage/initial decisions and real predecessor composition; no second core, calculator or Content design | Integration risk remains; size against C1–5 closed interfaces, not by counting inherited rule paragraphs as new implementation |
| 5.12-A | Actual on-behalf creation and initial response consumer, reusing submission/core rules and L-0162 closure | Retain prior combined boundary pending exact actor/response schema and fixture count; two actors alone do not justify a split |
| 5.15-Q/S/U and 5.24-E | Existing synchronous-first local source impacts and per-item selected People changes | Actual affected-query/workload/budget or item outcomes determine size; no automatic worker/progress machinery or split from employee count alone |

No boundary receives a final sizing PASS in this checkpoint. C1 is the next closure item,
followed by C2; C3/C4 must become actual prerequisites rather than implicit future work.
After those contracts, finish C5/C6 and revisit only boundaries with concrete excess scope.
Do not multiply approved story counts with these technical packages or historical parents.
No implementation, tests, migration, provider change, credential/grant or deployment.


## C1 core column, constraint and read allocation — 2026-10-23

**Consolidated physical design for 5.10-A sizing; actual migrations/models remain delivery
work.** The following replaces open-ended model discovery for this boundary. It does not
create actual submission, approval, transfer or finalization handlers inside A.

### Core records and insertion order

All identities are UUIDs. Mutable rows have server creation/update actor IDs and UTC times;
immutable rows have creation attribution only. Organization/external actor/employment IDs
are verified references, not cross-owner foreign keys. Local E3 type/policy/evidence links
use the actual predecessor schema, never a parallel type or ledger table.

| Record | Required columns beyond attribution | Keys / structural constraints / indexes |
| --- | --- | --- |
| `request` | `id`, `org_id`, `employment_id`, `leave_type_id`, `current_cycle_id`, `status`, `revision` | PK id; unique `(org_id,employment_id,id)` and `(org_id,id)`; positive bigint revision; status closed to submitted/in_approval/approved/rejected/withdrawn/cancelled. No Draft request row. Scoped current-cycle FK described below; index `(org_id,employment_id,status,id)` for minimum own lookup/filter support |
| `request_cycle` | `id`, `org_id`, `request_id`, `sequence`, `submission_actor_id`, versioned immutable submitted-input/evidence envelope | PK id; unique `(org_id,request_id,id)` and `(org_id,request_id,sequence)`; positive bigint sequence; scoped FK to request. Envelope requires explicit supported version/object shape, not arbitrary source/ORM snapshot. E3 calculation evidence referenced rather than duplicated |
| `approval_step` | `id`, `org_id`, `request_id`, `cycle_id`, `position`, fixed responsibility definition, `status`, nullable current assignee actor/employment, current authority basis, `revision`, nullable `decision_id` | PK id; unique `(org_id,request_id,cycle_id,id)` and `(org_id,request_id,cycle_id,position)`; positive position/revision; scoped cycle FK and scoped decision FK; index `(org_id,current_assignee_actor_id,status,request_id)` supports actual assigned lookup. Assignee may be NULL for truthful pending attention; no invented user |
| `approval_decision` | `id`, `org_id`, `request_id`, `cycle_id`, actual deciding `actor_id`, approved/rejected outcome, nullable actual comment, operation identity, evaluated authority instant/basis, immutable covered-step identity evidence | PK id; unique `(org_id,request_id,cycle_id,id)`; scoped cycle FK; outcome/authority envelope has explicit version/type. All business evidence immutable; same-person permitted coverage is one decision, not duplicated comments |

Use approved step status codes pending/approved/rejected/skipped/delegated/cancelled;
representation does not authorize skipping required decisions or infer final approval.
Actual command rules decide allowed transitions and delegated/temporary applicability.
Immutable responsibility/position belongs to a cycle; current assignment/status/revision
is mutable only through owning protected command paths. Accepted decision binding is
write-once. Reject a cross-cycle/wrong-outcome binding and any attempted expansion of the
immutable decision's original covered step set through the enforced owner write path.

For the request/current-cycle cycle, select a non-null scoped FK
`(org_id,id,current_cycle_id)` -> `request_cycle(org_id,request_id,id)` that is deferrable
and initially deferred. Generate both IDs before insert; insert request then its cycle,
steps/decision evidence in the same local transaction. Cycle-to-request FK remains checked;
commit must fail if the head lacks its actual cycle. Normal read consumers never observe
a committed half-pair. Insert steps with no decision link, then immutable decisions, then
bind permitted covered steps in the same command. No globally disabled constraints,
nullable permanently orphaned head or separate setup commit is needed.

Actual command state changes share the approved once-per-command request review revision.
Immutable submitted evidence and earlier decisions never change. Rejected correction
input remains outside these records; a future supported resubmission uses a new cycle
without rewriting the old one. Enforce closed-state protection with that explicit exception,
not a generic terminal flag blocking accepted resubmission or an unrestricted reopening.
E6 may later bind cancelled transitions; A exposes no early cancellation command.

### Read contract and scope limits

A implements the common current-read fragment and existing outcome union already specified
above. Its current-request projection adds only the current submitted-input/evidence views
needed by the first real consumer; do not return the entire stored evidence envelope.
Use explicit allowlisted schemas and conditional permission checks. Core structural fixtures
can establish valid persisted data; they are not fake implementations of later commands.

| Audience | Required current access basis | A's minimum read ownership |
| --- | --- | --- |
| Own employee | `leave.request.own.read`, verified current org access and caller-to-employment ownership | Common identity/revision/status/current cycle and own submitted summary needed by 5.11; no current internal route/absence/cover diagnosis or unpermitted document metadata |
| Assigned approver | Actual registered assigned-request capability plus current scoped responsibility/assignment and current access | Same coherent head/cycle plus permitted actionable step identities/revisions and evidence for its actual consumer; capability catalog binding belongs to C2/C5 before that projection activates |
| Authorized administration | Actual scoped management/source capability plus domain resource checks | Minimum source-impact/request inspection fields for that real consumer; own-read or role label alone is insufficient |

The own branch is available with the already specified capability. Assigned/admin branches
must stay unavailable until their consuming capability and field schema are actually bound;
A does not create a wildcard permission, interpret role names or ship a permissive placeholder.
The core projection/query mechanism is shared; later consumers add only their required
closed fields/scope rules. Full comments/formal history/pagination/calendar queries remain
5.30/5.29; readable decision attribution required by earlier consumer is not a second
history query subsystem.

### Restricted writes, receipts and compatibility

Force org RLS and verified per-transaction context under non-owner runtime roles. Immutable
cycle/decision fields and receipt evidence reject update/delete through enforced triggers
or an equivalently protected owning write interface; runtime cannot disable safeguards.
Request/step creation identity, attribution and original responsibility cannot be rekeyed.
Current user domain access still comes from API/Access, not tenant context alone. Keep
named expected constraint collisions mapped to safe typed errors; unexpected integrity
errors roll back and disclose no SQL.

Guard relation shape/preflight/privilege enforcement follows its bound lifecycle above.
Receipt draft/request union, scoped keys and command branches follow their bound sections;
no new outcome schema is invented here. For A, adding supported type branches does not
activate later producer endpoints. Verify the existing draft operation result remains
unchanged. The shared lookup's generated result union and client handlers must be upgraded
before request producers activate; older runtime versions supported during a normal release
must tolerate new branches or new producers remain disabled until coordinated cutover.
No claim that adding nullable columns alone supplies wire compatibility.

### C1 closure and sizing result

The relation/key/index/read scope and insertion strategy are now bounded. **C1 is not fully
closed**: E3's exact versioned submitted/evidence references and first own-summary fields
must be bound, along with assigned/admin consumer capability schemas and concrete supported-
old-runtime lookup strategy. These are explicit interface/activation items, not permission
to invent source fields or declare compatibility. Actual constraint names/DDL and independent
role/race fixtures are implementation work against the selected design, not another product
review or an existing test PASS.

5.10-A remains **at risk for single-agent size**, with four state records, guard relation,
receipt migration and two read contracts. A split cannot be decided merely from table count;
first isolate which of those mechanisms E1/E3 already deliver and which A must implement.
Next sizing action: a reuse-versus-new allocation for A against actual predecessor artifacts,
then either a justified bounded fit or one concrete split proposal. Do not stamp size PASS
because public mutations and ledger are excluded. No new boundary is approved here.

Planned E5-STATE-01–04 plus actual receipt/guard fixtures own integrity, immutable evidence,
coherent reads, denied scope, original/current recovery and old-wire compatibility. Actual
producer stories own creating/transferring/resubmitting/deciding and complete atomic effects.
Scaffold/shared UI/agent context/ADR impacts remain as already recorded for A; this is its
owning contract refinement. No models, migrations, runtime tests or app implementation ran.


## C1 predecessor reuse assessment and proposed recovery split — 2026-10-23

**Sizing proposal for user agreement; 78 approved boundaries remain unchanged.**
Inspected current working-tree artifacts, including builder examples/evidence and actual
Leave file inventory. Leave still has no application package manifest/Python/SQL runtime
implementation. Do not count planned E1/E3 behavior as already delivered or assume scaffold
examples are promoted generated Leave mechanisms.

| Concern | Actual predecessor/source inspected | Reuse versus new E5 responsibility |
| --- | --- | --- |
| Draft operation identity/revision/fingerprint/outcome | E1 persistence contract, D1/D2-A and shared error/recovery contract | Preserve and extend the predecessor's eventual concrete implementation. Request target union/scoped FK, request result variants/current target authorization and upgrade tests remain new E5 work |
| Atomic write/context helper | Existing `platform/builder-cli/examples/owned-service/atomic_write.py`, transaction context and WRITE_ATOMIC_EVIDENCE.md | Real bounded owner-copy candidate exists, with synthetic evidence. It is not public scaffold promotion or Leave integration. Verify algorithm/authority/result semantics before reuse; no automatic adoption of secret/key or KDG first-commit semantics |
| App/API shell | APPLICATION_BOOTSTRAP_EVIDENCE.md and current builder files | Disposable bootstrap proof exists; normal authenticated generation/full SERVICE remains explicitly undelivered there. No working Leave package or API test command inferred |
| Ledger and accounting effects | E3 3.9, 3.17-A/B, 3.18 and actual writer contracts | Reuse their actual owner interfaces once delivered; none of this is part of A's read/state implementation. No new ledger/calculator in core |
| Notification intent/worker | E3 3.23 and subsequent owner handover | Actual consequential writers compose those effects. A creates no notification worker/outbox or fake business command |
| Calculation evidence | L-0111 and E3 actual consequential consumers | A references retained evidence contract; it does not implement a second snapshot framework or evidence API |
| Request/cycle/step/decision state and current reads | No request implementation in Leave; C1 matrix is owning design | New E5 scoped records/immutability/reference constraints and authorized projection implementation/tests |
| Dependency/employee guards | E1 draft-scope guard is a different actual workflow; E3 3.9 already requires employee coordination | Reconcile with actual earlier owner implementation. A is read/state support and needs no new consequential lock service; introduce/extend one compatible guard implementation at the first real protected writer, not duplicated in A and B/source owners |

### Recommended split and order

Refine **5.10-A** to request/cycle/step/decision state, immutable evidence protection and
minimum authorized current-request reads. Move its receipt-specific ACs/target migration/
outcome-read integration once into proposed **5.10-C**. A preserves existing E1 operation
routes but does not extend them for requests yet. Place C after A and before B and every
actual consumer requiring request outcome insertion/recovery. B remains finalization.
No dependency on a future submit/decision producer is introduced: scoped valid persisted
records and actual owner transaction fixtures prove these infrastructure consumers.

Move no ledger/accounting/notification implementation into either A or C. Guard storage/
preflight implementation is assigned to the first actual consequential coordination
consumer (B or an earlier actual E2/E3 owner), reusing compatible predecessor guards;
C2/C3 must bind that one owner before final order. This corrects the six-relation count
in the earlier A sizing envelope: a read-only consumer does not create an unused guard
relation merely because later commands need it. It is an allocation proposal, not silent
approval of a new earlier-owner scope or a second locking mechanism.

#### Proposed 5.10-C: Recover request operations through the existing Leave outcome API

As an authorized Leave consumer,
I want request operations represented by the existing reliable outcome mechanism,
So that retries recover the original committed result without repeating business effects.

**Acceptance Criteria (proposed, not approved):**

1. **Given** actual scoped request targets and E1 receipts, **when** introducing request
   support, **then** enforce the checked draft/request command-target union, valid scoped
   references, immutable compact result and original input/version semantics without
   synthetic drafts or a parallel outcome store.
2. **Given** current permitted request outcome access, **when** the existing operation GET
   resolves a committed request result, **then** return its typed original result separately
   from current request state; no receipt/read changes a revision or executes business work.
3. **Given** no authorized committed outcome is established, **when** recovery runs,
   **then** preserve truthful unresolved/denied/unavailable distinctions and original operation
   identity; never infer failed/no effects from missing receipt.
4. **Given** matching versus changed command/target/input, **when** the owning transaction
   inserts/resolves an outcome, **then** preserve matching immutable replay and reject
   mismatched reuse; concurrent unique collision rolls back the losing local effects.
5. **Given** actual restricted owner transactions and induced failure, **when** writing local
   fixture effects and receipt together, **then** commit both or neither. Fixtures verify
   the real internal API/storage without implementing a fake Submit/Approve endpoint.
6. **Given** supported old draft consumers and expanded result schemas, **when** rollout
   activates request producers, **then** prove retained E1 rows/read/write behavior and
   old-runtime result compatibility or enforce the coordinated producer activation gate.

**Scope/verification:** Own receipt extension plus existing lookup/request authorization
adapter and migration/type/transaction fixtures. Consume A's request state and existing
E1 recovery. Actual 5.11/5.18/5.19 and other producers own real effects/canonical input/result
integration; C cannot claim those producers tested. Planned E5-STATE-03/receipt cases move
once, not duplicate in A. Scope remains subject to exact supported-old-runtime and consumer
capability binding; this is not final sizing PASS.

**Impacts:** Existing app-owned scaffold/context/error/outcome candidates reused only after
actual integration proof. Typed frontend result union changes, no new screen. Existing
agent/ADR rules suffice. Accepted rule semantics unchanged. If agreed, update A/C ownership,
original AC mapping and graph dependencies, then increase approved boundary count to 79.
Until then A and the 78-node approved boundary set remain intact. No code/tests/migrations.


## Recovery extraction accepted and refined size checkpoint — 2026-10-23

User accepted the preceding split. BMAD now records **5.10-A state/current read**, new
**5.10-C request operation recovery**, then **5.10-B finalization**. A's receipt ACs moved
once to C; original 5.10 criterion ownership and actual candidate graph updated. There
are 79 approved suffixed boundaries. Historical proposed/pending/count-78 notes for this
specific split are superseded; original scopes remain 32 and groups 10/10.

| Refined boundary | New work counted for sizing | Exclusions and remaining size input |
| --- | --- | --- |
| A | Four scoped state records, immutable evidence/reference integrity, coherent authorized current read and actual restricted storage/read fixtures | No receipt migration/lookup extension, guard implementation or business mutation. Close exact E3 evidence/own-summary field references and read schemas; later assigned/admin consumers bind their own field/capability extensions |
| C | Existing receipt target/result migration, outcome lookup/current target authorization, typed result union/compatibility and real atomic owner-transaction fixtures | Reuse actual E1 machinery; no fresh runtime recovery service, KDG retry semantics or key lifecycle. Close supported-old-runtime lookup/activation and request consumer capability catalog binding |
| B/first actual protected writer | One real dependency/employee guard implementation or compatible predecessor extension plus actual protected finalization composition | Guard implementation owner must be selected from actual predecessor behavior under C2/C3; no duplicate mechanism or assumption E3 already supplies the new shape |

A and C now have distinct bounded acceptance surfaces and no known need for another split
from this inspection. This is provisional fit, **not final single-agent sizing PASS**:
exact interface/type/fixture closure can still reveal excess work. Delivery proof remains
failing-first in actual approved packages; no runtime package/test-command/benchmark is
invented in planning. Updated graph has 79 nodes, 268 internal edges and 18 topological
layers with no cycle; external/semantic completeness is not proven by that check.

Next close C2 executable rule-foundation allocation and actual E3 interfaces, which also
assigns the first guard consumer. Then resolve the remaining C1/C5 field/capability/
compatibility inputs and C6 final atomic coverage/order/size. No new product policy, API
screen, ADR or implementation authorization follows from this accepted decomposition.


## C2 rule ownership and proposed request-accounting foundation — 2026-10-23

**Actual predecessor allocation; one new delivery foundation proposed for agreement.**
Read E3 3.7/3.9/3.17-A/3.18/3.20/3.23 and E5 5.6–9 criteria. E3 3.18 explicitly projects
without reservation writes; 3.9 leaves request reservation/consumption/reversal to real
request consumers. A typed projection is not a delivered protected commitment writer.

| Original scope | Implementation ownership / actual prerequisite | Additional E5 responsibility and order |
| --- | --- | --- |
| 5.1 configured route | Existing E5 route rule foundation, using People/Access/current local policy | Actual current route/responsibility result and setup/unavailable distinction before B; no assignment mutation, frozen supervisor authority or second employee master |
| 5.2 temporary eligibility | Existing E5 eligibility rule foundation | Person-first member/period/scope checks before 5.4/5.3/B and actual appointment consumers; controlled valid appointments test rules, not future creation handlers |
| 5.4 absence fallback | Existing E5 directional fallback rule foundation, consuming 5.1/5.2 and actual current absence/authority inputs | Deliver rule evaluation before 5.3/B; actual return/transfer producers keep their own mutation integration |
| 5.3 applicant responsibility coverage | Existing E5 interval/responsibility rule foundation, consuming 5.1/5.2/5.4 | Current full-absence coverage/gap/exception evidence before B; submission may remain pending with incomplete cover. No automatic candidate selection or appointment creation |
| 5.6 duration/capacity | E3 3.7 duration and 3.20 applicable restriction predicates | Reuse evaluator, add protected current same-date aggregate enforcement in actual E5 commands. Mixed working/nonworking ranges remain valid; capacity counts minutes, not requests |
| 5.7 employee/policy/date | E2 dated employment and policy assignments plus E3 3.5/3.20 rule predicates | Consequential current revalidation under owning source protocol. Preview policy/version or bounded draft observation is not commit authority |
| 5.8 funding | E3 3.17-A/3.18 plus untracked 3.40/3.41 classification | Consume same allocator/order/result and protect existing commitments; new actual reservation/settlement writer proposed below, not a second calculator |
| 5.9 documents | Applicable policy/threshold plus actual E4 association/readiness interfaces | Submission/B compose the required readiness gate and safe status; no duplicate Content protocol or extra sensitive permission |
| 5.10-B | A/C plus delivered rule foundations and actual E3/effect interfaces | Compose all independent gates and Approved/consume/evidence/outcome/intent once; no hidden implementation of every rule/storage mechanism inside B |

5.1–4 retain their already approved product scopes as candidate rule deliveries before B;
this table does not approve new suffixed boundaries or final size for them. The phase
order 5.1/5.2 -> 5.4 -> 5.3 precedes B regardless of their numeric order. 5.6–9 are explicit
reused rule/consumer obligations, not automatic duplicate executable stories. C6 must map
every original criterion once to actual tests and decide final delivery allocation.
Exact typed rule result/input evidence and source protocol remain closure work.

### Missing shared write interface

The actual request consumers need these internal owner operations against the same current
allocation representation: reserve validated submitted allocation; consume its actual
reservation once; release it once on supported terminal action. Reallocation extends that
same representation in actual funding/source consumers, rather than using a second store.
They also need one actual employee/dependency coordination implementation and stable effect
identity under the caller's atomic outcome. No public generic ledger mutation API is needed.

**Recommendation: proposed 5.8-A, Record and settle request commitments through protected
owner operations**, before B, 5.19-A and actual submission/funding producers. This is an
extraction of their shared required work, not a new product feature or second balance ledger.
Use A's real request/cycle state, C's outcome contract, E3 actual allocation/event/evidence/
intent interfaces and current source protection. The first actual consuming implementation
owns the guard relation/preflight/mode/order tests or a compatible extension of delivered
E3 coordination; it does not assume the draft_scope guard protects business funding.
Existing E2/E3 source writers must adopt the same protocol before unsafe producers activate.

#### Proposed 5.8-A: Record and settle request commitments through protected owner operations

As an authorized Leave command consumer,
I want one consistent protected commitment mechanism,
So that submission, approval and withdrawal cannot reserve, consume or release the same
entitlement inconsistently or more than once.

**Acceptance Criteria (proposed, not approved):**

1. **Given** current scoped request/cycle and validated date/source-portion allocation,
   **When** its owning transaction reserves it, **Then** retain the actual commitment
   against the same E3 identities/order, protect existing reservations and serialize
   conflicting employee/date/dependency mutations. The helper cannot trust a client
   allocation or a preview as authority.
2. **Given** a real active reservation, **When** the owning authorized finalization or
   terminal command consumes/releases it, **Then** apply that allowed transition once,
   retaining correct actual accounting/evidence and rejecting incompatible repeated
   effects. Reads/projections create no commitments; untracked policies create none.
3. **Given** the caller's required state/accounting/evidence/outcome/intent envelope,
   **When** commit or induced failure occurs, **Then** all promised local effects commit
   together or roll back together; no independent helper transaction or competing receipt.
4. **Given** duplicate/concurrent/stale/restarted executions, **When** resolving effects,
   **Then** use actual lifecycle/revisions/stable causal identity and bound coordination,
   with truthful original-operation recovery and no repeated consumption/release.
5. **Given** restricted actual owner storage and protected operation fixtures, **When**
   verifying the interface, **Then** prove reserve/consume/release, real ledger/original
   commitment observations, concurrent conflicts and rollback without a fake public
   Submit/Approve/Withdraw endpoint. Actual producers later prove their own domain gates.

**Scope:** Internal request commitment representation/write primitives, first real guard
adoption/extension and independent storage/atomicity fixtures only. No route/coverage/
document/employee-response evaluator, human approval, exceptional source authorization,
reallocation UI or new funding algorithm. Concrete allocation/effect schema/budgets and
fixtures must be bound before final single-agent sizing; split further only on actual
excess scope. It cannot be labeled ready just because the interface has a name.

**Impacts:** Reuse actual E3 ledger/calculation/intent and C outcome, never create parallel
stores/services. Guard/transaction scaffolding can be promoted only after real consumer
proof. No shared UI or new agent/ADR policy. If agreed, map shared accounting ACs from
5.8/5.10/5.11/5.19 to this foundation plus actual producer integration, add graph edges
A -> C -> 5.8-A -> B/5.19-A and update 79 boundaries to 80. Until agreement, count stays 79;
no approved story appended or consumer obligations removed. No code/tests/migrations.


## Request commitment foundation accepted — 2026-10-23

User accepted proposed **5.8-A**. Its approved BMAD story now owns protected reserve/
consume/release operations and the first actual dependency/employee guard implementation
or compatible predecessor extension. The request consumers retain actual domain decisions,
source effects and producer integration; common commitment storage/writes are not repeated.
Earlier proposed/count-79 language for this extraction is superseded.

Order is **5.10-A -> 5.10-C -> 5.8-A -> 5.10-B / 5.19-A**, followed by their actual
consumers. B is all-gate finalization, not a second accounting foundation. C supplies
owner outcome interfaces; 5.8-A does not create another receipt or expose a generic public
funding writer. E3 allocation/ledger/evidence/intent remain actual predecessors. Authorized
reallocation/correction extends the same representation in its consuming item; it is not
silently added to the three-operation foundation as another product workflow.

Guard allocation from C1/C2/C3 is now resolved to this first actual consumer, subject to
reconciliation with real earlier E3 coordination. Required source/reference writers must
adopt it before actual submission activation. First-consumer tests establish the primitive,
not a blanket claim that every writer participates. Count is now 80 approved suffixed
boundaries; original scopes/groups unchanged. Graph check: 80 nodes, 272 internal edges,
19 layers, acyclic; semantic/external completeness is not asserted.

### Initial sizing envelope for 5.8-A

Count three internal operations, one coherent commitment/effect representation, one shared
coordination implementation/extension and actual transaction/concurrency fixtures. Exclude
route/coverage/doc/response rules, human decisions, browser surfaces and new calculation/
ledger/notification frameworks. This is a concrete candidate envelope, not final fit.
Next bind active-versus-settled commitment identity, date/portion lines, stable effect
identity, repeated/incompatible transitions and the caller-owned transaction signature.
Only then assess whether coordination plus accounting fits one agent or needs a concrete
further split; no additional boundary is proposed now. Exact E3/receipt interface/schema,
execution budgets, source participation and final coverage/order/sizing/readiness remain
open. No code, migrations, runtime tests or benchmark occurred.


## Request commitment identity and transaction interface — 2026-10-23

**Technical baseline within accepted 5.8-A; exact E3 payload/physical integration still
needs binding.** Keep one request commitment identity per actual submitted cycle. A new
rejected-resubmission cycle has a different commitment; releasing an old cycle never
creates or consumes the new one's allocation. Ordinary drafts have no commitment.

### Identity and authoritative accounting

| Identity / state | Required binding |
| --- | --- |
| Commitment | Server UUID, organization/employment/request/cycle scoped; unique `(org_id,request_id,cycle_id)`; creation attribution and current revision/update attribution |
| Lifecycle | `active`, `consumed`, `released`; created by reserve, settled only by actual caller command. No automatic return to active or new reservation from a stale retry |
| Allocation basis | Actual retained E3 calculation/allocation evidence identity and its version/line identity; date/portion source provenance and amount units match E3 3.18, including earliest-expiry/source-age/stable tie order |
| Effect identity | Actual parent operation or durable causal work UUID plus closed effect kind reserve/consume/release, bound to the exact commitment/cycle and immutable effect evidence |
| History | Extend E3's immutable actual accounting events/source references; do not create another commitment event journal or independent effect registry. A mutable current head is subordinate coordination/projection, never sole historical balance truth |

Enforce scoped local request/cycle and evidence references with actual predecessor keys.
The exact head-to-allocation evidence reference uses E3's physical contract, not invented
cross-owner FKs or arbitrary JSON IDs. Date/source-portion lines reside in the retained
allocation/effect representation: use one authoritative representation, not a second set
of independently editable reservation amounts in a new table family. Exact E3 normalized
line schema and database-versus-owned-write enforcement remain explicit interface work.

Only paid entitlement portions actually reserved reduce available entitlement. Requested
unpaid amounts remain actual request/allocation evidence and participate in the request's
absence duration/capacity rules, but are not fictional entitlement sources. A tracked
request with zero paid reservation may retain a zero-amount lifecycle envelope; it posts
no fictional paid deduction. No-balance-tracking policies return typed not-applicable and
create no entitlement commitment/ledger effect; they retain their real paid/unpaid
classification and other domain gates. Never collapse these distinct cases into zero balance.

### Closed internal transaction interface

Use internal owner operations `reserve`, `consume` and `release`, receiving the caller's
already-open scoped transaction and actual command context, not opening/committing a
second transaction. Context carries verified organization/actor/initiator, target cycle,
original operation or durable causal identity, current protected revisions/input evidence
and total execution deadline. No public generic endpoint or client-supplied trusted plan.

`reserve` accepts the backend-validated current allocation evidence and creates one active
commitment with actual reserve effects. `consume`/`release` address that exact commitment
and expected revision; they do not recalculate a different source plan silently. Material
allocation change uses the real authorized source/funding consumer's reviewed update and
fresh evidence, not an implicit extra argument to settle. All required guards/current
checks remain valid through the caller's transaction, including related source writers.

The helper returns a typed effect result: `applied`, `already_applied` or `not_applicable`,
with permitted identity/state/revision references. Invalid lifecycle/revision/input identity
is a typed conflict, not `already_applied`. This internal result is not the outer HTTP
`committed` acknowledgement; the caller returns success only after actual commit.

### Transition, duplicate and conflict matrix

| Current state | Requested effect | Result |
| --- | --- | --- |
| No commitment, valid current tracked submission | reserve | Create one active commitment and immutable reserve evidence |
| Active, exact original reserve effect | same reserve replay | Original effect; no new reservation/revision |
| Active, valid actual finalization | consume | Set consumed and apply actual reservation-to-consumption effects once |
| Active, valid supported rejection/withdrawal | release | Set released and release actual reservation once |
| Consumed/released, exact original settled effect | matching replay | Original effect; no new ledger event/revision |
| Consumed -> release, released -> consume, or different duplicate reserve | incompatible effect | Conflict and rollback; E6 cancellation/reversal is not ordinary release |
| No commitment without a valid reserve context | consume/release | Conflict unless the actual policy contract is explicitly not-applicable; never silently create missing accounting |

The same parent transaction may reserve then immediately consume for an eligible automatic
completion: distinct effect kinds share one parent causal identity and commit atomically.
Internal commitment transitions do not imply multiple request review revision increments;
request creation still commits at revision 1. An ordinary intermediate approval retains
the active reservation without another reserve/consume effect.

Use actual immutable ledger source/effect uniqueness to prevent repeated effects across
restart. Same effect identity with changed target/kind/evidence cannot reuse success.
Different causal identities still cannot settle an already-settled commitment a second
time merely because their operation IDs differ. Canonical input mismatch/replay and
original HTTP recovery use C's existing mechanisms; no second command receipt.

### Complete local envelope and proof ownership

Request lifecycle/decision, commitment head, real ledger/calculation/audit, caller outcome
and required notification intent belong to one owning local commit when promised together.
The helper neither sends notifications nor commits partial settlement before the caller's
state. Any failure rolls the entire transaction back. Cancellation/timeouts release the
connection/transaction correctly; an uncertain response follows original recovery, not
assumed rollback. Reads/projections post no earning/reserve/consumption events.

5.8-A proves the real internal interface and shared coordination with restricted-role
fixtures, independent ledger/head/evidence oracles, both consume/release race orderings,
reserve-plus-immediate-consume, matching/different causal retries, wrong cycle/scope,
tracked-zero versus untracked, induced rollback and restart. B/5.11/5.19 later prove their
actual all-gate/domain/closure integration; no fixture pretends those commands exist.

### Sizing checkpoint and unresolved specifics

The accepted boundary remains three internal effects, one small current commitment head,
extensions to actual E3 accounting/evidence and one shared guard implementation/extension.
No new transition journal, allocator, ledger or receipt framework. This is provisionally
coherent; final fit still needs exact E3 effect/line schema/unique keys, current guard
adoption delta, concrete fixture count and execution/rollback budgets. If those exceed a
bounded session, isolate the actual excess rather than adding unrelated workflows or
silently dropping concurrency coverage. No further split proposed now and no size PASS.
Existing scaffold/UI/agent/ADR impacts stand. No code, migration, tests or benchmark ran.


## Accounting field binding and 5.8-A sizing verdict — 2026-10-23

The [owning E3 request accounting interface](e3-request-accounting-interface.md) now binds
request event/line/head fields, scoped effect uniqueness, original causal identity and
reserve/consume/release semantics. Request-specific references/types are added by 5.8-A
after A; E3 is not made dependent on future request tables. Existing E3 allocator/evidence
contracts remain prerequisites, not new code hidden inside this consumer.

**Sizing verdict: retain 5.8-A as one delivery item; no further split recommended.**
The selected scope is one current head, three related event effects on E3's ledger,
existing outcome/evidence/intent composition and one shared guard adoption/extension.
No allocator, public business endpoint, UI, general event journal or source workflow is
included. Its cohesive acceptance surface is protected commitment lifecycle and atomic
accounting, so splitting reserve from settlement would leave concurrency invariants
spread across independently incomplete foundations.

This is a bounded single-agent delivery assessment **conditional on actual predecessor
contracts/implementations being available**, not an implementation readiness PASS or a
claim of measured duration. If missing E3 portion/evidence, C recovery or owner coordination
is delegated into 5.8-A, the assessment is invalid and that prerequisite must be closed
first. Exact execution budgets, actual package/test command binding and complete C6 source
coverage remain readiness work. SQL constraint names and migration implementation are
normal delivery details against the selected schema, not grounds for endless repeat
product review. Required real concurrency/rollback evidence is delivery acceptance.

Next move to C3's actual writer/reference completeness, especially initial policy
assignment and rehire reachability; do not reopen the accepted foundation absent a concrete
new conflict. Progress remains 10/10 groups, 32 scopes and 80 approved boundaries.
No code, runtime tests, migration or benchmark ran.


## C3 initial-assignment and rehire writer allocation — 2026-10-23

**Positive source-path allocation under already approved scopes; not a runtime coverage
PASS or new behavior.** Read actual 3.28 initial assignment, 3.36 change/end and 2.13 rehire
criteria. Both additional sources explicitly require consequential effects when reachable;
neither may be dismissed from a title such as initial or return. Reuse the protected
assignment/People consequence seams once; retain actual source-specific producer tests.

| Actual source | Concrete allocation | Required positive / non-impact cases |
| --- | --- | --- |
| E3 3.28 initial policy assignment | 3.28 owns exact selected-set review/confirmation and source write/UI. Existing 5.15-I assignment-impact integration supplies the common protected assignment timeline/affected-request calculation seam, extended to typed create as well as change/end where applicable; 5.8-A supplies actual commitment effects | First genuinely unused assignment with no dependent requests; concurrent first assignment versus submission; rejected overlap; changed relevant timeline/funding where the source lawfully reaches retained requests. No blanket no-impact claim based on initial label |
| E2 2.13 return to employment | 2.13 owns actual new-period human workflow and People source attempt. Shared People prepare/fence/current dated read supports period-add as an explicit command variant; existing 5.15-K employment-impact integration supplies common Leave reconciliation, not a second employment editor | New period starts after a real employment gap; pending requested dates newly covered by that period; stale/no-overlap source revisions; unchanged historical requests; current access revoked; lost source response and resumed consequence |

This is a consumer integration allocation, not permission to reinterpret source validation.
3.28's allowed initial-versus-replacement selection is checked by its actual source schema;
3.36's supported resumption is not relabeled initial to bypass its reviewed rules. Bind the
real command discriminator and allowed prior state before its tests execute. Where a source
precondition makes existing-request impact impossible, prove that exact predicate and no
implicit holders; it does not exempt concurrent reference/source protection.

A new assignment cannot silently replace a submitted request's immutable policy/cycle
basis or generate guessed grants. It uses actual E3 effective timeline/entitlement rules,
retained source provenance and current protected allocation. Pending consequences retain
L-0151/0162 response/notification rules and L-0154 reassessment; approved requests remain
protected. Source review must not silently expand selected employees. Initial-assignment
UI remains 3.28's surface; 5.15-J is not a second copy of that initial-assignment editor.

Rehire preserves the enduring employment identity, all prior periods/ledger/decisions and
ordinary draft. It does not restore grants, merge gaps into continuous employment or reset
policy/profile/balance. Actual E3 employment-period earning rules determine newly available
funding. If a pending date eligibility gate genuinely resolves, its source reconciling
consumer invokes B under all current gates and existing valid decisions; it cannot invent
approval. Dates still in a gap stay ineligible. Approved-request/correction treatment does
not become an E5 automatic cancellation or rewrite. Rehire UI remains 2.13's surface.

### Guard and protocol coverage for both variants

Assignment create/change/end locks the actual employee-policy timeline and old/new policy
reference identities, then employee commitments in the bound order. Re-enumerate dependency
memberships after protection; no absent assignment row is an adequate guard. Period-add
uses the exact People attempt/expected relationship revision, scoped Leave preparation and
actual committed version before gate release. A source end-date-only payload is not a
valid substitute for period-add; extend the shared closed union explicitly.

Each source variant owns real source -> protected consequence -> outcome/intent tests and
rollback/recovery. 5.15-I/K common integration tests establish shared mechanics, while 3.28/
2.13 verify their actual producers. E5-5.32 links relevant owner evidence; no duplicate
complete suite or new monolithic scenario is necessary solely for this allocation.

### Size and closure status

No new E5 boundary is justified from these paths now: they reuse existing source workflows
and typed common consequence seams. The 5.15-I/K envelope must explicitly count these
variants in final sizing; if exact payload/state/scenario detail reveals excess work, raise
one concrete delivery split rather than hiding the work. Their earlier end/change-only
descriptions are not proof the newly identified producer paths are already implemented.

C3 now has accountable positive allocation for these two omissions, but not complete writer
coverage. Next finish the remaining type/profile/archive/default/effective-time paths against
source predicates and finalize the reference-path matrix. Exact input unions, selection
predicates, query/index plans and package/test bindings remain contract gates. No code,
tests, migration, grant or provider change; final coverage/order/readiness remain open.


## C3 remaining source/reference matrix and query predicates — 2026-10-23

**Consolidated planned writer inventory; not executed source coverage.** Completes the
identified source-family allocation alongside the preceding initial-assignment/rehire
variants. Existing 5.15-A–V, 5.21–25 and original E2/E3 scopes retain implementation ownership.
No extra product story follows just because a reference writer has its own test row.

| Source/reference family | Required participation and actual owner | Non-impact boundary / mandatory oracle |
| --- | --- | --- |
| Type create / first unused policy | 3.1/3.3-A establish stable type/policy guard before references; new selection/assignment writers use it | Prove no implicit employee assignment/entitlement. Creation alone is not used-policy request-impact mutation |
| Type metadata / permitted units | 3.39 protects type/version and current new-selection checks; actual submit/resubmit revalidate allowed date-aware inputs | Preserve submitted mode/policy/calculation. Pure labels/icons do not reallocate existing requests; removed draft mode clears only under approved compatibility rules, never on outage |
| Type deactivate / restore | 3.37/3.38 and assignment/reference writers share type guard and dependency predicates | Deactivation cannot bypass current/planned assignments or erase balances/requests. Restoration does not reinstate grants/assignments/closed work. Do not infer a new pending-finalization block from inactive label alone |
| Profile create / archive | 2.19 creates unused identity/version/guard; 2.24 takes exclusive profile protection and reloads assignment/default dependencies | No implicit holders on create. Archive blocks current/planned/default use, retains historical versions and does not auto-move holders; prove assignment/default races and historical resolution |
| Employee profile choice | 2.20 via 5.15-O/P; exclusive employee-work timeline and shared old/new profile/default/calendar references | An explicit profile is not a copied default. Replacing/ending a dated assignment re-enumerates actual inherited paths |
| Override / reset | 2.22 via 5.15-M/N, including timezone/calendar/standard-day fields | Reset removes override and restores inheritance; equal explicit value remains explicit. Fully overridden fields may have no calculation effect, but reference/read protection still applies |
| Organization default initial/change | 2.21 via 5.15-Q/R; persistent default-slot guard even when empty; reference writers share it | Candidates are actual fallback users, not every employee. Explicit assignments and field overrides retain their semantics; initial empty-to-default race protected |
| Shared profile version publish | 2.23 via 5.15-S/T; exclusive profile guard plus affected employee/dependency sets | Current/planned explicit holders and inherited default followers; actual changed effective fields/date intervals decide consequences, not profile label equality |
| Calendar entry add/edit/remove | 2.18 via 5.15-U/V plus direct/profile/default calendar reference writers | Guard calendar identity including absent date entry. Full/partial closure changes may affect duration and historical earning/funding; nonworking portions do not create leave consumption |
| Policy version/schedule and employee entitlement/assignment | 3.28/29/30/34/35/36 via existing 5.15-A/C/E/G/I plus initial-create variant | Retain original request policy/evidence, source portion provenance and valid reservations; current mutable timeline is revalidated, not substituted for recorded decisions |
| Request state/accounting and exceptional allocation | Actual 5.11/12/13/18/19/20 plus 5.8-A/B/C core | Changing one request can alter another's available funding or applicant/approver absence facts. Protect actual employee/dependency subjects; zero funding is distinct from untracked |
| Appointment, reassignment, expiry/return | Actual 5.21/22/23/24/25 and 5.5 where coverage evidence changes | Old/new subject/responsibility membership protected; completed decisions/final steps preserved. Due work rechecks actual source/current precedence; stale expiry cannot restore superseded supervisor |
| Shared employment/supervisor | People source protocols and 5.15-K/5.24-C/E, including period-add | No cross-owner locks/DB access; each actual source variant and effective boundary has real producer proof. Department/location remain descriptive unless an accepted rule consumes them |
| Access admission/membership/grants | Actual Access owner and every protected API/read/worker scope | Individual/organization disable does not delete request facts or grant recovery human authority. Reference actual Access revocation tests, not a copied grant store |
| Document association/readiness/retention | E4 actual writer contracts; 5.9/real producers compose requirement | No duplicated Content pipeline. Human document reading is not an extra approval gate; medical metadata requires separate permission |
| Import/provisioning/maintenance paths | Supported source owner/import contracts and controlled release/migration tooling | No hidden alternate API/worker/direct SQL bypass. E1 bootstrap timezone setup exposes no public change editor; later public setting changes use 2.20–23. E8 import stays inactive until its real protected writer contract is ready |

### Concrete membership/query predicates

Resolve employee effective work values through the actual chain: applicable explicit
assignment else organization default; each explicit field override wins independently.
A default follower is an employee without an applicable explicit profile, including one
whose some fields are overridden. A profile holder includes current/planned explicit
assignments and default followers where that profile applies. Calendar dependents include
explicit calendar override, explicit profile calendar and default inheritance, with the
actual applicable version/date interval. Do not approximate this with a single current
profile ID column or all employees in the same department/location.

Under exclusive source guard, re-enumerate current/planned reference candidates and compare
against the protected set. Use an allowed superset for safe discovery/locking, then actual
calculation to identify changed consequences for review; do not silently claim all candidates
are affected or omit a new holder. If the protected set is incomplete, restart rather than
locking a new dependency/employee out of order. Source/selection revision alone does not
replace old/new membership guard participation.

Affected request discovery has two paths: requested-date/duration impact **and** entitlement/
funding-history impact. A historical calendar/profile/policy change can affect later available
funding even when the request dates do not intersect the edited interval. Include relevant
pending employee/type commitments whenever the earning/allocation history can change; do
not use only request-range intersection as the universal predicate. Preserve recorded
approved/cycle evidence and apply actual approved-request protections/attention separately.

Index requirements follow those predicates: scoped employee/date assignment histories,
profile/calendar/default reverse dependencies and scoped request employment/type/state/date
lookup plus commitment/evidence links. Actual E2/E3 schema keys determine exact index DDL.
A missing supporting index is performance/implementation work to include in the source item,
not a reason to weaken membership correctness or add an unmeasured impact worker.

### Time without an administrative write

E3 on-demand earning/expiry/carry-over and current date-sensitive eligibility are evaluated
from current history at the protected action; do not wait for a daily posting job. Known
future configuration/People/appointment boundaries invalidate stale observations when due,
including timezone-dependent work dates. Current action must not use a pre-boundary preview
or stale worker assignment. Existing declared resolution producers may invoke B when a
real blocking condition resolves; no new universal polling/final-approval worker is added.
Actual source schedule amendment/cancellation fences obsolete due work.

### C3 planning closure status

The **identified writer/reference inventory and query-predicate allocation is complete at
planning level**, including first-create, empty slots, reset/archive, source time boundaries,
initial assignment, rehire and alternate supported writes. It is not a claim that every
predicate/input schema/test is implemented or that final atomic coverage is closed. Source-
specific closed payloads/commands go to C4/C5 and exact AC-to-case/package/command mapping
plus final workload/order/sizing goes to C6. Unresolved source validation cannot be hidden
behind this register, and a newly discovered actual path returns here with a concrete gap.

Next consolidate/adopt the remaining shared People protocol candidate rather than repeat
this inventory. Existing source stories own their tests and index work; 5.32 adds only
composition gaps. No boundary, product rule, shared UI/agent/ADR or implementation change;
80 approved boundaries, 32 scopes, 10/10 groups. No runtime tests/migrations or benchmark.


## C4 consolidated coordination contract — 2026-10-23

[People–Leave change coordination](../../../../../platform/docs/architecture/contracts/people-leave-change-coordination.md)
now owns the consolidated internal v1 routes, typed period-add/end/supervisor branches,
source-attempt/preparation binding, atomic commit/cancel order, protected affected-set
preparation and authoritative reconcile/release. Earlier sections are rationale; do not
create parallel versions of the same protocol in each source story. No new user action,
role, shared runtime coordinator or database boundary change.

C4 is more concrete but not fully accepted/closed: exact source review evidence, planned-
date normalization, People storage/row order, real cutover/transport and numerical bounds
still need binding. These are a finite adoption list, not a reason to reopen agreed owner
semantics. Next choose execution/recovery budgets against the existing synchronous-first
scope and 1,000-employee validation, then close actual source wire specifics and adoption.
No new boundary or implementation; final coverage/order/sizing/readiness remain open.


## E5 consequential execution budget binding — 2026-10-23

The [shared budget baseline](../../../../../platform/docs/architecture/contracts/people-leave-change-coordination.md#initial-execution-and-recovery-budgets--2026-10-23)
now selects 30-second execution, 3-second fact/outcome reads, at most 20-second internal
coordination hop, 1-second lock acquisition within 5-second local transaction, 35-second
browser wait and 15-second/3-lookup automatic uncertainty observation. No automatic
consequential mutation reissue; explicit Retry retains original identity and current checks.
E1 draft budgets unchanged. L-0163's already-checked transaction cannot exceed its remaining
5-second local budget; no authority check after the boundary uses old facts.

Durable causal recovery has bounded 20-second attempts, increasing 30/60/120-second retry
delays capped at five minutes and grouped technical incident after five minutes unresolved.
No expiry-based gate release or end-user escalation. These are selected operational design
values, not measured capacity/latency promises. Actual 1,000-employee/concurrent-use evidence
must show safe cleanup and feasibility before release; synchronous-first local impacts stay.
No new boundary, product flow or implementation; source schema/normalization/storage/cutover/
transport and final coverage/order/readiness still open. Next bind source-specific fields.


## C4 source fields/effective intent bound — 2026-10-23

The [shared source-field binding](../../../../../platform/docs/architecture/contracts/people-leave-change-coordination.md#source-fields-and-effective-intent-binding--2026-10-23)
now closes typed period-add/end and supervisor on_commit/at intent. People resolves current
change time at actual source commit after preparation. Planned Leave dates normalize from
the declared prior work-timezone observation per selected employee, with retained zone/data/
revision/instant evidence and changed-normalization re-review. Current People edits need no
Leave work profile. Period dates remain inclusive civil dates; no gap or grant reset.

Actual source handlers verify replay/normalization/boundary cases. Remaining C4 items are
source review projection and People attempt storage/order plus concrete cutover/transport;
execution budgets already selected. No new story or implementation, and full protocol
adoption/final coverage/order/readiness remain open.


## C4 review/attempt storage bound — 2026-10-23

[Shared review and storage binding](../../../../../platform/docs/architecture/contracts/people-leave-change-coordination.md#source-review-evidence-and-people-attempt-persistence--2026-10-23)
now defines versioned exact-source/consequence digests, source-family reviewed fields,
authorized private impact access and People-owned change_attempt fields/scoped keys/state
unions. No generic private request access from People credentials or substitute redacted
mandatory review. Source write order is attempt -> employment -> source child/history;
commit/cancel compete on the same row and terminal states cannot resurrect.

Actual source owner implements this storage with its consuming command, not E1's read-only
slice. Remaining C4 design items are credential transport and concrete source participation
cutover; actual capability bindings C5 and test/package evidence C6 remain separate. No
new story, role, review UI or source master. Adoption/final coverage/readiness remain open;
no implementation/tests/migration.


## C4 transport/cutover binding and adoption recommendation — 2026-10-23

The [shared final C4 binding](../../../../../platform/docs/architecture/contracts/people-leave-change-coordination.md#caller-transport-and-source-participation-cutover--2026-10-23)
selects owner/caller-specific X-Service-Key transport and People consumer_participation
barrier. Source writers share-lock the stable participation row before attempt/employment
locks and recheck at final source commit; deployment activation exclusively changes it
before Leave baseline/reconciliation/admission. No HTTP waits under that lock, no Access
flag as unregister instruction and no older bypassing writer as rollback.

Finite C4 design choices are specified. Recommend adoption at the user checkpoint, not yet
an accepted new ADR. C5 scopes/schemas and C6 exact tests/order/size plus real delivery proof
still gate readiness. No new human permission, UI, service registry or runtime change.


## C4 protocol adopted — 2026-10-23

User agreed to adopt the consolidated protocol. [P-0062](../../../../../platform/docs/architecture/decisions/0062-people-leave-prepared-source-change-coordination.md)
records the decision and [owning protocol](../../../../../platform/docs/architecture/contracts/people-leave-change-coordination.md)
now has adopted planning status. Earlier pending/candidate language is historical for this
design; no implementation or whole-epic readiness is implied. C4 design package is complete
at planning level, with real consumer/runtime acceptance still required in delivery.

Next C5 binds existing approved business capabilities to exact org-scoped action/read
contracts and role defaults, then actual closed command models. Use Features' permission
families and L-0149/0150/0153/0161; no new role, implicit grant or default document right.
C6 retains final atomic source-test coverage, executable foundation/order and sizing.
Progress unchanged: 10/10 groups, 32 scopes, 80 boundaries. No code/tests/migrations.


## C5 request capability/read bindings — 2026-10-23

The owning [capability/command contract](e5-capabilities-and-commands.md) now maps approved
permission families to exact request action/read catalog names and current domain predicates,
including unified approval, separate on-behalf/funding/reassignment/coverage-exception and
medical access. Existing standard/custom/temporary defaults are preserved; no live grants
or new role. Minimum assigned read accompanies actual approval scope, not broad team access.
C5 source action/temporary effective-scope representation and closed command schemas remain
next; catalog strings are not proof Access already implements those consumer scopes.

Replacement AGENTS focused migration guidance was read and applied to planned verification:
reuse ordinary Alembic/PostgreSQL and focused actual restricted-role/rollback cases, no
universal object whitelist or extra internal-ledger checker. Actual domain constraints
remain binding. No implementation/tests/migration. Progress unchanged at 80 boundaries.


## C5 source/temporary authority paths bound — 2026-10-23

The [C5 source/appointment section](e5-capabilities-and-commands.md#source-actions-and-temporary-appointment-authority--2026-10-23)
now maps actual source actions to approved capability families and distinguishes permanent
assigned approval from explicit local appointment authority. Access validates current
identity/membership/app admission; Leave checks exact appointment/current step. Declared
Access context/resource extension is an explicit predecessor, not an existing endpoint or
denial fallback. No permanent role/per-appointment Access grant is required merely to
represent approved L-0082 behavior. Source private impact review is scoped, not general
People-derived read. Exact People source catalog/on-behalf target selection and command
schemas remain closure work. No new boundary, grant, implementation or readiness claim.


## C5 on-behalf/employee-response models bound — 2026-10-23

The [owning C5 models](e5-capabilities-and-commands.md#initial-on-behalf-and-employee-acknowledgement-command-models--2026-10-23)
now bind normalized summary projection, on-behalf create input/reason/review/ref fields,
request-target result/canonical identity and employee-only exact unpaid response with its
actual per-cycle record. Pending new-cycle producers select in_approval; B alone supplies
approved completion. No queued routing stage, proxy consent or employee draft change.
E4's actual on-behalf association reference remains an explicit owner prerequisite, not
redesigned here. Exact C6 package/test mapping and remaining ordinary/correction/source
command models still open. No new boundary or implementation.


## C5 ordinary decision/withdraw models bound — 2026-10-23

[C5 decision/withdraw schemas](e5-capabilities-and-commands.md#approve-reject-and-pending-withdraw-command-models--2026-10-23)
now bind routes/fields, request/cycle/step revisions, one immutable same-person multi-step
decision, comments/reason, compact results and safe changed-step/closed-work conflicts.
Reject/employee-only withdraw compose 5.8-A release; approval composes B completion. Matching
replay precedes new lifecycle checks and cannot duplicate effects; no manager/proxy withdrawal
or private comments. Next rejected correction/save/resubmit models, then remaining actual
source/appointment/funding models. No count or product change; C6/readiness remain open.


## C5 correction/resubmit models bound — 2026-10-23

[C5 correction binding](e5-capabilities-and-commands.md#rejected-correction-and-resubmission-command-models--2026-10-23)
selects explicit create/resume/read/save/resubmit routes, per-rejected-cycle correction
identity/revision and compact request-target outcomes. Save is lightweight and leaves
request/history/ordinary draft/accounting unchanged; explicit resubmit closes corrections
with actual new cycle/effects and fresh own initial acknowledgement. No old decision or
late-save resurrection. E4 historical/current association contract remains its owner
prerequisite. Next remaining funding/coverage/assignment/appointment command models; C6
final coverage/order/size/readiness open. No new boundary or implementation.


## C5 exceptional funding models bound — 2026-10-23

[C5 funding/combined models](e5-capabilities-and-commands.md#exceptional-allocation-and-combined-approval-command-models--2026-10-23)
now bind read-only proposal and funding-only/Approve-with-exception body/result/error
unions, one reason and explicit permitted source lines. Backend allocates actual E3
portions and actual 5.13-A extends the same commitment/ledger with reviewed replacement/
request-specific grant effects. No per-line permissions, second ledger or hidden expansion
of 5.8-A. Combined authority/effects are atomic; funding-only may resolve B with prior valid
decisions without fabricating approval. Next coverage/reassignment/appointment models;
C6 final coverage/order/sizing/readiness open. No new boundary or implementation.


## C5 coverage and per-request transfer models — 2026-10-23

[C5 exception/transfer binding](e5-capabilities-and-commands.md#coverage-exception-and-selected-reassignment-models--2026-10-23)
now specifies bounded coverage evidence/reason/current B reassessment and exact per-request
unfinished step transfer/target membership/review/result. Neither grants approval or hides
a gap. One unresolved material batch choice is proposed for user agreement: per-request
atomic outcomes across multiple selected requests, truthful successful/conflicted/unresolved
items and no rollback of earlier success. One request's selected steps remain atomic.
Until agreement, no batch semantics/readiness claim. Next resolve that choice then actual
appointment models. No count or implementation change.


## C5 appointment lifecycle/receipt models bound — 2026-10-23

[C5 appointment models](e5-capabilities-and-commands.md#temporary-appointment-creation-and-lifecycle-models--2026-10-23)
now bind person-first membership/responsibility/interval/selected-return evidence, truthful
creation/start progress, extension/end/current-expiry and obsolete-work rules. Receipt
gets a scoped appointment branch rather than synthetic draft/request/employment. Existing
branches retain original constraints. First real expiry consumer owns required state and
actual producer later proves creation integration; no second worker/notification engine.

Guard register correction: approval_subject uses verified durable account actor UUID,
not mandatory employment, to support L-0079's active-member appointee. Employee capacity/
funding guards remain employment-scoped. This supersedes the earlier kind-09 subject key
only, no product authority change. Next consolidate read/query/source references and C5
remaining gaps, then C6 atomic coverage/order/size. No count or implementation change.

## C5 read/source consolidation — 2026-10-23

[Read contract](e5-read-models.md) links actual current/detail/history, queue, team, attention,
calendar/list and My Leave consumers to existing records and owner interfaces. Bounded
paging and scoped formal-history projection are technical baselines; G1–G6 explicitly
retain unresolved query semantics, preference/source/cross-owner/timed-work/schema gates.
No new screen, second history/balance store or implementation claim. Next resolve 5.17
current-versus-effective team grouping, then consolidate technical owner gaps and C6 atomic
coverage/order/sizing. Progress: 10/10 groups, 32 scopes, 80 boundaries; readiness open.

## C5 collection and preference design binding — 2026-10-25

[e5-read-models](e5-read-models.md) closes G1/G2 design: existing queue filters/order/task
identity, own history/year/section and current-date context, typed scoped attention branches,
and minimal account/org Calendar/List preference. Clock-only failure preserves verified
history; actual source/worker wire artifacts remain G3–G6. No operation-receipt extension
for preference. Next concrete source/rule interface reconciliation, then cross-owner/timed
wire and C6 atomic coverage/order/size. No new product scope or runtime verification.

## G3 configuration and rule-reference reconciliation — 2026-10-25

[Owning configuration/rule interface](leave-configuration-and-rule-inputs.md) binds actual
E1/E2/E3 source references, date-effective work/origin projection, stable configured route
responsibility IDs with principal-scoped bindings, full incoming-work coverage and narrow
rule result variants. No pending-step identity doubles as a responsibility and no draft
choice version doubles as governing policy. Existing guard/People protocol remains owner.
Remaining G3: deterministic E3 allocator/evidence provenance and concrete source-family
impact projections. G4–G6 and C6 remain open; no new boundary, feature, runtime engine or
implementation. Progress: 10/10 groups, 32 scopes, 80 boundaries.

## G3 funding evidence and actual source impacts bound — 2026-10-25

E3 owning interface now specifies deterministic automatic/event portion provenance/key,
allocation ordering/output and actual immutable calculation-evidence shape. Configuration/
rule-input contract binds typed old/new source review/digest and all 5.15 actual source
family projections, including later funding-history effects and complete protected sets.
No changed business funding order, background local impact engine or automatic remedy.
G3 planning design bound. Next G4 People management scope/Access context/Content association
owner types, then G5/G6 and C6 atomic coverage/order/sizing. Progress: 10/10 groups,
32 scopes, 80 boundaries; no implementation/tests/migration/readiness claim.

## G4 Access/Content types and People management catalog — 2026-10-25

Owning shared contracts now bind explicit Access context/resource wire, E4 association
ID/revision and exact target lifecycle across on-behalf/correction/submitted cycles, and
People's existing shared management action/resource naming. No new default grant or
Content pipeline. G4-P remains: compatible shared People capability/app-admission registry
contract; current app-bound Access catalog is not assumed sufficient. Next resolve that
owner design/adoption, then G5/G6 and C6 coverage/order/sizing. Progress: 10/10 groups,
32 scopes, 80 boundaries; no implementation/tests/migration/readiness completion.

## G4-P concrete internal People registration proposal — 2026-10-25

Proposed P-0063 reuses existing Access registry/org admission for internal app_id people
and explicit organization-scoped management authority, provisioned with shared-employment
setup. Independent of Leave; no launcher or additional customer setup/grant. Actual current
consumer still requires Access/People integration. This is a reviewable proposed design,
not adoption or runtime activation. Next user adoption; then G5/G6 and C6 remain.

## G4-P adoption and delivered-foundation correction — 2026-10-25

User accepted internal People Access registration and asked about KDG overlap. Source
inspection confirms existing implemented registry/protected registration/org-admission
commands; plan reuse, not reimplementation. Actual organization HTTP/SQL remains KDG-
specific and no People registration/service consumer was found in working tree. P-0063
and owning contracts now explicitly record delivered foundation versus remaining People
integration/adoption. G4 design bound. G5 timed work/error wire next, then G6/C6 actual
artifact/coverage/order/size reconciliation. No live state inspected or runtime tests run.

## G5 timed processing and error interfaces bound — 2026-10-25

[e5-timed-work-and-errors](e5-timed-work-and-errors.md) owns selected due variants/claim
fencing/budgets, same-step waiting/slot/occurrence/coalescing, actual coverage issue identity
and safe error details. Shared notification contract now explicitly adds Leave org timed
consumer, retaining separate account branch and no domain checks in shared delivery.
Actual owner acceptance remains delivery work. Next G6 artifact/package/source evidence,
then C6 atomic coverage/dependency/order/final-agent size. Progress: 10/10 groups, 32 scopes,
80 boundaries; no implementation/tests/migrations/readiness authorization.

## G6 delivery artifact and actual tooling reconciliation — 2026-10-25

Owning e5-verification-and-artifact-map credits implemented Access registry/admission,
API-client generation/preservation and shared Auth lifecycle/KDG managed-copy proof.
It maps planned Leave api/web schemas/adapters/tests/native DB evidence and actual shared
owner extensions to existing scripts/tooling, without claiming absent paths runnable.
C5 G1–G6 design mapped; next C6 atomic coverage/test allocation, actual external predecessor
reconciliation, order/duplication/final size. No runtime tests, implementation or readiness.

## C6 funding/source-family leaf allocation and attention gap — 2026-10-25

BMAD e5-coverage-audit now splits original 5.8 into 14 detailed funding obligations, with
E3 allocator/5.8-A protected commitment/actual submission and exception presentation owners;
no extra unsuffixed funding engine. Original 5.15 has 20 common leaf/evidence obligations
resolved through 11 concrete source pairs and their initial/reset/amend/cancel/rehire/etc.
variants. Reuse generic tests while proving each actual producer once.

Audit found missing minimum pending-source-issue manager attention in the two-kind read
contract. Existing original 5.15 AC4 is now concretely assigned to 5.15-A read/current issue
evidence and 5.15-B minimum existing attention/detail presentation, later source families
reuse it. No new story/permission/task store. Exact source/read contract updated; final
size must count this work. Next foundational rule/refinement leaf audit, remaining mutations/
displays/proofs and actual full graph/size. No final overall coverage/readiness PASS.

## C6 foundational and late-refinement evidence allocation — 2026-10-25

BMAD coverage audit now allocates all 53 original criteria in seven foundation scopes
across actual core rule, owned transition and required minimum-feedback/producer evidence.
5.4 predicate precedes 5.3 composition; 5.25 return, 5.26/27 clocks and B finalization are
not duplicate foundation mutations. 5.2 fixture-level rules do not claim actual appointment
storage/current expiry proof before 5.23/21/18 integration. E3 duration/calculation and E4
association/privacy retain their owners. Minimal promised feedback is counted, not hidden
in a later UI story. L-0146–0167 and P-0060/62/63 owners mapped explicitly, with E6 cancellation
kept outside E5. No boundary/size PASS; next remaining command/display/journey/non-5.15
writer allocation, then complete graph/external/cross-cutting coverage and final size.

## C6 all original source owners and appointment wording alignment — 2026-10-25

Coverage audit now maps remaining 161 command/display/journey criteria, reaching detailed
owner allocation for all 230 source criteria. Existing state/receipt/commitment/finalizer,
E3/E4 pipeline, first-use result/response/detail/attention and actual source/transfer owners
remain singular. Twelve journeys add bounded actual composition, not first safeguards.
Original editable 5.21 AC6 aligned to already agreed atomic appointment/selected intent
plus effective protected processing/progress; creation is not falsely all transfers done.
Hashes updated deliberately; no policy/ADR change. Next residual C3/cross-cutting coverage,
then full semantic/external graph and actual foundation/all-story size. No readiness PASS.

## C6 residual writers/cross-cutting disposition and graph finding — 2026-10-25

Coverage audit maps 17 residual real writer/alternate paths, all 122 existing BIZ/CALC/
FLOW/PRIV index entries to E5/inherited/later owners, and 21 cross-cutting acceptance
boundaries. Existing sources/ADRs/UX remain authority. Corrected older C3 E7 import typo
to E8, no new import scope. Actual all-writer, privacy, native role/transaction, current
access, errors/session, notifications/workers, accessibility/metrics/release/retention/
restore/impact obligations retained. No final test/coverage/readiness PASS.

Graph must resolve minimum first-use approval-coverage gap attention before relying on
later residual 5.28-A; core 5.3 gap evidence and actual producers alone are not a promised
complete manager read/presentation. Keep this concrete allocation finding open for final
executable order/size, and review any material split. Next actual external/foundation/full
semantic graph and sizing; implemented KDG/client/Auth foundations credited, no rebuild.

## First-use coverage attention accepted; external/foundation assessment — 2026-10-25

User accepted 5.28-C minimum actual gap representation/read/update interface and existing
manager attention/detail. Later 5.28-A/B allocation explicitly residual; no duplicate
gap engine or display. Approved suffixed count 81. Graph current views now include C
before B/real producers; seven original foundation candidates retained. Actual external
predecessors P01–P12 mapped to existing E1/E2/E3/E4 owner items with implemented KDG/
client/Auth/native substrate credited and real remaining consumer work distinguished.
Seven foundations have bounded-work/predecessor/fit assessment; no measured estimate or
readiness PASS. Next size actual remaining core/source/browser/proof units and reconcile
final graph/coverage status before user E5 completion agreement. No runtime work.
