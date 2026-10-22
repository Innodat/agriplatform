---
title: 'Prepared corpus caller replay qualification'
type: 'feature'
created: '2026-10-22'
status: 'done'
baseline_commit: '92817f2673b3ca8aa308a413f70d68c6bd0b54a9'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/_bmad-output/specs/spec-scribeswell-studies/corpus-publication.md'
  - '{project-root}/apps/scribeswell/docs/MIGRATIONS.md'
---

<frozen-after-approval reason="bounded continuation authorized by the user's next instruction">

## Intent

**Problem:** A prepared corpus operator makes strict dormant replay fail. We need a closed prepared-state profile before qualifying active enforcement or coordinated release.

**Approach:** Add explicit controlled native0003 replay validation of prepared caller custody and least privileges, while enforcement remains off and history empty. Preserve default dormant/host behavior.

## Boundaries & Constraints

**Always:** Implement the canonical Prepared-controller replay contract and decision161 transaction closure. Expected custody is a closed version1 dict with source_id, executor_actor_id, actor_kind service, actor_key, preparation_evidence_ref. Match protected local records; the input is not Identity verification. Require existing exact0003, actual restricted migrator, original pinned catalogue plus only exact operator schema USAGE and two entry EXECUTE grants. Preserve all other ACLs/objects. Operator flags/memberships/settings/ownership/explicit and effective authority must remain narrowly isolated, including cross-owner grants without USAGE. Permit current disabled/revoked mappings without rewriting them. Require false enforcement and empty epoch/binding/attempt/outcomes. One writable READ COMMITTED transaction, statement5s/lock2s, fixed SHARE-table order prevent configuration/state changes and authority phantoms. Stable owner DDL/role window remains required.

**Never:** Modify applied revisions/references, prepare roles/actors/grants, enable enforcement, accept history, import scripture, call/import another owner's implementation or read Identity tables. No new CLI/environment/host selector, factory/Access/Leave change, production action, browser UX/signup change or competing workflow. Default dormant paths remain strict. No source scan/network under locks; no target-derived reference blessing, state repair or re-enablement.

## I/O & Edge-Case Matrix

| Scenario | Input/state | Expected | Failure |
|---|---|---|---|
| Prepared replay | explicit profile, matching custody, exact0003 and false/empty state | successful pre/post validation, unchanged state | safe fixed code |
| Default replay | prepared target, profile omitted or only ambient env hint | dormant path rejects | no mutation |
| Bad selection/custody | unknown/None profile, extra/missing/invalid fields, mismatch, orphan bundle | reject before effects | safe fixed identifier |
| Unsafe authority/drift | extra ACL/helper/table/column/sequence grant, settings, membership, owner or cross-owner privilege | reject | preserve target |
| Wrong lifecycle/history | earlier/absent ledger, controltrue, epoch/attempt/outcome/binding rows | reject | no adoption/cleanup |
| Configuration race | concurrent authority insert/update/control change | serialize within bounds or fail closed | no partial success |

</frozen-after-approval>

## Code Map

- `apps/scribeswell/migrations/baseline.py`: preflight contains authority, isolation, migration lock, ledger and strict dormant comparison. Extract only a shared checked-authority/ledger prefix with characterization protection; keep preflight(connection) public behavior/signature.
- `migrations/catalogue.py`: full snapshots include ACL text in schema[0][2] and function[6]; normalize only three allowed cells against exact grantor/grantability, never ignore ACL columns.
- `migrations/env.py`: native Alembic pre/post checks; Config attributes select explicit prepared mode, existing adapter/CLI remains dormant.
- `tests/test_owned_migrations.py`: prepared/business_state/invoke fixtures and old97 migration cases; preserve expectations.
- `tests/test_corpus_publication.py`: restricted synthetic operator mechanics only; its enabled fixture must be set false/empty for this profile.
- `deployment/Migrations.Dockerfile`: copies migrations directory; new helper is already included/fingerprinted. No image build claim or platform changes needed.

## Tasks & Acceptance

**Execution:**
- [x] `apps/scribeswell/tests/test_prepared_controller_profile.py` — characterize dormant behavior, observe actual prepared acceptance failure, cover matrix and state preservation.
- [x] `apps/scribeswell/migrations/prepared_controller.py`, `migrations/baseline.py` — closed custody/privilege/state validator and preflight_prepared(connection,expected_actor), reusing protected common checks.
- [x] `apps/scribeswell/migrations/env.py` — select Config attributes scribeswell_validation_profile=dormant|prepared-controller-v1 and scribeswell_prepared_actor; reject invalid combinations. Set scribeswell_validated_profile only after both checks; preserve revision evidence and rollback.
- [x] `apps/scribeswell/docs/PREPARED_CONTROLLER_PROFILE.md`, `docs/MIGRATIONS.md`, `docs/CORPUS_CONTROLLER.md` — explain controlled native use, custody limits, unchanged host gate and actual proof.

**Acceptance Criteria:**
- Given a qualified prepared disposable0003 fixture, when direct validation and explicit Alembic head replay run, then profile evidence appears only on success and catalogue/business rows/sequences/ledger/custody are unchanged; default replay still rejects.
- Given any matrix denial or injected post-check failure, when rehearsal runs, then no target repair, grant widening, early success or partial ledger effect occurs.
- Given concurrent local configuration writes, when the checker holds its declared locks, then writes wait or bounded failure occurs; previous reader/importer authority stays compatible.

## Implementation Notes

Root owns canonical/delivery records, fixture setup/shutdown and final verification. Agent owns listed app files only; no duplicate BMAD lifecycle or commit. Use `/tmp/scribeswell-studies-tests-py312/bin/python` and root-supplied disposable PG17 URL, sequential suites. Actual red before behavior; characterize before extracting existing checks. No skipped acceptance counts. Impact decisions: no scaffold/shared UI/agent-context/ADR promotion; app docs and canonical handoff updated. Existing host adapter has no selector for this profile and must continue failing prepared targets. Active enforcement/history release support, verified live custody and host integration remain explicit later gates.

## Spec Change Log

## Review Triage Log


| Finding | Verdict | Evidence / route |
|---|---|---|
| Root R1: vacuous rollback/source snapshots | medium | Empty business tables and UPDATE WHERE false could not prove preservation. Seeded real rows/sequences and actual postcheck mutation; corrected focused cases passed. Resolved before independent review. |
| Root R2: masked history cases | medium | Every early history case retained epoch, hiding later checks. Replaced with asserted epoch-only, history-without-epoch and stale-binding-only states. Resolved before review. |
| Root R3: PUBLIC nonordinary object rights | high | Actual restricted operator CREATE/DROP SERVER succeeded under harmless PUBLIC wrapper USAGE while checker passed. Five failing negatives then89 focused passes prove wrapper/server/tablespace/parameter fix. Resolved before review. |
| Blind B1: protected system routines | high | Root grant-only probe made pg_catalog.pg_read_file(text) executable through PUBLIC and checker still passed. No file routine was invoked. Patch current effective authority against trusted PostgreSQL initdb initial ACLs for protected core routines, preserving ordinary system functions. |
| Blind B2: PUBLIC default business grants | high | Root empty reachable-schema default SELECT-to-PUBLIC probe passed; future business rows would acquire unapproved rights. Patch consequential PUBLIC table/sequence default grants in reachable/global scopes; preserve ordinary default function/type behavior. |
| Blind B3: caller timeouts widened | medium | Unconditional SET LOCAL5s/2s overwrites shorter caller bounds. Patch ceilings preserving existing stricter nonzero bounds, with actual caller-setting regression. |
| Blind B4: direct search path | high | Root temporary pg_roles copy hid an actual CREATEDB operator flag and checker passed under public,pg_catalog. Patch supported local path pg_catalog,pg_temp before inspection; pg_catalog alone still implicitly searches temp relations first. Test temp-role and explicit reordered-path cases. |
| Blind B5: reordered equivalent ACLs | medium | Existing tests exercise exact cells and negative privileges but no equivalent textual reordering. Patch positive replay test reordering the three allowed ACL cells; no production surface change. |
| Blind B6: infinite timestamps | false | Both preparation tables already CHECK isfinite(created_at/updated_at), owned0003 lines18–19/29–30. ALWAYS attribution trigger overwrites server timestamps, and full pinned catalogue comparison rejects removal/disablement before local-state checks. Infinite stored values cannot occur in the accepted structural profile; no bypassing constraints to stage an impossible case. |
| Blind B7: COMMIT failure evidence | medium | Existing injected failure precedes context exit. Add commit-boundary fault proving no validated_profile and fixed safe failure, with meaningful state preservation. Production evidence assignment already follows commit. |
| Verification V1: fresh caller transaction | medium | Other tests cover non-RC/autocommit/read-only but omit fresh ordinary connection before begin/query. Removing first guard would permit autobegin. Patch exact transaction_required/no-autobegin test. |

Each independent finding was verified/classified before grouping. B1–B5/B7/V1
route to bounded patches/tests/docs without new public state; B6 is rejected on its
specific structural refutation. Edge lens returned[]; no deferred findings.
Two reviewers launched concurrently; host thread limit delayed the third until the
edge review completed. All three results were collected before triage. Root's three
additional grant/default/temp-shadow probes failed as expected1.05s and cleaned their
owned fixture. PostgreSQL-owned initdb ACL metadata was read without invoking any
file/administrative function; official pg_init_privs semantics:
https://www.postgresql.org/docs/17/catalog-pg-init-privs.html.

## Verification

Focused prepared-profile suite first, then owned migrations/controller/operator suites, then full `apps/scribeswell/tests`. Root independently reruns affected acceptance, deployment regression and composition check-only; verifies unchanged reference/revision/source/importer hashes. Record exact commands, results, matrix coverage, three-lens review and limitations. Baseline is recorded before implementation; preserve unrelated dirty files and exclude canonical untracked tree from scoped local commit.

Root pre-implementation checks: composition check-only passed with no changes;
platform deployment suite25 tests/42 subtests passed1.60s. Exact fixture:
`scribeswell-prepared-profile-20261022`, container
`e754ffec24d727087773db9755557dfac2353fcfc6c5a1cee5d9c4fc16493962`,
PG17 image `sha256:212aeeeb8faaef6c46498d86cbec6b9344d8d9492996b174664ff82c562ab685`,
loopback port32774; root owns cleanup. Initial actual acceptance/characterization:
`SCRIBESWELL_TEST_DATABASE_URL=postgresql://postgres:fixture@127.0.0.1:32774/postgres /tmp/scribeswell-studies-tests-py312/bin/python -m pytest apps/scribeswell/tests/test_prepared_controller_profile.py -q`
produced1 passed (default and ambient-hint dormant rejection preserves state),1 failed
(missing baseline.preflight_prepared),2.73s. A test-harness ORDER BY typo was corrected
before this valid red. No implementation behavior existed at that red.

Implementation progress evidence: initial prepared suite2 passed2.89s; expanded
suite80 passed15.17s. Sequential affected suites
`SCRIBESWELL_TEST_DATABASE_URL=postgresql://postgres:fixture@127.0.0.1:32774/postgres /tmp/scribeswell-studies-tests-py312/bin/python -m pytest apps/scribeswell/tests/test_owned_migrations.py apps/scribeswell/tests/test_corpus_publication.py apps/scribeswell/tests/test_corpus_operator.py -q`
passed313/no skips100.27s. Root audit identified empty-source/no-op rollback and
history masking in early tests; fixture now seeds real corpus/sequence values,
postcheck fault changes a real row, and epoch-only/history-without-epoch/binding-only
states assert distinct counts before rejection. Corrected focused suite81 passed
24.24s; two additional orphan/type-ACL cases bring current suite to83, pending full
regression. Direct validation rejects prior-query AUTOCOMMIT; configuration writer-first
failure is bounded/safe. All8 protected reference/revision/source/importer hashes
still match baseline. Root read the entire scoped implementation/test/document diff.

Initial full regression passed781/no skips192.24s with one existing Starlette/httpx
deprecation. Final focused83 passed18.07s, including importer no-op UPDATE control
FOR SHARE compatibility assertion strengthened after the full run collected tests.
Root then ran a harmless isolated privilege probe:
`SCRIBESWELL_TEST_DATABASE_URL=postgresql://postgres:fixture@127.0.0.1:32774/postgres /tmp/scribeswell-studies-tests-py312/bin/python -m pytest /tmp/test_scribeswell_prepared_root_probe.py -q`
failed1 case0.97s: PUBLIC foreign-wrapper USAGE allowed the actual restricted operator
to CREATE/DROP a handlerless foreign server while preflight accepted. The synthetic
wrapper/server and fixture were cleaned. This is a concrete effective-authority gap;
app-only predicates/tests for PUBLIC foreign wrapper/server, tablespace CREATE and
nonordinary parameter privileges are being added before independent review. No ALTER
SYSTEM, filesystem or external service operation was performed. Official privilege
reference: https://www.postgresql.org/docs/17/sql-createserver.html.


The PUBLIC effective-authority gap produced five failing regression cases and one
ordinary-setting compatibility pass2.72s. Added effective-privilege predicates for
wrapper/server USAGE, tablespace CREATE and nonordinary parameter privileges;
`GRANT` metadata tests execute neither ALTER SYSTEM nor external/filesystem work.
Final focused89 passed19.18s/no skips, preserving original83. Root's harmless CREATE/
DROP SERVER probe separately established the real missing authority. Profile89
cases and earlier affected313 now cover all matrix rows: positive/default replay,
closed selection/custody, exact and effective authority drift, wrong lifecycle/history,
configuration lock order/phantoms and writer-first bounded failure. Root reads the
complete final scoped diff before independent review. Full final regression remains
required after review fixes; earlier781 run predates six PUBLIC privilege cases.


Review resolution: B1–B5/B7/V1 are corrected; B6 remains refuted on the
immutable structural evidence above. Implementation focused105 passed20.78s/no
skips. Root independently ran the same105 plus four formerly failing concrete probes:
`SCRIBESWELL_TEST_DATABASE_URL=postgresql://postgres:fixture@127.0.0.1:32774/postgres /tmp/scribeswell-studies-tests-py312/bin/python -m pytest /tmp/test_scribeswell_prepared_root_probe.py apps/scribeswell/tests/test_prepared_controller_profile.py -q`
passed109/no skips24.71s. One cache warning reflects pytest choosing filesystem root
for the external /tmp probe; no acceptance case skipped. Root read all final
validator changes, new security/input/ACL/commit tests and app documentation.
The current full regression, rather than the earlier781 run, is the remaining check.


Exact earlier platform commands (unchanged platform code):
`python3 tools/py/run_compose_supabase.py --check-only` passed without changes;
`/tmp/scribeswell-studies-tests-py312/bin/python -m pytest platform/deployment/tests/test_release.py platform/deployment/tests/test_host.py platform/deployment/tests/test_migrate_adapter.py platform/deployment/tests/test_target_contract.py -q`
passed25 tests/42 subtests1.60s. Final scoped seven-file app diff is59430 bytes;
root reread final source, tests and documentation. Canonical check command
`python3 /tmp/scribeswell-publication-contract-check.py` passes9 planning documents,
11 capabilities,38 unique acceptance cases, companion discovery, local links and
whitespace; this checks documentation coherence only. Applied references/revisions,
source and importer all8 SHA256 values match the recorded baseline; pre-existing
AGENTS.md and Scribeswell README bytes match their initial dirty state. Concurrent
KDG commits fba2b27 and7c0bac5 are retained and excluded from this delivery.


Final root verification after all review patches:
`SCRIBESWELL_TEST_DATABASE_URL=postgresql://postgres:fixture@127.0.0.1:32774/postgres /tmp/scribeswell-studies-tests-py312/bin/python -m pytest apps/scribeswell/tests -q`
passed803/no skips184.47s. One existing Starlette/httpx deprecation only. This
includes all105 prepared-profile cases and retained698 application regressions.
Every frozen matrix row and all three acceptance criteria are covered by the105
profile tests listed above; full regression also includes owned migrations/controller/
operator and actual reader/importer suites. Seven independent findings corrected,
one refuted, no deferrals. Code/test bytes remained unchanged during root verification.
No image build, browser/provider, live custody, production preparation/adoption or
active/history release qualification is claimed. No platform/scaffold/shared-UI/
agent-context/ADR changes required; app docs and canonical evidence updated.

The exact owned PG17 fixture was stopped and removal verified after final tests.
Final canonical coherence/preservation, protected8/final-code4 hash checks passed.
Pre-existing dirty canonical tree and unrelated owner changes are excluded from the
scoped local commit; no push/deploy.
