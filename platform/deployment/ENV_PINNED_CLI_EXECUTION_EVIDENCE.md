# Guarded pinned-CLI PostgreSQL execution evidence

Build: [bounded ENV execution](../../_bmad-output/implementation-artifacts/spec-env-pinned-cli-postgres-execution.md).
The [environment contract](../docs/architecture/contracts/scaffold-environment-and-generation.md)
and existing deployment owners retain authority. The explicit disposable execution proof passes on final source. Runtime readiness
remains false; final regression and independent review are recorded below.

## Purpose and boundary

The pinned Supabase CLI must actually emit its first create/copy/start commands.
The retained ENV owner validates their exact original operands, selected immutable
image, public synthetic inputs and archive before dispatch. A separately hand-built
container command cannot establish that CLI execution continuity. Default proof
controls remain synthetic; full `dev.py up` stays gated.

The execution profile deliberately tightens resource use and restart/log behavior;
the source-bound profile records exact differences. Existing standalone volume
admission remains strict. The executing owner admits only its verified recorded
container as a volume reference after creation, and refuses every additional reference.
A running/healthy observation is distinct from the separate SQL/bootstrap proof and
from future initialized-volume reuse or recovery acceptance.

Docker transport follows the [Docker API1.48 reference](https://docs.docker.com/reference/api/engine/version/v1.48/)
and its [versioned publisher schema](https://raw.githubusercontent.com/moby/moby/v28.0.0/docs/api/v1.48.yaml).
Only selected owner lifecycle/archive routes are added; this is not an arbitrary
Docker proxy. Archive bytes and success bodies require their own bounded framing.
Lost responses never authorize mutation replay or adoption.

Read-only preflight on Engine29.9.1 requested the exact cached PG child image's
API1.48 inspection. It returned status200, `Transfer-Encoding: chunked`, no
Content-Length. The old transport's chunked rejection would prevent actual owner
execution. The transport therefore needs bounded chunked decoding as part of this
item, with fragmented/ambiguous/over-limit framing regressions; this is an observed
runtime input, not a changed expected result to conceal an unexplained failure.
Selected safe header evidence is retained under the preceding run's
`.local/pinned-cli-execution-qualification/885056ba-e9dc-41a2-9e3e-f207d75bdeb2/framing.json`.
No response payload was printed or retained.

## Verification record

Implementation agent observed ordered-dispatch acceptance RED before production
changes: one test errored because the existing FreshGuard had no execution entry.
The added test then passed after retained-owner implementation. Root's intermediate
`python3 -m unittest discover -s platform/deployment/tests -p test_pinned_execution.py`
passes **16 tests,0.124s**, including lifecycle, ownership, transport and deadline cases.
The implementation agent also ran19 selected legacy CompleteCreateProfile cases,
all passing. After the pending-network characterization below, root repeated the
same focused command: **19 tests PASS,0.146s**. Final broader verification is recorded below.

Fresh run `638ce20b-ceac-4da5-8cd7-466b2af6650a` qualified prepare0.062s,
toolchain14.817s, images34.112s. Its first explicit public `pinned-cli-postgres`
control refused startup/unknown_control, exit2,10.341s: the internal
synthetic_probe allowlist omitted the new control. All13 retained files and the
running inventory were unchanged; no layers were downloaded or resource execution
reached. Protected `proof.json` SHA256
`a5e4026951a234e16e900057059f161517aba9da9d585a2c30e8a784ffc3463d` under
`.local/pinned-cli-execution-qualification/638ce20b-ceac-4da5-8cd7-466b2af6650a/`.

Additional characterization then observed RED for that omitted allowlist and
out-of-band starts before copy/start. Minimal fixes added the internal entry and
require created/nonrunning state before those mutations. Original five-second
acquisition also cannot borrow the new execution budget. These are explained behavior
corrections; earlier owner receipts remain unchanged and a new UUID qualifies final
source bytes. Root performs actual Docker/socket/process checks serially.

Intermediate source run `29dbed97-1dc4-48a4-9b63-d079feec118b` qualified prepare0.058s,
toolchain16.984s, images38.431s; no actual control ran there. Further primary-source
tracing found creation records retain the supplied endpoint settings before network
allocation ([Moby create](https://github.com/moby/moby/blob/v28.0.0/daemon/create.go),
[network settings](https://github.com/moby/moby/blob/v28.0.0/daemon/container_operations.go)).
A never-started created container may therefore have empty endpoint NetworkID.
The new focused characterization failed ownership validation before the correction.
The owner now permits pending empty ID only with strict never-started created state,
retains exact configured NetworkMode/current bridge checks, and requires exact observed
ID after any start attempt. Foreign IDs and late clearing still refuse. This source
change requires a fresh UUID; the intermediate receipts stay unchanged.

Intermediate run `b349b6d5-e41b-485b-8ca7-4f763f238034` qualified prepare0.057s,
toolchain14.792s and images43.499s. All approved direct pins remain selected,
including TypeScript7.0.2; child/config identities match preceding qualified receipt.
Only the three missing exact digest images were downloaded before actual execution.

The preflight read-only cache check using preceding run
`885056ba-e9dc-41a2-9e3e-f207d75bdeb2` found its exact PostgreSQL child present;
Kong, GoTrue and PostgREST children absent. This is cache observation only, not a fresh
source qualification. Root subsequently qualified source bytes before downloading only
missing receipt-bound digests and executing the actual disposable control.

## Impact decisions

Scaffold: extend the existing environment/transport/resource/profile/startup owners
and qualification entry point. No parallel generator, runtime service or delivery
workflow. Shared UI: no product UI or reusable UI change. Agent context: existing root
rules suffice; update the KDG handoff with actual commands and limitations.
Documentation: source-bound profile, this evidence, development runbook, next-session
and memlog. ADR: no accepted decision is edited; no business schema/release activation
is introduced. ADR0020 migration coordination remains a later environment acceptance
obligation. Selected structured diagnostics follow ADR0023 without payload/credential
dumps. Root inspected the actual source/test/profile/runbook diff against these decisions;
independent review disposition is recorded below.

## Remaining gates

Actual whole-stack startup, owner migrations/fixtures/current authorization,
initialized-volume reuse/reset/recovery, public stop/verify, provider/device topology
and P1/SERVICE generation remain open. Identity/Access/WRITE and server-backed KDG
wait for the foundation. No Leave/editor, real accounts/grants, production migration,
infrastructure provisioning, deployment or real-data pilot is part of this item.

## Affected suites and first real execution attempt

Root ran `python3 -m unittest discover -s platform/deployment/tests -p <pattern>`
serially for six affected suites: Docker session17 PASS0.396s, Docker gate15 PASS0.474s,
create profile21 PASS11.814s, startup lifecycle19 PASS50.087s, PostgreSQL bootstrap40
PASS0.440s and resources39 PASS159.273s: **151 tests PASS**. Protected per-pattern
logs and `affected.json` live under the b349b6d5 run directory above. Both earlier
intermittent resource tests passed; their prior deferred investigations remain open.

All four exact qualified children were inspected present after downloading only the
three missing digests; PostgreSQL was reused unchanged. Then the explicit real
control on runb349b6d5 returned startup/invalid_owner_handoff, exit2,25.085s.
All13 retained files and running inventory stayed unchanged. Protected `proof.json`
SHA256 `5e877cc535a4e626aaeb743e5d57ea56937416a4e434342e8eecf8f692dbc0ac`.
Read-only exact run-resource inspection afterward found its deterministic PostgreSQL
container, volume and bridge all absent; no manual deletion or same-run replay occurred.

Source diagnosis found create-specific environment requirements were incorrectly
applied to copy/start. The real CLI supplies four public container inputs to create,
while copy/start inherit only Docker routing context. New parent-envelope and
fake-socket serialization cases reproduced this mismatch before correction (one
serialization failure and two phase3/4 errors). Create still requires all four inputs;
copy/start carry only routing context, and routing drift refuses in every phase.
Root's same focused execution command now passes **22 tests,0.160s**, exit0.
Source/profile changes require fresh qualification; every prior run remains retained.
The CLI process group is deliberately terminated at the first executed start; any
successful `forced_shutdown=false` refers to the separately observed PostgreSQL exit,
not to completion of whole CLI startup.

## First successful real pinned-CLI proof

Fresh corrected run `ddfe3ded-b668-4497-a210-2f8feba701ad` passes prepare0.057s,
toolchain15.140s and images32.052s, with the same selected child/config identities
already cached. Exact command:

```sh
python3 platform/deployment/tests/qualify_startup.py --target platform/deployment/environments/kdg-local.json --run-id ddfe3ded-b668-4497-a210-2f8feba701ad --control pinned-cli-postgres
```

**Exit0,57.455s**: container_executed, named_volume_verified, healthy_verified,
shutdown_verified, cleanup_verified and first_start_only true; forced_shutdown=false,
runtime_ready=false. All13 retained files and running inventory unchanged. Protected
`.local/pinned-cli-execution-qualification/ddfe3ded-b668-4497-a210-2f8feba701ad/proof.json`
SHA256 `7f07e45b37b31ea3b6f14a698c6fc44c70ad6e2ded2979cf9e3ae5faa7d13e8d`.
The retained record binds exact source hashes and image receipt, not runtime payloads.

Before final verification, source inspection identified a cleanup failure edge:
finish_execution's failed cleanup could be entered again from the outer finally,
resetting its budget and retrying deletion. A consume-once cleanup guard and focused
RED/GREEN regression were then completed. The successful proof above remains evidence
of its exact earlier source bytes; final qualification below follows the correction.

## Cleanup regression and requirement traceability

Two new cleanup regressions failed before production fixes: repeated failed/timeout/
interrupted cleanup repeated15 requests including deletion, and completed cleanup
reset its deadline from110 to119. The owner now consumes cleanup_attempted before
setting its single ten-second deadline; the supervisor finally preserves the first
cleanup outcome. Duplicate calls cannot inspect, mutate or reset the deadline.
Root's focused command passes **24 tests,0.220s**, exit0, after this correction.
Source-bound profile and module descriptions match the new explicit execution control.

During test editing, an invalid1953-NUL gap prevented import. It was excluded from
behavioral RED evidence; the implementation agent preserved the bytes and removed
only that invalid gap before observing the intended assertions fail. Root retained
snapshot `test-byte-anomaly.bin` SHA256
`cea2564121c6ff19c556d0825128aa843d69dcb271907452b2990c1c678fc865`
in the protected qualification directory. Cause unobserved; valid test content and
expectations were preserved. After resume an unavailable temporary helper failed
before execution; retained proof records were intact. Private orchestration was
restored in ignored protected evidence storage, without changing delivery tooling
or repairing source-bound receipts. Neither unavailable invocation counts as a pass.

All named tests below are in `test_pinned_execution.py` and ran in the focused suite.

| Requirement / matrix row | Tests and additional evidence |
| --- | --- |
| Ordered exact real dispatch and returned ID | `PinnedExecution.test_ordered_real_dispatch_records_actual_id_and_consumes_phases`; explicit actual qualifier |
| Named volume, health, same-instance clean stop and removal | `FullRetainedOwner.test_named_volume_dispatch_health_strict_shutdown_and_proven_removal` |
| Preserve existing matching bridge | `FullRetainedOwner.test_existing_matching_bridge_is_preserved` |
| Existing/uncertain creation, no replay | `PinnedExecution.test_existing_or_uncertain_create_is_consumed_without_adoption_or_replay` |
| Only selected container may reference volume | `PinnedExecution.test_extra_volume_reference_latches_loss_before_later_cleanup` |
| Descriptor loss stays latched after restoration | `FullRetainedOwner.test_every_selected_descriptor_drift_latches_deletion_refusal`; existing resource custody cases |
| Exact input/ID/archive/order | `PinnedExecution.test_invalid_original_profile_never_dispatches`; `PinnedExecution.test_copy_start_only_recorded_id_archive_and_exact_phase` |
| Retained-only execution routes | `RetainedExecutionTransport.test_execution_routes_require_persistent_owner_before_connect`; unchanged one-shot network rejection |
| Strict empty/chunked response framing and closed routes | `PinnedExecution.test_fixed_transport_and_empty_success_framing_without_socket`; `PinnedExecution.test_chunked_fixed_route_fragmentation_and_ambiguous_framing`;17 legacy session/15 gate cases |
| Health/shutdown/cleanup total budgets | `FullRetainedOwner.test_health_shutdown_and_cleanup_have_distinct_total_deadlines` |
| Preserve original acquisition bound | `FullRetainedOwner.test_execution_opt_in_does_not_extend_five_second_volume_acquisition` |
| Interrupted/unclean execution cannot qualify | `FullRetainedOwner.test_interruption_retains_owned_cleanup_and_never_qualifies`; `FullRetainedOwner.test_unclean_state_and_restarted_instance_never_claim_clean_removal` |
| Pending created attachment versus actual started ID | `ExecutionEntry.test_never_started_created_pending_network_allows_copy_and_start`; pending foreign/started-state and after-start clearing cases |
| Internal actual entry remains reachable | `ExecutionEntry.test_internal_execution_control_reaches_existing_prerequisite_validator` |
| Phase-specific sender/parent envelopes | All three `ExecutionEnvelope` tests: routing-only copy/start, full create inputs, routing-drift refusal and exact serialized envelopes |
| Cleanup failure consumes one attempt without new budget | Both `CleanupConsumeOnce` cases: failed/interrupted/timed-out and completed cleanup |
| Required aliases survive reattachment | Both `EndpointAliases` cases: either missing alias latches refusal; Docker-added names allowed |
| Supervisor automatic cleanup, descendants and uncertain transport | All three `test_resources.ExecutionSupervisor` cases, including four lost/malformed response scenarios and missing-cleanup mutation |

## Pre-final source qualification and actual proof

Refresh `45780eb4-241d-498b-ad36-f5d2ed5df069` passed prepare0.067s and
toolchain14.812s; image qualification refused `manifest_response_invalid`, exit2,
25.498s. No execution began. That failure remains retained; no receipt was repaired.

Fresh pre-final run `6254efd8-e0db-42c0-92e8-b506fb24eea4` passed prepare0.066s,
toolchain19.264s and images34.862s. Exact selected child/config identities remain
unchanged from the first successful proof. Actual command:

```sh
python3 platform/deployment/tests/qualify_startup.py --target platform/deployment/environments/kdg-local.json --run-id 6254efd8-e0db-42c0-92e8-b506fb24eea4 --control pinned-cli-postgres
```

**Exit0,83.893s**: container_executed, named_volume_verified, healthy_verified,
shutdown_verified, cleanup_verified and first_start_only true; forced_shutdown=false,
runtime_ready=false. All13 retained files and running inventory unchanged.
Protected `proof.json` SHA256
`12d4a3f0776937744e284fa0453045eab53d8677991f37b9d740171982f2cd2d`;
image receipt SHA256
`aee990c8d543074ee9f7b8c328500d754dca470e1e2a8d70058681b54d271ee1`.
These source-bound records are under
`.local/pinned-cli-execution-qualification/6254efd8-e0db-42c0-92e8-b506fb24eea4/`.

Existing actual `--control postgres-bootstrap` passes **exit0,28.459s**, including
SQL/key checks, same-instance clean shutdown and removal. Its13 retained files and
running inventory stay unchanged; `bootstrap.json` SHA256
`1948db3a467375b56601daee45c6d333c29bb415c886f0aa3b8577fb91aab36d`.

Existing actual pinned-CLI `--control guarded-fresh` passes **exit0,67.063s**,
with first_start_refused=true and synthetic_create_acknowledged=true, confirming
the default boundary remains synthetic. All13 retained files and running inventory
stay unchanged; `controls.json` SHA256
`f5704ffdf884115923443aecd8b10f497dc3b11f4b6e2ca1f0d38e80260b29c6`.
Public `python3 platform/deployment/dev.py up --target platform/deployment/environments/kdg-local.json --run-id 6254efd8-e0db-42c0-92e8-b506fb24eea4`
returns expected **exit2,0.052s**, `runtime_adapter_unqualified`, runtime_ready=false.

## Regression-found transport boundary correction

The first full deployment attempt on run6254efd8 exposed the unchanged
`test_networks.BoundedTransport.test_arbitrary_routes_methods_and_requests_are_rejected_before_connect`:
new network deletion also reached the old one-shot exchange. Its expectation was
preserved. A new no-socket ten-route characterization failed before correction;
new execution container inspection/mutation routes now require a persistent retained
owner session. Existing one-shot read/acquisition routes retain their boundary.
Implementation agent reports25 focused tests PASS0.285s and the unchanged legacy
case PASS0.002s; root independently verifies the final source below. Earlier actual
proofs remain bound to their prior bytes; another UUID is required after this fix.

Root's first full attempt completed **493 tests,297.639s,exit1**, exactly one failure
in the unchanged one-shot network-delete rejection above. Durable output SHA256
`0a64f92b1481740d98358b4988d7fb072290f95ed648040f433db32757e380e1`;
`deployment-tests.json` SHA256
`01677bf5c0dbdfe71fc9a9019ca92b06f88e4c7a81684e7abbfa5918c26b5a61`.
Root independently repeated final focused suite: **25 PASS0.207s** and unchanged
legacy case **1 PASS0.001s**. No assertion or timing allowance changed.

## Corrected final-source qualification

Run `ce618f1e-95f2-4920-af03-afd9a2b973a4` passes prepare0.062s,
toolchain19.976s and images46.927s; all selected child/config identities remain
unchanged. The same explicit `qualify_startup.py --target platform/deployment/environments/kdg-local.json --run-id ce618f1e-95f2-4920-af03-afd9a2b973a4 --control pinned-cli-postgres`
passes **exit0,72.656s**, all execution/health/shutdown/cleanup/first-start facts true,
forced_shutdown=false and runtime_ready=false. All13 retained files and running
inventory unchanged. Protected records under this run directory include
`proof.json` SHA256
`bd9b2029ebe9fe051b0d039cd4249f186e0e989b988f7d060b53d40b6ac3efcd`,
with image receipt SHA256
`9896b0aacd004dd080ee8def15cc250d7085e843dd86beaf7bdc9871084f6755`.

On the same final run, existing actual `--control postgres-bootstrap` passes
**exit0,35.085s**, including SQL/key, strict shutdown and cleanup checks;
`bootstrap.json` SHA256
`7be5267a249dfe3173eaf1df23b4f885a4c933a17133f2193426b8eaabfbab21`.
Existing pinned-CLI `--control guarded-fresh` passes **exit0,88.209s**, retaining
synthetic create and refused first start; `controls.json` SHA256
`9996fc77e86a4a5abf0d99974ec7b29d5b468b6337aa65d8e2f324ceb1d0e3a9`.
Both preserve all13 retained files and running inventory. Public `dev.py up` with
that target/run remains **exit2,0.054s**, runtime_adapter_unqualified/runtime_ready=false.
Root compared all25 proof-bound source hashes after execution: unchanged.

Final root complete deployment discovery passes **494 tests,294.641s,exit0**.
It uses the retained diagnostic runner with unchanged unittest discovery/assertions;
selected diagnostics add evidence only, never retries/skips or expectation changes.
Exact command `python3 platform/deployment/.local/pinned-cli-execution-qualification/ce618f1e-95f2-4920-af03-afd9a2b973a4/full-diagnostic-runner.py`;
log `deployment-tests.log` SHA256
`b30fb46878177d9f47db872a2aef380eb0e8f7eb6f13a3392e14f32926afeb84`;
record `deployment-tests.json` SHA256
`f774f237a7ff90c88f6800c17527ef274dd0442405847749f582d5b665f4f17c`.
Both previously deferred intermittent guard cases passed here; their earlier
unexplained failures remain open in deferred-work and are not claimed fixed.
Every matrix row has executed passing coverage in the traceability table.
`git diff --check` passes. Three independent BMAD review layers follow.

## Independent review disposition

All three BMAD layers completed before root triage. Edge-case review returned no
findings. Root recorded each of ten blind findings and the verification-gap finding
separately in the Build spec. Two patch groups remain: required network aliases in
the current endpoint descriptor, and integrated supervisor execution/failure cleanup
coverage (including uncertain archive/start responses). Other claims are refuted or
rejected as low diagnostic enhancements with reasons; no new deferred item.
Root will verify patched bytes with a fresh source-qualified run; the preceding
494-test/actual proofs remain retained against their exact earlier source bytes.

Review patches: required-alias mutation first failed before the direct guard fix;
root **27 focused execution tests PASS0.205s** afterward. Docker-added names remain
accepted; missing either requested alias latches ownership loss.

First integrated fixture attempt failed3 tests/five scenarios before lifecycle
admission because its independent daemon templates used a foreign UUID; it is not
production behavioral RED. Test-only correction binds templates to the actual
prepared target/UUID. Safe lifecycle-reached/recorded-ID/refusal assertions precede
the cleanup assertion so the mutation control cannot pass vacuously.

Root `env PYTHONPATH=platform/deployment/tests python3 -m unittest test_resources.ExecutionSupervisor`
then passes **3 tests,12.187s**. Real private Unix peer, production DockerSession,
retained FreshGuard, supervisor and synthetic CLI/descendant processes prove:
post-start invalid health automatically performs one <=10-second owned forced
cleanup and terminates descendants; copy/start lost/malformed responses close the
peer, retain unresolved resources, never replay/claim success, and terminate
descendants. The third case removes only the supervisor finally cleanup invocation
in a test-only compiled function and detects the specific missing-cleanup assertion
after proving actual create/start was reached. No production source is mutated.
Protected `review-tests-first.json` and `review-tests-final.json` retain results.

## Final reviewed-source proof

Run `2a794d89-260c-4b4c-a8dc-34c7650fc2dc` passes prepare0.059s,
toolchain16.532s and images33.163s, same approved child/config identities.
`python3 platform/deployment/tests/qualify_startup.py --target platform/deployment/environments/kdg-local.json --run-id 2a794d89-260c-4b4c-a8dc-34c7650fc2dc --control pinned-cli-postgres`
passes **exit0,63.366s**. All execution/named-volume/health/clean-shutdown/cleanup/
first-start facts true, forced_shutdown=false, runtime_ready=false. All13 retained
files and running inventory unchanged. This includes actual created/running/stopped
endpoint alias observations after the review patch. Protected `proof.json` SHA256
`d2081df4e3cc0a6e1cb9fca4f2fead1e199296d6d6b41e3d53c6ae529e170921`;
image receipt SHA256
`2ed75ae159c6772e2ee78e8e3f88c0a21dd9e4407f6560bcf09a14a7383b61d5`.
Records reside under this run in the protected qualification directory above.

Same reviewed-source run: actual bootstrap **exit0,31.555s**, strict shutdown and
cleanup verified; `bootstrap.json` SHA256
`b19d3ce0e0d072f5f2440215114b8a2a2d1bc398e9b0cebd4a90af8ccfbb44c2`.
Existing pinned-CLI guarded-fresh **exit0,68.506s**, still synthetic with first start
refused; `controls.json` SHA256
`8bd3ec180c875e596fb6176b55cc00eed7cc16756dabe91442fea8a774a2e089`.
Each preserves all13 retained files and running inventory. Public up stays expected
**exit2,0.055s**, runtime_adapter_unqualified/runtime_ready=false. Root independently
compared all25 proof-bound source hashes and five concurrent documents/index entries:
unchanged. Final reviewed-source full regression result follows.

Final reviewed-source full deployment discovery: **499 tests PASS342.433s,exit0**.
Exact retained command:
`python3 platform/deployment/.local/pinned-cli-execution-qualification/2a794d89-260c-4b4c-a8dc-34c7650fc2dc/full-diagnostic-runner.py`.
The runner preserves original discovery/assertions and adds only selected failure
diagnostics; no skip, retry or expected-result/deadline change. Durable
`deployment-tests.log` SHA256
`f842a478cf8797f413e3887336afbb84c042ee93034f09ded2bdd122e1d2149d`;
`deployment-tests.json` SHA256
`4c722c08478423dc37dafa8f1f3ef8b8eb5a427efc3687058c034f0b6bbb22df`.
All named traceability cases ran, including the integrated review regressions.
Three-layer review and root verification are complete; no new deferred item.
The two pre-existing intermittent guard investigations remain open. Final five
impact decisions remain as recorded above; no UI, agent-rule or accepted-ADR edit.
This bounded execution Build is complete. Enclosing ENV/P1/SERVICE remains partial.
