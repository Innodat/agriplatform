# ADR-0008: Record Later-Step Acceptance on Submission

**Status:** Accepted  
**Date:** 2026-09-14  
**Scope:** Automatic approval ordering  
**Supersedes:** [ADR-0007](./0007-required-approval-and-automatic-decisions.md),
solely its unresolved later-step ordering; all other decisions remain in force.

## Context

ADR-0007 left open whether the second approver submitting on behalf must wait for
the first before their own acceptance is recorded. The user confirmed immediate
acceptance by the submitting second approver, followed by waiting for the first.

## Decision

On valid, authorized on-behalf submission, immediately record the submitting
approver's own step as approved even if it is later than an outstanding step.
Keep the application in approval and leave reserved until every required step is
satisfied. Do not require the submitting approver to repeat their decision.

Final approval means completion of the last outstanding required approval, not
necessarily the highest-numbered step. At that point, approve the application and
convert its reservation to consumption exactly once. Rejection of an outstanding
step rejects the application and releases the reservation under the existing
lifecycle rule; earlier acceptance remains in audit history.

Retain ADR-0007's required approval count, permission boundaries, attribution,
conflict checks, workflow snapshots, and all other retained decisions. This is
an exception for authorized automatic decisions on submission, not general
permission to bypass workflow ordering or another person's required approval.

## Alternatives considered

- Require the second approver to approve again after the first: rejected because
  their authorized submission already expresses acceptance.
- Complete the whole application on the second approver's submission: rejected
  because the first approval is still required.

## Consequences

- Step acceptance order may differ from configured workflow order; application
  completion must check all required steps.
- Acceptance examples are recorded in the existing feature specification, with
  consumption and rejection cases to implement after readiness under the platform
  [ATDD/TDD rule](../../../../../platform/docs/architecture/decisions/0009-atdd-and-tdd-development-loop.md).
- Scaffold and shared-UI impact: none; this is Leave-specific planning.
- Agent-context impact: existing rules suffice.
- Documentation impact: update the feature specification, delivery decision log,
  and ADR index. Preserve accepted ADR-0007 unchanged.
- ADR impact: resolves only ADR-0007's ordering question; no platform ADR changes.
