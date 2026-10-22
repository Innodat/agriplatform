## Current delivery — KDG organization permission check,2026-10-22

Access15 and POST /v2/check implement the KDG organization check through the existing
owner: nine exact service-policy capabilities, configured organization, current account/
member, app enablement, nonrevoked exact-member grant and durable actor setup. Native
SQL→HTTP lifecycle/isolation verification, independent review and final custody pass; see
[owner evidence](../../../../services/access/ORGANIZATION_CHECK_EVIDENCE.md). No real grants or consumer activation were performed.
Legacy v1 checks fail closed pending coordinated PtS account adoption. Other account/
person/discovery/assignment-target variants are implemented when their consuming story
needs them. Leave still requires its own capability and denial acceptance evidence.
Next review remaining WRITE prerequisites for the first KDG business API operation;
do not expand Access variants speculatively. Production/deployment/pilot, Leave/editor,
reset/prune/cleanup and concurrent-document changes remain outside this delivery.

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
| identity.organization_target(p_org UUID) | Private setup-only point check: exact active organization UUID or no row, independent of accounts/memberships. Requires nonnil selected org and actor assertions, absent account context and exact typed org equality. EXECUTE only for staged access_command_owner; no metadata/list or effective grant. |

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
| identity_account_verification_owner | NOLOGIN/NOINHERIT/NOBYPASSRLS, exact migrator SET-only edge; separate Auth-owner USAGE and SELECT(id,deleted_at) under its exact SELECT policy; selected ordinary-profile reads under current account-targeted ensure authority; fixed private live-account/UUID-collision verifiers executable only by Identity command owner. No Auth writes, profile directory or runtime role assumption. Implements ADR-0056. |
| identity_target_projection_owner | Selected profile/member/org columns under current-org RLS, actor/mapping columns for fixed target routines; no Access table read/write. No cross-org target result. |
| access_check_reader | Read-only registry and selected account/org grant/admission columns under corresponding forced RLS; EXECUTE current Identity projections only. |
| access_target_reader | Read-only registry plus grants/admission restricted to verified target-query org; EXECUTE target Identity projections only. Dedicated NOLOGIN definer owner, no role assumption by runtime. |
| access_runtime | Own selected-context reads/check/discovery wrappers; no target-owner execution or cross-account grant scans. |
| access_target_runtime | EXECUTE exact user-context Access list/point routines only; no raw table privileges, owner-role assumption or arbitrary app query. |
| access_setup_target_runtime / access_setup_target_reader | Setup-only point wrapper with explicit setup context and current-org read predicates; no list/raw table privileges or user-role assumption. |
| access_command_owner | NOLOGIN command definer with exact local DML/sequence/outcome grants and EXECUTE Identity exact target-account/member and private setup organization verification only. No arbitrary Identity table privileges, DDL, authority-map updates or implicit target grant. |
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


## Delivered account actor command —2026-10-21

Identity revision18 implements the existing `account_actor.ensure` envelope and compact
account/actor result through the protected operator CLI. Required classification provenance
is an operator assertion; live Auth/profile eligibility comes from a separate pinned
SECURITY DEFINER verifier, not the evidence string. Its dedicated NOLOGIN owner receives
Auth schema USAGE and only SELECT(id,deleted_at) through separate Auth-owner preparation,
plus selected Identity profile columns under current-account-target authority. Caller roles
cannot assume either owner or provide verification through GUCs. Foreign legacy UUID
collision detection uses a fixed exact-authorized boolean Auth-ID query; the retained
profile→Auth FK protects that namespace without profile-directory access.

Auth observation precedes retry/business locks and lasts at most five seconds from
the start of verification, including both observations, for this executing command.
Elapsed observation, including replay expiry, reports unavailable rather than ineligibility.
Enabled Auth RLS is mandatory during preparation/head verification; unexpected verifier
memberships refuse before Auth/profile reads, including inherited-policy effects. After waits the command rechecks local profile and protected
authority. Missing/unsafe verification dependencies refuse as unavailable rather than
absence. New executions/replays observe again; historical receipt lookup needs current
exact account authority but does not assert current account eligibility. Mapping, creation
attribution, compact outcome and created event commit together; verified identical mapping
returns unchanged without a new event. Unbound account actors may be adopted only under
the verified account UUID with null key and matching label. Other bindings, occupied
foreign UUIDs, existing own legacy actors bypassed by another UUID, system/keyed profiles,
and changed kind/label refuse. Historical mapping/actor retention is unchanged.

See [owner evidence](../../../../services/access/ACCOUNT_ACTOR_ENSURE_EVIDENCE.md) for
actual restricted-login tests, preparation/recovery and exclusions. This realizes ADR-0056;
accepted ADRs and the ACCESS-A/B membership-binding activation gate remain unchanged.


Reviewed account-actor qualification uses the existing synthetic root bootstrap and one
`--all` invocation over fresh cases. The private input explicitly supplies a protected
closed CLI owner fixture bound to the selected run/database and loopback Identity-migrator
URL; general bootstrap portability is an existing deferred prerequisite. Named stages and
repeatable retained inspection remain. Bounded Auth UUID observations do not reserve future
Auth allocations, and overlapping profile retirement gains no extra row locks or write
privileges. Current application access remains independently checked. Exact reviewed
command/results and preserved candidate reconciliation are in the owner evidence above.


## Delivered Access staged membership storage —2026-10-21

Access revision2 adds nullable bigint grants.membership_id with named positive CHECK,
without default, backfill, cross-owner FK or activation. Opaque grant IDs, original keys,
text attribution, permission CHECK, forced RLS and read-only runtime privileges remain.
The existing owner route now checks exact known clean/1/2 catalogs and private history
before effects and before commit, with bounded waits and serialized owner execution.
Unknown state refuses without normalization; recovery uses the controlled upgrade.
Both Access roles' restricted flags, incoming owner/bootstrap authority and effective
callable Identity SECURITY DEFINER authority is checked. Grants and ledger must be permanent
and have no ordinary inheritance links. See owner evidence for the exact existing
Supabase bootstrap profile; no shared global role authority changes in qualification.

[Owner evidence](../../../../services/access/ACCESS_MEMBERSHIP_BINDING_EVIDENCE.md)
records actual restricted-role, rollback/contention and genuine Identity18 preservation
proof. This is only the first ACCESS-A storage increment. Current v1 ignores this field
and remains incompatible/stopped for real consumers until coordinated ACCESS-A/B
delivery. Future effective organization access requires exact active org/account/member
equality; NULL cannot match. Registry, commands, consumer/admission eligibility, PtS
adoption and KDG activation remain independently gated.

## Delivered Access private registry storage —2026-10-21

Access revision3 stages empty global applications, permissions and entry_permissions
through the existing controlled owner route. Exact known clean/1/2/3 catalogs retain
revision2 membership storage and all original grants/history/ACL/RLS. Registry attribution
uses required non-nil external actor UUIDs and finite timestamptz values without Identity
FKs. Registry app IDs use the ASCII grammar above; permissions accept literal ASCII1–200
bytes, including controls and DEL. Matching application association and both scope and
association unique keys are enforced locally with RESTRICT foreign keys.

Only access_migrator owns or can read/write the new tables and execute their private
trigger routine. Statement guards refuse UPDATE, DELETE and TRUNCATE, including empty
and noop statements; parent-table TRUNCATE without dependent tables also has PostgreSQL's
ordinary FK refusal. Registration commands, mutable application commands and readers need
later explicit migrations. Owner fixture inserts supply synthetic attribution, without
claiming protected command verification. No registry or grant rows are seeded, runtime
privileges added, retained organization grants reinterpreted or consumers activated.
See [registry evidence](../../../../services/access/ACCESS_REGISTRY_STORAGE_EVIDENCE.md).
Storage staging leaves the ACCESS-A/B and coordinated PtS/KDG gates closed.

Reviewed registry storage requires UTF8 server encoding before Access migration effects;
unsupported source encodings refuse without normalization. Internal FK-trigger enablement
is part of exact catalog verification. See registry evidence for the separate isolated
SQL_ASCII refusal and fresh reviewed acceptance frame; prior frames remain historical.

## Delivered Access registry command inputs —2026-10-21

The pure `services/access/access_operator_input.py:parse_command(body: bytes)` now
accepts only version1 `application.register`, `permission.register` and
`entry_permission.register` envelopes with platform scope and explicit expected absence.
Distinct immutable records preserve accepted spelling and redact their representations.
It reuses the unchanged Identity decoder, envelope, scope and validation primitives;
Access failures expose only `access_operator_input_invalid`, without decoder context.
Literal ASCII permission values retain whitespace, controls and DEL, except forbidden
NUL. Parsing checks neither authority nor registered associations and performs no I/O.

The Identity parser, adapter, worker and CLI still refuse these registry commands before
target/connection/SQL dispatch. See [input evidence](../../../../services/access/ACCESS_OPERATOR_INPUT_EVIDENCE.md)
for strict matrix coverage, initial missing-module RED, Identity characterization and
focused passing checks. This input-only increment supplies reusable owner-local scaffold
fixtures; shared UI, agent context and accepted ADRs need no changes. Documentation links
the bounded delivery. Protected Access execution, receipts, mutable commands, database
privileges and effective authorization remain later work. ACCESS-A/B and coordinated
PtS/KDG activation gates stay closed; historical runtime proofs remain source-bound.

## Protected application registration implementation — 2026-10-21

The bounded `application.register` slice is implemented through Access0004 and the
existing isolated operator CLI with explicit `--owner access`. New applications remain
disabled; no permission/entry registration, enablement, grants or effective consumer
checks are activated. [Owner runbook](../../../../services/access/APPLICATION-REGISTER.md)
and [evidence](../../../../services/access/APPLICATION_REGISTER_EVIDENCE.md) record exact
preparation, current authority, retry/lookup, immutable evidence and qualification.

An Access-only bounded synthetic target namespace derives a fresh database/descriptor
inside the actual prepared disposable run while preserving its private Access secret.
No arbitrary database selection or second runtime lifecycle is introduced. The mutable
Identity helper recognizes only the exact prepared Access role bundle and validates
Access0004 metadata before excluding its owner-local dependencies from historical
Identity comparisons. Identity migrations/references and Identity target behavior remain
unchanged; no cross-owner business reads or role assumption is granted.

## Protected permission registration implementation — 2026-10-21

Access0005 adds the bounded `permission.register` command through the existing Access
operator/authority/command owners. It preserves immutable literal permission/app/scope
associations, supports current-authorized retry/targeted lookup, and atomically records
creation attribution, `access.permission_registered` evidence and the compact typed
outcome. Application authority does not confer permission authority. Disabled applications
may receive registrations; effective access and entry/enablement/grant commands remain gated.

The owner outcome key now includes scope, executor, exact command and operation with
NULLS NOT DISTINCT, preserving populated Access4 rows. Application execute/lookup selects
its exact command/platform scope so shared operation UUIDs cannot cross receipt types.
The mutable Identity helper verifies exact Access4 or Access5 metadata according to installed
routines, without reading Access history or business rows. Historical migrations/references
remain unchanged. See the [permission runbook](../../../../services/access/PERMISSION-REGISTER.md)
and [evidence](../../../../services/access/PERMISSION_REGISTER_EVIDENCE.md) for controlled
migration/recovery, synthetic qualification, source custody and delivery limits.


## Protected entry registration implementation — 2026-10-21

Access0006 adds protected `entry_permission.register` through the existing operator
route. It verifies the literal permission's exact registered app association and records
an immutable entry binding, server attribution, compact outcome and creation event with
empty transition atomically. Identical mappings return unchanged. Both permission scopes,
disabled apps and multiple entries are supported. No access, permission creation,
enablement, grants or consumer activation is implied. Command-specific authority and
outcome keys isolate application/permission/entry commands even with a reused UUID;
lookup requires current exact authority and explicit exact target. Existing bounded
transaction, uncertainty and safe error contracts remain. This retains the delivered
single-event registration subset; it makes no generic multi-event WRITE claim.

Exact known Access4/5/6 metadata is selected by the mutable Identity helper, without
Access data/history reads. Historical migrations and references remain unchanged.
See the [entry runbook](../../../../services/access/ENTRY-PERMISSION-REGISTER.md) and
[evidence](../../../../services/access/ENTRY_PERMISSION_REGISTER_EVIDENCE.md).

## Application enablement input only — 2026-10-21

The existing Access parser also accepts `application.set_enabled` with exact platform
scope and payload `{app_id, enabled, expected_revision}`. Enabled is an actual boolean;
revision is a preserved positive canonical signed-bigint decimal string. Distinct frozen,
repr-redacted records reuse Identity's unchanged strict decoder and decimal validator.
The closed envelope, provenance, byte limits and safe validation errors remain binding.
Parsing grants no authority and reads no registry state.

At the input-only checkpoint, Access adapter/CLI execute refused this command as `command_unsupported` before effects;
outcome was `command_invalid`, and the worker retained its closed preconnection
rejection. Identity consumers reject Access inputs. Mutable registry persistence,
revision/evidence guards, protected enablement execution and runtime activation remain
separate work. See [input evidence](../../../../services/access/APPLICATION_ENABLE_INPUT_EVIDENCE.md).
Historical registration/runtime proofs remain bound to their original source bytes;
ACCESS-A/B and coordinated PtS/KDG consumer gates remain closed.


## Protected application enablement implementation — 2026-10-21

Access0007 implements `application.set_enabled` through the existing bounded owner
route. Its exact original-session command/platform/app authority is independent of
registration. New operations require current expected revision even for matching state;
changed input increments once with server actor/time and atomic compact outcome plus
`access.application_availability_changed` before/after event. Unchanged preserves the
entire application row and has no event. Guards protect identity/creation fields,
OLD/NEW revision/attribution and required immutable evidence; only command owner gains
UPDATE(enabled). Retry/authority/application locks, current-authorized replay/lookup,
four-command namespace separation and controlled migration recovery remain binding.
The single-event subset is retained. No digest inversion claim is made.

The owner verifier retains explicit clean/1/2/3/4/5/6/7 catalogs; Identity18 selects exact7
from installed-routine metadata without Access business/history reads. Historical
migrations/references, populated rows and original receipts remain retained. See the
[runbook](../../../../services/access/APPLICATION-SET-ENABLED.md) and
[evidence](../../../../services/access/APPLICATION_SET_ENABLED_EVIDENCE.md). This command
adds no grants, organization enablement or consumer activation. ACCESS-A/B and
coordinated PtS/KDG delivery gates remain closed.

## Organization application configuration input only — 2026-10-21

The existing Access parser accepts `organization_application.configure` with exact
organization scope `{kind: organization, org_id}` and payload `app_id`, boolean
`enabled`, and exactly one of `expected_absent: true` or a canonical positive bigint
`expected_revision` string. Distinct frozen, repr-redacted create/update payload records
contain only their selected fields. Existing Identity scope/decoder/validation helpers
are reused without changing Identity bytes. UUID spelling and large revisions are
preserved. Parsing performs no existence, authority or persistence checks.

Access adapter/CLI execute refuses valid new input as `command_unsupported` before
connection, target or dispatch; outcome remains `command_invalid`, and workers retain
closed preconnection refusal. Identity consumers reject Access input. The existing four
platform commands stay platform-scoped. See [input evidence](../../../../services/access/ORGANIZATION_APPLICATION_INPUT_EVIDENCE.md)
for matrix coverage and exact commands. Organization storage, external organization
verification and protected execution remain undelivered; grants, effective admission,
ACCESS-A/B and coordinated PtS/KDG activation remain gated. Historical runtime proofs
remain bound to their original source bytes.

Complete synthetic create input (parsing only):

```json
{
  "schema_version": 1,
  "operation_id": "A1234567-1234-1234-1234-123456789ABC",
  "command": "organization_application.configure",
  "scope": {
    "kind": "organization",
    "org_id": "B2345678-2345-2345-2345-23456789ABCD"
  },
  "payload": {
    "app_id": "fixture_app",
    "enabled": true,
    "expected_absent": true
  },
  "reason_code": "synthetic_fixture",
  "evidence_ref": "setup:fixture/1"
}
```

Complete synthetic update input (parsing only):

```json
{
  "schema_version": 1,
  "operation_id": "C3456789-3456-3456-3456-3456789ABCDE",
  "command": "organization_application.configure",
  "scope": {
    "kind": "organization",
    "org_id": "B2345678-2345-2345-2345-23456789ABCD"
  },
  "payload": {
    "app_id": "fixture_app",
    "enabled": false,
    "expected_revision": "9007199254740993"
  },
  "reason_code": "synthetic_fixture",
  "evidence_ref": "setup:fixture/2"
}
```

## Private organization application storage — 2026-10-21

Access0008 stages empty `organization_applications` with the selected composite org/app
key, local RESTRICT app reference, defaults and constrained external attribution. Only
access_migrator has table privileges. Owner helpers set org context with SET LOCAL;
ENABLE/FORCE RLS compares the current org setting and cannot attest its session versus
transaction lifetime. No runtime/auth guard is added. The reused immutable statement guard blocks mutation,
including empty/noop/UPSERT/MERGE
update arms. Fixture organization/actor UUIDs are not verified by this increment.
Exact clean/1–8 catalogs retain7 behavior and source pins. Identity18 selects8 through
relation metadata and fixed Access verification, without business/history reads or new
privileges. See [owner evidence](../../../../services/access/ORGANIZATION_APPLICATION_STORAGE_EVIDENCE.md).
External organization verification, protected configure execution and effective admission
remain undelivered. ACCESS-A/B and coordinated PtS/KDG consumer gates remain closed;
historical runtime evidence stays source-bound.

## Protected organization application configuration — 2026-10-21

Access0009 extends the existing operator/CLI with organization_application.configure.
The earlier input-only/storage checkpoints above are historical. Exact enabled principal
and command/org/app authority precede Identity19 organization_target; explicitly all-app
authority is allowed within its exact command/org, while platform authority is not.
The original session login selects the executor; caller context cannot grant authority.
Transaction-local setup context supports the private point observation. Every execution,
including replay, reobserves; five seconds from verification start covers verification
and subsequent waits. Expiry is unavailable, never evidence of ineligibility. Historical
lookup rechecks exact current authority and org/app target without requiring current
organization eligibility.

Create requires expected absence and records revision1; update requires matching revision
before changed/unchanged. Changed increments once with server attribution; unchanged
preserves the row and has no event. A registered app may be configured while globally
disabled; global availability and organization configuration remain independent inputs.
Disable/re-enable preserves settings/grants. Atomic organization-scoped outcome/event
uses target {org_id,app_id}, disposition created/changed/unchanged, decimal revision and
nullable event_id. Event access.organization_application_changed carries before=null on
create, otherwise prior enabled/revision, and after enabled/revision. Existing JCS/SHA256
fingerprint, current-authorized scoped recovery and operation-lock-only busy rule remain.
No admission/grant/reader or coordinated consumer activation follows from configuration.

Existing forced Access organization RLS/constraints remain; only command owner gains
narrow local DML, with current authority and deferred exact row/outcome/event proof.
Raw/unsupported writes, missing evidence and unknown catalog/history refuse without
normalization. Immutable historical Access1–8 and Identity1–19 sources/references remain.
Identity's mutable verifier selects exact9 from installed routine metadata without new
Access business reads. Existing four platform commands and previous adapter contracts
remain. See [owner runbook](../../../../services/access/ORGANIZATION-APPLICATION-CONFIGURE.md)
and [evidence](../../../../services/access/ORGANIZATION_APPLICATION_CONFIGURE_EVIDENCE.md).


## Delivered strict organization grant assignment input — 2026-10-21

The existing Access pure parser accepts `grant.assign` with exact organization scope,
account UUID, positive decimal-string membership and literal ASCII permission. Exactly
one expected_absent=true or expected_revision is required. It preserves UUID spelling,
permission bytes and large integer strings in frozen redacted variants. Parsing does
not verify identity, current membership, permission association or command authority.
Access adapter/CLI execute remain command_unsupported before target/connection/dispatch;
worker transport remains closed and outcome stays command_invalid. Identity refuses.
No persistence, grants, admission or consumer activation is delivered by these inputs.

Create example (synthetic identifiers only):

```json
{
  "schema_version": 1,
  "operation_id": "a1234567-1234-1234-1234-123456789abc",
  "command": "grant.assign",
  "scope": {
    "kind": "organization",
    "org_id": "b2345678-2345-4345-8345-23456789abcd"
  },
  "payload": {
    "account_id": "c3456789-3456-4345-8345-3456789abcde",
    "membership_id": "1",
    "permission": "kdg_capture.read.own",
    "expected_absent": true
  },
  "reason_code": "synthetic_fixture",
  "evidence_ref": "setup:fixture/1"
}
```

A later update/regrant requires a fresh operation_id, with the same envelope shape
and organization/account/permission target and this payload instead:

```json
{
  "account_id": "c3456789-3456-4345-8345-3456789abcde",
  "membership_id": "2",
  "permission": "kdg_capture.read.own",
  "expected_revision": "7"
}
```

The expected revision identifies the retained grant state; a new current membership may
only be bound by a later explicit verified command. No parsed input enables this write.
See [input evidence](../../../../services/access/GRANT_ASSIGN_INPUT_EVIDENCE.md).


## Staged organization grant lifecycle storage — 2026-10-22

Access0010 additively stages organization-only scope and positive revision (defaults
organization/1), nullable revoked_at, created_actor_id, updated_actor_id and updated_at.
New optional actors reject nil and new optional times reject infinity; null means
unverified retained history. Original IDs/keys/creation values/defaults, membership
binding, three-PtS permission CHECK, forced RLS and ACLs stay intact. No data adoption,
actor verification, permission FK, effective-row CHECK, revision automation, protected
command writer or effective access reader is delivered here. Existing legacy owner
writes remain compatible. Scope/revision fields alone never establish current authority.

Controlled migrations retain exact1–9 recognition and add exact10; current Identity19
verification selects10 from fixed pg_attribute metadata then verifies its full catalog
without Access business-table reads. Source/ACL/history drift blocks activation without
normalization. Release recovery remains explicit and forward; no startup migration or
automatic reversal. See [storage evidence](../../../../services/access/GRANT_LIFECYCLE_STORAGE_EVIDENCE.md).
Remaining registry/adoption, verified member binding, command evidence and consumer gates
must complete before removing old permission protections or activating KDG/PtS access.

## Existing pre-grant account/member projection — 2026-10-22

`identity.organization_account_target(uuid,bigint)` already exposes the exact five-value
account/member/revision/actor/display-name projection to `access_command_owner`.
Current consuming qualification targets Identity19/Access10; no new function, migration
or privilege is required. Setup context permits an absent/empty caller account with
trusted organization/service actor; existing valid user context remains supported.
These settings are backend assertions, not command authority.

The point read requires active organization/profile/membership and account-kind actor
mapping. It requires no pre-existing grant, admission, person or employment, and does
not perform live Auth verification. It never selects a replacement membership: after
retirement/rejoin only the explicitly supplied new membership can match. Read observations
do not lock membership or confer lasting authority. The later protected Access command
must enforce its own current command authority, bounded observation and write safeguards.
See [qualification evidence](../../../../services/access/IDENTITY_PREGRANT_TARGET_EVIDENCE.md).
Registry adoption/final grant integrity, protected assignment, membership-bound effective
readers, ACCESS-B and coordinated consumer activation remain separate gates.

## Grant registry compatibility bridge — 2026-10-22

Access0011 replaces the three-PtS-only grant CHECK with a temporary derived discriminator:
`registry_permission` is stored/generated NULL for the exact legacy three PtS literals,
otherwise equals `permission`. Its composite organization-scope FK requires a registered
permission for every nonlegacy row, including revoked rows. Nonlegacy active rows require
nonnull membership and actor/update provenance under the existing positive/nonnil/finite
constraints. These fields remain external references, not independently verified authority.
No original business values are adopted or changed; legacy PtS writes remain compatible without
fabricated registry mappings. All existing owner/RLS/ACL boundaries remain.

This is a compatibility bridge, not final adoption. Coordinated legacy disposition must
precede direct permission FK/global active-row integrity and removal of the derived column.
Protected assignment stays unsupported; later assignment must exclude the legacy PtS
literals while v1 readers ignore membership/revocation. No effective reader, ACCESS-B or
KDG/PtS activation follows. See [evidence](../../../../services/access/GRANT_REGISTRY_BRIDGE_EVIDENCE.md).


## Strict organization grant integrity — verified2026-10-22

The user confirmed PtS is not yet used and should adopt the infrastructure being built.
ADR-0052 already excludes legacy PtS API/organization-grant compatibility as a preservation
requirement. Access0011 above is historical delivery, not a requirement to retain that
bridge. Controlled Access0012 removes its generated discriminator:
direct permission/scope registry FK and required active-row membership/actor/update fields
apply uniformly. Incompatible rows refuse atomically without deletion, inferred account
grants or permission registration. Preserve corpus assets and immutable migration history.

Storage integrity does not finish PtS adoption. The caller inventory includes Access v1,
PtS backend Access/Content clients and org dependencies, Content's PtS check, frontend org
selection, corpus/import/source association and deployment fixtures. Upgrade these through
existing ACCESS-B/CONTENT-READ/PTS-ADOPT owner work, using typed account checks and the
[approved corpus/Content transition](../../../../apps/pts/docs/architecture/contracts/account-access-and-corpus-transition.md).
Do not extend legacy writes to constrain the target architecture. Keep current denial
until replacement activation; no unprotected interim reader or automatic org-to-account
authority conversion. Protected organization assignment remains the next dependent owner
command after strict storage verification; account storage/checks and coordinated consumer
activation remain separate work. See [bounded spec](../../../../_bmad-output/implementation-artifacts/spec-access-a-strict-grant-integrity.md).


Reviewed synthetic acceptance passes15 native stages and independent read-only retained
inspection. See [evidence](../../../../services/access/STRICT_GRANT_INTEGRITY_EVIDENCE.md)
and [runbook](../../../../services/access/STRICT-GRANT-INTEGRITY.md) for requirement mapping,
exact source/log/state custody and recovery limits. This completes strict storage only;
next deliver protected organization grant.assign through existing Access owner tools,
with current command/org/app/target authority, bounded Identity observation, expected
state, server attribution/revision, atomic receipt/event and retry safeguards. PtS
account access and coordinated reader/Content/corpus adoption remain gated; legacy
writes are not a compatibility target. No real access or consumer activation follows.


### Protected organization assignment increment —2026-10-22

Access0013 delivers `grant.assign` via the existing owner command path: exact current
command/org/app/account authority, Identity's existing bounded setup projection, expected
absence/revision, membership-bound creation or deliberate regrant, server attribution,
atomic receipt/event and exact recovery selectors. Preparation with disabled admission
is supported; a receipt proves a historical binding, not current effective access.
The deferred outcome guard rejects expired observations for changed and unchanged writes.
Prior five-command clients and immutable migration history remain preserved.
See [runbook](../../../../services/access/GRANT-ASSIGN.md) and
[evidence](../../../../services/access/GRANT_ASSIGN_EVIDENCE.md). No new Identity privilege,
generator, framework, shared UI or ADR is introduced. Protected revocation and effective
readers/ACCESS-B remain subsequent work; PtS adopts account scope through coordinated
consumer delivery. No consumer activation or real-account operation is implied.


Final reviewed assignment evidence:1519 affected tests PASS,13 native stages and separate
read-only retained inspection PASS; both composition checks exit0. Three review lenses
completed with direct verification/doc corrections and no deferral. Root source/log/state
custody audit passed; normal local stop retained data/volumes/receipts and older frames.
Concurrent work and immutable history remain preserved. See owner evidence above.


### Strict organization revocation input —2026-10-22

The existing Access pure parser now accepts grant.revoke with organization scope and
exact grant_id text/account_id/membership_id/permission/expected_revision. Opaque grant
IDs are preserved, including empty/Unicode values; common decoder/body limits apply.
No latest-member inference, normalization, authority or existence check occurs in parsing.
Valid revocation still refuses before target/connection/dispatch I/O at Access adapter/CLI/worker boundaries;
lookup remains invalid and Identity stays closed. Protected execution is the next
bounded dependency; effective readers/consumer activation remain separate. See
[owner evidence](../../../../services/access/GRANT_REVOKE_INPUT_EVIDENCE.md).


Revocation-input verification:130 focused and1649 affected tests PASS; both composition
checks exit0. Configured oneshot review completed with direct test/evidence corrections,
no deferral. All202 protected Access files and concurrent work remain preserved; durable
receipts are in owner evidence. No native startup or runtime revocation is claimed.


### Protected organization revocation increment —2026-10-22

Access0014 adds grant.revoke through the existing protected owner path. Exact retained
org/grant/account/member/permission/revision is checked before noop, with independent
current command/app/account policy and shared grant serialization. Changed removal keeps
original binding/creation, increments revision and writes server attribution/event/receipt
atomically. Already-revoked matching state records receipt only. No current Identity
eligibility is needed to remove historical authority. Assignment's verification remains.
Exact six-selector recovery requires current revoke authority and returns past completion.
The new command supports bounded large opaque IDs through canonical input, command-specific
database receipt bound and CLI transport; previous command bounds remain unchanged.
See [runbook](../../../../services/access/GRANT-REVOKE.md) and
[evidence](../../../../services/access/GRANT_REVOKE_EVIDENCE.md). No Identity privilege,
new service/generator/UI or ADR change; effective readers and consumers remain gated.


### Check-reader bridge rehearsal gate —2026-10-22

The new reader requires more than its planned schema/projection grants: native19
contains PUBLIC execution on sensitive legacy callable routines, including the token
hook. Independent rollback-only rehearsal refused before bridge activation. No20
reference or bridge grant was committed; original19/Access14 sources remain intact.
[Owner evidence](../../../../services/access/CHECK_READER_BRIDGE_EVIDENCE.md) records
the exact inherited-ACL findings and unapplied bounded prerequisite proposal. Preserve
supported Auth/Expense/Identity policy callers explicitly and verify negative reader
access before retrying. No runtime/HTTP/consumer activation or contract relaxation.


### Approved check-reader bridge delivery —2026-10-22

The six-routine execution-ACL prerequisite and private Identity0020 bridge now pass
synthetic controlled upgrade, compatibility, denial, rollback/retry and retained-state
verification. This supersedes the blocked rehearsal status above. Schemas, function
bodies/owners, historical migrations and Access14 remain preserved; PostgreSQL PUBLIC
execution is restricted to the approved callers. The private role receives only Identity
schema usage and current-account organization projection execution. See
[owner evidence](../../../../services/access/CHECK_READER_BRIDGE_EVIDENCE.md) for exact commands, source custody and review closure.
Next: the membership-aware selected-organization effective Access SQL reader through
existing owner tooling, then its HTTP/consumer gates. No account-reader, application
grant, PtS/KDG activation, real access, deployment or cleanup follows from this bridge.
