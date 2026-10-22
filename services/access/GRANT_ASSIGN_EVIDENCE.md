# Protected organization grant assignment —2026-10-22

This delivery implements the existing Access owner command, not a new administration
service or an effective access reader. An explicitly authorized operator assigns one
registered organization capability to the exact verified account/membership. Access
checks current command/org/app/account policy; Identity supplies the current member and
account-actor projection without requiring any existing grant. Preparation can occur
with disabled admission. Activation still requires current protected readers and the
coordinated consumer release. PtS remains account-scoped; preserving old PtS org writes
is not a requirement.

Baseline666211dfecb2bf3a255277941aeff81781d926be. Root preservation snapshot
/tmp/grant-assign-preservation.json records54 immutable historical migration/reference
files,77 baseline production sources and concurrent observed bytes. Scope excludes
production/real accounts or access, provisioning, deployment, pilots, Leave/editor,
reset/prune/cleanup and push. Existing dependencies including TypeScript7.0.2 remain.

## Acceptance ordering

Before production edits, a fresh root-owned grant-assign-red-20261022 database installed
Identity19 and controlled Access12. The actual restricted access_operator connection
passed session identity checks, then the valid parsed assignment body failed with
command_unsupported before opening a business transaction. Exact before/after snapshots
matched. Expected RED exit1 is recorded in grant-assign-20261022/root-acceptance-red.log.
The frame and all older resources/data are preserved.

Focused agent missing-feature RED failed3 tests (head13, missing migration, exact grant
column dependency recognition). Root client RED independently failed3 routing/receipt/
lookup tests, with15 other negative checks passing. New execution replaces only formerly
unsupported Access expectations; Identity continues to reject all Access command bodies.
An initial client regression exposed changed timing of malformed lookup operation IDs;
validation ordering was corrected to retain previous safe wire behavior rather than
changing the expected result.

## Delivery impacts

Scaffold: extend existing controlled owner migration, exact catalog, adapter, CLI and
qualification seams. No new generator, runtime service or generic fixture framework.
Shared UI: none. Agent context: none. Documentation: owner runbook/evidence and mutable
shared substrate/deployment/KDG handoff. ADR: existing ownership, release safety,
transaction boundaries, attribution, structural integrity and safe logging decisions;
no accepted ADR edits. Existing owners retain schema/client/generator/test/runbook work.

The following sections preserve acceptance ordering and early diagnostics; final
reviewed-source results are recorded separately below. Early diagnostic migration is
not aggregate acceptance. Private bootstrap portability and full logical-restore qualification remain
explicit existing limits; no portable CI or backup/restore success is implied.


## Early native findings and corrections

Early clean13 smoke failed safely with42501. A fresh safe diagnostic selected only
exception class/SQLSTATE; source tracing identified trigger creation after premature
PUBLIC EXECUTE revocation. Matching existing0009's trigger-before-revoke order fixed
this; fresh smoke2 clean13 catalog/migration passed. All earlier frames remain retained.
First source-bound nine-case proof passed actual grant create/replay/lookup/noop/private
observation/audit, then stopped when its authority test tried to mutate immutable policy
identity. Production refused correctly. The qualifier now retains mappings, inserts
separate policies and changes enabled only; no production guard was weakened.

A root commit-boundary probe observed a real gap: statement-time checks alone allowed a
direct transaction to wait beyond the5s observation lifetime before commit. First sleep
probe hit its5s SQL timeout and rolled back; after verifying no grants remained, an explicit
bounded retry used two2.6s statements and observed a committed expired observation (RED).
Scripts/logs and synthetic committed diagnostic state remain retained. New0013 extends
the existing deferred outcome/event guard to refuse stale grant.assign outcomes with
AC004, including unchanged/no-event receipts; existing five-command semantics remain.
Native created/noop delayed-commit cases assert complete rollback. This is the controlled
adapter/deferred transaction contract; arbitrary SQL forcing constraints early is not an
unforceable PostgreSQL commit hook claim. No external reads or new framework were added.

Root client315 checks passed; agent affected133 checks passed after deadline/test-isolation
corrections. Earlier full Access1508 PASS predates this final correction and is not final
acceptance. Subsequent fresh source-bound proofs and independent retained evidence follow below.


Proof2 passed first-grant, exact authority and retry/recovery stages, then its isolation
negative test encountered a fixture ordering failure: the shared refusal helper issued
set_config before SET TRANSACTION ISOLATION LEVEL. Only that probe now passes context=None,
so isolation is first SQL and the assignment routine can produce expectedAC005. No
production/helper behavior or expected result changed. Proof2 remains retained; proof3
uses fresh namespaces after this direct correction. Static/focused11 checks pass.


Proof3 passed ten native stages, including both expired-commit rollback paths, before
a drift probe attempted ALTER FUNCTION as migrator rather than its restricted owner.
The production ownership boundary correctly refused42501. The fixture now assumes
access_command_owner only for that ALTER, resets role before preflight and rolls back
the whole probe. Fresh proof4 retains all prior frames unchanged.

Affected regression command (prepared Python below) passed1518 tests in55.01s:
`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$PYTHON" -I -B -m pytest services/access/tests apps/pts/tests/test_release.py platform/deployment/tests/test_migrate_adapter.py -q -p no:cacheprovider`.
Both `$PYTHON -B tools/py/run_compose_supabase.py --check-only` and
`$PYTHON -B tools/py/run_compose_supabase.py --identity-authority owned --no-seeds --check-only`
exited0. Root logs remain in ignored grant-assign-20261022 diagnostics.

## Requirement-to-test mapping

| Requirement | Independent behavior evidence |
| --- | --- |
| Exact account/member, disabled-admission preparation, server executor | functional stage and closed adapter/CLI tests |
| Current command/org/app/account policy, spoof/raw writer denial | authority_and_identity and guards stages |
| Expected state/noop, retry identity, exact lookup | functional, retry_and_recovery and concurrent retry stages |
| Fresh observation, retirement/rejoin, no automatic authority transfer | freshness_and_retirement plus delayed created/noop commit rollback |
| Narrow DML, atomic outcome/event, no partial effects | guards snapshots and deferred_observation_commit |
| Concurrent expected absence, bounded locks and revocation after wait | concurrency and freshness_and_retirement |
| Populated12→13, opaque IDs, creation/history/overflow, five old clients | upgrade_previous and exact catalog tests |
| Migration failure/recovery, drift, Identity metadata compatibility | rollback_recovery and catalog_and_identity |
| Supported real operator CLI and exact recovery flags | cli plus malformed closed client/worker unit cases |
| Source/input/log/state custody before independent DB inspection | source-bound all, separate retained invocation and root final audit |

PYTHON=platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python.


## Current native result

Fresh `grant-assign-proof4-20261022` passed all13 stages. Separate
`--verify-retained` invocation passed read-only exact13 inspection of all nine databases.
Root independently checked128 source hashes,24 qualification diagnostic hashes, generated
inputs/bootstrap logs and retained-state digest;54 historical sources remain unchanged.
Only the six intended existing production sources changed.

Exact native commands (outputs in grant-assign-20261022):

```sh
F=platform/deployment/.local/identity-baseline/grant-assign-proof4-20261022
PYTHON=platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python
"$PYTHON" -I -B "$F/bootstrap_run.py"
ACCESS_QUALIFICATION_DIR="$F" "$PYTHON" -I -B "$F/root_qualification_driver.py"
ACCESS_QUALIFICATION_DIR="$F" "$PYTHON" -I -B services/access/tests/qualify_grant_assign.py --verify-retained
```

Bootstrap/full/separate-retained all exit0. The root driver invokes the same qualifier
main with --all, selecting safe failure diagnostics only. Review, final stop/custody and
local commit follow; no effective reader or consumer activation claim is made.


## Review disposition

Three independent context-free lenses completed (sequential due the session thread
limit): blind10 findings, edge1 finding, verification-gap1 finding. The spec triage
records a verdict/evidence for every finding before grouping duplicates. Accepted
corrections extend the existing qualification paths and clarify the supported/default-
deferred transaction guarantee; no production privilege expansion, new API, framework
or ADR is required. No finding is deferred. Final corrected-source verification remains
required below; proof4 is historical once its captured qualifier/runbook sources change.

The early-constraint limitation is explicit: an arbitrary direct SQL caller can force
deferred checks early and later delay commit. The supported adapter rejects a caller-
owned transaction, does not force early checks and commits immediately under bounded
budgets. The delayed-commit test proves ordinary deferred transaction rollback, not an
unforceable PostgreSQL hook against arbitrary transaction control.


## Reviewed-source final verification

The same implementation agent applied the accepted test/runbook corrections;12 focused
tests and compilation passed. Production source hashes are unchanged from proof4. The
final source-bound frame is `grant-assign-final-20261022`, freshly bootstrapped with only
seven source/private template files copied (no generated credentials, state or logs).
Commands match the proof4 commands above with F changed to this final frame; root output
logs are root-bootstrap-final.log, root-all-final.log and root-retained-final.log.

Final affected regression uses the exact pytest command above:1519 PASS53.60s, recorded
in root-regression-final.log. Both previously recorded composition checks remain exit0
against the same production source; no dependency/composer change followed review.
Final native/retained completion, normal stop and custody audit are recorded below.


Final reviewed-source native run passed13 stages; separate --verify-retained exited0
with exact read-only inspection of all nine cases. Root independently matched128
sources,24 generated qualification diagnostics, bootstrap logs/generated inputs and
retained-state digest. Final production bytes equal the successful proof4 production
bytes; review changed only qualifier/tests/runbook. All12 individually triaged findings
were addressed through the existing owner seams; no deferral or unreviewed scope growth.

Normal stop used the existing lifecycle:

```sh
"$PYTHON" -B platform/deployment/dev.py stop \
  --target platform/deployment/environments/kdg-local.json \
  --run-id 99b7231c-0a5b-4bdb-98e8-3329564c526a \
  --supabase /home/ck/repos/innodat/agriplatform/platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/supabase/supabase
```

Exit0, code=completed, stage=stop, runtime_ready=false. Database data/volumes, receipts
and all historical diagnostic frames are retained; no reset/prune/recovery cleanup.

Final root audit passed:24 owned paths,54 immutable historical/reference sources,71
unchanged baseline production files and six intentionally changed current owner sources.
Frozen intent digest is unchanged. Original tracked concurrent documents match their
starting bytes; concurrent Scribeswell untracked documents evolved and new assets/reviews
appeared independently. They are recorded and excluded from the scoped commit, never
restored or staged. The ignored root-final-evidence.json binds final owned/source/input/
log/state hashes and concurrent observed bytes; its commit field is added after commit.

Next bounded command: protected organization grant revocation. Effective membership-safe
readers, ACCESS-B and coordinated KDG/PtS/Content/corpus adoption remain subsequent work.
No real account/access, production migration, provisioning, deployment or pilot occurred.
