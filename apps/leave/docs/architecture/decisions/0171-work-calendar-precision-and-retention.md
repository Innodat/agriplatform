# ADR-0171: Work/calendar precision and document-retention defaults

**Status:** Accepted  
**Date:** 2026-10-26  
**Decision owner:** User, explicit consolidated planning approval.

## Context

The reviewed final contracts resolve holiday/DST representation, exact odd-minute halves,
current-time timezone applicability and medical-document retention. They refine accepted
product rules without rewriting earlier accepted decisions.

## Decision

Adopt [work/calendar and exact minutes](../contracts/work-calendar-and-minute-precision.md):
net hours remain the default; Advanced intervals derive net minutes once. One dated closure
uses full-day, duration reduction or clock intervals; clock closures require actual work
intervals. Nominal local-clock quotas remain equal across DST transitions. Preserve exact
half-minute request, allocation, balance, reversal and report amounts: half of 435 minutes
is 217.5. Whole-minute usable entitlement flooring under ADR-0103 does not round those
amounts. Numeric constraints reject unsupported precision without typmod rounding.

Retain an explicit initial UTC applicability anchor and predecessor-timezone-derived
transition instants, with the documented midnight gap/fold/skipped-date rules. Dated
requests retain date-effective versions and submitted evidence. This does not reinstate
business-setup dependencies for lightweight draft preservation under ADR-0122.

Adopt the reviewed [document-retention contract](../contracts/document-retention.md):
24 calendar months by default, configurable 1–1,200 months, jurisdiction override before
organization/default, longest applicable jurisdiction period, retained closure/settings
provenance and prospective changes preserving recorded closed-document deadlines.
Settings Save never deletes documents. This technical default is not a legal finding;
the organization remains responsible for its applicable reviewed requirements.

Shared Identity/Access/Content choices follow [platform ADR-0064](../../../../../platform/docs/architecture/decisions/0064-approved-onboarding-continuity-and-content-contracts.md),
not copied service implementations. Existing tenant, access, history and immutable audit
rules remain binding. Earlier integer-only technical candidate mappings are superseded
by the minute contract; accepted ADR-0003/0041/0074/0103 remain intact.

## Consequences

The actual calendar/profile/duration/accounting/report/import owners prove exact examples,
concurrency, historical replay and generated client/storage compatibility. There is no
new accounting/calendar engine or precise absence-time input. Delivery uses controlled
compatible migrations; no Leave runtime schema has been created by planning.

The user requests a new Codex session before implementation. This decision records the
approved plan; it does not perform any runtime change or waive delivery acceptance.
