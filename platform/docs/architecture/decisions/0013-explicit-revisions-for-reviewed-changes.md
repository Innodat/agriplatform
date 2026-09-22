# ADR-0013: Explicit Revisions for Reviewed Changes

**Status:** Accepted  
**Date:** 2026-09-21  
**Scope:** Concurrent edits and confirmation of reviewed application state

## Decision

Use a server-managed integer revision for mutable records subject to reviewed
commands. Start at an initial revision and increment on each relevant committed
change. The application defines the reviewed record or aggregate and which changes
invalidate its review. All write paths affecting that state must maintain the
revision. Timestamps remain descriptive metadata, not concurrency tokens.

A confirmation supplies the resource ID and expected revision alongside its
operation ID. Resource identity selects the target; expected revision identifies
the reviewed state; operation identity makes retries safe under
[ADR-0012](./0012-operation-identity-idempotency-and-tracing.md).

Check the expected revision and apply the change with atomic database protection.
A separate unprotected read/check followed by an update is insufficient. On a
revision conflict, apply no business effects and require review of current details.
Do not silently substitute the new revision and replay the user's confirmation.
Authorization remains mandatory and an already committed matching operation is
handled as a replay, not executed again against a later revision.

A record revision does not establish freshness of related records. Applications
must validate and protect dependent data within their command transaction, including
policy, entitlement or other state that can change independently. No database lock
is held while a user fills in a form or reviews details.

The shared interaction explains that the information changed, preserves user input
where practical, and offers current details for review. Each application determines
which consequences and renewed acknowledgements must be shown. Exact request-field
names and conflict response contracts remain delivery design work.

## Consequences

- Scaffold: promote a proven conditional-update and conflict-response pattern with
  concurrent-write tests when implemented; no generic repository framework now.
- Shared UI: record the conflict interaction in EXPERIENCE; reusable controls follow
  a proven application implementation.
- Agent context: existing transaction, authorization and testing rules suffice.
- Documentation: Leave references this rule and retains domain freshness checks.
- ADR impact: additive; no accepted ADR is edited or superseded.
- Planning only; no runtime change or implementation authorization.
