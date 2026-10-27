# Inert administrator history request adapter — 2026-10-27

`web/src/admin-history.ts:adminHistoryCaptures` consumes one existing administrator
history page with an explicit authenticated same-origin GET. It returns a deeply
immutable validated page across owners or a safe typed outcome. It remains unmounted;
there is no automatic pagination, persistence, Auth/session wiring or startup change.

Parent qualification passes 121 adapter tests with strict TypeScript 7.0.2 types/emit,
108 existing own-history/read tests, 78 administrator-detail tests, 73 audit tests,
114 affected backend tests, 37 synthetic HTTP checks, administrator OpenAPI freshness
and five scaffold parities. Three independent review layers completed with no supported
findings or verification gaps. Exact commands/results, source/log custody, attempts and
requirement mapping are in [machine evidence](evidence/admin-history-adapter-20261027.json).

Caller/bearer/organization/inclusive dates/limit/cursor are pinned before awaits.
The closed page echoes the reader context; every original owner/actor, original
questionnaire/answers and actual update executor remain unchanged. Own-only owner
validation is preserved by passing each separately validated original owner to the
existing complete-detail validator. No offline observation, actor labels or edit
authority is invented.

Canonical cursors bind caller/org/read.all/dates/limit and exact microsecond UTC
creation-time/ID position. Rows are unique and strictly descend below the supplied
position; inclusive observation dates apply. Continuation equals the last included
row. Short byte-limited pages can continue, and terminal empty pages are valid.
Cursors navigate current authorized reads; no snapshot or signing claim follows.

Strict duplicate-key/UTF8/closed-shape validation, private/no-store JSON and redirect
refusal apply to successes and errors. Actual streamed response bytes are limited to
2 MiB; each compact complete detail retains its 512 KiB semantic limit. One original
maximum 10s deadline covers fetch/body/validation/publication. Cancellation, supersession,
ignored aborts, stalled streams and immediate empty chunks publish no late page;
owned-body cancellation is best-effort. Errors expose only stable typed identifiers.

Named cross-owner pagination acceptance failed against an inert stub before runtime
implementation. Only that acceptance executed RED; broader matrix tests executed GREEN,
without a claim of separately observed RED for every boundary. A copied detail test
initially treated an arbitrary different valid same-org capture ID as foreign. History
has no requested capture ID; that expectation was corrected to an invalid UUID. The
failed attempt is retained. No runtime failure was dismissed by changing expectations.

Sandbox subprocess EPERM, backend worker timeout and loopback socket refusal attempts
remain retained; the same checks pass with required execution permission. Parent's
initial verifier lacked an output base directory, then one command referenced nonexistent
test_capture_history. Both harness mistakes were corrected; the final 114-test command
passes. The HTTP fixture stopped normally and used synthetic Access/recorded storage.

All 574 baseline tracked KDG/dependency files were unchanged before documentation updates;
572 remain byte-identical after the contract append and handoff prepend, whose historical
bytes are preserved. No Docker/native database/resource lifecycle command ran. The
prohibited migration fixture was never accessed. Concurrent work and TypeScript 7.0.2
remain preserved.

Scaffold: reuse proven neutral primitives; all-read page/owner semantics remain local,
with all five adopted parities passing. Shared UI, agent context and accepted ADRs are
unchanged. Documentation, contracts and evidence update in this delivery.

This proves a synthetic inert request consumer. Full Story 3.1/3.2, historical actor
display via its separate Identity contract, mounted portal/session/device evidence,
real authority and controlled release remain gated. No UI/editor/Leave, startup/browser/
worker/queue activation, real services/accounts, provisioning/migrations/privilege
expansion, dependencies, deployment/production/pilot/push or cleanup is included.
Fingerprints/HMAC remain deferred.

From repository root using the retained toolchain:

```sh
platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node apps/kdg-capture/web/tests/admin-history-adapter-proof.mjs
```
