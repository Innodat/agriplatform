---
title: 'Recover conflicting writing and make independent own copies'
type: 'feature'
created: '2026-10-26'
status: 'done'
baseline_commit: '5c5d095f8da3da0b92432b59eaf5efba30153e27'
route: 'dispatch'
review_loop_iteration: 0
context:
  - /home/ck/repos/innodat/agriplatform/AGENTS.md
  - /home/ck/repos/innodat/agriplatform/_bmad-output/specs/spec-scribeswell-studies/ux-behaviour.md
  - /home/ck/repos/innodat/agriplatform/_bmad-output/specs/spec-scribeswell-studies/data-and-saving.md
  - /home/ck/repos/innodat/agriplatform/apps/scribeswell/docs/OWN_HIGHLIGHTS_V1.md
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

Complete own-note conflict recovery and independent copying: Review latest without losing the local branch; explicitly Use latest or Save mine as a new note; Duplicate own note into the same study; make a complete independent copy of an own study. Preserve text, connections, every highlight colour, private visibility and minimal source credit without synchronizing originals and copies.

## Boundaries & Constraints

**Always:** Current account Access/ownership and active parent/note lifecycle; atomic coherent whole aggregates and exact original-operation retry; one shared edit lane across tabs; trusted base evidence for unchanged historical anchors, fresh proof for new/repaired ones. Preserve unsaved input and unrelated dirty files. User requests continuous implementation without routine approval checkpoints.

**Never:** Call live owner services, execute/collect native SQL tests, apply migrations/grants, touch KDG ports55481/55482, deploy/push, change other apps/platform owners or accepted ADRs. Sharing/recipient/Notification consumers are owner-gated. No automatic merge/overwrite, copying another account's private work, privacy broadening, source FK/cascade, cached inaccessible teacher body/title/email, partial-copy success or old source resurrection.

</frozen-after-approval>

## Code Map

- `personal_notes_contract.py`, router/storage/access and generated app DTOs: existing bounded commands, receipts/fingerprints, current Access before local transactions, parent/note locks, attribution, revision/deletion protections.
- `own_highlights.py`, `reader_evidence.py`, `note_revision_metadata` from studies0006: exact anchor admission and immutable owner/note/revision metadata without body history. Reuse these; do not accept browser-claimed base proof.
- `context/StudiesContext.tsx` Lane/flush/exit/create/epoch/navigation; `components/studies/NoteEditor.tsx` current conflict notice and `SavedNoteReview` patterns; `StudiesPanel.tsx` actions; existing whole-note editor and tool/restoration protections. Avoid a second edit lane.
- `studies-migrations/versions/` next additive revision, owning sync generator and OpenAPI exporter/client generator. No historical migration/generated hand edits. Prepared Node26/pinned generator can be reused from `/tmp/scribeswell-codegen-isolated` with normal sandbox escalation for bounded local children.

Current implementation facts: checkpoint5c5d095f includes highlight source bc821997. `note_revision_metadata` is recorded for every new/replaced note revision, including legacy values; pre-migration rich bases cannot be invented. Current schema permits only immutable `visibility=study`; this slice must fail closed for unsupported kinds rather than broaden visibility or introduce private-response creation. Anchor references already supply context; copying must not add redundant connections. Definitive proof errors retire failed attempts, unknown outcomes retain theirs. Reuse the actual source checks and noteCommandFits framing.

Compatibility finding during parent read-only audit: a contract-valid260028-byte aggregate command yields5199330 JSON characters for20 note values; browser `personal-notes.ts::request` still rejects responses above4000000 characters. This prevents loading a full default note page permitted by the highlight contract. Preserve the declared max50-note/262144-byte-value read range by correcting the bounded response limit (e.g.50*262144 plus bounded envelope/attribution allowance), rather than reducing note budgets or pretending a partial page is complete. Add a meaningful API adapter test with20 large valid notes and a bound-overflow refusal; no source DB/native action is required.

## Tasks & Acceptance

- [x] Adopt `docs/OWN_COPIES_V1.md` before behavior: exact commands/errors/provenance, coherent copy bounds and privacy. Add `note.duplicate`, `note.conflict_copy`, `study.copy` DTO/router/receipt/lookup variants with safe generated clients. Duplicate payload is operation ID plus expected source note revision; own destination is same study. Conflict-copy adds original base revision and complete local value. Study copy takes expected study revision and creates a new private own study retaining the exact title (ordinary duplicate titles are allowed).
- [x] Server-derived immutable provenance with destination composite ownership, immediate source and bounded original-origin account/study/note IDs, relation and server actor/UTC attribution. No source foreign key, title/body/email cache or unbounded chain. Copy-of-copy preserves original credit. Presentation resolves source labels only with current authorized source reads; otherwise Original unavailable. Preserve visibility; closed own response visibility may be structurally supported without introducing a response creation/sharing route. Unsupported source kinds must fail closed rather than become ordinary notes.
- [x] Backend duplicate/copy: receipt reconciliation first, then current active source/destination under deterministic parent lock order and bounded coherent snapshot. Allocate new note/connection/highlight/passage entry identities, retain exact aggregate fields/anchor provenance/colour and independent attribution. Trusted server source anchors can be cloned without requiring fresh corpus availability; no historical ID rewriting. Whole-study copy includes all currently visible active own notes and ordered collected passages, at most128 notes/200 passages/2MiB canonical aggregate bytes; refuse the entire copy with safe copy_limit_exceeded when exceeded. Never treat one fetched page as a complete study. Every note, metadata record, provenance and receipt commits or rolls back together.
- [x] Conflict fork: original owned source must still be active; look up immutable metadata for the requested base revision, never fetch an old body or assign the current server revision to a stale branch. Validate exact original highlight ID/anchor against that base; genuinely new/repaired anchors require fresh actual observation before private write locks. Recheck lifecycle/current authority under locks; allocate new IDs only after branch validation and preserve private kind/provenance. Missing required rich base returns safe note_base_unavailable, retaining input. Legacy branches with no historical anchors need no invented body history; canonical references and current immutable source ownership still validate. Existing metadata from source revision cannot revive deleted records.
- [x] UI conflict workflow: Review latest reads authorized full current aggregate separately; local writing/colours remain untouched. Use latest explicitly replaces the shared lane. Save mine freezes one complete local branch/base/operation and opens its acknowledged new note; unknown outcome retains original identity and blocks another effect. Unsupported/composing DOM cannot silently copy the last-valid value. New edits or account/tab/navigation changes cannot be falsely marked saved or receive a stale automatic selection. Duplicate first confirms pending own source writes; whole-study copy confirms all its pending note lanes. Unresolved/invalid/conflicting lanes are recoverable and never quietly omitted. Reuse existing pending-creation/Open-created recovery for changed origins. No automatic copy after reauthentication.
- [x] Explicit Duplicate note/Copy study actions preserve reader positions and open editable/current own results. Changing either copy never changes its source. Source loss never deletes an existing independent destination; original acknowledged retry validates that destination rather than requiring live source again. Copy/remove/unknown/revision/deletion/session paths remain safe across every tab.
- [x] Runnable behavioral ATDD red first, focused TDD and affected editor/retry/whole-aggregate browser regressions, generated/build checks. Author restricted native concurrency/rollback/receipt/base/privacy/previous-history cases but do not collect/run them. Exact evidence/fingerprints and all failures retained; parent owns final review/checkpoint/canonical updates.

**Acceptance criteria:**
- Given a stale editor, when Review latest is selected, then the local complete branch remains unchanged; Use latest explicitly replaces it, while Save mine creates one independent note without overwriting the newer original.
- Given an active own note with writing/references/colours, when Duplicate succeeds, then new identities preserve all content in the same study and editing either note leaves the other unchanged.
- Given an own study within128notes/200passages/2MiB, when Copy succeeds, then its complete coherent content and minimal credit exist under a new own study; over-limit copies fail atomically.
- Given a lost command acknowledgement, when the original operation is retried, then one effect is reconciled; later source deletion does not erase an independently owned destination or require source resurrection.
- Given composition/invalid or unresolved source writing, when copy is requested, then input remains recoverable and no partial or privacy-broadened copy is reported.

## Implementation Notes

Own-highlight checkpoint and parent final verification are complete; planning has reread actual metadata, mutation and receipt code. No intent gaps remain. Authored forward migrations are reversible files only; actual database application is forbidden in this phase. Cohesive copy/conflict functionality spans contracts, storage, migration, generated consumers, shared editor and browser tests; user explicitly authorizes continuous implementation and keeping the cohesive full spec despite the template size target. Product intent is settled by ST19/ST28; copy bounds and minimal opaque credit are delegated app choices. No database action or new shared owner capability is implied. Scaffold/shared UI/agent-context/ADR: no promotion or rule/decision change; app contract/evidence document this app-specific extension. Preserve frozen intent; do not stage/commit or modify canonical SPEC companions/memlog. Native/owner/device/release integration remains final phase.

## Spec Change Log

## Review Triage Log

| Finding | Verdict | Evidence | Route |
| --- | --- | --- | --- |
| B1 | false | A user selecting another note increments this tab navigation; switching tabs changes originKey, and editing the source changes generation. All are rechecked before/after result read, preventing the claimed overwrite of another edited note. Whole-study result uses guarded openStudy. Distinct source-deletion/tool races are E1/P1. | reject |
| B2 | high | Successful fork selects the destination but never retires the original captured branch. beforeunload scans every lane and still reports that unchanged no-longer-referenced branch unsaved. Retire it only after acknowledged fork and only when no other context/new input still needs it; never call the original note saved. | patch |
| B3 | medium | study_revision_conflict retires the attempt but leaves study.revision unchanged. Another Copy click repeats that stale expected revision; current Retry loads library rows without refreshing selected metadata. Refresh authorized current source metadata under origin/input guards before a subsequent explicit copy. | patch |
| B4 | medium | readableNote checks the aggregate but never copy_credit; an object label reaches React. New study credit is likewise displayed from unchecked API data. Guard the new optional credit shape before attachment without expanding validation of unrelated preexisting fields. | patch |
| B5 | medium | response.text allocates before checking length; this exact read-then-check behavior predates copies and highlights. Current change corrects valid page allowance, not streaming. Record existing bounded-reader improvement separately; no claim of a streaming memory cap. | defer |
| B6 | medium | New provenance tables allow source/origin accounts different from account_id through alternate INSERT despite current own-only command semantics. Add same-account structural checks; future cross-owner copy adoption would need its explicit compatible migration. | patch |
| B7 | false | Frozen user-directed phase forbids executing/collecting native suites now, and evidence explicitly leaves SQL unqualified. Existing native assertions remain reserved for final qualification, rather than running contrary to current authorization boundary. | reject |
| B8 | medium | Authored native race covers source deletion but not create/replace/passages writers against coherent whole-study copy. Add focused parameterized concurrency assertions, authored only until final phase. | patch |
| B9 | medium | Interrupted matrix retains67pass4fail2interrupted29unrun. Two duplicate-alert failures now have targeted passes, while startup cause remains unproved; final parent checks must cover the two interrupted highlight cases and affected copy cases. Do not relabel the interrupted broad run green or rerun all102 solely for this. | patch (verification) |
| B10 | false | Supported NoteValue document/inline/reference fields are required and canonical; Closed forbids extras, strict validators preserve scalar text/URL/reference values and all arrays serialize back as JSON lists. No optional/default copy_credit exists inside NoteValue. independent_value changes only declared local connection/highlight IDs, then verifies that same grammar. The alleged supported-content normalization is not demonstrated. | reject |
| E1 | medium | Tool identity is checked before copied-note GET but not after it. Collapsing/switching inspector during that await can be overwritten by setTool analysis. Repeat existing origin-tool guard after the result read and retain Open created recovery. | patch |
| V1 | medium | Filed regression gap: copiesFixture omits credit, so both note/study Copied from rendering can be removed without browser failure. Assert real optional credit labels and Original unavailable in both surfaces. | patch |
| V2 | medium | Filed broken-verification gap: synthetic cursor cannot prove rollback; actual provenance-failure native case is authored but unrun. Preserve current explicit final-phase gate and execute that exact restricted fixture case there. | defer |
| P1 | high | Source deletion confirmation clears selected note/lanes without incrementing navigation. A copied-note GET pending after acknowledgement can still pass current fresh checks and reopen the copy over deletion focus; map identity/deletion/parent-pending guards are absent. Recheck complete source/origin validity after await and keep acknowledged independent destination recoverable. | patch (E1 shared post-await validity) |
| P2 (B2 recovery continuation) | medium | Generic openCreated still invokes openNote, whose exit guard sees the acknowledged unchanged source fork branch as dirty after a delayed result. Automatic selection retires it, but explicit Open created can still show a false unsaved prompt and retain phantom unload state. Consume only the exact acknowledged captured branch in this explicit recovery path, retaining newer input/other contexts. | patch (B2 continuation) |
| P3 | medium | Parent58-case run passed56 and failed the old shared-conflict E1 test in both viewports. The revised explicit reopen already sets Analysis active; the old next unconditional Analysis click collapses it, so no textbox is exposed. Failure snapshot still names the exact retained shared conflicting input. Change only that obsolete extra toggle to an Analysis-active assertion; retain exact input/no-extra-GET/no-dialog assertions. No runtime fix or tolerance weakening. | patch (test fixture adoption) |

## Verification

Observe a behavior assertion fail before implementing commands/actions. Use `/tmp/scribeswell-implementation-python/bin/python -m pytest -q` with explicit application-side node IDs; clear native DSNs/options and never include whole native-containing files. Browser uses existing hermetic local Vite/Chromium via affected workspace and normal escalation; focused new cases and affected old lane/editor tests before broader final-phase integration. Build affected web package and run owning export/codegen/database-sync reproducibility checks. Retain historical anonymous mobile-scroll failure as unverified unless actually fixed/proved. Record exact chronology, commands, passed/skipped/failed counts and before/after relevant source hashes; no native authority claim from doubles.

Parent final evidence: 290 application tests passed; browser56/58 followed by two corrected E1 cases passed after a test-only active-panel assertion adoption. Runtime/contracts identical across continuation; build/OpenAPI/catalogue/DTO/database-helper checks passed. See OWN_COPIES_EVIDENCE.md and parent result/source snapshots. Native/live-owner/device/release qualification remains explicitly unexecuted.
