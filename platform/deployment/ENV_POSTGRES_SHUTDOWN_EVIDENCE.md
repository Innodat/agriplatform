# Bounded PostgreSQL shutdown evidence

[Build item](../../_bmad-output/implementation-artifacts/spec-env-postgres-graceful-shutdown.md)
extends the [selected-image bootstrap proof](ENV_POSTGRES_BOOTSTRAP_EVIDENCE.md)
through the existing lifecycle owner and explicit `postgres-bootstrap` control.
Full ENV/P1/SERVICE acceptance remains partial and `up` remains gated.

## Required observations

Initialization still has a120-second total deadline. After successful SQL/key
verification and a final initialization-budget check, shutdown gets a separate
fixed15-second budget. Each child command remains bounded to ten seconds and65,536
combined output bytes. `docker stop --timeout 5 <recorded-ID>` uses the image's
normal stop signal; a successful command can still follow a forced kill, so exit0
of the command alone cannot qualify clean shutdown. See
[Docker's stop contract](https://docs.docker.com/reference/cli/docker/container/stop/).

The first verified running container's nonzero UTC StartedAt is captured before
SQL/key checks. Pre-stop inspection must identify that same started instance.
Post-stop observation requires Status exited, Running/Dead false, PID0, integer
ExitCode0, OOMKilled false, empty Error, unchanged StartedAt and a nonzero UTC
FinishedAt strictly later than StartedAt. Timestamp comparison preserves nanoseconds.
Configuration, ID, image, labels, isolation, limits and storage are checked before
each ownership-dependent action; observed ownership drift latches refusal even if
later observations match again. Clean stopped state is checked again before removal.

Only verified clean shutdown adds `shutdown_verified=true`, `forced_shutdown=false`
to the successful result. It then uses ordinary removal and verifies absence.
Earlier failures/interruption keep bounded owned force-cleanup without claiming
clean shutdown, durability or recovery. Cleanup has its independent ten-second
budget; uncertain ownership or failed removal/absence reports `cleanup_unresolved`.
Safe codes distinguish OOM, exit137, another nonzero exit, still running, stale/
invalid state, changed started instance, shutdown deadline and command failure.
Raw Docker state, child output and secret values are not emitted or retained.

## ATDD and focused TDD

Before production edits, the implementation agent ran
`python3 -m unittest discover -s platform/deployment/tests -p test_postgres_bootstrap.py`:
27 tests, exit1,0.215s. The new behavioral test failed with StopIteration because
the old successful command sequence contained no stop; all26 prior tests passed.
After implementation root ran the same command: **36 tests PASS,0.256s**.
The positive independent phase-budget case brought this to37 PASS. Review exposed
late final cleanup and malformed ownership latching defects; both new regression
cases failed before their fixes. After fixes and interruption coverage, root ran
the same command: **40 tests PASS,0.263s**.

| Requirement | Executed test in `test_postgres_bootstrap.py` |
| --- | --- |
| Actual stop and clean observation before normal removal | `Matrix.test_success_stops_and_observes_clean_exit_before_removal` |
| OOM/forced/nonzero/dead/error/stale/malformed state refuses | `ShutdownMatrix.test_unclean_or_incomplete_poststop_state_never_qualifies` |
| Pre-stop running instance is valid | `ShutdownMatrix.test_before_stop_requires_verified_running_state` |
| Stop timeout/failure cannot qualify | `ShutdownMatrix.test_stop_command_failure_or_timeout_cleans_without_claiming_shutdown` |
| Changed ownership blocks stop/deletion even if restored | `ShutdownMatrix.test_changed_owner_before_or_after_stop_never_deletes_even_if_restored` |
| Initialization may finish at119s and clean shutdown complete at123s | `ShutdownMatrix.test_shutdown_can_finish_after_initialization_deadline_with_its_own_budget` |
| Final cleanup observation cannot complete after its budget | `ShutdownMatrix.test_final_cleanup_observation_cannot_complete_after_cleanup_deadline` |
| Malformed, duplicate-key or NaN ownership never permits later cleanup | `ShutdownMatrix.test_one_shot_malformed_ownership_cannot_be_restored_for_cleanup` |
| Post-stop/recheck interruption never returns success | `ShutdownMatrix.test_interruption_in_poststop_observation_or_cleanup_never_succeeds` |
| Fixed shutdown phase and independent cleanup budget | `ShutdownMatrix.test_shutdown_has_separate_total_budget_and_cleanup_is_independent` |
| Restart cannot reuse prior SQL verification | `ShutdownMatrix.test_restart_after_key_cannot_qualify_a_different_started_instance` |
| Nanosecond ordering and final stopped-state recheck | `ShutdownMatrix.test_nanosecond_completion_and_cleanup_state_recheck` |
| Late initialization cannot obtain a new budget | `ShutdownMatrix.test_final_key_overrun_cannot_reset_expired_initialization_budget` |
| Earlier failure/interruption never claims shutdown | `ShutdownMatrix.test_initialization_failure_or_interruption_never_requests_success_stop`; existing interruption cases |
| Cleanup command/absence failure cannot claim success | Existing `Matrix` and `ReviewFixes` cleanup cases |

## Actual selected-image proof before review patches

Fresh run `625e0eb3-2e5b-4861-89c4-0ab52d65a45f` passes existing `dev.py prepare`,
`toolchain.py qualify`, `images.py qualify` with explicit target
`platform/deployment/environments/kdg-local.json`. The exact approved baseline,
including TypeScript7.0.2, remains selected. PostgreSQL17.11.0.004 Linux/amd64 child
`sha256:e85bc10ac5b141223b289e1e8dc8d448cf3df92501917149db0366b9c5aaf053`
and config `sha256:c4be96218454e68421a29c712e1a83c7a9fe186208c725d8bb2ebb474e2042f2`
match the already downloaded and separately inspected image from the preceding item.
No tag substitution, receipt repair or new image download is needed.

`python3 platform/deployment/tests/qualify_startup.py --target
platform/deployment/environments/kdg-local.json --run-id
625e0eb3-2e5b-4861-89c4-0ab52d65a45f --control postgres-bootstrap`:
**exit0,37.966 seconds**, with all SQL/key checks true, `shutdown_verified=true`,
`forced_shutdown=false`, `cleanup_verified=true`, `runtime_ready=false`.
All13 retained inventory/config/toolchain/image files match before/after hashes;
the running-container inventory is identical. This is not a full host health or
business-data comparison. Protected record:
`.local/postgres-shutdown-qualification/625e0eb3-2e5b-4861-89c4-0ab52d65a45f/bootstrap-shutdown.json`,
SHA256 `75298d0b518ec509f331b65de6b57806d7189cbae1d0dc696efcf41e03c8e2f7`.

## Final patched-source selected-image proof

Fresh run `885056ba-e9dc-41a2-9e3e-f207d75bdeb2`: prepare PASS0.076s,
toolchain PASS19.575s, images PASS33.322s, same approved PostgreSQL child/config
and exact TypeScript7.0.2. The explicit `postgres-bootstrap` command above with
this final UUID passes **exit0,35.832s**, SQL/key/shutdown/cleanup true,
forced_shutdown=false, runtime_ready=false. All13 retained files are unchanged.
Protected `bootstrap-shutdown.json` SHA256
`53d6ce7687dee40938a9638b9219c2670430f426eec6871f47ee81b46fdcd9ba`
in `.local/postgres-shutdown-qualification/885056ba-e9dc-41a2-9e3e-f207d75bdeb2/`.

The running inventory differs: no before-entry ceased running; three unrelated
Deals containers (`deals-core-20261015-bench`, `deals-core-20261015-db`,
`deals-core-20261015-redis`) appeared running. Qualification commands target only
the fresh recorded ENV proof container; no command starts/stops those Deals
containers, and their concurrent state is preserved. Their cause is not independently
observed. Do not claim unchanged whole-host inventory or host/data health.

`python3 platform/deployment/dev.py up --target platform/deployment/environments/kdg-local.json --run-id 885056ba-e9dc-41a2-9e3e-f207d75bdeb2`
returns exit2 in0.045s, `runtime_adapter_unqualified`, runtime_ready=false.

## Regression attempts and limitation

The first full command `python3 -m unittest discover -s platform/deployment/tests`
ran465 tests in321.689s and failed one existing case:
`test_resources.Resources.test_integrated_private_handoff_adversaries_and_drip_deadline`.
Its spawned-process stopped-state assertion exceeded its existing0.5s observation
deadline. The test did not identify which of its nine adversaries was active and
did not retain the process state from the failure. The exact cause is unobserved.
No new shutdown case failed. The guarded CLI runner and failing assertions are
unchanged by this item; no deadline/expectation was relaxed.

The exact focused command
`python3 -m unittest discover -s platform/deployment/tests -p test_resources.py -k integrated_private_handoff_adversaries_and_drip_deadline`
passed (1 test,10.030s). Three additional unchanged focused runs with a read-only
diagnostic wrapper all pass (10.815s,11.528s,15.211s), including all nine adversaries
each time. The wrapper only records safe per-defect process fields if failure recurs;
it changes no expected outcome. Passing reruns do not explain or erase the first
failure. Preserve this intermittent process-cleanup limitation for follow-up.

Protected initial full-suite files: `.local/postgres-shutdown-qualification/
625e0eb3-2e5b-4861-89c4-0ab52d65a45f/deployment-tests.{log,json}`;
log SHA256 `fead064f015383cc7c3852fd0a5d35bf782dd61f0e3035b75bd37efa113ca984`.
The unchanged465-test full rerun passed in297.721s, exit0. Protected
`deployment-tests-2.log` SHA256
`91f789aec8f5cadd6fb72a5e4e482722d4d0222fc68ddd9dd1ceb1eec99f0479`.
This run preceded the additional positive phase-budget test. One further full run
started before review patches; its result is retained separately and is not the
final patched-source regression. It ran466 tests in324.851s, exit1, with a
different existing failure: `test_integrated_owner_negative_matrix_never_replays_or_returns_proof`
returned `docker_timeout` rather than `image_identity_mismatch`. The exact focused
command with `-p test_resources.py -k integrated_owner_negative_matrix_never_replays_or_returns_proof`
then passed one test in13.012s. No expectation or production guard was changed.
`deployment-tests-3.log` SHA256
`edec8b991802b7450ddcafec38d72506b7d88e78555e403383ff5690c096f672`.
This second existing reliability limitation is separately deferred; its cause and
failing scenario were not captured by the original assertion. The final runner
adds safe failure labels/process-state capture only, without modifying assertions,
deadlines, discovery or production code.

## Review disposition

Three BMAD review layers completed. The runtime thread limit required the verification
layer to re-engage the independent investigation agent; it did not implement this item.
Two production guards and interruption coverage were patched. Individual verdicts
are recorded in the Build spec. Final documentation and commit scope were reconciled.
Two pre-existing guard reliability limitations are deferred with retained
failure evidence; neither is claimed fixed by passing reruns. Concurrent Leave changes
were visible in the all-baseline review diff and are excluded from this delivery commit.

## Impacts and limits

Scaffold: extend existing deployment/lifecycle owner; no new generator, schema,
transport, runner or runtime admission. Shared UI: no UI surface or shared UI change.
Agent context: existing AGENTS rules suffice; handoff records the operational limit.
Documentation: source-bound image profile, this proof, runbook and KDG handoff/memlog.
ADR: no new or changed accepted decision; observed forced termination remains distinct
from successful shutdown or recovery under existing operational/release principles.

No named volume, initialized reuse, crash recovery, real pinned-CLI container
dispatch, whole Supabase startup, owner migration/seed/account/grant, deployment or
real data is introduced. The unchanged synthetic container remains network none,
no ports/host binds, tmpfs data,2GiB memory, two CPUs,256 PIDs and Docker logging none.
This item qualifies one shutdown primitive; it does not implement public `dev.py stop`
or close enclosing ENV lifecycle/scaffold acceptance. Preserve TypeScript7.0.2 and
concurrent Leave/PtS work.

## Final regression and closeout

`python3 /tmp/env-shutdown-full-diagnostic.py` discovers the complete
`platform/deployment/tests` suite using unittest's default loader and TextTestRunner.
Its only additions are failure labels and stopped-state diagnostics; every original
assertion/deadline and all production code remain unchanged. **469 tests PASS,
288.899s, exit0** (wrapper elapsed289.059s), after all review patches.
Protected final-run `deployment-tests.log` SHA256
`3a7a80acf8c4b56197ae56be26649245b87e315c7836ed4a76f0c66508e62f9c`;
`deployment-tests.json` SHA256
`ca922c465abe6c7681d76e0ef58a504d265fb61f76d59231c530e491fbe244a5`.
Both live in the final UUID directory above. Diagnostic runner bytes are retained
there as `full-diagnostic-runner.py`, SHA256 `4e60dc7e805ccb3fc02045eb33c697dca0f3f557244dc8c2ce5617b234f54ea5`.
The runner has no retry/skip behavior and emitted no failure diagnostics on this run.
Passing final verification does not explain either earlier existing guard failure.

Three review layers complete; two production fixes and one coverage fix applied,
final evidence/memlog/commit scope reconciled, two existing guard reliability
investigations deferred in the append-only delivery backlog. All14 named requirement
references resolve to implemented tests; local Markdown links and whitespace checks
pass. No accepted ADR or shared UI changes. Full ENV readiness remains partial.
