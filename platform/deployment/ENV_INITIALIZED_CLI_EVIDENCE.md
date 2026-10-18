# Initialized-volume CLI restart evidence

Build: [bounded initialized CLI restart](../../_bmad-output/implementation-artifacts/spec-env-initialized-cli-restart.md).
Reviewed-source bounded initialized CLI verification passes, including541 deployment
tests and actual disposable restart qualification. Full environment/runtime readiness
remains false.

## Purpose and authority

The [preceding persistence item](ENV_POSTGRES_PERSISTENCE_EVIDENCE.md) proves one ENV
recreation on a fresh execution-owned initialized volume. This item uses a second
actual pinned CLI process for that replacement's create/copy/start, within the same
retained operation. It does not adopt volumes across operations or complete the CLI's
post-start database setup or full Supabase stack.

Pinned primary source commit
[753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4](https://github.com/supabase/cli/tree/753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4):
[postgres.service.ts](https://github.com/supabase/cli/blob/753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4/apps/cli/src/command-internal/db-bootstrap/postgres.service.ts)
builds the same container specification on fresh/existing volume paths.
[start-database.ts](https://github.com/supabase/cli/blob/753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4/apps/cli/src/command-internal/db-bootstrap/start-database.ts)
probes the volume before network/create; after health it selects fresh setup or
existing-volume webhook convergence, then current-branch initialization. Both CLI
processes terminate at the executed start boundary here, so none of those later
steps is qualified. The exact public create script/archive authorities remain
[the existing profile](fixtures/supabase-pg17-profile.md).

Initialized prefix: missing container, four unordered selected image observations,
existing volume observation, network observation, existing-volume ensure acknowledgement,
validated create/copy/start. The ensure is a guarded acknowledgement of the already
created/current unused volume, not another volume POST. Legacy existing fixture refusal
is not reused as a successful initialized-owner acknowledgement.

## Impact decisions

Scaffold: extend the existing ENV resource/startup/qualification owners and tests;
existing P1/SERVICE generator work remains open. Shared UI: no change. Agent context:
root rules suffice; KDG handoff records actual commands/limits. Documentation: profile,
runbook, this evidence, Build record and consuming handoff/memlog. ADR: accepted
records unchanged; no new decision needed. ADR0020 coordinated owner migrations,
compatibility/activation blocking/recovery remain separate undelivered gates. Synthetic
probe SQL is isolated verification, not an owner migration. ADR0023 safe selected facts
remain; no command/env/archive/SQL output or raw Docker payload dump is reported.

## Required verification

Observe acceptance RED before production changes. Run focused tests, affected
socket/process/startup tests, then full deployment discovery. Each of the six Build
matrix rows needs executed passing coverage. Qualify a fresh source-bound UUID through
prepare/toolchain/images, then actual initialized restart and existing persistence,
pinned-CLI execution, bootstrap and guarded controls. Public up must still refuse
runtime_adapter_unqualified. Retain failed/interrupted attempts and exact output hashes;
never repair receipts, weaken expectations or reset consumed deadlines.

## Remaining gates

Cross-execution initialized-volume admission/reconciliation; post-start CLI database
setup and whole-stack Auth/runtime; owner migrations/fixtures/current authorization;
public lifecycle/reset/recovery; provider/device topology; existing-owner P1/SERVICE
schema/generation/regeneration/custom preservation/locked install/build/start proofs.
Identity/Access/WRITE and server-backed KDG remain gated. No Leave/editor, product
migration/account/grant, infrastructure provisioning, deployment or real-data pilot.

Private preservation checkpoint: the initial new `concurrent.json` was empty when
checked after resume. The empty file is retained separately. All five concurrent
document hashes and index entries were verified against the preceding item's retained
snapshot before writing and rereading a replacement checkpoint at this item's baseline.
No concurrent document or qualification receipt was changed.

## Implementation verification

Exact focused command:
`python3 -m unittest discover -s platform/deployment/tests -p test_pinned_execution.py`.
Direct repository-supported full-suite reproduction from repository root:
`python3 -m unittest discover -s platform/deployment/tests`.
Process/socket cases require local Unix sockets and child-process execution outside a
restrictive sandbox; no real Docker daemon is needed for those unittest fixtures.
The recorded full run below uses the retained diagnostic runner via its private helper;
it invokes the same unittest discovery and adds selected diagnostics for the two older
intermittent guard investigations, without changing assertions/deadlines or skipping tests.
These direct commands reproduce the tests without relying on the ignored helper.

Acceptance RED before production changes:
`python3 -m unittest discover -s platform/deployment/tests -p test_pinned_execution.py -k InitializedCliAcceptance`
ran one test with AttributeError (missing FreshGuard.enable_initialized_cli).
Root initial focused suite passes55 tests0.736s. First initialized process command
`python3 -m unittest discover -s platform/deployment/tests -p test_resources.py -k initialized`
passes2 tests14.961s. Root diff inspection caught an accidental undefined variable in
an unrelated pre-existing PID assertion; the original expectation2 was restored.
No expected refusal/deadline was weakened. Additional secondary transport-failure and
phase-consumption timeout/interruption coverage follows.

Fresh source-qualified run `b0524560-4a20-431a-b25d-7becaab7a949` passes prepare0.096s,
toolchain27.915s and images35.690s. Approved immutable children/configs match the preceding
persistence item, including PostgreSQL child
`sha256:e85bc10ac5b141223b289e1e8dc8d448cf3df92501917149db0366b9c5aaf053`, config
`sha256:c4be96218454e68421a29c712e1a83c7a9fe186208c725d8bb2ebb474e2042f2`.
No image/tag substitution or receipt repair. Actual runtime qualification follows.

Root final focused command passes **56 tests,1.432s**. Expanded initialized process
command above passes **3 tests,58.005s**: successful second CLI, lost marker and four
second copy/start lost/malformed-response subcases. The harness independently requires
one peer, one cleanup attempt, the same FreshGuard, two distinct bound workdirs and
four terminated CLI/descendant processes. Closed-peer uncertainty preserves replacement
resources with no further delete/replay/persistence claim.

| Build matrix row | Executed coverage |
| --- | --- |
| Initialized CLI happy path | InitializedCliAcceptance.test_initialized_cli_has_separate_probe_ensure_and_replacement_authority; ExecutionSupervisor.test_initialized_cli_recreation_keeps_both_groups_and_private_custodies |
| Volume/image/bridge/custody loss | InitializedCliAcceptance.test_missing_changed_used_volume_bridge_and_image_latch_loss_before_mutation; test_both_fixture_and_listener_custodies_are_checked_and_never_rebound; ExecutionSupervisor.test_initialized_second_custody_mutation_latches_before_any_further_mutation; existing full owner descriptor cases |
| Exact phases/token/profile/routing/archive/IDs | InitializedCliAcceptance wrong-phase/repeated-observation, initialized-handoff and observation-prefix tests; ExecutionSupervisor.test_initialized_private_probe_ensure_envelopes_refuse; existing closed copy/start and operand tests |
| Uncertain responses and container-free gaps | InitializedCliAcceptance lost-probe/ensure and uncertain-create cases; ExecutionSupervisor.test_initialized_secondary_supervisor_uncertain_copy_start_preserves_without_replay, test_initialized_unknown_second_create_is_never_adopted and test_initialized_failure_before_secondary_launch_preserves_volume; existing intermediate removal/inspection uncertainty cases |
| Marker/cluster/init/health/unclean exit | ExecutionSupervisor.test_initialized_cli_lost_marker_never_claims_persistence; unchanged fixed SQL and shared owner failure matrix/strict shutdown tests |
| Deadlines/interruption/second supervisor | InitializedCliAcceptance.test_initialized_deadline_and_interrupt_consume_phase_without_replay_or_reset; ExecutionSupervisor.test_initialized_nested_deadline_and_interrupt_terminate_both_groups; second-supervisor transport-failure process cases; existing execution total-deadline/interruption tests |

The initial coverage passed in the focused runs noted above; the533-test pre-review
full regression below includes the unchanged shared owner cases. Added review cases
are recorded with final-source results below. Existing actual SQL predicate
semantics were proved in the preceding persistence evidence; this item's real positive
proof must additionally exercise those unchanged predicates after actual CLI replacement.

## Retained unintended fault-injection attempt

Run b0524560 returns exit2,73.391s, execution_sql_failed, with verified owned cleanup
and unchanged13 receipts/running inventory. Root's private helper extension accidentally
included `initialized` in its existing negative-injection branch. It therefore ran the
literal corrupt-cluster SQL check against the initialized CLI control. This is **not a
positive qualification** and its negative-predicate counter is not used as evidence.
The mode dispatch was corrected only in the ignored helper; production/profile sources
remain unchanged. Its exact prior bytes are retained privately as
`initialized-cli-qualification/verify-local-unintended-injection.py`, SHA256
`5382a1403ac7ec5169d26462b8cb9cacba496463414f57a2e6c02e68a30e14cc`.
Protected b0524560 `initialized.json` SHA256
`04071793b41fa17da42ac10242fd54493243a513978c3d13c5593761e7b2f5bc`.
A fresh UUID qualifies ordinary positive execution; no result/receipt is repaired.

Fresh ordinary run `53a5ec38-821c-40dd-98e3-87c10dd7f954` passes prepare0.066s and
toolchain16.406s; image qualification refuses registry/manifest_response_invalid,
exit2,28.949s. No runtime begins. Its failed prerequisites record stays retained;
another fresh UUID is used rather than borrowing or repairing an image receipt.

Ordinary positive refresh `18d3de94-7ff0-4464-bc99-3e7b5a813395` passes prepare0.178s,
toolchain17.065s and images36.782s, with the same four approved immutable identities.
Corrected private verifier SHA256
`51f9e0b23f4b7ee2651e48519da0bb10aa64a3cfec2c7ea6671ba48c85a9319a`.

## Actual ordinary initialized proof

Run18d3de94 actual `--control pinned-cli-postgres-initialized` passes **exit0,113.594s**.
The result identifies cli_start_count2 and cli_start_boundaries[fresh,initialized],
initialized_cli_recreation_verified, distinct_container_verified, persisted_run_marker,
same_cluster, initialization_markers, both_shutdowns and cleanup verified;
forced_shutdown=false, runtime_ready=false. Root independently checked the saved
result has the exact boundary array and no injection selector. All13 retained files
and running-container inventory are unchanged. Qualified source/profile bindings
match the positive run after execution. Protected `initialized.json` SHA256
`90900dc86c05daba0522d415b4b5bd135e71e796aa44577b17f653c14c59cae7`;
image receipt SHA256
`1493576ccdeee1d78b74348dbcc600a0ae2f48075b2ff13ca90f008e2fca9f22`.
At this checkpoint existing controls, full regression and review were still pending;
their subsequent records appear below.

Existing actual `--control pinned-cli-postgres-persistence` on18d3de94 passes
**exit0,108.949s**, retaining its original cli_first_start_only/owner_start_count2
payload, persisted predicates, both clean exits and disposal. All13 receipts remain
unchanged. Its whole running inventory differs: no prior running entry disappeared;
three unrelated existing Deals containers appeared running (`deals-core-20261015-bench`,
`deals-core-20261015-db`, `deals-core-20261015-redis`). Qualification targets none of
them; their cause is unobserved and current state preserved. No whole-host unchanged
claim is made for this check. Protected `persistence.json` SHA256
`56a0185baa7145cdf2ce0e3227a67c117233237ef9db3184a83a282bd94f067d`.

Existing actual `--control pinned-cli-postgres` on18d3de94 passes **exit0,62.824s**,
retaining first_start_only and verified health/clean shutdown/disposal. All13 receipts
and running inventory remain unchanged. Protected `proof.json` SHA256
`41766a59b9d20f73fcc008495f6d34a8609e01196b9ee38ed75706206b48f1ab`.

Existing actual `--control postgres-bootstrap` on18d3de94 passes **exit0,28.620s**,
including installed role verifiers, JWT/migration/internal-schema/key semantics and
same-instance clean shutdown/disposal. Loopback password enforcement stays separately
false, preserving the original scope distinction. All13 receipts and running inventory
remain unchanged. Protected `bootstrap.json` SHA256
`676ef6bf9ce10cef45b74efed42faf69f553fb2ad9224ec3bb91acd5858e2b8a`.

Existing `--control guarded-fresh` on18d3de94 passes **exit0,69.039s**, retaining
synthetic create/copy and refused first start. All13 receipts and running inventory
remain unchanged. Protected `controls.json` SHA256
`864b3418318f1ce284d5a5254c8ca265915d9d590dada266364df28f870ce073`.
Public `python3 platform/deployment/dev.py up --target platform/deployment/environments/kdg-local.json --run-id 18d3de94-7ff0-4464-bc99-3e7b5a813395`
returns expected **exit2,0.116s**, runtime_adapter_unqualified/runtime_ready=false.
At that checkpoint full discovery began on the unchanged pre-review source; its
completed result is recorded below.

## Full regression and matrix audit

`python3 platform/deployment/.local/pinned-cli-execution-qualification/verify-local.py tests 18d3de94-7ff0-4464-bc99-3e7b5a813395`
passes **533 tests,410.905s** (wrapper411.143s), exit0, no skips. The retained diagnostic
runner discovers the complete deployment suite without altered assertions/deadlines.
All six matrix rows above have executed passing coverage, including shared owner tests.
Protected `deployment-tests.log` SHA256
`e38391df1fee4a3b4eaae42a95a92b194b068ca4e483755660987ebbc4f65ddd`;
`deployment-tests.json` SHA256
`031f83fa1f9929dc8516dd64ec96b8f85cdf94d8793ba7238a4bdfceb2a403d0`.
The two preceding intermittent guard investigations stay open; this pass does not
explain them. Concurrent document/index and proof source/profile bindings are unchanged.
At that pre-review checkpoint, three review layers followed.

## Review and refresh

Three layers completed before root triage. Per-finding verdicts are in the Build log.
Confirmed patches cover stale repeated process-group signaling in the new nested
lifecycle, physical secondary custody failures and additional uncertainty/deadline/
interruption/gap verification. Current-status wording and direct reproduction commands
are corrected here. At this review checkpoint the production patch required a fresh
source-qualified run and final regression; preceding results remain valid only for
their recorded source. Completed refresh results follow below.

Review regression RED: root executed only
`test_resources.ExecutionSupervisor.test_initialized_cli_recreation_keeps_both_groups_and_private_custodies`
with an in-memory copy of `guarded_fixture_command` that disables only its new final
`group_terminated` signal guard. A diagnostic outer wrapper suppresses physical repeat
signals while recording their attempts. **1 test fails,8.322s**, 4 signal attempts for
2 distinct groups, exactly the original regression. Production files remain fixed;
all real first signals still terminate their proven groups. Root focused tests after
patches pass **59 tests,1.948s**. Expanded process checks then preceded fresh source
qualification and full regression, recorded below.

The first expanded process run failed **4 subcases across8 tests,251.929s**.
Malformed-ACK fixtures left a synthetic descendant holding output pipes after the
CLI parent exited; the owner reached a later daemon framing failure rather than
the intended immediate ACK refusal. Only those fixtures now redirect descendant
output to DEVNULL while retaining its group membership and termination assertions;
dedicated inherited-pipe coverage remains. Unknown second-create cases incorrectly
expected a cleanup attempt despite no recorded container ID. Their assertions now
require the original docker_response_invalid, zero cleanup attempts, consumed phase,
closed session, retained unknown replacement/volume/bridge and no adoption, replay
or deletion beyond the old container. Production behavior and deadlines are unchanged.
Deadline tests additionally compare the execution deadline at cleanup entry with
the original secondary deadline; only cleanup receives its separate10s budget.

Final-source prerequisite run `0003c705-2298-46b1-9ad3-cae3650bae46` passes prepare
0.060s, toolchain15.877s and images33.337s, retaining the same approved immutable
image identities. Runtime and final regression results follow.

Smallest malformed-handoff rerun: **1 test,28.930s**, one malformed ensure-envelope
failure. The fixture daemon's5s idle timeout could expire between sequential wrapper
launches; final owner checks then saw daemon EOF and masked invalid_owner_handoff.
Initialized fixture connections now allow120s idle, matching the existing owner
execution budget; production deadlines are unchanged and owner exit closes the
connection. Exact refusal assertions remain, with an added empty daemon-error check.

Final-source actual initialized qualification passes **exit0,80.575s** on0003c705:
the exact boundary array is `['fresh','initialized']`, with all persisted marker,
same-cluster, initialization, both-shutdown and owned-disposal facts true.
Runtime readiness remains false. All13 retained files and running inventory are
unchanged. Root independently verified the boundary array, absence of injection,
source/profile receipt bindings and concurrent document/index preservation.
Protected `initialized.json` SHA256
`6305435537b10e58e5db9f0995d688b4881ce7de0a810493b99b97497d63be77`;
image receipt SHA256
`cdb15edfde017beaefd01a3590eb5eacc729312298cafe5610b6c86c4ce53693`.

## Reviewed-source closeout — 2026-10-18

Root final focused discovery passes **59 tests,1.127s**. Smallest corrected process
reruns pass private_probe **1 test,21.436s** and unknown_second_create **1 test,13.747s**.
Affected initialized process discovery passes **8 tests,116.203s**. The subsequent
full suite also executes the added exact docker_timeout assertion for nested expiry.

All final actual controls use fresh source-bound run0003c705 above:

| Existing control | Result | Protected result SHA256 |
| --- | --- | --- |
| pinned-cli-postgres-persistence | exit0,79.143s | 3879304bcacd059665a498377059946ee512dcae9d94fc11bdb3c88e52b0e5c9 |
| pinned-cli-postgres | exit0,63.725s | aecd51357fdf348d62f8af1d02eae013c91a0cc8a32ee394f3ad3f2ea708e089 |
| postgres-bootstrap | exit0,32.523s | 8017c32371de1c9ce499ddc8bf55090fd89a05aee1231efb3dd2feffc16a50df |
| guarded-fresh | exit0,63.991s | 1bd1a754cf0af804b9723c5c7e6767573218dfaf17e538d38816ad2c6238ae30 |

Each retains its original result semantics, all13 receipts and running inventory.
Bootstrap loopback_password_required remains false. Public up returns expected
**exit2,0.078s**, runtime_adapter_unqualified/runtime_ready=false.

`python3 platform/deployment/.local/pinned-cli-execution-qualification/verify-local.py tests 0003c705-2298-46b1-9ad3-cae3650bae46`
passes **541 tests,439.549s** (wrapper439.761s), exit0, no skips. Root inspected the
completed log. Protected `deployment-tests.log` SHA256
`b88d216379d798a42c4c547c2ec029f47dc8d70e872958fdd83bd8aea15bd2b0`;
`deployment-tests.json` SHA256
`e789709eaa6e6448c97dc4ccc84a48f6afdb9b970fde877dcb1dc4678bf6d819`.

All six requirement rows have passing focused/affected/full coverage. Three-layer
review and root patch verification are complete: B1 signal regression fixed;
B2/B3/V1 secondary custody, B4 expiry, B5 interruption, B6 private exchange, B7 unknown
replacement and B8 launch-gap cases pass; B9/B10 documentation corrections are complete.
No new deferred item or loopback. The two preceding intermittent guard investigations
remain open. Five impact decisions above remain binding. Final source/profile bindings,
concurrent document hashes/index and scoped diff checks are verified before commit.
