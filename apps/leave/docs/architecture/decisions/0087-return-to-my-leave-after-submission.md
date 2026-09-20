# ADR-0087: Return to My Leave After Confirmed Submission

**Status:** Accepted  
**Date:** 2026-09-20  
**Scope:** Employee post-submission navigation and feedback  
**Supersedes in part:** [ADR-0070](./0070-simple-submission-confirmation.md)

## Context and decision

Opening request details after successful submission requires an extra close action
for an employee who has finished applying. The user selected automatic return to
My Leave instead.

Only after confirmed success, close the desktop form or return from the mobile
form to My Leave, preserving the previous list context and scroll position. Show
a brief Request submitted confirmation with an optional View request link, update
the request list with its dates and authoritative status, and remove the submitted
draft indicator. Request details and approval history remain available on demand.
Do not require the employee to open details or dismiss another task view.

Awaiting approval, authorized immediate Approved status, required employee responses,
internal identifiers, and privacy rules from ADR-0070 remain unchanged. Restore
useful keyboard focus without forcing a scroll jump; announce confirmed success.
The request list provides lasting confirmation after the brief message disappears.

Failed or uncertain submission keeps the form and entered information available.
A confirmed failure offers Retry with a plain-language error near the actions.
An unknown outcome first checks whether submission succeeded; prevent another
submission while checking. If checking cannot complete, offer Check status rather
than treating the unknown outcome as failure. Retrying must not duplicate requests
or reservations. Do not claim a failed list refresh means a confirmed submission
failed. Existing current authorization and exact unpaid-amount revalidation apply.

The shared [API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md)
and [ledger protections](./0001-immutable-balance-ledger.md) continue to apply.

## Consequences and impacts

- Acceptance coverage must distinguish confirmed success, confirmed failure and
  unknown outcome, including response loss after successful submission.
- Scaffold: no template change now; this return destination is Leave-specific.
- Shared UI: reuse proven navigation, focus, status and recovery primitives during
  delivery; do not impose this destination on other applications.
- Agent context: no change; existing planning-only and verification rules suffice.
- Documentation: synchronize product requirements, delivery tracker and UX contract.
- ADR: supersedes only ADR-0070's automatic opening of request details; preserves
  that accepted file and all remaining approval, privacy and recovery rules.
- Planning only; this does not authorize implementation before Phase 1 readiness.
