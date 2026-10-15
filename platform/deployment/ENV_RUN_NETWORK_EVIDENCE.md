# ENV run-owned network acquisition — 2026-10-15

The existing ENV owner has implemented acquisition and inspection of the disposable
run's network under the [environment contract](../docs/architecture/contracts/scaffold-environment-and-generation.md).
The [Build record](../../_bmad-output/implementation-artifacts/spec-env-run-network.md)
covers this bounded increment. Verification and independent review are complete; runtime
readiness remains false. No real Docker network is created by this delivery verification.

## Contract and source evidence

The [Docker API v1.48 reference](https://docs.docker.com/reference/api/engine/version/v1.48/)
defines network inspection and creation. The
[pinned Docker 28 router](https://github.com/moby/moby/blob/v28.0.0/api/server/router/network/network_routes.go)
rejects ambiguous names; full-ID lookup returns the identified network. Its create
route accepts typed network inputs. The
[network types](https://github.com/moby/moby/blob/v28.0.0/api/types/network/network.go)
include IPv4/IPv6, configuration-only and configuration-source fields beyond the
startup proof's selected descriptor. These need validation before projection. A bridge
with a valid name alone is insufficient ownership or isolation evidence.

The [network name error](https://github.com/moby/moby/blob/v28.0.0/libnetwork/error.go)
is classified as conflict, and the [HTTP error mapping](https://github.com/moby/moby/blob/v28.0.0/api/server/httpstatus/status.go)
returns 409. This supports the conflict-winner inspection path even though the API
reference's create response list does not enumerate 409.

The pinned Supabase CLI trusts existing network inspection and publishes PostgreSQL
without an explicit host IP; the prior [startup evidence](ENV_STARTUP_INVOCATION_EVIDENCE.md)
records that observation. ENV therefore owns the restricted bridge and publishing
option. Network metadata proof does not establish that the kernel enforces isolation.

## Verification

Initial acceptance was red because the network module was absent. That initial
availability-only assertion was replaced by behavioral tests. Separate focused red→green
cycles covered ConfigFrom omission and the public command's repository-relative target.
Existing 15 Docker gate characterization tests passed before and after extraction.

Before review, `python3 -m unittest discover -s platform/deployment/tests -p test_networks.py`
passes 20 tests in 13.194s, and `python3 -m unittest discover -s platform/deployment/tests
-p 'test_*.py'` passes 265 tests in 41.063s. No test is skipped.

Public command base from repository root:

```sh
python3 platform/deployment/dev.py prepare --target platform/deployment/environments/kdg-local.json --run-id 95708946-49ef-4981-ab3c-65017a97a624
python3 platform/deployment/tests/qualify_networks.py --target platform/deployment/environments/kdg-local.json --run-id 95708946-49ef-4981-ab3c-65017a97a624 --control positive
python3 platform/deployment/dev.py up --target platform/deployment/environments/kdg-local.json --run-id 95708946-49ef-4981-ab3c-65017a97a624
```

Preparation exits 0. The public proof was repeated with each control below; for
missing-preparation only, the run ID is unprepared 32829b7a-c151-419d-9fdf-3ed68c091af8.
Actual host up exits 2 with docker_28_required, preserving the blocked runtime boundary.

| Control | Exit / exact result |
| --- | --- |
| positive | 0 / network_synthetic_qualified; 7 API events |
| existing | 0 / network_synthetic_qualified; 5 API events, no POST |
| conflict | 0 / network_synthetic_qualified; 7 API events, verified winner |
| foreign, unsafe-options, ipv6, attached | 2 / network_not_run_owned |
| lost-response, malformed, oversized | 2 / docker_response_invalid |
| replacement | 2 / network_replaced |
| old-daemon | 2 / docker_28_required |
| slow | 2 / docker_timeout |
| daemon-error | 2 / network_inspection_failed |
| missing-preparation | 2 / prepared_run_required; no daemon access |

All 15 exact controls pass. Safe initial results are retained in protected ignored
`.local/network-qualification/initial-95708946.json`. Every result has runtime_ready=false.
The proof constructs an invocation using a synthetic, never-executed CLI path. It does
not execute Supabase or a container. Only the synthetic server sees network POSTs.

| Requirement | Executed test_networks.py coverage |
| --- | --- |
| Exact fresh create and verified ID handoff | prepared_absent_creates_exact_bridge_and_hands_id_to_startup |
| Existing reuse and closed descriptor | existing_reuses_without_post_and_descriptor_is_closed |
| Collision and uncertain create recovery | conflict_verifies_winning_network; create_response_and_conflict_winner_are_verified_without_retry; lost_create_response_never_retries_and_next_invocation_inspects_first |
| Foreign/unsafe/attached refusal | foreign_unsafe_and_attached_networks; all_actual_safety_fields_are_required_with_exact_types |
| Source/preparation/network identity changes | replacement_is_rejected; preparation_and_source_changes_during_daemon_exchange_refuse |
| Serialization and protected lock | concurrent_same_run_is_bounded_and_no_second_daemon_access; symlink_unprotected_and_replaced_lock_refuse |
| Bounded protocol and safe failures | malformed_oversized_slow_and_error_responses; one_operation_deadline; post_timeout_does_not_retry; arbitrary_routes_methods_and_requests |
| Public command, ambient isolation, missing preparation, old Docker | public_qualifier_success_and_negative_safe_codes; public_subprocess_accepts_repo_relative_target_and_ignores_ambient_daemon; no_public_endpoint_override; missing_preparation_and_changed_sources; old_docker_contacts_only_version |

Independent review fixed all nine reviewer instances and one root evidence correction;
none were deferred. Focused regressions observed failures before fixing the independent
request oracle, ordered observations, retained-ID/name replacement, changed lock
metadata, mismatched negative outcomes and invalid UUID handling. GET bodies now refuse
before socket access; a verified conflict winner reports created=false.

Final post-review commands above used fresh run
`e7af1eef-e0a9-49da-970c-d690ba3347f4`. All 15 controls returned the exact table outcomes;
positive/existing/conflict produced 7/5/7 events and created=true/false/false.
The focused suite passed **26 tests in 13.711s**; the affected deployment suite passed
**271 tests in 40.675s**, with no skips. Actual up again exited 2, docker_28_required.
All 11 source/preparation files retained their hashes, inodes, modes and modification
times across controls. Protected ignored final evidence is
`.local/network-qualification/final-e7af1eef.json`, SHA-256
`18f31487b61df837469cb4241356d88395a135cc2560494cde83589c2458308e`.

Additional requirement coverage in test_networks.py:

| Requirement | Regression |
| --- | --- |
| Independent create contract | wrong_production_flag_is_caught_by_independent_daemon_expectation |
| Complete ordered successful observations | event_validation_rejects_missing_duplicate_and_reordered_success_observations |
| Name continuity despite retained old ID | name_replacement_is_rejected_while_original_id_still_resolves |
| Held-lock protection through handoff | mid_operation_lock_state_changes_refuse_before_create_or_handoff |
| Reliable negative qualification | wrong_negative_code_reports_qualification_mismatch |
| Invalid run refusal before I/O | malformed_and_noncanonical_run_ids_refuse_before_input_or_daemon_access |


## Five impacts and remaining gates

- Scaffold: existing ENV acquires and verifies its network; P1/SERVICE retains recipe,
  generator, templates, clients and disposable output. No alternate generator.
- Shared UI: no change.
- Agent context: root rules suffice; actual commands and limits belong in the runbook.
- Documentation: owner evidence/runbook, Build record and KDG next-session navigation.
- ADR: existing ownership/isolation/release/logging decisions apply; none changed.

Real Docker>=28 and kernel isolation, digest enforcement at execution, complete
startup/helpers/bootstrap, deployed PostgreSQL compatibility, guarded lifecycle,
P1/SERVICE, Identity/Access/WRITE, provider/device and pilot evidence remain open.
Real dev.py up stays blocked; no live migration, account/access, provisioning,
deployment, Leave/KDG domain or real-data pilot action is part of this increment.
