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
