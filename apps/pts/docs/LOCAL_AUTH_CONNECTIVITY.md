---
title: 'Repair Windows-to-WSL local Auth connectivity'
type: 'bugfix'
created: '2026-09-24'
status: 'done'
route: 'oneshot'
---

<frozen-after-approval>

## Intent

Local Windows readers must reach Supabase sign-in and password-reset links.
Use the reachable localhost hostname for browser Auth and generated links, retain
restricted server-side access, and make transport failures distinguishable from
invalid passwords without indefinitely disabling the form. Keep credentials out
of logs and tracked files. Do not change the user's password.

</frozen-after-approval>

## Implementation Notes

- Reproduced from native Windows curl: 127.0.0.1:54321 times out; localhost:54321,
  localhost:5179 and localhost:8010 respond. Both Auth hostnames work inside WSL.
  Supabase accepts the supplied credentials; the account initially lacks membership.
- Frontend .env.local uses localhost for Auth. Supabase api.external_url sets the
  same hostname for email verification links. Existing server URLs remain loopback.
- Auth fetches receive a 15-second abort deadline, preserving caller cancellation;
  transport failures show safe connectivity guidance rather than raw SDK errors.
- Given a dropped or stalled Auth request, show the connection message and re-enable
  retry. Given a fresh local recovery email, verify its link uses localhost and
  actually opens password setup. Existing login/reader tests remain valid.
- Scaffold/shared UI: no change; app-local Auth adapter and local config. Agent
  context/ADR: no change. Documentation: Windows browser hostname and live evidence.
- Organization assignment depends on the user's pending selection, not on login.

## Requested organization and production release

The user requested **PtS**, description **Psalms that Sings**, locally and when
production is released. `deployment/organization.json` is the release's organization
manifest. The current identity schema stores the description in
`identity.org.settings.description`; no new schema column is needed.

Production provisioning is a required explicit release step, not API startup work:

1. Use the approved production identity-owner operation to resolve/create slug
   `pts`, name `PtS`, settings description `Psalms that Sings`. If that slug exists
   with different metadata, stop for review rather than replacing it.
2. Resolve the intended user in **production** Supabase Auth and grant organization
   membership plus `pts.poetry.read`, `pts.poetry.export`, `pts.poetry.documents`
   through the identity/access owners. Never reuse local Auth or organization UUIDs.
3. Select the production organization for the user's platform Auth context. Bind
   the import service to that organization; run the canonical importer and private
   source upload/association tooling, validating 312/190/33 and all ten documents.
4. Verify current access, source privacy, hosted Auth URLs, mail delivery and release
   migration evidence before activation. Production database mutations and public
   deployment retain their existing approval gate. No production mutation occurred.

The local implementation creates an independent organization scope. The previous
PtS Local Testing organization is preserved. It does not grant platform administration
or add permissions beyond the three explicit Reader capabilities.


## Verification and review

- Native Windows curl reproduced the original IPv4 timeout. After the configuration
  fix, native Windows password login returns 200, the directory resolves PtS, and
  collection reads return 190 text / 312 total / 33 checked records. Document access
  produces a signed localhost URL. The supplied password was not changed or saved.
- New organization import: 663 canonical entities, zero conflicts; ten stored source
  documents finalized and associated in the new organization scope. The original
  testing organization remains intact.
- A freshly generated localhost recovery link opens **Choose a new password** in
  Chromium. No password update was submitted. A separate fresh reset email was left
  unconsumed in local Mailpit for the requested user.
- Initial browser acceptance failed because connection-reset errors showed only
  the generic login message. Final command:
  `LD_LIBRARY_PATH=/tmp/pts-browser-libs/usr/lib/x86_64-linux-gnu apps/pts/web/node_modules/.bin/playwright test --config apps/pts/web/playwright.config.cjs`
  returned **36 passed** in 26.9s. This includes desktop/mobile reset failures,
  the real 15-second abort deadline, invitations and existing reader behavior.
- `npm run build --prefix apps/pts/web` passes; existing >500 kB bundle warning remains.
- Blind review found no actionable defects. Caller-provided cancellation is retained
  by composing signals, but that branch has no dedicated test. Browser automation
  covers current Chromium; Windows connectivity was verified with native curl.
- Local API external URL follows [Supabase's documented localhost configuration](https://supabase.com/docs/guides/auth/social-login/auth-azure#local-development-with-azure-oauth).
