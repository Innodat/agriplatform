# ENV Kong nullable OOM default evidence

Status: bounded correction complete; independent review addressed and actual controls pass. Baseline `e2285dfb40f8448af4765ba4c8a313361b84125d` plus
explicit validator/two-test-module worktree changes, bound by the source manifests.
The baseline is not an unmodified tested-source claim.

The [preceding observation](ENV_KONG_PROJECTION_EVIDENCE.md) and its immutable selected-
field fixture explain the old refusal. Pinned Moby source at
`af898abe44662d9554fb15ee4d4a7307f1b8e315` models OomKillDisable as a nullable bool;
adaptContainerSettings selects false and verifyPlatformContainerResources can clear
that pointer for an unsupported capability. Source resolution/hashes remain in the
preceding evidence. This is not attribution to the exact local daemon build/kernel.
Only explicit null in a copied Kong HostConfig is normalized to false; no disabled-
OOM request, other default-field admission or mutation of the observed row is added.

## Requirements and tests

| Requirement | Covering selector |
| --- | --- |
| Recorded null projection accepted without modifying source row; false equivalence | KongExecutionOwner.test_recorded_poststart_null_oom_projection_accepts_offline |
| Null at created/running/exited observations still completes normal owned cleanup | KongExecutionOwner.test_null_oom_default_completes_all_lifecycle_observation_phases |
| True and wrong primitive/collection types at each phase refuse, latch custody loss and prevent replay | KongExecutionOwner.test_oom_true_and_wrong_types_lose_custody_without_replay |
| Full selected recorded projection over private Unix/public process qualifier; canonical/boundary unchanged | ExecutionSupervisor.test_kong_execution_process_observed_container_projection and existing controls |

KongExecutionOwner selectors use module test_pinned_execution; ExecutionSupervisor
uses test_resources. Historical characterization is deliberately replaced by desired
acceptance RED for an explained observation, not dismissed as an unknown failure.

## Impact decisions

Scaffold: fix the existing ENV inspection owner and its existing qualification tests;
no generator/schema/client transfer or consuming scaffold claim. Shared UI: none.
Agent context: existing safeguards suffice, no root policy change. Documentation:
this record, runbook and KDG handoff/memlog carry exact results and remaining gates.
ADR: existing isolation, custody, release and safe diagnostics apply; no new or amended
accepted ADR needed. TS7.0.2, mail15484 and selected CLI/image pins stay unchanged.
Full runtime/ENV/scaffold readiness and dependent Identity/Access/WRITE/server-backed
KDG remain gated; production, account/access, provisioning, deployment and real data
stay outside this item.

## Acceptance and focused TDD

- Before runtime edits:2 methods/four observation subcases fail unsafe_create. Command: `PYTHONPATH=platform/deployment:platform/deployment/tests python3 -m unittest -v test_pinned_execution.KongExecutionOwner.test_recorded_poststart_null_oom_projection_accepts_offline test_pinned_execution.KongExecutionOwner.test_null_oom_default_completes_all_lifecycle_observation_phases`. Exit1, runner2.053s;48 unchanged bindings. Manifest SHA256 `95cf0960367df9aaa5c3313cf9d758895935d378ab3a7cbd79fc36c0294e75ac`; log SHA256 `1130bf6d27a11d3269878a893c54a5a533f9a6ddcd30aaa96870edbf97ab3582`. Retained result/log: `.local/kong-oom-default/owner-red{-result.json,.txt}`.
- Initial process attempt before runtime edits fails with docker_response_invalid because the test fixture loader used the harness temporary dev.ROOT, which lacks the fixture. This is a harness error, not product acceptance RED. Command: `PYTHONPATH=platform/deployment:platform/deployment/tests python3 -m unittest -v test_resources.ExecutionSupervisor.test_kong_execution_process_observed_container_projection`. Exit1, runner26.495s;48 unchanged bindings. Manifest SHA256 `95cf0960367df9aaa5c3313cf9d758895935d378ab3a7cbd79fc36c0294e75ac`; log SHA256 `2586d4dcb706da6cc7b665dc4f2b5f2ac3897dd47c2dea50166506c4d91394fe`. Retained result/log: `.local/kong-oom-default/process-red{-result.json,.txt}`.
- Before runtime edits:1 method/21 true or wrong-type phase combinations pass rejection checks. Command: `PYTHONPATH=platform/deployment:platform/deployment/tests python3 -m unittest -v test_pinned_execution.KongExecutionOwner.test_oom_true_and_wrong_types_lose_custody_without_replay`. Exit0, runner25.611s;48 unchanged bindings. Manifest SHA256 `95cf0960367df9aaa5c3313cf9d758895935d378ab3a7cbd79fc36c0294e75ac`; log SHA256 `f31f2641e0f13d6cab4ea6bbd9cd652b1996bf40a955da75344e7d6dfc94c84d`. Retained result/log: `.local/kong-oom-default/negative-characterization{-result.json,.txt}`.
- After correction:20 owner methods pass, including all current field/custody/lifecycle controls. Command: `PYTHONPATH=platform/deployment:platform/deployment/tests python3 -m unittest -v test_pinned_execution.KongExecutionOwner`. Exit0, runner174.049s;48 unchanged bindings. Manifest SHA256 `39858daab26cd7188f793099c2acb201f42cc469b024377f74defc196f61f866`; log SHA256 `11ff4e6d6eac51e6a505902528d3d4b1c74cec88a59a6f9305acc6ad51bf68cc`. Retained result/log: `.local/kong-oom-default/focused-green{-result.json,.txt}`.

Only validate_kong_container changes at runtime: explicit null in its copied
HostConfig becomes false. Missing and explicit false retain prior behavior; true and
non-bool values remain refused. The recorded observation/fixture and pinned upstream
source are unchanged. No create-request, image, transport, archive, owner-deadline or
normal cleanup change is made. Tests run serially; original failures remain evidence.


The first three-process attempt (`process-green`) retains one harness failure and
two passing controls (83.442s, exit1); its log SHA256 is
`a44378982ec5266b0d90f9eaa6375f1e1e18730e6fd6ef995aa88d82ab38d76c`.
The loader now resolves the immutable fixture from the test module repository path
before dispatch. With only the runtime normalization removed, the corrected process
case reproduces startup/unsafe_create (exit1,25.442s): this baseline comparison was
after the initial implementation, whereas the owner acceptance RED preceded it.
Retained `process-baseline-red` manifest SHA256
`982c9e9f351390292657e33b9d523d5a5ac20aa597c627a99be3ec2fd568e8d7`, log SHA256
`c422faec211862721650071fd3b78a4683635c67ebece4229a832a2e9a257606`.
No deadline or expected success result was changed to dismiss either failure.

Affected contracts: `PYTHONPATH=platform/deployment:platform/deployment/tests python3
-m unittest -v test_create_profile test_docker_session test_docker_gate test_startup_adapter`
passes133 methods (29.434s, exit0). Source manifest is the focused-green manifest;
log SHA256 `deb3423e2527fab576ca56186e925d70a1e37f9e4fe14d7b0ee334b9215fb189`.

The corrected observed-projection process case passes on restored runtime bytes
(`process-final`,30.690s total), but that invocation exits1 because I supplied two
nonexistent control selectors. Its two loader errors are retained, not counted as
passing tests. The two existing controls are invoked separately with their exact
tracked names; no product source was changed for these command errors.


The two corrected existing control selectors pass (exit0,62.558s):
`PYTHONPATH=platform/deployment:platform/deployment/tests python3 -m unittest -v test_resources.ExecutionSupervisor.test_kong_execution_process_ordered_lifecycle_and_post_cleanup_fact test_resources.ExecutionSupervisor.test_kong_boundary_process_source_intent_and_cleanup`.
Log SHA256 `fce9df6aa7541a6227b0c16e5179b511f0a1a947a539570cbf48eee55392a2f6`.
The observed-projection selector passes in the preceding invocation, whose aggregate
exit1 from two nonexistent selectors remains explicit. Both final process calls bind
48 unchanged files, manifest SHA256
`26c00caf66125757f1b9aff79461bfe08291568ab969d81fb73ae6a5867888d3`.
Compared with focused-green/affected, only test_resources.py changed (fixture-loader
correction); the other47 bindings, including runtime, are identical. Thus156 distinct
selected methods pass across retained calls (20 owner,133 affected,3 process), not a
claim that all were rerun on the final helper bytes or a full-suite result.


## Actual qualification prerequisites

Fresh run `4df3fc9c-643f-4b4c-b20e-10058ba104fa` passes prepare (0.114s) and
toolchain qualification (25.901s), then images refuses registry/manifest_response_invalid
(exit2,18.065s). All stderr files are empty; exact argv/digests are retained in
`.local/kong-oom-default/{prepare,toolchain,images}-result.json`. No Kong/ordinary
qualifier or Docker resource creation follows on that run. Its incomplete image
`.qualify.lock` and all inputs are preserved; no lock removal or receipt repair.
The first diagnostic script/result files are empty and provide no diagnostic proof.
A separately named `registry-check-2` read-only metadata diagnostic passes one selected
PostgreSQL index/tag/digest exchange (3.544s, expected401 then token200 and two200
manifests); this does not explain the original failure or prove all image identities.
Only status/allowlisted media/length metadata is retained, never credentials/bodies.

A second fresh run `ad277eef-a10e-4aac-bb82-5743653fb2e0` is selected for qualification.
The existing images.main entry point uses a local two-second request-spacing observer
inside the unchanged180s collection/request bounds. Pins, response/digest validators,
source files and receipt format are unchanged; no request is replayed inside it.
This metadata-only second attempt is separate from resource execution, which has not
started. All first-attempt files are hashed in first-attempt-bindings.json.


Second-run prerequisites pass: prepare0.071s, toolchain43.034s, images105.484s,
all exit0 and empty stderr. The exact command vectors and stdout/stderr SHA256s
are in `fresh-{prepare,toolchain,images}-result.json`; safe HTTP observations are
in `fresh-image-http.json`. The metadata-only wrapper calls unchanged images.main
with `qualify --target platform/deployment/environments/kdg-local.json --run-id
ad277eef-a10e-4aac-bb82-5743653fb2e0`; only inter-request timing/selected diagnostics
differ from direct `python3 platform/deployment/images.py qualify`.
Its13 fresh preparation/config/toolchain/image evidence files are bound before
resource execution in new-receipt-bindings.json. The current48 source/fixture frame
is the final process frame above; runtime source is identical to focused-green.

Initial inventory257 containers/298 volumes/14 networks becomes259/301/14 before
resource execution. The two added container IDs and three added volume names are
recorded in pre-execution-inventory-delta.json and preserved without attribution or
interference. No prior identity is removed; fresh-before is the execution baseline.


## Actual Kong acceptance

`python3 platform/deployment/tests/qualify_startup.py --target platform/deployment/environments/kdg-local.json --run-id ad277eef-a10e-4aac-bb82-5743653fb2e0 --control pinned-cli-postgres-kong-execution`
passes (exit0,131.424s, empty stderr). Raw selected result and exact argv are retained
in `fresh-kong.json` and `fresh-kong-result.json`; stdout SHA256
`2f7048e331d2a92e05ad959276168bce75441fde9d443dbf831f3c774987e068`.
Its source_sha256 entries shared with the final48-file test frame agree; the additional image-selection/contract entries also match their current files. Counts and paths are retained in actual-source-check.json.

Verified facts include owner_kong_execution_verified, kong_create_executed,
kong_three_file_transfer_verified, kong_healthy_verified, kong_shutdown_verified,
kong_disposal_verified, pg_shutdown_verified, cleanup_verified; all true.
forced_shutdown is false. CLI termination-before-dispatch semantics are retained.
Post-Auth tail, catalog and API-default proofs also report true. This proves the
bounded synthetic disposable owner lifecycle, not native-token functional Auth
routing, remaining ENV services or a consuming scaffold. runtime_ready and
fresh_setup_completed both remain false.

After normal cleanup,259 container IDs/301 volume names/14 network IDs exactly match
the execution baseline. No recovery removal, forced deletion or lost-custody adoption
was used. The ordinary API-default compatibility control follows on the same13
unchanged receipt/config files only after this success.


## Compatibility and preservation

`python3 platform/deployment/tests/qualify_startup.py --target platform/deployment/environments/kdg-local.json --run-id ad277eef-a10e-4aac-bb82-5743653fb2e0 --control pinned-cli-postgres-api-default-privileges`
passes (exit0,87.929s, empty stderr). Retained `fresh-ordinary.json` and
`fresh-ordinary-result.json`; stdout SHA256
`5ed7e38ed23b2963ac4eec8e9b128be7232673adcf77bc8f639c687582a17475`.
Ordinary source entries match the Kong source map. API-default/catalog/Auth-job,
PG shutdown and normal cleanup facts are true; forced_shutdown=false,
runtime_ready=false and fresh_setup_completed=false. No full-runtime claim follows.

Final pre-review audit:305 protected files,48 final test/source/fixture bindings,
18 first-attempt/diagnostic/helper files,13 new receipt/config files and index all
unchanged. Runtime/source delta is exactly create_profile.py and the two test modules;
other initial source bindings are unchanged. Final259 container IDs/301 volume
names/14 network IDs match fresh-before and after-kong exactly: no added/removed
identities. audit.py and verification-summary.json retain paths/differences/counts.
Original failed results, zero-byte diagnostic attempts and the incomplete first image
lock are preserved; no receipt repair, daemon/resource pruning or recovery cleanup.
The first registry failure and older timing investigations remain unexplained; this
successful fresh run does not resolve them. No full deployment suite was run here.


## Review reproducibility supplement

The complete session-only spacing/metadata observer used for the successful image
qualification is below. It imports the existing images owner; it does not replace
qualification, generate application code, alter validators or replay failed requests.
For reproduction, save in a new empty local evidence directory and invoke with
`python3 <saved-wrapper.py> qualify --target platform/deployment/environments/kdg-local.json
--run-id <new-prepared-and-toolchain-qualified-UUID>`. Existing output/receipt/lock
files must remain untouched. This is a diagnostic invocation, not a new delivery tool.
The helper's exact UTF-8 file SHA256 is `19846389fb9e18c5681d96407c256290a8bd5ead496199df3145cf45ea1c2ef1`.

```python
from pathlib import Path
import json, sys, time
sys.path.insert(0, str(Path.cwd() / 'platform/deployment'))
import images

out = Path(__file__).resolve().parent / 'fresh-image-http.json'
assert not out.exists()
original = images.https
rows = []
def spaced(path, headers, limit, deadline):
    if rows:
        images.remaining(deadline)
        time.sleep(min(2, images.remaining(deadline)))
    status, response, raw = original(path, headers, limit, deadline)
    media = response.get('content-type', '').split(';')[0]
    rows.append({'kind': 'token' if path.startswith('/token/') else 'manifest',
                 'status': status, 'media': media if media in images.INDEX_MEDIA | images.MANIFEST_MEDIA | {'application/json'} else 'other',
                 'bytes': len(raw)})
    return status, response, raw
images.https = spaced
try:
    code = images.main()
finally:
    images.https = original
    with out.open('x') as stream:
        stream.write(json.dumps({'spacing_seconds': 2, 'http_observations': rows,
                                  'limits_unchanged': True}, indent=2)+'\n')
sys.exit(code)
```

Selected verification-manifest hashes (all SHA256; paths relative to
`.local/kong-oom-default/`):

| Artifact | SHA256 |
| --- | --- |
| checkpoint.json | 17c6f87347434d30b61b528abba5e19153d2fe4b14d25a78b19be83e3e4e8992 |
| owner-red-sources.json | 95cf0960367df9aaa5c3313cf9d758895935d378ab3a7cbd79fc36c0294e75ac |
| focused-green-sources.json | 39858daab26cd7188f793099c2acb201f42cc469b024377f74defc196f61f866 |
| affected-sources.json | 39858daab26cd7188f793099c2acb201f42cc469b024377f74defc196f61f866 |
| process-baseline-red-sources.json | 982c9e9f351390292657e33b9d523d5a5ac20aa597c627a99be3ec2fd568e8d7 |
| process-final-sources.json | 26c00caf66125757f1b9aff79461bfe08291568ab969d81fb73ae6a5867888d3 |
| review-final-sources.json | 01e4163c488cc26b8c036c7a19d5b2ac86a39da92fcb25e5e1068a8fe0b63d25 |
| new-receipt-bindings.json | 0b7aa17c9778b2c944a97fd2318b13ad1cf2ef37dc9b67078fea49062c39792d |
| first-attempt-bindings.json | 4283e02cb16c2e75acdc6610994e2bed3c930d76d7451f86f835d031ab85a67d |
| actual-source-check.json | ed13a7e635c816d9ad11e2750b1385f0c5462a26cf4926cbf1d162c2d4764171 |
| command-index.json | ab7d1af0ed66f54e2055e77fb3c4126f0e68ea31df5c096db54e9a89772eceba |
| fresh-image-http.json | c9f93a73ebe58ef39457649cb9c5113f31c64a63d1293d1695409e113021ee03 |


## Final review acceptance — 2026-10-20

BMAD one-shot runs the independent blind-hunter review only; other layers are skipped.
All six findings are patched, grouped compatibility coverage1/4 together, none newly
deferred. The Build triage records each verdict/evidence. Runtime is unchanged from
actual qualification. Review adds created-only and null/false/absent lifecycle forms
(12 combinations), full inspected-row preservation, three unrelated hostile-field
regressions alongside null, versioned process-fixture consumption and the complete
spacing observer above.

Final review-focused command:
`PYTHONPATH=platform/deployment:platform/deployment/tests python3 -m unittest -v test_pinned_execution.KongExecutionOwner.test_recorded_poststart_null_oom_projection_accepts_offline test_pinned_execution.KongExecutionOwner.test_null_oom_default_completes_all_lifecycle_observation_phases test_resources.ExecutionSupervisor.test_kong_execution_process_observed_container_projection`
passes3 methods (exit0,43.402s),48 unchanged bindings. Log SHA256
`4a039ab71d0fe3f4d139332dda2dfd732314d2ed40dc7da1ccae971e96b52ccc`;
source manifest SHA256 `01e4163c488cc26b8c036c7a19d5b2ac86a39da92fcb25e5e1068a8fe0b63d25`.
These are targeted final-source results, not a rerun of all156 distinct selected
methods on final test-helper bytes. Both actual42-file source maps still match their
current files; review changes only two test modules and documents. All broader
runtime/scaffold/dependent gates and older investigations remain open as above.
