---
title: Qualify Scribeswell publication-command inputs
type: feature
created: 2026-10-22
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: e745be519773d2b288a37c4496ba6300382a656f
context:
  - AGENTS.md
  - _bmad-output/specs/spec-scribeswell-studies/corpus-publication.md
---

<frozen-after-approval reason="User next continues authorized bounded BMAD contract closure and test-first delivery">

## Intent

Qualify publication-command inputs before a future owner-controlled executor can begin, recover or seal a corpus attempt. Implement the canonical Publication-command qualification contract as pure immutable input preparation, independent of authority and database state.

## Boundaries & Constraints

Always preserve existing working-tree work. Use strict closed bounded JSON and the existing complete source validator; safe errors and immutable payloads. No source candidate/audit file is trusted as raw source. The canonical command contract is authoritative for exact fields/bounds/variant semantics. Prepared data has no authority and cannot prove execution, seal or publication. Actor setup consumes the existing Identity external verification contract; no supplied actor/time fields are accepted.

Never add a CLI/output artifact, DB/HTTP/file access in the module, migrations, caller/principal grants, actor provisioning, enforcement, importer/API changes, fingerprint/replay storage, Access/Identity/Leave/factory implementation, browser changes or push/deploy. Do not modify app README or generated reference assets. No competing feature lifecycle.

## I/O & Edge-Case Matrix

| Scenario | Expected behavior |
| --- | --- |
| Valid begin/recover/seal and complete raw artifact | Exact frozen typed command; source-qualified result contains only command, immutable counts and canonical source-candidate SHA256, no scripture/inventory. |
| Malformed/oversize JSON, duplicate/unknown/missing fields at any depth | Fixed corpus_publication.input_invalid; no echoed input, parser detail or unsafe exception cause. |
| Wrong types, floats/constants, invalid reason pairing/scope/labels/evidence, Unicode/NUL/deep nesting | Same fixed safe failure. Strict numeric/UUID/digest boundaries include max generation. |
| Actor/executor/time/ready/manifest or arbitrary fields | Rejected at every envelope/scope/input/payload boundary. |
| Changed source bytes, wrong checksum, incomplete inventory, submitted candidate/audit | Existing safe source_evidence errors; no prepared success. Command failure precedes source qualification. |
| Mutation of parsed/prepared values or caller input | Frozen nested records prevent mutation; no alias to mutable caller data; repr contains no payload/evidence. |
| Standard-library-only execution with forbidden I/O/import probes | Parsing/preparation opens no file/socket, reads no env/credentials, imports no DB/HTTP/application server implementation. |

</frozen-after-approval>

## Code Map

- `apps/scribeswell/backend/corpus_evidence.py`: reuse build_source_candidate(raw,expected_source_sha256,labels) and serialize_candidate; source bounds/semantics unchanged. `corpus_source.py` is the existing pure decoder.
- Add `apps/scribeswell/backend/corpus_publication_input.py`: public parse_command(raw:bytes), prepare_command(raw:bytes,source_raw:bytes), safe CommandValidationError, frozen typed command/payload/scope/input/count/prepared records with repr=False. Nested variants carry exact fields; do not retain mutable dict/list/source inventory.
- `apps/scribeswell/tests/test_corpus_evidence.py`: reuse pattern for synthetic complete39-book source; do not import tests as production dependencies. Add `tests/test_corpus_publication_input.py` covering all matrix rows, each command, boundaries and full checked-in artifact.
- `services/access/identity_operator_input.py` illustrates owner convention only; never import its implementation. Current owned migration/profile/bootstrap is deliberately unchanged.
- New `apps/scribeswell/docs/CORPUS_PUBLICATION_INPUT.md`: exact public Python API/example, input-only limits and actor/controller gates; reference canonical owner contract instead of duplicating feature specs. Root owns canonical/delivery updates, implementer owns app doc/module/tests.

## Tasks & Acceptance

- [x] Observe smallest missing-module/acceptance failure before implementation; then focused TDD for parser/prepare safety.
- [x] Implement all command variants, exact bounds/type checks and fixed safe failures. Complete canonical schema including required evidence/reason pairing; reject every override.
- [x] Qualify raw source through existing validator for all three variants; return only immutable counts/hash/command, no full source/candidate or invented authority/receipt.
- [x] Execute every matrix case including full checked-in artifact and standard-library/no-I/O isolation; preserve existing source/importer/auditor contracts.
- [x] Document executable input-only behavior, exact tests/results and remaining current-actor/caller/execution gates, with scaffold/shared-UI/context/ADR impacts.

Given valid command bytes and complete matching source, when preparation completes, then a deeply immutable source-qualified command exists without any external action. Given invalid or spoofed command input, when parsed, then only the stable safe failure is visible. Given an audit/candidate instead of source or changed bytes, when prepared, then no qualified success results. These are ST-38 prerequisites, not completed publication acceptance.

## Implementation Notes

Intent gaps: none; internal wire choices follow existing owner conventions. No irreversible target actions. Footprint is one pure app module, its focused tests, one app doc and delivery/canonical handoff. Scaffold/shared UI/agent-context: no change or promotion; accepted ADRs unchanged, app-local first-consumer qualification only. Existing Identity owner is external verification reference, not imported runtime. All command records should suppress payload repr; errors must not chain decoder/input-bearing exceptions.

Implementation agent runs focused pure tests, then reports before root final regression. No database fixture needed for new behavior. Existing321-test app suite has guarded PostgreSQL tests; root provides temporary isolated fixture for final full regression and stops it. Never point at an existing workstation/production cluster. No browser tests expected because no browser change.

## Spec Change Log

## Review Triage Log

## Verification

`/tmp/scribeswell-studies-tests-py312/bin/python -m pytest apps/scribeswell/tests/test_corpus_publication_input.py apps/scribeswell/tests/test_corpus_evidence.py -q`; root full app with explicit isolated PostgreSQL17 URL, `python3 tools/py/run_compose_supabase.py --check-only`, task whitespace and canonical preservation/link checks. Record exact red/green commands/results; missing/skipped DB tests are not acceptance.

## Verification evidence

Root created only task-owned disposable PostgreSQL17 container `scribeswell-command-input-20261022`, ID8e70787219df2a2ea866df43d3a0e09e29da1ff200b0ee0df290232c5dace35d, image sha256:212aeeeb8faaef6c46498d86cbec6b9344d8d9492996b174664ff82c562ab685, localhost32771, memory-backed data, 1GiB/2CPU limits. Guarded app fixtures use explicit `SCRIBESWELL_TEST_DATABASE_URL=postgresql://postgres:fixture@127.0.0.1:32771/postgres`; root stops exact container after final verification. No existing database/container or production target touched.

`python3 tools/py/run_compose_supabase.py --check-only` passed; no files changed. All19 adopted/spec companions resolve,11 CAP and38 ST IDs remain stable; authored links pass. Existing migration/deployment/source/importer paths match baseline; no platform implementation is affected by this pure module.


Test-first evidence: `/tmp/scribeswell-studies-tests-py312/bin/python -m pytest apps/scribeswell/tests/test_corpus_publication_input.py -q -x` failed as expected before implementation:1 failure, ModuleNotFoundError,0.04s. After implementation, `/tmp/scribeswell-studies-tests-py312/bin/python -m pytest apps/scribeswell/tests/test_corpus_publication_input.py apps/scribeswell/tests/test_corpus_evidence.py -q` passed195 tests11.23s, including146 new input cases and49 retained source cases. Root read all three app additions in the task-only unified diff, independently checked each matrix row against the tests and initiated full app regression with the explicit disposable database fixture. No skipped matrix case; full regression/review closure still pending.

### Independent review triage

All three lenses completed before triage. Edge returned no findings. Blind floor6 arithmetic was28.031kB→6; six findings below are individually assessed. Verification independently mutation-tested the unasserted attempt identity.

| Finding | Verdict | Evidence / route |
| --- | --- | --- |
| B1 exact returned field values not independently asserted | medium | Tests compare prepared command with the same parser and assert only some fields. A shared mis-mapping can survive. Patch assertions for all fields on parsed/prepared variants. |
| B2 expected candidate hash uses same production builder/serializer | low | Canonical source encoder already has independent existing vectors, but this new adapter has no fixed small-source hash proving its exact label wiring. Add one fixed golden expected hash to existing synthetic source test; direct test strengthening. |
| B3 escaped-equivalent duplicate keys untested | low | _pairs correctly sees decoded keys, but current tests repeat identical lexical spellings only. Add escaped-equivalent duplicate case within existing closure tests. |
| B4 field-invalid command/source precedence untested | medium | Existing precedence test uses malformed JSON, not a syntactically valid invalid command. Add invalid-field/source combination using same source-call sentinel. |
| B5 representation assertion checks only evidence_ref | medium | Nested source records contain no evidence_ref, so leaked labels/checksum would escape that assertion. Strengthen with each record's representative stored values; current repr=False implementation itself is correct. |
| B6 subprocess purity check unbounded | medium | subprocess.run has no timeout and could stall on future import/prepare regression. Add finite timeout to existing subprocess call. |
| V1 expected_attempt_id valid retention untested | medium | Reviewer verified an in-memory attempt=operation_id mutation still passes146 tests. Existing malformed-ID tests prove validation only. Add independent distinct operation/attempt identity assertions in both parsed/prepared recover/seal results. Same missing-field assertion root cause as B1; log retained individually. |

Group B1/V1 for the shared field-retention assertion gap; B2–B6 each retain separate causes. All seven route to small test-only patches, no new public surface or state, no production defect identified. No intent gap, spec change or deferred finding. Root re-engages the same implementation agent; root full regression follows fixes.

Root intermediate full regression before review additions: `SCRIBESWELL_TEST_DATABASE_URL=postgresql://postgres:fixture@127.0.0.1:32771/postgres timeout 240 /tmp/scribeswell-studies-tests-py312/bin/python -m pytest apps/scribeswell/tests -q` passed467 tests, no skips,138.29s; one existing Starlette/httpx deprecation. No production source change required by reviews; final root run follows test-only patches. Concurrent owner HEAD advanced to36f0302496c1e3dd3c6514be40a96d424ccfce30 and is preserved; this delivery's baseline remains full original e745be519773d2b288a37c4496ba6300382a656f.


### Review fixes verified

Same implementation agent patched only the input test file. Its exact command `/tmp/scribeswell-studies-tests-py312/bin/python -m pytest apps/scribeswell/tests/test_corpus_publication_input.py -q` passed151 tests2.93s. All B1–B6/V1 survivors resolved: independent exact field retention (including distinct operation/attempt IDs), independent hand-assembled canonical golden hash1213c12da4283b80f6e2bc5cc89d4ca4dc44ed5b430b29b929d596618c8a9cb0, escaped-equivalent duplicate keys at all four boundaries, valid-JSON field-invalid ordering, each nested record repr and15s purity subprocess timeout. Production module unchanged; root corrected app example to use separately reviewed expected artifact checksum and removed stale intermediate test-count wording. No new surface/state or deferred finding. Root read the complete patched test diff and initiated final full regression.

| Matrix / requirement | Executed covering tests |
| --- | --- |
| Valid all variants + immutable safe result | complete_source_qualifies_exact_immutable_command across3 variants, explicit all-field retention and fixed independent candidate hash; full_checked_in_source verifies39/929/23213/306785. |
| Closed duplicate/unknown/missing/oversize malformed JSON | bad_encoding_and_json_are_safe; missing_and_duplicate_fields_at_every_boundary; escaped_equivalent_duplicate_names; recovery_and_seal_require_exact_payload; begin_rejects_recovery_tuple. |
| Types/numeric/identity/reason/Unicode bounds | field_type_and_format_boundaries; attempt_and_generation_boundaries; exact_body_and_string_maxima; reason_pairing_and_synthetic; every_object_boundary_requires_an_object across all variants. |
| No actor/time/publication overrides | override_rejected_at_every_boundary across envelope/scope/payload/input. |
| Complete source requalification and precedence | source_requalification_for_every_variant all15 variant/fault combinations; command_failure_precedes_source malformed JSON and valid-JSON invalid-field variants, source spy. |
| No mutable alias / safe repr | recursive frozen/slotted record field checks and independent payload repr assertions in complete_source_qualifies_exact_immutable_command; caller mutation does not change parsed fields. |
| No external I/O/dependencies | standard_library_only_and_no_io fresh -S process, guarded imports/open/network/subprocess/environment, finite15s subprocess deadline. Root also read module/dependency source; no I/O path introduced. |

All151 focused cases ran, no skips. Root final app regression includes retained source/importer/auditor/migration/reader/lexicon/adapter tests; platform behavior is unchanged, so no unrelated platform/browser rerun is claimed. Requirement traceability is bounded to ST-38 input prerequisite; no current source state/actor verification or publication success asserted.


## Final verification and handoff

Root final command after all review patches:

```sh
SCRIBESWELL_TEST_DATABASE_URL=postgresql://postgres:fixture@127.0.0.1:32771/postgres timeout 240 /tmp/scribeswell-studies-tests-py312/bin/python -m pytest apps/scribeswell/tests -q
```

**472 passed, no skips,133.56s**, one existing Starlette/httpx deprecation warning. This includes151 new input cases and321 retained app/database regressions. Initial affected pure run195 passed11.23s; post-review focused input run151 passed2.93s. Composition check-only passed without mutation; canonical19 companion links,11 CAP/38 ST IDs and authored links/task whitespace pass. No platform or browser implementation changed; no platform/browser/build/image tests were rerun or claimed. Source/importer, original migration/profile/bootstrap and deployment paths match original full baseline e745be519773d2b288a37c4496ba6300382a656f. Root rewrote/read final task diff including test/documentation deltas and audited all matrix cases as actually executed. Seven review findings individually triaged/resolved, nothing deferred.

Root stopped exact owned PostgreSQL container8e70787219df2a2ea866df43d3a0e09e29da1ff200b0ee0df290232c5dace35d successfully; --rm removes memory-backed fixture. No other service or production target touched. Production migration adoption/role preparation, actor verification, command execution, importer transition, enforcement, audit sealing, ready manifest and reader proof remain unimplemented/gated. Input qualification is implemented and source checks are actual tests; no actor/authorization/execution/seal/publication success is implied. Full ST-38/D-2/D-5 and private Studies remain open. Standalone account entry/provider gates remain unchanged; Access is still its separate implementation session. No Leave/factory/Identity implementation.

Scaffold/shared UI/agent-context decisions: no change or promotion for this pure app-local first consumer. App executable API documentation updated; accepted ADRs unchanged. Canonical corpus-publication, brownfield and acceptance derived through bmad-spec; stable product/UX/privacy/signup rules preserved. Next bounded delivery must close the executable controller's prepared actual-session principal/exact-source command policy, verified stable executor evidence, stored exact-input retry/outcome contract and bounded invocation before operational migration/role/importer activation. No broad app factory or owner HTTP service invented.

Local commit is scoped to the three new app module/test/doc files plus this delivery record. Pre-existing app README and other sessions' work remain preserved/excluded; canonical updates stay in the pre-existing untracked specs tree, consistent with prior delivery boundaries. Concurrent factory commit36f0302496c1e3dd3c6514be40a96d424ccfce30 remains in history. No push/deploy.
