# Identity baseline and source handover (ID-A)

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
integration privileges granted by their actual owners: auth schema USAGE via the
schema owner (`supabase_admin` on the qualified native target), and TRIGGER,
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
exact known owned head, validates private ledger table and column ACLs, rechecks the
legacy source history and verifies the complete owned catalog fingerprint. This
postcondition applies to clean setup, adoption and retries; an unknown/elevated profile
or an upgrade target that leaves an empty ledger rolls back before commit. The trusted
source-derived reference must already be recorded and pinned; no bootstrap bypass
or target self-approval is available.

For equivalent legacy synthetic state, use the same upgrade command with
`IDENTITY_MIGRATION_MODE=adopt`. Adoption first compares a read-only catalog against
the pinned repository reference, applies only the existing Access bridge and records
`identity_0001`. It never reruns source CREATEs or edits the original Supabase ledger.
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

Actor registry, revised membership lifecycle, account/grant migration and Access v2
remain ID-B/ACCESS work. No readiness promotion, Leave implementation, runtime service,
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
