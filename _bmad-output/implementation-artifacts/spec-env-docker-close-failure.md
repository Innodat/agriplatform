---
title: 'ENV preserve failures during socket close'
type: 'bugfix'
created: '2026-10-19'
status: 'done'
route: 'oneshot'
baseline_commit: '7e2ceeb66892a7be08cf578c314971c322b62c75'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="standing bounded ENV implementation and synthetic verification approval">

## Intent

**Problem:** Existing DockerSession.close can raise OSError while an exchange or
context body is already failing, replacing that original failure and its safe JSON
classification. A second exit can repeat the same close attempt because the stream
reference remains installed.

**Approach:** Keep the existing transport owner. Permanently invalidate and detach
its stream before one close attempt. Preserve an already-active exchange/body error
when socket close raises OSError, including the original selected diagnostic and
existing timeout/unavailable mapping. Explicit close or normal context exit without
an active error still reports its close error. Repeated close/exit never retries;
closed session reuse never reconnects/sends. Preserve active cancellation exceptions;
non-OSError close exceptions keep their prior propagation. A failed close is not proof
of kernel closure or resource cleanup. Keep existing JSON schema, privacy, routes,
deadlines, custody and runtime gates; no new cleanup, replay, admission, service,
generator, dependency, account, deployment or real-data action.

</frozen-after-approval>

## Implementation Notes

bmad-help [BD] selects the existing transport-owner close-error investigation from
the previous Build before broader CLI/Auth continuation. This is one small failure-
preservation goal: no intent gap, no irreversible action, no new public API. Standing
approval covers dirty concurrent preservation and implementation; route oneshot.

Reuse dev.py DockerSession.close/__exit__/exchange, shared refusal_result and existing
ScriptedSocket/qualify_startup fixtures in tests/test_docker_session.py. Characterize
acceptance RED before code; focused TDD covers active timeout/OSError/Refusal/interrupt,
body-only failure, normal-exit/explicit-close failure and no second close/replay.
Production footprint is dev.py only. No startup/resource lifecycle changes.

Record requirement-to-test evidence and five impacts in ENV_DOCKER_CLOSE_EVIDENCE.md,
DEVELOPMENT.md and KDG next-session/memlog. Existing scaffold owner is enhanced;
shared UI/context unchanged; ADR0023 applies without editing accepted ADRs. Exact
TypeScript7.0.2/mail15484/target and concurrent documents/index/resources remain.

Verify the session/gate suites, selected existing resource no-replay process cases,
and affected fast network/volume/image owner suites; no actual Docker runtime
expansion or new readiness proof is claimed. Existing source-bound receipts remain
preserved and require fresh preparation before future actual qualification. The
prior638-test regression remains evidence for the preceding commit; do not relabel
it as this source's result. Complete the oneshot independent review and scoped local
commit without push. Broader ENV/runtime/P1/SERVICE and dependent gates remain open.

Acceptance RED observed: original docker_timeout becomes startup_proof_refused when
close raises OSError. Minimal dev.py correction detaches before close and ignores
only OSError during an existing failure. Four initial regression methods plus one
non-OSError propagation characterization cover all declared states. Root31 session
PASS0.428s,92 gate/network/volume/image PASS44.149s, one four-case private process test
PASS7.142s. Broad -k close sandbox attempt cannot bind a pre-existing peer fixture;
its error is retained and the authorized full session suite passes. No expected
result/deadline changes. Five impacts and command/log digests recorded in evidence;
existing broader638 verification is not relabelled as current. Review results follow.


## Review Triage Log

- R1 — low / patch: double-failure tests covered connect only; later-phase classification
  lacked direct protection. Added send/receive/idle_after/budget_after plus close OSError.
- R2 — low / patch, grouped with R1: no mutating lost-response combination. The same
  matrix now records partial/full POST transmission and asserts exactly one send/socket/
  close and refused reuse, retaining uncertainty without replay. Existing four-case
  process test separately verifies the unchanged owner handoff/cleanup boundary.
- R3 — low / patch: normal-close test did not follow successful exchange into public
  output. New qualifier regression proves successful wire response plus close OSError
  emits only failure/runtime_ready=false and no fabricated failure observation.
- R4 — low / patch: non-OSError coverage omitted explicit/body paths. Expanded existing
  matrix to exchange/explicit/body with RuntimeError and KeyboardInterrupt; propagation
  remains the same exception and the close is attempted once.
- R5 — low / patch: acceptance filenames lacked exact commands/digests. Added the
  executed command and immutable RED/GREEN log hashes to the evidence ledger.

All five verified coverage/evidence gaps addressed in four patch groups; none newly
deferred. Final33 session PASS0.449s,92 affected owner PASS44.149s, one four-case process
PASS7.142s:126 tests, no full-suite or fresh actual-Docker runtime claim. Source behavior
unchanged after the initial minimal fix; later edits add tests/docs only (including a
class docstring clarification). Five impacts and original failed sandbox/test evidence
are retained. Frozen intent, baseline and approved target remain unchanged; concurrent
files/index and all Docker resources are preserved. Scoped local commit follows.
