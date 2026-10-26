---
title: Unconnected own-edit request adapter
created: 2026-10-26
type: feature
status: done
route: dispatch
baseline_commit: 05e4b70e70ef88833f38adacf5e4d20015faa3ca
review_loop_iteration: 0
context:
  - apps/kdg-capture/docs/contracts.md
  - apps/kdg-capture/docs/OWN_EDIT_HTTP_EVIDENCE.md
  - apps/kdg-capture/docs/NATIVE_EDIT_HTTP_EVIDENCE.md
  - apps/kdg-capture/docs/RECOVERY_ADAPTER_EVIDENCE.md
  - apps/kdg-capture/AGENTS.md
---

<frozen-after-approval reason="human-owned intent">

## Intent

Implement the unconnected own-edit request adapter selected by the current native handoff. Consume generated edit request/receipt/error types, return typed safe conflicts, and accept a committed receipt only when its original operation and capture target match. This prepares a future caller without changing saved input or activating the editor/API.

## Boundaries & Constraints

One fixed same-origin PUT /api/v1/captures/{capture_id}, no account/org query selectors, JSON Content-Type, bearer from the pinned session, no-store and redirect refusal. Validate pinned canonical account/org/target/operation identity and supported command version/revision; snapshot serialized command and primitives before any await so caller mutations cannot retarget/change this request. Enforce131072 UTF-8 request bytes. Generated types describe request structure; backend retains original-definition/domain validation. Do not invent questionnaire, assignment or create validation here.

Require caller-owned AbortSignal/isCurrent generation fence following existing recovery conventions; predicate exceptions fail closed. Total deadline at most10 seconds covers headers/body even when transport ignores abort; response maximum16384 bytes, fatal UTF-8 and strict duplicate-key/Unicode/closed-shape validation. Check fences before dispatch and publication, including late bodies, stale errors and cancellation. No raw upstream message/body/exception is returned or logged.

Only matching v1 capture.edit committed receipt with exact operation/capture and canonical signed-bigint revision string can acknowledge success; preserve original string even at bigint max. A conflict is409 kdg_capture.capture_revision_conflict with required typed current_revision only; other409 errors cannot carry that field. Map only generated status/error pairs. Network/timeout/invalid responses never imply unresolved, rollback or safe new operation; cancellation after dispatch may still commit. Return safe classifications and preserve caller input. No automatic retry, recovery request, refresh, new identity, queue/store change or Synced feedback.

Synthetic local/CI only. No Docker/native, real Auth/accounts/Access, Leave/editor, browser/startup/queue activation, provisioning, deployment/production/pilot, migration or cleanup. Preserve concurrent work, historical evidence/resources and approved dependencies including TypeScript7.0.2; fingerprints/HMAC deferred. Never read/run/edit preexisting untracked migrations/tests/schema_fixture.py or hand-edit generated files.

## I/O & Edge-Case Matrix

| Case | Expected behavior |
|---|---|
| Valid edit | Exactly one pinned PUT/body; frozen matching compact receipt returned |
| Different op/type/version/target, extra/malformed receipt/revision | No acknowledgement; fixed invalid-response classification, input unchanged |
| Revision conflict / other safe error | Exact status/id plus conflict revision only; no upstream message/snapshot |
| Invalid account/target/operation/options, oversized command | Refuse before transport; no mutation |
| Caller changes session/command/options after start | In-flight URL/body/identity remain original; stale generation suppresses publication |
| Abort/stale/throwing fence at headers/body/return | No stale receipt/error; safe cancellation/supersession result and body disposal |
| Network failure, ignored abort, endless/oversized/invalid response | Bounded safe failure; no retry or rollback/absence promise |

</frozen-after-approval>

## Code Map

Paths under apps/kdg-capture:
- `contracts/edit-generated/types.gen.ts`, `write-candidate/edit-openapi.json`: current generated authority; no schema/backend/type regeneration needed.
- `web/src/recovery.ts`, `web/tests/recovery.test.mjs`: established pinned lease, strict response, deadline/stream cleanup and error-family conventions; reuse without broad transport/lifecycle refactoring. Characterize before any risky behavior refactor; existing recovery tests are protection.
- `web/src/entry.ts:Session`, `web/src/recovery-entry.ts`: pinned auth shape and later lifecycle-consumer pattern. Do not integrate Auth entry in this slice.
- `web/tsconfig.recovery.json`, `web/tests/recovery.types.ts`: direct Node26 TS testing and strict TypeScript7 fixture conventions.

## Tasks & Acceptance

- [x] `web/tests/edit.test.mjs`: behavioral ATDD RED before implementation, then focused TDD covering every matrix row, outbound byte snapshot/bounds, response/error families, cleanup and input preservation.
- [x] `web/src/edit.ts`: app-owned adapter, generated input/output types, safe closed results and runtime validation. Any tiny shared local helper extraction must retain recovery behavior; do not build a generic SDK or duplicate Auth lifecycle.
- [x] `web/tests/edit.types.ts`, `web/tsconfig.edit.json`: generated-contract consuming proof, typed conflict narrowing and negative cases; strict TS7.0.2.
- [x] `docs/EDIT_ADAPTER_EVIDENCE.md`, `docs/evidence/edit-adapter-20261026.json`, append `docs/contracts.md`, prepend `docs/next-session.md`: exact executable commands/results, source/log hashes, traceability and qualification limits; preserve historical suffix/prefix bytes.

Given valid input/current lease, when sending, then exactly one serialized original command reaches fixed own-API PUT. Given mismatch/failure/fence change, then input remains intact and no success publication or automatic side effect occurs. Given typed conflict, then consuming code can narrow safe revision without localized-text branching. Generated types and existing backend/Auth/startup behavior remain unchanged.

## Implementation Notes

bmad-help selects [BD] Build. No intent gap or irreversible effects; cross-file contract implementation warrants dispatch. User next authorizes this slice and skips routine approval halts. Root owns independent review and scoped local commit. BMAD already rendered once by root; use dispatched workflow, no second render.

Record scaffold/shared-UI/context/docs/ADR impacts. Existing generated contracts, Auth lifecycle and transport conventions are reused; KDG operation/target/error semantics stay silo-owned. Promote a concrete neutral fix through its owner/template/tests in this item if discovered; no speculative generic runtime.

## Verification

Pinned Node `platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node`. No installs. Observe meaningful acceptance RED, focused Node edit tests, then affected recovery/entry regression; strict root node_modules/typescript/bin/tsc on new edit config and affected existing recovery config (TS7.0.2). Three sync-kdg-write/database/native-database --check scripts verify adopted code/test parity. No backend/native suite claim if those sources remain unchanged. Preserve logs privately under platform/deployment/.local/kdg-edit-adapter-20261026, and record exact commands/results.

## Review Triage Log

All three independent layers returned before triage; edge-case hunter reported no findings. Each blind finding below was checked against implementation/tests and evidence. Verification-gap evidence is accepted as pre-verified by the workflow. All surviving corrections are local patches with no public surface or intent change.

| Finding | Verdict | Evidence and route |
|---|---|---|
| B1 cancellation during isCurrent | medium | The callback runs after the signal read, before abort subscription; it can abort and return true, allowing dispatch. The same ordering in finish can publish after callback cancellation. Patch ordering and regression tests; correct the copied recovery pattern under the same concrete regression. |
| B2 rejected lease traverses payload | low | Initial freshness gate occurs after JSON.stringify, so cancelled/stale executions can invoke answer getters/toJSON. Direct correction: gate before payload traversal and prove zero traversal. Patch. |
| B3 synchronous serialization resource claim | low | UTF-8 byte count follows JSON.stringify; synchronous JavaScript cannot be interrupted by the timer. Existing elapsed-time guard prevents dispatch after preflight expiration. Patch evidence wording to qualify allocation/preemption limits; no traversal engine. |
| B4 omitted undefined answer entries | medium | JSON.stringify drops direct undefined-valued answer entries; runtime callers can unintentionally replace the answer map with fewer entries. Patch direct entry rejection while preserving legitimate nested optional omissions. |
| B5 enum coverage loop | low | Current schema uses const variants and is covered, but enum fallback selects only the first ID. A direct loop correction makes the stated schema-driven coverage accurate for either representation. Patch test only. |
| B6 overlapping-call proof | low | Existing tests exercise one invocation at a time, leaving independent operation/cancellation isolation unqualified. Add one focused concurrent-call test; no implementation surface. Patch. |
| B7 RED/mutant source provenance | low | Logs retain commands/outcomes but the capsule contains final sources only; original modified states cannot be replayed from that capsule alone. Patch retained reproducible negative-control source/patch and distinguish reconstruction from original evidence. |
| B8 frozen intent hash reference | low | The record has a frozen-block hash without its spec path. Add the existing spec path to the evidence record as a direct provenance correction. Patch. |
| V1 exact success status qualification | medium | Reviewer mutation of status===200 to response.ok survived all48 tests; the existing201 case also has an invalid body. Add201/202 matching receipt rejection tests. Patch. |


Pre-review root acceptance audit (historical): inspected adapter/behavioral/type fixtures. All frozen matrix rows map to executed tests;48focused/116affected pass, no skipped cases. Source/log hashes and exact historical prefix/suffix bytes verified. Typed generated409 narrowing and eight negative cases compile under TS7.0.2; three parity checks pass. Predispatch deadline fixed/tested before review with a deterministic negative control. Backend/generated/recovery/Auth/entry unchanged, so no unrelated backend/native rerun or claim.

Final root audit: all nine findings addressed; no deferrals.54 edit +41 recovery +29 entry =124 passing affected tests, zero failed/skipped. Strict edit/recovery TS7.0.2 and three scaffold parity checks pass. Companion recovery race fix is characterized; generated Auth lease predicate is pure and unaffected, so no matching scaffold defect exists. Final root source/log capsule is separate from all historical/pre-review/post-review snapshots. No Docker/native/activation or dependency changes.
