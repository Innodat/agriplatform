# Auth return-selection prerequisite — 2026-10-23

This bounded candidate implements Story1.1 AC5 / platform ADR0032 return selection.
The scaffold owns the neutral helper and generated behavioral tests; KDG consumes the
same managed copies and its own current-context adapter. It does not complete Story1.1.

`createReturnSelection` in the existing generated Auth lifecycle module holds one
in-memory minimal approved path/account/scope intent. Capture, restoration, clear and
disposal invalidate prior work. Restoration consumes before observing; it calls the
owner observer with the approved route and cancellation signal, and requires matching
current account and scope. Denial, error, mismatch, timeout and stale work select only
the configured safe path. No arbitrary URL or owner extra fields are retained. Approved
paths currently exclude queries, fragments, escapes and dot segments; owners explicitly
list canonical internal routes. The safe page must be a permitted public entry surface.

KDG's `createEntryReturn` allows only `/`, using fixed configured organization and
fresh `GET /api/v1/context` via the existing strict no-store, redirect-refusing client.
The capture context is an identity hint, never admission. The observer must verify the
specific destination; KDG's entry context suffices only for its implemented root route.
Future record/form routes require their own current resource authorization and tests.

Caller integration is deliberately explicit: capture before leaving for sign-in, call
restore with the currently observed SDK session, clear on logout/account/owner changes
and dispose on unmount. Capture/restore/clear are NOT yet wired into the product React
lifecycle or a provider callback. The result is a selection, not a navigation, grant or
pending-action confirmation. The consuming adapter and synthetic SDK/browser fixtures
prove the contract without activating a product frontend. No durable return retention,
form recovery, provider launch, PKCE storage, callback exchange or registration is claimed.

## Acceptance and focused verification

- Emitted scaffold behavioral RED: `platform/deployment/.local/scaffold-auth-lifecycle-20261023/proof-kYlt0U/tests.log` — existing23 pass; new approved-return capture fails `false !== true`.
- Consuming KDG RED: `platform/deployment/.local/kdg-auth-entry-20261023/auth-aba3d8be-feb7-42f9-8823-58dbbff621b2/unit.log` — existing51 pass; both new return acceptances fail capture.
- Focused scaffold RED: `platform/deployment/.local/scaffold-auth-lifecycle-20261023/proof-gVOQOb/tests.log` — added identity/configuration/race/deadline assertions expose the conservative seed.
- First generated GREEN: `platform/deployment/.local/scaffold-auth-lifecycle-20261023/proof-KG1Qv8/result.json` —33 generated tests pass through actual renderer and preserving installer; owner seed/customization preserved.
- First KDG GREEN: `platform/deployment/.local/kdg-auth-entry-20261023/auth-76674fdb-e86e-4f88-8da6-947a1b5fa134/result.json` —65 tests (33 generated +32 owner),19 compiler/build/SDK/React/Chromium checks pass. Four added browser checks prove fresh same-account return once, external refusal, changed SDK account and current denial. No local/session storage, real Auth transport or external browser network.
- Builder regression: `/tmp/kdg-return-builder.log` —68 pass. Strict builder TypeScript7.0.2 check passes. Full offline generated application proof `platform/deployment/.local/scaffold-application/proof-e7xBj4/proof.json` passes all26 recorded commands, including generated33 tests, API/health, generated client, TS7/Vite8/browser and preservation/extension checks. Configured Blind Hunter review is recorded below when complete.
- Initial restricted-runner frames `proof-QmOjee` and `auth-713721ed-50fd-476a-b340-ea85ef55052a` have empty child logs and are infrastructure failures, not behavioral RED. Retained unchanged; reruns above establish actual assertion failures.

Commands use the retained selected Node26.11.1 executable under
`platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node`:

- `node platform/builder-cli/scripts/sync-kdg-auth.mjs --write`, then `--check`.
- `node platform/builder-cli/scripts/prove-auth-lifecycle.mjs`.
- `node apps/kdg-capture/web/tests/auth-proof.mjs --unit-only`, then without the option.
- `node --test platform/builder-cli/tests/*.test.mjs`.
- `node platform/deployment/.local/web-baseline-qualification/new-5/root/node_modules/typescript/bin/tsc --project platform/builder-cli/tsconfig.json`.
- Existing `test-generation-application.mjs` with the same qualified SCAFFOLD_NPM/UV/PYTHON/CHROMIUM and offline caches recorded in the previous scaffold proof.

No packages/locks/baselines change. Existing SDK declaration skipLibCheck qualification
remains scoped upstream; own-source negative control still fails with TS2322 as required.
Native context/API/SQL contracts are unchanged, so historical proofs remain source-bound
and no Docker startup, grant, migration or database operation is necessary here.

## Delivery impacts

Scaffold: applicable neutral code and emitted tests updated together; existing manifest
inventory and installer retained. Current-template parity refuses stale copies and
manual generated edits. Shared UI: no presentation change. Agent context: existing
same-item parity and owner-boundary instructions suffice. Documentation: this evidence,
receipt and prepended handoff; historical content preserved. ADR: none, implements
accepted0032 without changing it. Dependency baseline including TypeScript7.0.2 preserved.
Fingerprints/HMAC stay deferred. Synthetic local/CI only; no Leave/editor, production,
real account/access, provisioning, deployment/pilot, cleanup or Docker-resource change.

## Review and final verification

All six Blind Hunter findings were patched; none deferred. Epoch checks preserve
reentrant newer captures, and final validity is checked after abort cleanup callbacks.
KDG snapshots the supplied account/bearer before deferred work. The fixture disposes
its selector on organization replacement and clears old intent before failed captures.
Direct stalled-header/body owner tests verify deadline, abortion and late-response safety.
See the spec's per-finding triage and [durable receipt](evidence/auth-return-selection-20261023.json).

Review RED frames: generated `proof-hmErmp` (33 pass/3 reentrancy failures), consuming
`auth-75a3ecfd-a4bc-412a-8d42-50dac4ba5411` (session pinning failure plus shared cases).
Reviewed generated36 pass in `proof-nITCE4`; reviewed KDG71 (36 generated +35 owner) and
21 compiler/build/SDK/React/Chromium checks pass in
`auth-21747209-fc18-4922-8722-b000ed6aa618`, under the same retained parent paths above.
Reviewed builder68 and strict TS7 pass; receipt binds final generation result and logs.
An overlapping generation run `proof-eDb1AP` correctly refused builder_source_drift
when review fixes changed source; its frame is preserved and is not readiness evidence.

Final source-stable application proof: `platform/deployment/.local/scaffold-application/proof-yc4xuk/proof.json`,26 commands pass with reviewed generated36 tests. Historical proof-e7xBj4 remains a pre-review checkpoint. Exact current-source/log bindings and unchanged-file custody are in the durable receipt; unrelated concurrent deployment edits are identified separately and excluded from unchanged claims.
