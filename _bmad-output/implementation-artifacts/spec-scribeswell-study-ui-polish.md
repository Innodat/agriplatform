---
title: 'Consistent Studies, Notes and dialog presentation'
type: 'bugfix'
created: '2026-11-04'
status: 'done'
route: 'dispatch'
baseline_commit: 'c699fc82cfa6176b782e320c79a9405a62e212d0'
review_loop_iteration: 0
context: ['platform/docs/development/bmad-codex-usage.md']
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

Apply the visual-review recommendations approved by the user: make Studies, Notes, dialogs and supporting analysis controls feel consistent with the improved Hebrew reader and restored warm amber selector. Correct top-left confirmations, black borders, crowded actions, unclear analysis tabs and mobile writing space. Improve control sizing, feedback, secondary typography and colour legibility while preserving the reader's character.

## Boundaries & Constraints

**Always:** Keep native UI typography, bundled Hebrew reading font, bright orange and pale amber reference palette, click-only book selection, Hebrew closed-selector labels and discreet tab rename. Preserve authorization, draft/lane ownership, undo/selection handling, autosave, explicit configuration saves, confirmation semantics, async recovery, dictionary state and public reading. Render ordinary/deletion/unsaved dialogs centred and viewport bounded. Preserve every unrelated dirty edit. Visual verification on actual rendered desktop/mobile screens is required; passing tests alone is insufficient.

**Never:** Deploy/push, change business contracts, rewrite persistence/auth/editor machinery, change canonical references, import another application's runtime or promote unproven domain-specific UI to platform packages. Optional conceptual redesigns of focus mode and global reference-language policy from the audit are not prerequisites; keep their established behaviour.

## I/O & Edge-Case Matrix

| Scenario | Input / state | Expected output / behaviour |
|---|---|---|
| Confirmations | Delete note/study, unsaved exit, capacity choice | Centred bounded dialog, legible heading and separated actions; existing cancellation/confirmation preserved |
| Study actions | Open study or note | Clear Add note/Create study, secondary actions in accessible disclosure/menu; Delete study belongs to study actions rather than note formatting |
| Mobile editing | 390×844 and 320px wide | Editor appears substantially earlier than previous ~650px, empty related notes compact, save status/Retry adjacent and visible while editing, practical touch targets |
| Analysis | Selected word then Analysis; switch Word/Occurrences/Notes | Relevant selected-word content opens predictably; consistent active indicators; deliberate Notes access and state retained |
| Anonymous Studies | No account | Single explanatory empty state with direct sign-in/create-account actions, not duplicate retry/error messaging |
| Selection colour | Selected chapter | Same orange background with dark readable Hebrew glyph; current/candidate remain distinct |

</frozen-after-approval>

## Code Map

- `apps/scribeswell/web/src/components/studies/{StudiesPanel,NoteEditor,RelevantNotes}.tsx`: presentation, direct action callbacks, empty state. Preserve rich-editor handling above JSX. Menus must dismiss on Escape/outside click and keep focus restoration valid for edit dialogs and save/recovery.
- `apps/scribeswell/web/src/context/StudiesContext.tsx`: final dialog components (~824 onward) only for layout; no business-state rewrite.
- `apps/scribeswell/web/src/pages/ReaderPage.tsx`: analysis tab chrome, default selection on explicit opening, capacity dialog, mobile return action. Word selection currently allows compact WordStudy and full Analysis surfaces; unify visual shell/indicators without collapsing their distinct mobile reading behaviour or remounting state unnecessarily.
- `apps/scribeswell/web/src/components/bible/WordStudy.tsx`: soft preview/filter/result borders, action spacing, active tabs and target sizes; keep dictionary navigation state.
- `apps/scribeswell/web/src/components/auth/SignInDialog.tsx`: consistent focus treatment, action sizes.
- `apps/scribeswell/web/src/components/layout/Topbar.tsx`: already dirty. Existing `scribeswell-account-entry` event opens signin; extend narrowly for explicit signup if needed. Preserve launcher/auth changes. Improve narrow brand/account fit through responsive sizing/layout; a compact menu is acceptable if tested.
- `apps/scribeswell/web/src/components/bible/{book-chapter-selector,PassagePane,WorkspaceTabs}.tsx` and `src/index.css`: targeted contrast/touch sizing, soft active-pane accent, reusable application-local surface/button/input/dialog styles. No global CSS rule that unintentionally reveals hidden/inert content.
- `apps/scribeswell/web/tests/{personal-notes,reader,lexicon,account-entry,workspace-polish,four-passage,workspace-tabs}.spec.cjs`: existing behavioural protection. Reader/account-entry already dirty. Update only test interactions genuinely changed (e.g. opening an action menu), preserving all assertions of safety/state.
- `/tmp/scribeswell-audit/report.html`: approved visual review, 74 embedded before captures. `/tmp/scribeswell-audit*.cjs`: local synthetic browser capture fixtures, can adapt for after screenshots; not production data. Read actual relevant screenshots with view_image. Avoid fetching/deploying production.

## Tasks & Acceptance

- [x] Observe focused acceptance failures for centring, menu/action separation, mobile editor visibility and analysis selection before implementation; add meaningful UI acceptance coverage.
- [x] Apply consistent local UI styles, centred confirmations, spacing and hierarchy; make secondary study/note actions accessible through an unobtrusive disclosure without breaking keyboard/focus recovery.
- [x] Improve mobile editor/status layout, compact empty related notes and unify analysis selection styling/defaults. Add direct anonymous account actions and narrow header polish while preserving prior work.
- [x] Retain orange selection with dark glyphs, improve small secondary labels and practical touch controls. Visually inspect and refine desktop/mobile before finishing.
- [x] Run focused new tests, affected browser suites and application build; document exact results and remaining limits. Do not silently weaken old assertions to pass.

**Acceptance:** Given any listed matrix state, when opened on desktop/mobile, then the specified presentation and original behaviour both hold. Given a non-current book, when the pointer crosses it, then the chosen grid remains unchanged. Given existing pending input, when a new menu/dialog opens and cancels, then the same input and appropriate focus remain. Given a narrow screen, then content fits without horizontal overflow and controls remain reachable.

## Implementation Notes

- User explicitly approved the concrete visual recommendations and requested implementation in this turn. No new approval gate is needed; preceding dirty-tree authorization persists. Cohesive UI correction has no migrations or external side effects. Larger footprint uses dispatch.
- Scaffold/shared UI: application-local styles/components only. Agent-context: no changes. Documentation: this spec plus visual evidence; no ADR change because ownership/workflow contracts stay intact.
- Coordinator delegates implementation to Sol High as prescribed; reviewers inherit coordinator capability. Actual model metadata only reported if exposed. Agent must not invoke another delivery workflow or commit; coordinator owns review/commit. If a styling choice is underspecified, choose the smallest consistent solution and record it.

## Verification

- `npm exec --workspace=apps/scribeswell/web -- playwright test --config playwright.config.cjs <focused changed tests> --workers 2` then affected suites including personal-notes, reader, lexicon, workspace-polish and relevant account/arrangement checks. Local server binding may require tool escalation.
- `VITE_APP_BASE=/ VITE_PLATFORM_ORIGIN='' VITE_STUDIES_ENABLED=true VITE_SUPABASE_URL=https://reader-test.supabase.co VITE_SUPABASE_ANON_KEY=test-public-key VITE_APP_DIRECTORY_URL=http://127.0.0.1:8001 npm run build --workspace=apps/scribeswell/web`.
- Capture/view authentic rendered UI at 1440×1000 and 390×844, plus narrow overflow/keyboard checks at 320px. Check dialogs, menu, form, note editor, save failure, analysis, selector and signed-out Studies. Existing bundle warning is not a new regression.

### Implementation and observed acceptance

- Initial acceptance run: 7 failures and 1 desktop-only skip for dialog position, missing action disclosures, mobile editor position and Analysis selection. After implementation, the mobile editor was still at y=581; compacting its header moved it above the 565px acceptance boundary.
- Focused acceptance now passes: 13 passed, 1 intentional desktop skip, including 320×568 bounded menus, study deletion and unsaved-exit cancellation, anonymous sign-in/signup mode and focus recovery.
- Build passed (TypeScript and Vite); existing bundle-size advisory remains. Broad browser regressions are being completed.
- Reviewed rendered screenshots in `/tmp/scribeswell-after/`: desktop, 390px and 320px library/forms/editor/actions/confirmations/failed save/account entry. Earlier `/tmp/scribeswell-audit` captures were lost when the execution environment restarted; do not treat those paths as current artifacts. The implementer session was also unavailable after restart; coordinator completed refinements and verification inline.
- Existing workspace-restoration assertions still used Arabic tab numerals: updated display assertions to the already-approved Hebrew numerals without changing stored canonical references. Four-pane wrapping fixture now uses 806px height: normal reading height 235px; wrapped control/multiline-error chrome must cross the existing 200px fallback boundary. Auth SDK transport implementation now deliberately omits console logging: retain sensitive-data exclusion and safe inline feedback assertions without requiring a log to exist.

## Review Triage Log

| Layer / finding | Verdict and evidence | Route / result |
|---|---|---|
| Blind hunter | No supported findings after tracing actions, focus, state, account entry, selection and styling. | No patch. |
| Edge: bottom Study actions clips | Medium: measured popup exceeded its inspector at 1280px and 320px. The earlier test scrolled the command into view and masked internal horizontal overflow. Reproduced in both projects before fixing. | Patch: right-align the footer disclosure; assert its bounds before scrolling and zero inspector horizontal overflow. |
| Edge: Analysis hides failed morphology recovery | Medium: selecting a word with a failed lookup then explicitly opening Analysis forced Word while only the compact surface rendered an error. Both new tests failed before fixing. | Patch: retain safe error, Retry and Close in full Analysis. |
| Verification: keyboard blur dismissal untested | Medium verification gap: pointer/Escape checks did not traverse the menu using Tab. | Patch: Tab through commands and out; Shift+Tab through the trigger and out. Both keyboard cases pass. |

- No deferred review findings. Original implementer session could not be resumed after environment restart, so coordinator applied the small patches inline.
- Visual refinement removes the nested dictionary border inside full Analysis. Header gutters remain 16px at ordinary phone sizes, reducing to 8px only below 360px.
- Existing note tests updated for menu commands and returning focus to disclosure triggers. Two deletion tests now use the existing paused-clock fixture: extra menu interactions must not accidentally consume the autosave debounce before the tested deletion scenario begins. Candidate range assertions distinguish pending typed references from current selected chapters, retaining submitted reference checks.

### Final verification — 2026-11-04

- **1,205 distinct browser checks passed; 7 intentional skips.** The 1,188 existing checks cover Notes, reader, dictionary, workspace tabs/restoration, account entry and four-passage arrangements. The new polish suite contributes 17 passing checks and one desktop-only mobile-layout skip. Six existing skips require bounded-rollout settings or an explicitly configured native API fixture. No backend, native database or deployed-site verification is claimed by this presentation-only delivery.
- Existing suite commands: `npm exec --workspace=apps/scribeswell/web -- playwright test --config playwright.config.cjs reader.spec.cjs lexicon.spec.cjs workspace-polish.spec.cjs four-passage.spec.cjs workspace-tabs.spec.cjs account-entry.spec.cjs workspace-restoration.spec.cjs --workers 2 --max-failures 8`, then affected Notes checks through `/tmp/scribeswell-notes.config.cjs` on a separate local port. Interrupted runs were checkpointed by exact project/file/test title; only successful tests were retained.
- Final remainder: `npm exec --workspace=apps/scribeswell/web -- playwright test --config playwright.config.cjs personal-notes.spec.cjs reader.spec.cjs lexicon.spec.cjs workspace-polish.spec.cjs four-passage.spec.cjs workspace-tabs.spec.cjs account-entry.spec.cjs workspace-restoration.spec.cjs --test-list-invert /tmp/scribeswell-completed-tests.txt --fully-parallel --workers 6 --max-failures 10`: 677 passed, 6 skipped, 2 stale English-label assertions failed. Corrected the visible book assertion to Hebrew; `npm exec --workspace=apps/scribeswell/web -- playwright test --config playwright.config.cjs personal-notes.spec.cjs --grep 'off-passage book' --workers 2`: **2 passed**. Together with 509 checkpointed passes this gives 1,188 distinct existing checks. Ledger: `/tmp/scribeswell-verification-passed.txt`.
- Focused UI: `npm exec --workspace=apps/scribeswell/web -- playwright test --config /tmp/scribeswell-focused.config.cjs study-ui-polish.spec.cjs --workers 2`: **17 passed, 1 skipped**. Review regression first observed **4 failures, 2 passes**, then passed after menu alignment and full Analysis recovery fixes.
- Production bundle: `VITE_APP_BASE=/ VITE_PLATFORM_ORIGIN='' VITE_STUDIES_ENABLED=true VITE_SUPABASE_URL=https://reader-test.supabase.co VITE_SUPABASE_ANON_KEY=test-public-key VITE_APP_DIRECTORY_URL=http://127.0.0.1:8001 npm run build --workspace=apps/scribeswell/web`: **passed**, including TypeScript. Existing >500kB bundle advisory remains (JS 786.29kB; CSS 36.12kB).
- Actual production preview: `npm exec --workspace=apps/scribeswell/web -- playwright test --config /tmp/scribeswell-production.config.cjs study-ui-polish.spec.cjs --workers 2`: **17 passed, 1 skipped**. The initial preview invocation used its environment-default subpath against a public-root build and returned asset 404s; rerun used the same `VITE_APP_BASE=/` environment as the build. No product change was required.
- Visual evidence: **57 rendered captures** at 1440×1000, 390×844, 320×568, plus footer-menu bounds at 1280/390/320 widths. Inspected selector, compact/full analysis, occurrence list, comparison active cue, forms, editor, menus, account entry, deletion, unsaved exit and capacity dialogs. Footer menu has zero inspector horizontal overflow at all three widths. Gallery: `/tmp/scribeswell-after/report.html`; these use synthetic fixture data.
- `git diff --check -- apps/scribeswell/web`: passed. Three independent reviews completed, all supported findings patched; nothing deferred. No push, deployment, migrations or production mutation.
- Delivery observation: implementation selected `gpt-6.1-sol` / `high`; reviewers used the coordinator's capability. Original implementation continuation was lost on environment restart, so coordinator completed refinements inline. Retries include explained legacy assertions, debounce timing fixtures and preview base-path configuration. Actual model metadata, model-only elapsed time and billing are not inferred; available local usage is collected once at completion.
