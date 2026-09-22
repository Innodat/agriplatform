# ADR-0025: Record Attribution and Audit Provenance

**Status:** Accepted  
**Date:** 2026-09-22  
**Scope:** Project-owned database tables, persistence scaffolding and operational audit

## Decision

Default ordinary mutable business records to `created_at`, `created_by`, `updated_at`
and `updated_by`. Times are server-controlled UTC instants. Actor fields hold stable
identity references, not names or email addresses. Preserve creation attribution;
update last-change attribution only for a persisted change. On creation initialize
last-change attribution to the creation actor/time. Existing explicit integer revisions
remain separate; timestamps are not a substitute for optimistic concurrency versions.

Actors include authenticated people and identified services/jobs. Derive attribution
from verified execution context, not client-supplied audit fields. Record the actual
executing actor; preserve a human initiator separately in the audit when a service
executes their action. Do not impersonate that human for later worker processing.
Identity reference representation must support both people and services; exact schema
is resolved in delivery without creating a second editable person directory. Identity
renaming or deactivation must not destroy attribution or cascade-delete business audit.

Immutable event, audit and calculation-snapshot records need creation attribution,
not update columns implying editability. Model immutability explicitly and enforce it
through allowed write paths. Other table categories, such as disposable projections
or reference/join tables, require an explicit applicability decision rather than blindly
adding human-user columns to every table. Supabase-managed schemas remain outside this
project convention's migration ownership.

The four common fields are a latest-change summary, not an audit trail. Preserve each
consequential action in an immutable audit record, atomically with successful database
effects. Include actor, relevant initiator/executor distinction, target/NGO scope,
action, reason where required, operation identity, timestamp and outcome. Apply existing
sensitive-data access and minimization rules. Failed attempts must not be represented
as committed business changes; their diagnostic/security recording is a separate path.

For operational commands, also record a stable command name and deployed release/Git
commit identifier. Keep source file/line details in diagnostic stack traces when useful,
not as mandatory fields on every business row. A changing line number is not durable
business provenance. Audit identifiers confer no access rights.

## Scaffolding requirements

- Table/model generation must distinguish mutable, immutable and explicitly exempt
  table categories. Default mutable business tables to the four fields above; immutable
  tables to creation fields and append-only behavior.
- Generate owned-schema Alembic migrations and SQLAlchemy persistence support together.
  Keep attribution server-managed; Pydantic create/update contracts must not let callers
  set it. All supported write paths, including workers, support commands and bulk/import
  operations, must supply valid attribution. An ORM convenience hook alone is insufficient
  if other generated write paths bypass it.
- Reuse verified actor/tenant context and transaction ownership. No generic payload dump
  for audit and no unapproved cross-service identity-table dependency.
- Verify preserved creation fields, changed last-update actor/time, service execution with
  human initiation evidence, rejected spoofed attribution, rollback consistency, immutable
  records and supported bulk paths before promoting the pattern.

## Impact

- Shared UI: resolve actor names for display within permissions; no new form fields.
- Agent context: link the convention in repository guidance outside the managed block.
- Documentation: builder guidance and Leave requirements/tracker reference this ADR.
- ADR: complements 0012, 0013, 0014, 0015, 0018, 0023 and 0024; originals unchanged.
- Planning only: the builder is a placeholder; no generator, migration, database table
  or runtime attribution mechanism is implemented by this decision.
