# ADR-0010: Cancel and Replace Approved Leave

**Status:** Accepted  
**Date:** 2026-09-14  
**Scope:** Approved-request correction and on-behalf authorization

## Context

The functional specification left approved-request amendment open between
cancellation/replacement and a versioned amendment flow. The user selected
cancellation and a new request, with approval again, performed by the employee or
someone permitted to log leave on their behalf.

## Decision

Changing approved dates or duration requires cancellation of the original and
submission of a new linked replacement. Keep the cancelled request and its
approved content, decisions, and balance history intact. Give the replacement a
new identifier and process validation and approval anew; original approvals do not
transfer. The existing authorized automatic-decision rules still apply.

The employee may perform this correction for their own leave. Someone with
on-behalf permission may do so within their authorized employee/resource scope,
with attribution, reason, and conflict checks. Approval authority alone does not
grant on-behalf creation, cancellation, or replacement authority. Organisations
may separately grant both capabilities to the same person, preserving the boundary
in [ADR-0007](./0007-required-approval-and-automatic-decisions.md).

Cancellation needs no additional approval and reverses the original balance effects
exactly once. The replacement has its own reservation and consumption lifecycle.
Retain audited reversal semantics from the
[immutable ledger decision](./0001-immutable-balance-ledger.md). Rejected requests
continue to use [same-request resubmission](./0009-resubmit-rejected-request.md).

## Alternatives considered

- Edit approved content in place or introduce a versioned amendment flow: not the
  selected approach; cancellation/replacement makes renewed approval explicit.
- Give every approver cancellation/replacement rights: unnecessary; separate
  on-behalf permission already provides scoped authority.

## Consequences

- Preserve a navigable relationship between original and replacement requests.
- Functional acceptance examples remain in the existing specification. Implement
  tests after readiness under the platform
  [ATDD/TDD rule](../../../../../platform/docs/architecture/decisions/0009-atdd-and-tdd-development-loop.md).
- Scaffold and shared-UI impact: none now; this is Leave-specific planning.
- Agent-context impact: existing authorization and ADR rules suffice.
- Documentation impact: update lifecycle, permissions, employee workspace, tracker,
  and ADR index.
- ADR impact: additive lifecycle clarification; existing accepted ADRs unchanged.
