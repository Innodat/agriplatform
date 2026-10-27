---
title: 'Inert KDG administrator history request adapter'
type: 'feature'
created: '2026-10-27'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '11a4ec24ea3a72c1cebcf32e9fcb6ed575ff7298'
context: []
---

<frozen-after-approval reason="standing user authorization for ready synthetic slices without routine approval stops">

## Intent

Consume the existing administrator history GET with an explicit current-session request returning one complete validated immutable organization page across owners. This bounded Story3.1 consumer remains inert and unmounted.

## Boundaries & Constraints

Use owner-generated AdminHistory request/response/error types. Pin caller, bearer, organization, inclusive dates, limit and optional cursor before awaits. Default limit30/max100. Server current read.all remains authoritative. Preserve every original owner, original-definition snapshot and actual creation/update provenance. Never equate the reader with the owner or infer offline/edit authority.

Validate closed canonical base64url cursor shape/version/read.all/caller/org/dates/limit and canonical microsecond UTC position. Pages must echo request context, contain unique captures in strictly descending creation-time/ID order below any supplied position, respect inclusive observation dates and retain complete original-detail validation. Continuation must match the last included row; short byte-limited pages are legal. Empty terminal pages are legal. Own/all cursors remain incompatible. No invented snapshot, historical actor names or signature requirement.

One same-origin private/no-store JSON GET with redirect refusal. Strict duplicate-key/UTF8 parsing, 2MiB actual streamed page ceiling including errors, existing512KiB per-detail semantic byte limit. One maximum10s deadline through fetch/body/validation/publication; caller cancellation, supersession, stalled/ignored abort and immediate-empty streams discard late data with best-effort owned-body cancellation. Stable safe typed outcomes expose no raw error/body/bearer. No retries, automatic pagination, fallback, persistence or admission inference.

No UI/editor/Leave, Auth/session/startup/browser/worker/queue activation, real services/accounts, native database/Docker, provisioning/migrations/privilege expansion, dependencies, deployment/production/pilot/push or cleanup. Preserve concurrent/historical work, resources and TypeScript7.0.2. Fingerprints/HMAC deferred. Never read/run/copy/hash apps/kdg-capture/migrations/tests/schema_fixture.py.

## I/O & Edge-Case Matrix

| Given / when | Then |
|---|---|
| Current reader explicitly requests first/cursor pages across owners | One admin GET, complete deeply immutable page, original owners/executors and tied-time ID order preserved |
| Empty terminal or short byte-limited page | Accept valid owner semantics; continuation matches last included row |
| Invalid local caller/scope/options/dates/limit/cursor or own cursor | Typed refusal before dispatch; no selector or own fallback |
| Foreign echo/item, duplicate/out-of-order rows, invalid position/continuation/content/provenance/JSON/UTF8/headers/bytes | invalid_response; no partial page |
| Known backend status/error or transport failure | Safe typed result without raw content, retry or persistence |
| Cancellation/supersession/timeout or late completion | Bounded safe outcome, no stale publication; best-effort stream cancellation |

</frozen-after-approval>

## Code Map

- New web files under `apps/kdg-capture/`: `web/src/admin-history.ts`, `web/tests/admin-history.test.mjs`, `web/tests/admin-history-adapter.types.ts`, `web/tsconfig.admin-history-adapter.json`, `web/tests/admin-history-adapter-proof.mjs`. Implementation child owns only these five files and no commits. Parent owns documentation/evidence, qualification and review.
- `web/src/admin-detail.ts` and `audit.ts`: reuse established bounded request/publication pattern without modifying prior consumers. `history.ts`: own-page cursor/order semantics, but its observation and owner predicate cannot be reused as administrator authority. `read-validation.ts`: reuse strictJSON, object, date, id, token, validateDetail, freeze and safe error mapping. Validate each actual owner before passing it into complete-detail validation.
- `contracts/admin-generated/types.gen.ts`: AdminHistoryData/Errors/Response authoritative DTOs. `write-candidate/admin_read.py`, `capture_history.py`, `admin_http.py`, admin-openapi.json and docs/contracts.md online organization read section own server behavior. No generated-file edits.
- Proof runner should follow `admin-detail-adapter-proof.mjs`: retained Node26.11.1/TS7.0.2, unique retained source capsule/output/logs, selected source hashes, acceptance-only named cross-owner pagination test. Existing parent machine evidence lists affected backend/HTTP/parity commands.

## Tasks & Acceptance

- [x] Record cross-owner pagination acceptance RED before implementing runtime; retain failed source/logs (temporary inert stub permitted).
- [x] Implement adapter and focused TDD with behavioral/type coverage of every matrix row and original owner contracts.
- [x] Parent inspect actual diff/results; run affected existing client/backend/HTTP checks, owner freshness and five scaffold parities.
- [x] Complete independent review layers, supported fixes, evidence/contracts/handoff and scoped local commit without push.

Given current caller and valid cross-owner pages, when requested explicitly, then return only the validated immutable page. Given stale, malformed or foreign data, when request processing completes, then publish no page.

## Implementation Notes

Freeform consuming subset; global Leave sprint context is unrelated. Existing handoff authorizes this ready synthetic continuation and preservation of the expected dirty tree; no routine approval stop. Intent gaps:none; irreversible actions:none. Scaffold:reuse proven primitives; permission/owner/page semantics stay KDG-local. Shared UI, agent context and ADRs unchanged; docs/evidence update together. No neutral behavior change identified. Implementation selects gpt-6.1-sol/high; actual model/usage/time unknown unless exposed.

## Spec Change Log

## Review Triage Log

## Verification

Use isolated adapter strict types/emit/behavior proof, existing admin-detail/audit and own-history/read regressions, affected administrator backend tests and synthetic loopback, owner OpenAPI freshness and five adopted scaffold parities. Record exact commands/results and requirement mapping in docs/ADMIN_HISTORY_ADAPTER_EVIDENCE.md and docs/evidence/admin-history-adapter-20261027.json. No root build or native permission claim.

Parent inspected all five files and executed 121/121 adapter tests with strict types/emit. Every matrix row is covered and passing. Prior client regressions pass; backend and final evidence pending. RED was observed for named cross-owner acceptance only; broader tests ran GREEN, not individually observed RED. A copied detail test incorrectly rejected an arbitrary valid same-org capture ID; corrected to invalid UUID because list selection has no requested capture ID. Failed attempt retained; no runtime change dismissed an unexplained failure.

Final parent qualification passes121 new adapter tests,259 existing client tests,114 backend tests,37 HTTP checks, owner freshness and five parities. Three independent review layers completed: Blind Hunter0 supported findings, Edge Case Hunter[], Verification Gap0 gaps; nothing to triage, patch or newly defer. Durable review reports are bound in machine evidence. Parent inspected source/diff and passing coverage for all six matrix rows. No runtime source changed during review. Expected dirty tree and historical resources/evidence preserved; no prohibited fixture access or Docker/native database commands. Scoped local commit follows without push. Selected implementation gpt-6.1-sol/high; actual model/token usage/model-only elapsed unknown. Parent command/test waits are recorded; harness/sandbox failures retained and explained in evidence.
