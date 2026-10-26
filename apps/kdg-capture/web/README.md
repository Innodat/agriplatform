# Browser current-entry boundary

“Browser entry” is Story1.1's front door: sign in, check current Khula access and show
the authorized setup-not-completed landing page or a safe denied/retry state. This
module supplies only its typed access/session boundary. The visible React page,
provider adapter, renewal/callback and validated return flow remain to be implemented.
There is no runnable product frontend or workspace activation in this increment.
package.json is an ESM marker for standalone tests, with no dependency changes.

Auth owns the current account and access token. Call createEntryBoundary(configuredOrg,
publish) once per entry view, check(session) on every Auth event/recheck, clear() on
logout and dispose() on unmount. Do not feed a stale asynchronous Auth observation
back into it as a new current session. The boundary clears admission synchronously
and ignores any earlier completion, including failed/ignored-abort requests. It does
not renew tokens, navigate, store sessions, mint rights or create an offline lease.
Every consequential server action still needs its own current authorization.

getCurrentContext consumes only GET /api/v1/context with a bearer from that session.
It sends no service key, selector or request body. It uses same-origin, no-store and
redirect refusal. The existing generated Context type is authority; runtime checks
bind account, organization, own scope, permission, IDs, string bigint member and UTC
calendar timestamp. Only validated known context fields are published. Server checked_at
is not compared with the untrusted browser clock or converted into cached authority.
Response fields are currently closed under the existing API schema; future schema
changes need explicit previous-client compatibility verification.

Known error identifiers produce distinct authentication_required, access_denied,
actor_setup_required, authorization_unavailable and invalid_response states. Both
current error_id and historical detail.code families are recognized; English error
text and numeric fallback codes never establish authority. Raw errors/payloads/tokens
are never returned or logged. UI localization and presentation remain its consumer's
job. No automatic sign-in/retry loop is introduced.

Headers and streamed bytes share a10s deadline (tests may select a shorter bound).
A timer race bounds the returned result even if an injected transport ignores abort;
underlying transport cancellation is not claimed beyond the platform's abort support.
Decoded response input is limited16KiB. This is not protection against malicious code
already controlling the same origin or an Auth provider that reports stale sessions.

From repository root, with N the selected Node26.11.1 executable:

```sh
"$N" --test apps/kdg-capture/web/tests/entry.test.mjs
"$N" node_modules/typescript/bin/tsc --project apps/kdg-capture/web/tsconfig.json
"$N" apps/kdg-capture/web/tests/browser-proof.mjs
```

The browser proof uses retained Playwright1.64.0/Chromium and TS7.0.2. It emits JS only
in a new ignored private proof directory and serves a synthetic HTTP API/DOM fixture.
It tests real Chromium fetch and session transitions, not the product UI, actual KDG
handler/current SQL, provider sign-in or device qualification. All previous native
API/Access evidence remains historical and source-bound. No package install fallback,
root command, Docker operation, cleanup or dependency/lock update is performed.

Scaffold: consume generated DTO and own-fetch conventions, no generic promotion.
Shared UI: none; fixture markup is not a product component. Agent context: root policy
suffices; commands are above. Documentation: this guide, evidence and additive handoff.
ADRs: existing current access/errors/session/logging/release decisions; no new decision.
Fingerprints/HMAC, business writes, provider/real access and release/pilot stay outside.


## Accessible entry presentation

EntryScreen.tsx is the next bounded presentation component. Supply the current EntryState,
an online observation and synchronous onSignIn/onRetry callbacks. Import entry-screen.css
in its consuming entrypoint; mount one screen per page. It shows selected static copy,
never raw context or error data. The caller owns current-session events, bounded Auth
operations, renewal, clearing/rechecking after connectivity changes and disposal. A
stale asynchronous Auth result must never be supplied as a newly current session.
The disabled action remains focusable using aria-disabled; its handler suppresses
activation while checking/offline. No provider, sign-out or return-navigation flow is
implemented here. API admission is not domain setup or an offline lease.

Run the copied-source proof with the selected Node N:

```sh
"$N" apps/kdg-capture/web/tests/screen-proof.mjs
```

It compiles strict TS7.0.2 and builds Vite8.3.4/React19.3.0 with retained approved
packages in a fresh private capsule, then runs Chromium interactions and15 focused
static-render tests. `--unit-only` runs strict types plus the15 tests; `--acceptance-only`
runs the admitted-account/setup-state browser scenario. It never installs packages
or edits root dependencies/locks. The fixture is synthetic and is not a public app
entrypoint. See ../docs/ENTRY_SCREEN_EVIDENCE.md for source custody and proof limits.


## Auth session integration

AuthEntry.tsx binds the screen to an injected stable Supabase Auth client and stable
beginSignIn callback. Import the existing entry-screen.css in its owner entrypoint.
Pass the configured org, online observation and optional own-context request adapter.
The component owns bridge setup/disposal, including strict replay and online/client
replacement. Keep Auth session/storage/provider configuration with the Auth owner;
there is no automatic client creation, redirect, PKCE or callback parsing here.

createAuthEntry is also available for another framework host. Call start once, feed
state through publish, and dispose on unmount. retry reads current SDK session;
signIn attempts known-session refresh before the injected owner launch; signOut clears
local admission then requests SDK scope local. The screen does not yet expose sign-out;
its future host must apply pending-work rules when that feature exists. Sign-out/timeout
latch against late events; explicit retry/sign-in reacquires authority. A launch resolving
alone is not authenticated entry. No prior-user state or tokens are exposed by state().

Run `N apps/kdg-capture/web/tests/auth-proof.mjs` using the retained Node above; add
--unit-only for focused SDK tests or --acceptance-only for the initial behavioral case.
The private capsule reuses pinned SDK2.117.3/React19.3/TS7.0.2 and Vite8/Chromium; it
never installs or changes dependencies. Auth-specific skipLibCheck follows the known
upstream WebAuthn exception, with strict own-source checking. Read ../docs/AUTH_ENTRY_EVIDENCE.md
for exact proof limits. Real provider/callback/return integration remains separate.


Every SIGNED_OUT cancels recovery, including one emitted by refresh rejection; another
explicit Sign in is then required. A bare logout event cannot be treated as permission
to relaunch sign-in. Mismatched refresh accounts, errors and timeouts latch closed;
only an explicit fresh observation can re-enter. The28 focused tests cover actual SDK
proactive/expired rejection, every operation deadline and replacement/disposal races.
The Auth proof records15 checks, including an own-source TS2322 negative control;
upstream declarations remain excluded under the previously documented SDK exception.


## Scaffold-owned Auth code and tests

The neutral Auth lifecycle and React hook are now managed copies in src/auth; their
behavioral suite is scripts/test-auth-lifecycle.mjs. auth-entry.ts and AuthEntry.tsx
remain KDG-owned boundary/UI adapters. `npm run test:auth` runs the generated23 cases;
the full auth-proof also runs those alongside the existing28 owner/SDK tests (51 total).

From repository root, with selected N, run
`N platform/builder-cli/scripts/sync-kdg-auth.mjs --check` before delivery. After template
changes, use --write through the same owning generator; it preserves owner files and
refuses manually edited managed files. Never edit generated Auth code/tests or
.generated-files.json by hand. Builder tests compare current templates as well as
installed hashes, so stale generated tests fail too. See platform/builder-cli/AUTH_PATTERN_EVIDENCE.md
from repository root for the ownership inventory, same-item maintenance rule and proof limits.

## Return selection candidate — 2026-10-23

The scaffold-managed Auth module now includes an in-memory return selector; KDG's
`createEntryReturn` in auth-entry.ts allows only `/` and rechecks the current private
context before selecting restoration. Callers clear/dispose on lifecycle changes;
provider callback and React navigation wiring remain separate. No URL payload, storage
or automatic confirmation is introduced. See [current evidence](../docs/AUTH_RETURN_EVIDENCE.md)
for test commands, caller obligations and the distinction from complete callback flow.

## PKCE launch/callback candidate — 2026-10-23

`createEntryOAuth` adapts the scaffold controller to the supplied PKCE-configured
Supabase client and current fixed-organization context API. Provider/scopes, exact URLs,
transaction storage and navigation remain explicit owner inputs. Callback success never
bypasses current KDG access. See [evidence](../docs/OAUTH_CONTROLLER_EVIDENCE.md) for
SDK/browser tests and limits. No public Auth client configuration or storage is activated.

## Existing-account email-code entry — 2026-10-23

KDG's selected sign-in uses emailed six-digit codes; no Entra provider, password form,
signup or OAuth redirect is required. `EmailCodeEntry` composes the generated controller/
hook with existing AuthEntry/current-context checks. `createKdgEmailAuth` uses explicit
public Auth configuration and persistent browser storage under `kdg-capture-auth`.
Storage failure refuses the client; there is no silent memory fallback. Unfinished
email/code input stays in memory; the SDK's verified session/profile is persisted and
rechecked on reload. The app source is qualified in an isolated synthetic browser harness;
public startup/configuration and actual mail delivery are not activated. Configure Auth's
email template to use `{{ .Token }}` and qualify delivery before real use.
See [owner evidence](../docs/EMAIL_CODE_ENTRY_EVIDENCE.md).

## Explicit local entry route

`mountKdgLocalEntry(root, options)` is an explicitly invoked local/CI host. The caller
supplies a React Root and fixed `org`, Auth `url`/`publicKey`; browser/storage and Auth/API
transports may be injected for synthetic qualification. It imports the owner CSS, checks
the org and root route before SDK/storage work, then creates one stable Auth client
outside React rendering. At that checkpoint there was no automatic environment lookup or main/index startup.
There is no public deployment target or default account. Disposal detaches browser/React subscriptions
and requests SDK refresh shutdown; it does not erase SDK sessions or revoke accounts.

Only `/` and the existing `#kdg-entry-content` skip-link anchor are supported. Unexpected
query/hash/callback paths scrub the current address/history state, close the entry and
show Go to start. No OAuth exchange or return-URL interpretation runs. The link performs
an explicit clean page load and fresh API checks; a previously completed SDK session may
be recovered on that load, including one saved after local cancellation. Route disposal
prevents that late completion from reopening the currently refused page. Scrubbing cannot
remove an initial HTTP URL already observed by a server; do not add sensitive URL logging.

Browser connectivity events keep the same mounted code form and resend guard; refusal
unmounts it synchronously. SDK refresh is requested to stop while offline/refused; already
started work can still finish and is never described as revoked. Application routers
using pushState/replaceState must emit their own route notification; these methods do
not raise popstate. The candidate listens to real popstate/hashchange/online/offline.
At that historical route-only checkpoint, the only consuming mount was `tests/auth-fixture/local-entry.tsx`, using synthetic
SDK transport and loopback API; the fixture's sessionStorage selector is harness-only,
not app configuration or unfinished form persistence. That checkpoint had no app main/index;
the following actual-startup section supersedes that limitation.

## Actual local frontend startup

The real `index.html` loads `src/main.ts`, which starts from one inert script named
`kdg-local-config`. Checked-in content is null: no configured target, account, grant or
Auth request. Missing/bad config uses the existing closed entry surface and route scrub.
Only local/CI loopback page and Auth origins are accepted. No URL/sessionStorage/Vite-env
fallback or configurable API target exists. KDG business API stays same-origin at
`/api/v1/context`; host-owned reverse-proxy/API routing is still needed outside the proof.

The exact public fields are schema_version (1), environment_kind (local_disposable or
ci_disposable), org_id (configured canonical nonnil UUID), auth_url (loopback HTTP/S
origin only), auth_public_key (publishable or legacy anon). Unknown fields are refused.
Never place service/private keys or tokens in HTML; validation cannot undo exposing data
already shipped there. Embed data as application/json, no src, exactly once, <=8192 UTF-8
bytes; serializers must escape less-than characters to prevent script termination.
No deployment/provisioning/configuration command or real fixture is introduced.

Pure public config validation has no SDK import. Startup preflights the route and online
state before loading the Auth mount: the selected SDK probes local storage at import
time. Cancellation can suppress later mounting, but cannot undo an already initiated
module import or SDK side effect. Pagehide disposes the active root; cached pageshow
restarts from current configuration/session/access, never cached admission. A missing or
duplicate root fails closed without creating a client. Existing unfinished form input
is memory-only; no survival promise is added for page lifecycle restoration.

Run the selected Node26.11.1 command `node apps/kdg-capture/web/tests/auth-proof.mjs`
from repository root using the retained tool paths above. It now builds both the prior
fixture journey and the actual copied app index/main, then serves synthetic config
variants and loopback Auth/API HTTP with network/DOM/storage instrumentation. No npm
workspace/lock/dependency changes were made to add KDG to root; root npm dev/build
remain unsuitable. A public deployment or normal installed dev-server command is not
qualified by this internal build/startup proof.

The retained Chromium headless shell explicitly disables back/forward caching (CDP
BackForwardCacheDisabledForDelegate). The proof covers real Back with a reload and
fresh denial, plus a separately simulated persisted-page lifecycle with fresh denial
and no old admission rendered. It does not claim an actual BFCache restoration.
Held/rejected lazy imports prove disposal, offline/route refusal and explicit recovery
without constructing the Auth owner after cancellation.

## Opt-in loopback development host

`local-host.config.ts` connects the actual frontend to a running KDG API at the same
browser origin. It does not start shared infrastructure or create accounts/access.
Use it only with disposable synthetic local/CI services and the retained approved
Vite 8.3.4 / Node 26.11.1 / React 19.3.0 / TypeScript 7.0.2 installation. There is
still no ordinary installed KDG workspace; root npm dev/build remains unsuitable.

Supply an absolute `KDG_LOCAL_WEB_CONFIG` file path through the local process environment.
The file must be a regular JSON file outside the application and all node_modules
paths, including resolved symlinks, at most 8192 UTF-8 bytes. It has exactly the five
public startup fields documented above plus `api_origin`, a fixed HTTP origin with
literal 127.0.0.1 and an explicit nonzero port. No credentials, service keys, API paths
or remote API targets belong in this file. There is no checked-in configured target.
Only the five validated public fields are embedded; api_origin remains host-side.

From the web directory, with N the selected Node and V the retained Vite bin/vite.js:

```sh
KDG_LOCAL_WEB_CONFIG=/absolute/private/synthetic-local.json "$N" "$V" --config local-host.config.ts
```

The default web port is 5177; `--port 0` requests an ephemeral proof port. Port conflicts
fail rather than selecting another port. Resolved configuration rejects non-loopback
host overrides, HMR, CORS, HTTPS and alternate proxies. This host is intentionally HTTP
loopback only, not LAN/device HTTPS, a PWA delivery server or a production reverse proxy.
It explicitly selects tsconfig.auth.json to avoid stale root project references.

The generated opt-in host helper bridges declared GET /api/v1/context only. Unknown
API routes return JSON 404, never app HTML. It forwards only the bearer and JSON Accept,
rejects request bodies and duplicate bearers, suppresses redirects/cookies/service keys,
bounds upstream responses to 64 KiB and total waits to 12 seconds, and returns private
safe errors for unavailable/invalid responses. Current KDG API authorization still runs
on every request. No browser Auth request is proxied through this business API route.
Ambient VITE values, public directory serving and HMR are disabled; served file roots
are constrained and test/config sources denied. Host logs contain a selected listen
origin only; they never print request URLs, payloads or configuration.

`local-host-tools` is a separate managed root so the existing fixed Auth inventory is
preserved. Update canonical builder templates/tests, then run selected Node from repo
root with `platform/builder-cli/scripts/sync-kdg-local-host.mjs --write`; CI uses --check.
Never edit its generated code, tests or .generated-files.json directly. Run
`node --test apps/kdg-capture/web/local-host-tools/test-local-entry-host.mjs` and
`node apps/kdg-capture/web/tests/local-host-proof.mjs` using the selected Node. The latter
uses a fresh retained dependency capsule and actual Vite CLI / KDG FastAPI, synthetic
Auth HTTP and synthetic Access transport; it uses no database or Docker command.
See ../docs/LOCAL_WEB_HOST_EVIDENCE.md for exact evidence and remaining gates.


Explicit saved-edit delivery remains unmounted. `createEditDeliveryEntry` exposes
`deliver({account_id, org_id, action_id})` under one admitted Auth execution lease;
`deliverSavedEdit` is its isolated execution primitive. `lookupPreparedEdit` reads
one retained command under own-read; `importCurrentDetail` imports validated detail
without renewing permissions. See [the delivery evidence](../docs/EDIT_DELIVERY_EVIDENCE.md).

From repository root with the retained approved Node26.11.1 executable:

```sh
platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node apps/kdg-capture/web/tests/edit-delivery-proof.mjs
platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node apps/kdg-capture/web/tests/edit-delivery-http-proof.mjs
```

These commands use existing ignored approved modules/Chromium/Python prerequisites
and selected-source capsules; they install nothing. The strict Auth compilation
uses approved retained modules and the existing upstream declaration-check exception.
The checkout's older root node_modules cannot qualify the approved Auth SDK contract.
Neither proof starts normal application entry, schedules delivery or accesses real accounts.

Protected setup remains an unmounted candidate. `createProvisionEntry` exposes
`load({account_id, org_id})`; `loadProvision` is the strict request primitive.
No setup, observation or command is persisted by these consumers. See
[setup contract evidence](../docs/PROVISION_CONTRACT_EVIDENCE.md).

Run from repository root with the retained approved tools:

```sh
platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node apps/kdg-capture/web/tests/provision-proof.mjs
platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node apps/kdg-capture/web/tests/provision-http-proof.mjs
platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python -B -m unittest discover -s apps/kdg-capture/write-tests -p 'test_provision*.py' -v
platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python -B apps/kdg-capture/write-candidate/export_provision_openapi.py --check
```

The unit proof executes the actual `tsconfig.provision.json` chain in a selected-source
capsule with approved retained modules, TypeScript7.0.2 and existing Auth `skipLibCheck`.
It uses Node's sequential test-file mode; individual cancellation/deadline assertions
still execute. The HTTP proof owns and stops its synthetic fixture. No normal API
startup, account access, dependency installation or actual database work occurs.


Atomic completed local-create Save is an isolated schema3 candidate. See
[owner evidence](../docs/LOCAL_CREATE_SAVE_EVIDENCE.md). Run the retained Node26.11.1
against `apps/kdg-capture/web/tests/local-create-save-proof.mjs` and
`apps/kdg-capture/web/tests/local-create-http-proof.mjs`
from the repository root for real Chromium IndexedDB and synthetic HTTP/Auth integration.
The proof uses TypeScript7.0.2 and explicitly selected source capsules; no installation
is required. Setup, editor and sender remain unmounted. Schema3 activation needs
separate browser-update/connection qualification; no older storage is deleted/reset.


Explicit saved-create delivery/recovery remains unmounted. See
[owner evidence](../docs/CREATE_DELIVERY_EVIDENCE.md). From repository root, run retained
Node26.11.1 against `apps/kdg-capture/web/tests/create-delivery-proof.mjs` and
`apps/kdg-capture/web/tests/create-delivery-http-proof.mjs`. These selected-source
proofs use approved TS7.0.2 and retained Chromium/Python; no install or native database
is required. The HTTP host seeds explicit synthetic eligibility and owns its shutdown.


Pending-create edit persistence extends the isolated store's explicit `openEdit` and
`saveEdit` with separate local-base actions and actual receipt predecessors. Original
create bytes remain immutable; no server baseline/revision/audit is fabricated.
Use the explicit delivery entries after predecessor receipts resolve. This is unmounted
synthetic functionality; see [evidence](../docs/PENDING_CREATE_EDIT_EVIDENCE.md).
Retained Node26.11.1/TS7.0.2 are required for `tests/pending-create-edit-proof.mjs` and
`tests/pending-create-edit-http-proof.mjs`; no install or startup activation is needed.


Explicit confirmed-server conflict resolution is unmounted. It reuses current own
read/edit-context and conditional PUT, retaining original proposals and paused
branches. See [evidence](../docs/CONFLICT_RESOLUTION_EVIDENCE.md). New local schema4
is isolated and requires browser update/recovery qualification before activation.
Use retained Node26.11.1/TS7.0.2 for `tests/conflict-resolution-proof.mjs` and
`tests/conflict-resolution-http-proof.mjs`; no dependency installation or API override.

Same-phone unprepared conflicts now have pure local review/choice/recovery methods.
They preserve selected pending work and original create bytes; replacements use actual
receipt predecessors through existing explicit delivery. No HTTP occurs during local
choices. Run retained Node26.11.1/TS7.0.2 against
`tests/local-conflict-resolution-proof.mjs` and
`tests/local-conflict-resolution-http-proof.mjs` from repository root. See
[local conflict evidence](../docs/LOCAL_CONFLICT_RESOLUTION_EVIDENCE.md). Schema4 stays
unmounted; browser update/recovery and native/release qualification remain separate.

Local-conflict qualification after review:883 focused real-IDB and71 HTTP checks,24
affected commands including five scaffold parities;13 findings addressed, none deferred.
The HTTP proof owns a90second watchdog and10second requests. Its --force-stall negative
qualification records deadline failure and confirmed synthetic fixture shutdown.

Retained-proposal extensions use the same explicit server and local decision APIs for
confirmed v2 conflicts, active unsent stale work and paused re-review. Ordinary PUT/
recovery still delivers fresh selected edits. With N set to retained Node26.11.1, run from repository root:

```sh
"$N" apps/kdg-capture/web/tests/retained-proposal-resolution-proof.mjs
"$N" apps/kdg-capture/web/tests/retained-proposal-resolution-http-proof.mjs
```

See
[retained-proposal evidence](../docs/RETAINED_PROPOSAL_RESOLUTION_EVIDENCE.md) for current
qualification. Existing schema4 remains unmounted; previous decisions/bytes are retained.

The unmounted online administrator read candidate has a separate no-observation page
contract. Its generated types cannot substitute for the own-history offline observation.
From repository root with N set to retained Node 26.11.1:

```sh
"$N" platform/deployment/.local/web-baseline-qualification/new-5/root/node_modules/typescript/bin/tsc --project apps/kdg-capture/web/tsconfig.admin.json
"$N" apps/kdg-capture/web/tests/admin-read-http-proof.mjs
```

See [online administrator read evidence](../docs/ONLINE_ADMIN_READ_EVIDENCE.md) for
current proof status and limits. No portal, all-record cache or startup activation.

The inert online audit metadata candidate is documented in
[ONLINE_AUDIT_READ_EVIDENCE.md](../docs/ONLINE_AUDIT_READ_EVIDENCE.md).
Its generated audit contract is separate from own-observation caching. It returns
stable actor IDs and committed revision metadata only; historical display-name and
portal contracts remain outstanding. No business response is persisted by this proof.

From repository root with N set to retained Node 26.11.1, qualify the audit contract and synthetic transport:

```sh
"$N" platform/deployment/.local/web-baseline-qualification/new-5/root/node_modules/typescript/bin/tsc --project apps/kdg-capture/web/tsconfig.audit.json
"$N" apps/kdg-capture/web/tests/audit-read-http-proof.mjs
```
