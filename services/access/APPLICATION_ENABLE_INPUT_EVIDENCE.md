# Application enablement command input evidence

2026-10-21; [approved input-only spec](../../_bmad-output/implementation-artifacts/spec-access-a-application-enable-input.md).
Baseline `0da77323b948903b4a479c6486c6b919bf9d0fc2`. No database, target, native
stack, credential, configuration, grant, consumer or runtime resource changed.
Historical runtime evidence is preserved and remains bound to its original source.

## Requirement traceability

New tests are in `tests/test_application_enable_input.py`; the existing registration
suite remains unchanged, including its separate expected-absence assertions.

| Requirement | Executed test |
| --- | --- |
| True/false, revision1/max, app length2/64; distinct typed frozen redacted records, platform scope and accepted UUID spelling | `test_enablement_is_typed_frozen_redacted_and_preserved` |
| Strict bool; canonical positive bigint strings, no numeric/bool/zero/sign/space/leading-zero/Unicode/overflow/oversize revision; app ASCII grammar | `test_payload_rejects_without_coercion` |
| Missing/extra fields and ordinary/escaped duplicates at root/scope/payload; no actor, permission, owner or expected-absence override | `test_closed_fields_and_plain_or_escaped_duplicates` |
| Closed reasons/evidence, omitted→None and null refusal; UUID/version/command/scope; strict UTF8/JSON/nonbytes/nonfinite/deep nesting/large integers; NUL/surrogates recursively; exact65536/65537 boundary | `test_shared_strict_envelope_provenance_and_decoder`, reusing existing registration characterization helpers against the new body |
| Fixed safe input errors with no submitted sentinel/context/cause | Existing `reject` helper on all invalid cases; recursive decoder safe-error assertions |
| Identity parser/adapter/CLI/worker reject new Access body before effects | `test_identity_consumers_refuse_before_effects` |
| Access execute/CLI command_unsupported; outcome command_invalid; worker closed ValueError; target/connection/dispatch/SQL traps | `test_access_consumers_refuse_before_effects` |
| All registration shapes/absence/decoder behavior; existing Identity and registration adapters/CLI unchanged | Unmodified suites in commands below |

## Commands and results

Repository root; every pytest command uses this exact prefix:

```sh
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python -I -B -m pytest -p no:cacheprovider
```

Private retained logs: `platform/deployment/.local/access-enable-input-20261021/`.

1. Before implementation, append `services/access/tests/test_application_enable_input.py -k typed -x -q`:
   exit1, **1 failed,9 deselected**, valid enablement rejected as
   `access_operator_input_invalid`; `acceptance-red.log`.
2. Before implementation, append `services/access/tests/test_access_operator_input.py services/access/tests/test_identity_operator_input.py -q`:
   exit0, **204 passed**; `characterization.log`.
3. First new-suite run, append `services/access/tests/test_application_enable_input.py -q`:
   **7 failed,10 passed**; `focused-first.log`. Test assertions incorrectly searched
   object repr for short values `ab`/`1` (also present in class names/addresses), and
   traceback source included a literal fixture value. Corrected to assert exact object
   repr (no field representation) and call with a variable. No implementation behavior
   or expected result was changed to dismiss these test failures.
4. Append `services/access/tests/test_application_enable_input.py services/access/tests/test_access_operator_input.py services/access/tests/test_identity_operator_input.py services/access/tests/test_identity_operator.py services/access/tests/test_operator_cli.py -q`:
   exit0, **297 passed**; `focused-green.log`.
5. Append `services/access/tests/test_application_register.py services/access/tests/test_permission_register.py services/access/tests/test_entry_permission_register.py -q`:
   exit0, **84 passed**; `adapters-green.log`.

Root owns independent review, affected regression (`services/access/tests
apps/pts/tests/test_release.py platform/deployment/tests/test_migrate_adapter.py -q`),
both composition dry runs and preservation/frozen-intent checks after this source-frozen
handoff. Those are not claimed completed here. No root repository-wide test/lint/typecheck
command exists; no runtime-readiness qualification was attempted or claimed.

## Source hashes

Initial implementation-handoff SHA256 values, retained in `source-hashes.sha256`
in the private log directory. The test hash below is historical; the current reviewed
test hash is recorded in the correction checkpoint at the end of this document:

```text
9ac5bc3690857de3ea50b97814aa372162a69bc99e1fad69510a1afea80f32c2  services/access/access_operator_input.py
d1d5e0c9140c98c7c2bb3a08b8d2a4a08305bf5a4b14802a73a7f9fb149442c4  services/access/tests/test_application_enable_input.py
4f53c92a57333146b37e567b2dfba870a3774834c402345a3e2f43e2fe45637d  services/access/tests/test_access_operator_input.py
2e1cfca4cf4d291c60d156aff84515a21593789bdc37ffcddcdd0ad2a3a2f71d  services/access/identity_operator_input.py
94d2849aebed1f8a6edb436b526397e80a422d27328781339b2e5814e1462d13  services/access/access_operator.py
cb29b7e5f4f2685e0363ddf66ca181bcab186a2cadd75a935c7812b76810cc4c  services/access/operator_cli.py
90ddfd4fc87e25a4b641a9a9c3ddd8e47e17a4240556a4e3cc057839683381db  platform/docs/architecture/contracts/identity-access-execution-substrate.md
bac0254abc9758effc40517bbb97377eac4826ec06942c7c06c284814491e4dc  apps/kdg-capture/docs/shared-prerequisites.md
```

## Impact decisions and remaining scope

Scaffold: the existing parser and focused pure-input/refusal fixtures are the reusable
owner pattern; no generator implementation/configuration changes are needed or authorized.
Shared UI: none, no user interface change. Agent context: existing boundaries suffice,
AGENTS.md unchanged. Documentation: mutable substrate and KDG handoffs point here.
ADR: existing selected contracts suffice; accepted ADRs unchanged.

Only strict input preparation is delivered. Mutable registry persistence, revision and
immutable evidence guards and protected enablement execution remain future work. Access
adapter/CLI execute still refuse before effects as command_unsupported; outcome and
worker retain their existing refusal families. Parsing conveys neither authority nor
access. ACCESS-A/B, coordinated PtS/KDG consumers and real-target activation remain gated.


## Review correction checkpoint — 2026-10-21

The focused test file now checks adapter execute refusal with the existing safe-error
helper (fixed args, absent cause/context and redaction), using variable inputs to avoid
submitted values in traceback source. Access execute/CLI/outcome/worker refusal traps
run with both true and false without changing refusal families. Typed preservation also
accepts `a0_b`. A direct reused-decoder test proves deeply nested input rejection with
safe errors and a valid nested control, independently of envelope closure. Existing
numeric decoder proof and shared tests remain unchanged.

Exact focused correction command from repository root:

```sh
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python -I -B -m pytest -p no:cacheprovider services/access/tests/test_application_enable_input.py -q
```

Exit0, **23 passed in 0.24s**; retained as `focused-corrections.log` in the same private
log directory. Prior RED/characterization/first/focused/adapter logs and initial source
hashes remain historical and are not relabeled as verification of the corrected bytes.
No wider tests or native resources were run for this correction. Root owns broader checks.

Current corrected test SHA256 (also `source-hashes-corrections.sha256`):

```text
bc16baea792c6817869dfe6558fedd4ab2e6edd04ea7bab25d9e5b0e6a15fcaf  services/access/tests/test_application_enable_input.py
```

Only the focused tests and this evidence document changed during correction. Parser,
execution boundaries and historical sources remain unchanged. This is the final
source-frozen correction handoff; enablement execution and runtime activation remain gated.

## Final root verification

Root inspected the complete scoped diff and audited all six matrix rows against executed
tests. Three independent review lenses completed: edge and verification-gap returned no
findings; four small blind-review test corrections passed. Shared-test restructuring
suggestions were rejected as unnecessary complexity; the per-finding reasoning is in the
Build spec. No new work was deferred. Existing broader bootstrap/activation limits remain.

Final commands from the repository root:

```sh
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python -I -B -m pytest services/access/tests apps/pts/tests/test_release.py platform/deployment/tests/test_migrate_adapter.py -q -p no:cacheprovider
platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python -B tools/py/run_compose_supabase.py --check-only
platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python -B tools/py/run_compose_supabase.py --identity-authority owned --no-seeds --check-only
```

Results: **1259 passed in 35.57s**, no skips; both composition dry runs exit0 and change
no files. Logs are `root-regression.log`, `root-compose-default.log` and
`root-compose-owned.log` in the private directory above. The independent preimplementation
RED is retained as `root-acceptance-red.log`; root's earlier297-test focused check remains
historical to its pre-correction test bytes. Final suite includes the23 corrected cases.

Scoped whitespace and frozen-intent checks pass. All45 protected historical/Identity
source hashes match the starting snapshot; the Access adapter/CLI bytes remain unchanged.
Concurrent Leave/Scribeswell planning updates were observed, preserved and excluded from
the commit. `root-verification.json` records the source/log hashes and preservation audit.
No database/Docker/credentials or real access were used; no runtime-readiness claim follows.
