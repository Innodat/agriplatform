# Focused platform migration verification — KDG adoption

This code/scaffold slice applies the user's clarified platform-wide approach without
changing the Supabase Auth/PostgreSQL + FastAPI + Alembic architecture. The generic
helper no longer inventories all owned objects or reimplements Alembic ledger internals.
Owners retain histories, schema/grant policy and actual allow/deny assertions.

The motivating regression starts with an ordinary owned capture table and a newer
history. The old helper raises owned_migration_history_invalid before yielding a
migration connection. This was observed before implementation. It is a test-double
behavioral RED, not a PostgreSQL result. The earlier ten neutral/eight owner tests passed
before refactoring; identity refusal, failure blocking, bounded settings and safe errors
remain protected. Assertions specific to the intentionally removed catalogue whitelist
were replaced with the new contract, rather than relabeled as unexplained failures.

The neutral wrapper keeps exact nonadministrator migrator/session checks, prepared
schema ownership, one stable owner advisory transaction lock, bounded waits and
transaction handling. Alembic resolves revisions and runs migrations through its normal
transaction context. PostgreSQL privileges remain the authority for access. The wrapper
is not a complete privilege auditor; restricted provisioning and actual permission tests
remain prerequisites. No production coordination or release activation is implemented.

Canonical helper and emitted tests were updated together; KDG managed files were
synchronized by sync-kdg-database, including the manifest. The builder test installs a
fresh rendered application and executes its emitted tests. Owner wiring tests load the
actual KDG env with test doubles; actual CLI refusal checks execute Alembic without
configuration or in prohibited directions. No database connection is supplied or used.

Current evidence proves offline control flow, metadata, emitted-test execution and parity.
It does not prove PostgreSQL privileges, locks, rollback, unknown stored history handling,
business-table RLS, previous API compatibility or production release readiness. Native
KDG acceptance remains the next distinct item. The previous narrow fixture authorization
persists, but no Docker lifecycle, SQL, role/database setup or historical verifier was
executed in this slice. The failed draft fixture remains unqualified and unchanged.

Platform impact: neutral scaffold helper/tests and reusable guidance are updated now;
root agent context routes every app/service to that guidance. Other owners are not
rewritten or migrated. Shared UI has no impact. ADR0015–0020 are unchanged; the new
implementation follows their existing principles. Historical candidate evidence/receipts,
concurrent changes, Docker resources and approved dependency manifests remain preserved,
including TypeScript7.0.2. No Leave/editor, real accounts/access, production, general
provisioning, deployment/pilot, cleanup or fingerprints/HMAC.

Exact commands/results, requirement traceability, source bindings and review triage are
recorded in the [delivery receipt](evidence/focused-migration-verification-20261023.json)
and [BMAD item](../../../_bmad-output/implementation-artifacts/spec-platform-focused-migration-verification.md).
