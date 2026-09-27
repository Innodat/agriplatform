---
title: Focused reading with sequential chapter navigation
created: 2026-09-27
status: done
route: oneshot
---

<frozen-after-approval>
## Intent

Add focus mode and Previous/Next chapter navigation to the existing Hebrew reader. Focus hides the app header and analysis, retains passage navigation and mobile comparison switching, and provides a visible Exit focus control plus Escape. Clicking a word leaves focus to show analysis. Mode changes preserve passage references and reading positions. Previous/Next operate independently per passage, follow the collected book/chapter order across boundaries and stop at the collection ends. References remain in the URL with normal Back/Forward behavior. Public access and existing authentication remain unchanged.
</frozen-after-approval>

## Implementation Notes

The user requested both reading controls together; implement both as authorized reversible work. Existing dirty files are our immediately preceding, tested full-width header change and its evidence; preserve them. No unresolved intent gaps or irreversible actions. Small local frontend footprint: AppShell supplies focus state; ReaderPage owns controls/word exit and Escape; PassagePane uses a silo-local navigation hook built on existing useBook and book list; BookChapterSelector consumes Escape before the page does. No global letter shortcut, fullscreen API, persistence, server or schema changes.

Use each book's returned chapter list, sorted numerically, and the catalogue's returned book order. Load neighbor book details at boundaries. Disable controls while needed metadata loads, offer retry on failure, and never use a response for a different book as a navigation target. Reset only the navigating pane's scroll and selection, retaining the other pane. Keyboard and touch controls have accessible names.

Given analysis and a scrolled passage, entering/exiting focus preserves the reference and position and restores analysis. Given an open selector in focus, the first Escape closes the selector and the next exits focus. Given comparison, navigating either pane changes only that pane. Given a chapter at a boundary, next/previous uses the neighboring book's first/last existing chapter. Given end-of-collection or unavailable metadata, controls cannot navigate to invented references; retry recovers failed metadata.

Impact decisions: no shared UI promotion (reader-specific), scaffold or agent-context changes; existing ADRs cover this reversible presentation change, so no new ADR. Documentation/evidence recorded in this owner document. Release needs no migration, content import, production change or new configuration.


Focus state lives in AppShell's reader context and is transient; header authentication stays mounted while hidden. ReaderPage captures visible word anchors before layout changes and restores them afterward, including the pre-focus position when an enlarged viewport clamps scrolling at the bottom. New scrolling or a different chapter replaces that anchor. Clicking a word exits focus and displays that word even if it was already selected before focus.

The selector is now positioned within viewport bounds independently of its trigger's horizontal position, accounting for the new navigation arrows. It closes on keyboard focus leaving its container, and consumes Escape locally when open.

## Review Triage Log

- Medium, fixed: focus can clamp scroll position near chapter ends or change word wrapping. Added word-anchor preservation plus desktop/mobile bottom-of-chapter roundtrip and new-scroll tests.
- Medium, fixed: the Next arrow shifted the selector popup beyond the viewport. Existing narrow-layout acceptance checks reproduced this; fixed viewport-clamped positioning and reran all bounds checks.
- Medium, fixed: Escape could leave focus with a selector still open after keyboard focus moved away. Close on focus leaving; test Shift+Tab and subsequent Escape alongside the existing close-selector-first test.
- Medium, fixed: metadata failure/race and sparse chapter behavior lacked coverage. Added current and neighbor failure/retry, delayed old-book metadata, noncontiguous unsorted chapter lists, boundary disabled states and keyboard activation checks. No findings deferred.

## Verification

ATDD before implementation:

`LD_LIBRARY_PATH=/tmp/pts-browser-libs/usr/lib/x86_64-linux-gnu npm run test:browser --workspace=apps/scribeswell/web -- --grep 'focus mode preserves|previous and next chapters'` — four failures (missing focus and chapter controls), captured in `/tmp/focus-red.log`.

Final commands:

- `LD_LIBRARY_PATH=/tmp/pts-browser-libs/usr/lib/x86_64-linux-gnu npm run test:browser --workspace=apps/scribeswell/web` — 42 passed (`/tmp/comparison-tests.log`); includes all 30 existing checks.
- `npm run build --workspace=apps/scribeswell/web` — passed with the existing large-chunk warning.
- `LD_LIBRARY_PATH=/tmp/pts-browser-libs/usr/lib/x86_64-linux-gnu node /tmp/pts-local/focus-live.cjs` — passed against local collected content at 1440×900 and 390×844. Verified focus roundtrip at chapter end, actual Genesis 50 → Exodus 1 → Genesis 50, retained focus during navigation, Escape exit and no document overflow. Desktop/mobile focus screenshots visually inspected.
- `git diff --check` — passed.

Requirement-to-test mapping in `web/tests/reader.spec.cjs`:

| Requirement | Acceptance coverage |
| --- | --- |
| Focus hides header/analysis; restores analysis and selection; Escape priority; word-click exit | focus mode preserves the passage, restores analysis and handles Escape in order |
| Independent sequential comparison navigation, boundaries, URL/history and focus continuity | previous and next chapters cross book boundaries and preserve comparison state |
| Current/neighbor failure and retry; only actual sorted chapters | chapter navigation retries metadata and follows actual sorted chapters |
| Discard stale navigation targets | late navigation metadata cannot restore targets from the old book |
| Bottom-of-chapter anchor and new user scrolling | focus roundtrip preserves the final reading position and respects new scrolling |
| Keyboard dismissal outside selector | selector closes when keyboard focus leaves in focus mode |
| Shared launcher, public reader, protected file denial, scrolling and comparison regressions | Existing 30 reader checks |

No backend, database, shared packages or deployment changes; local server picked up frontend changes automatically.
