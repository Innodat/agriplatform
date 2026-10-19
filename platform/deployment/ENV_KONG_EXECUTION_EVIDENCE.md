# ENV owned disposable Kong lifecycle evidence

Baseline: d21e24b171ebd03648f32aa987e4d2758c710dcd. Build is done; final synthetic verification and review corrections are complete.
The new explicit `pinned-cli-postgres-kong-execution` control extends the existing
owner after verified Auth/backend/default privileges/setup tail/Kong boundary.
No actual Docker operation is run in this increment. Runtime/fresh-setup readiness
remain false; native-token/functional Auth routing and consuming scaffold proof remain open.

## Requirement to test traceability

Run from repository root with
`PYTHONPATH=platform/deployment:platform/deployment/tests python3 -m unittest -v`
and the selectors below. Test methods contain independently asserted subcase matrices;
counts below refer to unittest methods, not individual matrix rows.

| Requirement / matrix row | Covering selectors |
| --- | --- |
| One complete lifecycle, cleanup before fact, false readiness | test_pinned_execution.KongExecutionOwner.test_owned_kong_lifecycle_normal_cleanup_precedes_separate_fact; test_resources.ExecutionSupervisor.test_kong_execution_process_ordered_lifecycle_and_post_cleanup_fact |
| Identified effective API empty/default normalization only | test_pinned_execution.KongExecutionOwner.test_only_identified_empty_api_normalizations_are_accepted |
| Premature/replayed call terminal before observation | test_pinned_execution.KongExecutionOwner.test_premature_and_replayed_execution_consume_before_observation |
| Existing name, malformed/colliding ID, warnings/lost create preserve resources | test_pinned_execution.KongExecutionOwner.test_existing_unknown_colliding_and_lost_create_preserve_all_resources |
| Effective Config/state/network/mount custody changes preserve resources | test_pinned_execution.KongExecutionOwner.test_effective_config_state_network_and_mount_faults_latch_custody_loss |
| Copy/start/health/instance/expiry/cancellation no replay | test_pinned_execution.KongExecutionOwner.test_copy_start_health_expiry_and_cancellation_never_replay |
| Shared15s shutdown, single10s cleanup, original120s execution | test_pinned_execution.KongExecutionOwner.test_shutdown_shares_budget_and_cleanup_has_single_ten_second_budget; positive owner test |
| Changed stopped PG blocks Kong disposal | test_pinned_execution.KongExecutionOwner.test_changed_stopped_pg_blocks_kong_disposal_and_final_fact |
| Cleanup/final custody faults cannot publish fact | test_pinned_execution.KongExecutionOwner.test_cleanup_fault_and_final_custody_never_publish_success |
| Real private Unix/process loss/custody/failed exit controls | test_resources.ExecutionSupervisor.test_kong_execution_process_uncertain_create_and_custody_preserve_resources |
| Exact persistent per-exchange authority; default refusal/no carryover | test_docker_session.KongScopedTransport |
| Public qualifier inventory/real mapping | test_startup_adapter.StartupAcceptance.test_kong_execution_public_inventory_and_real_qualify_mapping |
| Ordinary/boundary behavior | Existing affected suites and selected process controls recorded below |
| Effective proc protections, live port bindings and endpoint options | test_pinned_execution.KongExecutionOwner.test_effective_protections_ports_and_endpoint_options_are_closed; test_pinned_execution.KongExecutionOwner.test_safe_dynamic_endpoint_fields_and_inactive_port_normalizations |
| Valid unhealthy is terminal before recovery | test_pinned_execution.KongExecutionOwner.test_unhealthy_is_terminal_before_later_same_instance_recovery |
| Expiry during Kong stop and between service stops | test_pinned_execution.KongExecutionOwner.test_shutdown_deadline_expires_during_kong_stop_and_between_service_stops |
| Health deterioration before normal shutdown | test_pinned_execution.KongExecutionOwner.test_health_deterioration_before_finish_refuses_without_normal_stop |
| Private-process cancellation, primary error and custody-sensitive cleanup | test_resources.ExecutionSupervisor.test_kong_execution_process_cancellation_after_start_preserves_primary_error |
| Lost stop/delete response, no replay or later disposal | test_resources.ExecutionSupervisor.test_kong_execution_process_lost_stop_and_delete_responses_never_replay |

## ATDD and retained failures

Raw records are retained under `.local/kong-owned-lifecycle/`; they contain safe
source/control diagnostics, never transferred archive content or container Env dumps.
`acceptance-red.log` records the positive owner acceptance failing with missing
execute_kong,1 method/0.245s, before runtime edits. It had completed the existing
synthetic prerequisite chain. Early GREEN and focused records, exact commands and
nine-file source freeze are in `delegate-freeze.json`. Later root manifests supersede
those early-source passes for final verification; originals remain unchanged.

`process-first.log` is a sandbox Unix-bind EPERM, not behavioral evidence. The first
negative/wire run failed an overrestrictive test assumption: a known current owned
instance with failed exit may be force-disposed during failure cleanup. The assertion
was corrected to the frozen matrix's current-ownership rule, without runtime change.
This does not relax unknown/lost-custody preservation.

`process-final.log` (4 methods/112.177s) failed in pre-Kong Auth handoff while another
focused suite overlapped. `process-negative-final.log` (1 method/69.231s), running
serially, also failed the prerequisite assertion before Kong. Contention alone is not
an established cause. Neither failure is relabelled as a pass.

Safe local diagnostic scripts traced only source function/line locations and guard
flags. The unchanged isolated positive, isolated custody case and serial three-scenario
sequence pass (sequence66.104s). The positive trace saw only an expected handled replay
refusal, so it does not identify the earlier escaping invalid_owner_handoff. A read-only
code audit found no obvious per-scenario state leak or artificial private-wire delay.

Open investigation: the wrapper's existing5s alarm covers startup import and backend
presence verification before deliberate CLI termination. Repeated full custody reads
are a plausible source of delay, but no original failing trace proves this chain.
Measure safe counts/elapsed times before optimizing; preserve every observation,
source/identity check and deadline. Do not cache custody across calls or enlarge the
alarm to force success. This remains an unverified operational limitation, separate
from successful synthetic Kong lifecycle evidence. Existing older investigations remain.

## Verification record

Root command (all methods registered, no skips):

```sh
PYTHONPATH=platform/deployment:platform/deployment/tests python3 -m unittest -v test_create_profile test_dev test_startup_adapter test_docker_session test_docker_gate test_pinned_execution test_startup_lifecycle.KongTransferArchive
```

344 methods PASS99.750s (runner99.905s),46 source/test/public-authority bindings
unchanged across the call. `root-affected-result.json` records the exact command,
source-manifest/log hashes and unchanged-source result. Source manifest SHA256
045ef91be88b51e1f06d013580f358b3b51b9b430efb1690c4d9a58fd0058260; log SHA256
e7ee5c364be4b0ebf7414397f3639ab4d744e921b3b6abd6dfa5f6b8b78c714b.

`root-process.txt` records both standard new process methods PASS, including all
three negative scenarios, on the identical46 bindings. That overall command FAILS:
its third selector was mistyped (`test_cli_db_backend_wrapper_alarm_stops_parent`),
yielding an AttributeError loader error. It ran3 methods in115.026s:2 actual tests
pass,1 loader placeholder errors. Do not call this command PASS or count the loader
placeholder as coverage. Correct existing alarm selector and ordinary controls run
separately. Original log/result retained (log SHA256
8be1bfdd54c8647c08a0d51b131d4fcd9a9e95ba7ff643fefc01a536b31aa422).

Ordinary command:

```sh
PYTHONPATH=platform/deployment:platform/deployment/tests python3 -m unittest -v test_resources.ExecutionSupervisor.test_cli_db_backend_wrapper_alarm_stops_cli_without_continuation test_resources.ExecutionSupervisor.test_kong_boundary_process_source_intent_and_cleanup test_resources.ExecutionSupervisor.test_post_auth_setup_tail_process_exact_artifact_and_cleanup test_resources.ExecutionSupervisor.test_api_default_privileges_process_order_and_verified_cleanup
```

`root-ordinary-process.txt`:4 methods/79.779s,3 pass, API-default positive errors
before Kong (overall FAIL). Exact trace escapes at resources.py780, backend
presence stable() after inspect_exec: the CLI is no longer live before the owner's
deliberate termination. This confirms the failed liveness check on that ordinary
control; it does not prove why the CLI died or explain the earlier original failures.
Same46 source bindings unchanged; log SHA256
fc823a997cb15e61d935e801f062485cb20e675df6b8e8d1a330d9efdc00b50e.
The alarm, boundary and setup-tail controls pass. Isolated API verification also
fails (`root-api-isolated.txt`,1 method/5.926s; unchanged46 bindings), this time at
the earlier original five-second fresh-acquisition custody deadline (resources.py92,
while creating the database volume). It is a distinct docker_timeout, not the same
Auth handoff error. Both original traces remain; neither establishes a root cause.
Log SHA2567a9ac686463b13a7420bb770081dd88f6437591829a4119b1a398f817741950a.

A safe instrumented unchanged API run (`profile_api.py`, `profile-api.log`) passes
21.424s. It measures217337 dev.read calls8.465s,1731 evidence checks14.177s,
1691 fixture custody checks5.124s and1216 session exchanges0.953s. Durations are
inclusive/nested and must not be added. Backend presence takes1.219s in this run;
there is no escaping failure. This proves repeated file/custody work dominates that
observed synthetic run, not that it caused either original failure.

Historical checkpoint before the completed correction results below: the Build was
characterizing and optimizing repeated parent-directory traversal only
within each fresh snapshot through existing filesystem/source owners. Every file is
freshly opened/read/checked/hashed each invocation, existing signatures and logical
observations remain, and parent pathname/device/inode must be rechecked before
return. No cross-call cache or deadline change is admitted. Post-correction serial
verification and review were pending at that checkpoint.

## Impacts and preservation

- Scaffold: extends existing ENV profile/resource/transport/qualifier owners; no new
  generator/runtime service. Consuming scaffold and full environment proof remain open.
- Shared UI: no UI or reusable presentation behavior introduced.
- Agent context: current instructions suffice; no context edit required.
- Documentation: runbook, this evidence, Build record and KDG handoff reflect scoped
  execution and continuing gates. Historical evidence remains tied to its source.
- ADR: existing release/custody/logging/owner decisions apply unchanged; no new or
  superseding architectural decision is needed.

The original CLI remains terminated. Source-derived marker keys are not native-token
proof. No real gateway health/HTTP response, full-suite result, deployment or production
readiness is claimed. TS7.0.2/mail15484 and all other approved pins/ports remain.
Checkpoint captures17 concurrent files,52 historical prerequisite files,17 prior
archive evidence and30 prior profile evidence files plus initial index. All must be
rechecked before scoped commit; no Docker resources are accessed or removed.


## Snapshot prerequisite characterization and TDD

Before changing runtime snapshot code, `test_dev.SourceSnapshotCharacterization`
passes4 methods/0.050s (`snapshot-characterization.log`): fresh content on each call,
existing file signature/inode/mode behavior, initial symlink/nonregular rejection,
failed reads/cancellation and descriptor closure. Acceptance then fails2 methods
with6 subcase failures/0.042s (`snapshot-acceptance-red.log`): excessive repeated
parent walks and missing post-read parent-replacement rejection in all three owners.
After the directory-only correction, the same6 methods pass0.085s in
`snapshot-focused-green.log`. Every read/duplicate/order/freshness and file signature
check remains; each held parent is freshly rewalked and identity-checked before
snapshot return. No bytes/hash/descriptor/authority persists into another call.
These tests characterize the refactor and its stronger final parent custody; they
do not claim to reproduce either earlier timing failure. Broader verification follows.


## Final frozen-source affected verification

```sh
PYTHONPATH=platform/deployment:platform/deployment/tests python3 -m unittest -v test_create_profile test_dev test_startup_adapter test_docker_session test_docker_gate test_pinned_execution test_startup_lifecycle.KongTransferArchive test_daemon_images test_resources.Resources
```

413 methods PASS336.513s (runner336.650s), no skips,47 source/test/public-authority
bindings unchanged across the call. `final-affected-result.json` records command,
source/log hashes and unchanged-source result. Manifest SHA256
5c595ffafc7b9605ed55d70e23d4eceaba500b9b39dde6fde8a7a9d59eaa4bb6; log SHA256
323faa371fb92653c4bd14310aa09afc0522c4daa1af1d500f18c917ff429e6a.
This includes every matrix selector above and the existing resource/image evidence
and mutation regressions. It is an affected selection, not a full-suite claim.

Relative to the earlier46-file root frame, the correction changes only dev.py,
startup.py,daemon_images.py and test_dev.py. The new47th binding is the previously
unmodified test_daemon_images.py, added because its full module now runs. All other
shared bindings match. Final snapshot-focused7 PASS0.059s and affected owner26
PASS3.663s are retained with commands/hashes in snapshot-correction-freeze.json;
the root413 call verifies those methods on its final source too.

Historical checkpoint before the completed results below: six serial process
controls, measured post-correction diagnostic, final preservation check and
independent review were pending. Current Build status is in-review.


Six process controls on that identical47-file snapshot PASS182.940s, no skips:

```sh
PYTHONPATH=platform/deployment:platform/deployment/tests python3 -m unittest -v test_resources.ExecutionSupervisor.test_cli_db_backend_wrapper_alarm_stops_cli_without_continuation test_resources.ExecutionSupervisor.test_api_default_privileges_process_order_and_verified_cleanup test_resources.ExecutionSupervisor.test_post_auth_setup_tail_process_exact_artifact_and_cleanup test_resources.ExecutionSupervisor.test_kong_boundary_process_source_intent_and_cleanup test_resources.ExecutionSupervisor.test_kong_execution_process_ordered_lifecycle_and_post_cleanup_fact test_resources.ExecutionSupervisor.test_kong_execution_process_uncertain_create_and_custody_preserve_resources
```

`final-process-result.json`: runner183.069s, same manifest SHA256
5c595ffafc7b9605ed55d70e23d4eceaba500b9b39dde6fde8a7a9d59eaa4bb6,
log SHA2567ecd7103a23e94b3a4c26d1d346349b747afb4f0f2008f79736c2f77794b6de9,
all bindings unchanged. These419 selected methods pass across the two retained calls;
original earlier failures remain causally unexplained, with no deadline relaxation.

Root matrix audit then found a valid-unhealthy health gap: the previous loop allowed
starting→unhealthy→healthy to qualify, contrary to the no-success matrix row. New
focused acceptance fails with Refusal not raised (1 method/0.816s, unhealthy-red.log)
before the correction. The owner now refuses valid unhealthy immediately and polls
only starting. This changes only the opted-in Kong loop, with no ordinary PG/Auth
policy change. Subsequent focused/relevant serial checks and review follow. Prior419
results remain tied to their exact snapshot, not relabelled as post-correction proof.


Post-matrix source verification (`matrix-final-result.json`): same seven-module
command as root-affected above,352 methods PASS107.899s (runner108.181s), no skips.
47 bindings unchanged; manifest SHA256
17350b5687ea858e96f733b99b4e0b467a7585b00fe91d417a4bd0e2e0f4dcec;
log SHA25688d6828494409420bc6596f0f2df2247141a0e329ddf485fd82593699b577161.
This runs all10 KongExecutionOwner methods, including terminal unhealthy, and all
unchanged profile/transport/public-qualifier and snapshot characterization checks.

The two Kong ExecutionSupervisor methods rerun together on that identical snapshot:
2 methods (positive + three negative scenarios) PASS120.936s (runner121.057s),
no skips; `matrix-process-result.json` log SHA256
c39957c74b74ca1a7175f3c7420d729f0fc87a2907d107b97c61690839a6695d.
The aggregate duration covers four separate synthetic lifecycles; no per-lifecycle
120s execution deadline is increased or reset.

`matrix-frame-delta.json` independently compares AST/source frames: only
FreshGuard.execute_kong changes, plus one added KongExecutionOwner test. All other
runtime functions, snapshot owners, test methods and the process harness are
unchanged. The62 resource/image methods and four ordinary process methods remain
retained evidence on their recorded pre-terminal-unhealthy frame; they do not call
the changed Kong health loop. There are420 distinct selected passing method IDs
across these retained calls, without pretending every method was rerun on the last
byte snapshot. No full-suite or actual-Docker claim follows.


Post-correction diagnostic (`profile_api.py`, same command and instrumentation as
before) PASS25.045s. Exact command:

```sh
PYTHONPATH=platform/deployment:platform/deployment/tests python3 platform/deployment/.local/kong-owned-lifecycle/profile_api.py
```

Its47 bindings match the matrix-process frame throughout (`profile-api-after-result.json`),
log SHA25632b39678d93c89620d6b03d970f3b6e28ccf26495072854424d74069e4708821.
Qualified evidence still runs1731 checks, fixture custody1691 checks, exchanges1216,
identical to the original measured run. No logical checks were removed. Inclusive
elapsed evidence16.437s, fixture5.902s, exchanges0.991s; backend presence2.741s.
The only invalid-handoff trace is the expected handled API-default replay after
verified CLI termination. There is no escaping error or payload output.

The observed total25.045s is slower than the earlier21.424s. No wall-clock improvement,
benchmark generalization or original-failure cause is claimed. The structural reduction
in parent walks is proved by tests; fresh read_at calls replace many dev.read calls,
so the dev.read counter reduction217337→8653 cannot be treated as fewer file reads.
Original timing investigations and all original failed records remain open/preserved.

## Final reviewed closeout — 2026-10-19

The bounded owned disposable Kong lifecycle is complete in synthetic verification.
The enclosing ENV foundation is still incomplete: actual current-source Docker qualification,
remaining services/native-token and functional Auth routing, and consuming scaffold proof
remain gates before dependent Identity/Access/WRITE or server-backed KDG implementation.

Final root command:

```sh
PYTHONPATH=platform/deployment:platform/deployment/tests python3 -m unittest -v test_create_profile test_dev test_startup_adapter test_docker_session test_docker_gate test_pinned_execution.KongBoundaryOwner test_pinned_execution.KongExecutionOwner test_startup_lifecycle.KongTransferArchive test_resources.ExecutionSupervisor.test_cli_db_backend_process_order_and_same_pg_disposal test_resources.ExecutionSupervisor.test_kong_boundary_process_source_intent_and_cleanup test_resources.ExecutionSupervisor.test_kong_execution_process_ordered_lifecycle_and_post_cleanup_fact test_resources.ExecutionSupervisor.test_kong_execution_process_uncertain_create_and_custody_preserve_resources test_resources.ExecutionSupervisor.test_kong_execution_process_cancellation_after_start_preserves_primary_error test_resources.ExecutionSupervisor.test_kong_execution_process_lost_stop_and_delete_responses_never_replay
```

Result: **190 methods PASS, no skips, 295.620s** (runner295.753s).
All 47 source/test/authority bindings remain unchanged during and after this run.
Source manifest SHA256: `59f22a5f2d5802e5611c9cc32026cba49f9dd7720bcbe556ce72a67b3ac9762c`.
Log SHA256: `2611d492733f573ad75a012241afcfbc45a90b0140ba6b9464e3c484d23e88ef`.
Receipts: `.local/kong-owned-lifecycle/reviewed-final-{result,sources,semantics}.json`
and `reviewed-final.txt`; final preservation and aggregate audit: `final-audit.json`.

Across the five successful retained root calls final-affected413, final-process6,
matrix-final 352, matrix-process2 and reviewed-final 190, there are **427 distinct
passing method IDs**. This is cumulative evidence across recorded source frames,
not 427 methods rerun on the final source bytes. The final 190 covers the modified
Kong projection, owner matrices and private process cancellation/lost-response controls,
plus ordinary backend and boundary process controls. Compared with matrix-final, the
only runtime symbol changed in review is create_profile.validate_kong_container;
the other changed symbols are test peers/matrices and the test module main-guard position.
The earlier resource/image and other ordinary controls retain their source-bound results.
The previous matrix-frame-delta records the earlier terminal-unhealthy correction.
Original failed runs and diagnostic results above remain evidence; later passes do
not explain those failures or establish a wall-clock performance improvement.

Three review layers are complete: blind10 findings, edge[], verification-gap1.
Ten findings were patched and verified; one was rejected with existing double-error
coverage demonstrated in the spec triage. No review finding was deferred. The separate
pre-review medium-unverified timing investigation remains in deferred-work.md.

Final preservation audit: all 17 concurrent/protected files, 52 historical prerequisite
files, 17 prior transport evidence files and 30 prior profile evidence files match their
checkpoint hashes. The original empty index is unchanged before scoped staging.
All 47 final source bindings match. No Docker API/resource action occurred in this
increment; uncertain resources and receipts remain preserved. Approved dependency,
CLI and mail-port baselines are unchanged. Only the17 owned paths enter the local commit.

Impact decisions remain: scaffold gains the existing opt-in qualifier and guarded
owner seam, with consuming generator proof still outstanding; shared UI has no
consumer-facing change; agent context requires no new global rule; runbook/handoff
and this requirement-to-test evidence are updated; existing ADR decisions apply,
so no new or amended accepted ADR is needed. Runtime_ready and fresh_setup_completed
remain false. No production, deployment, account/access, real-data or full-suite claim.
