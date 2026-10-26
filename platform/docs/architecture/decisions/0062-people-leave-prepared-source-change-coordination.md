# ADR-0062: Prepared People–Leave Source Change Coordination

**Status:** Accepted  
**Date:** 2026-10-23  
**Scope:** Consequential People employment/period/supervisor changes consumed by Leave  
**Complements:** [ADR-0060](./0060-application-owned-pending-supervisor-approval-transfer.md),
[ADR-0040](./0040-shared-employment-core-and-application-settings.md) and
[ADR-0022](./0022-short-transactions-and-external-service-calls.md).

## Decision

Adopt the [People–Leave coordination contract](../contracts/people-leave-change-coordination.md)
as the planning baseline for these protected source changes. People remains the sole writer
of shared employment/period/supervisor facts; Leave owns request assignments/consequences.
All cross-owner access is authenticated HTTP, never another owner's database tables.
This is not a universal distributed workflow or automatic subscription model for other apps.

After reviewed source confirmation, People registers an immutable-input-bound attempt.
Leave prepares the exact affected dependency scope under its short local protection,
rechecking current membership and reviewed consequences, then records a durable gate.
People commits only with the bound preparation and current source revision, recording its
fact/history/outcome/consequence intent and committed attempt atomically. Each owner's
write transaction is short; no external HTTP or human review occurs while its locks are held.

People commit and cancellation compete on the same durable attempt. Cancelled identities
cannot commit later. Leave releases its gate only after authoritative source cancellation
or reconciliation of actual committed consequences; a timeout/TTL never supplies that proof.
Keep separate owner outcomes and original causal identities through response loss/retry.
Do not reverse another owner's committed source fact or rewrite an original success receipt.

Use restricted owner/caller-specific service admission and narrow recovery authority.
Queued work stores causal references rather than credentials. Human source mutation needs
current human authority; recovery cannot impersonate approval or revive an unauthorized
source command. Access disable does not remove required source participation for retained
work or grant users access through the recovery identity.

A People-owned participation barrier protects activation before source writes can bypass
the consumer. Establish that cutover, then install/reconcile source/history/future-boundary
observations before consequential Leave admission. Source writers recheck participation
inside their local commit. Older bypassing writers are not a safe rollback; follow P-0020's
controlled compatibility/maintenance/recovery rules. No customer integration registry,
new app toggle or automatic retirement is introduced.

Current supervisor intent resolves at People commit after preparation; planned dates retain
explicit normalized instant/timezone evidence. Employment periods remain inclusive dates.
Known boundaries invalidate stale observations even if workers lag. Leave ADR-0163's final
protected authority instant remains that consumer's accepted in-flight rule, not a general
post-change grace period. Preserve completed decisions, selected final steps and L-0160
superseded temporary-responsibility precedence.

## Bounds and verification

The owning contract specifies source/review/attempt/preparation fields, state/lock order,
caller policy/transport, activation sequence and initial execution/recovery caps. Numerical
values are selected technical limits to verify, not measured latency/capacity guarantees.
Changes to technical tuning retain the accepted consistency and bounded-recovery rules;
material ownership/security/product changes require an explicit decision.

Actual owner delivery must prove both commit/cancel and source/activation race orders,
old read before preparation, intervening work, wrong caller/scope/input/version, source
response loss, failed/resumed consequence, future boundaries/worker lag, temporary-cover
interaction and disable/re-enable with retained coordination. Verify restricted roles,
immutable evidence, exact per-owner outcome and compatibility. Planning adoption is not
runtime evidence or overall implementation readiness.

## Impacts

Scaffold: reuse/prove restricted HTTP, scoped local transaction, durable causal recovery
and safe error/attribution helpers with actual consumers; no shared coordinator service.
Shared UI: existing source Review/Confirm/Retry and truthful partial outcomes, no new screen.
Agent context: existing owner boundaries, release/transaction/current-authority and immutable
ADR rules suffice; no extra approval convention. Documentation: owning protocol, identity/
admission cross-references, Leave spine/product references and BMAD owner/test mapping.
Accepted predecessors remain unchanged. C5 consumer capability/schema binding and C6 final
coverage/order/sizing/readiness stay open. No credentials, grants, code, tests, migration,
live settings or deployment changed during acceptance.
