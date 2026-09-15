# ADR-0061: User Language Preference Follows NGO Switching

**Status:** Accepted  
**Date:** 2026-09-15  
**Scope:** Interface and personal notification language

## Decision

The user approved each person choosing their preferred interface language, with
English fallback. Retain that preference when switching NGOs. Personal
notifications use the recipient's preferred language when translations are
available, otherwise English. A language preference does not change work timezone,
leave policy, jurisdiction, permissions, or stored business values.

Apply [English default and localization readiness](./0059-default-language-and-localization-readiness.md)
and [Portuguese audience planning](./0060-portuguese-mozambique-and-angola.md).
Use the platform's [common notification capability](../../../../../platform/docs/architecture/decisions/0006-common-notification-capability.md)
for recipient-language rendering, retaining all existing payload privacy limits.
Preference persistence must follow the platform's
[API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md).

## Alternatives considered

- Change language automatically with the active NGO: rejected; the user preference
  persists across NGO switches.
- Require all personal notifications to remain English: translated messages use
  recipient preference when available, with English fallback.

## Consequences

- The specification records NGO switching, recipient language, English fallback,
  and unchanged business calculations as acceptance expectations for later tests.
- This does not claim Portuguese translations are delivered or permit users to
  change another user's language preference.
- Scaffold impact: integrate preference and localization hooks when proven during
  delivery; no runtime code is introduced now.
- Shared-UI impact: shared shell language controls should respect user preference;
  Leave translations remain application-owned.
- Agent-context impact: no change now; existing authorization and ATDD/TDD rules suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog.
- ADR impact: additive preference decision; accepted ADRs remain unchanged.
- Planning only; Phase 1 readiness and failing acceptance tests precede implementation.
