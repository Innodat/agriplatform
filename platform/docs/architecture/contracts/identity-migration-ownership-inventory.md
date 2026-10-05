# E1 identity and migration ownership inventory

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
