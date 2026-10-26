# ADR-0163: Protected Authority Check at Supervisor Boundaries

**Status:** Accepted  
**Date:** 2026-10-23  
**Scope:** Leave decisions crossing an effective permanent-supervisor change  
**Resolves:** The in-flight supervisor-boundary rule left open by
[ADR-0147](./0147-current-supervisor-routing-and-concise-decision-attribution.md)
and [ADR-0160](./0160-permanent-supervisor-change-during-temporary-cover.md), under
[platform ADR-0060](../../../../../platform/docs/architecture/decisions/0060-application-owned-pending-supervisor-approval-transfer.md).

## Decision

Use the final protected authority check as the Leave action's authorization instant.
If the actor is currently authorized at that check, its short bounded local transaction
may finish even when a permanent-supervisor change becomes effective immediately afterward.
Any final check at or after the effective boundary must use the new effective supervisor
facts and current eligibility. A preview, queued command or earlier request-start check
is not this final check. Worker lag cannot preserve the old supervisor's authority.

Validate the actual request/step/assignment, current application authority and relevant
source revision/effective interval under the established current-input protection. An
expired observation or incomplete verification requires fresh preparation outside locks;
it does not authorize a stale decision. Recheck a restarted execution rather than carrying
forward an earlier transaction's authority instant. No external-service wait occurs under
business locks.

Record the authority evaluation instant and applicable source/version basis in the existing
consequential decision evidence. Do not introduce a separate authority log or snapshot
engine. Preserve valid completed decisions and independently selected final steps. Temporary
cover displaced by a permanent change retains ADR-0160's exact responsibility scope and
obsolete-return protection.

This does not grant a general grace period after a supervisor change. It does not extend
a temporary appointment, revive revoked Access rights, relax employment/date or funding
checks, or choose another application's in-flight policy. Existing Access and other-owner
contracts remain separately binding. Define and verify the maximum remaining transaction
and total execution budgets before affected readiness; no numerical limit is accepted by
this decision.

## Verification and impacts

Force final checks before/at/after the boundary, a bounded commit just after it, worker lag,
old/new/temporary actors, concurrent source preparation and restarted execution. Inspect
actual decision authority evidence, source revisions and retained prior decisions. Verify
transaction timeout/rollback and uncertain original-operation recovery without reusing an
old authority check. No runtime tests or implementation were performed during acceptance.

Scaffold: use proven bounded protected-command/evidence primitives with first consumers.
Shared UI: no new screen, grace-period label or confirmation. Agent context: existing
current-authority/transaction/immutable-ADR rules suffice. Documentation: align product
truth, spine, source/Leave contracts, BMAD checkpoint and planned evidence. Accepted
predecessors remain unchanged; full People protocol adoption, exact contracts, coverage,
agent sizing and implementation readiness remain open.
