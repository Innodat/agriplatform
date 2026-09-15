# ADR-0054: Notify Employees of Administrative Corrections

**Status:** Accepted  
**Date:** 2026-09-15  
**Scope:** Correction notification and acknowledgement

## Decision

The user approved email and in-app notification whenever an administrator corrects
an employee's request. Link to authorized before/after details, reason, and actor.
Keep payloads within [email privacy](./0014-email-notification-privacy.md) and
[in-app privacy](./0015-in-app-notification-privacy.md) limits. Require acknowledgement
only for an increased requested unpaid amount under
[ADR-0032](./0032-protected-reservations-and-explained-changes.md); other corrections
remain visible without requiring a response.

Use the platform's [common notification capability](../../../../../platform/docs/architecture/decisions/0006-common-notification-capability.md):
Leave owns the event, authorized recipients, and permitted context. Delivery is
asynchronous and failure does not undo a successful correction.

## Consequences

- The specification includes both notification channels, authorized detail access,
  minimal payloads, and conditional acknowledgement as acceptance expectations.
- Scaffold impact: no implementation now; update shared notification client/outbox
  templates when proven during delivery.
- Shared-UI impact: generic notification display is a candidate for shared UI;
  correction detail and acknowledgement remain Leave-specific.
- Agent-context impact: existing authorization, audit, and ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: additive notification rule; accepted ADRs remain unchanged.
- Planning only; Phase 1 readiness still precedes implementation.
