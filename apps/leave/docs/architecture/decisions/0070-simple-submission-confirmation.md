# ADR-0070: Simple Submission Confirmation with Reliable Recovery

**Status:** Accepted  
**Date:** 2026-09-15  
**Scope:** Employee post-submission experience

## Context and decision

The user approved a simplified confirmation after questioning the benefit of a
prominent reference number and next-approver name. After success, open request
details with Request submitted, leave dates, and current status. Keep a stable
internal identifier, but do not prominently display it or the next actor's name
in the confirmation. Approval history remains available on demand.

Use Awaiting approval when another actor must act. Clearly prompt the employee
when their own action is needed, including unpaid-amount acknowledgement. Show
Approved immediately when authorized automatic decisions complete approval.
The existing reminders and escalation support routine progress; contacting a
supervisor for urgency is not a prerequisite for processing.

If submission outcome is uncertain after a connection failure, check whether it
succeeded before offering retry. Recovery must not duplicate requests or reservations.
Apply [approval rules](./0007-required-approval-and-automatic-decisions.md),
[approval-history access](./0018-approval-history-visibility.md),
[acknowledgement rules](./0032-protected-reservations-and-explained-changes.md), and
[idempotent ledger protections](./0001-immutable-balance-ledger.md).
The platform's [API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md)
continues to apply.

## Alternatives considered

- Prominent reference number and next-approver identity: the user selected a simpler
  default while retaining internal identifiers and accessible history.
- Require direct employee follow-up for routine progress: not the selected workflow.

## Consequences

- The specification includes pending/immediate approval, required employee action,
  and lost-response recovery examples for later acceptance tests.
- Pre-submission summary requirements remain as recorded in ADR-0069; this decision
  changes the post-submission presentation, not historical attribution or permissions.
- Scaffold impact: promote proven generic retry/recovery mechanisms during delivery;
  no implementation now.
- Shared-UI impact: generic feedback components may be shared; Leave statuses and
  required-action semantics stay application-owned.
- Agent-context impact: existing authorization, idempotency, and ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: additive confirmation decision; accepted ADRs remain unchanged.
- Planning only; Phase 1 readiness precedes implementation.
