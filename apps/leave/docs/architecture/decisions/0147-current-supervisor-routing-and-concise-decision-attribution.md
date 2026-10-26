# ADR-0147: Current Supervisor Routing and Concise Decision Attribution

**Status:** Accepted  
**Date:** 2026-10-21  
**Scope:** Unfinished supervisor steps and approval history  
**Supersedes in part:** [ADR-0004](./0004-configurable-approval-workflows.md) as retained
by [ADR-0007](./0007-required-approval-and-automatic-decisions.md), and
[ADR-0076](./0076-approval-cover-and-planned-delegation.md), only the requirement for a
separate manual transfer of unfinished steps after a permanent supervisor change.
**Platform authority:** [ADR-0060](../../../../../platform/docs/architecture/decisions/0060-application-owned-pending-supervisor-approval-transfer.md).

## Decision

When an authorized supervisor change takes effect, unfinished supervisor-based steps
follow the new eligible supervisor. The change review explains this effect; no separate
transfer selection/confirmation workflow is required for this case. People owns the
relationship; Leave applies and verifies its approval consequences under P-0060.

Check current membership, explicit approval authority, self-approval and request scope.
The relationship itself grants none. Preserve all completed decisions, independently
selected final steps, required-step structure, policy/calculation evidence and normal
finalization gates. Missing/ineligible/unverifiable new authority leaves work pending
with appropriate setup/attention, never skipped or automatically approved. Prevent the
old supervisor from deciding solely through a superseded relationship after the
effective change; concrete observation and in-flight bounds remain contract gates.

Use the existing activity/audit mechanism for the change (actor, prior/new supervisor,
affected scope, effective/recorded time and actual outcome). Decisions record actual
actor, outcome, time/comment and relevant authority basis; temporary decisions identify
the original approver they acted for. No duplicate reassignment history, dedicated log
table, or elaborate workflow snapshot engine is required just to explain this change.
Keep local request/step state, revisions and compact retry/outcome evidence needed to
implement safe routing. Do not erase consequential audit or immutable decisions.

This does not authorize arbitrary directory changes to rewrite workflows. Temporary
appointments, selected pending-work inclusion and authorized return retain their own
rules; changing independently configured final approvers remains separate. Resolve
permanent change during active temporary cover, return targets, concurrent decisions,
due work and eligibility before affected readiness without implicit authority extension.

## Impacts and verification

Verify effective transfer, disclosure, current scoped eligibility, completed/final-step
preservation, notification intent to the newly responsible approver, safe failed/partial
owner coordination, concurrent decisions and duplicate/out-of-order retries. Attribute
temporary decisions directly rather than requiring inference from unrelated timelines.
Bind exact current-assignee/authority and consistency contracts before implementation.

Update features, spine, shared/Leave UX, affected E2/E5 stories/coverage, tracker and
handoff. Reuse existing activity/review/client patterns; no new history system. Agent
context references P-0060; accepted predecessors unchanged. No code, tests, migration,
runtime grants, deployment or implementation/readiness authorization.
