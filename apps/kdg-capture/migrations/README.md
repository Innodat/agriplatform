# KDG schema foundation candidate

This owner-local Alembic history is a reviewed code candidate, not an applied schema or
verified PostgreSQL security boundary. It prepares only kdg_capture's private migration
ledger; no questionnaire, child, assignment, capture or outcome tables exist here.
The API never imports this directory or starts migrations. The release registry remains
unchanged. Do not treat the checked-in revision or unit tests as native acceptance.

The neutral helper and its unit tests come from builder templates in a separate managed
`../database-tools` root. Update the owning templates, then use selected Node 26.11.1
from repository root:

```sh
"$N" platform/builder-cli/scripts/sync-kdg-database.mjs --write
"$N" platform/builder-cli/scripts/sync-kdg-database.mjs --check
```

Never hand-edit generated helpers/tests/.generated-files.json. Application owners retain
schema names, roles, revisions, migration history, domain tables and authorization.
Other apps can consume the same inert helper/tests; no existing app is migrated.
The helper is intentionally a strict empty-schema/initial-ledger candidate. Future
business tables need explicit owner catalog/migration evolution and new acceptance.

Candidate guards check an actual migrator login matching session_user, PostgreSQL17,
no superuser/BYPASSRLS/role or database creation/replication/database ownership, no incoming
or outgoing memberships for the three selected roles, exact prepared schema owner/ACL,
no effective cross-owner schema creation or relation/function authority, and only the
expected permanent non-RLS private Alembic ledger. Unexpected schema objects, ledger
columns/privileges/history/triggers/rules/policies or extra indexes refuse. The controlled
transaction sets bounded waits/deadline and takes a stable owner advisory transaction lock,
then rechecks after waiting and verifies the ledger before committing. Errors are fixed
safe identifiers; no connection URL, password, SQL payload or DB exception is rendered.
Only online upgrade head is supported. No stamp/downgrade or automatic rollback of an
applied migration is allowed; a reported failure requires state reconciliation.

No database is contacted by import, policy validation, history inspection or unit tests.
Using P as the existing approved Access migration environment's Python:

```sh
"$P" -I -B apps/kdg-capture/database-tools/test_owned_migration.py
"$P" -I -B apps/kdg-capture/migrations/tests/test_foundation.py
```

P is `platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python`.
It already contains approved SQLAlchemy2.1.4, Alembic1.20.0 and psycopg3.3.6 on Python3.15.
The current KDG API environment and generated HTTP-only API manifest do not include these
migration dependencies. Tests use the explicit retained migration environment; no default
API or clean-install migration dependency qualification is claimed. No manifest/lock or
installation change is included. Generated schema tests are opt-in migration-env tests.

## Native acceptance remains blocked

The known disposable PostgreSQL endpoint127.0.0.1:55482 is stopped. Port54322 belongs to
an unknown target and must not be used. The historical atomic fixture is not a compatible
KDG target: its migrator owns its database and its roles/schema are different. Do not
rerun its CREATE ROLE/DATABASE preparer or resume Docker under the existing no-provisioning
scope. No migration command below was executed against PostgreSQL in this delivery.

Native verification requires one explicitly prepared disposable database named
kdg_schema_<32 lowercase hex>, at fixed127.0.0.1:55482, with:

- Separate exact LOGIN roles kdg_capture_migrator, kdg_capture_runtime and
  kdg_capture_operator; nonprivileged, no memberships in either direction, no database
  ownership/CREATE. The fixture administrator owns the dedicated database.
- Existing empty kdg_capture schema owned by the migrator. Runtime/operator have USAGE
  only; PUBLIC/other roles have no schema authority. No shared business data or cross-owner
  privileges. Preparing these objects is separate from migration execution.
- A private explicit migration URL, target ID kdg-local and local_disposable/ci_disposable
  kind. URL uses postgresql+psycopg, exact migrator login and nonempty password; no query
  options, ambient URL fallback or alternative database/host/port.

After native target preparation is explicitly authorized and independently verified,
the future native proof must exercise actual separate migrator/runtime/operator logins,
empty upgrade, repeated upgrade, ledger/catalog/ACL mismatch refusal, DDL/ledger access
denial for runtime/operator, owner locking, rollback/forward retry and unchanged unrelated
schemas/data. Both current and previous API versions must remain compatible; this
candidate adds no API change or business data, but native compatibility is still unproved.
No role or target preparation, native run, production registration, release activation,
Auth/account setup or resource cleanup follows from these instructions.

Controlled candidate command (not executed natively): supply KDG_MIGRATION_TARGET_ID,
KDG_MIGRATION_ENVIRONMENT_KIND and KDG_MIGRATION_DATABASE_URL privately, then run
`P -I -B -m alembic -c apps/kdg-capture/alembic.ini upgrade head` from repository root.
Local-only connection arguments pin hostaddr and disable TLS/GSS/passfile fallback for
this disposable loopback candidate. They cannot select a remote or production target.
