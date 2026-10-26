# Existing boundaries and delivery gates

Derived companion to [SPEC.md](SPEC.md). This file identifies owners and dependencies; it does not duplicate their database/API designs or declare implementation readiness.

## Existing Scribeswell surface

| Surface | Evidence and implication |
| --- | --- |
| Public corpus API | [Bible router](../../../apps/scribeswell/backend/routers/bible.py) provides public books/chapters/verses, morphology, lexicon and occurrences. Preserve anonymous access; do not apply a blanket study-login guard. |
| Reader | [ReaderPage](../../../apps/scribeswell/web/src/pages/ReaderPage.tsx), [PassagePane](../../../apps/scribeswell/web/src/components/bible/PassagePane.tsx), [picker](../../../apps/scribeswell/web/src/components/bible/book-chapter-selector.tsx) and [WordStudy](../../../apps/scribeswell/web/src/components/bible/WordStudy.tsx) own current navigation/comparison/inspection. Study-note state is new; preserve source attribution, URL/back, late-response and focus/scroll protections. |
| Shared browser session | [Shared session delivery record](../../../apps/scribeswell/docs/SHARED_SESSION.md) and [AuthContext](../../../apps/scribeswell/web/src/context/AuthContext.tsx) describe optional sign-in/session sharing. The [standalone account consumer](../../../apps/scribeswell/docs/ACCOUNT_ENTRY.md) adds Create account, confirmation guidance and bounded safe public returns using the same Auth identity. Fixture-backed consumer evidence does not enable currently disabled live signup or prove Studies admission, recipient identity or invitations. |
| JWT helper | [Optional/required helper](../../../apps/scribeswell/backend/auth/jwt_optional.py) distinguishes a token payload from no token but does not implement the feature’s current Access/resource policy. Its current HS256/claim-validation assumptions require review with the existing identity owner before protected use. Do not promote it unchanged as the security contract. |
| Persistence | The existing Scribeswell schema describes public reference data. [Current runtime boundary](../../../apps/scribeswell/DIRECT_DATABASE.md) and app setup use FastAPI/restricted PostgreSQL roles; historical SQL comments about service-role import/Data API exposure are not new-note permissions. No studies/notes/shares migration is selected here. |
| Corpus identity | Existing word IDs and positions underpin analysis; importer upserts can preserve a row ID while replacing its text. Current responses and the importer’s printed file hash provide no activated revision/digest proof. A durable highlight needs a declared source/edition/token/range identity and invalid-anchor behaviour across supported import/release operations. Prototype indexes are not this contract. |
| Shared services | Access owns current protected capabilities/admission; Identity owns verified accounts/actors and recipient evidence. Scribeswell owns study content/resource sharing and private annotations. Any delivery service is integrated through its owner; no imported server code or direct owner-table access. |
| Notifications | [Platform ADR-0006](../../../platform/docs/architecture/decisions/0006-common-notification-capability.md) already selects common asynchronous email/in-app delivery with application-owned intent and platform-owned rendering/retries/deduplication/status. [Leave notification planning](../../../apps/leave/docs/planning-handoff-e3.md) records channel/inbox/UI foundations as planned, not a completed reusable runtime. Account-scoped Scribeswell delivery/inbox contracts remain a Q-1 dependency; Leave organization-scoped counts/read state confer no personal-study access. |

## Binding boundaries

- The adopted account-scope and launcher decisions keep Scribeswell organization-independent. Reading/public URL do not require a grant. The agreed personal-feature policy makes every verified signed-in reader eligible without administrator approval, organization, employment or PtS prerequisites; Access must implement that eligibility explicitly. Protected actions still check current account capability, suspension and Scribeswell resource authority. PtS menu eligibility is neither a Scribeswell grant nor a personal-study prerequisite; launcher eligibility remains unchanged.
- Invitation to a study is not organization enrollment or employment. [ADR-0057](../../../platform/docs/architecture/decisions/0057-invitation-onboarding-and-trusted-tenant-enrollment.md) and [ADR-0058](../../../platform/docs/architecture/decisions/0058-administrator-prepared-access-before-first-sign-in.md) do not implement account-level Scribeswell sharing. Reuse applicable verified identity principles without importing an organization onboarding workflow.
- Preserve the [silo boundary](../../../platform/docs/architecture/decisions/0003-application-silo-architecture.md). Scribeswell’s API checks domain/share rules; Access checks its current protected policy. Do not build a second generic access engine or weaken organization-grant tables to accommodate personal studies.
- [Record attribution](../../../platform/docs/architecture/decisions/0025-record-attribution-and-audit-provenance.md) and [durable actors](../../../platform/docs/architecture/decisions/0056-durable-actor-registry-separate-from-login-accounts.md) apply to new data/evidence. Account IDs and actor IDs are not interchangeable permission grants; no synthetic Auth/employee records.
- [Structural integrity](../../../platform/docs/architecture/decisions/0035-database-structural-integrity-and-application-rules.md), [lifecycle protection](../../../platform/docs/architecture/decisions/0033-draft-lifecycle-and-late-save-protection.md) and current retry/revision conventions apply alongside API validation. No late save or old create retry may resurrect a removed note/study.
- Use [safe structured logs](../../../platform/docs/architecture/decisions/0023-structured-operational-logs-and-sensitive-data.md), [machine-readable errors](../../../platform/docs/architecture/decisions/0031-machine-readable-api-errors-and-localized-presentation.md) and [short transactions](../../../platform/docs/architecture/decisions/0022-short-transactions-and-external-service-calls.md). Notes, pasted sources, invite URLs and credentials are not diagnostic fields. Remote identity/delivery waits stay outside business write locks; required durable intent belongs with its owner-local commit.
- Autosaved personal notes are working content, not unfinished requests awaiting submission. Document that classification under the adopted saving convention; do not add Submit, a publication workflow or an administrative draft store. Sharing/access changes retain their own explicit action and recovery evidence.
- Bind private-response visibility independently from its destination-study relationship. Study view access cannot authorize another account’s private note, highlights, search results or copies. First-version private responses have no sharing override; duplicates preserve privacy. Exact enforcement remains part of Q-2/Q-3, not a client-only badge.
- A note’s write boundary must coordinate the text and associated highlight branch used by conflict recovery. A stale editor cannot overwrite a newer revision; its explicit Save mine as a new note must copy that editor’s branch, not silently combine newer server highlights with older local writing. Define atomicity and response-loss recovery in Q-2’s owned contract.

## Active owner coordination

The user is implementing Access in a separate KDG platform implementation session.
This Studies session consumes that owner’s published contracts and qualification;
it does not run a parallel Access implementation. Decision236 reconciles delivered
personal enrollment/current checking at f02bf84b1a3d3281fb06e91aba01f0057216511c;
recipient/invitation wire remains proposed. Consume the adopted owner runbook and
retain its release/verification limits. Owner delivery alone is not app readiness. Scribeswell-owned account entry remains in scope; account
registration/verification belongs to authentication/Identity, separate from Access
capability assignment.

## Gates before implementation

This is the closure map for [architecture gates D-1–D-5](ARCHITECTURE-SPINE.md#deferred-and-readiness-gates). Q-1–Q-4 retain their spec question IDs; they are not additional workflows. All gates remain open. Settled UX and adopted AD rules constrain the contracts; they do not prove that the services exist.

The [account-access contract](account-access.md) now consumes the delivered ordinary enrollment/current-check owner interface. D-1 remains open for recipient/invitation and live qualification; that broader gate does not block implementing the bounded ordinary-note consumer. No documentation grants runtime provisioning authority.

| Gate / spec question | Owner and required contract output | Required evidence |
| --- | --- | --- |
| D-1 / Q-1: account access and recipient evidence | Access with Identity-owned projections: explicit Scribeswell account capability/self-service policy, restricted callers, verified current account/actor evidence and recipient binding, safe errors and bounded authorization observations. Scribeswell owns invitation/share transitions. | ST-01, ST-02, ST-17, ST-23, ST-26, ST-29, ST-36: accountless-org eligibility, wrong/recycled account/email, forwarding, suspension, revoke/accept races and replay. |
| D-2 / Q-2, Q-3: study domain, writes and provenance | Scribeswell: one owned API/OpenAPI and persistence contract for studies, documents, references, highlights, visibility, revisions, operation receipts and lifecycle. Include independently owned responses, copy semantics, search/count filtering and source-unavailable representation. | ST-03–ST-12, ST-18–ST-22, ST-24–ST-26, ST-28, ST-37, ST-38: safe rendering, corpus change, cross-account/privacy paths, source loss, coherent conflict branches, deletion races and lost-response recovery. |
| D-3 / Q-1: shared notification delivery | Common-notification owner with Scribeswell: account-scoped acceptance/deduplication, email and in-app inbox/read-state contracts, versioned intent, worker identity/retry/status/retention. Scribeswell atomically records required invitation intent in its own outbox. | ST-17, ST-26, ST-29, ST-30 plus owner contract cases for repeated dispatch, provider failure/recovery, duplicate channels, read versus acceptance, and account/organization isolation. |
| D-4 / Q-4: reader/editor integration | Scribeswell reader/UX owner: shared state and interaction contract for selection origin, current-note versus inspected-note, save coordination, workspace-tab/four-pane targeting and closure, bounded public browser history and identity-safe same-device restoration, global per-note lanes, focus and return context. | ST-04–ST-06, ST-10–ST-16, ST-22, ST-23, ST-31–ST-35: browser/keyboard history, same-chapter positions, retained writing, accessibility and actual iOS/Android selection/keyboard proof. |
| D-5 / release constraint: deployment and recovery | Application and shared release owners: restricted roles/pools, controlled owner migrations, private route policy, public/private readiness, compatibility and activation/recovery procedure. | ST-01, ST-25–ST-27 plus owner release evidence: restricted alternate write paths, prior-version compatibility, failed migration blocking activation and verified explicit recovery. |

### Contract boundaries to make concrete

D-4 has a [reader-interaction draft](reader-interaction.md) updated for the user-approved workspace tabs/up-to-four-pane scope. It centralizes tab/pane ownership, global per-note lanes, explicit Open here/beside/new tab, public browser history, closure and mobile return. Earlier two-pane limits and proposed independent pane histories are superseded. The focused workspace mockup is illustrative; bounded snapshot/resource limits, component sequence tests and real-device acceptance still gate delivery.

D-3 has a [shared delivery and account-inbox draft](../../../platform/docs/architecture/contracts/notification-delivery-and-account-inbox.md): producer-local intent, receiver acknowledgement/dedup, email versus inbox status, pre-registration continuation and scoped read state. ADR-0029 governs delivery/retention separately from the invitation’s 30-day expiry. Provider/worker/retention limits, private recipient binding, strict schemas and real handover/recovery evidence remain open; no notification or Leave runtime exists by implication.

D-2 now has one [data-and-saving draft](data-and-saving.md) for note aggregates, closed document grammar, canonical references, source evidence, operation recovery, private provenance and lifecycle. These are proposed shapes, not delivered schemas. Its remaining schema/role/RLS, catalogue/import, numeric-limit, cleanup/copy and qualification items still gate consuming stories. The [corpus-publication draft](corpus-publication.md) now defines the proposed whole-source manifest/gate, writer fencing, full-audit activation and additive reader evidence; physical enforcement, snapshot tests and compatible writer transition remain D-2/D-5 gates.

D-1 now has an [Access-owned enrollment draft](../../../platform/docs/architecture/contracts/scribeswell-study-enrollment.md) for the fixed capability, restricted first-use operation, current-account actor preparation, recipient resolve/verify protocol and subsequent canonical account check. It remains proposed; exact provider/normalization semantics, runtime SQL/command/receipt privileges, remaining bounds and compatibility/recipient-concurrency qualification are still required. It does not close D-1 or authorize implementation.

- **D-1:** Keep the existing Access integration boundary; obtain Identity-owned evidence through restricted projections, without requiring a separate Identity runtime. Define account eligibility assignment without restoring revoked authority on sign-in, actor setup, sign-in verification and target binding for invitations sent before account creation. Specify changed-email/account handling, accepted/declined/canceled/expired states, renewal and concurrent accept/revoke. Obtain remote evidence outside local write locks; define validity/execution bounds and reauthorization on restarted work. Legacy organization `/v1/check`, an email-string match and bearer-link possession cannot supply this contract.
- **D-2:** Define typed identities, source catalogue/versification and English/Hebrew alias normalization, valid verse/range boundaries including cross-chapter policy, and unsupported reference-only passages. Define exact occurrence evidence across corpus imports and explicit Needs review/repair. Choose the structured document schema/version/limits and allowed links; one note revision covers document, references and highlights. Specify serialized save coordination, operation receipts/retention and bounded unknown-outcome recovery, current authority/editability and distinct create/duplicate/conflict-copy commands. Define noncascading private provenance and permitted retained attribution when source content disappears. Keep private responses private in reads, search, counts and copies even within a shared destination. Physical schema, RLS/roles, constraints and generated clients derive from this one owner contract; prototype objects, offsets and regexes are not authoritative shapes.
- **D-3:** Both selected channels reach one Scribeswell Accept / Decline action. Notification reading/dismissal changes no study authority. Pending invitations sits above accepted Shared with me studies and hides when empty; owner statuses/actions remain within Share. Define permitted recipient metadata, outbox-to-shared handover receipts, stable intent identifiers, payload compatibility, delivery versus acceptance status, retry/deduplication and restricted recoverable workers. A provider outage cannot erase a committed invitation. Do not borrow Leave organization membership/count authority or assume planned delivery runs already.
- **D-4:** Qualify versioned bounded same-device public layouts and account-bound study/note metadata restoration (including storage failures, concurrent windows, identity/resource verification and no persisted unsent bodies), stable tab/pane identity, per-tab context, global note lanes, four-pane targeting/capacity/closure and public browser history/URL snapshots under the shared reader-interaction draft. Retain chapter arrows; no independent pane history. Preserve input on tab/tool switches, guard last unresolved editing-context closure, and reject stale responses after tab/pane/account changes. Prove responsive geometry, bounded inactive-workspace resources, native selection/Copy/IME and keyboard/assistive equivalents. Shared contracts close before consuming code; physical-device evidence closes at acceptance.
- **D-5:** Keep public Bible routing and permissions independent from protected feature readiness. Define the private connection context, provisioning, owning migration/worker identity, release ordering and bounded operational checks. Rehearse supported old-version compatibility and migration failures, including partial outcomes and recovery. No blanket service credentials, startup migration, automatic reversal or activation after failed required migrations.

### Dependency order

1. Resolve D-1's account/caller/actor and recipient evidence contracts first; D-2 and D-3 can then bind to the same account scope and stable errors. Shared-owner implementation must be proved before a consuming story depends on it.
2. Resolve D-2's common identities, document/anchor/write and private-provenance contracts before persistence/editor/highlight/copy stories. D-4 can be refined alongside it but must consume those shapes rather than invent its own.
3. Resolve D-3 before invitation delivery/inbox stories. Private self-study design need not wait for email-provider readiness; sharing cannot be claimed complete without its delivery and authority evidence.
4. Apply D-5 release constraints to every consuming design and migration from the start; complete compatibility/recovery evidence before target activation. It is not a final-stage permission to retrofit safe migrations.

These are targeted design/readiness tasks within BMAD. Refine the same spec and owning contracts, then select independently reviewable implementation stories. The user has now authorized a bounded standalone account-entry consumer delivery, independent of Studies enrollment and private persistence. Its [consumer contract](account-access.md#standalone-auth-consumer-contract--bounded-delivery) and [delivery record](../../implementation-artifacts/spec-scribeswell-standalone-account-entry.md) retain the activation gate and exact evidence. Record new owner-level decisions only where warranted; accepted ADRs remain immutable.

## Impact decisions

| Area | Decision for this feature |
| --- | --- |
| Application scaffold | Verify what exists before relying on it. Record actual owner/scope/saving/history inputs only after the pattern is proven; no generator/schema implementation is implied by [ADR-0059](../../../platform/docs/architecture/decisions/0059-schema-validated-scaffold-configuration.md). Consuming stories must include release/compatibility fixtures. |
| Shared UI | Study/passage/highlight domain UI stays in Scribeswell. Assess existing session/save/error/focus/return patterns; promote only proven domain-neutral reusable work with its first consumer and tests, not a generic annotation engine. |
| Agent context | No new root rule now: existing boundaries cover this spec. Reassess when resolved architecture introduces a contract that agents need to preserve. No Leave implementation is authorized. |
| Documentation | This folder is the sole feature specification; app documentation links here. Preserve existing reader/session/runtime records as baseline evidence. Prototype is illustrative, not a duplicate API/schema contract. |
| ADR | Existing decisions unchanged. Link applicable platform decisions; Q-1–Q-3 may warrant new owning decisions after design, not speculative accepted ADRs now. |
| Release | New app/shared persistence requires owner-specific migrations and coordinated compatibility/recovery evidence under adopted ADR-0020. No startup migration, blanket service credential, automatic applied-migration reversal or activation after failure. |

## Current verification boundary

The standalone account-entry consumer now has application browser tests and build evidence, recorded in its [delivery item](../../implementation-artifacts/spec-scribeswell-standalone-account-entry.md). Auth HTTP responses are fixtures; live signup enablement, required confirmation, exact callbacks and real mail remain owner activation gates. Full ST-36 and Studies D-1–D-5 remain open. The workspace/notes/sharing prototypes remain illustrative; no protected notes or shared invitations are implemented. Follow [acceptance.md](acceptance.md) for the wider required evidence.

The [source-candidate tool](../../../apps/scribeswell/docs/CORPUS_EVIDENCE.md) and pure
digest encoder are implemented with 86 affected checks passing, recorded in their
[delivery item](../../implementation-artifacts/spec-scribeswell-source-evidence-candidate.md).
Importer decoding/metadata were extracted compatibly; the lexicon builder consumes
the same pure owner metadata. Exact source continuity is qualified without database
connections. Corpus mutation, fencing, sealed database audit and publication/reader
proof remain proposed and gated. No new public/private API or source bytes changed.

The [read-only database auditor](../../../apps/scribeswell/docs/CORPUS_EVIDENCE.md#read-only-database-audit-candidates)
now qualifies complete source correspondence at one historical repeatable snapshot,
with conservative RLS visibility/current-role checks, bounded worker supervision
and observed word identities. Its [delivery record](../../implementation-artifacts/spec-scribeswell-database-audit-candidate.md)
records all 160 application tests passing, no skips, on disposable PostgreSQL 17.
That observation is not a sealed audit or current publication proof: existing
writers remain unfenced. Production schema/role/activation and D-2/D-5 release
qualification remain open; no protected Studies access or API has been implemented.

The [owned migration baseline](../../../apps/scribeswell/docs/MIGRATIONS.md) is now
implemented and registered with the existing host coordinator. Its
[delivery record](../../implementation-artifacts/spec-scribeswell-owned-migration-baseline.md)
records 231 application tests with no skips, 25 platform tests/42 subtests and
independent pinned-reference reproduction. Adoption-only PostgreSQL 17 guards
preserve corpus/sequence/reader/importer behavior and reject unsafe authority,
schema/trigger/ledger drift and prohibited commands; actual rollback and worker
timeout cleanup are proved. The migration image was not built. Production
role/ownership preparation, target profile/rehearsal and controlled adoption remain
open. Next corpus work must define and prove writer fencing through this owned
history, then sealed full audit/publication evidence; future revisions must extend
the baseline's revision-aware validation and runner. Access account enrollment and
all remaining Studies gates retain their separate owners and evidence requirements.

The [dormant writer-fence foundation](../../../apps/scribeswell/docs/CORPUS_WRITER_FENCE.md)
is now implemented as scribeswell_0002 with exact revision-aware validation. Its
[delivery record](../../implementation-artifacts/spec-scribeswell-dormant-writer-fence.md)
records 321 application tests with no skips, 25 platform tests/42 subtests and both
independently reproduced catalogue references. Shipped enforcement is false, epoch
rows are absent and binding routines remain owner-only. Enabled tests use explicit
synthetic fixture authority; they do not qualify production writer activation.
Original revision/reference/bootstrap/source bytes and actual old reader/importer
behavior remain protected. Next close verified actor/executor binding and bounded
publication-attempt/recovery/sealing commands, then coordinate importer/book seeding,
all prior writer paths, complete sealed audit and ready-reader evidence. D-1–D-5
and full ST-38 remain open; no Access, Leave or factory implementation is implied.


The [publication-command input qualifier](../../../apps/scribeswell/docs/CORPUS_PUBLICATION_INPUT.md)
implements only strict begin/recover/seal parsing and complete raw-source
qualification. Its [delivery record](../../implementation-artifacts/spec-scribeswell-publication-command-input.md)
tracks actual test-first, review and regression evidence. Frozen typed inputs retain
no scripture inventory and convey no authority, committed outcome, audit seal or
publication. The [canonical command contract](corpus-publication.md#publication-command-qualification-contract)
records exact schema/bounds and the existing Identity-owned external actor verification
boundary. Next close the executable controller's physical principal/source-command
policy, verified executor preparation, exact stored retry comparison/outcome and
bounded invocation before any role/importer/enforcement transition. Ready-reader
proof and full ST-38/D-2/D-5 remain open; Access and Leave/factory stay separately owned.


The [dormant transactional controller](../../../apps/scribeswell/docs/CORPUS_CONTROLLER.md)
is implemented as0003: actual-session/exact-source command policy, protected local
actor custody, attempt history, exact semantic outcomes and source-qualified
begin/recover/seal/lookup adapter. Its [delivery record](../../implementation-artifacts/spec-scribeswell-dormant-corpus-controller.md)
records final full614 and focused136 passing tests, platform25/42subtests, three
independent references and resolved three-lens reviews. Shipped routines stay
owner-only, controller/epoch tables empty and enforcement false. Synthetic fixture
actors/grants are not real Identity verification. Replay is deliberately dormant-only;
next close least-privilege live caller/verified actor preparation, active-state release
verification and supervised transport before coordinated importer/writer activation.
Sealed complete audit, ready manifest/reader proof and private Studies remain open.
Access/Identity and Leave/factory retain their separate ownership; signup/UX unchanged.


Supervised corpus invocation is locally implemented and qualified; see
[the supervisor contract](corpus-publication.md#supervised-invocation-contract--implemented-locally)
and [delivery evidence](../../implementation-artifacts/spec-scribeswell-supervised-corpus-invocation.md).
Root full Python regression passed698/no skips, affected acceptance367/no skips,
and platform deployment25 tests/42 subtests. Eight review findings were resolved;
no deferrals. This closes bounded transport/original-operation reconciliation proof,
including actual committed-response loss. It does not close ST-38 or D1–D5: verified
caller/actor custody, active release profile, coordinated importer adoption, sealed
full audit/publication/reader proof and private Studies contracts remain gates.
Production enforcement remains disabled; Access/Identity and Leave/factory ownership,
standalone account creation and agreed UX remain unchanged. No browser, image,
production/provider or live-adoption verification is implied.


Prepared-controller replay is locally implemented; see
[the contract](corpus-publication.md#prepared-controller-replay-contract--implemented-locally)
and [delivery evidence](../../implementation-artifacts/spec-scribeswell-prepared-controller-profile.md).
Root full803 tests passed/no skips184.47s, including105 prepared-profile cases;
independent105-plus-four-probe run passed109/no skips24.71s. Three BMAD review
lenses corrected seven findings and refuted one using existing structural protection;
nothing deferred. This qualifies explicit native replay of already prepared0003 with
false enforcement and empty history, exact custody/ACLs, safe catalogue inspection,
caller timeout ceilings and commit-only success evidence. It neither prepares a live
actor/caller nor verifies Identity. Default CLI/host remains dormant-only. Active/history
release support, live custody, coordinated importer transition, sealed full audit/
publication/reader proof and private Studies contracts remain open; ST-38/D1–D5
are not closed. Applied references/revisions/source/importer, accepted UX and
standalone account creation are preserved; Access/KDG and Leave/factory stay owned
by their separate sessions. No browser/image/provider/production verification inferred.


Controller-history replay is locally implemented, reviewed and qualified; see
[its contract](corpus-publication.md#controller-history-replay-contract--implemented-locally)
and [delivery evidence](../../implementation-artifacts/spec-scribeswell-controller-history-profile.md).
Final root full897/no skips246.21s and focused94 history tests/no skips35.52s passed,
retaining803 prior cases. Literal10000-attempt/20000-outcome capacity, coherent
active/paused/rotated history and actual transition/writer orderings are qualified.
Three user-run independent reviews resolved eight accepted findings (one duplicate
gap) and refuted one JSON-null claim; no deferrals. Added in-bound ordering tests
detect removal of each individual guard. Current-disabled-revision receipts reject;
changed-input recovery, rotation between origin/seal, post-replay original outcomes
and real-commit/injected-ack-loss reconciliation have actual PostgreSQL evidence.
The initial885 pre-review run/thread-limit handoff is historical, not the final state.
Native validation performs no live preparation, enforcement change, Identity
verification, importer transition or publication. Operational host/live custody and
broader ST-38/D1–D5 gates remain open; agreed UX, standalone signup and separate
Access/KDG/Leave/factory ownership stay unchanged.


Operational host-profile integration is locally implemented, independently reviewed
and verified; decision178/evidence179–183 and the [current contract](corpus-publication.md#operational-host-validation--implemented-locally-reviewed)
record explicit selection, bounded worker and commit/evidence activation gating.
Pre-review full932/no skips236.49s, focused37/18.60s and platform66/42/7.55s passed.
Initial acceptance reds, prepared characterization105, affected runs and931/1 timeout-
race discovery remain historical evidence. Supervisor termination is now isolated
from native lock expiry without changing production bounds; both paths pass.
Actual host-to-worker replay, real-commit/injected-ack-loss and explicit reconciliation
are fixture evidence; no image/live Identity/production qualification is inferred.
All independent reviews returned; seven bounded findings patched, one UTF8 claim
refuted, one pre-existing stdout-buffering issue deferred. Current wire-size limits
do not bound peak buffering memory. Host migration inputs are now privately frozen
and cleaned, with real denied/paused/rotated replay coverage. Final root full944/
no skips294.43s (47new/897retained) and platform70/42/4.20s pass (evidence182–183).
Earlier932 is pre-review evidence; the exact owned fixture is stopped/removed.
This extends earlier native-only host statements; dormant stays default and native
CLI has no selector. Live owner custody/image/target, importer/writer/publication and
broader ST-38/D1–D5 remain open. Separate Access/KDG/Leave/factory ownership and
standalone signup stay.


Caller preparation now has a specified [owner handoff contract](../../../apps/scribeswell/docs/CORPUS_CALLER_PREPARATION.md),
adopted as the twentieth companion (decisions186–187). It requires full private
Identity provenance/target pairing before restricted local preparation and committed
profile qualification; copied compact receipts/digests/local custody alone do not
verify Identity. Registration may create; disposable KDG CLI is not live target
support. New mappings start disabled; existing history and actual preparation actor
attribution are preserved. That delivery was documentation only. A subsequent test-only isolated local
mapping rehearsal exercises a bounded subset; external Identity provenance and
the full live handoff matrix remain required, with no live qualification claimed.
ElevenCAP/thirty-eightST, standalone account creation and separate owner boundaries
remain; actual owner preparation/target rehearsal and D1–D5 stay open.


Caller-handoff review correction (decision188): live actor replacement is limited by
current immutable principal key/reference and Identity unique retained keys; synthetic
UUID-rotation coverage is not live compatibility. Incompatible replacement waits for
a reviewed forward change. The contract now requires explicit revisions, atomic
four-row local preparation, independently bound actual session attribution and
separate local COMMIT reconciliation (no controller operation lookup). All five
review findings were documentation fixes. The later isolated rehearsal covers local
atomicity/concurrency/failure observations only; live owner/session attribution and
complete target qualification remain required.


The isolated local mapping rehearsal now passes29new cases and the affected
prepared/history suites pass228/no skips127.55s after review (evidence194).
It qualifies disabled atomic initial preparation, exact no-op, rollback, real
backend serialization/all three lock timeouts, native replay preservation,
restricted operator execute/lookup denial and ended-session COMMIT reconciliation.
Six review evidence gaps were fixed, none deferred. The first affected run had
223passes/one retained capacity statement-timeout; isolated26 and final228 pass
without changing production deadlines or expected results. Actor/session binding
is synthetic; the helper lives only under tests. Live Identity evidence, target/
image qualification, total execution/COMMIT deadlines and production preparation
remain open. This changes no D1–D5, owner, standalone signup or UX requirement.


The [app-owned preparation tool design](../../../apps/scribeswell/docs/CORPUS_PREPARATION_TOOL.md)
is adopted as companion21 (decisions197–199). Its parser is now implemented locally;
its admission/executor portions remain specified designs.
It closes the nine-field request/immutable parser error boundary, separate private
migrator target and trusted owner admission, proposed total execution/COMMIT bounds
and original-session recovery. References/UUIDs/parser values never prove authority.
Direct connections are required for proposed execution; pooler recovery is outside
this contract. Initial reuse requires the same preparer attribution or conflicts.
The initial parser implementation has no owner/file/network/DB effects;
specified worker result wire, unproved durable evidence capture and actual fixture admission
must close before SQL effects. Live owner channel/server identity/image/target proof,
Access/KDG/Leave/factory ownership, UX, standalone signup and D1–D5 stay unchanged.
No new runtime tests or live operations were run for this documentation delivery.


The preparation request parser is now implemented locally (decision203), consuming
the adopted tool contract's first two acceptance rows. It returns immutable nested
declarations through the app namespace and directly reuses unchanged pure custody
validation. Normal code loading is separate from parse calls; no referenced file,
owner, environment, network or DB is accessed during parsing. Equal preparer/service
UUIDs are permitted declarations, never authority. Repository-only import availability
is qualified separately from future runner packaging. The earlier tool document was
design-only; target/admission/deadline/result-wire/durable-attempt/executor and live
readiness remain specified/gated. UX, standalone signup, owner boundaries and D1–D5
are unchanged. Exact commands/results/review live in the
[parser delivery record](../../implementation-artifacts/spec-scribeswell-preparation-request-parser.md).


Reviewed parser evidence (event205): focused207passes2.23s and affected pure
394passes/11native cases deliberately deselected5.98s, with207new/187retained cases.
Six independent review findings were patched, none deferred; an actual two-case
caller-exception retention red preceded its fix. The safe error clears the real
caller/decoder context; depth/import/environment/command/UUID coverage is explicit.
No DB/image/provider/native/whole-app qualification is claimed. Existing pure
custody, applied revisions and owner implementations are unchanged.


The [worker result/attempt contract](../../../apps/scribeswell/docs/CORPUS_PREPARATION_EVIDENCE.md)
is adopted as companion22 (decisions208–209). Its original documentation delivery
ran no runtime tests; the five contract-review findings were fixed. The consuming
pure codecs are now implemented (decision213/event214), preserving the existing
request parser. They validate immutable values, canonical records/hashes, exact
original request and independently expected target, phase/proof/row/session
bindings, create timestamp equality and unchanged reuse. Partial prefixes are
readable; a worker reply requires matching terminal evidence. Encoders revalidate
manual values; one safe error clears decoder and active caller context. Fixed
independent digest oracles and isolated stdlib/no-I/O checks executed.

Final reviewed codec tests (event215):212focused2.41s; independently recreated
Python3.12/pytest9.1.1-only environment212passed2.20s. Affected pure tests606passed
8.57s with11native cases deliberately deselected. Eight verified blind-review
coverage/setup findings were patched, no deferrals or post-review codec behavior
change. Exact commands/setup and intermediate environment/collection failures are
in the codec delivery record and adopted app contract. Historical207/394 parser
evidence remains historical.
Correct hashes and schemas never prove custody or acknowledged persistence;
admitted-only missing session evidence remains unknown. File journaling is not
atomic database business audit: applicable ADR0022/0025 qualification stays required
before effects. Production storage/SQL/supervision/admission, real target/image/database and
crash qualification remain open. No live operations, UX/signup/owner changes,
Access/KDG/Leave/factory implementation or D1–D5 closure is inferred.11CAP/38ST and
all22companions remain stable. Byte/depth probes with multiple invalidities prove
safe rejection, not independent coverage of redundant guards.


### Local fixture record capture — implemented boundary

Decision218/event219 close the next app-local fixture storage contract in the
adopted [attempt-evidence document](../../../apps/scribeswell/docs/CORPUS_PREPARATION_EVIDENCE.md#fixture-storage-contract--bounded-consuming-slice),
without copying its filesystem/API schema here. Trusted root fd, exclusive run
reservation, owner modes, bounded canonical prefix validation, nonblocking locks
and no-clobber file-sync/publication/directory-sync acknowledgements are implemented
only for synthetic local fixtures. Failed appends poison the writer and retain
all residue. Read-only reopening returns validated retained bytes, including an
empty reservation, never proof of the original acknowledgement or no external
effect. No resume/cleanup/replay/live admission/SQL path exists.

Actual ATDD red preceded implementation. Final72storage tests passed7.80s;
affected pure suite678passed20.15s with11native database cases deliberately
excluded. Seven blind-review timing/coverage findings were addressed, no deferrals.
First and later-record process deaths preserve earlier acknowledged bytes; stalled
sync is terminated by the test harness after readiness, not a delivered supervisor.
Exact commands, intermediate fixture failure, setup and local ext2/ext3 evidence
are in the adopted app contract and delivery record. Existing codecs/request parser
remain unchanged. Physical power-loss, production filesystem, kernel I/O deadlines,
real owner/target/image admission, atomic business audit and supervised SQL effects
remain gated.11CAP38ST22companions, agreed UX/standalone signup and separate
Access/KDG/Leave/factory ownership remain intact; no D1–D5 closure is claimed.


### Synthetic communication supervisor — implemented boundary

Decision222 and events223–224 close the app-local
[fixture supervisor contract](../../../apps/scribeswell/docs/CORPUS_PREPARATION_TOOL.md#fixture-communication-and-supervisor-contract).
It exchanges already supplied synthetic terminal declarations through a fixed
isolated stdlib child. Parent independently validates original request/target/
prefix/reply; no parent storage/owner reads, new persistence acknowledgement or
SQL occurs. Frozen `fixture_reply_validated` observations prove communication only,
including when embedded fixture labels say committed/reused. The private closed
transport and unchanged codecs retain separate ownership and meaning.

All phases charge one58work/60total/2remaining-cleanup budget from public entry;
stdin65536/stdout4096 caps apply during transfer, stderr is discarded, no final
drain/retry or public timeout/command/env/callback override. Reaping after a kill
request requires observed SIGKILL before forced-stop attribution; natural exits
in that race stay child_exited. Final total deadline is rechecked after cleanup;
unverified termination remains explicit. OS/spawn scheduling is charged on return,
not claimed hard realtime preemption.

Actual acceptance red preceded implementation. Seven blind findings were fixed,
none deferred; two behavior regressions observed red2failed1.81s then green2passed
1.81s. Final83focused6.76s and761affected15.01s with11native database cases excluded;
63/741 are pre-review evidence. Real isolated malformed/overflow/live refusal,
well-formed mismatched bindings, byte bounds/backpressure, elapsed stalls and
repeated actual forced reaping/fd stability are exercised; fake clocks verify
shared and shrinking budget arithmetic. Exact commands/setup/intermediate failures
are in the adopted tool/evidence documents and delivery record. Existing codecs,
request parser and fixture store remain unchanged. Actual storage/SQL/owner/image/
server/current authority/atomic-audit and physical crash/deadline integration gates
remain open.11CAP38ST22companions and UX/signup/Access-KDG-Leave-factory boundaries
are preserved; no D1–D5 closure or production executor availability is inferred.


## Delivery focus after integrated fixture capture

Direction227/event228 record the effectiveness reassessment. Preparation-tool
validation/storage/supervision are now reused in one delivered capture path; this
is app-local risk reduction, not proof of generic factory or Studies UI velocity.
The [integrated capture evidence](../../../apps/scribeswell/docs/CORPUS_PREPARATION_EVIDENCE.md#supervised-fixture-capture-contract)
records152capture+legacy and830affected checks,11native cases excluded, all six
review findings addressed. No live/SQL/physical-crash readiness is inferred.

The cohesive first outcome is now implemented: explicit personal enrollment, study
creation, ordinary note autosave and saved-text reopening. Event239 and the
[bounded runtime delivery](../../implementation-artifacts/spec-scribeswell-personal-notes-runtime.md)
record native SQL/browser evidence and completed review corrections and affected acceptance (event240). The
[app contract](../../../apps/scribeswell/docs/PERSONAL_NOTES_V1.md) defines the opt-in
runtime; the adopted Access runbook defines owner evidence. Production remains
refused, standalone signup remains required and wider D1–D5 stay open. Shared
migration helper reuse is proven here; no generic factory or UI velocity claim follows.

Event247 extends this outcome through actual local Auth, Identity, Access and app HTTP in one fresh native run. Its [integration evidence](../../../apps/scribeswell/docs/STUDIES_OWNER_INTEGRATION_EVIDENCE.md) records ordinary migrations, restricted runtimes, real provider callbacks, independent SQL oracles, original-operation retries, isolation, disable denial and exact-run normal stop. Fixture preparation defects and collisions are retained as failures; no owner implementation or retained environment was changed. Event250 records completed independent review and final patched-source qualification: all13 findings addressed, none deferred. The supported injected-database factory bypasses default Access release-artifact startup validation; signup, production/release and physical-device gates remain open. This is reusable qualification for the ordinary-note path, not factory implementation or a measured future-change speed claim.

Event233 qualifies only the wire subset:129 affected tests pass3.55s with one
existing HTTP database-lifespan case excluded,10 review findings addressed and no
deferrals. Exact commands/triage live in the delivery record, not inferred runtime
readiness. The executable contract is reusable in the eventual app API; its future
persistence/UI benefit is still to be demonstrated through the real first journey.
