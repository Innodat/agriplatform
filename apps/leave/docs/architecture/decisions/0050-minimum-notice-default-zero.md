# ADR-0050: Minimum Notice Defaults to Zero Calendar Days

**Status:** Accepted  
**Date:** 2026-09-15  
**Scope:** Minimum notice and short-notice submission

## Context

The user approved configurable minimum notice in calendar days, with shorter-notice
requests permitted when explained and flagged for the approver. They explicitly
selected zero as the default.

## Decision

Each policy sets minimum notice in calendar days, default zero. Permit otherwise
eligible shorter-notice requests with a mandatory employee explanation and a clear
flag for assigned approvers. Do not require an explanation solely for minimum
notice on an otherwise eligible same-day request under the zero-day default.

Other eligibility and approval rules still apply. Zero minimum notice does not
authorize backdating, which remains a separate policy rule. Preserve
[versioned policies](./0002-versioned-leave-policies.md),
[required approvals](./0007-required-approval-and-automatic-decisions.md), and
[employee work timezone](./0023-employee-work-timezone.md) date handling. The
platform's [API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md)
continues to apply.

## Alternatives considered

- Default to a positive notice period: the user explicitly selected zero.
- Block every short-notice request: rejected; accept explained requests for review.
- Treat zero notice as permission for backdating: not part of this decision.

## Consequences

- The specification includes seven-day policy/three-day submission, missing-reason
  denial, and zero-default same-day acceptance examples for later executable tests.
- Scaffold impact: no scaffold change — application-specific notice policy.
- Shared-UI impact: none now; notice explanations belong in Leave.
- Agent-context impact: existing authorization, audit, and ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: additive notice decision; accepted ADRs remain unchanged.
- Planning only; Phase 1 readiness and failing acceptance tests precede implementation.
