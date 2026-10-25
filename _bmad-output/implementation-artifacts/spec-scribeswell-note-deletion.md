---
title: 'Delete an owned personal note without resurrection'
type: 'feature'
created: '2026-10-25'
status: 'in-review'
baseline_commit: 'c8a56681ba3eec7d104f4aab951b2e66195bb0e9'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/apps/scribeswell/docs/NOTE_DELETION_V1.md'
  - '{project-root}/apps/scribeswell/docs/PERSONAL_NOTES_V1.md'
  - '{project-root}/platform/docs/development/migration-verification.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Readers cannot remove an owned personal note, and naive removal could leave private payloads or let a delayed save/retry restore it.

**Approach:** Deliver confirmed own-note deletion under CAP-10/ST-24–25 with atomic erasure, current authority and original-operation recovery. Whole-study deletion follows separately.

## Boundaries & Constraints

**Always:** Preserve public reading, other notes, study metadata/passages, current Access/ownership, serialized saves, attribution, old-consumer compatibility and dirty/concurrent work. Use the adopted deletion contract; ATDD/TDD. Native/owner/session integration stays at the end under direction266.

**Never:** Upsert/resurrect, erase before explicit confirmation, delete another owner's work, derive success from an unknown outcome, retain deleted note bodies as recovery evidence, or auto-repeat consequential deletion after sign-in. No study deletion, sharing/Access competitor, Leave/factory, provider/config/deploy/activation or production-data mutation.

## I/O & Edge-Case Matrix

| Given / when | Then |
| --- | --- |
| Saved owned format1/2 note; Cancel versus Confirm | Cancel preserves input; confirmed delete erases only this aggregate, advances final revision/attribution once and acknowledges compactly. |
| Dirty/composing note or executing/unknown prior save | Retain local input, pause new saves, settle/recover the original save first within bounded preparation; only explicit confirmed ready deletion discards its unsent input on success. |
| Lost delete reply, same operation retry/lookup or changed payload | Recover original acknowledgement even after parent closure; changed payload refuses; uncertainty preserves operation/input without a rollback claim. |
| Concurrent save/delete, stale revision, late read/save/create receipt | One current revision/lifecycle wins; no lost overwrite, local reinsertion or deleted-note resurrection. |
| Foreign account, denied Access, navigation/account/sign-in change | Current protected boundary refuses; confirmation targets its captured note; late replies cannot affect another context or expose old private state. |
| Alternate closed-row write, overflow, migration failure, old writer | Empty tombstone constraint plus monotonic lifecycle prevent payload refill/reopening; fail atomically, preserve previous consumers and block unsafe activation. Native proof prepared only. |

</frozen-after-approval>

## Code Map

`A=apps/scribeswell`, `B=A/backend`, `W=A/web/src`. NOTE_DELETION_V1.md closes exact HTTP, erasure, save preparation and recovery semantics. `B/personal_notes_storage.py::execute/lookup/_live_outcome` owns operation→parent→note locking and compact receipts: only original note.delete may resolve against an owned inactive tombstone; historical create/replace must remain unavailable. Existing active predicates protect read/list/search. `B/personal_notes_contract.py` owns strict DTO, Command, correlated ack and OpenAPI; router owns dedicated DELETE/lookup allowlists. Existing migrations0001–0003 and restricted grants remain immutable; ordinary next0004 widens receipt checks and enforces inactive-value emptiness. `W/context/StudiesContext.tsx` owns timers/attempts/account epochs; coordinate deletion with that same lane. `W/components/studies/NoteEditor.tsx` and StudiesPanel own selection/actions. Reuse `W/lib/personal-notes.ts::execute` outcome lookup. Native historical fixture constructors must exclude0004 for earlier checkpoints.

## Tasks & Acceptance

- [x] `B/personal_notes_contract.py`, router/storage and owning OpenAPI/TS outputs: observe runnable API red; implement closed note.delete, atomic erasure/revision/receipt and narrowly scoped tombstone recovery. Regenerate through owners.
- [x] `A/studies-migrations/versions/0004_note_deletion.py` and affected release/history fixtures: prepare ordinary receipt/closed-value constraints and forward recovery; do not run migrations now. Preserve real previous-checkpoint consumer proof.
- [x] `W/context/StudiesContext.tsx`, note actions/editor and `W/lib/personal-notes.ts`: observe browser confirmation red; coordinate bounded save preparation, captured confirmation, typed failures, original retry and precise acknowledged eviction with stale-finalizer guards.
- [x] `A/tests/test_note_deletion.py`, affected API/contract and `A/web/tests/personal-notes.spec.cjs`: cover each component matrix row, desktop/mobile confirmation/focus, dirty/unknown-save/delete recovery, conflict, navigation/account races and unchanged unrelated work.
- [x] `A/tests/test_personal_notes_storage.py`, owner fixture/browser: prepare restricted erasure/rollback/races/alternate-write/old-consumer and actual-owner independent SQL proof; syntax/collect only.
- [x] `A/docs/NOTE_DELETION_V1.md`, `A/docs/NOTE_DELETION_EVIDENCE.md`, personal-note contract and canonical memory (parent-owned): distinguish implemented/executed/prepared status; record scaffold/shared-UI/context/docs/ADR impacts.

## Implementation Notes

Parent diff/matrix audit against c8a56681 covers23 app paths; frozen intent unchanged. Executed matrix: format1/2 erasure/revision/overflow method cases; desktop/mobile Cancel/dirty/composition; executing/unknown save; lost delete reply/original retry; delete/prior-save conflict and review-Cancel preservation; captured navigation/account races and stale list exclusion. Final focused36 browser and244 Python passed; exact commands/logs in app evidence. Structural/native rollback/races/old-consumer/owner SQL rows explicitly require preparation only here:22 native cases plus42 fixture/control cases collected, syntax checked, not executed. Actual previous-checkpoint DTO/storage byte/hash comparison passed. No claim of final integration or release acceptance.

Six parent implementation-audit paths were corrected before independent review: retained failed-save identity, final IME input, bounded save preparation, stale list metadata, prepared owner-script temporal declaration, and deletion review advancing autosave revision. Runnable failures and test-fixture corrections are retained in app evidence. Broad notes/reader regression follows independent review. Scaffold/shared-UI/context/docs/ADR impacts recorded in app evidence; parent-owned canonical status updated separately.

## Spec Change Log

## Review Triage Log

| ID | Verdict | Route | Evidence |
| --- | --- | --- | --- |
| B1 | medium | patch | reviewDelete accepts repeated clicks while status remains conflict and has no per-request exclusion; reversed same-target replies can replace newer reviewed writing/revision. Serialize the demonstrated reads. |
| B2 | medium | patch | DeleteDialog flattens current paragraphs/list items and displays external labels or passage labels alone; different saved destinations can be invisible during current-note review. Preserve readable structure and actual source/reference targets without technical payload dumps. |
| B3 | medium | patch | Acknowledged target eviction unmounts the dialog and Delete trigger; cleanup only focuses a connected trigger, leaving keyboard focus at body for the selected deleted note. Establish a visible surviving destination with current-context guards. |
| B4 | medium | patch | pendingDeletions can hold several notes, but every global recovery button has the identical visible/accessibility label. Distinguish retained targets under current authority and prove exact operation routing. |
| B5 | low | patch | Confirmation explains removal/discard but omits its permanent/no-undo consequence. A direct wording correction requires no new flow or state. |
| B6 | low | reject | Uncancelled race timers retain only bounded closures for at most5s and perform no late mutation. Everyday user impact is negligible; adding timer-management branches exceeds a direct correction, so reject under review's low-complexity rule. |
| B7 | medium | patch | New DELETE-specific route tests cover success/invalid/query input; existing401/403 assertions target other routes. Add direct DELETE and note.delete lookup refusal with storage untouched. |
| B8 | medium | patch | Prepared native save/delete race asserts one dictionary/one error only; it does not inspect winner-specific row or receipt state. Add those independent assertions without executing native SQL now. |
| B9 | medium | patch | Byte-frozen prior consumer proves ordinary post-migration reads/writes and tombstone reads, but its old save never races new deletion. Prepare the actual old-writer race and final row/receipt checks. |
| B10 | low | patch | Durable app evidence already records commands/results/limits; raw /tmp logs are supplementary. Its only owning-client invocation nevertheless points to a retained proof install, so add the repository entrypoint and supported installation/toolchain preconditions; keep the actually-run command as historical evidence. |
| P3 | medium | patch | New acknowledgement focus recovery checks note/study/navigation but not tool closure or deliberate surviving public-control focus. Return to reader/Analysis toggle leaves navigation unchanged, so global fallback can steal focus on a late reply. Four focused desktop/mobile reds reproduced, then14 focused passed9.3s. Same worker restricted recovery to removed/hidden target focus while preserving normal/fallback guards. |
| P2 | medium | patch | Parent full Python run291passed/1failed: final-oracle unit baseline still supplies one note/old receipts while the new oracle correctly requires erased target plus retained active note and deletion evidence. Update synthetic inputs and strengthen deletion/retained-note tamper variants, preserving oracle and existing negative assertions. Prepared under /tmp during browser freeze, applied after completion;12 focused cases passed and final297 Python passed with existing assertions unchanged. |
| P1 | medium | patch | Newly rendered full source destinations overflow the conflict-review dialog with a valid1940-byte URL; focused desktop/mobile both reproduced the failure. Apply direct anywhere-wrapping while retaining complete destinations and mobile/desktop assertions. |
| V1 | medium | patch | Verification-gap finding accepted as filed: confirming conflict tests retain server revision1, while revision2 review tests Cancel. Advance the server revision in confirmation tests and assert DELETE uses it and evicts only after acknowledgement. |

All three context-free same-model layers completed before triage; edge returned no findings.11 reviewer findings plus parentP1–P3:14 individual rows,13 actionable independent roots,1 rejected bounded-timer row. No intent gap, bad-spec loopback, deduplication or deferred new lifecycle. Corrections preserve user-deferred native/owner/session execution and frozen intent.

## Verification

Final parent component checks:418 desktop/mobile passes/2 expected native-browser skips7.8min;297 affected Python22.54s/1existingwarning; TypeScript/Vite build and owning exporter/client/catalogue/helper/composition pass. All151 runtime/test/migration hashes unchanged throughout final checks (`faee033689aa398a29e036756a51a930b6d4242b69a1cafdefd8ba2e33dfd481`).23 native cases collected0.97s, syntax only, never executed. Earlier414/2 browser pass and291/1 Python failure, P2 fixture correction and P3 focus reds retained in app evidence.14 individual review/parent findings,13 actionable corrected; bounded-timer row rejected. Actual prior-checkpoint bytes/frozen intent/README preserved. Component checkpoint only: status remainsin-review under direction266, with native/actual-owner/session/release gates open. No push or activation.


Smallest runnable API/browser failures first, focused DTO/storage-method/save-lane TDD next, then complete affected component Python and notes/reader browser checks, app build and owning exporter/client/catalogue/helper/composition checks. Prepare native/owner proof and collect/syntax only; no shared ports or session integration. Retain exact commands, results and failed-test chronology. Capture implementation baseline only after the search preservation checkpoint.
