# Existing-account email-code entry candidate — 2026-10-23

User approved Supabase Auth email codes for KDG, with automatic account creation disabled.
Entra remains a future Leave requirement for two separate clients with their own Entra
accounts; no Leave/client setup is implemented. Current KDG architecture/discovery/
readiness/prerequisite and ENV provider assumptions are corrected, while all historical
OAuth/Azure code/tests/evidence remain platform capability history.

The neutral scaffold owns email-code state, hook and protected persistent-store behavior,
plus generated tests. KDG owns labeled form/presentation, fixed key and SDK configuration,
account-bound entry composition and current API admission. Only existing accounts may
request sign-in; the UI has no signup, role, membership or grant operation. The actual
SDK sends create_user:false and verifyOtp type=email. Send feedback acknowledges neither
account existence nor admission. Six digits, safe error identifiers, explicit resend,
restart, offline refusal and bounded work are enforced. Email/code values never enter
controller publications, return URLs or a separate browser draft store.

`createKdgEmailAuth` accepts an explicit public URL/key and persistent browser storage,
uses fixed key `kdg-capture-auth`, manual URL handling and no PKCE challenge for numeric
codes. Protected storage probes/round-trips only that namespace and fails with safe
identifiers on unavailable/dropped writes; SDK fallback to memory is not claimed as
persistence. Private/service keys and unsafe URLs are refused before Auth I/O. Existing
SDK declaration skipLibCheck exception remains upstream-only; own-source TS7 negative
control still fails TS2322. No dependency or root lock changes.

`EmailCodeEntry` suspends the previous lifecycle during code entry. Only a current
successful verification resumes AuthEntry, pinned to the verified account, with a fresh
private context check. Cancelled/stale SDK success cannot reopen that mounted entry.
Auth still owns SDK session side effects: a late valid verification can save a session;
this is tested rather than described as cancelled/revoked. Reload may recover that
current SDK session, always rechecking access and without previous form context. Successful local
logout removes its SDK record. A runtime storage failure latches the current store closed,
including after the underlying store recovers. Failed removal is not reported as logout: it
cannot guarantee persistent bytes are gone, and a later reload can read surviving bytes
if storage works again, always with fresh KDG access checks. No offline lease or domain readiness is inferred.

The root entry composition is exercised through the existing isolated Vite/Chromium
harness. No public frontend/environment activation, real email, user/grant provisioning,
Auth server configuration or provider/device/pilot qualification is delivered. Actual
email-code delivery requires Auth's email template `{{ .Token }}` and selected existing-
account policy; SDK signInWithOtp alone otherwise can send a link. Template/delivery
qualification remains explicit before real use; callback routes are unnecessary for
this numeric-code sign-in.

## Test-first and current evidence

- Generated acceptance RED: `platform/deployment/.local/scaffold-auth-lifecycle-20261023/proof-nT4gpK/tests.log` — prior68 pass; new code stage remains email.
- KDG acceptance RED: `platform/deployment/.local/kdg-auth-entry-20261023/auth-b35fce0d-8728-4b5f-85d2-78ea9fbe4abc/unit.log` — previous111 pass; new controller and client missing.
- Focused RED: `proof-alDSOE` under the scaffold parent. React form RED: `auth-60c9177e-412b-4c37-bffb-be15b3ef4156` under KDG parent, email_form_missing after clicking Sign in.
- Initial controller/store GREEN: `proof-j0br0c`; actual SDK GREEN: `auth-aff1bafa-4a94-47a7-9d8c-758c828b594b`. Native ESM diagnostic frame `auth-d2539328-38ef-402e-8c50-28e70c242ee5` retained; extension was corrected, not a behavioral RED.
- Initial composed browser GREEN: `auth-2003628e-38be-49fa-b6b0-1af14637dfcb`. Includes invalid code/retry, resend guard, no unfinished input storage, successful fresh context, session reload, current denial, local logout, unfinished reload reset and cancelled late SDK success.
- Two intermediate browser frames (`auth-b21a73be-7338-4e61-8037-845200466c13`, `auth-c6662b4e-79f5-485e-81d3-f902e7306955`) exposed missing API-version metadata in the synthetic Auth error fixture. Source-matched version header restores machine-code parsing; expected results were not relaxed.

Final configured review, requirement-to-test/source/log bindings and exact selected-tool
commands are recorded in the durable email-code receipt after final regression.

## Delivery impacts

Scaffold: neutral code/hook/storage and generated tests/guidance updated in the same
item through existing managed synchronization, no ownership inventory migration. Shared
UI: owner branding/form stays KDG-local; reusable state/hook scaffolded, no UI-package
promotion. Agent context: existing parity and owner-boundary guidance sufficient.
Documentation: selected Auth method, corrected current contracts, new evidence/receipt
and prepended handoff; historical sources remain. ADRs unchanged; applies0032/0023.
Synthetic local/CI only; concurrent work, historical evidence/Docker resources and the
approved TypeScript7.0.2 baseline preserved. No Leave/editor, production, real account/
access, provisioning, deployment/pilot, cleanup or fingerprints/HMAC.

## Review resolutions

Blind Hunter returned eight findings. All were accepted and resolved in this slice:
reconnect retains attempt/cooldown; send masks known account-status errors including
user_banned while preserving rate-limit/outage feedback; actual SDK tests exercise late
write/read/remove failures and the latched store; final browser error assertions cover
the entire email journey; replacement races cover org changes and late A after B; direct
keyboard/focus/label/disabled/narrow/200% form checks pass; restart explains cooldown;
ENV's redirect callback prerequisite is conditional rather than required by numeric codes.
The retained browser failure exercising disabled resend used Playwright's enabled-only
click guard; the proof now uses actual keyboard activation and verifies no request.

The owner-replacement race also exercises the SDK's same-key BroadcastChannel: late A
emits an event to B's new client. The accepted-account gate deliberately closes admission
on that foreign event, while B's own stored session stays B; no A context request runs.
The first proof wrongly expected B's landing to stay open after that event. Inspection
confirmed the existing fail-closed policy; final proof checks the closed entry and B's
unchanged SDK identity rather than weakening the gate or treating the event as admission.

## Final proof

[Durable receipt](evidence/email-code-entry-20261023.json) binds source and proof hashes,
commands, preservation and requirement-to-test traceability. Final composed capsule:
`auth-610024c0-121f-4763-a643-ad591de92dfd` (138 tests,42 checks). Neutral rendered proof:
`proof-Gw6awI` (90 tests). Fresh offline generation: `proof-pYzxrY` (bootstrap_only true,
generation_ready false). Builder68/68 and strict TypeScript7.0.2 pass. All eight review
findings fixed; follow-up static review found no residual concrete gaps.
