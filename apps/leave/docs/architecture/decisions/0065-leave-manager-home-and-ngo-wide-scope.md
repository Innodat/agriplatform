# ADR-0065: Leave Manager Home and NGO-Wide MVP Scope

**Status:** Accepted  
**Date:** 2026-09-15  
**Scope:** Leave Manager landing experience and employee scope

## Context

The user approved the proposed Leave Manager home screen and the simpler MVP
scope of NGO-wide access, retaining separate action permissions.

## Decision

For MVP, Leave Manager employee scope covers the whole NGO where the actor holds
that role. Defer department/location restrictions on this role. NGO-wide scope
does not grant access to another NGO or automatically add action permissions.

Prioritize these items on the Leave Manager home screen:

- Escalated approvals and balance deficits needing review.
- Requests affected by employment or policy changes.
- Authorized corrections and on-behalf actions.
- An organization leave overview in the active NGO.
- Shortcuts to policies, schedules, entitlements, reports, and audit history.

Keep approval, on-behalf correction, balance-adjustment, and sensitive-document
permissions separate. Being a Leave Manager does not automatically make someone
an approver. Apply [field visibility](./0013-leave-manager-field-visibility.md),
[document metadata rules](./0017-leave-manager-medical-document-metadata.md),
[deficit review permissions](./0039-cancellation-deficit-review.md), and
[correction authority](./0053-administrative-correction-authority.md). References
to employee scope in these records resolve to NGO-wide scope for MVP Leave Managers;
their separate action checks remain intact. Other roles' assigned scopes are unchanged.

Use the platform's [API authorization boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md).

## Alternatives considered

- Department/location-restricted Leave Managers in MVP: deferred in favor of
  NGO-wide scope.
- Give every Leave Manager all approval and document powers: rejected; retain
  separate action permissions.

## Consequences

- The specification includes cross-department overview, cross-NGO denial, and
  missing-action-permission examples for later executable acceptance tests.
- Scaffold impact: no implementation now; promote proven generic layout patterns
  during delivery when appropriate.
- Shared-UI impact: generic layout/queue primitives may be shared; administrative
  Leave queues, permissions, and overview content remain application-specific.
- Agent-context impact: existing authorization, audit, and ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog;
  elaborate responsive layouts during UX planning.
- ADR impact: additive scope clarification and home layout; accepted ADRs unchanged.
- Planning only; Phase 1 readiness precedes implementation.
