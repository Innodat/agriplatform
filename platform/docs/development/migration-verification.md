# Focused migration verification

Applies to all Agriplatform application and service delivery, including scaffolding.
This implements the existing [migration authority](../architecture/decisions/0015-alembic-migration-authority.md),
[owner histories](../architecture/decisions/0016-owned-migration-histories-and-coordination.md),
[separate credentials](../architecture/decisions/0017-runtime-and-migration-database-authority.md)
and [release safety](../architecture/decisions/0020-safe-schema-changes-and-release-recovery.md)
decisions. It introduces no new architecture or delivery workflow.

- Keep controlled migrations, least privilege, application ownership and focused access tests.
- Prefer ordinary Alembic/PostgreSQL behavior over custom checks of their internal structures.
- Promote proven reusable fixtures and behavioral tests into scaffolding with their first consumer.
- Add a guard for an identified failure case, with a test showing what it prevents.

Alembic interprets the owner's revision history. PostgreSQL enforces grants, constraints,
RLS and transaction behavior. Avoid a second implementation of Alembic's ledger format
or a whitelist of every permitted application object. Such a whitelist would require
changing generic infrastructure whenever an ordinary business migration adds a table.
A specific contract may justify a targeted catalogue check; record its concrete purpose.
This guidance does not remove checks protecting actual application invariants.

Use the existing BMAD ATDD/TDD workflow. Start with the requested migration outcome and
its relevant failure. Test ordinary upgrade/repeat behavior, the supported previous
schema/data and previous consumer where applicable, and explicit failure/retry behavior.
Use actual restricted runtime identities for required allow/deny cases: owned operations,
forbidden DDL, cross-owner access and tenant isolation. An empty ledger does not prove
business-table RLS or compatibility. Test doubles prove wrapper control flow only.
Do not manufacture more mock coverage to replace an unavailable database test.

The opt-in application scaffold helper supplies a small PostgreSQL17+ transaction
wrapper: expected nonadministrator migration login, prepared schema owner, stable
owner advisory lock, bounded waits and safe failures. It deliberately does not audit
every effective privilege, membership, default grant or schema object on each upgrade.
Restricted role provisioning and actual permission tests remain prerequisites for
using it. Migrations explicitly qualify owned schemas and grant only required access;
review raw migration operations because autogeneration filters do not constrain them.
Keep the private Alembic ledger unavailable to runtime/operator credentials.

The helper does not implement coordinated multi-owner deployment, activation or
recovery. Required migration failure blocks activation; reconcile actual database state
before retrying, and never automatically downgrade an applied migration. Keep credentials
out of APIs/workers and migrations out of startup. Preserve previous-version compatibility
and explicit recovery evidence under ADR-0020.

Applications own schemas, histories, authorization and domain assertions. Platform owns
proven neutral helpers, fixtures and their scaffolded tests. Reuse an existing fixture
where compatible; do not rerun setup as a substitute for a read-only inspection. Keep
synthetic fixtures isolated, and preserve historical evidence and retained resources.
Promoting a fixture requires actual consuming evidence, not merely a shared-looking API.

KDG is the first consumer of the simplified helper. Its emitted wrapper/owner tests
remain offline evidence until separate native acceptance passes. Other existing owners
retain their histories, tests and implementations; adopt the shared approach in their
next relevant delivery rather than rewriting them automatically.
