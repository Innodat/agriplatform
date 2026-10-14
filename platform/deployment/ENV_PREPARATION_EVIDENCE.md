# ENV preparation evidence — 2026-10-14

This records only the bounded preparation increment specified in
[the Build delivery spec](../../_bmad-output/implementation-artifacts/spec-env-kdg-target-preparation.md).
The enclosing ENV item remains unqualified for runtime/bootstrap acceptance.

Verification uses dependency-free subprocess acceptance tests in copied temporary
workspaces; no owner command, repository migration, credentials or real-data fixture
is used. The available bootstrap interpreter is **Python 3.12.3**, distinct from the
approved selected Python 3.15.0 runtime. No selected tool/package installation or
compatibility qualification is claimed.

Requirement authority is the existing ENV item's isolation criterion and the owning
[environment contract](../docs/architecture/contracts/scaffold-environment-and-generation.md)
sections “Explicit isolated environment input” and “Guarded environment command
contract.” Only their preparation boundary is covered here; the enclosing ENV
bootstrap/runtime acceptance remains open.

| Requirement / matrix row | Passing public CLI evidence |
| --- | --- |
| Synthetic target, protected deterministic inventory, readiness false; repeat stability | `test_prepare_repeat_binds_sources_and_stays_unqualified` |
| Changed target and source evidence refuse reuse | `test_changed_target_refuses_reuse`, `test_all_source_changes_refuse_reuse` |
| Closed input, missing/unknown/duplicate keys, bool-as-int, foreign owner/root/prefix, production origin, bad port, invalid UUID | `test_closed_input_adversaries_refused_before_run_write`, `test_duplicate_key_invalid_uuid_and_unknown_cli_safe` |
| Target/source/run ancestor symlinks and traversal; no outside writes | `test_symlink_target_source_and_run_ancestor_refused`, `test_target_traversal_and_source_ancestor_symlink_refused` |
| Foreign run, tampered/unprotected inventory, inventory symlink | `test_foreign_run_and_unexpected_inventory_files_refused`, `test_tampering_permissions_and_inventory_symlink_refused` |
| Concurrent same-run installation preserves one receipt | `test_concurrent_same_run_never_replaces_inventory` |
| Occupied approved port refuses before run creation | `test_occupied_port_refuses_before_run_write` |
| Runtime stages refuse before/after prepare; reset requires matching confirmation | `test_undelivered_commands_fail_without_mutation` |
| Bool/number inventory substitution refuses without repair | `test_inventory_boolean_number_substitution_refused` |
| Malformed schema returns safe refusal, no traceback or run | `test_malformed_schema_refuses_without_traceback_or_run` |
| Writable output ancestors refused; owner-controlled .local0755 supported | `test_writable_output_ancestors_refused_before_run_write` |
| Exact UUID-derived resource names and disjoint reservations for two runs | `test_reserved_resource_names_are_exact_and_disjoint_between_runs` |

Red observed before implementation:

```sh
python3 -m unittest discover -s platform/deployment/tests -p test_dev.py -v
```

Initial 8-test suite failed: the fresh/repeat subprocess acceptance could not open
`dev.py` because it did not exist. Guard tests also failed without the command/input
fixture. The first sandbox invocation separately exposed its socket prohibition;
subsequent port acceptance ran with approved escalation, without skips or mocks.

Green after implementation and expanded guards, same exact command: **12 tests passed**
(`Ran 12 tests in 1.903s`, `OK`). The initial implemented 8-test suite also passed
before the four added guard tests. These tests copy source/authority inputs to isolated
temporary directories, replace only the synthetic workspace root, invoke the actual
CLI, and assert safe outputs, protected files and unchanged unrelated evidence.

Enclosing Build verification after implementation handoff:

- `python3 -m unittest discover -s platform/deployment/tests -p 'test_*.py'` —
  **135 passed**, `Ran 135 tests in 15.450s`, `OK`, with approved local socket access,
  after review fixes. The pre-review regression was also green (131 tests).
- `python3 platform/deployment/dev.py prepare --target platform/deployment/environments/kdg-local.json --run-id 24ddde67-183d-48f2-b879-37da6ec36b4d`
  — exit 0 on initial and repeat execution; `stage=prepared`, `runtime_ready=false`.
  Ignored inventory observed at directory mode0700/file mode0600 with six source
  hashes and `identities_state=reserved_only`. No runtime resource was created.
- `python3 platform/deployment/dev.py verify --target platform/deployment/environments/kdg-local.json --run-id 24ddde67-183d-48f2-b879-37da6ec36b4d`
  — expected exit 2, `stage=verify`, `code=runtime_adapter_unqualified`.
- `git diff --check` — passed for tracked changes; final review also checks newly
  added files through the complete temporary unified diff.

Review regression red: the expanded 16-test focused command reproduced both
boolean/number inventory substitutions, an uncaught malformed-schema error and
acceptance of a writable output ancestor (3 assertion failures/1 error). After
fixes the same command passed **16 tests in 3.430s**. Port tests now cover IPv4
web5188 and an IPv6-only database55482 listener; lifecycle tests assert exact stage/
code and missing/mismatched/matching reset confirmation. Review also added exact
two-run resource-name proof and directory fsyncs after creation/lock removal.
All nine accepted findings across three independent reviewers were resolved in seven
patch groups; one fixture-validation claim was refuted because preparation hashes
opaque owner source without executing it. No defect was deferred.

Final source was separately prepared successfully with fresh run
`c0ba3257-bd18-430e-b705-23fbfba59632`; the earlier run remains evidence of the
pre-review source and is not silently upgraded. Both reserve names only.

Publisher availability checks on 2026-10-14 returned HTTP200 for the exact selected
[TypeScript7.0.2 metadata](https://registry.npmjs.org/typescript/7.0.2),
[Node26.11.1 checksums](https://nodejs.org/dist/v26.11.1/SHASUMS256.txt) and
[uv0.13.1 metadata](https://pypi.org/pypi/uv/0.13.1/json). This is availability evidence
only, not installation, full baseline refresh or runtime compatibility qualification.

Five impact decisions:

- **Scaffold:** ENV's existing deployment owner now owns the closed input schema,
  checked-in target/metadata fixture and guarded preparation CLI. No generator or
  candidate pattern is promoted; P1/SERVICE proof remains open.
- **Shared UI:** none; this is a CLI-only preparation receipt and implements no user
  form, saving pattern or runtime shell.
- **Agent context:** existing root rules suffice. Preparation commands and remaining
  gates are documented; no generated agent instructions exist yet.
- **Documentation:** `DEVELOPMENT.md`, this evidence file and builder navigation point
  to the implemented command while preserving explicit runtime/generation limitations.
- **ADR:** existing architecture decisions and the approved dependency/environment
  contracts govern this increment. No new decision or accepted ADR edit is needed.
