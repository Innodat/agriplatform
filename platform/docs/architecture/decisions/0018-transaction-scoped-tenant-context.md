# ADR-0018: Transaction-Scoped Tenant and Actor Context

**Status:** Accepted  
**Date:** 2026-09-21  
**Scope:** Tenant-owned data access through application APIs and workers

## Decision

Authenticate the caller and verify access to the selected NGO before granting a
business-data transaction that context. Client-selected NGO IDs are requests for
scope, not proof of membership or authority. The trusted backend sets verified NGO
and actor context using transaction-local database settings on the same connection
as the protected reads and writes. Do this for reads as well as mutations.

RLS confines NGO-owned records to the transaction's NGO. Missing or invalid tenant
context denies access to tenant-owned data. Application authorization additionally
restricts employees, fields and actions; membership alone is not permission for all
records within an NGO. Runtime database identities follow
[ADR-0017](./0017-runtime-and-migration-database-authority.md).

Never retain request tenant/actor context as connection-wide state. Establish it
explicitly in each transaction and keep pooled connections free of tenant defaults;
commit or rollback ends that transaction-local context. No process-global current
NGO variable is an authorization source. Test reuse of connections across NGOs,
including rollback, missing-context and concurrent-request cases.

Background work supplies an explicit NGO and an authorized job/service identity.
Do not impersonate a logged-in employee. Preserve initiating user attribution
separately when needed for audit. Job authorization and service authority must be
bounded to the intended capability; tenant context is not itself authorization.

The backend is trusted to establish this context: RLS based on backend-set values
is defense against scoping mistakes, not proof against compromise of that backend.
Exact context keys, membership-resolution contracts and restricted cross-tenant job
discovery remain delivery/architecture decisions. They must not create broad access
to tenant business data when context is absent.

## Consequences

- Scaffold: prove and promote a shared transaction-context helper, restricted-role
  RLS examples and pool-reuse/tenant-denial tests in the owning delivery item.
- Shared UI: existing NGO selection remains; no additional user setup.
- Agent context: existing tenant-isolation rules suffice.
- Documentation: builder and Leave plan reference this convention.
- ADR impact: additive; no accepted decision changed.
- Planning only; no database policies or runtime behavior implemented.

## Evidence

[PostgreSQL SET LOCAL](https://www.postgresql.org/docs/17/sql-set.html) limits settings
to the current transaction. Safe use also requires no tenant-wide session defaults.
