---
title: 'Atomic local Save for completed KDG captures'
type: 'feature'
created: '2026-10-26'
status: 'done'
route: 'dispatch'
baseline_commit: 'd1cffdb0094fb3c17b9ff1085c79bbc2fc0d1159'
review_loop_iteration: 1
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/apps/kdg-capture/AGENTS.md'
  - '{project-root}/apps/kdg-capture/docs/PROVISION_CONTRACT_EVIDENCE.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Completed new observations cannot yet be saved locally using the verified setup contract; the store currently handles server-backed history/edits only.

**Approach:** Extend the isolated IndexedDB owner with atomic setup import, pinned in-memory create handles and completed capture/create-command Save/reopen. Preserve uncertainty under original identities. This is the next storage consumer, without editor or sender activation.

## Boundaries & Constraints

**Always:** Actual closed Provision contract, exact account/org/actor/membership and independent observations. Own-read gates viewing; initial Save needs selected create and child/assignment evidence, bounded by earliest expiry. Own-edit is independent and not required for initial Save. Pin original questionnaire/child/reference; refresh changes future opens only. Distinct capture and operation UUIDs identify one attempted Save. Commit completed record, immutable create action/bytes and definition together before saved feedback. Copy before awaits; retain original input/IDs on unconfirmed completion. Multiple same-child/date records remain valid.

**Never:** Fabricate server revision, server created/updated attribution or Synced; persist unfinished typing/drafts; mutate initial create bytes; activate UI/editor/Leave, sender/queue/browser/service-worker/default-startup/PWA. No real Auth/Access/accounts, native PostgreSQL/Docker work, provisioning/migration execution, deployment/production/pilot/cleanup, new dependencies or fingerprints/HMAC. Preserve approved baseline including TypeScript7.0.2, concurrent edits and historical evidence. Never read/run/copy/hash `apps/kdg-capture/migrations/tests/schema_fixture.py` or copy the entire silo. No push.

## I/O & Edge-Case Matrix

| Scenario | Input/state | Expected behavior | Failure handling |
|---|---|---|---|
| Save/reopen | Current validated setup and completed answers | Original local content and exact generated CreateCommand retained after reopen | Saved locally only after commit |
| Setup ordering | Concurrent refreshes, nullable denied slots, newer independent observations | Store-issued request generation before HTTP; stale result cannot import/unlock/restore; no authority inferred | No replacement of newer evidence or definitions |
| Pinned form | Setup/version refresh after open | Original definition/reference and token observations remain pinned; independently valid current authority also required | New success never extends old token expiry |
| Retry/multiplicity | Same immutable attempt, changed retry, IDs reused or fresh same-date capture | Identical retry idempotent across handles/reopen; changed/colliding attempt refuses; fresh distinct capture succeeds | No extra record/action |
| Form validation | Rating1/false, missing/unknown/invalid answer, hidden false details, invalid date/Unicode or command size | Validate full original definition, strip hidden details before durable identity, enforce131072 UTF8 command limit | No partial Save |
| Authority | Independent read/create/child expiry, assignment loss, known denial, clock jump, logout/account replacement | Affected use blocks; preserve pending bytes and unrelated rights | Failed denial write keeps process latch; only explicit newer verification restores |
| Atomicity | Quota, abort, failure between writes, completion staleness/expiry | No half record/action/definition; no false acknowledgement | Retain original attempt to recover any committed result |
| Compatibility | Populated v1/v2, opaque pending/conflict rows or unknown local versions | Additive schema upgrade and retained fields; safe stale-handle refusal | No deletion/reset or claim of activated browser-release readiness |

</frozen-after-approval>

## Code Map

- `apps/kdg-capture/web/src/history-store.ts`: existing IDB transaction/completion fences, observation clock watermark, read/edit denial generations and immutable definition map. Schema2 needs additive setup/create-action support. Keep local capture separate from actual `baseline`; existing openEdit/prepareEdit continue to refuse pending-only creates.
- `web/src/setup-download.ts` and store denial: HTTP denial publication must atomically compare the current setup generation/nonce before latching or locking. Provide explicit store-owned `denySetup` using existing denial implementation with that comparison in the same transaction. A stale403 is refused; latest403 locks. Reopening a denied store/new entry plus explicit newer restore is the supported recovery.
- `web/src/provision.ts`: validateProvision supplies closed structure, not local time/freshness/order. Import requires an opaque owner-issued refresh ticket minted before request, with durable generation comparison across handles; no generic request engine. A thin explicit setup download may compose existing Auth lease + loadProvision + import under one bounded fence; no automatic use.
- `web/src/create.ts`, `contracts/create-generated/types.gen.ts`: PendingCreate/immutable command shape. `read-validation.ts`: extract/reuse complete original-answer validation after characterization; never manufacture CaptureDetail to validate local input.
- `web/src/own-observation.ts`: closed create/read/edit observation validator. sensible currently assumes non-edit means read: generalize explicitly for supported capabilities and separately validate child window evidence.
- `web/tests/local-edit-save-proof.mjs`, history-store-proof/edit-reconciliation-proof and provision fixtures: selected-source real Chromium IDB, types, rollback/quota/reopen/timing patterns; no silo copies.

## Tasks & Acceptance

**Execution:**
- [x] `apps/kdg-capture/web/tests/local-create-save-proof.mjs` and types -- acceptance RED, then focused matrix cases in real Chromium IDB; characterize risky reused behavior first.
- [x] `apps/kdg-capture/web/src/history-store.ts` plus small local capture validation/types module as needed -- atomic setup/import generation and create handle/Save/read operations, additive stores and original identity recovery.
- [x] `apps/kdg-capture/web/src/` -- explicit request-to-import composition if needed to prove refresh tickets start before HTTP, with one Auth/session/deadline fence; keep unmounted.
- [x] `apps/kdg-capture/web/tests/` -- actual synthetic provision HTTP→Auth→IDB import→Save/reopen proof, strict config and existing storage/transport regression.
- [x] `apps/kdg-capture/docs/` and web README -- root owns final contracts, source-bound evidence and next handoff; preserves earlier bytes.

**Acceptance Criteria:**
- Given each matrix row, when registered proofs run, then required behavior passes with exact commands/source custody.
- Given the actual synthetic setup API, when an explicitly requested setup is imported and a completed capture saved, then reopen returns original local data and one immutable pending create without server provenance.
- Given old supported storage and transport, when affected regression/parity runs, then existing behavior survives.

## Implementation Notes

No human intent gaps or irreversible effects. Standing authorization bypasses routine checkpoints and continues after this slice. Workflow already activated; implement directly, no second lifecycle. Root owns final docs/review/broad verification/commit. Preservation baseline: `platform/deployment/.local/kdg-local-create-save-20261026/baseline.json`.

Impacts: KDG domain validation/authorization stays local. Existing builder-owned IDB helpers reused; promote only demonstrated neutral fixes with owning template/tests. Shared UI/context unchanged; documentation updated; existing ADRs suffice. Local schema/connection compatibility remains synthetic candidate evidence, not browser-update activation.

## Spec Change Log

Review iteration1: B1/E1 exposed missing ticket-aware HTTP-denial implementation guidance. Add the narrow denySetup publication path before the existing denial latch; never let older403 invalidate newer success. Frozen intent unchanged. KEEP all79 focused checks,13 integration groups, existing transaction/completion/clock primitives, immutable pending create shape, additive schema3, strict types and original-answer extraction. Preserve all passing regressions, source custody and old frames. Re-derive store/read-validation/setup-download from original baseline with retained tests; also apply direct verified review corrections B3–B9/B11/V1. Root owns HTTP ordering/denial tests and final qualification/docs.

## Review Triage Log

| Finding | Verdict / route | Evidence |
|---|---|---|
| B1 stale HTTP denial | medium / bad_spec | setup-download called unticketed deny after HTTP; older403 can invalidate a newer committed refresh. Code Map must require ticket-aware denial publication. |
| B2 same-entry restore | false | Explicit partition denial intentionally invalidates the owned handle/generation. Reopen store and construct a new explicit entry; restoreDenied is not a promise to revive stale handles. Add documentation and exercise this supported recovery. |
| B3 create capture/edit-operation collision | medium / patch | saveCreate checked edit_actions only by operation_id; capture_id could reuse an existing edit command identity. |
| B4 edit/create-operation collision | medium / patch | saveEdit checked only edit_actions; newly introduced create_actions exposes cross-command reuse. |
| B5 merged identity binding | medium / patch | Timestamp-only slot preservation can combine previous membership/actor observations with incoming envelope. Preserve only exact identity bindings and validate final assembled setup. |
| B6 child/assignment revision merge | medium / patch | Earlier timestamp with changed revision could be replaced by prior eligibility. Preserve independently newer child evidence only when revision/assignment identity agrees. |
| B7 unsupported create-action rows | medium / patch | readCreateActions promised typed v1 rows without support/identity/serialized checks. Preserve unknown rows but withhold them from supported action output. |
| B8 all/assigned transitions | low / patch | Actual HTTP proof already covers create.all/null assignment; focused transitions deserve direct coverage of the existing selected-permission check. |
| B9 partition tests | low / patch | New operations have explicit scope predicates, but add focused cross-partition ticket/handle/cursor/UUID evidence for these consumers. |
| B10 missing-definition Save rollback | false | Every reachable openCreate follows atomic importProvision that already persists its immutable definition. Save introducing a missing definition requires unsupported external local deletion; existing setup collision/atomic rollback and Save rollback cover reachable writes. |
| B11 fresh-realm reopen | medium / patch | Existing reopen retains module/token objects. Add a fresh page retaining the database, recover original action/identity and retry from durable retained content. |
| E1 stale HTTP denial | medium / bad_spec | Same root cause as B1; denial publication lacks durable latest-ticket comparison. |
| E2 capture/edit operation collision | medium / patch | Same root cause as B3; missing edit_actions capture-ID lookup. |
| V1 HTTP denial verification | medium / patch | Filed verified gap: success/outage/timeout cases do not execute setup access_denied→durable lock. Add actual HTTP denial, old form/read refusal, reopen and explicit restoration. |



Second review, after successful re-derivation:

| Finding | Verdict / route | Evidence |
|---|---|---|
| R2-B1 edit denial before collision | medium / patch | Current-ticket verified null edit evidence was latched only after immutable-definition lookup; a collision could leave old edit handles usable. Move existing latch before unrelated fallible persistence. |
| R2-B2 child loss freshness | medium / patch | A committed omission then older positive child evidence can reuse an old form when revisions coincide. Retain scoped child invalidation/freshness in existing owner metadata/latches, with private reviewed-generation binding. |
| R2-B3 retained reference format | low / patch | New local intents originate from exact43-character setup refs; supported-row validation accepted malformed consistently rewritten refs. Reuse that direct format constraint. |
| R2-B4 complete retained reviewed validation | false | Public LocalCreateIntent exposes content as an opaque string, not a typed ReviewedCreate. supportedCreate validates exposed command/answers/identity; new writes additionally require authentic owner review, and recovery authority compares actor/member to current verified setup. Invalid private reviewed metadata fails closed, grants no authority and is not promised as typed context. No duplicate full local-authority validator is added. |
| R2-B5 committed retry expiry | medium / patch | saveCreate checked original creation expiry before existing immutable result lookup. Exact committed-result recovery needs current own-read only; preserve create/child checks for new writes. |
| R2-B6 in-flight invalidation test | low / patch | Direct predicate test covered preflight false only. Add held-write invalidation and assert no false acknowledgement or partial writes. |
| R2-B7 completion expiry test | low / patch | Existing completion-staleness and separate expiry assertions do not combine completion/expiry. Add that registered boundary and exact committed-attempt recovery. |
| R2-B8 cross-realm full denial | low / patch | Add direct second-realm latest-ticket denial/old-handle refusal/reopened restoration to complement existing shared lock and cross-realm refresh-generation proofs. |
| R2-B9 populated upgrade structures | low / patch | Seed definitions/downloads and v2 edit_actions alongside opaque record for explicit schema3 retention evidence; additive upgrade code remains unchanged. |
| R2-B10 unsupported pagination | low / patch | Add small-limit traversal with unsupported rows between valid actions; assert cursor progress and no skipped valid command. |
| R2-E1 queued denial deadline | medium / patch | lock's separate partitions transaction did not subscribe to execution abort. Queued request could keep refresh/lease pending after deadline. Apply existing transaction abort semantics to this transaction. |
| R2-V1 import publication deadline test | medium / patch | Filed verified gap: HTTP-only timeout never reaches import. Hold real IDB publication after HTTP success, expire execution, release blocker and assert setup unchanged. |

Root follow-up to R2-B2: medium/patch. Process denied state incorrectly won an equal-generation durable restoration from another realm. A concrete two-page RED demonstrated it; prefer durable on equality, retaining strictly newer process failures. Focused two-page restoration now passes while pre-loss form remains invalid. No public surface or further guard added.

## Verification

Approved Node: `platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node`; modules: `platform/deployment/.local/web-baseline-qualification/new-5/root/node_modules`; Python: `platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python` (do not resolve venv symlink). Reuse retained Chromium/tool paths from existing proofs; no installs. Exact RED/GREEN source capsules under `platform/deployment/.local/kdg-local-create-save-20261026/`. Child/browser/loopback proofs may need escalation. Root prior37-job regression references: `platform/deployment/.local/kdg-provision-contract-20261026/root-verify/assembled.json`. No new backend execution needed if existing sources unchanged; never claim actual native permissions/rollback.

Root qualification:15 source-bound commands PASS, including141 focused IDB checks and18
integrated setup HTTP/Auth/IDB groups. Existing87 setup-client,73 edit-delivery,29
delivery HTTP,103 reconciliation,92 edit Save,61 history,575 compiled client checks,
16 prior loopback groups and five scaffold parities pass. Existing342 backend tests
are reused with85 unchanged effective source hashes. Exact commands and source maps
are in the owner machine record. Matrix rows map to named registered checks there.
