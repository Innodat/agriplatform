---
title: 'Rename a saved personal study without disturbing its notes'
type: 'feature'
created: '2026-10-25'
status: 'done'
baseline_commit: '837e580409494d97a38546924ce850e8cd6c76ff'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/apps/scribeswell/docs/PERSONAL_NOTES_V1.md'
  - '{project-root}/platform/docs/development/migration-verification.md'
  - '{project-root}/_bmad-output/specs/spec-scribeswell-studies/ux-behaviour.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Saved studies cannot be renamed, leaving the agreed CAP-1/ST-02 journey incomplete.

**Approach:** Add Rename with explicit Save / Cancel, preserving notes/reading context and existing access, revision and retry safeguards through UI/API/persistence.

## Boundaries & Constraints

**Always:** Preserve dirty work, public reading/signup, notes/save lanes and owner HTTP contracts. Use ATDD/TDD, current Access before locks, independent metadata revisions, attribution, receipts and safe no-store errors. Qualify controlled additive migrations/restricted SQL before opt-in use.

**Never:** Implement Access/Identity, Leave/factory, references/highlights/sharing/search/delete or production activation. No startup migration, applied-history edits, title autosave, automatic conflict/stale overwrite or rollback promise. Preserve manual fixture data; manual-user acceptance remains deferred.

## I/O & Edge-Case Matrix

| Given / when | Then |
| --- | --- |
| Owner saves an English/Hebrew title | Same study ID; title/revision/actor/time persist after reload; notes/creation attribution/reader unchanged. |
| Cancel or identical title | Cancel sends nothing; identical title receipts without revision/time change. |
| Invalid title/forged input | Safe400, no effect; retain editable input. Existing title/duplicate rules apply. |
| Concurrent metadata edit/stale revision | Safe409, retain candidate; deliberate current-title reload then explicit Save. Note save independent. |
| Lost completed reply, original retry/lookup, changed payload | Current authority; one effect, original outcome; mismatch409. Unknown retains original operation; no overtaking rename. |
| Wrong owner/closed study/access loss/late response | Safe401/403/404; no disclosure, resurrection or wrong-context update; preserve note/public reading safeguards. |
| Failed migration/old running consumer | Block activation; preserve old rows/commands/read behavior; forward recovery only. |

</frozen-after-approval>

## Code Map

`A=apps/scribeswell`, `B=A/backend`, `W=A/web/src`. Load context; the app contract's
proposed rename extension owns exact wire/transaction/UI/recovery rules.
`B/personal_notes_contract.py`, `personal_notes_router.py`, `personal_notes_storage.py`,
`personal_notes_access.py`: strict DTOs, fresh authority, operation-before-parent locks,
receipts/errors. Title UPDATE is already granted;0001 receipt CHECKs need widening.
`A/tools/py/export_personal_notes_contract.py`: generated OpenAPI/TS owner.
`W/lib/personal-notes.ts`, `W/context/StudiesContext.tsx`,
`W/components/studies/StudiesPanel.tsx`: recovery, generation guards, independent lanes,
heading/library. Separate title attempts from note/create attempts.
Reuse `A/tests/test_personal_notes_storage.py`, `A/tests/studies_owner_fixture.py`
and `A/web/tests/studies-owner.integration.cjs` for native/actual-owner proof.

## Tasks & Acceptance

- [x] Backend contract/router/storage/error files above: implement the owning proposed contract; test malformed inputs, no-op/conflict, receipts, ownership and stale replay.
- [x] `A/studies-migrations/versions/0002_study_rename.py` and native storage tests: compatible constraints, restricted permissions, attribution, concurrency, migration rollback/retry and old commands.
- [x] Exporter/generated outputs: regenerate/check schema/DTO/client agreement.
- [x] Browser client/context/panel above and `A/web/tests/personal-notes.spec.cjs`: explicit Save/Cancel/Retry, conflict reload and account/navigation/input safety on desktop/mobile.
- [x] Actual-owner fixture/browser files above, app evidence and canonical memory: UI rename/reload with independent unchanged-note/receipt/actor SQL assertions and exact executed results.

Given an existing note, when its study is renamed and reloaded through actual services, then its acknowledged content is unchanged. Given racing metadata/note saves, when both complete, then neither loses acknowledged data. Execute every matrix row; mocks do not prove SQL permissions.

## Implementation Notes

Implemented strict `study.rename` DTO/OpenAPI/client correlation and safe revision
conflicts; fresh authority remains ahead of operation/owner row locks. New metadata
writes change only title/revision/update actor/time and commit their receipt together.
0002 changes receipt CHECKs only; 0001 stays immutable. UI uses a separate in-memory
title attempt, explicit Save/Cancel, frozen uncertain Retry, deliberate conflict reload
and identity/navigation guards. Confirmed acknowledgements reread current metadata;
note buffers and reading context remain independent.

Native qualification passed13 including real restricted logins, actual0002 rollback
and retry, metadata/note races, old command compatibility, stale/closed replay,
no-op and overflow. The previous SQL consumer source is frozen from the baseline
commit under app test fixtures; its imports use compatible current interfaces.
Wire/API130, native13 and focused browser26 passed. Pre-review complete affected browser70
and session12 passed sequentially; earlier failures remain disclosed. Real-owner run
c948174c-86a7-4816-b3d5-736ca930428b passed UI rename/reload, independent unchanged-note
and single-receipt SQL, foreign/disabled denials, credential inspection and normal
owned shutdown. The prior fixture failure and preflight collisions are retained.
Canonical memory and bounded derived status are reconciled; all seven frozen matrix
rows map to executed passing tests in
[app evidence](../../apps/scribeswell/docs/STUDY_RENAME_EVIDENCE.md).

Scaffold: existing helper consumed, unchanged. Shared UI: app-specific, no promotion.
Agent context and accepted ADRs: unchanged. Documentation/evidence: app-owned contract
and evidence updated; canonical memory reconciled without broader scope changes.

## Spec Change Log

## Review Triage Log

| ID | Verdict | Evidence and route |
| --- | --- | --- |
| B1 | medium | openNote increments navigation while retaining study; refreshTitle then skips its heading and deletes the acknowledged attempt. Patch the existing selected-study condition; retain account/revision guards. |
| B2 | medium | execute success and subsequent GET share one catch; GET failure falsely says Title not saved and repeats confirmed PUT. Patch confirmed receipt handling to retry the existing metadata read only. |
| B3 | low | Terminal errors do remain frozen, but Leave study is always available and unavailable closed studies must not become editable. Payload mismatch cannot arise from ordinary frozen UUID/payload input. Reject additional recovery branches for these rare cases: safe exits/current-authority protections already hold. |
| B4 | low | HTML maxlength counts UTF16; backend Title counts scalar Unicode, so valid supplementary titles are truncated. Patch by deleting the premature HTML limit on rename and keeping strict server validation. |
| B5 | medium | Two conflict reloads can return out of order and lower edit.base despite heading revision guard. Patch using the existing titleReads generation/entry identity checks. |
| B6 | medium | Reload catch lacks its success navigation/study guard and can mask a later screen on late401/403. Patch equivalent existing guards in catch. |
| B7 | medium | loadStudies replaces a collection after refreshTitle advanced its title; an older list can regress displayed library metadata. Patch reconciliation against existing higher revisions; preserve page membership/order semantics. |
| B8 | medium | beforeunload only inspects note lanes; executing/unknown title attempts can lose in-memory operation identity without an exit warning. Patch the existing predicate to include those demonstrated title states; no persistence or rollback promise. |
| B9 | low | Removing autofocused form leaves keyboard focus on body after Cancel/Save. Patch focus return to surviving Rename within the same mounted study surface. |
| B10 | low | beginRename awaits GET with no busy feedback and leaves its trigger enabled, permitting redundant starts. Patch existing busy feedback/trigger disabling; no new loading surface. |
| E1 | medium | Same verified navigation-versus-selected-study defect as B1; merge only after this individual verdict. Patch existing condition. |
| E2 | low | Same verified scalar/UTF16 boundary as B4; merge after individual verdict. Direct deletion plus boundary assertion. |
| V1 | medium | Pre-verified gap: existing tests never return two same-study metadata reads in reverse revision order. Patch gated browser assertion so removing revision reconciliation fails. |

Surviving patch groups: B1/E1; B4/E2; B2; B5; B6; B7; B8; B9; B10; V1.
No intent change, public API addition, new workflow or unproven guard is needed;
fixes correct existing conditions/predicates/feedback and demonstrate those states.
B3 is rejected as low/rare with nontrivial proposed recovery complexity, not deferred.

All10 patch groups resolved. Patch red10fail/1pass and busy-cleanup red observed;
patch24/existing rename24 passed. Removing the heading revision guard caused the
ordering test to fail; restored source passed. Parent read the patches and executed
final browser94/session12/native13, backend and real-owner verification successfully.
No review deferrals or intent changes.

## Design Notes

CAP-1/ST-02 settles intent. API/command/additive migration require dispatch; only fresh
synthetic effects, separate activation. Reuse scaffold helper; app-specific UI with no
promotion. Agent context/ADRs unchanged. Preserve all broader requirements.

## Verification

Final native command with `SCRIBESWELL_NOTES_TEST_ADMIN_URL=postgresql://postgres@127.0.0.1:32768/postgres`
and `SCRIBESWELL_NOTES_BROWSER_QUALIFY=true`:
`/tmp/scribeswell-manual-python/bin/python -m pytest apps/scribeswell/tests/test_personal_notes_storage.py -q`
passed13; `/tmp/scribeswell-rename-native-qualified.log`. Owned PostgreSQL container
`scribeswell-rename-native-20261025` stopped normally, retained. Intermediate port5182
collision12passed/1failed remains in its distinct log, as do initial sandbox/head-only
fixture failures. No history or expected business result was weakened.

Exact remaining commands/results, including actual-owner collision attempts, generated
checks, app build and affected regression outcomes are in
[app evidence](../../apps/scribeswell/docs/STUDY_RENAME_EVIDENCE.md). Post-review final proof: browser94/session12/native13, backend172/Access56/public-release73+49subtests, build/generated/helper/composition and actual-owner run a1952f79 passed. Three review lenses completed; all13 findings triaged,12 resolved in10 groups, one low/rare rejected, none deferred. Manual acceptance and activation remain unclaimed; local commit recorded at completion.


Smallest red first; affected contract/API/native-storage and desktop/mobile cases,
generated checks/build. Fresh actual-owner UI rename/reload with independent SQL,
old-consumer compatibility and matrix traceability. Stop only owned manual65a01b23
if ports needed; retain data. Impacted sessions/helper/composition checks, exact commands,
failures and independent triage. No root-wide, user-manual or production pass claim.
