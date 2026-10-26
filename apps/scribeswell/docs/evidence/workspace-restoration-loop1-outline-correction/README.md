# Restored visible study outline correction

The genuine first red selects an acknowledged study/note through UI, waits for the
actual private-ID metadata checkpoint, reloads, waits for authorized restoration,
and opens Studies without Leave/reselection. The restored note list contained one
note instead of the current two; passages and controls were not initialized.
`01-outline-red.log` retains that pre-fix failure. `05-back-caller-red.log` retains
a second genuine red for NoteEditor's direct Back to Studies entry after the
initial rail-only fix. No runtime was removed to reconstruct either red.

Changes are confined to StudiesContext, its existing private HTTP adapter, and
component tests. Restored contexts retain a compact incomplete-outline marker,
including inheritance through existing tab state. A single visible-Studies effect
owns lazy readonly note-page and existing collection-lane loading across rail,
direct Back, tab return and inherited contexts. Hidden tools start no outline work.
Reads are sequential, independently bounded by the existing 15-second adapter,
with a 30-second overall cancellation bound. Visibility/account/tab departure
cancels the current attempt. Attachment checks account/token, tab/map identity,
current study/note, navigation, intent and the collection read generation. It
preserves dirty resource lanes and existing collection mutations; it never calls
ordinary openStudy/openNote during restoration. Pagination cursor and current
passages initialize through existing owners. Invalid owners fail safely with the
existing Retry surface. Ordinary explicit study selection retires the marker.
No metadata DTO, migration, Auth/session implementation or endpoint was added.

The personal-notes Auth fixture now maps explicit synthetic bearer tokens to their
owners entirely in Node, eliminating page-JS evaluation during teardown. The
account-replacement regression explicitly covers both reused `current` and
distinct `other-account` bearer tokens, preserving old-account input, label and
late-save masking assertions. Current bearer still verifies as its original owner;
a mismatching SDK account cannot change that identity. No errors or routes are
suppressed. Native/actual-owner/session/device/KDG/release gates remain deferred.

## Chronology

All logs are retained here. No parent broad run was repeated. Parent attempt02
remains under its existing evidence directory with the corrected partial counts:
117 passed / 1 failed / 4 interrupted / 1 skipped / 813 not run.

- `01-outline-red.log`: genuine missing-current-outline red, desktop.
- `02-outline-green.log`: first rail-owner implementation, 2 passed, 3.9s.
- `03-outline-adverse.log`: 20 passed, 27.7s; late note/collection completion,
  dirty input, leaving, closure, account switch, invalid owner and Retry.
- `04-outline-and-fixture.log`: 30 passed / 4 failed, 1.2m. Replacement-study
  cases exposed Retry routing through a stale captured study after Leave. It now
  checks the current fields-map study. Independent account-ID coverage and the
  rejected-title fixture lifecycle case passed.
- `05-back-caller-red.log`: genuine direct-Back bypass, desktop; fixed by moving
  loading into the one visible-panel owner, rather than modifying each caller.
- `06-visible-owner.log`: 41 passed / 3 failed, 1.2m. A paging observation checked
  the request count synchronously after click; it now waits for the same expected
  count. Replacement focus checks ran before B's selection had completed; they now
  wait for B's editor and explicitly focus a surviving rail before releasing A.
  The fixture holds A only and responds with B's actual parent for B passages.
  Content, focus and count expectations remain intact.
- `07-focused-final.log`: pre-modal-recovery source, 58 passed, 1.5m, both viewports. Includes
  all outline entry paths, actual selector/pagination interaction, dirty lane
  retention, old-A/new-B completion, current-account/token privacy, no hidden
  outline reads, and directly affected existing concurrency/deadline/401/403 tests.

Final command:

```sh
SCRIBESWELL_TEST_PYTHON=/usr/bin/python3 npm run test:browser --workspace=apps/scribeswell/web -- --workers=4 --fully-parallel workspace-restoration.spec.cjs personal-notes.spec.cjs -g 'outline return|account replacement discards prior private UI|rejected study title can be corrected|same-account reauthentication preserves input|collected passages persist|malformed Add Cancel|same verified owner refetches|late hydration ignores|overall30s hydration deadline|current hydration401|current admission403'
```

Only tests covering edited files ran; no full suite was run in this correction.
The owning package build ran after the final recovery change. Parent owns full
verification. `source.json` records final hashes of
the four changed runtime/test files. Their diff whitespace check passed.


## Final modal-cancel recovery

`08-modal-cancel-red.log` is a genuine additional red on the 58-pass source:
Rename opened and cancelled while the first note read was held, then the same
visible study stayed partial with no complete outline or Retry. The existing
freshness check correctly rejected changed intent but did not expose recovery.

The same readonly owner's finalization now offers the existing outline error/Retry
when its incomplete read retires but the exact account/tab/map/study/note remains
visible and there is no newer error. It changes no input, selected resource, command
or focus. Successful, replaced, hidden, closed and account-retired contexts cannot
receive this error. Retry runs both note and passage reads through that owner.

- `09-modal-cancel-green.log`: despite its filename, 4 passed / 4 failed, 39.5s.
  Rename cases passed. Delete cases used the wrong dialog label (`Delete study`
  rather than the actual `Delete this study?`) and timed out before cancellation.
  The selector was corrected; all semantic assertions were retained. Mutation
  counting now observes actual business requests independently of owner fixtures.
- `10-modal-cancel-final.log`: final source, all 8 desktop/mobile Rename/Delete x
  held notes/passages cases passed, 22.3s. Each either completes safely or uses the
  truthful explicit Retry, then proves complete notes, working passage controls,
  unchanged selected note, cancelled title and zero business mutations.
- `11-build.log`: `npm run build --workspace=apps/scribeswell/web` passed;
  Vite 17.36s, existing >500kB bundle warning.

The exact final focused command is in `10-modal-cancel-final.log`:

```sh
SCRIBESWELL_TEST_PYTHON=/usr/bin/python3 npm run test:browser --workspace=apps/scribeswell/web -- --workers=4 --fully-parallel workspace-restoration.spec.cjs -g 'outline return cancelled'
```

The earlier 58-pass run qualifies its explicitly earlier source; it is not relabeled
as final-source full qualification. Runtime/tests are now frozen for parent full
regression and independent review. Final four-file hashes were refreshed in
`source.json`; source diff whitespace checks passed. All earlier failures and
parent partial evidence remain intact.
