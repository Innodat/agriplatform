---
title: KDG accessible current-entry screen
type: feature
created: 2026-10-22
status: done
route: oneshot
review_loop_iteration: 0
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

Deliver the next bounded Story1.1 prerequisite: an accessible React entry screen
consuming the existing typed EntryState and injected sign-in/recheck actions. It lets
a person understand whether sign-in, current access verification or initial setup is
still required, without presenting domain data or implying offline readiness.

Given signed-out/authentication-required state, when the online screen renders, then
show KDG Capture, Khula Development Group and a labeled Sign in action. Given checking,
then announce Checking access and disable the stable action control. Given authorized
entry, then show Setup not completed and explain online setup is still required;
expose only a current-access recheck, never a questionnaire, capture/admin action or
successfully provisioned state. Given denial, actor setup, invalid/unavailable or
cancelled/superseded state, then display distinct safe static text and explicit recheck
without raw payload, IDs, credentials, false empty success or automatic sign-in loop.
Given offline before setup, then show online sign-in/setup guidance, mask any previous
authorized landing and disable network actions. Supplied brand text is not authority.

Given keyboard/touch/assistive fixture or narrow/200% text viewport, when interacting,
then preserve reading order, semantic headings/live status, labeled native controls,
visible focus and48px touch controls without horizontal clipping. Preserve focus when
the same action changes to checking/results. Use system16px text, inherited neutral
semantic tokens and responsive gutters, without inventing a brand palette or logo.

Observe behavioral browser acceptance RED before screen behavior; use focused TDD,
strict TypeScript7.0.2 and actual approved React19.3/Vite8/Chromium synthetic HTTP proof
integrating createEntryBoundary. Preserve previous source/evidence and concurrent work.
No dependency/lock installation/update, real Auth/account/access, provider renewal/
callback/return navigation, workspace/public activation, service worker/local storage,
provisioning/domain persistence, Leave/editor, Docker changes, deployment/pilot or cleanup.
Fingerprints/HMAC remain deferred. This screen is not complete Story1.1 sign-in.
</frozen-after-approval>

## Implementation Notes

- bmad-help selects [BD] bmad-build; previous boundary is done. This is a small
  presentation prerequisite, not the enclosing epic story. Root concurrent edits are
  authorized by the user to be preserved and excluded, not reset. No intent gap or
  irreversible step. No shared epic cache or Leave sprint mutation is needed.
- Read Story1.1 epics.md, DESIGN/EXPERIENCE, current contracts, baseline and source-bound
  browser evidence. Reuse web/src/entry.ts without changing it. Add EntryScreen.tsx,
  scoped entry-screen.css and standalone tsconfig.screen.json. No source app imports.
- Investigation found ui-core placeholder, no proven neutral sign-in component. Reuse
  scaffold semantic skip/main/native-control conventions and source-reference neutral
  shadcn tokens. Keep KDG presentation local; promotion waits for a proven common consumer.
- New tests/fixtures exercise actual screen plus boundary; screen-proof.mjs copies a
  source capsule into an exclusive ignored proof root, links retained approved dependencies,
  runs TS7/Vite8 and serves built output with synthetic own API. No product frontend
  activation or provider simulation represented as real sign-in. Existing client suite
  is the affected regression; API/nativeSQL evidence remains historical and unchanged.
- Scaffold impact: reuse conventions, no generator changes. Shared UI: no existing
  component owner to extend, no unproven promotion. Agent context: root policy suffices;
  record exact commands in web README. Docs: additive handoff and new owner evidence.
  ADR: existing scope/errors/session/logging/release decisions, no new decision.

- Behavioral RED observed after fixing isolated proof setup: built React failed waiting
  for authorized Setup not completed. Focused14 tests then failed before implementation.
  Final suite15 passes; unchanged client29 passes; strict TS7/Vite8 and13 Chromium proof
  checks pass. Negative injected custody read returns exit1 without source mutation.
- Stable aria-disabled button guards activation and preserves focus. Live status has
  no busy ancestor; busy semantics belong to the button. Neutral rendered contrast is
  measured. Ten long-state responsive screenshots retained, no actual AT/device claim.
- Final owner evidence/receipt preserves427 protected files and complete old handoff.
  All commands/builds emit only in new ignored roots; concurrent commits excluded.

## Review Triage Log

Only configured Blind Hunter layer ran. New-agent launch hit the session thread limit;
reused the available isolated reviewer with a new artifact-only task and waited for
its completed findings. No implementation agent or additional review layer ran.

- medium, patch: aria-busy ancestor could defer Checking access live status; reproduced
  DOM regression, moved busy state to button and final browser check passes.
- medium, patch: custody mismatch recorded false but exited0; set nonzero exit status
  after receipt and prove exit1 via injected in-process final read, never disk mutation.
- low, patch: blocked checking test checked only signIn though action selected retry;
  compare entire callback snapshot and exact request count during checking/offline.
- low, patch: responsive test only signed-out; cover authorized/actor/unavailable/denied/
  offline at320/1280px and200% text, retain ten screenshots.
- low, patch: static tests missed setup/failure explanatory copy; add positive required
  guidance and negative observation/setup-ready claims,15 focused tests pass.
- low, patch: owner evidence lacked named green receipt; record exact final proof and
  source fingerprints in owner docs plus durable custody JSON.

No review finding deferred; provider/mounting/renewal/return/device/Story1.1 completion
remain outside this frozen increment, not newly discovered implementation gaps.

- Final visual inspection uses fixed16px minimum mobile gutters with safe-area insets
  so enlarged text retains reading room. All13 screen checks/15 tests rerun after this
  CSS adjustment in screen-56b1bfab-9497-477a-b9b1-6b8c8f47fac4.
