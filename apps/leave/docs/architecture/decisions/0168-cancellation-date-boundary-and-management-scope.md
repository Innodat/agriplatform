# ADR-0168: Cancellation Date Boundary and Current Management Scope

**Status:** Accepted — user approved both E6 choices on 2026-10-25
**Date:** 2026-10-25
**Complements:** [ADR-0152](./0152-simple-approved-leave-cancellation-defaults.md),
[ADR-0164](./0164-initial-on-behalf-employee-scope.md),
[ADR-0023](./0023-employee-work-timezone.md)
**Implementation/readiness:** Not authorized

## Context

ADR-0152 accepts own future cancellation, scoped standard Approver future cancellation,
and Leave Manager correction for started/past leave. It deliberately leaves the exact
future/start boundary and default management scope for E6. Duration-only partial days
have no start/end times; schedule times must not invent a time for an absence.
The user requested one review after E6 planning and approved both choices on 2026-10-25.

## Decision

1. Treat an entire approved request as future only while the employee's current work-local
   civil date is strictly earlier than its first recorded requested leave date. On that
   first date, it is started for cancellation authorization, including partial-day requests
   and multi-date requests. Do not split out a remaining future tail or infer absence
   start times. Started/past changes use the accepted scoped Leave Manager correction path.
   This boundary governs Change leave as well as cancellation; ordinary new backdated
   submission retains its accepted separate rules.
2. For standard Approver cancellation, reuse ADR-0164's **current ordinary responsibility
   population**: current supervisor/configured final responsibilities for the target
   employee/policy. Evaluate the actual employee, relevant retained request policy and
   current configuration, rather than the actor who once decided the request. Temporary
   appointment, fallback, a prior decision or escalation never enlarges that population.
   Broader organization management needs explicit administrative correction authority.
   The cancellation capability is separate from initial on-behalf submission, so neither
   implies the other and replacement requires both applicable actions.

Use one protected server evaluation instant and current verified effective work timezone
for the boundary. Retain the instant, timezone/version, first requested date and actual
scope evidence in consequential evidence. If governing timezone changes materially,
refresh review. No fresh authority check after midnight may use the prior date; a bounded
already-authorized execution follows platform ADR-0021 and the existing five-second local
transaction budget. Unknown effective timezone or current responsibility fails closed.
A request with a nonworking first selected date still uses its first recorded requested
date: choosing a later first charged day must not extend self-service authority.

## Alternatives considered

- Use the first charged work minute as start: insufficient for duration-only partial
  leave and would invent absence timing. A first charged date would allow cancellation
  during an already-started selected range.
- Give every final-step assignee organization-wide cancellation or reuse historical
  decision attribution: broader than current management scope and accepted authority.

These accepted refinements preserve accrual, duration, approval, Leave Manager NGO-wide
scope and standard Approver initial on-behalf rights. Later changes require a linked
superseding decision. No production default/grant is changed.

## Impacts and proof

Scaffold/shared UI: reuse typed authority, reviewed-command and date display controls;
no shared cancellation engine. Agent context: existing instructions suffice. Docs:
Features, spine, written UX and E6 planning references adopt these choices. ADR impact:
this additive record binds the details left open by ADR-0152. Acceptance of these two
choices does not by itself approve every proposed E6 delivery item or implementation.

E6 6.5/6.6/6.9–12 and 6.43 own midnight/date-line/DST/timezone-change, full/half/hour,
multi-date, current-supervisor/final-responsibility, custom omission, temporary/fallback,
self/other organization, revoked grant and stale-review boundary proof. No runtime test run.
