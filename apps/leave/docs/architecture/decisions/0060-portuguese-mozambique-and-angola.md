# ADR-0060: Portuguese Targets Mozambique and Angola First

**Status:** Accepted  
**Date:** 2026-09-15  
**Scope:** Initial Portuguese localization audiences

## Context and decision

The user identified Mozambique and Angola as the first Portuguese-speaking
audiences. Plan Portuguese localization for both, building on
[English default and localization readiness](./0059-default-language-and-localization-readiness.md).
Validate wording and regional presentation for both audiences; do not silently
substitute Brazilian or Portugal-specific conventions. Shared translations may be
reused where appropriate, with regional differences supported where needed.

English remains the MVP default. Portuguese release timing remains open, and no
translation delivery is claimed complete. Language/locale choices do not change
the employee's jurisdiction, permissions, or
[work timezone](./0023-employee-work-timezone.md). Preserve the platform's
[API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md).

## Consequences

- Before Portuguese ships, validate representative employee and approver journeys,
  date/number presentation, and notification wording with speakers from each audience.
- Scaffold impact: reuse the localization hooks planned in ADR-0059; no code now.
- Shared-UI impact: regional labels and formatting must remain configurable;
  Leave translations stay in the application.
- Agent-context impact: no change now; existing localization planning suffices.
- Documentation impact: synchronize specification, roadmap, tracker, index, and memlog.
- ADR impact: additive audience selection; accepted ADRs remain unchanged.
- Planning only; implementation and translations remain subject to delivery gates.
