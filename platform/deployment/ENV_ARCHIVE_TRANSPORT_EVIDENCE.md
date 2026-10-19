# ENV bounded archive transport evidence

Source baseline: d53a3c38b03bd66c547b6591c19956a3c92e396e. This increment
removes a transport size mismatch before Kong lifecycle execution. It adds no
Docker route/control, owner execution authority or readiness fact. No actual Docker
resources are contacted. Runtime/fresh-setup readiness remain false.

## Requirement to test evidence

Run from repository root with
`PYTHONPATH=platform/deployment:platform/deployment/tests python3 -m unittest -v`:

| Requirement | Test selector / result |
| --- | --- |
| Source-generated three-file archive >16KiB transfers exactly; next request uses same connection | test_docker_session.DockerSessionTests.test_source_kong_archive_and_next_request_share_exact_private_wire |
| Empty/small/10240-byte PG/max 65536-byte archives preserve exact bytes/framing | test_docker_session.DockerSessionTests.test_archive_body_bounds_preserve_empty_small_and_pg_bytes |
| 65537 bytes, changed route/method/type/nonpersistent refuse before socket; existing connection closes without sending | test_docker_session.DockerSessionTests.test_archive_oversize_route_method_and_type_refuse_without_socket_or_reuse |
| JSON retains exact 16384 aggregate bound in both modes | test_docker_session.DockerSessionTests.test_json_aggregate_boundary_stays_16384_for_both_connection_modes |
| Short/EOF/timeout/send/cancellation invalidate session, no replay/reconnect or sensitive diagnostics | test_docker_session.DockerSessionTests.test_archive_transfer_failures_permanently_close_without_replay |
| Existing protocol/deadline/response behavior | Full test_docker_session and test_docker_gate modules |
| Semantic archive contract and create refusal remain intact | test_startup_lifecycle.KongTransferArchive and test_pinned_execution.KongBoundaryOwner |

ATDD RED: the first selector fails at existing docker_request_invalid before
implementation (1 test/0.054s); raw transport-red.log retained. The initial test's
204 response expectation was corrected from an empty object to None by independently
reading the unchanged response parser; it did not cause the observed RED. Focused
GREEN: five new methods pass (5 tests/0.028s), transport-green.log retained.

Affected verification command:

```sh
PYTHONPATH=platform/deployment:platform/deployment/tests python3 -m unittest -v test_docker_session test_docker_gate test_startup_lifecycle.KongTransferArchive test_pinned_execution.KongBoundaryOwner
```

67 tests PASS in 8.856s, no skips. Local runner elapsed 8.974s. Not a full-suite,
native publisher-conformance or actual gateway/runtime qualification claim.
The canonical fixed route bounds header size below 1024 in normal use; no fabricated
noncanonical route is admitted to exercise that defensive cap. Archive semantic
validation belongs to the existing owner, not this transport. Current marker keys
remain synthetic, not native minted JWT proof.

## Reproducible bindings and preservation

Local evidence directory: platform/deployment/.local/kong-archive-transport/.
Only source/test/log files are hashed; runtime archive bytes/content are never hashed
or persisted. affected-sources.json binds 40 source/test/public-authority files;
all remained unchanged across verification.

- affected-sources.json SHA256: `550462c3424a2a5829a72c83d6d159eda11e1a91d03f52af6a8a34fd8c4ec318`
- affected.txt SHA256: `7a729c6f80d9243577667bfad201f9af645c6890f873cc221c8af8917ca4e180`
- transport-red.log SHA256: `039d03e8a250dcbd2a7598842ad3dcdae4eeb0ae1f3b3bd9942aede6869e44ef`
- transport-green.log SHA256: `d696f1c26f2015b17a696a05a08857ceb721833bf50f2085fe7a7b172670ab76`

checkpoint.json records 17 concurrent files, 52 historical prerequisite files and the
original index hash. Recheck before scoped commit; preserve all uncertain/preexisting
Docker resources and old source-bound receipts. No recovery deletion or receipt repair.

## Reproducing source bindings and verification

The retained local logs are historical observations; a fresh checkout can produce
its own source manifest and affected-suite log with this command. It hashes only
repository source/test/public-authority files, never archive input. Run on the
committed source in an environment permitting private Unix sockets:

```sh
PYTHONPATH=platform/deployment:platform/deployment/tests python3 - <<'PYTHON'
from pathlib import Path
import hashlib, json, subprocess, sys
import dev
output = Path('platform/deployment/.local/kong-archive-transport-reproduction')
output.mkdir(exist_ok=True)
tests = ['test_docker_session', 'test_docker_gate', 'test_startup_lifecycle',
         'test_pinned_execution', 'create_profile_fixtures']
paths = sorted(set(dev.SOURCES +
                   ['platform/deployment/tests/' + name + '.py' for name in tests]))
manifest = {name: hashlib.sha256(Path(name).read_bytes()).hexdigest() for name in paths}
(output / 'sources.json').write_text(json.dumps(manifest, indent=2) + '\n')
command = [sys.executable, '-m', 'unittest', '-v', 'test_docker_session',
           'test_docker_gate', 'test_startup_lifecycle.KongTransferArchive',
           'test_pinned_execution.KongBoundaryOwner']
with (output / 'verification.txt').open('w') as log:
    result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
print('verification exit code:', result.returncode)
raise SystemExit(result.returncode)
PYTHON
```

The RED observation is preserved locally with its raw log hash above. It can be
reproduced by applying the new exact-wire acceptance test to baseline d53a3c38b03bd66c547b6591c19956a3c92e396e;
it refuses the >16KiB archive. Do that in an isolated checkout, preserving current work.

## Impacts and remaining gates

- Scaffold: existing ENV transport owner changed; no generator or consuming output proof.
- Shared UI: no UI change or neutral pattern promotion.
- Agent context: existing instructions suffice; no context change.
- Documentation: runbook bounds, Build record, KDG handoff and this evidence updated.
- ADR: existing operational logging/owner/release decisions retained; no new decision.

Next: safe disposable Kong profile/image defaults, native-key provenance, exact
network/file/resource custody, health and disposal, then remaining services and
consuming scaffold proof. Identity/Access/WRITE and server-backed KDG stay gated.

## Final review and verification

Three independent review layers complete: five blind findings patched, edge review
returns[], verification-gap review finds no gaps. Numeric mock call counts prevent
payload disclosure on assertion failure; a scripted partial-send prefix case proves
permanent invalidation/no replay. Source-manifest/log regeneration and prose/media-type
corrections are documented above. The scripted prefix case does not claim a kernel
partial-write conformance test. No runtime code changed during review; only the test
module differs among the40 verification bindings. No new deferrals.

Final affected command above:67 tests PASS in 7.945s, no skips; runner elapsed 8.049s.
- reviewed-sources.json SHA256: `d56cfbf31281e8ad219d2a29cf486cf794c3b98a42fb2cc4a3d21469e3956c64`
- reviewed.txt SHA256: `a44b233fad01958231a60ca5ddd87926d5c77a19145b61a195ffcfcca59710eb`
