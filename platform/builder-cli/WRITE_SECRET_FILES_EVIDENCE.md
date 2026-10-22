# Copyable KDG fingerprint secret-file candidate

Reviewed bounded candidate complete, 2026-10-22. BMAD-help selects Build for the next approved bounded WRITE
prerequisite after atomic outcome candidate8f14364. Baseline:
`8f14364a6549f36e775873131d34dee3c3f3adc0`. The owning contracts are
`platform/docs/architecture/contracts/owned-write-and-secret-execution.md` and its
KDG disposition link. This candidate supplies protected file loading only; production
mounts/host ownership, independently encrypted archive, matching data restore and
KDG business/release activation remain gates.

## Environment and acceptance ordering

D: `platform/builder-cli/.local/write-secret-files-20261022`.
P: absolute `platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python`.
N: absolute `platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node`.

Root `P -I -B D/acceptance.py` failed with ModuleNotFoundError before any production
loader source existed. Original source/output remain D/acceptance.py and
D/acceptance-red.log. Focused behavioral acceptance follows that initial witness.
The unchanged fingerprint baseline passed63 tests (D/fingerprint-baseline.log).

Real local kernel identity is supplied by
`unshare --user --map-user=10001 --map-group=10001 P -I -B ...`.
D/namespace.json records CPython3.15.0, UID/eUID/GID/eGID10001 and both actual maps
`10001 1002 1`. Host-owned1002 files appear owned10001 inside this namespace.
This changes no host accounts or ownership and uses no Docker resources. It proves
mapped local/CI filesystem behavior, not native host chown10001, container mount
isolation or a production read-only secret projection. sudo was unavailable; no sudo
privilege or host permission weakening is used.

Synthetic random key files belong only in ignored run-specific ENV proof directories,
with protected directory0700/files0400. No real key, provider, grant, account, application
activation or resource cleanup is authorized or performed. Historical evidence and
concurrent Leave/Scribeswell work remain preserved.

## Impact decisions

Scaffold: one owner-copied candidate and actual installer copy/replay proof, with
existing fingerprint sibling reused; no template/catalogue/public generation change.
Shared UI: unchanged. Agent context: existing safe logging/ownership rules suffice.
Documentation: example README, this evidence, Build spec and current KDG handoff.
ADRs: existing accepted decisions unchanged. Dependency baseline including
TypeScript7.0.2 remains unchanged. No shared keyring/runtime or backup service.

## Verification

- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 SECRET_TEST_RUN_ROOT=<absolute ENV/root-candidate> FINGERPRINT_TEST_NODE=N unshare --user --map-user=10001 --map-group=10001 P -I -B -m pytest platform/builder-cli/tests/test_fingerprint_secret_files.py platform/builder-cli/tests/test_command_fingerprint.py -q -p no:cacheprovider`:116 passed1.72s, D/root-candidate.log;53 candidate cases plus63 fingerprint cases. The final added descriptor-replacement test has separate agent verification below.
- Same namespace focused secret-file suite with explicit ENV/agent-final root:54 passed, D/focused-final.log. Initial51-case proof remains D/focused-first.log.
- `timeout 60s N --test platform/builder-cli/tests/*.test.mjs`:62 passed14.31s, D/builder-regression.log.
- Original `P -I -B D/acceptance.py` now exits0, D/acceptance-green.log, with no change to its original RED source.

Focused behavioral TDD: D/config-red.log records two actual failing cases for newline
and surrogate configuration paths (13 passed/38 deselected). Strict path validation
corrected them; D/focused-green.log records53 passing checks. Final54-case proof adds
a real-device descriptor check and filename replacement detection. Historical logs
are retained separately rather than rewritten.

| Requirement | Executed focused evidence |
| --- | --- |
| Actual runtime/leaf/file UID/GID and exact permissions | test_protected_active_material_executes_existing_helper; test_exact_modes_are_required; test_wrong_identity_and_actual_unmapped_owner |
| Explicit validated public configuration and namespace | test_configuration_is_explicit_closed_and_bounded; test_schema_namespace_and_material_refuse_without_repair |
| Strict bounded JSON/UTF8/duplicates and canonical32-byte Base64 | test_invalid_document_is_bounded_and_exception_chain_has_no_content; test_noncanonical_base64_padding_bits_are_rejected |
| No symlinks/ancestor aliases/FIFO/device/blocking or implicit scans | test_nonregular_files_never_block_or_follow; test_symlink_directory_components_are_rejected; test_missing_invalid_ids_and_no_directory_scan |
| Recorded original key, restart/rotation/old-active configuration overlap, wrong/missing key refusal and retained receipt preservation | test_separate_process_restart_rotation_old_active_configuration_overlap_and_missing_key |
| Exact scaffold bytes/import provenance, copied process execution and preservation | test_real_installer_copies_siblings_and_preserves_edits_and_provenance |

The helper validates existing requested files only. The subprocess fixture uses private
persisted fingerprint metadata as a surrogate outcome; it is not a database/data-backup
restore, application authority check or business API. Safe children emit only a fixed
success/refusal identifier. Runtime-ID negative cases use fault injection; kernel-positive
proof and unmapped /etc descriptors independently exercise actual numeric ownership.
Device proof redirects to a real /dev/null descriptor without substituting fstat.
No file/key cache, startup generation, permission repair or fallback is introduced.
Final reviewed verification and custody follow below.


## Review closure

All three independent Build lenses completed. Edge-case review returned no findings;
each blind and verification finding has its own verdict in the Build spec. Direct
corrections strengthen diagnostics and evidence without changing the production loader.
Preservation and child-output failures use fixed safe identifiers, including child
start/timeout errors. An intentionally failing six-case nested pytest run proves
rendered failure reports exclude secret/digest canaries; its sanitized log is retained.
Wrong-UID and wrong-GID cases now independently retain correct object kind/mode.
Available old-key verification succeeds despite absent or malformed active material,
while active readiness refuses and original files/outcomes remain unchanged.

Read-mutation cases cover filename replacement, in-place valid-key rewrite/truncation,
exact4096-byte acceptance and actual growth after initial stat with4097 bytes maximum
read. Same-code subprocesses prove restart and old/new active-configuration overlap,
not compatibility between different release implementations. Actual version-overlap,
production ownership/mount and matching encrypted data/secret restore remain gates.
No new deferral is introduced. Final source-bound results and custody follow below.


## Final verification and custody

Authoritative local specimen run:
`platform/deployment/.local/write-secret-files-20261022/root-reviewed-final`.

- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 SECRET_TEST_RUN_ROOT=<absolute authoritative run> FINGERPRINT_TEST_NODE=N unshare --user --map-user=10001 --map-group=10001 P -I -B -m pytest platform/builder-cli/tests/test_fingerprint_secret_files.py platform/builder-cli/tests/test_command_fingerprint.py -q -p no:cacheprovider`: **128 passed**,1.49s, D/final-combined.log;65 secret-file cases plus63 unchanged fingerprint cases, no skips.
- Existing builder regression: **62 passed**, D/builder-regression.log. Installer/Node test sources remain unchanged; the final namespace matrix executes actual copy/replay again.
- `unshare --user --map-user=10001 --map-group=10001 P -I -B D/verify_retained.py`: **exit0**, D/retained-inspection.log and retained-inspection.json. Independent read-only inspection checks65 retained cases/maps,18 valid protected old-key specimens and3 original-key retry recoveries. These counts describe synthetic specimens, not application-data recovery.
- `P -I -B D/audit.py`: **passed**. D/final-audit.json binds six executed source files,21 proof inputs/logs and818 retained fixture files across historical/current runs. All six source hashes match the pre-final-test snapshot.17 logs were scanned against191 synthetic key documents and27 retained-outcome digests; none contained their key encodings/representations or digest strings.

The mutation test was strengthened again after review: in-place rewrite now changes
only key_b64 to another canonical same-length32-byte key, retaining valid schema and
namespace. A fresh completed-file read succeeds, while the racing chunked read must
refuse. This prevents malformed JSON from masking the metadata protection. Its two
targeted cases pass before the final combined run. Additional review-specific cases:
`test_isolated_wrong_owner_metadata_refuses` (four UID/GID variants),
`test_recorded_key_verifies_independently_of_unavailable_active` (missing/malformed),
`test_exact_document_boundary_succeeds`, `test_read_time_growth_is_bounded` and
`test_deliberate_pytest_failures_exclude_child_output_and_material_canaries`.
The latter retains a sanitized report of six intentionally failing child cases while
the outer verification passes. Current helper source was unchanged throughout review.

Of2907 pre-existing tracked/untracked sources,2888 remain byte-identical. Nineteen
changed files comprise the two intended README/current-handoff changes plus17 ongoing
external Leave/Scribeswell planning/release edits, observed and left intact. All37
pre-existing dependency lock/manifest inputs remain unchanged, including TypeScript7.0.2.
All eight prior atomic execution sources and28 historical proof inputs/logs independently
match the earlier audit; Access/Identity, existing builder templates/installer/catalogue
and historic receipts remain preserved. The complete original KDG handoff remains an
unchanged tail below the new current section. Private ENV and builder proof roots are
ignored; their data is retained. No Docker/database lifecycle, host/account ownership
change, real access, provisioning, deployment, pilot, cleanup or push was performed.

Audit SHA256: `3622e299a27a5f33a61f2622339efc54bd2ab9a17fbddd04efdc527f3d9465d4`.
The audit covers execution/proof/fixtures, excluding its own digest-bearing narrative.
Final scoped whitespace checks pass. A scope-only local Build commit records the
loader/tests/guide/evidence/current handoff/spec; concurrent work stays excluded.
Next select matching separately protected encrypted secret/data recovery and release
preflight proof through existing owners, with actual archive/backend/authority inputs
identified before claiming that gate. This is not production mount or first KDG API
readiness; consumers still own DTOs/current authorization and release acceptance.
