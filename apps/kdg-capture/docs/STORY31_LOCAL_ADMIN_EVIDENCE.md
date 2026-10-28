# Story 3.1 ordinary local administrator portal — 2026-10-28

Status: implemented, locally qualified and independently reviewed. Story3.1 remains
incomplete. This follows active HTTP delivery `00c087a`; the Identity28 prerequisite
was consumed unchanged. [Exact safe receipts](evidence/story31-local-admin-20261028.json)
record selected artifact paths/hashes and actual results without credentials.

Ordinary local index/main now mounts `/admin` with the actual Supabase SDK,
existing-account email-code form, accepted-account fence and reviewed all-read portal.
Own `/` remains separate. Administrator admission never requests own context first.
The builder-owned bounded GET proxy now supports canonical record UUID routes and
owner-specific response bounds, forwards safe404, strips ambient credentials and
retains cancellation/private responses. Generated adoption matches its owner.

## Observed failures, corrections and review

The first new ordinary-startup proof failed waiting for `/admin` Sign in. The first
actual-provider browser run later exposed immediate signout→signin losing the explicit
email-form launch while SDK logout was pending. A held-logout real-SDK regression
reproduced it. App-owned signed-out composition now opens the fenced code form directly;
verification still creates a fresh controller and checks current all-read. Denied and
unavailable surfaces also expose Sign out for account recovery.

All three BMAD review lenses completed. The service refused a fresh third reviewer
and an old-thread followup with `agent thread limit reached`. Two independent reviewers
therefore covered three lenses; the blind reviewer ran the verification lens afterward.
This is not represented as three context-isolated reviewers. Both edge and verification
found one shared fixture-date defect: fixed2026 observations would fail against a
future-year default filter. Actual2027 RED is retained; the proof now pins its browser
calendar before navigation while Date, timers and monotonic deadlines keep advancing.
Independent patch review is clear. No finding deferred.

A host test's wall duration was14033ms while its monotonic duration was12045ms. The
unchanged11–14s deadline assertion now uses monotonic elapsed time and retains both
failure diagnostics. Another raw-header fixture initially hit Node400 because Host was
missing; correcting the fixture exercises actual middleware401. No product result or
budget was relaxed. The historical recursive local-host proof copy was replaced by
selected web/contracts/API sources before execution; migration paths are never copied.

## Actual local runtime evidence

Fresh frame: `platform/deployment/.local/kdg-story31-20261028/fresh-8f3e984596bb453a902adb8710b4860d`.
Additional uniquely named synthetic resources use cached pinned GoTrue2.197.0,
Mailpit1.31.3 and Python template-carrier images. Controlled vendor migration/check
precedes Auth start; previous containers/volumes/evidence remain retained. The approved
numeric-only template is served read-only on the fixture network. All accounts,
credentials and records are synthetic; credentials remain in private ignored inputs.

Seven real email checks prove actual SMTP receipt/template rendering, existing-account
code sign-in, invalid-code rejection, used-code rejection and unknown-account refusal
without account creation. The initial unknown-account test expected400; actual pinned
GoTrue returns422 `otp_disabled`. That observation and a subsequent resend throttle
failure remain separate failed attempts; the corrected run passes. No expiry of an
email code or external email delivery is claimed.

The actual browser runs ordinary Vite CLI with the exact copied local-host.config.ts,
actual SDK and running KDG→TLS Access/Identity→GoTrue/restricted PostgreSQL owners:

- Twelve checks pass for actual emailed code, two-owner history/original answers/native
  audit names, all-read-only admission after protected own-read revocation, keyboard
  focus and1440/390/320px layouts, real transport offline clearing/reconnect, protected
  all-read/org-app/app disable and explicit recovery, persisted reload with fresh access,
  real provider signout, second-account denial and absent business persistence.
- Four further checks use an actual180-second server-issued session. After real provider
  global logout revokes its synthetic refresh token, SDK automatic renewal is refused
  and clears old DOM. Actual expiry then yields KDG401 `authentication_required`.
  The test restores a genuine provider session through SDK-owned persistence; it does
  not fabricate a JWT/expiry or change the product's email-only sign-in UI.
- Three more checks use one additional synthetic read.all-only reviewer. Protected
  Identity membership retirement changes a previously allowed portal to403 and clears
  records. Normal stop of its actual Access owner changes the next check to unavailable,
  distinct from denial and false empty. Original denied-role fixture accounts are intact.

All these receipts bind unchanged selected runtime sources. HTTP gateway/owner children
are real servers, not simulated authorization/SQL/provider adapters. A localStorage
sentinel survives, while IndexedDB, CacheStorage and service workers remain absent;
that proves administrator non-persistence, not an implemented own PWA.
The held HTTP supervisor was deliberately interrupted after the outage test: parent143,
all three children exit0, no forced termination and no remaining runtime DB sessions.
Its overall `passed:false` remains correct for interrupted qualification; earlier
completed browser/native results are separate. No resources were deleted.

## Focused verification

Installed pinned Node26.11.1/TS7.0.2/React19.3/Vite8.3.4/SDK2.117.3/Playwright1.64 + retained Chromium
and Python3.15.0 were reused without installation or dependency upgrade.

```sh
N=platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node
"$N" apps/kdg-capture/web/tests/local-admin-entry-proof.mjs
"$N" --test apps/kdg-capture/web/local-host-tools/test-local-entry-host.mjs platform/builder-cli/tests/local-host-pattern.test.mjs
"$N" platform/builder-cli/scripts/sync-kdg-local-host.mjs --check
"$N" platform/builder-cli/scripts/sync-kdg-auth.mjs --check
```

Coordinator final ordinary-startup **9 groups** with strict types/build and proxy/
scaffold **10 tests** pass; both parities pass. Affected Auth **575 tests/71 checks**,
portal **20 controller/21 browser groups**, and safe actual Vite/FastAPI context-host
**10 groups** pass. Selected Auth/portal hashes still match. The context-host receipt
predates the final generated test-only/manifest correction; its runtime hashes match,
and coordinator separately reran the final generated test and parity. Actual native
browser sources remain unchanged. Original failures and earlier receipts are retained.

## Current AC-1–AC-6 matrix

| Criterion | Established local evidence | Remaining acceptance evidence |
| --- | --- | --- |
| AC-1 current all-read | Mounted SDK/current real authority; cross-owner reads, all-only without own fallback; denied API role/selector matrix | Complete actual foreign-record/cursor boundary extension alongside own API activation |
| AC-2 responsive review | Ordinary mounted phone/desktop/narrow portal, original definition/owner/answers; real facilitator HTTP create→history | Device-saved own work→actual synchronization→administrator refresh journey |
| AC-3 audit | Actual retained names/create attribution, original owner and immutable read/retry; mounted read-only audit | Actual committed edit/no-op producer attribution in running own path |
| AC-4 portal/PWA split | Real offline clears portal; no all-record IDB/cache/SW, own sentinel survives | Actual own capture/My observations PWA, durable queue and offline shell/cache separation |
| AC-5 invalidation | Actual SDK signout/account switch, grant loss, membership loss, app/org-app disable, renewal refusal/expiry and owner outage | Integrated retained pending/conflicting own work across these transitions; external delivery/provider evidence remains separate |
| AC-6 accessibility/boundaries | Mounted keyboard/focus,1440/390/320px layout; prior text enlargement/contrast and current API/runtime roles | True zoom/actual assistive technology, installed Android/iPhone extension and final own-PWA boundary matrix |

Next necessary unblocked item: native eligibility issuance and configured own APIs,
then actual own UI/foreground synchronization/offline shell. The existing schema gives
runtime SELECT but not eligibility INSERT, so observe restricted native RED before a
new narrow controlled migration. See the approved-continuation Build draft
`_bmad-output/implementation-artifacts/spec-kdg-story31-own-api-readiness.md`.
Physical device/assistive technology results cannot be replaced by emulation. No
production deployment, push, real account/credential change or release qualification.

Scaffold: bounded neutral proxy template/tests and generated consumer updated together.
Shared UI: existing app-specific portal reused, no speculative promotion. Agent context:
sufficient. Documentation: this matrix/evidence, web guide, readiness and preserved handoff.
ADRs: existing access/session/privacy/release decisions apply; no accepted ADR changed.
Selected implementation gpt-6.1-sol/high; actual usage/model-only time unavailable.
