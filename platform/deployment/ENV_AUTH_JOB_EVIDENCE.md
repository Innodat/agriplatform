# Bounded Auth migration-job execution evidence

Build: [Auth job execution](../../_bmad-output/implementation-artifacts/spec-env-auth-migration-job-execution.md).
Status: done. Reviewed-source actual/legacy controls and593 deployment tests pass; three-layer review and patches complete. Runtime readiness remains false.

## Scope and authority

The preceding [post-start boundary](ENV_CLI_POSTSTART_EVIDENCE.md) validates and
refuses the first actual CLI Auth job. This bounded extension executes that one
job through existing ENV owners in a fresh synthetic database. Original CLI
request validation precedes proven CLI-group termination, without success ACK;
only then does the owner recheck custody and dispatch the immutable job. This
keeps later CLI setup SQL unreachable and fixture5s unchanged. It does not qualify
CLI continuation or independently authenticate its earlier host-facing DB session.

Pinned CLI source remains753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4. Reviewed
[db-setup.ts](https://github.com/supabase/cli/blob/753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4/apps/cli/src/command-internal/db-bootstrap/db-setup.ts)
opens the host session before the job; job inputs use a separate container-network
connection, and later setup SQL waits for job success. Driver probes may issue SQL;
there is no zero-SQL claim. The retained [profile authority](fixtures/supabase-pg17-profile.md)
owns the original six public synthetic inputs and exact gotrue migrate request.

Authv2.197.0 [Dockerfile](https://github.com/supabase/auth/blob/v2.197.0/Dockerfile)
installs the auth binary, its migration directory and gotrue symlink, with supabase
user. Root read that primary source and the already cached immutable image config:
User=supabase, WorkingDir=/, Cmd=[auth], PATH and GOTRUE_DB_MIGRATIONS_PATH only;
no entrypoint override. The API lifecycle authority is
[MobyAPI1.48](https://github.com/moby/moby/blob/v28.0.0/docs/api/v1.48.yaml).
Image defaults must be verified before dispatch, not accepted from observed caller
input. These source/metadata observations are not job execution evidence.

Deliberate disposable tightening retains the completed job for ownership/exit
inspection: AutoRemove=false replaces the original --rm behavior, followed by
explicit verified owner removal. Linux/amd64, immutable child, unique run job name,
restricted resources, restart no/logging none, no mounts/ports/host namespace follow
the approved spec. Only the recorded job may join the existing PG bridge; PG volume
use remains PG-only. No attach/log/wait endpoint or generic Docker forwarding.
Acquisition5s, execution120s, shutdown15s and single cleanup10s do not reset for job
work. Fast completed jobs need not be caught running, but completion must have valid
same-job state/timestamps and integer zero exit, never a boolean or mere start ACK.
Unknown creation/ownership cannot authorize adoption or deletion by discovery.

## Requirement-to-test matrix

| Requirement | Required executed evidence |
| --- | --- |
| AJ1 exact actual request → CLI terminated → job exit/disposal → PG disposal | Independent owner/process tests and actual literal qualifier; no ACK/continuation |
| AJ2 exact image/input/config/current PG and fixture/resource custody | Profile/transport/state mutations and both pre-dispatch/revalidation faults |
| AJ3 fast exit and invalid/nonzero/OOM/dead/restart state | Focused independent state matrix; safe refusal/no completion claim |
| AJ4 uncertain mutation/transport, deadline/interruption and ordered cleanup | Create/start/inspect/delete lost-response cases; no replay/budget reset; process failure checks |
| AJ5 bridge/volume/port/duplicate boundaries | Extra member and forbidden exposure/mount/terminal cases; legacy PG volume-use regression |

Observe acceptance RED first, then focused owner/transport GREEN, affected actual
private-socket/process suite, full deployment discovery and source-bound actual
qualification. Root owns serial process/socket/Docker execution. Preserve all failed
attempts; no passing rerun explains an unidentified earlier failure.

## Impact decisions and remaining gates

Scaffold: extend existing deployment/profile/transport/resource/startup/test owners;
P1/SERVICE generator acceptance stays open. Shared UI: no change. Agent context:
existing root rules suffice, current commands/limits in runbook and handoff.
Documentation: this evidence, profile/runbook, Build record, next-session/memlog.
ADR: existing accepted decisions unchanged; no new decision. ADR0020 controlled
owner migrations, compatibility, activation-blocking/recovery remain separate gates;
this job runs only the publisher's Auth migrations in a fresh disposable database.
ADR0023 selected safe facts only; no argv/env/SQL, job/health output, exception dumps
or credential-derived diagnostic evidence. No application accounts/grants or owner SQL.

Actual Auth job exit will not prove complete Auth schema/service readiness, later
fresh/initialized setup, independent DB session identity, cross-execution admission,
public up/stop/reset/recovery, full environment, owner locks/migrations/fixtures/current
authorization, provider/device or P1/SERVICE scaffold acceptance. Identity/Access/WRITE
and server KDG stay gated; no Leave/editor/production/pilot action. The three existing
open investigations remain open. Approved previous storage cleanup removed only
superseded payloads/dependencies; retained diagnostics and qualified toolchains stay.


## ATDD and implementation progress

Implementation child observes acceptance RED before production behavior:
`python3 -m unittest discover -s platform/deployment/tests -p test_pinned_execution.py -k AuthMigrationExecution`
runs1 test with1 error, missing FreshGuard.admit_auth_job. The chosen exact job name is
supabase_auth_migrate_<project>, with API1.48 create query platform=linux%2Famd64.
Independent daemon/state coverage and root verification remain required.

The existing ignored verifier gains one literal `auth-job` mode selecting only
pinned-cli-postgres-auth-migration. Original helper bytes are retained under
`.local/auth-job-qualification/verify-local-before-auth-job.py`; original SHA256
`bb3b866ec6981615263f880804b2ba677cb7661beaeade6df6bea21913e0c627`;
updated SHA256
`4171fb56d488dd9801b3bc3fcd0b68592bfb6eb2214abf36a2fa49567f38965e`.
The negative-injection branch is byte-identical and excludes auth-job. No new runner
or public endpoint is created. Each actual proof requires a fresh qualified UUID;
previous receipts and failed records are never repaired.


Root focused owner suite passes87 tests,1.116s. Smallest new actual private-process
positive passes1 test,4.724s. First affected migration process suite runs3 tests36.145s
and fails the deadline subcase: fake AuthJobDaemon retains a finite deadline from its
unrelated direct-owner priming. Advancing the real-owner test clock also expires that
stale daemon deadline, so the fake peer refuses cleanup despite the actual cleanup
budget transition. Root resets only that unused fake priming deadline to infinity;
the actual retained DockerSession/guard remains the sole bounded owner. The original
cleanup/no-replay assertions and all production budgets stay unchanged. Failure is
retained separately; corrected smallest/affected verification follows.


The smallest rerun still fails1 test11.683s in the same deadline subcase. Further
tracing identifies the decisive injection point: shifting the clock inside the fake
server's start dispatch expires the real HTTP response exchange, which correctly
closes DockerSession. Cleanup cannot reconnect and must preserve uncertain job/PG
resources. No production defect follows from that refusal. Root retains that exact
in-flight case as a separate response-deadline subcase with explicit closed-peer/no-
delete/unresolved assertions, and adds the intended owner-deadline injection after
successful start ACK, before the next observation. That case still requires one
successful bounded owned cleanup. This distinguishes two real contracts rather than
weakening the owner-deadline assertion; all earlier failed outputs remain evidence.


Corrected root process failure check passes1 test31.619s, covering nonzero exit,
owner deadline, in-flight response deadline and interruption. Full affected command
`python3 -m unittest discover -s platform/deployment/tests -p test_resources.py -k auth_migration`
passes3 tests53.710s, including the positive two-process termination-before-dispatch
oracle and its deliberate skipped-termination mutation (which the oracle catches).
Root focused `test_pinned_execution.py` passes88 tests4.006s. A final malformed-image
response regression first reproduces4 AttributeErrors (null/list/string/bool); the
minimal pre-create object guard changes these to safe execution_image_changed
refusals. Focused RED/GREEN and full owner suite pass without job creation.


## First actual refusal and diagnosed correction

Fresh run1d418b00-9f8e-4aaf-8f4a-25ad299e51d1 passes prepare0.097s,
toolchain25.108s and image qualification36.687s. Actual auth-job refuses unsafe_create
after57.331s, preserving13 receipts and running inventory (record SHA256
7afda0d7e14a28033373908cbb783a5a296ec2363b1c398b7236265275d3f4ac).
No passing execution claim follows. Read-only selected image metadata through the
existing DockerSession identifies the mismatch: Docker CLI image inspect normalizes
away default fields; direct API1.48 returns18 keys. The five expected values match,
plus exactly the13 inert API defaults now recorded in profile authority. The original
exact-five-key validator wrongly rejects this valid immutable API representation.
A realistic independent API fixture must reproduce RED before the strict profile
correction; extra or changed defaults remain rejected. Effective container execution
fields remain separate from image-only empty hostname/default metadata. Old failed
receipts remain untouched; source/profile correction requires a fresh qualified UUID.

Job-specific inspect/delete uncertainty audit adds2 tests (immediately GREEN, existing
behavior), then root full focused suite passes90 tests4.708s. These cover malformed
inspect and lost/closed inspection, lost/bad delete ACK and lost/null/still-present
absence proof; no replay or unproven downstream disposal.

Strict correction RED: realistic18-field API fixture makes the smallest fast-zero-exit
acceptance fail unsafe_create (1error). GREEN: separate exact AUTH_IMAGE_API_CONFIG
validates all18 fields; effective job fields retain their existing independent subset.
Changed/missing/extra/default-type mutation checks pass. Root focused suite now passes
91 tests1.229s. Read-only failed-run inspections confirm PG/volume/bridge absent.


## Executed matrix audit

Root executes `python3 -m unittest discover -s platform/deployment/tests -p test_pinned_execution.py`:93 PASS1.675s.
Root executes `python3 -m unittest discover -s platform/deployment/tests -p test_resources.py -k auth_migration`:3 PASS29.924s after effective API-merge correction.

| Frozen row / requirement | Executed passing coverage |
| --- | --- |
| Exact request/current PG; AJ1 | AuthJobExecutionMatrix.test_fast_zero_exit_then_job_disposal_precedes_pg_shutdown_and_disposal; ExecutionSupervisor.test_auth_migration_cli_terminated_before_dispatch_and_owned_disposal; skipped-termination mutation oracle |
| Changed profile/config/custody/PG; AJ2 | AuthJobActualImageApiDefaults (all18 missing keys, changed defaults and unknown key); AuthJobEffectiveDockerMerge; AuthJobArgsEscapedApiNormalization; AuthJobMalformedImageResponse; AuthJobCustodyAndUncertainty.test_changed_pg_instance_health_bridge_and_volume_reference_refuse_before_job_create; existing33 original-profile mutations |
| Fast/nonzero/OOM/dead/malformed/restarted; AJ3 | AuthJobExecutionMatrix fast-zero/nonzero and invalid effective configuration/state matrix; AuthJobCustodyAndUncertainty timestamp/state tests; AuthJobReviewBoundaries malformed PG health/current attachment/strict finish timestamp |
| Uncertainty/deadline/interruption; AJ4 | AuthJobInspectDeleteUncertainty (2 tests); AuthJobExecutionMatrix uncertain create/start/delete; interrupted-create and running-timeout tests; ExecutionSupervisor failure method's four subcases and original-deadline assertions |
| Extra member/mount/port/duplicate; AJ5 | AuthJobExecutionMatrix strict transport and invalid effective configuration matrix; AuthJobCustodyAndUncertainty bridge/volume case; AuthMigrationExecution admission check; legacy terminal single-consumption/original-profile tests |

Every listed test is included in the executed93-test owner suite or3-test process filter;
none is skipped. Actual source-bound qualification and broader legacy regression follow.


Second actual run01bebf25-c4a8-40b9-98a7-c2a1a72aa298 qualifies prepare0.061s,
toolchain15.666s and images32.490s. auth-job refuses execution_cleanup_unresolved
38.742s (record SHA2565a1da1a4f47ef3227c627ed8c4a8c76eb2725b4e180698b48f9f8e6b70e7bd61).
13 receipts remain unchanged; running inventory changes because safe refusal preserves
the PG plus unstarted created job and their volume/bridge. Exact IDs, selected immutable
image/label/reference facts are retained privately in auth-job-qualification/
unresolved-01bebf25.json. No Auth migration job execution occurred.

Read-only inspection plus Moby28 primary daemon/commit.go merge source diagnose
supplied-before-inherited Env order and non-inherited ArgsEscaped. Independent realistic
merge fixture reproduces execution_ownership_changed RED before correction. Effective
checks now require six supplied Env entries followed by two image entries, and omitted
or typed-false ArgsEscaped. Image profile remains exact18 keys with ArgsEscaped=true.
A diagnostic initially misdescribes the omitted field as false and a read-only keyed
lookup raises KeyError; the final realistic omitted-field fixture observes another RED
and protects omitted/false positive and true/int/null/string negative cases. A separate
read-only assertion initially assumes PG labels have no inherited image labels; corrected
selected project-label comparison follows existing PG owner/image-merge behavior. No
mutation/recovery follows either diagnostic error. Root93 focused tests PASS1.675s.

Recovery is separate from qualification. DEVELOPMENT.md preserves lost-custody resources
and authorizes inspection only; exact four-resource cleanup approval is requested while
independent verification continues. No cross-execution adoption/restart or receipt repair.
Numerical correction to the earlier immutable memlog: API image Config has18 fields
(five execution values plus13 inert defaults), not19.


The user explicitly approves exact four-resource recovery. Root holds the existing run
lock, repeats recorded ID/name/image/project-label/mount/bridge/volume-reference checks
before mutations, removes the never-started job, normally stops PG (verified exited0),
removes PG, verifies empty volume/bridge use, then removes only that volume/bridge.
All exact resources are observed absent and13 retained receipts unchanged. Separate
manual recovery completes0.623s; approved-cleanup-01bebf25.json retains selected evidence.
This is not automatic cleanup, qualification success or restored lost custody. No
other Docker resources are removed. Corrected root process suite passes3 tests29.924s.


## Passing actual qualification before review

Fresh source-qualified UUIDead2be18-c5f1-497a-a798-17c03d026569 passes preparation
0.061s, toolchain19.490s and immutable images42.735s. Existing verifier command:

`python3 platform/deployment/.local/pinned-cli-execution-qualification/verify-local.py auth-job ead2be18-c5f1-497a-a798-17c03d026569`

PASS105.475s, exit0. Literal qualifier is pinned-cli-postgres-auth-migration.
Actual CLI health/request validation, CLI termination before dispatch, immutable job
dispatch/exit/disposal, same-instance PG normal shutdown and cleanup are all verified.
No forced shutdown; auth_job_refused=false, fresh_setup_completed=false, runtime_ready=false.
13 receipts and running inventory remain unchanged. Result record SHA256
9a1051d19eabe8e33d3779673ba89644d02e7d97fcba83fb5753a8b9bf1bc8e1; image receipt SHA256
23f797e4088dad05e499d7373b31a6fb99c6565b508bdfc54b2d56b1e5e10b2c.
Exact source hashes are retained in the actual result; old failures and manual recovery
are separate evidence. Legacy controls, full deployment suite and review remain required.


Legacy ead2be18 poststart PASS81.078s, initialized PASS97.251s, persistence PASS82.360s
and ordinary first-start PASS67.864s;13 receipts/running inventory unchanged each time.
Bootstrap refuses images_cli/command_deadline27.565s, preserving13 receipts and running
inventory (record SHA256b1d626127699b8ac7c75d0757625f488ea3b1a067dde026113a889ff4ba2e684).
The serial loop stops. Read-only exact-name inspection finds an unstarted created
env-pg-bootstrap-ead2be18-c5f1-497a-a798-17c03d026569 container ID
621adc552f9b181be107986dd6ad3199bb81db06062243c8585ca8bd9cf9bf82.
Existing run_bootstrap limits each command to10s and consumes creation outside its
known-ID cleanup try/finally. A lost create response intentionally cannot authorize
adoption/removal. This pre-existing control is unchanged by the Auth-job item. Its
resource and failed record remain preserved; no passing retry resolves the lost ACK.
Guarded-fresh regression proceeds separately, and bootstrap needs a fresh qualified UUID.


Guarded-fresh ead2be18 PASS82.476s (13 receipts/running inventory unchanged). Public up
refuses as expected, exit2 runtime_adapter_unqualified0.069s. Separate bootstrap UUID
5a192bdc-12ef-4c87-9ab4-ce7c0bcd62bd passes prepare0.078s, toolchain31.754s,
images44.564s and bootstrap42.137s (13 receipts/running inventory unchanged).
Bootstrap result SHA256a927fb35385b11ebda37547a20592df444b72a1deab97693f3b429cd1d45236e.
Source/profile/limits remain unchanged; this pass does not explain or recover the
original create-response timeout. Read-only selected inspection confirms its exact
container still created, StartedAt=zero, immutable approved PG config, UUID/proof
labels, network=none and Mounts=0. Keep that diagnostic resource and failed receipt;
no deletion, adoption, SQL or restart.

All six legacy controls now have passing evidence on the current frozen source. Exact
commands through the retained verifier (arguments are mode, canonical UUID):

```sh
python3 platform/deployment/.local/pinned-cli-execution-qualification/verify-local.py poststart ead2be18-c5f1-497a-a798-17c03d026569
python3 platform/deployment/.local/pinned-cli-execution-qualification/verify-local.py initialized ead2be18-c5f1-497a-a798-17c03d026569
python3 platform/deployment/.local/pinned-cli-execution-qualification/verify-local.py persistence ead2be18-c5f1-497a-a798-17c03d026569
python3 platform/deployment/.local/pinned-cli-execution-qualification/verify-local.py proof ead2be18-c5f1-497a-a798-17c03d026569
python3 platform/deployment/.local/pinned-cli-execution-qualification/verify-local.py controls ead2be18-c5f1-497a-a798-17c03d026569
python3 platform/deployment/.local/pinned-cli-execution-qualification/verify-local.py up ead2be18-c5f1-497a-a798-17c03d026569
python3 platform/deployment/.local/pinned-cli-execution-qualification/verify-local.py bootstrap 5a192bdc-12ef-4c87-9ab4-ce7c0bcd62bd
python3 platform/deployment/.local/pinned-cli-execution-qualification/verify-local.py tests ead2be18-c5f1-497a-a798-17c03d026569
```

Full-suite diagnostics use the retained runner SHA256
4e60dc7e805ccb3fc02045eb33c697dca0f3f557244dc8c2ce5617b234f54ea5.
It discovers every deployment test and reports safe labels/process states on failure,
then rethrows unchanged assertions; no timeout or assertion relaxation.


Verification ownership note: during implementation the child also ran
`python3 -m unittest discover -s platform/deployment/tests -p test_create_profile.py`
(21 PASS12.604s), which includes synthetic process fixtures despite the no-process
handoff boundary. Root had no simultaneous actual verification, and no child Docker
or actual qualifier ran. Root independently owns the final process/full regression
and every actual Docker qualification. Subsequent child checks stay no-socket.


## Full regression and pre-review closeout

Full deployment discovery PASS582 tests681.384s, no skips (wrapper681.677s, exit0).
Log SHA256e82a0359aa4417ca6c5d876814e1502c7a3d8b10d2e420ac1176c66da671df31;
result SHA256def7d453f0b99aca8f8c1f2578e77d349fcf47aadd10665492a27a159a6b4b2a.
All five matrix rows execute and pass, including all93 focused owner tests and3 new
process tests, with original assertions/limits. All25 actual source bindings still
match current source,13 current receipts are unchanged, and the approved toolchain
receipt records Node26.11.1/npm12.2.0/Python3.15.0/uv0.13.1/Supabase2.120.0/TypeScript7.0.2.
Frozen intent is unchanged. Protected semantic index and baseline HEAD remain unchanged;
concurrent Leave planning/features/UX advanced independently and are preserved, alongside
Expense/PtS work. Root reads the complete baseline diff and subsequent deltas, including
untracked files. All five impact decisions above remain valid. Independent review follows.


## Independent review triage

All three context-free layers complete before triage. Every finding has a separate
verdict/evidence row in the Build record:10 blind findings,1 edge finding and2
verification gaps, plus root's existing bootstrap observation. Root independent
no-socket injections reproduce effective interactive flags, host cgroup namespace,
contradictory Path/Args, paused/restarting flags and finish-timestamp drift incorrectly
qualifying. Root also reproduces pre-delete inspection timeout followed by cleanup
refusal with zero DELETEs. These become minimal profile/custody fixes; successful
repeated running, started-job lost ACK, valid start drift and pre-existing-name gaps
receive focused tests. Namespace findings share one cause; ten patch groups total.

The group-termination concern remains medium-unverified: actual group SIGKILL/leader
reap and the executed two-PID pre-dispatch oracle are established; no controlled live
(non-zombie) same-group descendant surviving that sequence is demonstrated. It is
recorded separately for investigation with PID/start/group/state evidence requirements.
The existing bootstrap create timeout is also deferred separately with exact selected
resource facts; the three prior ENV investigations stay open. One concurrent Leave
handoff finding is real but rejected from this intent: preserve it for its existing
planning owner; root changes no Leave files. No frozen-intent change or new public
surface follows these bounded fixes. All pre-patch passes/failures remain retained;
changed source/profile requires fresh qualification and regression.


Review TDD: independent AuthJobFinalReview starts RED10 tests59 subtest failures.
The existing owner/profile receives minimal typed IO flags, private cgroup mode, exact
Path/Args, typed Paused/Restarting, bound finish timestamp and pre-mutation deletion
consumption fixes. GREEN11 focused tests0.437s; affected AuthJob filter30 tests0.900s.
Root then runs full `test_pinned_execution.py`:104 PASS1.730s. This includes sequential
running success, lost ACK after started state/closed peer, valid start drift, completion
drift, occupied name/unexpected status, pre-delete timeout followed by single cleanup,
and existing lost-delete no replay. No public control/budget or frozen-intent change.
Root process, fresh actual qualification and full regression follow on patched source.


Root patched process suite passes3 tests29.752s. Fresh post-review attempt
89061d14-4b4d-49cb-97e7-1351d1f33c85 refuses prepare before resources:
ports/port_unavailable0.040s. Exact dual-family held-bind diagnostics find only
mail55484/IPv4 EADDRINUSE; all other approved ports/families bind. Read-only selected
socket metadata identifies ESTAB owned by codex PID12899, fd11; no listener. The
connection is preserved, no process is stopped, and the schema/port gate is unchanged.
Failed prerequisites.json is retained; do not overwrite/reuse that run's receipt.
Independent full regression starts on patched source while runtime qualification
waits for normal port availability. This is not a runtime pass or a gate bypass.


The user approves the concrete four-line disposable mail-port proposal15484 after
inspection of the existing target/schema/contract/test. Current55484 lies inside
observed host ephemeral32768–60999 and is held by an established Codex connection.
The proposal changes only mail to15484, outside that range; the original six Auth
inputs, all other ports, production and occupied-port refusal stay unchanged. The
current full run stays frozen until completion, preserving its failures. Root then
observes the new approved config assertion RED before coordinated config/schema/
contract GREEN and fresh source qualification. No active connection is interrupted.


Post-review full run (before approved port correction) runs593 tests644.732s:
88 failures and1 error, exit1. Log SHA256058acbebc03ae4e53eb39e4e5bdab8e41d6c451ff5fd859e4dd8b184515098f3;
result SHA2564286f3a81d7a3b5878cf46f77f03a3188192a62d4092b3738895d2af47a81bba.
Preparation-dependent failures expose occupied55484; missing-config error follows
failed preparation. A separate unchanged Resources.test_integrated_private_handoff_
adversaries_and_drip_deadline fails at drip after14.313s with28 expected-prefix events
instead of29 (last volume GET absent). Its selected owner budget is2s, not relaxed.
This failure remains separately retained and investigated; port correction alone
cannot explain it. Source Auth execution is false on that old metadata-owner path.

Approved four-line patch applies only to target/schema/contract/generated-config
assertion: mail55484→15484. A first pure-config diagnostic needs bytes decoding
corrected; corrected acceptance RED explicitly reports generated55484 versus approved
15484. After the coordinated correction, the same assertion is GREEN, preserving
Auth external URL, and existing test_run_config.py passes8 tests1.829s. Existing
assertion changes only for the user's explicit baseline choice, not to dismiss any
unknown result. No production input, active socket or refusal behavior is changed.


The separate unchanged drip adversary test passes directly in10.003s, with original
2s selected owner bound, exact29 events and descendant-stopped assertions intact.
That pass does not explain the full-run28-event failure or prove it resolved.
It stays an investigation alongside earlier intermittent cases. No production or
expected-result change is made for it. After the approved port correction, root
repeats the104-test focused owner suite and3 process cases before fresh actual checks.


Current-source eb033e51 prepares0.060s and toolchain qualifies19.290s; images refuses
registry/manifest_response_invalid17.845s. Original HTTP status is not retained by
that safe refusal. Existing bounded metadata collector diagnostic then validates
all four selected images/eight artifacts in16.111s, recording only HTTP status,
media and encoding (successful authenticated manifests200, expected challenges401,
identity encoding). No token/body or receipt is published. This does not explain
the original response. An assertion guarding an attempted direct images-only retry
finds its failed directory still present, so the owner is not invoked and no receipt
is altered. Preserve failed directory/record and use a new fresh UUID; no adoption,
repair, timeout relaxation or changed registry validation.


Fresh2cb59147-0378-4fff-bf09-ba3f9e353aa0 prepare0.062s/toolchain18.305s pass;
images again refuses registry/manifest_response_invalid28.350s. Retain its failed
record/lock. The existing private verifier gains only prereqs-diagnostic, observing
safe HTTP status/closed media/encoding categories inside the unchanged images.main
owner invocation; original responses/tokens/bodies are never altered or logged.
Existing limits and source implementations stay unchanged. Helper previous SHA256
4171fb56d488dd9801b3bc3fcd0b68592bfb6eb2214abf36a2fa49567f38965e;
new SHA256d1e2f8de7dab2de2b78cc36abcf12ab7bcca2a93cf098ebebe61889f1c05b46f.
Previous bytes are retained in verify-local-before-registry-diagnostic.py and the
negative-injection branch is byte-identical. New fresh actual qualification uses
that observer to identify any recurrence, rather than infer cause from a separate pass.


## Reviewed-source qualification after approved mail correction

Fresh run `c12d7e47-27f5-457d-8459-57b5d23eca57` passes prepare0.060s,
toolchain19.028s and image owner38.284s. The in-process observer records expected
401 challenges and authenticated200 manifests with identity encoding, under the
original owner limits. This pass does not explain the earlier two registry refusals.
All four immutable child/config identities match the approved baseline.

The actual Auth job passes65.447s: CLI termination precedes dispatch; exact job
exit/disposal, same-PG normal shutdown and bounded cleanup are verified. All13
retained files and the running inventory are unchanged. Record SHA256
`22e6994dafdeace7a6f58b56393097114ad62fc99b08b420bd54800db1d60893`;
image receipt SHA256`65238e6c5113d4afed132228ef32fa1c0ce947df03ae5922f8a478ad64c07786`.
Root independently compares all25 recorded source hashes to current bytes and
startup.source_snapshot(), plus all13 retained receipt/config hashes: PASS.
TypeScript7.0.2 remains pinned. Fresh setup and runtime readiness remain false.

After the approved four-line correction, focused owner/transport tests pass104
tests1.686s, actual private-socket/process cases pass3 tests29.464s and existing
run-config tests pass8 tests1.829s. No assertion or deadline changes dismiss the
separately retained drip failure. Legacy and full current-source checks follow.


All current-run actual/legacy controls pass serially; each retains13 files and
the running inventory unchanged. Records under the private existing verifier run
directory above (SHA256 shown):

| Control | Elapsed | Record SHA256 |
| --- | --- | --- |
| auth-job | 65.447s | `22e6994dafdeace7a6f58b56393097114ad62fc99b08b420bd54800db1d60893` |
| poststart | 62.138s | `f3a135d824cd31ea2bc784fb8906a2c9c20db2af168d9e0697467f3531472622` |
| initialized | 85.813s | `5fbb7dc239fa3bae077c35b5e12a029e64ca3f4903f48ae5b31f7238555c9029` |
| persistence | 91.385s | `887961cda571c233b1e64404d97702f9c3af2f3a974168ef1d6d72f552c7302d` |
| proof | 69.367s | `4657516d8afebb4b6cc594ba6ffbbc3e70b956a0b337829cb638fe60e2ba606f` |
| bootstrap | 29.398s | `eadbf6bc025734b05f9cacebdc3eb4cfcb3c5d9e79b025611fc0e7cb561aba09` |
| controls | 65.67s | `fb977f21a1f333bfb42d08249731d674c3f49f54aecdefb8e44ddae8584e484f` |

Public up refuses with expected exit2/runtime_adapter_unqualified in0.046s.
Full current-source deployment regression is running; its result is recorded below.


## Final closeout

Current-source full discovery PASS593 tests519.852s (wrapper519.996s), exit0,
no skips. Log SHA256`54c0c3c9ce7c35abb84d5cb1155eb9f2dcb5d4dfa65520243705f55a1e893466`;
result SHA256`30da01ae9a26d1123e15badf11e69435e7900bb2428f3fd6c76bcb74bcce0e44`.
Exact root commands after the approved mail correction:

```sh
python3 -m unittest discover -s platform/deployment/tests -p test_pinned_execution.py
python3 -m unittest discover -s platform/deployment/tests -p test_resources.py -k auth_migration
python3 -m unittest discover -s platform/deployment/tests -p test_run_config.py
python3 platform/deployment/.local/pinned-cli-execution-qualification/verify-local.py prereqs-diagnostic c12d7e47-27f5-457d-8459-57b5d23eca57
python3 platform/deployment/.local/pinned-cli-execution-qualification/verify-local.py auth-job c12d7e47-27f5-457d-8459-57b5d23eca57
for mode in poststart initialized persistence proof bootstrap controls; do
  python3 platform/deployment/.local/pinned-cli-execution-qualification/verify-local.py "$mode" c12d7e47-27f5-457d-8459-57b5d23eca57 || exit $?
done
python3 platform/deployment/.local/pinned-cli-execution-qualification/verify-local.py up c12d7e47-27f5-457d-8459-57b5d23eca57
python3 platform/deployment/.local/pinned-cli-execution-qualification/verify-local.py tests c12d7e47-27f5-457d-8459-57b5d23eca57
```

The expected up exit2 is checked separately before tests. The existing tests mode
runs the retained diagnostic discovery runner with unchanged assertions and records
its command/hash; this is not a new scaffold generator or runtime service.

| Requirement | Final passing evidence |
| --- | --- |
| AJ1 | Actual auth-job65.447s; three real process cases prove termination ordering, positive disposal, failures and omitted-termination mutation oracle |
| AJ2 | 104 owner/transport tests including strict image/config/health/start/finish/name continuity;25 source bindings and13 receipt hashes |
| AJ3 | Independent fast-exit, repeated running-to-success and typed/nonzero/OOM/dead/paused/restarting state mutations in focused104 and full593 |
| AJ4 | Lost create/start/inspect/delete, started-but-lost-ACK, no replay, pre-delete check timeout, in-flight transport expiry, owner deadline and interruption tests; all593 pass |
| AJ5 | Forbidden bridge/volume/port/duplicate cases, private cgroup/IO/path/args enforcement; six legacy controls and expected public up refusal |

All three review layers completed before triage; ten patch groups are verified.
Three new investigations remain deferred (descendant-survival claim unverified,
pre-existing bootstrap timeout, drip-event timing cause unverified), alongside three
prior investigations. The current pass does not explain retained registry failures,
earlier drip result or bootstrap timeout. No assertion/deadline relaxation or resource
adoption follows a passing rerun. The exact unstarted bootstrap diagnostic remains
preserved; the explicitly approved01bebf25 cleanup remains a separate recovery record.

Final impacts: existing scaffold/profile/transport/resource/startup owners extended;
shared UI unchanged; existing agent-context rules sufficient; evidence, runbook,
profile, handoff/memlog, Build record and investigation backlog updated. Approved mail
fixture adjustment is coordinated across target/schema/test/contract. Accepted ADRs
unchanged, no new ADR. Source-qualified receipts include that contract/schema revision.
Frozen intent is unchanged. Concurrent Leave/PtS/Expense changes and semantic index
are preserved and excluded from this delivery's18-path local commit. Public runtime,
remaining ENV/P1/SERVICE foundations and dependent delivery stay gated.
