---
title: Public launchpad and synchronized reader session
created: 2026-09-25
status: done
route: oneshot
---

<frozen-after-approval>
## Intent

Show the app launchpad in Scribeswell for anonymous and signed-in readers, and synchronize sign-in/sign-out with PtS while all existing Bible reading and morphology remain public. Preserve existing PtS sessions and authorization. Use the same Supabase project and browser origin for both trusted platform apps, with Scribeswell under `/scribeswell/`, and the existing `pts-auth` storage key/Supabase session notifications. No tokens in navigation URLs, custom authentication service, database changes or production deployment.
</frozen-after-approval>

## Implementation Notes

Root cause: different localhost ports and Supabase storage keys isolate sessions. Scribeswell already imports the launcher but its hook calls the authenticated-only `/me/apps` listing. Reuse the existing public `/apps` catalogue (filter disabled entries) for anonymous discovery; this does not grant collection access. Retain PtS read/document/export server-side checks.

Local routing preserves PtS `http://localhost:5179` and its stored session. Its Vite server proxies `/scribeswell/` to the separate Scribeswell frontend; that frontend strips its configured base only when proxying Bible API requests. Legacy 5174 browser navigation redirects to the canonical origin. Keep separate application builds/APIs; this is hosting configuration, not a server implementation import. Production needs the equivalent same-origin routing and same Supabase project before activation.

Impact decisions: scaffold has no implemented generators for this composition; shared UI is already reused, no new component. Agent context unchanged. ADR-0001/0032 boundaries remain intact; deployment/session sharing decision is documented here, with same-origin apps treated as one trusted browser security boundary. No accepted ADR edited. Documentation: local setup and release routing notes updated. No intent gaps or irreversible work; user already authorized local integration and synchronization.

Acceptance: an existing PtS session is recognized by Scribeswell without another login; login/logout from either tab updates the other; changing account clears prior PtS content; signed-out Scribeswell shows enabled app links and reads Hebrew/morphology; nested URLs preserve book/chapter without credentials; existing PtS reset/recovery behavior stays covered.

## Review triage

- Medium, fixed: configuration was not reproducible from tracked examples. Added the base/canonical origin to `.env.example` and documented matching Supabase and directory settings, routing, start commands and production requirements.
- False: review claimed the directory rejects localhost:5179 by default. `services/app-directory/main.py` already adds the configured PtS catalogue origin to CORS; no generated configuration edit is needed. Shared-reader requests use that same origin.
- Medium, fixed: a stale sign-in dialog survived another tab's login. Authentication now unmounts and closes the dialog; tests confirm fields are cleared when reopened.
- Medium, fixed: mocks bypassed the nested API proxy. Added a fixture HTTP server and test asserting it receives `/api/bible/*`, with `/scribeswell` removed by the real proxy.
- Medium, fixed: shared-session refresh/recovery coverage was missing. Added successful and failed refresh, password recovery completion and sign-out during recovery with both apps open.

## Verification

Initial two-app acceptance failed twice because nested routing was missing; after implementation those two tests passed. Expanded final suite: 11 passed (26.0 seconds), covering login/logout in both directions, public launchpad/morphology, failed logout, account replacement, canonical redirect, real API proxying, obsolete dialogs, refresh and recovery. Command: `LD_LIBRARY_PATH=/tmp/pts-browser-libs/usr/lib/x86_64-linux-gnu node_modules/.bin/playwright test --config apps/scribeswell/web/playwright.session.config.cjs`.

Regression commands: `LD_LIBRARY_PATH=/tmp/pts-browser-libs/usr/lib/x86_64-linux-gnu npm run test:browser --workspace=apps/scribeswell/web` — 16 passed (20.5 seconds); `LD_LIBRARY_PATH=/tmp/pts-browser-libs/usr/lib/x86_64-linux-gnu apps/pts/web/node_modules/.bin/playwright test --config apps/pts/web/playwright.config.cjs` — 46 passed (37.8 seconds). Both application build commands passed. Existing large-chunk build warnings remain.

After environment resumption, temporary Chromium libraries were missing and prevented browser startup; restored libnspr4, libnss3 and libasound2t64 under `/tmp/pts-browser-libs` and reran all suites. An interrupted test-file write left trailing null bytes; removed that padding before the successful runs. Neither failure was hidden by changing application expectations.

No database migration, reimport or production deployment. Development proxy and same-origin deployment instructions preserve separate application/API ownership.

Live verification passed on the prepared local Supabase stack: existing PtS test-reader session was recognized through the launchpad at `/scribeswell/`; Scribeswell sign-out cleared PtS; anonymous app links, Genesis reading and word morphology remained usable; mobile layout had no horizontal overflow; legacy port 5174 redirected with Psalm 23 selection preserved. Both local app stacks are running. The independent oneshot review completed and all substantiated findings were fixed; none deferred.
