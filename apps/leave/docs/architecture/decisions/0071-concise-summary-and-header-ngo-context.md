# ADR-0071: Concise Submission Summary with NGO Context in the Header

**Status:** Accepted  
**Date:** 2026-09-15  
**Scope:** Submission summary and active-NGO presentation  
**Supersedes in part:** ADR-0069's NGO and named approvers in the summary

## Context and decision

The user approved simplifying the pre-submission summary and avoiding repeated
NGO context for the common single-NGO case. Show leave type, dates, duration, and
paid/unpaid split, with Approval required where applicable instead of approver
names. Workflow details remain available on demand.

Keep the active NGO visible in the application header. Show an NGO switcher only
for users with multiple active NGO memberships. Do not repeat the NGO in the
submission summary. This presentation does not change request ownership or
authorization; drafts and submitted requests remain bound to their NGO.

This supersedes only the repeated NGO/named-approver summary content in
[ADR-0069](./0069-submission-summary-and-unpaid-acknowledgement.md). Exact unpaid
acknowledgement and submission validation remain unchanged. Retain
[save-before-switch behavior](./0068-ngo-switch-while-editing.md),
[NGO selector badges](./0055-ngo-scoped-notifications-and-badges.md) when the selector
is present, and the platform's
[API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md).

## Consequences

- The specification includes single/multiple-NGO presentation and unchanged request
  ownership examples for later executable tests.
- Scaffold impact: integrate proven header/switcher patterns during delivery; no code now.
- Shared-UI impact: conditional switcher and header context belong in shared shell
  components when proven; Leave summaries remain application-owned.
- Agent-context impact: existing tenant authorization and ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: scoped supersession; accepted original ADRs remain unchanged.
- Planning only; Phase 1 readiness precedes implementation.
