---
title: 'Inert KDG online audit request adapter'
type: 'feature'
created: '2026-10-27'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'e2b3445f09e93827199ef06b504d03c10b605a46'
context: []
---

<frozen-after-approval reason="standing user authorization to select and build ready synthetic local/CI slices without routine approval stops">

## Intent

Add an inert typed client consumer for the existing closed online audit metadata contract. One explicit request returns a validated immutable metadata page or safe typed outcome; malformed, foreign or stale responses never publish partial audit data. This is a technical Story3.1 subset, not a portal or historical actor-name implementation.

## Boundaries & Constraints

Use owner audit-generated types and current contracts.md bounded online audit section. Pin verified session account, requested organization/capture/limit/cursor before awaits. Each request relies on current backend read.all; no own fallback, offline authority, automatic retry, persistence or aggregation. Preserve independent statement timestamps, original owner and actual executor/nullable initiator, numeric bigint revisions and exact cursor binding. A current read caller may differ from the owner. Validate existing semantics; do not add contiguous-history or timestamp-monotonicity promises absent from backend.

Use same-origin GET, pinned bearer, private/no-store response, redirect refusal, strict duplicate-key/UTF8 JSON and 64KiB actual streamed bytes. One original maximum ten-second deadline covers fetch/body/validation/publication; support caller cancellation and current-generation checks, including transports ignoring abort. Cancel owned stream best-effort and discard late responses. No raw payload/error/bearer logging or error publication.

No UI/editor/Leave, Auth entry wiring, startup/browser/worker/queue/sender activation, native PostgreSQL/Docker execution, real services/accounts, provisioning/migrations/privilege changes, deployment/production/pilot/push, cleanup or dependency changes. Preserve concurrent/historical work/resources and TypeScript7.0.2; fingerprints/HMAC deferred. Never read/run/copy/hash migrations/tests/schema_fixture.py.

## I/O & Edge-Case Matrix

| Given / when | Then |
|---|---|
| Current caller requests first page for another owner's capture | One generated-contract GET; exact validated immutable closed metadata with actual actors/nulls; no owner impersonation |
| Valid continuation, numeric revisions including bigint values and unrelated statement times | Bind version/caller/org/capture/read.all/limit/last revision; strict descending bounded events; next cursor matches last included event; empty continuation accepted |
| Invalid local identity/scope/options/query/cursor | Safe local refusal before request; no own fallback or selectors |
| Foreign/malformed response, wrong event/header provenance, cursor mismatch, unknown fields or invalid JSON/UTF8/metadata | invalid_response without partial page; exact byte ceiling enforced |
| Known API error status/identifier or unavailable transport | Only safe typed outcomes; no English branching, automatic retry or raw content |
| Cancel, supersede or deadline at fetch/body/publication, including immediate empty chunks | Bounded result, late data discarded, best-effort cancellation; no durable side effects |

</frozen-after-approval>

## Code Map

- New `apps/kdg-capture/web/src/audit.ts`: standalone auditEvents adapter and page validation, reusing read-validation.ts strict JSON/closed object/id/decimal/instant/freeze/error helpers without modifying existing implementations. Import owner `contracts/audit-generated` request/page/error types. Keep actor labels absent.
- New `web/tests/audit.test.mjs`, `audit-adapter.types.ts`, `tsconfig.audit-adapter.json`, `audit-adapter-proof.mjs`: behavioral acceptance and focused TDD plus isolated TS emit/test runner using retained Node26.11.1/TypeScript7.0.2, unique private output path, no package installs. Existing read/history test/fixture and proof conventions are examples; new tests must not depend on compiled output shared with other sessions.
- Existing `write-candidate/audit_read.py`, audit_http.py, owner OpenAPI/generated types and web/tests/audit-read-http-proof.mjs define current server behavior. Reuse rather than change contract/backend.
- Parent owns this spec, docs/contracts append, handoff prepend and new AUDIT_ADAPTER_EVIDENCE.md/machine JSON. Child owns only the five new web files above, ATDD/TDD source/log custody and implementation notes; no edits to existing files or commits.

## Tasks & Acceptance

- [x] New acceptance test: run and retain meaningful missing-behavior RED before implementation, using a temporary stub if needed; then focused TDD for matrix cases.
- [x] Implement inert adapter/validation and meaningful runtime/type tests; provide repeatable proof runner with exact command results and immutable source/log snapshots under `platform/deployment/.local/kdg-audit-adapter-20261027/`.
- [x] Parent verify actual implementation/results, affected backend/helpers, existing client checks and five scaffold parities; audit every matrix row.
- [x] Independent three-layer review, patch supported defects, complete evidence/contracts/handoff and scoped local commit.

Given an authorized cross-owner audit response, when explicitly requested, then only its validated immutable metadata is returned. Given a stale or mismatched response, when it completes, then no audit page is published.

## Implementation Notes

bmad-help selected [BD] Build after reading current handoff/evidence/contracts. No human intent gaps or irreversible actions. Dirty tree and branch retained under explicit preserve-concurrent-work/no-routine-stops authorization. This freeform consuming subset does not update global/Leave sprint artifacts. Scaffold: reuse proven helpers; KDG audit/cursor semantics remain local, no new neutral pattern. Shared UI/agent context/ADRs unchanged; docs/evidence update together. Baseline records 558 existing tracked KDG/dependency files excluding append/prepend documents, with prohibited fixture excluded explicitly. Parent preserves prior handoff/contracts bytes in private custody.

Implementation selected gpt-6.1-sol/high for contract work; actual model/usage unavailable. Parent coordinates; review uses current coordinator capability. Retry/time observations recorded on completion.

## Spec Change Log

## Review Triage Log

| Finding | Verdict | Route | Evidence |
|---|---|---|---|
| E1: continuation at revision1 | low | patch | Full page ending at1 accepted impossible next cursor. Positive revisions plus backend limit+1 cannot produce an earlier row. Actual new regression fails before minimal last-revision guard and passes after. |

Blind Hunter: zero supported findings. Verification Gap: zero gaps. All three layers reported before triage; no new deferrals.

## Verification

New audit-adapter proof (strict TS7.0.2 emit/type plus Node tests); existing read/history proofs; affected audit backend HTTP/contract tests and existing audit HTTP loopback proof. Five existing adopted code/test parity checks. Exact commands/results/log/source hashes recorded in new machine evidence. No root build/test claim or native/resource action.

Parent verification:72 adapter tests,108 existing read/history clients,115 backend tests,43 existing audit loopback checks,owner export and five parities pass. Acceptance RED precedes implementation; expanded matrix tests followed first implementation, then genuine focused pagination RED→minimal correction→GREEN. Parent source-bound proof run-ad1121d4-8868-42c7-b3d2-82bd5ba586d5 passes. No tests changed expected results to dismiss failures. Three review layers follow.

Review triage: Blind Hunter reports zero supported findings; verification-gap reports zero gaps. Edge E1: low/patch — full first page ending at revision1 with matching nonnull continuation is accepted, but backend positive revisions and limit+1 cannot produce an earlier event. Add focused RED and minimal guard rejecting continuation at revision1; no new public API or contract choice.

Final review disposition: Blind Hunter0 supported findings; Verification Gap0 gaps; Edge E1 low/patch corrected with actual failing regression then GREEN. Rejecting revision1 continuation requires only a scalar guard, no new public surface. RED run-43334594-d08c-474e-97d3-400e9139a892 and GREEN run-f7fb3550-d351-4fd5-a7f7-94e27e7b63d5 retain full sources/logs. No new deferrals.

Final parent review-corrected qualification passes73 adapter tests,108 existing clients,115 affected backend tests,43 loopback checks,owner export and five parities. Parent proof run-532a2175-6e24-4693-9560-3da0a2b267b2 matches current source. Every matrix row has passing runtime coverage; negative local/scope/response/lifecycle cases return no partial data. All558 prior KDG/dependency files remain unchanged; append/prepend preservation passes. No runtime backend/schema/generated/shared/UI/context/ADR changes. Selected implementation model gpt-6.1-sol/high; actual runtime model, token usage and model-only elapsed unavailable. Retained command records measure test/tool waits; all failed sandbox and behavioral attempts retained. Final diff is limited to ten owned files; local commit follows, with no push.
