# Minimum shared-owner prerequisite work for KDG

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
| WRITE | Restricted owner DB context/RLS/constraints, safe errors and atomic conditional mutation/audit/outcome; KDG HMAC/JCS boundary | Actual runtime/operator/migrator roles; rollback/replay/no-op/concurrency/lost-response proof; safe error fixtures; JCS/rotation/missing-key/restore cases; controlled owner migrations/old-version evidence | Domain write substrate before 1.3/1.4 persistence and 1.6 sync |
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
existing accepted decisions suffice, no accepted ADR edited. Every consuming delivery
still records its own five required impact decisions.

## Readiness distinction and next work

**Current planning readiness: PASS, 2026-10-14.** Ownership and ENV/P1/SERVICE,
Identity/Access and WRITE selections are now concrete in their owner contracts.
The original acceptance/timing rows above remain delivery obligations, not unresolved
planning choices. [Owned WRITE](../../../platform/docs/architecture/contracts/owned-write-and-secret-execution.md)
closes outcome/evidence/role/recovery and secret inputs; earlier checkpoint paragraphs
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
