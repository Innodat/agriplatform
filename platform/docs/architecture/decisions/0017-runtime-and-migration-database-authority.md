# ADR-0017: Separate Runtime and Migration Database Authority

**Status:** Accepted  
**Date:** 2026-09-21  
**Scope:** Application/service database credentials and deployment

## Decision

Give each application/service its own restricted runtime database identity. Grant
only the data operations required in its owned schema; do not grant direct access
to another application's business tables. Cross-owner runtime capabilities retain
the [HTTP service boundary](./0003-application-silo-architecture.md).

Keep migration authority separate. Schema-changing credentials belong to the
controlled deployment process and are unavailable to running APIs and workers.
Coordinate each owner's migration privileges through the shared deployment entry
point under [ADR-0016](./0016-owned-migration-histories-and-coordination.md).
Bootstrap administration needed to provision schemas/roles is separate from normal
application runtime and must not become its default connection identity.

Runtime identities must not be database administrators, owners of protected tables,
or roles with BYPASSRLS or the ability to assume such privileged roles. Grant only
necessary operations, not blanket table privileges. Schema grants do not replace
NGO isolation or application-level authorization. Tenant-context propagation and
its transaction lifecycle are a separate architecture decision.

## Consequences

- Scaffold/deployment: define separate runtime and migration configuration and
  provisioning templates; deployment secrets must not enter API/worker environments.
- Verification: exercise actual runtime roles against permitted operations, forbidden
  cross-owner access, forbidden schema changes and tenant boundaries. Admin-role
  tests alone do not establish isolation.
- Shared UI: no impact.
- Agent context: existing least-privilege and silo rules suffice.
- Documentation: builder and Leave plan reference this separation.
- ADR impact: additive; accepted records unchanged.
- Planning only; no roles, credentials or database permissions changed.

## Evidence

[PostgreSQL row-security behavior](https://www.postgresql.org/docs/17/ddl-rowsecurity.html)
distinguishes ordinary runtime roles from table owners, superusers and BYPASSRLS.
