# Organization application configuration input evidence

2026-10-21; [approved input-only spec](../../_bmad-output/implementation-artifacts/spec-access-a-organization-application-input.md).
Baseline `71d2b85172137563f5e426b059f12b403878520a`. This delivery changes pure input
parsing, focused tests and mutable handoffs only. No database, target, Docker, role,
credential, schema, dependency, generated source, application setting or grant changed.
Historical evidence remains unchanged and source-bound.

## Requirement traceability

New tests: `tests/test_organization_application_input.py`. Existing registration and
enablement suites are unchanged; their absence/revision expectations remain separate.

| Requirement | Executed test |
| --- | --- |
| Create/update, true/false, app2/64/a0_b, revision1/above-JS-safe/max, exact supplied fields, frozen/redacted records, preserved values | `test_typed_frozen_redacted_exact_variant` |
| Both/neither expected keys rejected by presence, including null values | `test_variant_keys_are_exclusive_by_presence` |
| Exact true absence, actual boolean enabled, ASCII app grammar and canonical positive signed-bigint revision strings without coercion | `test_payload_values_without_coercion` |
| Organization scope only, nonnil hyphenated UUID, no payload organization/fallback/inference, uppercase and lowercase spelling preserved | `test_scope_has_no_fallback_or_inference` |
| All four existing commands preserve platform scope and refuse organization fields | `test_existing_commands_remain_platform_only` |
| Missing/extra fields and plain/escaped duplicates at envelope/scope/payload | `test_closed_fields_and_plain_or_escaped_duplicates` |
| Version/operation/reasons/evidence, omitted evidence→None/null rejected, strict UTF8/JSON/nonbytes/nonfinite/oversized integer/deep nesting, recursive NUL/surrogates and exact65536/65537 bytes, both variants | `test_shared_strict_envelope_provenance_decoder_and_byte_limit`, reusing existing characterization assertions |
| Fixed safe parser refusal without submitted values, args/context/cause | Local `reject` uses existing `assert_safe_refusal` throughout; decoder helpers assert the original Identity family |
| Identity parser/adapter/CLI/worker execute and lookup refuse before target/connection/dispatch | `test_identity_consumers_refuse_before_effects`, both variants |
| Access adapter/CLI execute→command_unsupported, outcome→command_invalid, worker→closed ValueError before I/O; both variants and enabled values | `test_access_consumers_refuse_before_effects` with connection/SQL/target/dispatch traps |
| Platform/Identity parser, adapter and CLI compatibility | Existing unmodified suites in the focused command below |

## Exact commands and results

Run from repository root. Every pytest invocation uses this exact prefix:

```sh
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python -I -B -m pytest -p no:cacheprovider
```

Logs are retained privately under `platform/deployment/.local/access-organization-input-20261021/`.

1. Before implementation, append `services/access/tests/test_access_operator_input.py services/access/tests/test_application_enable_input.py services/access/tests/test_identity_operator_input.py -q`.
   Exit0, **227 passed in 0.57s**, `characterization.log`.
2. Before implementation, append `services/access/tests/test_organization_application_input.py -k typed -x -q`.
   Exit1, **1 failed,24 deselected in 0.09s**; valid create input rejects as
   `access_operator_input_invalid`, `acceptance-red.log`. Root's independent earlier
   RED remains separately retained and unchanged.
3. After parser implementation, append `services/access/tests/test_organization_application_input.py -q`.
   Exit0, **60 passed in 0.33s**, `focused-first.log`.
4. Final focused command appends:

```sh
services/access/tests/test_organization_application_input.py services/access/tests/test_application_enable_input.py services/access/tests/test_access_operator_input.py services/access/tests/test_identity_operator_input.py services/access/tests/test_identity_operator.py services/access/tests/test_operator_cli.py services/access/tests/test_application_register.py services/access/tests/test_permission_register.py services/access/tests/test_entry_permission_register.py services/access/tests/test_application_set_enabled.py -q
```

Exit0, **452 passed in 1.68s**, `focused-green-freeze.log`. This includes strengthened
safe-error assertions, explicit Identity lookup refusal and a distinct organization UUID
with both accepted spellings. Earlier452-test `focused-green.log` and
`focused-green-final.log` remain historical to their preceding test bytes. No observed
behavior failure was dismissed or expected result relaxed.

Root owns independent review, broader regression (`services/access/tests
apps/pts/tests/test_release.py platform/deployment/tests/test_migrate_adapter.py -q`),
both composition dry runs, protected46/preservation and frozen-intent verification.
Those are not claimed completed in this implementation handoff. No native startup or
runtime qualification was attempted. There is no repository-wide root lint/typecheck/test
command; the scoped tests above are the actual verification performed here.

## Source custody

Final implementation-handoff SHA256 values, also retained in `source-hashes.sha256`
in the private log directory:

```text
25b2ead35f4caa6dd331b4c95bf9d4098c2dac373a1f66fbcd7c309c5df387d5  services/access/access_operator_input.py
8c6b1565ceb865701a0afb2b62474d77ece216abb293911841321b2bc92c9213  services/access/tests/test_organization_application_input.py
2e1cfca4cf4d291c60d156aff84515a21593789bdc37ffcddcdd0ad2a3a2f71d  services/access/identity_operator_input.py
e68a079128ed9631b75dac9925a798441934b90e0b98e90c6802d32a2d7955b6  services/access/access_operator.py
78f591ab115e22d34d9f91b5591c55bb7ae06c5fd31efc8e4d94d0078c97e0cb  services/access/operator_cli.py
3fc1d062ee26bb2b5bd5f15e99af1b40657971838fd0b0539c8528eb23877a9f  platform/docs/architecture/contracts/identity-access-execution-substrate.md
8186086af07129dfa45c215ca6d074252b058b5996cd03c81e5187eb1cbb3336  apps/kdg-capture/docs/shared-prerequisites.md
fc9ca5d0b8683974c0cd6401ed4f1211af88fa8766bd6e64d7b6b97c2419aa1a  apps/kdg-capture/docs/next-session.md
```

Identity parser, both execution adapters, CLI, lock/fingerprint/receipt/outcome helpers,
migrations and historical evidence have no edits. Concurrent dirty-tree work is preserved
and excluded from this delivery. Root owns the independent final preservation audit.

## Five impact decisions and limits

Scaffold: existing owner-local parser and strict input/refusal fixtures are the reusable
pattern; no generator, scaffold configuration or runtime engine changes are needed.
Shared UI: none; this is pure input preparation. Agent context: current ownership and
execution boundaries suffice; no AGENTS.md change. Documentation: this evidence and
mutable substrate/KDG handoffs record the bounded delivery. ADR: existing selected
contracts suffice; no new decision or accepted-ADR edit is needed.

Organization persistence, external organization verification and protected execution
remain undelivered. Parsing checks neither existence nor authority. Access adapter/CLI
execute refuses valid new bodies as command_unsupported before effects; lookup and
workers retain their closed error families. No grants, real access/configuration,
consumer/Leave/editor work or deployment occurred. ACCESS-A/B and coordinated PtS/KDG
activation remain gated; bootstrap portability remains deferred. Prior runtime proofs
are not qualification of these new parser bytes.

## Review patch checkpoint — 2026-10-21

The preceding implementation-handoff hashes and452-test results are historical to the
pre-review bytes. Root's subsequent broader run exposed36 exact-class assertion failures
and1288 passes (`root-regression.log`): existing Identity characterization intentionally
reloads its module, while Access retains its originally imported scope class. The test
now compares exact `operator.OrganizationScope`, preserving the required class-identity
assertion against the actual parser dependency; the unused Identity import was removed.
No production behavior or expected type was relaxed.

The typed-input parameter matrix now has one create variant and all three update
revisions for each app/enabled pair, removing12 duplicate create cases. Both the direct
`access_worker` and public `worker` dispatcher now receive each existing unsupported
Access execute/outcome request under the same I/O traps and safe-error assertions.
The mutable substrate now includes complete synthetic create/update JSON envelopes
with distinct organization/operation UUIDs, approved reasons and opaque evidence refs.
These are input examples only and make no execution claim.

Only the changed organization-input suite was run for this patch, from repository root:

```sh
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python -I -B -m pytest -p no:cacheprovider services/access/tests/test_organization_application_input.py -q
```

Exit0, **48 passed in 0.31s**, retained as `focused-review-patch.log` in the private
log directory above. Root owns all final broader verification and handoff updates.
No wider tests or native resources were run for this patch.

Final reviewed implementation source hashes (also `source-hashes-review-patch.sha256`):

```text
25b2ead35f4caa6dd331b4c95bf9d4098c2dac373a1f66fbcd7c309c5df387d5  services/access/access_operator_input.py
fdd595c4c07bcdb1418cf6160ccb667d125cde18564aa728a1cd6e2247d1e7c9  services/access/tests/test_organization_application_input.py
6700138b83051704915e91335bbe998f34f1808bf71466707b0ce2c0e18f3f18  platform/docs/architecture/contracts/identity-access-execution-substrate.md
```

Only the focused tests, substrate examples and this evidence were edited during the
patch. Parser/Identity/execution bytes and historical evidence remain unchanged. This
is the source-frozen review-patch handoff; no further agent writes follow.

## Final independent verification — 2026-10-21

The root checks listed as pending above are now complete. Three independent review
lenses completed: edge and verification-gap returned no findings. Blind review led to
removing duplicate create cases, public worker coverage and complete input examples;
root regression identified the module-reload assertion issue described above. These
were patched without changing production parser behavior. Each finding and its verdict
is recorded separately in the spec. No new deferred issue; existing bootstrap portability
remains deferred. Earlier handoff results/hashes remain historical to those bytes.

Final root command, repository root:

```sh
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python -I -B -m pytest services/access/tests apps/pts/tests/test_release.py platform/deployment/tests/test_migrate_adapter.py -q -p no:cacheprovider
```

Exit0, **1312 passed in39.14s**, `root-regression-reviewed.log`. The earlier failed
`root-regression.log` is retained; its36 assertion failures were investigated rather
than waived. Final parser/test hashes equal the reviewed hashes above.

Both composition commands exited0 with no files changed:

```sh
platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python -B tools/py/run_compose_supabase.py --check-only
platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python -B tools/py/run_compose_supabase.py --identity-authority owned --no-seeds --check-only
```

Logs: `root-compose-default.log`, `root-compose-owned.log`. Independent isolated Python
extraction/parse of both JSON contract examples passed, preserving distinct organization
and operation identifiers (`root-contract-examples.log`). All logs reside in the private
directory above. No native startup, database migration or resource modification occurred.

Root verified all46 protected historical/Identity file hashes and the frozen approved
intent. All43 pre-existing untracked files remain byte-identical. Concurrent Leave
changes in epics, decision index, features, implementation plan and E3 handoff were
observed and preserved outside this delivery; the other8 pre-existing tracked dirty
files remain byte-identical. Scope excludes all concurrent work. Final whitespace and
source/log custody checks are retained in `root-verification.json`.

Five impact decisions above remain unchanged. This completes only the input prerequisite;
organization storage, external verification and protected execution remain next work.
