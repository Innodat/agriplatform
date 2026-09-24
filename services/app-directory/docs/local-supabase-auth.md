---
title: 'Recognize current Supabase sessions in the application directory'
type: 'bugfix'
created: '2026-09-24'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
---

<frozen-after-approval>

## Intent

Local Supabase issues ES256 sessions. The directory's legacy HS256-only verifier
silently treats them as anonymous, preventing PtS organization resolution and
launcher navigation. Accept current Supabase sessions through the configured
project's Auth verification endpoint, retain legacy HS256 compatibility, and fail
closed for invalid sessions or unavailable authentication. Use the existing Auth
service; introduce no login service or authorization bypass.

</frozen-after-approval>

## Implementation Notes

- Live acceptance failure: valid local Supabase session reads PtS successfully,
  but `/api/me/apps` returns an empty list and null organization.
- Given a valid current Supabase session, directory lookup must return PtS and
  its organization; forged, expired, wrong-project and unavailable verification
  must not return authenticated context. Existing HS256 verification must pass.
- Update owning scaffold `platform/builder-cli/templates/backend/auth/jwt_optional.py`
  and refresh the directory's vendored copy from that template. No generator CLI
  exists yet. Bounded Auth HTTP verification matches the existing access owner.
- Scaffold impact: current Supabase Auth support. Shared UI: none. Agent context:
  none. Documentation: directory configuration and local PtS runbook. ADR: no new
  decision; existing Supabase identity and application authorization stay intact.
- No intent gaps or irreversible operations. Existing working-tree edits belong
  to this authorized local setup. No production change or deployment.

- Focused red: 2 failures (ES256 returned anonymous; vendored verifier differed).
  Final: `/tmp/pts-venv/bin/python -m pytest services/app-directory/tests/test_supabase_auth.py -q`
  run outside sandbox: **11 passed**, one upstream TestClient deprecation warning.
  The sandboxed TestClient invocation stalled; the same suite completed in 0.34s
  with normal local process permissions.
- Live acceptance: actual Supabase ES256 sign-in resolves PtS and organization;
  Chromium follows a real magic link, displays 190 records and filters to 33.
  Full local data/storage evidence is recorded in the PtS local setup runbook.
- Refreshed the existing Supabase settings block from the scaffold configuration
  template into the vendored directory configuration, preserving app-specific fields.

## Review Triage Log

- **Medium, fixed — configuration loader bypass:** URL/key now come from Settings;
  a test loads `.env.local` without exported variables. The configuration block is
  sourced from the existing scaffold template.
- **Medium, fixed — endpoint acceptance missing:** added the actual directory router
  TestClient check for PtS and organization context; also verified real local
  `/api/me/apps` and Chromium sign-in with the platform's auth hook.
- **Low, addressed at owned boundary — security coverage:** added RS256 branch
  coverage alongside ES256, denied/mismatched responses and Auth failure. Live
  Supabase rejects forged signatures and tokens with tampered expiry/issuer claims.
  These are not claimed as independently signed, legitimately expired/wrong-project
  fixture tokens; cryptographic verification belongs to Supabase Auth, and the
  directory fails closed when it rejects a token.
- **Low, documented — timeout semantics:** HTTPX uses five-second per-operation
  timeouts, not a total request deadline. Clarified the service documentation.
  An additional cancellable networking subsystem for a hostile slow-drip response
  from the configured trusted Auth server is outside this small compatibility fix.
