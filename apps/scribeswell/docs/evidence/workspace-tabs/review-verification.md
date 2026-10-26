### Account sign-out does not have verification for multiple retained dirty notes

- **Changed surface:** `apps/scribeswell/web/src/context/StudiesContext.tsx:468` adds `exitAccount`, which must inspect every retained dirty lane before signing out.
- **Impacted consumer or site:** the Sign out button at `apps/scribeswell/web/src/components/layout/Topbar.tsx:49`.
- **Existing test evidence:**
  - `Regression gap`: `apps/scribeswell/web/tests/personal-notes.spec.cjs:131` creates one failed note, verifies Stay preserves it, retries its save, then signs out. The invalid-input and composition sign-out tests at lines 179 and 198 also use one note.
  - The distinct retained-editor test at `apps/scribeswell/web/tests/personal-notes.spec.cjs:1301` exercises two notes but never signs out.
  - Repository-wide searches for `exitAccount`, `studies.exit`, `Sign out`, and `signOut`, plus reading the relevant personal-notes and session tests, found no multi-note sign-out assertion.
- **Missing verification:** signing out with a saved active note and a failed or composing background note must still guard departure; with two unresolved notes, accepting one departure must not bypass the other.
- **Demonstration:** restrict `exitAccount`’s pending list to the active note. The single-note sign-out tests and multi-editor switching test would still pass, while a failed background note would no longer prevent immediate sign-out.
- **Consequence:** signing out can discard background writing without the required opportunity to stay.
- **Disposition:** `patch` — add a browser test in `personal-notes.spec.cjs` covering background dirty-note protection and sequential handling of two unresolved lanes.

### Dictionary and occurrence “Open in new tab” actions are not exercised

- **Changed surface:** `apps/scribeswell/web/src/components/bible/WordStudy.tsx:160` and `:172` add new-tab actions for scripture previews and occurrence rows.
- **Impacted consumer or site:** `apps/scribeswell/web/src/pages/ReaderPage.tsx:149` translates the `"tab"` target into a new workspace containing the selected verse.
- **Existing test evidence:**
  - `Regression gap`: `apps/scribeswell/web/tests/lexicon.spec.cjs:89` opens a dictionary reference with Open beside and verifies the reference and verse position. The occurrence test at line 80 verifies pagination, filtering, and retries.
  - The workspace analysis test at `apps/scribeswell/web/tests/lexicon.spec.cjs:465` checks retained filters and expansion, without opening a result.
  - `apps/scribeswell/web/tests/personal-notes.spec.cjs:1376` verifies new-tab navigation from collected passages, which bypasses `WordStudy` and its target dispatcher.
  - Repository-wide searches for `Open in new tab`, `onOpen("tab"`, and `newTab(` found no tests invoking either new WordStudy action.
- **Missing verification:** each action must create and activate another workspace at the selected verse, preserve the source workspace, and avoid opening the passage picker.
- **Demonstration:** change both new WordStudy callbacks from `onOpen("tab", …)` to `onOpen("here", …)`. None of the checked tests clicks those controls, so their assertions would still pass.
- **Consequence:** selecting Open in new tab could replace the current reading instead of creating the requested workspace.
- **Disposition:** `patch` — add parameterized browser coverage in `lexicon.spec.cjs` for dictionary-preview and occurrence-row new-tab navigation.
