# Legacy reload consumer correction

Only `apps/scribeswell/web/tests/personal-notes.spec.cjs` changed. Runtime and
existing fixture method/native-integration limits are unchanged. All original
content, formatting, direction, link, operation and count assertions remain.
Actual browser reloads now wait for a real eligible public/current-account IDB
checkpoint, matching the active live tab incarnation and selected study/note IDs.
When a native snapshot exists, public pane identities/references and active pane
must also match. After reload, consumers wait for currently authorized rendered
study context and the restored note lane before sending new tool intent.

Note consumers use the restored study outline. Collection and malformed study
consumers explicitly leave/reopen when they need ordinary library/passage loading.
The composing deletion Cancel flow retains its final composed-text, saved-payload
and zero-deletion assertions. The public-only malformed-capacity case also waits
for its final new study metadata checkpoint before teardown, allowing the fixture
identity verification to finish without suppressing errors or clearing routes.
Storage is never cleared or bypassed.

Parent pre-correction evidence remains under
`../workspace-restoration/parent-loop1-regression-01/`: controlled stop after
311 passed / 11 failed / 4 interrupted / 1 skipped / 609 not run. Its frozen
165-file SHA was `673a1af4e9a0e8300410bf4b15b24410c9959dfd8f9902bca63e799a0beeb720`.

## Focused verification

The commands use `SCRIBESWELL_TEST_PYTHON=/usr/bin/python3` and only the edited
file's reload consumers. Full verification stays parent-owned. No actual-owner,
native SQL/session/device integration, KDG ports or release activation ran.

- `01-reload-consumers.log`: 22 failed / 8 passed / 2 native-gate skips, 1.2m.
  The initial checkpoint helper incorrectly required an optional native history
  snapshot before any public transition. The helper now identifies the actual
  active live tab control; no expected business result changed.
- `02-live-tab-checkpoint.log`: explicit enrollment and composing deletion Cancel,
  both viewports, 4 passed, 10.0s.
- `03-reload-consumers.log`: 29 passed / 1 failed / 2 native-gate skips, 1.1m.
  The mobile malformed-capacity case failed because its fixture Auth callback was
  still evaluating the page at teardown after final study creation. A final real
  metadata checkpoint is now awaited; no errors or routes are suppressed.
- `04-reload-consumers.log`: final source, 30 passed / 2 existing native-gate
  skips, 1.1m. Every edited executable reload consumer passed on desktop/mobile.

Final command (stdout/stderr retained in `04-reload-consumers.log`):

```sh
SCRIBESWELL_TEST_PYTHON=/usr/bin/python3 npm run test:browser --workspace=apps/scribeswell/web -- --workers=4 --fully-parallel personal-notes.spec.cjs -g 'explicitly enroll|native PostgreSQL browser reload|rich paragraphs|editor toolbar actions|Shift Enter soft|rename: explicit Save Cancel|collected passages persist|links source marks|across an owned atom survives|note deletion composing cancel|malformed Add Cancel|malformed capacity Add'
```

`git diff --check -- apps/scribeswell/web/tests/personal-notes.spec.cjs` passed.
`source.json` records the final edited test SHA-256. All failed logs are retained.
