# Inert audit display request adapter — 2026-10-28

`web/src/audit-display.ts:auditDetails` consumes the generated audit-display aggregate
with one explicit authenticated same-origin GET. It returns a complete deeply frozen
aggregate or safe typed outcome. It remains unmounted and has no Auth/session, UI,
storage, retry or activation effects. Current server read.all and browser publication
fences are separate responsibilities; `isCurrent` must represent the caller's pinned
account/organization/capture/page/session/access generation.

Qualification: **109 adapter tests**, strict **TypeScript7.0.2** compile/type/emit,
**73 existing audit tests**, **20 backend tests plus2 subtests**, owner schema
freshness, generated freshness and five scaffold code/test parity checks pass.
Retained Node26.11.1 is used throughout. Independent blind review reports no supported
code findings; documentation follow-up is recorded below. No new deferral.

The adapter validates duplicate-free closed JSON, strict UTF8, original numeric audit
revision/provenance/cursor semantics, exact sorted distinct actors from the included
page/header, resolved scalar names and unavailable discriminators. Actual streamed
bytes are capped at321KiB; original raw JSON subtree bytes, including whitespace and
escapes, are capped at64KiB audit/256KiB actor display. Maximum100-event continuation
with202 distinct actors and256-codepoint/1024-byte names passes. Per-actor unavailable
and temporarily unavailable batches remain distinct; no partial labels publish.
Private/no-store JSON is required; redirects, public/cacheable metadata and unsupported
content encodings fail closed. Safe API status/error IDs omit English bodies.

Session account/bearer and request organization/capture/limit/cursor are copied before
awaits. One maximum ten-second monotonic deadline covers transport, streaming,
validation and publication. Abort/current-generation/deadline checks run around reads
and publication; tests include ignored aborts, stalled and immediately empty streams,
reentrant predicates and every generation switch against delayed success and errors.
Owned stream cancellation is best-effort; the browser adapter does not claim awaited
cooperative server cleanup. There is no implicit retry or durable cache.

Acceptance RED compiled a temporary typed stub and failed `invalid_response != loaded`
before implementation, retained at `run-f540f152-c350-49cb-a31c-cef6f4db2fce` beneath
`platform/deployment/.local/kdg-audit-display-adapter-20261028/`. Expanded matrix tests
followed first implementation; they are not individually test-first claims. The first
implementation passed72/73 inherited tests: the old64KiB error-body test was adapted
to the selected321KiB aggregate ceiling, with no production workaround. Two sandbox
subprocess failures remain retained separately. Before exporting the existing pure
`pin`/`validatePage` seam, the original73-test audit proof passed; it passes afterward.
The only old audit source change adds those two export keywords.

Freshness initially failed on the existing generated manifest's schema source hash.
Scratch regeneration produced byte-identical `index.ts` and `types.gen.ts`. The owning
pinned generator repaired only `.generated-files.json`, then its freshness check passed.
Original source hash91b508feebde370d76d247549f058f2d5db29aeb6dada4ae7cc898505e5d0f85
was replaced by current3b3efc904ad5dd77782171c98b1726c57fc54186e5b61ae5184b7024e2368ebc.
No generated file was hand-edited. This corrects preexisting custody metadata; the
backend schema/wire/type implementation is unchanged.

Exact argv/results/log locations, source hashes, RED/GREEN capsules and preservation
checks are in [machine evidence](evidence/audit-display-adapter-20261028.json).
Additional retained qualification logs/commands and original-document bytes live in
`/tmp/kdg-audit-display-adapter-20261028/`. The final source-bound proof is
`run-f1330ba3-80e5-4e34-9f4a-8357511dc45b`. Successful commands can be repeated from
repository root with retained Node/Python; no dependency install is required:

```sh
platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node apps/kdg-capture/web/tests/audit-display-adapter-proof.mjs
platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node apps/kdg-capture/web/tests/audit-adapter-proof.mjs
python3 /tmp/kdg-audit-display-adapter-20261028/qualify.py
```

Traceability: KC7/browser and KC9/HD6–7 consume the generated aggregate. Inherited
request/audit cases cover identity/scope/cursor/provenance, strict parsing, status/error
pairs and bounded lifecycle; aggregate-specific cases cover closed labels/actor sets,
header-only/empty pages, name/byte bounds and generation invalidation. This is synthetic
fetch/stream proof, not an integrated browser portal/session or real-authority proof.

Scaffold: existing strict helpers/transport behavior reused; KDG audit and Identity
projection semantics stay local. Five adopted parities pass; no new neutral behavior
needs promotion. Shared UI and agent context unchanged. Documentation/evidence and
handoff update together. Existing ADR0023/0031/0056 apply; no ADR changes. No full
Story3.1/3.2 completion, installed-device, native Identity retention/projection privilege,
real credential/account or release qualification follows.

All preexisting KDG sources are preserved except the deliberate export keywords,
generator-owned manifest hash and append/prepend documents. Concurrent non-KDG changes,
old evidence, dependencies and resources remain preserved. No active startup, UI/editor/
Leave, workers/queues, real service/account, native DB/Docker/migration/grant, deployment/
production/pilot/push or cleanup operation ran. The prohibited fixture was not accessed.
Model/effort, token usage and model-only elapsed are unavailable; actual test/tool waits
are recorded in machine evidence. Reviewer's default Node24 blocked their test run;
coordinator inspected the retained26.11.1 passing logs directly.

Final independent documentation review reports zero supported findings. The reviewer
independently reran all109 capsule tests using pinned Node26.11.1 and strict TypeScript
against current source; both passed. Backend/freshness results were inspected through
retained logs. No open finding or new deferral. All614 protected KDG files match the
pre-delivery hashes, and original handoff/contracts bytes remain preserved.
