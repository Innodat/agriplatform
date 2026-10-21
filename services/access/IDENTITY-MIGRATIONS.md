# Identity baseline and durable actor foundation (ID-A / ID-B)

Identity retains its own migration history under the existing Access maintainer.
`identity-alembic.ini` uses `identity-migrations/`, `identity.alembic_version`, the
actual `identity_migrator` login and `IDENTITY_MIGRATION_DATABASE_URL`. Access's
`alembic.ini` and `access.alembic_version` remain separate. No process startup runs
these migrations. This recipe is owner-local and has not been promoted to scaffolding.

## Toolchain and verification

Run from repository root. The canonical owner lock uses Python 3.15, uv 0.13.1,
SQLAlchemy 2.1.4, Alembic 1.20.0, Psycopg 3.3.6 and pytest 9.1.1. Existing TypeScript
selection is unchanged. Install with the prepared pinned uv executable:

```sh
uv sync --locked --project services/access/identity-migrations --group dev
services/access/identity-migrations/.venv/bin/python -m pytest services/access/tests apps/pts/tests/test_release.py -q
python3 tools/py/run_compose_supabase.py --check-only
python3 tools/py/run_compose_supabase.py --identity-authority owned --check-only
```

Actual database qualification is root-controlled and uses explicitly synthetic native
Supabase/scratch databases, restricted LOGIN credentials, and supported Auth APIs.
See `tests/qualify_identity_baseline.py` and the retained qualification evidence. Do
not substitute ordinary development, production, real-account or provider targets.
Credentials stay in private prepared environment/files and never in argv/evidence.
Do not start Docker, replace shared resources or run seed fixtures on real accounts.

## Controlled setup

A restricted deployment administrator separately provisions the empty `identity`
schema owned by `identity_migrator`. The login is NOSUPERUSER, NOCREATEDB,
NOCREATEROLE, NOBYPASSRLS and has no inherited runtime authority. It needs CREATE/USAGE
on `public` for the inventoried compatibility function and narrowly approved Auth
integration privileges granted by their actual owners: auth schema USAGE WITH GRANT
OPTION via the schema owner (`supabase_admin` on the qualified native target), and TRIGGER,
REFERENCES(id), SELECT(id) on auth.users via its table owner
(`supabase_auth_admin` on that target). Inspect actual owners and verify effective
privileges: a GRANT warning that skips a grant is not proof of authority. Supabase-managed
Auth bootstrap remains a separate deployment responsibility; no Auth owner role or
other application schema authority is needed. `access_runtime` and standard Supabase
roles must exist. Role preparation is reviewed separately; source equivalence does
not justify new Auth INSERT authority for the legacy test helper.

The owned integration grants the retained legacy-composer `postgres` principal
USAGE on the Identity schema and REFERENCES(id) on identity.users and identity.org,
so CS/Expense foreign keys still bootstrap after source handover. These fixed grants
are included in the owned reference, separately from the legacy-source reference;
they confer no Identity schema ownership. The same internal fixed
`LEGACY_INTEGRATION_SQL` grants the retained synthetic Identity seed only its required
column-level reads and writes: users SELECT(id)/UPDATE(actor_key, is_system, username,
is_platform_admin, updated_at); org SELECT(id, slug)/INSERT(name, slug, created_by,
updated_by); org_member SELECT(id, org_id, user_id)/INSERT(org_id, user_id, is_owner,
created_by, updated_by); member_role INSERT(member_id, role, created_by, updated_by).
No DELETE, blanket table DML, Auth INSERT or new runtime authority is granted. Existing
Auth-owner bootstrap must separately authorize the legacy synthetic seed's Auth inserts;
these do not become Identity migration privileges.

With the private prepared owner URL exported, a clean synthetic setup runs:

```sh
services/access/identity-migrations/.venv/bin/python -m alembic -c services/access/identity-alembic.ini upgrade head
```

Only a genuinely empty, owner-controlled Identity schema is eligible for clean setup.
Unknown schema objects, empty/foreign version ledgers, owners, privileges/defaults or
conflicting legacy history refuse before persistent changes. Both CLI and Python
Alembic stamp/ensure-version routes are prohibited. All SQL and the ledger update
share one bounded PostgreSQL transaction; source outer BEGIN/COMMIT wrappers are
removed without changing historical files. The exact pinned initial CREATE SCHEMA IF
NOT EXISTS statement is also omitted because separate controlled bootstrap already
provided the schema; PostgreSQL otherwise requires database-wide CREATE even for
that no-op. No database CREATE grant is conferred on the migration login. An owner advisory lock prevents competing
Identity runners only; lock timeout is 5s and statement timeout 60s. Controlled setup
and adoption run under the existing coordinated release lock without concurrent
privileged DDL, ACL changes or permission-seed editing. The advisory lock does not
exclude noncooperating administrative sessions.

After migrations and private ledger grant cleanup, the same transaction requires the
exact known current-account projection head (`identity_0003`), validates private ledger table and column ACLs, rechecks the
legacy source history and verifies the complete owned catalog fingerprint. This
postcondition applies to clean setup, adoption and retries; an unknown/elevated profile
or an upgrade target that leaves an empty ledger rolls back before commit. The trusted
source-derived reference must already be recorded and pinned; no bootstrap bypass
or target self-approval is available.

For equivalent legacy synthetic state, use the same upgrade command with
`IDENTITY_MIGRATION_MODE=adopt`. Adoption first compares a read-only catalog against
the pinned repository reference, applies only the existing Access bridge and records
`identity_0001` before the additive `identity_0002` step in the same transaction. It never reruns source CREATEs or edits the original Supabase ledger.
Any six historical source entries found must form the complete exact named source
set. An absent ledger is supported for a manually established source-equivalent
schema. Unknown Identity history refuses. Business rows, sequence values and external
references are preserved; this is schema adoption, not account/data migration.

The reference is recorded independently from known clean pinned sources by the
synthetic qualification owner. `reference.json` contains legacy and owned normalized catalog category SHA256
fingerprints, row counts and source hashes; its exact digest is pinned in
`identity_baseline.py`. Category fingerprints use canonical JSON with sorted keys,
compact separators and ASCII escaping over the unchanged normalized catalog rows.
This preserves exact category comparison without duplicating raw schema definitions. There is no
caller-selectable reference path, target approval/export command or bypass flag.
The snapshot compares types, columns/defaults, constraints, indexes, sequence
configuration, RLS, routines, external Auth trigger, owners, ACL/default privileges,
role attributes/memberships, effective schema/table/column/function/sequence authority
and semantic role-permission seeds. Only OIDs/physical identities, sequence current
values and seed attribution/IDs/timestamps are excluded. Catalog values are not
printed on mismatch; errors identify safe categories. PostgreSQL 15+ is required.
The root qualification records provenance and hashes before pinning the reference.

The reference is exact: a legacy schema owned by another principal, including a
historical postgres-owned schema, is not automatically equivalent to the restricted
owner fixture. Production's documented PUBLIC get_user_roles revocation likewise
refuses rather than replaying old source grants. Resolve differences through an
explicit owner-reviewed compatible migration/design and independently trusted fixture;
never approve the target against its own exported catalog.

## One source authority and coordinated release

Default composition remains legacy. Explicit owned composition excludes precisely
the six inventoried Identity DDL sources while retaining CS, finance and other owners,
and records `identityAuthority` plus the Identity prerequisite in its manifest.
Run Identity before applying dependent composed SQL/seeds. Do not hand-edit generated
outputs or replay legacy Identity DDL after owned adoption. Owned composition rejects
`--no-clean` if historical Identity outputs would remain and produce duplicate
execution. Preserved historical sources and the old bridge remain source evidence.

The existing coordinator gains the explicit opt-in route:

```sh
services/access/identity-migrations/.venv/bin/python tools/py/deploy_pts.py --identity --release-id SYNTHETIC-ATTEMPT-ID --evidence /tmp/fresh-release-evidence.json
```

Prepare all four owner URLs through private environment first. The existing deployment
lock covers Identity, Access, Content, PtS in that order. Reports retain per-owner
before/after revisions and succeeded/failed/not_attempted states. Identity failure
stops every later owner; later failure preserves already-applied Identity history.
`activation_allowed` remains false even after migration completion: configuration,
previous-version compatibility and authorized release activation are separate checks.
The default coordinator route remains Access/Content/PtS.

## Recovery and compatibility limits

Never downgrade destructively or auto-reverse applied migrations. On failure retain
the report and database evidence, reconcile actual histories, repair through an
explicit forward migration or restore a tested backup under the coordinated recovery
procedure in ADR-0020. Retry only after reconciliation; completed baseline upgrades
verify the owned catalog/history before returning unchanged. A prior application can
be retained only after verifying compatibility with actual database state.

This delivery preserves legacy broad profile update/default grants, PUBLIC helper
execution and JWT role behavior. Qualification must characterize them explicitly;
ID-A does not claim legacy helpers are authorization-safe or silently harden them.
`access_runtime` receives only scoped organization/member SELECT columns and cannot
write profiles, organizations, members, grants or privileged fields. The Auth hook
retains account profile creation and existing claim behavior. The legacy create_user
helper remains defined but is not supported real-account provisioning; administrator
Auth INSERT authority is deliberately not conferred on the migrator.

The additive actor persistence foundation is described below. Controlled actor/account
provisioning, revised membership lifecycle, account/grant adoption and Access v2 remain
later ID-B/ACCESS work. No readiness promotion, Leave implementation, runtime service,
new release runner or deployment is introduced.

## Acceptance traceability and impacts

| Requirement | Evidence |
| --- | --- |
| Pinned sources and prohibited downgrade | `tests/test_identity_baseline.py` |
| Trusted reference and mismatch refusal | `tests/test_identity_baseline.py`; root synthetic clean/adopt/mismatch qualification |
| Legacy/owned composition, other owners retained, duplicate refusal | `tests/test_identity_composition.py`; both composer check-only commands |
| Identity before Access; failure stops dependencies; separate configuration | `apps/pts/tests/test_release.py` |
| Partial failure, existing PtS route, activation false | existing and extended release tests |
| Real LOGIN clean/retry/adopt/history/ACL/trigger/owner/default refusal | root `tests/qualify_identity_baseline.py` and retained reports |
| Supported native Auth creation/hook and scoped Access denials | root native Auth/runtime qualification and retained reports |

Scaffold: owner-local recipe remains unpromoted pending first-consumer proof. Shared
UI: none. Agent context: existing rules suffice. Documentation: this runbook plus
root-owned inventory/evidence/navigation handoff. ADR: existing 0016/0017/0020 and
Identity decisions govern; accepted ADRs are unchanged. Exact execution commands,
results, reference/lock/source hashes and normal environment stop are retained by
root qualification; unit tests alone are not actual restricted-role/Auth proof.


## Additive durable actor persistence (ID-B)

The actor foundation was introduced at `identity_0002`; the current route finishes at
`identity_0003` as described in the restricted projection section below. Preflight recognizes
exact private revision1/revision2 ledgers and the current revision3 ledger, comparing the catalog
against the reference for that revision before running any upgrade. Revision1 still
uses the original `reference.json` and original source pins byte for byte. Revision2
uses the additional fixed `actor-reference.json`, whose own digest and revision2
migration digest are pinned and checked. The final transaction requires revision2;
requests leaving the old head, unknown history, modified catalogs or unavailable
references roll back. Clean and verified adoption routes run both revisions in order;
an existing qualified revision1 receives only the additive step. Current-head retries
verify the full catalog and leave rows unchanged. Stamp and downgrade remain prohibited.

`identity.actor` stores stable account/system/service attribution without any Auth,
person, employment or organization dependency. `identity.account_actor` retains one
unique immutable account-to-account-kind actor association with no external Auth FK.
Neither table is an admission, membership, role or grant. Empty schema migrations seed
no actors or mappings, and account mapping existence does not verify a real account.
Later controlled provisioning must establish classification and live-account evidence.

Actor IDs and kind, assigned keys, and creation actor/time cannot change. A null key
may be assigned once; display labels may change. Local actor FKs use RESTRICT, including
the account-kind composite mapping FK. Actor deletion and truncation are rejected;
mapping update, deletion and truncation are rejected. Nil IDs, invalid kinds, blank or
more-than-200-code-point labels, invalid ASCII keys and conflicting mappings fail at
the database boundary. PostgreSQL rejects NUL text before the row can be stored.

No runtime actor selector or operator command is introduced. Only the actual
`identity_migrator` owner may exercise the new write triggers. Explicit synthetic owner
fixtures supply `created_by`, including a self-reference for a first bootstrap actor;
actor insertion derives `updated_by` from it. The server overrides insert timestamps
with `statement_timestamp()` and updates the last-change time for label/key changes.
No-op updates retain prior last-change fields. Fixture attribution is not a permission
to adopt real identities; runtime executor derivation remains a later delivery gate.

Legacy default privileges remain unchanged for existing consumers. The migration
revokes inherited/default ACL entries from every nonowner grantee on both new tables
and guard functions, including PUBLIC function execution. No new sequence exists.
The migration owner retains raw authority; ordinary browser, runtime and Auth roles
receive no new table or function privileges. Privileged database administrators,
including the qualified vendor postgres with pg_read_all_data/owner memberships,
retain their pre-existing administrative authority; this is not a sandbox against them. Functions have a fixed
`pg_catalog, pg_temp` search path and enforce retention at the structural boundary.

The synthetic qualification owner records the additional fixture through:

```sh
OWNER_PYTHON -I -B services/access/tests/qualify_identity_baseline.py --record-actor-reference
```

`OWNER_PYTHON` means the prepared fresh interpreter verified against the existing
owner lock, not an arbitrary system interpreter. The private validated qualification
fixture must include a genuinely empty `actor_reference` scratch case. The recorder
executes the original pinned sources, bridge and fixed integration, verifies the old
owned catalog, and applies the new revision SQL inside a transaction that always rolls
back. It rechecks clean eligibility after rollback and atomically publishes the new
fixture exclusively. It never approves an existing target catalog or alters the old
reference. Recording is developer fixture work, not a migration bypass or release step.

If fixture publication is interrupted, stop recording and preserve every partial
output, the module pin, private receipt/log and any `.actor-reference-recording` file.
An existing temporary file may belong to another recorder and must not be removed by
a competing invocation. Inspect source/pin/file identities and reconcile which steps
completed; a published file without its matching pin is not usable trusted evidence.
Retain partial artifacts separately before an authorized retry. Re-record independently
from the known pinned sources in a fresh empty synthetic case and compare the evidence;
never fill a missing pin by approving a target's exported catalog. Original ID-A
reference bytes and its pin remain unchanged. No automatic recovery or cleanup engine
is introduced.

Actual restricted-login tests and exact commands/results live in
[ACTOR_FOUNDATION_EVIDENCE.md](ACTOR_FOUNDATION_EVIDENCE.md). The implementation retains
legacy Auth hook/profile behavior, existing membership/role semantics, application
references and old source history. Release activation remains blocked until the
coordinated owner migration and relevant compatibility verification pass. Recovery
uses reconciliation and explicit forward repair or tested restore; no automatic
reverse migration is available.

Scaffold: the recipe remains owner-local and unpromoted. Shared UI: none. Agent
context: existing rules suffice; no update. Documentation: this runbook and root-owned
evidence, inventory and KDG navigation. ADR: existing 0020/0025/0056 govern the change;
accepted ADRs remain unchanged. Runtime projections, operator/outcome commands, account
adoption and authorization are outside this persistence-only foundation.


## Restricted current-account actor projection (ID-B)

The existing owner route now finishes at `identity_0003`. Before controlled migration,
a deployment administrator prepares the dedicated NOLOGIN reader using
`tools/prepare_identity_projection_role.sql`. This delivery executes preparation only
on its isolated synthetic target. The script deliberately refuses an existing role;
it does not repair or adopt unknown authority. The reader is NOSUPERUSER, NOINHERIT,
NOCREATEDB, NOCREATEROLE, NOREPLICATION and NOBYPASSRLS. Its sole membership permits
`identity_migrator` to SET ROLE, without inheritance or ADMIN OPTION. PostgreSQL 15
uses the migration login's existing NOINHERIT flag; PostgreSQL 16+ uses explicit
membership options. Operational qualification is PostgreSQL 17 only; the older
membership syntax branches are unqualified compatibility paths, not delivered
PostgreSQL 15/16 version proof. Runtime has no reader-role membership. Missing, unsafe or nonempty
preparation refuses with a safe `identity_projection_role_*` identifier.

The actual Auth schema owner must separately grant `identity_migrator` only Auth
schema USAGE WITH GRANT OPTION. Preflight checks this effective grant option before
source execution and refuses with `identity_projection_auth_grant_required` when
absent. Ordinary pre-existing schema USAGE alone cannot delegate the reader's grant.
This controlled prerequisite does not confer Auth ownership, table reads or writes,
CREATE, or another owner's role. The prepared reader stays empty until revision3;
there is no outside-transaction reader grant to normalize against old evidence.

Revision3 grants the reader Identity and Auth schema USAGE, profile SELECT(id, deleted_at), mapping
SELECT(account_id, actor_id, actor_kind), and actor SELECT(id, kind, display_name).
Auth USAGE is needed by the unchanged legacy PUBLIC profile policy's `auth.role()`
helper; no Auth table privilege or Auth CREATE is granted to the reader. The new-state
fixture explicitly verifies Auth USAGE, CREATE and both grant-option outcomes in
addition to Identity privileges. It adds both permissive and restrictive
current-account profile read policies: the
restrictive bound prevents legacy PUBLIC policies broadening this reader's access.
Schema CREATE exists only during ownership transfer and is revoked before commit.
No profile or actor writes, raw runtime reads, broad table privileges or owner-role
assumption are granted. All default routine ACL entries are removed before granting
only `access_runtime` EXECUTE on `identity.current_account_actor()`.

The STABLE SECURITY DEFINER routine has fixed `pg_catalog, pg_temp` search_path and
qualified objects. It requires `app.context_kind=user` and a valid nonnil verified
`app.account_id`, set transaction-locally by the backend. Actor and organization
settings do not select the account. It returns exactly account_id UUID, nullable
actor_id UUID and nullable display_name text. An active unmapped profile returns its
account with null actor/label; missing or deleted profiles and invalid contexts return
no row. Mapping is never provisioned as a read side effect. No person, employment,
organization, public RPC, service endpoint or application admission is introduced.
These GUCs remain verified backend assertions, not authentication against a compromised
database credential. The legacy Access API's actor GUC still means Auth account;
`main.py` and its existing behavior remain unchanged.

The old source files, revision1/revision2, `reference.json` and `actor-reference.json`
remain byte for byte evidence. The new `projection-reference.json` is independently
recorded from clean pinned source execution in a rollback-only transaction and pinned
by its own digest plus revision3 migration digest. The original catalog queries stay
unchanged. Old-state comparison removes only the exact newly staged membership, after
independently verifying reader flags, sole membership and empty current-database/shared
ACL and ownership dependencies. It never suppresses unrelated grants or catalog drift.
Other databases keep independent migration histories. New-state comparison adds reader
flags, memberships, effective schema/table/column/function/sequence privileges and
ACL/ownership dependencies to the full original catalog evidence. Unknown history,
old final heads, unsafe staging, changed references and failed postconditions roll back
the complete migration transaction. No target export/approval bypass exists.

Root qualification records the trusted reference with the existing owner helper:

```sh
OWNER_PYTHON -I -B services/access/tests/qualify_identity_baseline.py --record-projection-reference
```

The private fixture must identify the separate empty `projection_reference` case.
The projection recorder does not edit `identity_baseline.py`. It emits and records the
new reference digest and the captured helper/source digests. After successful independent
recording, explicitly reconcile those bytes against the retained receipt, then update
only `PROJECTION_REFERENCE_SHA256` to the recorded digest through a reviewed source edit.
The fixture remains unusable until that explicit pin update. The recorder checks all
three captured revision sources, source pins and helper bytes are unchanged immediately
before exclusive publication. Publication and interruption recovery retain the same
exclusive temporary-file and source/pin reconciliation rules as actor-reference recording. Never approve a target
against its own exported catalog. Existing applied migrations are never reversed
automatically. Recover by reconciling actual history and using reviewed forward repair
or a tested restore under ADR-0020. Old application queries/profile hooks and retained
memberships remain compatibility requirements. Neither role preparation nor passing
synthetic acceptance permits live deployment or readiness promotion.

Traceability: `tests/test_identity_baseline.py` records the initial missing-projection
acceptance RED and tests revision linkage, read contract, exact final-head selection,
fixed-reference corruption refusal and unsafe preparation. Root's actual restricted
PostgreSQL qualification covers mapped/unmapped/missing/deleted accounts, spoofed
actor/organization context, actual-login privilege denial, malicious search_path,
transaction-local connection reuse, old-head/clean/adoption upgrades and failure
preservation. Exact execution results and receipts are in the projection evidence;
unit checks alone do not establish actual restricted-login acceptance.

Scaffold: owner-local/unpromoted; no generator added. Shared UI: none. Agent context:
existing account/actor separation remains sufficient. Documentation: this runbook plus
projection evidence, mutable inventory and KDG navigation. ADR: existing 0018/0020/0056
and the selected substrate suffice; accepted decisions are unchanged.

## Restricted selected-account organization projection (ID-B)

The owner route now finishes at `identity_0004`. The existing reader preparation and
Auth schema grant-option prerequisite remain in force; no new roles or operator
commands are introduced. Exact revision3 catalogs continue to use the immutable
`projection-reference.json`; only revision4 uses `organization-reference.json`.
Preflight validates every earlier fixed fixture and migration digest before trusting
this new fixture. The old reference files, migration sources and source pins remain
unchanged. Clean/adopt execute all four steps transactionally; a verified head3
receives only revision4. Final-head checks require revision4, and current-head retries
compare the complete reader/catalog authority before doing any work.

`identity.current_account_organization()` is an internal STABLE SECURITY DEFINER read
with fixed `pg_catalog, pg_temp` search path and qualified owner objects. It requires
`app.context_kind=user`, valid nonnil verified `app.account_id` and selected
`app.org_id`. It returns exactly account_id UUID, org_id UUID, membership_id bigint,
membership_revision bigint and nullable internal actor_id UUID. Only nondeleted
profile, selected organization and matching membership qualify. An absent actor map
returns the same tuple with null actor; no mapping, actor, person, membership or
application grant is created. Actor assertions and JWT claims do not choose accounts.
This read grants no application admission and does not change the old Access HTTP API.

The existing nonowner reader receives SELECT only on required organization/member
columns. Paired permissive and restrictive policies require user context, selected organization
and a nondeleted row on `org`; `org_member` additionally requires the current account
and nondeleted membership. The function validates account and organization context and
joins the current nondeleted profile, organization and membership. Ordinary runtime
cannot assume the reader role; legacy PUBLIC policies cannot broaden this reader. The
reader remains RLS-bound; this item does not apply FORCE RLS or replace legacy
membership uniqueness, CASCADEs, retirement/unretire or attribution semantics. Runtime
receives only exact function EXECUTE. All inherited/default ACLs on the two new
functions are cleared; no broad legacy table permissions are revoked or added.

The additive member `revision bigint NOT NULL DEFAULT 1 CHECK > 0` is server managed.
Existing rows receive 1. A BEFORE INSERT/UPDATE guard overrides insert revision to 1,
compares every persisted nonrevision field and increments once on an actual change.
No-op updates preserve revision, including attempts to supply another revision.
The guard rejects a changed row at bigint maximum with SQLSTATE23514 and the safe
`identity_membership_revision_exhausted` identifier; the write rolls back atomically.
Supported seed `ON CONFLICT(org_id,user_id)` and unretire operations keep existing IDs
and change revision only when persisted values change. This does not introduce new
membership lifecycle rules or actor backfill.

Root records the independent rollback-only fixture with the existing recorder:

```sh
OWNER_PYTHON -I -B services/access/tests/qualify_identity_baseline.py --record-organization-reference
```

The private validated frame must identify an empty `organization_reference` case.
The recorder captures and executes all four migration sources, verifies prior
catalogs, captures helper/source pins and all prior immutable fixtures, rolls back,
rechecks empty eligibility and publishes exclusively. It leaves the helper unchanged
and emits captured digests plus `pin_update_required`. Root reconciles the receipt
against exact source/reference bytes before explicitly setting
`ORGANIZATION_REFERENCE_SHA256`. Existing destination/temporary files are not
replaced; interrupted recording follows the same retained-artifact reconciliation
rules as the projection recorder. No target catalog may approve itself.

Verification traceability:

| Requirement | Evidence / command |
| --- | --- |
| Prior fixtures remain trusted, head4 required, source changes/exclusive recording refuse | `OWNER_PYTHON -m pytest -q services/access/tests/test_organization_qualification.py services/access/tests/test_projection_qualification.py` |
| Actual restricted login, selected scope, nullable actor, no write side effects, RLS, search path and transaction cleanup | `OWNER_PYTHON -I -B services/access/tests/qualify_current_account_organization.py`, restricted-selected-organization-matrix |
| Insert/change/no-op/forgery/overflow; all legacy fields; seed upsert and unretire | Same actual qualifier, membership-revision-and-legacy-upsert |
| Clean/adopt/exact committed head3, old rows/external refs/Access queries/Auth profile hook, failure rollback, unsafe authority/history/catalog refusal | Same actual qualifier, organization-foundation-matrix and actual Auth-admin LOGIN token hook on the scratch database; vendor JWT pipeline remains separate |
| Owner unit regressions and release coordination | `OWNER_PYTHON -m pytest -q services/access/tests apps/pts/tests/test_release.py` |

Root retains actual command results, source/lock/reference hashes, exclusive receipts
and normal environment stop in organization evidence. The first full owner unit run
exposed an obsolete head3-as-final assertion (102 pass/1 fail); head3 now retains its
prior catalog check while dedicated head4 tests enforce the new final boundary.
After that explicit boundary update, `services/access/tests` passed 103 tests.
Focused recorder/provenance tests passed 43 tests before actual recording. These
checks do not substitute for actual PostgreSQL acceptance.

A failed migration blocks activation and preserves the previous schema/history in
its transaction. Reconcile actual owner history and retained evidence before retry;
use an explicit forward repair or tested restore when required. Never downgrade or
automatically undo applied migrations. Previous-version compatibility here covers
retained legacy reads/writers/hooks, not unfinished operator/lifecycle hardening or
HTTP adoption, and does not authorize deployment.

Scaffold: owner-local/unpromoted, no new runner or generator. Shared UI: none. Agent
context: existing instructions suffice. Documentation: this runbook and root-owned
organization evidence/inventory/KDG navigation. ADR: existing 0018/0020/0056 and the
selected substrate suffice; no accepted ADR edits or new decisions.


Organization qualification also reads an advanced committed revision through actual
`access_runtime` and verifies a committed no-op leaves it unchanged. Bounded competing
connections prove two committed changes advance twice. Actual retained SQL-seed writer
proof uses privileged vendor `postgres` LOGIN and records actual owner membership
and inheritance separately; it makes no
service_role or PostgREST endpoint claim and changes no grants. Overflow proof checks
whole-statement rollback for both an exhausted and an eligible membership.

## Strict operator input boundary (ID-B, parser only)

`identity_operator_input.parse_command(body: bytes)` parses one version-1 Identity
command and returns frozen command, scope and payload dataclasses. The four accepted
commands are `actor.register_system`, `account_actor.ensure`, `membership.join` and
`membership.retire`. This is a stdlib-only, owner-local parser: it performs no database
access, target binding, executor authentication, authorization, account verification,
receipt lookup or execution. No CLI is installed by this boundary. A parsed owner
flag is only a request; later execution of `membership.join` with `is_owner=true`
still requires the separate protected `membership.join_owner` authority.

Call it from owner-local Python with UTF-8 JSON bytes; inspect the typed fields only
in controlled application logic. `CommandValidationError` exposes only the fixed
`identity_operator_input_invalid` code/message. Decoder exceptions are not chained,
and command/scope/payload reprs omit their fields. Do not log submitted bytes or typed
payload fields, or infer authorization from successful parsing.

The input is limited to 65536 bytes, including whitespace, with strict UTF-8 and JSON:
no BOM, duplicate keys (including escaped aliases), nonfinite numbers, NUL or lone
surrogates anywhere. Excessive decoder/traversal nesting and oversized integers fail
with the same safe error. Unknown fields at every level are rejected, including
executor/authority overrides. Version is exactly integer 1; boolean flags require
actual JSON booleans, and expected absence is exactly true.

UUIDs use only the standard hyphenated spelling with upper/lower hex preserved; nil,
compact, brace and URN forms fail. Membership IDs/revisions are canonical positive
ASCII decimal strings bounded by signed bigint maximum `9223372036854775807`; numeric
JSON IDs, zero and leading zeros fail. `expected_previous_membership_id` is required
and may be null for first-ever join. Scope is exactly platform for actor commands or
organization with nonnil `org_id` for membership commands. Omitted `is_owner` is false.

Actor keys match `[a-z][a-z0-9_.:-]{0,127}`. Display labels retain Unicode unchanged,
with 1–200 code points and at least one character outside the exact Unicode
White_Space set used by revision2's database constraint. No Unicode normalization or
Python `str.isspace()` substitution is used. Reason codes are limited to
`initial_setup`, `synthetic_fixture`, `identity_adoption`, `access_change` and
`setup_correction`. Optional evidence references match
`[A-Za-z0-9][A-Za-z0-9_.:/-]{0,255}`, excluding `://`; null, query strings and URLs
fail. `account_actor.ensure` requires the envelope reference, but parsing it does not
verify that evidence or a live account.

Parser acceptance and lexical/safety boundaries are covered by
`tests/test_identity_operator_input.py`. From repository root, using the prepared
canonical qualification interpreter:

```sh
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 platform/deployment/.local/identity-baseline/qualification-im60qj1l/owner-env-djguxc78/offline-venv/bin/python -I -B -m pytest -p no:cacheprovider services/access/tests/test_identity_operator_input.py -q
```

Scaffold: this bounded parser remains owner-local; no generic framework or generator.
Shared UI: none. Agent context: existing rules suffice. Documentation: this runbook
and root-owned delivery evidence. ADR: no new decision or accepted ADR edit. Parser
tests do not prove execution authority, runtime adoption, database changes or readiness.

## Protected operator authority foundation (ID-B, revision 5)

`identity_0005` adds protected `operator_principals` and `operator_authorities` and
`identity.current_operator_authority(text,text,uuid,uuid)`. It creates no actors,
principal mappings or grants. A successful read selects current authority metadata;
it does not provision anything or authorize a later command without a fresh check
inside that command's short transaction. Operator effects, outcomes/events, CLI/target
preparation, membership hardening and Access/WRITE remain separate increments.

The deployment administrator separately runs
`tools/prepare_identity_operator_roles.sql` on the authorized target. This creates
`identity_operator` (LOGIN) and `identity_operator_authority_owner` (NOLOGIN), both
NOINHERIT and without superuser, database/role creation, replication or RLS bypass.
Preparation requires the controlled true-superuser administrator before creating
anything (qualified local fixture login: `supabase_admin`). The nonsuperuser vendor
`postgres` login is refused; PostgreSQL 16+ would otherwise add unwanted creator
ADMIN memberships. No automatic creator-edge repair is attempted.
Only `identity_migrator` receives SET-only, non-admin membership in the definer owner;
operator receives no memberships. On PostgreSQL 15 the migrator must already be
NOINHERIT, since per-membership INHERIT/SET options require PostgreSQL 16. Only the retained PostgreSQL 17 synthetic target is runtime-qualified by this
delivery. PostgreSQL 15/16 compatibility branches are code paths, not execution or
adoption acceptance for those versions. Existing
role names fail preparation atomically; neither preparation nor migration repairs
unsafe roles. Credentials are supplied separately through the existing protected
local target mechanism, never checked into SQL or passed in argv/evidence.

The migration verifies restricted role flags, membership edges, empty staged ownership/
ACL dependencies and effective privileges. Effective non-system sequence USAGE/UPDATE
is refused, including PUBLIC grants. Executable external SECURITY DEFINER routines
are refused except the exact existing `public.get_user_roles()` legacy read boundary,
whose definition and ACL remain canonically verified; this does not change its legacy
grants. Ordinary invoker Auth/UUID helpers remain compatible. Historical catalog comparisons accept only
the exact separately validated empty staged owner membership. After revision 5, the
new independent canonical catalog protects role flags, memberships, dependencies,
function ownership/definition/ACLs, table constraints/triggers/ACLs, and effective
schema/table/column/function/sequence privileges. All old reference files and revision
sources remain immutable. The head5 reference chains through the head4, head3, actor
and original reference verification; it does not replace their pins.

Only the migrator may perform controlled authority record changes, with explicit
verified attribution and deployment change/recovery evidence. This is not an ordinary
configuration API. Mapping keys/executor and authority tuple identity are immutable;
enable/disable is revisioned, and deletion/truncation is refused. Insert revision is
server-owned 1, changed enabled state increments it with overflow refusal, and no-op
revision/time/attribution forgery is ignored. Creation and update instants are server
statement timestamps. Actor references and principal linkage use local RESTRICT FKs;
null application scope, selected command/scope shape, nonnil UUIDs and NULLS NOT DISTINCT
full-tuple uniqueness are structural constraints. No unrelated actor/member behavior
changes in this revision.

The fixed STABLE SECURITY DEFINER read uses `session_user`, never the effective SET ROLE,
JWT, caller GUC or payload actor. It returns only executor actor UUID, principal revision,
authority UUID and authority revision, or no row. It supports:

- `actor.register_system`: platform scope, null organization and null account target.
- `account_actor.ensure`: platform scope, null organization and a nonnil account target.
- `membership.join`, `membership.retire`, `membership.join_owner`: organization scope,
  nonnil organization and account target. Join-owner is independent; a future owner join
  must check both ordinary join and join-owner authority.

Each row matches exact command/scope/organization and null application. A null authority
target explicitly covers all targets in that command/scope; a nonnull target matches
only that account. UUID ordering deterministically selects overlapping matching rows.
Missing, nil, mixed or unsupported inputs return no row without revealing target
existence. Every invocation rechecks enabled state and revisions; committed revocation
applies on the next statement on a reused connection. Ordinary transaction snapshot
semantics still apply: this read is not a durable authorization token.

Only the operator has invocation rights. The definer has selected local map columns and
schema USAGE, no map DML, actor DML, DDL or role authority. New objects revoke all default/
inherited named ACL grants before exact grants; the function has fixed
`pg_catalog, pg_temp` search path and qualified owner objects. The trusted body contains
no dynamic SQL, writes, waits or external calls. Migration and qualifier ACL maintenance
use catalog-selected quoted identities; that does not add dynamic runtime authorization.

### Independent source recorder and qualification

Root alone prepares and executes the isolated synthetic frame. The recorder consumes
`owner_urls.authority_reference` from the validated existing fixture, verifies the
historical references, captures helper/pin/reference/revision bytes before execution,
checks that the imported helper path and import-time source SHA match the captured
helper before execution (stale imports refuse), executes exact captured revisions 1–5 in a rollback-only transaction, verifies the
empty target again, and refuses publication if captured bytes changed. It exclusively
publishes `authority-reference.json` through an exclusive mode0600 temporary file
and hard link, independent of process umask;
prior evidence or temporary files are never overwritten. It never updates its trusted
pin. Root independently reviews the known-source receipt and binds the resulting digest
in `AUTHORITY_REFERENCE_SHA256`; no target catalog can approve itself.

With `IDENTITY_QUALIFICATION_DIR` already bound to the authorized prepared frame, use
the canonical prepared interpreter (`OWNER_PYTHON` below):

```sh
"$OWNER_PYTHON" -I -B services/access/tests/qualify_identity_baseline.py --record-authority-reference
"$OWNER_PYTHON" -I -B services/access/tests/qualify_operator_authority.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$OWNER_PYTHON" -I -B -m pytest services/access/tests apps/pts/tests/test_release.py -q -p no:cacheprovider
```

The actual qualifier requires the existing core private URL groups plus `operator_urls`
with actual `identity_operator` credentials for each case. It validates those URLs
as an exact required group against every corresponding frame target and exact login
before any qualification mutation. Required scratch cases are
`authority_reference`, `clean`, `legacy`, `previous`, `failure`, `unsafe`, `unknown`
and the retained `native` target used by existing fixture validation. It creates no
Docker resources, roles or credentials. Exact prior-head4 preparation must retain
`previous-source.json`, `previous-execution.json`, source copies and SHA-bound execution
logs for `previous`, `failure`, `unknown` using commit
`85b26f38dd66b5f1ac96854f82402c93f4a58700`, the existing canonical prior launcher, and
exactly the eleven prior owner files. New roles must be staged only after those actual
prior-source runs; old code must not be modified to understand the new staged roles.

Requirement/test traceability:

| Requirement | Executable evidence |
| --- | --- |
| Original-session identity, exact/wildcard selection, owner join independence, invalid input, immediate revocation, cross-principal isolation, spoof resistance, actual restricted-login permissions and browser/service map privilege removal | `AuthorityQualification.restricted_reads` |
| Nonnil/scope/tuple/FK integrity, immutable identity, forged insert revision/time/updater, changed-update attribution, server revisions/timestamps, no-op, retention and overflow atomicity | `AuthorityQualification.structure` |
| Clean/adopt/exact head4 upgrade, row/external-reference preservation, repeat, unsafe role/external definer/sequence/PUBLIC table/staged dependency, unknown history, canonical drift and injected mid-migration rollback | `AuthorityQualification.upgrades_and_failures` |
| Fail-closed head selection, source capture/race refusal, exclusive private publication/manual pin, imported-helper custody, all-target validation, historical reference chain, unsafe role preparation | `test_operator_authority_qualification.py` |

Focused tests were observed failing before implementation (6 failures: absent head5,
recorder/role helper and revision source); the actual root RED on head4 must also be
retained in the root-owned proof. Database qualification, source-bound root transcripts,
composer checks and scoped release evidence are separately recorded by the root owner.
The Python unit suite does not establish actual PostgreSQL qualification or readiness.

Five impact decisions: scaffold reuses the existing owner migration/reference/qualifier
pattern without a new generator; shared UI has no change because this is an internal
SQL foundation; agent context remains sufficient with no new operator CLI; documentation
updates this owner runbook and root-owned evidence/navigation; existing actor/access/
structural/release ADRs apply unchanged, with no new or edited accepted ADR. Recovery
uses the established coordinated migration procedure: failure rolls back the whole
migration, activation is blocked, and an applied migration is never auto-downgraded.

## Protected actor registration and recovery (identity_0006)

`identity_operator.execute(connection, body: bytes)` accepts only the strict parser's
`actor.register_system` variant. `identity_operator.outcome(connection, operation_id)`
recovers its original receipt. The caller must supply an explicitly prepared target's
idle SQLAlchemy Connection, using READ COMMITTED and actual `identity_operator` LOGIN
credentials. There is no credential discovery, target selection, implicit checkout,
CLI, account ensure or membership execution. Other parsed commands reject before SQL.
`rfc8785==0.1.4` is required in the frozen owner environment; the root owns dependency
manifest/lock preparation. Normalize UUIDs before JCS; absent evidence is included as
`evidence_ref:null` in the complete typed fingerprint envelope.

The fixed SQL entry points are
`identity.register_system(uuid,uuid,text,text,text,text,text,bytea)` (operation, actor,
kind, key, display name, reason, evidence and canonical UTF-8) and
`identity.system_actor_outcome(uuid)`. Both return the original compact result,
command/result versions and server commit timestamp. The server reconstructs this
one command's exact JCS bytes and computes SHA-256 itself. No supplied digest, GUC,
payload executor or assumed role establishes authority. Current original-session
login authority is checked on execution, replay and recovery, serialized with
configuration using the same per-login transaction advisory lock. Initiator is null.

The frozen Python receipt has operation_id, status `committed`, typed result
`{command,target:{actor_id},disposition,revision:null,event_id}`, command_version,
result_version and committed_at. Created actors have one linked immutable event;
an identical existing registration creates a new unchanged outcome with null event.
Conflicting registration or changed replay payload has no effects. Later controlled
label changes do not change a replay's original receipt. Unsupported stored versions
or verification algorithms remain retained and return verification unavailable.

Only a successfully returned commit acknowledges success. A missing lookup returns
None, meaning unresolved. `OperatorError.code` contains only fixed safe identifiers.
`execute` preserves the strict parser's existing `CommandValidationError` with fixed
code `identity_operator_input_invalid` for malformed command bytes. Parsed unsupported
commands and execution failures use `OperatorError`; invalid `outcome` identifiers use
`OperatorError` with `command_invalid`. Both public exception types contain safe fixed
messages without submitted input or SQL/driver chains; callers must handle both.
Execution errors retain the original operation_id for recovery. `operation_busy` means precisely
the bounded outcome advisory lock wait expired. Other lock/statement/deadline/transport
or commit failures return `operation_unavailable`; they never establish rollback or
justify a new operation identity. Recheck authority and recover with the original ID;
retry only the identical immutable command. Driver SQL, values and exception chains
are excluded. No cleanup/expiry or automatic retry/reconciliation is installed.

The ten-second monotonic budget starts before parsing. Transaction-local SQL statement
limits are at most five seconds and lock waits at most two seconds, capped by remaining
budget. Busy connections and unsupported isolation reject. Commit/rollback clears local
settings. No external calls occur while locks are held. The SQL wrapper is internal;
callers use the bounded owner adapter and supply the trusted connection.
The prepared caller also owns bounded driver/socket/transport configuration. The
monotonic deadline and PostgreSQL statement/lock timeouts do not interrupt a stalled
synchronous network or commit acknowledgement, so this adapter does not promise a
ten-second wall-clock return. A lost or delayed commit response remains an uncertain
outcome recoverable with the original operation identity.

Controlled true-superuser preparation runs
`services/access/tools/prepare_identity_command_role.sql` separately before upgrading.
It refuses existing names and non-superusers before creating `identity_command_owner`,
a restricted NOLOGIN/NOINHERIT role. Only the migrator has non-admin SET-only membership.
The operator gets fixed EXECUTE, never raw tables, authority editing, schema CREATE or
owner assumption. The command owner gets selected actor reads/inserts, append/read of
outcomes/events and the existing fixed authority read. Existing account-map guards stay
unchanged. Outcome/event tables have forced RLS for the current authorized executor,
migrator inspection policies, retained immutable guards and local RESTRICT FKs.

Root independently records the new reference in an empty synthetic `command_reference`
database with all roles safely staged. The recorder captures exact source bytes and
all five original references, executes revisions 1–6 rollback-only, proves the target
empty again, and exclusively publishes a private `command-reference.json`. It never
changes `COMMAND_REFERENCE_SHA256`; root reviews and manually pins the publication.
All historical reference bytes/pins and revisions 1–5 remain unchanged. New-role
normalization permits only the separately verified empty staged command role when
checking historical catalogs.

With `IDENTITY_QUALIFICATION_DIR` bound to the prepared frame and `OWNER_PYTHON` set to
`platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python`:

```sh
"$OWNER_PYTHON" -I -B services/access/tests/qualify_identity_baseline.py --record-command-reference
"$OWNER_PYTHON" -I -B services/access/tests/qualify_actor_command.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$OWNER_PYTHON" -I -B -m pytest services/access/tests apps/pts/tests/test_release.py -q -p no:cacheprovider
```

Required exact case groups are `command_reference`, `clean`, `legacy`, `previous`,
`failure`, `unsafe`, `unknown` and retained `native`; every core URL group and
`operator_urls` must match the frame and actual expected login. Root prepares exact
prior-head5 sources from commit `8472909ed59e7aa90f4784e50c2e1e717e68977e` for previous,
failure and unknown, preserving the thirteen owner files, SHA-bound logs, manifests
and original receipts. Observe missing-routine 42883 on the actual operator login
before staging/upgrading revision6. Neither recorder nor qualifier provisions Docker,
roles, credentials, trusted pins or deployment. Failed evidence remains retained.

Traceability: `test_identity_operator.py` proves parser rejection before SQL, complete
JCS/UUID lock fixtures, frozen receipts, budgets, safe exception codes/chains and commit
uncertainty. `CommandQualification.command_matrix` proves actual LOGIN effects,
replay/recovery/conflicts/no-op, current authority and concurrency;
`isolation_and_forgery` proves privilege/search-path/GUC/SET ROLE isolation and reused
connections; `timeouts_and_atomicity` proves distinct real lock waits and rollback on
outcome/event failure; `structural_evidence` proves retained evidence protection and
unsupported verification markers; `upgrades_and_failures` proves prior-source upgrade,
adoption, repeat, drift/unsafe/unknown refusal and injected migration rollback. Root's
actual transcripts and matrix mapping, not unit mocks, establish database acceptance.

Five impact decisions: scaffold extends the existing migration/recorder/qualifier
pattern with this first fixed command and no generic engine; shared UI has no consuming
surface or change; existing repository agent context remains sufficient; this runbook
and root-owned evidence/navigation document actual limits and recovery; existing actor,
release, structural and WRITE decisions suffice, with no new or edited accepted ADR.

## Explicit disposable Identity operator target

`identity_operator_target.prepare_target(environment_target, run_id)` exclusively
creates `platform/deployment/.local/kdg/<canonical UUID>/identity-operator.json`.
Controlled setup must already have prepared the native ENV marker/configuration and
an existing mode0600 `secrets/identity.env` in the mode0700 run/secrets directories.
The sole literal line is `IDENTITY_OPERATOR_PASSWORD=<nonempty literal password>`;
a final newline is optional. Files must be regular, owned by the current UID and
single-link; directory traversal and symlink components refuse. Preparation creates
no database, login, role, grant, migration, credential or environment lifecycle.
It refuses an existing descriptor rather than overwriting or repairing it.

From repository root with the canonical owner interpreter already selected:

```sh
"$OWNER_PYTHON" -I -B -c 'import sys;sys.path.insert(0,"services/access");from identity_operator_target import prepare_target;print(prepare_target("platform/deployment/environments/kdg-local.json",sys.argv[1]))' "$RUN_ID"
"$OWNER_PYTHON" -I -B services/access/operator_cli.py execute --owner identity --target "$DESCRIPTOR" --command-file "$COMMAND_JSON"
"$OWNER_PYTHON" -I -B services/access/operator_cli.py outcome --owner identity --target "$DESCRIPTOR" --command actor.register_system --operation-id "$ORIGINAL_OPERATION_ID"
```

Only the checked-in `kdg-local.json` native target is supported, with its validated
workspace, disposable environment kind, owner, ports, marker and configuration hash.
The database must be exactly `idop_<full run UUID hex>` on literal `127.0.0.1`,
using the ENV database port and actual `identity_operator` login. The descriptor
contains references and binding metadata, never a connection URL or password.
Each invocation and the isolated worker revalidate the complete target/secret.
Preparation proves configuration binding, not application readiness or protection
against a compromised local UID. No production or hosted-CI qualification is claimed.

The existing strict command parser runs before worker/network dispatch. Only
`actor.register_system` is executable; no account, membership, Access, actor override,
endpoint override or arbitrary SQL options exist. The fixed isolated interpreter
worker receives bounded private stdin, a minimal environment and no argv secret.
It uses SQLAlchemy NullPool, discrete URL fields, a three-second connection timeout,
READ COMMITTED, startup statement/lock limits of five/two seconds, no libpq environment,
service/password-file discovery, TLS or GSS negotiation. Before effects it verifies
actual session/current login, database, restricted role flags and absence of memberships,
then rolls the read transaction back to idle before invoking the unchanged adapter.
No automatic migration, seed, grant, reset or retry occurs.

The existing process supervisor enforces a twelve-second parent deadline with its
two-second cleanup bound, caps combined output at 8192 bytes and hides child stderr.
SIGINT/TERM triggers cleanup. Only a clean worker completion after commit and strict
receipt validation produces exit 0. Unresolved lookup and safe errors exit 2. Output
is a compact committed receipt including versions/time, unresolved plus original
operation ID, or an allowlisted safe code and known operation ID. Driver/parser text,
command contents and tracebacks never become CLI output.

An interrupted, timed-out, unavailable or invalid response may follow committed effects.
Preserve the immutable original command and operation ID; check `outcome` under current
authority. Unresolved/unavailable never authorizes a new operation ID and never proves
rollback. Retry only the identical command after recovery checks. The target wrapper
adds no cross-owner readiness or consumer acceptance claim.

Root qualification consumes an already prepared head6 database/authority and explicit
private fixture, with no provisioning:

```sh
"$OWNER_PYTHON" -I -B services/access/tests/qualify_operator_target.py --target "$DESCRIPTOR" --fixture "$PRIVATE_TARGET_FIXTURE"
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$OWNER_PYTHON" -I -B -m pytest services/access/tests apps/pts/tests/test_release.py -q -p no:cacheprovider
```

The mode0600 fixture in a mode0700 directory has exactly `owner_url`, `run_id` and
`database`; its `postgresql://` owner URL must name `identity_migrator`, literal
127.0.0.1 and the same validated port/database. The URL is private setup input and is
never printed. Qualification retains newly created private command files under the
native run and proves one actor/event/outcome, identical replay/recovery, unresolved
lookup, target/input refusal and unchanged state after replay/refusal. A temporary disable of
the existing dedicated synthetic authority proves execute/lookup denial without
effects; finally restores its original enabled value. Existing guards advance that
authority row's revision/timestamps, while business state remains unchanged. It creates no
roles, secrets or infrastructure and never repairs existing state.

Traceability: `test_operator_target.py` proves exclusive preparation, binding/secret
validation and unsafe private-file refusal; `test_operator_cli.py` proves closed
arguments/responses, fixed worker/minimal environment and actual subprocess stall/
output bounds. Actual restricted-login/commit evidence remains root-owned. ATDD RED
was two missing-module failures before implementation; the first affected regression
run passed 355 tests; the final affected run passed 372 tests. Real SIGINT/TERM
checks exposed selectors swallowing InterruptedError as a syscall retry; the handler
now uses a distinct exception and proves cleanup with no automatic command retry.
Root records actual qualification and composers separately.

Five impacts: scaffold reuses native preparation and the existing bounded process
helper without a new generator or supervisor; shared UI has no surface/change; existing
agent context remains sufficient; this runbook documents preparation/invocation/recovery
and root owns delivery navigation/evidence; accepted ADRs and schemas are unchanged.

The target qualifier now enforces its checks under optimized Python as well. It
compares every pre-existing row and unaffected Identity table after registration,
then verifies the exact new actor, outcome, event and their attribution/links.
Its private launcher records the CLI return status with the safe JSON: committed
responses require 0; unresolved/refused responses require 2. A fixed internal test
runs the real worker to commit, privately records `post-commit-witness.json`, then
suppresses its response and stalls. The bounded wrapper must return unavailable
with the original operation ID; normal lookup/replay must recover the same receipt
with exactly one effect. This is internal qualification, with no public fault flag.

Qualification has a one-shot 120-second alarm and SIGINT/TERM handlers that unwind
through authority restoration. Owner connections use a three-second connect timeout,
five-second statement limit and two-second lock limit, including restoration. Before
disabling the dedicated synthetic authority it durably writes mode0600
`authority-restoration.json` in its private qualification directory, identifying the
run/database/login/authority and original enabled value. After a confirmed restore
commit it writes `authority-restored.json` with the observed revision. These are
nonsecret recovery evidence, not authority or readiness claims.

SIGKILL, a host/process failure or a restoration SQL failure can leave the synthetic
authority disabled, or leave restoration uncertain. Preserve the directory, command,
original operation ID and witnesses. Do not blindly rerun qualification. Controlled
root setup must inspect the recorded exact target and current authority, restore the
recorded enabled value if needed using the bounded owner connection, verify current
state, and retain its recovery evidence. A missing restored witness alone does not
prove restoration failed; inspect current state. Prior business effects stay retained.

## Restricted selected-organization targets (identity_0007)

The additive owner revision provides two internal, fixed reads:
`identity.organization_account_candidates(after_account_id uuid)` and
`identity.organization_account_target(target_account_id uuid, expected_membership_id bigint)`.
Both return only account_id, exact membership_id/current membership_revision, mapped
account actor_id and its owner-verified display_name. An active selected organization,
profile and membership plus account-kind mapping are required. Candidates are ordered
by UUID; a nullable exclusive cursor starts the complete relation with no raw limit.
Point reads require a positive exact membership ID and never substitute another member.
No email, profile extras, role, person, employment or Access eligibility is exposed.

Trusted Access context uses transaction-local app.context_kind, app.actor_id and
app.org_id; user context additionally requires app.account_id. UUID context must be
canonical-format, nonnil and valid (case-insensitive). Setup requires account absent
or empty after pooled SET LOCAL cleanup. Invalid or missing context returns no rows.
Candidates accept user context only; point accepts user or setup. UUID arguments are
bound typed values: malformed UUID text fails PostgreSQL argument conversion with
22P02 before routine execution; null/nil point IDs and nonpositive/missing membership
IDs return no rows. Backend context is an assertion, never an authorization service.
Access must implement its protected wrappers, capability checks and separate pools
before these reads can be used by application callers.

The STABLE SECURITY DEFINER owner is identity_target_projection_owner, restricted
NOLOGIN/NOINHERIT, with fixed pg_catalog,pg_temp search_path and fully qualified owner
objects. Exact column SELECT grants and paired permissive/restrictive selected-org
profile/org/member policies prevent older PUBLIC policies broadening this owner.
Profile policies join members; member policies use context only, avoiding recursion.
Existing current-account functions and their callers remain unchanged.

Controlled true-superuser preparation separately runs
`tools/prepare_identity_target_roles.sql` under this directory. Existing names refuse;
there is no silent repair. It stages identity_target_projection_owner,
access_target_reader, access_setup_target_reader and access_command_owner, all
restricted NOLOGIN/NOINHERIT. Only the Identity definer has a non-admin SET-only edge
to identity_migrator. The Access roles have no membership, raw Identity reads or schema
CREATE. Only access_target_reader receives candidates. Point additionally permits
access_setup_target_reader and access_command_owner. No ordinary runtime, operator,
browser or Supabase service principal receives these routines. Every inherited named
function default grant and PUBLIC EXECUTE is revoked in the create transaction before
exact grants. Temporary CREATE for ownership transfer is removed in that transaction.

Head7 adds target-reference.json without rewriting the six historical references,
revisions or source pins. Historical comparisons may normalize the new migrator edge
only after verifying all four roles have exact flags/memberships, no current-database
ACL/ownership dependencies and no effective excess privileges. Head7 checks exact
current role dependencies and effective schema/table/column/function/sequence grants.
An unexpected grant, role assumption, catalog change or history refuses activation.
The reference recorder captures all seven revisions, all historical references and
helper/source identities; it verifies each prior catalog, executes the known source
chain rollback-only on target_reference, rechecks empty state, and exclusively publishes
a private fixed reference. Root reviews the source-bound record and pins only the new
TARGET_REFERENCE_SHA256. There is no arbitrary reference/target override or auto-pin.

Use the already prepared canonical owner Python and private frame:

```sh
"$OWNER_PYTHON" -I -B services/access/tests/qualify_identity_baseline.py --record-target-reference
"$OWNER_PYTHON" -I -B services/access/tests/qualify_organization_targets.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$OWNER_PYTHON" -I -B -m pytest services/access/tests apps/pts/tests/test_release.py -q -p no:cacheprovider
```

IDENTITY_QUALIFICATION_DIR uses the existing native fixture contract. Root alone
prepares scratch databases/roles/secrets: target_reference, clean, legacy, previous,
failure, unsafe, unknown and retained native. Previous/failure/unknown run the exact
15 head6 owner files at 48b95c9bfc8a199a84d3746c431312439b1a93e9 before staging new roles,
with source manifest and SHA-bound execution logs. No new LOGIN is introduced. The
qualifier temporarily grants only the two fixed routines to actual access_runtime
LOGIN credentials for synthetic invocation, restores original ACL bytes in finally,
and explicitly records that fixture-only execution delivers no Access wrapper.
No infrastructure, role or credential provisioning occurs in the qualifier. The new
qualifier and target-reference recorder refuse optimized Python before fixture access
or database effects, preserving their assertion-based custody and proof checks.

Temporary fixed-function fixture grants use bounded SQL and SIGINT/TERM unwind handlers.
Before granting, the qualifier durably writes a private target-acl-restoration-required
witness with the exact case/routines/ACL bytes; after confirmed restoration it writes
an independent private target-acl-restored witness. Grant and invocation both sit inside
the restoration finally block. SIGKILL, host failure or restoration SQL failure can
leave the synthetic invocation grant present or its restoration uncertain. Preserve
the witnesses and retained target; controlled root recovery must inspect current ACLs
on that exact prepared case, revoke only the recorded temporary access_runtime grants
if needed, verify the original ACL bytes and retain recovery evidence. A missing restored
witness alone does not prove a surviving grant. Do not blindly rerun qualification.

Traceability: test_target_qualification.py covers current/historical head selection,
full-chain source capture and mutation refusal, private exclusive reference publication
without auto-pin, historical trust chaining and all four unsafe-role preparations.
TargetQualification.permissions proves the exact caller matrix, actual ordinary-runtime
execution/raw-read/owner-assumption/DDL denial. reads proves a complete 103-member
ordered candidate relation, exclusive UUID boundaries, exact point/member identity,
setup-only point context, malformed/missing/nil context and inputs, deleted/unmapped
rows, wrong organizations, current revision/retirement, fixed search path, direct
restrictive RLS and reused connections after commit/rollback/SQL failure.
The additional rollback-only owner fixtures prove old/new replacement-member IDs,
UUID org predicates appearing as actual index conditions under the restricted definer,
and removal of an unexpected named function default grant plus PUBLIC before exact
caller grants. Same-connection user/setup/missing transitions include rollback and SQL
failure. Actual recipient-role excess membership, schema CREATE, column SELECT and
external SECURITY DEFINER execution each refuse and reconcile after exact restoration.
upgrades_and_failures proves source-bound head6 upgrade, legacy adoption, clean/repeat,
preserved business/external rows, unsafe role refusal with restoration, unknown history,
current catalog drift refusal and actual Alembic mid-revision rollback with unchanged
head6 ledger/catalog/data before reconciliation. Root's actual transcripts establish
PostgreSQL evidence; unit tests do not establish deployment or full ID-B readiness.

Five impacts: scaffold extends only the established owner revision/reference/qualifier
pattern; shared UI has no consuming surface; existing agent context already covers
ownership/context/release requirements; this owner runbook and root-owned evidence and
navigation document actual execution; accepted ownership, actor, structural and release
ADRs apply without edits. No generator, frontend, client, service or dependency is added.
Recovery retains the existing controlled migration-before-activation route, previous
running-version compatibility and atomic rollback before activation on migration
failure. Applied revisions are never automatically reversed. Access wrappers, eligible
public pagination, commands/grants and the remaining ID-B work stay separately gated.

## Protected authenticated profile fields (identity_0008)

Revision8 changes only INSERT/UPDATE ACLs for `authenticated` on `identity.users`.
It revokes that role's table writes and all existing per-column INSERT/UPDATE grants,
then grants INSERT(id,username) and UPDATE(username,deleted_at). Explicit protected
fields are denied even when values are unchanged or mixed with supported input.
UPDATE id/actor_key/is_system/is_platform_admin/created_by/created_at/updated_by/updated_at
and INSERT columns other than id/username are protected. Existing defaults and audit
triggers supply attribution. Security claims, trusted app context and legacy authorize
results do not create column privileges.

The migration checks effective privileges after changing ACLs, including PUBLIC and
inherited rights. Surviving protected authority refuses the transaction; it never repairs
another principal. The head8 catalog/reference also verifies exact effective writes and
all previous object/role/history fingerprints. SELECT's existing absence, DELETE, RLS,
defaults, shared audit functions, Auth hook, actor/account/member mappings, projections,
other tables and trusted legacy service_role/seed/migrator grants remain unchanged.
In particular, ordinary filtered UPDATE/upsert forms that require unsupported SELECT
remain denied; no SELECT grant is added to enable them. Existing self soft-delete and
unretire remain supported. The old legacy admin RLS policy still permits supported
profile inputs for another account when its trusted admin claim is present; protected
columns remain denied. Wrong-account INSERT proof uses an absent synthetic profile:
an existing duplicate profile may produce 23505 before the RLS check, which cannot
serve as evidence of 42501 denial. This is column hardening, not new lifecycle/provisioning.

Head8 adds independent `profile-reference.json` and PROFILE_REFERENCE_SHA256. The seven
prior references, source pins and revision sources are immutable. Existing rollback-only
reference recording captures the helper, eight revisions and seven historical references,
checks every prior catalog plus staged roles, verifies the scratch target empty again,
then publishes the new mode0600 reference exclusively. It refuses optimized Python before
fixture access and never updates its own pin. Controlled root reviews the source-bound
record and pins only PROFILE_REFERENCE_SHA256.

Use the existing canonical owner interpreter and root-prepared private frame:

```sh
"$OWNER_PYTHON" -I -B services/access/tests/qualify_profile_fields.py --characterize
"$OWNER_PYTHON" -I -B services/access/tests/qualify_identity_baseline.py --record-profile-reference
"$OWNER_PYTHON" -I -B services/access/tests/qualify_profile_fields.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$OWNER_PYTHON" -I -B -m pytest services/access/tests apps/pts/tests/test_release.py -q -p no:cacheprovider
```

Root owns all Docker/database/role/credential setup. Exact cases are characterization,
profile_reference, clean, legacy, previous, failure, unsafe, unknown and retained native,
using the existing IDENTITY_QUALIFICATION_DIR contract. Root prepares actual head7 before
changing privileges and records its supported self writes, missing-profile defaults/audit
and protected forgery behavior. `profile-fixtures.json` contains characterization/clean,
each with canonical distinct account/other/missing UUIDs. Root supplies synthetic Auth
stubs and self profiles; missing has Auth only. No real accounts are used. Qualifier
creates no infrastructure/login/credential or Auth account. Prior head7 custody is the
exact seventeen owner files at `630d1ae86db175c10806a3c3e3662962052aa978`, with manifests
and SHA-bound executions on previous/failure/unknown. It uses current sys.executable.

Actual restricted access_runtime LOGIN temporarily assumes authenticated/service_role
through SET-only, noninherited, non-admin edges. This models PostgREST role execution,
not provider/JWT verification or an HTTP consumer. Qualifier verifies the edges absent,
durably records mode0600 profile-role-restoration-required witnesses, grants only these
fixture edges via the existing restricted-frame administrator and restores exact prior
membership rows in finally. SIGINT/TERM unwinds restoration; bounded statements apply.
Confirmed restoration writes a separate private profile-role-restored witness. SIGKILL,
host failure or failed restoration can leave a fixture edge present or uncertain. Retain
frame and witnesses; controlled root must inspect the exact recorded target, remove only
recorded temporary edges if present, verify original membership rows and retain recovery
evidence. A missing restored witness alone proves no particular database state. Never
blindly rerun or automatically clean up the retained fixture. A separate synthetic
inheritance fixture temporarily grants anon UPDATE(is_system) and an INHERIT TRUE,
SET FALSE anon-to-authenticated edge. Its profile-inheritance-restoration-required /
profile-inheritance-restored witnesses record the prior column ACL and membership;
recovery restores only these recorded temporary effects and verifies both exactly.
Direct live verifier checks prove PUBLIC/inherited refusal. PUBLIC also reaches
restricted owner roles, so existing authority-role safety can reject migration
preflight before the profile/catalog guard; that earlier refusal is preserved.
PUBLIC/broad authenticated ACL and synthetic failure-event mutations also record private
profile-acl-restoration-required or profile-event-restoration-required witnesses before
any mutation, followed by separate restored witnesses only after exact verification.
ACL witnesses contain original table/column ACLs and literal temporary/cleanup grants;
event witnesses contain the verified absent synthetic function/trigger state and exact
create/drop statements. Existing synthetic names refuse. Recovery inspects those exact
objects/ACLs and restores only recorded changes; broad INSERT revoke also requires
restoring the recorded original INSERT(id,username) grants. All qualifier SQL mutations
and cleanup use five-second statement and two-second lock limits.

Traceability: `test_profile_fields.py` proves required/current and prior heads, effective
privilege refusal, full source-chain mutation detection, private exclusive publication
without auto-pin, historical trust chaining, optimized guards and exception-safe edge
restoration. `ProfileQualification.writes` proves every protected INSERT/UPDATE field,
same-value/mixed writes, existing upsert/SELECT refusals, claims spoofing, exact role/RLS,
no partial profile/audit/map effects, allowed self writes/default/audit, soft-delete and
unretire, trusted service compatibility and connection reuse after commit/rollback/error.
`upgrades_and_failures` proves clean/adopt/head7/repeat preservation, PUBLIC drift refusal,
actual mid-revision failure with original ledger/catalog/data, reconciliation and unknown
history refusal. Root retains independent source-bound head7 characterization, the unchanged native
run and both composer routes. Synthetic scratch Auth stubs exercise the existing profile
hook; this is not native Supabase Auth HTTP/provider/JWT proof. The pinned head7/head8
catalog difference contains only relation/column ACLs and their effective table/column
privileges; all hook, audit, seed integration, defaults and current-account/target routine
categories are identical. This preserves their existing source/privilege contracts,
without claiming a newly executed native seed/projection sequence. These fixtures and
root evidence establish bounded acceptance, not full ID-B/Access/WRITE/KDG readiness.

Five impact decisions: scaffold extends the existing owner migration/reference/qualifier
pattern without a new generator or runtime framework; shared UI has no consuming surface;
existing agent context already covers the applicable ownership/release/attribution rules;
this owner runbook and root evidence/navigation/inventory document behavior and limits;
existing accepted security/actor/structural/release ADRs apply unchanged. There is no new
API/client/schema field/dependency. Controlled migration-before-activation and atomic
failure rollback remain required; applied migrations are never automatically reversed.

## Exact active legacy role lookup (identity_0009)

Revision9 replaces only the body/search_path of the existing no-argument
`public.get_user_roles()` compatibility RPC. It preserves `TABLE(role text)`, owner,
ACL bytes, effective permissions, language, volatility and definer status. The query
uses qualified owner objects with `pg_catalog,pg_temp` and joins the exact JWT `sub`
through `auth.uid()`, `org_id` and positive bigint `member_id` to active profile,
organization and membership rows. Only undeleted roles on that exact member return.
Missing/empty/nil IDs, nonpositive member IDs, stale/retired or foreign bindings return
no rows. Malformed UUID/bigint and bigint overflow retain typed PostgreSQL errors.
App context and stale JWT role arrays cannot substitute identity or authority. No
actor/person mapping is required. Expense retains its existing RPC and role rows;
this compatibility helper does not become current Access authority.

The eight previous revisions, eight references and source pins remain immutable.
`legacy-role-reference.json` and its independent LEGACY_ROLES_REFERENCE_SHA256 bind
revision9 to the full previous trust chain. The established rollback-only recorder
captures the helper, source pins, all eight prior references and all nine revisions,
executes captured source, checks every previous catalog and all staged-role recovery,
then exclusively publishes a mode0600 reference. It refuses optimized Python before
fixture access and never updates its own pin. Root reviews the independent source
record before pinning only the new constant. The canonical head8/head9 fingerprint
difference is solely the functions category. Source-default PUBLIC execution is
preserved; a separate revoked-PUBLIC fixture proves CREATE OR REPLACE retains that
target difference rollback-only, without normalizing or adopting it.

Use the existing canonical owner Python and private fixture contract:

```sh
"$OWNER_PYTHON" -I -B services/access/tests/qualify_legacy_roles.py --characterize
"$OWNER_PYTHON" -I -B services/access/tests/qualify_identity_baseline.py --record-legacy-role-reference
"$OWNER_PYTHON" -I -B services/access/tests/qualify_legacy_roles.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$OWNER_PYTHON" -I -B -m pytest services/access/tests apps/pts/tests/test_release.py -q -p no:cacheprovider
```

Root alone prepares/runs all database/Docker operations. Exact cases in the existing
IDENTITY_QUALIFICATION_DIR frame are characterization, legacy_roles_reference, clean,
legacy, previous, failure, unsafe, unknown and retained native. Root supplies synthetic
Auth/profile/org/member/role rows. `role-fixtures.json` contains characterization and
clean objects, each with canonical account/other/org/other_org UUID strings and positive
decimal-string member/other_member/other_org_member/role/deleted_role IDs. Active account
has admin plus a deleted employee role; the other account in the first organization
and the first account in the other organization have employee roles. No actor/person
mapping is created. Characterization executes actual head8 before upgrade and records
actual results, including preexisting 42702 ambiguous member_id errors, never invented
old success. Previous/failure/unknown custody is all nineteen owner files from
`f52352fc31337f5f15b1f249775e2dcebaf134b7`, with full source/execution digests and the
current `sys.executable`.

The qualifier reuses ProfileQualification's restricted access_runtime LOGIN fixture
and temporarily grants authenticated/service_role SET-only, noninherited, non-admin
edges. Private durable profile-role-restoration-required/profile-role-restored witnesses,
exact restoration, bounded SQL and SIGINT/TERM unwind behavior remain as documented
above. This models database execution, not provider/JWT/HTTP verification. Retirement
fixtures use rollback-only service_role mutations followed by actual authenticated RPC
execution in the same transaction; profile/org/member/role/audit data hashes stay unchanged.
No normal lifecycle implementation, uniqueness change, seed replay or new role is added.

The inspected native Auth helpers use legacy context precedence: `auth.uid()` first
reads nonempty `request.jwt.claim.sub`, then plural `request.jwt.claims` sub;
`auth.jwt()` first reads nonempty singular JSON `request.jwt.claim`, then plural JSON
`request.jwt.claims`. Root copies those exact inspected native definitions into the
scratch databases; the qualifier checks byte-equal definitions against the retained
private `auth-helper-definitions.json` native source before characterization/reads.
The fixture sets or clears all three forms transaction-locally on every invocation.
Conflicting helper account/member bindings must return no rows; coherent legacy forms
select the correct account even when lower-priority plural JSON disagrees. Pool reuse
must clear all three settings. This proves the existing SQL helpers' binding semantics
under controlled database context; it does not verify JWT signatures, provider trust,
PostgREST context establishment or HTTP authentication. Migration SQL continues to use
`auth.uid()` and `auth.jwt()` as its authority without introducing a login protocol.
Missing or empty `auth.jwt()` sub is gated before calling `auth.uid()`, whose native
plural-sub UUID conversion otherwise raises 22P02 for an empty string. Empty identity
therefore returns no roles; nonempty malformed values still reach native typed conversion
and retain their errors.

The head8 characterization writes a private raw observation/function-row witness before
acceptance checks, then requires the approved target's three known 42702 observations.
Permission/missing-function or other unexpected errors refuse qualification while retaining
the raw evidence. Head9 comparison requires actual per-function rows from that witness:
only the public helper body/search_path may change; owner, ACL and the rest of its
function declaration plus every other function must be identical. Recorder DDL/catalog
transactions, including post-rollback verification, set local 60-second statement and
five-second lock limits before their first database query.

A bounded synthetic event trigger causes a real CREATE FUNCTION failure inside revision9.
Before creation the qualifier verifies exact synthetic function/trigger names absent and
writes private legacy-roles-event-restoration-required evidence. Its finally block drops
only those recorded fixture objects, verifies the original state and writes separate
legacy-roles-event-restored evidence. SIGKILL, host failure or restoration SQL failure
can leave fixture edges/objects present or uncertain. Preserve all witnesses/resources;
controlled root recovery inspects the exact target, restores only recorded temporary
effects, verifies exact original state and retains evidence. A missing restored witness
alone proves no particular database state. Do not blindly rerun. Migration failures
retain the prior ledger/catalog/data and block activation; applied migrations are never
automatically reversed.

Traceability: `test_legacy_roles.py` covers exact SQL identity bindings, newest-head and
historical-head selection, all source-custody mutations, private exclusive publication
without pinning, historical reference trust, optimized refusal and event recovery.
`LegacyRolesQualification.reads` proves exact active roles/deleted-role exclusion,
foreign account/org/member and stale admin-array refusal, missing/empty/nil/nonpositive
claims, typed malformed/overflow errors, profile/org/member/role retirement, current
alternate legitimate bindings, fixed search path with a distinct rejected spoof sentinel, complete multiple-live-role
rows, absent/empty/unrelated role arrays and pooled cleanup after rollback/error.
`compatibility`, `revoked_public` and `upgrades_and_failures` prove only helper definition
changes, canonical/default and separately revoked PUBLIC ACL preservation, clean/adopt/
head8/repeat migrations, full old-row/external-reference preservation, drift/unknown
refusal and real mid-revision rollback. Root retains actual execution, both composers,
protected-file audit and normal native stop evidence. These establish this bounded
increment, not full Identity/Access/WRITE/KDG readiness.

Five impacts: scaffold extends the existing owner migration/reference/qualifier pattern;
shared UI has no consuming surface or change; existing agent context already covers
ownership/release/current identity limits; this owner runbook and root-owned evidence,
navigation and inventory record behavior/verification; existing accepted ADRs apply
unchanged. Auth token-hook selection/metadata, invalid-selected-org policy, profile
hardening, seeds/upserts, mapping/audit and remaining membership/Access work stay separate.
No application/client/types/dependency, runtime service or generator is added.

## Active-organization token claims (identity_0010)

Revision10 replaces only `identity.custom_access_token_hook(event jsonb)` body and
search_path. All membership paths now join a nonretired organization: owners-first /
created_at fallback, exact account/selected-organization lookup and org_ids enumeration.
Explicit top-level user_metadata.current_org_id remains selected even when foreign,
invalid or retired; it receives no member, roles or owner flag and never falls back.
Missing/JSON-null selection keeps existing fallback ordering. The hook preserves slug
resolution, soft-deleted profile behavior (no added active-profile check; the existing
membership/profile foreign key is unchanged), typed UUID errors,
deleted-role filtering, unrelated event/claim fields and existing JSON null/array/boolean
shapes. It performs no writes and remains legacy Auth integration, not Access authority.
Qualified owner names and pg_catalog,pg_temp prevent caller search-path substitution.
Owner, signature, language, definer status, volatility, ACL and effective permissions
are preserved, including a separately revoked-PUBLIC target difference tested rollback-only.

The nine historical revisions/references, original SQL/composed files and source pins
remain immutable. `token-hook-reference.json` and TOKEN_HOOK_REFERENCE_SHA256 extend
independent historical trust. The established recorder executes captured source with
bounded SQL, verifies every earlier catalog and staged-role rollback, checks full source
custody, then exclusively publishes mode0600 evidence; it refuses optimized Python
before fixture access and never sets its own pin. Root reviews evidence before pinning.

One-time reference generation requires a new, uncommitted token-hook-reference.json
that is absent and TOKEN_HOOK_REFERENCE_SHA256 set to None. Prior references and pins
remain immutable. Preserve the exact source and every receipt before any correction;
never delete or clear the committed reference/pin to rerun generation. On the separately
prepared clean reference target, root runs once:

```sh
"$OWNER_PYTHON" -I -B services/access/tests/qualify_identity_baseline.py --record-token-hook-reference
```

Repeatable qualification uses the frozen owner Python and existing
IDENTITY_QUALIFICATION_DIR private frame, with the committed reference/pin. Root prepares
each required starting state; characterization requires unchanged9 and the migration
matrix requires its documented source-bound fixtures:

```sh
"$OWNER_PYTHON" -I -B services/access/tests/qualify_token_hook.py --characterize
"$OWNER_PYTHON" -I -B services/access/tests/qualify_token_hook.py
```

Root-only sequential execution is required for every qualification sharing a cluster:
temporary role memberships are cluster-wide, so fixtures must not overlap even when
their databases differ. Verify exact restoration before the next execution.

Root alone prepares/runs databases, Docker, roles and credentials. Exact cases are
characterization, token_hook_reference, clean, legacy, previous, failure, unsafe, unknown
and retained native. `token-hook-fixtures.json` contains characterization/clean objects
with canonical account/other/missing/org/other_org UUIDs and positive decimal-string
member/other_member/other_org_member/role/deleted_role IDs. Root supplies synthetic rows
with owned admin/deleted employee roles, another account's employee membership and an
alternate employee organization. Root retains the exact21 owner py/json files from
b790051bf93417640702ff450aff9d4e9b398575; previous/failure/unknown execute that source.
Scratch auth.uid/auth.jwt definitions must equal native definitions exactly.

`TokenHookQualification` records actual unchanged9 retired-selected and retired-owner
fallback claims before10. Restricted access_runtime temporarily assumes
supabase_auth_admin/service_role through SET-only, noninherited, non-admin fixture edges;
all row mutations roll back. Private token-hook-role-restoration-required/restored
witnesses bind exact edge restoration. Synthetic failure objects have separate private
token-hook-event-restoration-required/restored witnesses. Bounded SQL and SIGINT/TERM
unwind cleanup; host failure, SIGKILL or failed cleanup require root inspection of the
recorded exact target/effects, preservation of all resources/evidence and verified exact
restoration. Never infer database state from missing cleanup evidence or blindly rerun.

Focused CPU tests cover SQL boundaries, head/history, full recorder source custody,
independent trust, exclusive publication, no auto-pin and optimized/interruption refusal.
Actual qualifier proves retirement/foreign selection/fallback, roles, profile compatibility,
typed errors, spoof/pool reuse, unchanged data hashes and per-function declaration/ACL
compatibility. Clean/adopt/head9/repeat, drift/unknown refusal and mid-revision rollback
retain history/data and block activation on failure. Direct SQL proves no provider,
JWT-signature or HTTP authentication behavior. Root records actual matrix, both composer
routes and retained-data normal stop; this bounded item does not complete ID-B readiness.

Five impacts: scaffold extends only existing owner migration/reference/qualification
patterns; shared UI has no consumer/change; agent context remains sufficient; this owner
runbook and root evidence/inventory/navigation record the actual result; accepted ADRs
remain unchanged. No generator, service, API, grant, login, dependency, membership command,
uniqueness/CASCADE change or application implementation is added. Existing coordinated
migration-before-activation/recovery remains binding; no automatic downgrade is supported.

## Stable membership instance binding (identity_0011)

Revision11 replaces only `identity.guard_org_member_revision()` through CREATE OR
REPLACE. Before any UPDATE revision logic, an IS DISTINCT FROM change to id, org_id
or user_id raises SQLSTATE23514, message `identity_membership_binding_immutable`,
constraint `org_member_binding_immutable`. This includes retired memberships and mixed
binding/mutable updates. Identical bindings, caller-supplied INSERT IDs, server revision1,
mutable fields, no-op revision preservation and atomic overflow refusal remain unchanged.
The invoker function declaration, owner, ACL, search_path and existing trigger remain.
No uniqueness, retirement/unretirement, hard-delete/CASCADE, lifecycle command, seed
payload, actor mapping, application API or API error contract changes are included.

Ten historical migration/reference chains, source pins, source SQL and composed outputs
remain immutable. `membership-binding-reference.json` and the independent
MEMBERSHIP_BINDING_REFERENCE_SHA256 extend the existing chain. The recorder requires
the new pin to be None, executes captured source, verifies each prior catalog, rolls back,
rechecks staged roles/clean target, checks complete source custody, then publishes only
the reference exclusively with mode0600. It never edits the helper/pin. Root alone runs
isolated database/Docker work and sets the pin only after recorder PASS.

One-time reference generation requires the new, uncommitted
`membership-binding-reference.json` to be absent and its independent pin to be None.
Historical references and migration/source pins remain immutable. After root prepares
the isolated reference target, use the frozen OWNER_PYTHON and private root frame selected
by `/tmp/kdg-member-binding-proof`:

```bash
"$OWNER_PYTHON" -I -B services/access/tests/qualify_identity_baseline.py --record-membership-binding-reference
```

Only after recorder PASS does root record the new reference pin. Repeatable verification
uses the retained unchanged10 characterization target and the prepared migration cases:

```bash
"$OWNER_PYTHON" -I -B services/access/tests/qualify_membership_binding.py --characterize
"$OWNER_PYTHON" -I -B services/access/tests/qualify_membership_binding.py
```

Root alone executes these operations sequentially on the same isolated cluster, including
temporary role edges and failure objects. No parallel qualification or live cutover is
covered. The max-revision fixture is owner-only rollback DDL on that isolated target;
it is not a restricted-runtime permission or a supported business write path.

The exact IDENTITY_QUALIFICATION_DIR cases are characterization,
membership_binding_reference, clean, legacy, previous, failure, unsafe, unknown and
retained native. `member-binding-fixtures.json` supplies characterization/clean objects
with account/other/spare/org/other_org/spare_org canonical UUIDs and positive decimal
member/other_member/other_org_member/role/deleted_role strings. Spare profile/org exist
without memberships. The three membership IDs must be distinct, the primary ID must
leave bigint headroom for +1000000, and bounded prechecks must find the three exact
account/organization bindings and no row at that derived ID. Root retains the exact23 old owner py/json files from
`e8754cc9e53fc57cbc6b45d96725b5bc267b204a`; previous/failure/unknown execute that source.

The qualifier records actual10 accepted binding mutations before11. The original
member_role FK prevents changing a referenced membership ID; that characterization
removes only synthetic dependent roles inside its rollback scope, preserving constraints.
Actual restricted access_runtime sessions temporarily assume authenticated/service_role
through SET-only noninherited non-admin edges. Private restoration-required/restored
witnesses bind exact role edges and synthetic failure objects; SIGINT/TERM unwinds
cleanup. Missing cleanup evidence, host failure or SIGKILL requires root inspection and
verified exact restoration with all resources/evidence retained.

The binding matrix proves active/retired, mixed and multirow refusal with unchanged
membership/role/audit state, including NULL and combined binding assignments. A
data-dependent modifying CTE updates the permitted other member before the rejected
primary-member update, proving statement rollback beyond unordered multirow traversal.
It also checks unchanged bindings/noops, ordinary mutable updates, INSERT
revision ownership and overflow. The supported seed conflict(org_id,user_id) upsert still
retains the ID/roles and un-retires a retained seed row; the SQL seed lookup deliberately
keeps its original non-active-only predicate. This compatibility is not lifecycle safety.
Restricted legacy roles, token and current-account readers retain their IDs/roles and
directly deny the retired membership in rollback-only fixtures. Characterization evidence
binds the current proof path/run ID and fixture SHA256 and must record exactly the three
expected field transitions before its function-catalog evidence is accepted.
Only the guard function body may differ in the catalog; exact declaration/owner/ACL and
all other function rows are compared. Clean/adopt/head10/repeat, drift and injected-failure
rollback remain real migration commands. Unknown history uses rollback-only direct
owner preflight on the same connection; it makes no subprocess-migration claim.

Five impacts: scaffold extends the existing owner migration/reference/qualification
pattern; shared UI has no consumer; agent instructions remain sufficient; this runbook
and root evidence/navigation/inventory record actual results; accepted ADRs remain
unchanged. No new generator/service/framework, dependency, application implementation,
provisioning or deployment is added. Root records actual verification and retained-data
normal stop separately; this item does not complete ID-B or assert readiness.

## Retained membership history (identity_0012)

`0012_membership_retention.py` closes existing direct deletion and Auth-role
`TRUNCATE ... CASCADE` history loss. Before upgrade, the existing owner preflight
compares the complete exact11 catalog to its independently pinned reference. The
three canonical foreign keys must have their original names, columns, NO ACTION
update action, validated/nondeferrable state and CASCADE delete action; no target
normalization is allowed. New12 replaces only their delete action with RESTRICT:
org_member_org_id_fkey, org_member_user_id_fkey and member_role_member_id_fkey.
The profile→Auth users_id_fkey remains its original NO ACTION definition.

The existing guard receives an initial DELETE/TRUNCATE refusal with SQLSTATE23514,
message identity_membership_history_retained and constraint org_member_history_retained.
Its row trigger additionally handles DELETE; a BEFORE TRUNCATE statement trigger
uses that same function. Its function identity, signature, owner, invoker security,
ACL, search_path and all binding/revision behavior remain. Retired, active and roleless
memberships are retained. Owner DDL/trigger disabling remains trusted administration.
Standalone trusted legacy member_role DML still works; this is not full role audit or
membership lifecycle safety. Unique(org,user), seed upsert/unretirement and current
readers remain supported; rejoin, one-way retirement, actor adoption and commands remain
gated.

Root alone prepares and sequentially executes synthetic DB/Docker work. The retained
qualification frame supplies characterization, membership_retention_reference, clean,
legacy, previous, failure, unsafe, unknown and native targets. Its private
member-retention-fixtures.json uses the same characterization/clean key contract as
membership binding above. Exact25 historical owner py/json files from
`e124da80b9c0a3bbd3951d4ec1f248009502ac7d` are independently compared to Git and
executed for previous/failure/unknown. Existing private durable role-edge and failure
object restoration witnesses remain mandatory, including after interruption.

With IDENTITY_QUALIFICATION_DIR set to that private frame, run the frozen owner Python
with `-I -B services/access/tests/qualify_membership_retention.py --characterize` against
actual unchanged11 first. This records real member/org/profile DELETE through the restricted login/service_role
and membership TRUNCATE CASCADE through an owner-prepared supabase_auth_admin lane,
inside rolled-back synthetic transactions. Existing source grants service_role DML
but no TRUNCATE; a separate check proves its TRUNCATE remains42501. The administrator
connection uses SET LOCAL ROLE supabase_auth_admin inside a savepoint, verifies actual
current_user and existing effective TRUNCATE privileges, then rolls back the savepoint
and compares full state under the restored administrator. No new role edge or privilege
is granted. Old11 loses membership/role rows through that actual Auth-role truncate;
new12 refuses it for active/retired/roleless fixtures and member/org cascades.
Auth admin has no profile-table TRUNCATE privilege; its42501 denial is preserved,
and full membership/role/audit state is read under the restored administrator. The
source-bound witness binds the proof path, run ID, fixture digest and full old catalog.
No old Auth cascade is invented. The original Auth NO ACTION refusal is separately
checked through an administrator connection in a rollback-only transaction; it grants
no Auth privilege to the restricted runtime.

Run `tests/qualify_identity_baseline.py --record-membership-retention-reference` against
the empty known-source reference case. It executes captured source through12, verifies
every prior pinned catalog through11, sets bounded SQL deadlines before execution and
rollback verification, checks all staged roles after rollback, then exclusively publishes
membership-retention-reference.json mode0600 after rechecking source custody. The
independent pin requires root inspection/update; the recorder never updates its own pin.
Optimized Python is refused before fixture access. Historical files/references/pins
remain intact. Run the retention qualifier without arguments for the complete matrix.

The matrix checks only the intended three FK/function/trigger catalog changes, exact
function declaration/ACL and body delta, stable refusal with unchanged rows/roles/audit,
active/retired/roleless/multirow and modifying-CTE rollback, parent RESTRICT constraints,
TRUNCATE CASCADE, runtime/browser denial, and existing insert/update/seed/read behavior.
A conflicting owner reader lock proves bounded migration refusal with old catalog/data/
history unchanged and lock release before recovery. Event-trigger failures after the
first FK and after the new statement trigger prove early and late atomic DDL rollback.
Actual old11 FK drift and unknown history use rollback-only same-connection owner
preflight; neither claims subprocess migration execution. Explicit multi-target CONTINUE
IDENTITY runs under existing Auth table privileges; RESTART IDENTITY runs separately
under the administrator's sequence authority. Refused truncations preserve rows and
sequence state. This does not promise reversal of sequence consumption by ordinary
insert/seed fixtures. Role IDs must be numerically distinct and actual rows must prove
live admin/deleted employee roles on the intended member. The inherited native alias is
only the existing cluster/run custody anchor; all domain changes use eight scratch cases.
SQL evidence does not verify HTTP/provider/JWT or live-target adoption. Recovery retains applied history and all evidence; no
automatic downgrade, reset/prune, provision/deploy/pilot or production execution occurs.

Five impacts: scaffold extends the proven existing owner migration/reference/rollback
qualification pattern; shared UI has no consumer; agent context stays sufficient;
this owner runbook and root evidence/inventory/navigation record actual verification;
accepted ADRs are unchanged. New12 is a structural prerequisite, not an ID-B completion
or broader readiness claim.


## One-way retirement (identity_0013)

The existing membership guard additionally refuses changing a nonnull deleted_at through
ordinary UPDATE, seed conflict update or retry:23514,
identity_membership_retirement_immutable, org_member_retirement_immutable. Equal timestamps
remain noops; active updates/seed and null-to-retired keep existing revision behavior.
Initial legacy timestamps and all data remain intact. Only the guard body changes;
function identity/owner/ACL/invoker/search_path, triggers, constraints and other functions
remain unchanged. Historical revisions/references are immutable.

Active legacy seed writes remain supported; retired-member reactivation now deliberately
refuses atomically. Do not rerun legacy seeds as a membership recovery/rejoin procedure.
The unconditional org/account unique constraint remains; partial uniqueness and active
seed/provisioning lookups must change together in a later coordinated item. Server-time/
audit/expected-revision owner retirement and explicit fresh-ID join commands, protected
writer transition, live-account verification and Access/WRITE remain delivery gates.
No authorized lifecycle/API or real-target activation is implied by a structural guard.

Root prepares the existing private fixture protocol using membership_retirement_reference
instead of the previous reference case and retains member-retention-fixtures.json keys.
Run tests/qualify_membership_retirement.py --characterize against canonical12 first, then
the normal matrix. Use tests/qualify_identity_baseline.py
--record-membership-retirement-reference only once against its empty known-source case;
root independently inspects/pins13. Preserve all prior pins and source. Follow
[retirement evidence](MEMBERSHIP_RETIREMENT_EVIDENCE.md) for exact commands, receipts,
limits and five impacts. Live adoption/cutover requires ADR-0020 compatibility/recovery;
no automatic downgrade or source normalization, no reset/prune.

The synthetic CREATE FUNCTION failure fixture records a nontransactional sequence marker
only after the new guard is visible. Verify that witness before claiming rollback at the
injection point; generic safe migration failure alone is insufficient. The marker's narrow
migrator USAGE and all temporary event/function/sequence objects are fixture-only and
restored with retained witnesses. Final evidence distinguishes this from rollback of
ordinary sequence consumption. Retiming checks include backward and microsecond changes;
equivalent-offset representations of the same instant remain noops.


## Compatible active-uniqueness expansion (identity_0014)

Revision14 creates org_member_active_org_user_uidx, a UNIQUE btree index on
(org_id,user_id) WHERE deleted_at IS NULL. The original org_member_org_id_user_id_key
and backing full unique index stay. No rows, guards, triggers, functions or ACLs change.
Canonical14 therefore still forbids duplicate retired history: this is preparation,
not rejoin activation. Retain existing Python/SQL seeds and their supported behavior.

Full uniqueness removal requires coordinated owner commands/seed lookup/client changes,
exact dependency inspection and ADR-0020 compatibility/recovery. The current PostgREST
upsert has only a column-list conflict target; do not replace it with race-prone
read/insert or add an unaudited membership RPC. Current SQL seed lookup/SELECT privileges
also need explicit active-member transition. Real-target adoption remains unapproved.

Root runs tests/qualify_active_membership_index.py --characterize against canonical13,
then the full matrix. The private reference case is active_membership_index_reference;
member-retention-fixtures.json and other cases stay as established. Record reference14
once using qualify_identity_baseline.py --record-active-membership-index-reference and
independently inspect/pin. See [index evidence](ACTIVE_MEMBERSHIP_INDEX_EVIDENCE.md).
The rollback-only index-isolation lane temporarily drops the full constraint without
CASCADE under owner administration and restores all catalog/data. Canonical concurrency
retains both unique protections and one new synthetic winning membership; it is not
isolated-index attribution or an authorized join. Preserve all history/receipts/resources;
no resets, automatic downgrade or deployment. Five impacts remain in linked evidence.

The complete active-index matrix is single-use after its committed concurrency fixture.
Preserve the winner and precommit/result witnesses; use fresh synthetic cases for another
proof. An initial zero-members refusal is intentional rather than authority to reset,
delete, adopt or replay a prior winner. Failed/uncertain runs retain all diagnostics/data.


## Staged membership actor attribution — revision15

Revision15 adds nullable created_actor_id/updated_actor_id actor FKs with RESTRICT to
org_member. A new invoker trigger denies setting/changing them through ordinary writers,
including legacy table-wide writers; only identity_migrator may populate them in this
stage. Once nonnull, creation actor cannot be cleared/replaced even by that owner.
Existing table grants still cover new columns, so enforcement is the tested trigger,
not a claim that column privileges alone protect these fields. Its function inherits
no PUBLIC or default-grantee EXECUTE; no new command-owner privilege is granted.

No automatic backfill occurs. Legacy created_by/updated_by/timestamps remain intact;
unknown authors are not assigned to System and UUID equality is not mapping evidence.
Real adoption requires explicit verified account/service classifications, exact row/
revision preconditions, disposition of unknown references and retained mapping evidence.
Owner backfill is a controlled migration operation, not an API/startup task. Changed
actor fields advance the existing revision once per update; equal values do not.
This increment executes only rollback-only synthetic adoption with verified fixture
actors. Production/real-target adoption and membership commands remain unapproved gates.

The independent existing reference recorder uses
`--record-membership-actor-attribution-reference` with private case
membership_actor_attribution_reference. Root prepares the established fixture protocol,
runs `tests/qualify_membership_actor_attribution.py --characterize` against canonical14,
then the full source-bound matrix. Preserve historical references and every failed frame;
no reset, automatic downgrade, Docker removal or new generic qualification system.
[Build/evidence](../../_bmad-output/implementation-artifacts/spec-id-b-membership-actor-attribution.md)
records exact commands/results and limits. Full uniqueness and existing seed behavior
remain. Retirement still needs scoped immutable evidence/outcomes, authorization,
server attribution/time, protected writers and typed scoped CLI recovery.


Reviewed revision15 proof passes the actual matrix in47.815s and936 affected tests;
all three independent review layers complete with no deferrals. The matrix is now
single-use: repeat-upgrade proof retains one additional synthetic service actor and
attributed membership, with intent/result receipts and all original rows preserved.
No Auth account, account mapping or app grant is created for this attribution fixture.
Other adoption/default-ACL/current-guard drift lanes roll back. Preserve all receipts,
original frames and new fixtures; use fresh cases rather than resetting/deleting them.
The qualifier emits a fixed safe failure code instead of unhandled SQL diagnostics;
unknown-history writes use local statement/lock bounds with an actual blocking proof.


## Protected exact membership retirement — revision16

`identity.retire_membership` retires one exact organization/account/member/revision
through `identity_operator`; it derives the executor from the original database session
and protected `membership.retire` authority. It serializes the outcome namespace and
membership history, locks the exact row, then rechecks authority before mutation.
The server sets retirement/update time and durable update actor; creation attribution,
legacy history and roles are preserved. Membership, immutable event and outcome commit
atomically. Ordinary retirement INSERT/UPDATE/upsert/multirow writes refuse; equal
retired-value noops and active seeds remain supported. Migrator maintenance stays
controlled. Full uniqueness and the partial active index both remain.

Execute with the established prepared target and strict retirement command JSON:

```sh
OWNER_PYTHON -I -B services/access/operator_cli.py execute --owner identity --target PREPARED_TARGET --command-file COMMAND_JSON
OWNER_PYTHON -I -B services/access/operator_cli.py outcome --owner identity --target PREPARED_TARGET --command membership.retire --operation-id OPERATION_UUID --org-id ORGANIZATION_UUID --account-id ACCOUNT_UUID
```

The outcome flags are required only for retirement; actor registration keeps its
existing invocation/receipt. Missing or extraneous context fails before connection.
A committed receipt describes the original operation, including decimal revision and
event UUID; current authority is required for replay and lookup. Missing receipt is
unresolved. After response loss, recover the same operation before any fresh action;
changed input under the same operation conflicts. Busy/unavailable results never imply
rollback or authorize a fresh duplicate. Unknown receipt versions fail verification.

The existing rollback-only reference recorder adds
`--record-membership-retire-command-reference`, private case
`membership_retire_command_reference`, and verifies the historical chain through15.
Use `tests/qualify_membership_retire_command.py` on fresh head15 fixtures, then its
`--additional`, `--matrix`, `--recovery`, `--fresh-race` and `--review-fixes` stages.
These mutating stages retain committed synthetic memberships/events/receipts and are single-use;
never reset/reuse a committed frame. `--verify-retained` performs read-only database
consistency checks, retains a new proof receipt, and is repeatable on the committed frame.
Existing safe migration failure reconciliation
still applies: blocked activation, retained history and explicit recovery, no downgrade.

[Build/evidence](../../_bmad-output/implementation-artifacts/spec-id-b-membership-retire-command.md)
records runtime proof and review status. This delivers the bounded retirement command;
joining/rejoining, account verification/mapping, Access activation, WRITE and KDG server
readiness remain separate gates. No production migration, deployment or real authority
change is authorized by synthetic qualification.
