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
