---
title: Native candidate own-edit API qualification
created: 2026-10-25
type: feature
status: done
route: dispatch
baseline_commit: ff5d7dbe50a24dcfe3d48bce51fb54f3e8c3bfc2
review_loop_iteration: 0
context:
  - apps/kdg-capture/docs/contracts.md
  - apps/kdg-capture/docs/OWN_EDIT_HTTP_EVIDENCE.md
  - apps/kdg-capture/docs/NATIVE_OWN_EDIT_EVIDENCE.md
  - platform/docs/development/migration-verification.md
---

<frozen-after-approval reason="human-owned intent">

## Intent

Qualify the actual candidate PUT own-edit orchestration and stored-target replay against retained PostgreSQL, using fresh synthetic data and mocked current Access responses. Earlier native body proof did not exercise this boundary. Keep body/schema/API unchanged unless a reproduced failure requires a focused fix.

## Boundaries & Constraints

Use only known run99b7231c-0a5b-4bdb-98e8-3329564c526a, existing private custody, applied0002 provenance and actual restricted runtime sessions. Journal all planned parent/capture/operation IDs and inputs before seeding; internal outcome IDs remain body-generated and discovered independently. Actual create establishes revision1; all edits/replays go through actual edit_http.create_candidate with ASGITransport and its real ordinary write engine/pool. Mock only Access; contexts/actors grant no real authority claim. Warm-up, if needed, must be explicit and not renew request observations.

After each response require released writer lease, then independent fresh restricted read-only storage verification. Preserve original rows and evidence, exact planned deltas, sentinel and ledger. Retain failures/source capsules; no silent rerun or cleanup. Source-bind executed dependencies before imports/before writes/after verification, including dev.py/native_cli.py. Safe append-only attempt records retain intended IDs, observed execution results before oracles and failure stage/class, never raw exceptions, credentials or signed URLs.

No migration, provisioning, privilege expansion, custom schema/ledger inventory, real accounts/Access, Leave/editor, active startup/browser/queue/UI, native contention/cancellation/TCP-drain claim, production, deployment/pilot or cleanup. Fingerprints/HMAC deferred; preserve concurrent changes, resources and dependencies including TypeScript7.0.2. Never read/run/edit preexisting untracked migrations/tests/schema_fixture.py.

## I/O & Edge-Case Matrix

| Case | Expected native behavior |
|---|---|
| Answers-only and date-only PUT | Actual body commits revision2 then3 with linked original facts/editor/outcomes |
| Current unchanged PUT | New receipt at3, exact capture/timestamps/history unchanged |
| Committed replay with changed valid path/stale revision/domain-invalid answers | Original target and revision2 despite current3; no fresh writes |
| Stale fresh input / invalid original answers |409 typed current_revision3 /422 validation_failed; exact storage unchanged |
| Foreign account / separately configured organization |404 capture_unavailable, no writes or receipt disclosure |
| Either capability denied / malformed HTTP |403 or safe422/401 before checkout; no state change |
| Native SQL failure after changed update/outcome before history |500 internal_error, actual native failure and full rollback; original failed-command retry commits4 once |
| Retry duplicate after revision4 | Original committed receipt and no further writes |

</frozen-after-approval>

## Code Map

Paths below under apps/kdg-capture:
- `migrations/tests/qualify_own_edit.py`: reuse new_plan, expected_receipt, complete-row oracle/transition/deltas and independent read. Its duplicate-refusal expectation belongs only to fresh body, not HTTP replay.
- `migrations/tests/qualify_capture_commit.py`: actual create, explicit assignment seed. `capture_commit_fixture.py` owns custody/provenance/receipts; no preparer.
- `migrations/tests/qualify_recovery_http.py`: source-bound SELECT-only checkpoint, runtime checkout/context clearing/physical disposal instrumentation and MockTransport evidence patterns.
- `migrations/tests/qualify_edit_recovery_http.py`: reuse complete prior-row snapshots/counts; avoid its one-receipt-per-revision assumption for no-op.
- `write-candidate/edit_http.py`, `capture_edit_handler.py`, `capture_edit.py`: actual subjects. Keep current dual capability checks and original Budget; no test replaces authorization/transaction/body orchestration.

## Tasks & Acceptance

- [x] `write-tests/test_native_edit_http.py`: meaningful behavioral ATDD RED then focused TDD for native harness ordering, source drift, privacy, lease/storage oracles, failed evidence and no-op/replay corruption.
- [x] `migrations/tests/qualify_edit_http.py`: retained-only CLI, fresh journaled plan, actual PUT cases, real SQL fault, independent reads, exact preservation and safe append-only evidence.
- [x] `docs/NATIVE_EDIT_HTTP_EVIDENCE.md`, `docs/evidence/native-edit-http-20261025.json`, append `docs/contracts.md`, prepend `docs/next-session.md`: exact executable commands/results, traceability, source/report hashes and precise limits; historical handoff suffix intact.

Given successful qualification, then one dataset adds one capture, five outcomes, four histories and one of each five parents; initial14/26/24 and parents6 become15/31/28 and parents7. Given replay/no-op/refusal, then independent complete rows prove exact appropriate preservation. Given SQL/evidence failure, then no qualified success and observed effects remain traceable. Given all app lifespans end, then checked-out count is zero and observed physical connections are disposed. No native network or real identity/access qualification follows from ASGI/mocked Access.

## Implementation Notes

bmad-help selects [BD] Build. No intent gap; persistent synthetic effects warrant dispatch. User next authorizes the proposed native slice and skips routine approval halts. Scoped local commit authorized. Root owns Docker preflight/resume/normal-stop, final review and commit; implementation agent runs native only after root readiness. Freeze sources/capsule before native calls. Use prior SELECT-only checkpoint before/after. Preserve every attempt if review requires a new dataset.

Scaffold/shared-UI/context/ADR impact expected none: reuse proven neutral helpers, keep KDG SQL/authorization oracles local. Record actual decisions and propagate any neutral fix through owning template/tests in this item.

## Verification

Pinned Python `platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python`; pinned Node at `platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node`. No installs. Smallest acceptance RED, focused suite, affected write suite265 baseline (120s limit), three sync-kdg-write/database/native-database --check scripts, native pre/qualifier/post (60s per command). Use local process access for known sandbox worker/socket restrictions and record actual outcomes. Root normal-stops exact run and verifies preserved network/volume/no running containers; no reset/prepare/cleanup.

## Review Triage Log


Root acceptance audit: all frozen matrix rows executed in17 native create/PUT cases. Actual restricted runtime sessions, released leases/physical disposal, full no-op/replay preservation, typed conflict, foreign scopes, both denial branches, actual23514 after outcome and original-command retry verified. Root read harness and focused tests;32 executed source bindings match, prior rows/sentinel preserved, deltas exactly1/5/4 plus five parents. Root affected suite278PASS18.440s (exit0),13 focused tests and three parity checks pass. Native pre/qualification/post exit0. Root normally stopped exact run; original network ID/volume preserved and scoped running containers empty. No runtime/body/schema/dependency change.


Three context-free review layers completed: Verification Gap Reviewer found no gaps; Edge filed E1 below; Blind filed B1–B8. Root classified each independently.

| Finding | Verdict / route | Evidence |
|---|---|---|
| B1: measure leases at ASGI response-start | low / rejected | Frozen contract and new native docs require released leases after each response, before independent read; the current observation proves exactly that. Actual route awaits non-abandoning worker/lease exit before returning. Adding a send-wrapper instrument for an additional timing guarantee is more than a direct correction, without a demonstrated early-release defect. |
| B2: decode before retaining response metadata | medium / patch | response.json() can raise before recording already observed status/cache/lease/SQL. Retain metadata first, decode afterward and preserve safe failure class. |
| B3: positional grouping | low / patch | Fixed case list is currently correct and fails closed for most wrong scopes, but positional slices become fragile when adding the demonstrated same-pool reuse case. Standard contiguous grouping by explicit foreign_org removes index coupling with no public surface. |
| B4: refused permission sequences | low / patch | no_checkout branches check lease refusal but omit exact sequence. Reuse existing observation with explicit expected read-denial/edit-denial/no-auth sequence; a small oracle correction. |
| B5: denial on committed operation absent | low / patch | Existing denial targets fresh retry only. Reusing these same cases with the committed answers operation directly qualifies current authority before replay, without new business writes or authorization mechanisms. |
| B6: original-account reuse after foreign refusal | low / patch | First pool is disposed directly after foreign-account failure. Add an unchanged original receipt replay through that pool to qualify context clearance under account switching. |
| B7: consumed configuration unbound | low / patch | native_fixture.retained reads tracked kdg-local.json. Add its hash to executed source bindings/capsule; no catalogue/ledger inspection. |
| B8: full controlled exercise mutation fixtures | low / rejected | Actual native exercise already ran17 cases; focused response/storage/source/evidence oracles have corruption tests and existing API tests cover real orchestration with controlled collaborators. Building a second simulated engine/event/fault/disposal stack adds substantial duplicate machinery without an observed false native success. New focused permission/response-retention tests cover the concrete accepted gaps. |
| E1: non-JSON response loses effects | medium / patch | Same verified defect as B2; retain separately as a finding, group the two for one response-recording patch. |

Seven findings addressed through six small patch groups; two rejected, none deferred. Same implementation agent re-engaged. First sources/report/intent and focused test preserved. Reviewed harness will qualify a second fresh dataset with exact incremental deltas; root owns retained-run resume/stop and final verification.


Reviewed-source verification:18 focused tests PASS; root full affected suite283PASS13.302s exit0, including all18 focused cases. Three parity checks PASS again. Same retained run resumed, SELECT-only pre/new native/post all qualified. Reviewed native report capture-commit-edit-http-578d5b15b0a64bbfb5dbf312aed7e165.json records20 cases, exact denied replay sequences and same-pool scope reuse, genuine23514 rollback and same-command retry. All33 executed sources match. Final totalscapture16/outcome36/history32,parent8; both datasets retained and all earlier business rows preserved. All three application physical connections disposed, zero leases after each response. Final run normal-stopped; scoped running containers empty, original network/volume retained. No runtime/body/schema/dependency/scaffold changes.

Root inspected retained-response ordering, explicit scope grouping, exact authority oracle, committed denial cases, same-pool reuse and consumed configuration binding. No further patch required. First receipt/source capsule/test and review diff remain historical; final public record binds reviewed sources.

Final custody audit:33 current executed source hashes and27 current/historical artifact references match. Historical contract bytes remain the prefix and baseline handoff remains the exact suffix. Runtime/body/API, schema, deployment configuration and dependency manifests/lock unchanged; TypeScript7.0.2 verified. Scoped whitespace check passed; final review diff refreshed.
