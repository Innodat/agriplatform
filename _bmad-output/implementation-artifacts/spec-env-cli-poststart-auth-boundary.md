---
title: 'ENV CLI post-start health and Auth migration boundary'
type: 'feature'
created: '2026-10-18'
status: 'done'
baseline_commit: 'c8e1f65f96c371139aca591c5654fd4b69d78aa7'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/platform/docs/architecture/contracts/scaffold-environment-and-generation.md'
---

<frozen-after-approval reason="standing approval for bounded ENV prerequisites and isolated synthetic verification">

## Intent

**Problem:** Actual CLI qualification ends at PostgreSQL start. Its health observation and first fresh Auth migration-job inputs remain unproven, blocking safe continuation toward the isolated stack.

**Approach:** Add one explicit qualifier that retains the actual pinned CLI after fresh PostgreSQL start, answers its exact health requests from current owned observations, validates its first Auth migration-job profile, then refuses that job before dispatch. Terminate the proven CLI group, verify the same PostgreSQL instance's clean shutdown and dispose only proven owned resources.

## Boundaries & Constraints

**Always:** Existing FreshGuard/DockerSession/run lock, fresh source-qualified UUID, selected executable/images, exact PG profile and public root-key transfer. Preserve TypeScript7.0.2, existing controls/owners and concurrent Leave/PtS files/index. Validate exact request phase/token/operands/routing/prefix before owner action. Health responses contain selected safe fields from the current owned instance, never invented readiness or logs. Preserve its start identity across polls and final shutdown. Allow bounded read-only health polling; consume terminal job boundary once. Recheck executable/fixture/listener/evidence and resource custody through final exit. Existing acquisition5s, total CLI/execution120s, shutdown15s and single cleanup10s budgets remain; no reset/reconnect/replay. The first fresh PG17 setup job must be the approved Auth image, exact gotrue migrate command, named run bridge, Linux extra-host, two project labels, six exact public synthetic environment inputs, no mounts/ports/entrypoint override. Job input/environment stay memory-only. Return precise facts separating real PostgreSQL health, validated refused job, clean shutdown/disposal and runtime_ready=false.

**Never:** Dispatch the Auth job, complete fresh setup/webhooks/current branch, owner migrations/seeds/accounts/grants, cross-execution adoption, public lifecycle activation, whole-stack/Auth readiness, real data, provisioning/deployment/pilot, another generator/runner/service, generic Docker forwarding or SQL relay. Host-facing connection progress inferred from pinned source is not independent session identity/authentication proof.

## I/O & Edge-Case Matrix

| State | Required behavior | Failure handling |
| --- | --- | --- |
| Fresh CLI starts and health progresses | Truthful bounded observations then exact Auth job refusal, clean shutdown/disposal | Selected proof facts only |
| Wrong phase/name/token/prefix, duplicate terminal or malformed private exchange | Refuse before acknowledgement/next mutation | No replay or success |
| Changed image/bridge/volume/fixture/listener/start identity; unhealthy/exited state | Refuse or bounded truthful not-ready polling as appropriate | Never synthesize healthy; preserve ambiguity |
| Changed job argv/env/image/network/labels/routing; extra command | Reject exact profile and stop CLI | No job dispatch or setup claim |
| Lost response, deadline, interruption or supervisor failure | Terminate proven group and attempt cleanup once only with current custody | Preserve unknown resources; no budget extension |

</frozen-after-approval>

## Code Map

- `platform/deployment/startup.py`: fixture/handoff/supervisor/probe owners; distinguish missing inspect from post-start health by phase. Retain event/custody postchecks and legacy controls.
- `platform/deployment/resources.py`: FreshGuard current/owned/start/health/stop/cleanup; extend bounded post-start authority and reuse cleanup.
- `platform/deployment/create_profile.py`: exact refused Auth job validator using target URLs, run bridge/project and qualified Auth observation; no migration adapter.
- Pinned CLI commit753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4: db-bootstrap/{start-database,health-check,db-setup,internal-db-connection}.ts, docker-lifecycle.ts and docker-run.{args,layer}.ts. PG17 with Realtime/Storage disabled and Auth enabled connects host DB before Auth image/job, with setup SQL after that job. buildDockerArgs orders run/--rm/network/add-host/key-only -e/labels/image/command. Driver connection can issue probes; do not claim zero SQL.
- `platform/deployment/tests/test_pinned_execution.py`, `test_resources.py`: independent daemon, exact envelopes and real private-socket/CLI-descendant harness. Root alone executes process/Docker checks serially; child runs no-socket tests.

## Tasks & Acceptance

- [x] Tests above: observe acceptance RED, then focused TDD for matrix rows and unchanged legacy controls.
- [x] Profile/resource/startup owners plus `tests/qualify_startup.py`: add literal pinned-cli-postgres-auth-boundary control and safe closed facts.
- [x] `platform/deployment/fixtures/supabase-pg17-profile.md`, `ENV_CLI_POSTSTART_EVIDENCE.md`, `DEVELOPMENT.md`: pinned authority, command/evidence matrix and scaffold/UI/context/documentation/ADR decisions.
- [x] `apps/kdg-capture/docs/next-session.md`, `.memlog.md`, this record: exact progress, review and remaining ENV/P1/SERVICE gates.

Given qualified disposable inputs, when the new qualifier succeeds, then actual CLI health requests and exact refused Auth job precede verified clean disposal. Given uncertainty or changed input, when qualification refuses, then no job dispatch, setup completion or runtime readiness is claimed.

## Implementation Notes

Acceptance RED4 missing owner entry points; root oversized valid JSON regression observed before bound correction. Root68 focused PASS0.861s;3 affected process PASS43.355s after explained fixture/race corrections. Complete553 deployment tests PASS498.253s, including33 profile refusal mutations and final group/deadline assertions. Root read full unified diff and patch follow-ups. Five matrix rows/five impacts verified.

Fresh608704a3 actual new boundary PASS70.840s; all13 receipts/running inventory unchanged. Existing initialized/persistence/bootstrap/guarded controls pass; first-start initial images_cli/command_refused59.547s retained, exact prerequisite diagnostic passes32.651s and same-control safe diagnostic passes85.989s with phase7/cleaned. Original cause unobserved, not closed by passes. Public up refuses; production/profile remain source-bound and concurrent files/index unchanged. Three-layer review follows.

Review patches: malformed Health RED reproduced as AttributeError before explicit
dictionary guards at both sites. Root73 focused PASS0.812s; new repeated-not-ready
private process test PASS3.726s. Root read all patch deltas; source/profile frozen for
fresh e0098c0e qualification. One pre-existing prerequisite diagnostic investigation
appended to deferred-work; two older intermittent investigations remain open.

Reviewed-source closeout: fresh1a572768 actual boundary PASS68.083s and all six
qualifier controls pass with13 receipts/running inventory unchanged; public up refuses.
Root73 focused PASS0.812s,4 affected process PASS54.186s and559 full deployment
PASS591.285s/no skips. All three review layers and patches complete; five rows/five
impacts verified, current source/profile/receipt/concurrent index hashes checked.
One new pre-existing diagnostic investigation deferred; two older investigations
remain open. Registry-refused e0098c0e prerequisites and incomplete first regression
are retained separately, not explained by final passes. No runtime readiness claim.

## Spec Change Log

## Review Triage Log

All three layers completed before triage. Runtime thread limits required sequential
reviewer admission after simultaneous launches were attempted; each review was
context-free/read-only and saw the same93,735-byte diff. No layer was skipped.

| ID | Verdict | Evidence and route |
| --- | --- | --- |
| B1 | medium | Docker may supply null/non-object Health; both new chained .get calls raise AttributeError after current-instance checks. Patch explicit nested type rejection and both-site regression. |
| B2 | low | enable_persistence does allow an Auth-enabled owner, but the sole production caller selects disjoint literal controls (startup1176–1180); no reachable contradictory mode is demonstrated. Reject additional guard/tests as unlikely everyday defect with extra branching. |
| B3 | false | install_fixture and synthetic_probe call validate_selection_plan before constructing retained fixture; it rejects non-string selections, and fixture byte custody protects subsequent use. A list/dict cannot reach this lookup through the qualified caller. |
| B4 | false | Missing/wrong-repository/malformed selections and missing/malformed observations are rejected by startup.validate_selection_plan/validate_image_observations before fixture install; existing validation tests own this provenance. The new validator does not accept untrusted fixture authority. No duplicated validation matrix needed. |
| B5 | medium | No focused regression currently protects healthy→unhealthy admission reset or health change after last poll before terminal reinspection. Patch no-socket cases with exact refusal/no dispatch. |
| B6 | medium | shutdown_state enforces running/not-dead/not-OOM at both calls, but new-boundary tests do not exercise these states. Patch focused both-site state matrix without changing inherited behavior. |
| B7 | medium | Existing process continuation immediately asserts healthy; no private handoff case proves repeated starting/unhealthy replies within the original deadline. Patch one bounded process scenario with eventual health and unchanged deadline. |
| B8 | medium | Terminal consumed flag precedes profile validation, but duplicate test covers only successful validation. Patch failed-profile then valid-retry regression, proving zero job dispatch. |
| B9 | medium | Existing recv Mock can return more than requested and never tests realistic fragmentation/exact512. Patch size-respecting fragmented fake with512 PASS/513 refusal. |
| B10 | medium | Actual results cite private helper hashes but omit complete invocation/artifact/diagnostic reproduction recipe. Patch evidence with supported direct commands, retained paths and safe observational recipe; no new runner. |
| E1 | medium | Same null/non-object Health defect as B1, independently traced at health and terminal revalidation. Group with B1; patch once with both-site regression. |
| V1 | medium | Pre-verified gap: removing executed-start identity capture lets first poll adopt a replacement; current tests mutate only after health. Patch no-socket before-first-poll regression. |
| M1 | medium | Pre-existing images.bounded_command discards nested toolchain safe stdout on nonzero exit; the retained original first-start refusal cannot identify its failed probe/stage. Defer investigation with failure hash and safe-metadata follow-up; targeted passes do not explain cause. |

Patch groups: malformed health B1/E1; distinct boundary regression gaps B5/B6/B7/B8/B9/V1;
evidence reproduction B10. B2 rejected; B3/B4 refuted by upstream retained-owner validation.
M1 is pre-existing, outside this change's owners, and remains open without relaxing limits.

## Verification

Focused test_pinned_execution discovery, affected test_resources process cases, then complete deployment discovery. Fresh prepare/toolchain/images; actual new control and existing initialized/persistence/first-start/bootstrap/guarded controls; public up expected refusal. Retain failed attempts/results/hashes and source bindings; verify concurrent document/index preservation and all five impact decisions before scoped local commit.
