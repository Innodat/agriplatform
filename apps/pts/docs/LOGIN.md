---
title: 'PtS Supabase login and password setup'
type: 'feature'
created: '2026-09-24'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
---

<frozen-after-approval>

## Intent

Readers created or invited through Supabase can sign in with email and password,
request a password reset and set a password from a valid recovery/invitation link.
Microsoft sign-in is optional and appears only when explicitly configured. There
is no public registration form. Existing Supabase Auth and server-side PtS
membership/permission enforcement remain authoritative. Preserve validated
same-user return context and clear prior-account context when identities change.

</frozen-after-approval>

## Implementation Notes

- Small frontend change; no new runtime service, credentials, schema, grants or
  production mutation. User has authorized implementation and reversible local tests.
- Given a Supabase user, valid email/password opens the authorized reader; failed
  sign-in exposes a safe message and permits retry. Duplicate submission is disabled.
- Given a recovery/invitation callback, successful Supabase validation presents
  password setup before collection requests; failure cannot edit an older session.
  Reload and session refresh retain setup for the same account. Matching confirmed
  passwords are required; server password rules remain authoritative.
- Given a reset request, the result does not reveal whether the email exists.
  Expired links offer recovery. No password, callback token or raw Auth error is logged.
- Test desktop/mobile login, recovery, invitation, failures, optional Microsoft,
  unchanged reader behavior, and actual local Supabase callbacks.
- Scaffold/shared UI: keep the first application-specific form in PtS until proven
  reusable. Agent context: no change. Docs: local guide, Auth configuration and this
  delivery record. ADR: same Supabase identity and session-recovery decisions apply;
  no new architecture decision. Owner docs replace the earlier Microsoft-only assumption.


## Operator configuration

- Add users through Supabase Authentication → Users: create a password-based user,
  or send an invitation. Configure the Site URL and allowed redirect URL to PtS
  (`http://localhost:5179` locally). Configure SMTP for hosted email delivery.
- Keep public signup disabled in Supabase. The local configuration disables it;
  changing frontend visibility alone would not enforce that setting.
- Grant organization membership and explicit PtS permissions separately. Login
  and password setup never add memberships or application grants.
- Microsoft is optional: configure the Azure provider in Supabase, then set
  `VITE_MICROSOFT_SIGN_IN_ENABLED=true` at frontend build/start time.
- Recovery uses `resetPasswordForEmail`, the `PASSWORD_RECOVERY` event and
  `updateUser`; invitations also lead to password setup after successful Auth
  initialization. The SDK's implicit callback type is captured before its URL
  cleanup. Password setup state is bound to the authenticated account and retained
  across reloads in sessionStorage. Failed callbacks cannot reuse an older session.
- Passwords and tokens are never placed into app return URLs or operational logs;
  SDK session storage remains the existing authentication mechanism. Passwords
  are sent directly to Supabase Auth. No service-role key reaches the frontend.

References: [Supabase password recovery](https://supabase.com/docs/reference/javascript/auth-resetpasswordforemail)
and [administrator invitations](https://supabase.com/docs/guides/auth/users).


## Verification and review

Baseline: `e3abbaebc84f99d691042a305a64e1fb3580c18f`.
Initial acceptance red: the email-login test found the unwanted Microsoft-only
button before implementation. Auth-error fixtures initially lacked the cross-origin
exposed version header, so the SDK could not read their error codes. Corrected the
fixtures to reflect Supabase's wire contract without changing expected behavior.

Commands (from repository root):

```bash
LD_LIBRARY_PATH=/tmp/pts-browser-libs/usr/lib/x86_64-linux-gnu apps/pts/web/node_modules/.bin/playwright test --config apps/pts/web/playwright.config.cjs
PTS_TEST_MICROSOFT=true LD_LIBRARY_PATH=/tmp/pts-browser-libs/usr/lib/x86_64-linux-gnu apps/pts/web/node_modules/.bin/playwright test --config apps/pts/web/playwright.config.cjs login.spec.cjs --grep 'Microsoft sign-in'
LD_LIBRARY_PATH=/tmp/pts-browser-libs/usr/lib/x86_64-linux-gnu apps/pts/web/node_modules/.bin/playwright test --config apps/pts/web/playwright.config.cjs login.spec.cjs --grep 'tokenless|Microsoft sign-in'
npm run build --prefix apps/pts/web
```

- Full reader/login suite: **30 passed** across desktop/mobile (10.3s).
- Optional Microsoft enabled: **2 passed**, including provider URL and return context.
- Final focused checks cover empty-token callbacks and Microsoft hidden by default.
  The added provider test makes a subsequent complete default suite 32 cases.
- TypeScript/Vite production build passes; the existing >500 kB bundle warning remains.
- Actual local Supabase and Chromium: existing reader email/password login reads
  190 records; a fresh administrator invitation sets a password; an actual reset
  email captured in Mailpit opens recovery, updates the password and permits a new
  password login. The fixture has no organization/grants and cannot read the collection.
  Public signup returns 422. Existing reader credentials were not changed.
- Local Site URL now targets PtS. Global signup is disabled while email authentication
  remains enabled; disabling the CLI's email-level switch also disabled sign-in,
  which the live test exposed and the final configuration corrects.
- Desktop/mobile form screenshots inspected; no horizontal overflow. Browser tests
  use port 5181, leaving the configured local reader on 5179 undisturbed.
- No production settings, grants, schemas or source-library records changed.

## Review Triage Log

- **High, fixed — tokenless callback reused an older session:** callback intent is
  captured only with a nonempty access token, and initialization must succeed.
  The empty-token and expired-callback tests retain an older session without
  offering to change its password.
- **Medium, fixed — recovery lost the prior page:** saved allowlisted organization,
  poem and filter context is bounded to one hour and the prior authenticated user.
  It is consumed only for that user's recovery. The email URL carries none of
  those values. The desktop/mobile recovery test verifies restored filters.
- **Medium, fixed — failed logout hidden during password setup:** safe failure text
  is now passed to the visible form. Tests cover logout failure during invitation.
  Protected content is cleared immediately when logout starts.

All three actionable review findings were addressed; no deferred findings.
