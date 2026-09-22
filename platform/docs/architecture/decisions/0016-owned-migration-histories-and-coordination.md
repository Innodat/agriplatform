# ADR-0016: Owned Migration Histories and Deployment Coordination

**Status:** Accepted  
**Date:** 2026-09-21  
**Scope:** Application and shared-service schema evolution

## Decision

Each application or shared runtime service owns its database schema, Alembic
revision files and migration-version table. Shared platform database objects have
an explicitly assigned owner and history. Owners may share a PostgreSQL instance
without sharing a single revision chain. Supabase-managed schemas remain outside
project migration ownership under [ADR-0015](./0015-alembic-migration-authority.md).

Migrations change only objects owned by their application/service. Changes needed
in another owner's schema belong to that owner's migration history. Configure
Alembic metadata and schema filtering accordingly; discovery of another schema is
not permission to modify it.

Provide one deployment entry point that coordinates required migration histories
in declared dependency order. Application teams retain local revision ownership;
the deployment command must surface failures rather than claim a partially applied
multi-owner deployment completed. Do not imply that independent migration histories
form one atomic database transaction. Exact deployment locking, compatibility and
recovery behavior remain architecture/delivery work.

Keep the ownership model compatible with later extraction of an application to a
separate database, following [application silos](./0003-application-silo-architecture.md).
This decision does not authorize direct cross-application runtime data access.

## Consequences

- Scaffold: provide local Alembic configuration and version-table placement plus
  registration of migration ownership/dependencies with shared deployment tooling.
- Verification: prove owner filtering, independent histories and dependency ordering
  against disposable databases; no execution implementation is claimed now.
- Shared UI: no impact.
- Agent context: existing silo rules suffice; update operational commands when built.
- Documentation: builder guidance and Leave target plan reference this decision.
- ADR impact: additive refinement of ADR-0015, which remains immutable.
- Planning only; no migrations executed or existing histories rewritten.
