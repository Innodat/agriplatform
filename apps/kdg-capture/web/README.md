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
