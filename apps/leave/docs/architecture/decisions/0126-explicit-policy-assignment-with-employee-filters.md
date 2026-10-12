# ADR-0126: Explicit Policy Assignment with Employee Filters for MVP

**Status:** Accepted
**Date:** 2026-10-12
**Scope:** Leave policy applicability and employee selection
**Links:** [Versioned policies](./0002-versioned-leave-policies.md),
[shared employment ownership](../../../../../platform/docs/architecture/decisions/0040-shared-employment-core-and-application-settings.md),
[current authorization](../../../../../platform/docs/architecture/decisions/0019-current-server-side-authorization.md).
Accepted predecessors remain unchanged.

## Decision

For MVP, use filters to select employees followed by explicit policy assignment.
Do not implement automatic policy eligibility based on employment type, location,
tenure or dynamically matching groups. These may assist authorized employee selection
where their facts/contracts exist; filters are not persisted automatic assignment rules.
The reviewed exact selected employment identities define the assignment scope.

Changing filters, adding an employee or changing employment facts does not silently
add/remove policy assignments. Authorized managers maintain assignments when employees
join or circumstances change. Leave owns assignment facts/history; People owns shared
employment facts supplied over authorized HTTP. Accountless employment remains supported;
assignments do not create login accounts, organization membership or application grants.

The backend enforces applicable explicit assignment for consequential requests alongside
current authority and the existing employment/date, duration, balance, document and
approval rules. Filters or frontend visibility are never authority. This does not relax
draft preservation: selecting/saving unfinished input remains independent of complete
business setup. Recurring overrides and one-off balance adjustments remain distinct.

Policy versions retain effective dates and historical meaning. Reject conflicting
assignment/applicability configuration on save, including concurrency; a dependency
outage means Couldn't check / Retry, not ineligibility. Exact identity/version binding,
effective-date/conflict semantics and effects of later reassignment remain pre-story
contracts, not an inferred reset, retroactive recalculation or new automatic engine.

Any assignment mutation with entitlement or existing-request consequences must satisfy
the owning calculation/review/history and notification requirements before activation.
Group 5's business-delivery foundation precedes any mutation requiring notification;
this decision provides no exemption or future-story dependency for early writers.

## Impacts and verification

Update features §4, the architecture spine, planning/stories and approved written UX.
Earlier eligibility wording is narrowed to explicit assignment for MVP, without editing
accepted predecessor ADRs. Test exact selected-set assignment, no dynamic additions or
removals after filters/facts change, new employee remaining unassigned, current authority,
cross-organization denial, historical version resolution, conflict/concurrency, safe
unavailability and preserved drafts. Consequential writers own their actual effect,
recovery and required notification evidence.

Scaffold/shared UI: reuse proven scoped employee filters/selectors and review/recovery
patterns; no generic eligibility engine or shared policy tables. Agent context: existing
ownership/current-access/history rules suffice. Automatic rule-based eligibility is
deferred until a concrete need and separately agreed lifecycle semantics exist.
Planning only; no application code, assignments, migrations or readiness approval.
