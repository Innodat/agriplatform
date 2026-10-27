# Inert administrator edit-context request adapter — 2026-10-27

`web/src/admin-edit-context.ts:loadAdminEditContext` performs one explicit same-origin administrator GET and returns a complete deeply immutable original-version context or safe typed outcome. Caller, bearer, organization and capture are pinned before awaits. The server independently requires current read.all and edit.all. Original owner/creator, questionnaire/answers and actual update executor remain intact across owners.

The closed wrapper permits exactly capture and ordered observation_date/answers editable fields. It grants no offline observation or reusable authority. Strict duplicate-key JSON, fatal UTF8, closed content/provenance validation and private/no-store headers apply. Actual context/error bytes are bounded at544KiB; compact capture semantics independently remain512KiB. One maximum10s deadline, caller cancellation and generation checks protect final publication, including ignored abort, late/stalled bodies and immediate empty chunks. Owned streams are cancelled best-effort.

Parent verification passes98 focused tests with strict TypeScript7.0.2 compilation/emission,57 affected backend tests,52 existing synthetic owner HTTP checks,272 prior administrator/audit client tests,three owner exports/generated-client freshness checks and five scaffold parities. Every matrix row maps to executed passing coverage in [machine evidence](evidence/admin-edit-context-adapter-20261027.json), which records exact commands, source/log custody and attempts. Three independent review layers complete with no supported findings or verification gaps; no new deferrals.

The named cross-owner acceptance failed against the inert stub before runtime implementation; only that acceptance was observed RED. Earlier compiler/sandbox failures are retained harness attempts. The readonly type fixture was corrected before behavioral RED; no runtime expectation changed to dismiss an unexplained failure. Root generator dependencies are unavailable at the live root; the retained qualified generator has identical source and its freshness checks pass. Sandbox subprocess/socket/worker failures pass outside the sandbox.

Scaffold: proven neutral primitives reused; administrator scope/context semantics stay KDG-local and all five adopted parities pass. Shared UI, agent context and accepted ADRs unchanged. Documentation/evidence/contract/checkpoint update together. Existing sources, historical resources/evidence and concurrent work are preserved. The prohibited untracked migration fixture was never accessed. No native/Docker or resource lifecycle command ran.

This proves a synthetic inert consumer. Full Story3.1/3.2, historical actor labels through a separate Identity HTTP contract, mounted portal/session/device, real authority and controlled release remain gated. No UI/editor/Leave, Auth/session/startup/browser/queue/worker activation, real services/accounts, provisioning/migrations/privilege expansion, dependencies, deployment/production/pilot/push or cleanup. TypeScript7.0.2 retained; fingerprints/HMAC deferred.

Re-run from repository root:

```sh
platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node apps/kdg-capture/web/tests/admin-edit-context-adapter-proof.mjs
```
