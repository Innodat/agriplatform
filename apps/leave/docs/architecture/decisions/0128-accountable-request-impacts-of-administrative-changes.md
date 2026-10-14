# ADR-0128: Accountable Request Impacts of Administrative Changes

**Status:** Accepted
**Date:** 2026-10-13
**Scope:** Administrative changes affecting request funding or validity
**Refines:** [ADR-0032](./0032-protected-reservations-and-explained-changes.md),
[ADR-0039](./0039-cancellation-deficit-review.md),
[ADR-0048](./0048-upfront-grant-departure-recalculation.md).
**Links:** [ADR-0112](./0112-revalidate-calculation-inputs-at-confirmation.md),
[current authorization](../../../../../platform/docs/architecture/decisions/0019-current-server-side-authorization.md).
Accepted predecessors remain unchanged.

## Decision

The person authorizing an administrative change owns its request consequences.
Before confirmation, show affected requests and before/after funding or validity,
requiring the existing explanation/review rather than silently shifting responsibility
to the employee or approver. Required effects, attribution and outbound intent follow
their owning atomicity/recovery contracts; no remote waits under business locks.

For pending requests, unresolved impacts remain visible in the existing manager
attention view and authorized request details with the change actor/reason. Approvers
and authorized Leave Managers coordinate through ordinary human interaction and existing
approval, adjustment and correction actions. An approver uses a funding remedy only
with its current scoped authority; no implicit grant, temporary funding-permission
transfer, request-screen self-grant or new referral/task-routing workflow is introduced.

The system calculates and presents exact consequences. An increased unpaid amount
requires the employee's acknowledgement of that current amount before final approval;
the administrator's explanation cannot substitute for it. Other approval, employment/
date, funding, document and current-access gates remain independent. Acknowledgement
is not sufficient to resolve an invalid employment date or another unmet requirement.
Pending requests are not automatically cancelled or rejected because of the change.

For discretionary administrative changes affecting already approved requests, resolve
their impacts in the authorized change/correction review before committing the change.
Preserve the original approval and calculation evidence; ordinary approval is not reopened
and approved paid leave is not silently converted to unpaid. Exact resolution outcomes
remain the existing correction/adjustment domain actions, not direct history edits.

Necessary factual corrections, such as correcting a recorded employment end date after
leave was taken, may be recorded with explicit consequences even when restoring original
funding is impossible. Retain the existing authorized correction/deficit-review path and
visible unresolved attention. This exception does not authorize unexplained discretionary
changes or waive protected history, notifications, scope and consequential review.
It does not alter normal employee cancellation/replacement rights.

Known accrual, carry-over and expiry are already included in original date-by-date
projections; ordinary rollover alone must not unexpectedly increase unpaid amounts.
New reservations use only entitlement valid on each leave date and cannot displace
existing protected reservations. Later authorized changes/corrections can require the
above resolution; calculation of that impact is not a new user-facing shortfall workflow.

## Impacts and verification

E2/E3 configuration/employment/assignment writers integrate actual request-impact checks
and visibility with the first E5/E6 consumers before activation against real requests.
No earlier fixture-based story claims these workflows are implemented. Bind exact impact
classification, reviewed outcome, request revisions/current inputs, required local effects,
owner boundaries and attention resolution before the affected writer is ready. Reuse
existing capabilities and attention/request/approval/adjustment/correction surfaces;
do not introduce a universal task engine, extra approval role or permissions-transfer UI.

Test mandatory impact review, actor/reason and before/after amounts; denied funding
remedies; preserved original approvals; visible unresolved pending impacts; exact current
employee acknowledgement/finalization gates; discretionary approved-impact commit blocked
until resolution; necessary factual correction with retained deficit evidence/attention;
and concurrent changes/retries without duplicated effects or lost impact records.
Use current authorized business projections and minimal notification content; operational
logs contain no sensitive payloads. Notifications do not themselves acknowledge a request.

Scaffold/shared UI: promote proven generic review/revision/recovery/attribution controls
with first consumers, while Leave owns impact/resolution semantics. Agent context:
existing instructions suffice. Update requirements, written UX, architecture and delivery
tracking/test mappings. Additive refinement; accepted predecessors remain immutable.
Planning only; no runtime changes, permissions, data, migrations or readiness approval.
