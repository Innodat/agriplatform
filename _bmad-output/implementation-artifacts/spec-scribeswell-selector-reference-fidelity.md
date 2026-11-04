---
title: 'Match the chapter selector reference palette and finish'
type: 'bugfix'
created: '2026-11-04'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

Match the selector's visual language to the user's `/tmp/ch-sel-2.png`: faint warm-gray borders, original bright-orange selected chapter, pale amber book/hover/candidate surfaces, bilingual book rows/headings and roomier desktop chapter grid. Preserve the approved Hebrew selected-passage trigger, compact workspace, typed reference entry, current/candidate distinction, accessibility, cancellation, selection and responsive viewport containment. Correct the visibly black internal dividers and avoid treating functional tests as evidence of visual fidelity. Preserve unrelated work; no deployment.

</frozen-after-approval>

## Implementation Notes

- Small reversible app-only UI refinement; no unresolved intent or irreversible operation. User's prior dirty-tree authorization persists. Scope: `apps/scribeswell/web/src/components/bible/book-chapter-selector.tsx`, focused `web/tests/workspace-polish.spec.cjs`, this record. No service/dependency/scaffold/shared-UI/agent-context/ADR impact. Delivery record is documentation/evidence.
- Investigated reference via image viewing and pixel sampling: selected chapter #fe9a00, pale amber #fef3c6, border #e7e5e4. Current screenshot had uncoloured `border-b`/`border-r` utilities (inherit dark currentColor), brown amber-700 selection, stacked bilingual book rows and cramped four-column desktop grid. Restore original existing Tailwind amber-500/amber-100 palette and explicit stone borders, rather than introducing a new design system.
- Given an opened selector, when rendered on desktop/phone, then all separators are light gray and the current chapter uses reference orange; candidate and book surfaces use reference pale amber. Given desktop width, then bilingual books share a row and chapters use five columns with roomy tiles; phones retain bounded four-column grid. Given typed reference, hover, confirmation or cancellation, then existing behavior and current selection protections remain intact. Preserve original reference's white selected glyph treatment, while retaining explicit non-colour current semantics and keyboard focus.
- ATDD: new desktop/mobile reference checks failed before runtime edits: current chapter was brown `oklch(0.555 0.163 48.998)` instead of screenshot orange `oklch(0.769 0.188 70.08)`, and form divider was `rgb(0, 0, 0)` instead of light stone-100. Updated the prior expected selected colour deliberately to the newly supplied screenshot, not to dismiss an unexplained failure. All 10 focused cases passed after implementation, including geometry, bilingual alignment, colour, navigation, fallback and current/candidate distinction.
- Implementation: explicit light border colours for all separators; subdued input focus/cancel treatment; 560px bounded desktop popup and 240px book column, one-row bilingual names, bilingual chapter heading, five 50px-minimum desktop tiles per row; phones retain 4 columns and bounded height. Restored exact reference palette using existing amber-500/amber-100 utilities. No hook/confirmation/Router/owner changes. Typed-reference form remains for existing workflow behavior; this is intentionally not a pixel-identical copy of the pre-typed-entry design.
- Build command: `VITE_APP_BASE=/ VITE_PLATFORM_ORIGIN='' VITE_STUDIES_ENABLED=true VITE_SUPABASE_URL=https://reader-test.supabase.co VITE_SUPABASE_ANON_KEY=test-public-key VITE_APP_DIRECTORY_URL=http://127.0.0.1:8001 npm run build --workspace=apps/scribeswell/web` passed TypeScript/Vite, with existing bundle-size warning. Production-preview and reader regression evidence follows.
- First visual comparison confirmed palette/alignment improved; compacted the required typed-entry form to inline input/Cancel plus candidate preview so it occupies less space. Kept its accessible label, focus, errors, confirmation and cancellation unchanged.

## Review Triage Log

- Independent review found a duplicated English header for reference-only books with no Hebrew. Verified with actual mobile browser: `Rev 1` produced two `Revelation of John` elements; new single-heading assertion failed before repair. Initial `Revelation 1` probe used an unsupported alias and was corrected to existing `Rev`. Claimed internal horizontal overflow did not reproduce (`scrollWidth <= clientWidth`); confirmed duplication graded low, patched for normal reference-only browsing. Header now omits repeated English subtitle when Hebrew absent and bounds both sides with truncation/full-name titles. Preserve typed entry and Hebrew selected trigger. Follow-up production preview covers the repaired heading.
- Final independent source/visual review returned no additional supported findings; reviewer explicitly withdrew the unverified overflow claim. No deferred findings or extra review layers configured.
- Final verification after form/header repairs: `npm exec --workspace=apps/scribeswell/web -- playwright test --config playwright.config.cjs reader.spec.cjs --workers 2` — 52 passed; `WORKSPACE_POLISH_SCREENSHOTS=/tmp npm exec --workspace=apps/scribeswell/web -- playwright test --config playwright.polish.config.cjs --workers 2` — 12 passed against rebuilt artifact. Scoped `git diff --check` passed. Rebuilt with the exact public fixture command above after final source changes. No root-wide check exists.
- Both parent and reviewer viewed the reference and final browser captures `/tmp/scribeswell-selector-detail-{desktop,mobile}.png`. Compared actual orange/pale-amber palette, divider weight, bilingual row alignment and tile spacing; typed entry intentionally retained in a compact row, responsive phone grid intentionally four columns. Linux fonts/scrollbars may differ from the Windows reference; no pixel-identical whole-image claim. No production deployment.
- Model recommendation: consulted current official OpenAI Docs and recommended GPT-6 Astra/High for demanding visual work, without switching the active session. Coordinator/reviewer retain inherited capability (exact model/effort not exposed); no implementation delegation. One confirmed review repair, one unsupported test alias corrected, one final visual form refinement. Existing usage observer records available metadata; billing and exact model/tool elapsed split remain unknown.
