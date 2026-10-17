---
title: 'ENV Docker host upgrade'
type: 'chore'
created: '2026-10-17'
status: 'done'
route: 'dispatch'
baseline_commit: 'f41b5dfbc599d32aab9b02a7b360cd910383af99'
review_loop_iteration: 0
context:
  - 'platform/deployment/DEVELOPMENT.md'
  - 'platform/deployment/DOCKER_HOST_UPGRADE.md'
---

<frozen-after-approval reason="user approved host upgrade and interruption of existing Supabase/PostgreSQL workloads">

## Intent

**Problem:** Shared Docker Engine27.0.3 fails ENV's existing minimum28 localhost
isolation gate. The user has authorized upgrading this host and its maintenance
interruption; the earlier infrastructure exclusion no longer excludes this operation.

**Approach:** Upgrade the existing Ubuntu24.04 amd64 Docker packages to the selected
official stable Engine29.9.1 and matched tooling. Preserve existing workloads/data,
restore the previously running set and verify health plus the existing KDG gate.

## Boundaries & Constraints

**Always:** Use the host package manager/service owner. Verify recovery arrangements
before mutation; retain selected workload IDs/image IDs/health and package identities.
Preserve overlay2, Docker data root, volumes, existing container images/configuration,
port bindings and stopped-workload state. Restore only the previously running set.
Keep credentials/data out of reports. Preserve concurrent Leave work. Record actual
outcomes and failures; an available package or passing simulation is not an upgrade.

**Never:** Use Docker containers to bypass sudo; alter sudo policy; ask for passwords
in chat; reset/prune/delete Docker data; change application images, schemas/accounts,
port exposure or storage backend; deploy KDG/Leave; weaken the Docker gate; claim the
unfinished runtime adapter is delivered. No blind package downgrade after state changes.

## I/O & Edge-Case Matrix

| Scenario | State | Expected behavior | Failure |
| --- | --- | --- | --- |
| Preparation | Engine27.0.3, ten running containers | Record selected identities and simulate exact packages | No daemon mutation |
| Administrative access unavailable | sudo requires password | Leave workloads running; provide interactive-host procedure | Upgrade remains pending |
| Upgrade | Administrative terminal and recovery ready | Install exact selected packages with no removals; restore running set | Preserve evidence; recover through host procedure |
| Verification | New daemon active | Same workload identities/data roots and required health; KDG version gate passes | Report failed stage, no readiness claim |

</frozen-after-approval>

## Code Map

- `platform/deployment/DOCKER_HOST_UPGRADE.md`: concrete host operation and verification
  procedure; existing Docker package/service owners perform maintenance.
- `platform/deployment/DEVELOPMENT.md`, `apps/kdg-capture/docs/next-session.md`: current
  approved-maintenance status, distinct from unfinished ENV runtime support.
- `platform/deployment/dev.py`: existing unchanged Docker admission/adapter gates.
- `.local/docker-host-upgrade/90cc26c3-4900-4429-98cd-018e006028e7/`: protected selected
  pre-maintenance inventory; no environment variables or application payloads.

## Tasks & Acceptance

- [x] Inspect service/packages/running workloads and save selected protected inventory.
- [x] Simulate exact official six-package transaction; no removals or new packages.
- [x] Prepare host procedure and record administrative blocker/current impacts.
- [x] Record operator-performed package maintenance and the limits of recovery evidence.
- [x] Verify actual Engine/API/tool versions, old workload identities/health and KDG gate.
- [x] Record post-maintenance evidence, independent operational review and completion.

Given approved downtime and administrative execution, when the host is upgraded,
then Engine29.9.1 is active with preserved storage/workload identity and verified
previously-running services. Given the unchanged prepared KDG run, when read-only
`up` is retried, then the Docker version gate passes and the unfinished adapter still
refuses; runtime readiness remains false.

## Implementation Notes

2026-10-17: user approval covers this specific host maintenance and downtime. Current
branch/dirty Leave documents are explicitly preserved under standing authorization.
No extra owner acknowledgement or scope approval needed. Host is Ubuntu-24.04 on
WSL2; systemd Docker active. Both `sudo -n true` and `sudo -n -l` return exit1,
`sudo: a password is required`. No service/container stopped, package installed or
backup made. This is an execution credential boundary, not a missing user approval.

## Verification

Existing prerequisite RED: live daemon27.0.3, Docker admission requires28+. Package
simulation exits0: six upgrades, zero new, zero removals. No production code changed,
so new unit/TDD tests would mirror package management; use host acceptance checks.
Scaffold: existing owner/tooling only. UI/context/ADRs: no changes needed.
Documentation: maintenance runbook and current ENV/KDG status updated in this item.
Actual post-upgrade version/workload/KDG admission checks pass as recorded below.
Operator backup/recovery execution was not independently observed; recovery qualification
and unchanged-business-data claims remain unsupported. Independent operational review
and final closeout remain with root.

## Operator execution and verification handoff

The user reports running the host procedure. Do not repeat any installation, stop,
start, backup, rollback or other host mutation. Only documentation remains for the
implementation delegate; root already completed the read-only host acceptance below.
Update this spec's verification/task results, `platform/deployment/DOCKER_HOST_UPGRADE.md`,
the current status in `platform/deployment/DEVELOPMENT.md`, and the current maintenance
paragraph in `apps/kdg-capture/docs/next-session.md`. Preserve historical evidence and
the frozen intent. Root owns final memory append, review, scoped commit and unrelated
Leave-file preservation. No new production code or tests are needed.

Root-observed postchecks (all actual, no simulation): Engine/CLI29.9.1; Engine API1.56,
minimum1.40; overlay2 and /var/lib/docker unchanged. Six installed package versions
exactly match the runbook pins: Docker Engine/CLI/rootless-extras
5:29.9.1-1~ubuntu.24.04~noble, containerd2.4.2-2~ubuntu.24.04~noble,
Buildx0.38.0-1~ubuntu.24.04~noble, Compose5.6.0-1~ubuntu.24.04~noble.
Buildx and Compose executable probes agree. Protected before/after comparison of all
ten original container names/IDs/image IDs/status/health/restart policy passes; eight
existing health checks healthy, REST and systems-db have no Docker health check.
Both `docker --host unix:///var/run/docker.sock exec supabase_db_agriplatform pg_isready`
and the same command for systems-db-1 exit0, accepting connections. Container comparison
is saved mode0600 in the existing protected inventory directory as after-containers.json.
An additional teacher-supply-db-1 is running, whereas the earlier inventory showed it
stopped; root did not start or stop it and preserves this operator/concurrent state.
Do not claim the entire stopped-container set stayed unchanged.

Exact read-only `python3 platform/deployment/dev.py up --target
platform/deployment/environments/kdg-local.json --run-id
05e169bc-8a00-4c7c-aca2-1ada8bd97454` exits2 with
`{"code":"runtime_adapter_unqualified","ok":false,"runtime_ready":false,"stage":"up"}`.
Docker admission has passed; KDG runtime remains unfinished. No app-image/schema/
account/port change was performed by root. Operator backup/recovery execution was
not independently observed: explicitly retain that limitation, no restore-test or
unchanged-business-data claim. The original recovery requirement was presented in
the operator procedure; the user reports execution, not independently audited backup.

## Documentation implementation outcome — 2026-10-17

Updated this task result, the host runbook, current ENV status and KDG maintenance
handoff from root's actual postchecks above. Historical preparation, failed sudo checks,
prior Docker27 refusals and frozen intent remain retained. No host operation, production
code or test change was performed by this documentation delegate. The original ten
workloads pass the selected identity/health comparison; additional teacher-supply-db-1
running state and unobserved backup/recovery execution remain explicit limitations.
Documentation consistency and whitespace checks are recorded at handoff. Independent
operational review, final memory append and scoped commit remain root-owned; the final
completion task remains unchecked until those steps are complete.

Root retained `verification.json` alongside the protected container inventories, SHA256
`eaf48ba388b769ec6b4a0c282e78ef3a39bc51a34e92793891e336fb0278cee5`.
It summarizes package/API/storage/readiness/gate observations and limitations and binds
before/after container-inventory hashes. No further host probes were performed by this
documentation delegate.

## Review Triage Log

All three layers returned before triage. Verification-gap review found no gaps.
Each finding below was classified independently before routing; none is deferred.

| Finding | Verdict and evidence | Route |
| --- | --- | --- |
| Blind1 restart fallthrough | medium: retained shell block contains sequential sudo/start/readiness commands without failure handling; normal shell execution proceeds after a failed prerequisite. | patch fail-fast sequence |
| Blind2 immediate readiness | medium: the retained procedure runs pg_isready once immediately after start, so normal database startup can produce an unnecessary failure. | patch bounded readiness polling |
| Blind3 graceful shutdown evidence | medium: docker stop output does not establish graceful termination and the text lacks a concrete stop-state/evidence check before continuing. | patch selected state check and explicit qualification limit |
| Blind4 recovery prerequisite | medium: no operator backup/checkpoint reference was collected; recovery instructions must not imply a verified recoverable checkpoint already exists. Existing final limitations are accurate but prerequisite status needs to be explicit at the procedure. | patch label unresolved recovery prerequisite and required operator evidence |
| Blind5 API/mount acceptance | medium: actual comparison covers selected IDs/health/policy and API version range, not every Docker API consumer or mount/configuration detail. Current limitations are recorded but acceptance wording is broader. | patch narrow acceptance to observed checks and explicitly unverified items |
| Edge1 inventory path | low: .local inventory path lacks an explicit base; actual evidence is under platform/deployment/.local, so repository-root readers cannot locate it from the short path. | patch unambiguous repository-relative path and check files/hash |

No runtime code changed; all fixes are direct documentation corrections. Historical
operator execution remains recorded and no maintenance commands will be repeated.

All six patches are complete and root read the corrected runbook. A controlled stub
probe of the original restart block reproduced fallthrough after failed sudo (RED).
The corrected block passes failed-service isolation, bounded database refusal and
transient-readiness recovery probes (GREEN); real Docker/sudo/systemctl/sleep/timeout
commands were replaced by local shell functions. All six shell blocks pass bash -n.
Protected file paths/modes, verification.json SHA256 and referenced inventory hashes
pass. Local Markdown targets and scoped whitespace pass. No runtime regression suite
was repeated for this documentation-only closeout. None of six review findings deferred.
Host package/workload/KDG admission acceptance is complete within recorded limits;
operator recovery evidence and full consumer/mount/configuration checks remain unqualified.
