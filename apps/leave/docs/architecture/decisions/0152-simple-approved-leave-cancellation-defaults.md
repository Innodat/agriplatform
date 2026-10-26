# ADR-0152: Simple Approved-Leave Cancellation Defaults

**Status:** Accepted  
**Date:** 2026-10-22  
**Scope:** Default authority for approved leave cancellation; E6 delivery  
**Supersedes in part:** [ADR-0010](./0010-cancel-and-replace-approved-leave.md) and
[ADR-0053](./0053-administrative-correction-authority.md), only self-service/default
future-cancellation authority versus ongoing/past correction scope.
**Complements:** [ADR-0149](./0149-standard-approver-includes-scoped-on-behalf-submission.md)
and platform [ADR-0011](../../../../../platform/docs/architecture/decisions/0011-application-roles-and-business-permissions.md).

## Decision

Use these defaults for approved leave:

- Employees may cancel their own future approved leave.
- The standard Approver role includes scoped future approved-leave cancellation for
  employees within its authorized management scope, with a reason, actor attribution
  and employee notification.
- Leave Managers handle scoped on-behalf cancellation/correction, including leave
  already started or taken, under existing correction authority and reason rules.
- Temporary appointments alone supply no cancellation/correction capability; a separate
  current grant is needed. Custom approval-only roles may omit cancellation.

These are explicit capability/default-role mappings, not authority inferred from a
role-name string, supervisor relationship, past decision or temporary assignment.
Bind exact employee scope, future/start boundary and employee-work-timezone semantics
before affected readiness. A final-step assignment is not universal administration.
Keep current authorization/lifecycle/revision checks. Do not broaden coarse on-behalf
grants into unrelated past corrections, balance or document rights. Existing custom
roles require deliberate grant/version review.

Cancellation needs clear consequence review/confirmation, not another approval round.
Recalculate/reverse applicable consumption and dependent accrual/expiry consequences
exactly once, retaining original request, decisions and balance history. Untracked
policies retain usage evidence without fictional entitlement. Notify affected parties
using minimal messages and authorized details.

Changing approved dates/duration still uses cancellation plus linked replacement with
fresh validation/approval, not direct editing. Preserve failed-replacement validation,
approved-impact and necessary factual-correction/deficit safeguards. L-0151 applies to
later pending allocation changes, not rewriting approved paid leave. E1 discard and
E5 pending withdrawal/rejected resubmission stay separate.

## Impacts and verification

Detail actual E6 stories collaboratively later; this decision approves behavior/defaults,
not implementation or completed E6 decomposition. Verify own/other employee, standard/
custom/temporary authority, future/ongoing/past boundaries, correction scope, reason/
confirmation/notification, recalculation/history, duplicate/stale/racing commands and
safe recovery. Exact date/capability/API/test contracts remain open.

Comparison discussed 2026-10-22:
[Leave Dates roles](https://help.leavedates.com/article/100-user-roles-and-permissions)
and [defaults](https://help.leavedates.com/article/196-understanding-the-default-logic-used-by-leave-dates-and-how-to-change-it)
document own future cancellation and scoped approver administration;
[Simployer One](https://mysupport.simployer.com/en/support/solutions/articles/201000132003-how-do-i-edit-or-revoke-an-approved-time-off-request-in-simployer-one-)
documents scoped manager revocation and policy-dependent cancellation approval. Practices
vary; this is the user's selected rule, not a universal convention.

Update features, spine, written UX, default-role/E6 coverage, tracker/handoff and index.
Reuse proven capability/review/reason/activity/outcome controls; Leave owns recalculation,
Access owns grants. Existing agent instructions suffice. Accepted predecessors unchanged.
No code, tests, migrations, live grants, deployment or implementation/readiness permission.
