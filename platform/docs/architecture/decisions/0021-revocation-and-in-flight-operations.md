# ADR-0021: Revocation and In-Flight Operations

**Status:** Accepted  
**Date:** 2026-09-21  
**Scope:** Permission revocation ordering across application/service boundaries

## Decision

A short operation already authorized and executing may complete if permission is
revoked after its successful authorization check. Revocation affects subsequent
authorization checks without waiting for logout or token expiry. Do not claim that
revocation atomically cancels transactions already executing in other services.

Opening a form or review does not authorize a later confirmation. Perform current
authorization when the action is confirmed. Work that remains queued, restarts
after a delay or begins another business execution must obtain fresh authorization.
Do not reuse an old positive decision as an indefinite permission grant.

Bound executing operations with timeouts and record authorization and action
information sufficient to explain their ordering in audit. Exact time bounds and
audit fields must be specified before the affected implementation is ready.
A retry of an already committed operation must not re-execute it; access to its
recorded outcome still requires current authorization under
[ADR-0012](./0012-operation-identity-idempotency-and-tracing.md) and
[ADR-0019](./0019-current-server-side-authorization.md).

Authorized service work, such as delivery of a committed notification intent or
scheduled accrual, uses its own bounded service authority under
[ADR-0018](./0018-transaction-scoped-tenant-context.md). It does not inherit a former
user's revoked permission. This distinction does not permit a queued user command
to be relabelled as system work to bypass a required permission check.

This resolves the explicit in-flight ordering question in ADR-0019. It qualifies
'immediate revocation' as immediate effectiveness for subsequent authorization
checks, while allowing a previously authorized short executing operation to finish.

## Consequences

- Scaffold: provide authorization/execution boundaries, timeouts and audit hooks;
  test revocation before confirmation, before queued execution and during execution.
- Shared UI: no new workflow; stale screens confer no permission.
- Agent context: existing authorization rules suffice.
- Documentation: shared scaffold guidance and Leave membership requirements clarify
  the revocation guarantee. Exact timeout values remain an owned delivery task.
- ADR impact: additive resolution of ADR-0019's open question; accepted text unchanged.
- Planning only; no runtime permission or deployment change.
