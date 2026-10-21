# Access registry command input evidence

2026-10-21; bounded input-only increment under
[the approved spec](../../_bmad-output/implementation-artifacts/spec-access-a-registry-command-input.md).
Baseline: `f42d3f73a9b51cde0125898daaafc5bec7fc77c7`.
No database, native stack, target, resource, credential, registry row or effective access
was used or changed. Existing historical runtime/source/reference/receipt evidence stays
unchanged and makes no claim about these new parser bytes. ACCESS-A/B activation remains
closed. Final reviewed verification is recorded below; earlier pending checkpoints are historical.

## Requirement traceability

All test names below are in `tests/test_access_operator_input.py`.

| Requirement | Executed tests |
| --- | --- |
| Three distinct typed immutable commands/payloads, preserved uppercase UUID and fields, frozen platform scope and redacted repr | `test_registration_is_typed_frozen_preserved_and_redacted` |
| Closed root/scope/payload; missing/extra keys and ordinary/escaped duplicates at each level | `test_missing_extra_and_duplicate_fields` |
| Version, UUID grammar/nil, unknown command/scope, wrong types | `test_envelope_rejections` |
| Exact boolean expected absence on all commands | `test_expected_absence_is_exact_true` |
| ASCII app grammar including length2/64 vs1/65, case/Unicode/newline | `test_app_id_ascii_grammar` |
| Literal ASCII1–200 permission bytes; spaces, controls, DEL, punctuation; empty/201/nonASCII/NUL refusal | `test_permission_literal_ascii_boundaries` |
| Account/organization permission scope, no inferred prefix/association | `test_permission_scope_is_closed_without_inferred_association` |
| Five closed reasons; omitted evidence→None, explicit null/URL/oversize refusal, maximum opaque reference | `test_provenance_uses_identity_closed_semantics` |
| Bad UTF8/BOM, strict JSON, nonfinite/overflow, deep nesting, oversized integers, nonbytes; fixed safe exceptions without sentinel/context/cause | `test_decoder_and_nonbytes_fail_safely`; shared `reject` assertions apply to every invalid matrix case |
| NUL/lone surrogates in nested structures and keys | `test_forbidden_text_anywhere` |
| Exact65536/65537 UTF8 byte body bound | `test_exact_body_byte_boundary` |
| Identity parser, adapter, worker, CLI reject registry bodies before SQL/target/connection/dispatch; Access CLI owner remains unavailable | `test_identity_parser_adapter_cli_refuse_before_effects` |
| Existing Identity behavior | Unmodified Identity parser, adapter and CLI suites in the combined run below |

## Commands and results

Repository root working directory. Every pytest command used this exact prefix:

```sh
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python -I -B -m pytest -p no:cacheprovider
```

Retained logs: `platform/deployment/.local/access-registry-input-20261021/`.

1. Before creating the parser, append `services/access/tests/test_access_operator_input.py -q`:
   collection exit2, `ModuleNotFoundError: No module named 'access_operator_input'`;
   exact output in `acceptance-red.log`. Root independently observed module absence.
2. Before reuse, append `services/access/tests/test_identity_operator_input.py -q`:
   exit0, **127 passed**, in `identity-characterization.log`.
3. First implementation run used the acceptance-only suffix: **71 passed,3 failed**,
   retained in `focused-first.log`. Existing CLI `CODES` and `main` showed that the
   Identity route intentionally returns `identity_operator_input_invalid`, while
   argparse rejects `--owner access` as `command_invalid`. The new assertion was
   corrected to preserve these observed owner-specific codes; production CLI unchanged.
4. First combined run: **274 passed,3 failed**, retained in `focused-combined-first.log`.
   Existing Identity characterization imports its module by reloading `sys.modules`;
   parser/adapter references can therefore carry distinct same-named exception classes.
   The new refusal tests now assert each consumer's actual imported error class.
   This is test import isolation, with no changed Identity implementation or expectation.
5. Final combined command appended:

   ```sh
   services/access/tests/test_access_operator_input.py services/access/tests/test_identity_operator_input.py services/access/tests/test_identity_operator.py services/access/tests/test_operator_cli.py -q
   ```

   Exit0, **277 passed**, retained in `focused-green.log`.
6. `git diff --exit-code -- services/access/identity_operator_input.py services/access/identity_operator.py services/access/operator_cli.py services/access/tests/test_identity_operator_input.py`:
   exit0; reused Identity sources/tests unchanged from HEAD.
7. `git diff --check`: exit0, retained in `diff-check.log`.

Root will run the required affected regression
`services/access/tests apps/pts/tests/test_release.py platform/deployment/tests/test_migrate_adapter.py -q`
with the same interpreter/prefix, plus both composers (`--check-only` and
`--identity-authority owned --no-seeds --check-only`), after independent review.
These checks are not claimed complete at this checkpoint. There is no root repository-wide
test/lint/typecheck command; the evidence is limited to the listed Python suites.

## Source evidence

Exact SHA256 values also retained in `source-hashes.sha256` in the log directory:

```text
67d9fad581e14884092a40d9ae388bf77bc3b5337cad3325e8dbb7bfcc7e50f9  services/access/access_operator_input.py
452c8c5cfa13afb76265f0e04a1b8074f168420aab1861e9093ddc2956df31e5  services/access/tests/test_access_operator_input.py
2e1cfca4cf4d291c60d156aff84515a21593789bdc37ffcddcdd0ad2a3a2f71d  services/access/identity_operator_input.py
72fc62dc298608ec09ad42c939b3f30a9007cad559a9271bf146d06da0e21091  services/access/identity_operator.py
cf01dda96bbe0d5e2c57ce280065aa7a7ea4b480ef49ec066f6fceb8f0329f93  services/access/operator_cli.py
9e802e750365146ec3554a95603e4d4c506723b8d5f1410420920337c6b6b689  services/access/tests/test_identity_operator_input.py
16e5f16ac29a63c982a487f04ddfaa6aab77a1f8555a3ed023486de14e9baec1  platform/docs/architecture/contracts/identity-access-execution-substrate.md
12d8affc9f791d592816e9a5eb1d0e4708ed3244ea35e0fe95100932bfd36a06  platform/docs/architecture/contracts/e1-controlled-provisioning-and-evidence.md
d19a423228084c9bd5dca84ee3d68c298b92bc77f11674713dac3db4731ebacf  apps/kdg-capture/docs/next-session.md
```

## Five impacts and remaining boundaries

- Scaffold: owner-local pure parser and its closed-envelope/refusal fixtures are reusable
  here. Reuse existing Identity primitives; no shared package, parser framework, generated
  scaffold or generator schema is introduced.
- Shared UI: no UI impact.
- Agent context: current ownership/release/ATDD instructions suffice; no context changes.
- Documentation: this evidence, mutable substrate delivery note and prepended KDG checkpoint
  record actual input-only delivery; historical text remains intact.
- ADR: existing accepted decisions apply; no ADR change.

Protected Access execution, authority, SQL, fingerprints, receipts, routing and effective
authorization remain outside this increment. Parsed records alone assert no association
or authority. No commit, deploy, production/pilot action or push was performed.

## Reviewed test qualification —2026-10-21

The original logs and `source-hashes.sha256` remain historical and unchanged. The
original test hash above identifies the first focused277-test frame, before the review
changes below; it is not the current test source hash. Production parser bytes remain
unchanged.

| Review requirement | Reviewed test evidence |
| --- | --- |
| Independently establish recursive forbidden-text decoding | `test_reused_decoder_checks_nested_keys_lists_and_values` directly invokes the exact `_decode` imported by Access. Ordinary `json.loads` accepts each negative fixture; the reused decoder refuses NUL and both lone-surrogate boundaries in nested keys, list elements and object values. Matching nested positive controls preserve controls, DEL, nonASCII and supplementary Unicode without envelope/payload validation. |
| Preserve every permitted ASCII codepoint | `test_permission_literal_ascii_boundaries` round-trips the complete0x01–0x7f sequence byte-for-byte for both permission commands, retaining length and invalid-boundary cases. |
| Full safe owner refusal assertions | `test_identity_parser_adapter_cli_refuse_before_effects` first proves sentinel-bearing opaque evidence is valid Access input, then asserts exact Identity error message/code/args, absent context/cause and no submitted sentinel/provenance/identifiers in exception rendering for parser, adapter and worker. CLI responses are exact owner-specific code objects without submitted content or stderr. Existing target/connection/dispatch traps remain. |

Only the edited test suite was rerun for this review:

```sh
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python -I -B -m pytest -p no:cacheprovider services/access/tests/test_access_operator_input.py -q
```

Exit0, **77 passed**; retained separately as
`platform/deployment/.local/access-registry-input-20261021/reviewed-focused-green.log`.
Fresh test source hash, separately retained as `reviewed-test-hashes.sha256`:

```text
9761ef5ca7fa427e91d280197f48855f1e3da7bdde522cca6b15bed4409adaaf  services/access/tests/test_access_operator_input.py
```

`git diff --check` passed, with separate `reviewed-diff-check.log`. Root broad regression,
both composers and final review/commit remain pending; this qualification does not claim
their completion or any runtime/activation proof.


## Final root verification —2026-10-21

Three independent review lenses completed. Blind review supplied six suggestions:
three test-only improvements were applied; two decoder coverage claims were refuted by
executed direct shared-decoder/Unicode byte-bound tests, and the pending-checkpoint
suggestion was already an explicit finalization task. Edge and verification-gap reviews
returned no findings. Individual verdicts/evidence are in the Build spec; no deferrals.
Production parser bytes did not change during review.

Root reran the complete affected suites after these patches, using the canonical
interpreter and pytest prefix above with this exact suffix:

```sh
services/access/tests apps/pts/tests/test_release.py platform/deployment/tests/test_migrate_adapter.py -q -p no:cacheprovider
```

Exit0, **1152 passed in47.06s**, no skips; `root-affected.log` retains the output.
The reviewed77-test parser suite was included. Root then ran, sequentially:

```sh
platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python -B tools/py/run_compose_supabase.py --check-only
platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python -B tools/py/run_compose_supabase.py --identity-authority owned --no-seeds --check-only
```

Both exit0; `root-compose-legacy.log` and `root-compose-owned.log` retain output.
Final whitespace/preservation checks pass: all41 protected historical files and all13
preexisting concurrent tracked changes match their starting hashes; the frozen intent
matches its recorded hash. Original handoff text is retained byte-for-byte after the new
checkpoint. Unchanged Identity parser/adapter/CLI hashes match the initial focused frame.

`final-source-hashes.sha256` records final input/test, reused owner and delivery-document
sources; `final-log-hashes.sha256` records all retained logs, including initial failures.
Original manifests and logs remain unchanged. These are parser/affected-test results,
not current native database, production or portable CI bootstrap qualification. Native
resources/receipts were not touched. Existing deferred runtime/bootstrap/timing work and
ACCESS-A/B activation remain separate. Next is protected Access registration execution
with current owner authority, atomic outcomes/audit and later exact consumer checks.
