# ADR-0086: Archive Markers and Effective-Dated Versions

**Status:** Accepted  
**Date:** 2026-09-20  
**Scope:** Leave configuration lifecycle and historical interpretation

## Decision

Use an archive timestamp such as `archived_at` on a stable configuration record to
retire it from new use while preserving references. Archiving does not replace
version history. Use effective-dated versions for calculation-relevant settings,
including work profiles, policies and entitlement rules. Retain submitted request
version references and calculation snapshots, and audit who changed what and why.

For example, Maputo office remains the same profile while Friday changes from
8 to 7 hours effective 1 October. Preserve the earlier version for September and
the scheduled version before October. Later archiving retires the profile without
erasing either version or the requests that reference them.

Do not create a duplicate history table for every table by default. Ordinary
records may use audit history where sufficient; past calculation rules must not
need reconstruction from an audit log. Exact table names, keys and the versioning
mechanism remain architecture work rather than implied by this illustration.

This extends [policy versioning](./0002-versioned-leave-policies.md), retaining
[immutable balance history](./0001-immutable-balance-ledger.md) and
[schedule calculation snapshots](./0003-working-time-in-minutes.md). Access continues
through the [platform API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md).

## Consequences

- Profile archiving remains blocked while current/scheduled assignments depend on
  it or it remains the NGO default. Preserve historical assignments and snapshots.
- Scaffold/shared-UI impact: no generated code or shared history abstraction now.
- Documentation impact: synchronize requirements, tracker and UX decision record.
- Agent-context impact: existing historical-integrity and architecture rules suffice.
- ADR impact: additive clarification; accepted ADR text remains unchanged.
- Planning only; no schema migration, runtime change or implementation authorization.
