---
title: 'ENV bounded Auth migration-job execution'
type: 'feature'
created: '2026-10-18'
status: 'done'
baseline_commit: 'ee6b06e56b541e25fa798b1884a3fca92906c59c'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/platform/docs/architecture/contracts/scaffold-environment-and-generation.md'
---

<frozen-after-approval reason="standing approval for bounded ENV prerequisites and synthetic local/CI execution">

## Intent

**Problem:** ENV validates the first actual CLI Auth job request but never executes it. This leaves a required isolated-stack prerequisite unqualified.

**Approach:** Add one explicit startup qualifier. Admit the exact request, terminate the proven CLI group without acknowledging success, then execute its immutable GoTrue migration job through the retained ENV owner. Verify job exit/disposal and the same PostgreSQL instance's normal shutdown/disposal.

## Boundaries & Constraints

**Always:** Retained FreshGuard/DockerSession/run lock, fresh source-qualified UUID and approved baseline including TypeScript7.0.2. Retain original six public synthetic inputs, gotrue migrate, bridge, project labels and image-owner child/config identity. Validate original CLI profile before deliberately tighter detached API execution: Linux/amd64, unique run-derived job name, no mounts/ports, no privileged/host modes, logging none, restart no, memory/swap2GiB, CPU2, PIDs256. Validate inherited image execution configuration before create and effective job configuration afterward. Set AutoRemove=false so exit remains inspectable, then explicitly remove the proven owned job. Consume terminal/create/start/delete attempts before uncertain mutation. No adoption/reconnect/replay. Repeat source/fixture/listener/resource/PG-health/start-identity custody immediately before dispatch and through completion/cleanup. Only the recorded job may join the PG bridge; the job cannot reference the PG volume. Acquisition5s, total execution120s, shutdown15s and single cleanup10s remain; no reset for job work. Keep fixture5s unchanged. Cleanup handles proven job before PG/storage/network; unknown creation/ownership preserves uncertainty. Report separate dispatched/exit/disposal/PG-shutdown/cleanup facts, fresh_setup_completed=false and runtime_ready=false.

**Never:** Job success acknowledgement or later CLI setup SQL, full Auth/schema/session-identity/runtime readiness, long-running Auth, repository owner migrations/seeds/accounts/grants, cross-execution adoption, public up activation, production/real data/provisioning/deployment, dependent Identity/Access/WRITE/KDG, Leave/editor, another runner/generator/service or generic Docker/SQL forwarding. Migration effects exist only in this operation's fresh synthetic database.

## I/O & Edge-Case Matrix

| State | Required behavior | Failure handling |
| --- | --- | --- |
| Exact actual CLI request/current PG | Terminate CLI, recheck, create/start once, verify integer-zero job exit and disposal, clean PG shutdown/disposal | Safe selected facts only |
| Changed argv/env/image/config/network/custody/PG instance | Refuse before next mutation | No success/adoption |
| Fast exit, nonzero/OOM/dead/malformed state/restart | Fast valid exit may pass; others refuse | No inferred schema readiness |
| Lost/malformed create/start/inspect/delete response, timeout/interruption | No replay; bounded cleanup only with current ownership | Preserve unresolved resources |
| Extra bridge member, job volume/port, duplicate terminal | Refuse | No relaxed PG volume-use rule |

</frozen-after-approval>

## Code Map

All code paths below are under `platform/deployment/`.
- `create_profile.py`: reuse validate_auth_job; construct closed immutable job request.
- `dev.py`: exact persistent job-create route only; reuse start/inspect/delete.
- `resources.py`: FreshGuard admission/job custody/joint members/ordered cleanup; reuse PG shutdown.
- `startup.py`, `tests/qualify_startup.py`: literal pinned-cli-postgres-auth-migration control; kill/reap before dispatch; preserve refusal control.
- `tests/test_pinned_execution.py`, `test_docker_session.py`, `test_resources.py`: independent request/state/transport and CLI-descendant fixtures. Child owns code and no-socket tests only; root owns documentation/memlog/spec and serial actual process/socket/Docker verification.
- CLI commit753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4 db-setup/docker-run: separate job DB connection, later SQL awaits success. Authv2.197.0 Dockerfile: gotrue→auth symlink, supabase user/migrations path. Cached config confirms defaults; MobyAPI1.48 defines lifecycle/state.

- Approved local mail adjustment: `environments/kdg-local.json`, `schema/development-target-v1.json`, `tests/test_run_config.py` and platform scaffold-environment contract change mail55484→15484 together; root owns this four-line configuration correction. Auth six inputs, other ports, production and port-refusal rules stay unchanged.

## Tasks & Acceptance

- [x] Owning tests above: acceptance RED, focused TDD for all matrix rows; protect legacy controls.
- [x] Existing profile/transport/resource/startup owners: bounded actual job and closed facts.
- [x] `fixtures/supabase-pg17-profile.md`, `ENV_AUTH_JOB_EVIDENCE.md`, `DEVELOPMENT.md`: source authority, exact commands/results and requirement-test matrix; scaffold/UI/context/docs/ADR decisions.
- [x] `apps/kdg-capture/docs/next-session.md`, `.memlog.md` and this record: verified state/remaining gates and review.

Given fresh qualified synthetic inputs, when qualification succeeds, then actual request/CLI termination precede one verified job and safe disposal. Given uncertainty, when refused, then preserve ambiguity without setup/runtime completion.

## Implementation Notes

Acceptance RED precedes implementation and review fixes. Final reviewed-source run
`c12d7e47-27f5-457d-8459-57b5d23eca57` passes the actual Auth migration job65.447s
and all six legacy controls on the approved mail15484 configuration. CLI termination,
job exit/disposal, same-PG normal shutdown/cleanup and13 unchanged receipts/running
inventory are verified; setup/runtime remain false. Root104 focused,3 process and8
config tests pass; full593 deployment tests PASS519.852s, no skips. All25 source
bindings and current receipts match. Three independent review layers complete;
ten patch groups verified, three investigations deferred, one concurrent Leave
finding rejected/preserved. Prior three investigations and the unstarted bootstrap
diagnostic container remain. Exact commands, hashes, failures, five requirement rows
and scaffold/UI/context/documentation/ADR impacts are in ENV_AUTH_JOB_EVIDENCE.md.

## Spec Change Log

2026-10-18 — User explicitly approves the concrete four-line local mail15484 proposal after source-bound verification is blocked by an established Codex socket on fixed55484, inside host ephemeral32768–60999. Add coordinated target/schema/contract/generated-config assertion update; no original six Auth inputs, public surface, production, other port or refusal semantics change. Keep all working-tree/evidence state and the active connection. Observe approved assertion RED before configuration GREEN, then fresh qualification and full checks. Frozen intent remains unchanged.

## Review Triage Log

| ID | Verdict | Evidence and route |
| --- | --- | --- |
| B1 | medium | Root independent daemon injections Tty/OpenStdin/AttachStdout=true still qualify; effective noninteractive profile is unchecked. Patch typed false/default checks and mutations for all six IO flags. |
| B2 | medium | Root injected CgroupnsMode=host still qualifies; no explicit private request/default validation forbids daemon host default. Patch exact private mode in existing request/transport; group with E1. |
| B3 | medium | Root Path=sh or unrelated Args still qualifies despite gotrue migrate Config. Moby newContainer derives Path/Args separately; contradictory execution metadata must refuse. Patch exact path/vector plus fixture/mutations. |
| B4 | medium | Root Paused/Restarting=true exited rows qualify, contradicting admitted state. Patch typed-false lifecycle flags and malformed-state cases. |
| B5 | medium | Root timeout during pre-delete ownership check leaves zero DELETEs but delete_attempted=true; the allowed cleanup budget then refuses. Patch consume immediately before DELETE after ownership/current checks. |
| B6 | maybe-false | Production SIGKILLs owned group and reaps leader; executed two-PID oracle verifies normal stopped descendants before dispatch, mutation catches omitted termination. No controlled non-zombie same-group descendant surviving actual SIGKILL plus leader reap is demonstrated. Defer medium-unverified: capture start identities/group/state under bounded adverse scheduling; zombie presence alone cannot settle live execution. |
| B7 | medium | Current positive daemon exits inside start; running timeout covers failure, not stable repeated running-to-success observations. Patch independent successful polling sequence/budget/disposal assertions. |
| B8 | medium | Existing start failure returns500 before fake state transitions; it cannot protect lost ACK after actual start/closed transport. Patch started-job/lost-response test, no replay and unresolved-resource assertions. |
| B9 | medium | Root changes valid FinishedAt after verified exit and disposal still qualifies. Patch bound completion timestamp across subsequent job observations plus drift test. |
| B10 | medium | Current concurrent Leave copyable prompt still has historical E5-unapproved wording despite new approved checkpoint (also says follow latest). Reject out of scope: this intent excludes Leave work and user requires concurrent documents preserved; no edits to that handoff. |
| E1 | medium | Same verified host-cgroup acceptance as B2, including daemon-default path. Group with B2 and patch one root cause. |
| V1 | medium | Pre-verified regression gap: no valid StartedAt-to-different-valid-StartedAt sequence protects existing continuity comparison. Patch test only; current production check remains. |
| V2 | medium | Pre-verified regression gap: no existing-name/non404 preflight test protects existing refusal. Patch200/unexpected-status cases without create/start/adoption/delete. |
| S1 | medium | Root existing bootstrap create client times out and leaves exact never-started network-none/no-mount container; fresh unchanged-source bootstrap passes separately. Defer pre-existing timeout/operational investigation with selected identities; preserve failed resource/receipt, no recovery claim. |
| S2 | maybe-false | Post-review full593 exposes unchanged drip case: docker_timeout after28 metadata events versus expected29 under2s; direct unchanged repeat passes10.003s. Auth execution is disabled on this metadata path; cause/current-change attribution remains unobserved. Defer medium-unverified timing investigation with per-request/phase/PID evidence; do not relax assertions or infer resolution from a pass. |

Ten patch groups (B2/E1 share one root cause); three deferred investigations; one protected concurrent finding rejected. Every reviewer finding is graded individually before grouping. Frozen intent remains unchanged.

## Verification

Smallest RED, focused owner/transport tests, affected process tests, full deployment discovery. Fresh prepare/toolchain/images; new actual plus existing post-start/initialized/persistence/first-start/bootstrap/guarded controls; public up refusal. Retain commands/results/hashes/failures; verify bindings, concurrent Leave/PtS/Expense files/index, all matrix rows and five impacts before scoped local commit. Existing investigations stay open.
