---
title: 'ENV guarded pinned-CLI PostgreSQL execution'
type: 'feature'
created: '2026-10-17'
status: 'done'
route: 'dispatch'
baseline_commit: '040f7f01b4f5c4f4c3ef4fd3fb4fbe4427959ff4'
review_loop_iteration: 0
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/platform/docs/architecture/contracts/scaffold-environment-and-generation.md'
---

<frozen-after-approval reason="standing user approval for bounded ENV implementation and isolated synthetic verification">

## Intent

**Problem:** The pinned CLI currently receives synthetic container creation/copy acknowledgements and a refused start. Separate image bootstrap/shutdown proof does not establish CLI-to-daemon execution continuity on its actual named volume.

**Approach:** Extend existing retained ENV owners and startup qualifier through the CLI's first real PostgreSQL create/copy/start, then observe running/healthy state and bounded clean shutdown/removal of only proven disposable resources. Keep full environment admission gated.

## Boundaries & Constraints

**Always:** Exact approved baseline including TypeScript 7.0.2; fresh explicit prepared synthetic target/UUID and source-bound tool/image receipts. Original CLI operands, four public container inputs and key archive validate before owner dispatch. Use existing pinned CLI, private wrapper/handoff, DockerSession, create-profile, image/network/volume and lifecycle owners. Preserve executable/fixture/listener/source/run-lock custody. Return actual recorded container ID; copy/start only that instance. Refuse duplicates/reordering and consume phases before uncertain mutations; no reconnect/replay. Before create require no volume references; afterward require exactly the verified recorded container, rejecting every extra reference. Retain five-second acquisition budget; one explicit execution transition grants at most120 seconds including health observation, then shutdown15 seconds, cleanup10 seconds, never per-request resets. Bound commands, requests, output and CLI descendants. Validate same-instance clean shutdown with existing strict state semantics. Actual disposable profile uses approved image/bootstrap/key, existing run bridge/named volume, loopback-only reserved port, no host paths,2GiB memory/two CPUs/256 PIDs/logging none/restart disabled; document deliberate tightening of the CLI profile. Stop the CLI at its first executed start; no subsequent service dispatch. Cleanup only resources proven created in this execution, current ownership and no foreign use; ambiguous creation/ownership preserves evidence/resources and fails closed. Safe selected outputs only. Preserve concurrent Leave/PtS work and index.

**Never:** Enable full up, owner SQL/migrations/seeds/accounts/grants, production targets, infrastructure/deployment/pilot, arbitrary daemon endpoints/routes, another generator/runner/service, initialized-volume adoption or reset policy. No claim of SQL semantics, durable reuse/recovery, Auth or full stack readiness from running/healthy state. Default controls remain synthetic. Keep prior bootstrap/shutdown controls supported.

## I/O & Edge-Case Matrix

| Scenario | Input/state | Expected behavior | Failure handling |
| --- | --- | --- | --- |
| Fresh execution | Actual pinned CLI emits validated create/copy/start | Same owner dispatches exact selected container and archive, observes health, clean shutdown and removal; runtime_ready=false | Selected proof facts only |
| Existing/racing resources | Existing container/volume or extra volume reference | Refuse adoption/next mutation | Preserve unowned/ambiguous resources |
| Wrong identity/custody | Changed image, container, network, volume, source, executable or fixture | Refuse before next action, latch ownership loss | No later deletion on restored observations |
| Lost/malformed mutation response | Create/copy/start cannot be confirmed | No retry or synthetic acknowledgement | Owned cleanup only, unresolved state refuses |
| Invalid/reordered request | Wrong ID/archive/operands/env or duplicate phase | Reject before mutation | Safe failure, no continuation |
| Deadline/interruption/unclean exit | Stalled CLI/health/stop/cleanup, OOM/nonzero exit | No success or recovery claim | Independent bounded cleanup; retain forced/unresolved evidence |

</frozen-after-approval>

## Code Map

- `platform/deployment/resources.py`: FreshGuard/fresh_session retain one owner session/run lock; add closed execution phases and phase-specific reference checks, preserve standalone volume admission.
- `platform/deployment/startup.py`: fixture_command, owner_handoff, validate_owner_request, guarded_fixture_command and install_fixture already own the actual pinned CLI process boundary; extend explicit execution control without changing default synthetic proof.
- `platform/deployment/create_profile.py`: exact original argv/environment and detached execution request validation; add explicit bounded disposable profile, preserve legacy default.
- `platform/deployment/dev.py`: DockerSession closed HTTP framing; extend only fixed owner container lifecycle/archive/cleanup routes and empty success responses, never arbitrary transport.
- `platform/deployment/startup_lifecycle.py`: reuse archive and strict shutdown state validation. Existing run_bootstrap is tmpfs/network-none and must not be misrepresented as named-volume proof.
- `platform/deployment/tests/qualify_startup.py`: existing explicit-control qualifier owns real opt-in execution entry; synthetic fixture authorities remain independent.

## Tasks & Acceptance

**Execution:**
- [x] Existing deployment test owners -- observe ordered real-dispatch acceptance RED before implementation; focused TDD for matrix, transport/framing and legacy characterization.
- [x] Existing source owners above -- implement closed execution and resource ownership through pinned CLI first start and bounded health/shutdown/cleanup; update source-bound profile authority.
- [x] `platform/deployment/ENV_PINNED_CLI_EXECUTION_EVIDENCE.md`, `DEVELOPMENT.md` -- record exact tests/commands/attempts/retained proof, five impact decisions and limits.
- [x] `apps/kdg-capture/docs/next-session.md`, `.memlog.md`, this spec -- append truthful result/remaining ENV/P1/SERVICE gates and review disposition.

**Acceptance Criteria:**
- Given a fresh qualified synthetic run, when the actual pinned CLI emits its first lifecycle, then exact create/archive/start reach the retained owner, current real observations prove that same container healthy and cleanly stopped/removed, and runtime readiness remains false.
- Given invalid, uncertain, reordered or stale inputs, when execution proceeds, then affected mutation refuses without replay or deletion of unowned resources.
- Given final source changes, when verification completes, then fresh owner qualification, focused/affected regression and actual disposable proof pass; retained evidence and concurrent work are preserved, with unrelated host changes reported accurately.

## Implementation Notes

Root alone runs actual Docker and socket/process verification serially and owns final evidence/handoff/memlog/scoped commit. Implementation agent writes tests/source-bound authorities, observes behavioral RED before production changes, and runs only no-socket focused tests; report necessary socket/process commands for root. Do not commit or alter concurrent documents. Preserve existing guard assertions/deadlines; two intermittent pre-existing regression investigations remain deferred, not resolved by passing reruns.

Implementation observed ordered-dispatch RED before production changes, then
GREEN. Additional explained RED/GREEN cases cover public/internal allowlist reachability,
pending created-state network attachment, phase-specific copy/start envelopes and
consume-once cleanup. Final focused27 PASS0.205s, integrated supervisor3 PASS12.187s, unchanged legacy
rejection1 PASS0.001s; affected151 PASS. The matrix audit
maps every row to executed cases in the evidence document. Root inspected source,
test, profile and runbook changes directly; frozen intent remains unchanged.

Final reviewed-source run2a794d89-260c-4b4c-a8dc-34c7650fc2dc passes prepare/toolchain/images,
actual pinned-CLI create/copy/start/health/clean shutdown/removal (63.366s), existing
actual bootstrap (31.555s) and guarded-fresh (68.506s). Each proof preserves13 retained
files and running inventory. Public up remains runtime_adapter_unqualified, exit2.
Earlier unknown_control, invalid_owner_handoff and registry qualification refusals
are retained and explained in the evidence. Final reviewed-source499-test regression passes342.433s; preceding494-test regression
passed294.641s; earlier493-test run exposed one-shot
transport regression, fixed with unchanged expectation and new RED/GREEN coverage.
Independent review and patch results are recorded below; no receipt repair or uncertain-run replay occurred.

## Spec Change Log

## Review Triage Log

| Finding | Verdict | Evidence and route |
| --- | --- | --- |
| Blind1 changed StartedAt then forced cleanup | false | `finish_execution` refuses same-instance success; existing `test_unclean_state_and_restarted_instance_never_claim_clean_removal` explicitly requires failure cleanup of the same proven ID/config/volume after changed start state. Current ownership is the recorded container, not a successful clean-stop claim. No replacement-ID adoption/deletion occurs. Reject. |
| Blind2 populated-network created state needs pending-state checks | false | The extra zero-state checks authorize the otherwise unallocated empty NetworkID exception. With a populated ID, trusted Docker created/nonrunning state is checked by `created`; an actually started container is rejected by the out-of-band-start regression. No Docker transition producing the proposed contradictory created/nonzero-PID state was demonstrated. Reject. |
| Blind3 unchecked immutable config fields | false | User/WorkingDir/AutoRemove/ReadonlyRootfs cannot be altered through this closed route family or Docker container update after exact owner create; image defaults are bound by immutable config ID. The cited changed-input state requires rewriting trusted daemon state, rather than a caller accepted here. Existing mutable resource controls and identity are rechecked. Reject. |
| Blind4 missing endpoint aliases | low | Alias configuration can change through network disconnect/reconnect while retaining container/network identity; owned checks currently miss it. Direct comparison of the two requested aliases and focused mutation coverage is a patch with no new public surface. |
| Blind5 cleanup error replaces primary error | low | A cleanup refusal in finally can replace the selected top-level primary code; Python retains exception context, and neither path claims success. Combined structured failure diagnostics would add a new failure contract for an uncommon secondary failure. Reject low diagnostic enhancement requiring additional branching/surface. |
| Blind6 missing failure cleanup force/result fields | low | Failure output has no force/result metadata, but reports failure and never emits the successful clean-shutdown fields. Additional operational metadata is an uncommon diagnostic enhancement requiring a new public failure contract; reject at this bounded proof rather than expand it. Automatic cleanup effects receive regression coverage below. |
| Blind7 missing recovery IDs | false | Prepared inventory durably records UUID-derived project, exact DB container/volume name and bridge name; runbook directs inspection by those identities, not adoption or unverified deletion. Initialized-resource recovery is expressly excluded by user intent. A second mutable inventory is not needed to execute this proof. Reject. |
| Blind8 pre-container failures retain acquired resources | false | Existing fresh acquisition deliberately retains run resources; new cleanup is conditional on confirmed container ID and current ownership. Unknown creation/existing-container refusals do not grant disposal/adoption authority. Preservation is permitted by the approved failure boundary, with deterministic inventory names retained. Reject. |
| Blind9 missing integrated supervisor execution coverage | medium | Owner and envelope tests are separate; successful actual proof does not cover automatic failure cleanup at the process boundary. Patch tests through real private socket/process supervisor and retained owner effects. |
| Blind10 missing archive/start lost-response fallback coverage | medium | Current in-memory dispatch tests and generic closed-session transport tests do not cover these failure combinations through the automatic supervisor fallback. Patch integrated failure cases: no replay/success and closed-peer preservation. |
| Verification1 supervisor failure cleanup unverified | medium | Pre-verified gap: deleting the finally cleanup call would leave current direct-owner tests and successful real proof passing. Patch an execution-mode supervisor failure regression with descendant termination and automatic bounded cleanup assertions. |

Surviving groups: endpoint alias descriptor comparison (Blind4), and integrated
supervisor failure verification (Blind9, Blind10, Verification1). Both route to patch:
small direct corrections/tests, no new public surface or unobserved state.
Patches completed: alias RED/GREEN and root27 focused PASS; corrected integrated
supervisor3 PASS12.187s, including non-vacuous cleanup-removal mutation detection. Edge-case
layer returned no findings. No new deferred item is introduced by this triage.

## Verification

- Focused new execution acceptance, affected transport/resource/profile/lifecycle suites, then full deployment unittest discovery; retain exact command/count/exit evidence and earlier failures.
- Fresh existing prepare/toolchain/images qualification and explicit real startup-qualifier control; missing exact selected layers fails before mutation (root may download only qualified missing digests).
- Existing actual bootstrap control and pinned-CLI guarded-fresh regression; actual public up still returns runtime_adapter_unqualified/runtime_ready=false.
- Record scaffold/shared-UI/context/documentation/ADR impacts. Existing scaffolding owner is extended, no UI/context/accepted-ADR change anticipated; document final decisions rather than treating this expectation as proof.

Root verification: final full499 PASS342.433s; every matrix row maps to executed passing tests in the evidence. Five impact decisions, handoff and memlog recorded.

Final review patch verification: source-bound actual controls and all499 deployment tests pass. No new deferred item; two pre-existing guard reliability investigations stay open.
