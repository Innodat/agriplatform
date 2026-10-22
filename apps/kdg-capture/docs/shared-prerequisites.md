# Minimum shared-owner prerequisite work for KDG

Current KDG retry prerequisite, 2026-10-22: [ADR-0061](../../../platform/docs/architecture/decisions/0061-kdg-first-committed-operation-wins.md) selects first committed request wins with no command fingerprint/HMAC, fingerprint secret files or associated key backup/restore. Earlier 2026-10-14 secret checkpoints below are historical. Existing runtime/candidates/tests/evidence/resources and other owners remain unchanged; ordinary business-data recovery and child privacy gates still apply.

2026-10-14. Planning work packet, referencing existing owner delivery items rather
than duplicating their stories or authorizing Build. The sole owner acknowledged all
ownership boundaries. Selected engineering contracts are in the
[shared readiness addendum](../../../platform/docs/architecture/contracts/kdg-shared-readiness.md).
All five epics/19 KDG stories remain approved; no Leave decomposition is restarted.

## Approved lean ENV correction — 2026-10-20

The user approved normal pinned Supabase CLI lifecycle with a thin repository wrapper,
building only present development needs. ENV acceptance now uses explicit disposable
target/config/local-only guards, vendor start/status/stop and observable DB/Auth
reachability. Historical individual-container interception qualifiers are preserved
as diagnostics and no longer block this route. Fresh native runs do not adopt their
receipts/resources. The approved dependency baseline, including TS7.0.2, is unchanged.

Application owners retain migrations/fixtures and current authorization tests; a
reachable local Supabase stack is not Identity/Access/KDG readiness. Synthetic sign-in,
application integration and later provider/device evidence remain consuming work.
The development reset command means explicitly confirmed local Supabase DB reset,
not environment disposal or an alternate application migration authority. No PRD,
epic/story scope, UX or accepted ADR changes. No Leave/editor or production/pilot.
See [course correction](../../../_bmad-output/planning-artifacts/sprint-change-proposal-2026-10-20-lean-env.md)
and [active runbook](../../../platform/deployment/DEVELOPMENT.md).

## Ordered owner work and acceptance

P1/SERVICE's first bounded increment is recipe preflight in the existing builder:
versioned input validation and repository references, with candidate patterns kept
explicitly unproven. A valid recipe is not generation readiness. Full skeleton,
regeneration/custom preservation and current Access proof remain separate delivery
obligations. See the [Build record](../../../_bmad-output/implementation-artifacts/spec-scaffold-recipe-preflight.md).

The next increment adds disposable service-only output via the existing builder's
internal bootstrap harness: its own Python lock, clean offline installations and
actual health/safe-error HTTP proof. This does not promote service authentication or
complete the table's P1/SERVICE obligations. See [service bootstrap evidence](../../../platform/builder-cli/SERVICE_BOOTSTRAP_EVIDENCE.md).

Application bootstrap now adds a minimal presentational React/Vite shell with the
owning HTTP shell, copied-root locked offline install, strict type/build and real
Chromium checks. It leaves Auth/current Access, normal generation and custom-code
preservation unproven. See [application evidence](../../../platform/builder-cli/APPLICATION_BOOTSTRAP_EVIDENCE.md).

The approved next increment proves safe reruns with seed/custom preservation and
conflict/interruption handling through the existing builder and disposable proof.
Completed:46 builder tests and actual reviewed shell proof pass; review has no
deferrals. Journal-backed recovery, direct build admission and concurrent-writer
refusal are covered; uncertain state remains safely blocked.
Public generation/extensions and current Access remain
pending. See [preservation evidence](../../../platform/builder-cli/PRESERVATION_EVIDENCE.md).

The completed bounded increment adds explicit initial text-module import and source-independent
preservation through the existing installer.60 builder tests and reviewed actual import/
browser proof pass; no review deferrals. Normal
public generation and Auth/Access are still delivery work. See
[extension evidence](../../../platform/builder-cli/EXTENSION_EVIDENCE.md).

The bounded P1 client increment implements owner OpenAPI contracts, a thin client
and actual browser own-API proof through existing owners. Acceptance verification
passes after three-layer BMAD review and seven patch groups; no deferrals. The isolated tool compiler6.0.3 leaves app
TS7.0.2 and its ordinary tsc command intact. See
[client evidence](../../../platform/api-client/EVIDENCE.md). Auth/Access/public generation
remain separate delivery work.

ID-A's first bounded delivery now implements the separate Identity baseline,
verified synthetic adoption and explicit source/release handover. Actual owner/runtime/
Auth-role and mismatch/failure evidence passes; review corrections and focused checks
are complete. Exact live owner/
ACL differences, ID-B hardening/actors, Access v2 and later readiness remain separate.
See [Identity evidence](../../../services/access/IDENTITY_BASELINE_EVIDENCE.md).

ID-B's additive actor persistence foundation is implemented and reviewed;
actual structure/retention/private-role/upgrade/contention proof and 40 focused tests
pass. The next bounded increment adds the restricted current-account actor read;
actual runtime isolation, clean/adopt/previous-code upgrade and rollback pass alongside
90 focused tests and both composer checks. It does not complete controlled provisioning,
membership lifecycle, Access consumer adoption or activation. The subsequent bounded
selected-organization membership read and server revision also pass actual restricted-login,
legacy writer/Auth-hook, upgrade/rollback proof plus 119 affected tests and both composer
checks. It preserves current uniqueness/CASCADEs/unretire semantics and leaves hardening,
new-ID rejoin, operator provisioning and full ID-B open. See
[organization evidence](../../../services/access/CURRENT_ACCOUNT_ORGANIZATION_EVIDENCE.md),
[actor evidence](../../../services/access/ACTOR_FOUNDATION_EVIDENCE.md) and
[current-account evidence](../../../services/access/CURRENT_ACCOUNT_ACTOR_EVIDENCE.md).

The subsequent bounded increment validates the four selected Identity operator input shapes
with a strict owner-local parser and immutable typed requests. This is CPU-only input
validation; protected authority, target binding, execution/outcomes and full ID-B remain
open. See [operator-input evidence](../../../services/access/OPERATOR_INPUT_EVIDENCE.md).

The protected operator authority foundation adds controlled principal/authority records
and original-login-bound matching through the existing Identity migration owner. It
qualifies this database authorization boundary only; command effects, target adapter,
immutable outcomes/events and full ID-B remain open. See
[authority evidence](../../../services/access/OPERATOR_AUTHORITY_EVIDENCE.md).

The next bounded ID-B increment implements protected system/service actor registration
with atomic actor/outcome/event and scoped original-receipt recovery. Fresh actual
restricted-login/concurrency/revocation/structure/upgrade/rollback matrix passes27 named
stages;330 affected tests and both composers pass. All three review layers and patches
are complete with no deferrals.
At that increment, prepared-target/CLI integration remained open; only synthetic
fixtures were qualified. Other Identity commands/full ID-B remain open. See [command evidence](../../../services/access/ACTOR_COMMAND_EVIDENCE.md).

The following bounded increment supplies a private native disposable prepared-target
Identity CLI for existing actor.register_system execute/outcome. It reuses the ENV
configuration/private-file checks and bounded worker; no schema/role/credential/dependency
or generic service is added. Actual local synthetic execution/recovery/refusal and
focused boundary checks are recorded in
[target evidence](../../../services/access/OPERATOR_TARGET_EVIDENCE.md).
Controlled database/authority/secret preparation remains explicit and separate; the CLI
does not provision or reset. Account/membership commands and full ID-B/Access/WRITE/KDG
readiness remain gates. No production or hosted-CI acceptance is implied.

The next bounded ID-B increment adds restricted selected-organization candidate and
exact-member target reads under revision7. Complete UUID-keyset candidates and current
account/member binding use a separate read owner, narrow Access caller roles and
restrictive organization policies. See [target-read evidence](../../../services/access/ORGANIZATION_TARGETS_EVIDENCE.md).
This does not deliver Access eligibility/public paging/wrappers or account provisioning;
full ID-B and dependent readiness remain open. Prior references/migrations remain intact.

| Existing item / boundary | Minimum KDG-relevant outcome | Acceptance/evidence before consumer | Earliest consumer |
| --- | --- | --- | --- |
| ENV | Isolated synthetic Auth/PostgreSQL/Access/KDG target, root frontend lock and independent Python locks, compatible exact tool/container/package set; guarded bootstrap/stop/reset and reachable nonproduction HTTPS/provider callback | Record exact version/lock/source identities and actual command lines; target mismatch/missing config refuses writes; clean install/start with unchanged locks; genuine Entra callback qualification remains distinct from local password fixtures | 1.1 environment; real callback/device proof by 1.7 |
| ID-A | Verified Identity schema ownership/baseline and supported legacy writer inventory | Clean/adopt migration rehearsal and rollback/recovery; no dual migration authority or lost existing references; previous-release compatibility or planned maintenance evidence | Shared ID-B/Access foundation |
| ID-B | Stable account actor without person/employment, current membership projection/new-ID rejoin, protected per-owner operator execution binding | Restricted-role mapping/current-account tests; retire/rejoin/delayed commands; spoofed actor/runtime operator denial; supported legacy UUID/text references preserved; exact DDL/privilege/operator invocation matrix | 1.1; target setup 1.3 |
| ACCESS-A | Register kdg_capture, nine exact organization capabilities, read.own entry, explicit two-role bundles/global/Khula admission and membership-bound grants | Typed owner command input/result/expected-state fixtures; wrong-scope/target/membership rejection; compact atomic receipt/evidence and partial recovery; registry rows alone do not prove access | ACCESS-B and initial setup |
| ACCESS-B | Closed KDG own_account/organization response, no person requirement, fixed-org caller policy, narrow target list/check and separate setup verifier | Full shared variant/negative matrix; real current-check path; KDG request binding, target retirement/race/unavailability; retained Leave/PtS/mixed-scope contract compatibility and coordinated activation | 1.1 entry; point check 1.3; runtime list 5.2 |
| P1/SERVICE | Existing generator's one versioned recipe/schema and coherent web/API/service skeleton; explicit fixed-org vs selected-org options, safe errors/client and custom extensions | Generation/regeneration into disposable output; unsupported recipe refusal, custom code survives, declared dependencies only, type/build/start/API/browser checks with real narrow Access boundary; commands in shared addendum must actually exist | 1.1; no domain editor generated |
| WRITE | Restricted owner DB context/RLS/constraints, safe errors and atomic conditional mutation/audit/outcome; KDG first committed request wins | Actual runtime/operator/migrator roles; rollback/replay/no-op/concurrency/lost-response proof; safe error fixtures; changed-body replay/original-target authority/frozen-snapshot cases; business-data restore; controlled owner migrations/old-version evidence | Domain write substrate before 1.3/1.4 persistence and 1.6 sync |
| Owner initial setup (ID-B, ACCESS-A, KDG 1.3) | Verified account/profile/actor/Khula membership/grants, then KDG initial questionnaire/child/assignment using current trusted point check | Explicit synthetic target and expected state; same-operation recovery after one owner commits/next fails; user effective entry plus own version/child reads; no name/email account matching | 1.1 shared entry then 1.3 app setup |

WRITE's neutral proof can use the existing reference contract; KDG provides its
domain command evidence in consuming stories. KDG does not wait for People, Content,
notification workers, full Leave planning, complete questionnaire editor, invitation
automation, launcher publication or hosted verification app. A shared owner may finish
the bounded KDG substrate before its broader Leave item, with explicit evidence and no
claim that all Leave acceptance is complete. No incompatible live Access/Identity
intermediate version is authorized by that split.

## First consumer and later gates

KDG 1.2/1.5/1.6/1.7 prove shell-only PWA caching, atomic explicit local Save/reopen,
account/org partition, immutable queue identity/current-authorized sync and actual
installed Android/iPhone use. Promote neutral helpers/tests through retained builder/UI
owners within those consuming items. E2 proves ordered edits/claims/conflicts; 5.3
proves the concrete changed-format upgrade pair. Do not add a generic offline service,
mandatory adapter or unfinished observation draft. Update first, then sync.

Before pilot, 5.4 names Khula processing/privacy/device and business/audit/pending/locked
retention/disposal owners, and release provides coordinated KDG migrations, prior-version
payload/schema compatibility, activation blocking, data+key backup/restore and recovery.
Seven-day access/30-day download are not retention limits. Physical Android/iPhone
evidence is delivery acceptance, not a prerequisite to authoring the first code test.

## Impact decisions

Scaffold: existing P1/SERVICE/WRITE owners update recipe/schema/templates and disposable
fixtures once proven; no parallel generator. Shared UI: proven auth/error/status/update
primitives only; KDG renderer/domain remains app-local. Agent context: no root rule
change needed; generated app instructions gain actual commands/selected pattern limits
in their consuming item. Documentation: mutable shared contracts plus this navigation/
acceptance packet; model/OpenAPI authority replaces seed shapes during Build. ADR:
accepted ADR-0061 partially supersedes ADR-0012 for current KDG only; no existing accepted ADR edited. Every consuming delivery
still records its own five required impact decisions.

## Readiness distinction and next work

**Current planning readiness: PASS, 2026-10-14.** Ownership and ENV/P1/SERVICE,
Identity/Access and WRITE selections are now concrete in their owner contracts.
The original acceptance/timing rows above remain delivery obligations, not unresolved
planning choices. [Owned WRITE](../../../platform/docs/architecture/contracts/owned-write-and-secret-execution.md)
closes outcome/evidence/role/recovery inputs; ADR-0061 defers KDG fingerprint secrets. Earlier checkpoint paragraphs
below retain historical progression. Runtime target/adoption/qualification, actual
locks/images/credentials/restore and real-data policies remain their consuming gates.

The user has separately approved bounded shared-foundation implementation. Continue
bmad-build for ordered shared foundations, acceptance failure first then focused TDD.
No whole-Leave planning wait, duplicate shared story, deployment or pilot permission.


ENV/P1/SERVICE selection checkpoint, 2026-10-14: user chose newest stable versions,
including TypeScript7.0.2; existing PtS locks no longer cap the planning baseline.
[Exact direct versions](../../../platform/docs/architecture/contracts/scaffold-dependency-baseline-2026-10-14.md)
and [environment/generation contract](../../../platform/docs/architecture/contracts/scaffold-environment-and-generation.md)
now record command/target/schema/pattern/extension/seed ownership. Those selections
supersede the earlier unspecified-version/invocation entries above. Actual owner locks,
full resolution/images, callback/device qualification and PtS/shared stability remain
separately authorized delivery evidence. Identity/Access/WRITE execution contracts are
the next readiness closure; no installs/code/migrations were performed.

## Identity/Access selection checkpoint — 2026-10-14

The [execution substrate](../../../platform/docs/architecture/contracts/identity-access-execution-substrate.md)
selects the KDG actor/member/registry/grant constraints, private projections, runtime/
setup/operator privileges, entry command, pre-grant verification and owner CLI/adoption
matrix. It supersedes earlier unspecified physical input rows for this bounded foundation.
Actual target/ACL/clean-adopt/PtS transition proof is later delivery. WRITE outcome/evidence
and secret configuration are the next planning closure; wider Leave/People work stays separate.


Final WRITE checkpoint: independent fixes/rechecks complete, planning implementability
PASS. Existing owner items retain all common work; no runtime or secret execution occurred.


## Bounded ID-B profile protected columns — 2026-10-20

Identity revision8 narrows authenticated profile writes through exact column ACLs:
INSERT(id,username), UPDATE(username,deleted_at). Existing RLS/SELECT absence, Auth hook,
shared audit routines, postgres seed authority and trusted service_role rights remain.
The new independent profile reference preserves all seven prior revisions/references.
See [profile evidence](../../../services/access/PROFILE_FIELDS_EVIDENCE.md) for actual head7 characterization, synthetic role/upgrade/
rollback verification and review. This is no account provisioning or lifecycle redesign;
remaining Identity/Access/WRITE and server KDG remain gated. No real account or production
change, new dependency/service/generator or resource removal.


## Bounded ID-B legacy role lookup — 2026-10-20

Revision9 fixes the existing public.get_user_roles() ambiguity and requires its exact
current account/org/member binding with active profile/organization/membership/role.
Its existing no-argument role:string contract, owner and exact ACL remain; canonical
source PUBLIC defaults are not normalized to uninspected deployment differences.
See [role lookup evidence](../../../services/access/LEGACY_ROLE_LOOKUP_EVIDENCE.md) for actual source-bound characterization/currentness/
upgrade/rollback proof and review. Auth hook, membership lifecycle/uniqueness/CASCADEs,
account verification adapter and Access/WRITE/KDG remain separate gates. No new role,
credential, dependency, runtime service or generator; historical8 references/revisions
and all concurrent documents/resources remain preserved.

## Existing token-hook organization safety — 2026-10-20

Identity revision10 excludes retired organizations from the legacy Auth hook's fallback,
membership/role/owner authority and org_ids. Existing explicit selection and metadata
sourcing remain; JWT claims are never current Access authority. Reviewed restricted-role/
migration matrix PASS30.111s;577 affected tests and both composers PASS. All three review
layers complete, no deferrals. See [evidence](../../../services/access/TOKEN_HOOK_EVIDENCE.md). Membership
lifecycle, seed/direct-writer compatibility, live-account adapter, Access/WRITE and server
KDG remain delivery gates; no full ID-B or shared readiness claim.

## Immutable retained membership binding — 2026-10-20

Identity revision11 rejects changes to existing member id/org_id/user_id through the
existing revision guard. Mutable revision/seed behavior and function owner/ACL stay.
Final actual matrix PASS29.541s;649 affected tests and both composers PASS. Three
review layers complete with no deferrals. See
[evidence](../../../services/access/MEMBERSHIP_BINDING_EVIDENCE.md). This does not complete
retirement/rejoin/uniqueness/CASCADE or owner-command work, live-account verification,
Access/WRITE or server KDG. Historical sources/references and concurrent work stay.

## Membership history retention — 2026-10-20

Identity revision12 restricts the three legacy member/org/profile/role cascade links and
protects member DELETE/TRUNCATE without new grants. Reviewed actual matrix PASS42.081s;
715 affected tests and both composers PASS, three review layers complete, no deferrals. See [evidence](../../../services/access/MEMBERSHIP_RETENTION_EVIDENCE.md).
Original Auth FK and mutable/seed/read behavior stay. Retirement/rejoin/uniqueness, owner
commands/live-account verification, Access/WRITE and server KDG remain delivery gates;
no broader readiness or live-target activation claim. Historical/concurrent work stays.


## One-way membership retirement —2026-10-20

Revision13 adds a guard against retired-member reactivation/retiming; active seed/read
behavior remains. Retired seed upserts deliberately refuse. See
[evidence](../../../services/access/MEMBERSHIP_RETIREMENT_EVIDENCE.md). Reviewed actual matrix
PASS35.569s;766 affected tests/both composers PASS, three reviews complete, no deferrals.
Uniqueness/rejoin/seed transition, authorized lifecycle commands/protected
writers, live-account verification, Access/WRITE/server KDG remain gated.


## Staged active-membership index —2026-10-20

Revision14 adds the partial active-member unique index while retaining full uniqueness
and legacy writers. See [evidence](../../../services/access/ACTIVE_MEMBERSHIP_INDEX_EVIDENCE.md).
Reviewed actual matrix PASS46.265s;846 affected tests/both composers PASS, three reviews
complete, no deferrals. Historical duplicates/rejoin remain unavailable on canonical14;
owner commands/seeds/compatibility must be coordinated before full-constraint removal.
Access/WRITE/server KDG and real-target activation remain gated.


## ID-B membership actor-attribution staging — 2026-10-21

Revision15 prepares the existing membership table with nullable durable actor references,
RESTRICT FKs and guarded owner-only changes; populated creation actor is immutable.
Legacy attribution/timestamps, uniqueness, seeds and existing runtime contracts stay.
Unknown historical references remain null pending verified adoption, without inferred
System actors. Changed owner backfill advances revision. This does not activate
retirement/rejoin, Access/WRITE or server KDG; scoped owner commands/audit/outcomes and
protected writers remain next. See
[Build/evidence](../../../_bmad-output/implementation-artifacts/spec-id-b-membership-actor-attribution.md).

Reviewed actual revision15 matrix PASS47.815s;936 affected tests/both composers PASS.
All three independent reviews complete; findings resolved without deferrals. Retain
all prior frames and the new synthetic attributed repeat fixture. Commands and real
adoption/Access/WRITE/server KDG remain separate gates.


## Bounded ID-B protected retirement — 2026-10-21

Revision16 implements the exact organization/account/member/revision retirement command,
server actor/time, atomic immutable event/outcome, current-authority replay and scoped
CLI recovery. Actual restricted-session, concurrency/revocation, event/DDL rollback,
clean/adopt/head15 preservation and original actor-command regression proof pass.
[Build/evidence](../../../_bmad-output/implementation-artifacts/spec-id-b-membership-retire-command.md)
retains exact verification and independent review status. Full uniqueness remains;
new-ID joining/rejoining, account verification/mapping, Access/WRITE and KDG server
implementation/activation remain separate prerequisites. Synthetic receipts prove only
their owner-local changes; they do not prove consumer readiness or authorize real data.


## Bounded ID-B join/rejoin and seed cutover — 2026-10-21

Revision17 delivers protected first join/explicit rejoin and scoped recovery, fresh IDs,
empty copied roles/grants and atomic owner evidence. Direct inserts/owner changes refuse;
full uniqueness is removed, active uniqueness/history retained. Demo seeding refuses;
owned composition uses --no-seeds and rejects stale output.984 tests, both composers and
actual runtime proof pass; three reviews complete. See
[Build/evidence](../../../_bmad-output/implementation-artifacts/spec-id-b-membership-join-command.md).
Source seeds/history and archived generated outputs remain preserved. Current Access
still matches org/account grants and is incompatible with rejoin activation: separate
ACCESS-A/B membership binding/consumer proof is mandatory. Live account verification/
account_actor.ensure, Access/WRITE and server KDG remain gated; no real-target activation.

## ACCESS-A application enablement input only — 2026-10-21

The existing Access parser now accepts strict typed `application.set_enabled` input
with platform scope, actual boolean enabled and positive canonical bigint revision.
[Input evidence](../../../services/access/APPLICATION_ENABLE_INPUT_EVIDENCE.md) records
parser/registration compatibility and preconnection owner/adapter/CLI/worker/outcome
refusals. Execution remains closed pending mutable application storage and protected
revision/evidence guards. No application is enabled, grant issued or consumer activated;
ACCESS-A/B and KDG delivery gates remain open requirements. Historical runtime proofs
remain source-bound and do not qualify these new parser bytes.

## ACCESS-A protected application enablement — 2026-10-21

Access0007 delivers the protected mutable command after the input-only checkpoint.
Exact authority/revision and server attribution guard row/outcome/before-after evidence
atomically; unchanged preserves the row and disable/re-enable retains grants/mappings.
Reviewed synthetic verification passed:39 native stages, separate retained inspection,
real CLI recovery,1264 affected tests and both composition checks. The native run stopped
normally with all data/resources retained. See [evidence](../../../services/access/APPLICATION_SET_ENABLED_EVIDENCE.md).
Organization enablement, grant commands, effective authorization and coordinated consumer
activation remain separate gates; no real-target access/configuration change is claimed.

## ACCESS-A organization application input only — 2026-10-21

Strict `organization_application.configure` parsing now requires explicit organization
scope and exclusive create (`expected_absent: true`) or update (`expected_revision`)
payloads. Exact booleans, UUID spelling and bigint revision strings are preserved in
frozen redacted records. Existing platform inputs remain platform-only. Three review
lenses completed;1312 affected tests and both composition dry runs pass; [input evidence](../../../services/access/ORGANIZATION_APPLICATION_INPUT_EVIDENCE.md)
records commands and pre-I/O refusal tests. Organization storage, external verification
and execution remain undelivered; no organization is configured or consumer activated.
ACCESS-A/B, grants and coordinated PtS/KDG gates stay closed. Historical runtime proofs
remain source-bound; no native qualification or readiness claim is made.


## ACCESS-A private organization application storage — 2026-10-21

Access0008 stages empty organization/application storage with composite identity,
RESTRICT app reference, finite attribution, positive revision and owner-only forced
organization RLS. Owner fixture helpers set transaction-local context; runtime/operator
access and all updates/deletes/truncates remain closed. External identifiers are not
verified by storage. No effective admission or grant is created.

Three review lenses completed; confirmed findings were patched. Fresh15-stage native
proof, separate retained inspection,1320 affected tests and both composition checks pass.
All82 source bindings match. The native run stopped normally with data retained; both
failed frames and all historical proof remain. See
[evidence](../../../services/access/ORGANIZATION_APPLICATION_STORAGE_EVIDENCE.md) for
exact commands, requirement traceability, custody and five impacts. Existing bootstrap
portability remains deferred; concurrent work and historical migration/reference bytes
are preserved. Next deliver external organization verification and protected configure
execution. ACCESS-A/B, grants, effective authorization and coordinated PtS/KDG activation
remain gated; no Leave/editor, production/pilot or deployment work is included.


### Private Identity organization verification — 2026-10-21

Identity0019 adds a private account-free exact active-organization point check for
staged Access setup. It reuses existing target ownership, RLS and table privileges;
only access_command_owner gains EXECUTE. Invalid/mixed context returns no row. Context
settings remain trusted backend assertions; no command authority or access is inferred.
Access remains at8 and organization_application.configure execution stays closed.

Three review lenses completed; confirmed verification/fixture findings were patched.
Fresh15-stage native proof, independent retained inspection,1338 affected tests and
both composition checks pass. All108 source bindings match; protected historical bytes
and concurrent work remain preserved. The native run stopped normally with all data
retained. See [evidence](../../../services/access/ORGANIZATION_TARGET_VERIFICATION_EVIDENCE.md)
for commands, failed-frame disposition, requirements and five delivery impacts.

Next implement protected organization configuration through existing Access owner tools,
with exact current command/org/app authority, pre-lock Identity observation, revision,
attribution and atomic evidence/retry safeguards. Grants, ACCESS-B, effective admission
and coordinated PtS/KDG activation remain separate gates. No Leave/editor or real-target,
production/deployment/pilot change is included. Existing bootstrap portability stays deferred.


### Protected organization application configuration — 2026-10-21

Access0009 implements `organization_application.configure` through the existing
restricted owner adapter/CLI. Exact current command/org/app authority, Identity19
active-organization verification, expected absence/revision, server attribution and
atomic row/outcome/event evidence protect writes. Scoped retry and historical receipt
recovery are implemented; configuration alone grants no effective application access.

Three independent review lenses completed and all confirmed findings were patched.
Fresh16-group native proof, independent retained inspection,1348 affected regression
tests and both composition modes pass; all160 source bindings match. Previous8 clients
and all four existing commands work across9, with populated receipts preserved. Seven
late-wait cases prove bounded expiry and full rollback. See
[evidence](../../../services/access/ORGANIZATION_APPLICATION_CONFIGURE_EVIDENCE.md) and
[runbook](../../../services/access/ORGANIZATION-APPLICATION-CONFIGURE.md).

Next select the remaining bounded Access grant/admission prerequisite from the current
owner contract. ACCESS-B, effective admission, membership-binding/consumer gates and
coordinated PtS/KDG activation remain separate; do not infer readiness from configuration.
No real account/access, production, deployment, pilot, Leave or editor change is included.
Historical resources/data and concurrent work remain preserved. Existing private-bootstrap
portability remains deferred; no new review deferral was introduced.

The synthetic native run stopped normally with data retained; no reset/prune occurred.


### Strict organization grant assignment input — 2026-10-21

The existing Access parser now prepares `grant.assign` with exact organization/account/
member binding, literal permission and exclusive expected absence/revision variants.
Inputs are immutable and redacted; all execution/lookup/worker boundaries remain closed
before target/connection/dispatch. Parsing grants no authority or access. See
[evidence](../../../services/access/GRANT_ASSIGN_INPUT_EVIDENCE.md).

Next stage the required grant revision/attribution/scope integrity and exact Identity
pre-grant verification through existing owners before protected assignment execution.
ACCESS-B, membership-bound effective checks and coordinated PtS/KDG activation remain
gated. No native startup or real-target changes are included. Existing bootstrap
portability stays deferred; preserve historical source/evidence and concurrent work.

Final oneshot review complete: six documentation/verification findings patched, none
deferred.234 focused and1434 affected regression tests plus both composition checks
pass.109 current source bindings match;50 protected sources and all concurrent bytes
remain preserved. No native startup or additional runtime readiness claim.


### Staged organization grant lifecycle storage — 2026-10-22

Access0010 adds organization scope, revision and nullable revocation/actor/update fields
without backfill, preserving original grant IDs/values/creation attribution, membership,
legacy permission CHECK, owner writers, forced RLS and ACLs. Null attribution remains
unverified history. It does not verify targets, execute assignments or activate access.
See [owner evidence](../../../services/access/GRANT_LIFECYCLE_STORAGE_EVIDENCE.md) and
[runbook](../../../services/access/GRANT-LIFECYCLE-STORAGE.md).

Three review lenses complete: eight confirmed findings patched, one disproved, no new
deferral. Fresh23-group native proof, separate retained inspection, independent runtime
reads,1446 affected tests and both composers pass.164 source bindings/32 generated-log
digests match;79 baseline source files independently match Git. All historical resources,
data/receipts,51 protected sources and concurrent work remain preserved. Private-bootstrap
portability stays an existing follow-up, not portable CI readiness.

Next deliver exact Identity pre-grant account/member verification and protected Access
assignment through existing owner contracts. Registry adoption/permission FK/final
active-row guards, membership-bound readers, ACCESS-B and coordinated PtS/KDG activation
remain gates. Existing v1 does not become safe for real rejoin/grant activation merely
because these fields exist. No real-target, production/deployment/pilot, Leave/editor,
reset/prune or push follows from this synthetic item.

The native run stopped normally with data/volumes/receipts retained; no reset/prune.


### Existing Identity pre-grant target dependency — 2026-10-22

The existing `identity.organization_account_target(uuid,bigint)` already supplies exact
account/member/revision/actor/display-name evidence to the Access command owner.
Current-head consuming qualification adds no production function, migration or privilege.
It exercises supported synthetic Identity ensure/join/retire/rejoin and actual restricted
Access logins. Context remains a trusted backend assertion; the read grants no authority,
checks no live Auth, and supplies no lasting membership guarantee.
See [evidence](../../../services/access/IDENTITY_PREGRANT_TARGET_EVIDENCE.md) and
[runbook](../../../services/access/IDENTITY-PREGRANT-TARGET.md).

Next select the bounded protected assignment prerequisite from the owner contract.
Registry adoption/permission FK/final active-row integrity, protected grant execution,
membership-bound effective readers, ACCESS-B and coordinated PtS/KDG activation remain
gates. Existing v1 is not safe for real rejoin/grant activation from this proof alone.
No real account/access, production/deployment/pilot, Leave/editor, reset/prune or push.
Private-bootstrap portability remains deferred; preserve historical frames/data and
concurrent documents. The approved dependency baseline including TypeScript7.0.2 stays.


Final reviewed proof passes all8 native groups and independent read-only retained
inspection,13 focused safeguards,1459 affected regression tests and both composition
modes. All123 source bindings and3 generated-log digests match. Three independent review
lenses completed; seven findings patched, two low-value expansions rejected, no new
deferral. All75 production sources and52 protected historical files remain unchanged.
The native run stopped normally with data retained; concurrent work and earlier frames
remain preserved. This completes consuming proof of the existing dependency only.


### Compatible organization grant registry integrity — 2026-10-22

Access0011 replaces the legacy permission CHECK with a small derived registry bridge:
exactly three legacy PtS permissions retain their original rows/writes without invented
registry adoption; every other grant permission must be registered with organization
scope. Active nonlegacy rows require membership and actor/update provenance. Original
columns/values, RLS and ACLs remain; no grant-write privilege or execution is enabled.
See [evidence](../../../services/access/GRANT_REGISTRY_BRIDGE_EVIDENCE.md) and
[runbook](../../../services/access/GRANT-REGISTRY-BRIDGE.md).

Next implement protected `grant.assign` through existing Access owner tools: exact current
command/org/app/target authority, bounded pre-lock Identity observation, expected state,
server revision/attribution, atomic receipt/event and retry safeguards. Exclude the three
legacy PtS literals while v1 ignores membership/revocation. The temporary discriminator
is removed only with coordinated legacy adoption and final direct-FK/global integrity.
ACCESS-B, membership-safe effective readers and coordinated PtS/KDG activation remain
gated. No real access, production/deployment/pilot, Leave/editor, reset/prune or push.


Final reviewed acceptance: all8 native stages, independent read-only retained inspection,
13 focused safeguards,1472 affected regression tests and both composition modes pass.
All116 source bindings/21 generated diagnostic digests and retained-state digest match.
Three review lenses complete;11 findings addressed, no new deferral. Original migration/
reference and client bytes remain preserved; only intended mutable verifiers and new11
DDL change production source. The native run stopped normally with data retained.
Historical frames/resources and concurrent work remain preserved. Private bootstrap
portability remains an existing follow-up; no effective access or live activation claim.
