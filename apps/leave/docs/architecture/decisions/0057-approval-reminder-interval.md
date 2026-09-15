# ADR-0057: Approval Reminders Default to Three Calendar Days

**Status:** Accepted  
**Date:** 2026-09-15  
**Scope:** Reminders for required approval actions

## Context

The user approved a configurable reminder interval per policy, defaulting to three
calendar days, targeting only currently required approvers and stopping when their
action is completed or the request is withdrawn or cancelled.

## Decision

Use a per-policy approval-reminder interval with a three-calendar-day default.
Remind only approvers whose action is currently required. Stop reminders for an
action after the approver acts and stop request reminders on withdrawal or
cancellation. Reminders never automatically approve, reject, or reroute requests.

Respect [required approval state](./0007-required-approval-and-automatic-decisions.md),
[already-recorded later-step decisions](./0008-later-step-acceptance-on-submission.md),
[email privacy](./0014-email-notification-privacy.md), and
[in-app privacy](./0015-in-app-notification-privacy.md). Use the platform's
[common asynchronous notification capability](../../../../../platform/docs/architecture/decisions/0006-common-notification-capability.md)
with current recipient authorization checks.

## Alternatives considered

- Notify every resolved workflow approver regardless of actionable state: rejected.
- Automatically change decisions or routing after a reminder: not authorized.

## Consequences

- The specification includes a default three-day reminder, non-actionable recipient
  exclusions, stopping behavior, and absence of decision/routing side effects.
- Delivery retries must not duplicate the same reminder occurrence; workflow state
  must be checked so obsolete approval reminders are suppressed.
- Scaffold impact: integrate reusable scheduling/delivery mechanisms when proven;
  no implementation is introduced now.
- Shared-UI impact: reminder policy configuration stays in Leave; shared display
  continues to follow the notification contract.
- Agent-context impact: existing authorization and ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: additive reminder policy; accepted ADRs remain unchanged.
- Planning only; Phase 1 readiness and failing acceptance tests precede implementation.
