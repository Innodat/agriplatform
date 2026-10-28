---
title: 'Story 3.1 real local administrator entry and session integration'
type: 'feature'
created: '2026-10-28'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '00c087ac655e10218f82b8c20fe12b390522e828'
context:
  - apps/kdg-capture/AGENTS.md
  - apps/kdg-capture/docs/DESIGN.md
  - apps/kdg-capture/docs/STORY31_ACTIVE_HTTP_EVIDENCE.md
  - apps/kdg-capture/docs/EMAIL_TEMPLATE_CONTRACT_EVIDENCE.md
  - platform/docs/development/bmad-codex-usage.md
---

<frozen-after-approval reason="user approves successive necessary local Story3.1 items and routine BMAD checkpoints">

## Intent

Make the existing administrator review available through the ordinary local frontend,
real Supabase SDK session lifecycle and running KDG API. Use a distinct `/admin` entry
with current all-read admission, existing email-code sign-in and responsive history,
original-definition details and read-only audit. Qualify actual local session/access
changes and absence of administrator business persistence, then continue remaining ACs.

## Boundaries & Constraints

The administrator surface never requires own-read first and never falls back to it.
Preserve the existing own entry and numeric-code existing-account policy. Reuse the
email form and accepted-account fence, stable boundary/callback instances and reviewed
administrator controller. SDK/Auth callbacks do not themselves authorize records.
Session/account changes, signout, offline, page lifecycle disposal and explicit fresh
verification remove prior rendered data before awaiting new checks. Reconnect/restore
requires fresh all-read; known denial differs from unavailable. Ignore old HTTP outcomes.

Keep service keys, database credentials and Identity control plane out of browser config
and requests. The local host forwards only browser bearer headers to explicit GET read
routes, with canonical capture UUID paths, bounded payloads, private/no-store responses,
timeouts and cancellation. Preserve context proxy behavior. Update the owning neutral
proxy template/tests and regenerate its KDG adoption; never hand-edit generated files.
No all-record IndexedDB, localStorage, CacheStorage, service-worker download or offline
authority. Authentication persistence remains SDK-owned. Preserve saved own work.

Fresh synthetic local Auth/SMTP/database/browser work is authorized. Use existing pinned
tools and approved numeric-code template; no dependency upgrade, real account/credential
change, production deployment, push or destructive cleanup. Retain resources and failures.
Never access/run/copy/hash apps/kdg-capture/migrations/tests/schema_fixture.py. Preserve
concurrent work, accepted ADRs, managed Auth bytes and historical evidence. Do not claim
installed-device, actual assistive technology, external-provider or release qualification
from Chromium/local GoTrue. This item does not itself implement the missing own PWA.

## I/O & Edge-Case Matrix

| Scenario | Given/when | Expected result | Failure handling |
| --- | --- | --- | --- |
| Real entry | Actual SDK session with current read.all opens /admin | Native named history/detail/audit, no own check | Denial never falls back |
| Sign-in | Existing synthetic account requests/verifies actual email code | Original account fence plus fresh all-read | Invalid/reused/failed code grants no entry |
| Loss | SDK signout/account/session loss, offline or page restore | Clear prior DOM; fresh session/access recheck | Late responses cannot reopen |
| Current access | Protected grant revoke, app/membership denial or outage then refresh | Locked denied/unavailable respectively | No false empty or offline authority |
| Proxy | Allowed read, malformed UUID, unknown path/header/method, oversized reply | Only bounded intended GETs forwarded | Safe closed private response |
| Storage/UI | Phone/desktop, keyboard, refresh/reload and audit use | Usable navigation/focus; no business storage | Saved own sentinel work survives |

</frozen-after-approval>

## Code Map

- `web/src/startup.tsx` and `LocalEntryRoute.tsx` currently mount `/` setup status only.
  Reuse preflight, public config, online observation and main pagehide/pageshow disposal.
- `EmailCodeEntry.tsx` owns app-local email form and accepted-account Auth wrapper;
  separate or parameterize the signed-in surface without duplicating sign-in state.
  `email-auth.ts` constructs the actual SDK with scoped protected storage.
- `admin-portal.ts`, `AdminPortal.tsx` own all-read admission/execution and reviewed UI;
  `admin-portal-preview.tsx` remains a test/preview consumer, not an activation substitute.
- `web/local-host.config.ts` is app-owned; generated `local-host-tools/local-entry-host.mjs`
  currently permits exact `/context`,64KiB and lacks404 forwarding. Its owning template
  and tests live in `platform/builder-cli/templates/application/web/local-host-tools/`;
  `scripts/sync-kdg-local-host.mjs` updates adopted outputs and manifest safely.
- Existing `auth-proof.mjs` and `admin-portal-proof.mjs` supply retained Node26.11.1,
  TS7.0.2/React19.3/Chromium tools and source-bound browser patterns. No installation.
- `tests/qualify_story31_http.py` serves actual local owners and existing own producer;
  coordinator owns the fresh proof, real email sink/session/grant mutations and browser
  qualification. Existing `platform/deployment/fixtures/email-code-v1/` supplies template.

## Tasks & Acceptance

- [x] Ordinary startup/local entry and app-owned Auth UI — mount `/admin` with stable
  controller and actual SDK; retain own entry and explicit sign-in/account boundaries.
- [x] Owning local-host template, consuming config and tests — explicit bounded read
  route matching/response limits and404 handling; regenerate through existing sync tool.
- [x] Focused startup/controller/proxy/type tests — observe missing ordinary administrator
  entry before implementation, then cover every matrix row and existing compatibility.
- [x] Coordinator actual SDK/email/owner browser qualification, AC matrix, independent
  review and scoped commit; execute the next unblocked Story3.1 item afterward.

Given a read.all-only actual account, when ordinary `/admin` starts, then organization
history renders without own admission. Given actual invalidation or denied fresh access,
when the user interacts or restores the page, then old all-record content cannot render.
Given local browser qualification, when navigation/sign-in/cache checks execute, then
record exact sources/results and distinguish local runtime from physical evidence.

## Implementation Notes

No unresolved user intent gap. Route choice `/admin` follows existing distinct portal
contract. Native HTTP prerequisite is separately delivered; preserve its ownership.
Implementation Sol High; coordinator owns fresh resource lifecycle and real-browser proof.
Scaffold: promote only the proven neutral bounded proxy extension in its owning template
and consuming regression. Shared UI: reuse existing app review; no speculative promotion.
Agent context sufficient. Documentation/readiness/handoff updated together. Existing ADRs
apply unchanged. Model usage and model-only timing unavailable unless reported.

## Spec Change Log

## Review Triage Log

## Verification

Use pinned Node26.11.1/TS7.0.2 and installed Python3.15.0. Run smallest acceptance RED,
focused local-host/startup/UI suites, generated parity and affected Auth/portal checks.
Coordinator runs actual local GoTrue/SMTP/SDK/KDG/Identity/PostgreSQL browser journeys,
retaining commands, original failures, source binding, screenshots and bounded shutdown.

Implementation verification receipts: ordinary SDK/startup8 groups + strict types/build;
Auth575 tests and71 named checks; portal20 controller/21 browser groups; safe actual
Vite/FastAPI host10 groups; proxy/scaffold10 tests; Auth/local-host parity. Coordinator
actual GoTrue/SMTP/SDK/Access/Identity/PostgreSQL browser12 checks pass with stable
runtime sources. Original immediate-signin failure was reproduced with held SDK logout
and corrected in app-owned composition; denied screens now allow explicit signout.
Formal review/commit pending; task ticks indicate implementation/evidence preparation.

All three review lenses reported before triage. Fresh third reviewer creation and an
old-thread followup were actually refused with agent thread limit; the independent
blind reviewer then ran the verification lens in its existing thread. Thus three
lenses used two independent reviewers, not three context-isolated reviewers.

| Finding | Verdict / route | Evidence |
| --- | --- | --- |
| Edge: fixed2026 observation versus current-year default filter | medium / patch | detail() is2026-10-26; AdminEntry derives real current year; adapter rejects out-of-range observations. From2027 ordinary proof falsely fails. Pin fixture browser date before navigation. |
| Verification Other finding: unpinned clock versus fixed2026 fixture | medium / patch | Independently traces same initial history wait and date validation. Same root cause; grouped with preceding row for one direct fixture correction. |

Blind review found no supported product defect. Verification initially investigated
whether app-specific proxy routing was untested, then dropped that candidate after
reading the coordinator actual Vite/12-check source-bound result. No finding deferred.

Final correction observed future2027 RED then coordinator final9-group GREEN with
advancing clocks, strict types/build and normal fixture shutdown. Independent patch
review confirms the date finding resolved. Final proxy/scaffold10 tests and both
parities pass. Actual browser12, real provider expiry4, actual membership/outage3 and
SMTP7 checks pass. Three owned HTTP children exited0 without force under deliberate
supervisor SIGTERM; interrupted overall result staysfalse, parent143. Restricted
post-shutdown metadata proves zero runtime sessions. Evidence/current AC1–6 matrix:
apps/kdg-capture/docs/STORY31_LOCAL_ADMIN_EVIDENCE.md. No deferrals. Next native
provisioning/configured-own item follows; Story3.1 remains incomplete. Selected Sol
High; usage/model-only elapsed unavailable. Third reviewer launch denied by thread
limit; three lenses executed by two independent reviewers as recorded above.
