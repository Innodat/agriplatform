---
title: 'Contain controlled corpus publication and reconcile its original operation'
type: 'feature'
created: '2026-10-26'
status: 'done'
baseline_commit: '55681ae99fa883a04dcda15dcbe9517a110e0356'
route: 'dispatch'
review_loop_iteration: 0
context:
  - /home/ck/repos/innodat/agriplatform/AGENTS.md
  - /home/ck/repos/innodat/agriplatform/apps/scribeswell/docs/CORPUS_CALLER_PREPARATION.md
  - /home/ck/repos/innodat/agriplatform/_bmad-output/specs/spec-scribeswell-studies/corpus-publication.md
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

Finish the controlled caller boundary needed to qualify the existing durable corpus publisher. Run source qualification, audit and publication inside bounded app-owned containment, and reconcile the exact original publication after a missing acknowledgement. No public publisher endpoint or automatic import is introduced.

## Boundaries & Constraints

Always preserve explicit target custody, current restricted database authority, original operation/seal/source identity, safe errors and bounded process cleanup. Existing controller protocol and ordinary public reading remain compatible. The user authorizes technical choices and continuous implementation without routine stops.

Never provision owners, discover targets, consume ambient credentials, silently allocate another operation, restart a failed child, promise rollback, broaden private authority, push or deploy. No native SQL, migrations, grants, live owner calls, KDG ports or device/release claims during this implementation slice. Native transport/receipt qualification follows in the final integration phase.

</frozen-after-approval>

## Code Map

All app paths are under apps/scribeswell/.
- backend/corpus_operator.py: OperatorTarget/_target validate explicit restricted target; _exchange multiplexes bounded stdin/stdout and always kills/reaps direct child within reserved cleanup budget. Existing protocol version1 and execute_command/lookup_outcome must retain strict grammar and tests.
- backend/corpus_publish.py: publish_closed_attempt and lookup_publication own short transactions and durable publication receipts. _prepare accepts only the original seal with source qualification; _activation derives source revision; _receipt validates exact publication outcome. Caller currently owns transport containment.
- backend/corpus_publication_input.py and corpus_evidence.py own bounded source/command grammar. Do not invent a second parser or accept caller-claimed audit proof.
- tests/test_corpus_operator.py mixes native fixture tests and application transport tests: use explicit safe node IDs here. tests/test_corpus_publish_native.py owns final disposable real publication proof and stays uncollected during implementation.

## Tasks & Acceptance

- [x] Document additive app-local supervised publication/lookup contract, caller-retained immutable operation/seal/source and explicit error/recovery behavior before code. No durable operation store/runtime engine is needed: caller must explicitly supply retained values on lookup/retry. Reuse OperatorTarget and bounded containment rather than create another supervisor. Use a separately versioned private protocol for publication; keep version1 exact accepted keys/semantics.
- [x] Add supervised publication and lookup wrappers with mandatory explicit operation UUID, seal bytes and source bytes. Parent validates bounded input/operation and returned PublicationReceipt against original activation identity. Full source qualification runs inside child before any connection, using existing prepare logic. Child calls existing publisher APIs with restricted connection options and stripped environment. No credentials/bytes in logs, argv, error context or support output. Bound request/response/operation/cleanup, classify malformed/late/missing responses unknown, preserve explicit current-authority denial, and never infer rollback or automatically respawn/retry the outer operation. Existing publisher-internal original-operation receipt reconciliation remains unchanged.
- [x] Runnable application behavioral ATDD failure before implementation; focused TDD tests cover actual private child protocol, malformed/over-limit/late results, child timeout/forced cleanup, original operation/receipt identity, no ambient credential import and unchanged controller version1 behavior. Reuse meaningful existing containment assertions instead of multiplying mocks of identical internals. Native post-commit acknowledgement discard then original lookup/retry/current-authority cases authored only, ready for actual final execution. Distinguish deliberate stdout discard from real network-failure evidence.
- [x] Record exact commands/results, source snapshots, all failures and scaffold/shared-UI/agent-context/docs/ADR impact. App-only pattern, no platform promotion or accepted decision change. Do not edit canonical specs/memory, stage or commit; parent independently reviews/checkpoints and derives status.

Acceptance:
- Given an explicit prepared target and retained original seal/source/operation, when publication runs, then only the contained restricted child audits/publishes and a validated bounded receipt returns.
- Given a lost, malformed or late child acknowledgement, when the caller explicitly reconciles the original inputs, then the same publication identity is queried without source mutation, replacement operation or automatic reactivation.
- Given invalid target/protocol or current revoked authority, when invoked, then safe contract errors are returned without credential exposure or a competing authority path.

## Implementation Notes

Planning completed after study-details/discovery checkpoint55681ae99fa883a04dcda15dcbe9517a110e0356; current corpus_operator and corpus_publish APIs/transaction/receipt paths were reread. User continuous authorization overrides routine approval/dirty-main stops. Preserve full cohesive contract; no open intent questions. No intent gaps: this completes the already-required controlled caller qualification, not a new product surface. Footprint app supervisor/contract/tests only. No irreversible effects in this implementation phase. Final isolated native verification remains required before any claim of operational readiness.

## Spec Change Log

## Review Triage Log

| Finding | Verdict | Evidence | Route |
| --- | --- | --- | --- |
| B1 | maybe-false | Child preconnection _prepare and publisher public API both qualify source, consuming bounded time; the connection is idle/autocommit during second pass and no business transaction is held. No supported source deadline failure is demonstrated. Final real-source/capacity timing must establish whether this warrants optimization; do not add a trusted prepared-input path speculatively. | defer (medium unverified) |
| B2 | medium | Successful receipt tests mock exchange while real-child tests cover errors/null only. Add an actual isolated child valid receipt roundtrip binding original operation, dispatch/serialization/parent validator. | patch (coverage) |
| B3 | medium | New wrapper admission tests omit wrong/oversized source, oversized command and valid nonseal; old controller cases do not directly protect new branch. Extend no-spawn parameterization. | patch (coverage) |
| B4 | medium | Source child test invalid JSON does not prove valid JSON mismatching retained seal SHA is refused before connect. Add that concrete binding case and exact safe error assertion. | patch (coverage) |
| B5 | medium | Evidence hashes exist only in /tmp and full filtered argv is prose, so clearing temp loses reproducibility artifacts. Retain exact hashes/commands/result evidence in repository; distinguish HEAD comparison from true before-edit observation. | patch (evidence) |
| B6 | false | This is BMAD-required bounded execution spec referencing canonical corpus-publication and adopted caller contract, not another product authority/ADR or competing workflow. Root feature kernel/IDs/authority unchanged. The requested fix edits this build spec, which review instructions explicitly reject. | reject |
| V1 | medium | Publisher preserves safe corpus_mismatch, but both new worker and parent allowlists drop it into unknown_outcome, contradicting caller contract known-error promise. Preserve declared publisher identifiers in publication-only allowlist with regression. | patch |
| P1 | medium | Parent tracing independently confirms known closed-audit corpus_mismatch/deadline_exceeded propagate from publisher yet new protocol allowlists omit them. Preserve both safe declared identifiers without broadening controller-v1 protocol. | patch (V1 shared allowlist) |

## Verification

Prepared isolated Python; explicit application-only test IDs exclude native fixtures and clear database/native environment. Standard sandbox escalation for bounded local child processes. Use AST only for authored native tests. No global suite or native collection during this slice; parent owns final affected verification and final combined integration.

Prepared tools: isolated Python /tmp/scribeswell-implementation-python/bin/python. Hermetic child-process tests require normal sandbox escalation separately from workspace edits. Capture exact safe application node IDs to avoid collecting native-containing suites, and clear database/native environment. No new dependency installation is needed.

Parent independent verification:144affected application tests passed5.32s (runner5.95s),11selected source/reference hashes identical before/after. Exact commands/logs in apps/scribeswell/docs/evidence/supervised-publication/. Native case AST only; real receipt/permissions/performance/owner/device/release qualification remains final phase. All confirmed review patches complete; repeated-qualification timing remains unverified final-native gate.
