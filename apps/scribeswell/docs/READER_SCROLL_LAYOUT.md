---
title: Persistent reader navigation and morphology
created: 2026-09-27
status: done
route: oneshot
---

<frozen-after-approval>
## Intent

Use an icon-only app launcher in Scribeswell while preserving its accessible name and keyboard behavior. Keep the Hebrew text centered at a comfortable reading width; chapter text scrolls below persistent navigation, with word morphology remaining visible alongside it on desktop and in the existing bounded panel on mobile. Long analysis may scroll independently. Last verses must remain reachable above the mobile panel; changing chapter resets the chapter scroll position. PtS appearance, shared authentication and public reader access remain unchanged.
</frozen-after-approval>

## Implementation Notes

The document currently scrolls because AppShell and ReaderPage use minimum heights. Replace those with a viewport-height flex shell and min-height:0 constrained chapter row; only chapter text and long analysis overflow. Keep the book selector outside the chapter scroll area so its dropdown remains usable. Limit the text to 44rem and retain the overall centered workspace. Add an opt-in iconOnly shared launcher prop; default preserves PtS.

Impact: shared UI gains a small reusable presentation option; no scaffold generator exists to update. Agent context/ADR/auth/API/database unchanged. Documentation and acceptance evidence recorded here, with shared launcher usage documented in its owner README. Reversible presentation change, no intent gaps or deployment required.

Mobile implementation uses a bounded bottom sibling instead of an overlay so the final verses remain unobscured. Morphology's word heading and close button remain sticky while its longer contents scroll. Desktop text is limited to 44rem inside the existing centered workspace.

## Review triage

- Medium, fixed: long-analysis scrolling lacked coverage. Added 30-morpheme fixtures verifying independent scroll, reachable final content, persistent dismissal, and unchanged chapter/document scroll.
- Medium, fixed: analysis heading/close could scroll away. Made the panel header sticky inside its own scroll area.
- Medium, fixed: dropdown stress test could mask body scrolling. Added complete vertical bounds, zero document scroll and keyboard dismissal/focus checks on the short viewport.
- Low, fixed: shared launcher README lacked `iconOnly`; documented its opt-in behavior and unchanged default.

## Verification

Before implementation, focused desktop/mobile launcher and scrolling tests failed 4/4 (visible Apps label and chapter scrollTop staying zero). Initial full reader suite after the layout change: 18 passed. Both application builds passed, with their existing large-chunk warnings. Further long-analysis and dropdown checks recorded below.

Final verification:

- `LD_LIBRARY_PATH=/tmp/pts-browser-libs/usr/lib/x86_64-linux-gnu npm run test:browser --workspace=apps/scribeswell/web`: 20 passed. Covers icon-only accessible launcher, chapter-only scrolling, persistent navigation/analysis, unobscured last verses, chapter scroll reset, independently scrolling long morphology, readable centered width and bounded chapter menus on desktop/mobile.
- `LD_LIBRARY_PATH=/tmp/pts-browser-libs/usr/lib/x86_64-linux-gnu apps/pts/web/node_modules/.bin/playwright test --config apps/pts/web/playwright.config.cjs launcher.spec.cjs`: 2 passed; shared launcher default and PtS behavior preserved.
- `npm run build --workspace=apps/scribeswell/web` and `npm run build --prefix apps/pts/web`: passed; existing large-chunk warnings remain. Reader build repeated after the final sticky-header change.
- `LD_LIBRARY_PATH=/tmp/pts-browser-libs/usr/lib/x86_64-linux-gnu node /tmp/pts-local/layout-live.cjs`: passed against local Psalm 119 on desktop (1440×900) and mobile (390×844). Verse 176 remains visible, morphology stays positioned, document does not scroll. Screenshots visually inspected.
- `git diff --check`: passed.

No database migrations, production changes or additional configuration required.

## Full-width workspace header — 2026-09-27

User-requested follow-up removes the header's centered maximum-width container. Launcher/brand and account actions now use the viewport width with 16px edge padding; header height and centered single-passage reading width stay unchanged. This is a local presentation adjustment: no shared UI, scaffold, agent-context or ADR impact; no auth/API/database changes.

Acceptance evidence: extended the existing shared-launcher browser check to assert edge positions and 57px outer header height. Before the class change, `LD_LIBRARY_PATH=/tmp/pts-browser-libs/usr/lib/x86_64-linux-gnu npm run test:browser --workspace=apps/scribeswell/web -- --grep 'shared launcher'` failed on desktop alignment and passed on mobile. Afterward, the same command without `-- --grep 'shared launcher'` passed all 30 reader tests. `npm run build --workspace=apps/scribeswell/web` passed with the existing chunk-size warning; `git diff --check` passed.
