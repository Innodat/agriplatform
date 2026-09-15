# ADR-0069: Submission Summary and Exact Unpaid-Amount Acknowledgement

**Status:** Accepted  
**Date:** 2026-09-15  
**Scope:** Final request submission check

## Decision

The user approved a concise pre-submission summary of NGO, leave type, dates,
duration, paid/unpaid split, and required approvers. If the request includes unpaid
leave, require explicit acknowledgement of the exact requested unpaid amount.
Otherwise a single Submit request action is sufficient, subject to existing
validation and explanation requirements.

Tie acknowledgement to the amount being submitted. If revalidation changes it,
refresh the summary and obtain acknowledgement of that revised amount. This
does not replace [required approval](./0007-required-approval-and-automatic-decisions.md)
or authorize a balance override. Preserve the existing
[post-submission explained acknowledgement](./0032-protected-reservations-and-explained-changes.md)
rule for later increases. Submission revalidation follows
[draft rules](./0067-automatic-draft-saving.md) and the platform's
[API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md).

## Consequences

- The specification includes a 480-minute request with 120 unpaid minutes,
  exact-amount acknowledgement, revalidation changes, and a fully funded path.
- Checking a generic acknowledgement must not allow submission of an unseen
  different unpaid amount.
- Scaffold impact: no implementation now; promote proven generic summary patterns
  during delivery where useful.
- Shared-UI impact: summary primitives may be reusable; paid/unpaid calculations,
  approvers, and acknowledgement meaning remain Leave-specific.
- Agent-context impact: existing authorization, audit, and ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: additive initial-submission acknowledgement; accepted ADRs unchanged.
- Planning only; Phase 1 readiness precedes implementation.
