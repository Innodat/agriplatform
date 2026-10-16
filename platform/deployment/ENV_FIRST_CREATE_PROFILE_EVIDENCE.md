# ENV complete first-create profile — 2026-10-16

Bounded implementation completed under the existing ENV/startup owner and
[environment contract](../docs/architecture/contracts/scaffold-environment-and-generation.md).
The [Build record](../../_bmad-output/implementation-artifacts/spec-env-first-create-profile.md)
tracks acceptance and independent review. Preceding
[image observation qualification](ENV_DAEMON_IMAGE_EVIDENCE.md) does not validate the
complete command that would consume those observations. Runtime readiness remains false.

## Source-backed authority

All upstream references use pinned Supabase CLI source commit
`753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4`:

- [PostgreSQL service](https://github.com/supabase/cli/blob/753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4/apps/cli/src/command-internal/db-bootstrap/postgres.service.ts): PG17 bootstrap program, four environment inputs, volume, healthcheck, aliases and restart policy.
- [Argument builder](https://github.com/supabase/cli/blob/753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4/apps/cli/src/command-internal/db-bootstrap/docker-create-args.ts): fixed option order and key-only environment names.
- [Container lifecycle](https://github.com/supabase/cli/blob/753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4/apps/cli/src/command-internal/db-bootstrap/container-lifecycle.ts): project/workdir labels and child-process environment transfer; secret-file copying occurs after create and stays unqualified here.
- [Local container inputs](https://github.com/supabase/cli/blob/753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4/apps/cli/src/command-internal/db-bootstrap/local-container-inputs.ts): Linux host-gateway entry.
- [Published local defaults](https://github.com/supabase/cli/blob/753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4/packages/stack/src/Defaults.ts) and [Auth config](https://github.com/supabase/cli/blob/753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4/packages/config/src/auth/index.ts): synthetic default environment values.

The public bootstrap comes from the same commit's
`apps/cli/src/command-internal/db-bootstrap/templates/db-schema.sql.ts`,
`db-webhook.sql.ts` and `db-supabase.sql.ts`, composed by the PG>=15 function with empty
settings. Root independently decoded only the literal template escapes and composed
that function's fixed text: 9642 UTF-8 bytes, SHA-256
`6f995b129657d28b15a97a1c8a957a7c0015a9865880747c25ad00e3b6d7dd86`.
This hash describes reviewed public source bytes, not runtime credentials. Actual
pinned-CLI matching remains required; captured output never becomes approval authority.

## Acceptance and verification

Initial ATDD RED: `python3 /tmp/env-profile-red.py`,
`UnsafeAcceptance.test_arbitrary_script_refused`, failed because the old fixture accepted
an arbitrary shell canary and emitted a positive create event. Implementation, review corrections, public qualification and final
regression are complete; results are recorded below. Tests must cover complete argv,
container environment and routing, altered bootstrap, input mutation and safe diagnostics,
then exercise the actual qualified CLI through the existing refused-create fixture.
Public qualification and full regression run sequentially because owner revalidation
briefly reserves the selected target ports.

## Five impacts and remaining gates

- Scaffold: existing ENV/startup profile and test owners; P1/SERVICE retains generator,
  schemas/templates, clients and consuming-output proof.
- Shared UI: none; no user-facing application surface changes.
- Agent context: existing root rules suffice; actual commands remain in owner runbooks.
- Documentation: owner runbook/evidence, Build record, KDG navigation/memlog.
- ADR: existing release, isolation, dependency and safe-logging decisions apply; none changed.

This increment establishes complete request/profile conformity and custody only through
refused dispatch. It does not prove bootstrap semantic safety, secret-file delivery,
resource/daemon continuity during execution, volume use policy, full helper inventory,
guarded lifecycle, deployed PostgreSQL compatibility, provider/device qualification or
P1/SERVICE generation. Identity/Access/WRITE and the KDG server slice remain downstream.
No real Docker mutation, shell/SQL execution, migrations, accounts/grants, infrastructure,
deployment, Leave or pilot action is included.

## Requirement-to-test traceability

| Requirement | Executable coverage |
| --- | --- |
| Exact source-backed request, image-only substitution, original inputs preserved | `test_public_source_fixture_digest_and_unchanged_input`; existing startup immutable-selection test; actual pinned CLI positive control |
| Every operand accounted for | `test_every_operand_change_deletion_duplicate_and_reordering_refused` |
| Complete bootstrap conformity | Same operand test changes SQL/path/interpolation and appends shell text; `invalid-create-script` public control |
| Container environment and private routing | `test_environment_missing_changed_routing_inline_and_extra_names`; public environment/routing controls |
| Mutation between validation and handoff refuses | `test_environment_or_arguments_mutation_during_transform_refused`; existing transformer corruption test |
| Source/owner continuity | Preparation source binding includes validator, public fixture and authority document; existing changed-source/owner guards |
| Safe output and real wrapper transfer | `test_real_wrapper_forwards_environment_and_safely_rejects_canaries`; public runner checks sentinel/default/SQL absence |
| Existing controls and bounded refused dispatch | `test_public_profile_controls_reach_same_process_boundary`, affected startup suite and all eight public controls |

Focused implementation verification: `python3 -m unittest discover -s
platform/deployment/tests -p test_create_profile.py` passes six tests; corresponding
`test_startup_adapter.py` passes 38. Final post-review public and regression results are recorded below.

## Review corrections and final commands

Three independent review layers returned ten finding instances. All ten were fixed
(nine distinct corrections after grouping the duplicated TLS finding), none deferred.
Corrections cover Docker request overrides, tuple inputs, valid negative-control
baselines, reproducible fixture derivation, independent test setup, input boundaries,
exact safe events and prerequisite-sequence rejection. Docker environment behavior
is documented by the [Docker CLI reference](https://docs.docker.com/reference/cli/docker/).

Root reran focused checks after corrections:

```sh
python3 -m unittest discover -s platform/deployment/tests -p test_create_profile.py
python3 -m unittest discover -s platform/deployment/tests -p test_startup_adapter.py
```

Results: 10 tests in 7.856s and 38 tests in 10.162s, both OK. The documented
source derivation was independently executed against the retained pinned primary
sources: 9642 bytes and the recorded SHA-256 match exactly. The implementer's attempted
startup rerun awaited approval and was aborted before receiving a process session;
root's successful rerun supersedes that unexecuted attempt.

Initial actual pinned CLI positive qualification passed on
`d73e4702-9e0e-474e-a1b6-46093ed46011` before review corrections, with nine events,
complete profile proof and create refused. Its evidence is preserved unchanged.
Final source-bound qualification uses fresh run `dd2afb69-8065-4304-ba71-e244a1539bc9`:

```sh
python3 platform/deployment/dev.py prepare --target platform/deployment/environments/kdg-local.json --run-id dd2afb69-8065-4304-ba71-e244a1539bc9
python3 platform/deployment/toolchain.py qualify --target platform/deployment/environments/kdg-local.json --run-id dd2afb69-8065-4304-ba71-e244a1539bc9
python3 platform/deployment/images.py qualify --target platform/deployment/environments/kdg-local.json --run-id dd2afb69-8065-4304-ba71-e244a1539bc9
```

Each public control uses `python3 platform/deployment/tests/qualify_startup.py
--target platform/deployment/environments/kdg-local.json
--run-id dd2afb69-8065-4304-ba71-e244a1539bc9 --control <control>`.
The protected final record retains exact commands/results, thirteen evidence-file
identities and preparation/startup source hashes. The public harness checks safe
output and independently derives image observations from retained child bytes.

Additional requirement/test links:

| Requirement | Focused test |
| --- | --- |
| Equivalent supported input containers | `test_list_and_tuple_create_are_equivalent` |
| Bounded typed profile inputs | `test_validator_malformed_inputs_and_resource_limits` |
| Invalid baseline cannot qualify a negative control | `test_controls_reject_invalid_original_profile_before_injection` |
| Missing/duplicate/reordered prerequisites and prior positive create refuse | `test_negative_controls_require_exact_prerequisite_sequence` |

## Final public qualification

Fresh prepare, toolchain and image qualification all exit 0. The exact public command
matrix above passes all eight controls:

| Control | Exit / code |
| --- | --- |
| positive | 0 / synthetic_boundary_proven |
| invalid-network | 2 / network_not_run_owned |
| contaminated-workdir | 2 / workdir_contaminated |
| reject-command | 2 / expected_command_rejected |
| invalid-selection-plan | 2 / invalid_selection_plan |
| invalid-create-script | 2 / expected_create_profile_rejected |
| invalid-create-environment | 2 / expected_create_profile_rejected |
| invalid-create-routing | 2 / expected_create_profile_rejected |

All retain `runtime_ready=false`. Positive proof reports `complete_create_profile_proven`
and `create_refused`, with `container_executed=false`. No sensitive canary, synthetic JWT
value, container environment name or SQL marker appears in public output. The private
wrapper compares inputs in memory only. The public harness verifies all thirteen
retained files preserve bytes, inode, mode and mtime, with unchanged preparation/startup
source bindings. Existing and interrupted runs remain untouched.

Protected qualification record:
`.local/create-profile-qualification/dd2afb69-8065-4304-ba71-e244a1539bc9.json`, SHA-256
`08fbfdd287f51b0ccb8082db0ccf23e20dbbcc3b72a3a62e80ef3311753fb5f5`.
Harness command: `python3 /tmp/env-create-profile-public-proof.py
dd2afb69-8065-4304-ba71-e244a1539bc9` (exit 0); individual public commands are retained
in the record and documented above so qualification does not depend on the temporary
harness remaining available.

## Final regression and gate

`python3 -m unittest discover -s platform/deployment/tests -p 'test_*.py'`:
325 tests in 72.060s, OK, no skips; run alone after public qualification.

`python3 platform/deployment/dev.py up --target platform/deployment/environments/kdg-local.json
--run-id dd2afb69-8065-4304-ba71-e244a1539bc9`: exit 2, `docker_28_required`,
`runtime_ready=false`. This is the existing read-only prerequisite gate; no real
container starts. Changed Python files compile; scoped whitespace and local links pass.
All ten review instances are fixed, none deferred. Concurrent Leave/PtS changes remain
outside this item and its scoped local commit.
