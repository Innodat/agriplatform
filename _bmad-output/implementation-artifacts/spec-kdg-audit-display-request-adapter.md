---
title: 'Inert KDG audit display request adapter'
type: 'feature'
created: '2026-10-28'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
baseline_commit: '2259592df294cff4293e054f44057476371e1fc9'
---

<frozen-after-approval reason="explicit continuation authorization; recorded contract and scope">

## Intent

Implement one inert auditDetails browser request adapter against the existing generated audit-display aggregate and docs/audit-display-composition.md. An explicit same-origin authenticated GET returns a deeply immutable complete aggregate or a safe typed outcome. Validate closed JSON/UTF8, actual 321 KiB aggregate and 64 KiB audit/256 KiB display subtree bounds, original audit semantics/cursor binding and exact sorted page-derived actor labels. Resolved names follow Identity's scalar/256-codepoint/1024-byte/nonblank rules; unavailable actors and unavailable batches remain distinct.

Pin account/bearer/org/capture/query before awaits. Require caller cancellation and an explicit current-generation predicate representing account/org/capture/page/session/access invalidation; recheck before/after reads and publication with one maximum ten-second monotonic deadline. Discard whole delayed success/error results after invalidation, cancel owned streams best-effort, never cache/retry/log raw values. Preserve current server read.all responsibility.

No portal/UI/editor/Leave, Auth/session/device/startup integration, real services/accounts/credentials, native DB/Docker/migrations/grants, dependency changes, workers/queues, deployment/production/pilot/push or resource lifecycle/cleanup. Preserve concurrent work, historical evidence and TypeScript7.0.2. Never read/run/copy/hash migrations/tests/schema_fixture.py.

</frozen-after-approval>

## Implementation Notes

No intent gaps or irreversible action. Small bounded adapter plus tests/docs; oneshot inline implementation, independent blind review per installed workflow. Dirty main retained under explicit preserve-concurrent-work authorization. No epic/global sprint mutation: this is a freeform technical subset of Story3.1, not its completion.

Code map/ownership: web/src/audit.ts exposes existing pure pin/validatePage functions only (characterize first); new web/src/audit-display.ts reuses these and read-validation.ts. New audit-display.test.mjs, audit-display-adapter.types.ts, audit-display-adapter-proof.mjs and tsconfig.audit-display-adapter.json prove the generated contract without mounting. docs/AUDIT_DISPLAY_ADAPTER_EVIDENCE.md, evidence/audit-display-adapter-20261028.json, contracts.md append and next-session.md prepend record result and limits.

Given a valid cross-owner page, when requested, then complete exact actor labels and unchanged audit metadata return frozen. Given malformed/foreign/reordered/missing/extra labels or invalid cursors/bytes/names, when parsed, then no partial result publishes. Given account/org/capture/page/session or access generation change, cancel or deadline, when delayed success/error finishes, then no data publishes. Given a known API error, when current, then only safe status/error_id returns.

Scaffold: existing bounded transport behavior/strict helpers reused; domain audit/name contract stays KDG-local, no new neutral promotion. Shared UI: none. Agent context: unchanged. Documentation: delivery evidence/contracts/handoff. ADR: existing0023/0031/0056, no new or modified ADR. Release: unmounted candidate, no activation/migration change.

Coordinator inline per oneshot; selected/actual model and usage unavailable. Test/model elapsed recorded only where observable. Private source/log custody: /tmp/kdg-audit-display-adapter-20261028. Original audit adapter characterization passes73 tests plus TS7.0.2 before export-only seam.

Initial acceptance RED: run-f540f152-c350-49cb-a31c-cef6f4db2fce compiled successfully and failed invalid_response != loaded against the temporary stub. Two sandbox subprocess attempts are infrastructure failures, retained separately. The expanded aggregate matrix followed first implementation, not individually test-first. First implementation passed72/73 inherited tests; the remaining inherited test had a 64KiB error-body assumption and was adjusted to the selected321KiB aggregate contract (165000 multibyte characters). Expanded proof run-89a154df-9d1a-4112-a213-bb94512ce768 passes108 tests/strictTS7.0.2. Existing audit characterization rerun passes73. No production change was made to dismiss that test expectation.

Freshness diagnosis: existing generated manifest source hash did not match current owner schema, while scratch generation's index.ts/types.gen.ts bytes were identical. Owning pinned generator repaired only .generated-files.json; no hand edit, wire/type/schema change or dependency install. Scratch diagnostic is retained under /tmp/kdg-audit-display-adapter-20261028/generator-diagnostic. This adds the existing generated manifest to delivery ownership. Review found zero supported code findings; reviewer default Node24 prevented local proof, so coordinator verifies with retained26.11.1. Final evidence docs were not yet present at that review; request follow-up after writing them.

Final qualification:109 adapter tests/strictTS7.0.2 pass (303.53ms runtime),73 original audit tests pass after export-only seam;20 backend tests/two subtests pass in2.88s. Owner/generated freshness and five adopted parities pass. Exact commands/logs are in /tmp/kdg-audit-display-adapter-20261028/qualification.json and docs/evidence/audit-display-adapter-20261028.json. All614 protected KDG source hashes match; original contracts/handoff bytes remain append/prepend-preserved. No prohibited fixture or resource action. Final capsule binds sources and docs; no other dirty files staged.

## Review Triage Log

Installed oneshot workflow requires one blind layer; no other layer active. Initial review: zero supported code findings, documentation pending and default Node24 runtime limitation disclosed. Follow-up: zero supported findings in final documentation/evidence/generated manifest/test additions. Reviewer independently reran all109 tests with pinned Node26.11.1 and strictTS successfully; inspected retained backend/freshness logs. No findings to patch or defer. No new deferral. Full Story3.1/3.2 and mounted browser/Auth/session/device/real-authority/native/release remain gated.
