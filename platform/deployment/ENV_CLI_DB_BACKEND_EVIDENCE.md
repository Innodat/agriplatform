# CLI database backend lifetime evidence

Build: [ENV backend lifetime](../../_bmad-output/implementation-artifacts/spec-env-cli-db-backend-lifetime.md).
Status: bounded Build done; runtime_ready=false. Final acceptance below supersedes historical in-progress checkpoints.

## Authority and scope

The retained publisher CLI commit753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4
source db-setup.ts/runFreshDbSetup/connectLocalPostgres opens the host-facing
postgres/postgres session before the Auth job. The new literal qualifier observes
external backend presence before the existing CLI kill/reap and departure afterward,
then the unchanged Auth catalog/job and same-PG normal cleanup. No success ACK or
later setup SQL. This is backend presence/lifetime evidence, not exact OS-process
attribution, password-method proof or continuing session identity.

PostgreSQL17 [statistics documentation](https://www.postgresql.org/docs/17/monitoring-stats.html)
provides transaction-scoped activity snapshot semantics and pg_stat_clear_snapshot.
Departure polling refreshes the observer snapshot within its3s limit and the existing
statement/operation bounds; it does not reset statistics or mutate business state.

## Requirement-to-test matrix

| Requirement | Required proof |
| --- | --- |
| AC1 lifetime and order | Live CLI→presence→single group kill/reap→departure→catalog/job→same-PG normal cleanup; actual source-qualified control |
| AC2 exact SQL semantics | One complete external client set; role/database/state/port, observer/worker/socket/loopback exclusion, missing/duplicate/NULL refusal and bounded refreshed departure |
| AC3 custody and one-shot | Changed PG/image/fixture/resources, consumed attempts/IDs and early-phase/job/finish gates |
| AC4 uncertainty and limits | Lost/malformed create/start/inspect, state/config contradictions, interruption/deadline, no replay |
| AC5 compatibility | Eight prior controls, public up expected refusal, full deployment discovery |

## Impact decisions

Scaffold: extend existing lifecycle/transport/resource/startup/test owners only; no
new runner, PostgreSQL client/proxy, generator or generic service. Shared UI unchanged.
Agent context: existing rules suffice. Documentation: source profile, this evidence,
runbook, Build and KDG handoff/memlog. Accepted ADRs unchanged/no new decision.
ADR0020 owner-controlled releases/migrations remain gated; ADR0023 excludes backend
rows/query text/payloads/credentials/logs from diagnostics. Existing account/access,
production/pilot, dependent Identity/Access/WRITE/server KDG and Leave/editor exclusions
remain. Concurrent documents/index and retained diagnostics/resources are preserved.

## Results

Child acceptance observes AttributeError for missing FreshGuard.cli_db_backend_sql
before production edits. Root extends the existing ExecutionSupervisor process peer
for positive/refused predicates and an omitted-termination mutation oracle. Existing
private verifier adds backend and test-only backend-negative literal modes; prior modes are retained.


Root initial125 no-socket tests PASS2.638s and3 real private-socket/process cases
PASS34.926s after visibility guard (preceding process run40.402s also passed).
The ordering oracle requires both synthetic CLI/descendant PIDs alive before presence,
both stopped after exactly one group signal before departure/catalog/job, same execution
deadline and no job on either predicate failure. It detects omitted kill/reap despite
modeled daemon success. No actual PostgreSQL semantic claim comes from these fixtures.

Visibility follow-up observes focused RED before guard, then GREEN: pg_stat_activity
can hide other users' columns, so counting filtered rows alone is insufficient. Both
predicates require pg_read_all_stats privileges first, without creating/granting them.
Root adds real SQL semantic verification through a closed internal test fixture: only
fixed typed activity rows/observer-role input vary, production predicate remains intact.
The fixture is read-only, returns no rows and accepts only expected P0001 rejection.


Expanded no-socket coverage adds36 backend-specific custody permutations, both-mode
running/Pid0 startup→running/positivePid→completed transitions, completed-Pid0 refusal
and operation deadline expiry. The closed read-only SQL fixture includes20 presence
and4 departure cases; one departure case executes the actual3s refusal loop. It also
uses existing anon as a role-input datum to require visibility refusal, without SET
ROLE, account creation or grant changes. Root detects the first present fixture's
17095-character SQL would exceed the existing16384-byte transport request limit,
before any actual operation; representation is factored without removing cases or
changing the production DO predicate/limits. Results after correction follow.


## Initial source-qualified actual run

Run `85833e8b-0ca9-4f19-9f0d-3b8857d526f7`: prepare0.138s,
toolchain31.558s and immutable images42.501s PASS. Image receipt SHA256
`483264eb2cbf88fc09222087508457b3d6a577aba090389cea3abcbf8636062b`.
Actual backend control PASS110.612s; record SHA256
`3e4bf52c20710876a47097b9ec3a111ff583466cc7953790bc72f288c2c768b9`.
Both independent backend facts, prior catalog/job/exit/disposal and normal PG
shutdown/cleanup verified. All13 receipts/config files and running Docker inventory
unchanged. Observer's existing statistics visibility is sufficient; no privileges
are granted. Setup/runtime remain false. Root129 owner tests PASS6.799s.

The fixture transport RED is corrected by storing the unchanged DO once and varying
only fixed typed activity relation/observer-role data. Full requests7321/3481bytes fit
the unchanged16384-byte bound. Primary pinned CLI source files re-used as authority:
db-setup.ts SHA256d82ed106aa3bea8613e639175d20a05eb27fdad49762bf8637217d6d0d50fca4,
internal-db-connection.ts SHA256cd7cdee734eee02b45b64ad3ad3318ae795e917203f0fe0efe390888aeb73fea,
start-database.ts SHA256ba8b82b45ce6f84654d3a9128c0695b033caaf2d0dce4e742161bba7dbb24519.
These initial results precede the deadline correction below and are historical;
corrected-source results are recorded separately.


## Actual control results and recorded commands

Commands run serially from repository root using the existing private verifier:

```sh
python3 -m unittest discover -s platform/deployment/tests -p test_pinned_execution.py
python3 -m unittest discover -s platform/deployment/tests -p test_resources.py -k cli_db_backend
python3 platform/deployment/.local/pinned-cli-execution-qualification/verify-local.py prereqs-diagnostic 85833e8b-0ca9-4f19-9f0d-3b8857d526f7
for mode in backend backend-negative catalog auth-job poststart initialized persistence proof bootstrap controls; do
  python3 platform/deployment/.local/pinned-cli-execution-qualification/verify-local.py "$mode" 85833e8b-0ca9-4f19-9f0d-3b8857d526f7 || exit $?
done
python3 platform/deployment/.local/pinned-cli-execution-qualification/verify-local.py up 85833e8b-0ca9-4f19-9f0d-3b8857d526f7
python3 platform/deployment/.local/pinned-cli-execution-qualification/verify-local.py tests 85833e8b-0ca9-4f19-9f0d-3b8857d526f7
```

The recorded UUID is 85833e8b-0ca9-4f19-9f0d-3b8857d526f7. Future source/profile changes require a fresh UUID and
prepare/toolchain/image qualification; never repair old receipts. The up command is
checked separately for expected exit2. Full discovery uses the retained diagnostic
runner with unchanged assertions and900s wrapper bound, SHA256
4e60dc7e805ccb3fc02045eb33c697dca0f3f557244dc8c2ce5617b234f54ea5.

| Mode | PASS / seconds | Record SHA256 | Running inventory unchanged |
| --- | --- | --- | --- |
| backend | 110.612 | `3e4bf52c20710876a47097b9ec3a111ff583466cc7953790bc72f288c2c768b9` | true |
| backend-negative | 100.381 | `332cf112dd728e584cd338b507678f1f39d479b1e352051f8cb21d5d3b243a12` | true |
| catalog | 93.439 | `c031d7dd384f35ac07b74907f891686e5fcebbe543df021da91d780290744f8e` | true |
| auth-job | 84.76 | `42b4bd2a2c7bb5da724bf255888af60aed238fa9c52efbba26071c1124638bf9` | true |
| poststart | 81.79 | `92f4ae8ba9e8ce4b79718708449388098156e85bce4d9a1442af6ca6125dd68e` | true |
| initialized | 100.717 | `0f80556f0c2cdb007873b6fbc15e97fba4fc5f22fa5d073643244f5dcc268493` | true |
| persistence | 101.449 | `0b8e2a8d56820b99cfe841034876b915d686df4fab7104c189fbb4f13d50a1d3` | false |
| proof | 75.109 | `836ebc78d3c1cd0c64907c44f6dcaea314df9f438fb95525cc12d0cdb1275437` | true |
| bootstrap | 38.415 | `bea38033f694f00437e29a2cd8c5e30548e8ad9a087390b493426ad7ec8f5318` | true |
| controls | 87.068 | `b98e299c88618edb0e194ef8a6cf90d2862f96c043deeec3f1305c99e9d06d3e` | false |

All ten controls preserve13 receipt/config files. Persistence/guarded inventory
changes are unrelated Deals resources, retained in the private delta record; their
initiator/cause is not established and ENV does not interfere. Other eight inventory
snapshots are unchanged. Both actual backend facts and24 fixed-input SQL cases pass
with same-PG catalog/job/normal cleanup. Public up expected2 in0.075s; runtime false.

## Exact acceptance coverage

Module tests/test_pinned_execution.py, class CliDbBackendExecutionMatrix:

- AC1: test_presence_departure_catalog_job_and_cleanup; root process module
  test_resources.ExecutionSupervisor.test_cli_db_backend_process_order_and_same_pg_disposal
  and test_cli_db_backend_process_oracle_detects_skipped_cli_termination; actual backend.
- AC2: test_closed_predicates_and_exact_transport_allowlist,
  test_observer_visibility_is_required_before_either_external_count,
  test_internal_semantic_fixture_preserves_predicates_and_is_not_public_exec,
  test_semantic_fixture_fits_existing_encoded_docker_request_limit,
  test_departure_checks_deadline_after_zero_observation_before_exit and
  test_late_zero_fixture_preserves_original_predicate_and_transport_bound;25 actual SQL cases.
- AC3: test_required_phase_job_input_live_cli_and_termination_gates,
  test_backend_current_custody_surrounds_each_exchange (36 combinations),
  test_live_cli_rechecked_after_successful_exec_exit.
- AC4: test_custody_and_exec_faults_never_replay_or_claim_observation,
  test_backend_running_transitions_completed_zero_pid_and_deadline,
  test_predicate_failures_consume_attempt_and_block_job_catalog_finish; root
  test_cli_db_backend_process_predicate_failures_block_job and
  test_cli_db_backend_wrapper_alarm_stops_cli_without_continuation; no-socket
  test_generated_wrapper_alarm_raises_caught_timeout_and_stops_held_parent.
- AC5: eight prior control records, expected public refusal above and full
  deployment discovery. All named focused tests ran as part of132-owner/4-process passes.

Root checks25 proof-source hashes plus owned test hashes, approved frozen intent and
concurrent six files/index. Shared scaffold/UI/context/docs/ADR decisions are above;
no new lifecycle or ownership transfer. Prior investigations remain open and
original failed receipts/diagnostics/resources are preserved. Full discovery and
independent three-layer review remain before acceptance/commit.


## Deadline boundary correction

Root self-audit finds the departure loop checks count-zero before its3s deadline,
so a delayed zero observation can qualify late (within the outer5s statement bound).
The implementation child independently verifies the reachable branch without edits.
This violates the frozen wait bound; no intent or limit change is proposed.

The pre-correction full regression was intentionally interrupted with SIGINT sent only to the
pidfd-held, exact-path/hash/parent-verified owned diagnostic runner912133. Its parent
records exit -2 after270.758s, tests count unavailable, passed=false. Retained log SHA256
9a6a95b133e346104d6ab6745a548cff8428173441141863d2a57ab234017dc1;
record SHA25643c0a4c173d285200537c4f3a85a44bb74546cf8dc97ef3f4f9c68e75bcc063d.
This is an intentional stop against known-unfixed source, not a full test pass or
unexplained flake. No source edits occur during that run. Earlier control passes remain
historical evidence. A separate read-only3.05s delayed-zero regression runs against
unchanged qualified source before the fix; it fits the existing5s statement limit.


Actual delayed-zero RED37.522s, record SHA256
67995f8696ec1cb18e2eaf808d5e4723c9c26283c7a99a7520539fe5031046c4.
Phase-selected repeat RED41.481s confirms presence_verified_before_late_probe=true
and late_probe_reached_departure=true; record SHA256
b51631bf11aede02c780673affad32309c82b3fa2ab66e13176180f97f9b4e80.
Both refuse execution_sql_failed because the semantic fixture rejects unexpected late
acceptance; owned cleanup true/ownership_lost false and13 receipts unchanged. First
running inventory unchanged; repeat records only unrelated Deals changes (private delta
record). Neither is a qualified lifetime pass. Minimal post-count/pre-EXIT deadline
correction and its tracked separate fixed-input regression follow before fresh complete
source qualification. Frozen policy and timeouts remain unchanged.


## Corrected-source deadline GREEN and Docker timeout

After focused deadline RED/GREEN, root131 owner tests PASS3.242s and3 process tests
PASS39.554s. Fresh `ecc22e64-cb28-49c6-8b8a-9158fe94da41` prepares0.057s,
toolchain16.638s and images38.708s pass. Actual delayed-zero regression GREEN133.410s,
record SHA256a067f266278d045ac444a7fc738099e2b64ca9707b1555506c7aa59751aa6fd9:
late rejection, catalog/job and normal cleanup verified;13 receipts/running inventory
unchanged. Command elapsed includes prerequisite revalidation; execution120s/SQL5s
and inner departure3s limits are unchanged. The separate tracked regression request
is2007bytes and preserves the original DO except fixed input relation.

The following ordinary backend control refuses docker_timeout31.748s, record SHA256
f3f54b9e5a3d12cfe4b8f6f8de84301aed20d7b3ccad24005ae0a8dbfe973c8a.
All13 receipts and running inventory unchanged; this does not qualify the control.
Read-only inspection finds no run-named PG container or volume container references,
but retains the named volume and empty bridge39d98fe06a6e9851da4cd5f7bf261b2403390f0e15f097f0f3cefbfe00b10fc6.
Safe metadata is retained in .local/cli-db-session-qualification/timeout-resource-state.json.
Their current labels are not recovery/removal/adoption authority; both are preserved.
The original timed exchange/cause was not captured. No timeout increase or assertion
change. A fresh source-identical UUID d3a7cd57-607c-45bf-ab4d-cbe9a0b64a09 is qualified
for transparent safe method/category/elapsed/status observation; no request/response
bodies, Docker logs or credentials are recorded. Earlier failures are never repaired
or explained merely by a later passing run.


## Corrected-source control continuation

Fresh `d3a7cd57-607c-45bf-ab4d-cbe9a0b64a09`: prepare0.074s, toolchain43.459s,
images56.500s PASS. Image receipt SHA256
`4f151325da79db3f6acfe1675947cfc71d9a2e6d1955bf9b548371113059e3c2`.
Source identical to the corrected delayed-zero GREEN above.

| Mode | PASS / seconds | Record SHA256 | Running inventory unchanged |
| --- | --- | --- | --- |
| backend-diagnostic | 74.968 | `8334296d18705db86baad775892ab1f444deb50245f1efcff27587c0aede6762` | true |
| backend-negative | 104.179 | `96892cfa197b0d3b930e0aa1119e32a25c1b38ab793f89c02ae602b38e876ac5` | true |
| catalog | 71.607 | `f0d9cc8e288a3fc6c3aea4d621fb97408d2b0e8f6e28077711dec9e7f85600f2` | true |
| auth-job | 103.124 | `1f0417215c64a8c982fa621d7e17ac26f9d2dbbc60eac30678995176056a4e23` | false |
| poststart | 68.288 | `73f030a7d7d6b063111709667cf7394e91bce3a05e1df4b15f57df6a8f06e730` | true |

All five preserve13 receipt/config files. Backend-diagnostic runs the original closed
qualifier with transparent safe method/category/elapsed/status observation;1056
exchanges, no errors, guard cleaned/phase7 and ownership_lost=false. Slowest exchange
0.489898s. This passing run does not explain the preceding uncaptured timeout.
Backend-negative proves24 fixed-input SQL cases; together with the source-identical
separate delayed-zero GREEN, all25 SQL semantic cases pass. Auth-job inventory delta
contains unrelated resources and is retained without interference.

After the tool session ended, initialized.json was found empty and its process no
longer running. That control has no usable result and is not counted as PASS. Exact
run-named container, volume and bridge are absent on read-only inspection; resources.json
retains this observation. The empty record is preserved. Remaining controls require a
fresh qualified UUID rather than replacing the incomplete record. Full deployment
regression runs against unchanged corrected source using the same diagnostic runner.
Concurrent epics/Leave implementation-plan/handoff documents advanced independently;
the new preservation checkpoint retains those bytes and the original unchanged index.


Corrected-source commands (each mode separately, serially):

```sh
python3 -m unittest discover -s platform/deployment/tests -p test_pinned_execution.py
python3 -m unittest discover -s platform/deployment/tests -p test_resources.py -k cli_db_backend
python3 platform/deployment/.local/pinned-cli-execution-qualification/verify-local.py prereqs-diagnostic ecc22e64-cb28-49c6-8b8a-9158fe94da41
python3 platform/deployment/.local/pinned-cli-execution-qualification/verify-local.py backend-late ecc22e64-cb28-49c6-8b8a-9158fe94da41
python3 platform/deployment/.local/pinned-cli-execution-qualification/verify-local.py backend ecc22e64-cb28-49c6-8b8a-9158fe94da41
python3 platform/deployment/.local/pinned-cli-execution-qualification/verify-local.py prereqs-diagnostic d3a7cd57-607c-45bf-ab4d-cbe9a0b64a09
python3 platform/deployment/.local/pinned-cli-execution-qualification/verify-local.py backend-diagnostic d3a7cd57-607c-45bf-ab4d-cbe9a0b64a09
for mode in backend-negative catalog auth-job poststart initialized persistence proof bootstrap controls; do
  python3 platform/deployment/.local/pinned-cli-execution-qualification/verify-local.py "$mode" d3a7cd57-607c-45bf-ab4d-cbe9a0b64a09 || exit $?
done
python3 platform/deployment/.local/pinned-cli-execution-qualification/verify-local.py resources d3a7cd57-607c-45bf-ab4d-cbe9a0b64a09
python3 platform/deployment/.local/pinned-cli-execution-qualification/verify-local.py tests d3a7cd57-607c-45bf-ab4d-cbe9a0b64a09
```

The ecc ordinary backend command refuses as recorded above. The d3 serial loop has
complete results only through poststart; later modes are not claimed from that loop.
The full-suite invocation shown last is the corrected-source regression.


## Corrected-source full regression failure retained

D3 full discovery runs all626 tests846.217s, one failure/no skips; wrapper846.422s,
exit1/passed=false. Log SHA256
`67be2148851167c7e27d9357c69cc0771352073160bf10473985f81c6473a8ba`;
record SHA256`f6780af1431de1bf06a7bb86e6082d070273d789ac1c618e5cd12efc646c2ce4`.
ExecutionSupervisor.test_cli_db_backend_process_order_and_same_pg_disposal fails at
forbidden_after_start marker assertion. Original traceback first shows
workdir_contaminated inside present inspect_exec post-GET custody, before CLI kill/
departure/job, then execution_cleanup_unresolved during preservation, then the marker
assertion. This is not a regression pass and is not dismissed by prior focused passes.
Root investigates exact process boundary with safe numeric wrapper returncode/timing
observations, preserving the fixture5s and all production/assertion limits. No source
change occurs during the full run. Review/acceptance remains pending.


Root's unchanged exact positive diagnostic passes; a separate6s presence-delay
injection reproduces helper returncode -14 after5.046321s, forbidden continuation,
workdir_contaminated and custody loss/no job. Only numeric returncodes/timing and
selected guard facts are retained in .local/cli-db-session-qualification/
process-failure-diagnostic.json. This establishes a reachable default-SIGALRM bypass,
not the unrecorded original full-run trigger. The generated helper arms its5s alarm
before imports; default termination bypasses fixture_main's verified-parent pidfd
protection. Root adds tracked test_cli_db_backend_wrapper_alarm_stops_cli_without_continuation
before fixing it: RED1test8.435s, forbidden marker with cleanup refusal. Fix routes
alarm through caught TimeoutError, retaining the exact5s bound. Fresh source
qualification and full regression are required afterward; prior passes are historical.


Alarm fix focused GREEN: child132 no-socket tests2.848s, root independent132tests
2.679s; root4 private-socket/process tests48.452s. The tracked6s-delay case now
requires stopped CLI/descendant, invalid_owner_handoff, no marker/job/catalog, no
custody loss and same-PG cleanup. Both generated docker/podman handlers are tested
for TimeoutError, registration before unchanged alarm5, one verified-parent SIGKILL
and pidfd closure. Only startup.install_fixture and source profile change in the25
proof-source checkpoint; owned tests change separately. Fresh source-qualified run
`45e7c3ea-497e-4d1c-aca6-8959dae94935` follows; earlier source controls are historical.
The original full-run exact trigger remains unobserved; the controlled alarm path is
reproduced RED then fixed GREEN without changing expectations or timeouts.


## Alarm-corrected source qualification

Fresh `45e7c3ea-497e-4d1c-aca6-8959dae94935`: prepare0.055s, toolchain18.646s,
images33.583s PASS. Image receipt SHA256
`265a1a497d787c0a0b4c2f55510cd2cb4bf63bd24d3b28852703ff245471e0a4`.
Plain backend control (without diagnostic observer) PASS76.198s, record SHA256
`ad9ea034d03061dafdbed5ca5491eb083d439747f2c6450ebdda3345cdc9589e`.
Both backend facts, same-PG catalog/job/exit/disposal and normal shutdown/cleanup pass;
all13 receipts and running inventory unchanged. Setup/runtime false. SQL semantic
and eight prior controls run serially before full regression/review.


Latest source actual-control results:

| Mode | PASS / seconds | Record SHA256 |
| --- | --- | --- |
| backend | 76.198 | `ad9ea034d03061dafdbed5ca5491eb083d439747f2c6450ebdda3345cdc9589e` |
| backend-late | 82.519 | `858e0f9c6fe92cb0a96c2c2b664499df7daff913b6bf1a60db90686c2e9789b4` |
| backend-negative | 74.134 | `9479ab38ab7fd17d0a4d6fd188b450dc9d33cd1cab6b3463767f07e35652b50e` |
| catalog | 69.423 | `2c7029bf0fe11c7b02c6bbcee3aa01bf3798a063d9ecaf03203bd433bf0b6e2f` |
| auth-job | 64.829 | `5919c29a90d10a16cbcccb00a3831bd45c577d0a31b945f7c53abd74d55a0684` |
| poststart | 67.45 | `9bac056b197e50ec9c5feb26b834a7de9f946e42c0eed48ebf0ab18631c85884` |
| initialized | 88.405 | `5bb463cd5255cfc5c468452315c49808e1c23e93d1397fc648d6b3f968930451` |
| persistence | 86.484 | `181bcb9c1e0bd98d7fa2b848fce1673e7ef733ecadc9e69c27a863c3b0e3c497` |
| proof | 68.238 | `18004fc7733e500770f4ffa4723540520ac61a32c80b8531e546899504c0c841` |
| bootstrap | 31.566 | `4a364df49b47d02efdfe24c1e184e4d8872ce5f65fdf6a3969d37fd485f0357e` |
| controls | 69.748 | `e61441235d43c667b7a36e8d709638598cb1e6966f3f90e2df652d3b90436659` |

All eleven preserve13 receipts/config files and running Docker inventory. The new
three controls prove normal backend lifetime plus all25 SQL semantic cases; eight
prior controls retain their original behavior. Public up expected exit2 in0.053s,
runtime_adapter_unqualified/runtime_ready=false. Full regression is running with the
same unchanged assertions/discovery/900s runner; no pass is claimed until completion.

```sh
python3 platform/deployment/.local/pinned-cli-execution-qualification/verify-local.py prereqs-diagnostic 45e7c3ea-497e-4d1c-aca6-8959dae94935
for mode in backend backend-late backend-negative catalog auth-job poststart initialized persistence proof bootstrap controls; do
  python3 platform/deployment/.local/pinned-cli-execution-qualification/verify-local.py "$mode" 45e7c3ea-497e-4d1c-aca6-8959dae94935 || exit $?
done
python3 platform/deployment/.local/pinned-cli-execution-qualification/verify-local.py up 45e7c3ea-497e-4d1c-aca6-8959dae94935
python3 platform/deployment/.local/pinned-cli-execution-qualification/verify-local.py tests 45e7c3ea-497e-4d1c-aca6-8959dae94935
```

The up command is checked separately for expected exit2. All25 proof-source hashes,
seven owned code/test hashes and the separately retained target hash still match the
alarm-source/test/target checkpoints. Approved frozen intent and concurrent files/index
remain protected. Earlier failed receipts and preserved resources are not altered.


Exact alarm characterization command before the fix:

```sh
python3 -m unittest discover -s platform/deployment/tests -p test_resources.py -k cli_db_backend_wrapper_alarm
```

RED1test8.435s precedes the source fix. The safe controlled diagnostic record SHA256
is `73c0d879b6aa61739e32ae1e9fb48c1ea5b5c792b45de91c855663dd0bf1fecf`.
Root's post-fix full focused module/keyword commands above run132 no-socket and4
process cases, all PASS; the broader source-frozen suite remains separately recorded.


## Latest full regression and pre-review audit

Latest source full discovery PASS628tests624.508s, no skips; wrapper624.633s/exit0.
Log SHA256`d64fdbb7e834c3957479e3ebaddfaf451dce58db8f7ce194f57ffb600f9687b9`;
record SHA256`05e009d91c2aed9ea8260598282f583a1a24de8b8130af8749bc14891a55b7c3`.
All matrix tests run, including the controlled alarm regression and omitted-termination
mutation oracle. All eleven actual controls and public up expected refusal are above.
Owned diff whitespace,25 proof-source/seven code-test/target hashes, frozen intent,
HEAD/index and six concurrent-file preservation checks PASS. Original failures and
uncertain resources remain preserved; neither full PASS nor the controlled alarm fix
claims the original full-run precise trigger or the separate Docker timeout cause.
Three independent BMAD review layers remain before final acceptance/commit.


## Artifact locations and reproducibility

All result tables refer to protected files under
`platform/deployment/.local/pinned-cli-execution-qualification/<run-UUID>/`.
For a table row named `<mode>`, the result is `<mode>.json`; the corresponding exact
command and run UUID are recorded above and in its `command` field. Its safe
`result.source_sha256` binds the selected code/profile sources where applicable;
`retained_before`/`retained_after` identify all13 receipt/config paths and hashes.
`prerequisites.json` records prepare/toolchain/images commands and selected image identities.
Code/config provenance remains in the protected receipt manifests and selected control
source hashes.
Full discovery uses `deployment-tests.json` plus `deployment-tests.log`, whose digest
is `output_sha256`. Suffixed retry filenames are retained separately; the interrupted
initial discovery and original late-zero failures are never replaced. The source
baseline is05dd515782c26d036dffd7373b9759f9e101199e; changed working-tree sources are
identified by their per-file digests, not attributed to that commit's old bytes.

For example, verify the latest pre-review records from repository root:

```sh
sha256sum platform/deployment/.local/pinned-cli-execution-qualification/45e7c3ea-497e-4d1c-aca6-8959dae94935/backend.json
sha256sum platform/deployment/.local/pinned-cli-execution-qualification/45e7c3ea-497e-4d1c-aca6-8959dae94935/deployment-tests.json
sha256sum platform/deployment/.local/pinned-cli-execution-qualification/45e7c3ea-497e-4d1c-aca6-8959dae94935/deployment-tests.log
```

Required receipts/state and original diagnostic artifacts remain local and preserved;
this does not publish them externally or make another checkout's receipts reusable.
For a new checkout/run, use the tracked, self-contained
[prerequisites and four closed SQL invocations](DEVELOPMENT.md#reproduce-backend-qualification).
No ignored verifier is required to reproduce the normal control or all27 SQL cases.


## Review patches and retained investigations

Resumed independent reviews: blind10 findings, edge0, verification-gap0. Every finding
is graded in the Build triage log before grouping. P1 adds forced occupied→timely-zero
and occupied→late-zero fixtures; P2 documents tracked-only closed SQL invocations;
P3 maps artifact paths/source/commands; P4 documents prerequisite owner commands.
Two concurrent Leave findings are rejected under the user's explicit ENV-only scope;
those owner documents remain untouched. Three unverified investigations are appended
without changing old entries: pre-handle alarm windows, backward-clock elapsed bound,
and the original uncaptured Docker timeout. No real host clock is changed and no
unverified parent is signalled. Existing bounds, production predicates and runtime
gates stay unchanged; no new public SQL/runner/service or ADR decision is introduced.

Temporal fixture interface RED1test0.006s (missing helper), then focused GREEN0.008s.
Root catches subtransaction rollback erasing the session-local observation counter
on rejection before actual qualification: focused oracle RED1test0.004s precedes its
server-local exception-detail correction, GREEN0.006s. It carries only fixed ordinal2,
not business/query rows, across error handling. The unit comparison proves original
conditions/deadlines/exits/messages remain after removing only fixed relation input
and ordinal detail. Real PostgreSQL qualification and full regression follow the
review source freeze; previous628 PASS and actual controls are preserved as historical.


Post-review fresh f3284d07 prepare0.061s/toolchain14.133s PASS; images qualification
refuses registry/manifest_response_invalid17.882s after a publisher HTTP429 at a
manifest request. Safe HTTP status/media/encoding metadata is retained; no response
body/credentials/logs are recorded. Prerequisite record SHA256
`36259e1e54d309acb1b2877c0d5f5f17d2e856d0f34a030aeb7d8476f4e964a4`. No actual container control starts.
Preserve the failed partial qualification; pause requests before a fresh UUID attempt.
No pin, content check, timeout, proof or receipt is repaired or weakened.


After pausing publisher requests, fresh `14cf6356-c950-4682-a017-703986ca4545`
prepare0.057s/toolchain14.663s/images30.639s PASS with unchanged pins/checks/limits.
The existing private verifier now executes the exact tracked runbook Python heredoc
for matrix/late-first/timely/late-next and records its SHA256
`183e85de1004c2ebe9d1ef4aadf734a8dcb1c929aaac9f12ae0ff71a2b516738`.
This directly verifies documented reproducibility rather than relying on a private
implementation of those cases. The normal backend and eight old controls retain
original entrypoints. All controls run serially; actual results/full regression remain
pending. F328's failed record is retained, not repaired or claimed successful.


## Reviewed temporal cases and separate Docker refusal

Source-qualified14cf6356 exact tracked `timely` command PASS69.119s, record SHA256
`eadb43ab74c782e77832d8192eda085b65525dc885a4c23d07560bb54ab89657`;
`late-next` PASS73.492s, SHA256
`6bce1212011cec21c0d563f2524d728e21717d06e39ee7c2a1ee69e29552649a`.
Both enforce exactly two observations on real PostgreSQL, plus the unchanged actual
presence/catalog/job/normal cleanup;13 receipts/running inventory unchanged. The
recorded documented-script hash matches the tracked runbook. These close B4/B5.

The next plain backend invocation refuses docker/docker_timeout45.025s; record SHA256
`88fca982030369b9180ef8de1e03cb85ed2e72bc8b71eb2ec39155dfbaf182dd`.
It is not a PASS. Exact original exchange/phase remains uncaptured; this does not
establish the same cause as ecc22e64. All13 receipts/running inventory unchanged.
Read-only exact-name inspection finds no PG container/volume, but retains empty bridge
`49aac2e2c22cac7e749a5cc04df3e7ccfc4e50353e9d429c9cfebad94fe47457`.
Safe state in timeout-review-resource-state.json has SHA256
`ca402dd320caff290b9252132984565481cd4c4868c5d9fe644a638fafba1501`.
No removal/adoption/replay. Fresh source-identical b5543ce4-4d78-4b39-b201-39bc6d0065fc
uses the existing transparent exchange observer for normal backend verification;
passing later does not explain this refusal. Successful temporal cases need not be
repeated merely for one UUID; source/target/script identity will be checked across
both runs. Remaining fixed SQL/legacy controls and full regression are still required.


B5543ce4 prepare0.059s/toolchain14.891s PASS, then images refuses HTTP429 at the
same manifest step18.195s, before container controls. Prerequisite record SHA256
`a7a97a837c7b5cae22eb4037866c935dc728650284dc2843666679ccaf5dfe97`. Existing failed directories/records
remain preserved. Fresh237696d7-4564-4e00-84f1-e38892354cc8 uses a fixed2s pause
before each read-only publisher request, consuming the original180s collection
budget via the owning remaining(deadline) check. No retry, alternate registry, token
logging, response override, pin/content-check change or deadline extension. This is
local verification scheduling through the same owner, not a new registry client or
production behavior. Safe numeric Retry-After metadata is retained when provided.


## Reviewed-source remaining verification

Fresh237696d7 prepare0.054s/toolchain14.290s/images71.188s PASS. Publisher requests
have fixed2s spacing within unchanged collection180s; all original validators and
pins pass, no retries/overrides. Image receipt SHA256
`33d9c04231774d14faaab16b014123a512f36a57d835499476c9518a7f313979`.
Normal backend with transparent safe exchange observer PASS66.656s; record SHA256
`b90e51177db8547e44519480483ada94099ac2ae902d8d01f1bcdf015bb12fe5`.
Both actual backend facts, catalog/job/normal cleanup and13 receipt/running inventory
preservation pass. Trace has1041 exchanges/0 errors, slowest0.451941s;
guard phase7/cleaned true/ownership_lost false. No timed exchange occurred here, so
this does not explain the earlier14cf/ecc timeouts. Their records/resources remain.
Remaining exact documented matrix/late-first cases and eight prior controls run
serially; the two14cf temporal passes are source-identical and retained separately.


All four exact tracked SQL invocations PASS:27 cases across source-identical14cf
(timely/late-next) and237696d7(matrix/late-first). Each record carries the identical
tracked-script digest183e85de1004c2ebe9d1ef4aadf734a8dcb1c929aaac9f12ae0ff71a2b516738
and all25 source hashes exactly match review-source-checkpoint.json. All13 receipts
and running inventory unchanged on each. Matrix PASS76.331s/SHA256
`20dd365de24c554daa7d646017368d12ba1c236a7698489b28f132da9fa29b73`;
late-first PASS74.385s/SHA256
`32622d7434aa378aad7973056fce7256f9f1048243222695a08f3225dc75c580`.
This closes documented reproducibility P2 and both temporal cases P1 without source
or deadline changes. Eight prior controls and full regression still run separately.


## Reviewed-source control ledger

| Run prefix | Mode | PASS seconds | Record SHA256 | Inventory unchanged |
| --- | --- | --- | --- | --- |
| 14cf6356 | backend-doc-timely | 69.119 | `eadb43ab74c782e77832d8192eda085b65525dc885a4c23d07560bb54ab89657` | true |
| 14cf6356 | backend-doc-late-next | 73.492 | `6bce1212011cec21c0d563f2524d728e21717d06e39ee7c2a1ee69e29552649a` | true |
| 237696d7 | backend-diagnostic | 66.656 | `b90e51177db8547e44519480483ada94099ac2ae902d8d01f1bcdf015bb12fe5` | true |
| 237696d7 | backend-doc-matrix | 76.331 | `20dd365de24c554daa7d646017368d12ba1c236a7698489b28f132da9fa29b73` | true |
| 237696d7 | backend-doc-late-first | 74.385 | `32622d7434aa378aad7973056fce7256f9f1048243222695a08f3225dc75c580` | true |
| 237696d7 | catalog | 67.258 | `04bef7bb68e551b4010c733ee03e4851cf05ec6ff7844b1719aec931454d1f4f` | true |
| 237696d7 | auth-job | 68.983 | `fca32a7c5f4168315dc98d24e818330bff17a80b6a4a0c6ce5f8cbe4b22bab81` | true |
| 237696d7 | poststart | 66.557 | `305c179966e312e5c71faeb71cb751297a85c4c423e7a294374795fea022319c` | false |
| 237696d7 | initialized | 94.503 | `0ead41e6e86ffeefa383226d2c75c6b4f829d0c92040d6a1922998e2704b06d6` | true |
| 237696d7 | persistence | 82.282 | `5ef8be0dbe281153ed9f065b3a7ef5b26836f76002fdcb0600a68a3f3ee8ccee` | true |
| 237696d7 | proof | 65.678 | `cc4de7d906c402bfb6cd3c31685cbda6452bdcbddbc56f50546b0ae76e1db2dc` | true |
| 237696d7 | bootstrap | 28.938 | `12bb33c083c6db42598b9e7be8e7ea3023733bd12023864b956c9196184b01ed` | true |
| 237696d7 | controls | 70.334 | `319733e2eb84bfc7837bea8f0c86a532e1564f581dc0da9c4fe138293be48997` | true |

Run prefixes map to full UUIDs14cf6356-c950-4682-a017-703986ca4545 and
237696d7-4564-4e00-84f1-e38892354cc8. Use the explicit artifact-location mapping above.
All13 receipt/config files remain byte-identical on every successful control. Only
poststart records unrelated Deals additions, with no removal; initiator/cause is not
established and ENV does not interfere. Other12 inventory snapshots are unchanged.
All27 SQL cases and the normal real-backend/catalog/job/cleanup sequence pass on the
same25 source hashes. The tracked documentation code digest is identical across all
four semantic controls. Production predicate/owner deadlines are unchanged.

Final focused133 tests PASS2.563s. Existing contract test now requires one snapshot
clear inside LOOP; a source-in-memory mutation moving it outside is independently
caught as the one expected assertion failure. Production source is untouched.
Public up expected2/runtime_adapter_unqualified0.055s on237696d7. Final full discovery
is running using the same retained runner/assertions/900s bound. No new full pass is
claimed until that run completes.


## Retained full629 no-eof failure and unchanged focused diagnostic

First reviewed-source full629 runs789.028s, one failure/no skips; wrapper789.270s,
exit1. Log SHA256`655221e6d8c99bb110c2d67ad54a79cafe39b0413faf199bab2bdeb406e4e741`;
record SHA256`886f7c95fc34fd49369cc88bbaff81e71a7950d15a2e14a82441b10725f580b7`.
Unchanged Resources.test_integrated_private_handoff_adversaries_and_drip_deadline
fails at descendant witness count0 rather than1 in no-eof. Prior timeout code,
daemon prefix29, connection count and elapsed bound assertions pass. No intended
malicious request is confirmed. This is not a full PASS; source and expected
assertions remain unchanged.

Exact existing nine-case method with safe guard phase/remaining-time/witness diagnostics
PASS15.692s. Record SHA256
`2f9649a6bf0859ea645aed182af69527eeab8791ac0c1b2dd1a0aead4f6f451d`.
Diagnostic labels are unknown; rows map by the test's declared nine-case order, not
observed label capture. All9 witness flags true; final declared no-eof guard phase1,
entry remaining1.729770s, operation1.734734s, ending remaining-0.005066s. Existing
witness/stopped-state and2s/4s assertions pass. No source, deadline or expected-result
change. This pass does not explain original admission/timing/current-change cause.
R2 is individually triaged medium-unverified and appended once to deferred work.
A full unchanged rerun uses the retained runner and separate deployment-tests-2
artifacts, preserving the first failed result; no current full PASS is claimed yet.


## Final acceptance

Reviewed-source unchanged full rerun PASS629 tests801.123s, no skips; wrapper801.255s,
exit0. Artifacts are237696d7/deployment-tests-2.json and deployment-tests-2.log under
the explicit protected artifact root above. Record SHA256
`9cf089f13e8ed329bbe35d4c62e92af8d9ca61593fcaa93802885b864f6f63ea`;
log SHA256`a8fc5903184a143218579b0674b4e194ac3bb1ec319ace5f6fa90d56df750bee`.
The failed first full629 result, original no-eof non-admission and focused diagnostic
remain unchanged; this PASS does not establish their original cause or change attribution.

Final133 focused tests PASS2.563s and4 process cases PASS36.297s. All13 qualification
controls/27 SQL cases pass across source-identical14cf6356 and237696d7. Exact tracked
runbook code, all25 source hashes, final code/test hashes and target identity match.
All13 receipts/config files unchanged on every control. Twelve running snapshots
unchanged; one poststart delta contains only unrelated Deals additions, retained with
no interference. Public up expected2/runtime_adapter_unqualified0.055s.

Three independent BMAD layers complete: blind10, edge0, verification-gap0. Every
finding is individually triaged. All four patch groups verified: forced temporal
matrix, tracked-only invocations, explicit artifact mapping and prerequisite commands.
Two concurrent Leave findings are rejected under user intent and preserved. Four
medium-unverified investigations remain: pre-handle alarm, backward clock, uncaptured
Docker timeout, unconfirmed no-eof witness. Existing deferred entries remain byte-identical;
original failures/diagnostics and lost-custody volume/bridges are retained. No claim
that a passing repeat resolves any investigation.

All five impact decisions are recorded above. Existing scaffold/generator/test/runbook
owners retain implementation; no shared UI/context or accepted ADR change. This
completes the bounded backend-lifetime qualifier only. Full CLI setup/Auth service,
public runtime lifecycle and remaining ENV/P1/SERVICE consuming-scaffold proof remain
open before Identity/Access/WRITE or server-backed KDG. No Leave/editor, production,
accounts/grants, infrastructure provisioning, deployment or real-data pilot work.
