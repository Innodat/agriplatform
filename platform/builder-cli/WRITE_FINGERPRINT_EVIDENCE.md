# Copyable WRITE fingerprint candidate

This delivery adds an owner-copied example for normalized command fingerprinting, using
pinned RFC8785/JCS and HMAC-SHA-256. It is a prerequisite candidate, not a shared runtime,
registered proven pattern or complete WRITE/KDG implementation. Domain validation and
raw JSON/duplicate-key handling stay with the consumer. No database, actual secret-file
lifecycle, HTTP endpoint or release readiness is claimed.

Baseline: `1f7edfe61e314d76fa1f4a4e0a0c6ba768adffcc`. BMAD-help selected Build for the
next lean WRITE prerequisite after the KDG organization reader. The approved standing
scope covers implementation and synthetic offline proof; concurrent work is preserved.
The governing contract is `platform/docs/architecture/contracts/owned-write-and-secret-execution.md`;
KDG retains its canonical envelope and business meaning in its own contracts.

Root acceptance RED preceded production edits: actual import of the expected example
failed because the file was absent (`/tmp/kdg-write-fingerprint-red.log`, exit1).
The implementation agent then observed its focused missing-module test failure before
writing the helper. The same root acceptance script now succeeds with an identical
KDG-shaped retry (`acceptance-green.log`, exit0).

## Verification

Proof directory D: `platform/builder-cli/.local/write-fingerprint-20261022`.
P: absolute `platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python`.
N: absolute `platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node`.
The existing frozen approved environment supplies CPython3.15.0, pytest9.1.1 and
rfc8785==0.1.4; Node26.11.1 is explicit. No new lock or dependency baseline is introduced.

- `FINGERPRINT_TEST_NODE=N P -I -B -m pytest platform/builder-cli/tests/test_command_fingerprint.py -q -p no:cacheprovider`: **50 passed**, `D/focused.log`.
- `P -I -B /tmp/kdg-write-fingerprint-red.py`: **exit0**, `D/acceptance-green.log`.
- `timeout 60s N --test platform/builder-cli/tests/*.test.mjs`: **62 passed / exit0**,
  `D/builder-regression-bounded.log` (9.72 seconds). The initial sandbox subprocess runner stalled
  with no output and was explicitly interrupted (exit130); the bounded run uses the
  authorized local process environment. Its empty original log remains retained.

| Requirement | Passing focused evidence |
| --- | --- |
| Stable JCS/HMAC and preserved Unicode/array meaning | test_independent_jcs_and_hmac_vectors; explicit canonical byte vectors and stdlib HMAC expectations |
| Full command/account/org/version/payload binding; constant-time comparison | test_reordered_command_and_every_changed_meaning; valid alternate UUIDs, command/version and reordered/changed answers; compare_digest observation |
| Original key after rotation and reconstructed metadata | test_rotation_reconstructed_process_and_wrong_retained_key; both old/new entries, no old digest rewrite |
| Missing/bad retained key and unsupported metadata fail closed | test_malformed_stored_metadata_refuses_without_mutation; test_missing_or_bad_recorded_key_never_falls_back; bad creation material cases |
| Safe JSON and redacted immutable internal metadata | test_invalid_json_is_bounded_and_redacted; test_cyclic_and_excessively_deep_inputs_fail_safely; immutable/repr checks |
| Existing scaffold copy/provenance and owner preservation | test_existing_installer_copies_executes_and_preserves_owner_bytes; actual Node installer/check, copied execution/rotation/refusal, source removed before replay |

Reconstruction tests reload the module and rebuild stored metadata. They do not claim
an independent OS-process secret-file restore. Actual key loading/namespace/permissions,
rotation/release backup and data-plus-secret restore remain consuming/environment work.
No key/payload/digest is emitted by the helper; its internal metadata is never an API
DTO. No Access/Identity regression or database composition is needed because their
source and all database/environment tooling remain unchanged.

## Impact decisions

Scaffold: copyable example plus actual existing-installer import proof; templates,
recipe schemas, pattern registry and generator behavior stay unchanged. Shared UI:
unchanged. Agent context: existing ownership/safe diagnostic rules suffice; no edits.
Documentation: example README, this evidence and current KDG handoff. ADRs: existing
accepted decisions suffice; none edited. No generic crypto framework/service, alternate
generator, key provisioning, database startup/migration, Leave/editor or deployment.

## Reviewed closure

All three independent review lenses completed. Edge-case and verification-gap lenses
returned no findings. The blind lens supplied six individually recorded triage rows.
Direct corrections add a ten-second installer subprocess timeout, bounded allowlisted
process/import/scaffold diagnostics, RFC escaping/rounding vectors, exact-type/root
rejection and formatted-traceback canary tests. The helper itself remains unchanged.
Its owner must bound the normalized document, including any programmatic expansion;
this candidate is not a traversal/output budget guard. No new deferred work is created.

Final root focused command above: **63 passed**, 0.36 seconds, no skips;
`D/focused-reviewed.log`. Final root acceptance executes the retained `D/acceptance.py`
and passes (`D/acceptance-green-reviewed.log`, exit0). The exact original RED output is
retained as `D/acceptance-red.log`. The committed equivalent is
`tests/test_command_fingerprint.py::test_reordered_command_and_every_changed_meaning`
with its missing-source loader fixture and positive identical-command verification.
The original tmp paths are historical invocation records, not the only retained source.

Additional verification maps to `test_non_object_roots_are_rejected`,
`test_custom_containers_and_numeric_subclasses_are_rejected`,
`test_canonicalizer_exception_traceback_is_sanitized`, and
`test_installer_failures_are_bounded_and_classified`. Literal escaping/number cases
follow [RFC8785 sections3.2.2–3.2.2.2](https://www.rfc-editor.org/rfc/rfc8785.html#section-3.2.2).
The 62-test Node regression remains applicable: all builder implementation and existing
Node test bytes are unchanged by the review fixes; the revised Python acceptance also
executes the real existing installer and its preservation replay. No broader owner or
database suites are claimed or needed.

Final source audit passes: 308 bound source/lock files and nine retained proof inputs/
logs. Of 304 pre-existing builder/Access files, 303 are byte-identical; only the intended
example README changes. All Access/Identity history, runtime sources, builder templates,
installer, recipe schemas, pattern registry and approved dependency locks are preserved.
The frozen approved intent is unchanged. `D/audit.json` hashes every source and proof
input/log, including the retained acceptance source and original RED witness.


Audit SHA-256: `90893a02df7dc792b74fa16e046854322ad95a69efe0f8bb7984b53e0db11270`.

The local scope-only commit includes this example/tests/documentation and current KDG
handoff. Concurrent Leave/PtS/Scribeswell work is excluded and preserved. No Docker or
database lifecycle was invoked, no resources were removed, and nothing was pushed.
The five impact decisions above remain binding. Next select the bounded owner-local
write/context/outcome proof from the existing WRITE contract before business API work;
key-file lifecycle and real release/data recovery still require their own evidence.
