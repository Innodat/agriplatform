# Existing identity and receipt/expense consolidation review

**Date:** 2026-09-23  
**Scope:** Current working-tree source, not a deployed database certification  
**Workflow:** bmad-review; adversarial, edge-case and verification-gap lenses

## Conclusion

Retain the existing organization, membership and account identifiers and useful
receipt behavior. Change the implementation before treating it as the platform
identity/access/employment reference. The repository already has a shared identity
schema; a second user directory inside Leave would repeat existing work. However,
the current identity schema is account-centric and its authorization relies on token
claims. It is not an implementation of the now-accepted current-access or shared
employment contracts.

The receipt application is `apps/expense`. No separate employee/employment table
was found in the inspected migrations or generated Expense database types. Its
employee concept is represented by `identity.users`, the global `employee` role,
receipt `created_by` and purchase `user_id`. This finding concerns repository files;
an unrecorded table in a development database has not been ruled out.

## What to retain and what to change

| Existing element | Assessment and consolidation direction |
| --- | --- |
| `identity.org` | Retain organization identity and established `org_id`. Already neutral enough for nonprofit and for-profit organizations. |
| `identity.org_member` and `member_role` | Retain the organization-membership concept and map existing IDs. Add explicit lifecycle/current checks and reviewed restoration; restoring membership must not silently restore former grants. |
| `identity.users` | Retain existing account/profile references during transition. Its primary key must reference `auth.users`, so it is not an independent person or employment master. Add the shared person/account-link distinction deliberately. |
| Fixed `app_role`/`app_permission` enums | Useful evidence of existing Finance capabilities, but insufficient for application-owned default roles and organization/application-scoped custom roles under ADR-0011. Preserve intentional grants through an explicit catalog/role migration. An `employee` role is not proof of employment. |
| JWT organization and role claims | May support display/context selection; must not be the authority for current grants. Use the shared access contract and application resource checks under ADR-0019/0021. |
| Receipt `created_by` | Capturing actor/attribution, not necessarily the claimant or employee concerned. Preserve original provenance when migrating. |
| Purchase `user_id` | Currently references `auth.users`. Confirm whether this means claimant, beneficiary or another subject before mapping to shared employment; never mechanically rename it to `employment_id`. Resolve ambiguous historical mappings explicitly. |
| Audit fields/triggers | Retain the intent, revise enforcement: protect creation fields and privileged profile fields, support service actors, audit membership/grant changes and restrict audit-table writes. |
| Browser business-table access and privileged receipt RPC | Legacy application mechanisms requiring deliberate transition to the application's FastAPI API and authorized shared HTTP contracts. Do not copy these into Leave scaffolding. |

## Platform-wide scope

Identity, account linking, organization membership, business-capability access and
person/service attribution are platform-wide contracts. Employment is the shared
platform contract for applications that need it, including Leave and applicable
Travel/Expense features. Other applications and nonemployee administrators need not
create employment records. Leave policies, work profiles, balances and approval
workflows remain in Leave; Finance receipts and reimbursement rules remain in Expense.

The user agreed to one employment relationship per person per organization. Preserve
employment periods across leaving and rejoining. A person can have relationships in
multiple organizations. Shared nullable department/location/manual-supervisor ownership
is already accepted under ADR-0041. Service names, physical schema details and co-hosting
remain proposals in the [owning contract](../contracts/identity-access-employment-e1.md).

## Accountless employees

Recommend supporting a person and employment without a login account in the shared
model. Pre-onboarding records and historical/imported employment should not require
fake authentication accounts. Employment history should survive account closure.
This is a model capability, not a request for a new HR interface in E1.

Keep these actions separate: create a person, establish employment, link a verified
account, grant organization membership, and grant application capabilities. Linking
uses authorized verified identity evidence, not automatic email equality or an
arbitrary client-supplied employee ID. Default role assignment may be an explicit
part of authorized provisioning; employment alone must never grant it.

Accountless people cannot sign in or provide an employee-only acknowledgement.
Existing Leave on-behalf rules still apply, including the employee's own authenticated
response where required. Supervisor eligibility also requires actual current access,
not merely the existence of an employee record. The user subsequently accepted accountless support and the consolidation recommendations;
[ADR-0042](../decisions/0042-person-account-employment-and-legacy-adoption.md) records this direction.
The source findings below remain unresolved implementation work.

## Integration sequence

1. Before shared schema implementation, inventory supported development databases,
   existing users/organizations/memberships, actor references and Finance subject
   references. Characterize current behavior on disposable data. The app is not in
   production, but this does not authorize dropping development data.
2. Complete the E1 shared contract and verify the adoption baseline. Preserve account,
   organization and membership IDs where possible; explicitly map new person and
   employment identities. Do not turn every account or `employee` role assignment into
   employment automatically. Reconcile uncertain/duplicate mappings instead of guessing.
3. Assign project-owned schemas to their service/application migration histories under
   ADR-0015/0016. Test empty bootstrap and supported database upgrades, migrate in
   coordinated order under ADR-0020, and avoid two runners owning the same objects.
   Update composition/bootstrap tooling when service-owned assets are introduced.
4. Deliver the minimal shared contracts needed by Leave E1 after its readiness pass.
   E2 adds shared administration/history. Include compatibility evidence for existing
   consumers whenever shared identity changes; do not make a full Expense rewrite a
   prerequisite for the first Leave draft slice.
5. Give Expense its own bounded adoption work: clarify purchase subject semantics,
   add mapped employment references where required, preserve capture actors, introduce
   the FastAPI boundary, migrate role grants and replace unsafe legacy write paths.
   A future app requiring people data consumes the same shared contract. Each affected
   existing caller must either migrate with the shared change or remain supported by
   an explicitly tested compatibility path.
6. Remove legacy interfaces/fields only after all consumers and historical references
   are accounted for, with recovery evidence. A reset/rebaseline may simplify a purely
   disposable environment, but only after its data and reset policy are explicitly
   established; no reset is implied by the absence of production.

Required adoption examples: old account keeps its historical actor attribution;
one person works in two organizations without leakage; expired/revoked membership
fails with an otherwise valid token; rehire preserves history without restoring old
grants; an imported accountless employee can be linked without merging unrelated
people; on-behalf capture distinguishes subject from actor; legacy client queries
and generated types match the new contract.

## Evidence and review limitations

The full findings are retained below by lens and in the companion JSON file. Overlap
between lenses is intentional: independent reviewers identified the same authorization,
scope and attribution weaknesses. Findings are static paths and verification gaps, not
proof of a live exploit or certification of deployed grants. In particular, privileged
function reachability and RLS bypass depend on effective grants/function ownership;
test these under real restricted roles before closing the findings. The hook's returned
organization claim is not itself proof of valid membership.

`python3 tools/py/run_compose_supabase.py --check-only` passed (exit 0): it discovers
15 migrations across platform, Expense and Scribeswell and checks composition naming/
collisions. It does not execute SQL, verify dependency order semantically, validate
effective privileges or exercise authorization. No database was connected or modified.

Existing Expense RLS tests are not adoption proof: they use old role metadata and
fixtures missing required organization context. Their teardown can delete unrelated
records using the service role. They were inspected, not run. Repair and isolate them
before execution; no application tests or migrations were run for this review.

## Delivery impacts

- Scaffold: establish current-access clients, typed references, safe errors, actor
  attribution, owned migrations and disposable test fixtures with the first consuming
  delivery item; do not promote the legacy direct-table pattern.
- Shared UI: organization selector and authorized person/employment selection; no
  duplicate account/profile editor or required employment for every app user.
- Agent context: existing service ownership/organization rules cover this review;
  update exact paths/commands only when implementations are established.
- Documentation: shared contract, Leave source requirement, epic map and tracker
  record the agreement and consolidation dependency; no readiness item is complete.
- ADR: accepted ADRs remain immutable. This review proposes implementation alignment,
  not a replacement security or delivery policy.

## Findings by lens

All 29 findings are retained in [JSON](./identity-expense-consolidation-2026-09-23.json) and rendered below. No runtime finding has been independently reproduced in this review.


### adversarial

**Location:** `platform/supabase/migrations/20250815210000_platform_multitenancy_orgs.sql:77`

- **Trigger:** A membership, role assignment, user or organization is disabled while an already-issued JWT remains valid; authorize() still trusts its user_roles and org_id claims.
- **Guard:** Resolve current user, organization, membership and permission state for each protected operation under ADR-0019; treat JWT organization and role claims as context hints. Add retained-token revocation tests.
- **Consequence:** Static inspection shows no current membership check in this authorization function, so removed access can remain effective until token replacement; runtime behavior has not been exercised.

**Location:** `platform/supabase/migrations/20250815110000_platform_create_identity_schema.sql:177`

- **Trigger:** An authenticated user updates their own identity.users row, which later gains is_platform_admin and already contains is_system and actor_key.
- **Guard:** Expose an allowlisted self-profile command and deny direct updates to privilege, actor identity and attribution columns; test effective grants and RLS under the real authenticated role.
- **Consequence:** The self-update predicate imposes no column restrictions while authenticated receives table UPDATE privileges. Privileged fields can be self-assigned if this write path is usable; downstream exploitation is not established.

**Location:** `platform/supabase/migrations/20250815110000_platform_create_identity_schema.sql:17`

- **Trigger:** Planning treats identity.users as the shared employee/person master or needs a person without a Supabase Auth account.
- **Guard:** Preserve existing account IDs but introduce an independent person identity and an explicit optional account link, with a separate organization-scoped employment relationship and employment periods.
- **Consequence:** Every identity.users ID must currently reference auth.users. Reusing this table unchanged forces placeholder login accounts and conflates authentication, employment and business attribution.

**Location:** `platform/supabase/migrations/20250815110000_platform_create_identity_schema.sql:5`

- **Trigger:** Leave or another application introduces organization-configurable roles and application-specific permissions.
- **Guard:** Replace the fixed global role enum and global role-to-permission assignment with the ADR-0011 role model, including organization scope and application permission namespaces; migrate existing admin, financeadmin and employee assignments explicitly.
- **Consequence:** The existing enum and role_permissions uniqueness cannot represent per-organization custom roles, and the role name employee risks being mistaken for employment status.

**Location:** `apps/expense/supabase/migrations/20250815200000_finance_create_func_add_receipt_with_items.sql:23`

- **Trigger:** A caller invokes the SECURITY DEFINER receipt creation function with a non-null authenticated user and organization claim.
- **Guard:** Require current membership and the necessary receipt/purchase permissions before writes, validate each referenced record's scope, and restrict function execution to intended callers.
- **Consequence:** The function checks authentication and presence of organization context but contains no membership or permission checks; if its owner bypasses RLS, the intended table policies do not protect these writes.

**Location:** `apps/expense/supabase/migrations/20250815130000_finance_create_schema.sql:25`

- **Trigger:** A write supplies an expense category, expense type, currency or purchase beneficiary belonging to another organization.
- **Guard:** Enforce same-owner organization consistency with appropriate composite constraints and validate cross-owner references through authorized contracts. Validate the beneficiary's organization-specific employment separately.
- **Consequence:** The current foreign keys establish existence, not organization consistency. The receipt RPC copies supplied references without checking their organization, allowing structurally inconsistent cross-organization associations.

**Location:** `apps/expense/supabase/migrations/20250815130000_finance_create_schema.sql:80`

- **Trigger:** Receipt consolidation uses finance.purchase.user_id as the employee identifier or migrates it mechanically to an employment ID.
- **Guard:** Document whether user_id represents claimant, beneficiary or another subject; retain created_by as the capturing actor and map the business subject explicitly to shared employment where required, preserving historical mappings.
- **Consequence:** The existing field references auth.users, while ownership policies use created_by. Treating both as employee identity can misattribute on-behalf purchases or attach history to the wrong employment.

**Location:** `platform/supabase/migrations/20250815170000_platform_create_audit_triggers.sql:13`

- **Trigger:** A caller supplies created_by or created_at, changes them later, or a service performs a write without an end-user JWT.
- **Guard:** Make creation attribution immutable and server-managed, manage update attribution for all relevant tables, and define actor/initiator/executor context for both people and services under ADR-0025.
- **Consequence:** The trigger only assigns updated_by and, on UPDATE, updated_at. Creation fields remain caller-influenced, and service writes can receive null attribution.

**Location:** `platform/supabase/migrations/20250815210000_platform_multitenancy_orgs.sql:23`

- **Trigger:** An administrator changes organization membership, ownership or member roles.
- **Guard:** Add server-managed attribution and immutable consequential audit for organization, org_member and member_role commands, with organization, command and actor context.
- **Consequence:** The shown audit triggers cover users and role_permissions but not the subsequently created membership/role tables, leaving access grants and revocations without equivalent recorded evidence.

**Location:** `platform/supabase/migrations/20250815110000_platform_create_identity_schema.sql:237`

- **Trigger:** An ordinary database role can reach the SECURITY DEFINER identity.create_user test helper.
- **Guard:** Keep test-user creation outside deployable runtime migrations or revoke PUBLIC execution and grant it only to a dedicated fixture role; verify effective function privileges.
- **Consequence:** The helper inserts into auth.users and no explicit PUBLIC execution revocation is present in the inspected sources. PostgreSQL's default function privileges can expose an unintended account-creation capability; deployment reachability requires verification.

**Location:** `apps/expense/web/src/services/finance/purchase.service.ts:27`

- **Trigger:** The Receipt application is adopted as the implementation template for Leave or shared employment.
- **Guard:** Plan an explicit Receipt transition to its FastAPI business API and authorized shared-service HTTP contracts; retain useful domain behavior without copying browser-to-business-table CRUD into the new scaffold.
- **Consequence:** The current client directly reads and writes finance tables through Supabase. Reusing this pattern would bypass the agreed server ownership and API boundaries.

**Location:** `apps/expense/web/src/services/finance/purchase.service.ts:27`

- **Trigger:** getPurchases executes against the purchase schema defined by the inspected migrations.
- **Guard:** Align the ordering/filter contract with the existing created_at field or deliberately add a domain capture timestamp, then exercise the real client/schema query.
- **Consequence:** The client orders and filters by captured_timestamp, but the shown purchase table defines created_at and updated_at instead. This indicates a concrete schema/client mismatch that should be resolved before treating Receipt as a proven reference.


### edge-case-hunter

**Location:** `platform/supabase/migrations/20250815210000_platform_multitenancy_orgs.sql:77-104`

- **Trigger:** Membership, organization, profile, or assigned role is revoked while an issued JWT remains valid.
- **Guard:** Authorize against current active profile, organization, membership and assigned roles for auth.uid().
- **Consequence:** Revoked users retain permissions until token claims change.

**Location:** `platform/supabase/migrations/20250815210000_platform_multitenancy_orgs.sql:134-188`

- **Trigger:** Requested organization lacks membership, is deleted, or contains a malformed UUID.
- **Guard:** Parse safely; select current organization only through an active organization and current membership.
- **Consequence:** Tokens retain unauthorized organization context, or token issuance fails.

**Location:** `platform/supabase/migrations/20250815180000_platform_add_get_user_roles_function.sql:14-23`

- **Trigger:** get_user_roles executes with default PL/pgSQL variable-conflict handling.
- **Guard:** Rename variable to v_member_id; WHERE mr.member_id = v_member_id.
- **Consequence:** The unqualified member_id reference is ambiguous and role retrieval fails.

**Location:** `platform/supabase/migrations/20250815180000_platform_add_get_user_roles_function.sql:16-23`

- **Trigger:** A membership is deleted while its role assignments and JWT member_id remain.
- **Guard:** Join active org_member and org; verify membership belongs to auth.uid().
- **Consequence:** Role retrieval returns permissions belonging to an inactive membership.

**Location:** `apps/expense/supabase/migrations/20250815200000_finance_create_func_add_receipt_with_items.sql:15-36`

- **Trigger:** Authenticated caller has organization context but lacks current receipt-creation permission.
- **Guard:** Require current scoped membership and receipt/purchase permissions before SECURITY DEFINER inserts.
- **Consequence:** The privileged function bypasses table RLS and creates unauthorized receipts.

**Location:** `apps/expense/supabase/migrations/20250815130000_finance_create_schema.sql:24-25,74-80`

- **Trigger:** A purchase or expense type references another organization's employee, currency, or category.
- **Guard:** Enforce same-organization references with scoped constraints and authorized shared-employment validation.
- **Consequence:** Cross-organization employee and reference-data associations enter otherwise scoped receipts.

**Location:** `platform/supabase/migrations/20250815110000_platform_create_identity_schema.sql:17-29`

- **Trigger:** An employee or service actor must exist without a Supabase login account.
- **Guard:** Separate durable person/service identity from optional authentication-account links and organization employment.
- **Consequence:** The current profile requires an authentication account for every represented identity.

**Location:** `apps/expense/supabase/migrations/20250815130000_finance_create_schema.sql:74-80`

- **Trigger:** An employee changes login account or their original authentication account is deleted.
- **Guard:** Reference durable employment/person identity; migrate legacy auth UUID references through an explicit mapping.
- **Consequence:** Financial attribution stays bound to the old account and account deletion can fail.

**Location:** `platform/supabase/migrations/20250815210000_platform_multitenancy_orgs.sql:23-50`

- **Trigger:** A departed member rejoins after soft deletion while old role assignments remain active.
- **Guard:** Use explicit membership restoration with reviewed grants; retain separate employment-period history.
- **Consequence:** Reinsertion conflicts with uniqueness; restoration can reactivate old privileges.

**Location:** `platform/supabase/migrations/20250815110000_platform_create_identity_schema.sql:237-254`

- **Trigger:** An authenticated database/API caller invokes the privileged test-user helper.
- **Guard:** REVOKE EXECUTE ON FUNCTION identity.create_user(text) FROM PUBLIC; grant only dedicated provisioning authority.
- **Consequence:** Ordinary callers can create authentication records through a privileged helper.

**Location:** `platform/supabase/migrations/20250815210000_platform_multitenancy_orgs.sql:200-201`

- **Trigger:** A caller invokes the auth hook through inherited PUBLIC function-execution privileges.
- **Guard:** REVOKE EXECUTE ON FUNCTION identity.custom_access_token_hook(jsonb) FROM PUBLIC; grant supabase_auth_admin only.
- **Consequence:** Revoking named roles alone leaves privileged membership and role enumeration callable.

**Location:** `platform/supabase/migrations/20250815110000_platform_create_identity_schema.sql:266-267; platform/supabase/migrations/20250815160000_platform_create_audit_log_tbl.sql:1-10`

- **Trigger:** Authenticated callers insert into the later-created audit_log table.
- **Guard:** Revoke inherited audit-table writes; permit insertion only through restricted audit mechanisms.
- **Consequence:** Default table privileges permit forged audit entries without an audit-table RLS guard.

**Location:** `platform/supabase/migrations/20250815170000_platform_create_audit_triggers.sql:13-17`

- **Trigger:** A caller explicitly supplies or alters creation attribution fields.
- **Guard:** On insert derive created_by/created_at; on update preserve OLD creation fields.
- **Consequence:** Creation actors and timestamps can be forged despite the audit-field trigger.

**Location:** `platform/supabase/migrations/20250815210000_platform_multitenancy_orgs.sql:23-50`

- **Trigger:** Organization memberships, ownership, or role assignments change.
- **Guard:** Attach server attribution and immutable consequential audit to org, org_member and member_role changes.
- **Consequence:** Access changes lack the audit coverage attached to the older identity tables.

**Location:** `apps/expense/supabase/migrations/20250815130000_finance_create_schema.sql:60`

- **Trigger:** A referenced content-store record is physically deleted.
- **Guard:** Protect associated business records; use explicit attachment lifecycle instead of content-to-receipt cascading deletion.
- **Consequence:** Receipt deletion is attempted, potentially erasing evidence or failing on purchase references.


### verification-gap

**Location:** `platform/supabase/migrations/20250815210000_platform_multitenancy_orgs.sql:77`

- **Trigger:** The existing identity implementation is treated as verified against organization-scoped, current authorization, but the receipt tests still exercise the older single-role model.
- **Guard:** Seed actual organizations, org_member and member_role records; assert isolation between organizations and denial using an already-issued token after membership or role revocation. Wire this suite into a documented runnable command.
- **Consequence:** Current authorization or organization isolation could be carried into the shared service with defects that the existing test assets do not establish protection against. The fixtures cannot exercise the current model: they create app_metadata.user_role, create no memberships, and insert receipts without required org_id.
- **gap_shape:** broken-verification-gap
- **consumer:** Receipt RLS policies at apps/expense/supabase/migrations/20250815140000_finance_tables_policies.sql:130
- **evidence:** Read all three apps/expense/web/tests/rls files: finance.test.ts is empty; receipt.rls.test.ts:33-97 creates legacy role metadata and unscoped receipt fixtures; currency.employee.read.test.ts:20-35 likewise creates no organization or membership and inserts currencies without org_id, and :62 expects legacy jwt_role. Whole-repo test/spec symbol search for custom_access_token_hook, current_org_id, current_member_id, identity.authorize, org_member and member_role found no executable membership/revocation tests. Read the content-flow integration test too: it sets a random organization UUID in metadata without creating membership. apps/expense/web/package.json declares neither Vitest nor a test script; scripts/run_unit_tests.sh and run_integration_tests.sh target Deno content functions.

**Location:** `apps/expense/web/tests/rls/receipt.rls.test.ts:102`

- **Trigger:** The receipt RLS suite is run against any configured database containing receipts outside this test's fixtures.
- **Guard:** Require an explicitly disposable test database and restrict teardown to IDs created by this run; apply the same rule to currency.employee.read.test.ts:40.
- **Consequence:** The service-role teardown deletes every receipt whose ID is not -1, and the currency suite does the equivalent for all currencies. Reusing these tests as consolidation verification could delete unrelated development or pilot data; receipt foreign keys could instead cause teardown failure.
- **gap_shape:** other
