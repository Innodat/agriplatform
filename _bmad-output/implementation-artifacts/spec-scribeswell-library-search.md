---
title: 'Find and return to saved personal studies'
type: 'feature'
created: '2026-10-25'
status: 'in-review'
baseline_commit: '404f0956f58661cc90d87fdfdbb9142ee4048bc1'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/apps/scribeswell/docs/LIBRARY_SEARCH_V1.md'
  - '{project-root}/apps/scribeswell/docs/PERSONAL_NOTES_V1.md'
  - '{project-root}/apps/scribeswell/docs/NOTE_REFERENCES_V1.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Readers cannot find saved personal studies by their writing or passage references, and library return loses loaded search/position.

**Approach:** Deliver the own-library subset of CAP-1/ST-03: authorized saved-title/note/reference search with complete filtered pagination and retained account-safe library context.

## Boundaries & Constraints

**Always:** Preserve public reading, current owner HTTP authority, saved-content truth, stable ordering, ordinary list consumers, independent note/title/collection lanes and dirty/concurrent work. ATDD/TDD; integration stays at the end under direction266. Use the adopted app search contract for exact read/matching/retention rules.

**Never:** Treat a first-page/client scan as complete search, expose query/private content in URLs/storage/logs, search unsaved writing, infer authority from cursors, or mutate records while searching. No sharing/recipient/notification owner, Access competitor, Leave/factory, source publication, schema migration, provider/config/deployment/activation work.

## I/O & Edge-Case Matrix

| Given / when | Then |
| --- | --- |
| Title, formatted note/list/source-label text or stored link label matches beyond first unfiltered page | Find the active own study once; filtering precedes pagination and formatting boundaries do not split words. |
| English/Hebrew book/chapter/range input, cross-chapter or reference-only Matthew | Match catalogue-consistent reference overlap/book identity independently of labels; never fetch/fabricate scripture. |
| Literal punctuation, Unicode, invalid/ambiguous reference, blank/oversized/malformed body | Literal text semantics remain; no guessed reference; blank library works, structural invalid input safely refuses. |
| More/equal timestamps/query change/late success or denial | Stable query-bound continuation, deduplication and current-generation results/errors/loading; no stale overwrite or private disclosure. |
| Open result, change tools, return after several pages | Preserve reader/editor context; revalidate applied query and restore loaded depth plus best-effort stable scroll/focus anchor. |
| Account change, current denial or verification outage | Clear old private state on confirmed replacement/denial; hide unavailable private results and allow retry, without claiming deletion. |
| Search read and previous consumer | No receipt/value/revision change; old GET/list cursors remain compatible. Native/actual-owner proof prepared only. |

</frozen-after-approval>

## Code Map

`A=apps/scribeswell`, `B=A/backend`, `W=A/web/src`. LIBRARY_SEARCH_V1.md owns exact contracts. `B/personal_notes_router.py::handle` bounds/strictly dispatches protected reads before storage; existing `list` permits limit/cursor only. `B/personal_notes_storage.py::list` filters owner/active, orders created_at/id and limits; extend with a separate read search, not a client scan. `B/personal_notes_cursor.py` v1 is unchanged; separate closed search cursor. `B/personal_notes_contract.py` owns DTO/OpenAPI and format1/2 grammar. Use existing `passage_references.py` catalogue/aliases/targets; normalized passage_entries plus note JSON suffice. `W/lib/personal-notes.ts`, StudiesContext and StudiesPanel own API/library; current leave reloads page one and loadStudies lacks query generations. Preserve current lanes and corrected native editor unchanged.

## Tasks & Acceptance

- [x] `B/personal_notes_search.py`, cursor/contract/router/storage modules: test-first closed read query/body, normalization/reference interpretation, query-bound cursor and guarded database-side matching before limit. No migration/index model or mutation.
- [x] `A/tools/py/export_personal_notes_contract.py`, owned OpenAPI/TS: regenerate/check through owning tools; existing list wire remains unchanged.
- [x] `W/lib/personal-notes.ts`, `W/context/StudiesContext.tsx`, `W/components/studies/StudiesPanel.tsx`: separate search/read state, explicit Search/Enter/Clear, More/race/error guards and account-safe library return/scroll/focus without affecting editor/panes.
- [x] `A/tests/test_library_search.py`, affected API/contract tests and `A/web/tests/personal-notes.spec.cjs`: observe acceptance red, prove each matrix row, complete affected component/regeneration/build checks.
- [x] `A/tests/test_personal_notes_storage.py`, owner fixture and owner browser: prepare restricted SQL matching/isolation/pagination/old GET and actual-owner zero-mutation proof; no native/owner/session execution now.
- [x] `A/docs/LIBRARY_SEARCH_V1.md`, `A/docs/LIBRARY_SEARCH_EVIDENCE.md`, personal-note contract and canonical memory (parent-owned): exact implemented/tested/pending status and scaffold/UI/context/docs/ADR impact decisions.

Given multiple matching notes or equal timestamps, when paging, then each eligible study appears once under the stable keyset with current authority; it is never dropped by pre-filter limiting. Given a search across writing, when the current editor has unacknowledged input, then the query uses saved server state and changes neither that input nor its save lane.

## Implementation Notes

Parent audited all19 application paths against404f0956 plus this delivery record, preserving unrelated dirty/untracked work. Runtime supplies the separate read boundary and query/cursor lane; previous GET/list and editor code remain unchanged. Canonical event297 derives current bounded status without altering11CAP/38ST/27companions.

Matrix audit: rows1–2 have executed SQL-construction/parser/router/browser-body coverage and prepared actual-database matching, not real SQL acceptance. Row3 has strict transport/cursor tests plus Enter/Clear/400 correction; row4 has cursor binding and browser More/late success/denial/finally coverage, with actual equal-time SQL prepared. Row5 has multi-page return/scroll/focus and dirty-note preservation. Row6 has account replacement/403/401 mask/503 retry coverage. Row7 has one-read/no-write storage-method tests and unchanged GET compatibility; actual SQL snapshots/GET continuation prepared only as explicitly directed. Every executable component covering case ran; native/owner/session rows remain unexecuted under user-directed final-integration deferral. No complete SQL or full ST03 acceptance claim.

Review correction audit: all14 individual findings/12roots addressed. Five focused desktop reds reproduced the interaction defects;36 desktop/mobile search checks then passed. Typed invalid state, masked setter/control guards, composition guard, refresh-only visible restoration and schema parity are direct corrections. Native20 collected/syntax only. Final140-source SHA256 a30a1d1e5d30e6334342bb567ce2130a9a1cda6fed0d9baac604c0f0f97cce40; parent complete regression later finished359passed/1mobile scroll-return failure/2expectedskips9.6min; final Python277/build passed. P2 correction in progress; no final full pass.

Final component checkpoint:368 browser passed/2expectednative-skips6.8min;277 Python18.02s/1existingwarning; appbuild and exporter/catalogue/pinnedTS/helper/composition passed.140sourcehashes remained b50a21f024f41d31cb86d0c83e991831115ea5fe37d715be1de33965c70ac9d6.20native collected0.23s/syntax only. Original359/1/2 and all focused reds retained. All17 actionable individual rows corrected; P5 false, none deferred. Scoped local preservation commit authorized; status remains in-review for final integration, no full SQL/owner/production qualification.

## Spec Change Log

## Review Triage Log

All three reviewers completed before triage. Each finding receives its own verdict before shared-root grouping; no intent change or spec rewrite is needed.

| ID | Verdict | Evidence and route |
| --- | --- | --- |
| B1 | low | DTO AfterValidator rejects NUL while exported query schema only says maxLength200. Schema consumers can accept a runtime-refused value; direct owning-schema metadata correction/regeneration, patch. |
| B2 | medium | Search form submits unconditionally and has no composition/key guard. Composition-confirming Enter can trigger the ordinary submit path; add focused composition acceptance and minimal event guard, patch. |
| B3 | medium | authority mask returns empty searchCandidate but setter remains live; controlled editable input can replace retained private candidate while masking display. Disable/read-only masked editing and prove recovery retains exact original, patch. |
| B4 | medium | Every More success increments libraryRestore; effect focuses old result and writes remembered scroll even when user moved to input/More. Restrict restore to refreshed library reads and prove focus stays put, patch. |
| B5 | medium | Restore effect lacks tool visibility guard/dependency while shared aside hosts Analysis; delayed success can move its active scroll. Gate restore to visible Studies and prove delayed hidden completion is inert, patch. |
| B6 | low | Input aria-describedby references only help; input-invalid feedback lacks aria-invalid/error association. Direct accessible state/ID correction, patch. |
| B7 | low | Completed nonempty results remove Loading without a status message while focus stays on submit/input. Add concise query-free completion status, patch. |
| B8 | low | Prepared corrupt reference lacks all catalogue fields, so canonical mismatch can mask numeric-guard defects. Add otherwise-valid corrupt target fixtures for direct boundary qualification; native execution remains deferred, patch. |
| B9 | low | Prepared matching cases lack independently mismatched catalogue/version/versification and unsupported-document negative controls. Add narrow fixtures/assertions without altering semantics, patch. |
| B10 | low | Existing old-query denial test covers403 but not retained401/private-candidate behavior across same-account token refresh plus newer verified search. Add focused regression for existing generation guard, patch. |
| E1 | medium | Same defect as B4: unconditional restore counter at loadStudies success plus shared effect steals current focus after More. Direct pagination-versus-refresh correction, patch. |
| E2 | low | Same defect as B1: exported SearchStudies.query lacks NUL exclusion accepted by runtime. Owning-source/schema regeneration, patch. |
| V1 | low | Pre-verified gap: positive prepared saved-note fixture is format2, format1 fixture inactive; restricting search to2 escapes coverage. Add active format1 unique-body match to prepared native proof, patch. |
| P1 | medium | Parent trace: prepared owner first search expects403 before any actor setup, but same-stage GET expects503. services/access/studies_access.py53–55 explicitly returns503 when actor absent, app adapter maps503 to studies_access_unavailable. Correct search assertion to existing503/code and retain later actual403 tests. No owner semantics change, patch. |
| P2 | medium | Final parent362-case frozen run:359passed/1mobile scroll-return failure/2expectedskips9.6min. Focus restores, scroll becomes0 versus required>1215; direct restoration/capture race correction with unchanged assertion, patch. |
| P3 | medium | Controlled queued-RAF acceptance reproduced input focus theft after a newer query. The old callback guarded generation only after DOM focus/scroll and dependencies did not cancel it; check current account/epoch/query/navigation/selection before any DOM mutation, patch. |
| P4 | medium | Focused unfinished-selection red: a result detail request completed after a newer submitted query and reopened Study A (expected0 headings, received1). openStudy checked account/navigation but omitted changed library generation; directly fence stale selection success/error while preserving current loading ownership, patch. |

| P5 | false | Parent suspected a stuck lock when More supersedes a queued restore. Current loadStudies already executes `if(more)state.positionLocked=false` before the read starts, directly disproving that sequence. No correction or extra coverage required; reject. |

Group only identical roots B1/E2 and B4/E1. The initial12 surviving root entries and subsequent P2–P4 route patch; none deferred/rejected. Final SQL/owner execution remains user-directed final integration, not a review waiver or claimed proof.

## Verification

Executed before review: frozen complete notes296passed/2expected native-browser skips7.9min; focused search followups24passed; parent affected Python277passed/1existing warning16.97s; worker affected229passed. Build/export/catalogue/pinnedTS/helper/composition passed;19native collected/syntax only. Exact commands, original API-red chronology gap, interrupted runs and post-freeze two-test-file hashes are in [application evidence](../../apps/scribeswell/docs/LIBRARY_SEARCH_EVIDENCE.md). Independent review corrections and final component qualification are complete below; final integration remains open.

Smallest missing beyond-first-page/title/note/reference acceptance first, then strict DTO/cursor/storage-method/API and desktop/mobile library matrix. Parent complete affected notes/reader regression, app build, catalogue/OpenAPI/pinned TypeScript/helper/composition checks. Prepare native SQL/actual-owner scenarios and collect only; no native/owner/session execution or shared ports. Record exact commands/results and earlier failures; no root-wide or production qualification claim.

Capture implementation baseline only after the corrected note-link component checkpoint; final integration remains deferred.
