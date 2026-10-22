---
title: Prove first committed owner-local outcomes without fingerprints
type: feature
created: '2026-10-22'
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: aae72cff9071186b700dd0ba578769431bac78ba
context:
  - AGENTS.md
  - platform/docs/architecture/decisions/0061-kdg-first-committed-operation-wins.md
  - platform/docs/architecture/contracts/owned-write-and-secret-execution.md
---

<frozen-after-approval reason="user approved bounded synthetic WRITE and requested next after ADR0061">

## Intent

Prove the selected first-committed model with an additive owner-copy candidate and
neutral synthetic create/edit consumer using existing builder tools. A scoped operation
commits business state, immutable evidence and original compact receipt exactly once,
without command fingerprints, HMAC or keys. This is prerequisite proof, not KDG activation.

## Boundaries & Constraints

Preserve concurrent work, every historical candidate/source/test/evidence and Docker
resource. Keep dependencies including TypeScript7.0.2. Server command handlers define
command type. Exact org/account/command/operation uniqueness, current stored-target
authority, strict structural parsing and supported versions remain. Fresh execution alone
applies domain/revision/lifecycle checks. Replay returns original target/revision/version,
including after later changes. External checks stay outside locks; private discovery and
bounded rollback/recheck handle raced target changes within the original budget. Denial
must not disclose outcomes. Unknown retains the operation; never allocate a fresh one.
Use fresh exclusive synthetic namespaces, retain all proof/data. No Leave/editor,
production, real account/access, provisioning/deployment/pilot or cleanup. No real API,
UI/offline queue, migrations or release/restore readiness claim. Frozen client snapshots
and predecessor rules remain consuming obligations, not implemented UI.

## I/O & Edge-Case Matrix

| Scenario | Expected behavior |
| --- | --- |
| Create/edit then retry changed valid body/target | Original authorized receipt; one complete set of effects; no keys or body comparison |
| Different bodies race under same key | One winner supplies entire effects/evidence/receipt; both authorized attempts recover it |
| Stored versus supplied target differs | Stored authority controls replay; bounded restart on raced discovery, no network under locks |
| Later revision/lifecycle change or supported incoming version differs | Original supported receipt; fresh checks do not veto replay |
| Fresh invalid/stale, unsupported version, denied/foreign or unresolved | Safe distinct failure/unresolved; no false success or existence leak |
| Evidence/outcome insert failure, no-op or contention | Full rollback, no-op receipt without false history, bounded safe error; context clears |

</frozen-after-approval>

## Code Map

- Preserve `platform/builder-cli/examples/owned-service/atomic_write.py` and all historical siblings. Reuse Budget/VerifiedContext/OutcomeKey/transaction/execute/outcome_lock via imports; incidental historical module imports do not permit fingerprint calls.
- Add `examples/owned-service/first_committed_write.py` and `tests/first_committed_sample.py`, under `platform/builder-cli`: compact receipt validation plus explicit neutral sample orchestration, not a generic engine.
- Add `tests/first_committed_fixture.sql`, `tests/test_first_committed_write.py`: fresh no-fingerprint schema with existing RLS/immutable/linkage patterns and real restricted SQL tests. Reuse `tests/prepare_atomic_write.py` byte-identically staged beside new SQL in ignored proof directory (expected filename atomic_write_fixture.sql). Existing installer supports explicit source maps; prove copying/executing candidate dependencies and preserving edits.
- Existing prepared Python: `platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python`. Existing native `dev.py` target `platform/deployment/environments/kdg-local.json`, run99b7231c-0a5b-4bdb-98e8-3329564c526a; executable tools under `platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/`. Private admin input: `platform/deployment/.local/identity-baseline/access-registry-reviewed-20261021/credentials.json`; never print credentials.
- Proof root `platform/builder-cli/.local/write-first-committed-20261022`; preservation baseline already captured. Native start/stop through existing dev.py only, preserve resources.

## Tasks & Acceptance

- [x] Add focused acceptance before candidate implementation; observe missing-behavior RED, then implement/test incrementally.
- [x] Add candidate, explicit consumer and fresh no-fingerprint fixture; cover every matrix row with actual restricted PostgreSQL and safe diagnostics.
- [x] Prove copied execution with existing installer; run affected historical regression and Node builder tests.
- [x] Add `platform/builder-cli/WRITE_FIRST_COMMITTED_EVIDENCE.md`; prepend current status to example README and KDG next-session without changing original tails. Record exact commands/results, requirement traceability, limitations and five impact decisions.

Given changed retries and concurrency, when executing against the synthetic owner,
then real committed rows prove one original outcome under current authority without
fingerprint fields. Given failed local inserts, when the transaction exits, then all
business/evidence/outcome effects roll back and pooled context clears.

## Implementation Notes

No intent gaps. Footprint is additive candidate/tests/fixture plus current documentation;
no shared runtime surface or irreversible external action. User approval already covers
dirty-tree preservation and this bounded synthetic continuation. Root owns review,
final audit and scope-only local commit; do not stage or commit. Keep new interfaces
small; historical source hashes must remain unchanged. Escalated loopback/Docker access
may be needed; use narrowly scoped requests and preserve failed logs too.

Review patch adds `platform/builder-cli/tests/prepare_first_committed_write.py`, a thin
tracked wrapper reproducing the documented retained-staging procedure from unchanged
historical sources. Actual fresh attempt2 preparation passed; attempt1 remains unchanged.

## Spec Change Log

## Review Triage Log

| Finding | Verdict / route | Evidence and resolution |
| --- | --- | --- |
| Blind1: behavioral ATDD ordering | medium / patch (evidence qualification) | Initial RED was import-only; behavioral suite was added afterward. Chronology cannot be repaired. Explicitly record the ordering limitation rather than claim behavioral ATDD before implementation; review safe-error correction starts from a behavioral RED. |
| Blind2: rollback absence hidden by RLS | medium / patch | Context-free record count sees zero even with residual rows; assert attempted target/outcome/revision under exact authorized context. |
| Blind3: captured fingerprint alias evades guard | medium / patch | atomic_write imported verify_fingerprint at module load; patch both aliases and exercise changed replay. |
| Blind4: preparation not reproducible from tracked sources | medium / patch | Procedure was documented but manually staged; add thin retained-staging wrapper around unchanged existing preparer. |
| Blind5: version2 origination untested | medium / patch | Only v1-origin/v2-input covered; add native v2-origin/v1-replay for create/edit. |
| Blind6: losing race target not inspected | medium / patch | Winner alone did not exclude orphan target; inspect losing record/evidence/outcome and exact winner-body association. |
| Blind7: unexplained short busy wait | medium / patch | One retained attempt measured1.198s. Instrument actual timeout/blocker/SQLSTATE and investigate without weakening expectations; retain original run. |
| Blind8: review/custody promised but absent | low / patch | Evidence was prepared before review; append actual dispositions, final manifest reference and tested source hashes at closure. |
| Edge1: callback transport error leaks | medium / patch | authorize call had no exception adapter. Add behavioral canary RED then safe authorization_unavailable with suppressed context. |
| Verification1: exact linkage tests masked | medium / patch | Existing used outcome_id has UNIQUE conflict independent of composite FK. Use no-op outcome without revision and valid alternative target, assert actual FK SQLSTATE/constraint. |
| Verification2: parser success missing | medium / patch | Replacing parser with unconditional rejection passed its rejection-only tests. Decode valid JSON and execute that command natively. |

All three lenses completed. Thread capacity prevented a fresh third reviewer; the
context-free investigation agent was reused for verification-gap review, receiving
only its reviewer instructions/diff, without the Build claims file. Independent blind
and edge reviewers were freshly launched. All findings were assessed separately.

## Verification

Use prepared Python with PYTEST_DISABLE_PLUGIN_AUTOLOAD=1, isolated -I -B pytest,
-p no:cacheprovider, and fresh ATOMIC_WRITE_FIXTURE. Run the new suite, existing atomic37,
fingerprint63 and secret65 as applicable, then pinned Node --test builder tests.
Use independent read-only retained catalog/data inspection and exact source/proof
hashes; scoped whitespace/link checks. Scaffold impact is candidate-copy proof only;
shared UI and agent context unchanged; docs updated; ADR0061 adopted, accepted ADRs
unchanged. Do not claim business API/device/backup/production readiness.


Matrix audit: all six rows ran in the42-case native suite. Changed replay/later state:
test_changed_valid_target_body_versions_and_later_lifecycle; racing bodies:
test_different_bodies_race_and_raced_target_recheck and test_changed_edit_bodies_race_has_one_complete_winner;
stored authority/restart: test_raced_stored_target_denial_and_original_budget;
invalid/denied/foreign/unresolved: parser/malformed/stored-receipt/denied tests;
rollback/no-op/contention/context: four insert-failure variants, create/noop, timeout and pool tests.
Independent root42 passed6.35s; historical100 passed6.50s; builder62 passed16.18s;
independent read-only retained inspection exit0. Exact commands and failed runs in owner evidence.


Final reviewed acceptance49 passed7.28s on fresh attempt2; focused review14 passed;
independent read-only retained inspection exit0. Exact source custody and safe busy
diagnostics recorded. Initial import-only ATDD ordering limitation and earlier timing
anomaly remain explicitly qualified in owner evidence; neither is claimed repaired.
Published historical evidence/source hashes, dependencies and original document tails
pass preservation checks. Scope-only local commit excludes all concurrent changes.
