# ADR-0166: Current Team for Approval Availability

**Status:** Accepted  
**Date:** 2026-10-24  
**Scope:** E5 request-review team availability, Story 5.17  
**Complements:** [ADR-0125](./0125-supervisor-based-teams-for-mvp.md)

## Decision

Compare the requested leave dates against the employee's current supervisor/direct-report
team within the organization. Resolve grouping from currently effective People facts at
the time of the availability query, through authorized HTTP. Use requested dates to find
intersecting permitted leave, not to project a different reporting group for each future
leave date. Scheduled supervisor changes do not alter grouping before they take effect.
Refresh after an effective change uses the new current group.

This is current decision-support context. It does not redefine historical report grouping
or E7 as-of reports, rewrite request/decision history, or create team membership records.
A temporary approval appointment changes neither the employee's reporting facts nor the
reviewer's team-read scope. Current request-review and team visibility predicates continue
to bound the returned people and fields; knowing a group is not permission to read it.
Unassigned reporting relationships create no fake supervisor or organization-wide fallback.

Required current grouping verification must succeed before returning a confirmed result.
Unavailable People facts are not proof that nobody is away. The panel remains advisory;
its technical failure does not independently block approval or replace mandatory applicant
responsibility coverage checks.

This decision resolves only current versus leave-date/as-of grouping. Included request
states, concise summary/count and exact query field contracts remain explicit planning
work; they are not silently accepted by this ADR.

## Verification and impacts

5.17-A tests a future request before/after an effective supervisor change, a scheduled
change not yet effective, current relationships across a multi-date request, unassigned
supervisor, current scoped visibility, temporary responsibility without expanded team
rights, cross-organization denial and unavailable owner facts. 5.17-B consumes the same
current-group evidence; no second grouping rule or frozen team snapshot is introduced.

Scaffold: reuse authorized owner HTTP clients and typed query failures; no team engine.
Shared UI: existing advisory availability panel and Retry. Agent context: existing owner/
current-access rules suffice. Documentation: Features, spine, read contract and story/
handoff/tracker references. ADR-0125 and platform owner/authorization decisions remain
unchanged. No implementation, runtime tests, migrations, grants or readiness authorization.
