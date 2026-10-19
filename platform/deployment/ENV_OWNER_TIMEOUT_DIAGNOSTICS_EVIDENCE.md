# ENV owner-check timeout diagnostics

Current Build: complete; independent review corrections verified. This bounded increment distinguishes
existing owner-check timeout observations from Docker-request failures. It does not
identify the cause of earlier actual host timeouts or change runtime admission.

## Scope and authority

The previous [owner execution evidence](ENV_API_DEFAULT_PRIVILEGES_OWNER_EVIDENCE.md)
records an actual backend-control docker_timeout with no request observation and
an unused volume/empty bridge retained. Existing local custody checks can consume
the owner deadline outside DockerSession.exchange. This is a reproducible diagnostic
blind spot; it does not prove that any particular prior failure followed this path.

The existing dev/resources owners gain only optional owner_failure metadata with
schema_version, scope, check and bounded integer elapsed_ms. Scope/check identifiers
are closed; an already expired budget is distinguished from expiry detected after
checks. Metadata states the observation boundary, not which underlying check caused
expiry. Existing stage/code and Docker-request observations retain their meanings.
No resource, source, target, credential, payload or exception text is disclosed.

Check order, short-circuiting, refusal/cancellation precedence, original budgets,
connection/no-replay and cleanup authority stay binding. Observation errors never
change the original outcome. No custody read optimization or generic telemetry
service is included. All prior receipts, state and uncertain Docker resources are
preserved. TypeScript 7.0.2, mail 15484 and existing owners remain selected.

## Requirement-to-test evidence

Implementation observed acceptance RED before correction. Root independently replays
the exact new public-output test against isolated baseline
b37645394aa9fe71810308c0cfa0a15b23be1ca0: 1 FAIL, 0.145s because owner_failure is absent.
No shared source is reset. Initial six focused tests PASS, 0.458s. The initial child
sandbox/control-typo attempts are setup failures, not acceptance evidence.

| Matrix scenario | Passing named tests |
| --- | --- |
| Local owner timeout | Resources.test_owner_timeout_public_qualifier_keeps_custody_boundary_without_request_metadata; test_fresh_custody_timeout_and_already_expired_keep_executable_order; test_guard_outer_boundary_preserves_order_and_nested_observation |
| Already expired at entry | Resources.test_acquisition_already_expired_keeps_evidence_before_timeout_and_closes; Resources.test_fresh_custody_timeout_and_already_expired_keep_executable_order; Resources.test_guard_outer_boundary_preserves_order_and_nested_observation; DockerSessionTests.test_owner_observation_preserves_outcomes_and_bounds_elapsed |
| Nested cleanup | Resources.test_owner_context_cleanup_refusal_retains_observed_timeout_and_closes_once; DockerSessionTests.test_owner_formatter_closed_types_original_chain_and_truncation; Resources.test_guard_outer_boundary_preserves_order_and_nested_observation |
| Existing request failure | DockerSessionTests.test_owner_observation_optional_clock_attributes_and_request_metadata plus unchanged transport suite |
| Success/other error | Resources.test_guard_outer_boundary_preserves_order_and_nested_observation; DockerSessionTests.test_owner_observation_preserves_outcomes_and_bounds_elapsed; test_owner_entry_observation_propagates_clock_and_deadline_cancellation; test_owner_exit_observation_cancellation_preserves_original_error |
| Invalid observation | DockerSessionTests.test_owner_observation_optional_clock_attributes_and_request_metadata; test_owner_formatter_closed_types_original_chain_and_truncation; test_owner_deadline_observation_failure_preserves_success_and_original_error |

The public acceptance uses one real private Unix connection and synthetic owner
inputs. It advances a controlled clock six seconds during custody with the original
five-second budget: no handoff or subsequent request occurs, original stage/code
remain docker/docker_timeout and only selected owner metadata is added. This is not
an observation of which check caused the prior actual host timeout.

Initial pre-review root verification covers 332 unique passing cases on 74 unchanged source/test
bindings. Seven complete module/class calls pass 328 tests: session 36, gate 15,
daemon images 18, networks 28, volumes 31, pinned owner 158 and resource custody 42.
Four selected process cases pass across an initial group's first three successes
and a separate unchanged repeat of its failed fourth case. No successful combined
four-case process run or full deployment-suite run is claimed. No skips occur.

Exact root orchestration: `python3 platform/deployment/.local/owner-timeout-diagnostics/verify.py N`,
N=0..6 for the seven suites; the initial N=7 group is retained as a failure.
For a clean checkout, the equivalent direct commands for those seven complete selections are:

```sh
PYTHONPATH=platform/deployment/tests python3 -m unittest -v test_docker_session
PYTHONPATH=platform/deployment/tests python3 -m unittest -v test_docker_gate
PYTHONPATH=platform/deployment/tests python3 -m unittest -v test_daemon_images
PYTHONPATH=platform/deployment/tests python3 -m unittest -v test_networks
PYTHONPATH=platform/deployment/tests python3 -m unittest -v test_volumes
PYTHONPATH=platform/deployment/tests python3 -m unittest -v test_pinned_execution
PYTHONPATH=platform/deployment/tests python3 -m unittest -v test_resources.Resources
```

The initial failing four-case process selection (first three passed) was:

```sh
PYTHONPATH=platform/deployment/tests python3 -m unittest -v test_resources.ExecutionSupervisor.test_initialized_nested_deadline_and_interrupt_terminate_both_groups test_resources.ExecutionSupervisor.test_auth_poststart_instance_custody_deadline_and_interrupt_preserve_limits test_resources.ExecutionSupervisor.test_api_default_privileges_process_order_and_verified_cleanup test_resources.ExecutionSupervisor.test_cli_db_backend_process_order_and_same_pg_disposal
```

The final isolated fourth-case repeat command:

```sh
PYTHONPATH=platform/deployment/tests python3 -m unittest -v test_resources.ExecutionSupervisor.test_cli_db_backend_process_order_and_same_pg_disposal
```

All local evidence resides at `platform/deployment/.local/owner-timeout-diagnostics/`:
`root-acceptance-red.log`, `red-baseline.json`, `root-focused-green.log`,
`verify-NN.log`/`verify-NN-result.json`, `source-bindings.json`,
`verification-plan.json` and `verification-summary.json`. The direct commands above reproduce the selections without the local runner. The
retained `verify.py` and plans additionally bind the local logs to source hashes. These are local verification
artifacts, not committed runtime receipts. Original failed logs remain separate.

Retained unresolved observations:

- The first network suite fails its pre-existing 150ms/two-request timing assertion:
  one request is observed instead of two after a 90ms response delay. Exact unchanged
  test repeats PASS, 0.379s; isolated baseline PASS, 0.711s; whole unchanged suite repeats
  28 PASS, 21.769s. Network acquire's AST and test file are unchanged; it does not call
  the new owner observer. Original host timing/change contribution remains unconfirmed.
  See initial-network-failure/, network-deadline-repeat.log,
  network-deadline-baseline.log and network-failure-attribution.json.
- The first selected process group has three successes, then backend-positive
  refuses invalid_owner_handoff when the CLI is no longer live during present-backend
  observation. The guard correctly refuses qualification. Exact current test repeats
  PASS, 23.924s and isolated baseline PASS, 23.494s; backend liveness method AST is unchanged.
  Original process return code/signal timing were not recorded; fixture alarm, host
  scheduling and change contribution are unconfirmed. See initial-process-failure/,
  backend-positive-repeat.log, backend-positive-baseline.log and
  backend-failure-attribution.json. No liveness check, alarm or expectation is changed.

Later successes do not explain either first failure. Existing retained Docker
resources and receipts are never adopted, removed, rewritten or replayed. No actual
Docker command or fresh full 674 result is executed/claimed for this diagnostic-only
source; prior actual/full evidence stays tied to the previous commit. Future actual
qualification must begin with fresh source-bound preparation.

All three independent review layers completed: seven blind findings, one edge
finding and no verification-gap findings. Eight findings are individually triaged
in the Build record. The duplicate entry-cancellation defect is corrected with
`except Exception` at entry, allowing KeyboardInterrupt/SystemExit/GeneratorExit
before original work. Exit annotation still preserves an already-raised original.
The other direct corrections add integrated expired-entry/owner-cleanup/executable
custody tests, invalid deadline outcomes and committed direct commands. No timeout,
check order, custody authority or expected result is relaxed.

Review cancellation test RED: one test, four failing clock/deadline cancellation
subcases, 0.001s; child patched-source focused GREEN: 42 tests, 1.653s. Logs reside
under review-patch/. Root final verification is recorded separately under final/;
initial source-bindings/logs are retained without relabeling them as final source.
Three entries are newly deferred: remaining direct boundary diagnostics plus the
two unverified medium timing/liveness investigations above.

## Final reviewed-source verification

After the review patch, root regenerated a separate exact-ID plan and froze 74
source/test hashes in final/. All 337 distinct selected cases pass across the
recorded calls, without skips or expectation/deadline changes:

| Selection | Result / elapsed |
| --- | --- |
| test_docker_session | 39 PASS / 0.583s |
| test_docker_gate | 15 PASS / 2.213s |
| test_daemon_images | 18 PASS / 24.622s |
| test_networks | 27 PASS, 1 FAIL / 24.859s; exact failed case isolated repeat 1 PASS / 0.364s |
| test_volumes | 31 PASS / 18.356s |
| test_pinned_execution | 158 PASS / 13.991s |
| test_resources.Resources | 44 PASS / 239.618s |
| Four process cases listed above | 4 PASS together / 59.440s |

The final network-group failure repeats the same 150ms/two-request observation
(one request rather than two). Its unchanged isolated repeat passes after the
other tests finish. This does not explain either group failure or prove absence
of timing contribution. No successful combined final network suite or complete
deployment suite is claimed. The previously failing process group now passes
all four cases together; that does not explain its original CLI departure.

The seven direct commands above remain exact; final isolated network repeat:

```sh
PYTHONPATH=platform/deployment/tests python3 -m unittest -v test_networks.NetworkAcceptance.test_one_operation_deadline_spans_version_and_network_requests
```

final/verification-summary.json independently checks every executed passing ID,
log hash and all 74 final source/test bindings. Initial logs/bindings and final
failed network log are preserved separately. The scoped diff passes git diff
--check. Concurrent documents/index are preserved; only the independently edited
Scribeswell brainstorming memlog advanced from the initial checkpoint. No actual
Docker operation, prerequisite receipt rewrite or new runtime claim occurred.

## Impact decisions and remaining gates

- Scaffold: improve only the existing deployment/error/owner boundary; no generator,
  schema/client ownership change or new runtime service.
- Shared UI: no browser behavior or UI component changes.
- Agent context: existing custody/privacy/owner instructions suffice; no edit.
- Documentation: this evidence, existing DEVELOPMENT runbook and KDG resume/memlog.
- ADRs: ADR0023 applies; accepted decisions remain unchanged and no new decision.

Full CLI setup, running Auth/API services, public lifecycle and ENV/P1/SERVICE
consuming scaffold proof remain open before Identity/Access/WRITE or server-backed
KDG. No Leave/editor, production migrations/access/accounts/infrastructure,
deployment/push or real-data use follows.


## Coverage limitation

The direct final idle/budget pairs in acquire and the pre-constructor idle/budget
pair in fresh_session remain unobserved outside the selected current/guard checks.
A deadline crossed there can still produce a timeout without owner_failure. These
pre-existing boundaries are deferred; absence of metadata never proves a request
caused a timeout. No complete owner-timeout coverage claim is made.
