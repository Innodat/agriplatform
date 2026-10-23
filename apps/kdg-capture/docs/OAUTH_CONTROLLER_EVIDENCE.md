# Synthetic PKCE launch/callback controller — 2026-10-23

The scaffold now owns an injected OAuth controller and emitted behavioral tests. KDG's
`createEntryOAuth` adapts actual Supabase SDK2.117.3 signInWithOAuth and explicit-flow
exchangeCodeForSession, then verifies current fixed-org access through GET /api/v1/context.
This is a synthetic integration candidate, not public frontend/provider activation or
complete Story1.1. No dependency, SQL/API contract, migration or Docker operation changes.

Authority: Story1.1 AC5 and platform ADR0032/0023; current exact callback topology remains
in the scaffold environment contract. Auth authorization/provider callback/app callback
are distinct. The owner provides exact authorization/app callback URLs and provider/scopes.
The Azure/email values in tests are synthetic configuration, not Entra qualification.

## Behavior and caller obligations

The controller validates the SDK launch URL against exact configured endpoint/provider/
callback/scopes, requires S256 and the explicit SDK flow ID, stores minimal public
transaction metadata, then invokes navigation. Automatic SDK redirect is suppressed.
One pending transaction is not silently replaced; explicit invalidation consumes it.
It is configuration-bound and at most10 minutes old. On callback, the owner admission
is paused, the address is replaced with the clean callback URL, and the store atomically
takes the transaction before any exchange. Malformed/error callbacks consume it and
fail closed; callback code is not replayed automatically. Repeated launches and identical pending callbacks on one
controller share current work; completed/mismatched callbacks scrub and refuse; new callback views see consumed storage and cannot replay.
After exchange, fresh current KDG authority is required; session success is insufficient.

Owners must explicitly construct a PKCE client with detectSessionInUrl:false and provide
an isolated synchronous read/write/take store, safe navigation/history ports and admission
pause. The controller does not select production browser persistence or introduce a second
token/verifier store. Metadata contains only version, flow ID, time and exact public
configuration binding. Session/verifier ownership stays with Auth. Dispose settles local
work without deleting the pending record needed after redirect; invalidate consumes it.
Timeout/cancellation cannot undo SDK side effects, so a stale callback must not mount a
protected view even if the SDK later saves a session. Current admission is always rechecked.

Only a single `code` query is supported by this bounded callback handler. Other parameters,
fragments, implicit tokens, provider errors or arbitrary return URLs fail closed, are
scrubbed and do not trigger exchange. There is no automatic domain confirmation, arbitrary
route restoration, callback proxy, HTTP listener activation, real provider call or account.
Actual public bootstrap will still need selected storage/session retention and routing,
plus current owner/callback/device acceptance. Existing return selector remains a separate
validated primitive; only KDG root entry exists, and no prior-user form context is restored.

## Acceptance evidence

- Scaffold behavioral RED: `platform/deployment/.local/scaffold-auth-lifecycle-20261023/proof-16Mh3n/tests.log`: prior36 pass, launch returns authentication_required instead of launched.
- KDG RED: `platform/deployment/.local/kdg-auth-entry-20261023/auth-d6474144-c572-4670-96cf-e230c344e1b5/unit.log`: prior71 pass; emitted and consuming new launch acceptance fail.
- Focused RED: `proof-nYjZv3` under the same scaffold parent. Recovery RED `proof-lbHcWO` proves immediate invalidation/relaunch and navigation-failure state were not yet correct. All failed frames retained.
- Initial scaffold GREEN: `proof-vCLZQi/result.json` under that parent; actual rendered/installed tests and customization preservation pass.
- Actual SDK focused GREEN: `platform/deployment/.local/kdg-auth-entry-20261023/auth-9de0acce-6a1d-46a4-8db1-ec634a9243f7/result.json`: real SDK challenge equals SHA256(verifier), explicit flow exchange uses its slot, missing slot cannot borrow the latest, SDK failure cannot replay and current denial cannot admit.
- Initial browser GREEN: `auth-037ae7e1-6423-425a-b476-5626cc57d13e/result.json` under that KDG parent: actual SDK/React/Chromium launch pauses admission, callback code is absent before the synthetic SDK exchange and fresh context is checked. Current denial leaves the view unmounted. No external browser transport or local/session storage; SDK and metadata stores are synthetic memory ports.

Final reviewed source, exact commands/results and retained proof/log digests will be
recorded in evidence/oauth-controller-20261023.json after configured review and regression.

## Delivery impacts

Scaffold applies: same-item neutral controller/tests/guidance, managed KDG regeneration
and parity check; no inventory migration or forced overwrite. Shared UI unchanged.
Agent context existing owner-boundary/parity instructions suffice. Documentation this
owner evidence, receipt and prepended handoff; earlier evidence retained. No ADR change:
accepted0032/0023 applied; production storage/provider choices remain unactivated.
Concurrent changes, historical resources and approved TypeScript7.0.2 baseline preserved.
Synthetic local/CI only; no Leave/editor, real access/accounts, production, provisioning,
deployment/pilot, resource cleanup or fingerprints/HMAC.

## Configured review and corrections

Blind Hunter returned eight findings; all patched, none deferred. Completed callback
results no longer replay cached authority; deduplication is limited to identical pending
callbacks and each live invocation scrubs. Publication rechecks the pending store after
SDK begin, so overlapping controllers cannot overwrite an already published attempt.
Callback consumption snapshots its transaction before reentrant ports and takes only
that unchanged record while execution is current. Reentrant reads cannot start stale
SDK work. Test additions prove real SDK late session mutation after timeout/disposal
without admission, fixture owner/org invalidation, malformed browser callback scrubbing
and callback-specific pause failure cleanup. A consuming RED also proved mutable owner
configuration could change KDG org during work; the adapter now snapshots configuration.

The prior new test expectation that completed callback replay returned authorization
was deliberately replaced after review exposed stale authority; this was not an
unexplained failure. Pending identical calls still share the same executing operation.
Review RED `proof-qluqtn` and owner-config RED
`auth-db0f4e75-8e33-482d-9c7c-eca7e26ea4ea` remain retained in the parents above.

The parallel builder run observed an output directory created by the simultaneous full
application proof; its unchanged no-output assertion failed. It was rerun sequentially;
no expectation was relaxed and no resource was removed. Final receipt records the
sequential result and both retained logs.

Final reviewed neutral proof: `platform/deployment/.local/scaffold-auth-lifecycle-20261023/proof-2OATbt/result.json`,68 emitted tests pass. KDG final proof:
`platform/deployment/.local/kdg-auth-entry-20261023/auth-79a38360-78b0-4db3-bd43-57dc47a1d376/result.json`,111 tests (68 generated +43 owner),27 compiler/build/SDK/React/Chromium checks pass, sources unchanged and loopback server stopped normally. Builder final sequential regression68 and strict TypeScript7.0.2 pass. The final full offline generated application receipt and exact retained log/source hashes are bound by the durable receipt.

Verification commands use selected Node26.11.1 at
`platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node`:

- `node platform/builder-cli/scripts/sync-kdg-auth.mjs --write`, then `--check`.
- `node platform/builder-cli/scripts/prove-auth-lifecycle.mjs`.
- `node apps/kdg-capture/web/tests/auth-proof.mjs --unit-only`, then full proof without option.
- `node --test platform/builder-cli/tests/*.test.mjs` sequentially before full generation.
- `node platform/deployment/.local/web-baseline-qualification/new-5/root/node_modules/typescript/bin/tsc --project platform/builder-cli/tsconfig.json`.
- `node platform/builder-cli/scripts/test-generation-application.mjs` with the unchanged retained qualified SCAFFOLD_NPM/UV/PYTHON/CHROMIUM, npm and uv offline caches; commands/environment are recorded in its proof.json.

The existing upstream SDK declaration skipLibCheck qualification remains limited to
those declarations; own-source TS7 negative control still rejects TS2322. Baseline
manifest/lock/dependency authority and all historical proof frames remain preserved.

Final full application proof: `platform/deployment/.local/scaffold-application/proof-xu5dVs/proof.json`,26 commands pass with generated68 tests, client/type/build/browser checks and preservation/extension verification. See [durable receipt](evidence/oauth-controller-20261023.json) for exact final source/proof/log hashes and unchanged historical custody.
