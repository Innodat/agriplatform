---
title: Dormant Scribeswell transaction-bound writer fence
type: feature
created: 2026-10-22
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: 0720203627714a93f9b0c8f65538d93d31fea393
context:
  - AGENTS.md
  - _bmad-output/specs/spec-scribeswell-studies/corpus-publication.md
---

<frozen-after-approval reason="User next continues authorized bounded BMAD implementation; activation and shared-owner work remain gated">

## Intent

Install a dormant database writer-fence foundation through the existing owned history, preserving working public reading/imports while qualifying transaction-bound generation protection needed for ST-38.

## Boundaries & Constraints

Always implement the canonical dormant-expansion contract. Ship enforcement false, empty business gate/bindings, owner-only structures/routines, unchanged corpus grants/data/IDs/sequences/importer/API. Guard all five tables and serialize control/generation transitions. Keep original0001 revision/reference/source pins unchanged; exact revision-aware pre/post verification and bounded safe adapter advance together.

Never activate production enforcement, ship importer EXECUTE grants, seed real actors/attempts, implement begin/recovery/sealing/publication commands, modify legacy bootstrap, query Identity tables or implement Access/Leave/factory. Preserve dirty work and app README; no push/deploy.

## I/O & Edge-Case Matrix

| State | Required behavior |
| --- | --- |
| Exact legacy or0001 schema | Transactional upgrade to0002, dormant compatibility, exact replay. |
| Drift/unknown ledger or injected post-DDL failure | Fail safely; no partial migration or changed corpus. |
| Ordinary roles | No private table/routine access or owner assumption. |
| Disabled enforcement | Existing writes work; control share lock blocks concurrent enable until transaction ends. |
| Synthetic enabled gate and valid bound import transaction | Only matching updating epoch permits writes; generation/state changes wait for write transaction. |
| Missing/stale/closed/forged context; later transaction/pool reuse | Fixed safe denial, no write. Commit/rollback leave no bindings. |
| COPY/upsert/zero rows/INSERT/UPDATE/DELETE/TRUNCATE across five tables | Same fence boundary; existing narrower corpus grants still apply. |
| Adapter failure/timeout | Validated known-before revision only, uncertain after, activation blocked; no raw exceptions/secrets. |

</frozen-after-approval>

## Code Map

- `apps/scribeswell/migrations/`: add revision0002 DDL; extend `baseline.py`, `env.py`, `catalogue.py`, `generate_reference.py`. Existing ledger checks and safe roles/timeouts remain. Existing functions catalogue only names; add full security representation. Blanket owner-function rejection must permit only exact owner-local catalogue functions. Preserve `reference.json`; generate a separate head reference from pinned fresh fixture plus actual new DDL, never a target. Keep default legacy-reference reproduction compatible; add explicit head selection.
- `deployment/migrate.py`: new supported before/head revisions in success and safe failure paths, same180s supervisor. Existing image copies migrations, host fingerprints their Python/JSON; no new coordinator/registration needed.
- `tests/test_owned_migrations.py`, `tests/test_postgres_acceptance.py`: guarded PostgreSQL fixtures, real importer/runtime regressions. Characterize revision1 before refactoring. Add `tests/test_corpus_writer_fence.py` for enforced fixture-only cases. New catalogue profiles must not change expected old source/reference bytes.
- `deployment/bootstrap/001_direct_database_roles.sql`: immutable baseline reference, rejects importer SECURITY DEFINER grants. Ship no new grant; fixture-only grant/revoke qualifies future transition without breaking legacy bootstrap regression tests.
- `docs/MIGRATIONS.md` and new `docs/CORPUS_WRITER_FENCE.md`: document executable foundation, technical attribution exemptions, exact dormant boundary and future activation prerequisites. Root owns canonical updates and this delivery record.

## Tasks & Acceptance

- [x] Observe missing-fence acceptance red; characterize existing0001 behavior before changing revision dispatch.
- [x] Implement owner-private control/defaultfalse, empty attributed singleton epoch gate and transient actual-login/PID/full-xid8 context. Binding routine checks exact approved tuple; owner-only EXECUTE. Deferred commit cleanup and rollback remove context. Fixed safe errors/search paths and revoked default privileges.
- [x] Add all-table statement guards, control FOR SHARE even disabled, epoch FOR SHARE while enabled, consistent lock order. No caller GUC authority or long external waits.
- [x] Extend exact revision-aware catalogue/generator/adapter with immutable old profile and independently reproduced head. Verify control/gate/binding dormant postconditions, routine definitions/privileges and triggers; reject drift before mutation and fault after DDL to prove rollback.
- [x] Run every matrix case on actual PostgreSQL17, using only explicit synthetic gate actors and fixture-only importer EXECUTE/activation. Prove concurrent generation and dormant-enable ordering, direct alternate DML, rollback/pool reuse and restricted-role denials. Re-run affected existing migration/importer/reader/auditor suites without weakening expectations.
- [x] Update app runbooks with exact commands/results and remaining owner/actor/writer/release gates; record scaffold/UI/context/ADR impacts.

Given dormant head, old importer and public reader remain compatible. Given synthetic enforcement, only the current matching write transaction proceeds; no stale or forged binding survives transaction boundaries. Given migration failure, host activation remains blocked and prior successful owner evidence survives.

## Implementation Notes

Intent gaps: none. No irreversible target actions: only app code/DDL artifacts and disposable tests. Actor registry exists under Identity, but no approved Scribeswell actor projection/caller binding exists. Consume contracts later; no production actor seeds now. Control is technical release configuration and context is transient coordination (ADR0025/0056 explicit exemptions); epoch business rows have actor/UTC fields but remain empty in shipped migration.

Scaffold/shared UI/agent-context: none; existing owned-release pattern. Documentation required; accepted ADRs unchanged. Broader actor/publication/importer transition is separately gated, not a missing part of this dormant slice.

Fixture: root-owned PostgreSQL17 container `scribeswell-corpus-fence-20261022`, ID b8ff80fd60567b6eb1e4837e50e8ac0b10d65aff8eddce284f5d1bbf3a1c0fd4, localhost32770, fixture URL postgresql://postgres:fixture@127.0.0.1:32770/postgres via SCRIBESWELL_TEST_DATABASE_URL. Interpreter /tmp/scribeswell-studies-tests-py312/bin/python has all dependencies. Agent may run guarded tests outside sandbox; no concurrent role fixtures; root stops exact container. No other containers/credentials. Root retains canonical untracked specs outside scoped commit.

## Verification

Smallest acceptance red, focused guard/migration checks, full `apps/scribeswell/tests -q` with real fixture (prior231), independent old/head reference reproduction, affected platform deployment tests and composition `python3 tools/py/run_compose_supabase.py --check-only`. Record exact commands/results; skipped DB cases are not acceptance. No browser change/test expected. Root final regression follows review patches.

## Spec Change Log

## Review Triage Log


## Verification evidence in progress

Pre-change PostgreSQL17 characterization: `SCRIBESWELL_TEST_DATABASE_URL=postgresql://postgres:fixture@127.0.0.1:32770/postgres /tmp/scribeswell-studies-tests-py312/bin/python -m pytest apps/scribeswell/tests/test_owned_migrations.py -q` — **71 passed, 43.47s**. An attempted overlapping fixture run was safely refused by the known-role guard; it is not acceptance red. After the fixture released, missing-fence acceptance failed on `UndefinedTable corpus_fence_control` (**1 failed, 0.71s**) before implementation.

Enabled matrix initially passed43/44: COPY exposed the existing PostgreSQL RLS rejection before trigger execution. Its test now preserves shipped COPY denial, temporarily disables only fixture book RLS to exercise the underlying fence, then restores RLS in finally; production permissions/RLS remain unchanged. Focused migration/fence suites then passed **134 tests, 69.83s**. Full regression and independent reference reproduction remain pending; root requested populated migration fixture restoration after scope changed module→function, plus one actual committed5-table write/cleanup case. These strengthen existing preservation evidence without changing expected results or production code.

Implementation frozen after populated-preservation and committed-write strengthening: focused migration/fence suite136 passed64.92s. Earlier full295 passed125.19s before final added tests; root final full remains pending. Independent original/head reproduction both cmp exit0; original revision/reference/bootstrap/source diff clean. Legacy reference SHA25610ac1f9f5060093e248fb1ed6987cfa24136b6c0662280bcc0dbdccbc0ea3dbf; head a446ef7ff8de5adc7bd7163c99affdd71850341bca962963c76458d54bf6019f. Fixture roles/databases cleaned and released.


### Independent review triage

Edge-case and verification-gap lenses returned no findings. Blind finding floor10 produced the following individually verified findings:

| Finding | Verdict | Evidence / route |
| --- | --- | --- |
| B1 dormant real importer write absent | false | Existing test_postgres_acceptance fixture upgrades head before exercising test_interrupted_chapter_rolls_back_then_replays_and_extra_rows_fail, including real seed/import upserts with shipped login and no binding grant. Full295 run included it; source importer unchanged. No duplicate needed. |
| B2 transition-first waiting binder missing | medium | Current concurrency tests start writer first; row-lock revalidation after an earlier generation/state transition is not exercised. Add real inverse ordering and old-tuple denial, fresh tuple success where applicable. Patch tests. |
| B3 savepoint lifecycle missing | medium | Current finish variants cover commit/rollback/early constraints only. Add real rollback of binding inside savepoint and preservation when binding precedes a later savepoint. Patch tests. |
| B4 disconnect cleanup missing | medium | Existing rollback/commit cases retain live client; no actual close with active bound write and waiting owner. Add disconnect rollback/data/context/lock-release evidence. Patch tests. |
| B5 repeat binder conflict branch missing | medium | Binder has ON CONFLICT DO UPDATE, but every test calls it once per transaction. Add identical rebind, committed business effect and no retained binding. Patch tests. |
| B6 guard actual-owner login branch missing | medium | Owner login binder denial exists; enabled direct owner DML is untested. Add direct owner write denial, preserving existing narrow grants. Patch tests. |
| B7 new structural invariant cases missing | medium | Source-label CHECK tested; generation, UUID, checksum/state and singleton constraints are untested. Add parameterized rejected synthetic rows with no residue. Patch tests. |
| B8 cleanup-trigger replay drift missing | medium | Generic catalogue records cleanup metadata, but only fence-trigger mutations are executed in replay tests. Add disabled/timing-altered cleanup rejection without mutation. Patch tests. |
| B9 concurrency future timeout can leave blocking thread | medium | Owner connections lack statement/lock timeout; executor exit waits after client Future timeout. Add bounded DB waits and cancellation/cleanup in these new concurrency cases. Patch tests. |
| B10 head generation provenance wording | low | MIGRATIONS.md says generator executes only pinned inputs without distinguishing --head's actual reviewed0002 DDL. Direct doc correction distinguishes paths and release fingerprint; patch. |

All survivors are demonstrated test/wording gaps within the settled contract, adding no public surface or production state. Root will correct B10; same implementation agent patches tests B2–B9 after root full regression releases shared fixture. No bad-spec/intent gap or deferred findings. Production migration DDL need not change unless new tests expose a concrete failure.


### Review closure and traceability

The same implementation agent patched B2–B9 in the two affected test files only; root corrected B10 provenance wording. Focused command `SCRIBESWELL_TEST_DATABASE_URL=postgresql://postgres:fixture@127.0.0.1:32770/postgres /tmp/scribeswell-studies-tests-py312/bin/python -m pytest apps/scribeswell/tests/test_corpus_writer_fence.py apps/scribeswell/tests/test_owned_migrations.py -q` passed **161 tests, no skips/warnings, 72.34s**. New cases exposed no production defect and required no DDL/routine change. Original independent references remain byte-identical, with root comparison against their reproduced SHA256 values passing.

Root intermediate full regression before review additions: same fixture env/interpreter with `timeout240 -m pytest apps/scribeswell/tests -q` — **296 passed, no skips, 123.45s**, one existing Starlette/httpx deprecation. Affected platform command `/tmp/scribeswell-studies-tests-py312/bin/python -m pytest platform/deployment/tests/test_release.py platform/deployment/tests/test_host.py platform/deployment/tests/test_migrate_adapter.py platform/deployment/tests/test_target_contract.py -q` — **25 passed, 42 subtests, 0.96s**. Composition check-only passed without changing files. Final application regression follows the test-only review patches; unchanged platform behavior needs no duplicate rerun.

| Requirement / matrix | Actual covering cases in affected suites |
| --- | --- |
| Legacy/0001 upgrade and dormant compatibility | revision_one_catalogue_profile_is_unchanged_and_upgrades; upgrade_and_replay_preserve_rows_sequences_and_access with all5 populated tables/nondefault sequences; existing actual PostgreSQL importer/reader suite runs after head migration. |
| Safe drift and failed expansion rollback | head_replay_rejects_fence_drift_without_mutation covers search path/security/ACL/fence trigger/cleanup timing/control/epoch; post_ddl_failure_preserves_revision_one; existing initial-adoption rollback/authority/ledger tests retained. |
| Owner-only structures and actual login | shipped_private_access_denied; actual_login_required_even_with_execute; owner_direct_corpus_dml_has_no_import_login_authority across5 tables/all4 operations. No ordinary caller grant shipped. |
| All-table operations and exact tuple | every_statement_operation_requires_binding; exact_approved_tuple_required; copy_and_upsert_share_fence (shipped RLS denial preserved, test-only adjustment restored); closed_stale_missing_epoch_denied; missing_control_fails_closed_even_dormant. |
| Transaction context safety | guc_copy_and_other_backend_have_no_authority; binding_dies_at_transaction_boundary_and_pool_reuse; savepoint_rollback_removes_new_binding; savepoint_rollback_preserves_earlier_binding; committed_bound_business_writes_survive_binding_cleanup includes repeated binder and real committed FK chain; disconnect_rolls_back_bound_write_and_releases_waiting_owner. |
| Concurrent transitions | epoch_transition_waits_for_bound_write; dormant_writer_holds_control_until_commit; transition_first_waiting_binder_rechecks_committed_epoch. Actual pg_blocking_pids observation, finite owner SQL waits and cancellation/cleanup qualify both orderings. |
| Structural protection | epoch_source_label_matches_evidence_namespace; epoch_structural_constraints_reject_invalid_rows; control_and_epoch_singletons_reject_second_rows. |
| Safe adapter/release | adapter_supports_both_known_before_revisions; failed_worker_preserves_valid_known_before includes0001/0002; existing real worker timeout/backend cleanup and host migration-failure/partial-evidence activation-blocking tests retained. |

Root wrote/read the task-only unified diff including new files and compact full-reference additions, then rewrote/read review-fix delta. All matrix rows have executed covering tests; no skipped checks count as evidence. All accepted review findings resolved; B1 disproved by actual prior importer tests; edge/verification lenses empty. No deferred findings or scope/intent gap. Review fixes changed tests and documentation only.


## Final verification and release boundary

Root final command, outside sandbox for localhost PostgreSQL/TestClient access:

```sh
SCRIBESWELL_TEST_DATABASE_URL=postgresql://postgres:fixture@127.0.0.1:32770/postgres timeout 240 /tmp/scribeswell-studies-tests-py312/bin/python -m pytest apps/scribeswell/tests -q
```

**321 passed, no skips, 130.95s; one existing Starlette/httpx deprecation warning.** Includes all 161 focused fence/migration tests and the previous importer/runtime/reader/lexicon/source/auditor regression surfaces. Platform checks passed 25 tests, 42 subtests, 0.96s with the exact command above. Composition check-only passed and changed nothing. Original revision/reference/bootstrap/source bytes match baseline 0720203; independent old/head reference SHA256 values match reproduced assets. Task whitespace and canonical companion/ID/link checks pass.

All matrix rows have actual passing tests, including enabled fixture-only operations, committed FK-chain data surviving context cleanup, both generation/control lock orderings and rollback/disconnect cleanup. Copy acceptance preserves shipped RLS rejection and qualifies the underlying trigger only under a temporary restored fixture adjustment. Existing full-source auditor remains historical publication-false evidence; no sealing or current publication assertion is added.

Root stopped exact owned PostgreSQL17 container `b8ff80fd60567b6eb1e4837e50e8ac0b10d65aff8eddce284f5d1bbf3a1c0fd4` successfully after verification; --rm removes its memory-backed fixture. No other service/container or production target touched. Migration image was not built or deployed; target role/ownership/profile/rehearsal/adoption remain gates. No browser files changed, so no browser/build test claimed; no affected app-wide lint/type-check command exists.

Implemented behavior: dormant owner-private control/epoch/context structures and ALWAYS guards, exact revision-aware migration/replay/adapter, independent catalogue and executable fixture qualification. Shipped state remains enforcement false, empty epoch/bindings and owner-only routine EXECUTE. No real actors/attempts, importer grant/transition, begin/recovery/sealing/publication commands, ready-reader proof or private Studies persistence. Full ST-38/D-2/D-5 remains open. Standalone account entry and its live provider activation gates are preserved; Access enrollment belongs to its separate implementation session.

Scaffold/shared UI/agent-context: no change or reusable promotion. Existing owned migration/release coordination is reused; no additional framework or lifecycle. Application migration/fence runbooks updated, canonical contract/acceptance/brownfield handoff derived through bmad-spec. ADR0025/0056 technical control/transient-context exemptions are explicit; empty epoch business rows retain required actor/UTC fields for later owner-qualified commands. Accepted ADRs unchanged. No Leave/factory/Identity/Access implementation or table access.

Only this delivery's app/test/docs/record files enter the local commit. Pre-existing app README and other sessions' modifications remain untouched; canonical updates remain in the pre-existing untracked specs tree and are excluded from commit, as in preceding slices. No push or production activation.
