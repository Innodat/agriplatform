# ADR-0011: Application Roles Backed by Business Permissions

**Status:** Accepted  
**Date:** 2026-09-16  
**Scope:** Application role definitions and advanced customization

## Decision

Applications provide maintained default roles backed by explicit permissions for
meaningful business capabilities. Clients can use these roles without configuring
individual permissions. Avoid making every UI button its own permission.

Allow advanced custom roles, starting from copies of application-defined roles.
Application role definitions remain application-maintained; changes to a custom
role are explicit. Newly introduced permissions require review before addition to
custom roles and must not silently broaden their access. Do not use future-matching
wildcards as a substitute for reviewed grants.

Developers or business analysts may design role definitions; production access
changes require an authorized actor. Evaluate permissions against current tenant
membership, resource scope, and domain constraints, not just role names. This does
not grant administrators blanket business-data access or change separate sensitive
document controls.

Follow [API authorization boundaries](./0001-fastapi-openapi-api-boundary.md) and
[silo boundaries](./0003-application-silo-architecture.md). The exact administration
interface, default-role upgrade handling, and migration contracts remain delivery
design work.

## Consequences

- Scaffold: plan role/permission catalogs and examples when the owning implementation exists.
- Shared UI: reusable role-selection and advanced capability controls may be promoted when proven.
- Agent context: existing authorization and architecture rules suffice.
- Documentation: shared UX, application requirements, and delivery tracker reference this decision.
- ADR impact: additive; no accepted ADR superseded.
- No runtime or role grants are changed by this planning decision.
