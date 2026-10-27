---
title: 'Inert KDG administrator edit recovery request adapter'
type: 'feature'
created: '2026-10-27'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '183b57d1789de9886f1c1e126d45fbc15b045fb4'
context: []
---

<frozen-after-approval reason="standing authorization for remaining ready administrator consumers, delivery3 of up to3">

## Intent

Consume the existing administrator edit recovery GET explicitly, preserving the original pending operation identity and returning only its immutable committed receipt, ambiguous unresolved outcome or safe typed error. This inert Story3.2 consumer remains unmounted.

## Boundaries & Constraints

Use generated AdminRecoverEditData/Errors/Response, CaptureReceipt and Unresolved. Pin caller/bearer/org/operation/capture and literal command_type=capture.edit before awaits; closed inputs/options and canonical UUIDs. One same-origin private/no-store JSON GET to admin operations with exactly command_type=capture.edit query and no body or target/owner selectors. Server current read.all remains authoritative independently of edit.all; no own fallback or local grant inference. Original receipt lookup is current-executor/org/command/operation private; receipts have no own/admin surface discriminator, so never infer original authority or owner from this route.

Only exact operation/type/v1 committed receipt, expected original capture and canonical signed-bigint revision acknowledges recovery. Original revision may be old or from a no-op; never compare it to guessed current state. Closed unresolved retains exact operation/type only and never proves an in-flight request cannot later commit. No snapshot/proposal/actor label. Map exact generated status/ID errors with no raw message/body/exception/bearer. No writes, retries, automatic recovery, new operation identity, queue/store update, absence/rollback promise or Synced publication.

Strict duplicate-key JSON/fatal UTF8/closed result/error parsing and16384 actual streamed bytes including errors. One maximum10s deadline through fetch/body/validation/publication; current-generation/abort fences, late/ignored-abort/stalled/immediate-empty body handling and best-effort cancellation preserve bounded safe outcomes and discard stale results.

Preserve concurrent/historical work/resources and TS7.0.2. No UI/editor/Leave, Auth/session/startup/browser/queue/worker integration/activation, real services/accounts, native database/Docker, provisioning/migrations/privilege expansion, dependencies, deployment/production/pilot/push or cleanup. HMAC deferred. Never read/run/copy/hash apps/kdg-capture/migrations/tests/schema_fixture.py.

## I/O & Edge-Case Matrix

| Given / when | Then |
|---|---|
| Explicit original edit receipt or unresolved lookup, including after edit authority loss | One admin GET; deeply immutable exact original receipt or ambiguous unresolved; no PUT/edit requirement |
| Invalid local caller/scope/options/operation/target/type or selectors | Safe refusal before dispatch; no own fallback |
| Mismatched/extra/malformed receipt, unresolved or revision | invalid_response; no acknowledgement/absence inference |
| Generated error or wrong status/JSON/UTF8/headers/bytes | Safe exact status/ID or invalid_response; no raw content |
| Caller mutates inputs/options or requests overlap | Original pinned identity and independent cancellation/results preserved |
| Abort/stale/throwing predicate, transport/deadline, late/stalled/empty response | Bounded safe outcome with no stale publication, retry, persistence or rollback claim |

</frozen-after-approval>

## Code Map

- Implementation owns only five new files under apps/kdg-capture: web/src/admin-recovery.ts, web/tests/admin-recovery-adapter.test.mjs, web/tests/admin-recovery-adapter.types.ts, web/tsconfig.admin-recovery-adapter.json, web/tests/admin-recovery-adapter-proof.mjs. No commits; parent owns spec/docs/evidence, qualification/review/commit. Parent rendered BMAD; do not rerender.
- web/src/recovery.ts and tests/recovery.test.mjs supply own pending-edit recovery semantics; admin-edit.ts/admin-edit-context.ts supply current closed options and bounded transport. Reuse read-validation.ts id/token/object/strictJSON/decimal/invalid/InvalidResponse/Frozen/freeze without editing prior sources. Its READ error mapping is unsuitable for RECOVERY; implement generated recovery mapping locally.
- contracts/admin-edit-generated/types.gen.ts and write-candidate/admin-edit-openapi.json own authoritative recovery DTO/error families. write-candidate/admin_edit_http.py and docs/contracts.md administrator edit/recovery section own current read.all-only/executor-private behavior; no generated/backend/schema changes.
- Follow admin-edit-adapter-proof.mjs retained Node26.11.1/TS7.0.2 source capsule/log pattern including all compile/runtime/owner-schema dependencies. Named acceptance-only compiling stub must produce one meaningful recovery behavior RED before runtime. Enumerate generated errors, exact200 success, byte/deadline boundaries and every matrix row.

## Tasks & Acceptance

- [x] Observe named recovery acceptance RED before runtime implementation; retain compiling stub source/logs.
- [x] Implement five owned files with executed behavioral/type coverage for all matrix rows.
- [x] Parent inspect actual diff/results and qualify affected existing recovery/edit/admin consumers, owner backend/HTTP/freshness and five parities.
- [x] Three independent reviews, corrections, evidence/contracts, concise checkpoint/fresh-session handoff and scoped local commit.

Given current original pending edit, when recovery returns valid receipt or unresolved, then preserve exact identity and uncertainty. Given invalid or stale data, then publish no receipt or inferred absence.

## Implementation Notes

Freeform ready synthetic consumer; standing batch authorization preserves expected dirty tree without routine approval stops. No intent gaps/irreversible effects. Scaffold reuse; admin recovery semantics local. Shared UI/context/ADR unchanged; docs/evidence/handoff update together. Implementation gpt-6.1-sol/high; actual model/usage/model-only time unknown. Third and final delivery in this batch.

## Spec Change Log

## Review Triage Log

## Verification

New adapter strict types/emit/all tests; existing own edit/recovery and new administrator context/edit proofs with source-bound reuse when unchanged; affected administrator backend/loopback and owner export/client freshness plus five parity checks. Parent inspects actual logs/results and matrix coverage. Record commands/source/log custody, acceptance RED, five impacts/limits in docs/ADMIN_RECOVERY_ADAPTER_EVIDENCE.md and docs/evidence/admin-recovery-adapter-20261027.json. Fresh-session handoff goes in docs/next-session.md and concise docs/admin-request-batch-checkpoint.md. No activation/native claim.

Parent read the complete scoped diff and retained named acceptance RED log: compile/emit passed, stub verification_unavailable vs expected committed. Parent independent GREEN run-c1432410-c5e9-42e4-bc0f-7391596e5451 passes63 tests and strict types/emit; source unchanged. Every matrix row has passing executed behavioral/type coverage, including read-only request/no edit requirement, ambiguous unresolved, immutable original receipt, exact errors, mutation/overlap, streamed bytes and exact10s deadline. Shared batch69 backend/60 owner HTTP/95 own client and prior admin proofs reused only with full current source equality; five parities freshly rerun at final boundary. Review pending. Actual model/usage/model-only elapsed unknown; parent test waits recorded.

All three independent layers returned before triage: blind0 supported findings, edge[], verification0 gaps. No patches or new deferrals. All3 deliveries complete with220 new passing focused tests, shared affected verification and9 review layers. Fresh-session handoff/checkpoint will record delivery commits after scoped commit.
