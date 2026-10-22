---
title: Verified Scribeswell owned migration baseline
type: feature
created: 2026-10-22
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: 10b7c7fbf57eaf7c3160212f9b08dedf1bf65114
context:
  - AGENTS.md
  - _bmad-output/specs/spec-scribeswell-studies/corpus-publication.md
  - platform/docs/architecture/decisions/0016-owned-migration-histories-and-coordination.md
---

<frozen-after-approval reason="User next authorizes the next bounded BMAD delivery under existing owner boundaries">

## Intent

Scribeswell lacks an owned migration history needed for controlled writer-fence delivery. Adopt the existing supported corpus schema into a verified application-owned Alembic baseline and register its bounded migration runner with the existing host coordinator.

## Boundaries & Constraints

Always verify the independently pinned legacy SQL/direct-role-bootstrap catalogue before ledger DDL, including safe pre-provisioned migration authority, object ownership, ACL/default ACL and existing ledger. Reverify on replay, serialize and bound execution, preserve previous reader/importer behavior and data/sequence state. Owner-only ledger, safe diagnostics and actual release evidence are mandatory.

Never create corpus objects/data, provision/transfer roles/ownership, edit legacy/bootstrap SQL, stamp blindly, downgrade, migrate at API startup, activate a production release, implement fences/publication, change other owners or implement Access/Identity/Leave/factory. Preserve dirty files, especially app README and other sessions. No remote operations.

## I/O & Edge-Case Matrix

| State | Required outcome |
| --- | --- |
| Exact supported prepared schema | Upgrade records scribeswell_0001, owner-only ledger; rows/IDs/sequence state/reader and importer access unchanged. Replay revalidates and succeeds. |
| Missing/partial/drifted catalogue, policy/ACL/default ACL, unsafe authority or ownership | Fail before ledger DDL, no changes; safe error. Reference is never generated from the target. |
| Existing empty/malformed/multiple/unknown ledger | Fail closed; do not stamp, normalize or overwrite. |
| Concurrent adoption or held lock | Serialize safely; bounded timeout rolls back, retry succeeds after release. |
| Unsupported Alembic command/offline | Reject before mutation. |
| Bad project/URL, hostile ambient PG configuration, DB failure/worker timeout | No unsafe target substitution or secrets; bounded cleanup, safe failed/unknown evidence, activation blocked; no automatic reversal. |
| Host group succeeds/fails after earlier owners | Actual per-owner evidence retained; failure prevents activation. |

</frozen-after-approval>

## Code Map

- `apps/scribeswell/supabase/migrations/20260614000000_scribeswell_create_schema.sql` and `deployment/bootstrap/001_direct_database_roles.sql`: immutable reference inputs, SHA256 b5140822e9655b933a98f17df8b7a7cb8424246991e168238ba736a319b511f0 and d03e8e34227fe73d0572d74e9c799a76982ed6ec83a774fec86e2c757d54c66d. Five tables/views, four serial sequences; bootstrap grants and RLS preserved. Legacy default privileges originate with bootstrap owner (fixture postgres); unsupported profiles fail pending explicit qualification.
- New app `alembic.ini`, `migrations/` guard/catalogue/reference/revision, `deployment/migrate.py`, migration requirements/Dockerfile. Existing `backend/database.py` URL validation can be reused locally; do not import importer (loads dotenv) or another owner implementation. Pure `platform/deployment/target_contract.py` is approved utility for production project checks.
- `services/access/identity-migrations/env.py` is a reference pattern only: validate in engine transaction before Alembic ledger, block unsupported operations, revoke inherited default ledger grants before commit. No cross-owner imports.
- `platform/deployment/registry.json` and app `deployment/manifest.json`: add scribeswell-owned group/owner with separate credential env. Existing `release.py`, `host-release.py` already coordinate multiple groups; no new generic coordinator required. Host fixture assumptions in `platform/deployment/tests/test_host.py` are currently pts-only; update fixtures to derive registered groups, preserve current tests and add new owner failure evidence. `test_release.py` asserts group ownership.
- `apps/scribeswell/tests/test_postgres_acceptance.py`: guarded unique local fixture database with known-absent roles; migrate tests must explicitly guard new role absence and drop only owned fixture resources. Test-only ownership preparation, independently built reference and data setup are permitted. Do not run shared PostgreSQL role fixtures concurrently.

## Tasks & Acceptance

- [x] Observe relevant acceptance red before implementation; add focused unit tests and real PostgreSQL acceptance for every matrix row.
- [x] Implement adoption-only baseline with complete catalogue/role/ownership/ACL comparison against an independent pinned supported reference, ignoring volatile OIDs/current sequence values. Reject extra unsupported objects. A generated reference needs its owning generator and documented reproducible fixture derivation; never snapshot/bless target.
- [x] Guard actual session_user/current_user = scribeswell_migrator, LOGIN without super/bypass/createdb/createrole/replication or unsafe memberships. Verify schema/relation ownership before ledger. Lock/statement/idle timeouts and advisory transaction lock; validate known ledger shape, ACL and single known revision. Reject stamp/downgrade/offline/other commands, including programmatic entry. Postconditions run in transaction; rollback failure. No corpus mutation.
- [x] Implement bounded app-local subprocess adapter (180s maximum migration workflow including DNS/connect/inspection), safe project/URL validation, strip ambient PG* options, no dotenv/raw exception/credential output. Before/after evidence obtained inside bounded execution, committed success only. Reserve create-only evidence before database work, preserve prior files; timeout kill/reap and mark unknown outcome for reconciliation.
- [x] Add separate nonroot migration image/dependencies and host registration. No runtime migration dependencies/startup hook. Test host activation blocking on new group failure and earlier owner evidence retention.
- [x] Document supported profile, explicit target role/ownership prerequisites, operational schema-stability window, rehearsal/recovery and production gates in app-owned migration/deployment docs. Record exact red/green and compatibility verification. Root owns canonical handoff and final commit.

Given the exact prepared legacy schema, upgrade and replay must preserve corpus rows, sequence values, grants and existing actual PostgreSQL reader/importer tests. Given rejected adoption, no ledger or business changes may be committed. Given a failed/unknown new owner migration, existing host release cannot activate.

## Implementation Notes

Intent gaps: none. Schema-only technical ledger, no actor/business record creation. Scaffold/shared UI/agent-context/ADR impacts: no reusable generator/UI/context change; consume existing release tooling and ADR-0016/0017/0020, record app adoption pattern only. Factory belongs to separate session. App documentation updates required; no new/superseding ADR needed.

Root owns disposable PostgreSQL17 container scribeswell-corpus-migrations-20261022, ID edc32375a5c44e22b7c6911090f0539c87157c69d17598c06d535cf2c4b4f1ea, image sha256:212aeeeb8faaef6c46498d86cbec6b9344d8d9492996b174664ff82c562ab685. Local fixture URL postgresql://postgres:fixture@127.0.0.1:32769/postgres via SCRIBESWELL_TEST_DATABASE_URL only. Agent may run guarded tests outside sandbox; root stops exact container. No other containers/credentials. Python3.12 /tmp/scribeswell-studies-tests-py312/bin/python includes pytest, psycopg, Alembic1.20.1, SQLAlchemy2.1.6 and app test dependencies. Canonical untracked specs tree excluded from commit.

## Verification

Run smallest failing migration acceptance, focused tests, actual PostgreSQL migration acceptance, affected platform deployment tests, full apps/scribeswell/tests (previous160), then python3 tools/py/run_compose_supabase.py --check-only. Record exact results and skips. Localhost/TestClient tests require escalation in this sandbox. No browser change or browser verification expected.

Root host/release baseline before registration: `/tmp/scribeswell-studies-tests-py312/bin/python -m pytest platform/deployment/tests/test_release.py platform/deployment/tests/test_host.py -q` — 16 passed, 18 subtests (0.52s). ATDD registration red: new `test_scribeswell_has_one_separate_owned_migration_group` fails 0 != 1 before registry change. Catalogue JSON fingerprint red: changing reference bytes leaves identical fingerprint before fix; after narrow inclusion of migration `.json` alongside `.py`, focused case passes. Actual first consumer requires this existing release-tool correction; no new coordinator.

Root intermediate platform regression: `/tmp/scribeswell-studies-tests-py312/bin/python -m pytest platform/deployment/tests/test_release.py platform/deployment/tests/test_host.py platform/deployment/tests/test_migrate_adapter.py platform/deployment/tests/test_target_contract.py -q` — 23 passed, 31 subtests, 0.65s. Host tests prove new-group failure after earlier owner success blocks compose and preserves actual per-owner evidence; project/role/missing-key refusals occur before effects. `python3 tools/py/run_compose_supabase.py --check-only` passes, no files changed. Migration/backend implementation verification remains pending.

## Spec Change Log

## Review Triage Log

Implementation agent frozen after final focused real PostgreSQL verification: 72 passed, no skips (37.22s), existing Starlette/httpx warning. Exact command: `SCRIBESWELL_TEST_DATABASE_URL=postgresql://postgres:fixture@127.0.0.1:32769/postgres /tmp/scribeswell-studies-tests-py312/bin/python -m pytest apps/scribeswell/tests/test_owned_migrations.py apps/scribeswell/tests/test_postgres_acceptance.py -q`. Full app suite before last three catalogue/authority cases: 212 passed, no skips, 85.58s; final full regression remains root responsibility. Independent reference generator `--output /tmp/scribeswell-owned-reference-reproduced.json` and byte `cmp` both exit 0. PG17 profile is explicit fail-closed; no image build or production rehearsal/activation claimed.


### Independent review triage

| Finding | Verdict | Evidence and route |
| --- | --- | --- |
| B1 disabled internal FK triggers | high | Catalogue excludes all internal triggers and has no enabled-state field; DISABLE TRIGGER ALL leaves constraint definitions unchanged. Patch normalized constraint-trigger state and prove rejection, regenerate only from pinned fresh fixture. |
| B2 PUBLIC external column grants | high | Effective table privileges exclude column-only access; explicit column ACL branch checks actor OID only. Patch effective external column privilege query and real regression. |
| B3 PUBLIC external SECURITY DEFINER execution | high | Existing function branches inspect ownership/explicit grants, omitting effective PUBLIC execution through usable external schema. Patch that demonstrated authority and regression. |
| B4 PUBLIC database CREATE | medium | Existing database ACL branch checks explicit actor only; effective PUBLIC CREATE permits schema creation. Patch effective database privilege check and restore fixture grants. |
| B5 foreign-owner default ACL grants to migrator | medium | Current query checks global defaults owned by migrator, not grantees of other owner defaults. Future external tables gain authority undetected. Patch relevant default ACL grantees and regression. |
| B6 future revisions cannot pass baseline guard | false | This item deliberately implements adoption-only scribeswell_0001; future DDL must extend owned revision-aware validation/runner as its own bounded change. No forward revision is shipped or promised executable here. Existing history is the owner location, not automatic acceptance of future schema. |
| B7 incomplete compatibility fingerprint | medium | New image adapter/validator/dependency/Dockerfile inputs affect adoption behavior but are outside existing migration history fingerprint. Patch existing registry with explicit compatibility input paths and hash registered image Dockerfiles; first consuming app supplies inputs, no new coordinator. |
| B8 safe before observation discarded on worker failure | medium | Worker replaces all failures with a code-only response even after config records before revision. Patch retain validated known-before evidence while after/outcome remains uncertain; do not infer rollback. |
| B9 upgrade target not enforced | medium | Command-kind guard accepts upgrade base on an already adopted database. Documented supported target is head. Patch exact target check for CLI/programmatic calls and regression. |
| B10 importer/sequence compatibility absent | false | Existing test_postgres_acceptance now adopts before yielding. test_interrupted_chapter_rolls_back_then_replays_and_extra_rows_fail executes real importer default-ID writes and retries; test_actual_roles_deny_other_owners_and_runtime_writes checks denied runtime writes. Both ran in root full215. No duplicate test needed. |
| E1 disabled FK triggers | high | Same verified cause/outcome as B1; grouped patch. |
| E2 PUBLIC external column privilege | high | Same verified cause/outcome as B2; grouped patch. |
| V1 post-ledger rollback untested | medium | Pre-verified search finds only preflight rejection and successful commit tests. Add actual PostgreSQL injected post-migration validation failure; observe created ledger before fault then verify absent ledger and unchanged corpus from separate connection. Patch tests. |

All surviving entries are demonstrated states within the existing contract; smallest fixes add catalogue/authority predicates, exact target validation, safe evidence handling and regression coverage without a new product/API surface. Existing release metadata receives explicit first-consumer input paths. No intent gap, redesign or deferred finding. Root pre-patch full regression: 215 passed, no skips, existing Starlette/httpx warning, 93.30s; patches require final rerun.


### Review fixes and focused evidence

Same implementation agent patched all surviving findings. Before patch, actual PostgreSQL command `SCRIBESWELL_TEST_DATABASE_URL=postgresql://postgres:fixture@127.0.0.1:32769/postgres /tmp/scribeswell-studies-tests-py312/bin/python -m pytest apps/scribeswell/tests/test_owned_migrations.py -q -k 'reviewed_authority or public_database_create or nonhead or postvalidation or failed_worker'` produced **9 failed, 1 passed, 55 deselected (4.87s)**. The postvalidation rollback test already passed with its strict expectation; all nine demonstrated guard/evidence failures were fixed without weakening assertions.

Final focused command with the same fixture env/interpreter: `-m pytest apps/scribeswell/tests/test_owned_migrations.py -q` — **71 passed, no skips/warnings, 46.30s**. Independent `generate_reference.py --output /tmp/scribeswell-owned-reference-review-fixes-reproduced.json` and byte comparison to the checked-in reference both exit0. Only independently built pinned SQL fixtures generated the reference; no target-derived blessing or hand edit.

Root supplemental R1 (medium, patch): mock timeout did not prove actual migration-backend cleanup. Added real supervised worker blocked on held owner advisory lock, observed its backend, timed out/killed/reaped it, then verified backend disappearance while lock still held, absent ledger and unchanged corpus. Safe unknown/reconciliation evidence is asserted. This is in the 71-case focused run and final full suite.

Root compatibility-image input red: new test changing each Dockerfile/adapter/validator/dependency input produced five subtest failures plus missing-input failure before hashing was extended. Current registry names app input files, host hashes migration Dockerfiles and those inputs, and release validation rejects unsafe/missing paths. Final affected platform command `/tmp/scribeswell-studies-tests-py312/bin/python -m pytest platform/deployment/tests/test_release.py platform/deployment/tests/test_host.py platform/deployment/tests/test_migrate_adapter.py platform/deployment/tests/test_target_contract.py -q` — **25 passed, 42 subtests, 0.84s**. No new coordinator, scaffold generator or runtime engine.

| Requirement / matrix | Covering actual tests |
| --- | --- |
| Exact baseline and replay preserve corpus/sequence/access | upgrade_and_replay_preserve_rows_sequences_and_access; all existing PostgreSQL reader/importer acceptance now run after adoption. |
| Missing/partial/catalogue/ownership/ACL/default ACL drift | rejects_drift_before_ledger; missing_partial_or_extra_authority; reviewed_authority_and_trigger_gaps_reject_before_ledger; public_database_create_rejected. |
| Malformed/unknown ledger and replay drift | rejects_existing_unqualified_ledger; replay_rejects_ledger_drift; postvalidation_failure_rolls_back_created_ledger confirms created ledger rollback from separate connection. |
| Concurrency and bounded waits | concurrent_upgrades_serialize; lock_timeout_then_retry; actual_worker_timeout_reaps_and_releases_transaction. |
| Unsupported native/programmatic operations | rejects_unsupported_commands; programmatic_unsupported_routes; offline_upgrade_rejected_before_mutation; nonhead_upgrade_rejected_cli_and_programmatic. |
| Configuration, hostile environment, safe unknown failures | ambient_pg_does_not_redirect; adapter_safe_evidence_and_stripped_environment; adapter_rejects_bad_configuration_before_worker; adapter_timeout_kills_reaps_and_marks_unknown; actual_database_connection_failure_safe_evidence; real_supervised_worker_records_committed_before_after; malformed/failed-worker observation cases. |
| Existing evidence preserved | adapter_safe_evidence_and_stripped_environment refuses reusing completed destination before worker launch. |
| Host migration evidence/activation | scribeswell_failure_retains_prior_group_success_and_blocks_activation; existing host timeout/network/recovery suite; new role/project/key preflight cases; owned-group coverage and compatibility-input cases. |

Root read the task-only unified diff including untracked implementation files, then rewrote and read the review-fix delta. Pre-existing unrelated changes and canonical planning tree are excluded. All accepted findings resolved; false B6/B10 have concrete scope/test refutations above; no deferred findings. No further review loopback or intent gap.


## Final verification and release boundary

Root final command, outside sandbox for localhost PostgreSQL/TestClient access:

```sh
SCRIBESWELL_TEST_DATABASE_URL=postgresql://postgres:fixture@127.0.0.1:32769/postgres timeout 180 /tmp/scribeswell-studies-tests-py312/bin/python -m pytest apps/scribeswell/tests -q
```

**231 passed, no skips, 95.34s; one existing Starlette/httpx deprecation warning.** All 71 new migration cases and all previous160 application regressions ran. Existing PostgreSQL acceptance fixture now adopts the supported baseline before exercising actual importer writes/default IDs/rollback, denied runtime writes, RLS, public API/lexicon/reader behavior, bounds and connection reuse. No unchanged browser/build tests rerun or claimed. No affected app-wide lint/type-check command exists.

Affected platform checks: **25 passed, 42 subtests, 0.84s**, exact command above. Final `python3 tools/py/run_compose_supabase.py --check-only` passes; it composes the unchanged15 legacy SQL files and changes nothing. Source schema/bootstrap pins remain unchanged. Independent reference comparison, task `git diff --check`, canonical19 companion links and stable11 CAP/38 ST IDs all pass. All accepted review findings resolved; nothing deferred.

Root stopped exact owned PostgreSQL17 container `edc32375a5c44e22b7c6911090f0539c87157c69d17598c06d535cf2c4b4f1ea` successfully after final checks; --rm removes the memory-backed fixture. No other container/service or production target touched. No push, deploy, production ownership/grant preparation, schema adoption or publication activation occurred. Migration image is authored but not built; target profile, image qualification, representative rehearsal and controlled release remain gates.

This delivery implements only adoption of the supported PostgreSQL17/postgres-bootstrap catalogue into scribeswell_0001. It deliberately leaves writer fencing, sealed full audit, publication/reader evidence and private Studies persistence unimplemented. Future owned revisions must extend revision-aware guards/adapter before shipping. Access enrollment stays with its owner session; standalone account entry remains implemented with its earlier live signup activation gates. Leave/factory implementation remains outside scope.

Impact decisions: scaffold/shared UI/agent context unchanged; existing host coordinator gains proven first-consumer compatibility input paths, not another lifecycle/generator/runtime. App migration/deployment documentation is updated; accepted ADRs unchanged and consumed directly. Canonical updates stay in pre-existing untracked specs tree and are excluded from the scoped commit, consistent with earlier slices. Pre-existing app README and all other sessions' changes remain untouched. Concurrent builder commits including8f14364 and bedf73a are preserved atop the recorded baseline, with no reset/rebase.
