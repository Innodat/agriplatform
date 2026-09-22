# ADR-0020: Safe Schema Changes and Release Recovery

**Status:** Accepted  
**Date:** 2026-09-21  
**Scope:** Mandatory platform-wide release principle for all applications and shared services

## Decision

Treat safe schema evolution and recoverable deployment as release requirements.
Apply this principle to every application and shared service, including generated
applications. It is not an optional Leave-specific convention.

Run required migrations through one controlled deployment step before activating
the new API and worker versions. Prevent competing migration executions against
the same database. Individual API/worker startup must not run migrations. Retain
owner-specific histories and dependency ordering under
[ADR-0016](./0016-owned-migration-histories-and-coordination.md), using deployment-only
migration authority under [ADR-0017](./0017-runtime-and-migration-database-authority.md).

If a required migration fails, stop release activation and dependent migration
steps. Report which owner/revision steps succeeded, failed or were not attempted.
Reconcile any uncertain outcome against actual database state before resuming.
Do not assume that a multi-owner release is atomic, or that a failed migration
necessarily left no effects. Do not automatically reverse already-applied migrations:
reversal can destroy data and may not restore the previous application contract.

Ordinary releases preserve compatibility with the previous running application
version, including API and worker behavior. Use staged expansion, data transition
and later cleanup where needed: add replacement structures, deploy compatible
code, migrate/verify data, and remove obsolete structures only after older
consumers no longer require them. Coordinate dependent shared-service releases too.

Keeping or restoring the previous application version is a recovery option only
when compatibility with the actual database state has been verified. Prefer an
explicit corrective migration where appropriate. Changes that cannot preserve
compatibility require a planned maintenance window, affected-consumer coordination
and a documented recovery procedure before execution.

## Required delivery evidence

Integrate these requirements into the existing BMAD delivery/release gates:

- Identify schema changes, affected consumers and supported previous-version behavior.
- Test the migration on a disposable database and representative supported prior
  schema/data; verify both upgrade correctness and claimed compatibility.
- Demonstrate migration coordination, activation blocking on failure, and accurate
  progress/outcome reporting in shared release-tooling tests.
- Document the recovery action and data implications. Validate backup/restoration
  arrangements for changes whose recovery relies on them; a backup alone is not
  evidence of a tested recovery procedure.
- For incompatible changes, record the maintenance and recovery plan explicitly.

Exact orchestration technology, lock implementation and operational time targets
remain implementation decisions. None weaken these release requirements.

## Consequences

- Scaffold: include migration/release configuration and verification hooks; prove
  shared tooling before promotion. Do not generate startup auto-migration behavior.
- Shared UI: no new product screen; maintenance communication is operational work.
- Agent context: root AGENTS.md links this mandatory principle outside its managed block.
- Documentation: builder guidance and Leave release tracker reference this decision.
- ADR impact: additive refinement of ADR-0015/0016/0017; accepted records unchanged.
- Planning only; automation remains to be implemented and tested. No deployment,
  schema mutation or production-readiness claim is made by recording this decision.
