---
title: 'Protected KDG setup contract and explicit consumer'
type: 'feature'
created: '2026-10-26'
status: 'done'
route: 'dispatch'
baseline_commit: 'faac78ee0da3009ac7b69ca6423a2b74a6139b27'
review_loop_iteration: 0
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/apps/kdg-capture/AGENTS.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Pending-create local Save cannot safely consume setup: no concrete `/provision` producer or validated browser contract exists. Existing history/edit-context applies to server-backed captures only.

**Approach:** Implement and qualify an unmounted candidate current setup API, generated contract, strict transport and Auth consumer. Return exact independently verified capability/child/version evidence and committed opaque eligibility references; do not implement local Save or activate setup.

## Boundaries & Constraints

**Always:** Selector-free private/no-store GET `/api/v1/provision`; bearer-derived fixed organization/account/durable actor/membership. Entry own-read required; check own-edit and create-all/create-assigned independently, preserving actual decisions and exactly seven-day observations. Same account/actor/membership across positive checks. All external waits precede short DB transactions under one original10-second budget through checkout, worker drain, release and serialization. Explicit configured questionnaire identity selects latest immutable published display version. No fabricated server record/revision/audit or authority.

**Never:** UI/editor/Leave, local Save/setup persistence, PWA/shell/startup/queue/sender/service-worker activation; real Auth/Access/accounts, actual PostgreSQL/native-driver/Docker qualification, provisioning/migration execution, deployment/production/pilot/cleanup; fingerprints/HMAC; new dependencies or baseline changes (TypeScript7.0.2 retained). Never read/run/copy/hash `apps/kdg-capture/migrations/tests/schema_fixture.py` or copy the whole silo. Preserve concurrent edits and historical evidence. No remote operations/push.

## I/O & Edge-Case Matrix

| Scenario | Input/state | Expected behavior | Failure handling |
|---|---|---|---|
| Assigned setup | Current read/edit/create-assigned, active same-membership assignments | Exact child/revision/assignment evidence, original published definition, committed unique eligibility refs | No other account/org rows |
| All-create | Verified create-all | All active scoped children, no fabricated assignment | No inferred admin/edit grants |
| Missing capability | Verified edit/create denial | Omit corresponding positive observation; explicit not-permitted/no-eligible/no-published states | Entry denial blocks all setup |
| Verification failure | Upstream unavailable/malformed/foreign identity or any check stale | No partial success/ref issuance | Safe auth/denied/unavailable distinctions |
| Atomic issuance | Child/assignment changes, DB/commit/release failure | Coordinate existing child locks; validate current rows; refs bind account/membership/child/revisions/permission/actor | No successful response before commit/release; no false rollback claim |
| Empty/bounds | No eligible children/version or oversized result | Honest distinct state; bounded complete response, no silent truncation | Typed safe unavailable on excess |
| Client boundary | Foreign/extra/malformed DTO, unsafe caching, slow headers/body, session replacement | Strict closed scope/identity/capability/version/child relationships and limits | No stale publication; lease released once |
| Repeat/read-only effect | Repeated setup | Existing immutable definitions/captures/receipts/history unchanged; separately issued opaque refs grant no authority | No pruning, renewal of unverified rights or credentials returned |

</frozen-after-approval>

## Code Map

- `apps/kdg-capture/docs/contracts.md` sections Initial offline phone setup, Own-capture editing, Prior child eligibility; `docs/epics.md` Story1.4/1.5/2.2: product truth. Story1.4 candidate retains broader installed-device/readiness gates; this is only synthetic contract qualification.
- `write-candidate/capture_create_handler.py`: current Access checker, CreateEvidence, budget and safe worker unwind; `capture_edit_handler.py` independently checks own-edit. Reuse exact Access own_account resource scope, never invent child grants.
- `write-candidate/edit_context.py`, `edit_context_http.py`, `own_observation_openapi.py`: closed observation/schema/error/export/HTTP patterns. Reuse existing Python questionnaire/answer validation; avoid risky unrelated refactors.
- `migrations/candidates/0002_capture_storage.py`: existing questionnaire/version, child, assignment and immutable eligibility columns. Existing runtime lacks eligibility INSERT: do not alter old candidate/history or grants. Record controlled narrow grant migration plus native privilege qualification as activation prerequisites; tests do not establish them.
- `web/src/edit-context.ts`, `edit-context-entry.ts`, `read-validation.ts`, `own-observation.ts`: strict transport, Auth execution fence and validation primitives; generated runtime stays owner-managed.
- `web/tests/persistence-http-fixture.py`, `persistence-child.mjs`: synthetic HTTP fixture/resource ownership patterns. Prefer separate provision fixture/proof; avoid breaking existing explicit selected-source capsules.

## Tasks & Acceptance

**Execution:**
- [x] `apps/kdg-capture/write-tests/test_provision*.py` -- behavior acceptance RED then focused authority/transaction/HTTP/schema tests.
- [x] `apps/kdg-capture/write-candidate/provision*.py` -- closed DTO/current checks/bounded transactional read and eligibility issuance plus explicit HTTP factory. No active app import; membership/child coordination and trusted issuance attribution.
- [x] `apps/kdg-capture/write-candidate/*provision*openapi*`, `contracts/provision-generated/` -- export owning schema and generate client types through existing tool; no handwritten generated files.
- [x] `apps/kdg-capture/web/src/provision.ts`, `provision-entry.ts`, `web/tests/provision*`, `web/tsconfig.provision.json` -- strict complete DTO validation, one request/session lease, actual approved config compilation, focused and synthetic HTTP consumer proof.
- [x] `apps/kdg-capture/docs/` and `web/README.md` -- root records contracts, source-bound evidence and next handoff, preserving old bytes.

**Acceptance Criteria:**
- Given every matrix row, when registered proofs execute, then behavior and safe failure assertions pass with precise commands/source hashes.
- Given the actual synthetic candidate HTTP API, when explicit Auth consumer loads setup, then exact observations/eligible definition and refs reach the consumer without active startup or real services.
- Given existing transport/storage contracts, when affected regression and scaffold parity checks run, then supported behavior remains unchanged.

## Implementation Notes

No human intent gaps or irreversible actions. Candidate DTO field choices/bounds are engineering decisions, documented alongside implementation. Keep this one setup goal; no broader lifecycle. Standing authorization covers routine checkpoints/dirty-tree preservation. Root owns final docs, broad qualification, review and scoped local commit. Workflow already activated; do not start another workflow. Baseline custody: `platform/deployment/.local/kdg-provision-contract-20261026/baseline.json`.

Impacts: KDG domain contract stays local; update scaffold owner/tests only for a demonstrated neutral defect. Shared UI/context unchanged; docs updated; existing ADRs apply, no new decision needed. Explicit eligibility INSERT permission/native effects remain unqualified until a controlled release delivery; candidate must not activate or claim release readiness.

Implementation verification notes: client acceptance RED retained at `client-7cd39d3c-a466-4a99-8dbd-bcc0ff711d2d`; generated DTO/client proof uses approved retained modules and actual config. Extracted questionnaire validator after108 read/history characterization tests passed. Backend review RED retained for empty-message deadline and malformed runtime refs. Large row/Unicode guard tests use scoped controlled clocks after real fake-DB overhead caused deadlines; real deadline/cancellation tests and production budgets are unchanged. Raw interpreter setup failure from resolving the venv symlink is retained; final commands preserve the virtual-environment executable path.

Final qualification:37 jobs pass (87 setup clients,29 setup backend,18 integrated setup groups and all affected regression). Three concrete legacy test timing failures fixed using Node controlled clocks/timers and ordinary fixture budgets, without production changes or expectation relaxation. Domain entry tests are KDG-owned; generated Auth/scaffold tests are unchanged and parity passes. Machine evidence: `apps/kdg-capture/docs/evidence/provision-contract-20261026.json`. Review:7 addressed,4 rejected,2 native findings grouped into one appended deferred item. No actual native/grant/activation claim.

## Spec Change Log

## Review Triage Log

| Finding | Verdict / route | Evidence |
|---|---|---|
| Blind1 native privilege/rollback proof | medium / defer | Synthetic SQL doubles cannot establish native effects. Real DB qualification explicitly excluded here; retain with controlled INSERT grant before activation (same native qualification item as Verification2). |
| Blind2 multi-child coordination | medium / patch | Existing success fixture has one child; add deterministic multi-child locks, assignments, revisions and unique refs. |
| Blind3 later-child failure | medium / patch | Fail after first INSERT; prove safe failure/no commit/transaction unwind, while native rollback remains unclaimed. |
| Blind4 batch/performance redesign | low / rejected |1000 is a complete-response upper bound, not a latency guarantee. Existing original deadline limits execution. No measured native failure supports introducing batching; native load qualification remains before activation. |
| Blind5 size boundary | medium / patch | Constant-only assertion misses actual UTF8 precommit rejection; add legal Unicode oversize and accepted response cases. |
| Blind6 distinct row-count boundary | medium / patch | Duplicate fixture proves overflow before duplicate branch but not successful1000 distinct rows. Add both distinct limits. |
| Blind7 runtime ref format | medium / patch | Model permits1–200 while new issuer/schema/client promise43 URL-safe characters. Align runtime model and regenerate owner output. Historical create refs remain opaque≤200. |
| Blind8 cross-field validators | false / rejected | authorize checks all positive identities before DB; transaction derives assignment shape from exact permission and validated membership, derives state precedence, and generates every expiry by seven-day timedelta. No received DTO can bypass these constructors. Tests exercise these relationships; adding a second policy validator at a trusted output boundary is unnecessary. |
| Blind9 ignored prerequisites | false / rejected | Existing evidence/web README documents retained approved artifacts and clean-checkout limitation; new proof commands are added with this delivery. No install/bootstrap is authorized. |
| Blind10 missing read/history regression | false / rejected |108 tests characterized before extraction; root qualification includes575 compiled clients and all storage/read/history proofs after extraction. Review diff excludes final evidence, not the executed checks. |
| Edges1 empty ASGI messages | medium / patch | request.stream hides immediately returned empty messages; outer timeout cannot interrupt starved timer. Receive directly and enforce original budget each message. |
| Verification1 producer size gap | medium / patch | Pre-verified gap; same size-test root cause as Blind5, exercise >1MiB actual UTF8 before commit. |
| Verification2 latest SQL selection gap | medium / defer | SQL is correct DESC today; canned result dispatch cannot detect ASC mutation. Actual multiple-version query qualification belongs to explicitly excluded native work before activation, grouped with Blind1. |


## Verification

Retained Node26.11.1: `platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node`; Python: `platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python`. Approved modules: `platform/deployment/.local/web-baseline-qualification/new-5/root/node_modules`; API generator: `platform/deployment/.local/scaffold-application/proof-dI2Gy9/root/platform/api-client/src/cli.mjs`. Use existing selected-source proof patterns/Chromium and existing Auth skipLibCheck exception. Synthetic loopback/worker/browser tests may need escalation; no installs. Record RED/GREEN commands, source hashes and exact assertion names beneath `platform/deployment/.local/kdg-provision-contract-20261026/`. Root regression reference: prior `kdg-explicit-edit-delivery-20261026/root-verify/qualified.json`.
