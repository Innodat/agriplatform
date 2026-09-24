# ADR-0040: Shared Employment Core and Application-Owned Settings

**Status:** Accepted

**Date:** 2026-09-23

**Scope:** Employee information reused by Leave, Travel and other applications

## Context

The Leave architecture spine initially assigned employment settings to Leave.
During approved epic planning, the user identified employment as a reusable
cross-application concern and requested this deliberate ownership change be recorded.
Application-specific employee directories would duplicate common facts as further
applications are introduced. A shared table writable by every application would
instead obscure ownership and bypass the established service boundary.

## Decision

Give common employment facts one shared runtime owner under `services/`, consumed
through authorized HTTP contracts. Leave must not become the master employee
directory for Travel or unrelated applications. This establishes a small shared
employment capability, not a commitment to build a full HR suite.

Distinguish the shared person, linked authentication account, organization membership
and employment relationship. Employment belongs to a person in an organization;
login or membership alone does not establish employment, and employment alone grants
no application permission. Reuse the existing shared identity instead of creating
a second editable person record. Preserve multiple-organization relationships and
employment history, including rehire, without changing historical references.

The common core owns stable employment identity, person/organization references and
employment dates/status. Exact employee-number needs, relationship cardinality,
history representation and accountless-person support must be resolved in its
contract; do not silently equate an employment ID with an authentication user ID.

Applications own their domain extensions and actions. Leave owns work profiles,
schedule/calendar configuration, policy assignments, entitlement, requests, balances,
approval policy and document associations. Travel owns its own settings and workflows.
Employee-facing settings may compose shared facts with application-owned settings;
there must still be one authorized writer for each common fact. Do not store competing
editable copies or use cross-owner database queries/imported server implementations.

A schema called `hr` or `people` can implement the shared owner's persistence, but
the schema name, service name, deployment packaging and API remain delivery decisions.
Co-hosting is possible under existing service boundaries. Do not add a new directory
or service for every category of employee attribute.

Departments, teams, locations and supervisor relationships are not automatically
included in the new shared core. Their existing product requirements remain binding
until explicitly changed. Supervisor ownership and the minimal manual assignment
model are a discussion gate; no organization-chart editor, reporting-hierarchy engine
or Microsoft Graph synchronization is introduced. Current manual Leave supervisor
behavior remains in force until that decision is recorded. Graph integration remains
deferred and must not silently change pending approval assignments.

## Consistency and readiness

The Platform identity/people owner and Leave lead settle the shared contract before
the first dependent story becomes ready. E1 needs only the minimal authorized stable
employment reference/read contract required for draft ownership; E2 must not build
an independent employee master. Preserve the agreed first draft slice and all Phase 1
readiness checks.

Resolve access scope, allowed references, current/effective-dated reads, mutation
authority, revisions, audit attribution and unavailable-service behavior. Employment
updates may change Leave eligibility and calculation results. Define version/validity,
change notification and affected-request handling before dependent mutation stories.
A remote read is not proof that inputs remain current through a local commit; preserve
Leave's confirmation/review guarantees and ADR-0022 short transactions. Any local
projection is subordinate to the shared owner, versioned and recoverable, not a second
source of truth. Do not assume distributed atomicity or add a broker by default.

## Impact and verification

- Architecture: replaces the common-employment portion of Leave spine AD-1's earlier
  Leave ownership; Leave-specific settings and existing service-boundary ADRs remain.
  No accepted ADR is edited; this records the new cross-application ownership rule.
- Acceptance: shared facts have one authority; cross-organization access is denied;
  employment does not grant permissions; dates/history survive rehire; changed or
  unavailable shared inputs cannot silently validate stale consequential actions.
- Scaffold: establish typed service-client and stable-reference patterns with
  contract/compatibility tests when proven. Do not generate shared-table access or
  force employment into applications that do not use it.
- Shared UI: compose authorized shared employment fields with application settings;
  no general HR console or duplicate identity editor is required.
- Agent context: link common employment ownership and organization-neutral terminology.
- Documentation: synchronize Leave ownership, prerequisites and epic traceability;
  department/location/supervisor scope remains explicitly unresolved.
- Planning only; no HR product, service implementation, schema migration or readiness
  approval is created by this record.

## References

- [Application silo boundaries](./0003-application-silo-architecture.md)
- [Short transactions and external calls](./0022-short-transactions-and-external-service-calls.md)
- [Organization-neutral tenancy](./0039-organization-neutral-tenancy.md)
- [Leave architecture spine](../../../../apps/leave/docs/architecture/ARCHITECTURE-SPINE.md)
