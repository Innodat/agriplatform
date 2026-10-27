---
title: 'Inert KDG administrator detail request adapter'
type: 'feature'
created: '2026-10-27'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'c902101acec748ac319fa4134efd8bbb40ba0f45'
context: []
---

<frozen-after-approval reason="standing user authorization for ready synthetic slices without routine approval stops">

## Intent

Add an inert typed consumer for the existing administrator capture detail GET. An explicit current-session request returns a complete validated immutable original-definition snapshot across owners, or a safe typed outcome. This is a technical Story 3.1 subset; the candidate remains unmounted.

## Boundaries & Constraints

Use owner-generated admin detail request/response/error types. Pin authenticated caller, bearer, requested organization and capture before awaits. Server current read.all remains authoritative. A reader may differ from the original owner and executor; preserve original ownership, created_by owner-actor relationship, updated_by and all original questionnaire/answer validation. Never use the reader as the expected owner. Detail has no reader-account echo; publication relies on the pinned authenticated request and current-generation guard, not invented response evidence.

One same-origin GET, private/no-store JSON, redirect refusal, strict duplicate-key/UTF8 parsing and a 512 KiB actual streamed byte ceiling including error responses. A single maximum ten-second execution budget covers fetch/body/validation/publication. Caller cancellation, supersession, ignored aborts, stalled and immediate empty streams discard late data with best-effort body cancellation. Return only stable safe errors; no raw payload, error text or bearer publication/logging, retries, own fallback, writes, storage, offline observation or authority inference.

No UI/editor/Leave, session/Auth entry wiring, startup/browser/worker/queue activation, real services/accounts, native database/Docker, provisioning, migrations, privilege expansion, dependencies, deployment/production/pilot/push or cleanup. Preserve concurrent/historical work, resources and TypeScript7.0.2. Fingerprints/HMAC deferred. Never read/run/copy/hash apps/kdg-capture/migrations/tests/schema_fixture.py.

## I/O & Edge-Case Matrix

| Given / when | Then |
|---|---|
| Authorized reader requests another owner's capture | Exactly one admin detail GET; complete deeply immutable definition/answers/provenance, unchanged owner and actual executor |
| Valid own detail or bigint revision and independently ordered statement timestamps | Accept existing DTO semantics without invented monotonicity or edit authority |
| Invalid local session/scope/options or caller mismatch | Typed refusal before request; no selector or own fallback |
| Foreign capture/org, malformed provenance, unknown fields, invalid definition/answers/JSON/UTF8/headers or excessive bytes | invalid_response, no partial snapshot |
| Known backend status/error identifier or transport failure | Safe typed outcome, no raw error/body/credential, automatic retry or persistence |
| Cancellation, supersession, timeout or late completion during fetch/body/publication | Bounded safe outcome with no stale data; best-effort owned stream cancellation |

</frozen-after-approval>

## Code Map

- New `apps/kdg-capture/web/src/admin-detail.ts`: readAdminCapture and local closed pending/options/result types. Reuse existing strict read-validation helpers and original-detail validator. Validate real owner separately and pass that validated owner as the expected owner to the original-detail validator; this reuses content semantics without changing the own-only wrapper. No existing runtime file changes needed.
- Existing `web/src/audit.ts` demonstrates bounded fetch/body/publication and private request pattern. `web/src/read.ts` and `read-validation.ts` own existing detail validation; preserve their behavior. `contracts/admin-generated/types.gen.ts` owns AdminDetailData/Errors/Response. `write-candidate/admin_http.py`, admin_read.py, admin-openapi.json and docs/contracts.md online organization read section own server behavior.
- New `web/tests/admin-detail.test.mjs`, `admin-detail-adapter.types.ts`, `web/tsconfig.admin-detail-adapter.json`, `web/tests/admin-detail-adapter-proof.mjs`: isolated behavioral/type proof matching audit runner custody with retained Node26.11.1/TS7.0.2, unique output/capsule and exact selected source hashes. Acceptance-only option must run a named cross-owner test.
- Parent owns spec, new docs/ADMIN_DETAIL_ADAPTER_EVIDENCE.md and docs/evidence/admin-detail-adapter-20261027.json, contracts append/handoff prepend, verification and commit. Implementation child owns only five new web files, RED/GREEN proof and implementation report. No commits by child; do not edit existing files. Never alter generated files.

## Tasks & Acceptance

- [x] Record behavioral cross-owner acceptance RED before runtime implementation, using temporary inert stub if required; retain failed sources/logs.
- [x] Build adapter with focused TDD for safety boundaries; retain source-bound strict types/emit and runtime proof.
- [x] Parent inspect actual diff/results and matrix coverage; run affected existing client/backend checks and five scaffold parities.
- [x] Complete three independent review layers, supported fixes, evidence/contracts/handoff and scoped local commit without push.

Given a current caller and authorized cross-owner detail, when explicitly requested, then return only the complete validated immutable snapshot. Given stale, malformed or foreign data, when processing completes, then publish no snapshot.

## Implementation Notes

bmad-help selected [BD] Build after current handoff/contracts and linked adapter/native/backend evidence. Freeform consuming subset; no global/Leave sprint update. No human intent gap or irreversible action. Dirty tree is expected and preserved under explicit user authorization. Five new web files plus five parent documentation/evidence files; standalone API adds no caller/startup integration. Delegated implementation selects gpt-6.1-sol/high; actual model/usage/time unavailable unless exposed. Scaffold: reuse proven neutral primitives; new admin permission/ownership semantics stay KDG-local. Shared UI, agent context and accepted ADRs unchanged; documentation/evidence updated together. No neutral behavior change requiring template edits is currently identified.

## Spec Change Log

## Review Triage Log

## Verification

New isolated adapter proof with retained Node26.11.1/TS7.0.2. Existing audit/read/history client suites, affected administrator backend tests, admin HTTP loopback and owner contract freshness; five adopted scaffold parities. Exact commands/results, source bindings, immutable RED/GREEN logs and traceability in new machine evidence. No root build or native permission claim.

Parent verification passes78 adapter tests,108 existing read/history,73 audit,76 backend,37 loopback checks, owner export and five scaffold parities. Parent inspected source and all matrix rows. Full78-test matrix was written before implementation, but only named cross-owner acceptance executed RED against inert stub. This establishes ATDD RED and prewritten focused tests/GREEN, not separate observed per-boundary TDD cycles. No known runtime defect currently needs correction; do not manufacture one. All failed infrastructure/capsule attempts retained.

Three independent review layers completed before triage: Blind Hunter0 supported findings, Edge Case Hunter[] and Verification Gap0 gaps. No findings to grade, patch or defer. Durable reports are bound in machine evidence. All six matrix rows have executed passing behavioral coverage. Parent source/log audit confirms current implementation, original DTO/helpers, original backend and contract proof sources; 565 preexisting KDG/dependency files remain unchanged, contracts append and handoff prepend preserve historical bytes. No Docker/native database/resource command ran. Scoped local commit follows; no push. Selected implementation gpt-6.1-sol/high; actual model/token usage/model-only time unavailable. Test/tool waits are in command records; sandbox EPERM/timeout/listener refusal and missing capsule dependency attempts retained without changing runtime expectations.
