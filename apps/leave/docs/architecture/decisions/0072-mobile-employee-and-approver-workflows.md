# ADR-0072: Complete Employee and Approver Workflows on Phones

**Status:** Accepted  
**Date:** 2026-09-15  
**Scope:** Mobile employee and approver experience

## Decision

The user approved full employee request submission, document upload, balance and
history access, and required responses on phones. Approvers can review and decide
requests on phones as well. Preserve the same authorization, validation, decision
information, and explicit acknowledgement requirements as other screen sizes.

On small screens, the year calendar may use a compact month view with navigation
through the selected year. Keep the accessible companion history list available.
Apply [history and balance requirements](./0062-employee-history-and-balance-views.md),
[submission acknowledgement](./0069-submission-summary-and-unpaid-acknowledgement.md),
and [document permissions](./0006-sensitive-attachment-access.md). The platform's
[API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md)
continues to apply.

## Consequences

- The specification includes phone request/upload/acknowledgement, history/balance,
  approver decision, and compact-calendar/list acceptance expectations for later tests.
- This defines responsive capability, not a native application or offline mode.
- Supported browser/viewport coverage still requires definition during UX planning.
- Scaffold impact: promote proven responsive shell/layout patterns during delivery;
  no implementation now.
- Shared-UI impact: reusable responsive calendar/list primitives may be shared;
  Leave calculation and decision content remain application-owned.
- Agent-context impact: existing accessibility, authorization, and ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: additive mobile scope; accepted ADRs remain unchanged.
- Planning only; Phase 1 readiness precedes implementation.
