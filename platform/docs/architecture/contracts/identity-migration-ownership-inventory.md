# E1 identity and migration ownership inventory

**Leave acceptance update — 2026-10-26:** The user approved reuse of this existing
hardened sequential history as Leave's ID-A foundation. The earlier independent-ID-B
acceptance question below is resolved; no separate pre-ID-B history is required.
ID-B behavior, fresh current-head/provider qualification and live activation remain
separate delivery obligations. Historical migration/reference bytes are unchanged.

**ID-B review closure — 2026-10-26:** All17 review findings corrected. Revisions22/23
retain inherited Studies role/source checks; preferences structurally bind account/actor
attribution and expose typed existing error contracts. Fresh native proofs and1,996
source-bound tests pass; earlier candidate frames remain evidence. No downstream Access
grant integration or live activation is implied.

**ID-B delivery — 2026-10-26:** Additive revisions22/23 now supply independent
person links and own-account language persistence. Fresh synthetic Leave-local native
proof covers current clean bootstrap, supported legacy adoption preserving original rows,
previous21 upgrade/repeat, exact rollback/forward retry, restricted roles, membership
transitions and release failure gating. See [ID-B evidence](../../../../apps/leave/docs/testing/e1-identity-links-preferences-evidence.md).
Historical statements below describe their original frames. Current live-target/provider
qualification, Access grant integration and activation remain gated.

**Current-state qualification — 2026-10-26:** The original inventory/design below is
historical. Existing owner delivery now supplies the separate Identity history through
`identity_0021`, guarded clean/adopt/reference checks, explicit composer handover and
Identity-first coordinated failure gating. Revision0001 alone retained unsafe legacy
profile/helper behavior; delivered0008/0009/0010/0020 subsequently narrow profile writes,
bind legacy role lookup, filter current membership/organization claims and restrict
six sensitive callable routine ACLs. See the [owner runbook](../../../../services/access/IDENTITY-MIGRATIONS.md)
and [Leave criterion/evidence mapping](../../../../apps/leave/docs/testing/e1-identity-baseline-evidence.md).
Their retained synthetic database proofs do not establish live-target equivalence or
fresh current-head database qualification. Leave's strict independent-of-ID-B acceptance
remains open; no ID-B completion or application activation follows from this inventory.

Default composition remains legacy; the supported owned check is
`python3 tools/py/run_compose_supabase.py --identity-authority owned --no-seeds --check-only`.
Owned composition excludes exactly the six inventoried Identity DDL sources, retains
other owners and refuses legacy/stale seed execution. The existing coordinator's
`--identity` option orders Identity before Access/Content/PtS and blocks dependents on
failure. Later dated delivery entries supersede original statements below that these
routes or privilege corrections are only proposed; historical evidence is retained.

KDG execution closure, 2026-10-14: [Identity/Access substrate](identity-access-execution-substrate.md)
selects KDG-relevant physical actor/member/registry/grant constraints, current/target
projections, restricted role/command schema and owner CLI/adoption matrix. These refine
earlier unspecified DDL/privilege/command passages below; no objects or grants are applied.
Existing PtS/Leave scope and source-owned migration history remain. Actual target baseline/
rehearsal is later delivery evidence, not presumed equivalence.

**Status:** Repository inventory and adoption design; target baseline verification open  
**Date:** 2026-10-04  
**Owners:** Identity/Access maintainers; consuming E1-ID, E1-ACCESS and E1-ENV

This refines the [shared identity contract](./identity-access-employment-e1.md#identity-adoption-and-small-cohort-transition--2026-10-01)
under accepted ADR-0042/0045 and migration ADR-0015/0016/0020. Evidence is current
working-tree source, including uncommitted planning changes. No database was inspected
or changed. The user's three noncritical PtS users and read-only PtS/Scribeswell scope
remain the adoption assumptions; source references do not prove production data exists.

## Source-owned objects and successors

Paths below are repository-relative. A successor owner describes the planned authority,
not a migration already performed. Tables include their indexes, sequences/constraints,
RLS policies and grants; routines include execution grants and attached triggers.

| Source | Existing objects / dependency | E1 disposition and successor |
| --- | --- | --- |
| `platform/supabase/migrations/20250815110000_platform_create_identity_schema.sql` | `identity.users`: Auth-account UUID PK/FK, username, actor_key, is_system, soft deletion, self-referencing actor columns. `identity.org`: UUID, name/slug/settings and attribution. | Identity-owned baseline. Keep account profiles and organizations where possible; `identity.users` is not an employee master. Add independently identified people, verified account links and durable person/service actor mappings through the identity owner. Do not reinterpret all profile rows as employees. |
| Same source | `identity.app_role`, `identity.app_permission`, `identity.role_permissions`, initial role-permission inserts; `identity.authorize(permission)` and `identity.current_org_id()` | Identity owns legacy objects until explicit retirement. Access owns new live app admission/capabilities. Preserve the legacy consumer bridge deliberately; do not turn the `employee` role or JWT claims into People employment or new Leave authority. |
| Same source | `identity.handle_new_user()`, `on_auth_user_created` attached to `auth.users`; `identity.create_user(email)` test helper; profile RLS and broad schema/default privileges | Identity owns project-created hook/helper/grants, not Supabase's Auth tables. Verify function owners/search paths/execute grants, profile column privileges and trigger behavior during baseline adoption. Do not copy a helper that inserts Auth rows into application provisioning. Use supported Auth administration for real accounts. |
| `platform/supabase/migrations/20250815210000_platform_multitenancy_orgs.sql` | Adds `identity.users.is_platform_admin`; creates `identity.org_member` (bigint ID, unique org/account), `identity.member_role`, `identity.current_member_id()`; replaces `authorize` and token hook; organization/member RLS and grants | Identity baseline owns physical legacy membership/role structures. Access enforces current membership and exact grants; new authorized administration is E2. Preserve account-specific grants and bigint-as-string wire representation. |
| `platform/supabase/migrations/20250815150000_platform_auth-hook.sql` plus later multitenancy replacement | `identity.custom_access_token_hook(jsonb)`; auth-admin privileges | Adopt the final effective definition, not both files as competing authorities. Keep supported legacy claims only for explicit consumers; new Access checks query current authority. Invalid/stale selected-org metadata, deleted membership/org and empty roles require fixtures. |
| `platform/supabase/migrations/20250815180000_platform_add_get_user_roles_function.sql` | `public.get_user_roles()` reads legacy member roles using JWT member_id | Identity owns this compatibility routine despite its public schema. Inventory consumers and explicit execute grants before retaining/replacing/removing it. Do not exclude it from adoption just because it is outside `identity`. |
| `platform/supabase/migrations/20250815160000_platform_create_audit_log_tbl.sql` | `identity.audit_log`, `identity.log_audit()`, identity audit-log triggers | Identity-owned legacy evidence and routine. Routine captures row contents/diffs; not the new shared draft logging/audit default. Retain only required compatibility consumers until owner-local adoption; do not copy full-row snapshots into Leave outcomes/audit. |
| `platform/supabase/migrations/20250815170000_platform_create_audit_triggers.sql` | `identity.set_audit_fields()` and identity attribution triggers | Identity-owned compatibility routine, with cross-owner consumers below. New backend attribution uses verified execution context under ADR-0025; JWT-specific legacy trigger behavior is not proof of safe service attribution. |
| `services/access/migrations/versions/0001_initial.py` and `migrations/env.py` | `access.grants`, org-scoped forced RLS, runtime SELECT; `access.alembic_version`; permission CHECK limited to three PtS permissions; created_by is text | Keep Access history separate. Extend its permission/admission model and compatible attribution deliberately for E1-ACCESS. Never add identity tables to this migration history just because Access consumes them. Schema filter is not a privilege barrier; owner-role tests remain required. |
| `services/access/tools/identity_bridge.sql` | Identity schema/column SELECT grants and policies for `access_runtime`, scoped by transaction organization/actor | Identity-owned integration change currently stored with Access. Move its execution responsibility into the identity adoption plan; do not independently replay this non-idempotent policy-creation script. Current bridge cannot supply pre-selection discovery; add narrow caller-scoped discovery authority in the identity owner. |
| `platform/supabase/seeds/001_identity.sql` | Synthetic Auth-backed system/migrate profiles, one organization, owner membership and admin role | Legacy seed, not the future service-actor design or production membership plan. E1-ENV uses controlled synthetic fixtures; ID defines explicit durable service actors without manufacturing employees. |
| `supabase/config.toml` | Enabled Auth token hook; exposes identity/finance/cs through the Data API; seed glob | Deployment/configuration owner coordinates with Identity. Keep existing consumers deliberately compatible, while new Leave/People use owning HTTP APIs and restricted DB credentials. Do not expose new person/link/actor or employment tables by inheriting broad legacy grants/default privileges. |

## Receipt app and other dependent sources

The receipt application is `apps/expense`; its database schema is `finance`. The
inspected schema creates expense_category, expense_type, currency, receipt and purchase,
not a separate employee table. `finance.purchase.user_id` references `auth.users`;
finance attribution columns reference `identity.users`, and organization columns
reference `identity.org`. Its RLS calls identity authorization/context helpers, and its
audit triggers call `identity.log_audit()` / `identity.set_audit_fields()`.

Evidence: [finance schema](../../../../apps/expense/supabase/migrations/20250815130000_finance_create_schema.sql),
[policies](../../../../apps/expense/supabase/migrations/20250815140000_finance_tables_policies.sql),
[audit log triggers](../../../../apps/expense/supabase/migrations/20250815161000_finance_create_audit_log_tbl.sql),
[attribution triggers](../../../../apps/expense/supabase/migrations/20250815171000_finance_create_audit_triggers.sql).
The existing [purchase client](../../../../apps/expense/web/src/services/finance/purchase.service.ts)
filters purchases by user_id; that reference must not silently change meaning to an
employment ID. Future Expense adoption chooses explicit person/employment/account
semantics per field through its own API and People contracts. Under ADR-0045 no old
receipt/purchase conversion is required, but E1 does not authorize dropping finance
objects or breaking the repository's supported clean bootstrap.

Legacy `cs` content-type/store attribution also references identity profiles in
`platform/supabase/migrations/20250815120000_platform_create_content_system_schema.sql`.
This is a structural dependency to preserve or explicitly adopt; it does not introduce
a PtS/Scribeswell user-document migration against the user's stated read-only scope.
No blanket removal of the old identity source files is safe merely because Expense
has no production history.

## Existing execution paths

- [Composer](../../../../tools/py/run_compose_supabase.py): by default includes platform
  and all app Supabase modules. `--apps` narrows app selection, not platform objects;
  `--no-platform` removes all platform assets, not just adopted identity objects.
  Current options do not implement a selective identity ownership handover. Generated
  `supabase/migrations`, seeds/functions and manifest are outputs, never hand-edited.
- [Access Alembic environment](../../../../services/access/migrations/env.py): uses
  ACCESS_MIGRATION_DATABASE_URL and access.alembic_version. Its initial migration
  expects roles/schema bootstrap separately and refuses destructive downgrade.
- [Access manifest](../../../../services/access/deployment/manifest.json): declares
  access_migrator and Access's migration config, but `depends_on` is currently empty.
  The SQL bridge/identity prerequisite must be represented in coordinated setup before
  extending this for Leave; a healthy process alone does not prove identity readiness.
- [Existing PtS coordinator](../../../../tools/py/deploy_pts.py): explicit owner list
  access/content/pts; no identity or People history is registered. Extend existing
  coordination for the selected delivery path, do not add a competing release runner.

## Bounded adoption plan

1. **Verify the selected baseline.** At delivery, inventory target objects, definitions,
   ownership, grants/default privileges, dependencies and applied migration history.
   Compare to the source inventory, including the public routine and Auth-attached
   trigger. Record mismatches; do not stamp an unverified schema as equivalent.
2. **Establish one identity history.** Planned layout: `services/access/identity-migrations/`
   with separate `identity-alembic.ini`, `identity.alembic_version`, identity_migrator
   and IDENTITY_MIGRATION_DATABASE_URL. This is a proposed concrete placement under
   the existing maintainer, not a second runtime identity service or new Access table
   authority. Role permissions must cover only declared identity-owned objects and
   approved integration hooks. Verify least-privilege hook setup against Supabase.
3. **Provide both setup routes.** A clean disposable database creates the owned identity
   baseline once; an existing database adopts only after verified equivalence or
   explicit repair. Coordinate identity before Access bridge/migrations and People,
   and before dependent legacy finance/content bootstrap. Preserve immutable existing
   migration evidence; do not blindly rerun historical CREATEs or edit generated output.
4. **Retire duplicate execution.** Update composer source selection/bootstrap manifests
   so adopted identity objects have one authority in each supported setup route. Keep
   mixed-source and cross-owner compatibility objects explicitly assigned. No whole-file
   deletion until every object and consumer has a disposition and clean bootstrap passes.
5. **Adopt accounts explicitly.** Prefer retaining the three Auth UUIDs; record verified
   account/person/actor links and intended memberships/PtS read grants. Manual recreation
   remains permitted if needed; preserve old actors and reject replaced-account access.
   No automatic email merge, grant union or employment creation. Leave grants and
   employment are separately provisioned only for intended users.
6. **Prove release/recovery.** Synthetic clean/adopt/recreate rehearsals, old/new Access
   contracts, actual restricted-role discovery checks, Auth hook/profile creation and
   fail-before-activation/recovery evidence. If previous-version compatibility cannot
   hold, use the already-approved planned maintenance procedure. No startup migrations
   or automatic destructive downgrade.

## Concrete checks still required

The legacy source includes PUBLIC-default SECURITY DEFINER execution, broad profile
update/default grants and an admin flag on that profile. Effective access must be
characterized and narrowed deliberately; do not infer safety from RLS names. Test
self-updates to privileged fields, arbitrary-member role lookup, Auth helper access,
search-path behavior and current-vs-stale claims. These are source-derived adoption
checks, not a claim of a verified production exploit.

The Access v1 query checks membership/org deletion and exact grants; it does not join
identity.users to check profile deletion or verify a person/actor link. E1-ACCESS must
add the agreed current account/profile/link checks for v2 and explicitly determine v1
compatibility and disabled-app enforcement. Current bridge grants also omit fields
needed for v2 membership ID/organization name, so extending wire models alone is
insufficient. New caller-scoped discovery grants need actual DB isolation evidence.

This inventory settles repository ownership evidence and proposes the concrete history
placement. Target equivalence, safe grants, migration source handover and executable
compatibility remain readiness work. No accepted ADR was edited.

## Verification and impacts

`python3 tools/py/run_compose_supabase.py --check-only` passed on 2026-10-04: 15 migration
sources (8 platform, 6 Expense, 1 Scribeswell), 2 seeds and 5 composed function directories;
no files changed. This validates composition discovery/naming, not SQL execution,
migration correctness or deployability. No dependencies installed or runtime tests run.

Scaffold: distinct owner migration history/roles, controlled setup and synthetic adoption
fixtures must be promoted where generic. Shared UI: no new component. Agent context:
existing owner/ATDD/no-startup-migration instructions suffice. Documentation: this
inventory, shared contract and Leave tracker. Existing ADRs govern; no new architectural
policy or production execution is authorized by the proposed paths.


## Actor registry adoption constraint — 2026-10-07

[ADR-0056](../decisions/0056-durable-actor-registry-separate-from-login-accounts.md)
selects the separate Identity actor registry. Preserve verified human/System/Migrate
UUIDs and historical attribution; account profiles retain Auth identity semantics.
Inventory dependent attribution FKs and deletion actions, JWT-based audit triggers,
synthetic Auth seeds and service:pts-import text writers before migration. Existing
System/Migrate Auth rows are not automatically deleted. ID-A preserves the baseline;
ID-B owns new registry/mapping/bootstrap and affected consumer handover. No live schema
or account state is inferred from these repository definitions.

## Bounded ID-A implementation — 2026-10-20

The selected separate history now exists at services/access/identity-migrations,
with identity-alembic.ini and its own pinned Python lock. Explicit owned composition
excludes the six Identity DDL sources and retains other owners; the existing coordinator
has an opt-in Identity-first route. Exact equivalent synthetic adoption verifies a
trusted compact catalog before recording the baseline, preserving business rows,
external references and original applied history. Legacy source files remain evidence.

See [owner runbook](../../../../services/access/IDENTITY-MIGRATIONS.md) and
[executed evidence](../../../../services/access/IDENTITY_BASELINE_EVIDENCE.md).
This qualifies the selected restricted-owner profile only; live postgres ownership/
PUBLIC privilege differences need separate explicit compatible disposition. Legacy
broad grants remain characterized pending ID-B, not newly accepted as safe. Actual
provider sign-in, actors/membership/current Access and production activation remain
separate gates. No startup migration, real-account change or accepted ADR edit.


## Bounded ID-B persistence implementation — 2026-10-20

Identity revision2 adds actor/account_actor without new Auth/person/employment/org
requirements, implicit seeds or runtime authority. The original baseline/source pins
remain intact; new revision-specific trusted evidence qualifies additive upgrade and
rollback. See [actor evidence](../../../../services/access/ACTOR_FOUNDATION_EVIDENCE.md).
Protected classification/provisioning/outcome commands and legacy writer/account
adoption remain separate delivery work; no live migration or account deletion follows.


## Bounded ID-B current-account projection — 2026-10-20

Identity revision3 adds only the restricted `identity.current_account_actor()` read.
Verified user/account context resolves the nullable account actor without person/org
setup; account selection ignores actor/org assertions. A dedicated NOLOGIN reader has
narrow columns, account-bound profile RLS and fixed function search_path; access_runtime
gets exact EXECUTE only. Controlled preparation requires an empty reader, sole SET-only
migration-owner membership and Auth schema USAGE delegation for the legacy policy helper.
Only isolated synthetic preparation was executed. Original migrations/references and
existing Access runtime stay unchanged; new catalog evidence is independently pinned.
See [projection evidence](../../../../services/access/CURRENT_ACCOUNT_ACTOR_EVIDENCE.md).
Provisioning, mapping adoption, membership/current Access and production remain separate.


## Bounded ID-B selected-organization projection — 2026-10-20

Revision4 adds the internal current-account organization/member/revision/nullable-actor
read using the same NOLOGIN reader. Scoped restrictive/permissive policies and narrow
columns keep ordinary runtime from raw expanded reads. The additive server revision
covers retained legacy member changes/no-ops without changing IDs, uniqueness, CASCADEs
or seed/unretire behavior. Actual prior-code/legacy writer/Access/Auth hooks and full
rollback/refusal evidence pass. See [organization evidence](../../../../services/access/CURRENT_ACCOUNT_ORGANIZATION_EVIDENCE.md).
Protected lifecycle/new-ID rejoin, FORCE-RLS/actor backfill, operator provisioning and
current Access adoption remain coordinated later gates; this read grants no admission.
Original migrations/references and writer sources remain unchanged. No live execution.


## Bounded ID-B operator input boundary — 2026-10-20

The Identity owner now validates only the four selected setup-command input shapes,
returning immutable typed requests. No migration/schema/ACL/source pin, runtime login,
provider/account/access state or Docker resource changes follow. Verification is CPU-only;
see [input evidence](../../../../services/access/OPERATOR_INPUT_EVIDENCE.md).
Input acceptance grants no execution authority. Target/current authority/expected-state
checks and durable outcomes remain the protected operator adapter's next gate.


## Bounded ID-B protected operator authority — 2026-10-20

Identity revision5 adds principal/authority records and a fixed private original-login
selection routine. Only the controlled Identity owner changes configuration; the narrow
NOLOGIN reader and separate operator login gain no business writes or other-owner rights.
Existing actor/membership/projection behavior and original source/reference evidence stay
intact. See [authority evidence](../../../../services/access/OPERATOR_AUTHORITY_EVIDENCE.md).
Protected command effects, target binding, durable outcomes/events and coordinated
membership/Access hardening remain later delivery; no live configuration is authorized.


## Bounded ID-B system actor command — 2026-10-20

Identity revision6 adds only protected actor.register_system execution and original
receipt recovery, a separate restricted command owner, and Identity-local immutable
operation_outcome/business_event with forced executor-scoped RLS and RESTRICT links.
Existing migrations1–5, source/reference pins, account map and membership semantics
remain intact. Actual synthetic operator LOGIN/atomicity/retry/concurrency/authority/
structural/prior-head5/rollback proof passes:27 reviewed-source stages and330 affected
tests, with three-layer review/patches complete and no deferrals. See
[command evidence](../../../../services/access/ACTOR_COMMAND_EVIDENCE.md).
No operator CLI/target factory or account ensure/membership command is delivered.
Callers supply explicit prepared idle connections and bounded transport configuration;
full Identity/Access/WRITE/KDG readiness and live adoption remain separate gates.


## Bounded ID-B prepared operator target — 2026-10-20

A private native-disposable descriptor binds the existing Identity actor command to
one validated ENV/run/database/login/secret. A fixed isolated bounded worker verifies
restricted session identity before calling the unchanged adapter. There are no new
migrations/roles/credentials/dependencies; original owner chains/references remain intact.
See [target evidence](../../../../services/access/OPERATOR_TARGET_EVIDENCE.md) and the
existing Identity runbook for explicit setup, recovery, actual local proof and limits.
No automated target/role/credential bootstrap, real account/adoption or hosted-CI proof;
remaining Identity commands/hardening and full shared readiness stay gated.


## Bounded ID-B organization target projections — 2026-10-20

Revision7 adds only organization_account_candidates/organization_account_target, under
the contract-selected restricted target definer and fixed Access NOLOGIN recipients.
No ordinary runtime/browser/raw-table grants; existing current-account reads remain.
New independent canonical target reference protects this additive head; all prior
revision/reference/source pins are immutable. Actual synthetic read/role/upgrade/
rollback evidence is in [target reads](../../../../services/access/ORGANIZATION_TARGETS_EVIDENCE.md).
Future Access owner rights/wrappers and canonical ownership checks evolve together;
no Access eligibility, account ensure, membership hardening or full readiness is claimed.


## Bounded ID-B profile protected columns — 2026-10-20

Identity revision8 narrows authenticated profile writes through exact column ACLs:
INSERT(id,username), UPDATE(username,deleted_at). Existing RLS/SELECT absence, Auth hook,
shared audit routines, postgres seed authority and trusted service_role rights remain.
The new independent profile reference preserves all seven prior revisions/references.
See [profile evidence](../../../../services/access/PROFILE_FIELDS_EVIDENCE.md) for actual head7 characterization, synthetic role/upgrade/
rollback verification and review. This is no account provisioning or lifecycle redesign;
remaining Identity/Access/WRITE and server KDG remain gated. No real account or production
change, new dependency/service/generator or resource removal.


## Bounded ID-B legacy role lookup — 2026-10-20

Revision9 fixes the existing public.get_user_roles() ambiguity and requires its exact
current account/org/member binding with active profile/organization/membership/role.
Its existing no-argument role:string contract, owner and exact ACL remain; canonical
source PUBLIC defaults are not normalized to uninspected deployment differences.
See [role lookup evidence](../../../../services/access/LEGACY_ROLE_LOOKUP_EVIDENCE.md) for actual source-bound characterization/currentness/
upgrade/rollback proof and review. Auth hook, membership lifecycle/uniqueness/CASCADEs,
account verification adapter and Access/WRITE/KDG remain separate gates. No new role,
credential, dependency, runtime service or generator; historical8 references/revisions
and all concurrent documents/resources remain preserved.

## Bounded token-hook organization correction — 2026-10-20

Identity revision10 retains the existing hook owner/signature/ACL and metadata selection
while excluding retired organizations from fallback, member/role/owner authority and
org_ids. Original source/defaults are not replayed or normalized. See
[token-hook evidence](../../../../services/access/TOKEN_HOOK_EVIDENCE.md) for verification
and limits. This is synthetic owner delivery, not live target equivalence, provider
verification or full membership lifecycle/Access activation.

## Bounded immutable membership binding — 2026-10-20

Identity revision11 replaces only the existing member revision guard body to reject
changes to retained membership id/org_id/user_id. Owner/ACL/trigger and other mutable
revision/seed behavior stay. See [binding evidence](../../../../services/access/MEMBERSHIP_BINDING_EVIDENCE.md)
for source-bound synthetic proof and limits. Uniqueness, retirement/rejoin, cascade
retention, account verification and Access/WRITE activation remain separate gates.
This is not real-target adoption or full membership lifecycle readiness.

## Bounded membership retention — 2026-10-20

Identity revision12 replaces the three declared membership/role cascade references with
RESTRICT and protects membership DELETE/TRUNCATE through the existing revision guard.
Existing profile→Auth FK remains unchanged; physical account deletion is not promised.
See [retention evidence](../../../../services/access/MEMBERSHIP_RETENTION_EVIDENCE.md) for
source-bound verification and compatibility limits. Retirement/rejoin, seed transition,
owner commands/live-account verification and Access/WRITE/server KDG remain gated.


## Bounded one-way membership retirement —2026-10-20

Identity revision13 extends the same guard to retain a retired member's timestamp and
prevent ordinary update/seed/retry reactivation. It changes no rows, historical source,
constraints/triggers/ACLs or unique index. Active writers/readers remain; retired seed
reactivation deliberately refuses. [Evidence](../../../../services/access/MEMBERSHIP_RETIREMENT_EVIDENCE.md)
records actual proof and limits. Authorized lifecycle commands, partial active uniqueness,
active seed/rejoin transition and real-target compatibility/activation remain gated.


## Compatible active-membership index expansion —2026-10-20

Identity14 adds org_member_active_org_user_uidx WHERE deleted_at IS NULL; the existing
full unique constraint/index and all data/writers stay. Final replacement/rejoin requires
coordinated owner-command/seed changes and release-recovery disposition; canonical14
still forbids historical duplicates. [Evidence](../../../../services/access/ACTIVE_MEMBERSHIP_INDEX_EVIDENCE.md)
records source-bound canonical versus isolated-index proof and remaining gates.


## Bounded ID-B actor-attribution expansion — 2026-10-21

Revision15 stages nullable membership created_actor_id/updated_actor_id references to
the durable actor registry, RESTRICT FKs and owner-only field changes with immutable
populated creation actor. Legacy attribution/timestamps remain; no inferred/automatic
backfill, identity classification, owner command, seed transition or production adoption
is claimed. Owner-verified updates retain evidence and advance the existing revision.
See [Build/evidence](../../../../_bmad-output/implementation-artifacts/spec-id-b-membership-actor-attribution.md)
and [owner runbook](../../../../services/access/IDENTITY-MIGRATIONS.md#staged-membership-actor-attribution--revision15).

Reviewed actual revision15 matrix PASS47.815s;936 affected tests/both composers PASS.
All three independent reviews complete; findings resolved without deferrals. Retain
all prior frames and the new synthetic attributed repeat fixture. Commands and real
adoption/Access/WRITE/server KDG remain separate gates.


## Protected ID-B membership retirement command — 2026-10-21

Revision16 adds exact `membership.retire` execution and current-authority scoped outcome
lookup through the existing owner adapter/CLI. Organization/account/member/revision,
server retirement/update attribution, immutable event and outcome share one transaction.
Ordinary retirement writes refuse at the owner boundary while active seeds/noops and
controlled migrator maintenance remain. Full and partial uniqueness and historical
migration/reference bytes remain. Synthetic clean/adopt/head15/repeat and failure proof
are recorded in [Build/evidence](../../../../_bmad-output/implementation-artifacts/spec-id-b-membership-retire-command.md);
independent review remains recorded there. See the
[owner runbook](../../../../services/access/IDENTITY-MIGRATIONS.md#protected-exact-membership-retirement--revision16).
Joining, account setup, real-target compatibility/activation and later owners remain gated.

## Protected ID-B membership join and seed cutover — 2026-10-21

Revision17 delivers first join and explicit rejoin through the existing protected
Identity operator surface, with exact command/org/account authority and additional
`membership.join_owner` authority for initial ownership. It shares retirement's history
lock, creates a new revision1 member and atomic immutable outcome/event, and retains old
members/roles/receipts. Local profile/org validation does not claim live Auth verification.
Ordinary membership insertion/owner changes are blocked; full uniqueness is removed only
with protected writers and seed cutover, retaining active uniqueness and history guards.
Legacy demo execution stops before side effects; owned composition requires `--no-seeds`
and refuses stale generated seed SQL. Historical migrations/references and SQL seeds stay
unchanged. [Owner runbook](../../../../services/access/IDENTITY-MIGRATIONS.md#protected-membership-join-and-rejoin--revision17)
and [Build/evidence](../../../../_bmad-output/implementation-artifacts/spec-id-b-membership-join-command.md)
record actual restricted/native CLI/race and migration evidence. This bounded prerequisite
does not authorize account mapping, Access activation or downstream application delivery.
