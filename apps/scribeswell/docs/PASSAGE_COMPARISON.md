---
title: Compare two Hebrew passages
created: 2026-09-27
status: done
route: oneshot
---

<frozen-after-approval>
## Intent

Add an optional two-passage comparison using the existing public Hebrew text. Each passage has independent navigation and scrolling. Preserve the single-passage default. Wide screens show both passages; narrow screens provide passage switching without losing reading positions. URLs preserve both references across refresh, sharing and browser history. Word analysis identifies its originating passage and verse; switching or closing passages must never misattribute analysis. Existing authentication and public access remain unchanged.
</frozen-after-approval>

## Implementation Notes

Small reversible frontend change; no unresolved intent gaps or external mutations. Reuse BookChapterSelector, VerseReader and existing API hooks. ReaderPage owns URL state (`book`, `chapter`, `compareBook`, `compareChapter`) and shared selection; extract PassagePane to preserve independent hook/scroll lifecycles. Preserve DOM for inactive mobile pane. Opening comparison duplicates the current reference, ready for independent selection; closing retains passage 1. Analysis remains associated with its pane even for identical references. Responsive layout expands only for comparison. No synchronized scrolling for unrelated passages.

Acceptance: given a single passage, Compare opens two independent panes; given comparison, navigating/scrolling one leaves the other unchanged; given a shared URL, refresh/Back restore references; given words selected in either pane, only that pane highlights and analysis names its source verse; given a narrow viewport, switching retains scroll and no content overflows; failures/retries and delayed responses remain isolated.

Impact: application-specific UI only; shared UI, scaffold, agent-context and ADR changes unnecessary. No database/API/auth/release migration changes. Documentation lives here with requirement-to-test evidence. Focus mode, translations, session tabs and personal notes are outside this delivery.


Implemented in `ReaderPage`, extracted `PassagePane`, verse callback/context header and selector viewport sizing. Comparison expands the workspace, uses side-by-side passages from 1024px, and docks analysis from 1280px; below those widths analysis sits beneath text. Opening comparison clears old analysis and word selection sets the mobile pane, preserving attribution across resizing. Chapter parsing rejects values outside 1–150 before numeral rendering; valid book-specific missing chapters still use existing API error/empty handling.

## Review Triage Log

- Medium, fixed: positive safe integers allowed impractically large Hebrew numeral rendering. Bound both URL chapters to the collection-wide maximum of 150 and test oversized/negative values.
- Medium, fixed: comparison opening/resizing could show analysis from a hidden pane. Clear selection on opening and track the selected pane for mobile visibility; regression covers opening with existing analysis and resizing after selection.
- Low, fixed: mobile switcher accessible names omitted references. Include book/chapter and associate controls with stable passage IDs.
- Medium, fixed: comparison-specific late-chapter and keyboard coverage missing. Added delayed chapter replacement, independent pending requests, keyboard selector/scroll/word interaction and 1100px tablet analysis layout checks.
- Low, fixed: delivery evidence incomplete during review. Final commands, outcomes and requirement mapping recorded below. No findings deferred.

## Verification

ATDD before implementation: `LD_LIBRARY_PATH=/tmp/pts-browser-libs/usr/lib/x86_64-linux-gnu npm run test:browser --workspace=apps/scribeswell/web -- --grep 'compare passages independently'` — two failures, desktop/mobile missing Compare passages control (`/tmp/comparison-red.log`). Initial sandbox launch could not bind the test server; rerun with permitted local server access produced the acceptance failures.

Final commands:

- `LD_LIBRARY_PATH=/tmp/pts-browser-libs/usr/lib/x86_64-linux-gnu npm run test:browser --workspace=apps/scribeswell/web` — 30 passed, including all 20 prior reader checks (`/tmp/comparison-tests.log`).
- `npm run build --workspace=apps/scribeswell/web` — passed; existing large-chunk warning remains.
- `LD_LIBRARY_PATH=/tmp/pts-browser-libs/usr/lib/x86_64-linux-gnu node /tmp/pts-local/comparison-live.cjs` — passed using real Psalm 119 and Exodus 3 at 1440×900, 1024×768 and 390×844. Verified morphology context, independently scrolled passage, selector bounds and no document overflow. Desktop/mobile screenshots visually inspected.
- `git diff --check` — passed.

Acceptance-to-test mapping in `web/tests/reader.spec.cjs`:

| Requirement | Coverage |
| --- | --- |
| Independent navigation, default/close, shared URL, refresh and Back | compare passages independently, restore URL state and identify word origin |
| Independent scroll, mobile position retention, identical-word attribution | comparison preserves independent scroll and isolates identical-word selection |
| Failure/retry isolation, late analysis after closing | comparison chapter failure and delayed response leave the other passage usable |
| Safe shared chapters, mobile analysis consistency, named controls | comparison bounds shared chapter numbers and keeps analysis with the visible mobile passage |
| Late chapter isolation, keyboard navigation/scroll, intermediate viewport | comparison isolates a late chapter and supports keyboard reading at tablet width |
| Single reader, source protection, selector bounds, long morphology and fixed navigation regressions | Existing 20 desktop/mobile reader checks |

No database, production or deployment actions required. No backend/shared-package changes; verification scoped to the affected reader and live existing API.
