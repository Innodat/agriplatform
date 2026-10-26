---
title: 'Capture and preserve current-note highlights in the reader'
type: 'feature'
created: '2026-10-26'
status: 'in-review'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'faac78ee0da3009ac7b69ca6423a2b74a6139b27'
context:
  - /home/ck/repos/innodat/agriplatform/AGENTS.md
  - /home/ck/repos/innodat/agriplatform/_bmad-output/specs/spec-scribeswell-studies/ux-behaviour.md
  - /home/ck/repos/innodat/agriplatform/_bmad-output/specs/spec-scribeswell-studies/data-and-saving.md
  - /home/ck/repos/innodat/agriplatform/apps/scribeswell/docs/HIGHLIGHT_EVIDENCE_CONTRACT.md
  - /home/ck/repos/innodat/agriplatform/platform/docs/development/migration-verification.md
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

Deliver the agreed own-note highlight journey end to end in the existing opt-in: select an exact phrase, choose a freely coloured mark for the visibly current note, preserve it alongside writing, and revisit its correctly validated occurrence across passages/tabs. Close the concrete application contracts before implementation. Include coherent reader proof, atomic aggregate admission/preservation and selection UI in one delivery so text edits cannot erase marks.

## Boundaries & Constraints

**Always:** Preserve public reading during protected proof outages, standalone account entry, existing analysis/navigation and one shared note lane across tabs. Consume current Access admission without implementing its owner. New/repaired anchors require actual current server observation before private write locks. Retain exact prior anchors during proof outages; colour/removal is independent of corpus availability. No partial aggregate saves, silent retargeting, quotation or invented reference-only scripture. Preserve all unrelated working-tree changes. User explicitly delegates routine technical decisions and asks continuous implementation without approval stops.

**Never:** Execute native SQL/migrations, provision privileges, enable enforcement, use KDG ports55481/55482, call live Auth/Identity/Access, deploy/push or change Leave/PtS/factory. Do not change accepted ADRs, historical migrations or generated files manually. Actual native/owner/device/release qualification remains the final phase. Sharing/recipient/Notification owner work and independent copies are subsequent work, not permission to build competing services.

</frozen-after-approval>

## Code Map

- `backend/database.py`: pool/contextvar repository. Add bounded read-only repeatable snapshot; existing autocommit independent reads cannot prove correspondence. `services/bible_service.py::get_verses`, `schemas/bible_schemas.py`, frontend Bible schemas consume complete words. Legacy numeric IDs cannot become anchors via JavaScript conversion.
- `backend/highlight_evidence.py` already compares exact full-verse token evidence/positions and tolerates regenerated IDs only for unchanged tokens. `passage_references.py` is canonical catalogue authority. `corpus_publish.py` and forward0004 provide immutable publication; no browser-ready adapter yet.
- `migrations/versions/`: add narrowly scoped reader-evidence forward migration/routine; metadata remains private. Extend explicit versioned profile/runner revision handling while pinning historical targets. No new full catalogue whitelist/reference snapshot.
- `personal_notes_contract.py`: current NoteValue requires empty arrays; document versions1/2 stay exact. `personal_notes_storage.py` writes whole JSON under parent/note lock, fingerprints operations and protects doc2 downgrades. `personal_notes_router.py` performs fresh Access before storage. New source observation must finish before write locks, preserving original-operation replay during proof outage.
- `studies-migrations/versions/` currently ends0005. New private forward migration may add immutable per-owner/note/revision validated metadata (no historical note bodies), forced owner RLS and composite scope constraints. Keep separate public/private restricted DB credentials.
- `web/src/components/studies/NoteEditor.tsx::draw/read` rejects nonempty arrays and returns empty arrays: evolve all draw/read/mutation paths together. `lib/note-value.ts` guards response renderability; generated DTO/export tools must evolve with backend. `context/StudiesContext.tsx` owns shared lanes/change/flush/openNote/create and lane.invalid/composing/deletion guards.
- `components/bible/VerseReader.tsx`, `pages/ReaderPage.tsx`, workspace context/hooks: retain originating tab/pane/reference/navigation and ordinary analysis. Public restore/history controls already work. `personal_notes_search.py` and outline reference derivation currently only inspect structured passage links; include connections/anchor references, deduplicating notes.

## Tasks & Acceptance

- [x] `docs/OWN_HIGHLIGHTS_V1.md`: record exact compatible wire, limits, errors, freshness, aggregate/base metadata and interaction choices before runtime behavior. This app contract specializes adopted UX/data intent; no duplicate feature lifecycle.
- [x] Public snapshot/reader adapter and forward migration/profile: additive `anchor_evidence` discriminated ready/unavailable per verse, with canonical single-verse reference, source/revision/labels/digest and full ordered decimal-string observed IDs. Verify same-snapshot actual words with `observe_verse`. Unsupported catalogue/versification, stale pointer or missing function/schema produces unavailable proof while valid text renders. Isolate optional SQL failures in savepoint. One bounded read-only repeatable snapshot covers books/verses/words/publication; no autocommit fallback certifying proof. New narrow definer read routine returns no private publication/operator tables, and default privileges stay restricted. Preserve old profiles' pinned targets.
- [x] Aggregate DTO/storage/generated consumers: exact legacy NoteValue remains accepted; additive explicit format_version3 aggregate carries connections/highlights with document1/2. Strict unique UUIDs, uppercase canonical #RRGGBB, bounded canonical anchors. Anchor version1 binds source/revision/catalogue/versification/tokenization and ordered continuous single-book segments; each carries canonical single-verse reference, inclusive positions, selected decimal IDs and full-verse digest. All intermediate verse/position continuity must validate. Set bounded64 highlights/128 connections/128 total segments/4096 selected IDs and coherent262144-byte/32768-node whole-note budget; reject, never truncate. Old-format replacement cannot erase stored format3 even after all marks removed. Document2 downgrade fence remains.
- [x] Admission/preservation and base metadata: new/changed anchor identity requires current exact proof including IDs, not browser hash or highlight ID alone. Do fresh source reads outside private write locks, then current ownership/revision/lifecycle/aggregate validation atomically under existing locks. Same committed operation retries still reconcile without requiring a new source observation. Unchanged anchors, recolouring, removal and writing round-trip using trusted current/base metadata during proof outage. Atomically record immutable validated anchor/reference metadata per note revision, no historical body; stale base cannot resurrect deleted records. New errors use stable typed safe contracts and generated clients.
- [x] UI/editor/shared lane: every document edit retains latest valid connections/highlights; unsupported/composing/deleting lanes cannot be silently cleared by a mark action. Current note marks only, across its connected passages without requiring collection. Palette names destination with Change; choose/create own note explicitly once if absent. Selection toolbar/context menu exposes Highlight, Add note and Add to study with distinct behavior; Add note creates own connected observation/editor, Add to study collects containing verses. Never quote selected text. Recolour/remove and deliberate reselect repair preserve writing. Read status valid/needs_review/unavailable without changing note revision or painting uncertain marks.
- [x] Selection/origin/navigation: continuous drag and Shift-click on desktop; native long-press/OS copy on touch remain. Prevent cross-pane selection and stale account/tab/pane/navigation/source/note destination actions. Ordinary click inspection never changes current note. Clicking a current mark opens its note. Mobile bottom actions/palette/full-width Notes preserve reader passage/position. Lexical hover/selected styling cannot erase own colours; deterministic overlap presentation without invented colour semantics.
- [x] Search/outline derive passage context from connections, structured links and segments, one note once; removing collected passages leaves notes/marks.
- [ ] Acceptance behavioral red first, focused TDD, old-format/whole-note preservation/regression tests, desktop/mobile browser selection/save/reopen/stale-origin/needs-review/outage cases. Author native permissions/snapshot/races/rollback/upgrade/old-writer cases but do not execute or collect them. Record exact commands/failures/source fingerprints and limitations; parent owns final review/checkpoint/canonical derivation.

Acceptance: a selected ready phrase can be saved/reopened as a freely coloured mark of the chosen current note; later writing/link/colour/tab changes never drop other aggregate fields. New false/unavailable proof rejects the whole aggregate with recoverable input, while unchanged anchors remain editable. Source correction suppresses uncertain paint and offers explicit repair; matching current exact verse may render after regenerated IDs without rewriting history. Anonymous public reader/analysis works with no publication. Existing save/retry/revision/deletion/session protections continue to pass.

## Implementation Notes

No human intent gaps identified: UX is already agreed; technical choices above are delegated. Files/migrations are reversible authored changes only; no database action is authorized in this phase. The cohesive cross-layer footprint exceeds the template token target; keeping it together follows the user's explicit continuous implementation direction and avoids unsafe independently enabled partial consumers. Do not stage/commit, modify canonical SPEC companions/memlog, or claim final integration. Hermetic FastAPI TestClient needs execution outside the restrictive sandbox in this environment; preserve assertions and skip live DB startup only via an explicitly reported fixture harness, never a production bypass.

## Spec Change Log

## Review Triage Log

| Finding | Verdict | Evidence | Route |
| --- | --- | --- | --- |
| B1 | high | Definitive highlight_proof_unavailable clears no attempt; removal changes lane.value but flush retries the rejected frozen payload. Retire only this definitely uncommitted attempt; preserve unknown-outcome identities. | patch |
| B2 | medium | Map deduplication takes the last visible segment, hiding earlier needs_review and its repair action. Aggregate the worst visible state. | patch |
| B3 | high | Repair ID survives selection dismissal and origin navigation; later Add can replace an unintended existing mark. Clear repair when that workflow ends. | patch |
| B4 | medium | Colour/remove ignore false from mark during demonstrated composing/invalid/deleting states, giving silent failure. Disable or report rejection using existing lane state. | patch |
| B5 | medium | Readability caps only serialized value; command operation/revision wrapper can exceed the same server byte limit. Check the actual bounded command envelope before accepting mark mutations. | patch |
| B6 | medium | Every mark appends permanent connections although anchors already provide passage discovery; repeated add/remove fills128 slots. Remove redundant implicit connection insertion while retaining explicit Add-note connections and existing saved connections. | patch |
| B7 | medium | Mouse completion leaves ignoreNative true until pointer-down/dismiss, so keyboard native selection is ignored. Bound suppression to the drag-generated event. | patch |
| B8 | medium | Keyboard Enter/Space calls click without shiftKey; existing range endpoint intent is lost. Preserve Shift in the existing keyboard activation. | patch |
| B9 | medium | Chooser lists only loaded notes despite existing notesCursor/moreNotes; expose the existing pagination action. | patch |
| B10 | false | Actual native qualification is explicitly deferred by frozen user-directed constraints and evidence; no SQL qualification claim is made. Retain the final-phase gate rather than execute forbidden SQL now. | reject |
| E1 | medium | Same independently verified last-segment classification defect as B2. | patch (B2) |
| E2 | high | Account-dependent effect recaptures an existing phrase for a replacement account while VerseReader clears only origin/tab. Clear phrase on account replacement. | patch |
| E3 | high | Same independently verified retained repair target defect as B3. | patch (B3) |
| V1 | medium | Filed regression gap: initial colour and repair coverage do not exercise existing-mark recolour control. Add rendered/saved/reopened colour assertions retaining ID, anchor and writing. | patch |

## Verification

Start with a runnable behavior assertion failing for the missing feature, not a missing-module collection error. Use `/tmp/scribeswell-implementation-python/bin/python -m pytest -q` with explicit application-side node IDs only, avoiding native fixture collection. Browser: `SCRIBESWELL_TEST_PYTHON=/tmp/scribeswell-implementation-python/bin/python npm run test:browser --workspace=apps/scribeswell/web -- --workers=4 --fully-parallel ...` with hermetic mocks/local Vite; request normal sandbox escalation for local sockets/Chromium where needed. Build the affected workspace and run owning DTO/catalogue generators' reproducibility checks. Characterize risky editor/refactoring before changing it. Do not weaken an unexplained failing expectation. Retain the prior anonymous mobile-scroll regression as unverified; target relevant regressions first, broad final integration at end. Parent performs independent BMAD review and final affected-source freeze.

## Parent audit status

All14 independent review findings have individual rows above. Twelve distinct entries remain after grouping duplicates E1/B2 and E3/B3; eleven require corrections and B10 is rejected under the explicit final-phase constraint. Original implementer corrected the surviving roots; parent actual-source audit confirms the changes. Review focused20 desktop/mobile cases passed3.0min; earlier10pass2mobile startup/return failures remain unproven and retained. Parent corrected-source application/pure-evidence276tests passed16.31s (runner19.03s). Final affected-source browser/build/generation checks remain running. Native tests remain authored/uncollected/unexecuted. The final task stays unchecked because complete pre-refactor characterization and all inner-loop red chronology cannot be retroactively supplied; the process gaps and final integration gates remain explicit.


Parent final:276 application/pure-evidence tests16.31s,54 desktop/mobile affected
cases5.3min,2 hermetic reader cases, build/OpenAPI/catalogue/pinned-client checks
passed. All41 selected before/after/current hashes match. Exact commands and logs
are in OWN_HIGHLIGHTS_EVIDENCE.md and parent-results.json. All11 distinct review
correction entries addressed; B10 rejected under final-phase constraint. No native,
owner, physical-device or release claim. Status remains in-review for those explicit
final gates and disclosed historical characterization/red-chronology gaps. Proceed
directly into authorized own-copy/conflict-recovery implementation.
