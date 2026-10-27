---
title: 'Inert KDG administrator explicit edit request adapter'
type: 'feature'
created: '2026-10-27'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '1d6eafd36b102bdd332734491261d30fdbe99c51'
context: []
---

<frozen-after-approval reason="standing authorization for remaining ready administrator consumers, delivery2 of up to3">

## Intent

Consume the existing administrator conditional PUT with one explicit current-session request, returning only a matching immutable original-operation receipt or safe typed conflict/error. Keep this Story3.2 request consumer inert and unmounted.

## Boundaries & Constraints

Use generated AdminEditCaptureData/Errors/Response and EditCommand. Pin caller, bearer, org, capture, operation and serialized nested command before awaits; caller input remains unchanged. Closed inputs/options, canonical UUIDs and signed-bigint revision, command_version1,131072 actual UTF8 serialized request bytes. Backend owns original-definition/domain validation. One same-origin JSON PUT, private/no-store response, redirect refusal, no tenant/owner selectors or own fallback. Server current read.all AND edit.all remains authoritative; no original-owner impersonation.

A committed v1 capture.edit receipt acknowledges only exact original pending operation/capture, canonical revision and closed result. Preserve receipt revision even if it equals expected revision (no-op) or predates incoming expected revision (first-commit replay); never infer a new effect. Backend can replay an original target after a changed retry path, but a different target cannot acknowledge this pending original input.409 conflict returns only stable identifier and required typed current_revision; all other errors forbid that field. Map exact generated status/ID variants; no raw upstream body/message/exception/bearer.

Strict duplicate-key JSON/fatal UTF8/closed receipt/error parsing.16384 actual streamed response bytes including errors. One maximum10s deadline through preflight/fetch/body/validation/publication; caller cancellation/generation fencing, late/ignored-abort/stalled/empty-chunk responses publish no stale result; best-effort owned-body cancellation. After dispatch, timeout/cancel/transport/invalid response may still commit: never imply rollback, absence or safe new identity. No retry, automatic recovery, revision refresh, queue/store change or Synced publication.

Preserve concurrent/historical work/resources and TypeScript7.0.2. No UI/editor/Leave, Auth/session/startup/browser/queue/worker integration/activation, real services/accounts, native database/Docker, provisioning/migrations/privilege expansion, dependencies, deployment/production/pilot/push or cleanup. HMAC deferred. Never read/run/copy/hash apps/kdg-capture/migrations/tests/schema_fixture.py.

## I/O & Edge-Case Matrix

| Given / when | Then |
|---|---|
| Explicit valid edit, no-op or first-commit original receipt | Exactly one pinned PUT/body; only matching deeply immutable receipt acknowledges |
| Invalid session/local scope/command/options/oversized or unserializable input | Safe refusal before dispatch; no mutation or fallback |
| Mismatched operation/type/version/target or malformed/extra receipt/revision | invalid_response, no acknowledgement |
| Conflict or generated error | Safe exact status/ID, conflict revision only; no raw content |
| Caller mutates command/session/options after start or calls overlap | Original serialized identity/body stay pinned; requests and cancellation remain isolated |
| Abort/stale/throwing predicate, network/deadline, late/stalled/empty/oversized/invalid response | Bounded safe outcome, no stale publication, retry or rollback/absence claim |

</frozen-after-approval>

## Code Map

- Implementation owns only five new files under apps/kdg-capture: web/src/admin-edit.ts, web/tests/admin-edit-adapter.test.mjs, web/tests/admin-edit-adapter.types.ts, web/tsconfig.admin-edit-adapter.json, web/tests/admin-edit-adapter-proof.mjs. No commits. Parent owns spec/docs/evidence, qualification/review/commit. BMAD already rendered by parent; use dispatched implementation, no second render.
- web/src/edit.ts and tests/edit.test.mjs supply proven conditional edit/receipt/conflict/input serialization semantics. Preserve their existing behavior without editing them. web/src/admin-edit-context.ts and admin-detail.ts supply current closed options, bounded transport and best-effort cancellation pattern. read-validation.ts exports id/token/object/strictJSON/decimal/invalid/InvalidResponse/Frozen/freeze; reuse these primitives without changing prior consumers. Its errorResult is READ-specific, so implement exact generated EDIT error mapping locally.
- contracts/admin-edit-generated/types.gen.ts and write-candidate/admin-edit-openapi.json own authoritative command/receipt/error families. write-candidate/admin_edit_http.py and docs/contracts.md administrator conditional edit/recovery section own behavior. No generated/backend/schema edits.
- Follow tests/admin-edit-context-adapter-proof.mjs retained source-capsule pattern, Node26.11.1/TS7.0.2; include all compile/runtime/owner-schema dependencies. Named acceptance-only mode must reach one meaningful PUT/receipt failure against inert stub before runtime implementation. Tests should enumerate actual generated error variants from owner schema, including exact success status200, byte/deadline boundaries and all matrix rows.

## Tasks & Acceptance

- [x] Observe named PUT/receipt acceptance RED before runtime implementation, with compiling inert stub and retained source/logs.
- [x] Implement five owned files and executed behavioral/type coverage for each matrix row.
- [x] Parent inspect actual diff/results; qualify affected existing own edit/recovery/admin context clients, admin backend/HTTP, owner freshness and five scaffold parities.
- [x] Three independent review layers, supported corrections, evidence/contracts/checkpoint and scoped local commit.

Given valid current original input, when committed matching receipt arrives, then return only immutable receipt. Given conflict/failure/staleness, then preserve input and return safe classification with no automatic follow-up.

## Implementation Notes

Freeform ready synthetic consumer; batch authorization covers expected dirty-tree preservation and no routine approval stop. No intent gaps, no irreversible action. Scaffold: reuse proven primitives; admin command/receipt semantics local. Shared UI, agent context and ADR unchanged. Docs/evidence update together. No neutral behavior change planned. Implementation selected gpt-6.1-sol/high; actual model, usage and model-only time unknown. Sequential delivery2 only.

## Spec Change Log

## Review Triage Log

## Verification

New adapter proof strict types/emit/all tests; affected own edit/recovery/client tests and administrator context proof; affected admin edit/context backend suites and synthetic admin-edit loopback; owner OpenAPI/generated-client freshness and five adopted parities. Parent reads actual results and every matrix row's executed coverage. Exact commands/source/log custody, acceptance RED, limits and five impacts go in docs/ADMIN_EDIT_ADAPTER_EVIDENCE.md and docs/evidence/admin-edit-adapter-20261027.json. No activation/native claim.

Parent read the scoped unified diff and actual acceptance RED log: strict compile passed; one named test expected one PUT but inert stub made zero. Parent independent GREEN passes59 tests and strict types/emit (source unchanged). All six matrix rows have executed passing coverage, including no-op/replay revisions, conflict typing, mutated input, overlapping calls, deadline and byte boundaries. Affected69 backend tests,60 synthetic owner HTTP checks,95 own edit/recovery tests/types pass. Reuse unchanged source-bound prior context/client/freshness/parity evidence from delivery1. Review pending. Model-only time/usage unknown; failed sandbox attempt is not RED. Combined mutation/proof approval wait was interrupted before execution, then split into normal workspace edits and approved proof invocation. No mutation from the interrupted call.

All three independent layers returned: blind0 supported findings, edge[], verification0 gaps. No patches or new deferrals. Scoped local commit follows.
