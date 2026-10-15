# ENV run-owned database-volume acquisition — 2026-10-15

This increment belongs to the existing ENV owner under the
[environment contract](../docs/architecture/contracts/scaffold-environment-and-generation.md).
The [Build record](../../_bmad-output/implementation-artifacts/spec-env-run-volume.md)
tracks implementation and verification. Runtime readiness remains false.

## Source evidence and boundary

The [preceding pinned-CLI proof](ENV_IMMUTABLE_CREATE_EVIDENCE.md) observes the database
volume name `supabase_db_<project>`. Preparation previously reserved `<project>-database`.
This item aligns preparation with the observed CLI convention and verifies ENV ownership
before handing a descriptor to the existing startup fixture.

The [Docker 28 volume router](https://github.com/moby/moby/blob/v28.0.0/api/server/router/volume/volume_routes.go)
looks up local volumes by name and returns HTTP 201 from its create route. The
[volume store](https://github.com/moby/moby/blob/v28.0.0/volume/service/store.go)
can return an already-existing volume without changing its labels or options.
A 201 response therefore does not prove this attempt created the volume. Returned
metadata and a subsequent inspection must satisfy the exact owned local profile.

The [volume API type](https://github.com/moby/moby/blob/v28.0.0/api/types/volume/volume.go)
includes name, driver, scope, labels and options; creation time is optional. Ordinary
inspection omits the usage information supplied by system disk-usage reporting.
This adapter proves an observed ownership/configuration profile only. It does not
prove immutable identity, emptiness, absence of attachments or runtime isolation.
Mountpoint is neither followed nor published. Uncertain creates are never retried or
deleted automatically.

## Acceptance and verification

Before implementation, the preparation acceptance suite ran 16 tests with exactly one
failure: `test_reserved_resource_names_are_exact_and_disjoint_between_runs` still
received `<project>-database`. The new volume suite also failed because its adapter
did not exist. After implementation the focused volume suite passed 16 tests in
8.333s, startup 36 in 5.297s, and preparation 16 in 2.660s. The root independently
repeated preparation: 16 passed in 2.678s.

Fresh run `701106c9-09f1-44ac-8350-d2172a005ffd` passed preparation, cached tool
qualification and manifest-only image qualification using the unchanged dependency
baseline. Commands from repository root:

```sh
python3 platform/deployment/dev.py prepare --target platform/deployment/environments/kdg-local.json --run-id 701106c9-09f1-44ac-8350-d2172a005ffd
python3 platform/deployment/toolchain.py qualify --target platform/deployment/environments/kdg-local.json --run-id 701106c9-09f1-44ac-8350-d2172a005ffd
python3 platform/deployment/images.py qualify --target platform/deployment/environments/kdg-local.json --run-id 701106c9-09f1-44ac-8350-d2172a005ffd
python3 platform/deployment/tests/qualify_volumes.py --target platform/deployment/environments/kdg-local.json --run-id 701106c9-09f1-44ac-8350-d2172a005ffd --control positive
python3 platform/deployment/tests/qualify_startup.py --target platform/deployment/environments/kdg-local.json --run-id 701106c9-09f1-44ac-8350-d2172a005ffd --control positive
python3 -m unittest discover -s platform/deployment/tests -p test_volumes.py
python3 -m unittest discover -s platform/deployment/tests -p test_startup_adapter.py
python3 -m unittest discover -s platform/deployment/tests -p test_dev.py
python3 -m unittest discover -s platform/deployment/tests -p 'test_*.py'
```

The volume command was repeated for every control below; missing-preparation used
a fresh unprepared UUID. Every output retained runtime_ready=false.

| Control | Exit / exact code |
| --- | --- |
| positive, existing, racing-owned | 0 / volume_synthetic_qualified |
| foreign, racing-foreign, unsafe-options, cluster | 2 / volume_not_run_owned |
| changed | 2 / volume_changed |
| lost-response, malformed, oversized | 2 / docker_response_invalid |
| old-daemon | 2 / docker_28_required |
| slow | 2 / docker_timeout |
| daemon-error | 2 / volume_inspection_failed |
| missing-preparation | 2 / prepared_run_required |

The actual pinned CLI positive reached its nine expected events through the acquired
descriptor, selected the qualified PostgreSQL child digest and refused create.
Actual `dev.py up` with this target/run still exited 2 / docker_28_required.
All four startup negatives retained their exact prior codes: invalid-network →
network_not_run_owned; contaminated-workdir → workdir_contaminated; reject-command →
expected_command_rejected; invalid-selection-plan → invalid_selection_plan (exit 2).
All 13 retained preparation/tool/image files preserved bytes, inode, mode and mtime;
source bindings stayed identical. Protected ignored control record:
`.local/volume-qualification/701106c9-09f1-44ac-8350-d2172a005ffd.json`, SHA-256
`7072ae8b3036cb03fd34802f6b90e89242c603e16a3fd3a51f09712c38965e1c`.

| Requirement / matrix row | Executed volume acceptance coverage |
| --- | --- |
| Absent volume, exact create/reinspection, startup handoff | absent_acquires_exact_volume_and_hands_complete_descriptor_to_startup |
| Owned existing / racing-owned, foreign collisions | all_private_controls |
| Exact profile, null/empty options, cluster/unsafe metadata | descriptor_requires_exact_safety_fields_and_types; startup_refuses_incomplete_or_mismatched_volume |
| Response errors, bounded total deadline, no uncertain retry | all_private_controls; one_operation_deadline_spans_version_and_network_requests; lost_response_later_attempt_inspects_without_post |
| Preparation/source/run/lock changes | preparation_and_source_changes_during_daemon_exchange_refuse; symlink_unprotected_and_replaced_lock_refuse; changed_evidence_before_post_and_handoff_refuses; changed_target_inventory_and_lock_at_mutation_and_handoff; changed_source_inside_handoff_refuses_result |
| Changed descriptor / POST response / missing reinspection | create_response_and_reinspection_must_match; all_private_controls |
| Same-run and cross-network serialization | concurrent_same_run_is_bounded_and_no_second_daemon_access; network_lock_blocks_volume_adapter_before_daemon_contact |
| Missing preparation, old daemon, fixed endpoint | missing_preparation_no_daemon_access; all_private_controls; public_endpoint_override_is_rejected |

Root regression: **294 deployment tests passed in 58.221s**, no skips. Compilation
and scoped whitespace checks pass. Independent review classified eight finding instances (seven distinct causes), with
no deferred item. All eight instances are fixed. The CreatedAt marker test observed unsafe publication
before the public result omitted that field. Internal continuity still uses it.
Removing either forwarding hop independently caused one expected assertion failure,
`boundary_not_proven`, with no test errors; the experiment altered in-memory test
functions only. With forwarding intact, the new integrated test checks the actual
private CLI volume-inspect response against an independently expected full descriptor.
Acquisition refusal prevents startup qualification. The racing-owned fixture now
preserves a distinguishable pre-existing winner timestamp; two simultaneous runs
acquire independently and reject cross-run descriptors. A valid create command with
missing/foreign volume evidence refuses before any create event.

Final focused suites: **19 volume tests in 10.688s**, **38 startup tests in 11.367s**.
The internal callback is explicitly a trusted immediate nonblocking constructor;
deadline checks cannot preempt arbitrary Python. Public CLI qualification closes the
private acquisition daemon/lock before the separate process proof, so it proves
transfer rather than locked continuity through startup.

The first post-review public harness used an outer 60-second limit and interrupted
startup evidence revalidation on run `930846fe-6217-44f1-95c9-2f4efec4cb8c`.
Its `.qualify.lock` remained, and retry correctly refused with
`existing_images_required`. That run is retained unchanged, not repaired. The final
harness allows 180 seconds for the whole qualification (including repeated owner
evidence checks); production adapter and CLI execution deadlines are unchanged.

Final public commands above were repeated using fresh run
`3d701a44-6ed0-4dba-9eef-e851dc957a51`: preparation, tools and image qualification
passed; all 15 volume and five startup controls passed with the same expected codes.
All 13 retained preparation/tool/image files and source bindings stayed unchanged.
Protected ignored record `.local/volume-qualification/3d701a44-6ed0-4dba-9eef-e851dc957a51.json`
has SHA-256 `466e9cccf6508d1acfa61120c14d1e84891dec38b2401fe9fb98b790ab6d7097`.
The earlier initial run's 13 evidence files were independently rechecked and unchanged.

## Five impacts and remaining gates

- Scaffold: reusable ENV volume adapter and reserved identity alignment; existing
  P1/SERVICE retains generator/schema/template/client/output work. No alternate generator.
- Shared UI: no change.
- Agent context: current root rules suffice; actual commands and limits belong in the runbook.
- Documentation: owner runbook/evidence, Build record and KDG navigation/memlog.
- ADR: existing isolation, dependency, release and logging decisions apply; none changed.

Real Docker >=28 and kernel isolation, volume usage/attachment policy, residual
name-replacement races, execution-time digest enforcement, full startup/helpers,
deployment PostgreSQL compatibility, guarded lifecycle and P1/SERVICE remain open.
Identity/Access/WRITE and KDG server work remain downstream. Verification uses private
synthetic daemons/process fixtures only; no real Docker mutation, SQL, migration,
account/access, infrastructure, deployment, Leave domain or real-data pilot action.

Final regression first ran 299 tests in 115.729s with one error in the existing
detached-process cleanup test: `/proc/<pid>/stat` disappeared between existence
check and read (`ProcessLookupError`). The test now accepts FileNotFoundError or
ProcessLookupError as observed termination; its live-process failure remains.
Focused cleanup regression passed (1 test, 0.467s). No bound proof source changed.

The next full run (299 tests, 108.277s) exposed the identical `/proc` read race
in the other existing grandchild-cleanup test. Applied the same narrow termination
handling there; its focused test passed (1 test, 0.306s). Neither change alters
production cleanup, deadlines, or the assertion against running descendants.

Final post-correction regression: **299 tests passed in 96.309s**, no skips.
Compilation, scoped whitespace and local documentation links pass. Final actual
`dev.py up` again refused with `docker_28_required`. All eight review instances
are fixed, none deferred; the two additional cleanup-test races are corrected.
