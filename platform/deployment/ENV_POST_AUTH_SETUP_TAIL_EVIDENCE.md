# ENV owner post-Auth setup tail

Complete: independent review corrections and final affected verification pass. The selected increment completes only the existing owner's
post-Auth empty/disabled setup tail and initializes its private current-branch
artifact. It does not resume the terminated CLI, deliver running Auth/API services,
or qualify a complete fresh setup. Runtime and fresh-setup readiness remain false.

## Source and selected inputs

Pinned Supabase CLI 2.120.0 commit
753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4 supplies the continuation after verified
API default privileges. The existing generated ENV config, not root Supabase config,
fixes disabled migrations/seed with empty paths and omits Vault inputs. The closed
invocation excludes experimental mode; enabling experimental schema execution would
invalidate this no-SQL conclusion. Strict fixture custody excludes roles.sql.

| Pinned primary source | Relevant behavior | SHA256 |
| --- | --- | --- |
| [vault.ts](https://github.com/supabase/cli/blob/753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4/apps/cli/src/command-internal/vault.ts#L34) | Empty resolved secrets return before database calls | 343dfa475e3ced6007f7e349af55d7ff50b939f71c0ace9f99b827ec7be3c1c3 |
| [migrate-and-seed.ts](https://github.com/supabase/cli/blob/753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4/apps/cli/src/command-internal/migrate-and-seed.ts#L62) | Disabled, nonexperimental migration path skips execution | 55538d83a0e956e9ec158fdbcaa7f7844798031903475e799e508836435da9e7 |
| [seed.ts](https://github.com/supabase/cli/blob/753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4/apps/cli/src/command-internal/seed.ts#L71) | Disabled seed returns before filesystem/history SQL | 0519501a6af36ea62042f0cc8f67e7d0b62a2d0471204d44d9faac13142fcecb |
| [db-setup.ts](https://github.com/supabase/cli/blob/753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4/apps/cli/src/command-internal/db-setup.ts) | Empty Vault, absent roles; branch marker main, no newline, requested mode0644 | d82ed106aa3bea8613e639175d20a05eb27fdad49762bf8637217d6d0d50fca4 |
| [start-database.ts](https://github.com/supabase/cli/blob/753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4/apps/cli/src/command-internal/start-database.ts) | Branch initialization follows fresh setup | ba8b82b45ce6f84654d3a9128c0695b033caaf2d0dce4e742161bba7dbb24519 |

Local snapshots/URL/hash manifest are retained in
platform/deployment/.local/post-auth-setup-tail/primary-source/. All five hashes
were independently rechecked. They are implementation evidence, not runtime inputs.
The existing retained owner performs this selected tail; upstream existing-marker
preservation does not authorize this owner to adopt an unproven preexisting artifact.

## Requirement-to-test evidence

Acceptance RED precedes implementation: the existing process fixture's new selected
control raises startup/unknown_control (one test, 0.151s). Its first GREEN passes
one test, 30.778s before final identity/replay refinements. The child final owner
matrix passes eight tests, 9.420s; final unchanged serial process selection passes
two tests, 61.275s, covering positive and preexisting/replaced artifact cases.
These results are not added to root totals as distinct cases.

| Matrix row | Named verification |
| --- | --- |
| Selected success | PostAuthSetupTailOwner.test_selected_tail_exact_bytes_no_sql_and_fact_only_after_cleanup; ExecutionSupervisor.test_post_auth_setup_tail_process_exact_artifact_and_cleanup; test_startup_adapter.StartupAcceptance.test_post_auth_tail_public_inventory_and_real_qualify_mapping |
| Missing/order/replay | PostAuthSetupTailOwner.test_missing_prerequisites_phase_and_terminal_finish_never_mutate; test_missing_tail_completion_blocks_terminal_finish_and_replay |
| Contamination | PostAuthSetupTailOwner.test_preexisting_config_roles_and_branch_contamination_not_adopted; test_changed_replaced_unsafe_or_extra_artifacts_block_custody_and_cleanup; test_artifact_owner_mismatch_refuses_custody; test_final_cleanup_observation_cannot_publish_changed_artifact; ExecutionSupervisor.test_post_auth_setup_tail_process_preexisting_or_replaced_artifact_preserves_uncertain_resources |
| Budget/cancellation | PostAuthSetupTailOwner.test_deadline_and_interrupted_write_consume_attempt_without_retry; ExecutionSupervisor.test_post_auth_setup_tail_process_expiry_and_interruption_during_artifact_creation |
| Ordinary controls | Existing ApiDefaultPrivilegesOwner matrix; ExecutionSupervisor.test_api_default_privileges_process_order_and_verified_cleanup; test_cli_db_backend_process_order_and_same_pg_disposal; test_auth_catalog_process_order_and_same_pg_disposal |

The process oracle uses a real private Unix peer and disposable child processes,
not an actual Docker daemon. It independently checks existing SQL sequence, original
CLI termination, exact marker before cleanup, no early fact and normal disposal.
Tampering cases must reach verified default privileges before refusing; earlier
unrelated refusal is not accepted as passing negative proof. Owner tests additionally
check unchanged SQL mode list, original deadline, strict ordinary inventory and
absence of mutation/replay after failed prerequisites or an interrupted write.

Retained child commands (from repository root):

```sh
python3 -m unittest discover -s platform/deployment/tests -p test_resources.py -k test_post_auth_setup_tail_process_exact_artifact_and_cleanup
python3 -m unittest discover -s platform/deployment/tests -p test_pinned_execution.py -k PostAuthSetupTailOwner
python3 -m unittest discover -s platform/deployment/tests -p test_resources.py -k test_post_auth_setup_tail_process
```

An earlier two-test process attempt fails in acquisition/before the tail: positive
hits docker_timeout and replaced-artifact case never reaches verified defaults.
Source/unit work overlaps that attempt, so no stable single-source binding exists;
load or change contribution is unconfirmed. Initial failure and unchanged serial
repeat are both retained. No assertion/deadline was changed, and the later pass
does not explain the first failure.

Local evidence directory: platform/deployment/.local/post-auth-setup-tail/.
child-verification.txt records exact commands/chronology; acceptance-red.log,
acceptance-green.log, owner-matrix.log, process-tail-initial-failure.log and
process-tail.log retain output. child-source-sha256.txt binds final child source.
Root verification has separate source-bindings.json, exact-ID verification-plan.json
and verify-NN.log/result files. No runtime receipt is fabricated from test results.

## Pre-review root affected verification

Root inspected the entire scoped diff and audited all tasks and five matrix rows.
Before review patches, on 74 frozen source/test bindings, all 274 distinct selected cases pass with no skips:

| Selection | Result | Elapsed |
| --- | --- | --- |
| test_pinned_execution | 166 PASS | 19.350s |
| test_startup_adapter | 40 PASS | 10.314s |
| test_startup_lifecycle | 19 PASS | 65.225s |
| test_resources.Resources | 44 PASS | 226.786s |
| Selected process cases below | 5 PASS | 105.032s |

Exact direct commands, independent of the ignored local runner:

```sh
PYTHONPATH=platform/deployment/tests python3 -m unittest -v test_pinned_execution
PYTHONPATH=platform/deployment/tests python3 -m unittest -v test_startup_adapter
PYTHONPATH=platform/deployment/tests python3 -m unittest -v test_startup_lifecycle
PYTHONPATH=platform/deployment/tests python3 -m unittest -v test_resources.Resources
PYTHONPATH=platform/deployment/tests python3 -m unittest -v test_resources.ExecutionSupervisor.test_post_auth_setup_tail_process_exact_artifact_and_cleanup test_resources.ExecutionSupervisor.test_post_auth_setup_tail_process_preexisting_or_replaced_artifact_preserves_uncertain_resources test_resources.ExecutionSupervisor.test_api_default_privileges_process_order_and_verified_cleanup test_resources.ExecutionSupervisor.test_cli_db_backend_process_order_and_same_pg_disposal test_resources.ExecutionSupervisor.test_auth_catalog_process_order_and_same_pg_disposal
```

Local root orchestration is `python3 platform/deployment/.local/post-auth-setup-tail/verify.py N`,
N=0..4. verification-summary.json independently validates exact verbose passing IDs,
log hashes and all source bindings. All39 preserved historical prerequisite hashes
match their prior manifests; current source does not relabel those old runtime
receipts as fresh proof. No full deployment-suite or actual-Docker run is claimed.

## Authority and remaining gates

Only isolated synthetic unit/process fixtures are used in this increment. Existing
source/config/resource checks, deadlines, consumed attempts and terminal finish are
binding. The new owner fact is separate from fresh_setup_completed/runtime_ready.
No SQL allowlist expansion, arbitrary user SQL, migrations/seeds/Vault writes,
reconnect/replay, recovery deletion or resumed CLI authority is introduced.

Prior actual-Docker/full-suite receipts remain historical source-bound evidence.
Changed source requires fresh prerequisites before future actual qualification.
All existing receipts/state and uncertain Docker resources are retained unchanged.
No actual Docker is contacted here. TS7.0.2 and local mail15484 remain selected.

## Impact decisions

- Scaffold: existing ENV owner/startup/qualification tooling only; no generator,
  schema/client owner transfer or new runtime service.
- Shared UI: no UI/browser change.
- Agent context: existing custody/privacy instructions suffice; no edit.
- Documentation: this evidence, existing DEVELOPMENT runbook and KDG handoff/memlog.
- ADR: existing ownership, release safety and diagnostic/privacy decisions apply;
  no accepted ADR edit or new architecture decision.

Full setup/CLI continuation, running Auth/API stack, public lifecycle, consuming
ENV/P1/SERVICE scaffold acceptance and provider/device qualification remain open.
Identity/Access/WRITE and server-backed KDG remain gated. No Leave, production,
account/access, provisioning, deployment/push or real-data pilot use follows.


## Review and verification limits

Three review layers completed (9 blind,1 edge,1 verified gap). Root reproduced two
identity-binding windows; the original implementation agent corrected pinned
publication/parent custody, filesystem error/process cancellation coverage and real
public dispatch acceptance. Root additionally reproduced a tmp-path staging escape;
all staging mutation/publication now uses retained directory descriptors, with
deterministic no-foreign-creation tests. Findings are individually triaged in the Build record.
Two unverified medium investigations are appended to deferred work: the initial
pre-tail timing failures and hard filesystem blocking. Local filesystem budgets are
checked around operations; no hard preemption of a blocked filesystem syscall is
qualified. No safety assertion or budget is relaxed.


## Final patch audit and bindings

Review race RED retains two failures before the publication/parent fix. The later
tmp-substitution RED retains two failing subcases before the descriptor-only staging
fix. Final focused owner coverage is14 passing tests, including empty/nonempty
no-replace publication races, mutation/publication tmp swaps, six filesystem EIO
boundaries and public-process expiry/cancellation. The public routing adapter checks
both inventories through real startup.qualify and rejects daemon override options.
The process positive also enters qualify_startup.main through the real adapter into
the private peer. Source is frozen for separate final root verification in final/.

A temporary fault-injector setup error wrapped custody reads as well as marker
writes; review-test-injection-failure.txt retains its excerpt/provenance and the full
original remains in the tool transcript. It is not acceptance RED. The corrected
injector targets marker wb only. Initial valid race/timing logs remain separate.

The following committed hashes identify the reviewed implementation/test surfaces.
Complete source and exact-ID manifest digests follow after final verification. The
four complete-module/class selectors and explicit process IDs above reproduce the
selection from this document's containing Git tree without ignored runner inputs.

| File under platform/deployment | Final SHA256 |
| --- | --- |
| resources.py | 6660a682039fb1f3046e7cdedd22d4a6e24b1cbdcee2d51b4dbebab3695906c5 |
| startup.py | 34fbb468eaf57ab50fbc507bf7608d42648eb384664e4e449741785958cb8625 |
| tests/qualify_startup.py | 87d83fe758f8afc618fa6bd9e99b773b79cc5e7a56e3b365e3d6a4770bb00a60 |
| tests/test_pinned_execution.py | 7d72452e43a90f4c6e8fb1c3e075868a00115a514b4145103e4aac58b4010e30 |
| tests/test_resources.py | a44344ef4ea6309c3db860d2854c604e78cc25c35ab14e63a65db699aa98d9e9 |
| tests/test_startup_adapter.py | 01d5a6523136b21cc6e330c71370dad47a1108d11e284fc557b70d384733c722 |


Final selectors use the same first four complete module/class commands above.
The final process group additionally includes artifact expiry/interruption:

```sh
PYTHONPATH=platform/deployment/tests python3 -m unittest -v test_resources.ExecutionSupervisor.test_post_auth_setup_tail_process_exact_artifact_and_cleanup test_resources.ExecutionSupervisor.test_post_auth_setup_tail_process_preexisting_or_replaced_artifact_preserves_uncertain_resources test_resources.ExecutionSupervisor.test_post_auth_setup_tail_process_expiry_and_interruption_during_artifact_creation test_resources.ExecutionSupervisor.test_api_default_privileges_process_order_and_verified_cleanup test_resources.ExecutionSupervisor.test_cli_db_backend_process_order_and_same_pg_disposal test_resources.ExecutionSupervisor.test_auth_catalog_process_order_and_same_pg_disposal
```

pre-review-scoped.diff retains the original review artifact; final root logs and
bindings are separate from all earlier proof. Linux directory publication uses
RENAME_NOREPLACE and fails closed if unavailable; no overwrite fallback is used.


## Final acceptance

All282 distinct selected cases PASS on the final reviewed/patched source, no skips:

| Final selection | Result / elapsed |
| --- | --- |
| test_pinned_execution | 172 PASS / 17.575s |
| test_startup_adapter | 41 PASS / 6.641s |
| test_startup_lifecycle | 19 PASS / 46.957s |
| test_resources.Resources | 44 PASS / 171.164s |
| Six final process cases above | 6 PASS / 128.961s |

Root verifies every executed ID and log hash, all74 frozen source/test bindings,
and all39 prior prerequisite files unchanged. Frozen intent matches the original
review artifact. All17 concurrent files and the original empty index are preserved
exactly. No actual Docker operation or fresh runtime/full-suite qualification occurs.
The initial274-test run remains pre-review evidence, separate from final/.

Three review layers complete: all11 filed findings are individually triaged, with
two root verification/audit observations additionally recorded. Race, error-boundary,
public routing and evidence corrections are verified, including the additional tmp
path escape. Two negligible private-fixture concerns are rejected with evidence;
two unverified medium investigations remain deferred as described above. No budget,
assertion or expected result is weakened. Existing receipts/uncertain resources,
TypeScript7.0.2 and mail15484 stay unchanged. Enclosing ENV/scaffold/dependent gates
remain open; only a scoped local commit follows, never a push.

Committed artifact digests (files relative to local evidence directory):

| Artifact | SHA256 |
| --- | --- |
| final/source-bindings.json | 9254183ecdb3e10b22226f211f28f137f6a3b700e03339658b41b118ac80f8b9 |
| final/verification-plan.json | 07719a25275fcc7f41f416fac5762e818941d356ec11e6d7fce0662e82ddae9f |
| final/verification-summary.json | a90fa859750d3dd495de43cd1caf6cbaf3d609dcfcb23393a04757a99b967ec7 |
| pre-review-scoped.diff | 1aaa2d0bd184b2f2e19116c1c99eed51f265204e3d3cbbd8c94b2284e6271843 |
