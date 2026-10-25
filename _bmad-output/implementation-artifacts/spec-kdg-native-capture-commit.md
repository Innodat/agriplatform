---
title: 'KDG restricted-runtime durable create qualification'
type: 'feature'
created: '2026-10-25'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'aa2ce1ec8d1c12e922715c9c3631f2dbbfa4eb6d'
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/apps/kdg-capture/docs/CREATE_HANDLER_EVIDENCE.md'
  - '{project-root}/apps/kdg-capture/migrations/README.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Create/retry lacks committed cross-connection durability and concurrency proof.

**Approach:** Apply candidate0002 through restricted-migrator Alembic; qualify real runtime sessions with MockTransport Access. Retain committed data and evidence.

## Boundaries & Constraints

**Always:** Exact run99b7231c-0a5b-4bdb-98e8-3329564c526a, localhost55482, database `kdg_schema_659350f762c8494c9241b7b1c8ea9566`, existing KDG roles. Permanent effects: complete candidate DDL/RLS/grants, ledger0001→0002 and recorded synthetic KDG rows. Preserve prior data/evidence/concurrent work/resources/dependencies/TS7.0.2. Fingerprints/HMAC deferred; bootstrap unchanged.

**Never:** New databases/schemas/roles, broader privileges, Auth/Identity records/grants, active migration promotion, mounted API, real access, production, Leave/editor, provisioning/deployment/pilot, cleanup/reset/drop or automatic downgrade. No generic schema inventory.

## I/O & Edge-Case Matrix

| State | Expected behavior |
|---|---|
| Fresh commit | Independent connection sees one capture/outcome/history triplet |
| Lost delivery / changed-body retry | Original receipt; no duplicate effects |
| Concurrent duplicate | First commit wins; bounded busy may retry |
| Native write failure | Complete rollback; later valid attempt may commit |

</frozen-after-approval>

## Code Map

- `apps/kdg-capture/migrations/`: existing env/policy/candidate and tests/native_fixture.py custody; never prepare.
- `apps/kdg-capture/write-candidate/`: actual handler/create/outcome; preserve authority/deadlines/ownership.
- `apps/kdg-capture/docs/contracts.md`, handler evidence and ADR-0020: authoritative contracts/gates.

## Tasks & Acceptance

**Execution:**
- [x] `apps/kdg-capture/migrations/tests/capture_commit_fixture.py`: custody/private receipts; test-only discovery combines versions/candidates. Ordinary upgrade head uses existing env/policy/migrator; no stamp/bypass/active-config edit.
- [x] `apps/kdg-capture/migrations/tests/qualify_capture_commit.py`: separate explicit `--migrate-retained` and `--qualify-retained` phases. Administrator seeds fixture parents only; runtime executes handlers, independent reads verify, bounded barriers prove overlap.
- [x] `apps/kdg-capture/write-tests/test_capture_commit_qualification.py`: ATDD plus focused failure/phase/oracle tests; characterize native defects before fixes.
- [x] `apps/kdg-capture/docs/NATIVE_CAPTURE_COMMIT_EVIDENCE.md`, `docs/evidence/native-capture-commit-20261025.json`, `docs/next-session.md`, `migrations/README.md` under this app: record sources/results/effects/fixture transition; preserve historical evidence.

**Acceptance Criteria:**
- Given absent storage, when acceptance runs, then observe missing-table failure without writes. Given verified0001, when migration succeeds, then reach0002; failure blocks qualification with phase reporting.
- Given a runtime create commits and closes, when a fresh restricted session reads, then owner/actor/version/history/outcome agree. Given discarded delivery, when changed-body retry executes, then return the original receipt.
- Given overlapping sessions, when duplicates race with identical/differing bodies, then one triplet commits and busy/retry recovers it. Given first-writer failure after inserts, then rollback leaves a waiting valid writer able to commit.
- Given different operations sharing one capture ID, when they race, then one commits and the safe loser leaves no orphan outcome/history. Foreign-org/account, DDL/ledger/role-switch attempts remain denied.
- Given assigned replay, when authority is checked, then current stored-child membership/assignment governs, never incoming target/eligibility. No network under locks; existing deadlines/cancellation safeguards stay intact.

## Implementation Notes

Baseline `aa2ce1ec8d1c12e922715c9c3631f2dbbfa4eb6d`. Investigation only; no database/Docker changes or tests run. Persistent effects require dispatch checkpoint; no unresolved intent questions.

## Design Notes

After migration, this fixture is deliberately0002 while active discovery remains0001. Old ledger-only inspectors/qualifiers become historical and inapplicable here; preserve files/receipts and unresolved metadata-hash discrepancy. Record a new transition receipt, not a replacement baseline.

On failure/uncertainty, block progress and reconnect to reconcile ordinary Alembic revision/relevant effects before explicit retry. Retain successful migration/data even if tests fail; stop normally without reversal. Preserve previous context/fresh-body behavior through regression. Production compatibility/recovery and activation remain ADR-0020 gates.

Scaffold helpers unchanged unless a reproduced generic defect requires template/test sync. Domain tests stay app-owned. No UI/agent-context/new ADR impact.

## Verification

Use retained owner-env Python P and pinned Node/Supabase.

- `P -I -B -m unittest discover -s apps/kdg-capture/write-tests -p 'test_*.py'`
- New qualifier's explicit migration, then qualification phase, only after implementation/review.
- Scaffold sync `--check`; receipts, restricted identities, independent reads, foreign sentinel and source/dependency preservation.

Offline Alembic graph check passes: active head0001, test-only head0002 with parent0001; no database connected. Concurrent changes are preserved; no database/Docker operation.

Approval recorded2026-10-25: user approved and continued this exact persistent scope. No further user confirmation for these approved fixture changes. Before running persistent migration, report completed harness/offline test readiness to parent for code inspection; parent then returns internal continuation. This is implementation inspection, not another user approval.

Pinned tools: P=`platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python` (`-I -B`); Node=`platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node`; Supabase CLI uses the same toolchain prefix plus `/payload/supabase/supabase`. Existing run lifecycle: `python3 platform/deployment/dev.py up|stop --target platform/deployment/environments/kdg-local.json --run-id 99b7231c-0a5b-4bdb-98e8-3329564c526a --supabase ABSOLUTE_PINNED_CLI`. No new fixture/preparer/reset/cleanup. Credentials only through existing custody adapter; never print private files/URLs/raw subprocess diagnostics. Existing fixture path is `platform/deployment/.local/kdg-native-focused-20261023/fixture-cff53592f5ca43a1a0cc65398957140f/fixture.json`.

Dirty-tree authorization persists. Parent snapshot `/tmp/kdg-commit-approved-before-20261025.json` records current HEAD/preexisting paths. Scope only planned KDG files/spec; preserve concurrent Leave/Scribeswell/platform changes and old native evidence. Do not stage, commit or push; parent handles scoped diff/review/commit. Managed generated helpers/templates stay unchanged unless a concrete reproduced generic failure warrants synchronized changes. Synthetic worker tests may need bounded tool escalation because the sandbox stalls their worker/event-loop interaction. Use MockTransport only.

Implementation audit: all four tasks completed. Matrix rows map to passing native fresh-commit, discarded-delivery, duplicate/busy/retry and post-insert failure groups. Actual restricted logins and independent reads verified; migration/qualification and normal stop succeeded. No business implementation changes. Parent proceeding to required diff review.


## Review Triage Log

B1 medium / patch — Successful migration receipts record candidate source hashes but qualification never compares them. A changed candidate could be claimed against an older schema; require matching applied-candidate provenance before seed/qualification.
B2 medium / patch — Existing-head reconciliation can currently mint new source evidence from the ledger alone, bypassing B1's provenance check. Require a prior successful applied-candidate receipt matching fixture/run/current candidate before clearing failure state. Ordinary Alembic revision remains authoritative; reject the suggested catalogue inventory expansion as unnecessary for this concrete fix.
B3 low / patch — migrate_retained writes observed-head failure details, then main writes a newer generic failure that hides them from latest-receipt selection. Preserve one detailed failure result/reference; never replace its observed revision with a less informative record.
B4 medium / patch — Private execution source inventories omit imported owner models, native/custody helpers, migration helper/config/foundation. Include the relevant known files so future evidence cannot silently omit an executing input; retain old phase receipts unchanged.
B5 medium / patch — Replay/race tests verify the expected triplet but omit alternate capture absence and final per-dataset totals before qualification success. Add explicit alternate-target and five/five/five checks to the qualified path, not only an ad hoc later inspector.
B6 low / patch — Failed-first case checks capture absence but claims history absence. Native FKs protect structural orphaning, but add the explicit failed-history count and surviving operation linkage to make this test's claim direct.
B7 medium / patch — Persisted-input comparison omits child/questionnaire/date/eligibility/member and history command/revision identity. Extend the existing native read oracle against accepted command and verified dataset facts; no new application behavior.
B8 medium / patch — Start intent identifies parents but final failure lacks correlation/completed cases and generated command IDs were not journaled. Link start/success/failure by attempt identity and record selected operation/capture IDs before executing each case; never log payloads or overwrite prior evidence.
V1 medium / patch — Pre-verified broken-verification gap: CLI failure test mocks the entire migration function, bypassing its actual reconnect/observed-head branch. Add focused upgrade-failure cases invoking real migrate_retained and assert observed revision or unavailable, with no qualification.
Edge-case layer returned no findings. All findings are current harness/evidence patches with private surfaces; no intent change or deferred item. Migration schema/production code remain unchanged.


Review patch completion: all nine findings patched; reviewer recheck confirms B1–B3 addressed. Focused qualification tests21 PASS, full affected suite101 PASS (2.353s), all three scaffold sync checks PASS. Final explicit migration reconciled the existing0002 against original applied provenance without DDL; corrected-source qualification passed8 native groups. Independent SELECT-only inspection verifies final dataset5/5/5 and aggregate10/10/10 across two retained runs, exact source bindings, roles and foreign sentinel. Known run stopped normally again. Original receipts and initial dataset preserved. One unmocked offline failure appended only a receipt; mock corrected, receipt retained; no database effect. No new application or shared-helper defect.
