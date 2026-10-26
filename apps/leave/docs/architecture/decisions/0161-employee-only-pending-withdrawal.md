# ADR-0161: Employee-Only Pending Withdrawal

**Status:** Accepted  
**Date:** 2026-10-22  
**Scope:** Withdrawal versus rejection of submitted/in-approval requests  
**Complements:** [ADR-0007](./0007-required-approval-and-automatic-decisions.md),
[ADR-0149](./0149-standard-approver-includes-scoped-on-behalf-submission.md)
and [ADR-0152](./0152-simple-approved-leave-cancellation-defaults.md).

## Decision

Keep pending withdrawal employee-only, including requests originally submitted on that
employee's behalf. Do not add the proposed Leave Manager on-behalf withdrawal capability
or standard role default. Withdrawal means the employee retracts their request.

An authorized assigned approver may instead reject with an employee-visible reason under
the existing decision flow. A Leave Manager can reject only if separately authorized
and assigned to the required approval step. Otherwise use existing authorized reassignment
to an eligible approver. Reassignment alone does not grant the recipient approval rights.

Keep actual intent and actor attribution: do not record an administrative rejection as
an employee withdrawal. Preserve existing reservation release, task closure, history,
notifications and same-ID rejected correction/resubmission behavior. This does not extend
initial on-behalf submission or temporary approval into withdrawal authority, and does
not change E6 approved cancellation/correction defaults.

## Impacts and verification

Verify employee own withdrawal including on-behalf-created requests, denied manager/
approver/temporary withdrawal of someone else's request, assigned authorized rejection
with visible reason, unassigned manager denial, and existing transfer eligibility.
Reference owner lifecycle/race/recovery suites; no new withdrawal command or permission.
Reuse proven action/confirmation/reason/history controls; promote generic gaps with first
consumer. Update features, UX, spine, Story 5.19 and tracker/handoff/index. Existing agent
instructions suffice. Accepted predecessors unchanged. Exact contracts, final source/test
coverage, dependency order, agent sizing/readiness remain open. No code, runtime tests,
migrations, live grants, deployment or implementation authorization.
