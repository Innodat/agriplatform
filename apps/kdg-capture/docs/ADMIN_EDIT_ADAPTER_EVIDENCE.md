# Inert administrator explicit edit request adapter — 2026-10-27

`web/src/admin-edit.ts:editAdminCapture` performs one explicit administrator PUT under the existing generated owner contract. It pins current caller/bearer/organization/capture/operation and serialized nested input before awaits. Server current read.all AND edit.all remains authoritative. No owner impersonation, own fallback or local authority is introduced.

Only a closed v1 capture.edit receipt matching the original operation/target with exact signed-bigint revision acknowledges success. No-op and first-commit replay retain the original receipt revision, without assuming a new effect or comparing it to incoming expected revision. A mismatched target cannot acknowledge this pending original input. Conflict409 exposes only the stable error identifier and required current_revision; all other errors forbid that field. Raw messages/content are discarded.

Closed options, strict JSON/duplicate-key/UTF8 validation, same-origin JSON/private/no-store, redirect refusal,131072 serialized request-byte and16384 actual response-byte ceilings apply. One maximum10s original deadline covers preflight/fetch/body/validation/publication. Caller cancellation, generation fences and owned-body cancellation suppress stale results, including ignored abort, stalled/empty chunks and overlapping requests. Timeout/cancellation after dispatch may still commit; input remains unchanged and no retry, automatic recovery, new operation identity, persistence or rollback/absence promise follows.

Parent verification passes59 new focused tests and strict TS7.0.2 compilation/emission,69 affected backend tests,60 existing synthetic owner HTTP checks and95 own edit/recovery tests plus strict types. Delivery1 context/prior clients/owner freshness/five scaffold parities are reused with every successful proof source hash checked against current files. Exact commands/results, source/log custody and matrix mapping are in [machine evidence](evidence/admin-edit-adapter-20261027.json). Three independent layers complete with no supported findings or verification gaps; no new deferrals.

The compiling inert stub failed the single named PUT acceptance before runtime implementation: zero requests instead of one. Only named acceptance was observed RED. Environmental EPERM and an interrupted combined edit/proof approval wait are retained separately; the held command made no changes or running process. Workspace edits and proof invocation were then separated. No failed runtime expectation was changed.

Scaffold: proven primitives reused, admin semantics local, five adopted parities pass. Shared UI, agent context and accepted ADRs unchanged; docs/contracts/checkpoint update together. Prior KDG implementation bytes, historical resources/evidence and concurrent work remain preserved. No prohibited fixture access, native/Docker or resource lifecycle action occurred.

Synthetic inert consumer only. Full Story3.1/3.2, separate Identity historical actor labels, mounted portal/session/device, real authority and release remain gated. No UI/editor/Leave, integration/activation, real services/accounts, provisioning/migrations/privilege expansion, dependencies, deployment/production/pilot/push or cleanup. TS7.0.2 retained; fingerprints/HMAC deferred.

Re-run from repository root:

```sh
platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node apps/kdg-capture/web/tests/admin-edit-adapter-proof.mjs
```
