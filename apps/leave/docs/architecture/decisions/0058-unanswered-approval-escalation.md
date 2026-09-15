# ADR-0058: Escalate Unanswered Approvals After Seven Calendar Days

**Status:** Accepted  
**Date:** 2026-09-15  
**Scope:** Notification escalation of required approval work

## Decision

The user approved notifying an authorized Leave Manager after seven calendar days
without action on a required approval, with the threshold configurable per policy.
Keep the current assignment unless an actor with existing rerouting permission
explicitly changes it with a recorded reason. Escalation itself grants no new
authority and changes no approval outcome.

Apply [reminder and actionable-state rules](./0057-approval-reminder-interval.md),
[required approvals](./0007-required-approval-and-automatic-decisions.md), and
[notification privacy](./0015-in-app-notification-privacy.md). Use the platform's
[common notification capability](../../../../../platform/docs/architecture/decisions/0006-common-notification-capability.md).

## Consequences

- The specification records escalation timing, unchanged assignment/outcome, and
  authorized rerouting with a reason for later executable acceptance tests.
- Automatic rerouting or automatic approval is not the selected escalation behavior.
- Scaffold impact: reuse proven notification mechanisms during delivery; no code now.
- Shared-UI impact: configuration and rerouting remain Leave-specific.
- Agent-context impact: existing authorization, audit, and ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: additive escalation rule; accepted ADRs remain unchanged.
- Planning only; Phase 1 readiness and failing acceptance tests precede implementation.
