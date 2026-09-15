# ADR-0067: Automatically Save Unfinished Requests as Drafts

**Status:** Accepted  
**Date:** 2026-09-15  
**Scope:** Draft persistence and resume experience

## Decision

The user approved automatic draft saving while an employee fills in a request,
with a visible Saved/Not saved indicator and an explicit Save and close action.
Keep drafts tied to their NGO and accessible from My Leave. Drafts reserve no
entitlement until submission, which rechecks all applicable rules.

Show Saved only after successful persistence. On failure, show Not saved and
preserve entered data rather than representing an unsuccessful save as complete.
Do not treat draft persistence as validation, submission, or approval.

Apply the existing [employee home](./0063-employee-home-screen.md),
[overlap exclusions for drafts](./0052-overlaps-and-administrative-corrections.md),
and [reservation rules](./0032-protected-reservations-and-explained-changes.md).
Business-data persistence follows the platform's
[API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md).

## Consequences

- The specification includes save/resume, truthful failure state, no reservation,
  and submission revalidation expectations for later executable tests.
- Scaffold impact: promote proven generic save-status mechanisms during delivery
  where useful; no implementation now.
- Shared-UI impact: generic status/action primitives may be shared; Leave draft
  fields, validation, and NGO association stay application-owned.
- Agent-context impact: existing authorization, data-preservation, and ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: additive draft behavior; accepted ADRs remain unchanged.
- Planning only; Phase 1 readiness precedes implementation.
