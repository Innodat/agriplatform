# ADR-0026: Worker Service Identity and NGO Scope

**Status:** Accepted  
**Date:** 2026-09-22  
**Scope:** Tenant-aware background processing across applications and shared services

## Decision

Use an owner-specific restricted worker service identity across the NGOs it is
explicitly authorized to serve. Do not provision a separate worker database account
or key for every NGO by default. This is not a single universal platform credential:
application/service ownership, capability and environment boundaries retain separate
restricted authority under ADR-0017.

A narrowly authorized discovery/claim operation may find due work across permitted
NGOs and return the metadata needed to claim it. It must not expose general tenant
business data. The owning implementation selects and verifies the concrete mechanism.
Process each item under its authoritative recorded NGO ownership and service identity,
established explicitly for every protected transaction under ADR-0018. Check item
ownership; do not trust an arbitrary payload or client-supplied NGO as authority.

Transaction-local context ends on commit/rollback and cannot leak through pooled
connections. NGO context scopes access but does not grant permission. Workers retain
only their bounded job authority, not database administrator or unrestricted business
record access. Preserve human initiation separately where needed for audit; the worker
does not impersonate that human. Cross-owner access remains through service contracts,
not shared worker access to application tables.

## Impact and verification

- Acceptance: interleaved NGOs, missing/mismatched scope, rollback/pool reuse, limited
  cross-NGO discovery, denied unrelated access and explicit service attribution.
- Scaffold: prove restricted queue-discovery and per-item context patterns before
  promotion; no per-NGO secret generation or universal cross-application queue reader.
- Shared UI: no NGO credential setup or new control.
- Agent context: record this platform-wide interpretation alongside tenant safeguards.
- Documentation: builder guidance and Leave requirements/tracker link here; Leave
  ADR-0115 remains its accepted concrete application, not a new conflicting rule.
- ADR: complements [0017](./0017-runtime-and-migration-database-authority.md),
  [0018](./0018-transaction-scoped-tenant-context.md) and
  [0025](./0025-record-attribution-and-audit-provenance.md); originals unchanged.
- Planning only; no credentials, database grants or worker implementation created.
