---
title: 'Collect, reopen and open passage references without interrupting writing'
type: 'feature'
created: '2026-10-25'
status: 'in-review'
baseline_commit: '9827908ab7570b4e84f13de19bca91e1aac71d4c'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/apps/scribeswell/docs/PASSAGE_REFERENCES_V1.md'
  - '{project-root}/apps/scribeswell/docs/PERSONAL_NOTES_V1.md'
  - '{project-root}/platform/docs/development/migration-verification.md'
  - '{project-root}/_bmad-output/specs/spec-scribeswell-studies/ux-behaviour.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Personal studies cannot yet collect and reopen scripture references, so saved writing lacks its agreed passage outline.

**Approach:** Deliver a versioned reference catalogue, one English/Hebrew typed/browsable picker, and a persisted notes-first Passages list with explicit Open. Add preserves reading/writing; unsupported text remains reference-only.

## Boundaries & Constraints

**Always:** Preserve dirty/concurrent work, public reading/standalone account entry, existing notes/title/receipt behavior and owner HTTP authority. Use ATDD/TDD, independent collection revisions, immutable source identity, current access/lifecycle checks, bounded original-operation recovery, safe no-store errors and actor/UTC attribution. Integration testing is deferred to the final phase by user direction266; report pending evidence honestly and keep KDG ports free.

**Never:** Implement competing Access/Identity/Notifications, Leave/factory or activate/deploy/change providers. No scripture-text expansion, guessed numbering conversion, silent reference correction, startup migrations/applied-history edits, automatic conflict overwrite, rollback/persistence promise or note/highlight mutation. Later note links/highlights/workspaces/sharing retain their agreed requirements.

## I/O & Edge-Case Matrix

| Given / when | Then |
| --- | --- |
| Owner adds English/Hebrew chapter, verse or range and reopens study | Canonical identity/order persists; whole chapter stays whole; notes/title/reading unchanged. |
| Picker typing, Enter/matching chapter, different chapter or Cancel | Highlight candidate; confirm exact range once; different chapter clears range; Cancel sends nothing and restores focus. |
| Duplicate or overlapping references | Exact duplicate reuses entry; overlapping distinct ranges remain separate; identical snapshot receipts without revision/time bump. |
| Invalid/ambiguous/version-mismatched reference or forged input | Safe typed rejection, no effect; retain editable input and choices, never guess. |
| Explicit Open, range or reference-only Matthew | Navigate active reader only; keep note/other pane; retain complete range, unavailable text is clear with no fabricated words. |
| Concurrent list/title/note edits or stale list revision | Independent revisions; safe409 preserves candidate; deliberate current-list review and explicit new action. |
| Lost reply, retry, changed payload or failed post-ack read | One effect/original outcome; mismatch409; frozen attempt blocks overtaking; confirmed success retries only read. |
| Wrong owner/closed parent/access loss/late account-navigation reply | Safe401/403/404, no disclosure/resurrection/wrong-context update; notes/public reading stay safe. |
| Migration failure or old consumer | Block activation, preserve old data/commands; forward recovery. Native/final owner proof stays pending until executed. |

</frozen-after-approval>

## Code Map

`A=apps/scribeswell`, `B=A/backend`, `W=A/web/src`. Adopted passage contract owns
all exact source/wire/storage/UI rules. Reuse `B/corpus_source.py::BOOK_METADATA`,
`A/scripts/hebrew.json`, `A/data/reference-catalogue/nt-verse-counts.json`.
`B/personal_notes_{contract,router,storage,access}.py`: authority/locks/receipts.
`W/context/StudiesContext.tsx`, `W/lib/personal-notes.ts`: independent recovery lanes.
`W/components/bible/book-chapter-selector.tsx`, `W/pages/ReaderPage.tsx::navigate`,
`W/components/bible/PassagePane.tsx`, `W/components/studies/StudiesPanel.tsx`: browsing,
explicit Open and notes-first outline. Preserve NoteValue and legacy URLs.

## Tasks & Acceptance

- [x] `A/tools/py/build_reference_catalogue.py`, `A/data/reference-catalogue/`, `B/passage_references.py`, `W/lib/passage-references.ts`: generate/check pinned inventory/parser parity and English/Hebrew/bounds tests.
- [x] `B/personal_notes_{contract,router,storage,access}.py`, `A/studies-migrations/versions/0003_collected_passages.py`: implement exact collection wire, constrained storage/receipts, test-first.
- [x] `A/tools/py/export_personal_notes_contract.py` and owned generated outputs: regenerate/check wire/client agreement, no manual generated edits.
- [x] `W/context/StudiesContext.tsx`, `W/lib/personal-notes.ts`, picker/outline/reader files above: collect/remove/open with independent recovery, ranges, reference-only presentation and stale-input guards.
- [x] `A/tests/test_passage_references.py`, affected contract/API tests and `A/web/tests/personal-notes.spec.cjs`/`reader.spec.cjs`: execute every component matrix row on desktop/mobile; build and relevant generated/helper checks.
- [x] `A/tests/test_personal_notes_storage.py`, `A/tests/studies_owner_fixture.py`, `A/web/tests/studies-owner.integration.cjs`: prepare native compatibility/failure/race/permission and actual-owner UI+independent SQL proof for the final integration phase; do not run/use KDG ports now.
- [x] `A/docs/PASSAGE_REFERENCES_V1.md`, `A/docs/COLLECTED_PASSAGES_EVIDENCE.md`, canonical memory: truthful status, exact results and traceability.

Given dirty note input, when adding/removing/opening a collected passage, then the
same note lane/content survives. Given old study/note/title clients, when collection
support is installed, then their supported reads/commands remain compatible.

## Implementation Notes

Implemented the adopted opt-in collection slice: pinned offline66-book catalogue and
browser parity, strict source/reference DTOs, collection-specific131072-byte bound,
independent revision/receipt storage through additive0003, one collection recovery
lane per study, reusable typed/browsable picker, notes-first outline and explicit
active-pane Open with complete range endpoints/reference-only presentation. NoteValue,
legacy reader URLs, public reading and existing title/note operation lanes remain intact.

All checked tasks above refer to implementation and executed component/contract scope.
The native/actual-owner task is **preparation only** under direction266:17 native tests
collected,0 executed; actual-owner UI+independent SQL assertions prepared,not executed.
No migration, integration provider/KDG use, activation or deployment occurred. Production
and real-device/manual gates remain open. No SQL guarantee is inferred from mocks.

Scaffold/shared helper: consumed unchanged. Shared UI: app-specific picker/lane retained,
no neutral promotion. Agent context and accepted ADRs unchanged. Owner contracts and
[delivery evidence](../../apps/scribeswell/docs/COLLECTED_PASSAGES_EVIDENCE.md) updated;
canonical-memory reconciliation is maintained by the parent execution.

## Spec Change Log

-2026-10-25: Adopted contract refinement permits131072 bytes only for the200-entry
collection command; note/title/create/enrollment retain65536 and existing JSON budgets.
No frozen intent/scope change. Parent records canonical direction270.

## Review Triage Log

All three independent lenses completed before triage. Each finding is classified
separately below before grouping. Parent checked surrounding code and reproduced
B1/B2; current catalogue has zero ambiguous aliases. Native execution timing follows
explicit user direction266, overriding ordinary per-slice integration timing.

| ID | Verdict | Evidence and route |
| --- | --- | --- |
| B1 | high | Both normalizers strip U+05C0/U+05C3 punctuation: actual Python `Gen 1׃1`/`Gen 1׀1` becomes chapter11. Patch: remove pointing only and reject numeric separators, parity red/green. |
| B2 | medium | Actual `I. Samuel 2` fails despite declared book-punctuation normalization. Patch book-only punctuation without accepting decimal coordinates. |
| B3 | false | Current generated catalogue has zero colliding normalized aliases; ambiguity cannot arise from any shipped book input. Python synthetic collision test proves parser failure; no reachable picker ambiguity defect is established for this inventory. Reject; future colliding inventory requires UI qualification. |
| B4 | medium | Reference-only next/previous stop at every book boundary; adjacent declared reference books exist. Patch existing sequential arrows to follow declared catalogue bounds without changing corpus navigation semantics. |
| B5 | low | Reference-only pane calls useChapterNavigation with its unsupported corpus ID and discards its result; the hook always invokes useBook. Patch disable this unused request; verify no NT corpus calls. |
| B6 | high | New urlReference coerces explicit zero/invalid endpoints to start values through Number-or-default, then Add current can save altered reference. Patch strict present values; default only genuinely absent fields. |
| B7 | medium | openStudy/leave increment collectionNavigation before exit returns Stay, invalidating the retained study read and leaving loading state. Patch increment when departure proceeds and add gated Stay coverage. |
| B8 | medium | Remove intent retains only ID; reviewed UI cannot name the intended reference. Patch retain original reference in this existing in-memory intent and display its label. |
| B9 | medium | confirm awaits collection, then unconditionally closes/restores trigger focus even after explicit dismissal or a newer picker opening. Patch reject obsolete opening completion before close/focus. |
| B10 | medium |200-entry DTO boundary is executed but native cases use small lists; per-entry SQL under bounded deadline remains unqualified. Patch prepare maximum add/reorder plus competing note/title proof for final integration; optimize only if measured evidence requires it. No SQL performance claim now. |
| E1 | low | beforeunload includes confirmed collection attempts after read failure; users can receive an unsaved warning for confirmed success. Patch exclude confirmed attempts, matching metadata behavior. |
| E2 | low | Duplicate branch sets Already in this study but collect returns true and closes/clears editable entry. Patch return false for duplicate confirmation so existing input remains editable, without another write. |
| V1 | medium | Existing conflict test changes only injected failure, leaving revision1 and empty entries; it cannot detect stale cached review. Patch advance fixture revision/add concurrent entry and assert new base plus preserved complete list. |
| V2 | medium | Native migration/roles/races tests exist but have not executed; intercepted browser/storage doubles cannot establish these guarantees. Open gate retained for final integration per direction266; no native/release qualification or done status. This authorized timing deferral is not a pre-existing defect. |

Survivors have distinct causes and retain their own outcomes; B4/B5 may share an
edited component but remain separate fixes. No intent change or spec amendment is
needed for the direct corrections. B3 rejected; V2 remains explicit final-integration
work. B10 adds prepared proof only until that same phase.

### Review resolution and final component verification

B1/B2 are covered by52 parser cases and Python/browser accepted/rejected parity;
B4/B5 by reference-only boundary/no-corpus-request coverage; B6 by strict malformed
and genuinely absent URL-coordinate cases; B7 by pending-read/Stay; B8 by named remove
intent after concurrent deletion; B9 by gated dismissal/focus/reopen; E1 by confirmed
success versus executing/unknown unload checks; E2 by editable duplicate/no-write;
V1 by genuinely newer revision/entry review and complete subsequent replacement.
B10's maximum200-entry reorder plus competing note/title5-second-deadline test is
registered among17 native cases, **prepared only**. B3 remains rejected and V2 open.
All direct runtime corrections passed the parent final affected browser226 cases.

Per direction266 this is a reviewed component checkpoint. Status stays `in-review`
until final native/owner integration; the local preservation commit does not mark
full acceptance, activation or product completion. Further authorized slices may
build on this checkpoint while those gates remain explicit.

## Verification

- Red: missing reference module; desktop dirty-note acceptance waiting for absent Add
  passage;200 valid range entries refused by prior65536-byte cap; retained canonical
  reference could be rebound to a new ID. Focused corrections retain original expectations.
- `P -m pytest apps/scribeswell/tests/test_passage_references.py apps/scribeswell/tests/test_personal_notes_contract.py apps/scribeswell/tests/test_personal_notes_api.py apps/scribeswell/tests/test_studies_owner_integration.py apps/scribeswell/tests/test_personal_notes_release.py -q`:217 passed,1 existing TestClient warning,12.55s. Log `/tmp/scribeswell-passages-python-final.log`.
- `npm run test:browser --workspace=apps/scribeswell/web -- reader.spec.cjs personal-notes.spec.cjs --workers 1`:176 passed,2 native-only skips,4.4m. Stable browser runtime. Log `/tmp/scribeswell-passages-browser-final.log`.
- Following test-only Python portability correction, explicit `SCRIBESWELL_TEST_PYTHON`
  parity run:2 passed4.6s. Log `/tmp/scribeswell-passages-parity-portable.log`.
- Focused collection/picker/legacy responsive cases:44 passed1.1m. Log `/tmp/scribeswell-passages-focused-browser.log`.
- App build, pinned catalogue/OpenAPI/TypeScript generated checks, shared migration-helper
  check and Supabase composition dry run passed. Build retains existing chunk warning.
- Native SQL suite `--collect-only`:16 collected,0 executed. Actual-owner scenario syntax
  and fixture-control checks pass; owner UI/domain/SQL execution remains pending final phase.
- Intermediate broad run overlapped final edits:157 passed,5 failed,2 native skips;
  these were corrected and the final affected run above passed. This intermediate run
  is not claimed as frozen-source evidence. Exact failure history and matrix traceability
  are recorded in the linked delivery evidence.

`P` is `/tmp/scribeswell-manual-python/bin/python`. Reusable browser parity tests default
to `python3`, with documented `SCRIBESWELL_TEST_PYTHON` override. No KDG ports used.


Parent final frozen-source checks after review corrections:

- `SCRIBESWELL_TEST_PYTHON=/tmp/scribeswell-manual-python/bin/python npm run test:browser --workspace=apps/scribeswell/web -- reader.spec.cjs personal-notes.spec.cjs --workers=1`:226 passed,2 native-only skips,5.0m; `/tmp/scribeswell-passages-parent-browser.log`.
- Same five affected Python suites listed above:226 passed,1 existing TestClient warning,12.52s; `/tmp/scribeswell-passages-parent-python.log`.
- App build passed (existing chunk warning); catalogue/OpenAPI/pinned TypeScript client
  (`api_client_current`)/migration-helper/composition checks passed. Owner browser syntax passed.
- Native suite collection:17 collected0executed,0.67s; `/tmp/scribeswell-passages-parent-native-collection.log`.
-31 runtime/test/generated files remained byte-identical throughout final checks.
  No native/actual-owner/session integration, KDG ports, provider/config activation or deployment.
