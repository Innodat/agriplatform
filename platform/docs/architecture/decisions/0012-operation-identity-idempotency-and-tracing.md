# ADR-0012: Operation Identity, Idempotency and Tracing

**Status:** Accepted  
**Date:** 2026-09-21  
**Scope:** Application commands and cross-service handover

## Decision

Identify a retriable business action with a stable operation ID, distinct from the
resource primary key. Preserve it across retries of that action; a different
action receives a different ID. The owning application records successful operation
identity and outcome atomically with its business changes. A matching retry returns
the recorded outcome without repeating the effects; reuse with different submitted
content is rejected. Resolve uncertain outcomes without creating a new operation.

Operation records belong with each application's business data, not in a central
operation service. Scope duplicate prevention to the authorized tenant/caller and
command contract; an identifier is never authority to act or read an outcome.
Concurrent attempts must not both commit the same operation.

Downstream actions/events have their own stable identifiers. Preserve their link
to the originating operation ID. For example, submission A creates notification
event B; a notification consumer deduplicates acceptance of B, rather than using A
to suppress all notifications caused by that submission. Distinct intended
recipients/channels must not be collapsed into one action.

Trace/correlation identifiers connect diagnostic activity; they are not substitutes
for durable duplicate-prevention keys. Retries may have separate traces or attempt
identifiers while retaining their business operation/event identity and causal links.
This does not promise exactly-once delivery by an external email provider.

Follow the [API boundary](./0001-fastapi-openapi-api-boundary.md),
[application ownership](./0003-application-silo-architecture.md) and
[notification outbox decision](./0006-common-notification-capability.md).
Exact wire fields, retention windows, recovery responses and telemetry propagation
formats remain contract/delivery decisions; they must preserve these invariants.

## Consequences

- Scaffold: prove atomic operation recording, duplicate handling and causal tracing
  in delivery, then promote domain-neutral templates and tests in the same item.
- Shared UI: no new visible reference numbers; recovery behavior follows each
  application's approved experience. No component implementation in this decision.
- Agent context: existing security, transaction and test instructions suffice.
- Documentation: applications reference this contract and define affected commands
  and atomic effects locally. The Leave tracker records adoption and verification.
- ADR impact: additive; accepted records remain unchanged.
- Planning only; no runtime implementation or implementation-readiness approval.
