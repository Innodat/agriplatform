---
title: 'KDG email-code entry and isolated session storage'
type: 'feature'
created: '2026-10-23'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

Connect KDG's existing session/current-access/entry presentation to its selected non-Entra Supabase Auth sign-in method and explicit local/CI browser storage and route composition. The user clarified that Microsoft Entra ID is not used for KDG; Entra is a later Leave requirement for two separate clients with their own Microsoft Entra accounts. Keep reusable Auth/session/return/storage behavior and behavioral tests scaffold-owned, with KDG-specific fixed-org, route and admission policy local.

## Boundaries & Constraints

**Always:** Honor the user's non-Entra KDG choice. Authenticate through Supabase Auth; use the KDG API for current business admission. Keep exact fixed organization and account isolation, fresh access checks, safe errors, no callback credentials/form values in URLs or logs, and no automatic domain action after sign-in. Declare the selected Auth/session persistence and any temporary return-state policy explicitly before wiring. Reuse the generated lifecycle/return helpers; existing OAuth helper qualification remains reusable platform evidence rather than a KDG provider mandate. Update applicable neutral scaffolding and emitted tests in the same item. Observe behavioral acceptance RED before implementation and focused TDD before risky changes.

**Never:** Invent a KDG sign-in method from historical synthetic password or Azure fixtures. Do not implement Leave, configure either Leave client's Entra trust/registration, create accounts/grants, provision, deploy, access production or real accounts, remove historical resources/evidence, or change the approved dependency baseline including TypeScript7.0.2. Fingerprints/HMAC remain deferred. Preserve concurrent changes and Docker resources.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| Entry | Current selected Auth session | Fresh fixed-org KDG context before protected landing | Denied, setup, unavailable and unauthenticated remain distinct |
| Selected sign-in | Explicit user action using the chosen Supabase method | Only that method's necessary form/request/return flow | Safe inline recovery; no raw Auth response or credential logging |
| Return if applicable | Selected method uses a callback | Clean address before processing, fresh current authority, permitted internal destination only | Malformed/replayed/foreign callbacks fail closed |
| Lifecycle | Logout, another account, owner change, unmount or late completion | Prior admission cleared; no prior-user data or stale return publication | Explicit retry, no automatic consequential replay |
| Persistence | Reload/reopen under the declared storage policy | Behavior matches the explicitly selected retention policy | Unavailable browser storage fails safely, no silent private-data fallback |


### User decision and bounded implementation

The user approved emailed one-time code sign-in for existing KDG accounts, with automatic account creation disabled and no access grants. Implement a six-digit email/code surface on the existing KDG entry composition, with explicit user send/verify/resend/restart, generic non-enumerating send feedback, safe typed errors, bounded work and late-result suppression. SDK verification alone never grants KDG access. Persistent SDK sessions use a fixed KDG-specific browser storage key; unfinished email/code input is memory-only and reload restarts that unfinished interaction. Storage failure fails closed rather than silently claiming persistence. The current online session/admission rules stay binding; no offline lease/domain setup is added. Numeric email codes require no OAuth redirect; retain generic OAuth code/evidence as an optional platform capability, including future Leave needs. Only synthetic local/CI SDK/browser proof is activated here; actual mail delivery/template configuration remains separately qualified.

</frozen-after-approval>

## Implementation Notes

- Resume draft after explicit user method approval. Original frozen draft intent preserved verbatim above; the appended user decision resolves the question. Reversible single-goal candidate, no irreversibles or remaining method choice. Storage follows existing SDK browser persistence convention with fixed app key and no memory fallback; this is an implementation choice disclosed in commentary, not a new offline authorization policy.
- Step02 investigation reused investigate_entry_view. SDK2.117.3 signInWithOtp must pass shouldCreateUser:false; verifyOtp(type:email) saves/emits SIGNED_IN before resolving. Numeric verification does not consume PKCE verifiers, so this client explicitly uses manual URL handling and non-PKCE numeric-code flow. Server email template determines code vs link; no real template/provider changes or mail are performed.
- Code map: builder templates/application/web/src/auth/lifecycle.ts and use-lifecycle.ts plus scripts/test-auth-lifecycle.mjs own neutral controller/hook/storage protection and emitted tests; existing sync-kdg-auth preserves the three-file ownership inventory. KDG web/src/EmailCodeEntry.tsx owns form/entry composition, web/src/email-auth.ts owns fixed-key SDK client and safe public config, existing AuthEntry/EntryScreen/entry.ts own refreshed admission. Extend existing tests/auth-entry.test.mjs, fixture and auth-proof capsule; preserve all prior tests/evidence.
- Plan: emitted controller acceptance RED and consuming actual SDK RED first; focused TDD for strict request fields, safe rate-limit/invalid/expired code errors, restart/disposal/timeout, persistence failure and account binding. Then prove labeled real React form, live-region feedback, invalid code/retry, persisted reload/current denial/logout, no code/email persistence and no Entra navigation with actual SDK and loopback API fixture. Run managed parity, builder regression then full offline generation sequentially.
- UI composition suspends the existing lifecycle while entering/verifying a code; only a current successful attempt mounts fresh AuthEntry. Pin its accepted account so unrelated/late SDK account events clear admission instead of restoring an old verification. Do not claim SDK side effects can be undone. Restart/dispose clears local attempt identity and prevents late completion from mounting entry.
- Impacts: scaffold applicable for neutral OTP lifecycle/hook/storage tests, same delivery; shared UI package promotion unnecessary (KDG branding/layout stays owner-local, reusable state/hook is scaffolded); agent context existing parity and owner-boundary guidance sufficient; docs complete prior non-Entra corrections plus selected method/evidence/handoff; accepted ADRs unchanged, applies0032/0023. Preserve concurrent Leave/Scribeswell/deployment/root docs and baseline TS7.0.2. No root lock or dependency changes.

- Final verification: 90 emitted tests plus48 KDG-owned tests =138, all pass; composed TS/SDK/React/browser proof42 checks, own-source TS7 negative control retained. Builder68/68; strict builder TypeScript pass; full offline fresh generation bootstrap candidate pass (generation_ready remains false); managed template/test parity pass. Exact commands/source/log hashes in apps/kdg-capture/docs/evidence/email-code-entry-20261023.json.
- Review follow-up confirmed all eight fixes by static inspection, no residual concrete gaps; reviewer did not rerun tests. No deferrals from this delivery. Real email/template/service/device qualification remains the declared outside-scope limitation, not a completed integration.

## Review Triage Log

1. medium — patch: online was a controller-creation dependency; browser RED auth-cdd3c512 reproduced lost code stage. Hook preserves controller, updates connectivity separately; final reconnect/cooldown check passes.
2. medium — patch: user_banned differed from generic send ack. Generated RED proof-B0ZqgA reproduced; known account statuses now masked with tests, outage/rate-limit feedback retained.
3. medium — patch: late storage failures lacked actual SDK proof and recovery could read surviving bytes. RED proof-tkE6B6 retained. Store latches closed; actual SDK write/read/remove tests prove unavailable results and no false persistence/logout. Failed deletion may leave bytes for later reload; disclosed, no revoke claim.
4. medium — patch: browser error assertions preceded email phase. Final exact HTTP/console expectation after complete journey now fails unexpected errors.
5. medium — patch: new composition lacked owner/account race proof. Remount owned state on Auth/org change; browser proves old A after verified B cannot request A context or reopen admission. Same-key SDK broadcast intentionally closes B admission while retaining B's own stored session; initial incorrect open-landing expectation investigated and corrected to the established fail-closed contract.
6. medium — patch: existing presentation checks did not cover new form. Direct keyboard, field labels, rejection/reconnect focus, disabled resend/request activation,320px and200% text checks pass.
7. low — patch: restart retained deadline with ordinary guidance. Display waiting feedback while resend deadline blocks new email send; browser proves guidance and keyboard refusal.
8. low — patch: stale current ENV row required provider callback. Corrected existing numeric-code prerequisite, keeping redirect callbacks conditional; no new architecture decision.
