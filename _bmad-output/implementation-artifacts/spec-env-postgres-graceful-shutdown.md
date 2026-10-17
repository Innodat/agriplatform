---
title: 'ENV bounded verified PostgreSQL shutdown'
type: 'feature'
created: '2026-10-17'
status: 'done'
route: 'dispatch'
baseline_commit: '15adfda286d843fd170620eff7e2091761cec340'
review_loop_iteration: 0
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/platform/deployment/ENV_POSTGRES_BOOTSTRAP_EVIDENCE.md'
---

<frozen-after-approval reason="standing user approval for bounded ENV implementation and isolated synthetic verification">

## Intent

**Problem:** The actual selected-image bootstrap proof removes a running PostgreSQL container with force even on success. It proves initialization but provides no reusable evidence of bounded, clean shutdown needed by ENV lifecycle delivery.

**Approach:** Extend the existing lifecycle owner and existing `postgres-bootstrap` control to request bounded normal shutdown and verify the actual stopped process state before reporting successful qualification. Keep full runtime admission and all dependent work gated.

## Boundaries & Constraints

**Always:** Keep exact approved dependency baseline including TypeScript7.0.2 and current owners. Reuse current prepared/source/image evidence, exact bootstrap/key authority, bounded runner, fresh network-none/tmpfs container and ownership checks. Require matching ID/image/labels/network/storage/limits before shutdown and removal. Initialization retains its120-second deadline; shutdown has a separate fixed phase budget (at most15 seconds), Docker stop timeout5 seconds, individual command cap10 seconds, followed by existing independent cleanup budget. Bound all waits/output. A successful stop command alone is insufficient: require observed exited state, not running/dead, PID0, exit0, no OOM or error, and a nonzero completed UTC FinishedAt after the verified started instance. Return selected safe fields/codes only. Always remove only the currently verified owned synthetic container, and verify removal. Uncertain ownership refuses deletion. Preserve every current Leave/PtS working-tree/index change.

**Never:** Enable `up`, real CLI container dispatch, persistent volumes/reuse/recovery, whole Supabase startup, owner SQL/migrations, app accounts/grants, infrastructure/deployment or real data. No second generator/service/runner. Do not claim durable data, crash recovery or clean shutdown after forced removal, timeout, OOM or unexplained exit. Existing default Docker transport restrictions remain unchanged.

## I/O & Edge-Case Matrix

| Scenario | Input/state | Expected behavior | Failure handling |
| --- | --- | --- | --- |
| Clean shutdown | Successful actual bootstrap checks; owned running PostgreSQL | Fixed bounded stop then observed clean exit then removal; shutdown_verified=true, forced_shutdown=false, runtime_ready=false | Safe selected evidence |
| Unclean termination | OOM, nonzero exit, dead/error state, incomplete/stale timestamps | Refuse successful shutdown qualification | Explicit safe shutdown failure code; owned cleanup only |
| Still running or stalled | Stop exits0 but process running, command timeout or exhausted shutdown deadline | Refuse; never report clean exit | Independent bounded cleanup; no replay/adoption |
| Changed ownership | ID/image/label/network/limits change before or after stop | No further ownership-dependent stop/removal | cleanup_unresolved if ownership cannot be established |
| Earlier bootstrap failure/interruption | SQL/key/control fails before clean shutdown | Preserve failure and existing owned cleanup semantics | Never synthesize successful shutdown evidence |
| Cleanup failure | Stop succeeds but rm/absence observation fails | No overall success | cleanup_unresolved |

</frozen-after-approval>

## Code Map

- `platform/deployment/startup_lifecycle.py`: `run_bootstrap` owns exact bounded command sequence, selected SQL/key checks and independent cleanup; `qualify_bootstrap` validates owner receipts before/after. Extend this owner, not a new runtime adapter. `owned()` currently validates configuration but not state; add a focused clean-shutdown state validator as appropriate.
- `platform/deployment/images.py`: existing bounded process runner; no new runner needed.
- `platform/deployment/tests/test_postgres_bootstrap.py`:26 existing acceptance/matrix tests and DockerDouble protect initialization, isolation, ownership, budget and cleanup. Evolve stateful double to distinguish before/after stop, without changing unrelated expected failures.
- `platform/deployment/tests/qualify_startup.py`: existing explicit control already invokes the owner; additive safe output only, no new CLI entrypoint.
- `platform/deployment/fixtures/supabase-pg17-profile.md`, `ENV_POSTGRES_BOOTSTRAP_EVIDENCE.md`, `DEVELOPMENT.md`: current authority/limits and proof status. Source-bound authority changes must precede final fresh qualification.
- `apps/kdg-capture/docs/{next-session.md,.memlog.md}`: append exact bounded completion and remaining ENV/P1/SERVICE gates, preserving historic evidence.

## Tasks & Acceptance

**Execution:**
- [x] `platform/deployment/tests/test_postgres_bootstrap.py` -- add behavioral acceptance first: a successful proof must actually issue stop and observe clean shutdown before rm; observe failure against current production code before edits. Then focused TDD for all matrix rows.
- [x] `platform/deployment/startup_lifecycle.py` -- implement bounded shutdown and strict selected state/timestamp validation through current ownership and cleanup paths. Preserve existing120-second initialization and10-second cleanup bounds.
- [x] Existing proof/runbook/source-authority documents -- record requirement-to-test commands/results, actual fresh selected-image verification, unexpected attempts, and scaffold/shared-UI/context/documentation/ADR impact decisions.
- [x] KDG handoff/memlog/spec -- record completion and remaining real CLI/durable-volume/scaffold work without claiming enclosing readiness.

**Acceptance Criteria:**
- Given the selected image initialized successfully, when qualification shuts it down, then real Docker reports the same owned instance exited cleanly before removal, and the result reports verified shutdown plus runtime_ready=false.
- Given forced/uncertain/incomplete shutdown or changed ownership, when the command finishes, then it cannot report clean shutdown or successful qualification, and cleanup never deletes unowned resources.
- Given final source changes, when verification completes, then focused cases and deployment regression pass, actual image proof uses fresh owner receipts, and all retained evidence remains unchanged.

## Implementation Notes

No intent gaps or irreversible live action. User's standing approval and latest next cover this bounded synthetic item. Implementation agent runs only no-socket focused unit tests, records behavioral RED before production edits, and reports it to root; root alone performs serial actual Docker/public CLI/socket verification. No agent commits. Characterize old behavior before any risky refactor; prefer direct extension. Root owns final evidence/runbook/handoff/memlog and scoped commit; implementation agent updates source-bound authority text before declaring sources stable.

## Spec Change Log

## Review Triage Log

All three layers reported before triage. Blind and edge reviewers were fresh; the runtime thread limit required re-engaging the independent read-only investigation agent for the verification layer (not the implementer). Verification layer reported no gaps.

| Finding | Verdict and evidence | Route |
| --- | --- | --- |
| Blind 1: late final cleanup observation | medium: call checks completion only in shutdown; a final empty container listing after cleanup deadline can qualify. Patched cleanup completion bound; delayed final observation regression passes. | patch |
| Blind 2: forced-cleanup diagnostic fields | false: failed qualification returns selected refusal, never success flags; cleanup_unresolved separately identifies unresolved cleanup. Existing failure cleanup is explicitly retained, with no claim of clean shutdown/recovery. No caller interprets a refusal as clean exit. | reject |
| Blind 3: future timestamps | false: contract requires same started instance and strictly ordered valid UTC timestamps, not host wall-clock synchronization. Capturing StartedAt before SQL and comparing it after stop establishes instance continuity without a cross-clock freshness promise. | reject |
| Blind 4: interruption at post-stop/final recheck | medium: these distinct finally paths lack explicit focused cases; added tests asserting no successful result and expected removal behavior; both paths pass. | patch |
| Blind 5: final evidence placeholder | low: final results are pending at review time; replace placeholder with durable final results before completion. | direct documentation correction |
| Blind 6: unchecked spec tasks/review log | low: delivery bookkeeping is pending; complete statuses and log. Skill rejects findings whose fix is editing this spec. | reject; ordinary completion bookkeeping |
| Blind 7: missing memlog | low: required completion entry is pending, add one append-only event before commit. | direct documentation correction |
| Blind 8: unrelated Leave diff | low: all-baseline review intentionally included concurrent work, but scoped commit must exclude it. Preserve and verify unrelated hashes/index. No Leave changes will be committed. | commit-scope correction |
| Edge 1: duplicate/nonstandard JSON ownership not latched | medium: dev.decode raises duplicate_key/invalid_json directly; owned latches neither, so subsequent valid observation permits cleanup. Patched both; malformed/duplicate/NaN restored-observation cases pass. | patch |
| Root: existing image-negative matrix timeout | medium: pre-patch full run466 returned docker_timeout instead of image_identity_mismatch in unchanged resources guard; exact focused test passed13.012s. Scenario was not retained because assertion is outside subTest; capture safe labels on recurrence. | defer, pre-existing reliability limitation |
| Root: existing intermittent process-cleanup assertion | medium: first full run failed unchanged test_resources assertion; four focused runs and subsequent full run passed without altered expectations. Cause remains unobserved; retain failed log and investigate diagnostic capture on recurrence. | defer, pre-existing reliability limitation |

## Verification

Final closeout: root focused40 PASS0.263s; fresh patched-source run885056ba-e9dc-41a2-9e3e-f207d75bdeb2 prepare/toolchain/images PASS, actual SQL/key/clean shutdown/cleanup PASS35.832s. All13 retained files unchanged; three unrelated Deals containers appeared running, no before entry disappeared, no proof command targeted them. Public up exits2 runtime_adapter_unqualified. Final diagnostic-only unittest full discovery469 PASS288.899s exit0; no assertions/deadlines changed. Final exact commands/hashes and earlier failed attempts are in ENV_POSTGRES_SHUTDOWN_EVIDENCE.md. Three review layers complete, patch fixes verified, two pre-existing reliability investigations deferred. Five impact decisions recorded; concurrent Leave/PtS files and index preserved.

Observed: behavioral RED 27 tests (one expected failure), focused GREEN 37 tests. Actual selected-image shutdown proof PASS in 37.966s, retained evidence and running inventory unchanged. Full regression initially failed one pre-existing process-cleanup assertion (465 tests); focused reproductions passed and full rerun passed 465. Final regression includes all additional positive budget and review regression tests.

- `python3 -m unittest discover -s platform/deployment/tests -p test_postgres_bootstrap.py` -- behavioral RED, then all matrix rows GREEN.
- Existing `dev.py prepare`, `toolchain.py qualify`, `images.py qualify` with explicit target and fresh UUID -- source-bound prerequisites PASS.
- `python3 platform/deployment/tests/qualify_startup.py --target platform/deployment/environments/kdg-local.json --run-id <fresh-UUID> --control postgres-bootstrap` -- actual SQL/key plus clean shutdown and cleanup PASS; runtime false.
- `python3 -m unittest discover -s platform/deployment/tests` -- original465-test passing rerun and failed attempts retained. Final patched suite uses `python3 /tmp/env-shutdown-full-diagnostic.py`, identical complete unittest discovery/assertions with safe failure-only diagnostics:469 PASS, durable log/exit/count and runner bytes retained.
