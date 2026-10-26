# Provider review correction evidence

This correction changes the existing provider storage recovery ordering, its focused browser tests, and the two owning application documents. Runtime and tests are frozen after run 05. No controller, native storage, migration, actual-owner integration or KDG-port change is included.

## Commands and chronology

All browser commands used `SCRIBESWELL_TEST_PYTHON=/usr/bin/python3 npm run test:browser --workspace=apps/scribeswell/web --` followed by these exact arguments:

| Log | Arguments | Result |
| --- | --- | --- |
| 01-provider-red.log | `--workers=2 --project=desktop --fully-parallel workspace-restoration.spec.cjs -g 'provider queued success'` | 2 genuine pre-fix failures: third projection remained at 3 durable tabs instead of 4; an older queued success hid a newer storage-read failure. |
| 02-provider-green.log | `--workers=2 --project=desktop --fully-parallel workspace-restoration.spec.cjs -g 'provider queued success'` | 2 passed, 3.4s. |
| 03-max-wait-and-pop.log | `--workers=3 --project=desktop --fully-parallel workspace-restoration.spec.cjs -g 'provider continuous|remembered dialog history POP|provider successful public'` | 2 passed, 2 failed, 9.7s. POP fixture gated only one of StrictMode's two bootstrap opens and failed before exercising POP; retained unchanged as chronology. |
| 04-pop-strictmode-gate.log | `--workers=2 --project=desktop --fully-parallel workspace-restoration.spec.cjs -g 'remembered dialog history POP'` | 2 passed, 3.1s, after the fixture explicitly observed and gated both bootstrap opens. No POP runtime change. |
| 05-focused-final.log | `--workers=4 --fully-parallel workspace-restoration.spec.cjs -g 'provider queued success|provider successful public|provider continuous|remembered dialog history POP|denied storage Retry remembers|cross-window future version|changed intent during identity verification|loop1 eviction Retry'` | 20 passed, 26.4s, desktop and mobile. |

`git diff --check -- apps/scribeswell/web/src/context/ReaderWorkspaceContext.tsx apps/scribeswell/web/tests/workspace-restoration.spec.cjs apps/scribeswell/docs/WORKSPACE_RESTORATION_V1.md apps/scribeswell/docs/WORKSPACE_RESTORATION_EVIDENCE.md` passed.

The provider tests exercise real IndexedDB transactions and actual eligible UI changes. An operation sequence releases failure suppression only when successful completion is at least as recent as the latest failure; private recovery feedback is preserved. The paused-clock maximum-wait test proves the durable current projection remains unchanged at 1999ms and commits at 2000ms despite changes every 150ms, with no lifecycle flush. POP tests prove stale accept/victim choices remain inert and Cancel followed by a current Retry works.

## Source proof and limits

`05-source-before.json` and `05-source-after.json` hash the four changed runtime/test/document files immediately before and after the final focused run. `05-source-proof.json` records their equality. `qualified-source-reference.json` preserves the prior parent-qualified provider/test hashes extracted from the existing immutable parent manifest; it is not a reconstructed pre-red manifest. Genuine pre-fix failures remain in 01.

The prior parent whole-browser qualification was 982 passed / 2 expected native integration skips with a passing production build. Those results belong to its recorded source snapshot. This correction has only the focused verification above; new full-browser/build qualification and independent review remain with the parent. Actual-owner/native-device/session/shared-resource/release integration remains deferred.
