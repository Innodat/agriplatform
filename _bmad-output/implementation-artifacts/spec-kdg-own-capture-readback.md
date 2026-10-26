---
title: 'KDG protected current own-capture readback'
type: 'feature'
created: '2026-10-26'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '6c406485be200417e6857b0b935e4f400fe878cc'
context:
  - '/home/ck/repos/innodat/agriplatform/AGENTS.md'
  - '/home/ck/repos/innodat/agriplatform/apps/kdg-capture/AGENTS.md'
  - '/home/ck/repos/innodat/agriplatform/apps/kdg-capture/docs/next-session.md'
---

<frozen-after-approval reason="human-owned intent — continuation authorized without routine approval stops">

## Intent

Current create/edit/recovery candidates return receipts, but cannot retrieve the saved observation and its original questions. Implement protected current-own capture detail through an explicit candidate GET, generated contract, isolated transport/Auth consumer and synthetic loopback proof after creation and editing.

## Boundaries & Constraints

Always recheck current fixed-organization `kdg_capture.capture.read.own` authority and verified durable actor; select only the original account owner's current record. Return the authorized child label even after unassignment/inactivation and the exact original questionnaire definition, identifiers and version. Retain stored provenance without inventing actor names. Reuse existing read-only transaction, deadline, safe-error and exclusive worker/release patterns. Readback never confirms an uncertain write, marks it Synced or grants later write authority.

Synthetic local/CI only. No native/DB/Docker qualification, migrations, provisioning, browser/editor/queue/default-startup activation, Leave, real accounts/Access, deployment/pilot/production or cleanup. No listing/history pagination or offline cache/observation renewal yet. Fingerprints/HMAC deferred. Preserve historical evidence, concurrent changes/resources and dependency baseline including TypeScript7.0.2. Never read/run/copy/edit untracked `apps/kdg-capture/migrations/tests/schema_fixture.py`; copy selected sources only. Generated files through owning exporters/templates. No dependency installation or broad native-importing suites.

## I/O & Edge-Case Matrix

| Scenario | State | Expected behavior |
|---|---|---|
| Current own record | Valid current read authority | GET detail with observation/date/answers, current decimal revision, original immutable questionnaire and child label |
| After edit | Current revision2, recovered original receipt1 | GET current revision2; original receipt remains1; no operation mutation |
| Inactive/unassigned child | Original owner still authorized | Detail readable; no create/edit/eligibility prerequisite |
| Missing/foreign record | Wrong account/org or absent ID | Indistinguishable safe404; explicit org/account query predicates |
| Auth/actor failure | Missing, denied, stale or unverifiable evidence | Existing safe typed errors; no unauthorized snapshot or checkout before authorization |
| Bad request | Malformed ID, extra query/body, bearer issues | Strict boundary rejection; private/no-store response |
| Invalid storage | Broken definition/answers/provenance or oversized result | Safe unavailable response, no partial snapshot or internal payload |
| Deadline/cancellation | Access/acquire/read/release stalls or cancellation | One bounded operation; worker retains connection ownership until unwind; no late success |
| Client/Auth fence | Wrong identity, malformed/duplicate/oversized response, cancellation/account switch/release failure | Safe failure; no snapshot published after freshness fence; release lease exactly once |
| Valid client result | Original definition and current detail | Generated contract consumed, immutable validated snapshot; one request, no retries or write effects |

</frozen-after-approval>

## Code Map

- `apps/kdg-capture/docs/contracts.md` own-read/history sections; `docs/epics.md` Story1.6 and2.1: original definition/current own detail; later2.4 keeps audit chrome out of routine UI.
- `write-candidate/operation_recovery.py`, `recovery_http.py`: current read.own authorization, read-only engine, safe HTTP and bounded worker ownership.
- `write-candidate/capture_create.py`, `capture_edit.py`, `api/questionnaire.py`, `api/capture_commands.py`: persisted fields and authoritative definition/answer validation.
- `migrations/candidates/0002_capture_storage.py`: existing scoped capture/child/questionnaire_version columns and read policy; no migration needed.
- `web/src/{create,create-entry,recovery,recovery-entry,edit,edit-entry}.ts`: isolated transport/Auth lease patterns.
- `web/tests/{auth-proof,persistence-http-proof}.mjs`, `persistence-http-fixture.py`: selected immutable source capsules, synthetic SQL model and real loopback route/client proof.
- `write-tools/transaction_context.py`: generated neutral owner; scaffold changes only if a concrete reusable defect is found.

## Tasks & Acceptance

**Execution:**
- [x] Add focused Python own-read DTO/handler/GET/exporter/schema tests under `write-candidate/` and `write-tests/`. Use one scoped joined SELECT for consistent current capture, child display_name and original version; no lock/external wait in transaction. Reuse trusted definition/answers validators and canonical positive bigint strings. Exclude eligibility/member refs, operation outcomes and revision archives from DTO. Enforce bounded512KiB response.
- [x] Generate `contracts/read-generated/` with owner API-client CLI. Add `web/src/read.ts`, `read-entry.ts` and focused transport/Auth/strict TypeScript tests. Validate bounded strict UTF8 JSON and identity/version relationships, immutable snapshot, existing signal/generation/deadline fences and lease cleanup. Avoid a generic SDK/schema engine.
- [x] Extend selected-source Auth proof and synthetic persistence loopback fixture/proof for GET before/after edit, original questionnaire and receipts, wrong-owner denial and safe failures. SQL double must reject unexpected statements and model stored provenance accurately.
- [x] Cover every matrix row with executed tests. Observe genuine behavioral ATDD failure using importable non-dispatching stub before implementation; import/compiler failures alone are infrastructure failures. Use focused TDD inside.
- [x] Root coordinator owns final `docs/OWN_CAPTURE_READBACK_EVIDENCE.md`, source-bound JSON evidence, appended contracts, prepended next-session, complete verification/review and scoped local commit. Implementer reports exact red/green logs, paths and limits; does not commit or modify these final docs.

**Acceptance Criteria:**
- Actual loopback HTTP runs client/Auth and real GET handler with synthetic authority/storage, showing create/read/edit/read and original receipt recovery without renewing write authority.
- Existing create/edit/recovery behavior, release protection, generated parity and approved dependencies stay intact. No startup wiring or actual PostgreSQL qualification is claimed.
- Record scaffold, shared UI, agent context, documentation and ADR impacts. Keep domain readback local; promote only a demonstrated neutral fix through owner/templates/tests in this delivery.

## Implementation Notes

Continuation scope selected using bmad-help; implementation approved by persistent continuation authorization. Routine gates skipped per user instruction. Agent may choose internal DTO names and file factoring consistent with these contracts.


Final review patches: compact UTF8 round-trip; aware timestamp normalization; Python nonblank parity; integer error metadata; serialization before final budget; exact wire bound and complete Auth validation freshness. Three review lenses completed; nine addressed, one false, B9/VG1 grouped into one native qualification prerequisite recorded in deferred-work. No new shared template/UI/context/ADR decision required.

Final coordinator verification:240 synthetic backend,399 compiled Auth/client,179 direct adapter/context/child and3 fixture guard tests pass; nine loopback groups pass; strict TS7.0.2/four adapter configs, eight owner schema/client checks and four scaffold parities pass. Sources unchanged during final executions. Exact commands/results and retained earlier timeouts/unchanged40ms timing-test failure are in `platform/deployment/.local/kdg-own-capture-readback-20261026/root-verify/post-review-commands.json`. Final source capsule is under `root-post-review/`. All matrix rows have executed passing coverage (traceability in readback evidence); native SQL join qualification is explicitly deferred, not claimed.

## Spec Change Log

## Review Triage Log

All three layers completed before triage: blind10 findings, edge0, verification1.

| Finding | Verdict / route | Evidence |
|---|---|---|
| B1 Unicode definition expansion | medium / patch | `_snapshot` re-encodes stored JSON with default ASCII escaping/spacing before the128KiB parser limit. A valid compact multilingual definition can exceed that artificial size; use compact UTF8 and a round-trip regression. |
| B2 non-UTC DB timestamps | medium / patch | PostgreSQL timestamptz may return an aware nonzero-offset datetime under session timezone; no engine UTC setting exists. Normalize aware values to UTC; continue rejecting naive values. |
| B3 whitespace mismatch | medium / patch | Client trim treats FEFF as blank but Python strip does not, while Python treats0085/001c as blank. Valid persisted answers/labels can be rejected; mirror existing backend whitespace semantics with parity cases. |
| B4 blank text schema | medium / patch | New read schema TextAnswer only limits length/Unicode, while validate_answers rejects blank text. Add the direct nonblank constraint and schema parity tests. |
| B5 fractional error code | low / patch | New read parser accepts finite1.5 while generated ErrorEnvelope code is int. A direct integer predicate correction prevents malformed responses; no API change. Existing sibling consumers have the same pre-existing predicate, without a scaffold owner. |
| B6 inner join hides missing related rows | false / reject | Same-org child/version FKs are NOT NULL and ON DELETE RESTRICT (0002 lines112-115); their SELECT RLS uses the same verified org/account/actor mode scope without an extra filter (lines260-285). An authorized existing capture cannot lack these joins under the ordinary constrained schema. No broken-integrity bypass is demonstrated; do not add speculative queries/guards. |
| B7 serialization after budget | medium / patch | FastAPI revalidation/serialization follows the route's final budget check. Construct the validated body response before that check; demonstrate expiry during serialization and suppress success. No ASGI network-completion promise. |
| B8 backend byte boundary test | low / patch | Client tests exact524288/+1 bytes; backend only tests an oversized result. Add an actual response byte-boundary case including multibyte data without changing accepted limits. |
| B9 native SQL proof missing | medium / defer | SQL equality doubles cannot establish executable PostgreSQL joins or role permissions. Native qualification is explicitly excluded by current user intent and every evidence limit; retain this activation prerequisite. |
| B10 evidence pending versus completion | low / patch (root) | During review the source-bound machine record explicitly has pending backend/review status. Root must reconcile final results and qualification limits before marking done; retain failed attempts. |
| R1 stale validation result | medium / patch | Root traced a pending getter that replaces Auth then throws: read-entry catches invalid_request without the else-branch freshness check. Add the already proven finish-before-release check to every branch and an accessor-triggered replacement regression. |
| VG1 original-version join substitute | medium / defer | Preverified gap: deleting the original-version join predicate would not change the prepared SQL-double rows. Same native qualification prerequisite as B9; add a focused two-version actual PostgreSQL proof only in authorized native work. |


## Verification

Use retained Python `platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python` and Node `platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node`. Retained owner generator: `platform/deployment/.local/scaffold-application/proof-dI2Gy9/root/platform/api-client/src/cli.mjs`. No install.

- Focused new Python/read transport/Auth tests first; source-bound behavioral red and green logs, strict TypeScript7.0.2 and generated schema/client freshness checks.
- `web/tests/auth-proof.mjs --unit-only` and selected persistence loopback proof; direct create/edit/recovery regressions as applicable. Adapter tsconfig extends existing base; Auth entry compiled through retained proof SDK.
- Synthetic Python suite explicitly names `test_capture_create test_capture_create_handler test_capture_edit test_capture_edit_handler test_create_contract test_create_http test_edit_contract test_edit_export test_edit_http test_operation_outcomes test_operation_recovery test_owner_context test_recovery_contract test_recovery_http` plus new read modules. Exclude native/schema/commit qualification modules.
- All four builder `sync-kdg-{auth,write,database,native-database}.mjs --check`; private capsules under `platform/deployment/.local/kdg-own-capture-readback-20261026`; preserve prior docs by prefix/append, record exact commands/results and source/log hashes.
