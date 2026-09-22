# ADR-0114: Owned Outbox Worker Without an MVP Workflow Engine

**Status:** Accepted  
**Date:** 2026-09-22  
**Scope:** Leave MVP delivery and future orchestration boundary

## Decision

Use a PostgreSQL transactional outbox and a separate Leave-owned worker process for
MVP outbound delivery. The Leave API writes business changes and outbound intent
atomically. Its worker reads and updates handover state, delivering to the shared
notification service over HTTP. One owning application controls the outbox; other
services must not access Leave tables. Start with one worker instance without relying
on singleton deployment for correctness.

Use short durable claims, release the claim transaction before remote calls, and
recover abandoned work after claim expiry. Only the current claim holder may finalize
its attempt. Reuse stable event identity across retries, including a crash after remote
acceptance but before local acknowledgement. The receiving service must durably accept
and deduplicate the handover. A completed handover is not proof of final email delivery.
Existing notification capability owns subsequent channel delivery and its status.

Keep the worker limited to claiming, handing over, retrying and reporting delivery
state. Do not build a generic orchestration engine. Leave approval remains explicit
application state with durable reminders. Neither a message broker nor Temporal is
required for MVP. Retain stable operation/event identities, versioned payloads,
idempotent APIs and causal trace links.

Reconsider broker/pub-sub for independent multi-consumer delivery, and Temporal or
another durable workflow engine for a committed multi-service process with ordered
steps, waits and recovery/compensation. Travel booking and future AI investigation,
approval and PR creation are candidates, not selected implementations. A future worker
may publish to a broker or start a workflow; this requires integration work and does
not eliminate the local database-to-external-handover atomicity problem.

## Impact and verification

- Acceptance: API rollback leaves no outbound intent; worker restart recovers claims;
  overlap/retries do not duplicate receiver effects; stale claim completion is rejected;
  remote acceptance before local crash is recoverable; no remote call holds domain locks.
- Scaffold: prove generic outbox mechanics in delivery before template promotion;
  payloads and business routing stay application-owned.
- Shared UI: no new administrator control or workflow-engine UI.
- Agent context: existing silo, transaction and idempotency rules suffice.
- Documentation: requirements and tracker synchronized; future engines remain deferred.
- ADR: inherits platform 0006, 0012 and 0022; no accepted predecessor changed.
- Planning only; no worker, broker, workflow engine or schema implemented.

## References

- [Platform notification capability](../../../../../platform/docs/architecture/decisions/0006-common-notification-capability.md)
- [Platform operation identities](../../../../../platform/docs/architecture/decisions/0012-operation-identity-idempotency-and-tracing.md)
- [Platform short transactions](../../../../../platform/docs/architecture/decisions/0022-short-transactions-and-external-service-calls.md)
