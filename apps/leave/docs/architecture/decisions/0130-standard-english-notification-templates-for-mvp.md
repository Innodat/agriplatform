# ADR-0130: Standard Shared English Notification Templates for MVP

**Status:** Accepted
**Date:** 2026-10-14
**Scope:** Initial Leave email/in-app rendering through the shared notification capability
**Complements:** [ADR-0059](./0059-default-language-and-localization-readiness.md),
[ADR-0060](./0060-portuguese-mozambique-and-angola.md),
[ADR-0061](./0061-user-language-preference.md) and
[platform ADR-0006](../../../../../platform/docs/architecture/decisions/0006-common-notification-capability.md).
Accepted predecessors remain unchanged.

## Decision

For Leave MVP, use standard shared English notification templates with clear dates
and relevant organization identification. Defer organization-specific logos/colors,
editable/custom templates and Portuguese notification delivery. Keep strings/templates
translatable and business identifiers/dates/units independent of rendered language.
Existing preferences and English fallback remain intact; Portuguese stays planned for
Mozambique and Angola under its release/validation gates.

Organization identification provides initial tenant context without a branding editor.
Shared rendering owns channel/template mechanics; Leave owns permitted business content
and recipients. Retain strict event-family privacy and current authorized destinations.
This narrows first-consumer rendering scope, not API ownership or future richer branding/
localization support. No reliability, deduplication, retention or failure-visibility
requirements are relaxed.

## Impacts and verification

Update features, architecture, written UX, tracker and Story 3.25's rendering criterion.
Verify standard English output, correct organization binding/clear dates across channels,
minimal event content and authorized links, no foreign-organization metadata leakage
and translatable structure without claiming translations/custom branding exist.

Scaffold/shared UI: prove reusable standard template/formatting hooks with first consumers;
no custom template/branding editor. Agent context: existing instructions suffice.
Additive scope refinement; immutable predecessors unchanged. No code, translations,
provider changes, notifications, migrations or implementation/readiness permission.
