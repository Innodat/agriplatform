# Inert administrator detail request adapter — 2026-10-27

`web/src/admin-detail.ts:readAdminCapture` consumes the existing administrator detail
contract with one explicit same-origin authenticated GET. It returns a complete deeply
immutable original-definition snapshot or a safe typed outcome. It is unmounted and
does not perform Auth entry, UI, storage, retry or startup work.

Parent qualification passes 78 adapter tests and strict TypeScript7.0.2 types/emit,
108 existing read/history client tests, 73 audit-adapter tests, 76 affected backend tests,
37 existing synthetic HTTP checks, administrator OpenAPI freshness and five scaffold
parities. Three independent review layers completed with no supported findings or verification gaps. Exact commands, source/log capsules and
requirement mapping are in [machine evidence](evidence/admin-detail-adapter-20261027.json).

Caller/bearer/org/capture primitives are pinned before awaits. The response preserves
the original owner/actor, original definition/version/answers, created_by and actual
updated_by even when the reader differs from those actors. The unchanged original-detail
validator checks content using the response's separately validated owner; own-only
consumers keep their original owner predicate. No edit authority is inferred. Existing
detail contains no reader-account echo: binding comes from the pinned authenticated
request and current-generation publication check, with current read.all enforced by
the server. No actor names or offline observation are invented.

Strict JSON rejects duplicate/unknown fields, invalid UTF8 and malformed original
definition/answers/provenance. The actual streamed response, including errors, is limited
to512KiB. JSON/private/no-store metadata and redirect refusal apply. Caller cancellation,
supersession, ignored aborts, stalled streams and immediate empty chunks share one
original maximum ten-second execution budget through final publication; owned body
cancellation is best-effort. Typed errors expose no raw body, error text or credentials.

Behavioral cross-owner acceptance failed against a temporary inert stub before runtime
implementation. The complete 78-test matrix was written before implementation; only the named
cross-owner acceptance executed RED. Focused boundary tests then all ran GREEN; separate
per-boundary RED cycles are not claimed. Both failed source and log remain retained. Sandbox subprocess EPERM,
backend timeout and listener refusal attempts remain historical; the same checks pass
with required execution permission. Parent's first existing-history capsule omitted
own-observation.ts; the corrected isolated capsule passes without application changes.
No expected application result was changed to dismiss a failure.

All 567 baseline tracked KDG/dependency files were unchanged before documentation updates;
565 remain byte-identical after the two append/prepend documents change.
Contracts append and handoff prepend preserve historical bytes. Concurrent work and the
approved TypeScript7.0.2 baseline are preserved. No Docker/native database/resource
lifecycle operation ran; the prohibited migration fixture was never accessed.

Scaffold: reuse proven neutral validation and request patterns; administrator owner
semantics remain local, with five adopted parities passing. Shared UI, agent context and
accepted ADRs unchanged. Documentation, current contracts and evidence update together.

This proves a synthetic request/stream consumer. Portal/session/device evidence,
historical actor labels, real Identity/Access, full Story3.1/3.2 and controlled release
gates remain open. No UI/editor/Leave, startup/browser/worker/queue activation, real
services/accounts, provisioning/migrations/privilege expansion, dependency changes,
deployment/production/pilot/push or cleanup is authorized. Fingerprints/HMAC deferred.

From repository root using the retained toolchain:

```sh
platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node apps/kdg-capture/web/tests/admin-detail-adapter-proof.mjs
```
