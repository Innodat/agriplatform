---
title: 'Inert KDG administrator edit-context request adapter'
type: 'feature'
created: '2026-10-27'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '651ba0d925e7f741d2c52e5113daeadcbe027671'
context: []
---

<frozen-after-approval reason="standing authorization for remaining ready synthetic administrator consumers, up to three deliveries">

## Intent

Consume the existing administrator edit-context GET explicitly, returning a complete immutable original-version context across owners for the current online administrator. This is one inert Story 3.2 request consumer, with no mounting or integration.

## Boundaries & Constraints

Use owner-generated AdminEditContext request/response/errors. Pin caller, bearer, organization and capture before awaits. Server current read.all AND edit.all remains authoritative; local freshness is no authorization. Validate the closed context with exactly capture and editable_fields, ordered observation_date/answers. Preserve complete original definitions, answers, original owner and actual update executor. The reader need not be the owner. No own-only observations, offline leases, actor labels, impersonation or edit/recovery effect.

One same-origin private/no-store JSON GET, redirect refusal, no body/query/selectors. Strict duplicate-key/UTF8/closed-shape parsing; 544KiB actual streamed context/error ceiling and 512KiB semantic capture ceiling. One maximum10s deadline through fetch/body/validation/publication; cancellation, supersession, ignored abort, stalled or immediate-empty streams discard late results and best-effort cancel owned bodies. Safe immutable typed outcomes expose no raw content/bearer. No retry/fallback/persistence/admission inference.

Preserve concurrent/historical work, retained resources and TypeScript7.0.2. No UI/editor/Leave, Auth/session/startup/browser/queue/worker activation, real services/accounts, native database/Docker, provisioning/migrations/privilege expansion, dependencies, deployment/production/pilot/push or cleanup. Fingerprints/HMAC deferred. Never read/run/copy/hash apps/kdg-capture/migrations/tests/schema_fixture.py.

## I/O & Edge-Case Matrix

| Given / when | Then |
|---|---|
| Explicit current cross-owner or own-owner request | One admin GET; complete deeply immutable original context and actual executors retained |
| Invalid local session/caller/scope/options or extra selectors | Safe typed refusal before dispatch; no own fallback |
| Foreign/malformed capture, wrong editable fields, observations, content or provenance | invalid_response with no partial context |
| Wrong headers/status/error/JSON/UTF8 or excessive actual/semantic bytes | invalid_response; supported status/ID pairs yield safe typed errors |
| Transport fails or response stalls | Bounded verification_unavailable; no retry or persistence |
| Cancellation, supersession, timeout, late completion or empty-chunk starvation | No stale publication; owned-body cancellation attempted |

</frozen-after-approval>

## Code Map

- Implementation owns only five new files: apps/kdg-capture/web/src/admin-edit-context.ts, web/tests/admin-edit-context-adapter.test.mjs, web/tests/admin-edit-context-adapter.types.ts, web/tsconfig.admin-edit-context-adapter.json, web/tests/admin-edit-context-adapter-proof.mjs. No commits. Parent owns all docs/spec/evidence, qualification/review and commits.
- web/src/admin-detail.ts supplies current bounded transport and cross-owner validation pattern; read-validation.ts supplies strictJSON, object, id/token, validateDetail, freeze, errorResult and Frozen. Reuse without modifying existing consumers/primitives. Own edit-context.ts illustrates wrapper validation but own observations are forbidden here.
- contracts/admin-edit-context-generated/types.gen.ts supplies AdminEditContextData/Errors/Response. write-candidate/admin_edit_context_http.py and docs/contracts.md online administrator context section own runtime semantics and byte limits. No generated-file edits.
- web/tests/admin-detail.test.mjs and admin-detail-adapter-proof.mjs supply focused coverage/proof patterns. Proof must use retained Node26.11.1/TS7.0.2, unique retained source capsule/logs/result JSON and explicit named cross-owner acceptance-only mode. Include every compile/runtime dependency in capsule/source bindings. Test owner freshness and five adopted scaffold parities on parent.

## Tasks & Acceptance

- [x] Observe named cross-owner acceptance RED against inert stub before runtime implementation; retain failing source/logs.
- [x] Implement adapter and focused behavioral/type coverage for all matrix rows in the five owned files.
- [x] Parent inspect actual diff and results; qualify affected prior client/backend/HTTP and freshness/parities.
- [x] Complete three independent review layers, corrections, delivery evidence/contracts/checkpoint and scoped local commit.

Given a current administrator explicitly requests context, when a complete valid response arrives, then return only the pinned immutable context. Given stale or foreign data, when the request finishes, then publish no context.

## Implementation Notes

Freeform ready consumer under standing batch authorization; expected dirty tree is preserved. No intent gaps or irreversible actions. Scaffold: reuse proven neutral primitives; all-edit/context semantics stay KDG-local. Shared UI, agent context and ADR unchanged; documentation/evidence update together. No neutral pattern change identified. Implementation selected gpt-6.1-sol/high; actual model/usage/elapsed unknown unless exposed. Sequential deliveries; implement this item only.

## Spec Change Log

## Review Triage Log

## Verification

Run new adapter proof (strict types/emit and all behavioral tests), affected admin detail/history/audit client regressions, affected admin-edit-context backend and synthetic loopback proof, owner export/client freshness and five scaffold parities. Parent reads actual logs/results and maps each matrix row. Record exact commands, source/log custody and limits in docs/ADMIN_EDIT_CONTEXT_ADAPTER_EVIDENCE.md and docs/evidence/admin-edit-context-adapter-20261027.json. No native or activation claim.

Parent inspected named acceptance RED at retained run-0b7d90c1-6436-4cd6-9847-74fcd53de6fc: strict compile passed; one behavior failed expected loaded vs inert invalid_request. Earlier toolchain EPERM and shallow-vs-deep readonly type-test compilation failures are harness attempts, not behavioral RED; retained unchanged.

Parent verified all98 focused tests and strict types/emit at run-ebe2c708-57f9-4a45-bdd1-418ccd5a6885, 57 affected backend tests,52 existing owner loopback checks,272 prior administrator/audit client tests, three owner export/generated-client freshness checks and five adopted parities. Every matrix row has passing executed behavioral coverage; initial named acceptance alone was observed RED. Actual diff read at /tmp/kdg-admin-edit-context-review-20261027.diff. Independent review pending.

All three independent layers returned: blind0 supported findings, edge[], verification0 gaps. No corrections or new deferrals. Parent observed and audited actual GREEN results and frozen matrix coverage; review complete. Scoped local commit follows.
