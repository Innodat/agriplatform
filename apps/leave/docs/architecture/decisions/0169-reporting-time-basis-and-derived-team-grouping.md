# ADR-0169: Reporting Time Basis and Derived Team Grouping

**Status:** Accepted — user approved the E7 package and both choices on 2026-10-25
**Date:** 2026-10-25
**Complements:** [ADR-0125](./0125-supervisor-based-teams-for-mvp.md),
[ADR-0107](./0107-corrected-balances-preserve-decision-evidence.md),
[ADR-0166](./0166-current-team-for-approval-availability.md)
**Implementation/readiness:** Not authorized

## Context

E7 includes current and point-in-time balances and leave-used/team reports. ADR-0125
requires their current/as-of grouping semantics before readiness. ADR-0166 resolves
current grouping for E5 approval availability only; it deliberately does not decide
historical reporting. People owns effective-dated supervisor/department/location facts.
The user requested complete planning before review and approved the E7 package and
both choices on 2026-10-25.

## Decision

1. **Dated balances use corrected history known when the report is generated.** Evaluate
   the selected effective date with E3's authoritative replay, including now-known factual
   corrections and subsequent effective events through that date. Do not describe it as
   what the system knew then, or replace retained Balance at approval evidence. A report
   generated later can differ after an authorized correction. Display the balance date
   and generated-at/known-at context. MVP adds no second recorded-knowledge time-travel mode.
2. **Use current grouping for staffing views and effective grouping for historical facts.**
   Organization overview, upcoming absence and pending aging use People relationships
   effective at the one captured generation instant, even for a historical overview window.
   Dated balances use grouping effective on their balance date. Leave-used rows use the
   supervisor/department/location effective on each actual leave date; split a request
   crossing a grouping change, without duplicating minutes. Accrual/adjustment and
   override reports use grouping effective on each row's declared effective date.

Current authority always restricts both modes. An old membership/team relationship grants
no present access. An organization-wide manager can report historical former employees
with retained records; Show all employees is a staffing display option, not a reason to
drop retained report history. No recursive/named/project teams or team-profile defaults.
Unknown required historical facts yield an explicit unavailable/limited result; they are
never assigned silently to today's team or to a fabricated Unassigned group. Verified
absence of a supervisor is a legitimate Unassigned group within permitted scope.

Use one captured UTC generation instant and employee work-local dates for calculations.
Civil absence dates remain dates, not viewer-shifted UTC intervals. Overview's current
month/navigation is presentation context in the viewer's validated IANA display timezone;
it never changes the employee's leave dates or governing schedule. People effective-date
contracts determine historical relationships. A future dated balance is not quietly
labelled historical: the report validates that the selected date is no later than the
work-local current date for every selected employee, or asks for a compatible selection.
Current balances can use each employee's own current local date, identified per row.

## Alternatives considered

- Recreate exactly what was known at an earlier recorded instant: a separate product
  requirement with bitemporal retention/query implications; immutable decision evidence
  already answers what an approver saw at that action.
- Put all historical leave under today's supervisor: useful for current staffing, but
  rewrites historical team meaning and obscures where leave was used.
- Count a whole multi-team request in every team it touches: duplicates usage; use
  date/minute attribution and retain a distinct request count separately.

## Impacts and proof

Features, spine, written UX and the owning E7 contract adopt these accepted choices.
E7 story planning is closed by user agreement; executable delivery evidence and
whole-product validation/readiness remain open. Accepted predecessors are unchanged.
People supplies HTTP history evidence, not a second directory maintained by Leave.

Scaffold: reuse proven source/date/query adapters; no universal reporting engine. Shared UI:
use existing date/filter/table patterns, keeping report definitions and explanations in
Leave. Agent context: existing instructions suffice. Docs: E7 contract/coverage/dependency
register and accepted product/UX adoption. ADR: additive choice only, no new grant or
change to E5 availability/cancellation/approval routing. 7.7/7.9/7.11/7.13/7.15/7.17 and
7.28/29 own the actual as-of/correction, midnight/timezone, mid-request team change,
unassigned/unknown and wrong-organization oracles. No runtime test was executed.
