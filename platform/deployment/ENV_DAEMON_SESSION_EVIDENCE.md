# ENV bounded daemon connection continuity — 2026-10-16

Completed bounded delivery through the existing ENV owner and
[environment contract](../docs/architecture/contracts/scaffold-environment-and-generation.md).
[Build record](../../_bmad-output/implementation-artifacts/spec-env-daemon-session.md).

## Scope and authority

The current transport reconnects for every HTTP request. The selected increment keeps
version qualification and resource requests on one connection within each network,
volume or image adapter operation. A broken connection must refuse without reconnect
or request replay. Existing run ownership/evidence checks and fixed routes remain.

[Moby v28.0.0 daemon source](https://github.com/moby/moby/blob/v28.0.0/cmd/dockerd/daemon.go)
constructs Go http.Server and serves configured listeners (lines 179–181, 288, 302–307).
[Go HTTP server documentation](https://pkg.go.dev/net/http#Server.SetKeepAlivesEnabled)
records keepalive enabled by default. This supports the selected mechanism; isolated
synthetic verification does not qualify an actual daemon or every server configuration.
A daemon that closes the connection is refused without fallback.

## Limits and five impacts

This is per-operation connection continuity, not resource exclusivity or a combined
network→volume→image→container execution session. Volume freshness/reuse, bootstrap and
secret policy, complete helper-image inventory, guarded lifecycle/recovery/health,
actual deployment PostgreSQL compatibility and owner migration integration remain open.
P1/SERVICE and provider/device proof remain separate. No container, SQL, account/access,
production infrastructure, deployment, real-data pilot, Leave or KDG domain work occurs.

- Scaffold: existing ENV transport and acquisition owners; no new generator/service.
- Shared UI: none.
- Agent context: root rules suffice; actual commands remain in the owner runbook.
- Documentation: runbook, evidence, Build record, KDG resume and append-only memlog.
- ADR: existing isolation, safe logging and release decisions apply unchanged.

## Acceptance and verification

Initial characterization:
`python3 -m unittest discover -s platform/deployment/tests -p test_docker_gate.py -k DockerProtocol`
passed 8 tests against the existing parser.

ATDD RED:
`python3 -m unittest discover -s platform/deployment/tests -p test_networks.py -k event_validation`
failed `synthetic_connection_mismatch` after independent connection counting was added
to the private server. Existing code reconnected between prerequisite/resource requests.
An initial sandbox attempt returned `port_unavailable`; the socket-capable run above
is the accepted RED. This was the initial RED checkpoint; subsequent GREEN and final proof follow below.

Root focused checks outside the restricted socket sandbox:
- `python3 -m unittest discover -s platform/deployment/tests -p test_docker_session.py`: 9 passed, 0.360s.
- Same command with `test_docker_gate.py`: 15 passed, 0.583s.
- Same command with `test_networks.py`: 28 passed, 13.729s.
- Same command with `test_volumes.py`: 21 passed, 8.275s.

The implementer's final network test request stalled waiting for tool permission and
was aborted without a returned execution/session ID. The root runs above supersede
that uncompleted request. An initial malformed-response test was corrected before
review: non-truncation cases now keep the peer open and assert the protocol error,
so EOF cannot mask a missing parser guard. Truncation has its own EOF test.

| Requirement | Test coverage |
| --- | --- |
| One version/resource connection and cleanup | `test_sequential_requests_share_one_connection_and_release_descriptor`; all three qualifiers count accepted connections |
| Socket replacement cannot redirect acquisition | `test_socket_path_replacement_cannot_receive_subsequent_requests`; all three adapters' `test_acquisition_retains_original_peer_when_socket_path_is_replaced` |
| Disconnect/uncertain mutation never replay | `test_disconnect_before_or_after_mutation_never_replays`; adapters' `test_disconnect_at_every_exchange_never_reconnects_or_replays` |
| Strict later response framing and failed-session refusal | `test_bad_second_response_poisoning_cannot_send_or_reconnect`; `test_truncated_second_response_refuses_on_eof`; `test_late_unsolicited_bytes_are_refused_before_next_request` |
| HTTP close/1.0 refusal | Bad-second-response matrix |
| One deadline across exchanges and trickled bytes | `test_total_deadline_spans_individually_fast_requests`; `test_slow_trickle_cannot_reset_total_deadline` |
| Foreign/stale/preparation guards | Existing network/volume/image negative and evidence-mutation tests |
| Invalid route and exception cleanup | `test_callback_exception_and_invalid_route_close_without_additional_send`; existing gate/route tests |

The full image suite initially ran 18 tests with one error: its fresh-observation test
invokes two acquisitions on one synthetic server, but reset only events between calls.
The new counter correctly observed two connections across those two operations. The
test now validates and resets both per-operation counters, preserving complete fresh
observation checks. Focused `test_daemon_images.py -k exact_fresh` passed 1 (0.302s),
then full `test_daemon_images.py` passed 18 (6.990s). No production guard was weakened.

Three independent review layers launched together against the complete 55,190-byte
implementation/test/runbook diff. Review disposition and final source-bound proof follow below.

## Independent review

Three layers returned twelve finding instances. Eleven require local corrections;
one evidence-absence claim is disproved by this existing root-owned record. No deferral.
Individual verdicts are recorded in the Build spec. Root reproduced high-descriptor
select failure using fd2048 and a deadline overrun by advancing a deterministic clock
during decoding (deadline1, completion2, incorrect success). Remaining fixes cover
final/disconnect branch coverage, deterministic observation boundaries, the partial-body
EOF test-server loop, exact image preflight refusal/socket assertions and documentation.

Connection continuity does not guarantee future liveness: trailing bytes/EOF are
rejected when visible during framing/idle checks. Bytes arriving after a completed
operation cannot retroactively invalidate it. Final-response tests must synchronize
observable failure rather than infer scheduler timing after server sendall.

## Review-fix verification

Root reruns after fixes: session14 passed0.387s; gate15 passed0.500s;
network28 passed14.902s; volume21 passed8.481s (same focused commands above).
The revised image exact-refusal test initially expected `existing_tools_required` for
corrupted tool receipt. Root traced `test_images.PersistenceGuards.setUp`, which pins
`images.existing_tools` to its initial payload/hash; `images.qualify_evidence.inputs_current`
therefore correctly raises `images/qualification_input_changed`. The assertion now
requires that exact code and zero socket construction. Focused `test_daemon_images.py
-k missing_and_stale` passed 1 in 0.118s; no production behavior changed.

Additional review coverage: `test_high_descriptor_supports_idle_observation`,
`test_decode_processing_cannot_exceed_total_deadline`,
`test_final_idle_processing_cannot_exceed_total_deadline`,
`test_partial_request_body_eof_releases_peer_promptly`, and
`test_final_observable_trailing_bytes_and_eof_refuse`. Adapter disconnect tests now
include every final request and network existing/conflict plus volume existing paths;
SHUT_WR/event synchronization makes final EOF observable before the assertion.

Final image suite after exact fixture expectation correction: 18 tests passed in 7.397s.
All eleven retained review findings are fixed; one claim disproved, none deferred.
Root inspected the updated diff and every matrix row has executed focused coverage.
Python compilation, scoped whitespace and local links passed for all 17 delivery paths.

## Frozen-source public qualification

Fresh run `2037418f-ce7d-49b0-9c2b-65f5e65fc454` passed preparation, pinned-tool and
read-only registry-manifest qualification, in that order:

```sh
python3 platform/deployment/dev.py prepare --target platform/deployment/environments/kdg-local.json --run-id 2037418f-ce7d-49b0-9c2b-65f5e65fc454
python3 platform/deployment/toolchain.py qualify --target platform/deployment/environments/kdg-local.json --run-id 2037418f-ce7d-49b0-9c2b-65f5e65fc454
python3 platform/deployment/images.py qualify --target platform/deployment/environments/kdg-local.json --run-id 2037418f-ce7d-49b0-9c2b-65f5e65fc454
python3 /tmp/env-session-public-proof.py 2037418f-ce7d-49b0-9c2b-65f5e65fc454
```

The temporary harness invokes existing public `tests/qualify_networks.py`,
`tests/qualify_volumes.py` and `tests/qualify_daemon_images.py` with the same target/run
and each existing `--control`. Missing-preparation cases deliberately use new unprepared
UUIDs. It checks exact result/exit codes, safe output, retained evidence identities and
source snapshots. The final protected record contains every exact command/result;
this orchestration script is not a new delivery entry point.

All **42 public controls passed**: 15 network, 15 volume and 12 image cases. Successful
acquisitions passed the independent one-connection and exact request-sequence oracles;
negative cases returned their exact expected codes. Every result retained
`runtime_ready=false`, with no stderr or checked sensitive markers. All thirteen
retained files kept identical hashes, inodes, modes and mtimes; preparation/startup
source snapshots also remained identical.

Protected record:
`.local/daemon-session-qualification/2037418f-ce7d-49b0-9c2b-65f5e65fc454.json`
SHA-256 `88de47d84204bb2ff8ea634700bb2977f44335e5ecb297387782de4770e83f39`.

| Qualifier | Control | Exit / code |
| --- | --- | --- |
| `qualify_networks` | `positive` | 0 / `network_synthetic_qualified` |
| `qualify_networks` | `existing` | 0 / `network_synthetic_qualified` |
| `qualify_networks` | `conflict` | 0 / `network_synthetic_qualified` |
| `qualify_networks` | `foreign` | 2 / `network_not_run_owned` |
| `qualify_networks` | `unsafe-options` | 2 / `network_not_run_owned` |
| `qualify_networks` | `ipv6` | 2 / `network_not_run_owned` |
| `qualify_networks` | `attached` | 2 / `network_not_run_owned` |
| `qualify_networks` | `lost-response` | 2 / `docker_response_invalid` |
| `qualify_networks` | `replacement` | 2 / `network_replaced` |
| `qualify_networks` | `old-daemon` | 2 / `docker_28_required` |
| `qualify_networks` | `malformed` | 2 / `docker_response_invalid` |
| `qualify_networks` | `oversized` | 2 / `docker_response_invalid` |
| `qualify_networks` | `slow` | 2 / `docker_timeout` |
| `qualify_networks` | `daemon-error` | 2 / `network_inspection_failed` |
| `qualify_networks` | `missing-preparation` | 2 / `prepared_run_required` |
| `qualify_volumes` | `positive` | 0 / `volume_synthetic_qualified` |
| `qualify_volumes` | `existing` | 0 / `volume_synthetic_qualified` |
| `qualify_volumes` | `racing-owned` | 0 / `volume_synthetic_qualified` |
| `qualify_volumes` | `foreign` | 2 / `volume_not_run_owned` |
| `qualify_volumes` | `racing-foreign` | 2 / `volume_not_run_owned` |
| `qualify_volumes` | `unsafe-options` | 2 / `volume_not_run_owned` |
| `qualify_volumes` | `cluster` | 2 / `volume_not_run_owned` |
| `qualify_volumes` | `changed` | 2 / `volume_changed` |
| `qualify_volumes` | `lost-response` | 2 / `docker_response_invalid` |
| `qualify_volumes` | `old-daemon` | 2 / `docker_28_required` |
| `qualify_volumes` | `malformed` | 2 / `docker_response_invalid` |
| `qualify_volumes` | `oversized` | 2 / `docker_response_invalid` |
| `qualify_volumes` | `slow` | 2 / `docker_timeout` |
| `qualify_volumes` | `daemon-error` | 2 / `volume_inspection_failed` |
| `qualify_volumes` | `missing-preparation` | 2 / `prepared_run_required` |
| `qualify_daemon_images` | `positive` | 0 / `daemon_images_synthetic_qualified` |
| `qualify_daemon_images` | `index-only` | 0 / `daemon_images_synthetic_qualified` |
| `qualify_daemon_images` | `missing` | 2 / `image_missing` |
| `qualify_daemon_images` | `wrong-id` | 2 / `image_identity_mismatch` |
| `qualify_daemon_images` | `wrong-platform` | 2 / `image_identity_mismatch` |
| `qualify_daemon_images` | `variant` | 2 / `image_identity_mismatch` |
| `qualify_daemon_images` | `replacement` | 2 / `image_identity_mismatch` |
| `qualify_daemon_images` | `old-daemon` | 2 / `docker_28_required` |
| `qualify_daemon_images` | `malformed` | 2 / `docker_response_invalid` |
| `qualify_daemon_images` | `oversized` | 2 / `docker_response_invalid` |
| `qualify_daemon_images` | `slow` | 2 / `docker_timeout` |
| `qualify_daemon_images` | `daemon-error` | 2 / `image_inspection_failed` |

## Final regression and closure

`python3 -m unittest discover -s platform/deployment/tests -p 'test_*.py'`
passed **358 tests in 105.942s**, exit 0, after public qualification and outside the
restricted socket sandbox. Output retained at `/tmp/env-session-regression.log`.

`python3 platform/deployment/dev.py up --target platform/deployment/environments/kdg-local.json
--run-id 2037418f-ce7d-49b0-9c2b-65f5e65fc454` exited 2 `docker_28_required`,
`runtime_ready=false`. No runtime activation or real Docker mutation occurred.

Compilation, scoped whitespace and local links passed. Final review: eleven finding
instances fixed, one disproved, none deferred. All matrix rows have executed coverage.
Seventeen scoped delivery files are included; concurrent Leave/PtS planning stays outside
the commit. During work, epics.md and Leave implementation-plan/planning-handoff-e3 changed
concurrently; their current contents are preserved, never restored to the initial snapshot.
No dependency pins, accepted ADRs, shared UI or root agent instructions changed.
