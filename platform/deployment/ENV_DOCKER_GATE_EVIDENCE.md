# ENV local Docker prerequisite — 2026-10-14

This bounded increment implements a prerequisite in the existing `dev.py up` command,
under the [environment contract](../docs/architecture/contracts/scaffold-environment-and-generation.md).
It does not implement startup. The [Build record](../../_bmad-output/implementation-artifacts/spec-env-kdg-docker-prerequisite.md)
records implementation and review. Selected tool/dependency pins remain unchanged.

## Behavior and limits

`up` requires an existing, protected, unchanged preparation, rechecks all reserved
ports, then sends exactly `GET /version` to `/var/run/docker.sock`. It ignores ambient
Docker hosts/contexts and never invokes the Docker CLI. A stable Linux server version
at least 28.0.0 is required. This minimum follows
[Docker's documented pre-28 localhost-publishing limitation](https://docs.docker.com/engine/network/port-publishing/).
The [Engine API reference](https://docs.docker.com/reference/api/engine/version/v1.48/)
defines the read-only version endpoint. No daemon credential or response body is logged.

The request has one five-second total budget and a 64KiB total response cap. Only a
successful HTTP/1.0 or HTTP/1.1 response with one Content-Length and no transfer/content
encoding is admitted. Malformed, duplicate, oversized, truncated, prerelease or non-Linux
responses fail closed; this first target has no remote/rootless/custom-socket fallback.
The gate reads preparation without locks, writes or repairs. A supported version still
returns `up/runtime_adapter_unqualified`, with `runtime_ready=false`.

A version observation does not prove run-owned network isolation, supported image/DB
identities, toolchain consumption, owner migration/fixture coordination, Auth, provider,
device or application readiness. Future startup must recheck prerequisites at use.
`verify/stop/reset` retain their undelivered-adapter refusal and reset confirmation.
Source binding deliberately invalidates earlier prepared runs and toolchain receipts;
prepare and qualify a fresh UUID after source changes, never rewrite old receipts.

## Requirement-to-test evidence

| Requirement | Test in test_docker_gate.py |
| --- | --- |
| Existing preparation required; no implicit creation | test_public_up_requires_existing_preparation_without_creating_it |
| Exact local read-only request; supported server still cannot start; inventory unchanged | test_valid_preparation_inspects_only_local_version_and_still_refuses_start |
| Tampered run refused before daemon access | test_tampered_preparation_refuses_before_daemon_contact |
| Old, prerelease, invalid or non-Linux server refused | test_old_and_prerelease_or_nonlinux_daemons_refuse |
| Stable >=28 version passes only prerequisite | test_stable_current_or_future_major_passes_only_prerequisite |
| Bounded closed response framing | test_malformed_oversized_truncated_and_error_responses_refuse |
| Missing/denied/timed-out socket safe errors | test_unavailable_and_timeout_are_safe_refusals |
| Total deadline; Docker environment cannot redirect target | test_total_deadline_and_environment_override |
| Changed source, boolean substitutions, modes, symlink and extra file refuse before probe | test_preparation_source_mode_and_symlink_adversaries_refuse_read_only |
| Port conflicts refuse before daemon probe | test_occupied_port_prevents_daemon_probe |
| CLI error output excludes daemon exception details | test_daemon_failure_output_is_safe_json |
| Malformed header controls rejected | test_malformed_header_control_characters_refuse |
| Decoder recursion failure maps to daemon-response error | test_nested_json_is_reported_as_daemon_response_failure |
| Successful fragmented status/header/body and exact 64KiB cap | test_fragmented_success_and_exact_response_cap |
| Slow progressing reads share deadline; connect/send/receive timeout | test_slow_progress_uses_one_deadline_and_shrinking_timeouts |

The existing 16 preparation characterization tests passed before extracting unchanged
inventory construction (`6.059s`). Public acceptance red was observed before implementation:
expected `preparation/prepared_run_required`, actual `up/runtime_adapter_unqualified`;
the prepared-run case also showed no daemon request, and focused tests showed the
missing prerequisite function. Corrected discovery ran eight tests with two failures
and fourteen subtest errors. After implementation all eight passed in 0.313s.
The timeout assertion was corrected to expect the explicitly designed timeout code;
no unexplained behavior was dismissed. Synthetic tests replace the socket transport,
not the prepared-run or JSON/version validation code.

Actual host commands, using a fresh synthetic run:

```sh
python3 platform/deployment/dev.py prepare --target platform/deployment/environments/kdg-local.json --run-id 1ecc2833-825c-45cd-a01c-bef26edbfdb9
python3 platform/deployment/dev.py up --target platform/deployment/environments/kdg-local.json --run-id 1ecc2833-825c-45cd-a01c-bef26edbfdb9
```

Preparation returns exit0; up returns expected exit2 with `stage=docker`,
`code=docker_28_required`, `runtime_ready=false`. No container/image/network/volume API,
daemon upgrade, schema migration, account/grant change or deployment occurred.
Final regression/review results follow.

Review resolved all five findings without deferral: mutable preparation ancestor
checks, strict header control validation, decoder-depth normalization, progressing
deadline tests and fragmented/exact-cap tests. Ancestor and malformed-header regressions
failed before their fixes. The bootstrap JSON decoder accepts depth1500; depth10000
reproduces its native RecursionError and now returns a safe Docker response error.

Final reviewed source used fresh run `9ea3b977-f414-4414-b05e-444e6305c615` with the
same prepare/up commands above. Prepare exits0 and up exits2 with docker_28_required,
runtime_ready=false. Earlier run1ecc2833 records pre-review source and is preserved.

Final full owner command
`python3 -m unittest discover -s platform/deployment/tests -p 'test_*.py'` passes173
tests in83.494s. Focused command
`python3 -m unittest discover -s platform/deployment/tests -p test_docker_gate.py -v`
passes15 tests in2.369s. Both use isolated socket-capable execution. One prior focused
run overlapped actual preparation and failed during its shared-port probe; serialized
reruns pass. Run these suites and actual preparation/qualification sequentially.
Scoped whitespace and local documentation links pass. No test is skipped.

The existing `toolchain.py qualify` command was also run sequentially against final
prepared run9ea3b977-f414-4414-b05e-444e6305c615. It exits0 after all six real pinned
versions, compiler/GIL checks pass, with toolchain_ready=true/runtime_ready=false.
Its new mode0600 receipt is1958bytes and fingerprints13655 entries; SHA256
`7152e1fb6d996ad515d1ad05729cc8cce473241b36aabc302ab7d36963f45676`.
Old source-bound receipts were retained unchanged.

## Five impacts

- **Scaffold:** existing ENV owns the prerequisite in its existing startup command.
  No generator or pattern is added/promoted; P1/SERVICE remain downstream.
- **Shared UI:** none; no user screen or saving behavior changes.
- **Agent context:** root instructions suffice. Runbook and KDG handoff identify actual
  commands and remaining gates; no generated context exists.
- **Documentation:** this evidence, DEVELOPMENT and KDG navigation distinguish the
  executable refusal from undelivered runtime acceptance.
- **ADR:** accepted isolation/release/ownership/scaffold decisions remain unchanged;
  no new decision or edit to an accepted ADR is required.
