# Explicit local browser entry-route candidate — 2026-10-23

The KDG owner now explicitly mounts its selected email-code entry into a caller-owned
React Root using fixed organization and Auth public inputs. It imports the current
screen CSS, validates org before storage/client work, waits for an allowed online route
before constructing one stable SDK client outside React rendering, and keeps fresh KDG
API admission separate. No public main/index, environment activation or default target
is installed. Existing email template/delivery runtime limitations remain unchanged.

Neutral `observeBrowserEntry` and its emitted tests are scaffold-owned and synchronized
through the existing managed inventory. KDG owns root-only policy, skip-link anchor,
branding and recovery. Unexpected callback/query/hash/unknown paths scrub the current
address/history state before publishing refusal. No credentials or raw location appear
in published state. Scrub/read/listener failures close safely. Connectivity alone cannot
clear refusal; explicit clean history navigation/new start can observe again.

The local host commits refusal synchronously, unmounting code entry before pending SDK
results can reopen it. Existing Auth code still owns session side effects: a late verified
session may persist, but the refused mounted page stays closed. Explicit Go to start can
reload and recover that session only through fresh KDG checks. Native pushState and
replaceState do not emit popstate; host routers must notify observation when using them.
Initial HTTP URLs may already have reached a server; address scrubbing is not erasure.

Connectivity rerenders preserve the mounted EmailCodeEntry and its unfinished code and
cooldown. SDK refresh shutdown/start is requested for offline/refused/online changes;
no cancellation/revocation of already executing Auth work is claimed. Disposal detaches
observer/root subscriptions and requests refresh shutdown, preserving session data.
No private SDK channel manipulation or cleanup of historical resources occurs.

ATDD RED: emitted browser observer missing and local route mount absent in the composed
browser proof. Focused RED: caller mutation redirected the safe path before it was pinned.
The existing browser journey ran before the local-mount acceptance failure. An initial
new-fixture check expected signed-out state despite a prior synthetic persisted session;
final proof explicitly selects cold storage for that scenario and separately verifies
persisted bootstrap/reload. The offscreen skip-link mouse click diagnostic was corrected
to its intended focus/keyboard activation; no application assertion was relaxed.

[Durable receipt](evidence/local-entry-route-20261023.json) records exact RED/GREEN logs,
source/proof hashes, commands and requirement-to-test mapping. Prior evidence stays
immutable. Current proof covers real browser events, invalid org/storage and initial
callback refusal before SDK I/O, safe skip link, code/cooldown across offline/reconnect,
fresh reload/current denial, mid-verification callback refusal/late SDK result, explicit
new start, hash refusal, listener/root disposal and complete browser error accounting.

Scaffold impact: neutral browser observation/runtime tests/guidance in the same slice,
no inventory expansion; managed KDG copies synchronized by generator. Shared UI: existing
owner branding/CSS reused, no domain UI promotion. Agent context: existing instructions
sufficient, no edit. Documentation: README, this evidence/receipt and prepended handoff.
ADRs unchanged; applies 0023/0032, no schema/migration or release activation.

Synthetic local/CI only. No real email/account/access, provisioning, production,
deployment/pilot, Leave/editor, Docker commands, cleanup or fingerprints/HMAC.
Concurrent work, historical artifacts and approved TS 7.0.2 dependencies are preserved.

## Reviewed proof additions

Fixture dispatch now lazily imports the chosen journey before any SDK construction;
legacy-entry.tsx preserves the previous SDK/OAuth journey under existing characterization.
Explicit email selection takes precedence over the harness-only local reload selector.
Initial offline proof supplies the browser's navigator observation before mounting and
asserts zero storage/Auth/API work; reconnect starts the owner. In-session connectivity
proof uses actual browser offline/online plus events. No cached-offline-PWA claim follows.
Bad URL/key, org and storage cases all fail safely. A held loopback context response
released after route refusal cannot render admission. Direct disposal during held SDK
verification leaves the root empty and makes no context request on late completion.
The fixture instruments the actual SDK's public refresh methods and verifies requested
stop/start/stop ordering; timer completion or cancellation of prior work is not claimed.
Real browser Back traversal emits paired history/hash events, remains refused without
extra API work, then clean Back rechecks access. Subsequent unsafe fragments still scrub
while refused. Final error assertions include the last explicit journey selection.

All eight Blind Hunter findings are patched, with no deferrals. Follow-up static review
confirmed fixes and no residual concrete findings; reviewer did not rerun tests.

Final verification: 98 emitted and 48 owner tests (146 total), 58 compiler/SDK/React/
browser checks, 68 builder tests, strict builder TypeScript and managed parity pass.
Fresh full offline generation passes as bootstrap-only, generation_ready=false.
Composed capsule: auth-7c6d9210-3066-45e0-9ef1-7b6751557fb8 (sources unchanged, server
stopped). Neutral: proof-h64kLg. Full generation: proof-XxXL0y. Exact commands and
immutable proof/source bindings are in the receipt.
