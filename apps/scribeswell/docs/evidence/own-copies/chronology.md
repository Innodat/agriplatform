# Component chronology

Only app-side synthetic tests and hermetic Vite/Chromium run. No owner services,
native collection/execution, migrations/grants, KDG ports, deployments or pushes.

1. `env -u SCRIBESWELL_STUDIES_DATABASE_URL -u SCRIBESWELL_TEST_DATABASE_URL -u DATABASE_URL /tmp/scribeswell-implementation-python/bin/python -m pytest -q apps/scribeswell/tests/test_own_copies.py::test_copy_commands_accept_exact_source_revision_and_local_base` failed at the behavior assertion: `note.duplicate` was rejected as ContractInputError. After adopted app contract/DTO implementation, the same node passed (1).
2. Initial new component file run progressed through12 tests, then sandbox TestClient stalled; interrupted. Escalated identical explicit app-side file run passed15 tests/1 deprecation warning in2.08s. No SQL fixture loaded.
3. Initial attempted browser red did not run: wrong relative append path, followed by sandbox Vite startup rejection. Corrected the test path and used normal escalation. `npm run test:browser -- --project=desktop -g 'copies: review latest'` then failed at the missing Review latest button (1failed/10s). This is the actual behavior red before conflict UI implementation.
4. Initial pinned generator failed `api_client_generation_failed` inside the sandbox. Normal escalation of the same bounded local generator succeeded `api_client_generated`. No generated hand edits.
5. First build failed missing SavedNoteReview import and unknown legacy-array item type. Fixed imports and used the existing aggregate adapter; next build passed (Vite38.28s), retaining its existing large-chunk advisory.
6. The single Review latest browser case passed1 in38.4s. Expanded new copy/explicit-reopen matrix passed16/failed2 in1.4min. Both failures were strict test locators matching retained hidden original editor plus visible fork. Changed only new copy locators to visible role=textbox; retaining the original dirty lane is required behavior.
7. Six-case correction rerun passed5/failed1 in1.6min: mobile fixture startup timed out at existing firstNote/Add note before any copy operation (detached element). Original assertions retained. No cause claim or general device qualification.
8. Explicit application-node regression via `/tmp/scribeswell-copy-verify.py` passed277/failed2 in43.06s. Failures identified optional `copy_credit:None` changing exact legacy round trips. Preserved original assertions by excluding absent credit on serialization and current reads. Repeated expanded command passed290/1warning in16.58s; exact node IDs and output in application-python.json/log.
9. The older conflict-reopen test now proves the authorized revised UX: opening the existing shared lane retains input; Review latest is separate; only Use latest explicitly replaces it. Its prior implicit-discard expectation was intentionally superseded by this feature, not relaxed to dismiss an unexplained failure.

The historical anonymous mobile-scroll assertion remains unverified and unchanged.
Native source files were parsed with ast only; they were not collected or run.

10. The102-case affected matrix was interrupted after67passes/4failures/2interrupted/29notrun in4.9min. Two failures were existing fixture startup (Add note/device-ready), with no root-cause claim. Two new error cases exposed duplicate visible alerts: the existing global error surface already presented the copy error; the added editor paragraph duplicated it. Removed the redundant paragraph, preserving error assertions. Two in-progress mobile highlight cases were interrupted, not adjudicated. No overall matrix pass is claimed. Exact extracted errors are retained in interrupted-browser-errors.md. Per parent direction, this matrix is not repeated here; final broad qualification belongs to the end phase.
11. A parent-reported transport defect received its own runnable adapter red: a parse_command-accepted259965-byte aggregate repeated20times produced response_invalid against the4Mcharacter transport bound (1failed/9.5s). Raised only that bound to50*262144+65536; per-value/page guards and the2MiB whole-copy bound stay unchanged. The same case also checks one-character-overflow rejection. This is grammar/transport evidence, not actual published-corpus proof.

12. Corrected adapter/overflow behavior passed1 in4.0s (same exact test after transport-only change). Final build/OpenAPI/catalogue/pinned DTO/database-sync checks passed on unchanged19-file hashes; final-checks.json carries exact commands/timings.
13. Per parent direction, ran only previously unreached copy acceptance:10 desktop/mobile error/session/tab cases passed in18.7s, then mobile Save mine passed1 in7.3s. Focused source hashes remained unchanged; focused-results.json/logs retain exact commands and output. These passes establish those case assertions and do not erase earlier startup failures or qualify the interrupted matrix.
14. Self-audit added final post-await creation exclusivity and current-lane identity checks; the focused runs include those guards. Native11cases and the updated frozen-history fixture received AST syntax parsing only; no collection or database authority claim.

## Consolidated review correction batch

Parent requested only focused covering tests, with full verification reserved for the parent. Changes retire only last-context unchanged acknowledged fork buffers; recheck tool/source lane/current/lifecycle/deletion after copied-note reads; refresh authorized study metadata after revision conflict for a next explicit copy; validate optional credit before note/study attachment; constrain own-only credit accounts structurally; and prepare concurrent source-child copy scenarios. Existing failed/interrupted evidence remains unchanged.

The first review-focused browser run passed16/failed4 in1.0min. All lane/tool/deletion/refresh/adapter assertions passed. The four credit-display failures exposed a synthetic fixture page containing both source-study and destination-study notes after Duplicate then Copy study. Its existing study-ID guard correctly rejected it. Corrected the fixture to return only destination-study rows; no adapter guard was weakened. First-run exact output retained in review-corrections-browser-first.log/json. Added malformed trailing-newline actor/timestamp cases with strict lexical lengths. Only the six credit display/adapter cases were rerun; results are in review-corrections-browser.log/json.

The exact earlier interrupted cases were `[mobile] own highlights: first destination is explicitly created and Add note never quotes selected text` and `[mobile] own highlights: native phrase selection preserves touch context menu and desktop context route`. They were not repeated by this batch.

Additional native same-account negative cases and parameterized concurrent note create/replace/passage replacement cases were authored and AST parsed only, with no collection/execution, migration or grants. No broader build/regression check was run in this correction batch.

## Explicit acknowledged fork recovery correction

Parent requested a narrow additional correction, not broader verification. Extended the held-GET/tool recovery case to click Open created and assert no false exit dialog/unload for the unchanged last-context captured branch. Before implementation, the desktop Studies case failed (expected Changes not saved dialog count0, received1;8.7s); command/assertion retained in explicit-recovery-red.json.

Automatic and explicit opening now share the same captured-branch retirement helper. Explicit recovery first authorizes/validates the known destination, rechecks the original operation/account/current tab/navigation/tool/selection/lifecycle, prepares its saved lane and retires only an unchanged branch with no other live context, newer input, running save, invalid/composing input or deletion requirement. It never marks the original server note saved. Newer-input explicit recovery still prompts and Stay preserves that input.

Only the10 covering desktop/mobile cases ran afterward: held-GET Analysis/Studies explicit recovery, newer-input recovery, automatic last-context retirement and preservation with another live context. All10passed in26.0s; exact argv/stdout in explicit-recovery-browser.json/log. No build, broader matrix, native collection/execution or owner action occurred.
