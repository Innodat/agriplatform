# First committed owner-local WRITE candidate

Bounded synthetic delivery for [ADR-0061](../docs/architecture/decisions/0061-kdg-first-committed-operation-wins.md),
using the existing builder owner-copy installer and historical atomic primitives.
Baseline: `aae72cff9071186b700dd0ba578769431bac78ba`. Review and final custody are recorded below.
The candidate has no command fingerprint fields, key configuration, creation or verification.
Historical fingerprint/secret/atomic candidates remain unchanged and reusable.

## Scope and acceptance ordering

The additive `examples/owned-service/first_committed_write.py` validates compact sample
receipts and strict bounded JSON. `tests/first_committed_sample.py` owns the explicit
neutral record.create/edit SQL and current-authority orchestration. It is a synthetic
consumer, not a KDG domain implementation, API, offline queue or runtime engine.
Historical `atomic_write.py` supplies transaction/context/budget/lock primitives. Its
incidental fingerprint-module import is retained for byte compatibility; no fingerprint
function is called, and no fingerprint key/configuration is required.

Before implementing the new candidate, isolated pytest `test_candidate_import` failed
with ModuleNotFoundError for first_committed_write. Exact observed output is retained
as a transcript capture in D/acceptance-red.log. This missing-module RED witnesses the
new candidate's absence; the behavioral matrix below supplies actual consuming proof.
The initial RED was import-only. The full first-committed behavioral acceptance was
added after the initial implementation: this misses the repository's intended behavioral
ATDD ordering and is not claimed as compliant evidence of that ordering. Chronology
cannot be repaired by rerunning a test. Review corrections use behavioral RED before
implementation, and all failed native attempts remain in the proof directory.

D: `platform/builder-cli/.local/write-first-committed-20261022` (ignored).
P: absolute `platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python`.
N: absolute `platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node`.
S: `payload/supabase/supabase` beside the same pinned toolchain.

Existing `dev.py up --target platform/deployment/environments/kdg-local.json --run-id
99b7231c-0a5b-4bdb-98e8-3329564c526a --supabase S` resumed the retained local stack,
exit0. The existing preparer was copied byte-identically to D/preparer, beside the new
fixture SQL under its expected atomic_write_fixture.sql name. Its fixed loopback55482/
postgres guard created an exclusive synthetic database and restricted migrator/runtime
roles, without changing any old fixture. D/attempt1/prepared.json binds exact executed SQL;
fixture.json is private0600 and never printed. TCP and Docker execution required the
authorized local process environment outside the sandbox; all resources/data remain.

## Requirement-to-test traceability

| Requirement | Executed test |
| --- | --- |
| Changed body/target, original receipt/version after later revision/lifecycle, lookup and current stored authority | test_changed_valid_target_body_versions_and_later_lifecycle |
| Create and edit, no-op without fake history, same UUID across commands | test_create_replay_noop_and_exact_command_scope |
| Real different-body/target concurrency and rollback/recheck outside locks | test_different_bodies_race_and_raced_target_recheck |
| Stored-target denial, foreign scope, unresolved then original operation commits | test_denied_original_target_and_foreign_unknown |
| Create/edit full rollback on evidence/outcome failure | test_required_insert_failure_rolls_back_every_effect (four variants) |
| Unsupported retained metadata, no overwrite/reexecution | test_unsupported_stored_receipt_is_retained |
| Strict wire/DTO parsing and fresh-only stale validation | test_strict_wire_parser; test_invalid_fresh_stale_and_structure_before_authority |
| No fingerprint fields/calls or keys | test_no_fingerprint_fields_or_calls |
| Restricted runtime, FORCE RLS, alternate writes, exact local linkage and pool context | databases; test_pool_context_commit_rollback_and_foreign_isolation; test_immutable_guards_runtime_ddl_and_exact_linkage |
| Busy/domain/statement waits, stale observations, late commit and idle transaction recovery | timeout/budget/safe-error tests in test_first_committed_write.py |
| Actual installer copy, executable siblings and edit/provenance preservation | test_existing_installer_copied_candidate_executes_and_replay_preserves |

## Delivery impacts and limits

Scaffold: additive owner-copy candidate plus actual existing-installer proof; no template,
public recipe or runtime promotion. Shared UI: unchanged; frozen snapshot acknowledgement,
receipt-target reconciliation and predecessor blocking remain consumer obligations.
Agent context: unchanged; repository owner/safe-logging instructions suffice.
Documentation: this evidence, example README, Build spec and current KDG handoff.
ADRs: adopts0061; accepted ADR bytes unchanged. Dependencies including TypeScript7.0.2
and all historical migration/reference sources remain unchanged.

The sample uses trusted backend org/account/actor assertions and a bounded authority
callback standing in for the consuming owner's HTTP checks. It does not authenticate
requests or implement Access integration, KDG questionnaire/child/assignment policy,
OpenAPI/frontend DTOs, physical devices or browser queue mechanics. Synthetic local
actor FKs demonstrate attribution/linkage, not cross-owner application actor FKs.
Lookup absence is unresolved, not proof no concurrent transaction can commit. Original
successful receipts survive later changes, with fresh current authority on the actual
stored target; no automatic expiry or new operation is added. Lost response is simulated
by discarding a committed receipt, not actual HTTP fault injection.

Historical primitives bound SQL/lock/transaction waits and check one monotonic budget;
consuming network/driver timeouts must separately bound transport. No hard total socket
wall-clock, ordinary backup/restore, controlled release compatibility, production/pilot,
real-account/access, Leave/editor or deployment readiness is claimed. No fingerprint/HMAC
key work is restored as a current KDG gate.


## Executed verification

- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 ATOMIC_WRITE_FIXTURE=<absolute D/attempt1/fixture.json> FINGERPRINT_TEST_NODE=N P -I -B -m pytest platform/builder-cli/tests/test_first_committed_write.py -q -p no:cacheprovider`: agent **42 passed6.47s**, D/first-suite-final.log; independent root **42 passed6.35s**, D/root-candidate.log. No skips. Exact executed source hashes captured in D/execution-sources.json.
- Same invocation with historical ATOMIC_WRITE_FIXTURE=D/../write-atomic-20261022/attempt3/fixture.json and unchanged test_atomic_write.py/test_command_fingerprint.py: **100 passed6.50s**, D/historical-regression.log. Fingerprint pre-change baseline **63 passed**, D/fingerprint-baseline.log. Secret-file sources/proofs are byte-verified; their unchanged UID10001 suite was not rerun for this unrelated additive candidate.
- `timeout 60s N --test platform/builder-cli/tests/*.test.mjs`: **62 passed16.18s**, D/builder-regression.log.
- `P -I -B D/verify_retained.py D/attempt1/fixture.json`: **exit0**, D/retained-inspection.log/json. All connections explicitly read-only; verifies actual runtime flags/ACLs, FORCE RLS, no fingerprint columns, validated constraints, missing-context zero visibility and exact outcome/revision/owner/executor/org/target linkage. Retains safe counts and state digests, no row dumps.

Failed development runs remain: attempt1 sandbox TCP refusal, attempt2 authority callback
signature mistake in test setup, attempt3 wrong test Node path and unexpectedly short
busy-lock measurement (1.198s against inherited1.7s lower bound). No assertion was
weakened. Correct Node path and unchanged wait expectation passed attempt4 and final
agent/root matrices. The earlier timing observation remains unexplained rather than
claimed fixed. Database behavior still reports safe operation_busy and retains no effects.
Concurrent isolation, budget and changed-edit-body tests are additionally covered by
`test_same_uuid_isolated_by_exact_org_account_command`,
`test_raced_stored_target_denial_and_original_budget`, and
`test_changed_edit_bodies_race_has_one_complete_winner`.


## Review closure and final reviewed proof

All three Build review lenses completed. Eleven findings were assessed separately in
[the Build triage log](../../_bmad-output/implementation-artifacts/spec-write-first-committed-candidate.md#review-triage-log).
Corrections add safe authorization_unavailable with suppressed transport details,
authoritative rollback/losing-target absence checks, exact FK23503/constraint evidence
without incidental UNIQUE/RLS refusal, captured fingerprint-alias guards, original v2
receipts replayed from v1, successful parser/native execution and a thin checked-in
preparation wrapper. The authority transport canary failed before its fix; see
D/authority-canary-red.log. Focused review correction **14 passed35 deselected4.20s**,
D/review-focused-final.log; the earlier expected FK-name truncation failure remains.

Reproduce preparation with `P -I -B platform/builder-cli/tests/prepare_first_committed_write.py
--admin <private-existing-local-fixture> --proof <new-exclusive-directory>`.
The wrapper retains a UUID-named staging sibling containing exact original preparer and
new SQL. It does not modify the original preparer, upgrade old fixtures or remove resources.
Root executed this route into **D/attempt2**, exit0; attempt1 remains retained.

Final reviewed command: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 ATOMIC_WRITE_FIXTURE=<absolute D/attempt2/fixture.json> FINGERPRINT_TEST_NODE=N P -I -B -m pytest platform/builder-cli/tests/test_first_committed_write.py -q -p no:cacheprovider`:
**49 passed7.28s**, no skips, D/final-reviewed-candidate.log. Final independent read-only
inspection: same verifier with D/attempt2/fixture.json, **exit0**,
D/final-retained-inspection.log and D/retained-inspection.json. Builder62 and unchanged
historical100 regressions above remain applicable; none of their execution sources changed.

Instrumented busy proof captures actual blocker, configured2s, SQLSTATE55P03 and server/
monotonic duration under D/attempt1 and D/attempt2/busy-diagnostics-*.json. Original timing
expectation remains unchanged. The earlier1.19793s anomaly lacks server/config evidence
and remains a diagnostic limitation, documented in D/busy-timing-investigation.md;
no retrospective cause or fix is claimed. This does not weaken safe busy/uncertainty behavior.

D/execution-sources.json records exact tested source SHA256 values. D/final-audit.json
binds those sources, private fixture/preparation receipts, retained proof/log hashes,
prior-published atomic/secret evidence preservation and concurrent-tree exclusions.
These private local artifacts are not published credentials. Current evidence does not
claim portable CI bootstrap or a checked-in source-verification command; sources and exact
commands are present in this repository, and the local audit records this specific run.
Historical candidate sources/proof/data and approved dependency baselines are preserved.
Original README/handoff tails are retained byte-for-byte. Final scoped links/whitespace
and dependency/historical-source checks pass. No new runtime feature is deferred by review;
full consuming business API/queue/device/recovery/release evidence remains separately gated.


Tested source manifest (repository paths, SHA256):

| Source | SHA256 |
| --- | --- |
| `platform/builder-cli/examples/owned-service/first_committed_write.py` | `080b23d6e70777fc7e47611e32e81f6340d7cc66a967e059df6f986d939c2ff5` |
| `platform/builder-cli/tests/first_committed_sample.py` | `bda958e35ba9ac1f8d6f6fd8fa7a7ae3426dedd9e3f477c0d79d0c747b218314` |
| `platform/builder-cli/tests/first_committed_fixture.sql` | `efd26487c0fdd1d3d56e9da778c839411eaf041308b31d12ed35487df61ec103` |
| `platform/builder-cli/tests/test_first_committed_write.py` | `e17859ace9198859698e659d464b4b1ca639a55ae344453edd2634f734a3ae2f` |
| `platform/builder-cli/examples/owned-service/atomic_write.py` | `1c5db177b8ec5ad9e7aff831898c1cd1728567dad667f8efb644cdaf18032d20` |
| `platform/builder-cli/examples/owned-service/command_fingerprint.py` | `0f4bd07fe69eb507c32acbddc2505a4830e724d819ea34ea296d710b39cb1713` |
| `platform/builder-cli/tests/prepare_atomic_write.py` | `8b518b9f219b5f50db3477f6a2e873a96cacfb4c778b28a1e2472d9fca91e7d9` |
| `platform/builder-cli/src/scaffold-install.ts` | `b0c5a41d0fa0738cde40d5b8c0b00be3fdc972d7329cd615fb27cb33c0ab7671` |
| `platform/builder-cli/tests/prepare_first_committed_write.py` | `56a7632e1597fb0cb95962852a5ba2c26abe2d26633ec0818cddfbc47dba92ce` |


Native `dev.py stop` for the retained target/run completed exit0 after final verification.
All databases, roles, volumes and prior resources/data remain; no reset/prune/cleanup.
The local scope-only Build commit is not pushed.
