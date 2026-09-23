# ADR-0032: Session Recovery and Return Navigation

**Status:** Accepted  
**Date:** 2026-09-23  
**Scope:** Shared application shell, API client and authentication return flow

## Decision

Attempt normal session renewal when supported before interrupting the user. If
interactive sign-in is required, preserve recoverable application context and explain
that the user must sign in again to continue. Do not turn temporary authentication
service unavailability into a claim of revoked permission or an endless sign-in loop.

After successful sign-in, return the same authorized user to the location they were
using before authentication, including the active NGO, page, selected record, relevant
filters and recoverable drawer/form/draft context. Capture a validated internal return
target before navigation. Do not default to the home screen when the prior destination
is still valid and permitted. Restrict return destinations to approved application
routes/origins; reject arbitrary external redirects.

Restore context only after checking authenticated identity, current NGO membership,
permissions and resource access. A different signed-in person must not see or submit
the previous person's form. Removed permissions, deleted records or unavailable NGO
context require an explanation and a safe permitted destination rather than exposing
protected content or looping. Existing application draft ownership rules remain binding.

Preserve entered information where supported and tell the user if only the last saved
draft could be recovered. Never claim unsaved edits survived when they did not. Do not
put sensitive field contents, credentials or a complete form payload in return URLs.
Use existing scoped draft/recovery mechanisms; the concrete retention/storage policy
for unsaved values must be specified in affected UI stories rather than introducing
unreviewed persistent storage of sensitive forms.

After restoration, reload current permissions and refresh consequential calculations.
Sign-in completion alone does not submit or confirm the pending action. Resolve an
uncertain prior mutation using its original operation identity before allowing another
attempt; do not convert sign-in retry into a duplicate business action. Known access
denial remains distinct from authentication expiry and temporary connectivity failure.

## Impact and verification

- Acceptance: renewal without interruption; required sign-in returns to page/record/NGO
  and recoverable form context; malicious return URL rejected; different account and
  revoked NGO access protected; unavailable/deleted destination handled; uncertain
  mutation resolved without duplicate effect; honest partial draft recovery.
- Scaffold/shared UI: prove shared shell/API-client renewal and validated return context;
  applications own draft content and confirmation rules, generated clients share errors.
- Agent context: link identity-safe return navigation and no automatic confirmation.
- Documentation: builder/shared experience and Leave requirements/tracker synchronized.
- ADR: complements 0012, 0019, 0021, 0023 and 0031; accepted originals unchanged.
- Planning only; no authentication flow, storage mechanism or runtime navigation changed.
