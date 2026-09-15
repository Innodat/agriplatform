# ADR-0009: Edit and Resubmit the Same Rejected Request

**Status:** Accepted  
**Date:** 2026-09-14  
**Scope:** Rejected-request identity and history

## Context

The lifecycle used the label Resubmitted without defining request identity or a
corresponding application status. The user clarified that employees should edit
and resubmit the same rejected request, preserving its history.

## Decision

Keep the request identifier across correction and resubmission. Preserve prior
submitted versions, rejection reasons, approval outcomes, and revision history.
Resubmission re-enters the existing submission flow; it is an action, not a new
application status. Do not create a linked replacement as this correction path.

For the revised content, perform validation and start a fresh approval cycle with
its own workflow snapshot. Prior approval outcomes remain history rather than
authorizing changed content. Apply the existing automatic-decision rules anew.
Keep prior snapshots intact, consistent with
[ADR-0007](./0007-required-approval-and-automatic-decisions.md) and
[ADR-0008](./0008-later-step-acceptance-on-submission.md).

Rejection releases the prior reservation. Valid resubmission reserves the revised
allocation once and uses existing approval/consumption rules, preserving the
[immutable ledger](./0001-immutable-balance-ledger.md). This decision concerns
rejected requests; approved-request amendment remains a separate lifecycle issue.

## Alternatives considered

- Create a new linked replacement for a rejected request: not the selected
  correction flow; the user chose editing and resubmitting the same request.
- Overwrite rejected content and decisions: rejected because history must remain.
- Carry old approvals onto edited content: rejected because they authorize the
  earlier submitted version.

## Consequences

- Request history must distinguish submission cycles and their decisions.
- The existing feature specification contains the acceptance example; executable
  tests follow the platform [ATDD/TDD rule](../../../../../platform/docs/architecture/decisions/0009-atdd-and-tdd-development-loop.md)
  after implementation readiness.
- Scaffold and shared-UI impact: none now; this is Leave-domain planning.
- Agent-context impact: existing history, testing, and ADR rules suffice.
- Documentation impact: align lifecycle wording, delivery decision log, and index.
- ADR impact: additive clarification; accepted ADRs remain unchanged.
