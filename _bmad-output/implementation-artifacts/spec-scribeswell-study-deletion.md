---
title: 'Delete an owned study and its content without resurrection'
type: 'feature'
created: '2026-10-26'
status: 'in-review'
baseline_commit: 'f6b33ac6fb20a433f7b3ed72af82f9b8bc6694be'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/apps/scribeswell/docs/STUDY_DELETION_V1.md'
  - '{project-root}/apps/scribeswell/docs/NOTE_DELETION_V1.md'
  - '{project-root}/apps/scribeswell/docs/PERSONAL_NOTES_V1.md'
  - '{project-root}/platform/docs/development/migration-verification.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** A reader cannot remove an owned study and all its notes/passages. Uncoordinated deletion could leave private payloads or let delayed work restore them.

**Approach:** Deliver confirmed whole-study deletion under CAP-10/ST-24–25 using the adopted study-deletion contract, current authority, atomic owned cleanup and original-operation recovery.

## Boundaries & Constraints

**Always:** Preserve public reading, unrelated studies/copies/recipient-owned responses, current Access/ownership, actor attribution, independent metadata/note revisions, bounded operations and previous consumers. Preserve dirty/concurrent README, canonical and Leave/KDG work. ATDD outer/focused TDD inner.

**Never:** Upsert/resurrect, erase before explicit confirmation, infer rollback from uncertainty, auto-confirm after recovery/sign-in, retain erased private bodies/titles as evidence or invent aggregate revision/async deletion engines. No competing Access/Identity/sharing/notification path, Leave/factory, deployment/provider/activation/production mutation. Native SQL/migrations/actual-owner/session integration stay at final phase; do not acquire KDG55481/55482.

## I/O & Edge-Case Matrix

| Given / when | Then |
| --- | --- |
| Owned active study with notes, links/highlights and passages; Cancel versus Confirm | Cancel preserves input; confirmation atomically erases/closes only owned scope, advances affected revisions/attribution once and returns compact acknowledgement. |
| Dirty/composing notes/title or executing/unknown save/title/collection/create/child-delete | Pause target lanes, retain input, bound preparation5seconds total; recover prior originals first and require separate confirmation. Other studies/reader remain usable. |
| Lost delete response; original retry/lookup; changed payload | Recover original receipt without writes; reject changed payload; uncertainty retains original operation, never promises rollback. Original note.delete survives parent closure. |
| Stale metadata revision, concurrent child write or late read/write/error | Explicit current metadata review before fresh confirmation; parent locking serializes current children; closed/deleted scope never reappears from a stale continuation. |
| Foreign owner/current denial/account or navigation change | Refuse protected boundary, retain captured target and reject stale private effects. No automatic consequential replay after sign-in. |
| Overflow, closed-parent alternate writes, preexisting violations or old consumer | Refuse atomically; constrained tombstones/parent guards prevent resurrection; migration failure blocks activation. Prepare native proof only. |

</frozen-after-approval>

## Code Map

`A=apps/scribeswell`, `B=A/backend`, `W=A/web/src`. STUDY_DELETION_V1.md settles exact command, erasure/sentinel, parent insert/closure guards, migrator RLS visibility and browser lanes. `B/personal_notes_contract.py` owns Command/parser/correlated acknowledgement/OpenAPI; study.delete is study-shaped including browser adapter acknowledgement decoding. Router owns strict DELETE/lookup allowlists. `B/personal_notes_storage.py::execute/_live_outcome/lookup` owns operation→parent locking and receipt lifecycle. Existing child writers already parent-lock. Migration0005 follows immutable0001–4. `W/context/StudiesContext.tsx` coordinates note lanes/finalizers, titles/titleReads, collections, creation and child deletions; guard both success/error continuations and late list/search/pages. Reuse execute outcome lookup and existing note-deletion focus provenance. Avoid child UPDATE parent-lock triggers and inverse locks. Preserve note.delete-only recovery after parent closure.

## Tasks & Acceptance

- [x] `A/tests/test_study_deletion.py`, affected API/DTO tests, `A/web/tests/personal-notes.spec.cjs`: observe runnable route/action acceptance reds and focused DTO/storage-method reds before implementation; cover every matrix row on desktop/mobile.
- [x] `B/personal_notes_contract.py`, router/storage, owning OpenAPI/generated TS and `W/lib/personal-notes.ts`: implement strict study.delete, atomic owned erasure/receipt, current authorization and narrowly scoped original tombstone recovery; regenerate through owners.
- [x] `A/studies-migrations/versions/0005_study_deletion.py`: prepare ordinary receipt/title constraints, minimal INSERT/closure guards, narrow collection-header DELETE and transactional visible preexisting-data validation. Never execute now.
- [x] `W/context/StudiesContext.tsx`, `W/components/studies/StudiesPanel.tsx`: coordinate all target lanes, captured confirmation, conflict review, original retry and precise acknowledged eviction. Prove unsent/IME preservation, bounded preparation, navigation/account/public-focus and stale success/error safety.
- [x] `A/tests/test_personal_notes_storage.py`, migration/owner fixtures and `A/tests/test_studies_owner_integration.py`: prepare restricted erasure/overflow/rollback/alternate-write/races and actual prior-f6 consumer proof; preserve existing baselines. Update owner browser/oracle and matching unit-fixture inputs together. Syntax/collect only for native/actual-owner paths.
- [x] `A/docs/STUDY_DELETION_EVIDENCE.md`, adopted contracts and delivery tasks: record exact commands/results/chronology and component-versus-final integration limits; record scaffold/shared-UI/context/docs/ADR impacts. Parent alone updates canonical memory/specs and commits.

## Implementation Notes

No human-intent gap or irreversible execution: user delegates routine approval. Implementer owns app changes/delivery record; parent owns canonical/audit/reviews/checkpoint. Preserve README/deferred-work/unrelated files. Run focused matrix/Python/build/owning checks and native collect/syntax; parent runs broad browser regression after review.

## Spec Change Log

## Review Triage Log

| ID | Verdict | Route | Evidence |
| --- | --- | --- | --- |
| B1 | medium | patch | recoverStudyWrites sets preparing then sequentially awaits running/original operations without the existing shared preparation deadline; several retained unknown lanes can extend one action by many request budgets. Apply the already-declared bounded wait to this path and retain original identities on timeout. |
| B2 | medium | patch | Direct child.attempt recovery has no typed definitive-conflict transition; note_revision_conflict reaches the generic outer catch with the obsolete child attempt retained. Repeating recovery cannot reach a fresh confirmation. Reuse existing child-conflict handling. |
| B3 | medium | patch | Successful unknown creation recovery clears creation.current before materializing the committed note in the selected list; Cancel exposes an incomplete collection. This is premature retirement of the same creation/ack pair identified by E1/V2. |
| B4 | medium | patch | Direct note-save recovery updates lane.note/saved/status but omits the normal flush setNotes mapping. Cancel can retain a stale saved preview despite a known acknowledgement. Mirror the existing acknowledged-list update under live guards. |
| B5 | medium | patch | Concurrent authentication_required increments epoch while preparation awaits another lane; the old prepare exits without changing preparing. Reopening the retained target calls no new preparation, leaving Delete disabled. Explicit reopening after same-user reauth must restart current preparation without auto-confirmation. |
| B6 | medium | patch | Original note.create replay may return resource_unavailable after its committed note was deleted elsewhere while parent remains active. Generic recovery retains that definitively unavailable attempt forever; classify it as known failure, retain useful input and require separate fresh whole-study confirmation. |
| B7 | low | patch | The named ordinary unsent-Cancel test navigates through a flushing exit and only asserts no DELETE; the composing-Cancel case separately proves retention/resumption. Strengthen this small test directly to cover ordinary dirty Cancel and truthful naming; no new runtime complexity. |
| B8 | medium | patch | Existing executing-lane browser loop isolates each lane, so simultaneous pending lanes never test the shared preparation aggregator/ordering. Add a combined-lane test preserving no-delete-before-separate-confirmation and total bound. |
| B9 | medium | patch | Prepared current/previous writer races use one unordered gather and accept any NotesError; one lock order can remain untested and an unrelated storage failure can pass. Prepare deterministic both-order cases and exact expected refusal plus winner row/receipt checks; execute native only at final integration. |
| B10 | medium | patch | New study-delete native cases use only owning identity; direct API denial doubles do not establish allowed foreign-account storage isolation. Prepare foreign DELETE/replay/lookup with independent full owner-state/receipt equality. |
| E1 | medium | patch | Source322 stores creationConfirmed=outcome then clears its creation.current binding. After Cancel, addNote/create build a new attempt but consume this detached old acknowledgement, skipping POST and reopening old work. Verified in the actual branch despite the review's proposed guard snippet; same premature-retirement root as B3/V2. |
| V1 | medium | patch | Pre-verified regression gap accepted as filed: one stalled save and quick executing-lane cases pass if the subsequent metadata read incorrectly receives a fresh5seconds. Add a near-deadline release followed by stalled metadata and assert the original total bound. |
| V2 | medium | patch | Verification layer Other finding independently traces the detached creation acknowledgement through next addNote/create; source322 and358–377 confirm it. Same premature-retirement root as B3/E1; keep ack paired with original until materialized/retired together. |

All three context-free same-model layers completed before triage:10 blind findings,1 edge finding and1 verification gap plus1 Other finding.13 individual rows are recorded before grouping. Only B3/E1/V2 share one actual root;11 independent patch roots remain, including distinct simultaneous-lane and successive-wait coverage gaps. No intent gap, spec loopback, actionable defer or rejected finding. Frozen intent and final integration boundary remain unchanged.

B7 evidence correction after tracing the actual caller: Back to Studies only changes the tool, without flushing or exiting. The actionable low finding is the named test's missing retained-value/resumed-save assertions; composing Cancel already covered those outcomes separately. Its direct test strengthening remains valid; no runtime exit behavior was changed.


## Verification

Use `/tmp/scribeswell-manual-python/bin/python -m pytest` affected component modules; focused app Playwright desktop/mobile; `npm run build --workspace=apps/scribeswell/web`; owning exporter/catalogue/pinned-client/helper/composition checks (prior NOTE_DELETION_EVIDENCE commands). Native `--collect-only`, owner syntax only. Parent broad browser uses notes+reader suites/2workers. Local TestClient/browser escalation authorized; no native services/ports. Keep in-review for final native/actual-owner/session qualification.

Parent implementation audit reads the25-path unified app diff against f6b33ac6fb20a433f7b3ed72af82f9b8bc6694be, including prepared migration/history/owner proof and owning generated artifacts. Matrix has executed component coverage in17 study-delete Python and50 desktop/mobile browser cases; native erasure/rollback/alternate-write/previous-writer rows are explicitly preparation deliverables only under direction266 (26collected/syntax). Full affected Python335 passed21.84s; app build/owning checks pass. Actual f6 DTO/storage bytes match Git and manifest; README/index and frozen intent preserved. Independent reviews and broad notes/reader regression follow. Parent implementation audit corrected cross-account creation refs, editor freeze, definitive prior-save recovery, known-ack creation reuse, focus provenance/title overflow and overflow-safe native fixture reset before this handoff; app evidence retains partial/failing iterations.

Review corrections touched only StudiesContext, personal-notes browser tests and prepared native tests. All13 rows/11 roots addressed with direct internal corrections; no intent/spec loopback or actionable defer.24 focused desktop/mobile cases passed35.0s, then expanded creation coverage2 passed3.2s;32 native collected0.34s/syntax only. Parent read the actual three-file repair diff and verified acknowledged materialization/retirement, bounded late-result guards, explicit reauth restart and deterministic gated native lock orders/foreign full-state oracle. Complete affected regression/build follows on frozen sources.


Parent final component checks:490 browser passes/2expected native skips9.0min,335 affected Python22.72s/1existingwarning,build/owning checks passed.157-source inventory 17fec41877e9c00dcc07acfecf1de5ded2a479d765bfb11e189fb6ae074a8548 unchanged before/after full browser; only clock-test file differed from prior Python/build inventory. Earlier488/2/2 host-timing failures and controlled-clock6pass correction retained in app evidence.32native collect/syntax only; actual-owner/session/device/release still final-phase. Frozen intent/README/index preserved. Keep in-review under user direction266 rather than marking final acceptance done.
