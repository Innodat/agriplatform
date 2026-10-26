---
title: Own-edit execution through current Auth admission
created: 2026-10-26
type: feature
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: 95e54f90b37d7b7c0c00c0a4c7ee3acdd29f5a43
context:
  - apps/kdg-capture/AGENTS.md
  - apps/kdg-capture/docs/EDIT_ADAPTER_EVIDENCE.md
  - apps/kdg-capture/docs/RECOVERY_ENTRY_EVIDENCE.md
---

<frozen-after-approval reason="human-owned intent">

## Intent

Bind KDG's existing edit adapter to the existing Auth entry execution lease. A future caller can execute an original edit only under current admitted account/organization, without supplying or caching bearer authority or introducing a second session lifecycle. This is separately imported candidate code, unconnected to browser/editor/startup.

## Boundaries & Constraints

Reuse createAuthEntry/acquireExecution and editCapture; hide the raw lease API on this consuming entry. Pin configuration and compare pending account/org with admitted session/context and configured org before transport. Snapshot pending input through the adapter before awaiting. Release each acquired lease in finally, including invalid inputs/errors. Recheck lease freshness before returning; replacement returns superseded even when an adapter result is ready. Do not change authorized state/publications in response to operation results.

Retain adapter original-operation/capture binding, exact revision/conflict typing, strict safe responses, one same-origin PUT, body limits and maximum10-second deadline. Owner refresh, account/session replacement, retry, sign-in/out, password recovery, offline and disposal invalidate current work through the existing lifecycle. A→B→A never revives old authority. Completing one request leaves other current requests usable. Organization change needs disposal/replacement of fixed-org owner. Current result is an observation at completion, never cached future authority.

Synthetic local/CI only. No automatic retry/recovery, Auth refresh/sign-in triggered by editing, new operation, saved-input/store/queue mutation, Synced feedback or rollback/absence claim. No real Auth/accounts/Access, Docker/native, Leave/editor, browser or API startup activation, provisioning, migration, deployment/production/pilot or cleanup. Preserve concurrent changes, historical evidence, resources and dependency baseline including TypeScript7.0.2; fingerprints/HMAC deferred. Never read/run/edit preexisting untracked migrations/tests/schema_fixture.py or hand-edit generated files.

## I/O & Edge-Case Matrix

| Case | Expected behavior |
|---|---|
| Current admission + original edit | One pinned PUT, original matching compact receipt; no additional SDK calls/publications |
| Not admitted/disposed or mismatched account/org | Superseded or safe invalid_request; no write |
| Invalid runtime input/accessor | Safe result, no write, lease released |
| Refresh/account/retry/sign-in/out/recovery/offline/disposal | Old headers/body results suppressed; transport aborted; no revival after A→B→A |
| Refreshed current admission | Fresh bearer used; disposed old org owner cannot edit |
| Conflict/safe denial/malformed response/network/deadline | Existing typed safe result, input and admission preserved; no retry/Auth side effects |
| Concurrent calls + completion/timeout | Each releases its own lease; other current work survives |
| Caller/config mutation or reentrant invalidation | Original snapshot preserved or superseded without stale write/publication |

</frozen-after-approval>

## Code Map

All paths below are under apps/kdg-capture unless stated.
- `web/src/recovery-entry.ts`, `web/tests/recovery-entry.test.mjs`, `web/tests/recovery-entry.types.ts`: proven minimal owner-wrapper and compiled fixture pattern; reuse, do not refactor recovery.
- `web/src/auth-entry.ts`, `web/src/auth/lifecycle.ts`: existing createAuthEntry and generated acquireExecution lease; lifecycle already owns invalidation. Managed source comes from platform/builder-cli/templates/application/web; neutral fixes must update owner/template/generated tests in this item.
- `web/src/edit.ts`, `contracts/edit-generated/types.gen.ts`: existing synchronous snapshot and typed transport/result contract. Keep its semantics; no duplicate response/parser/permission logic.
- `web/tests/auth-proof.mjs`, `web/tsconfig.auth.json`: retained strict TS7/SDK source capsule and synthetic unit proof; add new source/type/test inclusion. Unit-only execution starts no browser/listener. Existing retained tool paths/dependency checks remain.

## Tasks & Acceptance

- [x] `web/tests/edit-entry.test.mjs`: meaningful behavioral RED against explicit non-dispatching wrapper stub, then focused TDD for matrix. Capture exact stub/tests before mutation; characterize any discovered neutral regression before correction.
- [x] `web/src/edit-entry.ts`: minimal createEditEntry consumer using current lifecycle and adapter, with configurable editTimeoutMs; no other runtime integration.
- [x] `web/tests/edit-entry.types.ts`, `web/tsconfig.auth.json`, `web/tests/auth-proof.mjs`: strict consuming fixtures for generated command/conflict narrowing and hidden lease; add capsule paths and focused `--edit-entry-only` test option that skips browser/listeners. Preserve existing unit/browser options and source-bound evidence.
- [x] `docs/EDIT_ENTRY_EVIDENCE.md`, `docs/evidence/edit-entry-20261026.json`, append `docs/contracts.md`, prepend `docs/next-session.md`: exact commands/results, hashes/capsules, traceability and qualification limits. Preserve historical prefix/suffix byte-for-byte.

Given current admission, when editing, then only the pinned original command can receive its matching receipt. Given a replaced lease at any phase, when work settles, then no receipt/error escapes from the old execution. Given current failures/conflicts, then input remains intact and no authentication or consequential side effect is inferred.

## Implementation Notes

bmad-help selects [BD] Build. No intent gaps or irreversible actions; cross-file runtime/type/proof integration uses dispatch. User next authorizes the proposed slice and previously waived routine approval halts; dirty concurrent work is preserved. BMAD rendered once by root; do not render it again. Root owns final review and scoped commit; do not commit. Existing lifecycle online is fixed at construction; the current host handles offline by disposal/recreation. Qualify offline with disposed prior owner plus online:false replacement, without adding a connectivity API or browser wiring. Record scaffold/shared-UI/context/docs/ADR impacts; no new neutral pattern is expected, but propagate a demonstrated neutral fix through its owner/tests if discovered.

## Verification

Use pinned Node platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node, no installs. First run new acceptance only via auth-proof --edit-entry-only; observe behavior failure, not missing-module/compiler failure. Then full auth-proof --unit-only (strict retained TS7.0.2, compiler negative control, compiled consumer/Auth/generated lifecycle tests), direct --test --test-isolation=none edit/recovery/entry tests, strict tsc edit/recovery configs and sync-kdg-auth/write/database/native-database --check. Run scaffold auth-pattern.test.mjs only if neutral lifecycle/template changes require it. No browser/native/backend qualification claim. Retain immutable RED/green source/log capsules under platform/deployment/.local/kdg-edit-entry-20261026, with requirement mapping and exact source/log hashes.

## Review Triage Log

Root acceptance audit: inspected owned diff and every matrix row against executed31 consumer cases. All passed with no skips; full compiled suite230 and direct affected124 passed. Verified514 retained proof-file hashes,22 final-source hashes,8 final log hashes and historical contracts prefix/handoff suffix. Repeated capsule inventories were compacted into hashed retained manifests; the expanded original record remains intact privately. No runtime/template/generated/dependency changes beyond the new consuming wrapper and proof integration.

All three review layers completed before triage. Edge-case and verification-gap reviewers reported no findings. Blind findings individually verified below; all are small qualification/documentation corrections with no runtime intent or public surface change.

| Finding | Verdict | Evidence / route |
|---|---|---|
| B1 combined mode executes zero cases | medium | acceptance-only applies an old test-name filter even when edit-entry-only selects a disjoint test file, allowing zero selected cases to exit0. Patch explicit edit-mode precedence and execute the combined flags to prove31 cases run. |
| B2 subset proof metadata ambiguous | low | result.json contains generic sdk_session_tests and lacks selected mode/files/counts, so consumers of that artifact alone cannot distinguish the new subset. Patch selected mode and executed-test metadata; existing logs remain count authority. |
| B3 replacement organization never admitted | medium | Replacement fixture uses org:B but returns an ORG-scoped context, so it only proves refusal. Patch fixture/test to admit B, accept its B-scoped edit and keep disposed old owner unusable. |
| B4 offline transition split across cases | low | Parameterized offline is disposal alone; offline replacement is tested separately without in-flight work. Direct test correction combines the documented disposal/replacement transition and late old response. Patch. |
| B5 pending/denied/unavailable admission | medium | Current consuming tests cover before-start/disposed but lack pending context and completed denial/outage contexts. Existing lifecycle protects these; patch consuming no-PUT qualification for each state. |
| B6 edit timeout option boundaries | low | Only valid short deadlines are exercised; invalid per-entry editTimeoutMs reaches existing adapter refusal but is unqualified through this wrapper. Patch invalid-value cases with no PUT, current admission retained and independent valid work unaffected; release remains in finally. |
| B7 wrapper pre-capture deadline wording | low | Pending spread precedes adapter deadline selection; current evidence can be read as bounding that synchronous wrapper capture too. Patch wording: adapter budget begins after wrapper capture, synchronous work is not preemptible. No second deadline/lifecycle. |

Final root audit: runtime wrapper/adapter/lifecycle unchanged after review. Combined flags execute38 consumer tests; full compiled Auth237 and direct regressions124 pass with zero failures/skips. Strict TS7.0.2 edit/recovery and four scaffold parity checks pass; legacy acceptance-only also passes one selected case. All seven findings patched, none deferred. Final proof includes selected mode/files/counts and preserved historical records. No Docker/native/browser/startup/real-access/dependency actions.
