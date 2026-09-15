# ADR-0011: Colleagues See Availability Without Leave Details

**Status:** Accepted  
**Date:** 2026-09-14  
**Scope:** Ordinary colleague visibility

## Context

The user selected “Unavailable” for every leave type in ordinary colleague views,
rather than revealing ordinary types and hiding only sensitive ones.

## Decision

For ordinary colleagues, label every leave absence Unavailable. Permit the employee
identity and absence interval where absence viewing is authorized, but hide leave
type, reason/note, approval comments, and attachment metadata. Apply this boundary
to shared calendars, dashboards, notifications, exports, and their API responses.
Do not allow filtering, grouping, colours, icons, or tooltips to disclose the hidden
type. UI-only hiding is insufficient.

The request owner retains their own permitted details. Access to an absence view
does not itself grant detailed request access. Approver and administrative field
visibility remain to be defined explicitly. Document authorization remains separate
under [ADR-0006](./0006-sensitive-attachment-access.md), following the platform's
[FastAPI boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md).

## Alternatives considered

- Show ordinary leave types and hide only sensitive ones: not the user's selected
  privacy rule.
- Hide labels while allowing type filters or colour distinctions: rejected because
  those cues disclose the same information.

## Consequences

- The existing feature specification holds the colleague-view acceptance example.
- The full role/field visibility matrix is still incomplete; this resolves only
  the ordinary-colleague row of review finding R5.
- Scaffold and shared-UI impact: none now; these are Leave-specific access rules.
- Agent-context impact: existing authorization and testing rules suffice.
- Documentation impact: align calendar filters, privacy rules, tracker, and index.
- ADR impact: additive visibility decision; accepted ADRs remain unchanged.
- No implementation or executable acceptance tests are authorized by this record
  alone; Phase 1 readiness remains required.
