# Outline Retry eligibility across surviving tab updates

`01-lifetime-red.log` records four genuine pre-fix failures: Next chapter and tab
Rename, each during a held first notes or passages read. The current public chapter
or explicit tab label had changed successfully, but the stale read retired without
an outline Retry because its captured mutable tab object was no longer in the live
array. Every failure was the missing Retry assertion; no expected value changed.

The minimal runtime change captures the current incarnation and changes only final
Retry eligibility to match the live tab key/incarnation. Existing current account,
token, fields-map, selected study/note, active/visible tab and error checks remain.
The stale-data read guard still requires its original object/intent; it was not
relaxed. No alternate owner, navigation, endpoint or public API was introduced.

Tests retain all earlier modal recovery cases and add both public updates during
both read phases. They prove stale partial data is not attached, explicit Retry
loads the current outline, passage controls work, the new public chapter/tab label
survives and the selected acknowledged note remains unchanged. Next-chapter cases
explicitly use the wide reader viewport where Studies and chapter navigation are
simultaneously visible; mobile-project Next-chapter runs are resized and do not
claim phone-layout coverage. Tab Rename retains the configured viewport.

Final focused command:

```sh
SCRIBESWELL_TEST_PYTHON=/usr/bin/python3 npm run test:browser --workspace=apps/scribeswell/web -- --workers=4 --fully-parallel workspace-restoration.spec.cjs -g 'outline lifetime Retry|outline return cancelled|outline return late.*(close tab|account switch)|outline return tab reentry'
```

`02-lifetime-green.log`: **26 passed, 38.4s**, covering the new lifetime cases,
existing modal recovery and unchanged hidden/closed/account-retirement behavior.
Only tests covering the edited files ran; no full suite or build was run. Parent
owns full verification. `source.json` records the final two-file hashes. Their
`git diff --check` passed. All prior evidence is retained; actual-owner/native,
KDG, integration and release gates remain deferred. Runtime/tests are frozen.
