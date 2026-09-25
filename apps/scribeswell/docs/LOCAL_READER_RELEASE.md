---
title: Usable app switching and local Hebrew reader
created: 2026-09-25
status: done
route: oneshot
---

<frozen-after-approval>
## Intent

Make switching from PtS to the existing Scribeswell Hebrew Bible reader usable for this release. Replace the unstyled app selector with a readable, responsive shared component, recognizable app icons, current-app identification and keyboard navigation. Run the existing Hebrew reader locally against the already imported Supabase Bible data, repairing reader display/navigation defects needed for desktop and mobile reading and word morphology. Preserve existing PtS authentication, collection restrictions, and Scribeswell's public read-only API. No new data imports, production changes or public deployment.
</frozen-after-approval>

## Implementation Notes

Investigation: PtS does not load Tailwind, but the shared launcher depends on Tailwind utilities. Scribeswell has a vendored duplicate. Shared build-time UI imports are allowed by current repository architecture; replace the duplicate with the shared component and self-contained CSS. Scribeswell's fixed-width dropdown/sidebar clip mobile screens; async hooks permit stale requests to replace current chapter/word data. Existing Bible counts match the audited import: 39 books, 929 chapters, 23,213 verses, 306,785 words, 471,674 morphemes. No import is needed.

Scope: shared launcher component/styles; Scribeswell launcher adapter/build aliases, responsive reader and race handling; focused browser acceptance tests and local runtime setup/docs. No intent gaps, migrations or irreversible actions. Work is reversible within the user's authorization.

Impact decisions: shared UI updated in its owner; scaffold has no implemented generation path to update; no agent-context or ADR changes (existing build-time package and HTTP API boundaries retained). Documentation includes exact setup and validation evidence here; no duplicate feature specification elsewhere.

Acceptance: given either reader, opening Apps shows readable app cards and current location on desktop/mobile; keyboard navigation and dismissal work. Given existing local Bible data, choosing Scribeswell opens Genesis, book/chapter navigation renders the correct Hebrew, and selecting a word shows morphology without clipping. Delayed responses must not replace newer selections. Existing PtS reading/auth/source tests remain green.

The request was delivered as one app-switching/readability improvement; small fixes remained within reversible local scope. Replaced the Scribeswell vendored launcher with the existing build-time shared package. Added a scoped Vite filesystem allowlist so starting the second frontend cannot expose the PtS private archive. Installed backend dependencies into ignored `apps/scribeswell/.local/venv`; local browser configuration uses localhost. No database changes/imports were performed. Visual inspection also found missing glyphs for Hebrew cantillation; the reader now bundles Noto Serif Hebrew with its SIL OFL notice at `/fonts/OFL-Noto-Serif-Hebrew.txt`.

## Review triage log

- Medium, patched: mobile analysis appeared after the whole chapter; changed to a bounded viewport panel and tested against a 50-verse fixture and live Psalm 119.
- Medium, patched: Scribeswell's launcher was untested; added populated-directory keyboard/current-app/bounds coverage and live PtS→Scribeswell opening.
- Medium, patched: late-response test used a 150 ms delay; now waits for response completion and rendering frames before assertions.
- Medium, patched: book-detail and morphology races lacked coverage; added delayed book, newer-word and close-before-response cases.
- Medium, patched: Tab closed a focused menu without a defined destination; focus returns to the trigger before normal Tab progression. Tests assert the next control and Shift+Tab return.
- Medium, patched: reader failures lacked retry; books, chapter and morphology now expose the existing hook's retry operation. Initial books/chapter failure recovery is covered.
- Low, patched: responsive navigation lacked stress cases; added 320 px width, bilingual names, 150 chapters and short landscape checks.
- Low, patched: setup/evidence incomplete during review; updated the reader README with configuration, start/stop and verification commands and release routing requirements.

## Verification

Red evidence: after correcting fixture/locator mistakes, the original launcher failed both projects on missing current-app identification. Original reader failed mobile bounds (dialog started at x=-74); desktop tests reproduced late Genesis replacing Exodus and word analysis remaining after Forward. All were observed before the respective implementation fixes.

- `LD_LIBRARY_PATH=/tmp/pts-browser-libs/usr/lib/x86_64-linux-gnu apps/pts/web/node_modules/.bin/playwright test --config apps/pts/web/playwright.config.cjs`: 46 passed. After the review focus/header adjustments, the focused `launcher.spec.cjs` suite passed 2/2 again.
- `LD_LIBRARY_PATH=/tmp/pts-browser-libs/usr/lib/x86_64-linux-gnu npm run test:browser --workspace=apps/scribeswell/web`: 16 passed, desktop/mobile, including races, retries, privacy and responsive stress cases.
- `apps/scribeswell/.local/venv/bin/python -m pytest apps/scribeswell/tests -q --disable-warnings`: 8 passed (one third-party warning).
- Both application TypeScript/production builds passed; existing approximately 500–531 kB main-bundle size warnings remain.
- Live local API: 39 books; Genesis 1 has 31 verses/434 words; Psalm 119 has 176 verses/1,067 words; morphology requests succeed. Read-only database counts match the prior import audit.
- Live browser: authenticated PtS test reader opens Scribeswell through the real launcher; Genesis and Psalm 119 render with word analysis on desktop/mobile. No login is required for public Bible reading. Authentication does not transfer between different localhost ports; PtS remains open in its original tab.
- No production deployment, migration, reset, source fetch or new data import. No review findings deferred.

## Running locally and release follow-up

Open `http://localhost:5179` → Apps → Scribeswell, or `http://localhost:5174` directly. Both frontends, Scribeswell API 8000, and existing PtS/directory services are running on the prepared workstation. The Scribeswell API/web process identities and logs are ignored under `apps/scribeswell/.local/`. Use the README terminal commands for future starts and Ctrl+C for stopping those terminal-owned processes; preserve Supabase's data.

Production configuration remains an explicit release step: route Scribeswell `/api/bible/*` to its backend and set directory/frontend environment URLs for the released environment. Keep service credentials server-side. The earlier PtS organization manifest remains the source for creating the production PtS organization at release.

Font verification initially failed because the narrow Vite allowlist excluded installed font files (2 failed, 14 passed). The allowlist now includes only that font package in addition to this frontend and shared platform files; the private PtS archive remains denied. Browser tests explicitly require the Hebrew font to load.

Final font-enabled browser run: 16/16 passed (12.4 s); both builds pass. Live app switch rechecked with an assertion that Noto Serif Hebrew actually loads, followed by visual inspection of the Hebrew vowel/cantillation marks. `git diff --check` passed. The workspace package installer reported six existing dependency advisories (three moderate, three high); no blanket dependency upgrade was performed as part of this UI/local-runtime change.
