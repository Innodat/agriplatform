# ADR-0019: Current Server-Side Authorization

**Status:** Accepted  
**Date:** 2026-09-21  
**Scope:** Protected application requests and shared access capability

## Decision

Validate authentication tokens to establish identity. Embedded role claims alone
must not authorize a protected action. Each protected request checks current NGO
membership and permissions through the shared access capability using the agreed
[service boundary](./0003-application-silo-architecture.md). Applications additionally
enforce current resource and domain constraints, such as assigned approver status.

An open page or active login does not preserve revoked authority. Recheck on the
protected request, including confirmation of a previously opened review and access
to prior operation outcomes. Suspended or ended memberships must not require sign-out
or token expiry before subsequent protected requests are denied.

Initially do not cache positive permission decisions across requests in a way that
could continue granting revoked access. Later caching requires an explicit validity
and invalidation design. If current access cannot be verified, fail closed and
return an actionable retryable service-unavailable outcome. Distinguish unavailable
verification from a confirmed authorization denial. Do not fall back to old grants.

Follow [permission definitions](./0011-application-roles-and-business-permissions.md)
and [verified transaction context](./0018-transaction-scoped-tenant-context.md).
A per-request authorization check alone does not atomically coordinate a remote
revocation with an already executing transaction. The precise ordering of revocation
and in-flight commits remains an explicit architecture decision; no stronger
cross-service atomicity guarantee is implied here.

## Consequences

- Scaffold: prove shared access-client/dependency conventions and error handling;
  test revoked membership, changed permissions and access-service outages.
- Shared UI: stale controls grant no authority; distinguish permission loss from
  temporary verification failure and preserve entered data where appropriate.
- Agent context: existing authorization and tenant-isolation rules suffice.
- Documentation: builder and Leave plan reference this convention.
- ADR impact: additive; accepted records unchanged.
- Planning only; no shared access service or runtime checks implemented.
