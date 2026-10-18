---
title: 'ENV initialized-volume CLI restart qualification'
type: 'feature'
created: '2026-10-17'
status: 'done'
baseline_commit: '202a2ed14e1594bbea603b9c9f27a28ba52ab092'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/platform/docs/architecture/contracts/scaffold-environment-and-generation.md'
---

<frozen-after-approval reason="standing approval for bounded ENV prerequisites and isolated synthetic verification">

## Intent

**Problem:** The persistence qualifier recreates PostgreSQL through ENV directly; the actual pinned CLI has not recreated it on an initialized volume. This leaves restart command/profile integration unproven.

**Approach:** Add one explicit qualifier that starts fresh through the CLI, commits the existing synthetic probe, clean-stops/removes the first container, then uses a second actual CLI process through initialized-volume create/copy/start. Verify the unchanged committed probe/cluster and initialization predicates before final clean shutdown/disposal.

## Boundaries & Constraints

**Always:** Same fresh UUID, qualified immutable images/executable/source evidence, one FreshGuard/DockerSession/run lock and execution-owned volume/bridge throughout. Preserve TypeScript7.0.2, existing owners/tooling, concurrent Leave/PtS files/index and existing controls. Retain both independent private fixture/workdir/listener custodies through final verification/cleanup; never overwrite/rebind the first. Validate original profile/routing/archive and exact initialized CLI prefix before each corresponding owner action. Existing-volume inspect and ensure acknowledge only the already-confirmed unchanged unused volume; no duplicate volume POST or adoption. Require old container absent and distinct replacement ID. Each transition consumes before uncertainty; no replay/reconnect/deadline reset. Budgets stay acquisition5s, first execution/probe120s, first shutdown/removal15s, second CLI/recreation/verification120s, final shutdown15s, one final cleanup10s. Kill each proven CLI group at its executed start before further service/setup commands. Owner then verifies SQL/health/same-instance clean exits; only one cleanup authority. Return precise safe facts including two CLI start boundaries and runtime_ready=false.

**Never:** Public up/stop/reset activation, cross-execution adoption, post-health CLI webhook/fresh setup/current-branch claims, full stack/Auth readiness, recovery/backup, product migrations/seeds/accounts/grants, real data, provisioning/deployment/pilot, another runner/generator/service, generic SQL/exec or arbitrary restart callback interface.

## I/O & Edge-Case Matrix

| State | Required behavior | Failure handling |
| --- | --- | --- |
| Qualified fresh run then initialized CLI | Truthful existing inspect/ensure, exact create/copy/start, persisted probe/cluster/init, both clean exits and final owned disposal | Selected proof facts only |
| Missing/changed/used volume, image/bridge drift or custody loss | Refuse before next mutation; latch custody loss | Preserve unresolved resources |
| Wrong/repeated phase, token, profile/routing/archive/ID or extra command | Refuse before dispatch; preserve old controls | No repeated mutation |
| Lost/malformed probe/ensure/create/copy/start/removal response | Consume uncertainty, no replay/adoption | Cleanup only where recorded container custody remains proven; preserve container-free gaps |
| Bad marker/cluster/init, health/restart/unclean exit | No initialized persistence success or repair | Single bounded owned cleanup |
| Timeout/interruption/secondary-supervisor failure | No success, no budget extension | Terminate proven groups; cleanup once, preserve ambiguity |

</frozen-after-approval>

## Code Map

- `platform/deployment/resources.py`: FreshGuard owns persistence SQL, joint/owned checks, stop/cleanup. Split removal/recreation; retain both fixture/listener custodies, explicit replacement authority and existing consume-once budgets.
- `platform/deployment/startup.py`: reuse fixture/lifecycle/handoff/observation validators and supervisor. Add truthful initialized inspect/ensure sequence. Keep secondary private context through final verification; no premature successful-start cleanup.
- `create_profile.py`, `startup_lifecycle.py` under deployment retain exact profile/archive/SQL. Pinned source753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4 db-bootstrap/{postgres.service,start-database}.ts has identical fresh/existing create spec; post-health differs. Existing nine-event prefix uses existing_volume_create_refused; new mode needs ensure acknowledgement. Second workdir changes approved workdir labels/routing only.
- `platform/deployment/tests/qualify_startup.py`: literal pinned-cli-postgres-initialized control, default daemon only.
- `platform/deployment/tests/test_pinned_execution.py`, `test_resources.py`: PersistenceDaemon and ExecutionSupervisor own independent sequence/process/cleanup fixtures.

## Tasks & Acceptance

- [x] Tests above: acceptance RED, then focused TDD for all matrix rows.
- [x] Resource/startup/qualifier owners: closed second CLI integration and truthful facts.
- [x] `platform/deployment/fixtures/supabase-pg17-profile.md`, `ENV_INITIALIZED_CLI_EVIDENCE.md`, `DEVELOPMENT.md`: source/command/test evidence and five required impacts.
- [x] `apps/kdg-capture/docs/next-session.md`, `.memlog.md`, this Build record: status/review/remaining gates.

Given qualified disposable inputs, when qualification succeeds, then both CLI start boundaries and persisted data/cluster precede clean disposal. Given uncertainty, when it refuses, then no persistence/readiness or replay is claimed.

## Implementation Notes

Authorized synthetic mutation only. Root runs Docker/socket/process verification serially and owns final evidence/handoff/memlog. Child runs no-socket tests only; no nested workflow/renderer. Preserve existing deferred investigations.

Root56 focused tests PASS1.432s; initialized process3 tests PASS58.005s (four transport-failure subcases). Root read the full staged unified diff and test-only follow-ups. Initial actual b0524560 attempt used unintended private helper fault injection; refused SQL with owned cleanup, not a positive qualification. Helper-only dispatch fixed; first refresh53a5ec38 registry refused before runtime. Fresh18d3de94 qualification pending. Production/profile frozen; no expectation weakened.

Matrix audit: all six rows have passing focused/affected coverage and shared owner cases executed again in full533 PASS410.905s, no skips. Actual ordinary18d3de94 proof113.594s and all legacy controls pass; public up still refuses. Five impacts and concurrent/source binding checks recorded in evidence; review follows.

Reviewed-source closeout2026-10-18: final source-qualified0003c705 actual initialized proof PASS80.575s; exact fresh/initialized boundaries, marker/cluster/init, both clean exits/disposal,13 receipts and running inventory unchanged. Existing persistence/first-start/bootstrap/guarded controls pass; public up refuses. Root59 focused PASS1.127s,8 affected process PASS116.203s and541 full deployment PASS439.549s. All six requirement rows and five impact decisions verified. Earlier fixture failures are explained and retained in evidence; no production deadline or expected refusal weakened. Scoped source/profile and concurrent document/index preservation checked before commit.

## Spec Change Log

## Review Triage Log

All layers reported before triage; edge-case layer found none. Runtime initially refused a third simultaneous reviewer, so its independent context-free run started after the first two finished; no finding was triaged until it returned.

| ID | Verdict | Evidence and route |
| --- | --- | --- |
| B1 | medium | New nested supervisor retains the first reaped numeric group ID through the second lifecycle, then unconditionally killpg signals it again in finally. Numeric reuse could signal unrelated work. Patch: record successful termination and never signal that completed group again; retain failure-path descendant termination. |
| B2 | low | Existing mock failure occurs at first custody check. Patch: fail second custody while first passes and prove authority loss. |
| B3 | medium | Secondary custody is mocked, with no real changed path after replacement creation. Patch: physical wrapper/listener mutation process cases must refuse before next mutation and latch loss. |
| B4 | low | Current initialized deadline test injects a timeout exception, not elapsed secondary phase time. Patch: advance the observed clock past the actual secondary deadline; prove termination/preservation without execution-budget extension. |
| B5 | low | Transport/SQL failures cover nested unwind but no nested KeyboardInterrupt. Patch: inject it after replacement creation and assert both groups terminate, cleanup at most once and no persistence success. |
| B6 | low | Prefix tests omit malformed initialized private envelopes/acknowledgements. Patch: cover their parser/refusal paths and prevent replay. |
| B7 | medium | Direct uncertain-create test omits the nested supervisor on lost/malformed second-create response. Patch: real private-socket cases must preserve unknown replacement and volume, without adoption/delete/replay. |
| B8 | low | Secondary fixture construction/Popen gap lacks a failure case. Patch: inject initialization/binding or launch failure after old removal; assert retained volume, no success and only proven-group termination. |
| B9 | low | Earlier progress notes retain present-tense pending/running statements before later completed results. Reject spec-only revision under workflow; patch current documentation wording to distinguish historical checkpoints from current review gate. |
| B10 | low | Evidence omits exact focused command and direct supported discovery equivalent. Patch documentation with both commands and distinguish actual diagnostic-runner execution. |
| V1 | medium | Pre-verified gap: a phase>=9 mutant skips second custody after replacement create while existing assertions pass. Patch physical post-create secondary wrapper/listener cases before copy/start/verification; latch loss and refuse deletion/persistence. |

B2/B3/V1 share missing secondary-custody failure coverage; grouped under that cause. Other findings remain separate. All surviving work is a direct patch of demonstrated existing paths, no new public surface or unresolved intent. No new defer or spec loopback; prior two guard investigations stay open.

All patch routes closed: B1 regression RED4-for2 and final process/full GREEN; B2/B3/V1 secondary custody at replacement phases plus physical mutations; B4 exact elapsed-deadline refusal with unchanged pre-cleanup budget; B5 nested interrupt; B6 exact private parser/ACK failures; B7 unknown replacement preservation; B8 secondary initialization gap; B9/B10 current/historical wording and exact reproduction commands. All pass in final541-test discovery. No new deferred item.

## Verification

Focused tests → affected process/startup checks → full deployment discovery. Fresh prepare/toolchain/images; actual initialized proof and existing persistence/pinned-CLI/bootstrap/guarded controls; public up refusal. Retain failures/hashes/matrix coverage. No weakened expectations or receipt repair; five impacts recorded.
