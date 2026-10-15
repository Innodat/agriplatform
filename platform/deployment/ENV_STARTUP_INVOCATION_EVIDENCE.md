# ENV guarded startup invocation — 2026-10-15

This increment belongs to the existing ENV owner under the
[environment contract](../docs/architecture/contracts/scaffold-environment-and-generation.md).
The [Build record](../../_bmad-output/implementation-artifacts/spec-env-startup-invocation.md)
covers a reusable invocation constructor and an actual pinned-CLI synthetic process
proof. Final qualification and regression checks pass; independent review is complete.
Runtime readiness is false.

## Boundary and source evidence

Supabase CLI2.120.0, pinned source commit
`753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4`, shells out to Docker by name.
The [container CLI implementation](https://github.com/supabase/cli/blob/753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4/apps/cli/src/command-internal/container-cli.ts)
prefers `docker` and may try `podman` on spawn failure. The proof must intercept both
through private fixture executables with absolute Python interpreters. A nonexistent
private Docker endpoint provides an additional boundary; no real executable dispatch
is permitted. The earlier Unix-API parser fixture alone cannot intercept this path.

The invocation fixes `SUPABASE_EXPERIMENTAL_STACK=0`,
`SUPABASE_USE_SLIM_IMAGES=0`, `SUPABASE_INTERNAL_IMAGE_REGISTRY=public.ecr.aws`,
and explicit workdir/network arguments. The
[registry implementation](https://github.com/supabase/cli/blob/753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4/apps/cli/src/command-internal/docker-registry.ts)
permits mirror fallback when the override is absent; project dotenv inputs can
override environment settings. The private workdir must exclude those inputs.

Upstream network inspection trusts an existing network without proving ownership or
publishing defaults. Its PostgreSQL create publishes55482→5432 without a host IP,
making the run-owned bridge's loopback-default option essential to future execution.
This increment validates network descriptor fixtures; it does not inspect or create
a real network or qualify actual network isolation.

The synthetic Docker boundary will supply only controlled inspection responses needed
to reach the first PostgreSQL create. That create is refused, before container start
or secret copying. Proof may retain selected safe image/name/network/port/mount facts,
never full argv, environment values, child output or request payload dumps.

## Acceptance and executed qualification

Acceptance was observed red before implementation:
`python3 -m unittest discover -s platform/deployment/tests -p test_startup_adapter.py`
failed with missing startup module. The final focused suite passes30 tests in3.265s.
The existing33 image-owner tests also pass after the repeat-only extension.

A necessary image-owner change prevents verification from recreating an absent run:
`images.qualify(args, existing_only=True)` never creates an image evidence directory
or enters collection. The default public qualifier keeps its collection behavior.
The race test renames the existing run before owner verification and asserts no
registry collection or replacement run. This source change invalidates older image
receipts, so final proof uses a fresh run instead of repairing or adopting old evidence.

Preparation and tool qualification succeeded for
`9d5d990f-e627-4fcb-bb0a-65a9e8c1570f`, using the existing verified tool archive cache.
The public image qualifier then retained the same four selected manifest identities.
Exact setup commands from repository root:

```sh
python3 platform/deployment/dev.py prepare --target platform/deployment/environments/kdg-local.json --run-id 9d5d990f-e627-4fcb-bb0a-65a9e8c1570f
python3 platform/deployment/toolchain.py qualify --target platform/deployment/environments/kdg-local.json --run-id 9d5d990f-e627-4fcb-bb0a-65a9e8c1570f
python3 platform/deployment/images.py qualify --target platform/deployment/environments/kdg-local.json --run-id 9d5d990f-e627-4fcb-bb0a-65a9e8c1570f
```

Final proof commands (positive uses the actual pinned CLI; invalid-network and
contaminated-workdir are preflight controls; reject-command invokes the fixture directly):

```sh
python3 platform/deployment/tests/qualify_startup.py --target platform/deployment/environments/kdg-local.json --run-id 9d5d990f-e627-4fcb-bb0a-65a9e8c1570f --control positive
python3 platform/deployment/tests/qualify_startup.py --target platform/deployment/environments/kdg-local.json --run-id 9d5d990f-e627-4fcb-bb0a-65a9e8c1570f --control invalid-network
python3 platform/deployment/tests/qualify_startup.py --target platform/deployment/environments/kdg-local.json --run-id 9d5d990f-e627-4fcb-bb0a-65a9e8c1570f --control contaminated-workdir
python3 platform/deployment/tests/qualify_startup.py --target platform/deployment/environments/kdg-local.json --run-id 9d5d990f-e627-4fcb-bb0a-65a9e8c1570f --control reject-command
```

| Control | Executed result |
| --- | --- |
| positive | Exit0, synthetic_boundary_proven;9 selected events, expected PG create refused, runtime_ready=false |
| invalid-network | Exit2, network_not_run_owned; no CLI start |
| contaminated-workdir | Exit2, workdir_contaminated; no CLI start |
| reject-command | Exit2, expected_command_rejected; exact direct fixture rejection event verified |

Final safe results and unchanged image-receipt metadata are retained under ignored
`.local/startup-invocation/final-controls-verified.json`. Initial pre-review controls
remain separately retained.
The positive image receipt SHA256 is
`e6d8919c18a1fd52e6d4dbf562396e915201a8584535962ae60a259a4e77e2fc`.
The positive source hash for startup.py is
`09a107de6230aecca78b7c12c934ebfc7f73152195b072ec57effee11e5768cf`.

Actual CLI characterization exposed two incorrect fixture assumptions before a
positive result: container inspect places its name before --format, and Effect places
the Docker child in its own session. Initial boundary_not_proven results were retained
as failures. The corrected parent stop verifies the direct CLI parent's UID, session/
process-group leadership, native executable and exact invocation arguments, using a
pidfd opened before those observations, then signals only that CLI.
Detached fixtures have a parent-death signal and five-second lifetime bound; protected
event files use nonblocking admission and a half-second lock deadline. Before/after
source snapshots bind the entrypoint and imported owner implementations/pins. A
synthetic CLI deliberately spawns its Docker child
in a separate session and proves that code after create never executes.

Nine observed events are container inspection, four cached-image inspections, volume
inspection, network inspection, duplicate-volume refusal and first PostgreSQL create.
Only synthetic cached-image/existing-volume state is supplied. The create uses selected
`public.ecr.aws/supabase/postgres:17.11.0.004`, the exact run project/volume, fixture
network ID,55482→5432 publishing and named-volume data mount. No host bind is admitted;
generated configuration bytes and allowed private Supabase
files are checked. The generated shell command’s SQL content remains unqualified
and is neither retained nor hashed; this proof establishes no broad runtime SQL policy.
The duplicate-volume attempt also receives a nonzero refusal;
this does not prove a fresh-volume startup or database bootstrap.

| Requirement / matrix row | Executed coverage in test_startup_adapter.py |
| --- | --- |
| Qualified run reaches controlled first create | isolated_process_boundary; actual positive CLI control |
| Missing/changed evidence, no install/refresh | missing_preparation; missing_image_receipt; changed_existing_receipt; incomplete_evidence; replaced_image_run |
| Wrong network/labels/options/attachments refuse | closed_network_contract; actual invalid-network control |
| Ambient/workdir/command isolation and safe selected output | private_invocation; unsafe_create_variants; every_unexpected_command; duplicate_volume; actual contamination/rejection controls |
| Malformed/oversized/link state, hang/flood/interruption | malformed_oversized_and_linked_fixture; malformed_state; hang_and_output_flood; interruption; no_running_grandchild; nonisolated_parent |

`python3 -m unittest discover -s platform/deployment/tests -p 'test_*.py'` passes245
tests in28.573s. Reserved-port owner probes and regression suites ran sequentially.
Compilation, scoped whitespace and local documentation links pass. The image receipt’s
hash, inode, modification time and mode stayed unchanged across all final controls.
These are isolated process/contract
checks, not a running environment or production readiness result.

## Independent review and final traceability

Three independent review layers reported12 instances. Eleven verified findings were
fixed; one was rejected with evidence because no runtime security-option/restart-policy
qualification was claimed. Nothing is deferred. The per-instance verdicts remain in the
Build record. Added tests cover:

| Review instances | Executed regression coverage |
| --- | --- |
| B1 | root_mode_owner_symlink_and_replacement; mutation_during_probe |
| B2/E1/E2 | state_hardlink_fifo_and_permissions; state_lock_is_bounded_and_replacement |
| B3/E2 | separate_session_fixture_dies_after_timeout_and_interruption |
| B5 | selected_facts has no repository_sql_inputs assertion; explicit shell_command_sql_qualified=false |
| B6 | missing_duplicate_and_reordered_prerequisites; isolated_process_boundary |
| B7 | source_changed_during_probe with temporary sources only |
| B8 | direct_control_requires_exact_rejection_event; synthetic_cli_unexpected_command |
| E3 | pidfd_precedes_observations_and_closes_on_death_or_mismatch |
| V1 | unchanged_inputs_succeed_and_mid_probe_mutations_refuse: image/tool receipt, payload, preparation/config/inventory |

## Five impacts and remaining gates

- Scaffold: reusable ENV invocation construction only; P1/SERVICE retains generator,
  schema, template, client and consuming-output work. No alternate generator.
- Shared UI: no change.
- Agent context: current root rules suffice; actual command and bounds belong in the
  [owner runbook](DEVELOPMENT.md).
- Documentation: this evidence, Build record, runbook and KDG next-session navigation.
- ADR: existing ownership, release and operational logging decisions apply; no accepted
  ADR changes.

Real Docker>=28/network ownership/binding, digest enforcement at execution, complete
startup/helper execution, database deployment compatibility, owner migration/fixtures,
guarded lifecycle, P1/SERVICE, Identity/Access/WRITE, Entra and installed-device proof
remain separate gates. Real `dev.py up` stays blocked. No real container, pull, SQL,
migration, account/access, infrastructure, deployment, Leave/KDG domain or pilot action
occurs in this increment.
