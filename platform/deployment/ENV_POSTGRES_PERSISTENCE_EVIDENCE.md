# PostgreSQL named-volume persistence evidence

Build: [bounded ENV persistence](../../_bmad-output/implementation-artifacts/spec-env-postgres-volume-persistence.md).
Bounded runtime persistence verification passes on the final source. Three-layer
review and patches are recorded below; full environment readiness remains false.

## Purpose and boundary

The previous [pinned-CLI execution proof](ENV_PINNED_CLI_EXECUTION_EVIDENCE.md) removes
its fresh named volume at the first clean shutdown. This item retains that volume
only inside the same guarded operation, replaces the container and verifies committed
synthetic data/cluster identity. It does not adopt a volume from another execution,
qualify the full CLI initialized branch, or enable public up/stop/reset.

The existing ENV owner, DockerSession, profile, bootstrap/archive authority and
startup qualifier retain ownership. No generator, offline service or production
runner is introduced. Exact approved baseline includes TypeScript7.0.2.

## Source grounding

Docker's [versioned API1.48 schema](https://raw.githubusercontent.com/moby/moby/v28.0.0/docs/api/v1.48.yaml)
defines detached exec start and JSON exec inspection. The closed control requests no
attached streams, admits only fixed predicate commands, and checks identity/config,
completion and integer exit zero. Completed exec PID alone is not a completion rule.
No raw-stream/hijack transport is added.

Root read the retained selected-image entrypoint audit at
`.local/postgres-source-audit/46880d40-9483-4485-96c6-ca5b211d21f7/docker-entrypoint.sh`:
PG_VERSION sets DATABASE_ALREADY_EXISTS; image initialization scripts run only when
that flag is empty. Recreating a container still rewrites its container-local bootstrap
files, and the public root-key file must be copied again. Persistence requires actual
data checks after replacement, not an inference from that source branch.

## Impact decisions

Scaffold: extend existing ENV lifecycle/transport/qualification owners and their tests;
P1/SERVICE generator remains a later existing-owner gate. Shared UI: no change.
Agent context: root rules suffice; consuming handoff records actual commands/limits.
Documentation: source-bound profile, runbook, this requirement/test evidence, KDG
handoff/memlog and Build record. ADR: accepted decisions unchanged. ADR0020 owner
migration/release compatibility and recovery remain undelivered gates; the isolated
qualification probe is test data, not a product migration. ADR0023 selected diagnostics
exclude SQL output, runtime payloads and credential dumps.

## Remaining acceptance

Cross-execution initialized-volume admission/reconciliation, full CLI/stack runtime,
owner migrations/fixtures/current authorization, public lifecycle/recovery,
provider/device and P1/SERVICE generation remain open. Identity/Access/WRITE and KDG
server work stay gated. No Leave/editor, production migration, app grant/account,
infrastructure provisioning, deployment or real-data pilot action is authorized here.

## Focused implementation verification

Implementation observed persistence acceptance RED before production changes, then
GREEN. Root `python3 -m unittest discover -s platform/deployment/tests -p test_pinned_execution.py`
passes **39 tests,0.422s**. New cases cover retained-volume replacement, fixed SQL,
exec identity/exit/order, lost marker/cluster/initialization, consumed uncertain
mutations, changed resources/references, fixed replacement deadline and no replay.
Existing27 focused cases retain their expectations.

First affected supervisor run passes **5 tests,25.484s**, but its original new negative
fixture failed before verification exec start; this is not proof of a missing-marker
SQL rejection. Root identified the seam. The corrected independent daemon models
committed marker/cluster/initialization and applies verification failure only after
exec start. Both direct/process negative cases now require write/schemas/verify to
have executed, execution_sql_failed and no repeated write/repair. Corrected process
verification follows. No production expectation was changed to conceal that gap.

Corrected affected supervisor command
`env PYTHONPATH=platform/deployment/tests python3 -m unittest test_resources.ExecutionSupervisor`
passes **5 tests,39.179s**. This includes actual local socket/process persistence
success and post-start lost-marker failure, both CLI/descendant termination, one
retained peer, automatic one-attempt cleanup and no repair. Earlier three supervisor
failure/mutation cases also pass unchanged.

Acceptance RED exact command was
`PYTHONPATH=platform/deployment/tests python3 -m unittest test_pinned_execution.PersistenceAcceptance`:
`test_distinct_owner_recreation_proves_same_volume_marker_and_clean_disposal`
failed(errors=1), missing FreshGuard.enable_persistence, before production changes.

| Matrix requirement | Executed focused coverage |
| --- | --- |
| Distinct replacement and retained initialized volume | PersistenceAcceptance; positive ExecutionSupervisor persistence case |
| Lost marker/cluster/initialization and SQL rejection | PersistenceFailureMatrix.test_lost_marker_or_cluster_nonzero_after_replacement_fails_without_repair; negative ExecutionSupervisor case |
| Resource/reference/custody loss stays latched | PersistenceFailureMatrix.test_gap_foreign_reference_or_changed_volume_latches_custody_loss; existing descriptor/custody cases |
| Uncertain create/remove/exec consumes transition | Both PersistenceUncertainty lost-create/exec cases; PersistenceFailureMatrix.test_uncertain_intermediate_remove_consumed_and_never_retried |
| Fixed operands/IDs/order and no replay | PersistenceFailureMatrix closed-route/malformed-exec/repeated-exec cases; PersistenceUncertainty.test_wrong_order_and_repeated_lifecycle_operands_refuse_without_dispatch |
| Fixed deadlines/interruption/restart/unclean exit | Replacement deadline and exec-polling cases, intermediate-remove interruption, existing unclean/instance/interruption/CleanupConsumeOnce cases |

Root runs actual Docker/socket/process work serially. Private verification orchestration
extends the preceding ignored helper with literal controls; it only invokes existing
owners and retains selected results. It is not new production delivery tooling.

## First actual source-qualified run

Run `216f1ede-c4a0-4b2f-b035-ba850d3506c4` passes preparation0.095s,
toolchain20.234s and images41.886s. Selected image child/config identities match the
preceding completed execution proof (PG child e85bc10ac5b141223b289e1e8dc8d448cf3df92501917149db0366b9c5aaf053,
config c4be96218454e68421a29c712e1a83c7a9fe186208c725d8bb2ebb474e2042f2;
each prefixed sha256). No tag substitution or source-bound receipt repair.
The actual explicit command is:

```sh
python3 platform/deployment/tests/qualify_startup.py --target platform/deployment/environments/kdg-local.json --run-id 216f1ede-c4a0-4b2f-b035-ba850d3506c4 --control pinned-cli-postgres-persistence
```

Protected records remain in `.local/pinned-cli-execution-qualification/<UUID>/`,
using the existing private qualification helper. The concurrent document/index
snapshot for this Build is `.local/postgres-persistence-qualification/concurrent.json`.

First actual persistence attempt: **exit2,36.474s**, startup/execution_invalid_exec.
All13 retained files and running inventory unchanged; protected `persistence.json`
SHA256 `ed8afc49c8caa92c3040b600c11e335d7810ccc0d617c90456e32c565e26c7f4`.
Read-only inspection by exact inventory identities afterward found its container,
volume and bridge absent. No manual deletion or same-run replay occurred.

Source diagnosis: [Moby exec inspection](https://raw.githubusercontent.com/moby/moby/v28.0.0/daemon/inspect.go)
passes the optional ExitCode pointer; [exec lifecycle](https://raw.githubusercontent.com/moby/moby/v28.0.0/daemon/exec.go)
sets it on completion. The initial validator instead required an integer before
start. Characterization now distinguishes explicit pre-start/running null from
completed integer zero; missing or completed null must still refuse. This is an
explained source-contract correction, not an expected-result relaxation to dismiss
a failure. Final actual verification must follow the corrected source qualification.

Null-exit characterization exact command:
`PYTHONPATH=platform/deployment/tests python3 -m unittest test_pinned_execution.PersistenceAcceptance.test_distinct_owner_recreation_proves_same_volume_marker_and_clean_disposal`
first failed execution_invalid_exec with independent pre-start null/PID0 fixture.
After correction root repeats the full focused command: **42 PASS0.512s**.
Three DockerExecLifecycle cases require null/PID0 before start, allow null while
running, and reject missing/completed-null/boolean/nonzero results. Completion
still requires confirmed start followed by a matching completed integer-zero exec.

After the correction, root's affected supervisor suite passes **5 tests,26.524s**.
Fresh run `629d85cd-8b2f-4d89-be97-357f577df9b0` passes prepare0.086s,
toolchain21.124s and images43.382s, same approved child/config identities. Earlier
216f1ede receipts/refusal remain unchanged; no requalification repair or replay.

Actual corrected persistence control on run629d85cd passes **exit0,113.812s**:
distinct_container_verified, owner_recreation_verified, persisted_run_marker_verified,
same_cluster_verified, initialization_markers_verified, both_shutdowns_verified,
healthy_verified, named_volume_verified and cleanup_verified true; owner_start_count=2,
cli_first_start_only=true, forced_shutdown=false, runtime_ready=false. All13 retained
files and running inventory unchanged. `persistence.json` SHA256
`f89f42a8e1bf98f386af13abdd0b8747a765c81d7b128f49cdaab631bcbb767f`;
image receipt SHA256
`02445e21fbafbf546579a2d2f1217cad0f8a3747717788de4fe043430c652dc9`.
This establishes the corrected exec lifecycle through actual selected-image SQL and
container replacement, rather than inferring success from the unit fixtures.

After resume the qualification process handle for run3a92e7aa-fbeb-495f-a09b-2baff3e3ea37 was unavailable and no final prerequisites record existed. Its partial artifacts remain preserved; it is not counted as a qualification pass. A fresh UUID is used for the negative check, without receipt repair.

Separate negative-check run `0942680e-d57c-444e-b1cc-214250bebd0d` passes prepare0.076s
and toolchain16.726s; images refuses registry/manifest_response_invalid, exit2,31.517s.
No runtime execution begins on that UUID. Its failed prerequisites record remains;
no image receipt is repaired or borrowed. Existing controls use their valid unchanged
629d85cd source qualification; a fresh negative UUID will retry independently.

Existing actual `--control pinned-cli-postgres` on unchanged run629d85cd passes
**exit0,92.895s** with its original first_start_only payload and clean shutdown/disposal.
All13 retained files and running inventory unchanged; `proof.json` SHA256
`efd0edd92520d6b7a4e4fbdda7824d4d1fa2f6a66e5c31f6e17bf9df23521f54`.

Negative-check refresh `1f53baff-a153-488e-b755-9be00060f07d` passes prepare0.068s,
toolchain24.936s and images48.410s, same approved immutable children/configs.
The private literal negative-marker control changes only the verify predicate's
public UUID to00000000-0000-4000-8000-000000000001. It records owner probe modes,
requires execution_sql_failed after write/schemas/verify, and observes owned cleanup
without a persistence/readiness claim. Production files/commands are unchanged;
this fault-injected check is distinct from ordinary positive qualification.

Actual wrong-marker check on1f53baff returns expected **exit2,56.569s**, startup/
execution_sql_failed, after owner probe modes write/schemas/verify. The fixed SQL
predicate rejected the wrong public UUID in the real replacement PostgreSQL;
owned_cleanup_verified=true, persistence_verified=false, negative_check_passed=true,
runtime_ready=false. All13 retained files and running inventory unchanged.
Protected `negative-marker.json` SHA256
`937a197d5539a2eebaed6697d7ea538bc379dbd546abef05ded36ad5d9626f47`.
This is expected fault rejection, not an ordinary qualification success or clean
shutdown claim for the failed verification path.

Existing actual `--control postgres-bootstrap` on629d85cd passes **exit0,31.116s**,
including SQL/key semantics, same-instance clean shutdown and disposal; loopback
password enforcement remains separately false as documented in the original proof.
All13 retained files and running inventory unchanged; `bootstrap.json` SHA256
`09ea10224dc3588bbd0b5b7b9e106eef13874b6e921c003ce356c8cd34d92e18`.

Existing `--control guarded-fresh` on629d85cd passes **exit0,66.461s**, with synthetic
create and refused first start retained. All13 files and running inventory unchanged;
`controls.json` SHA256
`b7206e1f8e54d9d5e9564f2832efe9200c9feb5ced53b117619d90a4ef4496da`.
Public `python3 platform/deployment/dev.py up --target platform/deployment/environments/kdg-local.json --run-id 629d85cd-8b2f-4d89-be97-357f577df9b0`
returns expected **exit2,0.047s**, runtime_adapter_unqualified/runtime_ready=false.

## Final regression and matrix audit

`python3 platform/deployment/.local/pinned-cli-execution-qualification/verify-local.py tests 629d85cd-8b2f-4d89-be97-357f577df9b0`
passes **516 tests,348.807s** (wrapper349.007s), exit0, no skips. The retained
diagnostic runner discovers the deployment suite without changing assertions or
deadlines. `deployment-tests.log` SHA256
`ba8d2e6082c25342bed52fd9a308633a359107912e94f2df2d19d0978b0a03c2`;
`deployment-tests.json` SHA256
`704fef9eee30ddac1e2662f1a59807509e3b64e751ea49499632049c08d71725`.
All six matrix rows above have executed passing focused coverage and were included
again in this full run. The two preceding intermittent guard investigations remain
open; this pass does not explain or close them. Concurrent five Leave/PtS document
hashes and their index entries match the initial snapshot. Review follows.

## Review corrections

All three BMAD layers completed. Edge-case review returned no findings. The full
per-finding verdicts are in the Build triage log. Review identified missing real
cluster-predicate rejection, independent initialization-predicate negatives and
five focused lifecycle/transaction-fixture coverage cases. The implementation
owner added the focused tests and read-only unresolved-resource inspection steps.
Root read those patches; no production source or bound profile changed.

The fixture failed-write test first failed before the model correction: a rejected
write incorrectly retained its simulated marker. The fixture now commits only on
success. Root focused command passes **47 tests,0.518s**. New named coverage under
`PersistenceReviewCoverage` exercises failed-write rollback, final schema failure,
reused exec identity, finish replay after success/failure and uncertain post-delete
inspection. Final full regression and real predicate checks follow.

Fresh review-negative run `707b9ed0-52b8-4f66-8ba7-1734a36dc554` passes prepare0.060s,
toolchain16.551s and images33.759s with the same immutable image identities.
The private literal `negative-cluster` check executes seven actual SQL corruption
cases using the generated predicate statements: wrong stored cluster identifier,
missing migration, extra migration, wrong JWT secret, wrong JWT expiry, missing
`_analytics` and missing `_supavisor`. Each case runs in a PostgreSQL subtransaction:
the generated predicate must raise P0001; accepting corruption raises a different
uncaught error. A private sentinel then rolls the temporary corruption back. The
write and first schema exec must both complete with exit0 to advance to verify.

After these checks, the synthetic write deliberately commits a wrong stored cluster
identifier while preserving the correct run UUID. Replacement verification executes
the original unmodified generated predicate against that persisted row. Expected
**exit2,51.934s**, execution_sql_failed, follows write/schemas/verify, with all seven
negative predicate cases executed, owned_cleanup_verified=true, persistence_verified=false
and negative_check_passed=true. This rejects the review's cluster-matching mutation:
without that predicate, the first write's negative case cannot advance successfully.
All13 receipts and running inventory remain unchanged. No failed-path clean-shutdown
or persistence/readiness claim is made.

Reproduction command uses the retained ignored helper:
`python3 platform/deployment/.local/pinned-cli-execution-qualification/verify-local.py negative-cluster 707b9ed0-52b8-4f66-8ba7-1734a36dc554`.
This is an isolated fault-injection check, not a production control or a reusable SQL
interface; use a fresh qualified UUID for another execution. Private helper SHA256
`f7c68581b3c29a5023e7a3bd7d029eac73473249382be743af70c3777da084fd`;
protected `negative-cluster.json` SHA256
`543134d096df87a784968b17439ca38f7f91304ff5b2c9cc03f45e10e30f8584`.
Production/profile and preparation/image source bindings remain unchanged. Final
post-patch full regression follows; no new deferred item.

## Reviewed-source closeout

Final command repeats the unchanged diagnostic-runner discovery after the test/runbook
patches: **521 tests PASS320.764s** (wrapper320.934s), exit0, no skips. Protected
`deployment-tests-2.log` SHA256
`369ecb2a78afcf8f1aaf7221014ccf09049198d66f40c9fa2bf0133e940ab404`;
`deployment-tests-2.json` SHA256
`d1cb3a54e5d04a3c4d65cce195483836e40937bf920cc3b87005d98fb9711364`.
The affected process fixtures and all six acceptance-matrix rows run and pass within
this suite. Root verified the patched diff, source bindings, concurrent document/index
preservation and `git diff --check`. All review findings have individual verdicts;
accepted patches are complete, no new deferred item. The two preceding intermittent
guard investigations remain deferred and unexplained by passing runs.

This bounded persistence item is complete. Full environment/runtime readiness and
the remaining ENV/P1/SERVICE gates listed above remain open. No production migration,
access/account change, infrastructure provisioning, deployment or real-data pilot
has occurred.
