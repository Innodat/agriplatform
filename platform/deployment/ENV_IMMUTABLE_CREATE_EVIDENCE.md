# ENV immutable first-create selection — 2026-10-15

This bounded increment extends the existing image/startup owners under the
[environment contract](../docs/architecture/contracts/scaffold-environment-and-generation.md).
The [Build record](../../_bmad-output/implementation-artifacts/spec-env-immutable-first-create.md)
tracks completed implementation, verification and independent review. Runtime readiness
remains false.

## Why the boundary is needed

The selected Supabase CLI is 2.120.0, pinned source commit
`753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4`. Its
[image resolver](https://github.com/supabase/cli/blob/753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4/apps/cli/src/command-internal/docker-image-resolve.ts)
checks image-inspect exit success and returns the original candidate reference; it
does not use inspect output to replace that reference with a digest. The
[registry selector](https://github.com/supabase/cli/blob/753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4/apps/cli/src/command-internal/docker-registry.ts)
controls registry candidates, while the
[start gates](https://github.com/supabase/cli/blob/753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4/apps/cli/src/commands/start/start.gates.ts)
explicitly omit Kong from linked-project version pins. These sources do not establish
a native all-service digest override. Actual first-create behavior is established by
the [preceding CLI proof](ENV_STARTUP_INVOCATION_EVIDENCE.md).

The image owner already retains verified index and Linux/amd64 child manifests.
This increment connects that evidence to a pure startup command transformation.
The private executable fixture refuses the transformed create. Neither a manifest
receipt nor successful construction proves that a container ran with that image.

## Initial acceptance and verification

The first focused acceptance failed with missing immutable_first_create before code
was added. Focused suites then passed: startup 32 tests (root 3.945s), image owner
34 tests (implementer 4.110s). All 274 deployment tests passed in 60.422s, no skips.
The anonymous-token fixture previously reused one manifest across four images;
it now uses the existing distinct per-image fixtures with its token assertion unchanged.

Commands from repository root used fresh run b46431a1-c11b-45c5-8b7f-e19d8ea03470:

```sh
python3 platform/deployment/dev.py prepare --target platform/deployment/environments/kdg-local.json --run-id b46431a1-c11b-45c5-8b7f-e19d8ea03470
python3 platform/deployment/toolchain.py qualify --target platform/deployment/environments/kdg-local.json --run-id b46431a1-c11b-45c5-8b7f-e19d8ea03470
python3 platform/deployment/images.py qualify --target platform/deployment/environments/kdg-local.json --run-id b46431a1-c11b-45c5-8b7f-e19d8ea03470
python3 platform/deployment/tests/qualify_startup.py --target platform/deployment/environments/kdg-local.json --run-id b46431a1-c11b-45c5-8b7f-e19d8ea03470 --control positive
python3 -m unittest discover -s platform/deployment/tests -p test_startup_adapter.py
python3 -m unittest discover -s platform/deployment/tests -p test_images.py
python3 -m unittest discover -s platform/deployment/tests -p 'test_*.py'
```

Preparation, cached tool qualification and manifest-only image qualification exited 0.
The actual pinned CLI proof exited 0, synthetic_boundary_proven, with nine events;
its selected PostgreSQL image was
`public.ecr.aws/supabase/postgres@sha256:f2a84af37797675f0b27e27ea1fad2ebcd913ebf7ad60be05d7df0bcbd29e4b5`.
Image receipt SHA-256 was
`c109bee5615cdc14520946c37be53887e40b0527ed7831918ea36c774b74a3ec`.
All 13 retained evidence files and source bindings stayed unchanged across controls.

The public command was repeated with each negative control:

| Control | Exit / exact code |
| --- | --- |
| invalid-network | 2 / network_not_run_owned |
| contaminated-workdir | 2 / workdir_contaminated |
| reject-command | 2 / expected_command_rejected |
| invalid-selection-plan | 2 / invalid_selection_plan |

All outputs retain runtime_ready=false; positive also records container_executed=false,
create_refused=true, immutable_selection_proven=true and digest_enforcement=false.
Actual dev.py up on this run still exits 2, docker_28_required.

| Requirement | Executed focused coverage |
| --- | --- |
| Exact child mappings and repeat without collection | test_images.selection_plan_binds_exact_distinct_child_manifests |
| Only one operand changes; input preserved | test_startup_adapter.first_create_selects_child_and_preserves_every_other_operand |
| Unsafe/ambiguous/wrong image refusal | ambiguous_create_is_rejected_before_selection; unsafe_create_variants_refuse |
| Private process proof and sensitive-output exclusions | isolated_process_boundary_records_selected_facts_and_refuses_create |
| Missing/stale or changed evidence | missing_image_receipt_never_qualifies_or_installs; unchanged_inputs_succeed_and_mid_probe_mutations_refuse; existing image-owner tamper tests |
| Source/workdir/event/process guards | source_changed_during_probe_refuses_with_only_temporary_sources; mutation_during_probe_refuses; missing_duplicate_and_reordered_prerequisites_refuse; separate_session_fixture_dies_after_timeout_and_interruption |
| Exact negative controls | negative_controls_never_start_cli_for_invalid_inputs; direct_control_requires_exact_rejection_event |

Independent review classified seven finding instances, all fixed; none deferred.
The two reproduced guard regressions were observed red before fixes. Added coverage:

| Review instances | Executed regression |
| --- | --- |
| B1 | snapshot_replacement_during_read_refuses binds bytes/identity to one protected descriptor |
| B2 | transformer_cannot_change_other_arguments_or_mutate_original checks complete argument preservation |
| B3 / V1 | owner_plan_reaches_actual_synthetic_cli_with_retained_child_identity connects owner evidence through public qualification to the synthetic CLI process |
| B4 | ambiguous_create_is_rejected_before_selection now passes its event list to the boundary |
| B5 | invalid_mapping_shapes_refuse_before_cli covers duplicate/malformed/non-string digests |
| B6 | This evidence now records commands, exact outcomes and requirement traceability |

A mutation-sensitivity experiment substituted a well-shaped unrelated plan in both
owner checks. The integrated test failed at its independent retained-child equality,
with one expected assertion failure and no errors. The pure constructor documents its
internal owner-verified-plan precondition; structural validation alone is not provenance.
Final post-review commands above were repeated with fresh run
`a87297ea-1730-47a0-8a4e-d56214041118`. Preparation, tool and image qualification passed.
The pinned CLI positive proof again returned the same exact child reference and nine
events; all four negative controls returned the table's exact codes. Final focused
startup suite: **36 tests in 12.826s**. Final affected deployment suite: **278 tests in
59.769s**, no skips. Actual up again refused with docker_28_required.

All 13 retained image/tool/preparation files preserved their hashes, inodes, modes and
modification times; proof source bindings remained identical. Final image receipt SHA-256:
`2fda26a4f94bc442267dd27392330ad4af46463ee6c24a9b9a03108978fa5bfe`.
Protected ignored record `.local/immutable-create/final-a87297ea.json` has SHA-256
`9bfc7ce3865e158462e9f51c675049144de2239d83a35896a40cc5eea1c8ecec`.
Earlier evidence remains unchanged at `.local/immutable-create/initial-b46431a1.json`.
Compilation, scoped whitespace and documentation-link checks pass.

## Five impacts and remaining gates

- Scaffold: existing ENV image/startup owners only; P1/SERVICE retains generator,
  templates, schema, client and consuming-output proof. No new generator or proxy.
- Shared UI: no change.
- Agent context: existing root instructions suffice; actual commands belong in the runbook.
- Documentation: owner runbook/evidence, Build record and KDG navigation/memlog.
- ADR: existing isolation, release, dependency and sensitive-log decisions apply;
  no accepted decision changed.

Real Docker >=28, network/kernel isolation, execution-time enforcement, other service
and helper creates, full startup/bootstrap, layer/runtime and deployment PostgreSQL
compatibility, guarded lifecycle and P1/SERVICE remain open. Identity/Access/WRITE and
the KDG server slice remain downstream. No real container, pull, SQL, migration,
account/access, infrastructure, deployment, Leave domain or pilot action is performed.
