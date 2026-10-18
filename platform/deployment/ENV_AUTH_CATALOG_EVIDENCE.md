# Independent Auth migration catalog evidence

Build: [Auth catalog verification](../../_bmad-output/implementation-artifacts/spec-env-auth-migration-catalog-verification.md).
Status: complete; reviewed-source verification passes. Runtime readiness remains false.

The preceding [Auth execution proof](ENV_AUTH_JOB_EVIDENCE.md) establishes exact
request, CLI termination, immutable job exit/disposal and same-PG clean disposal.
This increment independently verifies the source-defined migration outcome inside
that same fresh owned database, using existing deployment owners and detached exec.
It neither continues CLI setup nor identifies its earlier host-facing DB session.

## Source and ownership

The retained official Authv2.197.0 tree resolves to commit
`4eee58f296d9698a1c2c0ae14d7a0b379c7622d3`, with75 up migrations. Their filenames
supply literal version strings; the initial one is `00`, not integer0. The exact
inventory is retained privately at `.local/auth-catalog-qualification/expected-versions.json`,
SHA256`a27ae5228893136196488c99f99b42aab0a934ddc4456bfafcd13732e35aa78a`.
Source cmd/migrate_cmd.go SHA256`9a80dde9aba8e9b3a8d42d2abde5d931f87d5372b31196063967ff326f84acc5`
uses embedded MigrationBox and UpTo(0), schema_migrations/namespace. Main embeds
migrations/*. Popv6.1.1 parser and insertion preserve Version as a string.
[Source profile](fixtures/supabase-pg17-profile.md#independent-auth-migration-catalog-verification)
records the ledger and selected structural authority. Expected data is defined before
execution and independently compared to the constant; no observed catalog is adopted.

Web raw-source lookup initially returned404 for a guessed internal/storage path;
no runtime operation followed. Official repository tree identified cmd/migrate_cmd.go.
Two guessed Pop filenames returned404; the official archive located the parser.
A diagnostic substring lookup failed after safely retaining file_migrator.go; actual
parser source is then read. These are source-discovery failures, not test passes.

## Requirements and executed evidence

| Requirement | Required evidence |
| --- | --- |
| AC1 fresh transition | Actual precheck → job → postcheck → same-PG normal cleanup; real process termination ordering |
| AC2 exact ledger/selected structure | Independent7/75/82-version inventories, real rollback-isolated corruption controls and strict SQL predicates |
| AC3 custody/one-shot | Changed PG/image/fixture/resources, duplicate attempts and exec ID/config/state mutations |
| AC4 uncertainty/bounds | Lost/malformed create/start/inspect, nonzero/deadline/interruption; no replay/reconnect |
| AC5 compatibility | Existing execution/refusal/legacy controls, expected public up refusal and full deployment suite |

## Impact decisions

Scaffold: existing lifecycle/transport/resource/startup/test owners only, no generator
or runtime service. Shared UI unchanged. Agent context: existing rules suffice.
Documentation: source profile, this evidence, runbook, Build record and KDG handoff/
memlog. Accepted ADRs unchanged; no new decision. ADR0020 owner migrations/release
coordination/compatibility/recovery stay gated. ADR0023 no query output, payload,
credential or job logs; report selected booleans and operation references only.
Concurrent Leave/PtS/Expense files/index and all retained diagnostics/resources stay
protected. No production, owner SQL/accounts/grants, editor or dependent work.

## ATDD and focused implementation

Child acceptance RED:3 missing-interface errors before production edits. Implementation
adds the closed SQL/transport/retained-owner/control interfaces. Final child no-socket
suite114 PASS6.649s, ten catalog methods: pre/post failure,16 lost/malformed/nonzero/
interrupted exchange combinations,18 custody mutations,14 malformed lifecycle/config
branches, running-to-success, expired deadline, started-but-lost-ACK and duplicate
attempt/ID/phase cases. A first deadline fixture repeats its own still-current fake
clock; synchronizing fake daemon/guard expiry fixes the diagnostic without production
or expected-outcome changes. Root independently verifies below.

Root first process run:3 tests36.044s,1 failure/2 errors. New mutation oracle matched
a nonexistent source string (group variable/wait1 rather than actual process.pid and
bounded wait). Predicate-failure assertions incorrectly required normal stop, whereas
existing failure cleanup force-disposes a still-owned resource. Source and cleanup
code are unchanged: root corrects the mutation target to actual SIGKILL/wait/flag block
and verifies owned disposal on failure, normal shutdown on success. This is fixture
alignment with the existing contract, not a relaxed unknown failure or runtime pass.


Root current-source focused suite114 PASS2.077s. Corrected real private-socket/
process acceptance3 PASS24.403s, proving both process PIDs stopped before precheck,
no success acknowledgement, pre→job-create→job-delete→post→PG disposal ordering,
failed precheck prevents job creation and failed postcheck cannot qualify. The
mutation oracle observes omitted group termination before any catalog exec.
Independent retained75-version inventory equals the production constant exactly.
Private corruption control requests remain below16384 bytes (pre2267, post12997).
Existing verifier gains only catalog/catalog-negative literal modes; previous SHA256
d1e2f8de7dab2de2b78cc36abcf12ab7bcca2a93cf098ebebe61889f1c05b46f,
new SHA2564d8a788686a8d6c1eb0ce7a88b64b872e92cbaa71cf9480adef69417f22a22c2.
Previous helper is retained, original negative-marker/cluster branch byte-identical.
91 real corruption cases are planned:4 precondition and87 postcondition, including
each75 missing ledger version, extra/duplicate/NULL rows, six renamed tables and
three latest-column faults. Each case rolls back and only P0001 from the unchanged
predicate is accepted. The real executed count will be recorded after qualification.

## Actual refusal and publisher baseline diagnosis

Freshc27ec42d-ebe1-4c1f-8a26-8ab719fbe347 prepare0.063s, toolchain16.006s,
images37.715s pass. Actual catalog control refuses execution_sql_failed41.492s;
record SHA2567e001880bfa792661d64fd7212a45e5fddbecc06c6404fe209323351dbc9ebea.
All13 receipts and running inventory unchanged. Unchanged-source safe phase diagnostic
refuses38.948s; precondition verified, job dispatched, post fails, owned cleanup true,
ownership_lost false. Record SHA2560a061d87cfa58177b00e8fd78a442fcab7dc171d1d9ea8b711cbfab7e9964b0f.
Selected read-only boolean diagnostic refuses39.610s, record SHA256
6c347692bc37b46eb4a466f83b43d73b6dc8286a6b02946e2f5f32b3189823d4:
all selected tables/latest nullable timestamptz/initial00/latest marker true;
count75/distinct75/exact ledger/no-unknown false, legacy0 false. It uses existing
bounded CLI runner for a separate read-only catalog diagnostic only, rechecking the
same healthy owned PG before/after, returning only checked booleans in memory, never
account rows or logs. It does not repair or qualify the failed production predicate.

Root's initial exact75 criterion omitted the PostgreSQL publisher bootstrap ledger.
Official selected17.11.0.004 release resolves commit
cf90815413819eb057a9916c1598692c160ebeb4. Its
[migrations/db/init-scripts/00000000000001-auth-schema.sql](https://github.com/supabase/postgres/blob/cf90815413819eb057a9916c1598692c160ebeb4/migrations/db/init-scripts/00000000000001-auth-schema.sql)
SHA25665a4a55ba3248716eb4946a8677be41c94bc90eafaa22c0eb95b09908f96fa4f
explicitly inserts seven historical versions:20171026211738,20171026211808,
20171026211834,20180103212743,20180108183307,20180119214651,20180125194653.
These do not occur in current Auth's75 source files. Source supplies the candidate
exact7-before/exact82-after union independently of observed catalog rows. No ledger
row is deleted, adopted as arbitrary expected state or excluded from exact comparison.
A separate injected diagnostic tests this precise publisher-preserving hypothesis.

Concrete unapplied proposal at `/tmp/kdg-auth-catalog-publisher-baseline.patch` adds
that seven-version constant and exact pre/post7/82 comparisons, preserving the75 Auth
constant, structure checks, timeouts, ownership and all existing execution boundaries.
It also corrects this Build's frozen criterion; no production correction is applied
before the required explicit frozen-spec decision. Remaining91 planned corruption
checks have not run and will be expanded to cover the combined publisher baseline.

The separate source-defined baseline-union diagnostic PASS64.305s, record SHA256
5b714ad3249824fd54b0866d70953d10f129716b3fad9f39201c60f8cf587e83.
Exact7 precondition/exact82 postcondition, selected structure, job exit/disposal,
same-PG normal shutdown/cleanup all verified;13 receipts/running inventory unchanged.
Image receipt SHA256e652c31186d292d46d8d3a5b9aed2393a2dc9487085a67b8d9ca5bf7044fec9f.
Root verifies all25 source/current13 receipt bindings and original frozen intent.
Protected index and six concurrent documents remain unchanged from this Build's
checkpoint. Proposal SHA25630e85dd8439581ce9c4345fdcaa7af08e1fb9f11f4c4be5aef9f9a02720c3102;
git apply --check PASS. Proposed correction is not yet applied or committed.

Existing private verifier additionally retains phase-only, selected-boolean and
baseline-union diagnostics; current SHA256
1514382bd47dd7c2c0204e8a8036aacae7313dc220e967cca061169ceecfa68d.
Each prior helper version is retained. These explicitly labeled diagnostic records
do not repair the original failed production qualification. No public bypass or
new generator/service is introduced. Full regression,91/expanded negative controls,
legacy requalification and three-layer Build review have not run for this new item.
Implementation waits for the frozen-spec correction decision required by Build.

## Approved publisher-baseline correction

2026-10-18: after the migration/image explanation, the user says “ok, happy, next”.
The reviewed exact patch is applied. Preserve seven publisher bootstrap markers,
require exactly those seven before the job and exactly their82-version union with
current Auth afterward. No database history is removed or modified by this correction.
Original frozen snapshot and newly approved snapshot are retained separately.
Both constants independently match the retained publisher SQL/file inventory.
Focused114 tests PASS1.993s. Expanded real SQL negative mode now has109 cases:
14 precondition,95 postcondition, including every missing baseline/current version,
extra/duplicate/NULL entries, missing/renamed tables, a view masquerading as a table,
and missing/wrong-type/non-nullable latest column. Requests remain bounded (pre3619,
post13868 bytes). Current helper SHA256b10d86df4a045304589802d8907c49ec77d1203d36fad9205b9104938a3a6453;
previous bytes retained. Actual corrected-source proof requires fresh qualification.

Corrected-source actual53a254d6 catalog PASS69.336s: exact7 precondition/exact82
postcondition and selected structures, CLI termination/job exit/disposal and normal
same-PG shutdown/cleanup verified. Record SHA256
964769d5e87066f9672fd1da7613149209bd087dfef22ea78e92de15e46c535b;
image receipt SHA256a3b858dc586f39fd1038ab7a61d7c2356c146077c1abfc35541e07ad4f48b61f.
All25 source/current13 receipt bindings and approved frozen snapshot independently
match. Root process3 PASS22.526s. Runtime/fresh setup remain false.

First109-case negative run refuses during pre in41.222s; no cases claimed complete.
Record SHA256af644f37d4f6d7b28697a7ba8cee590be142e412a0869cbb26ac93496a2015f7,
13 receipts/running inventory unchanged. The private fixture tries ALTER TABLE
one_time_tokens before Auth creates it; pinned PostgreSQL bootstrap contains no such
table. Replace that specific precondition corruption with CREATE TABLE carrying the
forbidden column, rolled back after the predicate's required rejection. Production
predicate/expected rejection remain unchanged. The existing helper retains retries
as catalog-negative-2.json etc using O_EXCL, never overwriting the failed record;
source/profile change still requires a fresh qualified UUID. Current helper SHA256
a5f0317df903a2a30c1a05b12dc12bc16335288b6897bab7d3f82ea5f8955635;
previous helper retained. This is a fixture correction, not a passing runtime claim.


Second negative run also refuses in pre38.768s, record SHA256
9845a728dfe31a21195b647bcfc6f5f804b1008350be19b9cb22103d9ff4c259.
The missing-table correction is a real source-defined fixture fix, but did not
explain the original failure: subsequent selected case diagnostics identify all14
pre mutations as SQLSTATE42501 (insufficient privilege). The production postgres
role can read Auth metadata but cannot mutate Auth-owned tables/schema.
An initial diagnostic attempt had a missing dev import and raised NameError after
the original refusal; owner finally cleanup still ran, no qualification receipt
was published. Corrected diagnostic refuses38.040s, record SHA256
526b1c42f3c99027099b9a269d72132532b717e85a9a3aa37a380e894f80404a,
all13 receipts/running inventory unchanged, case indices/SQLSTATE only retained.

Negative fixture now reuses the image's existing supabase_admin over local socket
for rollback-isolated corruptions. Each unchanged production predicate executes
after SET LOCAL ROLE postgres, then resets for the next setup; the final unchanged
predicate also runs as postgres. No accounts, privileges or production body change.
This matches existing bootstrap's privileged catalog-test owner while independently
proving restricted reader behavior. Current private helper SHA256
8b04a522c11ad325afa463083153d6f6581ca64d7ad0a9d9bf708024944f85ed;
previous helper retained. Final executed negative count remains pending.


Final109-case corruption control PASS85.800s, record SHA256
130d439a6e238993e34c48194fd90466c797a9a193daef1bd3e18ec5d1e4b616.
All14 pre and95 post corruption cases reject under production postgres authority;
valid unmodified predicates pass after rollback. Exact original catalog/job/PG
completion and normal owned cleanup still pass. All13 files/running inventory
unchanged, no account/grant changes. This establishes executed SQL semantics beyond
mocked exec exit codes; earlier fixture failures remain separately retained.


## Corrected-source control matrix

All records under existing private verifier run53a254d6-c97d-4018-a0be-46dc194ec105.
Every control preserves13 receipt/config files. Running inventory differences occur
only for the unrelated Deals benchmark identity; retain exact before/after rows in
concurrent-docker-deltas.json, with initiator/cause unobserved and no interference.
The bounded qualifier's resource mutations stay confined to its proven run.

| Control | Elapsed | Running inventory unchanged | Record SHA256 |
| --- | --- | --- | --- |
| catalog | 69.336s | True | `964769d5e87066f9672fd1da7613149209bd087dfef22ea78e92de15e46c535b` |
| catalog-negative-4 | 85.8s | True | `130d439a6e238993e34c48194fd90466c797a9a193daef1bd3e18ec5d1e4b616` |
| auth-job | 77.185s | True | `995b4f380944fb0a447c6de6782c2bbcb59777e5b7347f1aa6e4b1f5849262ef` |
| poststart | 78.194s | False | `1e6915f931b7e904597025afb6e164b9978fa306e44791767dddc4b1f7e199b8` |
| initialized | 97.491s | False | `4e628b10c388d46d67fe9e1096115f12054bd5828a1cb61bc6dc87e858361420` |
| persistence | 104.863s | True | `b7c6bc7b69b5be7b6589e4c926e5253d2537b7c11c42a66a9fcdde18e46cb601` |
| proof | 75.483s | True | `f7ab29015528e109c65155a00f86ffb2f6e5364bd447b5762d3f981ade2bb5d4` |
| bootstrap | 28.326s | True | `fda307251153598e85b0e059fe76a576013de0f302c77941c99af1ad28ac6832` |
| controls | 84.591s | False | `450e0822dde954f73390b88ee41d79e6fe8ff095b11e06ce7275fb6d1c6a513b` |

Public up expected exit2/runtime_adapter_unqualified0.078s. Root then starts the
full deployment discovery using the retained diagnostic runner, unchanged assertions
and900s wrapper bound. No source/profile edit occurs during the suite.

## Recorded commands and requirement audit

These commands record the source-qualified run above. For new source/profile bytes,
choose a fresh UUID and repeat prepare/toolchain/image qualification using the
[development runbook](DEVELOPMENT.md); do not repair/reuse a stale receipt. Root
executes checks serially from repository root. The up exit2 is the expected
refusal and is checked separately before full tests. Existing private test mode
invokes the retained full diagnostic discovery runner (SHA256
4e60dc7e805ccb3fc02045eb33c697dca0f3f557244dc8c2ce5617b234f54ea5),
which preserves original assertions and safe failure categories.

```sh
python3 -m unittest discover -s platform/deployment/tests -p test_pinned_execution.py
python3 -m unittest discover -s platform/deployment/tests -p test_resources.py -k auth_catalog
python3 platform/deployment/.local/pinned-cli-execution-qualification/verify-local.py prereqs-diagnostic 53a254d6-c97d-4018-a0be-46dc194ec105
python3 platform/deployment/.local/pinned-cli-execution-qualification/verify-local.py catalog 53a254d6-c97d-4018-a0be-46dc194ec105
python3 platform/deployment/.local/pinned-cli-execution-qualification/verify-local.py catalog-negative 53a254d6-c97d-4018-a0be-46dc194ec105
for mode in auth-job poststart initialized persistence proof bootstrap controls; do
  python3 platform/deployment/.local/pinned-cli-execution-qualification/verify-local.py "$mode" 53a254d6-c97d-4018-a0be-46dc194ec105 || exit $?
done
python3 platform/deployment/.local/pinned-cli-execution-qualification/verify-local.py up 53a254d6-c97d-4018-a0be-46dc194ec105
python3 platform/deployment/.local/pinned-cli-execution-qualification/verify-local.py tests 53a254d6-c97d-4018-a0be-46dc194ec105
```

| Requirement | Executed passing coverage |
| --- | --- |
| AC1 fresh transition | Actual catalog69.336s;3 process tests22.526s cover both PIDs stopped before SQL, phase/disposal order and omitted-termination mutation |
| AC2 exact ledger/structure | Independent publisher inventories;109 actual rollback-isolated corruptions85.800s plus unchanged predicates as postgres; selected table-kind/type/nullability proof |
| AC3 custody/one-shot | Focused114 includes18 PG/image/fixture/network/volume mutations at exec create/inspect/start, duplicate attempts/IDs, disabled/early phases |
| AC4 uncertainty/bounds | Focused114 includes16 pre/post exchange faults,14 malformed lifecycle/config branches, running-success/deadline and started-but-lost-ACK; process pre/post refusals verify owned cleanup/no qualification |
| AC5 existing controls | All seven preceding controls pass, expected public up refusal; complete current-source regression result follows |

Scaffold/UI/context/documentation/ADR decisions remain as above: existing ENV owners,
no UI or root instruction change, current evidence/runbook/profile/handoff/Build updates,
no accepted ADR edit/new decision. Six prior investigations remain open. The original
unstarted bootstrap diagnostic resource is preserved; no recovery/deletion is inferred
from this passing bootstrap check. This Build proves a fresh publisher Auth catalog
transition only. Full Auth service/schema equivalence, CLI host-session identity,
later setup, public lifecycle, owner release/fixture readiness and P1/SERVICE consuming
scaffold acceptance remain separate, before dependent Identity/Access/WRITE/server KDG.


## Pre-review completion

Full discovery PASS606 tests755.251s (wrapper755.521s), no skips, exit0.
Log SHA25659177c69ace014e9031c5007ea626ceda4675a82c87283fdbc1473dab306c8a6;
record SHA2560046f604b8a452046e0f9d9148546cbcd1879b4ce49dcd98e4576adc6f169e77.
All five matrix rows have executed passing coverage as above. Root rechecks25 source
bindings and13 receipt/config hashes, approved frozen snapshot and protected index: PASS.
All five impacts recorded. No source/profile changes during full regression. All six
previous investigations/resources remain preserved. Independent three-layer review next.


## Independent review and patch verification

All three independent layers completed before triage. Root reproduced accepted
contradictory running ExitCode and successful completed Pid0 metadata in the no-socket
fixture. Mobyv28 daemon/exec.go sets Running before Process assignment, so a transient
running Pid0 with NULL ExitCode is legitimate; do not prohibit it. Inspect derives
PID from Process; failed startup supplies nonzero126. Tighten terminal/running checks
without requiring a poll to catch a fast process running. Primary source retained in
.local/auth-catalog-qualification/moby28--daemon--{exec,inspect}.go.

Other patch groups make the closed corruption fixture and independent publisher
inventory available in tracked test owners, cover post-job custody mutations, and
clarify runbook/recorded commands/test traceability. No new public control, runtime
configuration or generator. Concurrent Leave findings are rejected under the user's
explicit preservation/exclusion; six prior investigations stay open, none newly deferred.
Root repeats source-bound verification after implementation returns.

Exact executed test identifiers (module `platform/deployment/tests/test_pinned_execution.py`,
class `AuthCatalogExecutionMatrix`):

- AC1: `test_independent_pre_job_post_then_same_pg_cleanup`; process module
  `test_resources.ExecutionSupervisor.test_auth_catalog_process_order_and_same_pg_disposal`
  and `test_auth_catalog_process_oracle_detects_skipped_cli_termination`.
- AC2: source-defined109-case actual catalog-negative control above; the tracked
  inventory/body fixture tests accompany the review patch.
- AC3: `test_current_pg_checks_surround_each_exchange_before_next_mutation` and
  `test_invalid_order_disabled_early_cli_and_duplicate_exec_id_refuse`.
- AC4: `test_exec_uncertainty_consumes_attempt_and_never_replays`,
  `test_running_exec_then_success_and_deadline_preserve_one_start`,
  `test_malformed_exec_lifecycle_and_config_never_start_or_qualify`,
  `test_closed_exec_rejects_type_confusion_extra_keys_and_changed_flags`, and process
  `test_resources.ExecutionSupervisor.test_auth_catalog_process_predicate_failures_do_not_qualify`.
- AC5: seven actual legacy control records and expected public refusal above; final
  full discovery includes their owning registered deployment test methods.


## Reviewed-source qualification

Fresh run `2fc0da48-8839-410c-a06b-464e7722707b` binds the final review patches. Child observes
RED before the minimal fixes, then14 focused catalog tests PASS0.509s. Root118
owner tests PASS2.180s and3 process tests PASS21.491s. The independent tracked
fixture is checked against retained primary Auth filenames and PostgreSQL bootstrap
SQL:75 Auth,7 publisher markers and82 exact union. Root confirms the tracked
corruption helper produces byte-identical pre/post bodies and14/95 counts compared
with the previous verified private fixture. The existing verifier delegates only
that construction; its old marker/cluster negative branch remains byte-identical.
No public runner/control is added for corruption SQL.

Recorded control modes below use the existing verifier path and this fresh UUID;
the command sequence is the same as above. Prepare0.093s, toolchain18.941s and immutable
image qualification31.955s pass. Image receipt SHA256
`9ed36cdbffab6925a3916e02fb3caaef4e78b88e41bb45015b9f55b404c9aa95`.

| Mode | Result / seconds | Record SHA256 |
| --- | --- | --- |
| catalog | PASS / 67.145 | `fc803272410ada7f3b61202757a877b0c5779707e58c6f2b366ec22608262904` |
| catalog-negative | PASS / 67.636 | `561087e9512bd1629c65a9ba9b2f4434dfac787734b18334e8faf8b63f2faafc` |
| auth-job | PASS / 69.949 | `75d3e11691564d042a223f1201890bfe2b3515498d0008a4ec92dcb25c8d291a` |
| poststart | PASS / 63.177 | `fe14e620daade16ae5ecf80339f17939fa153a4a1f5f763dcc7bfcb058e14a27` |
| initialized | PASS / 80.985 | `f52b3f4fab832a65be267d3c224889f2020e406648f7ebd176891fb4fc24a756` |
| persistence | PASS / 77.989 | `0f3e68ceac8e7c0e68b30bca61e3b177a98b5809b3e40164757bf9823ee022e9` |
| proof | PASS / 64.699 | `125407b4eb270ab27c98f67524cc3c156a62c62c0550a8a17eea0790816f4778` |
| bootstrap | PASS / 27.663 | `92e0ccf80e0e627a2f29e7ea72c85d986e18ee336258b0695a445a53b825307b` |
| controls | PASS / 62.36 | `7d13b92b3143ed2633b0043404c87baf8e2c299793cf79b23472231b5387b5fa` |

All nine controls preserve13 receipts/config files and the running Docker inventory.
Catalog and109 rollback-only corruptions verify same-PG normal shutdown/cleanup;
no account or grant changes. Public up refuses exit2/runtime_adapter_unqualified
in0.049s. Setup/runtime remain false. All25 source/target bindings match before
full discovery. Original failed runs/diagnostics and six prior investigations remain.

Exact review-patch coverage adds these AuthCatalogExecutionMatrix methods:
`test_terminal_exit_while_running_and_completed_zero_pid_refuse`,
`test_starting_zero_pid_then_running_then_completed_qualifies`,
`test_tracked_corruption_builder_is_closed_bounded_role_scoped_and_rollback_only`,
and `test_static_source_inventory_independently_matches_baseline_auth_and_exact_union`.
The custody matrix now covers36 combinations across pre and post, with no mutation
after custody changes. These verify all six patch groups with the documentation
and exact-test-ID corrections above. Two concurrent findings remain rejected; none
newly deferred. Full discovery and final preservation/diff audit follow.

Private orchestration checks: the first AST extraction selected the wrong conditional
and raised KeyError before editing the verifier; direct function selection then
verified equivalence before the change. A source-count audit initially counted24
file bindings without the separate target; including the recorded target gives25.
Neither changes assertions, production source, receipts or qualification results.


## Final acceptance

Reviewed-source full discovery PASS610 tests508.504s (wrapper508.646s), no skips,
exit0. Log SHA256`bb9797f029f902bdbfe6dac0318c68c0a0a0418168abffb3b9b7e62713d6009b`;
record SHA256`67027bab39bffcb644c5873c6e78bdb8cef2031993baa91c697f2c061c43f8d2`.
Root final audit verifies25 source/target bindings,13 retained receipt/config hashes,
all owned test/fixture hashes, approved frozen intent and concurrent six files/index/HEAD.
All five acceptance rows and five impact decisions are satisfied within this bounded
Build. Three independent review layers completed; all six patch groups verified.
Two concurrent Leave findings rejected under explicit exclusion/preservation; no new
deferred work. Six prior investigations and retained diagnostics stay open/preserved.

This proves the fresh publisher Auth migration catalog transition. Full Auth service/
schema equivalence, CLI DB-session identity, later fresh setup, public runtime lifecycle,
owner release/fixture prerequisites and P1/SERVICE consuming scaffold acceptance remain
open. Select the next bounded ENV prerequisite through bmad-help; keep dependent
Identity/Access/WRITE/server KDG and Leave/editor/production/pilot gated.
