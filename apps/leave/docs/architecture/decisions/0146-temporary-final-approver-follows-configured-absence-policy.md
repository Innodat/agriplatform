# ADR-0146: Temporary Final Approver Follows the Configured Absence Policy

**Status:** Accepted  
**Date:** 2026-10-21  
**Scope:** Temporary final-approval responsibilities under the optional absence policy  
**Supersedes in part:** [ADR-0080](./0080-directional-absence-approval-policy.md),
only its restriction on inheriting configured step-reduction authority; replaces the
separate appointment-level authorization in the subsequent feature/UX clarification.
**Refines:** [ADR-0079](./0079-temporary-appointment-grants-scoped-authority.md).
Preserves [ADR-0081](./0081-absence-fallback-timing-and-return.md) timing/return and
[ADR-0078](./0078-approval-coverage-before-final-approval.md) coverage safeguards.

## Decision

An authorized temporary final approver takes on the original final approver's scoped
responsibilities, including the absence fallback when enabled in the applicable
workflow policy. Do not require a separate checkbox or additional appointment
responsibility allowing omission of the absent supervisor's step.

When both usual approvers are absent and that policy is enabled, the eligible
temporary final approver may decide alone. When it is disabled, both required steps
still need valid decisions/coverage. The supervisor cannot decide alone merely
because the final approver is absent. This does not enable fallback globally, change
a submitted workflow's snapshotted policy or expand the appointment beyond its
original responsibilities, organization and effective dates.

Evaluate recorded absence when approval is needed, not on the applicant's future
leave dates or from slow response. Record an omitted supervisor step as Not required
under absence policy, retain the policy basis and actual actor, and require at least
one valid approval. Preserve self-approval, current membership/authority, funding,
documents, employee unpaid response and all other independent finalization checks.
Recognize this valid fallback as coverage of the responsibilities it actually handles;
other responsibilities still require cover or an authorized explained exception.

Appointment remains person-first: an authorized manager selects the intended colleague
and Leave validates scope, dates and conflicts. Show the applicable policy consequence
in ordinary appointment review, without an extra opt-in permission choice. Preserve
explicit pending-work transfer, scheduled return, expiry and completed decision history.
No permanent role, unrelated approval power, on-behalf or medical-document access is
granted. Previously recorded decisions/appointments are not silently rewritten.

## Consequences and verification

Verify the both-absent case with enabled/disabled policy; temporary final appointment
without an extra fallback flag; absence timing, scope/date/membership/self-approval
limits; supervisor-only denial; omitted-step evidence; no duplicate substitute for
covered responsibilities; supervisor return and preserved completed decisions; all
independent finalization gates and duplicate-safe request effects. Bind exact policy/
appointment evidence and current-input protection before affected readiness. Runtime
integration belongs to the owning submission/decision/transfer consumers.

Scaffold/shared UI: use existing person/date/review patterns; remove the redundant
appointment option from affected examples, not the workflow policy's optional setting.
Leave owns authority/coverage semantics. Agent context: existing immutable-ADR and
current-authority instructions suffice. Documentation: synchronize features, spine,
UX/examples, E5 stories/FLOW coverage, tracker, handoff and ADR index. Accepted
predecessors remain unchanged. No application code, migrations, active grants,
deployment, runtime test evidence or implementation/readiness authorization.
