---
title: 'ENV: preserve daemon connection continuity during acquisition'
type: feature
created: '2026-10-16'
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: f3251d22a6a8b9862f3753727d72688a9d54c648
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/platform/docs/architecture/contracts/scaffold-environment-and-generation.md'
---

<frozen-after-approval reason="Standing bounded ENV implementation approval and user continuation">

## Intent

**Problem:** Each Docker request reconnects. A version check and subsequent resource
acquisition can therefore reach different endpoints during one adapter operation.
**Approach:** Reuse one bounded Unix HTTP connection for each existing network, volume
and image acquisition. Never reconnect or replay after disconnect/uncertainty.

## Boundaries & Constraints

**Always:** Acceptance failure before implementation and focused TDD; characterize the
existing parser before risky refactoring. Preserve fixed route/method allowlists,
strict framing, request/response limits, safe error codes, current run locks/evidence
checks and total daemon deadlines. Close session resources on every exit. Keep existing
single-exchange callers compatible. All verification uses isolated synthetic Unix
servers; source-bound preparation must be fresh. Preserve concurrent Leave/PtS work
and the exact baseline including TypeScript 7.0.2.

**Never:** Real Docker mutation, pulls/containers/SQL, deployment, infrastructure,
account/access changes or pilot data. No proxy/server, generic service, new generator,
new public endpoint selector or runtime activation. No automatic reconnect/retry,
redirect, pipelining, chunked-body support or expanded Docker routes. One adapter's
connection is not a combined startup session, resource exclusivity, volume freshness,
bootstrap safety or full runtime readiness; report those limitations explicitly.

## I/O & Edge-Case Matrix

| State | Required behavior |
| --- | --- |
| Valid version and network/volume/image operation | Exactly one accepted connection carries every request; unchanged resource result |
| Socket path replaced after version | Original connected peer continues or operation refuses; replacement receives no request |
| Peer closes before/after create or between reads | Safe refusal, no reconnect or replay, including uncertain mutation |
| Malformed/truncated/duplicate/oversized or unsolicited extra HTTP bytes | Safe refusal; unusable session cannot be reused |
| HTTP connection-close signal or HTTP/1.0 response | No continued session or fallback reconnect |
| Slow trickle or multiple individually fast requests exceed total budget | Deadline applies to entire operation, no per-request reset |
| Invalid route, foreign resource, stale evidence or invalid preparation | Existing refusal and no unauthorized request/handoff |
| Normal exit, refusal, callback exception or reuse after close | Descriptor released; closed/failed session cannot send |

</frozen-after-approval>

## Code Map

- `platform/deployment/dev.py`: extract/share existing closed route allowlist and strict
  Content-Length parser in a context-managed session. Preserve one-shot callers and
  docker_prerequisite compatibility. Connect only after preparation validation; never
  reconnect or reuse a failed session. No new module unless needed (then bind it in
  dev.SOURCES and tests/test_dev.py:FILES).
- `networks.py:acquire`, `volumes.py:acquire`, `daemon_images.py:acquire`: use one session
  for version/resource requests under current locks/deadlines; preserve evidence and
  handoff checks. Image tool probes remain outside the daemon phase/connection lifetime.
- `tests/qualify_networks.py`, `qualify_volumes.py`, `qualify_daemon_images.py`: extend
  existing private servers to sequential keepalive requests with independently counted
  connections, exact old request oracles and disconnect/replacement controls.
- `tests/test_docker_gate.py`, new `tests/test_docker_session.py`, adapter suites:
  characterize parser, prove matrix including bad second responses, total deadlines,
  uncertain mutation without replay, replacement endpoint isolation and cleanup.
- `DEVELOPMENT.md`: guarantee/limits and runtime gates. Root owns evidence/navigation/
  memlog/spec/commit; implementer owns code, focused tests and runbook.

Compatibility sources: Moby v28.0.0 constructs standard Go http.Server and Serve
listeners; Go documents default keepalive. This supports mechanism, not real qualification:
https://raw.githubusercontent.com/moby/moby/v28.0.0/cmd/dockerd/daemon.go
https://pkg.go.dev/net/http#Server.SetKeepAlivesEnabled

## Tasks & Acceptance

- [x] Characterize old parser and observe one-connection acceptance RED.
- [x] Implement shared bounded session and integrate all three existing adapters.
- [x] Cover every matrix row; run focused affected tests, preserve old controls.
- [x] Fresh preparation and private-daemon public qualification; full deployment suite
  sequentially afterward, compile/whitespace/local links and real read-only up gate.
- [x] Record requirements/tests, five impacts, review/fixes and scoped local commit.

Given a current prepared run, when an adapter acquires its resources, then its version
and resource requests use one connection and unchanged owner checks remain binding.
Given a failed or replaced connection, when acquisition continues, then it cannot
switch endpoints or replay a request, and cannot report readiness or handoff success.

## Implementation Notes

No unresolved product choice or irreversible action. Dispatch implementer owns code,
focused tests and runbook; root owns final qualification, evidence, next-session,
memlog, review and commit. Do not run full regression or public prepare concurrently
with root. Capture exact RED and passing commands/results. New private adapter APIs
make this a dispatch change. Five impacts: existing ENV scaffold owner; no shared UI
or root agent-context change; owner docs updated; accepted ADRs unchanged.

## Spec Change Log

## Review Triage Log

## Verification

Focused unittest test_docker_session/test_docker_gate and affected adapter suites,
then existing public qualifier controls using fresh source-bound preparation. Image
qualification may need fresh tool/image receipts; root handles this serially. Run
`python3 -m unittest discover -s platform/deployment/tests -p 'test_*.py'` outside
restricted socket sandbox after public controls. Compile affected Python; scoped diff
check and local documentation links. Real up must still refuse before activation.

## Review disposition — initial pass

All three layers returned before triage. Every finding is recorded individually below;
B1/E2 and B2/E1 share causes. Corrections remain local, add no public surface and guard
demonstrated states. No intent gap or decision change; no finding deferred.

| Finding | Verdict / route | Evidence |
| --- | --- | --- |
| B1 select descriptor ceiling | medium / patch | Root reproduced ValueError with descriptor2048; poll removes the artificial limit, with focused proof. |
| B2 final exchange omitted | medium / patch | Loops stop before network7/volume4/image9. Include final missing/truncated response and synchronized observable EOF. |
| B3 disconnect coverage omits existing/conflict paths | medium / patch | New loops use only default create path; existing controls cover normal behavior but not disconnect boundaries. Extend these small matrix cases. |
| B4 unconditional extra-byte claim | low / patch | Zero-time poll cannot detect future bytes after completed exchange. Document detection at framing/idle checks and no guarantee of future liveness; add synchronized final-trailer coverage. |
| B5 disconnect-after race | medium / patch | sendall then handler return races client idle check. Synchronize EOF visibility for deterministic final-boundary assertion. |
| B6 decode exceeds deadline | medium / patch | Root deterministic clock advances to2 during decode against deadline1; existing exchange returns success. Check budget after response processing. |
| B7 single-caller ownership unspecified | low / patch | Existing callers are sequential; class wording lacks explicit single-caller restriction. Direct documentation correction, no concurrency API/locking added. |
| B8 missing delivery evidence | false / reject | Root-owned ENV_DAEMON_SESSION_EVIDENCE.md already records exact RED/GREEN, traceability and all five impacts; excluded from code review diff, finalized after qualification. |
| E1 final disconnection gap | medium / patch | Same omitted final requests as B2; retain individual finding, grouped correction. |
| E2 select descriptor ceiling | medium / patch | Same independently reproduced high-descriptor failure as B1. |
| E3 synthetic partial-body EOF hang | medium / patch | Peer body loop appends recv result without EOF check, so b-empty never advances and blocks shutdown. Add EOF exit plus bounded regression. |
| V1 image preflight mock obsolete | medium / patch | Acquisition now uses session.exchange; old docker_exchange mock cannot detect premature connection and broad exception assertion masks it. Observe socket boundary and exact evidence refusals. |

Final verification: focused 14 session / 15 gate / 28 network / 21 volume / 18 image passed;
42 public controls on frozen run `2037418f-ce7d-49b0-9c2b-65f5e65fc454` passed with
thirteen retained files/source snapshots unchanged. Full 358 tests passed 105.942s;
compile/whitespace/local links passed. Real up refuses `docker_28_required`. Eleven
review instances fixed, one disproved, none deferred. Exact commands, attempts,
requirement/test mapping, record hash and five impacts:
[owner evidence](../../platform/deployment/ENV_DAEMON_SESSION_EVIDENCE.md).
