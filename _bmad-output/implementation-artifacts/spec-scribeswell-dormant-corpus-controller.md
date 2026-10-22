---
title: Dormant transactional Scribeswell corpus controller
type: feature
created: 2026-10-22
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: 0467248f45580dc640058e693ba9499ebca8d1e2
context:
  - AGENTS.md
  - _bmad-output/specs/spec-scribeswell-studies/corpus-publication.md
---

<frozen-after-approval reason="User next authorizes bounded BMAD implementation, with production activation and shared-owner work gated">

## Intent

Implement the canonical Dormant executable controller contract: actual short transactional begin/recover/seal commands and durable authorized replay, with a Python qualifier-to-SQL adapter. Preserve working public reading/imports while proving the next ST-38 prerequisite.

## Boundaries & Constraints

Always follow the exact canonical controller record/routine/receipt/lock/bounds/replay contract. Ship0003 with empty protected controller state, false enforcement and owner-only routines; no ordinary grants/actors/roles. Preserve0001/0002 revision/reference and source/bootstrap bytes. Keep singleton corpus; actual-session dedicated operator mapping consumes externally verified Identity actor custody. Fixture actors are synthetic only. Atomic attempt/epoch/outcome; source qualification outside DB locks. Preserve all dirty work, app README, other owner sessions and canonical untracked tree.

Never activate/provision a live caller/actor/target, alter importer/corpus data/API, expose CLI/HTTP, implement Access/Identity/Leave/factory, add fingerprints, seal audit or publish ready proof. No long source/network wait in transaction, startup migration, blind stamp/reversal, push/deploy or hand-edited reference JSON. Migration replay stays explicitly dormant-only; active release profile/supervised operator transport remain gates.

## I/O & Edge-Case Matrix

| Scenario | Required behavior |
| --- | --- |
| Exact earlier profiles/head | Upgrade/replay0003 atomically, dormant legacy compatibility, old reference bytes unchanged. |
| Missing/drifted structure/authority/post-DDL fault | Fail without changed corpus/partial ledger; safe adapter known-before evidence. |
| Shipped ordinary roles | No controller table/EXECUTE/owner rights; enforcement remainsfalse and tables empty. |
| Fixture actual restricted operator + exact current principal/source-command | Parser/full source then atomic begin1, recover fresh generation/attempt, seal closed; actor/UTC/history/receipt accurate. |
| Missing/revoked/unsafe/rebound actor mapping, wrong-source/command, GUC/SET ROLE spoof | Safe denial; no change or historical receipt leakage. |
| Matching retry/lookup after subsequent transitions | Original committed receipt only; never reapply/reactivate. Changed semantic input conflicts; missing outcome returnsNone. |
| Stale/pre-existing/cross-source/sealed mismatch/overflow | Conflict without partial mutation. |
| Concurrent retries/begins, writer-first/transition-first recovery and seal, authority revocation | Serialized current authority/tuple decisions, bounded waits, stale workers deny, no binding residue. |
| Transaction fault/rollback/uncertain result; invalid/nonidle/isolation/response | Atomic rollback or safe unknown-outcome reconciliation; receipt only after successful commit; source parsing precedesSQL. |

</frozen-after-approval>

## Code Map

- `apps/scribeswell/migrations/versions/0003_corpus_controller.py`: additive owner-only DDL/routines, canonical structures and SQLSTATE contracts. Existing0002 guards/binder untouched. Head function catalogue already captures definitions/security.
- `migrations/baseline.py`: explicit profile mapping0001/0002/0003 and dormant state checks; preserve existing role/ledger/cross-owner guards. `generate_reference.py`: explicit revision selection generates ordered actual DDL from guarded pinned fixture. Preserve default/--head old behavior; new reference-controller.json for0003. `deployment/migrate.py`: new known before/head, same supervisor/evidence semantics.
- New `backend/corpus_publication.py`: existing strict corpus_publication_input qualifier/parser plus psycopg bound JSONB calls; caller-owned idle connection and finite SQL waits, frozen safe receipts/errors. No connection/credential/CLI management.
- New `tests/test_corpus_publication.py`: guarded actual PostgreSQL fixtures, absent dedicated operator role, temporary grants/principal stand-ins, actual adapter/transaction/concurrency and direct routine negative paths. Existing `test_corpus_writer_fence.py` remains standalone0002 foundation compatibility; no new epoch FK that invalidates its synthetic state.
- `tests/test_owned_migrations.py`: retain populated corpus/sequence characterization; add explicit0002→0003 upgrade, new table/function/ACL drift and rollback/adapter evidence. Existing hardcoded0002 adapter assertions must target new head without weakening prior profiles.
- New `docs/CORPUS_CONTROLLER.md`, update `docs/MIGRATIONS.md`: executable protocol/actual evidence/dormant boundary/operational gates. Root owns canonical and delivery record; implementer owns app docs/code/tests.

## Tasks & Acceptance

- [x] Characterize prior migration behavior, observe actual missing-controller acceptance red, then focused TDD.
- [x] Implement protected mappings/attempt/outcome constraints, safe native validation and current-authorization locked command/lookup routines; all canonical replay/state/concurrency semantics.
- [x] Implement source-qualified adapter and validated postcommit frozen receipts; safe errors, nonidle/isolation guards and finite SQL waits.
- [x] Advance exact owned revision/reference/generator/adapter safely; independently reproduce all three pinned profiles, rollback and dormant replay, unchanged source/legacy behavior.
- [x] Execute every matrix row on real PostgreSQL, including direct alternate calls, actual committed outcomes/revocation, both writer/transition orderings and injected rollback. No skipped acceptance.
- [x] Document actual commands/results, scaffold/UI/context/ADR impacts and remaining owner/activation/transport/sealed-audit/publication gates.

Given supported dormant schema, when upgraded, then prior public reading/importing still works. Given fixture current authority and full source, when command commits, then exactly one attributed transition/outcome exists. Given stale/forged/revoked authority or repeated old command, then no unauthorized transition/old-state reactivation occurs. Given failure, then durable evidence is preserved and activation remains blocked.

## Implementation Notes

No intent gaps or irreversible target actions: app artifacts and disposable qualification only. Canonical contract makes internal choices. Scoped native controller is one goal; production caller provisioning/operational migration/outer supervisor is deliberately separate and not claimed. Scaffold/shared UI/agent-context: no new pattern promotion; reuse owned release coordination. Documentation required; accepted ADRs unchanged.

Root-owned fixture: PostgreSQL17 container0026a36a501610087e7005908474be91a15e25cb51f2293e2cb7b5cd156a4b5c, image sha256:212aeeeb8faaef6c46498d86cbec6b9344d8d9492996b174664ff82c562ab685, localhost32772. Use SCRIBESWELL_TEST_DATABASE_URL=postgresql://postgres:fixture@127.0.0.1:32772/postgres and /tmp/scribeswell-studies-tests-py312/bin/python. Escalated local test access permitted; no overlapping DB fixture suites on same cluster. Root stops exact container. Keep app docs reproducible via existing app-local environment, session paths in this record only.

## Spec Change Log

## Review Triage Log

## Verification

Smallest actual red→focused controller and migration suites sequentially→full apps/scribeswell/tests with fixture; affected platform deployment tests if adapter changes; composition check-only; independent0001/0002/0003 reference reproduction; source/revision/profile immutability, task whitespace and canonical link/ID preservation. Exact results required, no browser/build/image/production claim. Root runs final full regression after independent BMAD review fixes.

## Verification evidence in progress

Actual PostgreSQL acceptance red before implementation: test_controller_ships_empty_and_dormant failed UndefinedTable corpus_operator_principal (1 failed, no skip). Initial sandbox networking denial was resolved by the normal escalated local-fixture test route; it is not the acceptance failure. Before editing baseline/generator dispatch, the implementation agent characterized prior0002 head with the not-yet-registered0003 file temporarily outside Alembic versions and restored it immediately: same explicit fixture environment/interpreter, pytest tests/test_owned_migrations.py::test_upgrade_and_replay_preserve_rows_sequences_and_access -q passed1 test1.09s, and ::test_revision_one_catalogue_profile_is_unchanged_and_upgrades -q passed1 test1.15s. This preserves populated corpus/sequence and exact original-profile evidence before refactoring revision dispatch. No production state touched.

Root composition `python3 tools/py/run_compose_supabase.py --check-only` passed without file changes. Final full regression/reference reproduction/review remain pending.


Implementation frozen for independent review. Agent focused controller63 passed4.89s; migration97 passed82.85s; initial full app545 passed/no skips131.53s (one existing Starlette/httpx deprecation). Final whitespace-only DDL cleanup regenerated0003 reference via its generator; post-generation focused64 passed5.49s. All three references independently generated from fresh guarded fixtures and cmp pass:0001 SHA10ac1f9f5060093e248fb1ed6987cfa24136b6c0662280bcc0dbdccbc0ea3dbf,0002 SHAa446ef7ff8de5adc7bd7163c99affdd71850341bca962963c76458d54bf6019f,0003 SHA28ff9fab8ebfd9d83cde1e7510150cb65462edcb295489a858aebfa3ba653d0a. Root read task-only unified source/test/runbook diff and generated-reference structural delta: only four new tables, six indexes,47 constraints, five owner-only functions, four ALWAYS protection triggers and12 FK triggers; old corpus/profile definitions untouched. Root independently checked matrix coverage against executed controller/migration tests; three-lens review and root final regression follow. No production actor/caller/activation or source audit proof.

### Independent review triage

All three review lenses completed before triage. Blind finding floor165.17kB→10 produced10 findings; edge returned none; verification returned2 independently searched gaps. Host thread limit delayed the third fresh reviewer until earlier reviewers completed; all three were launched/collected before classification, with no reviewer given another's findings.

| Finding | Verdict | Evidence / route |
| --- | --- | --- |
| B1 injected outcome failure only begin | medium | Current injected trigger test hits initial insertion only; manual rollback covers all variants but not an error after recover/seal writes. Add injected failure variants with complete predecessor-state snapshots. Test patch. |
| B2 malformed receipts only incomplete | medium | Four current response fixtures fail shape before identity/generation/state branch guards. Add otherwise valid receipts mutated at each guarded field, then assert rollback/unknown_outcome. Test patch. |
| B3 direct native validation begin only | medium | Byte-parser tests cover variants, but native execute is independently callable with typed JSONB. Current native mutants are begin-only. Add recover/seal negative IDs/generations/closure/identity cases. Test patch. |
| B4 no explicit native request size guard | medium | Closed fields already bound valid semantic inputs, but oversized direct JSONB still enters detailed validation without the declared65536-byte guard. Add a small early semantic-size predicate and direct oversized rejection case; no new public surface or valid state. Code/test patch and regenerate0003 profile only. |
| B5 rejected operation tests compare counts only | medium | Counts cannot detect unintended edits to existing epoch/attempt/outcome. Snapshot full records around rejected operations. Test patch. |
| B6 competing recovery/seal interleavings untested | medium | Current tests prove initial begin serialization, not recovery/recovery or recovery-first/seal. Add actual blocked competing transitions. Refute proposed blanket one-winner rule for seal-first/recover: canonical recovery accepts closed predecessor, and existing committed-history test already proves both can validly commit in that order. Preserve that accepted behavior; test both orderings. |
| B7 revocation-first wait/revalidation absent | medium | Existing revocation tests acquire execution/lookup shares first; row-lock revalidation after a prior uncommitted disabling update is not observed. Add principal/authority and execute/lookup inverse ordering. Test patch. |
| B8 shipped function ACL test checks execute only | medium | Generated profile captures all owner-only functions, but native privilege assertions omit lookup/internal/validation/protection helpers. Add exact signatures for all controller functions. Test patch. |
| B9 record-protection branches sampled narrowly | medium | Current tests exercise outcome mutation, one attempt identity and principal key only. Add immutable creation attribution, nonincreasing revision, authority key, terminal lifecycle and retained attempt deletion cases with no residue. Test patch. |
| B10 runbook words join numbers/identifiers | low | Root runbooks contain the0002/timeout5s/version1 and error identifiers adjoining prose. Direct formatting correction by root; no behavior change. |
| V1 recovery never changes approved identity | medium | All existing recoveries reuse source bytes/labels, so copying predecessor identity could pass. Add new qualified source and labels, old-history preservation, new attempt/epoch identity and new-checksum-only binding. Test patch. |
| V2 seal rejection checks only tokenization | medium | Dropping another approved identity comparison can evade current mismatch test. Parameterize all four fields, with valid alternate source/checksum so input qualification reaches SQL, then full-state preservation. Test patch. |

Keep findings individually logged. Group B1/B5 by insufficient rejected-transition state observation; B3/V2 by native/identity rejection coverage only where the same tests are extended; all others retain their separate root causes. All survivors route to small patches within demonstrated state and existing contract. B10 is root-owned; same implementation agent handles tests and B4 guard/regeneration. No intent gap, contract reversal or deferred finding; seal-first/recover success must survive.

### Review closure and final traceability

Same implementation agent resolved B1–B9/V1/V2 with complete state snapshots, injected rollback across all3 commands, otherwise-valid receipt mutants, native recover/seal negatives, four identity comparisons, changed qualified recovery input/new-checksum binding, competing transition and inverse revocation orderings, all5 function ACL checks and protected-record branches. B4 adds one native65536-byte JSONB-text size predicate; no other production behavior changed. Owning generator independently reproduced current0003 reference to /tmp/scribeswell-controller-review-reference.Qt8qw3/reference-controller.json; cmp and root byte comparison pass, SHA78f23cb01e2b91ff963bfc249631f8317b6c09ed9e41f45fd44abc72e8563d9a. Old profiles/revisions/source/bootstrap remain unchanged. B10 runbooks corrected by root. No deferred finding or contract change; seal-first then recover remains valid.

Focused post-review command, explicit fixture environment/interpreter below with `-m pytest apps/scribeswell/tests/test_corpus_publication.py -q`:132 passed7.37s. Root noticed B2 had replaced the earlier four incomplete-response cases; the same agent restored them alongside the new value cases. Final focused command passed**136 tests, no skips,7.55s**. Only tests changed after root full collection; no production/reference change.

Root full regression after production review patch:

```sh
SCRIBESWELL_TEST_DATABASE_URL=postgresql://postgres:fixture@127.0.0.1:32772/postgres timeout 300 /tmp/scribeswell-studies-tests-py312/bin/python -m pytest apps/scribeswell/tests -q
```

**614 passed, no skips,130.73s**, one existing Starlette/httpx deprecation. Final focused command:

```sh
SCRIBESWELL_TEST_DATABASE_URL=postgresql://postgres:fixture@127.0.0.1:32772/postgres /tmp/scribeswell-studies-tests-py312/bin/python -m pytest apps/scribeswell/tests/test_corpus_publication.py -q
```

**136 passed, no skips,7.55s** includes the four restored malformed-response cases after full collection. Current collection-only command `python -m pytest apps/scribeswell/tests --collect-only -q` using the same interpreter reports**618 tests collected0.53s**. Full614 plus final focused136 covers all618 current cases (132 repeated controller cases,4 restored additions); no claim of a single full618 execution. Source/implementation unchanged between those runs, so no redundant full repetition.

Root affected-platform command `/tmp/scribeswell-studies-tests-py312/bin/python -m pytest platform/deployment/tests/test_release.py platform/deployment/tests/test_host.py platform/deployment/tests/test_migrate_adapter.py platform/deployment/tests/test_target_contract.py -q`:**25 tests,42 subtests passed0.98s**. Composition check-only passed with no writes. No app browser/build/image test or production action claimed.

| Matrix requirement | Actual executed coverage |
| --- | --- |
| Earlier profiles/dormant head/compatibility | Existing populated upgrade/replay/read/import tests plus revision_two_profile_upgrade_and_rollback; full app passes against0003. All3 independent generator profiles match, default/legacy selector preserved. |
| Drift/rollback/safe adapter | controller_head_drift_blocks_replay across ACL, routine, trigger, FK and nonempty state; revision_two post-DDL fault; retained adoption/ledger/authority/timeout tests; all-known-before adapter cases. |
| Shipped private structures/routines | controller_ships_empty_and_dormant; shipped_roles_have_no_controller_privileges covers all5 functions/all ordinary roles; operator_direct_table_access_denied and owner-assumption denial. |
| Qualified execute/history/attribution | committed_history_replay_and_attribution; recovery_replaces_approved_identity_and_only_new_checksum_binds; all3 command results and stored actor/revision evidence. |
| Current authority/role/forgery | current_authority_gates_historical_receipts; unsafe_actual_role_denied flags/memberships; missing_mapping_disabled_fence_and_forged_session; live_login_revocation; both revocation orderings and lookup shares. |
| Original/changed retry and lookup | committed_history replay after later transitions; changed semantic request full-state preservation; concurrent same operation; inflight lookup; simulated COMMIT-response loss after actual durable commit and authorized lookup. |
| Stale/cross-source/sealed/overflow/identity | conflicts_are_atomic full-record snapshots; overflow guard; each_seal_input_mismatch_reaches_sql across all4 fields; native negative begin/recover/seal and native size bound. |
| Concurrent state/writer/current authority | pg_blocking_pids observed both writer/transition orders for recover/seal, distinct absent begins, competing recover/recover and both recover/seal orderings, operation-first and revocation-first principal/authority execute/lookup. All waits/cancel cleanup finite. |
| Rollback/invalid response/connection | injected outcome failure all3 transitions; explicit rollback all3; complete stored-state preservation for every rejected command/response; incomplete and valid-shape value mutants; nonidle/serializable/source-invalid guards, direct authority2s bound and unknown-outcome reconciliation. |

Root read task-only source/test/runbook diff and final review-fix delta, including generator-owned reference witness comparison. All matrix rows have executed tests with no skipped acceptance. Every independent finding is logged/resolved, nothing deferred. Owner/current-authority boundary and exact semantic replay remain unchanged by testing improvements.


## Completion and remaining release boundary

All tasks and matrix cases verified; no skipped acceptance, unresolved review finding or deferral. Root stopped exact owned disposable container0026a36a501610087e7005908474be91a15e25cb51f2293e2cb7b5cd156a4b5c successfully; --rm removes memory-backed fixture. Canonical coherence/preservation,19 companions,11 CAP/38 ST IDs, authored links and task whitespace pass. Root byte-compared8 immutable source/importer/bootstrap/revision/reference paths against full baseline0467248f45580dc640058e693ba9499ebca8d1e2. Final controller reference independently matches generator witness SHA78f23cb01e2b91ff963bfc249631f8317b6c09ed9e41f45fd44abc72e8563d9a. Root read restored4-case delta; earlier negative protection remains alongside stronger tests.

Implemented: dormant0003 native execute/lookup, protected service-executor/exact-source authority, attributed attempt/outcome persistence, exact semantic retry, source-qualified postcommit adapter and revision-aware controlled migration/reference evidence. Tests enable synthetic fixture authority only. Shipped state remains enforcementfalse, empty controller/epoch state, owner-only functions and no operator role/grants/actors. No production role/actor/target setup, active-state migration profile, outer supervised operator invocation, importer transition, sealed complete-source audit/attestation, manifest activation, ready-reader proof or private Studies persistence. SQL bounds do not claim transport/COMMIT deadlines. Identity verification stays owner-controlled external preparation; Access remains its separate KDG session. Standalone account entry/provider gates, accepted UX and Leave/factory boundaries are preserved.

Scaffold/shared UI/agent-context: no change/promotion; reuse existing owned release coordination. App controller/migration runbooks and canonical corpus/brownfield/acceptance updated; accepted ADRs unchanged. Next bounded work closes supervised caller/target/verified-actor preparation and supported active release-state evidence before writer activation, then complete sealed audit/publication/reader proof. No competing shared runtime or app factory lifecycle introduced.

Local commit includes only10 task app files plus this delivery record. Pre-existing app README, other sessions and canonical updates inside the pre-existing untracked specs tree remain excluded/preserved, consistent with earlier deliveries. No push/deploy or production service touched.
