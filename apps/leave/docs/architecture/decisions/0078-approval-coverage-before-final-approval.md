# ADR-0078: Require Approval Coverage Before Final Leave Approval

**Status:** Accepted  
**Date:** 2026-09-16  
**Scope:** Absence of employees with approval responsibilities

## Decision

Allow submission when an applicant's approval responsibilities lack coverage, but
require eligible temporary coverage throughout the absence before final approval.
Include incoming requests, not just existing pending approvals. An authorized actor
arranges coverage; the applicant does not need assignment permissions. Employees
without approval responsibilities are unaffected by this condition.

An authorized Leave Manager may record a justified exception with a mandatory
reason, including unexpected sickness or emergencies. Keep unresolved coverage
visible. The exception neither creates coverage nor grants approval authority or
waives unrelated approval requirements. Actual absence dates must remain truthful.

Enforce this condition wherever approval would become final, including automatic
completion. This qualifies the automatic finalization in
[ADR-0008](./0008-later-step-acceptance-on-submission.md) and the approval rules in
[ADR-0007](./0007-required-approval-and-automatic-decisions.md); existing automatic
step decisions remain valid but cannot bypass this finalization condition.
It extends [ADR-0076](./0076-approval-cover-and-planned-delegation.md).

## Consequences

- Delivery checks must cover submission with a gap, complete/partial coverage,
  no approval responsibilities, authorized explained exceptions, and automatic completion.
- Exception permission assignment and changes invalidating previously arranged
  coverage require explicit design before implementation.
- Shared-UI/scaffold: use existing review/error patterns; no generic implementation now.
- Agent-context: unchanged.
- Documentation: synchronize specification, tracker, UX, ADR index, and decision log.
- ADR impact: finalization qualification above; accepted historical text is unchanged.
- Planning only; implementation awaits Phase 1 readiness and acceptance tests.
