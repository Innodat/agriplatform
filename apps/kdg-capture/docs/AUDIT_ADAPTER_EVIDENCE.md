# Inert online audit request adapter — 2026-10-27

`web/src/audit.ts:auditEvents` consumes the existing online audit metadata contract.
One explicit same-origin authenticated GET returns a deeply immutable validated page
or a safe typed outcome. It is unmounted and performs no Auth, storage or retry work.
Current read.all remains the backend's responsibility; no offline authority is inferred.

Qualification passes 73 adapter tests, strict TypeScript 7.0.2 types/emit, 108 existing
read/history client tests, 115 affected backend tests, 43 existing synthetic loopback
checks, owner OpenAPI freshness and five scaffold code/test parities. Parent reran the
new isolated proof and inspected actual results. Three independent review layers complete: one edge finding corrected, no new deferrals.
Exact commands, source/log capsules, hashes, preservation and requirement mapping are
in [machine evidence](evidence/audit-adapter-20261027.json).

The adapter pins caller/bearer/org/capture/limit/cursor before awaits. Closed metadata
preserves the original owner, actual executor and nullable initiator across another
reader's account. Numeric bigint revision navigation and canonical cursors bind current
caller/org/capture/read.all/limit/position. Continuations match the last returned event;
nonnull continuation requires a full page under the existing limit+1 audit contract.
No contiguous-history or monotonic statement-time assumption is added.

Strict JSON rejects duplicate/unknown fields, invalid UTF8 and malformed provenance.
The actual streamed response is limited to 64 KiB, including errors. Response metadata
requires JSON/private/no-store and rejects redirects. Caller cancellation, supersession,
ignored aborts, stalled streams and immediate empty chunks share one original bounded
execution deadline, with a final publication check and best-effort stream cancellation.
Safe typed errors expose no raw error body, payload or credential and trigger no retry.

Behavioral acceptance RED compiled against a temporary no-page stub before implementation.
Expanded matrix tests followed the first implementation; they are not claimed as prior
TDD. A new focused pagination regression then failed against the real adapter before
its minimal correction and GREEN. Review added a second real RED/GREEN regression
rejecting continuation after revision1, which can have no earlier positive event. All attempt capsules/logs remain retained, including
sandbox infrastructure failures. The sandboxed backend run timed out; the same synthetic
suite passed outside the sandbox without production correction.

All 558 recorded prior KDG/dependency files remain unchanged. Contracts append and handoff
prepend preserve historical bytes. Concurrent Access test changes were observed and left
in place. No Docker/native database/lifecycle/resource command ran. Existing retained
resources and TypeScript 7.0.2 remain intact; fingerprints/HMAC stay deferred.

Scaffold: existing proven strict validation helpers reused; audit semantics remain local,
with five adopted code/test parities passing. Shared UI, agent context and accepted ADRs
are unchanged. Documentation/evidence and current contracts update together.

This proves a synthetic request/stream consumer, not an integrated portal, Auth session,
physical device, historical actor labels, native SQL or real Identity/Access. Full
Story 3.1/3.2 and controlled release/compatibility/recovery remain open. No UI/editor/Leave,
startup/browser/worker/queue activation, real services/accounts, provisioning/migrations,
dependency changes, deployment/production/pilot/push or cleanup is authorized.

From repository root using retained Node26.11.1:

```sh
platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node apps/kdg-capture/web/tests/audit-adapter-proof.mjs
```
