---
title: 'App-owned OpenAPI client and real browser API call'
type: 'feature'
created: '2026-10-20'
status: 'done'
route: 'dispatch'
baseline_commit: '20620682f15afd004093b67c0a1433437d65b9dc'
review_loop_iteration: 0
context:
  - '{project-root}/platform/docs/architecture/contracts/scaffold-environment-and-generation.md'
  - '{project-root}/platform/docs/architecture/contracts/scaffold-dependency-baseline-2026-10-14.md'
  - '{project-root}/platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md'
---

<frozen-after-approval reason="standing bounded shared-foundation approval; next selects missing P1 client boundary">

## Intent

The generated shell has no typed browser/API boundary. Export its owner FastAPI
OpenAPI, generate app-owned TypeScript contracts using an upstream CLI, and consume
them through a thin health client. Prove real browser success and safe unavailability,
plus regeneration after owner DTO edits without losing custom code.

## Boundaries & Constraints

Use existing platform/api-client build-time owner and builder templates/installer/proof.
No shared backend SDK, handwritten OpenAPI-to-TS generator, runtime engine or alternate
journal. Derived clients stay generated; DTO/routes/client adapter remain owner seeds.
Public generation and Auth/Access candidates stay unpromoted. No business endpoint,
Identity/Access/WRITE/Leave/editor, database/migration/account/provider/Docker/provision/
deploy/real-data action. Preserve concurrent work and prior receipts/resources.

Pin @hey-api/openapi-ts0.99.0, types-only CLI. Actual TS7 API failure justifies an
isolated compiler-API dependency directly pinned to TypeScript6.0.3 in the build-tool
owner. The qualified compatibility shim6.0.2 was rejected after its transitive bin
collided with app TS7; direct6 pins that same verified payload without the shim.
All app/compiler commands remain TS7.0.2.
Declare tool through the web dev dependency and root workspace lock. No nested frontend
lock, floating tools, peer overrides, implicit downloads or hidden checkout dependencies.

Use local exported schema only, no remote refs/config discovery. Client output uses
existing installer in its own generated subdirectory; no competing ownership manifest.
Check mode detects stale schema/output without changing target. Refuse edited generated
clients, invalid input/tools and incomplete states with safe identifiers. Never log or
render payloads/raw error text. Browser uses only its own API; no Supabase business call.

## I/O & Edge-Case Matrix

| Scenario | Expected behavior |
| --- | --- |
| Export and generate | Actual owner OpenAPI produces deterministic generated contracts; strict TS7 passes |
| Edited DTO | Stale client/type check fails; regenerate/check succeeds; owner code survives |
| Tampered output/unsafe input | Refuse without altering target; prior output retained |
| Browser success | Real same-origin own-API health call uses generated type; rendered status verified |
| Unavailability/errors | Stable safe client result and visible failure; no sensitive text or false success |
| Fresh install | Declared copied-workspace tools only; no ancestor fallback; full install/build/API/browser proof |

</frozen-after-approval>

## Code Map

- `platform/api-client/README.md`: stale Phase2/global-SDK placeholder; implement this
  owner as build-time tooling, not shared runtime contracts.
- `platform/builder-cli/src/scaffold-install.ts`: generated hash preflight, check,
  journal/recovery. Reuse for client output root with fixed generator/recipe identity
  and schema hash as changing source identity. Upstream emits types.gen.ts/index.ts.
- `templates/service/main.py`, `safe_errors.py`: typed Pydantic health DTO and declared
  error schema; keep existing health JSON and safe errors. Offline app.openapi() export
  needs no public OpenAPI endpoint. Stable relative servers prevent path-dependent output.
- `src/application-renderer.ts`, `templates/application/`: add owner client/export
  guidance and thin client seed. Preserve imported custom behavior.
- `scripts/test-generation-application.mjs`: existing fresh copied-root proof. Package
  actual tool/builder sources into disposable workspace; qualify local tool/compiler
  identities. API environment/schema/client generation must precede web type/build.
- `templates/application/web/scripts/browser-smoke.mjs`, `proof-support.mjs`: currently
  forbid all fetch/XHR. Explicitly allow only GET own /api/health for client proof;
  same-origin preview proxy targets actual generated API. No general proxy permission.
- `tests/application-renderer.test.mjs`: whole service hash is historical pre-refactor
  characterization; explain intentional DTO/template changes, never dismiss unknown failure.

## Tasks & Acceptance

- [x] `platform/api-client/package.json`, `src/`, `tests/`: thin pinned CLI wrapper
  using existing installer, local-only schema, check/regenerate/conflict tests; RED first.
- [x] Builder renderer/templates/tests: typed health/error OpenAPI export, owner client,
  declared build tooling, safe error mapping tests and renderer ownership verification.
- [x] Existing application proof: generate/check client; add an optional owner DTO field
  omitted from health JSON, observe stale TS failure, regenerate and prove new type.
  Retain failed output. Assert owner/import hashes survive, and tampered client refuses.
- [x] Browser proof: typed owner health request/rendered success before/after reload;
  explicit real API outage shows unavailable, with narrowly expected diagnostics and
  completed teardown. Keep keyboard/mobile/import behavior and all other request guards.
- [x] Owner runbooks and root evidence/contract/KDG navigation: exact traceability,
  dependencies/compatibility, scaffold/UI/context/docs/ADR impacts and remaining gates.

Given an owner API contract, when exported/generated and consumed in fresh output,
then real browser HTTP behavior and TS7 match it. Given contract drift or failure,
then stale/unsafe success is rejected and custom code remains intact.

## Implementation Notes

No intent gaps or external irreversible action. Agent owns api-client and builder code/
runbooks. Root owns spec/evidence/contracts/KDG docs, canonical root-lock update, final
verification/review/commit. Do not render BMAD or commit. Focused logs in deployment/
.local/scaffold-api-client. Tool qualification receipts: ts7-1ksu1i6h fails SyntaxKind;
compat6-rmrh9tb3 passes and contains cached pinned tools. Root handles root lock/install;
coordinate once package manifests are stable. Existing README gives selected Node/npm/
uv/Python/Chromium/cache paths. No checkout node_modules mutation by agent.

## Spec Change Log

- Fresh installation proof-kuDIrM demonstrated that the initially selected compatibility
  shim forwards to actual TypeScript6.0.3 and hoists its tsc bin over root7. Direct
  exact tool-owner TypeScript6.0.3 passes direct6-layout-nm9xpv2e. This refines an
  implementation dependency under the standing pinned-baseline/lean-repository approval;
  app7, upstream tool and behavior boundaries stay fixed. No compiler-command wrapper
  or peer override is added. Failed proofs and previous qualifications remain retained.

## Review Triage Log

| Finding | Verdict | Evidence and route |
| --- | --- | --- |
| Blind1 import outside exporter try | medium | Owner import executes before the safe exception handler; a raised sensitive message escapes. Patch: guarded import and negative process test. |
| Blind2 export direct write | low | Interrupted derived-schema writes can require re-export; owner DTO source remains intact. Reject: rare local interruption, inexpensive regeneration, atomic temp-state machinery exceeds a direct correction at this candidate stage. |
| Blind3 check follows symlink | low | is_file/read_text follow an existing link unlike the export branch. Patch: move the existing refusal before both branches and prove preservation. |
| Blind4 malformed JSON mapping | low | response.json SyntaxError falls into transport catch while bad decoded shape returns invalid_response. Patch: distinguish SyntaxError safely and prove exact result. |
| Blind5 unrestricted health-body buffering | low | A replacement/misconfigured200 source could allocate a large body within the deadline; actual owner health response is fixed and small. Reject: this synthetic health-only consumer gains no practical current benefit from a new streaming/size engine. Revisit with a concrete broader endpoint. |
| Blind6 proxy only in harness | low | Actual proof supplies the exact route; generated Vite configuration intentionally has no runtime integration. Patch: name that routing prerequisite explicitly in owner README without adding a server/proxy feature. |
| Blind7 effect leaves request in progress | low | active flag blocks late state; native fetch already expires at5s. Development StrictMode can duplicate this tiny GET. Reject: bounded harmless synthetic health calls do not justify a new cancellation surface/state. |
| Blind8 timeout not exercised | medium | Existing assertion checks signal presence but not actual stalled native fetch/body termination. Patch: bounded real loopback header/body stalls and cleanup. |
| Blind9 wrapper refusal gaps | medium | Schema/ownership guards exist but wrapper tests omit those direct boundary permutations. Patch: negative preservation tests for symlink, missing manifest, edited index, size/depth. |
| Blind10 handoff says implementation in progress | false | Before receipt of the review, handoff was already revised to acceptance-pass/review-in-progress; checked tasks and remaining P1 gates agree. Final completion wording follows commit. |
| Edge1 owner import leak | medium | Same verified cause as Blind1; grouped into its guarded-import patch, retaining this row. |
| Gap1 existing stale exported schema untested | medium | Filed mutation demonstrates removal of the content comparison would pass existing tests. Patch: edit owner DTO, assert openapi_stale and unchanged old bytes, re-export/check. |

No intent changes or deferred work. Seven patch groups; three low rejections; one false.

## Verification

Selected builder and api-client tests; builder TS7/schema checks; fresh service proof
when bound files change; complete existing application proof with generated client,
expected stale-contract RED and real browser/outage. Record source/output/lock/tool
hashes. Existing ADR0001/0059/0031/ownership apply; accepted ADRs unchanged.

Executed:62 builder tests,7 CLI tests,2 health-client tests, TS7/schema checks and fresh service/application/browser proofs pass; exact paths/results in platform/api-client/EVIDENCE.md. Three intentional actual acceptance failures were observed before successful regeneration/refusal verification.
