---
title: Candidate current-access own-edit API and replay
created: 2026-10-25
type: feature
status: done
route: dispatch
baseline_commit: 9827908ab7570b4e84f13de19bca91e1aac71d4c
review_loop_iteration: 0
context:
  - apps/kdg-capture/docs/contracts.md
  - apps/kdg-capture/docs/OWN_EDIT_BODY_EVIDENCE.md
  - apps/kdg-capture/docs/NATIVE_OWN_EDIT_EVIDENCE.md
  - apps/kdg-capture/AGENTS.md
---

<frozen-after-approval reason="human-owned intent">

## Intent

Expose the qualified inert own-edit body through an explicitly constructed candidate PUT API with current own-read/own-edit authorization and stored-target-authorized first-committed replay. This closes the server orchestration gap without activating the API or editor.

## Boundaries & Constraints

Always strictly parse path/body shape and supported version before outcome discovery. One original ten-second Budget includes body streaming, current Access checks, acquisition, worker, transaction, commit and acknowledgement. Bound both capability checks together to at most three seconds; establish both before SQL/acquisition. Require matching verified account, durable actor, membership instance, fixed organization and own-account scope. Use the older monotonic observation; do not renew freshness. Preserve the existing one-second local-entry limit and cancellation/connection ownership until worker unwind.

Always authorize the actual stored receipt target under current own-read/own-edit authority before disclosure, independent of incoming target/content/revision. No grant arises from incoming IDs. Fresh actions use the unchanged actual edit body; original version, ownership, no-op and revision safeguards remain binding. No create/assignment/active-child prerequisite. Successful acknowledgement follows durable commit only; late/failed acknowledgement preserves unknown-outcome semantics.

Synthetic local/CI only. No Docker/native writes, schema/migration, provisioning, real accounts/Access, active startup, Leave/editor, browser/queue/UI, production, deployment/pilot or cleanup. Preserve concurrent changes, historical bytes, resources and approved dependencies including TypeScript7.0.2. Fingerprints/HMAC deferred. Never read/run/edit preexisting untracked migrations/tests/schema_fixture.py. Never hand-edit generated files; neutral fixes propagate through owner/template and consuming tests in this item.

## I/O & Edge-Case Matrix

| Scenario | Expected behavior |
|---|---|
| Fresh own edit/no-op | Both current capabilities then actual body; committed compact receipt, no-op unchanged revision |
| Committed duplicate, different valid path/body/stale revision/domain-invalid answers | Authorize stored own target and return original receipt/revision; no fresh validation or writes |
| Missing/foreign stored target or malformed stored outcome | Safe private verification failure; no receipt/existence disclosure |
| Fresh stale proposal |409 kdg_capture.capture_revision_conflict with only typed current_revision metadata; no snapshot |
| Fresh missing/foreign capture |404 capture_unavailable, same safe response |
| Invalid/duplicate JSON keys, bounds/version/path, query/header ambiguity | Safe validation/authentication failure before Access or SQL as applicable |
| Denial, actor setup, scope/account/actor/membership mismatch, Access outage/body overflow/deadline | Allowlisted safe errors; zero acquisition/writes; no fallback capability |
| Slow acquisition, SQL/commit failure, expiry, direct/repeated cancellation | Original deadline/freshness, no provisional receipt, worker retains exclusive connection until unwind |

</frozen-after-approval>

## Code Map

All paths below under apps/kdg-capture unless stated:
- `write-candidate/capture_create_handler.py`: reuse bounded closed Access decoding, safe errors, non-abandoning `_complete_worker`; no service implementation imports. Its `_permissions` iteration is fallback, unsuitable for requiring both capabilities unchanged.
- `api/context.py:Context`, `write-candidate/operation_recovery.py`: current own-read evidence; exact stored org/account/target authorization projection pattern.
- `write-candidate/capture_edit.py`: qualified fresh-only body; use same write helper identity. Scoped lock/private lookup precedes fresh body; duplicate path must not select stored target.
- `write-candidate/recovery_http.py`: ordinary numeric-host bounded engine/pool, candidate factory/lifespan, private responses; write candidate must not inherit read-only connections.
- `api/capture_commands.py:parse_edit/MAX_COMMAND_BYTES`: strict bounded parser; domain answers validate only fresh branch.
- `api/safe_errors.py` generated: do not edit. Local typed conflict envelope extends compatible ordinary wire shape.
- `write-tests/test_capture_create_handler.py`, `test_capture_edit.py`, `test_recovery_http.py`, `test_recovery_contract.py`: proven synthetic connection/transport/runtime fixtures.

## Tasks & Acceptance

- [x] `write-tests/test_capture_edit_handler.py`, `test_edit_http.py`: behavioral ATDD failure before implementation; focused TDD covers every matrix row using actual orchestration/body where relevant, not only patched results.
- [x] `write-candidate/capture_edit_handler.py`: inert authorization/transaction/replay handler; reuse existing helpers without gratuitous refactoring.
- [x] `write-candidate/edit_http.py`: explicit lazy candidate factory and PUT /api/v1/captures/{capture_id}; one bearer, no query, bounded JSON bytes, private no-store responses, safe errors and typed conflict details. No exported live app/startup import. Acquisition follows Access; numeric-host pool/driver waits finite; cancellation drains worker before release.
- [x] Candidate OpenAPI export/check and generated consuming TypeScript via existing owning generator where applicable: truthful request/response/error metadata, conflict type and reproducible no-I/O export. Keep active read/recovery schemas intact.
- [x] `docs/OWN_EDIT_HTTP_EVIDENCE.md`, `docs/evidence/own-edit-http-20261025.json`, append `docs/contracts.md`, prepend `docs/next-session.md`: exact commands/results, source hashes, traceability/limits and next qualification; original handoff suffix unchanged.

Given a candidate synthetic request, when fresh or duplicate executes, then tests observe actual required authorization, stored-target binding and same Budget through commit. Given failed authorization/validation, then no pool checkout occurs. Given a worker cancellation, then lease release waits for unwind and no success is returned. Given conflict, then runtime and OpenAPI agree on safe typed metadata. Given export, then no engine/credentials/network are needed. Connection doubles establish control flow, not new native RLS/concurrency or real Identity/Access/release readiness.

## Implementation Notes

bmad-help selects [BD] Build from the current handoff. No intent gap; no irreversible effects, but cross-layer public candidate contract warrants dispatch. User's next authorizes this slice and skips routine approval halts; scoped local commit authorized. Root handles independent review/final commit. Implementation agent may update non-frozen notes/tasks, not intent. Record scaffold/shared-UI/context/docs/ADR impact decisions; reuse proven neutral helpers, keep KDG capability/domain SQL local.

## Verification

Pinned Python `platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python` and Node `platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node`. No installs. Observe meaningful acceptance RED, focused tests, then affected write suite (baseline219) with120s limit; sandbox subprocess timeouts may be rerun unrestricted with honest logs. Run three sync-kdg-write/database/native-database --check scripts; appropriate contract generation/check and pinned TypeScript checks for new generated types. Record exact commands; do not touch Docker.

## Review Triage Log


Implementation split: the dispatched agent implemented handler/HTTP and36 behavioral tests; root implemented offline schema/export, seven contract/export tests, generated consuming types and documentation. Meaningful pending transaction and schema RED observed; initial import failures are not treated as acceptance evidence. All frozen matrix rows map to executed tests in the source-bound record. Root affected suite262PASS20.637s; three parity checks, schema/generated checks and TypeScript7.0.2 with11negative cases pass. Current neutral templates unchanged; local application policy remains KDG-owned. No Docker/native action or dependency install.

Three context-free review layers completed. Edge Case Hunter returned []; Verification Gap Reviewer filed V1 below. Every Blind Hunter finding is classified separately before grouping.

| Finding | Verdict / route | Evidence |
|---|---|---|
| B1: unbounded TCP drain versus finite driver wait wording | medium / patch | Configured connect/server/pool timeouts do not bound a stalled network or non-abandoning worker unwind. Existing text overstates that limit; narrow documentation and retain explicit native drain gate. No new network control is justified here. |
| B2: Content-Type disagreement | medium / patch | The actual route parses JSON bytes under missing/text/plain or duplicate Content-Type while export declares application/json. Require one JSON media type with existing422; standard parameters remain accepted. |
| B3: same-operation overlapping fake writes | low / patch | The test demonstrates exclusive connections but its identical operation IDs imply duplicate serialization it cannot prove. Use distinct IDs; a stateful fake lock manager would duplicate PostgreSQL and is unnecessary. Native duplicate contention remains unqualified. |
| B4: limiter saturation test absent in new PUT suite | low / rejected | Unchanged `_complete_worker`/`_worker` are used directly. Existing executed `ProtectedCreateAcceptance.test_worker_admission_expires_without_late_sql` saturates the same default limiter and proves timeout without late SQL; new PUT acquisition is wholly inside that worker. Another synthetic saturation fixture would duplicate established neutral behavior without a demonstrated divergence. |
| B5: commit-phase cancellation coverage | low / patch | Existing cancellation phases omit commit although it lies inside the retained lease. Extend existing loop with on_commit; no production mechanism change. |
| B6: foreign organization/account target branches | low / patch | Existing target test mismatches ID first, leaving each org/account comparison unprotected. Add matching-ID foreign-scope cases to the same table. |
| B7: populated answer schema coverage | medium / patch | Empty answer-map tests do not protect manual UUID/text/Boolean schema rewrites. Add runtime/parser agreement on populated accepted and rejected values. Shared root cause with V1; same test patch covers both. |
| B8: generated Boolean permits false details | medium / patch | Generated BooleanAnswer is boolean plus optional details because the tool loses conditional allOf semantics. Use equivalent explicit Boolean oneOf branches and regenerate through owner CLI; a negative type fixture protects consuming contract. No public runtime behavior changes. |
| B9: cumulative/multibyte streamed byte limit | low / patch | Existing one-chunk overflow test does not exercise cumulative accounting or UTF-8 byte length. Add exact/one-byte-over chunks using a structurally valid replay, avoiding new domain fixtures. |
| B10: optional-command notation in exact evidence | low / patch | Literal [--check] cannot reproduce the invocation. Split generated/export and check command records; no tooling change. |
| V1: exported answer restrictions lack schema cases | medium / patch | Filed regression gap: manual conditional could be removed without current tests failing. Accepted as pre-verified; same populated-answer parity tests as B7 cover it. |

Same implementation agent re-engaged for small patches (including root-owned schema/test artifacts). No intent gaps, architectural change or deferred findings. Preserve prior logs and record post-review sources/results separately. Root will regenerate and run final checks.


Final review patches independently inspected: one JSON media type before streaming/Access; equivalent explicit Boolean branches and actual regenerated literal types; populated parser/schema parity; distinct operations for overlapping connection ownership; blocked commit cancellation; foreign stored org/account with matching ID; exact/one-byte-over multibyte chunks; precise commands and narrowed driver-wait wording. All ten accepted findings (B7/V1 share a root cause) addressed; B4 rejected with executed shared-helper evidence. None deferred.

Final root verification:265 affected tests PASS22.033s, including46 focused tests; all three scaffold parity checks, offline schema --check, owner-generated --check and TypeScript7.0.2 with12negative cases PASS. No Docker/native action, dependency install, schema or active startup change.

Final custody audit:31 current source bindings and7 retained logs match. Historical contracts remain the exact prefix and handoff the exact suffix. Protected runtime/generated helpers, dependency manifests/lock and TypeScript7.0.2 remain unchanged. Review diff refreshed after patches; staged scope excludes concurrent work and the untouched untracked schema fixture.
