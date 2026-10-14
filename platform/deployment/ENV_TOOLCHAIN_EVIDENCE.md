# ENV toolchain qualification — 2026-10-14

This is the second bounded increment of the existing ENV item, after guarded target
preparation. Requirement authority is the
[environment contract's dependency authority/qualification section](../docs/architecture/contracts/scaffold-environment-and-generation.md)
and the [approved exact baseline](../docs/architecture/contracts/scaffold-dependency-baseline-2026-10-14.md).
The [Build record](../../_bmad-output/implementation-artifacts/spec-env-kdg-toolchain-qualification.md)
tracks implementation/review; no product specification or delivery workflow is replaced.

## Exact qualified scope

| Tool | Selected exact version | Actual check |
| --- | --- | --- |
| Node | 26.11.1 | Selected executable reports v26.11.1 |
| npm | 12.2.0 | Separate pinned npm package reports12.2.0 under selected Node; bundled11.20.0 unused |
| TypeScript | 7.0.2 | Selected tsc/native compiler reports Version7.0.2; valid code succeeds; invalid code returns exit1 with TS2322 |
| CPython | 3.15.0 | Ordinary GIL, Linux x86_64, ssl/sqlite3/ctypes/zlib/bz2/lzma/venv/ensurepip imports pass |
| uv | 0.13.1 | Publisher GNU binary reports uv0.13.1 and its expected platform suffix |
| Supabase CLI | 2.120.0 | Selected publisher binary reports2.120.0 using private SUPABASE_HOME |

These are actual tool executions, including a run under the normal filesystem sandbox.
They do not qualify React/Vite/FastAPI/native owner dependencies, frontend/root or
Python owner lock graphs, generated output, database/container images or actual Auth.
The bootstrap interpreter remains Python3.12.3; it installs/runs the selected Python
without changing workstation tools. Tool cache locations do not create app/frontend locks.

The [pin document](toolchain-pins.json) owns seven archive URLs, layouts and integrity
values. All were fetched and verified before execution. Primary sources:
[Node checksums](https://nodejs.org/dist/v26.11.1/SHASUMS256.txt),
[Supabase release assets](https://api.github.com/repos/supabase/cli/releases/tags/v2.120.0),
[uv wheel metadata](https://pypi.org/pypi/uv/0.13.1/json),
[npm12 metadata](https://registry.npmjs.org/npm/12.2.0),
[TypeScript metadata](https://registry.npmjs.org/typescript/7.0.2),
[native compiler metadata](https://registry.npmjs.org/@typescript/typescript-linux-x64/7.0.2),
and [uv0.13.1's CPython catalogue](https://raw.githubusercontent.com/astral-sh/uv/0.13.1/crates/uv-python-managed/download-metadata.json).
CPython's ordinary build is20261013, variant null, target linux-x86_64-gnu.

## Requirement-to-test traceability

| Requirement / adversary | Executed verification |
| --- | --- |
| No implicit prepare/default target; safe argument errors | test_public_missing_preparation_refuses_without_tool_writes; test_public_invalid_uuid_unknown_argument_and_symlink_target |
| Changed prepared source refuses before tool writes | test_prepared_source_change_refuses_before_tool_writes |
| Archive traversal, unsafe link parents, private nested directories | test_archive_escape_and_link_parent_refuse_before_extraction; test_archive_nested_parents_private_and_payload_link_escape_refused |
| Publisher integrity and malformed/unknown pins | test_digest_mismatch_and_symlink_archive_never_extract; test_unknown_malformed_pins_fail_closed |
| Fingerprint includes legitimate links and content changes | test_payload_safe_symlink_recorded_and_tampering_detectable |
| Repeat preserves receipt; altered types/checks/binding refuse before execution | test_unit_repeat_preserves_receipt_and_rejects_receipt_tampering_before_execution |
| Changed payload refuses without overwriting receipt | test_unit_changed_payload_refuses_before_execution_and_keeps_receipt |
| Partial install and concurrent lock never adopted/repaired | test_public_partial_install_and_concurrent_lock_refused_without_repair |
| Mutable state cannot overwrite outside through links | test_state_symlink_and_hardlink_cannot_overwrite_outside_file |
| Pin byte snapshot remains current | test_pin_snapshot_changed_after_decode_refuses |
| Receipt cannot change during execution | test_unit_receipt_changed_during_execution_refuses |
| Planned link graph remains inside payload | test_planned_link_graph_escape_refused |
| Replaced output ancestor cannot redirect writes | test_ancestor_replacement_cannot_redirect_installation_writes |
| Corrupt cache refuses before extraction/receipt | test_corrupt_cached_archive_refuses_before_extraction_or_receipt |
| Concurrent cache publication is complete | test_concurrent_cache_publication_verifies_one_complete_archive |
| Downloads and archive indexing stay bounded | test_progressing_download_has_total_deadline; test_archive_limits_checked_before_eager_indexing |
| Truncated transport emits safe refusal | test_truncated_download_is_safe_json_refusal |
| Wrong version, exit or compiler diagnostic refuses | test_execute_rejects_wrong_version_exit_and_diagnostic |
| Native grandchild retains access to pinned directory | test_pinned_directory_path_survives_grandchild_descriptor_closure |
| Six real versions, GIL/stdlib and valid/invalid compiler behavior | Actual public qualification and repeat, recorded below |

Unit receipt-sequencing fixtures replace extraction/execution with tiny synthetic
payloads; they prove guard ordering, not tool versions. Real qualification uses actual
publisher binaries without those replacements. No public bypass option exists.

## Red/green chronology

An initial unverified implementation draft was written before the public acceptance
test. It was moved out of the workspace to preserve it and restore the missing-feature
baseline. The one-test public acceptance then failed because toolchain.py did not exist
(expected exit0, actual2; unittest exit1). Focused tests also failed on missing import.
Only after those failures was the implementation restored/re-derived. This chronology
is recorded explicitly rather than claiming the first draft was test-first.

The initial seven focused guards passed after implementation. Expanded guard tests
cover receipt types/ordering, interruption, link safety and repeat immutability.
Real execution first failed because npm12 rejects the same /dev/null config path for
both user/global configuration. Distinct empty private files fixed it. The compiler's
verified exit1/TS2322 behavior replaced the draft's unexplained legacy exit2 assumption.
All six actual tools and probes then passed under the normal filesystem sandbox.

Pre-review public command and repeat both succeeded:

```sh
python3 platform/deployment/toolchain.py qualify --target platform/deployment/environments/kdg-local.json --run-id 67110d88-5625-49ef-9ba4-3fe4fa2b7fb5
```

Both exit0 with toolchain_ready=true and runtime_ready=false. The mode0600 receipt is
1958bytes, fingerprints13655 installed entries, and remains unchanged after repeat:
SHA256 `644d80f5e20d8bb40ca07be4b4cef144aa8c32a5710ac973efa3119ddf564590`.
`python3 -m unittest discover -s platform/deployment/tests -p test_toolchain.py -v`
passed12 tests in1.425s; full owner command
`python3 -m unittest discover -s platform/deployment/tests -p 'test_*.py'`
passed147 tests in33.865s with local socket permission. Review/final results follow.

Failed diagnostic run51478f59-9960-4e55-8d6f-68aab5f88adf remains ignored
partial evidence; it is not repaired or represented as qualified.

## Review fixes and final verification

All twelve review findings were accepted and resolved; none were deferred. Regression
coverage now includes pin snapshot consistency, receipt mutation during execution,
planned symlink graph escapes, output ancestor replacement, corrupt cached archives,
concurrent cache publication, incremental archive limits, total download deadlines,
truncated transport refusal and negative executable/compiler results. TypeScript uses
an explicit empty typeRoots directory to exclude ambient repository declarations.

The first descriptor-anchored real run (986b42bd-4d88-40db-8a9f-6f15d65d85d0)
refused at the valid compiler fixture: its native grandchild closes inherited file
descriptors. Referring to the still-running owner's `/proc/<pid>/fd` paths fixed this;
a child/grandchild regression proves the path remains usable after descriptor closure.
The failed run remains partial evidence and was not repaired.

Final public qualification and repeat use prepared run
`afd91508-2c2d-448e-a4f0-eed79e3c9a68` with the command above and that run ID.
Both return exit0, toolchain_ready=true and runtime_ready=false. The protected receipt
SHA256 is `7eb397f18739e2853199591fc54f19f43c121e6a85e781aa6de337fb97407091`.
The receipt remains mode0600, 1958bytes and fingerprints13655 payload entries after
repeat. The focused command passed23 tests in4.471s. The final full owner command
`python3 -m unittest discover -s platform/deployment/tests -p 'test_*.py'`
passed158 tests in36.861s with isolated local socket permission. Scoped whitespace and
relative documentation-link checks pass. No review finding remains deferred.

## Runtime gate and impacts

The actual local Docker daemon was27.0.3. The owning runtime must require>=28 before
publishing this loopback-only stack, per
[Docker's documented pre28 L2 limitation](https://docs.docker.com/engine/network/port-publishing/).
No daemon upgrade, infrastructure, container startup, migration, account/grant,
Identity/Access/WRITE, Leave, KDG editor or pilot action occurred. Runtime adapters,
publisher image/DB qualification, synthetic roles/fixtures, generator, full owner locks,
Entra and installed-device proof remain open. toolchain_ready never implies runtime_ready.

- **Scaffold:** existing ENV owner supplies fixed tools/pins/cache/qualification command;
  P1/SERVICE can consume proven tooling later. No generator or candidate pattern promoted.
- **Shared UI:** none; no application shell, domain screen or saving behavior changed.
- **Agent context:** root rules suffice; actual commands and limitations live in the
  owner runbook and KDG handoff. No generated instructions exist yet.
- **Documentation:** this evidence, DEVELOPMENT and current KDG navigation retain the
  distinction between installed tools and undelivered runtime/application prerequisites.
- **ADR:** existing accepted ownership/release/scaffold decisions apply unchanged;
  no new ADR or edit to an accepted decision is needed.
