# ADR-0035: Database Structural Integrity and Application Rules

**Status:** Accepted  
**Date:** 2026-09-23  
**Scope:** Project-owned schemas, persistence design and scaffolding

## Decision

Enforce straightforward structural guarantees in the database in addition to helpful
API validation. Use appropriate nullability, check constraints, unique constraints/
indexes and foreign keys within the owning schema/domain. Examples include required
fields, valid references, operation/event identity uniqueness within its defined scope,
and one active draft where the application has chosen that rule.

Tenant-owned relationships must not accidentally join records from different NGOs.
Where both records are tenant-owned within the local persistence boundary, enforce
matching tenant scope through an appropriate tenant-aware reference/constraint design.
RLS remains necessary but is not a substitute for structural integrity. Shared/global
references have different semantics and must be modeled explicitly, not assigned a
fictional NGO. Do not introduce cross-service table access or foreign-key dependencies
that violate accepted owner boundaries merely to satisfy a generic scaffold pattern.
Existing explicitly accepted shared identity exceptions are not silently superseded.

API/domain validation runs first where useful for user feedback. Database enforcement
protects concurrent requests and other supported writers, including workers/imports
and operational commands. Translate recognized structural conflicts into the existing
safe API error contract; do not leak SQL/constraint internals or misclassify every
integrity exception as the same user error. Roll back failed transactional work.

Complex policy calculations and business decisions such as available entitlement or
approval eligibility remain in application workflows with agreed transaction and
current-authorization safeguards. A check-then-write in application code alone is not
a concurrency guarantee. This split does not prohibit proven database safeguards for
complex invariants, but it does not require a database-resident policy engine.

## Impact and verification

- Scaffold: generate coherent SQLAlchemy models and reviewed Alembic constraints for
  declared scope, required/reference fields and uniqueness. Do not infer all business
  rules or tenant semantics from naming. Applications supply domain-specific metadata.
- Acceptance: constraint enforcement via supported alternate write paths, concurrent
  duplicate creation, cross-NGO reference rejection, valid shared references, rollback
  and safe error mapping under actual restricted runtime roles. RLS tests remain separate.
- Shared UI: reuse existing validation/conflict feedback; no new control required.
- Agent context: record the database structural/application business-rule split.
- Documentation: builder guidance and Leave requirements/tracker synchronized.
- ADR: complements 0003, 0013–0018, 0031 and 0034; accepted originals unchanged.
- Planning only; no schema migration, constraint, ORM model or generator implemented.
