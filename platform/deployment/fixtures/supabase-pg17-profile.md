# Pinned first-create profile authority

Supabase CLI 2.120.0, source commit
[`753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4`](https://github.com/supabase/cli/tree/753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4).
All paths below are relative to that commit. This profile is Linux, PostgreSQL17,
empty db.settings, no restore, no OrioleDB, and no Bitbucket filtering.

- `apps/cli/src/command-internal/db-bootstrap/postgres.service.ts`:
  `buildPostgresStartContainerSpec`, `postgresEntrypointScriptPg15`, and
  `postgresSettingsToPostgresConfig` define env order, volume/port, healthcheck
  (10s/2s/3), restart, aliases, and the shell operand.
- `apps/cli/src/command-internal/db-bootstrap/docker-create-args.ts`:
  `buildStartContainerCreateArgs` fixes the exact option order and key-only env.
- `apps/cli/src/command-internal/db-bootstrap/container-lifecycle.ts`:
  `createContainer` appends project, compose-project, workdir labels in that order,
  merges Linux extra hosts, and passes the four env values to the child process.
- `apps/cli/src/command-internal/db-bootstrap/local-container-inputs.ts` supplies
  `host.docker.internal:host-gateway` for Linux.
- `packages/stack/src/Defaults.ts` supplies the public local JWT default.
  The postgres service fixes password `postgres` and host `/var/run/postgresql`;
  config auth.jwt_expiry defaults to 3600 and the generated ENV config does not
  override it. These public synthetic defaults are not user credentials.

[supabase-pg17-bootstrap.txt](supabase-pg17-bootstrap.txt) retains public bytes,
independently assembled from `postgresEntrypointScriptPg15` and the decoded
`START_DB_SCHEMA_SQL`, `START_DB_WEBHOOK_SQL`, `START_DB_SUPABASE_SQL` template
literals in `db-bootstrap/templates/db-{schema,webhook,supabase}.sql.ts`.
The three SQL strings have an added newline between each, followed by `EOF\n`,
the empty-settings header `\n# supabase [db.settings] configuration\n`, another
newline, and final `EOF` without trailing newline. The exec line retains its
space after `/etc/postgresql`. The leading newline is significant.

The resulting UTF-8 bytes are 9642 bytes with source-derived SHA256
`6f995b129657d28b15a97a1c8a957a7c0015a9865880747c25ad00e3b6d7dd86`.
This digest describes fixed public source, never observed runtime input. Runtime
validation compares exact bytes and does not hash rejected SQL/env values.
The actual pinned CLI must independently match this authority during fresh owner
qualification; captured argv never becomes authority and receipts are not repaired.

The private wrapper checks DOCKER_HOST against its workdir's nonexistent socket,
DOCKER_CONFIG against its empty private docker directory, and rejects context/TLS/
certificate/API-version overrides. Other inherited variables are not container env
unless requested with -e; the exact profile allows only its four key-only names.

This qualifies source conformity and custody through refused create only. It does
not qualify bootstrap semantic safety, secret-file delivery, execution continuity,
complete startup, runtime readiness or repository migrations. The refused-create path executes none of these
bytes and `dev.py up` remains gated. The separate opt-in `postgres-bootstrap`
qualification executes the exact public fixture in a disposable selected-image
container; its selected SQL/key observations and limits are recorded separately
in `../ENV_POSTGRES_BOOTSTRAP_EVIDENCE.md`.

## Reproduce the public bytes independently

Run this investigation recipe from the repository root. It downloads immutable public
primary sources into a new temporary directory, assembles a candidate there, and compares
it with the reviewed fixture. It neither writes the repository fixture nor executes its
shell/SQL. The inline Python is an auditable derivation recipe, not a runtime generator.

```bash
profile_sources=$(mktemp -d /tmp/env-profile-source.XXXXXX)
profile_base=https://raw.githubusercontent.com/supabase/cli/753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4/apps/cli/src/command-internal/db-bootstrap
curl --fail --silent --show-error "$profile_base/postgres.service.ts" -o "$profile_sources/postgres.service.ts"
for part in schema webhook supabase; do
  curl --fail --silent --show-error "$profile_base/templates/db-$part.sql.ts" -o "$profile_sources/$part.ts"
done
python3 - "$profile_sources" <<'PY'
from pathlib import Path
import hashlib
import re
import sys

source = Path(sys.argv[1])
service = (source / 'postgres.service.ts').read_text()
# Review these two source functions against the explicit assembly below.
for name, ending in [('postgresEntrypointScriptPg15', '\n}\n'),
                     ('postgresSettingsToPostgresConfig', '\n}\n')]:
    start = service.index('function ' + name + '(')
    print(service[start:service.index(ending, start) + len(ending)])

parts = []
for name in ['schema', 'webhook', 'supabase']:
    template = (source / (name + '.ts')).read_text()
    literal = template.split(' = `', 1)[1].rsplit('`;', 1)[0]
    assert '${' not in literal  # These pinned public templates have no interpolation.
    # Their only TS escapes are doubled backslashes and escaped backticks.
    assert re.search(r'\\(?![\\`])', re.sub(r'\\[\\`]', '', literal)) is None
    parts.append(re.sub(r'\\([\\`])', lambda match: match[1], literal))

script = ("\ncat <<'EOF' > /etc/postgresql.schema.sql && \\\n"
          "cat <<'EOF' >> /etc/postgresql/postgresql.conf && \\\n"
          "exec docker-entrypoint.sh postgres -D /etc/postgresql \n"
          + '\n'.join(parts)
          + "\nEOF\n\n# supabase [db.settings] configuration\n\nEOF")
raw = script.encode('utf-8')
assert len(raw) == 9642
expected = '6f995b129657d28b15a97a1c8a957a7c0015a9865880747c25ad00e3b6d7dd86'
assert hashlib.sha256(raw).hexdigest() == expected
assert raw == Path('platform/deployment/fixtures/supabase-pg17-bootstrap.txt').read_bytes()
(source / 'candidate.txt').write_bytes(raw)
print(len(raw), expected)
PY
```

This preserves literal template trailing newlines, inserts one additional newline
between each SQL template, retains the exec line's trailing space, and adds no final
newline. A mismatch stops the recipe; never replace authority with CLI-captured input.
Docker TLS activation (`DOCKER_TLS`), default-platform selection and custom HTTP headers
are also forbidden even when empty, alongside the routing overrides listed above.

## Closed PostgreSQL create request

After validating the original profile, image-owner child selection and current
run network/volume descriptors, the refused-create boundary constructs one detached
in-memory Docker API1.48 request. It independently checks every nested key, value
and primitive type before retaining only `create_request_proven: true` beside the
existing safe facts. The body, env and bootstrap are never retained or hashed as
observed runtime evidence. There is no transport invocation and the real transport
still rejects the container-create route before socket access.

Primary mapping authorities are Docker CLI28.0.0
[`cli/command/container/opts.go`](https://github.com/docker/cli/blob/v28.0.0/cli/command/container/opts.go),
Moby28.0.0
[`client/container_create.go`](https://github.com/moby/moby/blob/v28.0.0/client/container_create.go),
and its
[`docs/api/v1.48.yaml`](https://github.com/moby/moby/blob/v28.0.0/docs/api/v1.48.yaml).
The CLI options map the four explicit `-e` names to ordered `Env` values, `sh`
to `Entrypoint`, the unchanged `-c` operand/bootstrap to `Cmd`, and the three CLI
labels to `Labels`. Named `-v` maps to `HostConfig.Binds`; it does not declare an
anonymous `Volumes` destination. The published TCP port supplies `ExposedPorts`
and `HostConfig.PortBindings`. Health shell command maps to `CMD-SHELL`, with
interval 10000000000ns, timeout 2000000000ns and retries 3. Restart is
`unless-stopped` with maximum retry count 0. Linux host-gateway maps to
`HostConfig.ExtraHosts`; network ID maps to `HostConfig.NetworkMode` and the
`NetworkingConfig.EndpointsConfig` key, with aliases `db` and
`db.supabase.internal`.

The request has method `POST` and path
`/v1.48/containers/create?name=<run-database-name>&platform=linux%2Famd64`.
API Config fields are flat beside `HostConfig` and `NetworkingConfig`, without
an enclosing `Config` property. The selected child digest supplies `Image`.
Explicit `linux/amd64` platform and `127.0.0.1` HostIp deliberately tighten the
ENV profile; this is not a claim of byte-identical CLI serialization. Unknown
fields, defaults, inherited env names and arbitrary overrides are forbidden.

This construction does not qualify bootstrap semantics, secret provisioning,
fresh-volume setup execution, real lifecycle continuity, runtime readiness or KDG
fingerprint keys. The guarded fresh invocation now observes volume absence without
pre-acquisition; the [lifecycle authority](supabase-pg17-lifecycle.md#fresh-branch-admission-and-synthetic-acknowledgement)
records its pinned source and separate synthetic missing/create/copy/refused-start
proof. Its planned volume profile is not observed metadata, and synthetic volume
acknowledgement proves no real ownership or freshness. `runtime_ready` remains false
and `dev.py up` remains guarded.

## Separate disposable bootstrap execution

`tests/qualify_startup.py --control postgres-bootstrap` requires current prepared
run evidence and repeat-qualified image-owner receipts before local Docker use.
It selects the pinned Linux/amd64 child reference and verifies the local config
identity, platform, repository digest, inherited labels and declared volumes.
Its fresh run-labelled container uses network none, no published ports, no host
binds and a 1GiB tmpfs database directory. Fixed limits set memory and total
memory-plus-swap to 2GiB, CPU to two cores and PIDs to 256; Docker logging is
disabled with log driver `none`. Exact corresponding HostConfig values are
rechecked before ownership-dependent operations. It never shares the guarded create
request transport or changes its route refusal. Bootstrap SQL remains exactly
the source-backed bytes above; no repository SQL or seeds are executed.

The public proof checks catalog password verifiers for all seven source-listed
roles, JWT database settings, both exact `supabase_functions.migrations` versions
and `_analytics`/`_supavisor` schemas in `_supabase`. Password installation is proved by comparing each catalog MD5/SCRAM verifier
with the public synthetic password. Separate positive and deliberately wrong-password
TCP queries characterize the pinned loopback trust policy; they both must succeed,
with the current HBA file matching the inspected immutable image authority
(SHA256 `a925911753f4975548eb4079177441c886aa22b6dd69f2b0cff98f779fb0b66a`).
Only after these observations does the result report
`loopback_password_required: false`; no password-enforcement claim is made.
The image HBA uses `trust` for local `supabase_admin` and loopback hosts, and
`scram-sha-256` for other configured hosts. The first actual run exposed this
source-derived distinction: an attempted negative-password enforcement assertion
failed despite correct installed verifiers; its owned cleanup completed. The
qualifier retains the exact bootstrap/environment instead of changing HBA policy
to make that assertion pass. Runtime network exposure remains outside this proof.
Commands, output and total initialization time are bounded; only selected safe
booleans/codes escape. Creation is attempted once. Cleanup requires the recorded
ID plus current matching image/labels/isolation; uncertain creation or replaced
resources are never adopted, replayed or deleted. This proves neither durable
volume freshness/reuse nor complete runtime/scaffold readiness.

The active PostgreSQL `SHOW data_directory` must return
`/var/lib/postgresql/data` before its actual filesystem is checked as `tmpfs`
after initialization.
Docker inspection must continue to show only the `none` network, no published
ports, no binds and the exact tmpfs declaration before every owned operation.


## Bounded observed shutdown for the disposable proof

After the SQL/key checks, the same lifecycle owner starts a separate fixed
15-second shutdown phase, keeping the 120-second initialization budget unchanged.
It records the nonzero UTC StartedAt of the first verified running instance before
SQL/key checks and requires the same started instance immediately before stop,
requests `docker stop --timeout 5` by the exact recorded ID, then rechecks both
ownership and process state. Every command remains capped at ten seconds and
65,536 combined output bytes. Stop command success alone does not qualify a
shutdown: Docker may kill a process after the stop timeout.

Successful qualification requires Status `exited`, Running and Dead false, PID
zero, integer exit code zero, OOMKilled false, empty Error, unchanged StartedAt,
and a completed nonzero UTC FinishedAt strictly later than StartedAt. UTC timestamp
validation preserves nanosecond ordering. The successful result adds only
`shutdown_verified: true` and `forced_shutdown: false`; `runtime_ready` stays false.
Safe failure codes distinguish OOM, forced exit137, another nonzero exit, still
running, changed started instance, invalid state, shutdown deadline and command failure without emitting
Docker state, child output or business content.

Cleanup retains an independent ten-second budget. It checks current ownership
again, and after successful shutdown rechecks the same clean stopped state before
normal `rm` and observed absence. Earlier failures/interruption retain owned force
cleanup, never clean-shutdown evidence. An observed identity/configuration change
latches refusal: even a later matching descriptor cannot authorize stop or deletion
in that execution. Uncertain ownership, failed removal or failed absence observation
reports `cleanup_unresolved`. No container adoption/replay, durable storage or real
CLI transport/runtime admission is added.


## Explicit pinned CLI named-volume execution

The `pinned-cli-postgres` startup qualifier alone extends the retained ENV owner
through the actual CLI's first create/archive/start. Default controls retain the
synthetic acknowledgements and refused start. Original ordered CLI operands and
four public environment inputs pass the existing exact profile validator before
immutable image selection and owner dispatch. The disposable API profile tightens
CLI defaults deliberately: loopback-only selected database port, memory and swap
2 GiB, two CPUs, 256 PIDs, logging `none`, restart `no`, no privileged mode. The
approved bootstrap/key, run-owned bridge and freshly created named volume remain.
The database port is checked again immediately before creation; Docker's selected
loopback binding must succeed rather than falling back to another address/port.

The five-second acquisition phase remains. One explicit transition grants at most
120 seconds for CLI dispatch and same-instance running/healthy observations, then
15 seconds for strict observed shutdown and an independent ten-second cleanup.
Each phase uses one total deadline on the retained peer, never per-request resets.
The first successful owner start terminates the CLI process group before any
subsequent service command. Only the actual recorded container ID can receive the
validated archive/start; phases are consumed before uncertain mutations. No retry,
reconnect, adoption, owner SQL or full-stack activation is introduced.

The owner rechecks source/executable/fixture/listener/run-lock custody, immutable
image descriptors, current bridge/volume identity and sole container volume use.
Container inspection checks effective image defaults plus approved overrides,
mount/network/port/resource controls, including both requested database aliases on
the recorded endpoint. Docker-added endpoint names may remain. Identity loss permanently revokes cleanup
permission. Cleanup removes only the recorded container, confirmed newly created
volume and, when its creation response was confirmed in this acquisition, bridge.
An existing matching bridge is retained. Uncertain creation/ownership/transport
preserves unresolved resources and refuses rather than fabricating success.

Docker API 1.48 responses support bounded Content-Length or strict chunked framing
on the existing closed transport: no ambiguous CL+TE, chunk extensions, trailers,
content encodings, extra/trailing bytes, reconnect or replay. Empty lifecycle
successes are route-specific. Running/healthy named-volume execution proves neither
SQL semantics, durable reuse/recovery, Auth nor environment admission; every result
keeps `runtime_ready=false`.


Created-state network observations follow Docker's staged attachment: immediately
after create, the verified network-name entry may have an empty `NetworkID` before
network allocation at start. Only a never-started `created` container with Running,
Dead and OOMKilled false, PID/exit/restart count zero, empty Error and both zero UTC
start/finish timestamps may use this pending value, and only before this execution
attempts start. The immutable `HostConfig.NetworkMode` ID and current run-owned
bridge checks remain exact throughout. Foreign nonempty IDs always refuse; after
start is attempted, running and stopped observations require the recorded network
ID. An empty pending value does not prove an attached or running network.


Private handoff envelopes preserve the CLI's phase-specific environment boundary:
create alone carries and validates all four public container inputs plus exact
Docker routing. Copy/start carry only exact `DOCKER_HOST`/`DOCKER_CONFIG` routing
inputs; they do not inherit or retransmit create's command-specific container
inputs. Unexpected Docker routing overrides refuse in every phase. Original
create operands and inputs remain validated before any owner create dispatch.


Cleanup consumes its single independent ten-second budget before any inspection
or mutation. Success, uncertainty, timeout or interruption cannot authorize a
second attempt, repeat a delete, or restart that deadline. The CLI supervisor's
finally path starts owned cleanup only if that execution has not attempted it;
a failed cleanup preserves its original failure and unresolved-resource evidence.


## Explicit named-volume persistence qualification

The separate `pinned-cli-postgres-persistence` control extends only its fresh,
source-qualified execution-owned volume through one container replacement. Actual
CLI first create/copy/start remains unchanged; the CLI is terminated at that boundary.
ENV commits a public run/cluster probe, clean-stops and confirms removal of the first
container, retains the unchanged unused volume/bridge, then creates a distinct
container with the same immutable profile and reinstalls the public key archive.
Final verification requires healthy stable execution, existing initialization markers
and the committed run/cluster probe before clean shutdown and final owned disposal.
There is no cross-run initialized-volume adoption, reset, backup or recovery claim.

Fixed predicate SQL uses detached exec on the retained connection, with no attached
stdin/stdout/stderr or TTY, no privileged mode, explicit postgres user and public
synthetic password. Only closed probe commands are admitted; no arbitrary SQL/exec
selector or response-payload report. Exec identity/configuration, completion and
integer zero exit are required; a successful start response alone is insufficient.
Before start, exec inspection must describe an unstarted process with explicit null
ExitCode, Running=false and PID0. During execution null remains valid; only confirmed
completion after successful start accepts integer exit zero. Missing/completed-null or
boolean exit codes refuse. Docker may retain the completed exec PID. Each uncertain
mutation is consumed once.

Budgets remain acquisition5s, first execution/probe120s, first clean shutdown/removal15s,
replacement/verification120s, final clean shutdown15s, final cleanup10s. Intermediate
removal is not final cleanup and cannot consume/reset its single attempt. Loss of
custody/reference/transport prevents continuation or unsafe disposal. Failures in a
confirmed container-free gap may retain run resources with a refusal; they do not
claim cleanup. Existing matching bridge preservation and default controls remain.

## Explicit initialized-volume CLI start qualification

The separate `pinned-cli-postgres-initialized` control replaces the persistence
qualifier's ENV-created replacement with a second actual pinned CLI process. Both
processes are terminated at their executed PostgreSQL start boundary. The replacement
consumes only the same operation's confirmed-created volume after committed probe,
clean first shutdown, old-container absence and unchanged unused volume/bridge checks.
An initialized volume from a different execution is not admitted.

Pinned `start-database.ts` probes the volume before network/create. Its container
specification is shared with the fresh path in `postgres.service.ts`; the reviewed
public bootstrap/archive remain unchanged. An independent second private workdir
changes only workdir-derived labels/routing. Both fixture/listener custodies stay
current through replacement verification and final disposal. Initialized inspect/ensure
must verify the proven unused volume; ensure acknowledges it without another volume
POST. The initialized event sequence uses its own ensure acknowledgement, preserving
the legacy synthetic existing-volume refusal behavior.

The two CLI start boundaries, distinct replacement, persisted run/cluster/init predicates,
both clean shutdowns and final owned disposal are separate required proof facts.
Budgets stay acquisition5s, first execution/probe120s, first shutdown/removal15s,
second CLI/verification120s, final shutdown15s and single cleanup10s.
The second supervisor hands a successfully started replacement to the same outer
owner; it cannot dispose it before SQL verification. Failed/uncertain operations
cannot reconnect, adopt, retry mutations or claim success. Public lifecycle, full
post-health fresh/webhook/current-branch setup, cross-execution reuse and recovery
remain unqualified; `runtime_ready=false`.

## Post-start health and refused Auth migration-job authority

The explicit `pinned-cli-postgres-auth-boundary` qualification retains the fresh
actual CLI beyond start, through its health observations and first Auth job request.
It refuses the job without dispatch. Immutable source commit remains
`753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4`:

- `docker-lifecycle.ts` / `db-bootstrap/health-check.ts` inspect exactly
  `container inspect supabase_db_<project> --format {{json .State}}`. This is the
  same argv as the initial missing-container probe; guarded phase distinguishes it.
- `db-bootstrap/start-database.ts` invokes fresh setup after health. PG17 setup with
  Realtime/Storage disabled and Auth enabled reaches the Auth migration job first.
- `db-bootstrap/db-setup.ts` opens the host-facing database session before resolving
  that job. Its later setup SQL follows successful job completion. Connection-driver
  probes are possible; reaching the job is not a zero-SQL or independently verified
  session-identity/authentication claim.
- `db-bootstrap/internal-db-connection.ts` derives the job's container-network URI
  using role `supabase_auth_admin`, internal port5432, database postgres and the public
  synthetic password. This is distinct from the CLI's host-facing database port.
- `docker-run.args.ts` and `docker-run.layer.ts` serialize `run --rm`, named network,
  Linux `--add-host host.docker.internal:host-gateway`, key-only environment flags,
  project labels, image and command. Environment values enter the child environment,
  not argv. No mounts, ports, working-directory or entrypoint override apply here.

Ordered Auth job environment names: API_EXTERNAL_URL, GOTRUE_LOG_LEVEL,
GOTRUE_DB_DRIVER, GOTRUE_DB_DATABASE_URL, GOTRUE_SITE_URL, GOTRUE_JWT_SECRET.
Values respectively use the configured Auth external URL, error, postgres, exact
internal URI, configured app origin and existing public synthetic JWT secret.
Both `com.supabase.cli.project` and `com.docker.compose.project` labels match the run.
The image is the approved qualified GoTrue reference; command is `gotrue migrate`.
Neither this profile nor a refused request authorizes executing that job.

Health replies select only safe current owned state fields, excluding health logs.
Current instance identity, resources and private fixture custody remain checked.
Budgets stay acquisition5s, total execution120s, shutdown15s and one cleanup10s.
Qualification requires the exact refused boundary and same-instance normal shutdown
before owned disposal. Public lifecycle, actual Auth migrations, later setup and
whole-stack readiness remain separate gates.

## Explicit disposable Auth migration-job execution

The separate `pinned-cli-postgres-auth-migration` qualifier extends the existing
retained ENV owners through this exact first job only. It first validates the actual
pinned CLI request against the original profile above, consumes terminal admission
and terminates/reaps the proven CLI group without a success acknowledgement. It then
rechecks the same healthy owned PostgreSQL start identity and fixture/listener/source/
resource custody before owner dispatch. This closes the CLI's earlier host session;
the job's container-network connection is separate. Later direct-session CLI setup
SQL cannot follow this boundary. Fixture5s and total execution120s remain unchanged.

Use the qualified immutable GoTrue Linux/amd64 child/config pair. Authv2.197.0
[Dockerfile](https://github.com/supabase/auth/blob/v2.197.0/Dockerfile) installs
`/usr/local/bin/auth`, a gotrue symlink to it and migrations under
`/usr/local/etc/auth/migrations`, then selects User=supabase and Cmd=[auth]. Root
read the primary source and inspected the already cached selected image's Config:
User=supabase, WorkingDir=/, Cmd=[auth], Env contains exactly the public PATH
`/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin` and
GOTRUE_DB_MIGRATIONS_PATH=/usr/local/etc/auth/migrations, ArgsEscaped=true.
The Docker CLI normalizes away empty/default fields. Direct Docker API1.48 image
inspection additionally returns exactly AttachStderr/AttachStdin/AttachStdout, OpenStdin,
StdinOnce and Tty=false; Domainname/Hostname/Image=""; Entrypoint/Labels/OnBuild/Volumes=null.
The image validator requires these exact API defaults alongside the five values above.
Healthcheck, ExposedPorts and Shell are absent. Effective container checks retain the
execution fields separately; generated container hostname is not an inherited image
requirement. Moby28 merge preserves supplied six environment values first and appends
the two unmatched image values; it does not inherit image ArgsEscaped. Linux effective
ArgsEscaped is false, omitted by the API or explicit boolean false; true, null and
non-boolean values refuse. Image inspection still requires ArgsEscaped=true.
See [Moby merge](https://github.com/moby/moby/blob/v28.0.0/daemon/commit.go). The closed owner rejects additional or changed executable/volume/exposure
behavior outside this approved image profile; current image config identity remains independently bound
by the existing image owner. Observed caller input never becomes authority.

The owner maps the original six exact environment values, gotrue migrate command,
run bridge, Linux extra-host and two project labels to a detached Docker API1.48
create/start/inspect/delete lifecycle. Its exact job name is
`supabase_auth_migrate_<project>` and create path is
`/v1.48/containers/create?name=<job-name>&platform=linux%2Famd64`.
It explicitly selects Linux/amd64 and the immutable image, uses restart=no/logging=none,
2GiB memory and total swap, two CPUs/PIDs256, and forbids mounts, published ports,
privileged or host namespace behavior. AutoRemove=false deliberately replaces the
CLI's --rm: retain the exited container to verify identity, effective configuration,
strict non-OOM/non-dead integer-zero exit and valid start/finish evidence before
normal deletion and observed absence. Fast exit before the first running poll is
permitted; a start acknowledgement alone never qualifies completion. Unknown or
uncertain creation is not adopted by name and cannot authorize unsafe cleanup.

The existing bridge may contain only recorded PG/job identities while that job is
owned; existing PG volume references must still contain PG alone. Job custody is
rechecked independently through exit/removal. Dispose a proven job before PG/storage/
network teardown, preserving ambiguity after lost transport/ownership. Every mutation
is consumed once, including removal; the one cleanup10s deadline is not reset.
Successful PG shutdown retains its separate15s phase and existing same-instance
normal-exit proof. No reconnect/replay, attach/log/wait endpoint or generic forwarding.

Selected result facts distinguish job dispatch/exit/disposal from PG shutdown and
complete owned cleanup. Job exit0 is not full Auth schema/service readiness, CLI
continuation, independent session authentication, full fresh setup or runtime
admission. `fresh_setup_completed=false` and `runtime_ready=false` remain. Only
publisher Auth migrations in the fresh operation-owned synthetic DB execute;
repository owner migrations/accounts/grants, production/pilot and dependent app or
service work remain outside this qualification. Accepted ADRs and legacy controls
remain unchanged. See [job evidence](../ENV_AUTH_JOB_EVIDENCE.md).


Review hardening of this same bounded profile explicitly requests and verifies private
cgroup namespace (CgroupnsMode=private). Effective interactive/attachment flags must be
omitted/default false or boolean false only. Top-level execution Path=gotrue and exact
Args=[migrate] must agree with Config.Cmd, as defined by Moby28
[newContainer/getEntrypointAndArgs](https://github.com/moby/moby/blob/v28.0.0/daemon/container.go).
Paused/Restarting must be typed false. Once observed, start and completed finish
timestamps remain bound through subsequent ownership/removal checks. Deletion is
consumed immediately before DELETE after prechecks; timeout before any delete does
not consume the one final cleanup attempt. Lost/uncertain mutation remains unreplayed.

## Independent Auth migration catalog verification

The explicit `pinned-cli-postgres-auth-catalog` control extends the completed
migration-job proof with read-only database pre/postconditions. Source authority is
[Authv2.197.0](https://github.com/supabase/auth/tree/4eee58f296d9698a1c2c0ae14d7a0b379c7622d3/migrations),
commit4eee58f296d9698a1c2c0ae14d7a0b379c7622d3. Its75 up migrations have literal
versions `00` through `20260831180000`; the postgres-specific20220614074223 file
is included. `main.go` embeds migrations/* and cmd/migrate_cmd.go uses Popv6.1.1
MigrationBox/UpTo(0), with schema_migrations in the configured Auth namespace.
Pop's ParseMigrationFilename preserves the numeric prefix as a string; its migrator
inserts that exact Version. No observed database output defines the expected ledger.

Selected structural evidence follows the publisher migrations: real auth.users,
identities, sessions, one_time_tokens, mfa_recovery_code_sets and mfa_recovery_codes
tables; the latest migration adds nullable timestamptz one_time_tokens.expires_at.
Before migration the latest version, recovery tables and expires_at must be absent.
The pinned PostgreSQL bootstrap contributes seven historical Auth markers, defined
by commitcf90815413819eb057a9916c1598692c160ebeb4 auth-schema.sql. Require exactly
those seven before the job. An already-current baseline cannot qualify this fresh
transition. After the job exits0 and is removed, require the exact82-entry union
of those seven and the75 current Auth migration versions, together with selected
structure, not merely a count or maximum version. This is selected structural proof,
not byte-for-byte/full schema equivalence or Auth service readiness.

Both predicates run only through exact detached psql exec requests on the same
currently healthy, owned PostgreSQL instance after proven CLI termination. Use a
read-only transaction, bounded statement/lock waits and error on false/NULL. Consume
each attempt/exec identity once; verify process configuration, running state and
integer-zero completion. Recheck fixture/resource/image/start identity before and
after exchanges; no replay, reconnect, adoption or generic SQL/exec route. No query
output is attached or logged. Existing execution120s/shutdown15s/cleanup10s limits
remain. Unknown ownership/closed transport preserves resources. The job is disposed
before postcheck, and normal PG shutdown/disposal still precedes qualification.

Existing execution-only and refusal controls retain their original meaning. New
catalog success does not authenticate the earlier CLI host-facing session, acknowledge
the job to that CLI, execute later setup SQL or apply repository owner migrations.
No accounts/grants are created. `fresh_setup_completed=false`, `runtime_ready=false`;
public lifecycle and dependent KDG work remain gated. Exact source hashes, ATDD/TDD,
real predicate-negative controls and final regression are recorded in
[Auth catalog evidence](../ENV_AUTH_CATALOG_EVIDENCE.md).


Catalog exec state authority: Mobyv28 daemon/exec.go marks Running before Process
assignment, and daemon/inspect.go reports Pid0 when Process is absent. Therefore a
running starting-window Pid0 is permitted only with NULL ExitCode; it cannot itself
qualify. Successful completed execution requires integer-zero ExitCode and a positive
PID from its process. Pre-start remains not running/Pid0/NULL exit. No observation
of an intermediate running state is mandatory for a fast valid completed process.


## Host-facing database backend lifetime

The explicit `pinned-cli-postgres-cli-db-backend` qualifier extends the retained Auth
catalog control. Pinned CLI source runFreshDbSetup/connectLocalPostgres opens the
host-facing postgres/postgres connection before the blocked Auth-job request. Before
terminating that proven CLI group, ENV independently checks exactly one non-loopback
TCP client backend besides its observer; it must have positive client port,
postgres user/database and idle state. Count the complete external-client set before
validating those fields: wrong roles/databases/states cannot disappear through a filter.
Background workers, Unix-socket clients and loopback health probes do not qualify.

After the existing single kill/reap, one read-only detached SQL invocation waits up to
3s for zero external clients, with pg_stat_clear_snapshot before observations and
bounded sleep. PostgreSQL17 [statistics authority](https://www.postgresql.org/docs/17/monitoring-stats.html)
explains that activity remains cached within a transaction until the snapshot is
cleared. This refreshes observer-local information, not persistent state or statistics
counters. Existing statement5s/lock1s/idle5s and execution120s bounds remain.
The departure deadline is checked after the count returns and before accepting zero;
a late first or later empty observation refuses. A separate3.05s delayed-zero fixture
proves this without extending the SQL or operation limits.

Both observations require pg_read_all_stats privileges before querying activity, so
restricted views cannot hide wrong-role external clients. Existing role privileges
are checked, never granted or changed. Both use current healthy same-PG/resource/
image/fixture custody and exact closed typed detached execs. Lost responses/attempts/IDs cannot be replayed. Selected
presence/departure facts do not identify an OS process/backend pair or prove a password
method or continuing CLI-session identity. No job acknowledgment is sent. After verified
departure the existing Auth catalog/job and normal PG shutdown/disposal must pass.
Later CLI setup/privilege/vault/seed/migration work stays gated; public setup/runtime
remain false. See [backend lifetime evidence](../ENV_CLI_DB_BACKEND_EVIDENCE.md).


The existing fixture helper's five-second alarm raises TimeoutError through its
normal refusal path. Once fixture_main holds the verified CLI parent's pidfd, that
path stops the parent before returning failure. Default SIGALRM termination must
not bypass this protection while the owner checks backend presence. No alarm or
operation limit is extended. The private process regression deliberately delays
presence6s and requires no CLI continuation marker/job and owned cleanup; this is a
failure-boundary fixture, not permission to keep a CLI alive after its deadline.


Two additional closed SQL fixtures force occupied→timely-empty and occupied→late-empty
observations. A transaction-local setting counts exactly two evaluations of fixed
input rows; rollback/exec exit discards it. The rejection fixture carries only this
ordinal in server-local exception detail, preserving the oracle across subtransaction
rollback. Conditions, deadline checks, exits and rejection messages remain those of
the production predicate; unit comparison removes only fixed relation substitution
and this diagnostic detail. No role, table or business data changes. These fixtures
prove polling branches, not live pg_stat_activity cache behavior; snapshot-refresh
placement and normal real-backend observation retain their separate evidence.
