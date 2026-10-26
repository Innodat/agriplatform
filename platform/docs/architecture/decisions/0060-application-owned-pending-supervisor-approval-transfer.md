# ADR-0060: Application-Owned Pending Supervisor Approval Transfer

**Status:** Accepted  
**Date:** 2026-10-21  
**Scope:** Shared supervisor changes and Leave pending approval ownership  
**Supersedes in part:** [ADR-0041](./0041-shared-supervisor-department-and-location.md),
only its requirement that Leave supervisor changes affect new routes alone and that
outstanding supervisor steps require a separately initiated transfer.

## Decision

An application may make transfer of unfinished supervisor-based approvals a disclosed
consequence of an authorized supervisor change. Leave adopts this behavior under
[Leave ADR-0147](../../../../apps/leave/docs/architecture/decisions/0147-current-supervisor-routing-and-concise-decision-attribution.md).
People retains supervisor facts, effective dates and history; Leave owns assignment
changes, current approval eligibility, request revisions and decision evidence.

When the relationship change takes effect, Leave moves applicable unfinished supervisor
steps to the eligible replacement. The change review explains this consequence without
requiring a separate user transfer workflow. Preserve completed decisions, independently
selected final approvers, workflow policy and calculation history. Relationship assignment
alone grants no approval permission. An unavailable/ineligible replacement cannot act;
retain pending work and authorized setup/attention rather than skipping or approving it.

Use existing owner activity/audit and operation mechanisms, not duplicate reassignment
logs or a new audit service. Record the source change and actual coordinated outcome;
each decision identifies its actual actor and, for temporary authority, whom they acted
for. Required local consequential evidence remains atomic with its owning mutation.

Do not combine owner databases or wait on remote services under business locks. Bind
effective-change observation, authorized application consequence, bounded propagation,
stale-actor prevention, operation/version identities, race/retry reconciliation, active
temporary-cover interactions and truthful partial outcomes before affected readiness.
No new role, implicit privilege, universal workflow engine or automatic migration.

## Impacts and verification

Verify reviewed supervisor changes, effective boundaries, eligible/denied replacement,
concurrent old/new decisions, repeated/out-of-order delivery, preserved completed/final
steps, source/outcome activity links and actual decision attribution. Prove behavior
across real owner contracts before activation; a source relationship save alone cannot
claim Leave transfer completion. Scaffold/shared UI reuse scoped change/review/outcome/
audit patterns proven by the consumer. Update shared UX, Leave authority/planning and
agent references; accepted predecessors remain immutable. No implementation or readiness
authorization, runtime tests, migrations, grants or deployment.
