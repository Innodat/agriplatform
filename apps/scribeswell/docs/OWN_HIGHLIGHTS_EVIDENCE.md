# Own-note highlights component evidence

Implemented in the existing opt-in under [OWN_HIGHLIGHTS_V1.md](OWN_HIGHLIGHTS_V1.md).
Parent independent review and corrected-source checks are complete; local checkpoint and canonical reconciliation are recorded by the delivery spec.
No migration, native SQL, privilege provisioning, enforcement activation, live
Auth/Identity/Access call, deployment, push or commit was performed.

The additive aggregate retains document1/2 and exact legacy values, with sticky
format3 and whole-note budgets. New/changed anchors use actual current public
observations before private write locks. Current unchanged anchors, colours,
removal and writing need no source observation. Committed-operation replay is
checked before source waits. Active note create/replace writes immutable validated
reference/anchor metadata in the same private transaction, without historical bodies.
The new metadata trigger checks correspondence with the current owned revision;
forced owner RLS, immutable history and an alternate-write format fence are authored.

Public text/proof use one bounded read-only repeatable snapshot. Optional publication
queries use a savepoint and one chapter batch, including Psalm119's176 verses.
Unsupported/missing/stale proof does not prevent valid public text. The narrow reader
routine exposes no private publication tables. Historical migration profiles remain
pinned; reader-evidence-v1 independently recognizes0005 and supports repeat/postflight.

The reader supports current-note colours, Shift-click, actual continuous desktop
pointer dragging, native DOM selection, desktop context actions, and touch context-menu
preservation. Explicit destination selection/creation, distinct connected Add note and
collected Add to study, repair/recolour/removal, shared-tab writing, safe read statuses,
origin checks and ordinary marked-word analysis are implemented. Word controls retain
button semantics/keyboard operation while permitting native selection. Valid paint is
indexed once per verse/highlight change; writing retains the existing highlight arrays.
Search/outline derive deduplicated connection/link/segment references.

## Final focused checks

All paths below are relative to the repository root. Python means
`/tmp/scribeswell-implementation-python/bin/python`.

| Check | Exact command / evidence | Result |
| --- | --- | --- |
| Application-side Python | `Python -m pytest -q apps/scribeswell/tests/test_own_highlights.py apps/scribeswell/tests/test_personal_notes_contract.py apps/scribeswell/tests/test_personal_notes_api.py apps/scribeswell/tests/test_library_search.py apps/scribeswell/tests/test_note_deletion.py apps/scribeswell/tests/test_study_deletion.py apps/scribeswell/tests/test_publication_profile.py` |235 passed; [output](evidence/own-highlights/final-python.log). No native fixture files selected. |
| Desktop/mobile own-highlight and affected editor matrix | `SCRIBESWELL_TEST_PYTHON=/tmp/scribeswell-implementation-python/bin/python npm run test:browser --workspace=apps/scribeswell/web -- --workers=2 --fully-parallel personal-notes.spec.cjs --grep 'own highlights:|composition defers|insert at caret retains|native insertion Undo Redo preserves writing and source at 0'` |38 passed; [output](evidence/own-highlights/final-browser.log). Hermetic HTTP fixtures/local Vite/Chromium. |
| Build | `npm run build --workspace=apps/scribeswell/web` |Passed; [output](evidence/own-highlights/final-build.log). Existing large-chunk warning remains. |
| Reader integrity | `Python apps/scribeswell/docs/evidence/own-highlights/run_reader_hermetic.py` |2 passed. Explicit test-only fixture replaces public DB open/close lifecycle; unchanged HTTP assertions. No production bypass. |
| OpenAPI | `Python apps/scribeswell/tools/py/export_personal_notes_contract.py --check` |Passed. |
| Catalogue | `Python apps/scribeswell/tools/py/build_reference_catalogue.py --check` |Passed. |
| Generated TypeScript | Pinned Node26 with `/tmp/scribeswell-codegen-isolated/platform/api-client/src/cli.mjs --schema /home/ck/repos/innodat/agriplatform/apps/scribeswell/contracts/personal-notes-v1.openapi.json --output /home/ck/repos/innodat/agriplatform/apps/scribeswell/web/src/generated/personal-notes --check` |`api_client_current`; existing pinned @hey-api0.99.0/TypeScript6.0.3 isolated tooling, no repository toolchain edits. |
| Native preparation | `ast.parse` only for new public0005/private0006 and both new native test files |Syntax passed; new native tests were never collected or executed. SQL syntax/behavior is unqualified. |

[Before](evidence/own-highlights/final-before.json) and
[after](evidence/own-highlights/final-after.json) hashes match for41 selected
implementation/contract/test files across the final focused browser/Python/build
checks. The evidence narrative/harness are not a whole-repository freeze; parent
owns final affected-source review/freeze.

## Requirement traceability

| Requirement | Executed coverage |
| --- | --- |
| Exact aggregate/lexemes/limits/continuity | `test_own_highlights.py`: strict values, bad labels/IDs/versions/colours, full interior-verse proof and newline rejection; existing contract limits/regressions. Browser/server guard parity. |
| Actual coherent text/publication proof | Actual digest comparison against complete synthetic verse words; optional-query savepoint recovery;176-verse one-batch regression. Actual PostgreSQL snapshot/permissions remain prepared only. |
| Fresh proof before locks and atomic preservation | Storage orchestration asserts proof before parent/note locks, rejects before mutations, records metadata before receipt, preserves exact unchanged anchors without source reads and replays before source waits. Existing note/study deletion suites retain revision/lifecycle guards. |
| Mark selection/save/reopen and writing | Browser exact decimal IDs, arbitrary colour, writing/reload/removal, source outage, source correction and explicit same-ID repair. |
| Origin/destination/shared lane | Browser stale generation refusal, cross-pane selection refusal, explicit first destination, shared-tab writing and current-note-only paint. |
| Desktop/touch/ordinary analysis | Actual mouse drag spans two verses and saves continuous segments; native DOM range, touch default context menu, desktop context route, marked-word ordinary analysis. Physical OS/device qualification remains outstanding. |
| Distinct actions and recoverable rejection | Separate Add note/Add to study assertions, no quotation, composing-lane refusal, unavailable-proof rejection and original-operation Retry. |
| Reference discovery | App search SQL adds canonical guarded connections/segments; outline deduplicates all reference sources. Actual PostgreSQL matching remains prepared-only. |

## Failure history and method limits

- The genuine initial behavioral red was the runnable format3 note-create assertion
  in `test_own_highlights.py`: existing parsing rejected the new aggregate. It then
  passed after DTO implementation. Source/UI tests were not all written red-first;
  no stronger inner-loop chronology is claimed.
- The first attempted editor characterization could not start local Vite in the
  restrictive sandbox. The escalated12-case run finished8passed/4failed after editor
  edits had begun, so it does not establish pre-refactor characterization. Failures
  included Undo/caret0 and mobile startup/timeouts. The final focused matrix retains
  and passes the original relevant Undo0/composition/reference assertions; no expected
  behavior was weakened. Initial complete pre-refactor characterization remains a
  method gap.
- Early Python runs exposed the inadvertently widened ordinary-command body/node
  limits, historical-profile head expectations, a stale generated contract and an
  aliased synthetic proof fixture. Ordinary commands retain65536bytes/8192nodes;
  note commands alone use262144bytes/32768nodes. Historical head invocations stay
  pinned; the selected current-head assertion now correctly includes forward0005.
- Initial generator attempts used an invalid extra `generate` argument, then lacked
  pinned tooling; an isolated generator attempt hit sandbox child-process EPERM.
  The existing prepared pinned tooling subsequently generated/checked successfully
  with ordinary escalation. An initial catalogue check used a nonexistent
  `generate_reference_catalogue.py` path; the owning `build_reference_catalogue.py`
  command passed.
- An expanded browser run passed14/16; two test locators incorrectly treated Notes
  as a button rather than a tab. Corrected locators preserved behavioral assertions.
  Another20-case run exposed a real new-destination stale-render capture failure.
  Creation now returns its acknowledged/materialized note ID; subsequent palette
  capture binds that identity, with no timing delay.
- Native mouse dragging initially failed on button/span-only native capture. A
  bounded mouse pointer range now selects contiguous words without preventing touch
  native selection/copy. Desktop cross-verse dragging passed after that correction.
- A later6-case run passed4/6, with mobile startup failure before Start a study and
  a private-context-not-restored snapshot after a mark. Cause was not proved. The
  fixture now awaits the existing device-ready signal before private actions; no
  sleep or production recovery bypass was added. The targeted subsequent6/6 and
  final38/38 include actual drag, ordinary analysis and useful shared note/mark
  preservation. These passes do not establish a general restoration-race fix.
- Two restrictive-sandbox async Python runs hung and their owned sessions were
  interrupted; escalated hermetic runs passed. One intermediate command mistakenly
  selected all of existing `test_owned_migrations.py`:242passed/72skipped, collecting
  existing native cases contrary to the requested collection boundary. No native
  fixture ran and no SQL executed. Final verification excludes that file; both new
  native suites remain syntax-only and uncollected. This deviation is retained.

Prepared native cases cover private metadata RLS/immutability/correspondence,
alternate old writers, competing replacements, rollback/retry and search;
public routine grants/upgrade/repeat/failed-DDL rollback, missing optional function,
and independent-connection snapshot/corpus changes. They are authored assertions,
not evidence of actual SQL permissions, concurrency or migration correctness.
Actual owner/session/native/device/release qualification remains the final phase.
The earlier anonymous mobile-scroll regression remains unverified, with its original
expectation unchanged. No full browser regression or final integration is claimed.

Impact decisions: app-owned documentation/contracts/runtime only; no scaffold,
shared UI, agent-context or ADR change/promotion. Accepted ADRs, historical migrations,
generated-file ownership and unrelated working-tree changes are preserved.

Post-matrix parent correction: repair now initializes the palette from the affected
mark's colour. The existing repair case starts with custom `#123456` and asserts
that repair retains it. The focused command with
`--grep 'own highlights: source correction needs review'` passed2 desktop/mobile
cases; [output](evidence/own-highlights/repair-browser.log). The workspace build
passed again with the same chunk warning; [output](evidence/own-highlights/repair-build.log).
[Before](evidence/own-highlights/repair-before.json) and
[after](evidence/own-highlights/repair-after.json) hashes match for the same41 selected
files across these correction checks. The earlier38-case result is from the preceding
source state; it is not represented as a rerun after this isolated correction.


## Independent review corrections

Three fresh BMAD review lenses produced14 individually triaged findings in the
delivery spec. E1/B2 and E3/B3 share roots;11 distinct correction entries were
addressed. The request to execute native SQL now was rejected under the explicit
user-deferred final phase, without claiming those database contracts qualified.

Corrections retire only definitive pre-write highlight-proof rejections, leaving
unknown-outcome identity intact. Current-note status retains the worst visible
segment; account replacement clears the phrase, and dismissal/navigation cancels
repair. Existing colour/removal controls now reflect blocked lanes, and command
budgets include operation/revision framing. Highlight references themselves supply
discovery rather than accumulating redundant permanent connections; explicit
Add-note connections and existing saved connections remain preserved. Later native
selection and Shift keyboard endpoints work after dragging; the existing destination
pagination is now reachable. Existing recolouring is exercised through saved and
reopened paint while retaining identity, anchor and writing.

The original implementer ran20 focused desktop/mobile cases successfully3.0min
([output](evidence/own-highlights/review-final-browser.log)). An earlier run passed10
and failed2 mobile startup/return cases before feature assertions; that failure is
retained in [output](evidence/own-highlights/review-first-browser.log). Its cause is
unproven; later passes do not establish a general startup/restoration fix. Review
patches were source-directed; no stronger individual red-first chronology is claimed.
Parent corrected-source verification is recorded separately below when complete.


## Parent final corrected-source qualification

All seven checks in [exact argv/results](evidence/own-highlights/parent-results.json)
passed:276 application/pure-evidence tests16.31s (runner19.03s),54 affected
desktop/mobile browser cases5.3min,2 hermetic reader cases, production build,
OpenAPI/catalogue and pinned TypeScript generation checks. The build retains its
existing large-chunk warning. These are focused application/component checks,
not final native/owner/device/release integration.

The41 selected source/contract/test hashes are equal
[before](evidence/own-highlights/parent-before.json),
[after](evidence/own-highlights/parent-after.json), and at parent inspection.
Earlier failed runs, incomplete pre-refactor characterization and inner-loop
chronology limits remain above. The54-case final result includes all review
regressions after the colour-preservation correction; it supersedes neither the
historical failed runs nor their unproved causes. No native SQL was executed.
