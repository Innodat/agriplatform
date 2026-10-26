# ADR-0160: Permanent Supervisor Change During Temporary Cover

**Status:** Accepted  
**Date:** 2026-10-22  
**Scope:** Affected unfinished supervisor work during an active temporary appointment  
**Clarifies:** [ADR-0147](./0147-current-supervisor-routing-and-concise-decision-attribution.md)
under platform [ADR-0060](../../../../../platform/docs/architecture/decisions/0060-application-owned-pending-supervisor-approval-transfer.md).

## Decision

When a permanent supervisor change becomes effective during temporary cover, the new
eligible supervisor takes over that employee's unfinished supervisor approvals. The
previous supervisor's temporary cover no longer routes or authorizes decisions for
that superseded supervisor responsibility. The temporary appointment continues only
for other responsibilities still validly assigned to it; do not terminate unrelated
cover or implicitly broaden it to the new supervisor's responsibilities.

Example: Ben temporarily covers Ana. Cara permanently replaces Ana as one employee's
supervisor. That employee's unfinished supervisor approvals move to eligible Cara;
Ben's valid cover for other employees/responsibilities remains. Later expiry/return of
Ben's appointment must not return the transferred work to Ana or overwrite Cara.

Preserve completed decisions, independently selected final steps, required gates and
existing audit/actual acting-for attribution. Missing/ineligible/unverifiable replacement
retains pending work with attention under L-0147; it does not preserve decision authority
through the superseded relationship or automatically approve a step. Any new temporary
cover follows the existing explicit appointment process.

## Remaining contracts and impacts

Bind affected employee/responsibility identity, effective change observations, scoped
appointment applicability, in-flight decision bounds, obsolete return fencing and
truthful People/Leave coordination/recovery. Preserve same unfinished-step waiting clock
under L-0156. Verify actual active-cover transfer, partial appointment scope retained,
new/old actor authority, stale expiry return denial, completed/final-step preservation,
ineligible replacement attention and concurrent/out-of-order retries before readiness.

Reuse existing transfer/appointment/queue/activity/notification mechanisms, with no new
history system or confirmation step. Promote generic gaps with first consumer. Update
features, spine, UX, Stories 5.21–5.25/5.32, tracker/handoff and ADR index. Existing agent
instructions suffice; accepted predecessors unchanged. Exact contracts, final source/test
coverage, dependency order, agent sizing/readiness remain open. No code, runtime tests,
migrations, live grants, deployment or implementation authorization.
