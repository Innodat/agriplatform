# ADR-0007: Required Approval Steps and Authorized Automatic Decisions

**Status:** Accepted  
**Date:** 2026-09-14  
**Scope:** Leave approvals, on-behalf submission, and balance timing  
**Supersedes:** [ADR-0004](./0004-configurable-approval-workflows.md)

## Context

Product clarification confirms that organisations need different approval counts,
such as one or two, but no policy should bypass approval altogether. Automatic
approval represents an authorized person's decision when they submit a request;
it must not bypass another required approver.

## Decision

Require at least one approval step, configurable per NGO and leave policy. Retain
one-tier and two-tier MVP presets. Remove the independent zero-step policy option.

On valid submission, record the submitting person's own resolved step as approved
when they are authorized to perform it. Self-approval must be explicitly enabled.
An approver submitting on behalf also needs separate on-behalf permission, a
mandatory reason, visible attribution, and conflict checks. Approval authority
alone does not authorize on-behalf submission. Another person's required step must
never be automatically approved through this action.

The application becomes approved and its allocation is consumed exactly once only
when all required steps are satisfied. Otherwise it remains in approval, with the
allocation reserved. Intermediate approval never consumes leave. Automatic
decisions retain individual step outcomes and an audit trail identifying the
employee, submission actor, and authorization basis. Use the existing `approved`
step state for accepted outcomes.

Retain ADR-0004's other decisions: resolve and snapshot ordered step instances on
submission; maintain separate application and step histories; audit explicit
self-approval and configured duplicate-step collapse; reroute explicitly rather
than silently changing in-flight approvers. Approved cancellation requires no new
approval and reverses balances with audit; capacity warnings remain informational.
Optimistic concurrency, idempotency, and authorization/transition tests remain
required.

This Leave-domain decision follows the platform's
[application-silo boundary](../../../../../platform/docs/architecture/decisions/0003-application-silo-architecture.md)
and [ATDD/TDD delivery rule](../../../../../platform/docs/architecture/decisions/0009-atdd-and-tdd-development-loop.md).

## Alternatives considered

- Retain zero-step policies: rejected because no employee self-recording use case
  without approval is required.
- Approve every step when an approver submits on behalf: rejected because this
  bypasses another person's required approval.
- Require a separate approval click for the submitter's own authorized decision:
  rejected in favour of recording that decision on valid submission.

## Consequences and remaining detail

- Functional acceptance examples live in the existing feature specification's
  approval-workflow and balance-reservation sections; no duplicate feature spec
  is introduced.
- Before the affected story passes readiness, resolve how an automatic decision
  for a later step interacts with sequential ordering when an earlier step belongs
  to another person. This does not permit bypassing the earlier approval.
- Scaffold impact: none now; approval rules are Leave-domain behavior.
- Shared-UI impact: none now; no proven domain-neutral component is introduced.
- Agent-context impact: existing authorization and immutable-ADR rules suffice.
- Documentation impact: synchronize the feature specification, confirmed decisions,
  and ADR index. Preserve the original ADR-0004 file unchanged.
- ADR impact: this accepted decision supersedes ADR-0004 with the user's confirmed
  scope and authorization semantics. No platform decision changes.
- Implementation and automated acceptance tests remain gated by Phase 1 readiness.
