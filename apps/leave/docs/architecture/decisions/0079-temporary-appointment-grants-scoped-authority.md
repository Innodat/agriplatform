# ADR-0079: Temporary Appointment Grants Scoped Approval Authority

**Status:** Accepted  
**Date:** 2026-09-16  
**Scope:** Eligibility and authority of temporary approvers

## Decision

An authorized Leave Manager may appoint any active member of the same NGO as a
temporary approver. The explicit appointment grants approval authority for the
specified original approver's responsibilities and dates; a permanent Approver
role is not a prerequisite. Record appointing actor, reason, scope, and dates.

This grant does not provide organization-wide or permanent approval powers,
on-behalf request editing, or separate sensitive-document access. Normal assigned
approver visibility applies to requests validly assigned under the appointment.
Self-approval restrictions and known-absence checks remain. Suspension or loss of
active NGO membership prevents use of the temporary authority.

The grant ends at expiry. Preserve the authorized return and failed-return behavior
in [ADR-0077](./0077-scheduled-return-of-temporary-approvals.md). Do not implicitly
alter already assigned work outside the agreed pending-request inclusion process.

This partially supersedes [ADR-0076](./0076-approval-cover-and-planned-delegation.md):
the appointment now supplies scoped approval authority rather than requiring it
beforehand. It does not change general role-assignment administration under
[platform ADR-0011](../../../../../platform/docs/architecture/decisions/0011-application-roles-and-business-permissions.md).

## Consequences

- Tests must cover appointments without permanent approval roles, scope/date limits,
  inactive membership, self-approval conflicts, and separate document permissions.
- Shared UI/scaffold: reuse member/date controls when proven; no runtime changes now.
- Agent context: existing rules suffice.
- Documentation: synchronize product requirements, tracker, UX, index, and log.
- ADR impact: partial supersession above; historical decisions remain unchanged.
- Detailed capability storage and enforcement remain delivery architecture work.
