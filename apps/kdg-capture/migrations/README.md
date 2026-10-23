# KDG controlled migration candidate

KDG owns schema kdg_capture and its separate Alembic history under ADR0015–0020.
This history contains no business tables. Controlled native execution was confined to
the isolated synthetic fixture; API startup and the release registry remain unchanged. The initial revision only lets Alembic initialize its private ledger
in an explicitly prepared schema. Native acceptance now passes for this initial-ledger foundation only.

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

## Native foundation acceptance

The approved retained synthetic run was resumed and one fresh template0 database plus
three restricted roles were prepared by tests/native_fixture.py. Roles already present
are refused before alteration/adoption. The earlier schema_fixture.py remains unchanged
as an unqualified failed historical draft. Do not run it, historical preparers or the
rejected broad Access verifier. All created resources and private credentials are retained.

The actual first Alembic upgrade succeeded. The reusable native suite proves separate
migrator/runtime/operator logins, upgrade/repeat, private-ledger/DDL/cross-owner/SET ROLE
denials (SQLSTATE42501), owner-lock refusal/retry, transactional DDL rollback and ordinary
unknown-history refusal/restoration/retry. A separate SELECT-only inspector verifies
retained head, absence of the rolled-back probe, foreign sentinel and unchanged
preexisting role/database metadata. Historical business rows are not rehashed. Add a
specific guard only if a reproduced failure requires it. Domain RLS and business-write
cases belong with their first table/API slice. Preserve all historical databases,
roles, data, source-bound evidence and Docker resources; stop normally after testing.
No general provisioning, real accounts/access, deployment/pilot or cleanup is authorized.

Qualified initial-ledger local command: supply
KDG_MIGRATION_TARGET_ID, KDG_MIGRATION_ENVIRONMENT_KIND and
KDG_MIGRATION_DATABASE_URL privately, then run
`P -I -B -m alembic -c apps/kdg-capture/alembic.ini upgrade head`.
A reported failure blocks progress; reconcile actual state before retrying.
No automatic downgrade or claim of release readiness follows from this candidate.

The [earlier candidate evidence](../docs/SCHEMA_FOUNDATION_CANDIDATE_EVIDENCE.md) remains
historical and source-bound. Its exhaustive inventory assertions describe that version,
not the current simplified helper.


Native scenarios/tests are managed separately in ../native-database-tools. Update their
canonical templates, then use selected Node26.11.1 with
`platform/builder-cli/scripts/sync-kdg-native-database.mjs --write` and `--check`.
Never hand-edit either managed root or its manifest. The native module does not provision
anything; KDG owns its explicit fixture adapter and fixed target/role/history policy.
See [native evidence](../docs/NATIVE_SCHEMA_FOUNDATION_EVIDENCE.md) for exact retained
fixture references, proof commands, review and limitations. Only rerun native acceptance
against that retained new fixture after verifying its custody and resuming the known run.


## Separate bounded WRITE prerequisite

`../write-tools` is a separate scaffold-managed source/test inventory; it does not
change this migration or native-check inventory. See
[WRITE context evidence](../docs/WRITE_CONTEXT_EVIDENCE.md). Run optional synthetic
checks with the retained migration environment P, not the dependency-minimal API env:
`P -I -B apps/kdg-capture/write-tools/test_transaction_context.py` and
`P -I -B apps/kdg-capture/write-tests/test_owner_context.py` from repository root.
No database connection or API startup integration follows from these tests. Update
canonical write-tools templates, then selected Node26.11.1
`platform/builder-cli/scripts/sync-kdg-write.mjs --write` / `--check`; do not edit managed
copies. KDG remains responsible for current authority, exact target/mode and domain SQL.

The managed WRITE helper now also supplies OutcomeKey/outcome_lock for exact org/account/
handler-command/operation serialization. Use only inside the verified owner transaction.
This synthetic extension does not apply a migration, create an outcome table, prove native
lock timing/release or supply stored-resource authorization/replay. KDG business unique
constraints and atomic outcome/evidence/domain writes remain a separate consuming gate.

The app-owned inert outcome storage candidate adds a separate optional synthetic suite:
`P -I -B apps/kdg-capture/write-tests/test_operation_outcomes.py` using the retained
WRITE environment above. See [candidate evidence](../docs/OUTCOME_STORAGE_CANDIDATE_EVIDENCE.md).
This introduces no migration/table, connection or public recovery route; native capture/
revision/outcome linkage and atomicity still require a coordinated consuming delivery.

## Unapplied linked storage candidate

`candidates/0002_capture_storage.py` is deliberately outside active `versions` discovery;
head remains0001_kdg_foundation. Do not copy/promote it until the consuming native/writer/
release gates pass. It declares complete supporting parents and linked capture/history/
outcome, not an outcome-only migration. Optional offline smoke command from repo root:
`"$P" -I -B apps/kdg-capture/write-tests/test_capture_schema.py` with the retained WRITE env.
It calls Alembic offline Operations directly without changing env.py's --sql refusal or
connecting. See [schema evidence](../docs/LINKED_STORAGE_SCHEMA_EVIDENCE.md). No creation
of a database/schema/role, seed rows, native target operation or cleanup occurs.
Historical0001 native qualification remains tied to its old source/head; a consuming
suite must qualify the new schema/current authority without rewriting that evidence.
