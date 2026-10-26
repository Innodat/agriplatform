---
title: 'Finish study details and relevant own-note discovery'
type: 'feature'
created: '2026-10-26'
status: 'done'
baseline_commit: '47529be6acde6e0dd8373ee1bbf571e9d5e09e75'
route: 'dispatch'
review_loop_iteration: 0
context:
  - /home/ck/repos/innodat/agriplatform/AGENTS.md
  - /home/ck/repos/innodat/agriplatform/_bmad-output/specs/spec-scribeswell-studies/ux-behaviour.md
  - /home/ck/repos/innodat/agriplatform/_bmad-output/specs/spec-scribeswell-studies/data-and-saving.md
  - /home/ck/repos/innodat/agriplatform/_bmad-output/specs/spec-scribeswell-studies/reader-interaction.md
  - /home/ck/repos/innodat/agriplatform/apps/scribeswell/docs/OWN_COPIES_V1.md
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

Complete the remaining owner-independent study experience: optional introduction/source details and discovery of relevant own notes from the current passage. Inspect another explanation without silently changing the current highlight destination; explicitly Open when a destination change is intended. Preserve all existing writing, copies and public reading.

## Boundaries & Constraints

Always use current Access/owned-resource authority and one shared note lane. Keep whole-form Save/Cancel for study configuration and note autosave independent. Preserve all unrelated dirty changes, accepted ADRs, generated ownership and app silos. User delegates technical choices and continuous implementation without routine stops.

Never implement shared recipient/notification owners or relax visibility for sharing/private responses. No native SQL/migrations/grants, native-test collection, KDG ports55481/55482, live owner calls, deployment/push or other-app/platform edits. Actual native/owner/device/release qualification remains the final phase.

</frozen-after-approval>

## Code Map

Read the completed own-highlight and own-copy implementations before behavior. Paths: backend/personal_notes_contract.py, personal_notes_storage.py, personal_notes_search.py, personal_notes_router.py, own_copies.py; web/src/context/StudiesContext.tsx, pages/ReaderPage.tsx, components/studies/StudiesPanel.tsx and NoteEditor.tsx, lib/personal-notes.ts; studies-migrations/versions/0008 is next. All paths app-relative under apps/scribeswell/. Existing StudyView/title commands/revisions, immutable provenance and copy snapshot routines must preserve additive metadata. Existing safeNoteUrl/backend SafeUrl own URL rules; no new parser. Existing search SQL owns canonical reference overlap and guarded JSON traversal; reuse it for contextual matches. StudiesContext owns account/tab epoch, edit lanes, navigation/departure guards and pending-operation recovery. ReaderPage knows active pane/reference; NoteEditor and StudiesPanel own the existing shared tool surfaces.

## Tasks & Acceptance

- [x] Adopt app `STUDY_DETAILS_DISCOVERY_V1.md` before behavior. Plain introduction nullable max10000 Unicode scalars (retain line breaks, reject NUL for PostgreSQL compatibility), source URL nullable existing safe HTTP(S) max2048 UTF8 bytes. Add compatible create fields and StudyView defaults, forward nullable columns and server attribution. Add `study.details.replace` with operation, expected study revision and complete title/introduction/source. Existing rename updates title only. Preserve old study.create receipt fingerprints: omit absent new optional fields from canonical payload serialization, while retaining the old title/null semantics; test an old receipt replay across this additive adoption. Details replacement still binds explicit null-clearing fields. Whole-study copy retains details and counts their bytes in its existing complete-copy2MiB bound; no historical migration/generated hand edits.
- [x] Explicit whole-form details Save/Cancel, optional create fields and readable safe external source link. Reuse exact receipt/unknown identity/current lifecycle/revision protections. A stale metadata response never replaces another tab/account or unacknowledged candidate. Conflict offers deliberate current read, no silent overwrite; Cancel must not imply rollback of an unknown write. Preserve current Rename behavior/regressions and independent note autosave.
- [x] Authenticated bounded context-notes endpoint accepts one canonical PassageReference plus query/account-bound keyset cursor, default20/max50. SQL filters account, active parent/note and supported visible kind before ordering/limit/preview. Match connection/document passage link/highlight segment overlap using existing canonical reference rules; each note once. Return bounded preview, current study/owner attribution, note ID/revision/references, no inaccessible counts. No client all-notes crawl or shared visibility fallback.
- [x] Show relevant own notes in the existing Notes/context surface, tied to originating account/tab/pane/reference request identity. Late results cannot replace newer context; errors keep reading/writing usable and access loss masks private results. Pagination retains authorized items and has retry. Read-only Preview does not change current note/marks/study or edit lane; explicit Open uses existing guarded study/note navigation and preserves reader references/positions. Current unsaved lane is never labelled as server-saved. No all-note colour superimposition or accidental highlight retargeting. Explicit note Open (outline or relevant result) must reveal a relevant anchored/reference passage when none of its references is visible, using the existing navigation command and source-occurrence target; do not navigate merely when opening a study or previewing a note. Preserve existing visible relevant panes/positions and avoid a second navigation/history step. Canonical reader-interaction action transitions and UX workspace/notes clauses settle this behavior.
- [x] Runnable behavioral ATDD red before implementation, focused TDD and affected title/copy/editor/navigation/retry desktop/mobile coverage, generated/build reproducibility. Native SQL privacy/pagination/copy-metadata/migration cases authored only, uncollected/unexecuted. Retain all failures/chronology gaps, exact commands/results and relevant before/after source hashes. Parent owns independent review/checkpoint/canonical derivation.

Acceptance: create/edit/reopen/copy a study with optional details without losing title or notes; unsafe source URLs reject with recoverable candidate. Find a note from another own study by its passage, inspect it without changing current colours, and explicitly open it through the normal save guard. Account/lifecycle/reference changes cannot expose or redirect stale private results.

## Implementation Notes

Planning reread actual study create/receipt hashing, search SQL dispatch, copy snapshot and guarded navigation after own-copy checkpoint47529be6acde6e0dd8373ee1bbf571e9d5e09e75. No intent gaps remain. Footprint is additive app contract, storage, migration, generated consumers, UI and tests. No irreversible action is authorized in this phase; files only. The user explicitly delegates continuation, technical choices and cohesive remaining implementation without routine gates. Preserve the full cohesive contract despite the suggested size target. Technical limits and endpoint shape specialize existing accepted intent. App-only documentation/runtime: no scaffold/shared UI promotion, agent-context or ADR changes. No new product decision or owner service is implied. Do not stage/commit or modify canonical SPEC/companions/memlog.

## Spec Change Log

## Review Triage Log

| Finding | Verdict | Evidence | Route |
| --- | --- | --- | --- |
| B1 | false | Cross-study Open sets restoredOutline=true; existing explicit Studies/openStudies path invokes loadRestoredOutline, loads authorized first page and real continuation. The claimed permanent one-note outline is disproved by that caller. | reject |
| B2 | medium | revealNote checks every pane; inactive panes are hidden in single-pane layouts, so a matching hidden pane suppresses visible reveal. Reuse normal matching-pane activation/reveal without duplicating history or changing positions. | patch |
| B3 | medium | Preview error promises Retry Preview without a direct action; deleted rows remove the original button. Provide explicit retry for recoverable failures and truthful unavailable/close behavior for unavailable resources. | patch |
| B4 | medium | Existing focus restoration tracks only titleEdit; removing a focused details form leaves focus at body. Extend existing direct focus restoration to Edit study details. | patch |
| B5 | false | api.note is readNote, which already validates returned note.id and study_id against both requested IDs before inspect receives the result. Owner is additionally checked by inspect. | reject |
| B6 | medium | Context identity includes saved note revision; every autosave clears results, pagination and read-only preview. Preserve inspection across unrelated current-note saves while retaining account/tab/pane/reference/tool identity guards. | patch |
| B7 | high | New create fields remain editable while creation.current freezes the original unknown command; another Create displays changed values but reconciles old payload. Freeze the visible candidate during pending recovery and expose its original operation recovery. | patch |
| B8 | maybe-false | Actual realistic-volume query-plan/deadline qualification is unexecuted. Statement/total deadlines bound failure but do not establish useful performance. Final native representative-volume execution settles this; no performance readiness claim now. | defer (medium unverified) |
| B9 | false | The current user-directed slice explicitly forbids native execution and evidence declares migration/permissions/query unqualified. Running now contradicts that boundary; final execution remains mandatory and is separately tracked by V2. | reject |
| B10 | medium | Seven native cases lack details-vs-rename/delete/copy concurrency. Author bounded competing-operation assertions for coherent metadata/revision/erasure; do not run until final phase. | patch (authored coverage) |
| E1 | medium | Independently confirms hidden-pane suppression in revealNote. Same demonstrated defect as B2. | patch (B2) |
| E2 | medium | context_item validates the entire stored aggregate; a matching known-version note with an unsupported sibling block raises and aborts the whole page. Keep unsupported/malformed rows from poisoning discovery while preserving bounded server filtering and keyset reachability; no unbounded client crawl. | patch |
| V1 | medium | Filed regression gap: browser mocks record bodies but never assert reference; omitting request.reference leaves current tests green. Assert exact initial canonical reference and changed active passage request. | patch |
| V2 | medium | Filed broken-verification gap: SQL-string checks and canned browser rows do not prove PostgreSQL filtering. Existing native cases explicitly unrun; execute in final phase, never label doubles as native qualification. | defer |
| P1 | medium | Previous writer delete only clears title/active, retaining newly added details. Added forward-migration BEFORE-close clearing/closed constraint and authored old-writer case before freeze; previous migrations unchanged. | patch complete, native unrun |
| P2 | medium | Eight restoration cases failed before actions because baseline ownedNote fixture lacked already-required visibility=study. Added only that field; all eight pass with original timing/assertions. Failed runs and baseline comparison retained. | patch complete (fixture only) |

| P3 | medium | New exit guard skips abandoned lanes, but change/composition/invalid-input do not clear abandonment. After Switch anyway retains an unknown attempt and destination GET waits, the still-visible source accepts new input; the second guard then skips that newer branch and selects destination silently. Reactivate the same lane on genuinely new input, preserve frozen unknown attempt, and characterize held-result/new-input guard. Parent310/44/18 checks precede this correction. | patch |

| P3 correction | false | Parent initial tracing missed editorLanes filtering !abandoned and NoteEditor rendering only that list. Switch anyway unmounts source editor before a user can type while destination GET waits; no reachable normal UI reproduction exists. No synthetic same-event manufacture or speculative runtime guard. Original parent310/44/18 source hashes remain identical; prior row retained as chronology, this refutation supersedes it. | reject |

## Verification

Observe behavioral red, then explicit application-only pytest node IDs excluding native-containing suites; use prepared isolated Python. Hermetic Playwright/local Vite/Chromium requires normal sandbox escalation. Run only new/affected component cases now; final broader integration remains at end. Build affected workspace, owning OpenAPI/client/database-helper/catalogue checks where affected; no root verification claim. Retain unexplained historical anonymous mobile-scroll and startup/restoration failures with original assertions.

Parent independent verification:310application tests3.17s;44affected browser55.8s and18review regressions23.5s on191unchanged before/after/current selected hashes. Build/OpenAPI/catalogue/pinnedDTO/database-helper checks pass. Native12parameterized cases authored only, no collection/SQL; final owner/device/release/registration gates remain. See STUDY_DETAILS_DISCOVERY_EVIDENCE.md and parent result/source JSON/logs.

Final2normal-UI R8 characterization cases passed3.9s. Only the new test suffix differs from parent310/44/18 state; prior test prefix and all190other selected hashes match. parent-refutation snapshots record the distinct test-only final state.
