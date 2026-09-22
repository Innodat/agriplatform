# ADR-0102: Upfront Entitlement Changes at the Next Leave Period

**Status:** Accepted  
**Date:** 2026-09-22  
**Scope:** Annual amount changes for upfront policies

## Decision

Apply a change in an upfront policy's annual entitlement at each affected
employee's next leave-period start. Preserve the current period's grant; do not
silently recalculate an amount already granted or consumed. Use the applicable
calendar-year or anniversary boundary.

Example: Ana received 18 days upfront for the current year. A policy increase to
24 days gives 24 days at her next leave-year start, subject to applicable rules.
An immediate additional allocation uses a separately authorized balance adjustment
with reason and impact review. This does not reset her current remaining balance.

Show old/new annual amounts and effective dates to the editor and affected
employees, following [ADR-0101](./0101-monthly-rate-changes-and-effective-date-notifications.md).
Notify by email/in-app on confirmation and on subsequent amendments/cancellations;
preserve sensitive-type privacy and override handling.

Retain [policy versions](./0002-versioned-leave-policies.md),
[period-start grants](./0043-annual-grants-at-period-start.md),
[availability-method boundaries](./0098-availability-method-changes-at-period-boundaries.md),
and existing joining/leaving and historical correction safeguards. This governs
ordinary prospective annual-amount changes, not the correction of an erroneous
historical grant through an explicitly authorized correction workflow.

## Consequences

- Acceptance: unchanged current grant, next calendar/anniversary amount, separate
  immediate adjustment and accurate effective-date notifications.
- Scaffold/shared UI: Leave-specific effective dates; shared review/notifications reused.
- Agent context: existing historical-integrity and authorization rules suffice.
- Documentation: requirements, tracker and UX contract synchronized.
- ADR impact: additive; accepted records unchanged.
- Planning only; no grant or notification executed.
