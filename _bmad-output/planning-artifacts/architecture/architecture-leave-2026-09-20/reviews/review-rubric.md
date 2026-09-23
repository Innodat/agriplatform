# Leave architecture — independent rubric review

**Date:** 2026-09-23  
**Reviewed:** `apps/leave/docs/architecture/ARCHITECTURE-SPINE.md`, AD-1–AD-13 draft.  
**Method:** Installed `bmad-architecture/references/reviewer-gate.md` good-spine checklist, following independent UX reconciliation. No edits to the architecture spine.

## Gate verdict

**Pass for architecture consolidation, with the spine's explicit delivery gates retained.** No critical, high, medium or low semantic findings are raised against this draft. This is not an implementation-readiness pass: concrete shared contracts, dependency versions, database/concurrency details, operational deployment choices and runtime accessibility evidence still have assigned pre-story/pilot gates.

## Mechanical evidence

Ran:

```text
uv run .agents/skills/bmad-architecture/scripts/lint_spine.py --workspace apps/leave/docs/architecture
```

Result: `ok: true`, `total_findings: 0`. This checks mechanical structure only; it does not prove runtime compatibility or correct implementation.

## Good-spine checklist judgments

| Dimension | Judgment and evidence |
|---|---|
| Fixes actual divergence points | **Pass.** AD-1 separates application/shared ownership; AD-2 distinguishes current platform authority from Leave action checks; AD-3/4 require atomic effects, short coordination, operation identity and reviewed state; AD-5/6 establish derived calculation and historical evidence. These are the seams where independent slices could otherwise implement conflicting semantics. |
| Rules are enforceable and prevent stated divergence | **Pass.** Each AD names bound components and a testable prohibition/obligation. Examples include no browser business-data bypass, no transaction-local partial outbox/audit effects, no changed payload under the same operation ID, no closed-draft resurrection, no unconfirmed attachment treated as evidence, and no local outbox skip presented as remote cancellation. The contract deliberately leaves schema/lock syntax to gated stories, rather than pretending a concrete lock alone guarantees all dependencies. |
| Deferrals cannot silently become incompatible implementations | **Pass with explicit gates.** Deferred identity/access and operation/error contracts must be settled before the first draft-slice story; content and notification protocols before their affected stories; persistence coordination requires all writers and technical-lead consistency ownership. These gates are substantive prerequisites, not optional backlog items. Shared date/calculation behavior remains in accepted ADRs rather than deferred under an unbounded “engine implementation.” |
| Current technology and brownfield fit | **Pass at stated decision level.** The stack is presented as accepted seed choices, not verified current versions or installed runtime. It explicitly requires compatibility verification and pins before dependent implementation, acknowledges planned Leave/builder runtime, and gates the existing numeric-error-template compatibility transition. No unsupported “already implemented” UI/service claim was found. Version research is correctly deferred to the pinning gate rather than invented here. |
| Source capability coverage | **Pass.** The capability map includes identity/setup/roles, policies/schedules/derived balances, employee requests/history/drafts, approval/coverage/correction, documents, notifications, reports/audit, import and operations. Independent UX reconciliation found no remaining spine contradiction. The one obsolete UX rounding sentence was corrected separately under parent authorization; fixed rounding remains authoritative. |
| Inherited invariants and supersessions | **Pass.** AD-5 follows derived on-demand accrual while preserving immutable actual events/evidence; AD-6 uses current precision and boundary decisions rather than resurrecting selectable rounding. AD-7 includes ADR-0088's independent acknowledgement gate, and AD-8 includes latest revision/lifecycle/create-resume protections. Platform HTTP ownership, explicit revisions and short-transaction exceptions retain their accepted bounds. |
| Owned architectural dimensions | **Pass.** In addition to domain calculation, the draft explicitly covers deployable API/worker processes, provider boundaries, migration ownership, restricted runtime identities, observability, recovery/backup objectives, restore side effects, alerts, versioned support commands and frontend accessibility/localization. Environment topology/secrets, monitoring deployment, provider capability and browser/performance evidence are visible owner/deadline gates, not silent omissions. |

## Important downstream checks, not new findings

1. **Do not treat inheritance as permission to implement an unspecified transition.** In particular L-0098 leaves changes of leave-period basis and transitions to/from manual-only/untracked policies as separate decisions. Existing period/method gates and authoritative requirements remain binding; generic policy CRUD must not invent those conversions. This is a source guardrail, not a newly discovered product requirement.
2. **Enforce the dependency gates before the first dependent slice.** A draft slice is not permission to defer shared access, operation/error compatibility, explicit revision fields, single-draft uniqueness or closed-draft retry evidence until later. The spine already orders these correctly; readiness must verify that ordering in actual stories.
3. **Keep accessibility and notification truth in delivery acceptance.** Written tokens and mocks do not prove WCAG behavior. Notifications describe events, not current request truth; balances show corrected results while historical snapshots retain original evidence. API DTOs, shared controls and tests must implement these distinctions.

## UX reconciliation disposition

`reviews/reconcile-ux.md` records one medium source-document conflict, **UX-R1**, now **resolved**: the obsolete “Enabling proration reveals rounding” sentence was replaced with the already accepted fixed-rounding/no-selector rule. No product choice changed and no accepted historical ADR was edited. The subsequent actual-spine comparison has no unresolved UX contradiction.

## Verification limits

This review reads a planning contract and its source constraints; it does not execute Leave, migrate a database, benchmark calculation, test browser/assistive technology or verify a production restore. Separate configured review lenses and the parent's synthesis may identify issues outside this rubric pass. Implementation remains gated by Phase 1 readiness.
