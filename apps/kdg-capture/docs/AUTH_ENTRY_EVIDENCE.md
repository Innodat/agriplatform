# KDG Auth session bridge — 2026-10-23

The bounded slice is complete after Blind Hunter review:28 focused SDK/lifecycle
tests and15 built React/Chromium proof checks pass. See
[the durable receipt](evidence/auth-entry-20261023.json). bmad-help selected [BD] bmad-build for the next bounded
current-entry integration. Actual provider redirects/callbacks, PKCE storage and return
navigation remain unqualified; interactive launch is an injected owner action.

## Authority and behavior

Auth owns sessions. The bridge pins only SDK user.id/access_token for the unchanged
KDG current-context boundary; only a successful current KDG API response admits entry.
It subscribes before lookup, clears admission on new session/token events, ignores
superseded lookup/request/operation results and late INITIAL_SESSION after a live event.
A refresh for a different account fails closed instead of restoring its previous user.
SDK callback work is synchronous; asynchronous operations are deferred outside it.

Explicit Sign in with a known session attempts one SDK refresh. If the refreshed
context is still unauthenticated, continue the requested
interactive owner action once. SIGNED_OUT always takes precedence and cancels
recovery, requiring another explicit Sign in action. Completion of a launch does not establish admission.
Only a subsequent SDK session plus current KDG verification does. Permission denial
is distinct from expired authentication; no automatic sign-in/retry/refresh loop.

Local sign-out clears KDG admission immediately and calls SDK scope local. Logout,
error/timeout and disposal close admission against late events; explicit retry/sign-in
starts fresh observation. Offline prevents context network work, and changing the
React online prop recreates the bridge and rechecks current state before admission.
React layout-effect setup/cleanup supports strict replay, prop replacement and unmount.
Tokens/raw errors never enter view state, URLs, bridge logs or returned diagnostics.

Each executing observation/action has a10s deadline (shortenable in tests). Invalidation
settles obsolete returned work and aborts context requests even if transport ignores
cancellation. SDK work cannot be cancelled; late SDK mutation/revocation is not claimed
prevented. In particular SDK local logout can remove a replacement SDK session after
awaiting its response; the bridge stays closed, does not repair session data and does
not claim server revocation until SDK success. It remains the integrating Auth owner's
job to qualify provider configuration/storage and safe diagnostics. SDK debug is off
in tested fixtures, but upstream SDK error paths can log; no universal no-log claim.

## ATDD and focused TDD

The conservative bridge seed stayed signed_out. Before implementation, the acceptance
failed expected authorized / actual signed_out after start with a synthetic SDK session
and an actual own-context client request fixture. Proof auth-55393259-cf5b-4362-80af-ba0abc19db96
contains full unit.log and source capsule. Focused lifecycle tests then ran against
that seed in auth-6ce43271-4acd-488b-be14-16f23bb26848; most failures are absent callbacks,
so only the outer scenario is claimed as observed behavioral RED.

An emitted ESM import extension harness issue was corrected after first implementation;
its failure remains retained. The initial browser account-change proof exposed invalid
base64url synthetic JWT segments. The fixture now uses correct base64url and explicitly
checks setSession errors; account-change assertions were preserved. Both failed runs
remain retained. These are harness failures, not user behavior changes or live Auth proof.

Additional targeted tests failed before corrections: unauthenticated refreshed-session
fallback, refresh-emitted SIGNED_OUT fallback, and previous-account TOKEN_REFRESHED
rejection (auth-a7f1d28b-cdcc-49f6-aec8-644c5caf9686). The source correction preserves
those expectations; the pre-review proof passed19 tests and its browser journey; final review results follow below.

## Commands and dependency limits

From repository root, N is the selected retained Node executable:
platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node.
D is platform/deployment/.local/kdg-auth-entry-20261023.

- `N apps/kdg-capture/web/tests/auth-proof.mjs`: fresh source capsule, strict own-source
  TS7 compile,28 focused tests including actual SDK2.117.3, Vite8/React19 build and native
  Chromium journey. `--unit-only` omits browser/build; `--acceptance-only` selects the
  initial behavioral scenario after compile. Every invocation chooses a new proof root.
- Existing `screen-proof.mjs` and `entry.test.mjs` are the affected unchanged regressions.
  Exact final results and hashes follow after review.

Retained new-5 root supplies SDK2.117.3, React/DOM19.3.0 and TS7.0.2. Scaffold proof-dI2Gy9's
app-local modules supply Vite8.3.4/plugin6.1.2; its Playwright1.64 and the existing Chromium1248
are reused. No dependency install, manifest/lock update or previous proof rewrite.
Auth TS config adopts the already qualified skipLibCheck exception for upstream SDK
WebAuthn declarations (ENV_WEB_BASELINE_EVIDENCE.md); application source remains strict.
No full dependency-declaration/WebAuthn qualification is claimed or fabricated shim added.

Actual SDK tests use only injected in-memory storage/fetch: synthetic token/user/logout
responses, no external provider/account creation. Browser native fetch reaches only the
synthetic own API over loopback. Strict-mode mounting, token refresh, access denial,
explicit authentication recovery, account change, offline/reconnect, logout/owner-launch
and unmount/remount are covered. No browser local/sessionStorage persistence is introduced.
These fixtures do not exercise actual KDG handler/Access/SQL, Entra or installed devices.

## Five delivery impacts and exclusions

Scaffold: use existing client/shell conventions, no generated source edit or generic
Auth promotion. Shared UI: consume the unchanged KDG EntryScreen. Agent context: root
rules suffice, actual commands/usage in web README. Documentation: new owner evidence,
custody receipt, Build spec and additive handoff. ADR: existing Auth/scope/errors/session/
logging/release decisions, no new or changed accepted ADR.

No public entrypoint/configuration, provider registration/callback/return, domain setup,
persistence/queue, real sign-in/accounts/access, provisioning, Docker, Leave/editor,
production/deployment/pilot or cleanup. Fingerprints/HMAC remain deferred. This is not
complete Story1.1, installed-device, restore or release readiness.

## Review and final source-bound proof

Only configured Blind Hunter review ran, using the available isolated reviewer after
prior session thread limits. All seven findings are patched, none deferred:

- A subscription returned after synchronous callback/consumer disposal is detached.
- Every SIGNED_OUT cancels recovery; a generic SDK logout event cannot prove a failed
  refresh. The earlier self-authored test expected automatic fallback after that event;
  review exposed its unsupported assumption. The new concurrent-logout regression
  failed before correction in auth-4f51c5d4-9e3f-4b7d-9da5-e6cec4352880, together with
  reentrant-disposal cleanup. The revised rejected-refresh test requires a new explicit
  action after SIGNED_OUT; this is an explained safety correction, not a dismissed failure.
- Mismatched-account refresh results clear recovery and latch events closed until an
  explicit fresh retry. The new regression proves a later token event cannot bypass it.
- Actual SDK rejection tests prove proactive failed refresh can preserve an unexpired
  session (no SIGNED_OUT), whereas expired rejection removes it and emits SIGNED_OUT.
- Stalled getSession/refresh/interactive-launch/signOut all meet the selected deadline;
  late resolution/events do not reopen admission; explicit retry reacquires current state.
- Actual SDK owner replacement detaches the old bridge subscription while work is
  pending; old refresh cannot publish. Configured-org replacement rejects mismatched
  evidence and never displays prior admission, then a fresh valid configuration rechecks.
- The exact successful receipt and all source fingerprints are identified below.

The actual SDK failure tests initially assumed expired/proactive failures were identical;
source inspection of the retained _callRefreshToken proved the distinction. The fixtures
now test both paths separately without weakening their state or launch assertions.
The interactive-timeout recovery fixture also initially returned null for every later
lookup; it now makes a current session available for the explicit retry being tested.
Both harness failures remain retained in auth-a4360e97-c3c7-4396-afd6-cfb3f8baba87.

The pending interactive-launch state additionally reproduced a duplicate-action gap
in auth-fde1e989-7923-49d9-8f80-4b74ccfc8053; the fallback now stays checking until launch
completes, and a second Sign in cannot invoke the owner action again.

Final reviewed proof: D/auth-17ddb1cf-22a4-4be9-9db4-283ec7c8b413/result.json.
All28 tests pass in unit.log; all15 recorded checks pass; source fingerprints match;
the HTTP server stops normally. types-negative.log proves own-source TS2322 is still
rejected under the documented upstream skipLibCheck exception. No source shim or pin
change. Final emitted JS/CSS, screenshot, source capsules and selected tool hashes are
bound in the durable receipt. Prior failed/green proof directories remain intact.

Affected unchanged screen regression passes its13 proof checks and15 presentation
tests in screen-b33fb192-75e5-411d-8ebd-a03150fabeaf. D/screen-regression.log points to
that exact source-bound result. D/client-regression.log records29 passing client tests;
its strict TS7/readonly assertions also exit0. These do not qualify new API/native SQL
or actual provider/device behavior, and none was rerun or newly claimed here.

All437 protected prior KDG/API/contracts/Access/builder/root dependency files and the
approved dependency contract are unchanged from baseline
f3cf330322ca2beb8259f8ba5aab4f76c8dbf69c. The prior handoff is an exact suffix, prior web
README an exact prefix; only those authorized additive guides changed. Concurrent
work/commits and Docker resources are preserved. No cleanup or external messages.
