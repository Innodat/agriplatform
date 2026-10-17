# Docker host maintenance — upgraded and postchecked

2026-10-17. The user approved upgrading the shared host and interruption of Supabase
and the other PostgreSQL workload. This overrides the earlier host-upgrade exclusion
for this specific operation. [Build record](../../_bmad-output/implementation-artifacts/spec-env-docker-host-upgrade.md).

The user reports completing the host procedure below. Read-only agent postchecks
confirm Engine/CLI29.9.1 and preserved original running-workload identities and health.
Do not repeat installation, stop/start, backup or rollback as part of this closeout.
Operator backup/recovery execution was not independently observed. Historical preparation
and the interactive procedure are retained below. Independent operational review is
complete; six documentation findings corrected, none deferred. The corrected shell
procedure was validated with controlled function stubs, not replayed against the host.

## Prepared evidence

- Ubuntu24.04 amd64, WSL2, distro `Ubuntu-24.04`; Docker managed by systemd.
- Engine/CLI27.0.3, containerd1.7.19, Buildx0.15.1, Compose2.28.1.
- Storage driver `overlay2`, data root `/var/lib/docker`, live restore disabled.
- Ten containers running: nine existing `supabase_*_agriplatform` containers and
  `systems-db-1`. Most Supabase services have healthy health checks; REST and
  systems-db have no Docker health check. The procedure required restoring only the previously running set.
- Selected IDs/image IDs/status/health/restart-policy inventory is protected under
  `platform/deployment/.local/docker-host-upgrade/90cc26c3-4900-4429-98cd-018e006028e7/` (directory0700,
  files0600). No payloads, credentials or full inspect output were saved.
- An initial health-template attempt failed before writing inventory; its empty run
  directory is retained. The successful inventory uses a missing-health-safe selector.
- Exact package simulation below passes: six upgrades, zero new packages, zero
  removals. The other118 available host upgrades are not selected.

| Package | Selected version |
| --- | --- |
| docker-ce, docker-ce-cli, docker-ce-rootless-extras | 5:29.9.1-1~ubuntu.24.04~noble |
| containerd.io | 2.4.2-2~ubuntu.24.04~noble |
| docker-buildx-plugin | 0.38.0-1~ubuntu.24.04~noble |
| docker-compose-plugin | 5.6.0-1~ubuntu.24.04~noble |

Versions are the official stable repository candidates observed during preparation;
Engine29.9.1 is also confirmed by [Docker release notes](https://docs.docker.com/engine/release-notes/29/#2991).
Follow [Docker's Ubuntu package procedure](https://docs.docker.com/engine/install/ubuntu/).
Upgrading an existing installation need not enable the new containerd image store;
retain overlay2 and existing daemon configuration. [Storage guidance](https://docs.docker.com/engine/storage/containerd/).

## Host-terminal procedure (retained execution handoff)

Run in an interactive **Ubuntu-24.04 host terminal**, where sudo can prompt locally.
Do not stop workloads until administrative access and the existing backup/snapshot
recovery arrangement are ready. No backup or recovery qualification was performed
by the agent. A cold backup must include the actual Docker/containerd data mounts and
configuration; do not assume a WSL root export includes externally mounted data.

**Unresolved recovery prerequisite in the agent record:** no operator backup reference,
coverage record, validated checkpoint or matching old-package/configuration recovery
procedure was collected. Before reusing this maintenance procedure, the operator must
record a protected backup/snapshot reference and timestamp, covered Docker/containerd
data mounts and configuration, checkpoint validation results, and a recovery procedure
with available matching old package versions and saved configuration. Validate the
selected checkpoint after shutdown and before installation; stop if coverage or
validation is missing or ambiguous. User-reported execution does not close this gap.

Authenticate and refresh official package metadata before the downtime:

```sh
sudo -v
sudo apt-get update
```

Preview the exact transaction again after refreshing metadata. It must retain the
same six-package scope and remove nothing:

```sh
sudo apt-get -s --no-remove --only-upgrade install \
  docker-ce=5:29.9.1-1~ubuntu.24.04~noble \
  docker-ce-cli=5:29.9.1-1~ubuntu.24.04~noble \
  docker-ce-rootless-extras=5:29.9.1-1~ubuntu.24.04~noble \
  containerd.io=2.4.2-2~ubuntu.24.04~noble \
  docker-buildx-plugin=0.38.0-1~ubuntu.24.04~noble \
  docker-compose-plugin=5.6.0-1~ubuntu.24.04~noble
```

Recheck that the running set still matches the saved inventory before maintenance.
Request a bounded stop of those ten containers (only after recovery is ready):

```bash
(
set -euo pipefail
docker --host unix:///var/run/docker.sock stop --time 60 \
  supabase_studio_agriplatform supabase_pg_meta_agriplatform \
  supabase_storage_agriplatform supabase_rest_agriplatform \
  supabase_realtime_agriplatform supabase_inbucket_agriplatform \
  supabase_auth_agriplatform supabase_kong_agriplatform \
  supabase_db_agriplatform systems-db-1
docker --host unix:///var/run/docker.sock inspect \
  --format '{{.Name}} id={{.Id}} status={{.State.Status}} running={{.State.Running}} restarting={{.State.Restarting}} dead={{.State.Dead}} pid={{.State.Pid}} exit={{.State.ExitCode}} oom={{.State.OOMKilled}} finished={{.State.FinishedAt}}' \
  supabase_studio_agriplatform supabase_pg_meta_agriplatform \
  supabase_storage_agriplatform supabase_rest_agriplatform \
  supabase_realtime_agriplatform supabase_inbucket_agriplatform \
  supabase_auth_agriplatform supabase_kong_agriplatform \
  supabase_db_agriplatform systems-db-1
)
```

Retain only these selected state fields and command exit results in protected evidence;
do not dump logs, environment or full inspect output. Require all ten expected identities,
`status=exited`, `running=false`, `restarting=false`, `dead=false`, `pid=0`, `oom=false`
and a completion timestamp in this maintenance interval. Check exit codes against each
workload owner's documented expected shutdown result. An unexpected exit, OOM, timeout,
forced termination or missing/ambiguous evidence blocks installation for investigation.
A printed stop name, exit0 from `docker stop`, or a container exit code alone does not
prove application-level graceful shutdown; selected state checks cannot prove it either.
Missing shutdown qualification remains unqualified. The agent did not independently
observe or verify historical graceful shutdown in this operator execution.
Complete and validate the selected recovery checkpoint before installing packages.
The actual installation is the same exact transaction without `-s`:

```sh
sudo apt-get --no-remove --only-upgrade install \
  docker-ce=5:29.9.1-1~ubuntu.24.04~noble \
  docker-ce-cli=5:29.9.1-1~ubuntu.24.04~noble \
  docker-ce-rootless-extras=5:29.9.1-1~ubuntu.24.04~noble \
  containerd.io=2.4.2-2~ubuntu.24.04~noble \
  docker-buildx-plugin=0.38.0-1~ubuntu.24.04~noble \
  docker-compose-plugin=5.6.0-1~ubuntu.24.04~noble
```

After successful installation, check the service and restore the recorded running
set, databases first. Starting here means existing container IDs; no image pulls or
Compose recreation are involved:

```bash
(
set -euo pipefail
sudo systemctl start docker
systemctl is-active --quiet docker
docker --host unix:///var/run/docker.sock start supabase_db_agriplatform systems-db-1
for database in supabase_db_agriplatform systems-db-1; do
  deadline=$((SECONDS + 120))
  while true; do
    remaining=$((deadline - SECONDS))
    if ((remaining <= 0)); then
      printf '%s\n' 'Database readiness deadline exceeded' >&2
      exit 1
    fi
    probe_seconds=$remaining
    if ((probe_seconds > 5)); then probe_seconds=5; fi
    if timeout "${probe_seconds}s" docker --host unix:///var/run/docker.sock exec "$database" pg_isready >/dev/null 2>&1; then
      break
    fi
    remaining=$((deadline - SECONDS))
    if ((remaining > 0)); then
      poll_seconds=2
      if ((remaining < poll_seconds)); then poll_seconds=$remaining; fi
      sleep "$poll_seconds"
    fi
  done
done
docker --host unix:///var/run/docker.sock start \
  supabase_pg_meta_agriplatform supabase_auth_agriplatform \
  supabase_rest_agriplatform supabase_realtime_agriplatform \
  supabase_storage_agriplatform supabase_inbucket_agriplatform \
  supabase_kong_agriplatform supabase_studio_agriplatform
)
```

The Bash subshell exits on failed service/start prerequisites; dependent starts occur
only after both databases become ready. Readiness polls every two seconds, with each
probe limited to five seconds and a total120-second deadline per database. This bounded
polling is a corrected retained procedure; it was not observed during operator execution.
If a command fails, stop this sequence and retain safe failure evidence. Do not prune/delete data,
change storage backend or blindly downgrade the major Engine/containerd versions.
Recover using the verified host backup and matching old package/configuration state.
No automatic rollback or data-recovery success is claimed here.

## Post-maintenance acceptance

The root agent performed the following read-only checks after the operator reported
completion; these are acceptance evidence, not instructions to repeat maintenance:

```sh
docker --host unix:///var/run/docker.sock version --format '{{json .Server.Version}} {{json .Server.APIVersion}} {{json .Server.MinAPIVersion}} {{json .Client.Version}}'
docker --host unix:///var/run/docker.sock info --format '{{json .ServerVersion}} {{json .Driver}} {{json .DockerRootDir}}'
docker --host unix:///var/run/docker.sock ps --all --format '{{.Names}} {{.Status}}'
docker buildx version
docker compose version
dpkg-query -W -f='${Package} ${Version}\n' docker-ce docker-ce-cli docker-ce-rootless-extras containerd.io docker-buildx-plugin docker-compose-plugin
docker --host unix:///var/run/docker.sock exec supabase_db_agriplatform pg_isready
docker --host unix:///var/run/docker.sock exec systems-db-1 pg_isready
python3 platform/deployment/dev.py up --target platform/deployment/environments/kdg-local.json --run-id 05e169bc-8a00-4c7c-aca2-1ada8bd97454
```

Acceptance is limited to the reported Engine/API version range, selected original
container IDs/image IDs/status/health/restart policies, storage driver/data-root and
KDG admission result. Full Docker consumer API compatibility and mount/configuration
verification were not performed. Database probes establish connection readiness only;
a running container alone does not establish application readiness. The KDG command
advanced past `docker_28_required` and exited2 with `runtime_adapter_unqualified`,
`runtime_ready=false`. No KDG stack was started by it.
If preparation/source evidence changed, use the existing owner qualification flow
with a fresh UUID; never edit old receipts.

The agent made no port changes; published-port/configuration preservation was not independently verified. This maintenance does not
qualify their network reachability or redesign staging/production isolation.

## Observed post-maintenance results — 2026-10-17

- Engine and CLI29.9.1; Engine API1.56, minimum1.40. `overlay2` and
  `/var/lib/docker` match preparation.
- Installed Engine/CLI/rootless-extras, containerd, Buildx and Compose packages exactly
  match all six selected versions in the table above. Executable Buildx0.38.0 and
  Compose5.6.0 probes agree.
- Protected before/after comparison passes for all ten original container names/IDs,
  image IDs, running status, health and restart policy. Eight existing health checks
  are healthy; REST and systems-db have no Docker health check.
- Both `docker --host unix:///var/run/docker.sock exec supabase_db_agriplatform pg_isready`
  and `docker --host unix:///var/run/docker.sock exec systems-db-1 pg_isready` exit0,
  accepting connections. This is database connection readiness, not a business-data audit.
- The comparison is retained as mode0600 `after-containers.json` in the protected
  inventory directory above. Additional `teacher-supply-db-1` is running although the
  earlier inventory showed it stopped. The agent did not start or stop it and preserved
  this operator/concurrent state; the entire stopped-container set is not unchanged.
- The exact KDG `up` command above exits2 with
  `{"code":"runtime_adapter_unqualified","ok":false,"runtime_ready":false,"stage":"up"}`.
  Docker admission passed. No KDG stack was started; runtime delivery remains unfinished.

Protected `verification.json` in the same inventory directory summarizes package/API,
storage, readiness and gate results and limitations, with SHA256 references to the
before/after container inventories (`running-containers.json` and `after-containers.json`).
Documentation verification confirmed those files exist and their hashes match the
summary; no inventory contents were printed. Its SHA256 is
`eaf48ba388b769ec6b4a0c282e78ef3a39bc51a34e92793891e336fb0278cee5`.

These are actual root-observed postchecks. The operator reports execution of the host
procedure; the agent did not observe the package transaction, shutdown/restart sequence
or backup/recovery execution. No restore test, unchanged business-data assertion or
independent recovery qualification is claimed. The recovery prerequisite remains unresolved
in the agent record. Root made no application-image, schema,
account or port changes. The selected identity comparison does not independently verify
mount/configuration details, full consumer API compatibility or network reachability.

## Impact and delivery status

Existing ENV/package/service owners retained; no new scaffold/generator/runtime
capability. No shared UI or agent-context change; accepted ADRs unchanged. Documents
retain authorization, selected packages, historical dry-run/blocker and actual postchecks.
The host version/workload/KDG admission checks and independent operational review are
complete within the limits above; ENV runtime readiness remains false. Shell syntax,
controlled failure/readiness behavior and protected evidence integrity checks pass.
