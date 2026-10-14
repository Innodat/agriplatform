# Identity and Access execution substrate for the KDG first slice

2026-10-14. Concrete selected planning contract under acknowledged ID-A/ID-B and
ACCESS-A/B ownership. No migration, privilege, command, account or grant is executed.
This closes the KDG-relevant physical/command choices left by the
[shared addendum](kdg-shared-readiness.md); [ownership inventory](identity-migration-ownership-inventory.md)
and [existing Identity lifecycle](identity-access-employment-e1.md) remain source
authority. It does not finish Leave/People or add a second identity service.

## Physical Identity contract

Use the existing planned Identity Alembic layout under services/access, with its own
identity.alembic_version/identity_migrator/IDENTITY_MIGRATION_DATABASE_URL. Access history
never creates Identity objects. All instants are timestamptz/UTC; new revisions are
positive signed bigint and wire decimal strings. PostgreSQL15+ is the explicit floor
for NULLS NOT DISTINCT; the supported Supabase target must meet it. Reject nil UUIDs and NUL text.

| Identity-owned object | Exact minimum shape / constraints |
| --- | --- |
| identity.actor | id UUID PK; kind text CHECK account/system/service; display_name text nonblank, ≤200 code points; actor_key nullable text, ASCII `[a-z][a-z0-9_.:-]{0,127}`, UNIQUE when present; created_by/updated_by UUID local non-cascading FK to actor; created_at/updated_at timestamptz NOT NULL; UNIQUE(id,kind). No Auth/person/employment FK. id/kind/non-null assigned key immutable; label mutable under controlled owner command only. |
| identity.account_actor | account_id UUID PK, actor_id UUID UNIQUE NOT NULL, actor_kind text NOT NULL CHECK account; composite FK(actor_id,actor_kind)→actor(id,kind) ON DELETE RESTRICT; created_by UUID actor FK RESTRICT, created_at timestamptz NOT NULL. Mapping immutable and retained; account_id is verified external Auth reference with no cascading Auth FK. |
| identity.org_member (existing) | Preserve bigint id/org_id/user_id/is_owner/deleted_at/legacy attribution. Add revision bigint NOT NULL default1 CHECK>0 and created_actor_id/updated_actor_id UUID local actor references, with compatible staged backfill. Replace unique(org_id,user_id) by unique active index on those columns WHERE deleted_at IS NULL. org/account/id immutable; retirement timestamp can transition only null→instant; no unretire/hard-delete through supported commands. |
| identity.member_role (existing) | Retain member_id binding and enum role compatibility; no role copying on rejoin. Convert required-history membership FK from CASCADE to RESTRICT in coordinated transition. Existing rows and attribution stay evidence; KDG uses Access explicit capability bundles, not this legacy enum. |

Membership org/profile references become RESTRICT for retained history, not CASCADE.
Profile remains Auth-linked; this plan does not authorize Auth/profile/org deletion or
promise account deletion works. New grants/memberships do not change original authorship.
Legacy UUID actor fields remain unchanged while compatibility consumers need them; new
actor columns are populated only through verified adoption mappings. Unknown references
stop activation for explicit disposition rather than receiving invented System attribution.

Structural enforcement: owner-local constraints plus immutable-field/retirement guards;
no API-only enforcement. Account-kind mapping prevents a normal account using a service
actor. Bootstrap creates verified System/Migrate/service actors with explicit baseline
evidence; a clean bootstrap actor may reference itself. Preserve classified legacy UUIDs
and never create another actor per run. display_name is owner-verified display text,
never an automatic copy of legacy username/email for target lists.

## Exact Access persistence extension

All Access-owned references to Identity are verified external identifiers without
cross-owner FKs. Registry IDs match `[a-z][a-z0-9_]{1,63}`; permission IDs are ASCII,
1–200 bytes, literal registered values. Registration association/scope is immutable.

| Access-owned object | Exact keys / constraint extension |
| --- | --- |
| access.applications | app_id text PK; enabled boolean NOT NULL default false; revision bigint>0; created_by/updated_by UUID and created_at/updated_at timestamptz NOT NULL. No exclusive app-wide scope column. |
| access.permissions | permission text PK; app_id FK→applications RESTRICT; scope_kind CHECK account/organization; UNIQUE(permission,scope_kind); creation actor/time only. No wildcard or implicit capability expansion. |
| access.entry_permissions | app_id,permission composite PK; FK to permissions with matching app association, enforced by UNIQUE(app_id,permission) on permissions; creation actor/time. Explicit entry set; KDG read.own only. |
| access.organization_applications | PK(org_id UUID,app_id); app FK RESTRICT; enabled default false, revision>0 and four attribution fields. org_id non-null verified external reference. |
| access.grants (existing organization table) | Preserve PK(org_id,id text) and UNIQUE(org_id,user_id,permission); scope_kind fixed organization; composite FK(permission,scope_kind)→permissions; membership_id bigint>0 NOT NULL in final active shape; revoked_at nullable; revision>0; preserve legacy created_by text/created_at and add created_actor_id/updated_actor_id UUID plus updated_at. id is a stable opaque existing identifier, never changed to a UUID by casting. |
| access.account_grants | id UUID PK; UNIQUE(account_id UUID,permission); scope_kind fixed account; composite permission/scope FK; revision>0/revoked_at and four attribution fields. No org/member columns or synthetic organization. |

Legacy unmatched organization grants may remain quarantined during additive transition
with null membership/actor references: they are never eligible. Final effective-row CHECK
requires non-null verified membership/actor references when revoked_at IS NULL; retain
unmatched rows explicitly revoked or in the owner migration evidence, never infer a grant.
Valid regrant changes binding/revision only through an explicit current-member command.
KDG exact nine permissions/default bundles and resource_scope variants remain in the
shared addendum; no role-table/People dependency is added here. Role bundles are explicit
configuration lists consumed by owner setup, not platform-admin authority.

Mutable owner rows use verified actor/time, positive revision and short write transactions.
No-op matching desired state after expected-state validation keeps revision unchanged,
records a compact receipt and creates no fake change event. Local changes, immutable
evidence and receipt commit together. Runtime has no write permission to any registry/grant.

## Current Identity projections and target-query isolation

Provider/user/service verification precedes SQL. Trusted Access sets app.account_id,
app.actor_id and selected app.org_id transaction-locally after verification; an account
is not inferred from actor equality. Missing/malformed required context fails closed.
These GUCs are trusted backend assertions, not independent authentication against a
compromised Access credential. No client account/person/actor override on ordinary check.

Selected owner routine signatures (internal SQL, not browser RPC):

| Identity routine | Exact returned columns / guard |
| --- | --- |
| identity.current_account_actor() | account_id UUID, actor_id UUID, display_name text; current verified account/profile row with nullable internal actor_id/display_name when mapping is absent. No profile yields no row; profile with absent mapping yields that nullable row, so Access can distinguish missing identity from actor setup after authority checks. Public success always requires a mapped account actor. No implicit ensure. |
| identity.current_account_organization() | account_id UUID, org_id UUID, membership_id bigint, membership_revision bigint, actor_id UUID nullable internally when mapping is absent; exact current account/org, nondeleted profile/org/member. Access first evaluates admission/grant, then maps absent actor to the safe setup outcome; HTTP success never has nullable actor. No person prerequisite for KDG. |
| identity.organization_account_candidates(after_account_id UUID nullable) | account_id UUID, membership_id bigint, membership_revision bigint, actor_id UUID, display_name text; current org only, active profiles/members, valid account actors, ordered account UUID with no raw-candidate LIMIT. Private scoped candidate set only; no email/role/person fields. Access applies app/grant eligibility **before** public page limit. |
| identity.organization_account_target(target_account_id UUID, expected_membership_id bigint) | Same columns for exact active org/account/member binding; missing/changed/ineligible identity produces no target. No latest-member substitution. |

Retain existing current_account_memberships()/Access discovery contracts unchanged;
normal KDG does not require their broader pre-selection use. Leave person projection
is separately qualified by its existing contract; these account projections do not
invent a person for it or replace its person-link requirement.

Use distinct access_runtime, access_target_runtime and access_setup_target_runtime
logins/pools. User execution sets app.context_kind=user, verified app.account_id,
app.actor_id and app.org_id. Setup execution sets app.context_kind=setup, verified
service app.actor_id and app.org_id, with app.account_id absent; do not manufacture an
operator Auth account. The setup login is permitted only with its protected service-key
mapping, verified service executor and configured org policy. Ordinary target login
accepts user context only, setup login setup context only; reject missing/mixed contexts.
Caller roles and private wrappers enforce the combination, not the GUC alone.

Use distinct access_runtime and access_target_runtime database logins/pools. Ordinary
check path may call only current-account projections; target pool may call only the
target Access functions below and has no direct Identity-table reads. Runtime target
HTTP authenticates current assignment.manage; setup-only point check authenticates its
protected service executor/org policy as in the shared addendum. Do not switch the main
account GUC to the target account or give the normal check path target-discovery powers.

ACCESS-B owns access.kdg_assignment_targets(after UUID, count integer) and
access.kdg_assignment_target(target UUID, expected_member bigint). Each is one read
statement joining Identity projection, enabled KDG admission and exact current-member
nonrevoked create.assigned/create.all grants. For list, eligibility precedes keyset page
limit: join the complete current-org candidate relation above the keyset position before
LIMIT, never return a short first page merely because raw candidates were filtered. Count100 plus one eligible
row determines next cursor; no caller can request another app/capability with this routine.
Identity routine is stable and reusable in that statement; no per-target HTTP loop.
Both wrappers produce the shared addendum's exact HTTP models/errors/no-store policy.
Setup login may call access.kdg_assignment_target only, never list; user target login
may call list/point. Their separate NOLOGIN reader roles receive the respective fixed
wrapper grants and current-org RLS; common query/target predicates are identical.
Setup has no account/person field and its service actor is attribution, not a target
account or grant. Neither role can assume the other or select raw tables.

## Privilege matrix and safe routine owners

All service/operator logins: NOSUPERUSER, NOCREATEDB, NOCREATEROLE, NOBYPASSRLS;
no unlisted role membership/schema CREATE/table/sequence/EXECUTE privilege. Use distinct
NOLOGIN reader/command owners and explicit grants; never reuse table owner/migrator.

| Principal / owner | Allowed authority |
| --- | --- |
| identity_migrator | Identity-owned DDL/version/history plus explicitly inventoried legacy public/Auth-hook integration objects. No Access/KDG table authority; Supabase-managed Auth schema bootstrap grants are separate restricted deployment work. |
| access_migrator | Access-owned DDL/version/history only; no Identity DDL. |
| identity_account_projection_owner | Selected Identity profile/member/org columns under current-account RLS; actor/mapping read columns needed by fixed current-account routines. Runtime cannot assume this NOLOGIN role. |
| identity_target_projection_owner | Selected profile/member/org columns under current-org RLS, actor/mapping columns for fixed target routines; no Access table read/write. No cross-org target result. |
| access_check_reader | Read-only registry and selected account/org grant/admission columns under corresponding forced RLS; EXECUTE current Identity projections only. |
| access_target_reader | Read-only registry plus grants/admission restricted to verified target-query org; EXECUTE target Identity projections only. Dedicated NOLOGIN definer owner, no role assumption by runtime. |
| access_runtime | Own selected-context reads/check/discovery wrappers; no target-owner execution or cross-account grant scans. |
| access_target_runtime | EXECUTE exact user-context Access list/point routines only; no raw table privileges, owner-role assumption or arbitrary app query. |
| access_setup_target_runtime / access_setup_target_reader | Setup-only point wrapper with explicit setup context and current-org read predicates; no list/raw table privileges or user-role assumption. |
| access_command_owner | NOLOGIN command definer with exact local DML/sequence/outcome grants and EXECUTE Identity exact target-account/member verification only. No arbitrary Identity table privileges, DDL, authority-map updates or implicit target grant. |
| identity_operator / access_operator | Owner-local command EXECUTE and scoped compact outcome read only; no raw business DML, schema CREATE, authority-map editing or other-owner role membership. |

Identity organization/member and Access org grant/admission tables enforce ENABLE+FORCE
RLS. Actor/mapping are global identity objects: restricted projection owners may read
necessary columns through their fixed routines, but ordinary runtime/browser roles have
no raw registry SELECT; global objects do not gain a fake org column. Identity profile
policies scope account owner to current account and target owner to profiles joined to
current-org members. Member policies depend only on context/current-org/account, avoiding
actor/profile→member→profile recursion. Access target RLS scopes org, not acting account,
because authorized assignment managers deliberately inspect other current members.

Read routines are STABLE SECURITY DEFINER with search_path=pg_catalog,pg_temp and fully
qualified owner objects, bound typed arguments, no dynamic SQL/external waits/writes.
Revoke PUBLIC/anon/authenticated/service_role EXECUTE in the same create transaction,
then grant only the exact stated callers. Runtime has no CREATE on these schemas and
cannot replace functions. New Identity tables do not inherit legacy broad default grants.
Owner migrations revoke inherited/default privileges for new objects and verify actual
ACLs; a function name and RLS policy name are not security proof.

PostgreSQL sources checked 2026-10-14:
[definer security](https://www.postgresql.org/docs/current/sql-createfunction.html),
[RLS](https://www.postgresql.org/docs/current/ddl-rowsecurity.html),
[SET ROLE](https://www.postgresql.org/docs/current/sql-set-role.html).
Live pinned-target privilege/pooled-connection tests remain delivery acceptance.

## Operator authority records and invocation

Each owner schema has operator_principals(database_login name PK, executor_actor_id UUID,
enabled boolean, revision bigint>0, four attribution fields) and operator_authorities
(id UUID PK, database_login FK RESTRICT, command text, scope_kind platform/organization,
org_id UUID nullable only for platform, application_id text nullable, target_account_id
UUID nullable, enabled boolean, revision>0, four attribution fields). UNIQUE across the
full authority tuple uses NULLS NOT DISTINCT. CHECK scope requires org only for org scope.
application/target null means explicitly all within that command/owner/scope; Access
KDG setup rows bind application_id=kdg_capture and intended account when provisioning
one user. Platform scope does not imply other-owner rights. No wildcard commands.

Only controlled owner deployment/bootstrap can write these authority records. Operator
command routines derive executor from original session_user/protected mapping and check
exact command/scope/app/target plus enabled state inside the short transaction before
effects; no payload actor/SET ROLE/GUC can select that executor. Separate NOLOGIN command
owners have only required local DML under explicit RLS/sequence grants, no DDL/mapping
mutation. Operator logins cannot assume those roles. A membership.join with is_owner=true
requires a separate protected authority literal membership.join_owner in addition to
membership.join for that exact scope/target; is_owner=false needs only ordinary join.
No payload boolean or legacy owner-role claim creates that extra authority.
Current operator authority is also
required to retrieve a prior receipt; mapping revision/change evidence is retained.

Planned owner CLI: `uv run --locked python -m operator_cli execute --target <prepared
run target> --command-file <JSON>` and `uv run --locked python -m operator_cli outcome
--target <prepared run target> --command <literal> --operation-id <UUID>`, run from
services/access with explicit owner selection `--owner identity|access`. Entry modules
are planned, not installed. Target preparation binds owner/environment/DB login/secret
reference; command schema is the existing version1 envelope, no owner/actor override.
ID-B owns generic trusted binding; Access reuses envelope/target mechanics with its own
policies/commands. KDG owner CLI follows the same trusted shape in its consuming item.
Never pass credentials or arbitrary SQL in command files/argv/reports.

## Command payload/result closure

Common envelope/receipt remains [controlled provisioning](e1-controlled-provisioning-and-evidence.md).
Unknown/duplicate fields fail; command body max65536 UTF-8 bytes, reason/evidence refs
max128/256 ASCII characters. expected_revision is positive decimal string; creates
use expected_absent=true. Actor/executor and times are always derived. Core payloads:

| Command | Exact payload / expected state |
| --- | --- |
| account_actor.ensure | account_id, actor_id, display_name, expected_absent=true; required envelope evidence_ref verifies live Auth/profile and classified legacy actor. Identical verified mapping unchanged, conflicting mapping denied. |
| actor.register_system | actor_id, kind system/service, actor_key, display_name, expected_absent=true. No Auth account or app grant. |
| membership.join | account_id, expected_previous_membership_id (null only first-ever), is_owner=false unless exact owner authority permits true. Serialize org/account with owner lock; verify full retained predecessor history/no active member. Allocate new ID/revision1, empty roles/grants. |
| membership.retire | account_id, membership_id, expected_revision. Retire that exact member/revision and record evidence; delayed retirement cannot target replacement. |
| application.register | app_id, expected_absent=true; new disabled revision1. |
| permission.register | app_id, permission, scope_kind, expected_absent=true. Identical existing mapping unchanged, reassignment rejected. |
| entry_permission.register | app_id, permission, expected_absent=true. Verify exact registered matching app association; insert immutable entry mapping/creation attribution and compact receipt. Identical mapping unchanged; no permission or grant created. |
| application.set_enabled | app_id, enabled, expected_revision. |
| organization_application.configure | app_id, enabled, expected_absent=true OR expected_revision (exactly one). |
| grant.assign | account_id, membership_id, permission, expected_absent=true OR expected_revision. Create opaque grant UUID rendered as text when new; retain all existing grant IDs. Exact current membership required. |
| grant.revoke | grant_id text, account_id, membership_id, permission, expected_revision. Target original grant binding/revision; no replacement lookup. |
| account_grant.assign/revoke | Existing account-only payload policy retained; no membership on PtS commands. Preserve coordinated adoption contract, no KDG account-grant usage. |

Pre-grant verification is distinct from KDG post-grant assignment eligibility. Before
grant.assign write locks, Access verifies its actual operator command/org/app/target
policy and invokes Identity's organization_account_target with the exact account/member
under a protected owner-command context. That routine verifies current profile/actor/
member/org only, without any Access grant predicate. access_command_owner receives
EXECUTE on that Identity projection, while dedicated Identity target owner grants/policies
remain current-org scoped. A valid member with no capture grant can therefore receive
its first explicit grant. No KDG assignment-target endpoint or arbitrary-bearer check
is used to bootstrap authority. Record verified target/member evidence; recheck on a
new/delayed execution and retain exact binding if retirement races the short write.
Actor ensure similarly verifies live Auth/profile through supported owner verification
before local locks; it does not infer a current account from a retained historical map.

membership.join implies expected absence of an active membership; retired predecessor
is its history guard, not a reused id. New joining attempt racing another join returns
expected-state conflict unless it is the same operation; it does not copy grants.
Per-owner outcomes unique(scope_kind,scope_id,executor_actor_id,command,operation_id),
with scope_id null only platform and NULLS NOT DISTINCT uniqueness. Store versioned
SHA-256/JCS input fingerprint for bounded identifier/setup commands as already selected,
compact typed result and committed_at. Sensitive observation commands instead use KDG's
separate HMAC disposition. Outcome/history table shape is finalized with WRITE.

Result target variants: actor→{actor_id}; account mapping→{account_id,actor_id}; member→
{org_id,account_id,membership_id}; app/permission→{app_id,permission when applicable};
grant→{grant_id,account_id,permission,org_id/membership_id for organization only}.
All use existing disposition/revision/event_id receipt; actor registration/account
mapping have revision=null, unchanged has event_id=null, mutable targets return their
recorded decimal revision. No personal payload/secret/fingerprint in results. Safe
errors use existing validation/access/conflict/unavailable/unknown-outcome distinctions.

## Source adoption and coordinated activation

ID-A inventories actual target definitions/ACLs/triggers/FKs/applied histories and compares
to the repository inventory. Target equivalence is checked before adoption/stamping,
never inferred. Production status documents a 2026-09-29 PUBLIC get_user_roles EXECUTE
revocation; do not blindly replay older source defaults or infer uninspected live grants.
Retain exact target differences as migration inputs and preservation assertions.

1. Establish Identity baseline once for clean target, or verified equivalent adoption;
   exclude adopted Identity objects from composer execution, retaining other-owner source
   bootstrap. Include public.get_user_roles/Auth hook integration in Identity ownership.
2. Add actor/mapping/current projections and revision columns compatibly; classify each
   legacy UUID and named service text through an explicit mapping fixture. Preserve
   legacy Auth-backed System/Migrate rows while consumers require them; no deletion.
3. Add Access registry/account grants/admission/actor columns; known PtS capabilities
   adopt account grants only through the separately approved PtS resource/Content transition.
   KDG organization grants remain distinct. Unknown/unmatched rows are not activated.
4. Before replacing membership uniqueness/CASCADEs or retiring legacy writer assumptions,
   characterize seed ON CONFLICT(org,user), Auth hooks/public role lookups, broad profile
   self-update/default grants and all supported direct writers. Narrow protected-column
   updates so users cannot change admin/system/actor mappings. No blanket service_role
   grant for new objects. Legacy-only finance/CS functions retain explicit disposition.
5. Deploy scoped role/client/query changes with coordinated Identity/Access/PtS consumers.
   Since current Access ignores admission/membership-instance and PtS v1 is not a target
   compatibility API, use planned maintenance for incompatible live cutover when actual
   old writers cannot coexist; specify backup, stop, migrate, verify, activate and recovery
   before live execution. Additive changes alone do not prove mixed-version access safety.

Owner compatibility matrix: profiles/Auth hook preserve supported account creation;
actor/profile UUID references preserve legacy attribution; member_role/get_user_roles/
JWT selectors reject retired/wrong-account members; Access old text creation fields
retain provenance; finance/CS/import text writers are retained or explicitly mapped, never
cast blindly. KDG's new writes use actor registry IDs only. No direct KDG Identity-table
access. Recovery preserves already-applied migrations, restores approved compatible
version/data through existing release procedure, and never auto-downgrades.

## Required evidence and impact

ID-A/B prove clean/adopt mismatch refusal, exact actor classification, stable account
mapping without person, no account recreation takeover, constrained lifecycle/foreign
IDs, member join races/old retry, effective PUBLIC/default privileges and no cascading
history loss. ACCESS-A/B prove scope FK integrity, explicit entry/bundles, grant revision/
rejoin/noop/concurrent recovery, selected own/all checks, filtered target pagination,
target replacement/revoke between list and save, setup-vs-runtime denial and actual
restricted-role RLS/search-path/connection-pool reuse. KDG A01/A02/A03/A14/A16 consume
these; WRITE supplies atomic owner outcome/audit fixtures. Synthetic scenarios use real
owner HTTP/query paths, not owner/migrator-role successes disguised as runtime proof.

Scaffold: proven owner migration/context/projection/command/client fixtures promoted in
existing items. Shared UI: no new identity/admin console. Agent context: current actor/
membership/exact command limits and actual verified commands only. Documentation: mutable
owner contracts/inventory/runbooks, not duplicate product stories. ADR: existing ownership,
actor/access/structural/release decisions suffice, none edited. All execution/rehearsal
is separately authorized delivery acceptance. WRITE outcome/evidence/secret details are
the next bounded planning gate; this does not assert readiness PASS or live transition.


Final WRITE checkpoint, 2026-10-14: the
[owned write/secret contract](owned-write-and-secret-execution.md) closes the formerly
open outcome/evidence/role/recovery and KDG secret-file/library planning choices.
Planning selections are complete for ordered shared foundations/KDG consumption;
actual owner/consumer test, target adoption, provider/device, release/restore and
pre-pilot policy evidence remain mandatory delivery gates. No code is authorized.
