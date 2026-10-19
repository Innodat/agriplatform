---
title: 'ENV bounded binary archive transport'
type: 'feature'
created: '2026-10-19'
status: 'done'
route: 'dispatch'
baseline_commit: 'd53a3c38b03bd66c547b6591c19956a3c92e396e'
review_loop_iteration: 0
---

<frozen-after-approval reason="standing bounded ENV implementation and isolated synthetic verification approval">

## Intent

The source-derived Kong three-file archive exceeds the Docker transport's 16KiB
aggregate request limit, so the existing transport cannot carry the next gateway
lifecycle's validated input. Support bounded binary archive transfer through the
existing persistent Docker session, with exact wire/framing and failure evidence.
This is a prerequisite within ENV, not gateway execution or full runtime readiness.

## Boundaries & Constraints

Always retain the exact existing persistent PUT route
`/v1.48/containers/<64 lowercase hex>/archive?path=%2F`, exact bytes type and
application/x-tar. Allow at most65536 body bytes and1024 header bytes (including
header terminator) independently on that route. Preserve16384 aggregate request
bytes for every other admitted request, including JSON. Check limits before
constructing the final combined request or opening/sending on a socket. Reject
oversized binary input before copying it into a request. Preserve the current
empty/small archive compatibility; archive structure/content remains the existing
caller's responsibility, not a transport-layer policy or extraction operation.

Retain one persistent connection, exact Content-Length, existing deadline, idle,
response framing, failure diagnostic vocabulary and permanent no-replay invalidation.
Observe actual source-generated Kong archive transfer and a subsequent request on
the same private peer. Preserve PostgreSQL single-member archive compatibility.
Keep transfer contents out of logs, evidence, hashes and exception text; public
source snapshots may retain their existing source hashes. Synthetic peers may
compare received bytes in memory using safe assertions without dumping content.

Never add a route, public daemon selector, qualifier control, Kong create/copy/start
owner authority, retry/reconnect, generic transport/service engine, or change source
fixtures/profile/native-key behavior. Keep original CLI terminated and all existing
custody/cleanup contracts; runtime_ready and fresh_setup_completed remain false.
No actual Docker, migration, provisioning, deployment, real credentials/data or push.
Preserve concurrent work/index and52 historical prerequisite files, uncertain Docker
resources, existing owners, TS7.0.2/mail15484 and pinned dependency baseline.

## I/O & Edge-Case Matrix

| Scenario | Input/state | Expected result | Failure |
| --- | --- | --- | --- |
| Kong archive | Validated source-derived three-file archive >16KiB, persistent canonical route | Exact body/framing,204 then next request over same connection | No new success/readiness fact |
| Boundary | Binary body65536/65537 bytes | First accepted, second refused before socket/send | docker_request_invalid |
| Other requests | Oversized JSON, changed route/method/type or nonpersistent archive | Existing limit/route refusal | No socket access |
| PG compatibility | Existing10240-byte public archive | Exact bytes transmitted under current contract | Existing behavior |
| Transport failure | Short response/EOF, timeout, cancellation or send error | Session closed permanently; next exchange refused | Existing safe error/observation |

</frozen-after-approval>

## Code Map

- `platform/deployment/dev.py`: `_docker_request` owns route/type serialization and
  request bounds; DockerSession.exchange owns connection/deadline/error semantics.
  Change only bounded request construction; retain existing lifecycle/response code.
- `platform/deployment/startup_lifecycle.py`: public_archive and kong_archive /
  validate_kong_archive supply actual test inputs; no implementation change needed.
- `platform/deployment/tests/test_docker_session.py`: existing private Unix Peer and
  scripted sockets, transport acceptance and edge cases. Extend byte observation
  safely in memory; never print payloads or persist archive hashes.
- `platform/deployment/tests/create_profile_fixtures.py`: boundary_fixture supplies
  closed pinned synthetic Kong profile; no new generator or source snapshot.
- `platform/deployment/tests/test_docker_gate.py`: existing protocol compatibility.
- `platform/deployment/tests/test_startup_lifecycle.py` and test_pinned_execution.py:
  selected archive and unchanged Kong-refusal regression tests.
- `platform/deployment/DEVELOPMENT.md`, ENV_ARCHIVE_TRANSPORT_EVIDENCE.md,
  `apps/kdg-capture/docs/next-session.md` and .memlog.md: requirement/test evidence,
  honest limits and scaffold/UI/context/documentation/ADR impact decisions.

## Tasks & Acceptance

- [x] Existing private transport tests: observe source-derived archive acceptance RED.
- [x] dev.py and transport tests: focused TDD for separate binary/header bounds and
  unchanged other limits/routes, exact wire and failure/no-replay behavior.
- [x] Existing owner tests: verify PG transfer and Kong-create refusal unchanged.
- [x] Evidence/runbook/handoff: commands/results, source bindings, five impacts and
  remaining image/profile/native-key/custody/health/disposal/scaffold prerequisites.

**Acceptance Criteria:**
- Given a validated Kong archive, when the existing persistent transport sends it,
  then the private peer sees exactly its bytes and a next request without reconnect.
- Given oversize/invalid input, when exchange is attempted, then no request is sent
  and safe refusal permanently invalidates the session without payload disclosure.
- Given failure after a transfer begins, when another exchange is attempted, then
  no replay/reconnect occurs and the original error precedence remains unchanged.

## Implementation Notes

bmad-help selects Build after completed Kong boundary. Read-only delegated
investigation confirms archive-specific allowance is compatible with owner contracts;
DEVELOPMENT.md's historical16KiB statement needs clarification. No intent gaps or
irreversible effects; dispatch footprint is transport/tests/docs. Standing approval
covers the dirty-tree continuation and this bounded implementation. Root owns
spec/docs/evidence/review/commit; implementation delegate owns dev.py and tests.
Checkpoint: platform/deployment/.local/kong-archive-transport/checkpoint.json binds
17 concurrent files,52 receipts and original index. No dependent work is admitted.

## Verification

Use PYTHONPATH=platform/deployment:platform/deployment/tests with python3 -m unittest
for transport acceptance/focused tests, affected transport/protocol suites and selected
archive/Kong-owner regressions. Record exact test IDs/counts/results and source/log
hashes in evidence; never hash or dump runtime transfer data.

## Review Triage Log

- Acceptance RED1/0.054s; focused GREEN5/0.028s. Root affected transport/protocol/archive/Kong-owner verification67 PASS8.856s without skips;40 source/test bindings unchanged. Initial204 expectation corrected using existing parser contract (None); response code unchanged. Root reviewed all code/tests and audited every matrix row against passing selectors in ENV_ARCHIVE_TRANSPORT_EVIDENCE.md.


| Finding | Verdict | Evidence / route |
| --- | --- | --- |
| B1 payload-bearing mock assertion failure dumps | medium | Mock assertion failures include call arguments, which contain the archive. Patch numeric call_count assertions in new tests; no runtime change. |
| B2 no explicit partial-send witness | low | Existing case raises before modeling prefix acceptance. Add a prefix-accepted failure scenario to the existing no-replay test. Patch, preserving production sendall ownership. |
| B3 ignored evidence lacks regeneration recipe | low | Exact test command already exists, but source manifest generation uses an ignored runner. Add a self-contained source/log reproduction command to durable evidence. Patch. |
| B4 joined words/numbers in prose | low | Runbook/evidence/handoff contain missing spaces. Direct prose correction, patch. |
| B5 incorrect media-type spelling | low | Runbook uses application-x-tar; actual code uses application/x-tar. Correct prose and separate the two HTTP headers, patch. |

Edge review returns[]; verification-gap review finds no gaps. Gap review's attempted
sandboxed run could not bind sockets and is not PASS evidence; root's authorized
67-test observation is the verification authority. All5 blind findings individually
triaged before grouping; no rejections/deferrals. B1/B2 delegated test patches;
B3/B4/B5 root documentation patches. Runtime source remains unchanged.

Final patch verification:67 affected methods PASS7.945s, no skips;40 source/test bindings unchanged across final call. Only the test module changed during review. All5 findings patched, no new deferrals. All matrix rows audited against final passing tests.
