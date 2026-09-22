# ADR-0101: Monthly Rate Changes and Effective-Date Notifications

**Status:** Accepted  
**Date:** 2026-09-22  
**Scope:** Monthly annual-rate changes and communication of entitlement changes

## Decision

For monthly policies, apply a changed annual amount from the next applicable
instalment period start. Keep the current instalment's rate unchanged and do not
recalculate earlier instalments. This is distinct from daily prospective changes
and individual recurring overrides, which retain their own effective-date rules.

Example: Ana's 15 July–14 August instalment uses an 18-day annual amount and a
nominal 1.5-day portion. An increase scheduled during that period to 24 annual days
begins with the 15 August–14 September instalment, whose nominal portion is 2 days.
Under end-of-period availability the new portion is usable on 14 September;
under start-of-period availability it is usable on 15 August.

For an annual entitlement change, show the person making it the calculated
effective date during editing and the old amount, new amount and effective date
on confirmation. Show which affected employees change on which dates when their
anniversary schedules differ. Distinguish rate effectiveness from the first date
on which new entitlement is usable. Do not claim an employee's effective amount
changed if a continuing individual override means it did not.

After the change is confirmed, notify actually affected employees by in-app
notification and email through the shared notification capability. For ordinary
leave types explain old/new annual entitlement and effective date, with the first
new instalment availability date where relevant. Sensitive leave-type changes use
a generic message and an authorized detail link. Amendments or cancellations of
an already-notified scheduled change trigger an updated notification.

Record notification intent atomically with the confirmed change under
[platform notification rules](../../../../../platform/docs/architecture/decisions/0006-common-notification-capability.md)
and [operation identity](../../../../../platform/docs/architecture/decisions/0012-operation-identity-idempotency-and-tracing.md).
Failed delivery does not undo the change. Opening details checks current access.
Existing request-notification privacy rules remain; this decision concerns
entitlement-change messages, not permission to include request notes/documents.

Follow [aligned monthly periods](./0099-monthly-instalments-aligned-to-leave-year.md),
[daily rate changes](./0096-daily-earning-across-policy-versions.md) and
[individual override boundaries](./0083-recurring-entitlement-period-boundaries.md).
Cross-rate fractional instalment reconciliation remains calculation-readiness work.

## Consequences

- Acceptance: current instalment unchanged, next-period rate, start/end availability,
  different employee boundaries, overridden employees, minimal sensitive messages,
  amendment/cancellation updates and duplicate-safe notification intent.
- Scaffold/shared UI: reuse shared notification delivery and review primitives;
  effective-date calculations and message content belong to Leave.
- Agent context: existing privacy and event rules suffice.
- Documentation: requirements, tracker and UX contract updated.
- ADR impact: additive; accepted records unchanged.
- Planning only; no notifications sent or policy records changed.
