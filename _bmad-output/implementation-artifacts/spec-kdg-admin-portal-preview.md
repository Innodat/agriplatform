---
title: 'Synthetic administrator history and record review portal'
type: 'feature'
created: '2026-10-28'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '7eb27133a887b481e84b0c2f2ce2de5c5c112e55'
context:
  - apps/kdg-capture/AGENTS.md
  - apps/kdg-capture/docs/DESIGN.md
  - apps/kdg-capture/docs/audit-display-composition.md
  - platform/docs/development/bmad-codex-usage.md
---

<frozen-after-approval reason="user next authorizes separately bounded synthetic portal integration; continuous reversible implementation requested">

## Intent

Provide one responsive online administrator review preview: bounded history with child,
observation date and original capturer, original-questionnaire record details, expandable
read-only audit and session-bound invalidation. Move Story3.1 AC1–6 client acceptance
beyond inert helpers, without claiming full Story3.1/native/device/live qualification.

## Boundaries & Constraints

Always use current server read.all through existing admin adapters, never own context.
Use unchanged generated generic Auth lifecycle with an app-owned boundary and execution
fences. Session/account/org/view change, explicit fresh verification, signout, offline
or disposal synchronously remove rendered business data and cancel old work. Check
all-read again after reconnect; denial and unavailable feedback stay distinct. Owner
callbacks alone never publish admission; epoch-checked returned outcomes do.

Browser history enrichment is intentionally bounded: fixed five-row pages, one history
GET then at most five audit-details GETs with limit1 for those returned capture IDs,
under one maximum10s execution deadline. No arbitrary actor batch or Identity browser
call. Map names using existing projection; unmapped and outage differ. Reject failed/
partial enrichment as unavailable, never empty. Verify immutable capture/owner/creator
binding before using labels. Empty successful pages require no enrichment.

Record detail uses fresh admin detail plus audit-details under one maximum10s deadline;
require matching record/owner/creator and current revision/update attribution before
combining answers with latest audit. On concurrent mismatch show unavailable with
explicit Retry, never quietly combine differing revisions. Audit pagination replaces
one page; retains header facts, opaque cursors and exact server times/revision strings.
Retry repeats complete authorized reads. No implicit retry, prefetch archive or storage.

Render original definition questions in order with rating/boolean/text values and
optional boolean details, safe text nodes, no new questionnaire. Audit starts collapsed;
show original creator/latest modifier and actual executor with separate optional
initiator. Keep metadata on admin surface; no edit/export/restore/version picker.
Use existing neutral entry theme,48px targets, visible focus, responsive wrapping,
semantic headings/list/description markup, status/loading/error announcements. English
preview labels follow existing UI; preserve approved Afrikaans questionnaire wording
and Ja/Nee; do not invent approved translations. Retain focus/scroll return to selected
history row after fresh Back read; focus headings after navigation/pagination.

Mount only through a new explicit preview host and synthetic browser fixture. Existing
main/index/startup/local own-entry route/config and managed Auth files remain byte-for-
byte unchanged. No live Auth/services/accounts/credentials, native DB/Docker/migrations/
grants, worker/queue, dependency install/change, deployment/production/pilot/push or
resource lifecycle/cleanup. Preserve concurrent work and historical evidence/resources.
Never access/run/copy/hash apps/kdg-capture/migrations/tests/schema_fixture.py.

## I/O & Edge-Case Matrix

| Scenario | Input/state | Expected behavior | Error handling |
| --- | --- | --- | --- |
| Authorized | Cross-owner current all-read history/detail | Correct child/date/capturer, original answers and optional real-event audit | No own fallback |
| Paging | History/audit next cursor, Back/Refresh | Bounded replaced pages, header retained, return focus, fresh refresh | Failed/partial distinct from empty |
| Names | Resolved/unmapped/temporary batch outage | Exact current name or distinct safe fallback/Retry | Never UUID-as-name or guessed System |
| Loss | Denied, expired, signed-out, account/org switch, offline | Remove DOM immediately before awaiting current checks | Late successes/errors cannot reopen |
| Integrity | Malformed/foreign/partial labels, changed detail/audit revision | No mixed content or partial rows | Safe unavailable and explicit Retry |
| Accessible | Phone/desktop/keyboard/zoom | Usable labels/focus/paging/loading/layout | Synthetic browser evidence distinct from devices |

</frozen-after-approval>

## Code Map

- `web/src/admin-history.ts:adminHistoryCaptures`, `admin-detail.ts:readAdminCapture`
  validate current all-read responses, original definitions, bounds/cursors. Reuse unchanged.
- `web/src/audit-display.ts:auditDetails`, `audit-presentation.ts:auditPresentation`
  supply validated selected actors and semantic name states. Do not duplicate parser.
- `web/src/auth/lifecycle.ts:createSessionLifecycle<T>` exposes current execution leases;
  generic hook does not expose them. Integrate directly; never edit managed code.
- `web/src/entry-screen.css`, `EntryScreen.tsx` provide neutral values/accessibility precedents.
- `web/tests/auth-proof.mjs` records retained Node26.11.1/TS7.0.2/React19.3/Vite8.3.4/
  Playwright1.64/Chromium paths, capsule compile/build/loopback browser proof. Reuse tools;
  no installation or broad recursive fixture reads.

## Tasks & Acceptance

- [x] `apps/kdg-capture/web/src/admin-portal.ts` — app-owned all-read/session/history/
  detail/audit boundary and controller; exact public API is an implementation choice.
- [x] `apps/kdg-capture/web/src/AdminPortal.tsx`, `admin-portal.css` — responsive review
  and explicit preview mount with synchronous invalidation, no startup wiring.
- [x] `apps/kdg-capture/web/tests/admin-portal-*`, `tsconfig.admin-portal.json` — retained
  acceptance RED before behavior, focused unit/type cases and loopback Chromium proof
  for every matrix row. Include real browser DOM clearing during delayed responses,
  keyboard focus, mobile/desktop/200% layout, HTML-name escaping and no business storage.
- [x] `apps/kdg-capture/docs/ADMIN_PORTAL_PREVIEW_EVIDENCE.md`, `docs/evidence/admin-portal-preview-20261028.json`
  — exact source/command/log/test custody and explicit synthetic/native/device limits.
  Coordinator owns final evidence/readiness/handoff reconciliation and scoped commit.

Given current all-read, when a synthetic Auth port starts preview, then authorized
cross-owner review renders through actual admin adapters. Given a matrix failure or
switch, when it occurs, then no old/partial/foreign business content remains visible.
Given browser interaction, when history/detail/audit are navigated, then the selected
content and focus reflect only the current bound view.

## Implementation Notes

No unresolved user-visible policy choice or irreversible action. One cohesive portal
preview is larger than oneshot: dispatch. Continuous-next authorization supersedes a
routine plan confirmation; no live activation exclusion is relaxed. Preserve dirty
main and global Leave tracking. Sole implementation owner is delegated Sol High.
Coordinator captures evidence baseline under /tmp/kdg-admin-portal-20261028; original
tracked KDG manifest excludes the prohibited untracked fixture by construction.

Scaffold: reuse managed generic lifecycle and strict transports unchanged; domain
pagination/name composition stays local. Shared UI: existing theme reused, no neutral
promotion without proven reuse. Agent context unchanged. Docs/evidence updated in same
item. ADR0022/0023/0031/0032/0056 and ADR0061 apply; no accepted decision/release change.
Record exact model/effort, available timing/usage; unavailable model-only data stays unknown.
No native/device/service startup; a disposable loopback synthetic test server may start
and stop, with its proof artifacts retained. Do not commit or stage concurrent work.

Implementation completed and parent inspected the scoped staged diff. Matrix audit:
Authorized/Paging/Names/Loss/Integrity/Accessible each have executed controller and/or
actual Chromium assertions; no test is inferred from a mere agent report. Final capsule
run-721c0b55-dc5e-488a-81a4-2d19761f674d passes16 controller cases/19 browser groups and
strict TS. Parent verified source/result/log hashes, normal fixture shutdown and all333
affected cases. Parent118 generated Auth cases and parity pass. All637 preexisting KDG
files were unchanged before documentation reconciliation; final protected count excludes
only six intended mutable documents. Delegated model selected gpt-6.1-sol/high; actual
model/usage and model-only timing unavailable. Context headroom unknown.

Behavioral RED is emitted checking!=history, with strict compilation failing on UI
files not yet created; never claim compile-success RED. Original missing-factory RED,
infrastructure EPERM and draft outage-test correction remain retained. English preview
uses plain Created/Edited actions; exact revision lives in optional audit. Initial host
connectivity is observed without requiring a prior offline event. No accepted ADR,
managed/generated source, old runtime, dependency or schema changes.


## Review Triage Log

| Finding | Verdict / route | Evidence |
| --- | --- | --- |
| Blind B1: persistent selected-record404 traps user on Retry | medium / patch | Parent reproduced history→unavailable→Retry unavailable; hidden Back restored history. Add visible existing fresh-history action. |
| Edge E1: reconnect during pending signout recreates unlocked lifecycle | high / patch | Parent held Auth signOut unresolved, observed signed_out→offline→history on reconnect. Existing explicit-signout requirement needs a controller fence across automatic lifecycle replacements; no new public API. |
| Edge E2: missing recovery action for selected404 | medium / patch, grouped with B1 | Same reachable missing visible navigation as B1; one UI correction and regression cover both findings. |
| Verification V1: Apply dates not exercised | medium / patch | Reviewer inspected complete tests/references; no test changes dates or submits Apply. Add browser range/cursor/reset/replacement assertions. |
| Verification V2: mounted executor/initiator values not asserted | medium / patch | Browser checked counts/labels only; projection tests do not execute React mapping. Assert distinct event-scoped values. |

All three review layers completed before triage; five findings grouped into four
patches, no intent gap or new owner policy. Same implementation agent re-engaged with
minimal-fix instructions and affected-only testing. Parent will rerun the full portal
proof after return and retain pre/post-review capsules. No new deferral or scope expansion.


Final resumed qualification:20 controller cases/21 named Chromium groups and strict TS
pass in platform/deployment/.local/kdg-admin-portal-20261028/run-8015e572-c0b4-4fac-b303-
7354374ae298. All333 affected regressions still match current source/result hashes;
parent repeated118 generic Auth tests and current parity with durable logs. All631
protected preexisting KDG blobs match baseline7eb27133a887b481e84b0c2f2ce2de5c5c112e55.

Original implementation agent was unavailable after interruption; existing fixes were
preserved and parent completed verification/harness repair. Patch review independently
ran20 cases and verified current source/log hashes; no remaining finding or deferral.
All five triage rows above are resolved by the four recorded patches. Final browser
assertions cover the two verification gaps and persistent record/audit404 recovery.

Earlier /tmp artifacts did not survive resume. Initial RED/pre-review GREEN are marked
historical/unavailable, not independently verified receipts. Parent recovered exact
pre-review controller from the index (SHA256 matches old record), compiled a private
capsule and observed four expected logout-regression failures; final code passes.
This is post-resume reproduction, not original ATDD custody. New proof capsules/logs
are stored in the ignored repo qualification directory. Moving proof storage exposed
stale root Tsconfig selection; the new browser harness explicitly selects its capsule
config, matching existing Auth proof, with no root or dependency modification. The
failed first repository-local run is retained. Context/model usage remain unknown.
