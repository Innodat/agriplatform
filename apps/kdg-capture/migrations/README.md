# KDG controlled migration candidate

KDG owns schema kdg_capture and its separate Alembic history under ADR0015–0020.
No business tables, migration execution, release registration or API startup migrations
are delivered here. The initial revision only lets Alembic initialize its private ledger
in an explicitly prepared schema. Native PostgreSQL acceptance remains unfinished.

Follow the platform-wide [focused migration verification approach](../../../platform/docs/development/migration-verification.md).
The shared helper now provides a small controlled transaction wrapper instead of an
empty-schema/exact-ledger inventory. Alembic resolves revision history; PostgreSQL
enforces privileges and transactions. Normal owned tables and new revisions do not
require editing a generic allowlist. The helper checks the exact nonadministrator
migration login/schema owner and keeps bounded waits, an owner advisory lock and safe
failures. It does not certify all role memberships, ACLs or cross-owner privileges.
Those require controlled setup and focused tests using real restricted logins.

Owner URL/command policy stays restricted to explicitly selected synthetic kdg-local
at 127.0.0.1:55482, database kdg_schema_<32 lowercase hex>, with the exact migrator and
no URL query options or ambient fallback. Only online upgrade head is permitted.
Unknown endpoint54322 is untouched. Keep ledger access private and migration credentials
separate from API/runtime/operator credentials. Runtime/operator receive only the
operations required by the consuming domain migration.

The neutral helper and behavioral tests are managed in ../database-tools. Update the
builder templates, then use selected Node26.11.1 from repository root:

```sh
"$N" platform/builder-cli/scripts/sync-kdg-database.mjs --write
"$N" platform/builder-cli/scripts/sync-kdg-database.mjs --check
```

Never hand-edit generated helpers/tests/manifest. Owners retain schema, roles, histories,
URL/command policy, domain rules and authorization. No other owner is migrated.

Using P as the approved retained migration environment's Python, from repository root:

```sh
"$P" -I -B apps/kdg-capture/database-tools/test_owned_migration.py
"$P" -I -B apps/kdg-capture/migrations/tests/test_foundation.py
```

P is platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python:
Python3.15, SQLAlchemy2.1.4, Alembic1.20.0 and psycopg3.3.6. No install, manifest, lock,
API environment or TypeScript7.0.2 baseline change. Tests are offline control-flow and
metadata evidence, not actual PostgreSQL privileges, locks or rollback.

## Pending native acceptance

The user authorized the narrow exception to resume the retained synthetic stack and
prepare one isolated KDG test database and three restricted roles. That authorization
has not been used successfully: the draft fixture failed while reading its input,
before connecting or creating anything. The stack was stopped with resources retained.
The draft schema_fixture.py is unqualified and must not be treated as a working setup.
Do not rerun historical preparers or the rejected broad Access verifier.

The next native item should use ordinary isolated fixture setup and actual separate
migrator/runtime/operator logins. Prove upgrade/repeat, private ledger/DDL and cross-owner
denials, owner serialization, a failed transaction's retained state and explicit retry.
Alembic should reject unknown history through its ordinary revision handling. Add a
specific guard only if a reproduced failure requires it. Domain RLS and business-write
cases belong with their first table/API slice. Preserve all historical databases,
roles, data, source-bound evidence and Docker resources; stop normally after testing.
No general provisioning, real accounts/access, deployment/pilot or cleanup is authorized.

Current local-only command, not yet natively qualified: supply
KDG_MIGRATION_TARGET_ID, KDG_MIGRATION_ENVIRONMENT_KIND and
KDG_MIGRATION_DATABASE_URL privately, then run
`P -I -B -m alembic -c apps/kdg-capture/alembic.ini upgrade head`.
A reported failure blocks progress; reconcile actual state before retrying.
No automatic downgrade or claim of release readiness follows from this candidate.

The [earlier candidate evidence](../docs/SCHEMA_FOUNDATION_CANDIDATE_EVIDENCE.md) remains
historical and source-bound. Its exhaustive inventory assertions describe that version,
not the current simplified helper.
