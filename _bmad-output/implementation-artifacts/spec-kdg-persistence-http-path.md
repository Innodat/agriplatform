---
title: Complete synthetic create edit and recovery HTTP path
created: 2026-10-26
type: feature
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: d7f942a1c247570e07bb5dd7be4d242566b9e734
context:
  - apps/kdg-capture/AGENTS.md
  - apps/kdg-capture/docs/EDIT_ENTRY_EVIDENCE.md
  - apps/kdg-capture/docs/OWN_EDIT_HTTP_EVIDENCE.md
  - apps/kdg-capture/docs/RECOVERY_HTTP_EVIDENCE.md
  - apps/kdg-capture/docs/CAPTURE_CREATE_BODY_EVIDENCE.md
---

<frozen-after-approval reason="human-owned intent">

## Intent

Complete the missing create HTTP/client boundary and qualify the coherent create→edit→recovery path using existing KDG business handlers and current Auth entry. User authorizes continuing implementation across internal slices without another next/approval cycle. Deliver working candidate code and synthetic network evidence; do not claim the entire KDG product complete.

## Boundaries & Constraints

Explicit candidate POST /api/v1/captures, no default app/runtime activation. Reuse CreateHandler authority/transaction logic, existing owned-worker cancellation and engine conventions. One original budget spans streamed bytes, current authorization, checkout, SQL, commit and release; do not wrap execute() and restart its budget. Current authorization precedes checkout. Preserve create-all then assigned fallback, verified account/durable actor/membership, stored-child assigned replay checks, exact original receipts and atomic transaction effects.

Single bearer, application/json, no query selectors, bounded strict131072-byte JSON, safe machine errors/private no-store, bounded acquisition/exclusive connection through repeated cancellation/unwind and normal/exceptional engine disposal. Preserve existing create/replay semantics and domain validation; denial/outage fails closed. Offline-export schema and generate client types through owner tooling, never edit generated files.

Add create transport and Auth-entry consumer using generated types and existing edit/recovery conventions: pin session/org/command/capture/op before await, closed matching v1 capture.create receipt, safe generated errors, <=10s adapter budget/16KiB strict response, cancellation/generation checks, finally release. No retry/refresh/new identity or saved-state effects. Synchronous capture/serialization cannot be preempted; do not promise end-to-end hard wall time or rollback/absence after cancellation.

Synthetic local/CI only, selected source capsules and explicit loopback fixture host. Authority/storage doubles prove integration/control flow, never native permissions/rollback. Preserve concurrent work, historical evidence, retained Docker/resources, dependency baseline including TypeScript7.0.2. Fingerprints/HMAC deferred. No Leave/editor, real accounts/Access, provisioning/migrations, active browser/API startup, deployment/production/pilot or cleanup. Never read/run/copy preexisting untracked apps/kdg-capture/migrations/tests/schema_fixture.py; no whole-silo recursive copies.

## I/O & Edge-Case Matrix

| Case | Expected behavior |
|---|---|
| Authorized create→edit→recovery over HTTP | Create1, edit2, recover original create1/edit2; matching generated client receipts |
| Duplicate create/edit and no-op | Original operation receipt, no duplicate effect; no-op receipt preserves revision |
| Stale revision / wrong receipt target | Safe typed conflict or invalid_response; input unchanged |
| Missing/malformed auth/body/selectors/version | Safe refusal before inappropriate authority/storage work |
| Denied/expired/mismatched current authority | No checkout; no write; stored replay remains protected |
| Acquisition/SQL/commit/release failure, deadline/cancellation | No premature receipt; worker retains connection through unwind; no rollback claim |
| Auth replacement/disposal with late headers/body | Superseded old result, new current execution remains usable |
| Unknown operation | Verified unresolved only from successful authorized recovery; outages never imply absence |

</frozen-after-approval>

## Code Map

Paths below are under apps/kdg-capture.
- `write-candidate/capture_create_handler.py`: existing _authorize/_transaction and safe error map; execute owns a fresh budget and already-open connection, so HTTP must compose the lower-level existing pieces.
- `write-candidate/edit_http.py`, `recovery_http.py`: proven strict request, lazy pool, worker/drain, lifespan and safe-response patterns; preserve existing behavior. Tiny justified local reuse is fine, no generic SDK/DB engine.
- `write-candidate/edit_openapi.py`, `export_edit_openapi.py`, `write-tests/test_edit_contract.py`: offline contract/type generation owner path; inspect actual installer invocation.
- `write-tests/test_*_http.py`, existing create/edit/recovery handler tests: reuse recorded synthetic connection fixtures; characterize before refactoring. Use actual route/authorization/transaction handlers in integration; do not replace the entire business operation with a canned success.
- `web/src/edit.ts`, `edit-entry.ts`, `recovery-entry.ts`, `web/tests/auth-proof.mjs`: established generated transport, pure lifecycle leases and source-bound TS7 harness. Extend selected sources and focused create tests without breaking existing modes.

## Tasks & Acceptance

- [x] `write-candidate/create_http.py`, create OpenAPI/export/schema and generated create contracts: implement POST and executable behavioral tests under write-tests, observing acceptance RED first.
- [x] `web/src/create.ts`, `create-entry.ts`, focused behavioral/type fixtures and auth-proof/tsconfig inclusion: implement complete future-caller create boundary with meaningful RED and focused TDD.
- [x] `web/tests/persistence-http-proof.mjs` plus selected synthetic Python fixture/support: run actual loopback HTTP through candidate POST/PUT/GET and context with existing Auth consumers, shared synthetic transactional storage and synthetic Access. Prove matrix; stop owned processes normally and retain source/log artifacts.
- [x] `docs/PERSISTENCE_HTTP_PATH_EVIDENCE.md`, compact source-bound JSON, append contracts and prepend next-session: exact commands/results, source/log hashes, traceability, honest synthetic/native limits and remaining real gates. Preserve historical bytes. Record scaffold/UI/context/docs/ADR decisions; promote only demonstrated neutral fixes through owners/templates/tests in this item.

Given current admission, when creating/editing/recovering, then typed clients and actual HTTP handlers agree on original identity/receipts. Given denial/staleness/failure, then no stale acknowledgement, leaked metadata or automatic consequential side effect occurs. Given completed local tests, then native/release/real-access qualification stays explicitly unclaimed.

## Implementation Notes

bmad-help selects [BD] Build; no intent gaps or irreversible work. User explicitly approved continued implementation and waived repeated checkpoints, including cohesive larger batch scope. BMAD already rendered once by root. Use dispatch; no further render or commit by implementer. Keep implementation simple and ordinary; no invented workflow/ADR, fingerprint, schema inventory or generic runtime framework. Root owns review and scoped local commit.

## Verification

Pinned Node platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node and Python platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python. Verify retained dependencies; no installs. Observe new acceptance failure before implementation, focused suites first, then affected write-tests (exclude native and forbidden fixture), auth-proof --unit-only, direct create/edit/recovery/entry regressions, strict TS7, offline schema/generated checks and sync-kdg-auth/write/database/native-database --check. Execute persistence-http-proof over loopback with a bounded host lifetime. Retain immutable RED/control/final selected source manifests and logs under platform/deployment/.local/kdg-persistence-http-path-20261026. No backend/native permission or release claim from doubles.

## Review Triage Log

Root owns docs/evidence and broad verification. Explicit synthetic14-module backend198, retained Auth327, direct adapters124, strict adapter types and four parity checks pass. Native-import verifier rejected by automatic approval review; explicit synthetic alternative completes scope. Client80fail/10pass is genuine RED; backend import failure is infrastructure and refusal control a later replay. Create config corrected to adapter-only checks; Auth consumers checked through retained SDK harness. No dependency change.

All three layers completed before triage. Verification-gap reviewer reported none. Each finding checked individually; surviving changes are local schema, fixture, harness and evidence patches with unchanged product intent.

| Finding | Verdict | Evidence and route |
|---|---|---|
| B1 captured_at schema | medium | Runtime _device_time enforces UTC/calendar syntax but new schema only says string. Patch ordinary format/pattern metadata and runtime/schema parity cases; retain runtime ownership of validation. |
| B2 eligibility reference schema | medium | Runtime _nonblank rejects empty/whitespace/NUL; new schema lacks those constraints. Patch string constraints/description and parity tests. |
| B3 answer lone-surrogate schema | medium | Runtime _text UTF-8 encoding rejects unpaired surrogates; schema pattern excludes only NUL. Patch pattern/parity, propagate the same demonstrated defect to sibling edit schema through exporters/generator and focused tests. |
| B4 retained tool paths | low | Proof depends on approved private dependency capsules, so a fresh checkout needs those prerequisites. Patch tracked prerequisite documentation and baseline reference; do not add provisioning/installers or broaden approved dependencies. |
| B5 missing child executable | medium | ChildProcess error event has no handler; spawn failure can bypass failed-proof record. Patch standard error handling and retained negative control. |
| B6 unbounded shutdown request | medium | Exit timeout begins after awaited shutdown fetch, so stalled shutdown fetch is not bounded. Patch request deadline and owned-child termination fallback with honest forced-stop evidence. |
| B7 unknown SQL accepted | medium | Fixture defaults to successful Rows for unmatched statements, masking missing modeling on future handler SQL. Patch explicit known operations/context statements and safe refusal of unknown SQL; not a production schema inventory. |
| B8 synthetic lookup org scope | medium | Child/eligibility/assignment/version branches return facts without p.org check, so wrong-scope SQL would pass this model. Patch scoped recorded lookups and negative tests. |
| B9 commands only private manifest | low | Tracked receipt delegates exact commands to private manifest, limiting committed reproducibility. Direct patch: include exact command/cwd/status/log references in tracked receipt while preserving private manifests. |
| B10 copied edit/PUT test names | low | Create tests retain misleading operation labels; direct rename to create/POST makes failures/traceability accurate. Patch tests only. |
| E1 POST prior-RED claim | false | Cited evidence explicitly labels initial missing-module as infrastructure and API refusal as later replay, never prior behavioral RED. Root records this protocol limitation; no original POST RED timing is claimed. Editing a completed spec task alone is not an implementation fix under this workflow. |

Final audit: all ten surviving review findings patched; E1 refuted by explicit evidence wording, none deferred.199 selected synthetic backend tests,327 compiled Auth/client cases,124 adapter+3 child cases,2 strict fixture guards pass; seven current source-bound loopback requirement groups pass normally. Strict create/edit/recovery TS7.0.2, four scaffold parity and create/edit schema/generated checks pass. No corresponding scaffold child-process helper exists; proof-only helper remains local. Native-import broad verifier excluded after auto-review rejection; no native qualification claim. Original POST ATDD timing remains explicitly limited, later refusal replay not relabeled.
