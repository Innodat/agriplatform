# ENV combined run-resource acquisition — 2026-10-16

Completed bounded delivery under the existing ENV owner and
[environment contract](../docs/architecture/contracts/scaffold-environment-and-generation.md).
[Build record](../../_bmad-output/implementation-artifacts/spec-env-combined-resources.md).

## Scope and limits

Compose the existing image/network/volume owner algorithms under one run lock, daemon
connection/version check and total five-second daemon phase. Verify owner tools/evidence
outside that phase, inspect images before resource POSTs, and recheck joint observations
before a constructor-only handoff. Existing standalone APIs retain their policies.
All verification uses isolated synthetic Unix daemons. `dev.py up` remains gated.

This establishes guarded joint acquisition observations, not a reservation against
other clients, fresh/exclusive volume storage, execution continuity, bootstrap/secret
safety or runtime readiness. No container, SQL, migrations, accounts/access, infrastructure,
deployment, real-data pilot, Leave or dependent KDG implementation is included.

## Source investigation and item selection

The pinned CLI source commit is `753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4` (2.120.0).
[Start gates](https://github.com/supabase/cli/blob/753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4/apps/cli/src/commands/start/start.gates.ts)
select Kong/Auth/PostgREST for the effective minimal config; PostgreSQL is handled
separately. The [image catalogue](https://github.com/supabase/cli/blob/753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4/apps/cli/src/shared/services/Dockerfile)
also contains one-shot diff/test images used by other commands.
[PG setup](https://github.com/supabase/cli/blob/753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4/apps/cli/src/command-internal/db-bootstrap/db-setup.ts)
gates Realtime, Storage and Auth migration jobs on effective configuration. The selected
config disables Realtime/Storage; Auth's helper reuses the already-qualified GoTrue
identity. No additional image identity is required by this source trace. Actual helper
execution, immutable dispatch and SQL policy remain unqualified. That source accounting
is why joint resource acquisition was selected rather than another image collector.

## Five impacts

- Scaffold: existing ENV owners and test tooling compose acquisition; no new generator/service.
- Shared UI: none.
- Agent context: existing root rules suffice; owner runbook holds actual commands.
- Documentation: runbook, evidence, Build record, KDG resume and append-only memlog.
- ADR: existing isolation, safe logging and release decisions apply unchanged.

## Acceptance and verification

Pre-extraction characterization outside the restricted socket sandbox:
- `python3 -m unittest discover -s platform/deployment/tests -p test_networks.py`: 28 passed,14.857s.
- Same command with `test_volumes.py`: 21 passed,8.496s.

Initial acceptance failure, image characterization, final focused checks, requirement/test
mapping and independent review follow below. No source extraction preceded these runs.

Image characterization: `python3 -m unittest discover -s platform/deployment/tests
-p test_daemon_images.py` passed 18 in 15.743s, before extraction.

Initial `test_resources.py` RED was a missing-module import (1 loader error0.000s).
A temporary delegating implementation then exercised the three unchanged standalone
adapters. Its first test stopped at missing constructor handoff (1failure0.200s);
placing the independent connection assertion first produced the intended behavioral RED:

```sh
python3 -m unittest discover -s platform/deployment/tests -p test_resources.py -k combined_exact_order
```

One test failed0.272s with `AssertionError: 3 != 1`. No shared core extraction preceded
this failure. The temporary delegating implementation is characterization scaffolding,
not the delivered coordinator. Root runs socket verification serially outside sandbox.

Initial connected implementation `test_resources.py` ran10 tests in21.187s, with one
error: deleting the tool receipt raised raw FileNotFoundError in shared custody
file_snapshot before owner verification. Nine tests passed, including ordered one-peer
acquisition and boundary failures. Missing owner evidence must produce an explicit safe
refusal before any socket; test expectations will stay narrow. Subsequent correction and passing verification follow below.

Missing owner snapshot input now maps to the established
`startup/existing_images_required` refusal. The missing image/tool cases both assert
that exact stage/code and zero socket construction. Focused `test_resources.py
-k missing_owner` passed 1 in 0.127s; full combined suite passed 10 in 19.779s.
Post-extraction network suite passed 28 in 15.692s.

| Requirement | Executed focused coverage |
| --- | --- |
| One connection/version, exact joint order and constructor | `test_combined_exact_order_single_connection_and_constructor` |
| Exact failures before later POST/handoff | `test_negative_matrix_refuses_without_handoff_or_later_requests`; qualifier literal terminal counts |
| Missing protected owner evidence, no daemon contact | `test_missing_owner_evidence_refuses_before_connection` |
| Source/receipt/target/inventory/lock changed before each mutation/handoff | `test_changed_evidence_before_each_post_and_handoff_prevents_progress` |
| Final child/config/network/volume replacement | `test_late_resource_replacement_refuses_before_constructor` |
| Disconnect/truncation/observable EOF at every exchange | `test_transport_failure_at_every_exchange_never_reconnects_or_replays` |
| One total deadline across resource phases | `test_single_total_deadline_does_not_reset_at_adapter_boundaries` |
| Callback, evidence, deadline and post-owner failures release resources | `test_callback_exception_and_final_evidence_change_release_lock_and_connection` |
| Socket pathname replacement retains original peer | `test_socket_path_replacement_retains_original_peer` |
| Same-run concurrency refuses before second connection | `test_same_run_concurrent_acquisition_refuses_before_second_connection` |

Every matrix row has executed test coverage; final independent review/qualification follows.

Post-extraction volume suite passed 21 in 8.889s and image suite passed 18 in 8.358s.
All four affected focused suites are green. Root inspected the complete implementation/
test/runbook diff and its matrix coverage. Three independent review layers launched
together against the42,816-byte diff. No final public proof is claimed before review fixes.

## Independent review and corrections

Three layers returned eight finding instances; seven retained for local fixes, one
evidence-absence claim disproved by this record. Edge-case review found no additional
issue. B2/V1 share the public-command verification gap; every verdict is in the Build.
No findings deferred and no public runtime surface or product decision changed.

Root independently reproduced the final handoff gap with
`python3 -m unittest discover -s /tmp -p test_env_combined_audit.py` (1test0.291s):
read EOF injected during final evidence validation after the last response remained
observable, yet the constructor ran. Corrections add an immediate readiness/budget
check plus synchronized regression. Coverage fixes include public status/JSON projection,
explicit same-run recovery after uncertain creation, private network-conflict sequencing,
identical-byte/restore custody, and final unsafe/missing/error descriptors.

Review regression RED before applying the handoff fix:
`python3 -m unittest discover -s platform/deployment/tests -p test_resources.py
-k observable_eof` ran1 in0.642s with2 failing subcases. Both before-constructor and
after-constructor injections failed because no refusal was raised. This independently
protects the reproduced state before source correction.

## Final review-fix checks

`test_resources.py -k observable_eof` passed 1 in 0.412s after the fix; the full expanded
combined suite passed 16 in 32.894s. Root strengthened the restore case to preserve the
original mtime as well as bytes; `test_resources.py -k same_byte` passed 1 in 1.414s.
All seven retained review instances are fixed; one claim disproved, none deferred.

Added traceability: `test_public_main_status_json_parser_and_constructor_wiring`,
`test_same_run_after_lost_create_response_inspects_and_reuses_without_duplicate_post`,
`test_private_network_conflict_recovers_owned_winner_and_finishes_joint_checks`,
`test_same_byte_evidence_replacement_or_restored_write_blocks_each_boundary`,
`test_final_network_and_volume_checks_reject_foreign_unsafe_missing_and_error`, and
`test_observable_eof_at_final_evidence_boundaries_refuses`.

Root inspected the updated 55,790-byte implementation/test/runbook diff. Compilation,
scoped whitespace and local links passed across 13 delivery paths. No root UI/context,
accepted ADR or dependency pin changes are needed. Final public qualification and full
regression below use the frozen production/qualifier sources.

## Frozen-source public qualification

Fresh run `32ea0b48-b882-464a-b5ce-e5544af648b3` passed preparation, pinned-tool and
read-only registry-manifest qualification serially. Public adapter proof follows:

```sh
python3 platform/deployment/dev.py prepare --target platform/deployment/environments/kdg-local.json --run-id 32ea0b48-b882-464a-b5ce-e5544af648b3
python3 platform/deployment/toolchain.py qualify --target platform/deployment/environments/kdg-local.json --run-id 32ea0b48-b882-464a-b5ce-e5544af648b3
python3 platform/deployment/images.py qualify --target platform/deployment/environments/kdg-local.json --run-id 32ea0b48-b882-464a-b5ce-e5544af648b3
python3 /tmp/env-combined-public-proof.py 32ea0b48-b882-464a-b5ce-e5544af648b3
```

The temporary harness invokes the existing `tests/qualify_resources.py` with all 13
`--control` values and standalone `qualify_networks.py`, `qualify_volumes.py`,
`qualify_daemon_images.py` positives, using that same target/run. It checks exact
exit/result codes, safe output, one version event, thirteen retained file identities
and preparation/startup source snapshots. The protected record retains each exact
command/result; this temporary orchestration is not a separate delivery entry point.

All **16 public checks passed**: all 13 combined controls plus standalone network,
volume and image positives. Combined positive/existing returned the exact 30/27-request
sequences, one connection/version and constructor-only handoff. Negative controls
matched exact refusal codes and terminal event prefixes. No checked sensitive markers
or stderr appeared; every result kept runtime_ready=false. All thirteen retained files
kept identical hashes, inodes, modes and mtimes; source snapshots also remained identical.

Protected record:
`.local/combined-resources-qualification/32ea0b48-b882-464a-b5ce-e5544af648b3.json`
SHA-256 `b67e8c461609346bde7e2d1d5ed7f6a38c76be5bc948ab906e98dbb92942aeeb`.

| Qualifier | Control | Exit / code |
| --- | --- | --- |
| `qualify_resources` | `positive` | 0 / `resources_synthetic_qualified` |
| `qualify_resources` | `existing` | 0 / `resources_synthetic_qualified` |
| `qualify_resources` | `image-missing` | 2 / `image_missing` |
| `qualify_resources` | `image-foreign` | 2 / `image_identity_mismatch` |
| `qualify_resources` | `network-foreign` | 2 / `network_not_run_owned` |
| `qualify_resources` | `network-replaced` | 2 / `network_replaced` |
| `qualify_resources` | `volume-foreign` | 2 / `volume_not_run_owned` |
| `qualify_resources` | `volume-changed` | 2 / `volume_changed` |
| `qualify_resources` | `lost-network-response` | 2 / `docker_response_invalid` |
| `qualify_resources` | `lost-volume-response` | 2 / `docker_response_invalid` |
| `qualify_resources` | `old-daemon` | 2 / `docker_28_required` |
| `qualify_resources` | `malformed` | 2 / `docker_response_invalid` |
| `qualify_resources` | `slow` | 2 / `docker_timeout` |
| `qualify_networks` | `positive` | 0 / `network_synthetic_qualified` |
| `qualify_volumes` | `positive` | 0 / `volume_synthetic_qualified` |
| `qualify_daemon_images` | `positive` | 0 / `daemon_images_synthetic_qualified` |

## Final regression and closure

`python3 -m unittest discover -s platform/deployment/tests -p 'test_*.py'`
passed **374 tests in 157.842s**, exit 0, after public qualification and outside the
restricted socket sandbox. Output retained at `/tmp/env-combined-regression.log`.

`python3 platform/deployment/dev.py up --target platform/deployment/environments/kdg-local.json
--run-id 32ea0b48-b882-464a-b5ce-e5544af648b3` exited 2 with `docker_28_required`,
`runtime_ready=false`. No container or real Docker mutation occurred.

Compilation, scoped whitespace and local links passed. Review closed seven retained
finding instances; one disproved, none deferred. All matrix rows have executed coverage.
Thirteen delivery paths are scoped for commit. Concurrent epics.md and Leave
implementation-plan/planning-handoff-e3 changed during this work; their current contents
are preserved outside the commit. Dependency pins, accepted ADRs, shared UI and root
agent instructions remain unchanged. Remaining ENV runtime/bootstrap/secret, volume
freshness/reuse, lifecycle/recovery/health and deployment-target compatibility gates,
P1/SERVICE and provider/device proof remain explicit before dependent consumers.
