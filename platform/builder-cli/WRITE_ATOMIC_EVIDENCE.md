# Owner-local atomic WRITE candidate

Reviewed bounded candidate complete, 2026-10-22. BMAD-help selected Build for the approved bounded WRITE
atomic-write/context/outcome prerequisite after Access15 and fingerprint foundation
`2a1f3d658ee1200367776bfdf2d7ea2474cfa2b4`. Baseline is
`10b7c7fbf57eaf7c3160212f9b08dedf1bf65114`. The owning contract is
`platform/docs/architecture/contracts/owned-write-and-secret-execution.md`.

The candidate stays in the existing builder's owner-copy examples. Its synthetic
schema is a test fixture, not a KDG application schema or production migration.
No shared runtime service, public scaffold promotion, business API, secret-file
lifecycle or release readiness is claimed.

## Acceptance ordering and environment

D: `platform/builder-cli/.local/write-atomic-20261022`.
P: absolute `platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python`.
N: absolute `platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node`.
S: pinned Supabase executable beside N under `payload/supabase/supabase`.

Before production edits, `P -I -B D/acceptance.py` exited1 with FileNotFoundError
for `examples/owned-service/atomic_write.py`. Original source and output remain in
D/acceptance.py and D/acceptance-red.log. This witnesses the missing candidate only;
focused tests must establish its behavioral acceptance.

Existing `dev.py up --target platform/deployment/environments/kdg-local.json
--run-id 99b7231c-0a5b-4bdb-98e8-3329564c526a --supabase S` resumed the retained
synthetic stack, exit0/completed (`D/native-up-escalated.log`). Initial sandbox Docker
refusal is separately preserved as `D/native-up.log`. All previous resources remain.
Fresh test namespaces must never overwrite old databases, roles or receipts.

## Impact decisions

Scaffold: copyable candidate and real existing-installer proof; templates, recipe,
registry and public generation unchanged. Shared UI: unchanged. Agent context:
existing context/ownership/safe logging instructions suffice. Documentation: example
README, this evidence, Build spec and current KDG handoff. ADRs: existing accepted
decisions apply unchanged. Approved dependency baseline including TypeScript7.0.2
and historical migration/reference bytes stay intact.

## Verification

Root pre-change fingerprint regression:63 passed in0.32s, `D/fingerprint-baseline.log`.
Fresh fixture: D/attempt2/fixture.json (private); prepared.json records its exclusive
synthetic database/roles and exact fixture SQL SHA256. Attempt1 failed at sandbox TCP;
both directories/logs remain. Preparation used P -I -B tests/prepare_atomic_write.py
with --admin pointing to the retained private Access fixture and --proof D/attempt2.
Only the explicit loopback55482/postgres target is accepted. Existing databases,
roles, migration sources and historical proof are unchanged.

- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 ATOMIC_WRITE_FIXTURE=<absolute D/attempt2/fixture.json> FINGERPRINT_TEST_NODE=N P -I -B -m pytest platform/builder-cli/tests/test_atomic_write.py -q -p no:cacheprovider`: **25 passed**,5.77s, D/focused-candidate.log. Local TCP requires the authorized process environment outside the sandbox.
- `timeout 60s N --test platform/builder-cli/tests/*.test.mjs`: **62 passed**,11.28s, D/builder-regression-escalated.log. Sandboxed subprocess run timed out124 with empty output; its D/builder-regression.log remains.
- `PYTHONPATH=platform/builder-cli/examples/owned-service P -B D/acceptance.py`: exit0, D/acceptance-green.log. The sibling import path is explicit for this root import witness; actual copied execution is independently tested below.

First actual native matrix:22 passed/two failed, D/focused-attempt2-escalated.log.
The failing rollback tests rejected any INSERT INTO in a Python formatted traceback,
including static source callsites. Corrected checks exclude dynamic record/actor IDs
and driver IntegrityError, require suppressed exception context and retain exact
before/after rollback equality. No failed business expectation was changed. Subsequent
race tests observe both actual sessions waiting on locks before releasing a held row.
A sandbox-only matrix had8 unit passes/16 connection errors; its log is retained.

| Requirement | Executed evidence |
| --- | --- |
| Atomic mutation, attribution, immutable evidence, original receipt after later change and denied recovery | test_atomic_commit_lost_response_later_change_and_denied_recovery |
| No-op, mismatch, old key unavailable, unsupported retained versions | test_changed_payload_missing_original_key_noop_and_unknown_result; test_stored_unsupported_metadata_and_structural_hmac_key_refuse |
| Complete rollback on evidence/outcome failure | test_required_insert_failure_rolls_back_every_local_effect, both variants |
| Actual duplicate and independent-operation races | test_concurrent_same_key_and_different_key_revision_race, observed database Lock waits |
| Exact stable lock tuple and scoped operation uniqueness | test_exact_lock_vector_and_all_key_dimensions; test_reused_uuid_isolated_across_actual_org_account_command |
| FORCE RLS, actual restricted login, missing/foreign context, pool reuse after commit/rollback | databases fixture; test_pool_context_commit_rollback_and_foreign_isolation |
| Immutable alternate writes, DDL refusal, exact local linkage and nonexistent actor | test_immutable_guards_runtime_ddl_and_exact_linkage; test_wrong_mode_write_missing_actor_and_no_network_under_lock |
| Bounded busy/statement/domain waits, stale observation, exhausted execution, safe errors | test_outcome_lock_timeout_only_is_busy_and_budget_observation_bounds; test_actual_domain_lock_timeout_is_not_operation_busy; test_safe_sql_and_commit_errors_and_post_response_deadline |
| Existing installer copies exact bytes, executes copied siblings on PostgreSQL, preserves edits/provenance | test_existing_installer_copied_candidate_executes_and_replay_preserves |

Primitives intentionally support the organization/account v1 candidate only. Operator
variants already belong to Identity/Access; no new generic algorithm/version registry
is added. The fixture uses a local synthetic actor registry to prove nonexistent-actor
and exact outcome link failures; it does not introduce cross-owner KDG actor FKs.
The sample demonstrates explicit edit/no-op orchestration, not capture.create or
application release/migration readiness. Lost response is demonstrated by discarding
an actual committed result and recovering the original receipt, not a killed server
or real HTTP transport. Secret-file loading/rotation/archive/data+secret restore,
first-consumer DTOs/OpenAPI and release compatibility remain separately gated.

## Review closure

All three independent Build review lenses completed. Every finding has an individual
verdict in the owning Build spec. Direct corrections bind immutable revision record_id
to outcome target_id and enforce original-owner context. New cases use existing targets
and distinguish actual FK refusal from RLS refusal rather than relying on unrelated
uniqueness errors. Active-key failures now use the safe owner error and roll back
all tentative effects. Shape/identity validation precedes the sample authority adapter.
Postcommit deadline checks retain truthful outcome uncertainty. Fixed lock-v1 bytes,
in-budget observation freshness and actual idle transaction expiry strengthen proof.

Server statement/lock/transaction bounds and client monotonic checks cannot interrupt
a blocked socket or bound a delayed commit response. The candidate makes no total
transport wall-clock guarantee; first-consumer network/driver bounds remain required.
The neutral sample conservatively refuses a changed stored target before disclosure;
full consumer routing must perform its exact rollback/recheck/restart outside locks
under the original budget. Added restart machinery was rejected as unnecessary sample
complexity; no permission relaxation or readiness waiver follows.

Root found private builder proof was not ignored; `.gitignore` now follows the existing
deployment `.local/` convention. `git check-ignore` confirms fixture.json is excluded;
all existing evidence remains physically retained. No new deferred-work entry is introduced.


## Final reviewed verification and custody

Authoritative fixture: **D/attempt3**. The target-FK/owner-policy corrections were
installed in this fresh namespace; D/attempt2 and its original SQL/data/receipts remain
historical and unchanged. No existing fixture was restamped or upgraded in place.

- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 ATOMIC_WRITE_FIXTURE=<absolute D/attempt3/fixture.json> FINGERPRINT_TEST_NODE=N P -I -B -m pytest platform/builder-cli/tests/test_atomic_write.py platform/builder-cli/tests/test_command_fingerprint.py -q -p no:cacheprovider`: **100 passed**,7.38s, D/final-combined.log;37 atomic candidate cases plus63 unchanged fingerprint cases, no skips.
- Existing Node builder regression remains **62 passed**; builder implementation and Node tests are unchanged, and the final Python matrix executes actual installer copying/preservation again.
- `P -I -B D/verify_retained.py`: **exit0**, D/retained-inspection.log and retained-inspection.json. Independent read-only inspection verifies restricted runtime flags/ACLs, forced RLS, validated constraints, exact target/executor/org/outcome linkage and retained state digests. Final fixture retains2 actors,34 records,16 outcomes and9 revisions across supported synthetic test runs.
- Existing `dev.py stop --target platform/deployment/environments/kdg-local.json --run-id 99b7231c-0a5b-4bdb-98e8-3329564c526a --supabase S`: **exit0/completed**, D/native-stop.log. All database data, roles, volumes and historical resources remain. No reset/prune/cleanup occurred.

Review-specific coverage includes test_two_existing_records_and_foreign_owner_cannot_reuse_outcome
(no-op outcome prevents incidental uniqueness refusal; checks FK23503 and RLS42501),
test_actual_transaction_timeout_rolls_back_and_releases_lock_while_owner_idle
(server terminates the idle transaction before owner code resumes),
test_in_budget_observation_expiry_and_fresh_acceptance,
test_late_commit_acknowledgement_retains_uncertainty,
test_fixed_historical_lock_v1_literal, test_missing_bad_active_key_rolls_back_tentative_mutation
(five configuration variants), and test_malformed_shapes_ids_never_invoke_authority.
Root added test_unresolved_and_foreign_lookup_do_not_prevent_later_commit: absent and
foreign scoped lookup creates no receipt/effect; the same original operation can
subsequently commit and return its original receipt. The final combined run executes
all these cases. The agent's earlier new-native subset passed7; its initial sandbox
connection errors and both subset logs remain separately retained.

Final audit D/final-audit.json binds **eight exact executed source files and28 proof
inputs/logs**, including private fixture/preparation hashes and retained inspection.
All eight execution sources match the final pre-test snapshot. Of454 pre-existing
protected owner/dependency files,450 remain byte-identical; four concurrently edited
Scribeswell host-release/registry/test files are observed, preserved and excluded.
All dependency locks/manifests, Access/Identity sources/history and builder installer/
templates remain unchanged. Additional concurrent Leave/Scribeswell planning edits
were observed and left untouched. The complete historical KDG handoff remains the
unchanged tail below the new current section. No API/database composition change was
made, so no owner-wide regression/composition/release readiness is claimed.

Audit SHA256: `8173273e3910bf5eba3fe0682560256c00a33c72fb5abab3e381e0fc4a5f97fe`.
The audit intentionally covers executed source and proof, not its own digest-bearing
narrative. Final scoped whitespace checks pass. A scope-only local Build commit
records the candidate/tests/ignore rule/docs; concurrent changes are excluded, nothing
is pushed. Next select secret-file lifecycle and matching data+secret recovery proof
under the existing contract before the first KDG business API. Full consumer authority/
DTO/release acceptance remains required; additional Access variants wait for consumers.
