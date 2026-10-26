---
title: 'KDG online administrator edit context'
type: 'feature'
created: '2026-10-26'
status: 'in-review'
route: 'dispatch'
baseline_commit: '5b2d5097d29ef806d12ecd1b4213c182920ab188'
review_loop_iteration: 0
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/apps/kdg-capture/AGENTS.md'
---

<frozen-after-approval reason="standing authorization for ready synthetic persistence/API work without routine stops">

## Intent

Add an inert administrator original-version edit-context read, requiring current read.all AND edit.all. This is Story 3.2 AC-1's backend context subset; it does not complete Story 3.1/3.2 or authorize writes, conflict decisions or activation.

## Boundaries & Constraints

**Always:** Separately constructed `GET /api/v1/admin/captures/{capture_id}/edit-context` returns only closed `AdminEditContext {capture: CaptureDetail, editable_fields: ["observation_date","answers"]}`. Preserve original child, owner/actor, questionnaire definition/version, shown revision and creation/update provenance. A current administrator need not equal the original owner/actor. Historical reads need no active child/assignment/create eligibility.

Check current fixed-organization read.all then edit.all independently before checkout; exact typed organization authorization/resource scopes, verified account/durable actor/membership, matching account/actor/membership between decisions. Success requires both; denial never falls back to own capabilities. Preserve distinct authentication/denial/setup/outage errors. Use existing safe error identifiers and private/no-store headers.

One original ten-second Budget covers streaming, both checks, acquisition, read-only all_read transaction, release, context validation and final serialization. One outer three-second Access timeout covers the pair together. Retain the FIRST check's monotonic observation: second check and slow checkout cannot renew its one-second SQL-entry freshness. No external waits under transaction/locks; validate after commit. Cancellation retains worker ownership through unwind. Reuse admin detail's independently scoped query and512KiB full-detail bound; whole-context actual UTF8 <=544KiB follows existing own-context precedent.

**Never:** Observations/expiry/offline leases, actor names, command/outcome/receipt fields, body or query selectors. No PUT/recovery/conflict API, server proposal/draft, cache/IndexedDB/browser/session UI, startup/sender/queue/worker activation, schema or existing helper/API changes. Synthetic local/CI only; no Leave/editor/UI, real accounts/services, native PostgreSQL/Docker, provisioning/migration execution, installs/dependency edits, deployment/production/pilot/cleanup/push. Preserve concurrent work/history/resources/TypeScript7.0.2; fingerprints/HMAC deferred. Never read/run/copy/hash `apps/kdg-capture/migrations/tests/schema_fixture.py`.

## I/O & Edge-Case Matrix

| Given / when | Then |
|---|---|
| Both all capabilities, another owner's record | Complete original capture/revision, exact editable fields, immutable provenance; no ownership impersonation |
| First or second denial/outage/setup/session failure | Safe401/403/409/503, no checkout/fallback or partial capture |
| Account/actor/membership/org/resource/permission mismatch | Refuse before SQL; separate valid decisions must match verified identity |
| Slow second check/checkout, body/Access timeout | First freshness and original total/pair deadlines hold; no renewal or late success |
| Foreign/missing capture, inactive/unassigned child | Same private404 for missing/foreign; valid historical correction context remains readable |
| Bad UUID/query/body/Bearer/duplicates | Safe422/401 before authority/storage; exact closed DTO, no offline authority |
| Invalid stored record, boundary sizes, driver/release/serialization failure, cancellation | Safe whole-response failure, after-transaction validation, owned unwind and no business mutation |

</frozen-after-approval>

## Code Map

- New `write-candidate/admin_edit_context.py`: typed all-edit evidence and paired-authority handler; reuse `admin_read.AdminReadHandler/AllReadEvidence/_transaction/DETAIL`, `capture_read.Lookup/CaptureDetail`. Reuse the pattern of `capture_edit_handler.EditHandler._authorize_pair`, not its own-only permissions or owner-actor equality.
- New `admin_edit_context_http.py`, `admin_edit_context_openapi.py`, `export_admin_edit_context_openapi.py`, `admin-edit-context-openapi.json`; existing admin/own context HTTP, safe-error, read-only engine and export conventions; no edits to those owners.
- New `write-tests/test_admin_edit_context{,_http,_contract}.py`; `contracts/admin-edit-context-generated/`; `web/tsconfig.admin-edit-context.json`, `web/tests/admin-edit-context.types.ts`.
- Parent owns `web/tests/admin-edit-context-http-{fixture.py,proof.mjs}`, `docs/ONLINE_ADMIN_EDIT_CONTEXT_EVIDENCE.md`, machine evidence, append contracts, prepend handoff and README. Reuse selected synthetic fixtures; no broad copying/discovery.

## Tasks & Acceptance

- [x] Observe actual missing foreign-owner context route404 expected200 before implementation; retain importable RED source/log.
- [x] Implement the closed handler/route and focused TDD for every matrix row; tests independently importable, deterministic phase-entry expiry as in current history/audit tests.
- [x] Owner-export OpenAPI and generate client; strict TypeScript7.0.2 proves exact fields and absence of offline/write authority.
- [x] Parent qualifies loopback, focused regressions, exports/types and five adopted scaffold parities; reconcile docs and evidence.

Given both current capabilities, when context is read, then only the authorized original capture and editable-field declaration return. Given failed evidence/execution, when completing, then no capture or reusable rights escape.

## Implementation Notes

Investigation closes this technical read subset without a user-visible choice or irreversible action. Full all-edit write/conflict/outcome schemas and Identity labels remain separate. KDG permission/record semantics stay local; scaffold/UI/context/ADR unchanged unless a demonstrated neutral defect requires coordinated promotion. Docs/contracts/types update here. Standing authorization covers dirty-tree/routine checkpoint/size decisions; do not touch shared Leave planning.

Parent owns workflow, integration, docs, broad verification and commits; implementation child must not render skills, edit this spec/parent files or commit. Retained tool paths: web/README.md and previous machine evidence command argv. Restricted async workers may stall; use required execution permissions for retained synthetic tests, never change runtime/dependencies.

## Spec Change Log

## Review Triage Log

| Finding | Verdict | Route | Verified evidence |
|---|---|---|---|
| B1 | low | patch | Pair-timeout acceptance can succeed without proving the edit check started; assert both phase entries before expiry. |
| B2 | low | patch | Injected serialization failure currently hits the worker dump; separately fail final HTTP serialization after lease release. |
| B3 | low | patch | Re-encoding parsed JSON discards wire padding; measure received bytes before parsing in the new loopback proof. |
| B4 | low | patch | Proof success omitted shutdown_failed; require successful owned stop as well as zero process exit. |
| B5 | low | patch | Final storage artifact was written but unchecked; validate disposal, balance and immutability after shutdown. |
| B6 | low | patch | Selected snapshot fields leave substitutions undetected; compare the complete independently specified original capture. |
| B7 | low | patch | Nested capture assignment alone accepts extra fields; assert exact generated CaptureDetail equality. |
| B8 | low | patch | Worker cancellation has coverage but first/second Access cancellation does not; add gated pair-phase checks. |
| B9 | low | rejected | The unchanged inherited CreateHandler._authorize decoder is already exercised by test_capture_create_handler.test_transport_error_body_bounds_duplicates_encoding_fail_closed and the existing edit-handler malformed response tests; duplicating all raw-wire permutations per adapter adds test maintenance without a demonstrated adapter defect. |
| B10 | low | defer | A closing injected AsyncBaseTransport fails on the existing all-read handler second invocation and on the new pair; private transport-characterization.py demonstrates both. Existing own pairs use the same pattern. Default transport=None creates separately owned clients and is unaffected; defer this pre-existing custom test-transport ownership issue to its shared handler owner. |

All three review layers completed before triage: blind ten findings, edge none, verification-gap none. Eight direct test/proof corrections; one low redundant-coverage suggestion rejected; one pre-existing low injected-transport issue deferred.

## Verification

Retained Python owner-env (do not resolve), Node26.11.1/TS7.0.2; no installs. Explicit new modules plus existing admin/own-context regressions; actual loopback; owner export/generated check; strict types; five scaffold parities. Reuse prior evidence only after complete effective-source equality. Private custody `platform/deployment/.local/kdg-online-admin-edit-context-20261026/`;188 protected files and292 prior sources. Native SQL/RLS/driver, actor names, mounted UI/session and release qualification remain outstanding.

Candidate qualification passes ten commands on one unchanged307-source map:90 focused backend tests (20 new),49 actual loopback checks, export/client freshness, strictTS7.0.2 and all five scaffold parities. All292 prior implementation sources and188 protected files remain unchanged;22 earlier HTTP/browser/store proofs retain complete effective-source equality. Every matrix row has executed coverage. Actual loopback RED404 and independent ASGI RED are preserved; watchdog negative records expected failure and normal shutdown at10.38seconds. No whole-story/native/activation claim. Independent review follows.

Final qualification after review: ten commands on the unchanged307-source map,92 focused tests (22 new),52 loopback checks including received wire bytes and final lifespan disposal/storage validation. Eight direct review corrections are verified; one low redundant coverage suggestion is rejected and one pre-existing low injected-transport issue is recorded in deferred work. All292 prior sources/188 protected files and22 reused proofs remain unchanged.
