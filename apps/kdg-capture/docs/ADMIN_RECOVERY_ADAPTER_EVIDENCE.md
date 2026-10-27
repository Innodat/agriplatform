# Inert administrator edit recovery request adapter — 2026-10-27

`web/src/admin-recovery.ts:recoverAdminEdit` makes one explicit administrator GET with exactly command_type=capture.edit, bearer and pinned original operation. Caller/account, organization, capture, type and options are captured before awaits. The request has no body, owner/target selectors or own fallback. Server current read.all alone remains authoritative independently of edit.all. Executor-private receipts have no own/admin surface discriminator; this consumer invents no original authority or ownership provenance.

Only a closed exact original operation/type/v1/capture receipt with canonical signed-bigint revision acknowledges recovery. Old/no-op revisions stay unchanged without guessing current state. Closed unresolved retains exact operation/type and remains ambiguous: an in-flight edit can still commit. Safe errors expose exact generated status/identifier pairs, no conflict metadata or raw content. No retry, PUT, new identity, queue/store change, Synced feedback or rollback/absence promise occurs.

Strict duplicate-key JSON/fatal UTF8, closed shapes, private/no-store, same-origin/redirect refusal and actual streamed16384-byte response/error ceiling apply. One maximum10s original deadline covers preflight through final publication. Abort/current-generation checks and best-effort owned-body cancellation discard stale receipts/unresolved/errors, including ignored aborts, stalled/empty chunks, overlapping lookups and exact10000ms boundary.

Parent independently passes63 focused tests and strict TS7.0.2 types/emit. Previous batch69 affected backend/60 synthetic owner HTTP/95 own client tests and context98/PUT59 proofs are reused only after every successful proof source hash matches current files. Five adopted scaffold parities freshly pass at the final boundary; owner export/generated-client freshness remains source-bound. Exact commands/results, source/log custody and every matrix row are in [machine evidence](evidence/admin-recovery-adapter-20261027.json). Three independent review layers complete with no supported findings or verification gaps; no new deferrals.

The compiling inert stub failed one named GET acceptance before runtime: verification_unavailable versus committed. Only that acceptance ran RED; all broad cases ran GREEN. Capsules/attempts are retained. No runtime expectation was changed to dismiss an unexplained failure.

Scaffold: established neutral primitives reused; administrator recovery semantics local. Shared UI, agent context and accepted ADRs unchanged. Docs/contracts/checkpoint and fresh-session handoff update together. Original implementation bytes, historical contract/handoff text, evidence/resources and concurrent work remain preserved. No prohibited fixture access, native/Docker or resource lifecycle operation ran.

This is the third/final synthetic inert request delivery in the batch, not full Story3.1/3.2 or activation. Historical actor labels need a separate Identity HTTP contract; mounted portal/session/device, real authority and controlled release remain gated. No UI/editor/Leave, integration/activation, real services/accounts, provisioning/migrations/privilege expansion, dependencies, deployment/production/pilot/push or cleanup. TS7.0.2 retained; fingerprints/HMAC deferred.

Re-run from repository root:

```sh
platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node apps/kdg-capture/web/tests/admin-recovery-adapter-proof.mjs
```
