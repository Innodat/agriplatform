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
