### Newly selected private context is not verified through persistence and reload

- **Changed surface:** `apps/scribeswell/web/src/context/StudiesContext.tsx:56–66` projects live study/note selections into private device metadata.
- **Impacted consumer or site:** `ReaderWorkspaceContext.tsx:36–48` writes that projection for subsequent restoration.
- **Existing test evidence:** **Regression gap.** Repository searches for `privateProjection`, `workspace-storage`, and their import references located restoration coverage in `workspace-restoration.spec.cjs`. Its private-restoration tests seed private records directly, including the test at line 63. The create/save/reload test in `personal-notes.spec.cjs:115–128` manually reselects the study and note after reload.
- **Missing verification:** Start without private metadata, select an acknowledged study/note through the UI, assert the stored IDs, then reload and verify automatic restoration without selecting them again.
- **Demonstration:** Skipping projection rows when no matching remembered candidate exists would preserve the seeded restoration cases. The personal-notes reload test would still reopen content manually. None of these assertions requires a newly selected context to become remembered.
- **Consequence:** Existing remembered contexts restore correctly while first-time selections disappear on return.
- **Disposition:** `patch` — add a browser test in `workspace-restoration.spec.cjs` covering UI selection → actual IndexedDB contents → reload restoration.

### Device-restoration victim selection lacks coverage of dirty live contexts

- **Changed surface:** `apps/scribeswell/web/src/hooks/useReaderWorkspace.ts:440–444` routes closure of a current tab through the existing departure guard.
- **Impacted consumer or site:** The “Close current tab” choices rendered by `apps/scribeswell/web/src/components/bible/WorkspaceTabs.tsx:31`.
- **Existing test evidence:** **Regression gap.** Symbol/import-reference searches located the controller, its UI caller, and `workspace-restoration.spec.cjs`. The capacity tests at lines 54–59 and 120–123 exclusively choose **remembered** victims. `personal-notes.spec.cjs:1319–1355` verifies dirty-context protection through ordinary tab closure and history restoration, using different controller paths.
- **Missing verification:** Choose a current tab containing the sole unresolved note context during device restoration; assert that Stay preserves its input and prevents installation, and that explicit discard permits installation.
- **Demonstration:** Replacing the guarded call at line 444 with `perform()` would bypass dirty-input protection. The device-restoration tests would still exercise remembered victims, while ordinary-close and history-restoration tests would retain their separate guards.
- **Consequence:** Restoring remembered setups could remove the last live context containing unsaved input without consent.
- **Disposition:** `patch` — add a browser test in `workspace-restoration.spec.cjs` exercising a dirty current victim through the restoration dialog.

### The mismatched-note response check is not exercised

- **Changed surface:** `apps/scribeswell/web/src/context/StudiesContext.tsx:90–91` validates the returned note’s ID, parent study, and owner before hydration.
- **Impacted consumer or site:** The same hydration worker installs the returned note into the shared lane and attaches its selection to the restored tab.
- **Existing test evidence:** **Regression gap.** The test named “wrong owner or parent responses…” at `apps/scribeswell/web/tests/workspace-restoration.spec.cjs:130–131` returns a foreign-owned **study**. Validation fails at `StudiesContext.tsx:88`, before requesting a note. Repository searches for the hydration symbols/imports and mismatched owner/parent fixtures found no test exercising rejection at line 91; the other restoration fixtures I read return matching note fields.
- **Missing verification:** Return a valid owned study followed by a note with a mismatched ID, parent, or owner, and assert that neither its content nor the candidate’s private label becomes visible.
- **Demonstration:** Removing the note-response validation at line 91 would leave the existing foreign-study test failing safely at line 88. The matching-note success fixtures would remain accepted.
- **Consequence:** An inconsistent note response could populate a restored private context without the checked tests detecting it.
- **Disposition:** `patch` — parameterize a browser test in `workspace-restoration.spec.cjs` over mismatched note ID, study ID, and owner ID.