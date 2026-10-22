---
title: KDG browser current-entry session boundary
type: feature
created: 2026-10-22
status: done
route: oneshot
review_loop_iteration: 0
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

Deliver the next small browser-side prerequisite of Story1.1: a typed own-API current
context client and session-generation boundary. Browser entry means sign-in/current
access checking and the setup-not-completed landing screen; this increment supplies
the access/session boundary before assembling that screen and its provider callback.

Given an Auth-owned current session and configured organization, when checking entry,
then call only GET /api/v1/context with its bearer, no selectors/body, no-store,
same-origin and redirect refusal. Validate the generated Context shape, exact current
account/organization/own scope, permission, canonical IDs, bigint-string membership
and UTC date. Preserve safe distinct authentication-required, denied, actor-setup,
unavailable and malformed-response outcomes; no raw body/message/token presentation.
Bound headers and body together within10s; abort/cancel safely and retain no authority
from an earlier successful check. Given logout, account change or another recheck,
then clear admission synchronously and ignore all prior completions, even transports
that ignore abort. Disposal prevents later publication.

Behavioral ATDD first, focused TDD and actual Chromium/native-fetch synthetic HTTP
proof. Use existing generated DTOs and approved TypeScript7.0.2/retained browser tools.
No dependency/lock updates, React/provider implementation, live sign-in/account/access,
return navigation, local/offline storage, domain writes, Leave/editor, provisioning,
deployment/pilot, Docker/resource changes or cleanup. Fingerprints/HMAC stay deferred;
preserve concurrent work and historical evidence. This is not complete browser entry.
</frozen-after-approval>

## Implementation Notes

- bmad-help selects [BD] bmad-build for this independently testable browser boundary.
  No user intent gap or irreversible operation; small owner module/tests/evidence.
  Existing dirty concurrent work remains explicitly authorized and excluded.
- Reuse contracts/generated/types.gen.ts Context and own-fetch template conventions;
  existing legacy AuthContext lacks bearer/current-entry and late-session guards, so
  do not copy it into a purported qualified provider flow. No new Auth owner/service.
- Use web/src/entry.ts plus standalone strict tsconfig, Node tests and a Chromium test
  fixture. No app workspace/package/lock changes or public frontend activation.
- Full Story1.1 sign-in, renewal/return/navigation, React UI/accessibility and actual
  provider qualification remain next consuming work; client emits no automatic renewal
  or navigation and cannot grant server authority or an offline lease.

- Final verification:29 Node tests; strict TypeScript7.0.2 including nested readonly
  assertions; seven real Chromium/native-fetch synthetic fixture checks. No package
  installation or backend change. Evidence and preservation receipts are owner docs.

## Review Triage Log

Configured Blind Hunter completed; no other review layers are configured for oneshot.

- medium, patch: year0000 passed JS Date but violates Python DTO; observed RED, reject it.
- medium, patch: ignored-abort late headers leaked body reader after cleanup; observed RED, cancel late body before acquiring reader.
- medium, patch: reentrant publish overwrote replacement controller; observed RED, clear completed controller before callback and return its own result.
- low, patch: nested TypeScript scopes were mutable despite runtime freeze; nested readonly types and compiler mutation assertions align the contract.
- low, patch: in-flight disposal/body abort lacked direct tests; new tests verify cancellation and no later publication.
- low, patch: nested extras/missing fields/malformed UTF-8 lacked direct tests; added closed-schema regressions.
- false, reject: preliminary trailing-newline regex suspicion withdrawn; selected Node runtime and actor/member newline tests reject the inputs unchanged.

All final checks pass; no review finding deferred. Complete Story1.1/provider/UI work
remains a separate consuming slice, as frozen intent requires.
