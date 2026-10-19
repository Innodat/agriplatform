# ENV observed Kong container projection correction

The two-field correction is implemented and selected synthetic verification passes.
Fresh actual qualification still refuses at a newly exposed post-start OOM-default
projection; actual Kong lifecycle acceptance remains open. This increment changes
only missing-null OnBuild and protection ordering at the existing validator. Baseline commit is
9e01fa31cfd6ffcfca5243a8543b80f9709670ed; the tested worktree includes the explicit
validator and two test-module changes bound in the local source manifests. Do not
interpret the baseline as an unmodified tested source commit.

The preceding [failed actual qualification](ENV_KONG_ACTUAL_EVIDENCE.md) remains
historical evidence, including its separately approved exact cleanup. This increment
adds no general default-field admission or new Docker transport/create authority.

## Requirement-to-test evidence

| Requirement | Covering selector |
| --- | --- |
| Omitted null OnBuild alone, path permutation alone, and combined through created/running/exited lifecycle and cleanup | test_pinned_execution.KongExecutionOwner.test_observed_null_omission_and_protection_order_complete_owned_lifecycle |
| Non-null OnBuild, missing/extra/duplicate/malformed protections and other missing-null Config fields still refuse, latch custody loss, no cleanup/re-execution | test_pinned_execution.KongExecutionOwner.test_projection_normalizations_keep_nonnull_and_invalid_protections_closed |
| Actual observed projection over private Unix wire and public process qualifier | test_resources.ExecutionSupervisor.test_kong_execution_process_observed_container_projection |
| Canonical projection and existing custody/failure controls | full KongExecutionOwner and existing selected process/contract controls |

## Impact decisions

Scaffold: fix the retained ENV validator and its existing owner/process qualification
fixtures; generator/schema/client templates stay with existing owners, and consuming
scaffold proof remains open. Shared UI: no surface change. Agent context: no new rule
or root instruction edit. Documentation: this record, runbook and KDG handoff/memlog
track exact commands/results and remaining gates. ADR: existing isolation, release,
custody and safe diagnostic decisions apply; no new or amended accepted ADR needed.
Approved TS7.0.2, CLI/image pins and mail15484 remain unchanged.

Native keys/functional Auth routing, remaining ENV services and consuming scaffold
acceptance still precede Identity/Access/WRITE and server-backed KDG. Production,
access/account changes, provisioning, deployment and real-data use remain outside scope.

## Acceptance and focused TDD

- Before runtime change, owner acceptance RED: four positive observation subcases reject startup/unsafe_create. Exact command: `PYTHONPATH=platform/deployment:platform/deployment/tests python3 -m unittest -v test_pinned_execution.KongExecutionOwner.test_observed_null_omission_and_protection_order_complete_owned_lifecycle`. Exit1, runner1.608s,47 unchanged bindings. Result/log: `.local/kong-projection-correction/owner-red{-result.json,.txt}`. Source manifest SHA256 `bc5626292705b67952aa179ff1fe403c546099bd9d7322d8af850f21c0f837d2`; log SHA256 `04886e8028054d46fe18f3081502790a9850cf7da21447a9b85aeb851f126c55`.
- Before runtime change, private-process/public qualifier acceptance RED: status2 instead of0, startup/unsafe_create. Exact command: `PYTHONPATH=platform/deployment:platform/deployment/tests python3 -m unittest -v test_resources.ExecutionSupervisor.test_kong_execution_process_observed_container_projection`. Exit1, runner21.773s,47 unchanged bindings. Result/log: `.local/kong-projection-correction/process-red{-result.json,.txt}`. Source manifest SHA256 `bc5626292705b67952aa179ff1fe403c546099bd9d7322d8af850f21c0f837d2`; log SHA256 `39984e61086c1100998f4e9c1b73d4e85e404369bf8029449b78582d0cb5bb21`.
- Before runtime change, existing closed behavior characterization GREEN:27 malformed projection subcases. Exact command: `PYTHONPATH=platform/deployment:platform/deployment/tests python3 -m unittest -v test_pinned_execution.KongExecutionOwner.test_projection_normalizations_keep_nonnull_and_invalid_protections_closed`. Exit0, runner36.167s,47 unchanged bindings. Result/log: `.local/kong-projection-correction/negative-characterization{-result.json,.txt}`. Source manifest SHA256 `bc5626292705b67952aa179ff1fe403c546099bd9d7322d8af850f21c0f837d2`; log SHA256 `a933383d66e32bb328bc826fdd06503a9db7ec15874afed3e48788afa5031fce`.
- After narrow correction, all16 owner methods GREEN. Exact command: `PYTHONPATH=platform/deployment:platform/deployment/tests python3 -m unittest -v test_pinned_execution.KongExecutionOwner`. Exit0, runner154.54s,47 unchanged bindings. Result/log: `.local/kong-projection-correction/focused-green{-result.json,.txt}`. Source manifest SHA256 `0830f7f36ea9bc4b6578de558d0f8b5a736de53aee4d1c6a172537a685c18ae9`; log SHA256 `793ddedf7dceaeefb1565a7921332e904712484948257b6da7044a899971c848`.

The red owner call runs one method/four subcases; the negative characterization runs
one method/27 subcases. Counts are not inflated into separate unittest method IDs.
Only validate_kong_container changes at runtime: one omitted-null field normalization
and exact duplicate-free string-set comparison for the two required protection lists.
The approved create request, pinned-image Config check and all other Config fields
remain unchanged. Full canonical owner coverage is retained independently of the
observed-shape process variant.

## Affected and process regression

- 133 methods PASS, no skips. Exact command: `PYTHONPATH=platform/deployment:platform/deployment/tests python3 -m unittest -v test_create_profile test_docker_session test_docker_gate test_startup_adapter`. Runner24.605s. Source manifest SHA256 `0830f7f36ea9bc4b6578de558d0f8b5a736de53aee4d1c6a172537a685c18ae9`; log SHA256 `ddb806466a250b90e86468a9eeb839a0acf43b8992fef45b31b955ed6b27a493`. Result/log: `.local/kong-projection-correction/affected{-result.json,.txt}`.
- 3 methods PASS, no skips. Exact command: `PYTHONPATH=platform/deployment:platform/deployment/tests python3 -m unittest -v test_resources.ExecutionSupervisor.test_kong_execution_process_observed_container_projection test_resources.ExecutionSupervisor.test_kong_execution_process_ordered_lifecycle_and_post_cleanup_fact test_resources.ExecutionSupervisor.test_kong_boundary_process_source_intent_and_cleanup`. Runner88.23s. Source manifest SHA256 `0830f7f36ea9bc4b6578de558d0f8b5a736de53aee4d1c6a172537a685c18ae9`; log SHA256 `45b284216b89ece0712511b0a2ba712127eeeaad1fabc13480016f9849cf30a7`. Result/log: `.local/kong-projection-correction/process-green{-result.json,.txt}`.

Together with focused-green,152 distinct selected method IDs pass on the same47-file
source/test/authority frame. This is affected verification, not a repository-wide
suite claim. The three private-process controls cover observed projection, canonical
projection and the separate Kong refusal boundary, all serially.

## Fresh actual qualification — refused after startup

Fresh run `b32e04df-ffb0-4a36-ab23-c66e5b1f29ba`, tested worktree bindings above. All commands
were serial, with the same target and current source; no receipt was repaired and no
resource execution was replayed. Ordinary API-default compatibility was not run after
refusal. Exact commands:

```sh
python3 platform/deployment/dev.py prepare --target platform/deployment/environments/kdg-local.json --run-id b32e04df-ffb0-4a36-ab23-c66e5b1f29ba
python3 platform/deployment/toolchain.py qualify --target platform/deployment/environments/kdg-local.json --run-id b32e04df-ffb0-4a36-ab23-c66e5b1f29ba
python3 platform/deployment/images.py qualify --target platform/deployment/environments/kdg-local.json --run-id b32e04df-ffb0-4a36-ab23-c66e5b1f29ba
python3 platform/deployment/tests/qualify_startup.py --target platform/deployment/environments/kdg-local.json --run-id b32e04df-ffb0-4a36-ab23-c66e5b1f29ba --control pinned-cli-postgres-kong-execution
```

| Command | Exit | Measured total seconds | Result |
| --- | --- | --- | --- |
| prepare | 0 | 0.207 | prepared / prepared |
| toolchain | 0 | 37.338 | qualified / toolchain_qualified |
| images | 0 | 54.464 | base_images_qualified / base_images_qualified |
| kong | 2 | 77.3 | startup / unsafe_create |

Durations are monotonic measurements around each complete child invocation. All four
stderr files are empty. commands.json retains argv, exit, elapsed and stdout/stderr
digests. Helper invocations/outcomes and their unavailable elapsed durations are in
operational-commands.json. No full environment or sensitive payload is retained.

The qualifier returns ok=false, stage=startup, code=unsafe_create, runtime_ready=false,
with no lifecycle/cleanup success fields. No fresh_setup_completed field is emitted;
its absence cannot establish completed setup. Read-only inspection after refusal found both
Kong and PG running; they were subsequently removed under separate exact approval. The original two differences now pass the unchanged portions
of the validator; a source trace rejects at create_profile.py:492, where the observed
post-start HostConfig.OomKillDisable is null but the current scalar-default allowlist
requires false. Inserting only false for that field into an in-memory diagnostic
copy passes the validator. This is diagnosis, not restored custody or qualification.
No OOM-field code change is included in this delivery.

[Moby's resource type](https://github.com/moby/moby/blob/af898abe44662d9554fb15ee4d4a7307f1b8e315/api/types/container/hostconfig.go#L402)
models that option as a nullable boolean; its
[daemon resource handling](https://github.com/moby/moby/blob/af898abe44662d9554fb15ee4d4a7307f1b8e315/daemon/daemon_unix.go#L329)
uses false in adaptContainerSettings and can clear the pointer in
verifyPlatformContainerResources when the capability is
unsupported. This supports investigating an explicit null/default projection; it is
not proof of the exact Docker29.9.1 build or this host's kernel capability.
Both files were inspected at Moby v28.0.0 peeled commit
`af898abe44662d9554fb15ee4d4a7307f1b8e315`, resolved from tag object
`383a9d96e2dd4915861d98ceca095fdf100b7643`.
upstream-oom-source.json retains exact resolution argv, URL/file hashes and selected
source lines; the downloaded public files remain local evidence, never executed. An attempted
v29.9.1 upstream source URL returned404. The exact observation and current validator
are the evidence for this rejection; no timing explanation or general nullable-default
admission follows from it. A future correction needs focused acceptance-first proof,
continued rejection of true/wrong types, and another fresh source-bound run.

## Preservation and approved exact cleanup

Inventory before/after refusal:252→254 container IDs,293→294 volume names,14→15 network
IDs. Every original identifier remains; exactly the two run containers, one run volume
and one run bridge were added. This compares container/network IDs and volume names,
not container/network names or contents. No unchanged-workload-content claim is made.

The resources retained while running after refusal are recorded with image identities,
labels, states and mount/network references in retained-resources.json and
retained-resource-references.json:

- Kong `5750b93e29d2221e1e86820204dc3950410d8eb9711bf8af442f2c14729f105c`.
- PG `d52a8690ebab51bad0336f0c9c9f3bdea73207fdc671c683a4ae29aa1db2d1fe`.
- Volume `supabase_db_agriplatform-kdg-sy4E3_-wSjarI8ZuWx8pug`.
- Bridge `8d4e11ab7f598291d34e52a5b0a3877b48f1c5b2a1ad4a9bcaa61d0da38d025c`.

The user explicitly approved that exact cleanup under DEVELOPMENT.md's lost-custody
rule. The helper rechecked IDs/images/labels/states and mount/network/all-container
volume-use references; it stopped Kong then PG normally, both exit0, and removed only
these four resources without force, each followed by404 confirmation. Exact requests,
statuses and durations are in cleanup-journal.json; cleanup-result.json records success.
This is separately authorized recovery cleanup, not the qualifier's normal-cleanup
success or restored lifecycle custody. Final sets are identical to initial252 container
IDs/293 volume names/14 network IDs; all four failed-run resources are absent. Older
resources and all receipts/diagnostics remain.

Two read-only diagnostic inspections used API1.48 GETs on these exact resources. Only
the final safe projection and comparison survive in inspection-diagnostic.json; raw
Config environment/command content and logs were not saved or printed. The first
helper version was superseded. The final helper requires live resources; no complete
offline response fixture or full replayability is claimed after removal.
The later sanitized selected-field fixture below preserves only the relevant projection;
its remaining fields/identities come from the existing synthetic peer, not an invented
full actual response.

Preservation audit:235 protected concurrent/historical/evidence files unchanged;
only the declared validator and two test modules differ within the initial47-file
source frame. The initial final47 bindings match affected/focused/process evidence;
review-only test/fixture changes are bound separately below. Original empty
index and13 new source-bound prerequisite files remain unchanged. semantic-delta.json
shows validate_kong_container is the only changed runtime symbol; runtime-patch.diff
records its exact patch. Pinned-image validation, source/create request, transport,
archive, lifecycle owner and deadline functions are unchanged.


## Review corrections and final verification

One-shot blind review produced five findings; all surviving coverage/source-evidence
parts are patched, with the already-covered absent-key portion rejected in the spec
triage. No new review deferral. Historical timing investigations remain unresolved;
the post-start null OOM default remains the next required ENV gate, not a readiness claim.

Review adds eight late hostile cases across running/exited observations, each with
accepted omission/order normalizations present, and same-length substitutions plus
complete wrong-container-type projections. The negative matrix now has35 subcases.
Existing selected running-state tests already cover absence of both protection keys.
The new sanitized selected-field fixture is
`fixtures/supabase-kong-observed-container-api-projection.json`: exact observed missing
OnBuild plus the two protection lists and null OomKillDisable, with explicit partial-
observation provenance. The offline test overlays it onto the canonical synthetic
peer, demonstrates the current OOM refusal, then localizes it with a false-only copy.
It neither changes the OOM policy nor claims all other fields were captured from Docker.

Final command: `PYTHONPATH=platform/deployment:platform/deployment/tests python3 -m unittest -v test_pinned_execution.KongExecutionOwner.test_projection_normalizations_keep_nonnull_and_invalid_protections_closed test_pinned_execution.KongExecutionOwner.test_normalized_projection_still_loses_custody_on_late_hostile_content test_pinned_execution.KongExecutionOwner.test_recorded_poststart_null_oom_projection_refuses_offline`. **3 methods PASS, no skips,22.150s** (runner22.297s),48 unchanged source/test/fixture/authority bindings. Manifest SHA256 `81c64d86d100e1ff9038a9c5e8653760e677b5c925632e880fdcc2b9cfe9ba6a`; log SHA256 `9394207059d7d42d022a196847b5befa67d33aeea168a3707566cd08c97383c9`.

Across the retained focused/affected/process/review calls,154 distinct method IDs pass.
This is cumulative source-bound evidence:152 passed on the earlier47-file frame; only
three targeted methods reran on the final48-file frame. review-frame-delta.json records
one changed test module,46 identical earlier bindings and one added fixture. Runtime,
process harness and actual prerequisite inputs remain unchanged after the Docker attempt.
No broader or actual execution was repeated after refusal. Five impact decisions above
remain applicable, including the new owner-maintained regression fixture.

## Final evidence digests

The local evidence-bindings.json binds 66 underlying evidence/helper/public-source files.
All bindings, published digests,235 protected files,48 final source/test/fixture bindings,
13 new prerequisites, original index and restored identifier sets rechecked.

| Artifact | SHA256 |
| --- | --- |
| evidence-bindings.json | bcd55be26afc668ea3f3f4f01141670dd2d2a00c26f36c908b2dd4c119b39d63 |
| checkpoint.json | 34cd09d68d7a5e15cce545a726c6bd8e1efafebd6a0be0333c6f4e4dfb7d96bf |
| commands.json | d822d66f9440749987748aaa93b95b2e87516b5a94f03e4c16fac973067b7fe8 |
| operational-commands.json | 8ddc29e5e1746ab62ce01924261700770884a30b81102d57cd9ab56ef2033245 |
| verification-summary.json | 6e51088f203cfdfa1eea5ba4dc039b1c6cde3c018f0e629b15e0d6f441369f45 |
| new-receipt-bindings.json | a4ebe41e11f8b6d000b19998af631c8359a0e537ae754763323d4b8493cd7d4f |
| semantic-delta.json | 94e54f2000890795d4a5d0896a016fbbacb5e013901a121fb2d465caf45782c8 |
| review-frame-delta.json | 5cd63113aef41127517f8bd1554aad076dea38e6f10e01d1bc337f560f143f7f |
| inspection-diagnostic.json | a303b12134f8929fb519bab616e0711f1c9b5073fc2f4ca51060c4a173a73afa |
| retained-resources.json | 2af192f681b4f0954e01e926bc87e8cc1928e12006a906f95f29682bd64e9ab5 |
| retained-resource-references.json | b3ef13c4e05e0935fad175d978e71ff5deb450dd21b8956531915d513af7e7e6 |
| cleanup-approval.json | b5458449c43bdbea19878666f35d27f5c457b080f1c78acdd61e4d28c18752ab |
| cleanup-journal.json | 357249197e9e3982a334417d486af686d273f1b45ed86d79b3e567f40b820b23 |
| cleanup-result.json | 6689c5bab6a8cbedccc374b3278882a711e51892439c8dfaab382db713c5ab18 |
| upstream-oom-source.json | 16af09eb4883441ed01140768aaadcfe9c920b3bd50b109383c0fa419f9345bd |
