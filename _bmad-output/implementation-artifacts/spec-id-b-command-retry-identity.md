---
title: 'Identity typed command retry identity'
type: 'feature'
created: '2026-10-21'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="standing approval for bounded shared prerequisites">

## Intent

Prepare consistent fingerprints and scoped outcome lock identities for the four
already-parsed Identity command variants. Given a parser-produced command, canonical
bytes normalize every UUID while retaining all typed fields, defaults, Unicode and
string bigint values. Given an executor and command, the lock key binds the accepted
version1 Identity tuple: organization/platform scope, executor, command type and
operation ID. Payload changes alter fingerprints without changing that retry key.
Existing actor registration bytes and two-argument lock helper remain compatible.

Given account_actor.ensure, membership.join or membership.retire at the adapter,
execution still refuses before touching the connection. This pure owner-helper change
adds no SQL migration, command activation, account verification, permission, seed
transition, schema/client/generator, UI or new runtime framework. Preserve all current
working-tree changes, local data/resources and approved dependency pins. Requirements
come from the existing execution-substrate command/outcome contract; full authorized
membership commands and full-unique removal remain later gates.

</frozen-after-approval>

## Implementation Notes

- bmad-help selection: continue ID-B via bmad-build; pure retry-identity prerequisite
  before owner lifecycle command activation. All four input parsers already exist.
- Small, reversible owner-helper change with known contracts/callers: oneshot route.
- Baseline: `4b4368568a174b37b95697eafd40835cb595f4ed`.
- ATDD: extend owner adapter acceptance before implementation; focused TDD covers
  JCS bytes, UUID aliases, string bigint/null/defaults, key namespace separation,
  payload conflict identity and refusal of all unimplemented commands before SQL.

- Added typed `command_outcome_lock_key(executor, command)` alongside the compatible
  two-argument actor helper; shared private tuple hashing avoids arbitrary loose scope
  parameters. These helpers accept parser-produced inputs and confer no authority.
- Initial acceptance RED: five failures /25 passes (membership actor_id KeyError,
  unnormalized account UUID, missing scoped helper). Focused GREEN:189 passed in1.93s.
  During test authoring two fixtures were corrected against existing contracts:
  reason_code uses the allowed setup_correction; internal worker refusal is ValueError,
  while public CLI/adapter refusal remains command_unsupported. No production behavior
  or expected result was changed to dismiss these fixture errors.

## Requirement-to-test evidence

| Requirement | Test in services/access/tests |
| --- | --- |
| Complete canonical typed envelopes, normalized UUIDs and organization scope, Unicode, string bigint, null/default owner | test_identity_operator.py::test_typed_retry_identity_matches_complete_normalized_wire_contract (four variants); existing test_complete_normalized_jcs_and_write_lock covers absent evidence_ref/null and previous actor bytes |
| Exact version1 tuple and old actor helper compatibility | Same four-variant test: independent stdlib JSON/SHA-256 oracle; legacy actor-vector regression |
| Payload/reason/evidence fingerprints change while retry namespace stays fixed | test_identity_operator.py::test_retry_key_binds_namespace_but_fingerprint_binds_payload |
| Different organization, command, executor or operation separate lock namespaces | Same namespace test |
| No command activation | test_identity_operator.py::test_adapter_exists_and_rejects_unimplemented_command_before_sql (three variants); test_operator_cli.py::test_prepared_retry_inputs_do_not_activate_cli_or_worker (three variants), poisoned target/dispatcher/connection |

## Five impact decisions

- Scaffold: use existing Identity owner adapter; no generator/template/schema/client
  or qualification framework changes. No new dependency; TypeScript7.0.2 stays.
- Shared UI: no visible interaction or reusable UI consumer.
- Agent context: existing repository safeguards suffice; no AGENTS.md change.
- Documentation: this evidence and KDG continuation record preparation versus activation.
- ADR: existing execution-substrate contract, ADR-0020 release compatibility and
  ADR-0059 ownership apply; no new decision or accepted ADR edit.

## Verification

Repository-root commands, frozen existing owner Python3.15.0:

```bash
OWNER_PYTHON=platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$OWNER_PYTHON" -I -B -m pytest services/access/tests/test_identity_operator.py -q -p no:cacheprovider
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$OWNER_PYTHON" -I -B -m pytest services/access/tests/test_identity_operator.py services/access/tests/test_identity_operator_input.py services/access/tests/test_operator_cli.py -q -p no:cacheprovider
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$OWNER_PYTHON" -I -B -m pytest services/access/tests apps/pts/tests/test_release.py -q -p no:cacheprovider
```

CPU/local-process verification only. No new database runtime/concurrency proof claimed;
future SQL command implementations must independently prove the same canonical tuples,
authorization, audit, outcomes and locking. No database/Docker/retained frame mutation.
Historical source/reference pins remain byte-identical to baseline.

- Preservation check: all33 tracked files under services/access/identity-migrations
  compare byte-for-byte to HEAD. Existing Scribeswell/brainstorming/specs/Expense
  changes remain outside this delivery. No composer rerun is needed because migration,
  composition and manifests are unchanged; no root npm verification is claimed.
- Contract source: [Identity/Access execution substrate](../../platform/docs/architecture/contracts/identity-access-execution-substrate.md),
  command inputs and outcome handling. This Build record is delivery evidence, not a
  duplicate product specification or substitute runtime contract.

- Affected regression GREEN:856 tests passed in35.90s. `git diff --check` PASS.

## Review Triage Log

One-shot blind review complete; larger-route edge-case and verification-gap layers
skipped as prescribed for this bounded route. No deferred findings.

- Low, patch: independent dynamic expected values lacked frozen cross-implementation
  vectors. Added four fixed canonical SHA-256 and signed lock-key vectors, generated
  from explicit fixture dictionaries with stdlib JSON/SHA-256, without owner helpers.
- Low, patch: payload-conflict coverage only exercised join. Added account/actor/display
  and retirement membership/revision mutations with stable retry key assertions.
- Low, patch: Unicode preservation lacked composed/decomposed distinction. Added both
  display-bearing command variants; distinct fingerprints and unchanged retry keys.
- Low, patch: verification results were scattered rather than paired to each command.
  Added the consolidated command/result record below. Broad regression result had
  already been appended during review; the reporting correction still improves clarity.


Final command/result record (all commands shown above):

| Command selection | Result / exit status |
| --- | --- |
| Owner adapter only, initial ATDD | 5 failed,25 passed in0.50s /1 |
| Owner adapter only, final reviewed tests | 37 passed in0.46s /0 |
| Adapter/parser/CLI, initial GREEN | 189 passed in1.93s /0 |
| Adapter/parser/CLI, after review patches | 196 passed in1.85s /0 |
| Access/PtS release, initial full regression | 856 passed in35.90s /0 |
| Access/PtS release, final after review patches | 863 passed in28.52s /0 |
| git diff --check | PASS /0 |

Review patches only add verification/evidence; production helper code is unchanged
since initial GREEN. No findings remain deferred. Supported register execution and
receipt behavior remain covered by the affected regression suite.
