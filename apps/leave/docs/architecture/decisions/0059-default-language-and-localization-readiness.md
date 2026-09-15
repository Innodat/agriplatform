# ADR-0059: English Default with Portuguese Planned Next

**Status:** Accepted  
**Date:** 2026-09-15  
**Scope:** Leave language and date presentation

## Context

The user approved English as Leave's default and the unambiguous date format
“15 Sep 2026”, and wants the ability to add Portuguese soon.

## Decision

Default the Leave experience to English and display English dates using day,
abbreviated month name, and four-digit year (for example, 15 Sep 2026). Continue
calculating business dates in the [employee work timezone](./0023-employee-work-timezone.md).

Prepare the initial implementation for localization: keep user-facing strings
and notification templates translatable, support locale-aware date/number
presentation, and keep stored dates, canonical units, identifiers, and permissions
independent of translated labels. Portuguese is the next planned language, not a
translation claimed complete in the English MVP. Its regional variant and release
date remain to be selected before Portuguese translations are finalized.

Use existing [canonical minute calculations](./0003-working-time-in-minutes.md)
and the platform's [common notification capability](../../../../../platform/docs/architecture/decisions/0006-common-notification-capability.md).
Do not choose a localization library or duplicate platform runtime logic in this
product decision; architecture will define implementation contracts.

## Consequences

- The specification includes the English date example and requirements to add
  Portuguese without changing business logic or stored data.
- Portuguese spelling, regional conventions, and translations need verification
  for the chosen audience before that language ships.
- Scaffold impact: establish reusable translation/formatting hooks when proven
  during delivery and update templates in that item.
- Shared-UI impact: shared components must accept localized labels and formatting;
  Leave-specific translations stay in the Leave silo.
- Agent-context impact: no change now; record proven localization conventions later.
- Documentation impact: synchronize specification, roadmap, tracker, ADR index,
  and memlog; do not present Portuguese as already delivered.
- ADR impact: additive language decision; accepted ADRs remain unchanged.
- Planning only; Phase 1 readiness precedes implementation.
