# API errors and operation recovery — E1 contract proposal

**Status:** Bounded recovery behavior approved; detailed wire compatibility and implementation evidence pending  
**Date:** 2026-09-24  
**Owners:** Platform API owner and first consuming application lead

Implements [ADR-0012](../decisions/0012-operation-identity-idempotency-and-tracing.md)
and [ADR-0031](../decisions/0031-machine-readable-api-errors-and-localized-presentation.md).
This defines a reusable contract proposal, not a central operation service. Each
application stores its own outcomes atomically with its business mutations.

## Error envelope

Retain `error` as a safe fallback message and `code` as an optional integer. Add
`error_id` as the stable string discriminator required on responses from the new
contract. Keep `details` optional, with an allowlisted typed schema for each identifier.
Optional `operation_id` identifies the caller's attempted operation, not proof of
its success. Optional `trace_id` is a safe diagnostic reference, never authority.

Example (identifiers and exact HTTP mapping are proposed):

```json
{
  "error": "This draft changed elsewhere. Your latest changes haven’t been saved.",
  "error_id": "leave.draft_revision_conflict",
  "details": { "current_revision": 8 }
}
```

Do not replace an existing numeric code with text, assign new meanings to existing
codes or parse the fallback message. New clients recognize the discriminator and
localize presentation. Unknown/missing identifiers use HTTP-aware generic handling,
retain recoverable input and never infer mutation success. Old endpoints remain
compatible during explicit adoption; adding fields must be tested against strict
old clients rather than assumed compatible. Authentication/validation/unhandled-error
adapters and declared OpenAPI response schemas must use the same contract.

## Common outcomes

| HTTP | Proposed `error_id` | Required behavior |
| --- | --- | --- |
| 401 | `authentication_required` | Renew authentication or sign in; preserve only supported same-user recovery context. Recheck authority before retrying the original operation. |
| 403 | `access_denied` | Explain confirmed loss/lack of authority without protected record details; no stale-grant fallback. |
| 404 | `resource_not_found` | Missing or inaccessible resource under the endpoint's disclosure policy; do not reveal cross-organization existence. |
| 409 | `operation_payload_mismatch` | The operation ID was reused with different canonical input; do not repeat or silently issue a new action. |
| 409 | `operation_busy` | A matching action is still being resolved; retain its operation ID and perform bounded recovery. A response alone does not prove whether another attempt will commit. |
| 422 | `validation_failed` | Safe field paths and validation identifiers; preserve input and explain correction. Never include raw validation input, exception context or secret values. |
| 503 | `authorization_unavailable` | Authority could not be checked; distinguish from denial and offer retry, not cached authorization. |
| 503 | `dependency_unavailable` | Required dependency unavailable; preserve input. For a mutation with an uncertain outcome, resolve the original operation rather than generating a new one. |
| 500 | `internal_error` | Safe generic explanation/trace reference. A failed response is not evidence that a mutation failed to commit. |

If rate limiting is introduced, use HTTP 429 and the common envelope; its thresholds
and retry timing need a separate concrete contract. Do not convert authentication,
authorization or validation errors into generic server errors. Preserve necessary
protocol headers such as authentication challenges and bounded retry guidance.

## Committed outcome receipt

Propose a typed success/recovery representation with:

- `operation_id`: original UUID, scoped to authenticated caller, organization and command.
- `status`: `committed`.
- `result`: command-specific compact acknowledgement, e.g. draft ID and committed revision.

No `replayed` flag is needed for correctness; repeats report the same committed
acknowledgement. Current resource state is read separately and may have changed.
The operation receipt must not duplicate sensitive draft payloads for recovery.
Only return an acknowledgement after both business change and receipt commit.

Propose an authenticated application-local outcome lookup with selected organization
context. The route and HTTP schemas must be included in the consuming OpenAPI contract.
A known, authorized committed receipt returns HTTP 200 with the representation above.
A lookup with no visible receipt returns HTTP 200 and `status: unresolved`, without
claiming that the command failed or that no other attempt is executing. Unrelated
callers cannot enumerate whether receipts exist. Current authorization denial or
unavailability uses the corresponding HTTP error instead of a success status.

`unresolved` permits bounded retry of the identical operation/payload with backend
concurrency protection. It does not permit an automatic fresh operation, advancing
an expected revision, or silently converting a closed draft into a new one. Timeout,
disconnect, unparsable response and unexpected server error use this same uncertainty
path. Avoid an unbounded polling loop; after the agreed recovery budget, leave a
truthful unresolved state with a user-triggered retry. Exact budgets remain required
before story readiness.

User agreement, 2026-09-24: attempt brief, bounded automatic recovery for uncertain
saves, then show a truthful not-yet-confirmed state with Retry rather than an endless
spinner. Retry retains the original operation identity/payload. New edits may remain
local, but no subsequent save is sent until that operation is resolved. A known
validation error, access denial or revision/lifecycle conflict takes its own recovery
path and must not enter an automatic network retry loop. This approval does not
select time budgets or claim an implementation test has passed.

## Compatibility evidence and impacts

The inspected backend and builder template currently emit `error`, optional numeric
`code` and untyped `details`; their validation adapters expose `exc.errors()` directly.
Do not copy that raw validation structure into this new contract: explicitly select
safe paths/identifiers rather than potentially echoed input. Retain documented legacy
responses until their compatibility transition is verified.

Required fixtures cover old numeric-code responses, new known identifiers, unknown
identifiers, framework errors, unavailable versus denied access, localized text changes,
safe detail filtering, commit-then-lost-response, duplicate concurrency, unresolved
lookup and permission loss before recovery. Generate or validate TypeScript contracts
from Pydantic/OpenAPI. Exact commands/results accompany the implementation item.

Scaffold: update owning templates/generator, exception adapters, generated types and
disposable-sample tests together once proven. Shared UI: common recovery/error handling,
with application-owned wording and domain transitions. Agent context: existing ADR-0031
guidance suffices. Documentation: owning contract and first-consumer mapping. ADR:
no accepted decision changed. No code, tests or migration implemented by this proposal.
