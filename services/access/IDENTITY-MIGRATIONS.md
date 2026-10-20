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
