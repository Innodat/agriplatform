# ADR-0165: Per-Request Outcomes for Selected Reassignment

**Status:** Accepted  
**Date:** 2026-10-23  
**Scope:** Manual reassignment of unfinished steps across multiple selected Leave requests  
**Complements:** [ADR-0153](./0153-standard-leave-manager-includes-reassignment.md),
[ADR-0156](./0156-preserve-approval-waiting-clock-on-transfer.md) and the existing protected
transfer scope in Story 5.24.

## Decision

For manual reassignment across selected requests, commit each request's selected unfinished
steps atomically and report each request's actual outcome independently. A stale/closed/
unauthorized item does not roll back valid transfers already committed for other requests.
Do not promise one cross-employee all-or-nothing transaction or report the entire selection
as successful merely because processing started.

Freeze the exact reviewed request/step selection and target. Each request has a distinct
retained operation ID and frozen payload. Matching retries resolve that original operation;
committed items are not transferred/notified again. Unresolved results stay unknown until
original recovery establishes an outcome. Retry only applicable failed/unresolved items;
changed selection/target/review requires explicit new confirmation after original uncertainty
is resolved. Never silently replace expected revisions or expand from a changed filter.

Within one request, all selected steps still move together or none do. Required current
reassignment/recipient authority, reason, lifecycle/revisions, immutable completed decisions,
waiting clock/escalation preservation, actual audit/outcome and recipient notification
intent remain binding. This does not create temporary authority, approval or funding rights.

Use the existing selection/detail surface to show committed items and specific items needing
attention. No new job dashboard, background impact engine, bulk rollback or outcome service.
Scope is this manual selection workflow; appointment creation, source updates and other
bulk actions keep their own declared atomicity contracts rather than inheriting it silently.

## Verification and impacts

Verify mixed valid/stale/closed/denied items, interrupted selection, lost item response,
within-request multi-step atomicity and original-item retry without repeated transfer/
notice. Inspect current assignments and immutable actual outcomes independently. A partial
result must neither erase successful changes nor claim unresolved items failed.

Scaffold: reuse actual per-command scoped revision/receipt/recovery primitives and bounded
client orchestration; no generic batch transaction engine. Shared UI: existing result/Retry
and source selection, no new screen. Agent context: existing current authority/recovery
rules suffice. Docs: C5 schemas/results, 5.24-A/B AC mapping, Features/spine/handoff. Accepted
predecessors unchanged. No code, tests, migration, grants or readiness authorization.
