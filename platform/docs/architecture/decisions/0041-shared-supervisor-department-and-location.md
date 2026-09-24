# ADR-0041: Shared Supervisor, Department and Location

**Status:** Accepted

**Date:** 2026-09-23

**Scope:** Shared employment and consuming application workflows

**Supersedes in part:** [ADR-0040](./0040-shared-employment-core-and-application-settings.md)
only its interim Leave-owned supervisor assignment; resolves its open department,
location and supervisor ownership questions.

## Decision

The shared employment owner maintains one optional supervisor relationship and
optional department and location assignments for each organization-specific
employment record. These are not global attributes of the person or login account.
Assignments may differ between organizations and must retain effective-dated history.

Department and location references are nullable: unassigned is a valid state and
does not prevent an employee record, draft or otherwise valid application workflow.
Use stable references to simple organization-owned department/location records,
maintained by the shared owner and reusable by applications. Do not require sentinel
records such as Unknown or duplicate editable labels in each application. A failed
lookup is an unavailable result, not an unassigned value. References must belong to
the same organization; referenced history must survive renames and retirement.
Exact table/API field names and lifecycle contracts remain delivery design.

Maintain the optional supervisor relationship manually through authorized shared
employment administration. Reference the supervisor's organization-specific
employment identity; reject cross-organization and self references. No full
organization-chart editor, recursive approval hierarchy, matrix reporting or
Microsoft Graph synchronization is required. Teams are not added to the shared
core by this decision; existing team requirements remain separately scoped.

Applications own approval policy. Leave's Employee's supervisor step resolves the
shared relationship at submission, checks current membership, approval eligibility
and self-approval rules, and snapshots the resolved assignment in the request's
workflow. A supervisor reference alone grants no approval authority. A missing or
ineligible supervisor prevents submission when that configured route needs one;
preserve the draft and explain the setup issue. It does not invalidate the shared
employee record. Explicit alternate routes and temporary cover retain their
existing authorization rules.

Subsequent supervisor changes affect newly resolved routes. Never silently reroute
already submitted requests; preserve their workflow snapshots and use authorized,
audited rerouting for changes to outstanding steps. Travel and other applications
may use the same relationship under their own policies without copying Leave's
workflow implementation. Future directory import may populate this relationship
only through a separately designed contract preserving authorized manual overrides,
organization mapping and existing request history.

Shared location describes organizational placement. Leave work profiles separately
own schedules, timezones, holiday calendars and standard-day conversion. Location
may suggest an initial profile under existing Leave rules; changing or clearing
department/location must not silently replace a profile, discard overrides or
alter historical calculations. Neither assignment grants data access by itself.

## Delivery impact and verification

- Contracts: Platform identity/people owner and Leave lead define scoped lookup,
  authorized edits, effective dates, revisions, retirement/history, null values and
  failure responses before E2 shared employment administration. Define supervisor
  read freshness and change races before dependent approval stories. Existing
  ADR-0040 consistency and short-transaction gates remain binding.
- Acceptance: null department/location/supervisor is accepted for an employee;
  organization-specific assignments remain independent; cross-organization and self
  supervisor references are rejected; unauthorized edits fail; historical values
  survive changes; unavailable reads are not treated as null. Verify valid supervisor
  resolution, missing/ineligible route recovery, no implicit permission grant and no
  silent reassignment of pending requests. Location changes preserve Leave profiles.
- Scaffold: prove nullable scoped references, typed clients and contract tests before
  promotion; do not generate a mandatory HR dependency for every application.
- Shared UI: simple optional selectors in employee administration, including a clear
  unassigned choice. Reuse authorized lookup and edit/review patterns; no chart UI.
- Agent context: existing ownership/organization guidance links this refinement.
- Documentation: synchronize Leave source, spine, tracker, UX and epic coverage;
  approved epic grouping and first draft slice remain unchanged.
- ADR: accepted predecessors remain immutable; no broader HR suite is introduced.
- Planning only; no schemas, runtime code, imports or readiness checks implemented.
