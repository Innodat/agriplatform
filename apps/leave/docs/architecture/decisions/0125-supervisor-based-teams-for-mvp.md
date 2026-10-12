# ADR-0125: Supervisor-Based Teams for MVP

**Status:** Accepted
**Date:** 2026-10-12
**Scope:** Leave team grouping, filters and MVP administration
**Links:** [Platform ADR-0041](../../../../../platform/docs/architecture/decisions/0041-shared-supervisor-department-and-location.md)
and [current authorization ADR-0019](../../../../../platform/docs/architecture/decisions/0019-current-server-side-authorization.md).
Accepted predecessors remain unchanged.

## Decision

For Leave MVP, a team is a supervisor's direct reports within the organization. Derive
it from shared People supervisor relationships through authorized HTTP contracts; do
not create independently named team records, separate team-membership maintenance or
recursive/matrix hierarchy. Departments and locations remain optional independent
organization-placement facts. This resolves the earlier mixed managed-team/direct-report
wording in requirements and UX without adding teams to the shared employment core.

Use supervisor-based groups in Leave team/calendar/report filters where required. Labels
may identify the supervisor's team, but reference exact organization-scoped employment
identities rather than names or login accounts. Unassigned supervisors remain valid;
represent them as permitted unassigned grouping/filter data without fake team records.
Supervisor changes update the applicable derived grouping but do not grant data/approval
rights or silently reroute submitted requests. Preserve existing role/resource/colleague
privacy and immutable workflow snapshots. Temporary approval appointments are bounded
workflow authority, not reporting-line or team-membership changes.

Future reporting/date-range consumers must define current versus as-of grouping and
supervisor-history/changed-input rules before readiness; do not silently rewrite historic
group meaning or duplicate totals when reporting relationships change during a period.
The existing current view and required historical evidence remain separate from automatic
approval reassignment. People owns relationship facts/history; Leave owns permitted view,
report/query and approval semantics.

Keep explicit work-profile assignment and organization fallback. Location may suggest an
initial profile under the existing rules; no independently configured team-profile default
or supervisor change silently changes work settings. Independently named/project teams,
team-specific profile configuration and broader directory synchronization are deferred.
Revisit only when a real cross-department/project-group need requires them.

## Impacts and verification

E2 employee/supervisor/selected replacement stories supply the grouping facts without a
new team catalogue story. E5 team availability and E7 calendars/reports consume them
with their own scoped projections/authorization tests. Test same-org direct-report
selection, unassigned supervisor, effective relationship change, other-org denial and
no implicit grants/rerouting. Supervisor/date/visibility contracts remain pre-story inputs.

Scaffold/shared UI: reuse validated supervisor/employee selectors and grouping/filter
controls when proven; no generic named-team table generator. Leave domain query rules
stay in Leave and no app imports another service server. Agent context and requirements/
UX/tracker link this decision; update accepted team-filter interpretations without editing
immutable predecessor ADRs or static historical mockups. No implementation, data changes,
new API/entity or readiness completion is performed by this planning decision.
