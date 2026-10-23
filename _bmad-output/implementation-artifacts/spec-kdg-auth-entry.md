---
title: KDG Auth session integration
created: 2026-10-23
type: feature
status: done
route: oneshot
review_loop_iteration: 0
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

Connect the current KDG entry screen to the retained Supabase Auth SDK's session
lifecycle through a small typed bridge and React binding. Existing Auth owns identity,
tokens, refresh and interactive login; KDG API remains current application authority.
Given an existing SDK session, when starting entry, then subscribe before lookup and
check its bearer/account through the existing context boundary. Given a newer session,
token refresh, logout or account change, then clear admission immediately and prevent
older lookup, request or SDK-operation completions from restoring it. Ignore a late
INITIAL_SESSION after a newer live event. Never await SDK work inside its event callback.

Given authentication-required entry with a current session, when Sign in is explicitly
selected, then attempt one SDK refresh before the injected owner interactive-login action.
Only a newly observed current session and successful KDG context check establish entry;
resolving an interactive launch alone does not. Given explicit local sign-out, timeout,
error or disposal, then fail closed, bound returned work and ignore late completions.
Logout/timeout latch admission closed until explicit retry/sign-in; unsubscribe on
unmount, including React strict effect replay. Offline input prevents context network
work and re-entry reacquires current session. No token/error payload is published/logged.

Bound each executing bridge observation/action to10s, including headers/body via the
existing client; tests can shorten it. Invalidation settles obsolete returned work even
when SDK/transport ignores cancellation. Late SDK side effects cannot be cancelled;
never claim session deletion/revocation succeeds until SDK confirms it. Sign-out uses
scope local, never default global. No automatic sign-in/retry/renewal loop.

Use behavioral ATDD and focused TDD, SDK2.117.3 with synthetic storage/fetch and built
React/Chromium proof. Keep existing screen/client/API/contracts/history unchanged;
append docs/evidence and preserve concurrent work/dependency baseline, including TS7.0.2.
Interactive redirect/callback, PKCE persistence, return navigation, provider registration,
real accounts/access, new client configuration/public activation, domain persistence,
Leave/editor, Docker, provisioning/deployment/pilot and cleanup remain outside scope.
Fingerprints/HMAC stay deferred. No complete Story1.1/provider/device readiness claim.
</frozen-after-approval>

## Implementation Notes

- bmad-help selected [BD] bmad-build. This small session integration prerequisite has
  no unresolved visible choice/irreversible action; existing user authorization covers
  preserving and excluding dirty concurrent work. No Leave epic/sprint artifacts touched.
- Read current handoff, Story1.1, contracts, UI evidence, scaffold AuthContext and ENV
  callback contract. SDK source investigation establishes event ordering and async
  callback hazards. Legacy scaffold lacks bearer/generation guards; do not copy it.
- Add web/src/auth-entry.ts and AuthEntry.tsx, standalone tsconfig.auth.json, focused
  tests and synthetic SDK/browser fixtures. Reuse existing entry.ts/EntryScreen/CSS
  unchanged. Use retained new-5 SDK/React/types and scaffold-local Vite8/plugin; no install.
- Interactive launch is injected because provider callback/storage/return is not yet
  qualified. getSession handles SDK expiry renewal; explicit authentication recovery
  refreshes once. SDK local logout can clear a replacement SDK session after waiting;
  bridge stays closed, never promises SDK side effects are cancelled or restored.
- Scaffold impact: reuse conventions, no generic/template promotion. Shared UI: reuse
  current KDG screen unchanged. Agent context: root rules suffice, document real commands.
  Docs: new owner evidence/receipt and additive handoff. ADR: existing Auth/access/session/
  logging/release decisions; no accepted ADR edit or new decision.

- Final source-bound proof auth-17ddb1cf-22a4-4be9-9db4-283ec7c8b413 passes28 focused
  SDK tests and15 checks, including a TS2322 own-source negative control. Auth-specific
  skipLibCheck follows the prequalified upstream WebAuthn exception; TS7 unchanged.
- Existing29 client tests/strict readonly types and15 screen tests/13 browser checks
  pass unchanged. Initial acceptance RED and all failed/harness attempts are retained.
- Corrected pending fallback to checking after an observed RED, suppressing duplicate
  owner launches. Provider redirects/callback/storage/return remain injected owner work.

## Review Triage Log

Only configured Blind Hunter review ran; reused the available isolated reviewer after
known session thread limits, then waited for completion. No other layer configured.

- medium, patch: synchronous registration callback could dispose before returned
  subscription assignment; observed RED, immediately detach on disposed registration.
- medium, patch: SIGNED_OUT during recovery was incorrectly assumed refresh failure;
  concurrent logout RED proves ambiguity. Always latch logout and cancel recovery.
  Revise the explained self-authored failed-refresh expectation; another explicit
  Sign in is needed after any logout event. Frozen user intent remains unchanged.
- medium, patch: mismatched refresh result left events unlocked; clear recovery and
  latch closed. Regression verifies subsequent token event cannot admit that account.
- low, patch: real SDK failure semantics absent; add proactive and expired rejection
  tests. Retained source shows only expired rejection emits logout; both paths pass.
- low, patch: deadlines covered only lookup; stalled refresh/launch/local logout now
  prove timely resolution, ignored late events and explicit-retry reobservation.
- low, patch: owner/config replacement absent; built React fixture replaces actual SDK
  clients and configured org under pending requests, proves detached old subscription
  and no stale admission. Provider/client configuration remains outside runtime code.
- low, patch: successful receipt unnamed; identify exact source-bound green and all
  affected regressions in owner evidence, with final durable custody hashes.

No review finding deferred.437 protected files, dependency contract, full prior handoff
and prior README prefix remain intact; concurrent work/resources/history excluded.
