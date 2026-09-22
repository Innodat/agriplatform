# Platform Architecture Decision Records

Platform ADRs record decisions that apply to the platform, common services, builder
scaffolding, or more than one application.

## Rules

- Statuses are `Proposed`, `Accepted`, `Superseded`, or `Deprecated`.
- Accepted ADRs are immutable historical records. Change a decision with a new ADR
  that links to and supersedes the old one.
- Numbering is local to this directory and never reused.
- Application ADRs link here rather than copying platform decisions.
- Each builder-impacting ADR must be represented in templates, validation, tests,
  and documentation when implemented.

## Index

| ADR | Status | Decision |
|---|---|---|
| [0001](./0001-fastapi-openapi-api-boundary.md) | Accepted | FastAPI/OpenAPI is the application API boundary |
| [0002](./0002-supabase-auth-and-entra.md) | Accepted | Retain Supabase Auth and federate Microsoft Entra ID for MVP |
| [0003](./0003-application-silo-architecture.md) | Accepted | Applications are self-contained silos with explicit platform/service boundaries |
| [0004](./0004-shared-fastapi-content-service.md) | Accepted | Content control is a shared FastAPI runtime service |
| [0005](./0005-direct-to-storage-uploads.md) | Accepted | File bytes use signed direct-to-storage transfer |
| [0006](./0006-common-notification-capability.md) | Accepted | Notifications are a common capability with domain-owned events |
| [0007](./0007-continuous-scaffold-evolution.md) | Accepted | Builder scaffolding evolves continuously with proven patterns |
| [0008](./0008-selective-structured-prompt-driven-development.md) | Superseded | Use governed SPDD selectively and evolve prompts continuously |
| [0009](./0009-atdd-and-tdd-development-loop.md) | Accepted | Use ATDD as the outer loop and TDD as the inner loop |
| [0010](./0010-bmad-as-delivery-workflow.md) | Accepted | Use BMAD as the generic delivery workflow with project-owned quality gates |
| [0011](./0011-application-roles-and-business-permissions.md) | Accepted | Application-maintained default roles, explicit business permissions, and advanced custom roles with reviewed grants |
| [0012](./0012-operation-identity-idempotency-and-tracing.md) | Accepted | Stable operation IDs for safe retries, application-owned atomic records, downstream event identities and separate causal tracing |
| [0013](./0013-explicit-revisions-for-reviewed-changes.md) | Accepted | Explicit record revisions and atomic checks protect reviewed changes; stale confirmations require renewed review |
| [0014](./0014-python-database-access-and-api-models.md) | Accepted | SQLAlchemy/Psycopg PostgreSQL access, separate Pydantic API schemas and proven opt-in CRUD scaffolding |
| [0015](./0015-alembic-migration-authority.md) | Accepted | Alembic owns project schema migrations; reviewed drafts, explicit database security changes and deliberate adoption of existing SQL assets |
| [0016](./0016-owned-migration-histories-and-coordination.md) | Accepted | Separate schema/revision/version-table ownership per app or service, with shared deployment coordination |
| [0017](./0017-runtime-and-migration-database-authority.md) | Accepted | Per-owner restricted runtime database identities; migration authority isolated in deployment |
| [0018](./0018-transaction-scoped-tenant-context.md) | Accepted | Backend-verified NGO/actor context per transaction, fail-closed tenant RLS and explicit worker identities |
| [0019](./0019-current-server-side-authorization.md) | Accepted | Current membership/permission checks per protected request; domain checks, no stale grants and fail-closed access verification |
| [0020](./0020-safe-schema-changes-and-release-recovery.md) | Accepted | Mandatory platform-wide migration coordination, compatible schema evolution, failure gates and explicit recovery |
| [0021](./0021-revocation-and-in-flight-operations.md) | Accepted | Revocation blocks subsequent authorization checks; bounded already-authorized operations may complete |
| [0022](./0022-short-transactions-and-external-service-calls.md) | Accepted | Keep transactions short and external service waits outside business locks by default; document justified exceptions |
| [0023](./0023-structured-operational-logs-and-sensitive-data.md) | Accepted | Structured operational diagnostics with safe correlation fields; exclude sensitive content and keep audit separate |
| [0024](./0024-durable-delivery-retries-and-audited-recovery.md) | Accepted | Bounded durable-delivery retries, retained failures and scoped audited operational recovery |
| [0025](./0025-record-attribution-and-audit-provenance.md) | Accepted | Stable actor/time attribution, immutable audit provenance and table-category-aware scaffolding |
| [0026](./0026-worker-service-identity-and-ngo-scope.md) | Accepted | Restricted owner-specific worker identity across NGOs with narrow discovery and per-item transaction scope |
| [0027](./0027-bounded-worker-shutdown-and-deployment-reporting.md) | Accepted | Bounded recoverable shutdown, automatic forced-stop fallback and truthful deployment warnings |
| [0028](./0028-event-payload-versions-and-queued-work-compatibility.md) | Accepted | Explicit event type/version and compatibility for queued, in-flight and retryable work across releases |
| [0029](./0029-notification-retry-expiry-and-retention.md) | Accepted | Notification-only 90-day retry window, terminal retention and expiry-safe deduplication cleanup |
