---
title: 'Insert and follow passage links inside personal notes safely'
type: 'feature'
created: '2026-10-25'
status: 'in-review'
baseline_commit: '2a383ffcb5c7e75645cf3c2bc1dab0d30ab8f7ae'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/apps/scribeswell/docs/NOTE_REFERENCES_V1.md'
  - '{project-root}/apps/scribeswell/docs/PASSAGE_REFERENCES_V1.md'
  - '{project-root}/apps/scribeswell/docs/PERSONAL_NOTES_V1.md'
  - '{project-root}/platform/docs/development/migration-verification.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Readers cannot deliberately insert a passage reference into their explanation and revisit it without collecting or quoting scripture.

**Approach:** Extend the existing note grammar/editor with safe canonical passage links, preserve one save lane, and implement the agreed reading/editing navigation distinction in the same Notes tab.

## Boundaries & Constraints

**Always:** Preserve ordinary v1 notes, source links, independent collection/title/note lanes, current owner HTTP authority, actor/UTC/revision/lifecycle/receipt safety and dirty/concurrent work. Use ATDD/TDD; integration stays at the final phase under direction266. Protect prior editors from erasing unsupported rich documents.

**Never:** Quote scripture, auto-collect/paint, implement highlights/sharing/owner competitors/Leave/factory, rewrite applied migrations or activate/deploy/change providers. No private note payloads in browser storage/logs/URLs; no silent downgrade/truncation or persistence/rollback promise. Broader accepted requirements remain.

## I/O & Edge-Case Matrix

| Given / when | Then |
| --- | --- |
| Insert valid English/Hebrew chapter/range/Matthew at a note caret | One safe link and version2; surrounding writing remains, no quotation/collection/highlight or reader movement. |
| Cancel, invalid bounds, IME or stale account/note/input selection | No wrong-context insertion; editable input and useful writing/focus remain. |
| Read/Edit, click link, explicit Open | Same lane/input; reading opens directly, editing positions caret and offers Open; active reader only, full range/current note/other pane preserved. |
| Bold/list/direction, paste, deletion or save/reload | Closed safe roundtrip, label/identity intact; deleting final link retains format2, ordinary notes stay1. |
| Malformed/foreign/versioned/oversized link or unknown node | Safe typed refusal/unsaved input, no effect/truncation or sensitive diagnostics. |
| Older v1 writer submits current revision for rich v2 |409 format refusal before mutation/receipt; existing committed v1 replay acknowledges history without overwriting current content. |
| Delayed/unknown save, conflict or account/navigation response | Existing frozen original-operation/generation/authority guards preserve coherent whole-note value and truthful feedback. |
| Prior consumer and final integration | Ordinary compatibility stays; genuine old-format refusal is isolated from live DTOs. Native/owner proof prepared, unexecuted until final phase. |

</frozen-after-approval>

## Code Map

`A=apps/scribeswell`, `B=A/backend`, `W=A/web/src`. Adopted NOTE_REFERENCES_V1.md
owns exact format2, transition, UI and release rules. `B/personal_notes_contract.py`
owns closed DTO/budgets/generated wire; `B/personal_notes_storage.py::execute` has
locked current note and receipt replay. Preserve existing `view` refusal plus explicit
format fence when widening. `W/components/studies/NoteEditor.tsx` owns safe DOM and
currently emits only1; StudiesPanel preview assumes link.content. Reuse BookChapterSelector,
StudiesContext note lane and ReaderPage range/active-pane controller. Existing frozen
`A/tests/fixtures/personal_notes_storage_previous.py` imports live DTOs: preserve its
bytes and add isolated true baseline-format evidence rather than trusting that import.

## Tasks & Acceptance

- [x] `B/personal_notes_contract.py`, `B/personal_notes_access.py`, `B/personal_notes_storage.py`: test-first exact format2/link models and locked anti-downgrade409; preserve v1 fingerprints/no-op/replay.
- [x] `A/tools/py/export_personal_notes_contract.py`, owned OpenAPI/TS outputs: regenerate/check, no manual generated edits.
- [x] `W/components/studies/NoteEditor.tsx`, StudiesPanel preview, `W/context/StudiesContext.tsx`, `W/pages/ReaderPage.tsx`: insertion, safe atomic DOM, minimal Read/Edit, terminal format refusal and existing explicit navigation; one lane/current note.
- [x] `A/tests/test_personal_notes_contract.py`, focused format/API/storage-method tests, `A/web/tests/personal-notes.spec.cjs`: observe acceptance red, execute all component rows on desktop/mobile, build/generated checks.
- [x] `A/tests/fixtures/`, `A/tests/test_personal_notes_storage.py`, `A/tests/studies_owner_fixture.py`, `A/web/tests/studies-owner.integration.cjs`: prepare isolated baseline contract/storage, native downgrade/replay and actual-owner UI+SQL proof; no integration/ports now.
- [x] `A/docs/NOTE_REFERENCES_V1.md`, `A/docs/PERSONAL_NOTES_V1.md`, `A/docs/NOTE_REFERENCES_EVIDENCE.md`, canonical memory: exact status/traceability, compatibility activation prerequisite and scaffold/UI/context/docs/ADR impacts.

Given an ordinary untouched note, when the new editor reads/saves it, then its version1
representation and original-operation semantics remain unchanged. Given a v2 note,
when a link is removed or ordinary text edited, then unsupported older writers cannot
erase its richer format through a downgrade.

## Implementation Notes

- Added exact DocumentV2/PassageLink alongside unchanged ordinary DocumentV1;
  inherited budgets count stored labels and nested reference models. Command,
  receipt and v1 fingerprint serialization remain unchanged. Locked replacement
  validates current lifecycle/revision then refuses format2→1 with safe409 before
  mutation/receipt; original committed v1 replay stays on the existing receipt path.
- Generated OpenAPI and pinned TypeScript through their owning tools. No generated
  file was hand-edited and no migration was added.
- Editor-owned WeakMap atoms hold validated reference identity and safe label text.
  Picker capture guards account/lane/input/range; selected writing is retained,
  IME refuses insertion, per-note picker input survives correction/reopen, and note
  or account replacement clears it. Source-anchor insertion splits safe URL/marked
  text without nesting links; a caret inside an owned atom resolves after it.
- Read/Edit retains one DOM/lane and truthful saving status. Editing click/keyboard
  offers Open; reading activation delegates full-range active-pane navigation.
  Mobile navigation reveals the reader while keeping the same Notes context.
  Terminal format refusal pauses autosave and retains input with Reload wording.
- Preserved historical previous-storage fixture bytes. Added exact baseline
  contract/storage snapshots at2a383ffcb5c7e75645cf3c2bc1dab0d30ab8f7ae with hashes
  and an isolated loader. Native downgrade/replay/actual prior refusal and actual-owner
  UI+independent SQL checkpoints are prepared only under direction266.
- Impacts: application-specific editor/navigation/contract; no shared UI/scaffold
  promotion, agent-context change or accepted ADR change. Existing migration helper
  reused unchanged. App contracts and NOTE_REFERENCES_EVIDENCE.md updated; canonical
  memory reconciled separately by the parent delivery workflow. Production disabled.

## Spec Change Log

## Review Triage Log

| Finding | Verdict | Evidence and route |
| --- | --- | --- |
| B1 no-caret final position | medium | `querySelectorAll('p')` chooses an earlier paragraph despite supported trailing DIV/text. Direct final-document-position correction and acceptance: patch. |
| B2 interrupted composition | medium | Explicit Switch anyway can replace a composing lane without compositionend; component ref remains true while replacement lane is false. Synchronize the ref on lane replacement, preserving old lane protection: patch. |
| B3 native Undo | high | Raw Range insertion/extractContents bypasses native history. Independent Chromium reproduction shows Undo deletes surrounding typed text while retaining the new link; saved data can lose writing. Correct the existing insertion transaction and prove Undo/Redo, without a new public surface: patch. |
| B4 external link wraps atom | medium | Existing createLink accepts a selection crossing owned atoms, while parser rejects passage atoms under A. Refuse the demonstrated invalid selection before mutation, keeping input/candidate: patch. |
| B5 over-limit insertion reports success | medium | changed() swallows read failure; insertion still clears feedback and returns true. Directly propagate validation refusal and preserve pre-insertion writing/selection; boundary acceptance: patch. |
| B6 retained picker book | low | begin() retains valid text but unconditionally resets hovered to Gen; text effect does not rerun. Use retained candidate book on reopen: direct patch. |
| B7 inaccessible rejection feedback | medium | Dynamic feedback/error are ordinary paragraphs with no input relationship or live announcement. Add associated announced feedback to existing input: patch. |
| B8 formatting across atoms coverage | medium | Original browser matrix never formatted across an existing owned atom. New corrected acceptance proves Bold/Italic pass while Bullet/Numbered list fail on both viewports (4pass/4fail), confirming native reconstruction loses WeakMap binding. Direct transaction ownership correction plus save/reload acceptance: patch. |
| B9 other-note owner oracle | medium | New before/after SQL oracle extracts only target note; does not prove other notes unchanged. Add equality assertion for non-target rows and focused oracle negative test; integration remains prepared: patch. |
| B10 transient detailed logs | false | Repository-owned evidence already preserves commands, counts, chronology, limitations and baseline; source/tests remain version-controlled. /tmp logs are supplementary local diagnostic references, not the sole qualification record or claimed durable CI artifacts. No required artifact store exists for this bounded component delivery; rejected. |
| E1 Undo boundary | high | Same raw-DOM history defect as B3, with independent Chromium reproduction of surrounding-writing loss. Group with B3 only after this individual verdict: patch. |
| E2 composing replacement | medium | Same reachable explicit-switch path and stale component ref as B2; replacement lane itself is false. Group with B2: patch. |
| E3 trailing document position | medium | Same supported DIV/text tail versus last-P mismatch as B1. Group with B1: patch. |
| V1 preview label coverage | medium | Preverified regression gap: Notes-list selection never asserts link-only summary text, so dropping passage labels escapes tests. Direct browser assertion before opening: patch. |
| V2 custom stored label coverage | medium | Preverified regression gap: only canonical generated labels exercise browser draw/read; DTO custom-label test cannot detect normalization in DOM. Add exact mixed-Unicode/HTML-looking label display/read/edit roundtrip: patch. |

| P1 post-patch atomic Backspace | medium | Parent complete frozen312-case regression passed310 and failed both existing desktop/mobile Backspace removal expectations after the native caret change. Same implementation worker reengaged for native-history-compatible one-step deletion, retaining the unchanged expectation and new caret behavior; patch pending. |

Survivors group only B1/E3, B2/E2 and B3/E1 by identical root causes. All fixes correct existing behavior or add focused assertions; no intent gap/new public capability, owner implementation or integration execution is needed. B10 is specifically refuted rather than grouped away. Final native/owner/session qualification remains pending by direction266.

## Verification

Final component qualification: **324 desktop/mobile browser checks passed8.0min**
against frozen source; **249 affected Python passed11.67s**, one existing framework
warning. App TypeScript/Vite build, catalogue/OpenAPI/pinned TS (`api_client_current`),
shared helper, composition dry-run and prepared owner syntax pass.116runtime/test
hashes unchanged.18native cases collected only, none executed. Exact commands,
chronology, earlier failures and traceability: `apps/scribeswell/docs/NOTE_REFERENCES_EVIDENCE.md`.

Review completion: all14 patch rows addressed; B10false specifically refuted. B1/E3,
B2/E2 and B3/E1 alone share root causes. V1/V2 add coverage for already-correct behavior;
B8 proves/fixes list reconstruction; B9 strengthens prepared SQL oracle with5negative
cases. Parent P1 correction preserves original one-step deletion and native history;
first full310/312 failed, targeted28 passed, final full324 passed. No expectation
changed to suppress a runtime failure.

Keep `in-review`: native restricted SQL, actual-owner/session/provider, coordinated
read-aware previous-release adoption, physical devices and production remain pending.
A local scoped component preservation checkpoint enables the next authorized slice;
it is not BMAD step05 full acceptance. No integration/shared ports or activation.
