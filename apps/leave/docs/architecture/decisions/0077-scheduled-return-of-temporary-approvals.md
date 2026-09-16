# ADR-0077: Authorize Scheduled Return of Temporary Approvals

**Status:** Accepted  
**Date:** 2026-09-16  
**Scope:** Temporary approval assignment expiry

## Decision

Disclose and authorize automatic return of outstanding steps to the original
approver when setting up a temporary assignment. At expiry, recheck that person's
eligibility and known continuing absence, preserve completed approvals, record the
transfer, and notify the returning approver.

If checks fail, retain the pending request and flag an authorized Leave Manager.
Never extend temporary authority automatically. An authorized extension before
expiry postpones the return.

This resolves the expiry question in [ADR-0076](./0076-approval-cover-and-planned-delegation.md)
and partially supersedes its requirement for an explicit reroute at the time of
every assignment change: the return can execute under the authorization recorded
at setup. Directory changes and unplanned reassignment still require explicit
authorized action. Preserve the platform
[API boundary](../../../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md).

## Consequences

- Record original approver, authorized return, assignment period, and transfer outcome.
- Delivery acceptance must cover valid return, ineligible/absent original approver,
  extension before expiry, preservation of completed decisions, and expiry of authority.
- Shared-UI/scaffold: no implementation now; reuse date/person controls when proven.
- Agent-context: existing instructions suffice.
- Documentation: update specification, tracker, UX, index, and decision log.
- ADR impact: partial supersession above; historical ADR text remains unchanged.
- Scheduling, concurrency, timezone boundaries, and retry contracts remain architecture work.
