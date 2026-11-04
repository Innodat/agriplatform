---
title: 'Choose selector books by explicit activation'
type: 'bugfix'
created: '2026-11-04'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

Moving across another book while travelling from the chosen book to its chapter silently changes the chapter grid. Change browsing to explicit book activation (click, tap or keyboard activation), preserving typed reference navigation and chapter confirmation.

</frozen-after-approval>

## Implementation Notes

- No intent gaps or irreversible operations; small component/test correction. Prior authorization to preserve unrelated dirty work remains applicable. Baseline: 889f387728a6b60af0610ffd2aa3ac47c75de50a.
- Scope: `apps/scribeswell/web/src/components/bible/book-chapter-selector.tsx`, `apps/scribeswell/web/tests/workspace-polish.spec.cjs`, and only the existing hover expectation in `apps/scribeswell/web/tests/reader.spec.cjs` (preserve its pre-existing edits).
- Acceptance: given a clicked book, when the pointer crosses another book, its chapter grid stays put and chapter confirmation selects the clicked book. Explicit keyboard activation and typed references still switch the grid.
- Scaffold/shared UI: none, application-specific interaction. Agent context/ADR: none, no architecture change. Documentation: this delivery record captures the correction.
- Subsequent user request adds a read-only full-site visual audit and recommendations after the fix; no blanket redesign or deployment authorized.
- ATDD: `npm exec --workspace=apps/scribeswell/web -- playwright test --config playwright.config.cjs workspace-polish.spec.cjs -g 'crossing another book' --workers 2` failed on both desktop/mobile because hovering Isaiah removed the clicked Jeremiah grid. After removing mouse-move mutation and renaming the browsing state, both passed including chapter confirmation, keyboard activation and typed reference browsing.
- Existing reader acceptance explicitly expected hover browsing; changed only that step to click and its test title to reflect the user-approved interaction, retaining typed-navigation coverage.
- Verification: `npm exec --workspace=apps/scribeswell/web -- playwright test --config playwright.config.cjs workspace-polish.spec.cjs reader.spec.cjs --workers 2` — 66 passed. `VITE_APP_BASE=/ VITE_PLATFORM_ORIGIN='' VITE_STUDIES_ENABLED=true VITE_SUPABASE_URL=https://reader-test.supabase.co VITE_SUPABASE_ANON_KEY=test-public-key VITE_APP_DIRECTORY_URL=http://127.0.0.1:8001 npm run build --workspace=apps/scribeswell/web` — passed, existing bundle-size warning remains.
- Independent context-free Blind Hunter review inherited coordinator capability, returned no supported findings. No other review layers configured for oneshot; nothing deferred from this fix.
- Execution stayed on coordinator; actual model/effort not exposed here. One expected acceptance-failure cycle, no product repair retries; usage observation recorded by the repository utility. Separate read-only visual audit uses synthetic data in local Chromium, not a production availability assessment.
