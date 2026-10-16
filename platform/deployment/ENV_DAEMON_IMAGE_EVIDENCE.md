# ENV daemon-local image identities — 2026-10-15

This bounded increment belongs to the existing ENV image/startup owners under the
[environment contract](../docs/architecture/contracts/scaffold-environment-and-generation.md).
The [Build record](../../_bmad-output/implementation-artifacts/spec-env-daemon-image-identities.md)
tracks the completed bounded implementation and verification. Runtime readiness
remains false.

## Source evidence and boundary

The [preceding volume proof](ENV_RUN_VOLUME_EVIDENCE.md) and
[immutable selection proof](ENV_IMMUTABLE_CREATE_EVIDENCE.md) preserve guarded startup.
They do not establish what image a daemon resolves from the selected child reference.

Docker 28's [InspectResponse type](https://github.com/moby/moby/blob/v28.0.0/api/types/image/image_inspect.go)
defines Id as the digest of image configuration, distinct from manifest digests in
RepoDigests. Repository metadata can be absent and multiple manifests can reference
the same config. The [image inspect route](https://github.com/moby/moby/blob/v28.0.0/api/server/router/image/image_routes.go)
resolves the requested name through ImageInspect. This increment uses exact digest
references, then config IDs, and checks the returned ID and platform. It does not
derive identity from a mutable tag or require a child entry in RepoDigests.

The existing image owner already retains verified child-manifest bytes containing
the config descriptor. Extracting its digest requires no config or layer download.
The resulting check establishes daemon-reported identity observations only: it does
not independently hash local image bytes or establish continuity across separate
daemon connections and a later execution. The existing 64 KiB response bound remains;
oversized real metadata must fail qualification rather than expand limits silently.

## Acceptance and verification

Initial owner contract RED: `python3 -m unittest discover -s platform/deployment/tests
-p test_images.py -k selection_plan` failed with missing `config_plan`. The same focused
check passed after the existing image owner returned child-reference→config-digest
bindings alongside the unchanged tag→child selection plan. The private-daemon adapter
and startup transfer pass final qualification and independent review.

## Five impacts and remaining gates

- Scaffold: extend existing ENV image/startup/transport owners and proof fixtures.
  P1/SERVICE retains schema, generator, templates, clients and consuming-output tests.
- Shared UI: no change.
- Agent context: existing root rules suffice; actual commands belong in owner runbooks.
- Documentation: owner runbook/evidence, Build record and KDG navigation/memlog.
- ADR: existing isolation, release, dependency and safe-logging decisions apply; none changed.

Real Docker >=28/kernel isolation, image availability/layer compatibility, execution-time
enforcement, complete startup/helper inventory, volume use/replacement policy, guarded
lifecycle, deployment PostgreSQL equivalence and P1/SERVICE remain open. Identity/Access/
WRITE and KDG server delivery remain downstream. No real daemon mutation, pull,
container, SQL/migration, account/access, provisioning, deployment, Leave or pilot use.

## Requirement-to-test traceability

| Requirement | Executable evidence |
| --- | --- |
| Owner-derived child/config identities | `test_images.py` selection-plan test derives expected IDs from retained child bytes |
| Four exact references, fresh observations, no tag authority, safe projection | `test_daemon_images.py::test_exact_fresh_observations_ignore_tags_and_discard_sensitive_metadata`; public positive/index-only controls |
| Missing or mismatched image/platform refuses without mutation | `test_complete_negative_matrix`; public missing/wrong-id/wrong-platform/variant/replacement controls |
| Owner evidence required before daemon access | `test_missing_and_stale_evidence_refuse_before_daemon` |
| Mid-observation evidence/lock changes refuse | `test_changed_evidence_and_lock_during_observation_refuse` |
| One bounded daemon phase and strict HTTP handling | `test_one_total_deadline_includes_version_and_all_inspections`; public old-daemon/malformed/oversized/slow/daemon-error controls |
| Closed read-only image routes | `test_foreign_and_mutating_routes_refuse_before_connect`; exact nine-GET event oracle |
| Same-run serialization and distinct-run isolation | `test_same_run_lock_bounds_concurrent_checks`; `test_distinct_run_has_independent_lock_and_observations` |
| No missing/foreign fixture descriptors | `test_omitted_and_foreign_startup_descriptors_refuse_before_events`; startup command guards |
| Observation transfer into process fixture | `test_startup_adapter.py` public acquired-descriptor integration and retained-child owner tests; public pinned CLI positive proof |

Public qualification uses a fresh source-bound UUID. The runner independently derives
all four expected identities from raw retained child bytes, asserts exact statuses,
safe output and GET-only image traffic, and preserves thirteen evidence files plus
preparation/startup source bindings. The whole-command harness allows 600 seconds for
bounded owner tool revalidation; this does not expand the five-second daemon deadline.

## Qualification attempts

Fresh run `26946863-91af-4e92-b9bd-ceca8201bcf2` passed prepare, six-tool
qualification and image-owner qualification. The first public positive attempt refused
with `images_cli/command_refused`; an unchanged owner repeat then passed. This refusal
is retained as an unsuccessful attempt, not counted as acceptance evidence.

An overlapping initial regression run reported 26 failures and one downstream error
among 308 tests, all in network/config preparation with `port_unavailable`. Owner
repeat qualification calls `dev.prepare`, which reserves the selected ports. Isolated
network 26 and run-config 8 checks passed unchanged afterward. Final regression and
public qualification must run sequentially to avoid competing for these ports.

## Commands

Fresh owner preparation and qualification (all exit 0):

```sh
python3 platform/deployment/dev.py prepare --target platform/deployment/environments/kdg-local.json --run-id 26946863-91af-4e92-b9bd-ceca8201bcf2
python3 platform/deployment/toolchain.py qualify --target platform/deployment/environments/kdg-local.json --run-id 26946863-91af-4e92-b9bd-ceca8201bcf2
python3 platform/deployment/images.py qualify --target platform/deployment/environments/kdg-local.json --run-id 26946863-91af-4e92-b9bd-ceca8201bcf2
```

Each public image control uses:

```sh
python3 platform/deployment/tests/qualify_daemon_images.py --target platform/deployment/environments/kdg-local.json --run-id 26946863-91af-4e92-b9bd-ceca8201bcf2 --control <control>
```

Each public startup control uses the same arguments with
`platform/deployment/tests/qualify_startup.py`. The protected final record retains
all exact argv arrays, results, source bindings and evidence hashes.

Independent review produced nine finding instances: seven coverage findings grouped
into six focused test patches; two rejected with specific call-boundary/handler evidence.
The edge-case reviewer returned no findings. No deferred work or new production surface.
Focused fix verification: `python3 -m unittest discover -s platform/deployment/tests -p test_daemon_images.py` passes 16; corresponding `test_startup_adapter.py` passes 38. Final full regression passes 315 tests in 57.409s.

Public image controls on the fresh run:

| Control | Exit / code |
| --- | --- |
| positive, index-only | 0 / daemon_images_synthetic_qualified |
| missing | 2 / image_missing |
| wrong-id, wrong-platform, variant, replacement | 2 / image_identity_mismatch |
| old-daemon | 2 / docker_28_required |
| malformed, oversized | 2 / docker_response_invalid |
| slow | 2 / docker_timeout |
| daemon-error | 2 / image_inspection_failed |

Every output retains `runtime_ready=false`. Both positives report exactly nine GETs;
negative qualifier event validation checks the exact expected prefix before emitting
the safe code. Public output excludes the sensitive metadata/error sentinel.

Public startup controls all pass: positive→exit 0 `synthetic_boundary_proven`;
invalid-network→exit 2 `network_not_run_owned`; contaminated-workdir→exit 2
`workdir_contaminated`; reject-command→exit 2 `expected_command_rejected`;
invalid-selection-plan→exit 2 `invalid_selection_plan`. The positive uses the actual
qualified Supabase CLI 2.120.0, asserts all four returned observations against retained
child bytes and preserves `create_refused=true`, `container_executed=false`.

All 17 public controls completed successfully. Thirteen retained evidence files preserve
bytes, inode, mode and mtime; preparation/startup source hashes are unchanged. Protected
record: `.local/daemon-image-qualification/26946863-91af-4e92-b9bd-ceca8201bcf2.json`,
SHA-256 `4e39af62be7858040f68b061656fd24094a4b99235c79c253d23048725fe74ab`.
No old receipt or interrupted run was repaired.

## Final verification

`python3 -m unittest discover -s platform/deployment/tests -p 'test_*.py'`:
315 tests, 57.409s, OK. Run alone after public qualification; all matrix/patch tests
were discovered and executed, with no skips. Focused implementation suites previously
passed image 34, startup 38, daemon 16, network 26 and run-config 8.

`python3 platform/deployment/dev.py up --target platform/deployment/environments/kdg-local.json
--run-id 26946863-91af-4e92-b9bd-ceca8201bcf2`: exit 2 `docker_28_required`,
`runtime_ready=false`. This remains a read-only prerequisite check; no upgrade or
container execution occurred. Changed Python files compile; scoped `git diff --check`
and local documentation-link validation pass. Requirement/test matrix and all five
impact decisions are recorded above. Seven review instances fixed, two disproved,
none deferred. Concurrent Leave/PtS documents are outside the scoped commit.
