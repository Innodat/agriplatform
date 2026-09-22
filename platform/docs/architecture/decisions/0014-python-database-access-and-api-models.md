# ADR-0014: Python Database Access and Separate API Models

**Status:** Accepted  
**Date:** 2026-09-21  
**Scope:** Default for new application backends and their scaffolding

## Decision

Use Supabase PostgreSQL with SQLAlchemy and the Psycopg driver for application
business-data access. Use separate Pydantic request/response schemas for FastAPI
contracts. Do not adopt SQLModel as the default. Exact compatible dependency
versions and pooling configuration are selected and verified during delivery.

The business-data path is browser to FastAPI to SQLAlchemy/Psycopg to PostgreSQL.
Do not introduce Supabase Data API/PostgREST as a second business-data read/write
path in new applications. Existing applications migrate deliberately rather than
being rewritten as a consequence of this decision. Supabase Auth and authorized
signed file transfers retain their specialized responsibilities.

Application workflows own transaction boundaries; data-access helpers participate
without independently committing. Ordinary records may use ORM mapping, with
explicit SQL expressions where needed. Preserve NGO isolation and restricted
runtime database roles; this choice does not authorize RLS bypass.

Keep persistence models distinct from public contracts. Create/update schemas
expose only permitted inputs; response schemas expose only permitted information.
A database column is not automatically an API field. Frontend business contracts
are generated or validated from FastAPI OpenAPI, not directly from table shapes.

Scaffolding may generate session setup, database models, explicit API schemas,
routine access functions, opt-in CRUD routes, permissions/tenant-scoping hooks,
revision handling, pagination and verification examples. Explicit domain commands
implement submission, approval, cancellation and balance adjustments. Generated
CRUD must not bypass domain rules. Prove generic patterns in a working application
and promote them in the same delivery item; no speculative shared repository
framework is required.

## Related decisions and evidence

- [API boundary](./0001-fastapi-openapi-api-boundary.md)
- [Application silos](./0003-application-silo-architecture.md)
- [Scaffold evolution](./0007-continuous-scaffold-evolution.md)
- [Operation identity](./0012-operation-identity-idempotency-and-tracing.md)
- [Reviewed revisions](./0013-explicit-revisions-for-reviewed-changes.md)
- [Supabase SQLAlchemy integration](https://supabase.com/docs/guides/troubleshooting/using-sqlalchemy-with-supabase-FUqebT)
- [SQLAlchemy PostgreSQL drivers](https://docs.sqlalchemy.org/en/20/dialects/postgresql.html)

## Consequences

- Scaffold: update templates, generation and disposable-app tests when this pattern
  is implemented; the current builder remains a placeholder.
- Shared UI: consume explicit API contracts; no new UI component now.
- Agent context: existing API-boundary and silo instructions remain applicable.
- Documentation: builder guidance and Leave tracker reference this default.
- ADR impact: additive refinement; accepted ADRs remain unchanged.
- Schema migration ownership/tooling is the next architecture decision.
- Planning only; no installed dependencies, migrations or implementation approval.
