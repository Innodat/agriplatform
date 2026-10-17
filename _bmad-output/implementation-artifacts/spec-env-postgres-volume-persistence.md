---
title: 'ENV PostgreSQL named-volume persistence qualification'
type: 'feature'
created: '2026-10-17'
status: 'done'
route: 'dispatch'
baseline_commit: '057880e40f20a80d7a027b11a76bfeecde983452'
review_loop_iteration: 0
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/platform/docs/architecture/contracts/scaffold-environment-and-generation.md'
---

<frozen-after-approval reason="standing approval for bounded ENV implementation and isolated synthetic verification">

## Intent

**Problem:** Fresh named-volume CLI execution now passes, but no proof shows initialized data surviving container replacement.

**Approach:** Add an explicit persistence qualifier to the existing retained ENV owner: actual CLI first start, committed synthetic marker, clean stop/container removal, owner recreation on the same proven volume, marker/cluster verification, then clean shutdown and disposal.

## Boundaries & Constraints

**Always:** Preserve exact approved baseline including TypeScript7.0.2, current owners and concurrent Leave/PtS work/index. Fresh qualified synthetic UUID only; retain source/executable/fixture/listener/run-lock custody and one DockerSession. Keep original five-second acquisition and first execution120s; first shutdown/removal15s, one recreation/verification120s, final shutdown15s, final cleanup10s. Consume transitions before uncertain mutation; never reset polling budgets. Recheck image/profile/bridge/volume and references at each mutation. Require old ID absent, unused unchanged volume and empty bridge before distinct new container ID; only this execution's confirmed-created volume may cross that gap. Restore the existing public root-key archive to the replacement container. Verify both stable healthy instances and strict clean exits. SQL checks must fail on false predicates: commit run UUID plus PostgreSQL system identifier, require that exact row/cluster and existing initialization markers after recreation. No reinitialization or marker repair. Return only safe proof facts, runtime_ready=false. Preserve ambiguous resources and report failure; container-free-gap failures may retain run resources without a cleanup claim.

**Never:** Public up/stop/reset admission, cross-run initialized-volume adoption, recovery/backup claims, full CLI restart-branch or Auth readiness, product migrations/seeds/accounts/grants, real data, infrastructure/deployment/pilot, another generator/service or generic SQL/exec interface. Existing controls keep their behavior.

## I/O & Edge-Case Matrix

| State | Behavior | Failure handling |
| --- | --- | --- |
| Fresh qualified run | CLI first lifecycle, distinct replacement, persisted marker/cluster, both clean exits, owned disposal | Selected facts only |
| Lost marker/reinitialized database/SQL nonzero | No persistence success or repair | Bounded owned cleanup |
| Changed ownership/reference/custody | Refuse next mutation; latch loss | No later deletion after restoration |
| Lost/malformed create/remove/exec response | Consume phase, no retry/reconnect/adoption | Preserve uncertain resources |
| Wrong/repeated lifecycle or exec operands/ID | Reject before dispatch | Safe failure |
| Deadline/interruption/restart/unclean exit | No successful persistence/recovery claim | Single bounded cleanup, unresolved refusal |

</frozen-after-approval>

## Code Map

- `platform/deployment/resources.py`: extend FreshGuard.finish_execution through explicit recreation phases; reuse owned/joint/created and strict shutdown checks. Never reset phase2/execution_started to replay create; do not consume cleanup_execution for intermediate removal.
- `platform/deployment/dev.py`: persistent-only fixed exec-create/start/inspect JSON routes. Detached exec, no attached streams/hijacking: all attachments/Tty/Privileged false, User postgres, fixed public PGPASSWORD and fixed psql argv/predicate SQL only. Validate exec/container identity, ProcessConfig, completed Running=false and integer ExitCode0. Pre-start requires explicit null exit/PID0; completed exit requires integer zero. Docker may retain a positive Pid after exit.
- `platform/deployment/startup_lifecycle.py`: owns public bootstrap predicates/archive; add closed UUID-bound probe SQL here. No external subprocess transport for retained operations.
- `platform/deployment/startup.py`, `tests/qualify_startup.py`: add explicit `pinned-cli-postgres-persistence` control; keep actual CLI killed at first executed start. Report owner recreation separately from CLI first-start proof.
- `platform/deployment/tests/test_pinned_execution.py`, `test_resources.py`: independent daemon and process fixtures; preserve existing expectations. PG_VERSION skips image initialization; key transfer remains necessary.

## Tasks & Acceptance

- [x] Existing test owners: observe persistence acceptance RED, then focused TDD for every matrix row and legacy characterization.
- [x] Existing source owners above: guarded SQL, replacement lifecycle and precise explicit-control facts.
- [x] `platform/deployment/fixtures/supabase-pg17-profile.md`, `ENV_POSTGRES_PERSISTENCE_EVIDENCE.md`, `DEVELOPMENT.md`: exact authority/commands/requirement-test evidence and five scaffold/UI/context/documentation/ADR impacts.
- [x] `apps/kdg-capture/docs/next-session.md`, `.memlog.md`, this spec: truthful completion/remaining gates and review disposition.

Given a fresh source-qualified target, when the explicit proof succeeds, then a distinct replacement reads the committed run/cluster marker and initialization predicates before verified clean disposal. Given uncertainty or stale custody, when qualification fails, then it cannot replay mutations or claim persistence/readiness.

## Implementation Notes

Acceptance RED observed before implementation (missing enable_persistence); root42 focused tests PASS0.512s and corrected supervisor5 PASS26.524s. Initial real exec refused invalid_exec; primary Moby optional ExitCode semantics explain it. Null lifecycle characterization failed before correction, without weakening completed-zero checks. Fresh629d85cd proof passes actual persistence113.812s and preserves13 receipts/running inventory. Earlier failed/interrupted qualification artifacts remain retained; existing controls pass; full516 tests PASS348.807s. Review follows.

Root alone runs Docker/socket/process checks serially and owns evidence/handoff/memlog/commit. Agent runs no-socket focused tests only. Two prior intermittent failures remain deferred. No intent gaps.

## Spec Change Log

Matrix audit: all six frozen rows have executed passing coverage in the42 focused tests and5 supervisor tests, included again without skips in full516 PASS. Exact named coverage and retained actual positive/negative results are in the evidence. Five impact decisions recorded; source-bound proof inputs and concurrent files/index unchanged.

## Review Triage Log

All three layers reported before triage; edge-case layer returned no findings.

| ID | Verdict | Evidence and route |
| --- | --- | --- |
| V1 | medium | Pre-verified mutation removes cluster matching while42 focused tests pass. Real SQL mismatch rejection is missing. Patch: run a real fixed negative cluster qualification; retain failure/cleanup evidence. |
| B1 | false | The only production caller is finish_execution, which consumes its own entry before probes; a failed probe unwinds into supervisor finally cleanup (startup.py912–942), never the next probe. Direct private-helper retry cannot complete finish or produce qualification. No caller resumes at schemas after failure. |
| B2 | false | healthy_instance validates unchanged StartedAt/restart state across polling and downstream SQL/stop observations. “Stable” denotes the same running instance; no elapsed health interval is promised. The existing health policy is preserved. |
| B3 | low | initialization_markers currently rejects verify before final schemas. Direct final-schema failure coverage is missing. Patch: fail only the second schemas exec after successful verify. |
| B4 | medium | Independent model does not evaluate individual migration/JWT conjuncts. Patch: exercise actual generated SQL with missing/extra migrations and bad JWT settings and record rejection. |
| B5 | low | Simulated write sets marker before assigning failure, so failed transaction state is inaccurate. Patch: commit model marker only for successful write and prove a failed write leaves no marker. |
| B6 | low | Reused exec-ID guard exists but lacks its direct later-probe test. Patch: assert refusal before another start and no persistence claim. |
| B7 | low | Named replay test repeats SQL only; other uncertainty tests repeat failed finish but successful finish replay is missing. Patch: assert both finish outcomes cannot dispatch or extend deadline. |
| B8 | low | Phase8 protects uncertain post-delete inspection, but tests currently inject uncertainty during delete only. Patch: cover lost/malformed/non404 absence checks and no subsequent mutation. |
| B9 | false | Lost exec identity cannot change the already proven container identity. Existing cleanup owns the container and can safely terminate its exec; uncertain container removal/creation remains preserved. Proposed spec-only wording correction is rejected by workflow; no unsafe cleanup outcome shown. |
| B10 | low | Runbook points at exact inventory without concrete read-only persistence inspection steps. Patch: list selected safe inspect commands/ownership facts without lifecycle replay or deletion. |

Survivors have distinct causes; no grouping. All route to patch; no new defer or intent/spec loopback. Implementation owner patched tests/runbook; root47 focused tests PASS0.518s. Fresh707b9ed0 actual SQL executes all seven corrupt-state predicate checks, then rejects persisted wrong cluster under correct UUID with execution_sql_failed51.934s and verified owned cleanup. Production/profile unchanged; root post-patch521 tests PASS320.764s (no skips); all patches closed. Existing two deferred guard investigations remain open.

## Verification

Run focused/affected tests then full deployment discovery. Fresh prepare/toolchain/images; actual persistence, pinned-cli-postgres, postgres-bootstrap and guarded-fresh controls. Up still refuses runtime_adapter_unqualified. Retain hashes, failures and executed matrix coverage; no relaxed assertions or receipt repair.
