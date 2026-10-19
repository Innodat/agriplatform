# ENV pinned-image disposable Kong profile evidence

Baseline: fb6a43029673f8e59e9f06b4e1e57a3c4c00e8f3. The existing Kong boundary
now validates a closed selected image Config and separate disposable create profile.
Both source and disposable create requests remain classifier-only refusals. No new
Docker route, control, success field or actual gateway execution is introduced.
Runtime/fresh-setup readiness remain false and the original CLI stays terminated.

## Authority and observation

The root read the already cached exact image through the fixed local Docker API 1.48:
`GET /v1.48/images/sha256:3cefb958bcd694597b65adc00053a762b1f9a6df3c6031af528d052d75a64e1a/json`.
Identity/platform matched linux/amd64. This was read-only, with no pull/container
creation/start/copy or Docker mutation. Only environment names appeared in tool output.
The [public Config projection](fixtures/supabase-kong-image-api-config.json) and
[provenance/limits](fixtures/supabase-kong-image-api-config.md) participate in source
custody. The normalized public projection hash 33f41b2a864c66de040bd8ad42dc637cb6565cfe251439b1acfadad9616c45a4
is distinct from the image configuration object's content identity above.

The image supplies user kong, empty working directory, SIGQUIT, and kong health
with 10s interval/timeout and 10 retries. The separate disposable profile makes user,
root working directory, health and stop signal explicit, closes image Env/labels and
source/image exposed ports, and applies no-restart/no-log/resource/network limits.
The three source-derived transfer files and public synthetic key markers stay as
before. No native minted-token or actual container-merge/routing proof is claimed.

## Requirement to test traceability

Use `PYTHONPATH=platform/deployment:platform/deployment/tests python3 -m unittest -v`
from repository root with the selectors below.

| Requirement | Test selector |
| --- | --- |
| Independent complete image/default and disposable request oracles, detached inputs and refused create | test_create_profile.KongDisposableProfile.test_exact_independent_image_and_disposable_oracles |
| Recursive missing/extra/nested/scalar-type mutations and privacy | test_create_profile.KongDisposableProfile.test_recursive_image_and_disposable_mutations_are_closed_and_private |
| Source arguments/env/request/transfer revalidation | test_create_profile.KongDisposableProfile.test_disposable_constructor_revalidates_every_source_input |
| Changed fixture bytes refuse safely | test_create_profile.KongDisposableProfile.test_fixture_byte_change_refused_without_recording_content |
| Owner validates Config plus both profiles, without sending create | test_pinned_execution.KongBoundaryOwner.test_current_image_and_both_closed_profiles_checked_without_exchange |
| Changed image/profile consumes attempt, no replay/completion/disclosure | test_pinned_execution.KongBoundaryOwner.test_image_default_and_disposable_corruption_consume_attempt_without_disclosure |
| PG observations surround image/profile/classifier boundary | test_pinned_execution.KongBoundaryOwner.test_pg_checks_surround_image_profile_and_classifier_validation |
| Existing invalid prerequisites/terminal/replay/deadline/cancellation/custody/cleanup protection | Full test_pinned_execution.KongBoundaryOwner |
| Private process exact positive, expiry/interruption, transfer/cleanup and new image/profile rejections | Four test_resources.ExecutionSupervisor Kong methods listed below |
| Ordinary setup-tail/default controls | Two existing process methods listed below |

## Test sequence and results

The initial acceptance assertion incorrectly assumed one image inspection; existing
joint custody checks deliberately repeat descriptor observations. Its failure 78!=1
was a test-assumption failure, not relevant ATDD RED. That raw initial output is in
the delegated tool transcript, not a reconstructed log. The implementation draft
preceded the corrected assertion: acceptance-first sequencing was missed.

To correct verification without rewriting history, only the owned resources.py draft
was saved temporarily and the baseline module restored. The corrected acceptance
then failed Config validator call count 0!=1 (1 test/0.396s), retained as
corrected-baseline-red.log. Restoring the draft made the same test pass, retained as
corrected-restored-green.log. This is explicitly a post-draft baseline comparison,
not historical acceptance-first proof. Focused source/profile/owner 19 tests pass 5.925s.
An attempted 2-selector private-process run was blocked by sandbox Unix socket bind
EPERM (2 tests/3 errors/0.304s); that is not behavioral or PASS evidence.

Root affected command:

```sh
PYTHONPATH=platform/deployment:platform/deployment/tests python3 -m unittest -v test_create_profile test_dev test_startup_adapter test_docker_session test_docker_gate test_pinned_execution.KongBoundaryOwner test_startup_lifecycle.KongTransferArchive
```

161 tests PASS in 35.299s, no skips (runner 35.432s). The original affected source
manifest binds 44 source/test/public-authority files, all unchanged across that call.
Later process/final manifests also include test_dev and test_startup_adapter source
bindings; retain both observations instead of replacing the original.

- affected-sources.json SHA256: `a7c46f5722a500e758607e67cb60f12db28f56c23e5e4419b92f12c74832de77`
- affected.txt SHA256: `4eec13eda3de3651db7fdab49dbdf2abf249c8c3a0abe8add2fc2f7e6d42fa58`
- corrected-baseline-red.log SHA256: `0d3694c14b0ac279177c5f4baa045f0005b4ff729f2095945cb93989c2397a3b`
- corrected-restored-green.log SHA256: `55e429a9b5c0193527a28f69590847f642fedc7d4c45a02d21ababb5ef347800`

## Impacts and preservation

- Scaffold: existing ENV profile/resource owners changed, source fixtures bound through
  existing preparation. No new generator or consuming output proof.
- Shared UI: no UI change or proven neutral pattern to promote.
- Agent context: existing instructions suffice; no context edit.
- Documentation: Config provenance, runbook, Build/evidence and KDG handoff updated.
- ADR: existing owner/logging/release decisions retained; no new decision.

Checkpoint under platform/deployment/.local/kong-execution-profile/ preserves 17
concurrent files, 52 historical prerequisite files, 17 preceding transport evidence
files and original index. No Docker resource deletion/adoption/replay is authorized.
Transport/admission function/class ASTs are unchanged from baseline; only source
fixture bindings change in dev.py. Old actual receipts stay historical; future
actual qualification needs fresh source-bound prerequisites.

Remaining: owner Kong create/transfer/effective-container custody/health/disposal,
native-key/functional Auth routing proof when consumed, remaining ENV services and
consuming scaffold acceptance. Identity/Access/WRITE and server-backed KDG stay gated.

Private-process acceptance command (the four Kong methods cover seven scenarios,
followed by two ordinary-control scenarios):

```sh
PYTHONPATH=platform/deployment:platform/deployment/tests python3 -m unittest -v test_resources.ExecutionSupervisor.test_kong_boundary_process_source_intent_and_cleanup test_resources.ExecutionSupervisor.test_kong_boundary_process_deadline_and_interruption_never_qualify test_resources.ExecutionSupervisor.test_kong_boundary_process_altered_transfer_and_cleanup_failure_no_fact test_resources.ExecutionSupervisor.test_kong_boundary_process_image_and_disposable_profile_rejection_are_private test_resources.ExecutionSupervisor.test_post_auth_setup_tail_process_exact_artifact_and_cleanup test_resources.ExecutionSupervisor.test_api_default_privileges_process_order_and_verified_cleanup
```

6 process tests PASS in 202.027s, no skips (runner 202.183s). All 46 process source/test/public-authority bindings remain unchanged.

- process-sources.json SHA256: `4925868aca966795b7f8d767ef442b390bd78e0258de5f619cb3b26b9c7bd1ab`
- process.txt SHA256: `7b0a3e897fcc8a9d77a852326ea216487adee8fe606d6b5228526038bf6660c2`

167 distinct test IDs pass across affected/process calls; focused 19 are a subset. No full-suite or actual Kong execution claim.

## Reproducing source bindings and checks

Run on the committed source in an environment permitting private Unix sockets.
This hashes repository source/test/public-authority files only, never transfer input:

```sh
PYTHONPATH=platform/deployment:platform/deployment/tests python3 - <<'PYTHON'
from pathlib import Path
import hashlib, json, subprocess, sys
import dev
output = Path('platform/deployment/.local/kong-profile-reproduction')
output.mkdir(parents=True, exist_ok=True)
tests = ['test_docker_session', 'test_docker_gate', 'test_startup_lifecycle',
         'test_pinned_execution', 'test_create_profile', 'test_resources',
         'test_dev', 'test_startup_adapter', 'create_profile_fixtures']
paths = sorted(set(dev.SOURCES +
                   ['platform/deployment/tests/' + name + '.py' for name in tests]))
manifest = {name: hashlib.sha256(Path(name).read_bytes()).hexdigest() for name in paths}
(output / 'sources.json').write_text(json.dumps(manifest, indent=2) + '\n')
selectors = ['test_create_profile', 'test_dev', 'test_startup_adapter',
             'test_docker_session', 'test_docker_gate',
             'test_pinned_execution.KongBoundaryOwner',
             'test_startup_lifecycle.KongTransferArchive']
with (output / 'affected.txt').open('w') as log:
    result = subprocess.run([sys.executable, '-m', 'unittest', '-v', *selectors],
                            stdout=log, stderr=subprocess.STDOUT)
print('verification exit code:', result.returncode)
raise SystemExit(result.returncode)
PYTHON
```

The separate process command above regenerates process verification; historical
observations/log hashes are retained in the ignored local evidence directory.

## Final review and verification

Three independent layers complete: seven blind findings individually triaged and
patched; edge review returns[], verification-gap review finds no gaps. No new
findings are deferred. Added explicit image status/shape/identity/platform/variant
negatives, exchange cancellation/timeout/unavailability, and independent second
classifier success/error cases. Shaped source mutations prove the disposable builder
is not entered. The public recipe creates missing parents on clean checkouts.

Concrete test inheritance duplicated four source tests under new IDs in the initial
167-ID run; the new class now reuses only fixture/oracle helpers. Final affected
verification is 160 tests PASS in 43.884s, no skips (runner 44.120s), including three new
owner methods. Together with the six retained process methods, 166 distinct final
selected methods pass across recorded calls; removed duplicate IDs are excluded.
No full-suite or actual Kong execution proof follows.

Only three bindings differ from the process snapshot: create_profile.py (one
misleading docstring corrected), test_create_profile.py (coverage/helper changes),
and test_pinned_execution.py (new owner tests only). Restoring the prior docstring
in memory reproduces the exact process source hash; all earlier process-helper
hunks in test_pinned_execution are identical. The process harness and production
behavior are unchanged; all 43 other source/test bindings match. See
review-runtime-comparison.json. Retain original process/affected source frames/logs;
no replacement or repaired receipt is claimed.

- reviewed-affected-sources.json SHA256: `0d35566a71ebcd5230688dc250b16fa190dee67dce4ebe4df79e39f6254a6762`
- reviewed-affected.txt SHA256: `c381d9201fb4a70e805c481b2d4c62b809833e6d440295fcecace8b35ce8e8f7`

All 46 final source/test/public-authority bindings stay unchanged across final verification.
