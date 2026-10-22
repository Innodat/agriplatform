# Local development through the Supabase CLI

The active ENV direction is a thin wrapper around pinned Supabase CLI2.120.0.
The CLI owns its supported PostgreSQL/Auth/gateway lifecycle. Historical Docker
interception qualifiers below are retained evidence and are not prerequisites for
this route. Full KDG/Identity/Access readiness still requires their owner work.

## Daily commands

Select a fresh canonical UUID, the explicit disposable target and a CLI2.120.0
executable. Existing retained toolchain binaries can be used directly; a new
source-bound toolchain/image qualification receipt is not required by this route.
The approved wider baseline, including TypeScript7.0.2, is unchanged.

```sh
KDG_TARGET=platform/deployment/environments/kdg-local.json
KDG_RUN_ID=$(python3 -c 'import uuid; print(uuid.uuid4())')
KDG_SUPABASE=/absolute/path/to/supabase-2.120.0
python3 platform/deployment/dev.py prepare --target "$KDG_TARGET" --run-id "$KDG_RUN_ID" --supabase "$KDG_SUPABASE"
python3 platform/deployment/dev.py up --target "$KDG_TARGET" --run-id "$KDG_RUN_ID" --supabase "$KDG_SUPABASE"
python3 platform/deployment/dev.py verify --target "$KDG_TARGET" --run-id "$KDG_RUN_ID" --supabase "$KDG_SUPABASE"
python3 platform/deployment/dev.py stop --target "$KDG_TARGET" --run-id "$KDG_RUN_ID" --supabase "$KDG_SUPABASE"
```

Preparation reuses the existing config renderer and project naming with a small
native target/config marker. Use a fresh run: historical unmarked/qualified runs
are preserved and refused. Normal CLI .temp/state files are allowed. Routine source
or documentation edits do not require rebuilding all toolchain/image receipts.

Startup checks local Docker>=28 and occupied target ports. It uses a project-specific
bridge configured for localhost binding and passes that network consistently to the
CLI, including reset. Stop retains data. Vendor stdout/stderr are captured because
they can contain keys; results expose safe stages/codes rather than payload dumps.
Private CLI/Docker config and the local socket prevent ambient remote context use.
A failed/timed-out command is not automatically retried or cleaned up; inspect state
through the explicit target before further action. No Docker prune is provided.

verify means vendor status, database TCP reachability and Auth health. It does not
prove SQL authentication, synthetic sign-in, app permissions or owner migrations.
Application runtime readiness remains false until those separate gates are delivered.
The wrapper starts no application API/web and provisions no real accounts/provider.

## Reset means local database reset

For a disposable synthetic run whose data may be discarded:

```sh
python3 platform/deployment/dev.py reset --target "$KDG_TARGET" --run-id "$KDG_RUN_ID" --supabase "$KDG_SUPABASE" --confirm-target kdg-local
```

This delegates to `supabase db reset --local --no-seed --yes` in that exact
workdir/network. It clears the local database; it is not full environment disposal.
Repository Supabase migrations/seeds are disabled in generated configuration.
Reapply application schemas/fixtures through existing owner coordinators when those
are delivered. No remote reset, automatic grants or migration ownership transfer.
Do not use this against historical or real-data environments.

[Native route evidence](ENV_NATIVE_CLI_EVIDENCE.md) records actual verification and
limits. [Approved course correction](../../_bmad-output/planning-artifacts/sprint-change-proposal-2026-10-20-lean-env.md)
records the change in direction. Historical code/resource cleanup needs a separate
reviewable inventory; nothing below is a mandate to resume interception work.

## Safe inspection and incomplete preparation

Start with the wrapper's `verify` command above. For container status metadata only:

```sh
KDG_WORKDIR="$PWD/platform/deployment/.local/kdg/$KDG_RUN_ID"
KDG_PROJECT=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["project"])' "$KDG_WORKDIR/native.json")
env -i PATH=/usr/bin:/bin DOCKER_HOST=unix:///var/run/docker.sock DOCKER_CONFIG="$KDG_WORKDIR/docker" docker ps -a --filter "label=com.supabase.cli.project=$KDG_PROJECT" --format '{{.Names}} {{.Status}}'
```

Record the wrapper stage/code/exit, CLI version and this safe status summary for
troubleshooting. Avoid dumping Docker Config/Env or vendor debug output. If initial
prepare fails partway, preserve that directory and choose a fresh UUID; an incomplete
run is deliberately refused. No automated repair/deletion is needed. Concurrent
prepare of the same UUID can fail closed; retry after the first finishes. Repeating
up for a running matching project uses normal vendor already-running behavior.

## Private local credentials for owner setup

Normal output hides credentials. When a consuming owner needs local bootstrap
configuration, explicitly capture vendor status into a new private secret file while
the run is started. This is secret configuration, not a diagnostic log or readiness
receipt. Do not print/paste its contents. Owners retain restricted runtime-role and
migration boundaries; this file does not authorize app grants or production access.

```sh
python3 - "$KDG_TARGET" "$KDG_RUN_ID" "$KDG_SUPABASE" <<'PYCODE'
from pathlib import Path
import os, subprocess, sys, uuid
sys.path.insert(0, str(Path('platform/deployment').resolve()))
import dev, native_cli
source, run_id, cli = sys.argv[1:]
assert str(uuid.UUID(run_id)) == run_id
raw = dev.read(Path(source).absolute())
target = dev.decode(raw)
dev.validate(target, dev.decode(dev.read(dev.ROOT / dev.SCHEMA)))
run = dev.ROOT / 'platform/deployment/.local/kdg' / run_id
native_cli.check_run(run, target, raw, run_id)
network = native_cli.network(target, run_id, False, run)
secrets = run / 'secrets'
secrets.mkdir(mode=0o700, exist_ok=True)
with dev.directory(secrets) as parent:
    dev.check_private(parent)
    fd = os.open('supabase-local.env', os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=parent)
    with os.fdopen(fd, 'wb') as output:
        subprocess.run([cli, '--workdir', str(run), '--network-id', network, 'status', '-o', 'env'],
            env=native_cli.environment(run), cwd=run, stdin=subprocess.DEVNULL,
            stdout=output, stderr=subprocess.DEVNULL, timeout=30, check=True)
print('Private local credential file written; contents not displayed.')
PYCODE
```

The exclusive file create protects an existing secret file from overwrite. If the
command fails, preserve the partial private file for deliberate local handling;
normal lifecycle commands do not consume it or change any application role.

## Access staged membership storage (Access revision2)

Prepare the Access schema separately under access_migrator, with runtime schema USAGE
granted by that owner and no broad defaults. Use the existing Access Alembic route and
actual restricted access_migrator URL; optional coordinated Identity migration remains
first. The migration verifies the exact known catalog/history/ACLs before effects and
before commit, serializes owner execution and bounds waits. Unknown schema/history or
privileges refuse without repair. Both Access roles' restricted flags are checked, as
are the exact existing native Supabase administrator profiles/incoming owner edges and
effective callable Identity-definer authority (schema USAGE plus EXECUTE). Grants and ledger must be permanent with no ordinary
inheritance links. No global role authority is changed for qualification. Offline/stamp/downgrade are prohibited; preserve the
failed history/data and reconcile before an explicit controlled upgrade retry. Never
auto-reverse applied migrations or activate on failure.

Revision2 only stages nullable positive grants.membership_id. It performs no backfill,
Identity FK, inference or activation. Current v1 ignores the field and remains stopped
for real consumers until exact active org/account/member checks and coordinated owner/
consumer delivery; NULL is never a match. Runtime SELECT intentionally covers the new
column while writes and owner assumption remain denied.

[Access owner evidence](../../services/access/ACCESS_MEMBERSHIP_BINDING_EVIDENCE.md)
contains the preparation and aggregate commands, private fixture requirements, repeatable
source-bound retained inspection and recovery results. Fresh preparation must have a
successful unchanged before/after execution-custody witness before aggregate acceptance;
post-preparation source capture alone is insufficient. Optimized Python is explicitly
refused before parsing or fixture access so assertions cannot be bypassed. The current final frame is
access-membership-final-optimized-20261021; final aggregate and retained inspection passed,
and the native run is normally stopped. Restart the retained run through dev.py before
retained inspection. Reuse the existing native fixture
framework with separately validated access_owner_urls; do not substitute Access URLs
for Identity owner_urls. The older PtS port55439/minimal-Identity bootstrap is unsuitable
for the current native target and its guards remain unchanged.

## Protected account actor setup (Identity revision18)

The existing Identity owner CLI now executes `account_actor.ensure`. Prepare the
NOLOGIN verifier with `services/access/tools/prepare_identity_account_verification_role.sql`
under the controlled true administrator, then apply the separate restricted Auth-owner
preparation in `prepare_identity_account_verification_auth.sql` to the selected database.
The exact role has only migrator SET membership; Auth preparation grants schema USAGE,
SELECT(id,deleted_at), enabled Auth RLS and its exact SELECT policy. Unexpected verifier
memberships refuse before Auth/profile observations. Identity migration adds scoped profile
reads and fixed verifiers. Missing or unsafe preparation refuses; no role/ACL repair or
Auth mutation runs in the migration or command.

Run the existing controlled Identity `alembic upgrade head` before activating the CLI
consumer. Clean and exact known historical catalogs are checked before effects; revision18
has its own independently recorded reference and retains references1–17. Failure blocks
activation. Preserve applied migrations, compact receipts and command files for explicit
recovery; do not downgrade, reset, reverse applied migrations or invoke migration on startup.

Use a version1 platform command with explicit `account_id`, `actor_id`, `display_name`,
`expected_absent=true` and required classification `evidence_ref`. Current account-targeted
`account_actor.ensure` authority is mandatory. The server independently checks live Auth
and an ordinary nondeleted profile before retry/business locks. The observation supports
only this bounded execution (five seconds from the start of verification); restarted execution observes
again and rechecks current local profile/authority after waits. No person, employment,
organization membership or application grant is created. System/keyed profiles and foreign
UUID adoption refuse. Historical actors/mappings remain after account deletion.

```sh
# From services/access, using the existing frozen owner environment and prepared target:
python -m operator_cli execute --owner identity --target <prepared-target> --command-file <command.json>
python -m operator_cli outcome --owner identity --target <prepared-target> --command account_actor.ensure --operation-id <UUID> --account-id <UUID>
```

Lookup requires current exact target authority and returns the historical receipt even if
that account later becomes ineligible. New execution/replay still verifies live eligibility.
An unavailable response is not proof of rollback: recover with that operation/account,
then retry only the identical command. Changed input under the same operation conflicts.
Only retry-lock contention reports busy; other waits/dependencies report unavailable.
No receipt is emitted before acknowledged commit. Credentials stay in the existing target
secret; no verifier credential or caller-supplied verification flag is introduced.

Synthetic acceptance uses `services/access/tests/qualify_account_actor_ensure.py --all`
with fresh root-prepared cases and an explicit protected `cli_owner_fixture_path` in the
private fixture input. Its closed owner fixture binds the exact existing run/database,
loopback port and Identity migrator URL; no old private frame is discovered. General
bootstrap portability remains a pre-existing deferred prerequisite. Named stages remain;
`--all` is single-use, `--verify-retained` is repeatable. Bounded UUID/profile observations
add no global reservation or profile retirement lock. Exact proof commands and limits are in
[account actor evidence](../../services/access/ACCOUNT_ACTOR_ENSURE_EVIDENCE.md).
Existing ACCESS-A/B membership-binding activation gates remain; this does not authorize
real consumers, production deployment or broader KDG/Leave implementation.

---

# Historical qualification notes (retained)

These notes describe earlier experimental delivery and its stronger custom-owner
assurances. Their in-progress/next-action wording is historical. Use the normal CLI
route above for current development; preserve their receipts and uncertain resources.

# Disposable KDG target preparation

## Current ENV delivery status

ENV is **partially implemented; the isolated KDG stack is not runnable yet**.
Completed increments qualify selected inputs and refuse unsafe handoff; they do not
close the enclosing ENV acceptance item. See individual evidence records below.

| Boundary | Implemented evidence | Remaining acceptance |
| --- | --- | --- |
| Target/configuration | Protected disposable run preparation, exact source/config binding, deterministic owner names and Docker>=28 gate | Actual isolated stack startup and current readiness |
| Dependency baseline | Six pinned executables including TypeScript7.0.2; Python wheel-lock and frontend compatibility fixtures | Generated consuming application/service proof; target/native compatibility; documented third-party declaration limitations |
| Images/resources | Four immutable image identities, guarded owned bridge/database-volume acquisition, daemon observations, current volume-use refusal, joint same-session acquisition and absent-volume startup construction | Cross-execution initialized-volume admission/recovery, full-stack execution enforcement and reservation/exclusivity |
| PostgreSQL startup | Exact first-create profile, guarded volume owner; selected-image SQL/key proof; opt-in real pinned-CLI create/copy/start on its fresh named volume with health, clean shutdown and owned removal; explicit retained-volume replacement/SQL persistence proof and actual CLI fresh/initialized start boundaries | Cross-execution reuse/reset/recovery, post-start CLI database setup, public lifecycle commands and complete stack/owner readiness |
| Post-Auth privilege setup | Opt-in retained owner applies exact source default-ACL SQL, independently verifies, then cleans owned synthetic resources; eleven-case actual predicate proof and ordinary-control compatibility | Remaining post-Auth setup/CLI continuation; retained operational failure investigations; full stack/scaffold readiness |
| Owner integration | Ordered ENV/P1/SERVICE/Identity/Access/WRITE contracts and retained ownership | Existing generator recipe/schema/templates, regeneration/custom preservation, generated install/type/build/start/current-Access proof, coordinated owner migrations/fixtures/recovery |
| Provider/device | Explicit nonproduction origins/callback contracts | LAN HTTPS/DNS/testCA, actual Entra callbacks and installed Android/iPhone proof at consuming gates |

`up` means `python3 platform/deployment/dev.py up --target <JSON> --run-id <UUID>`:
the repository's intended isolated-stack start command. Its current implementation
validates preparation and ports, checks the Docker Engine and refuses startup.
The shared host was upgraded by the operator after the user approved maintenance and
Supabase/PostgreSQL interruption on2026-10-17. Actual postchecks show Engine/CLI29.9.1,
API1.56 (minimum1.40), unchanged overlay2 and `/var/lib/docker`, and the exact six
selected package versions. All ten originally running container identities/image IDs,
status/health and restart policies match the protected inventory; eight health checks
are healthy and both databases accept connections. An additional previously stopped
`teacher-supply-db-1` is running; the agent preserved that operator/concurrent state.
Backup/recovery execution was not independently observed; no restore-test or unchanged
business-data claim is made. See [maintenance evidence](DOCKER_HOST_UPGRADE.md).

The unchanged prepared KDG run now passes Docker admission and exits2 with
`runtime_adapter_unqualified`, `runtime_ready=false`. Engine>=28 remains required for
the selected localhost-isolation behavior; the runtime adapter remains unfinished.
Other infrastructure provisioning and production/pilot actions remain outside approval.
Continue bounded ENV and scaffold implementation before dependent Identity/Access/WRITE
or KDG server work.

The opt-in [pinned-CLI execution qualifier](ENV_PINNED_CLI_EXECUTION_EVIDENCE.md)
uses the existing retained resource owner and private CLI wrapper through its first
real PostgreSQL create/copy/start. It requires a fresh source-bound prepared run,
qualified tool/image receipts and all four exact selected images present locally.
It rechecks the database port, binds loopback only, caps memory/swap at2GiB, CPU at
two cores and PIDs at256, disables restart/logging, and accepts no host-directory bind.
The CLI group terminates at the first successful start; ENV observes health and the
same instance's clean exit, then confirms removal of its container, fresh volume and
only a bridge proven newly created by that acquisition. Existing matching bridges stay.

```sh
python3 platform/deployment/tests/qualify_startup.py --target platform/deployment/environments/kdg-local.json --run-id <UUID> --control pinned-cli-postgres
```

Acquisition retains its five-second budget. Execution/health has one120-second phase,
shutdown15 seconds and cleanup10 seconds. Cleanup consumes one attempt; a failed or
interrupted attempt cannot replay deletion or acquire a new budget. Requests/output are bounded; malformed or
lost responses never authorize replay or adoption. Failed/ambiguous ownership can
preserve resources for inspection; use only exact identities from that run's inventory,
not broad cleanup. The qualifier is disposable execution proof, not public up/stop,
SQL/domain readiness, initialized reuse/reset/recovery or full Supabase startup.
The separate bootstrap control below remains the SQL/key semantic proof.

The separate [named-volume persistence qualifier](ENV_POSTGRES_PERSISTENCE_EVIDENCE.md)
retains the fresh execution-owned volume across one confirmed container removal and
distinct owner recreation on the same peer. Fixed detached SQL checks commit the run
UUID/cluster identity and verify that data plus initialization markers after recreation.
The public key archive is copied again to the replacement. Both instances must reach
stable health and clean shutdown before final owned disposal. The CLI still ends at
its first start; `cli_first_start_only=true` and `owner_start_count=2` distinguish the
owner's second lifecycle from CLI initialized-branch support.

```sh
python3 platform/deployment/tests/qualify_startup.py --target platform/deployment/environments/kdg-local.json --run-id <UUID> --control pinned-cli-postgres-persistence
```

Use a fresh prepared/qualified synthetic target and exact selected cached images.
The budgets are5s acquisition,120s first execution/probe,15s first shutdown/removal,
120s recreation/verification,15s final shutdown and10s single-attempt cleanup.
Missing marker/cluster/initialization refuses without repair; lost mutation responses
cannot authorize replay/adoption. Container-free-gap or ambiguous ownership failures
may preserve resources for exact-inventory inspection. This control does not admit
volumes across executions, enable full up/stop/reset or qualify backups/recovery.

For unresolved persistence resources, first read only the selected identity fields
from the preserved inventory (replace `<UUID>` with that execution's canonical UUID):

```sh
jq '{run_id,target_id,project:.identities.project,network:.identities.network,database_volume:.identities.volumes.database}' platform/deployment/.local/kdg/<UUID>/inventory.json
```

The inventory reserves names; it does not prove resource creation or ownership.
Its `identities.containers` lists planned application-owner containers, not this
qualifier's PostgreSQL container. Both PostgreSQL instances use the name
`supabase_db_<project>` (also the database-volume name), with distinct Docker IDs;
the bridge is `<project>-network`. Copy the exact project, volume and network values
from this inventory into the placeholders below. These commands only inspect the
local daemon and print selected fields; an absent resource may return nonzero.

```sh
docker --host unix:///var/run/docker.sock container ls --all --no-trunc --filter 'name=^/supabase_db_<project>$' --format '{{.ID}} {{.Names}} {{.Status}}'
docker --host unix:///var/run/docker.sock container ls --all --no-trunc --filter 'volume=<database-volume>' --format '{{.ID}} {{.Names}} {{.Status}}'
docker --host unix:///var/run/docker.sock volume inspect '<database-volume>' --format 'Name={{.Name}} Driver={{.Driver}} Scope={{.Scope}} Labels={{json .Labels}} Options={{json .Options}}'
docker --host unix:///var/run/docker.sock network inspect '<network>' --format 'Id={{.Id}} Name={{.Name}} Driver={{.Driver}} Scope={{.Scope}} Labels={{json .Labels}} Options={{json .Options}} Containers={{json .Containers}}'
```

For each exact container ID returned, inspect only these selected facts:

```sh
docker --host unix:///var/run/docker.sock container inspect '<container-id>' --format 'Id={{.Id}} Name={{.Name}} Image={{.Image}} Project={{index .Config.Labels "com.supabase.cli.project"}} ComposeProject={{index .Config.Labels "com.docker.compose.project"}} Status={{.State.Status}} Running={{.State.Running}} Pid={{.State.Pid}} ExitCode={{.State.ExitCode}} OOMKilled={{.State.OOMKilled}} Dead={{.State.Dead}} StartedAt={{.State.StartedAt}} FinishedAt={{.State.FinishedAt}} RestartCount={{.RestartCount}}'
docker --host unix:///var/run/docker.sock container inspect '<container-id>' --format '{{range .Mounts}}Type={{.Type}} Name={{.Name}} Destination={{.Destination}} RW={{.RW}} {{end}}{{range $name, $value := .NetworkSettings.Networks}}Network={{$name}} NetworkID={{$value.NetworkID}} Aliases={{json $value.Aliases}} {{end}}'
```

Compare the bridge/volume labels `io.agriplatform.env.owner=platform/deployment`,
`io.agriplatform.env.target=<target_id>`, `io.agriplatform.env.run=<UUID>` and
`io.agriplatform.env.project=<project>` with the preserved inventory; the volume
also carries `com.supabase.cli.project` and `com.docker.compose.project` equal to
`<project>`. Check the container's two project labels, exact image config identity
against the qualified image receipt, single named-volume mount at
`/var/lib/postgresql/data`, expected bridge/aliases, and all volume references,
including stopped containers. In a confirmed container-free gap, the volume-use list
and bridge `Containers` must both be empty. A matching current observation does not
restore lost custody or establish persistence, cleanup or recovery success. Preserve
unresolved resources and receipts for investigation; these inspection steps authorize
no removal, restart, SQL, adoption or replay. Avoid unformatted container inspection,
logs and dumps of `Config.Env`, commands, payloads or credential files.

The separate [initialized CLI qualifier](ENV_INITIALIZED_CLI_EVIDENCE.md) uses a second actual pinned CLI process for the initialized-volume
create/copy/start boundary, within the same fresh operation. It preserves the existing
profile/archive and two private fixture custodies through final SQL verification and
disposal. Neither post-start CLI setup nor cross-execution reuse is qualified.

```sh
python3 platform/deployment/tests/qualify_startup.py --target platform/deployment/environments/kdg-local.json --run-id <fresh-qualified-UUID> --control pinned-cli-postgres-initialized
```

The exact existing volume must be current and unused before initialized inspect/ensure
acknowledgements; ensure performs no duplicate volume POST. The second CLI group ends
at its start boundary, then ENV verifies persisted marker/cluster/initialization and
same-instance clean shutdown before final disposal. Budgets and uncertainty-preservation
rules match the persistence control above. Source changes need a fresh prepared and
qualified UUID; preserve previous receipts. Reviewed-source actual proof and541 deployment
tests pass; exact results and requirement coverage are in the linked evidence.

The bounded [post-start qualification](ENV_CLI_POSTSTART_EVIDENCE.md) retains the actual
fresh CLI through current PostgreSQL health observations and validates/refuses the first
Auth migration-job request. Reviewed-source actual proof and559 deployment tests pass;
the job is never dispatched and later setup remains unqualified. Public up stays gated.

```sh
python3 platform/deployment/tests/qualify_startup.py --target platform/deployment/environments/kdg-local.json --run-id <fresh-qualified-UUID> --control pinned-cli-postgres-auth-boundary
```

The control requires the exact pinned job profile and selected safe current health
fields from the same owned PostgreSQL instance. It then terminates the proven CLI group,
verifies normal shutdown and performs bounded owned disposal. It does not independently
prove the CLI database session identity/authentication. Preserve refused attempts and
use a fresh prepared/qualified UUID after source/profile changes. The evidence records
one unexplained nested prerequisite refusal and a targeted successful diagnostic;
the passing diagnostic does not explain the preceding refusal.

The bounded [Auth-job qualifier](ENV_AUTH_JOB_EVIDENCE.md) passes actual execution.
Reviewed-source actual/legacy controls and593 deployment tests pass after three-layer
review and patches. Three new investigations remain deferred; see the evidence.
Disposable local mail uses the approved port15484.
It validates the actual CLI request, terminates that CLI without success ACK and executes
one immutable owner job before verified job/PG disposal. No later setup/full-runtime
claim follows. Its explicit command, after fresh prepare/toolchain/images:

```sh
python3 platform/deployment/tests/qualify_startup.py --target platform/deployment/environments/kdg-local.json --run-id <fresh-qualified-UUID> --control pinned-cli-postgres-auth-migration
```

Do not use an earlier receipt after source/profile changes. This job only mutates the
fresh disposable synthetic database; owner migrations/accounts/grants, provider/device
and existing ENV/P1/SERVICE/public-lifecycle gates remain open.

The separate opt-in [PostgreSQL bootstrap qualification](ENV_POSTGRES_BOOTSTRAP_EVIDENCE.md)
now demonstrates actual selected-image initialization and public synthetic key transfer
in a disposable network-none container with no published ports or host binds. It checks
all seven role password verifiers, JWT settings, SQL markers/internal schemas, actual
key bytes/mode/owner and tmpfs storage, then verifies its owned container was removed.
It caps memory at2GiB, CPU at two cores and PIDs at256, disables Docker logs, and
verifies PostgreSQL's actual data directory. Current ownership checks enforce these
settings before each copy/start/exec/removal.
The [bounded shutdown increment](ENV_POSTGRES_SHUTDOWN_EVIDENCE.md) now requests
normal stop within a fixed phase, verifies the same started instance exited cleanly,
and rechecks that stopped state before ordinary removal. Timeout, OOM, nonzero exit,
restart or uncertain ownership cannot report clean shutdown. Failure cleanup remains
bounded and confined to the verified disposable container; it is not recovery proof.
The pinned image trusts loopback; the proof records that fact separately from password
installation and makes no authentication-enforcement claim. This does not admit `up`.

Run after the existing preparation/toolchain/image qualifications for a fresh source-bound
run, with the exact pinned PostgreSQL child image already downloaded:

```bash
python3 platform/deployment/tests/qualify_startup.py --target platform/deployment/environments/kdg-local.json --run-id <UUID> --control postgres-bootstrap
```

This explicitly executes disposable synthetic image initialization. Commands/output and
initialization/shutdown/cleanup have separate fixed bounds. An uncertain create or lost ownership refuses
without adoption/replay/deletion; `cleanup_unresolved` requires inspection of the recorded
run-labelled resource before recovery. Never use broad container/volume cleanup.
For manual inspection, the exact deterministic name is `env-pg-bootstrap-<UUID>`;
check its current ID, image and `io.agriplatform.env.run` / proof labels against the
failed invocation. A matching name or labels alone does not authorize deletion or
automatic adoption, and uncertain creation must not be retried into the same name.

ENV now implements the first bounded preparation increment of the
[environment contract](../docs/architecture/contracts/scaffold-environment-and-generation.md).
It validates the selected target and reserves deterministic names in a protected receipt.
The preparation command keeps `runtime_ready` false; no containers, database, Auth configuration, accounts,
grants, migrations, fixtures or generated application are provisioned.

From the repository root:

```sh
python3 platform/deployment/dev.py prepare --target platform/deployment/environments/kdg-local.json --run-id 31a38cec-3b65-4bc6-ab5a-3d2924498393
```

Use a new canonical lowercase UUID for each intended run. The checked-in target's
`workspace_root` must equal the absolute checkout root; update that input deliberately
when using another checkout. The command derives the actual root from its own source,
including when invoked from another working directory. The input's root never controls
output placement. The closed version 1 schema admits only the approved KDG owners,
ports, origins, callbacks, project prefix and references. `local_disposable` and
`ci_disposable` are the only environment kinds. The explicit endpoints also reserve
future provider/device inputs; their presence does not qualify DNS, TLS or Entra.

Successful output is safe JSON with `stage: prepared` and `runtime_ready: false`.
Failures are nonzero safe JSON stage/code references without input values, exception
dumps or credentials. CLI help/unknown/missing arguments also fail safely. The command
requires a POSIX filesystem with directory descriptors, no-follow opens, hard-link
installation and IPv4/IPv6 TCP port probes. A sandbox that denies sockets fails closed;
run synthetic verification with the narrowly approved socket-capable test execution.

Only `inventory.json` and `supabase/config.toml` are installed under
`platform/deployment/.local/kdg/<UUID>/` for the run.
The `.local/` owner ignore rule already excludes it. New directories are mode 0700;
the inventory and transient exclusive lock/staging file are mode 0600. The inventory
binds exact target bytes, implementation/schema/contract/baseline/fixture/registry
source hashes, target/run IDs and **reserved** project, owner-container, database-volume
and network names. These names are planned identifiers, with `identities_state:
reserved_only`; they are not observations that runtime resources exist. Raw target
input, secret references and secret contents are not copied into the inventory.
The project ID is the existing prefix plus unpadded URL-safe base64 of the full UUID
bytes (39 characters), keeping the selected CLI's40-character truncation from discarding
run identity. Canonical UUID command/path arguments are unchanged. Inventory also binds
the exact generated configuration hash; old prepared runs are not migrated.

All eight approved ports must be available over IPv4 and IPv6. Probes are held through
preparation and released on exit. This proves availability only during preparation;
a future runtime adapter must recheck before startup. Nothing attaches to an existing
process and no fallback port is chosen. The synthetic fixture is metadata-only and
explicitly has no provisioned accounts, grants or domain records. `secret_refs` are
exact run-local references containing `{run_id}`; preparation neither requires their
existence nor opens them, and does not generate secrets.

Repeating identical preparation verifies the unchanged inventory and source/target
hashes without replacing the receipt or creating another run. Changed sources or
input require a new run UUID. Symlinks, traversal, unexpected files, insecure inventory
permissions and foreign/incomplete run directories are refused. Preparation also
checks ownership and rejects group/other write on existing mutable output ancestors;
an owner-controlled mode0755 `.local` remains supported. One exclusive lock
serializes installation; a concurrent loser may fail safely and can retry once the
successful command exits. Inventory installation uses an fsynced temporary file and
an atomic no-clobber hard link, with directory entries fsynced through creation and
lock removal. An interrupted preparation can leave protected partial
evidence, which subsequent execution refuses to adopt. There is no automatic recovery,
cleanup or permission repair in this increment; preserve and inspect partial evidence.

`verify`, `stop`, and `reset` deliberately return nonzero
`runtime_adapter_unqualified` after input validation. `up` additionally validates an
existing preparation, ports and the local Docker prerequisite described below; a
passing prerequisite still returns `runtime_adapter_unqualified`. `reset` first requires
`--confirm-target` to match the supplied target ID. Confirmation never enables a reset.
No lifecycle command executes owner commands or SQL. The current release registry is
hashed **only as source evidence**: it contains other application/production migration
registrations and must never be executed wholesale for a disposable KDG run. Future
runtime delivery needs a separately verified owner-filtered disposable registration,
using the existing controlled migration coordinator rather than duplicating it.

The [selected dependency baseline](../docs/architecture/contracts/scaffold-dependency-baseline-2026-10-14.md)
is referenced and hashed without changing its versions, including TypeScript 7.0.2.
Running this dependency-free bootstrap on the available Python is separate from
qualification of selected Python 3.15.0, Node 26.11.1, package locks, native wheels,
Supabase image identities and the supported database target. ENV remains open for
those gates, guarded runtime adapters, real owner migration/fixture/readiness proof,
Auth and provider/device qualification; P1/SERVICE generation remains subsequent work.

[Preparation verification and impacts](ENV_PREPARATION_EVIDENCE.md) records exact scope,
requirement/test traceability and red/green evidence.

## Pinned toolchain qualification

After preparing a fresh run, qualify its selected tools:

```sh
python3 platform/deployment/toolchain.py qualify --target platform/deployment/environments/kdg-local.json --run-id <the-prepared-UUID>
```

This command implements the next existing ENV increment on **Linux x86_64 GNU**.
It verifies the unchanged prepared target before installation. It installs Node26.11.1,
npm12.2.0, TypeScript7.0.2 with its Linux native compiler, ordinary GIL-enabled
CPython3.15.0, uv0.13.1 and SupabaseCLI2.120.0 from
[publisher archives and fixed integrity values](toolchain-pins.json).
Node's bundled npm11.20.0 is not used as the selected npm12.2.0.

Per-run tools and a mode0600 receipt live under ignored
`platform/deployment/.local/kdg-toolchains/<UUID>/`, with mode0700 directories.
The separate ignored `kdg-toolchain-downloads/` contains mode0600 archives named by
tool and digest. These are executable-tool caches, not frontend installation roots;
root npm and future independent Python owner locks retain their existing authority.
Nothing installs globally, invokes npm lifecycle scripts or depends on existing
repository `node_modules`. No HOME override is used. Child processes use explicit
executables, empty private npm config files and private Supabase state.

Before a receipt reports `toolchain_ready=true`, every actual tool version must match,
CPython must pass GIL/platform/stdlib probes, and TypeScript must accept a valid fixture
and reject a type mismatch with TS2322. TypeScript7.0.2 returns exit1 for that rejection.
The immutable receipt binds the prepared inventory, target, source/pin hashes and a
fingerprint of every installed payload path/type/mode/file content/link target.
Repeating qualification verifies all of that before executing and preserves the receipt.
Changed input, payload or receipt refuses; no silent repair or adoption occurs.
An interrupted installation remains protected and incomplete; use a new prepared UUID.
Concurrent qualification cannot replace an active install's lock or receipt.
Linux `/proc` must expose the qualification process's retained directory descriptors
so native compiler grandchildren use the same pinned directories. Archive downloads
have a 120-second total deadline with bounded reads; per-archive cache locking waits
at most 120 seconds. Changed output-directory identities refuse completion.

Qualification always reports `runtime_ready=false`. The actual workstation Docker
daemon checked during delivery was27.0.3. Docker documents that releases before28
can expose localhost-published ports to hosts on the same L2 segment, so they do not
qualify this target's loopback-only publishing requirement. Runtime delivery must
enforce Docker>=28 and a verified run-owned loopback-default network **before** any
container startup; printed localhost URLs are not binding evidence. The shared daemon
was not upgraded and no container was started. See
[Docker publishing guidance](https://docs.docker.com/engine/network/port-publishing/).

Pinned Supabase2.120.0 also requires explicitly isolated legacy-backend state/network
selection and disabled repository migrations/seeds/roles inputs for base startup.
Its actual images, PostgreSQL compatibility, controlled synthetic fixture/role smoke,
guarded lifecycle, Entra/device and consumer checks remain ENV runtime obligations.
Neither this receipt nor the candidate builder templates prove those gates.

[Toolchain evidence and impact decisions](ENV_TOOLCHAIN_EVIDENCE.md) record the
executed checks and the remaining runtime blocker.

## Local Docker prerequisite before startup

`dev.py up --target <JSON> --run-id <prepared-UUID>` now validates the existing
preparation without creating or repairing it, rechecks ports, then reads only
`GET /version` from the fixed `/var/run/docker.sock`. Docker environment/context
settings cannot redirect this check. Stable Linux Docker Engine >=28.0.0 is required;
old daemons return `docker/docker_28_required`. Missing/denied sockets, malformed
responses and deadlines return safe failures. The request is bounded to five seconds
and 64KiB, with Content-Length framing; no custom/remote socket fallback is provided.

Even a supported daemon returns `up/runtime_adapter_unqualified`: no runtime startup
is implemented. Verify/stop/reset remain unqualified. These observations are not
network isolation or readiness evidence. Existing source-bound preparations and tool
receipts become stale after this dev.py change; use a fresh prepared/qualified UUID.
See [gate evidence and impacts](ENV_DOCKER_GATE_EVIDENCE.md).

## Run-local Supabase configuration

Preparation now writes and fsyncs protected `supabase/config.toml` before publishing
inventory. Repeat/up verify the exact config bytes, private modes and directory contents;
missing, altered or extra config/SQL/roles files refuse without repair. Interrupted runs
remain incomplete. Use a fresh UUID after this source change, then requalify tools.

The generated config disables CLI migrations/seeds and unused services, selects only
desktop callbacks and exposes no business schemas. It contains no secrets or provider
configuration. PostgreSQL17 is the selected CLI's default, pending actual image and
deployment-target qualification. Device TLS and run-owned loopback network delivery
remain separate; a config file cannot prove runtime binding or readiness.

Use the opt-in pinned CLI parser fixture command in
[configuration evidence](ENV_CONFIGURATION_EVIDENCE.md) with an already verified binary.
It uses a temporary synthetic Unix API, and never the real Docker daemon. Normal owner
regression remains `python3 -m unittest discover -s platform/deployment/tests -p 'test_*.py'`.
Run reserved-port suites and actual prepare/qualify sequentially.

## Python dependency qualification

The [ENV Python fixture](qualification/python/README.md) now resolves and executes the
approved Python package subset using the selected ordinary CPython3.15.0/uv0.13.1.
Its generated uv.lock and synthetic tests qualify isolated clean wheel installation,
native calls, loopback HTTP and offline SQL/library behavior. Use the fixture's explicit
clean-environment commands; it never supplies application/service requirements or locks.
Owner/runtime schemas, database/image compatibility and production readiness remain open.
See [qualification evidence](ENV_PYTHON_BASELINE_EVIDENCE.md).

## Frontend dependency qualification

The [ENV frontend fixture](../env-web-qualification/README.md) uses the approved exact
pins and the canonical root lock. Use its [disposable proof runner](qualification/web/README.md)
for explicit selected Node/npm, private configs/cache, clean installs, source/lock
provenance and affected-consumer checks. Never install it into the existing checkout
node_modules. Existing owner manifests and independent PtS locks retain ownership.
See [evidence and limitations](ENV_WEB_BASELINE_EVIDENCE.md), including the explicitly
reproduced Supabase/TS7 declaration conflict and separate browser/runtime gates.

## Planned base-image manifest identities

After an existing run has both protected preparation and a qualified tool receipt:

```sh
python3 platform/deployment/images.py qualify --target platform/deployment/environments/kdg-local.json --run-id <the-prepared-and-qualified-UUID>
```

The command verifies the unchanged preparation and calls the existing toolchain's
repeat qualifier before executing the selected Supabase CLI2.120.0. Missing receipts
or tools refuse; it never installs or repairs them. CLI `services --output json --agent no`
runs in a disposable private workdir with the prepared config, isolated state/cache,
no dotenv or `.temp` override and an explicit nonexistent Docker socket. The fresh
workdir begins with no `.temp`; afterward only the CLI-generated bounded `cli-latest`
marker is allowed there. Project links, service-version overrides, symlinks and config
mutation refuse. Generated private CLI telemetry/state is discarded with the workdir.
All remote
service fields must be empty. It cross-checks PostgreSQL/Auth/PostgREST tag values;
that CLI list omits Kong and is not a list of enabled or startup services.

[The closed selection](image-pins.json) records the pinned release commit and upstream
Dockerfile/start-gates/registry source URLs for PostgreSQL17.11.0.004, Kong2.8.1,
GoTruev2.197.0 and PostgRESTv16.4. Kong is selected from the pinned release sources.
The evidence policy selects legacy backend, slim off and no environment/temp overrides;
this is not an implemented startup policy. Only `public.ecr.aws/supabase/<basename>`
is admitted for evidence. Docker Hub and other mirrors cannot substitute for that
registry or be presumed byte-equivalent.

Collection reads manifest metadata only, over bounded direct HTTPS without redirects.
An anonymous auth challenge must use ECR's exact HTTPS token realm, service and `aws`
scope; the token request asks only for the selected repository's pull scope. Tokens
remain in memory and never enter output or evidence. The exact raw SHA256 is checked
against any supplied digest header and against every digest-addressed request. When
ECR omits a root digest header, collection additionally rereads the root by its computed
digest and requires identical bytes. Each selected index binds exactly one Linux/amd64
child's media type, size and digest. Config and layer descriptors are validated but
their blobs are never fetched. A tag resolving to a lone manifest refuses because its
platform cannot be established without a forbidden config-blob read.

Immutable evidence lives under ignored `.local/kdg-base-images/<UUID>/`: one raw
`services.json`, eight raw index/child manifests and a last-published `receipt.json`.
Directories are0700, files0600, owner-controlled, single-link and opened without
following links. The receipt binds target/prepared/config/tool-receipt hashes, selection
and local implementation/source hashes, manifest identities and explicit limits. The
selection records upstream source identity/URLs; it does not claim a separate retained
copy of upstream source bytes. Every network request has a20-second whole-process bound,
including DNS/TLS/headers/body; collection has a180-second deadline, manifests are at
most1MiB and token bodies64KiB. CLI capture has a30-second bound with1MiB total output;
the existing owner repeat check has180seconds. No real Docker daemon is contacted.

Repeating qualification rechecks retained raw bytes, index/child bindings and unchanged
source/tool inputs without registry requests, CLI services capture or file replacement.
Changed inputs, modes, links, extra files, concurrent writers and incomplete runs refuse.
The exclusive lock and receipt-last publication prevent partial collection from being
qualified. A failed fresh publication retains its lock, including failures after a
receipt has been linked. Receipt presence alone is not qualification: a retained lock
or pending file refuses every repeat. Failed lock-release synchronization restores
only an absent blocker; foreign receipts, pending files and locks are preserved.
An interruption can leave protected partial evidence; preserve it for
inspection and use a deliberately new prepared/qualified UUID. There is no cleanup,
adoption, automatic refresh or permission repair.

Success reports `base_identities_ready=true` and `runtime_ready=false`. It establishes
four planned base identities only. Actual enabled/startup/helper completeness, container
execution/libc, deployed PostgreSQL compatibility, adapter registry enforcement and all
runtime/provider/device gates remain unqualified. No image layers/config blobs, image
pulls, container startup, migrations, SQL or infrastructure/account changes occur.
See [base-image evidence and impact decisions](ENV_BASE_IMAGE_EVIDENCE.md) for exact
requirement/test traceability, public collection/repeat results and remaining gates.

## Guarded startup invocation and synthetic Docker boundary

`startup.py` constructs the next bounded ENV invocation from an already qualified
run's configuration and a validated run-owned network descriptor. It does not activate
`dev.py up`. The reusable constructor forces the legacy backend, non-slim images,
`public.ecr.aws`, an explicit private workdir and explicit network ID; ambient Docker,
Supabase, dotenv and linked-project settings cannot supply overrides.

The closed network descriptor has exactly `Name`, `Id`, `Driver`, `Scope`, `Internal`,
`Options`, `Labels` and `Containers`. It must use the prepared reserved network name,
a nonempty bounded ID, local bridge driver, `Internal=false`, no attached containers
and exactly `com.docker.network.bridge.host_binding_ipv4=127.0.0.1`. Its closed labels
are `io.agriplatform.env.owner=platform/deployment`, `io.agriplatform.env.target=<target>`,
`io.agriplatform.env.run=<UUID>` and `io.agriplatform.env.project=<reserved project>`.
The current proof supplies this descriptor synthetically: it is no evidence that a real
network exists or that Docker enforces its options. A future real adapter still needs
the Docker prerequisite and actual network ownership/isolation verification.

For the opt-in actual pinned CLI proof, use an existing unchanged preparation, tool
qualification and base-image qualification; the command refuses missing evidence:

```sh
python3 platform/deployment/tests/qualify_startup.py --target platform/deployment/environments/kdg-local.json --run-id <already-qualified-UUID>
```

It invokes the existing image owner's repeat qualifier before and after the proof.
That verification can take transient owner locks and run selected installed-tool
probes; it is not read-only. Missing/changed receipts refuse without installation,
registry refresh or repair. Preparation/tool sources remain unchanged. The image owner now exposes a repeat-only
consumer seam that cannot create a replacement run or collect registry metadata if
evidence disappears during verification. Its source hash changed; qualify a fresh
prepared/tool-qualified run rather than adopting an old image receipt.

The proof runs the selected Supabase binary in a new private workdir with generated
configuration and separate state/config/cache/temp/Docker directories. The root must
be owned by the current user with mode0700; a held directory descriptor binds its
identity throughout execution and replacement or permission changes refuse proof. Its Docker
endpoint does not exist and PATH contains only private `docker` and rejecting `podman`
Python fixtures, using an absolute Python shebang. No fixture code can dispatch a
real Docker executable. Only controlled inspect responses succeed. The exact run-owned
named-volume create receives a synthetic nonzero `volume already exists` refusal,
which the pinned CLI accepts as an existing-volume case; no volume is created. First
PostgreSQL `create` is validated and refused, retaining only selected safe image,
name, network, publishing and mount facts. After verifying the private CLI parent
identity and isolated process group, a pidfd signal stops it before rollback commands.
Child stdout/stderr, complete argv,
environment values and generated SQL are discarded. The CLI process group has a
30-second bound and 1MiB combined output limit. Each private fixture installs a Linux
parent-death signal before importing the owner modules or doing fixture work, and has
a five-second lifetime bound, including when the CLI creates a separate child session.
Event state is opened nonblocking without following links, must be regular, owned,
mode0600 and single-link, and retains its path identity through reads/writes. Exclusive
nonblocking lock acquisition has a half-second deadline. Fixture input/state, command
count and command argument sizes are bounded. Source identities bind startup, its
opt-in entrypoint, imported owner implementations/pins and preparation sources before
and after execution; source changes refuse proof. Temporary files are discarded on exit.

Negative controls select `--control invalid-network`, `--control contaminated-workdir`
or `--control reject-command`. The first two are adapter preflight controls and do not
start the pinned CLI. The third invokes the private Docker fixture directly, requires
the exact expected unexpected-command rejection event, and reports
`expected_command_rejected`; another failure does not pass that control. Each returns
nonzero safe JSON with `runtime_ready=false`. Synthetic unit coverage separately proves
a CLI process issuing an unexpected Docker command receives refusal without a Podman
fallback. These controls do not claim an actual pinned-CLI unexpected-command path.
The private workdir never includes repository migrations, seeds, roles or dotenv.
The pinned CLI still publishes PostgreSQL as `<host port>:5432`, so validated network
default loopback publishing remains an essential future runtime guard.

This synthetic proof follows the existing-volume path only. Positive evidence requires
the pinned path’s nine observations: missing-container inspect, exactly one inspect
for each of the four selected images (in any concurrent order), volume inspect, network
inspect, duplicate-volume create refusal and the refused PostgreSQL create. Missing,
duplicate or reordered prerequisites refuse proof. The selected PostgreSQL tag is
checked at its create boundary. The retained facts cover the exact generated config
bytes, the Supabase directory’s allowed files and absence of host bind mounts. The
shell command’s SQL content is unqualified; it is neither logged nor hashed. These
checks do not establish a broad runtime SQL-input policy. This does not enforce
its manifest digest or execute its bytes; no container, secret-copy, SQL, migration,
account or grant action occurs. Other startup/helper completeness, image/libc,
deployment PostgreSQL compatibility and runtime/provider/device readiness remain open.
The [startup evidence](ENV_STARTUP_INVOCATION_EVIDENCE.md) records actual proof results,
requirement traceability and the five impact decisions.

### Run-owned network acquisition proof

`networks.py` now acquires or verifies the prepared run's bridge through the fixed
local Docker Unix socket, with a stable Linux Docker 28 prerequisite. This adapter
is deliberately **not activated by `dev.py up`**. It constructs startup arguments
only; successful synthetic proof reports `runtime_ready=false`. It neither starts
the selected CLI nor establishes kernel isolation or application readiness.

After a fresh protected `prepare` against the current sources, run:

```bash
python3 platform/deployment/tests/qualify_networks.py --target platform/deployment/environments/kdg-local.json --run-id <prepared UUID>
```

The opt-in qualifier injects its own private Unix socket internally. It has no
socket/host/context command-line option and never contacts the real Docker daemon.
Production acquisition ignores ambient Docker variables and uses only
`/var/run/docker.sock`. The transport permits `GET /version`, versioned v1.48 network
inspection and `POST /v1.48/networks/create`; request and response sizes, framing,
per-operation total deadline and protected same-run lock wait are bounded.

The create request selects the reserved name, exact owner/target/run/project labels,
a local bridge, IPv4 enabled, IPv6/ingress/attachable/internal/config-only disabled
and exactly `com.docker.network.bridge.host_binding_ipv4=127.0.0.1`. It omits
`ConfigFrom`, because an empty reference still selects Docker's config-from branch.
Actual inspection must additionally show an empty `ConfigFrom.Network`, no attached
containers and a canonical full lowercase 64-hex network ID. Only validated fields
enter the existing closed startup descriptor. The adapter verifies returned create
IDs, conflict winners and immutable-ID/name continuity immediately before constructing
startup arguments. It refuses foreign, unsafe or attached networks without repair.

`--control existing` proves reuse with no POST; `--control conflict` proves verified
winner adoption. Negative controls are `foreign`, `unsafe-options`, `ipv6`, `attached`,
`lost-response`, `replacement`, `old-daemon`, `malformed`, `oversized`, `slow`,
`daemon-error` and `missing-preparation`. Each must return nonzero with its documented
safe code; use an unprepared UUID for `missing-preparation`. No daemon body appears
in output. Synthetic source/path/lock replacement and competing-call controls live
in `test_networks.py`. A lost or timed-out create is never blindly retried or deleted;
a later explicit call inspects by the reserved name first. Persistent empty protected
`.network-<UUID>.lock` files sit beside run directories to preserve flock inode
identity; preparations and immutable image/tool receipts are never repaired.

Source-bound preparations include `networks.py`, `startup.py` and the public qualifier;
source changes require fresh preparation. Evidence and requirement-to-test links are
in [ENV_RUN_NETWORK_EVIDENCE.md](ENV_RUN_NETWORK_EVIDENCE.md). Scaffold impact is this
ENV adapter only; shared UI has no impact; root agent rules suffice; this runbook and
proof evidence are updated; accepted ADRs remain unchanged.


## Immutable first-create selection

The public startup proof now requires an image selection plan from the existing image
owner's retained-evidence verification. Exactly four approved tagged references map
to their own repository's distinct Linux/amd64 child manifest digests. The plan uses
neither index nor config digests. No unqualified positive path exists. Prepare and
qualify a fresh run after these source changes; missing or stale evidence cannot
trigger collection, installation, adoption or repair through this proof.

At the private executable boundary, `immutable_first_create` validates the original
PostgreSQL create, constructs a new argument list by replacing only its image operand,
and has no dispatch capability. This internal constructor accepts only selection plans
already verified by the image owner; its structural checks do not establish manifest
provenance. The full public qualification path owns that verification and its rechecks.
The fixture independently validates the constructed
request before refusing creation. Safe facts record `original_image`, selected `image`,
`immutable_selection_proven=true` and `create_refused=true`; argv, environment values
and SQL are never retained. Protected receipt/manifest bytes and filesystem identities,
preparation, tools, source and workdir guards are checked around the proof.

The existing public qualifier command remains unchanged. Its additional negative
control `--control invalid-selection-plan` removes one approved mapping and must fail
before CLI execution with `invalid_selection_plan`. Existing negative controls retain
their exact refusal codes and bounded process cleanup.

Selection proof is separate from execution enforcement: `runtime_ready=false`,
`container_executed=false` and `limits.digest_enforcement=false` remain mandatory.
The CLI still requests tags natively; the constructor transforms only its first
PostgreSQL request. Other services/helpers and real digest-bound execution remain
unqualified. No real Docker mutation, layers, containers, SQL or migrations occur.
The [immutable-create evidence](ENV_IMMUTABLE_CREATE_EVIDENCE.md) records verification
and impact decisions; the earlier startup evidence remains historical.

## Complete first-create profile

The private wrapper now passes one explicit in-memory environment snapshot alongside
argv. `create_profile.py` checks the complete ordered Linux/PG17 profile for CLI2.120.0:
all flags/operands, exact public bootstrap bytes, four key-only container env names
and their public synthetic values, and private Docker client routing. Missing, extra,
duplicate, reordered or changed inputs refuse before a positive create event. Other
inherited process variables do not become container inputs. Inputs are copied for
transformation; caller/transform mutation and changes outside the image operand refuse.
Both the original and transformed requests must match the complete profile.

[Profile authority](fixtures/supabase-pg17-profile.md) identifies pinned upstream
sources and the independently assembled public bootstrap fixture. It is source-bound
with the validator in prepared evidence; new qualification requires a fresh run.
No runtime argv, environment values, SQL, or hashes of rejected content are retained.
Safe facts add `complete_create_profile_proven=true`.

Public negative controls `invalid-create-script`, `invalid-create-environment` and
`invalid-create-routing` mutate only synthetic input at the private executable boundary
and must return `expected_create_profile_rejected` after exact prerequisite events and
one redacted rejection. The pinned CLI is stopped at that refusal. Existing controls
and positive qualification remain available through `tests/qualify_startup.py`.

This proves source/profile conformity and custody through refused dispatch. It does
not prove bootstrap semantic safety, secret-file delivery, image/resource continuity
during execution, complete startup or runtime readiness. `dev.py up` remains gated.
See [first-create profile evidence](ENV_FIRST_CREATE_PROFILE_EVIDENCE.md) for commands,
results and requirement traceability. Scaffold impact: reusable ENV boundary only;
shared UI and agent context: none; documentation: this runbook/authority and evidence;
ADR: existing constraints apply, no new decision or accepted ADR change.

## Run-owned database volume qualification

Preparation reserves `supabase_db_<project>`, matching the pinned CLI's PostgreSQL
volume/mount name. The bounded `volumes.py` adapter inspects that exact name after
current preparation/source checks and the Linux Docker28 prerequisite. Only a404
allows one create POST, followed by independent reinspection. Existing volumes need
no POST. A201 response can represent an existing volume, so output reports
`post_attempted` and the verified profile; it never claims newly created storage.

Run the public private-daemon proof with a fresh prepared run:

```sh
python3 platform/deployment/tests/qualify_volumes.py --target platform/deployment/environments/kdg-local.json --run-id <prepared-UUID>
```

`--control existing` and `--control racing-owned` are positive controls. Negative
controls are `foreign`, `racing-foreign`, `unsafe-options`, `cluster`, `changed`,
`lost-response`, `old-daemon`, `malformed`, `oversized`, `slow`, `daemon-error`, and
`missing-preparation` (use an unprepared UUID). They return nonzero safe codes.
There is no public daemon endpoint override; all qualifier traffic uses its own
private synthetic Unix daemon. The actual adapter fixes `/var/run/docker.sock` and
ignores ambient Docker endpoint variables. Transport adds only v1.48 volume
inspection and creation routes to the existing bounded HTTP mechanism.

The descriptor requires exact name, local driver/scope, the four ENV ownership
labels plus both Supabase/Compose project labels, and explicit null or empty options.
Cluster-volume metadata is refused. Optional CreatedAt is bounded and retained internally
for observation continuity, but omitted from public diagnostics because it is daemon
text; Mountpoint is never followed or published. Full selected
observations must agree before handoff. Name-addressed volume inspection cannot
establish immutable identity, empty/unused/unattached storage or kernel isolation.
Foreign collisions and uncertain POST responses fail without retries, repair or
delete; a later explicit attempt begins with inspection.

Both resource adapters use the existing protected `.network-<UUID>.lock` in the run
parent. This is intentionally the same bounded serialization lock, despite its
historical network name. Preparation/source/run/lock evidence is checked before
mutation and handoff. Old preparations and immutable receipts are preserved; source
changes require a fresh run.

The internal `_handoff` callback is only for trusted immediate nonblocking construction.
The total acquisition deadline is checked around it; it cannot preempt arbitrary Python
or safely bound runtime execution. Do not perform startup or external waits in it.

The public pinned-CLI startup qualifier acquires a synthetic volume through this
adapter and supplies its complete descriptor to the existing startup fixture. Volume
acquisition releases its lock and closes the private daemon before this separate process
proof: the qualifier proves descriptor transfer, not continuous locked observations
through startup. Volume
inspection and PostgreSQL creation validate that descriptor and exact mount identity;
volume creation and the first container create remain refused. `dev.py up` stays
gated, `runtime_ready=false`, and no real Docker mutation, pull, SQL or migration is
part of these proofs. See [ENV_RUN_VOLUME_EVIDENCE.md](ENV_RUN_VOLUME_EVIDENCE.md)
for results and impact decisions.

## Bounded daemon connection continuity

Each network, volume and image acquisition uses one Unix HTTP connection for its
version check and all resource observations or create requests. The connection opens
only after preparation validation. Replacing the socket pathname cannot redirect an
already-connected acquisition. Failure closes the session permanently; there is no
reconnect, replay, redirect, pipelining or chunked transfer support. An uncertain
create result refuses without retry. Existing route/method allowlists, 16KiB ordinary request
and 64KiB response bounds (with the bounded binary archive exception below),
strict Content-Length framing, resource ownership checks,
run locks and source/evidence checks remain binding. HTTP/1.0, Connection: close,
malformed framing and extra bytes observed during parsing or an idle check refuse
a persistent session. Idle checks observe readiness without waiting: bytes or EOF
arriving after the final check are not guaranteed to be detected. A fully framed
success reports the completed exchange, not future peer liveness. Each session has
one sequential caller; concurrent use is unsupported.

The same total daemon deadline covers every exchange; it never resets per request.
All exits close the descriptor, including evidence refusal and callback exceptions.
Image-owner tool probes run before opening and after closing the daemon session,
under their own bounds. The one-shot read-only Docker prerequisite retains its
existing Connection: close behavior and uses the same parser and route checks.

Private qualifier servers count accepted connections independently and retain their
exact request-sequence oracles. Adapter and session tests cover socket replacement,
disconnection before/after exchanges, uncertain mutation without replay, malformed
second responses, total deadlines and descriptor cleanup. These are isolated
synthetic proofs; they do not qualify a real daemon's behavior.

Standalone connection continuity is bounded to one adapter acquisition. The combined
resource constructor below extends that scope without executing startup, reserving
resources, establishing volume freshness/exclusivity, proving bootstrap safety or
granting runtime readiness. Real `up` remains
refused before activation. No Docker mutation, pull, container, SQL, deployment or
application activation is enabled by this change.

## Daemon-local image identity qualification

`daemon_images.py` verifies the four selected images using current protected preparation,
tool and image-owner evidence. The image owner derives a closed child-reference/config
plan from retained manifest bytes; no config blob or layer download is needed. Existing
receipts and the tag-to-child selection plan are unchanged. Source changes require a
fresh run UUID and fresh qualification; never repair an old receipt.

After owner repeat qualification, the adapter checks Linux Docker28 and inspects each
exact child reference, then each exact config ID through the existing v1.48 transport.
Every response must report the retained config digest as `Id`, `Os=linux`,
`Architecture=amd64` and absent/empty `Variant`. RepoTags and RepoDigests have no authority;
missing or index-only repository digests are accepted when identity/platform match.
Only Id/Os/Architecture are transferred. Config, environment, paths, timestamps and
daemon error text are discarded. Missing images refuse without pull, import, tagging,
repair, retries or deletion.

```sh
python3 platform/deployment/tests/qualify_daemon_images.py --target platform/deployment/environments/kdg-local.json --run-id <qualified-UUID>
```

This command always starts a private synthetic Unix daemon. `--control index-only` is
also positive. Negative controls: `missing`, `wrong-id`, `wrong-platform`, `variant`,
`replacement`, `old-daemon`, `malformed`, `oversized`, `slow`, `daemon-error`. Every
negative control returns a nonzero safe code. There is no public real-daemon command
or endpoint override. The internal adapter defaults to the fixed local Docker socket.

The daemon phase has one five-second total deadline and the existing 64KiB HTTP
response bound. Oversized real image metadata remains a qualification failure. Owner
tool revalidation runs outside that deadline with its own bounded probes. The existing
same-run lock covers qualification and observations; evidence identity, bytes and
selected observations are checked before successful return. Every call observes afresh.

The separate public startup proof acquires these observations and forwards them through
both the qualifier and fixture installation to the pinned CLI. Missing or foreign
descriptors refuse before image/create events. First PostgreSQL create remains refused.
The observation lock is released before this separate process proof; it does not prove
execution enforcement, connection continuity into that later startup process, independently hashed daemon
bytes, complete startup helpers or runtime readiness. `runtime_ready=false`, no containers,
SQL, migrations or dependent application activation remain binding. See
[ENV_DAEMON_IMAGE_EVIDENCE.md](ENV_DAEMON_IMAGE_EVIDENCE.md) for results and impacts.

## Synthetic PostgreSQL create-to-start qualification

The existing startup qualifier adds `--control lifecycle-positive`. It validates the
complete pinned first-create profile, returns one fixed synthetic container identifier,
validates the subsequent exact `docker cp - <identifier>:/` transfer in memory, then
refuses the first `docker start <identifier>`. No container is created and no secret
is installed. The default `positive` control still refuses create.

```sh
python3 platform/deployment/tests/qualify_startup.py --target platform/deployment/environments/kdg-local.json --run-id <fresh-qualified-UUID> --control lifecycle-positive
```

The new negative controls are `invalid-lifecycle-target`, `invalid-lifecycle-archive`
and `invalid-lifecycle-order`. Each first validates the original pinned request and
archive before injecting its defect. An invalid original cannot qualify a negative
control. The prior eight controls retain their behavior. Run process qualification
outside a restrictive execution sandbox: this pinned executable uses socketpair stdin,
whose transfer may be denied inside that sandbox. Empty input always fails validation.

The archive must match the observed plain USTAR format: exactly 10240 bytes, one regular
member at the pinned root-key path, mode 0644, uid/gid 0, the public local default content,
448 zero member-padding bytes, and 9216 zero bytes after the padded data block. Links, extra members, extended headers, compression, traversal,
malformed fields, truncation and trailing data refuse. Reading is bounded to one second,
inside the unchanged five-second wrapper deadline. Nothing extracts or persists the
archive, logs its contents/member names, or hashes its secret input. Selected safe facts
are the only events. Terminal refusal kills only the proven pinned parent to prevent
cleanup execution. Changed sources/evidence require a fresh qualification.

This proof establishes synthetic sequencing only. `dev.py up` remains gated and
`runtime_ready=false`; bootstrap/secret policy, helper inventory, daemon/resource
session continuity, volume reuse, recovery/health, deployment PostgreSQL compatibility
and later owner migrations remain real runtime gates. P1/SERVICE/provider/device
proof is separate. See [ENV_CREATE_TO_START_EVIDENCE.md](ENV_CREATE_TO_START_EVIDENCE.md)
for qualification results and the five impact decisions.

## Combined run-resource acquisition

`resources.acquire` composes the existing network, volume and daemon-image owners under
one persistent run lock and one Docker connection/version check. Current protected
preparation, tool receipt, image receipt, retained manifests and source identities are
required before daemon work. Owner executable probes run before opening and after
closing the connection, with their own bounds. The daemon phase has one total
five-second deadline across every phase and the immediate constructor handoff.

The ordered daemon checks are: version; four exact child image references and four
config identities; bridge acquisition; volume acquisition; repeat child/config
observations; bridge ID/name/ID; volume. Every request rechecks current protected
evidence. Before each POST and the optional constructor, these checks still hold.
The constructor receives joint `network`, `volume`, `images`, `post_attempted` (volume)
and `runtime_ready=false`. Fresh startup uses the distinct `resources.invocation`
path described below; it leaves the volume absent for the CLI probe. Neither path
executes startup. Final source/evidence and
owner postchecks must succeed before returning a result. Callback failure closes the
connection and releases the lock. The trusted callback must be immediate and nonblocking;
budget checks cannot preempt arbitrary Python.

```sh
python3 platform/deployment/tests/qualify_resources.py --target platform/deployment/environments/kdg-local.json --run-id <fresh-qualified-UUID>
python3 -m unittest discover -s platform/deployment/tests -p 'test_resources.py'
```

The public qualifier always uses an isolated private synthetic Unix daemon. `--control
existing` is also positive. Negative controls are `image-missing`, `image-foreign`,
`network-foreign`, `network-replaced`, `volume-foreign`, `volume-changed`,
`lost-network-response`, `lost-volume-response`, `old-daemon`, `malformed` and `slow`.
The independent oracle checks exact ordered bodies, one connection/version and the
specific terminal request for each negative control. There is no configurable endpoint,
real Docker mutation, image pull, container, SQL or owner migration. Changed sources
require fresh preparation and fresh tool/image qualification on a new run UUID.

A connected acquisition constructs a candidate startup handoff. It does not reserve
resources, establish volume freshness or exclusivity, qualify bootstrap/secret policy,
prove continuous container execution or promise future peer liveness. Each standalone
adapter retains its existing contract and reuses the extracted owner algorithm.
`dev.py up` stays gated and `runtime_ready=false`. This extends the existing ENV scaffold;
shared UI and agent context need no change, owner documentation is updated, and accepted
ADRs remain unchanged.

## Run-volume current-use admission

Standalone volume acquisition now checks container references after its final selected
volume inspection. Joint acquisition repeats that check after its final joint volume
inspection. Each check uses the existing guarded connection, run lock and total daemon
deadline. The only admitted list route is Docker API1.48 `GET /containers/json` with
`all=true` and exactly one `volume` filter containing the exact reserved run-volume
name. This includes stopped containers; a destination-name match may conservatively
refuse too. Only an empty JSON array admits handoff. Any reference, including one from
a container with matching ownership labels, refuses with `volume_in_use`. A non200
response refuses with `volume_use_failed`; invalid JSON types or framing retain
`docker_response_invalid`. Container details never enter public output or errors.
Other routes still require object responses. Standalone handoff also rechecks observable
EOF/unsolicited bytes and the deadline immediately before and after construction.

The existing private synthetic qualifiers expose `use-running`, `use-stopped`,
`use-same-owner`, `use-object`, `use-null`, `use-scalar`, `use-error`, `use-oversized`,
`use-truncated`, `use-eof` and `use-malformed`. The joint qualifier also exposes `use-late`: the first
check returns no references, while the final joint check refuses before construction.
Each negative control must return nonzero with safe stage/code output. Commands:

```sh
python3 platform/deployment/tests/qualify_volumes.py --target platform/deployment/environments/kdg-local.json --run-id <fresh-prepared-UUID> --control use-stopped
python3 platform/deployment/tests/qualify_resources.py --target platform/deployment/environments/kdg-local.json --run-id <fresh-qualified-UUID> --control use-late
python3 -m unittest discover -s platform/deployment/tests -p 'test_volumes.py'
python3 -m unittest discover -s platform/deployment/tests -p 'test_resources.py'
python3 -m unittest discover -s platform/deployment/tests -p 'test_docker_session.py'
```

These observations establish current metadata admission only. An existing matching
unused volume remains admissible; storage contents and initialization are unproven.
The checks do not reserve a volume, guarantee exclusive use, prove immutable identity,
or qualify execution. A reference can appear after observation. No cleanup, replay,
reconnect or real Docker operation is enabled; `runtime_ready=false` and the existing
`up` refusal remain. Changed source bindings require fresh preparation and fresh
owner tool/image qualification. Scaffold impact is this bounded ENV admission;
shared UI and agent context need no change, documentation is this runbook and delivery
evidence, and accepted ADRs remain unchanged.

## Closed PostgreSQL create-request construction

The existing refused-create boundary now constructs and validates a detached in-memory
Docker API1.48 request from the exact pinned PostgreSQL profile and selected child
image. It includes only the four approved public synthetic environment inputs, exact
bootstrap command, run labels/volume/network, health/restart settings and aliases.
The constrained ENV request explicitly selects Linux/amd64 and publishes PostgreSQL
on127.0.0.1; these tighten the CLI profile rather than reproduce every CLI default.
Every nested key, value and primitive type is checked before safe
`create_request_proven: true` evidence is recorded. Ambient variables are excluded;
request body/environment/bootstrap are never saved or hashed as runtime evidence.

```sh
python3 platform/deployment/tests/qualify_startup.py --target platform/deployment/environments/kdg-local.json --run-id <fresh-qualified-UUID> --control positive
python3 platform/deployment/tests/qualify_startup.py --target platform/deployment/environments/kdg-local.json --run-id <fresh-qualified-UUID> --control invalid-create-request
python3 -m unittest discover -s platform/deployment/tests -p 'test_create_profile.py'
```

The negative control validates the baseline, corrupts loopback binding and proves safe
refusal. Existing source-profile and lifecycle controls remain available. The real
Docker transport still rejects container-create requests before opening a socket.
No container, SQL or secret provisioning is enabled; `runtime_ready=false`.

This is execution-input construction, not bootstrap semantic/secret, freshness/reuse
or runtime qualification. The pinned CLI checks volume existence before fresh setup;
a pre-acquired volume may skip that setup. Fresh constructor ordering and the private
CLI branch are now proved below; live creation/ownership and setup execution remain open.
[Profile mapping](fixtures/supabase-pg17-profile.md#closed-postgresql-create-request)
and [delivery evidence](ENV_POSTGRES_CREATE_REQUEST_EVIDENCE.md) record the authorities,
limits, requirement/test traceability and all five impact decisions.

## Fresh-start volume admission

`resources.invocation` constructs the initial startup command under the existing run
lock, qualified evidence, one daemon connection and five-second budget. It checks
version/images and exact volume absence before bridge acquisition, then rechecks
images, bridge identity and volume absence before construction. It never creates the
volume. Any existing volume, including a foreign one, refuses
`volume_reuse_unsupported`; ambiguous inspection refuses `volume_inspection_failed`.
Late appearance preserves the acquired bridge and refuses handoff without cleanup or
replay. Custody, idle-connection, budget and owner postchecks remain required.
`resources.acquire` retains its metadata acquisition contract.

The existing private startup qualifier's fresh mode skips volume pre-acquisition and
keeps `planned_volume` separate from observed metadata. The pinned CLI receives a
truthful synthetic missing-volume response, followed by exact volume-create
acknowledgement, validated immutable PostgreSQL request, in-memory root-key copy and
refused first start. The CLI's two labels do not establish the planned ENV six-label
ownership profile. This proves branch/order only: no reservation, live creation,
initialized contents, setup SQL, bootstrap-secret safety or runtime readiness.
Execution-time absence checks and guarded volume ownership/creation remain open.

```sh
python3 platform/deployment/tests/qualify_resources.py --target platform/deployment/environments/kdg-local.json --run-id <fresh-qualified-UUID> --control fresh
python3 platform/deployment/tests/qualify_startup.py --target platform/deployment/environments/kdg-local.json --run-id <fresh-qualified-UUID> --control fresh-lifecycle-positive
```

Resource controls `fresh-existing`, `fresh-foreign`, `fresh-error` and `fresh-late`
prove bounded refusals. Startup controls `fresh-existing`, `fresh-racing` and
`fresh-invalid-lifecycle-{target,archive,order}` prove refusal before later phases.
Existing positive/acquisition controls remain available. All peers and acknowledgements
are private synthetic fixtures; no real resource or container is created.
See [fresh-start evidence](ENV_FRESH_START_EVIDENCE.md) for commands, results,
requirement-to-test traceability and scaffold/UI/context/documentation/ADR impacts.

## Guarded CLI volume-owner integration

The fresh pinned-CLI qualifier can now retain the existing resource guard through
its volume probe/create boundary. `resources.fresh_session` retains the run lock,
qualified evidence, one connection/version and total five-second daemon budget.
Constructor-only `resources.invocation` retains its existing absence-only contract.
The CLI's exact two-label create operands are admitted to the existing owner, which
sends its six-label ENV request, validates acknowledgement and reinspection, refuses
current container references and repeats image/network/volume/use observations before
acknowledgement and after the CLI terminates. Existing metadata acquisition keeps its
adoption behavior; fresh creation refuses an already-present volume.

A closed private fixture handoff services only the missing probe and exact create
phase. The generated private socket, peer PID/UID, in-memory capability, source/root,
fixture/wrapper/config bytes and total deadline are checked. Per-request custody also
covers changes between the outer handoff check and volume POST. Framing/output are
bounded, partial requests use remaining total time, and terminal failure kills the
proven process group. Capability bytes are never persisted or hashed. Only the
private disposable workdir is removed after the guard's final checks.

```sh
python3 platform/deployment/tests/qualify_startup.py --target platform/deployment/environments/kdg-local.json --run-id <fresh-qualified-UUID> --control guarded-fresh
```

This public qualifier always creates a private synthetic Docker peer; it accepts no
caller daemon endpoint. Its independent positive oracle contains70 requests on one
connection. Negative controls use `guarded-` plus `existing`, `foreign`,
`lost-response`, `truncated-response`, `bad-ack`, `bad-descriptor`, `changed`, `use`,
`late-image`, `late-network`, `late-volume` or `late-use`, with exact terminal requests.
They terminate without replay, adoption, cleanup or a returned readiness claim.

The observed selected volume descriptor is separate from the planned profile and
omits unsafe/nonessential metadata. These are synthetic daemon observations: Docker's
idempotent create,201 or labels cannot prove immutable identity, exclusive reservation,
empty contents or initialization. PostgreSQL create/copy remains synthetic and first
start refuses; no actual container or setup SQL is executed. Bootstrap/secret safety,
initialized reuse, live lifecycle/health/recovery, full `up` integration and P1/SERVICE
consuming scaffold proof remain open. See [integration evidence](ENV_GUARDED_CLI_VOLUME_EVIDENCE.md)
for exact results, traceability and all five impact decisions.

The bounded [Auth catalog qualifier](ENV_AUTH_CATALOG_EVIDENCE.md) adds independent
source-defined pre/post SQL predicates around that migration job. Reviewed-source
610 deployment tests and109 rollback-only corruption cases pass; all review patches
are verified in the evidence. Public runtime remains unqualified. After fresh prerequisite qualification:

```sh
python3 platform/deployment/tests/qualify_startup.py --target platform/deployment/environments/kdg-local.json --run-id <fresh-qualified-UUID> --control pinned-cli-postgres-auth-catalog
```

It requires a fresh precondition, exact82-version Auth ledger (seven publisher bootstrap markers plus75 current versions) and selected real tables/
latest column on the same healthy owned PG instance, then normal cleanup. Closed
read-only queries have bounded waits and no attached output. Existing execution-only
control semantics remain. This neither resumes CLI setup nor proves full Auth service,
independent CLI session identity or application-owner readiness. Preserve refused
attempts; use a fresh source-qualified UUID after source/profile changes.

The bounded [CLI database backend qualifier](ENV_CLI_DB_BACKEND_EVIDENCE.md) adds
independent presence/departure observations around the same CLI termination, before
the existing Auth catalog/job checks. The bounded qualifier and27 SQL cases are
verified; public runtime remains unqualified. After fresh source-bound prerequisite qualification:

```sh
python3 platform/deployment/tests/qualify_startup.py --target platform/deployment/environments/kdg-local.json --run-id <fresh-qualified-UUID> --control pinned-cli-postgres-cli-db-backend
```

It requires one expected external backend with the CLI alive, then zero after its
single termination/reap. Observer visibility, same-PG custody and bounded read-only
SQL checks are mandatory. Facts do not identify an OS process/backend pair or prove
a password method or continuing CLI session; later CLI setup stays gated. Test-only
synthetic activity fixtures are internal to existing qualification tooling and do not
provide a public arbitrary-SQL command. All other runtime/owner/scaffold gates remain.

### Reproduce backend qualification

Use the existing [Linux Docker prerequisite](#local-docker-prerequisite-before-startup)
and exact selected cached images; missing images refuse rather than being pulled by
this qualifier. Replace the UUID below with a fresh canonical lowercase UUID. The
target's approved workspace root must match this checkout. From the repository root,
run the existing [preparation](#current-env-delivery-status),
[toolchain](#pinned-toolchain-qualification) and
[image-manifest](#planned-base-image-manifest-identities) owners in order:

```sh
KDG_RUN_ID='<fresh-canonical-lowercase-UUID>'
python3 platform/deployment/dev.py prepare --target platform/deployment/environments/kdg-local.json --run-id "$KDG_RUN_ID"
python3 platform/deployment/toolchain.py qualify --target platform/deployment/environments/kdg-local.json --run-id "$KDG_RUN_ID"
python3 platform/deployment/images.py qualify --target platform/deployment/environments/kdg-local.json --run-id "$KDG_RUN_ID"
python3 platform/deployment/tests/qualify_startup.py --target platform/deployment/environments/kdg-local.json --run-id "$KDG_RUN_ID" --control pinned-cli-postgres-cli-db-backend
```

The following self-contained invocation uses only tracked functions in the existing
qualification owner; it does not require a private verifier script. Select `matrix`
for the 24 fixed-row cases, `late-first` for late initial zero, `timely` for occupied
then timely zero, or `late-next` for occupied then late zero. These four choices prove
27 SQL cases. Each successful invocation disposes its own resources normally. On
refusal preserve diagnostics/resources and follow the custody rules above; do not
blindly retry an uncertain resource name. Source/profile changes require fresh
preparation and qualification. No production target or real data is involved.

```sh
KDG_SQL_CASE=matrix
python3 - "$KDG_RUN_ID" "$KDG_SQL_CASE" <<'PY'
import contextlib
import io
import json
import sys
from unittest.mock import patch

sys.path.insert(0, 'platform/deployment')
sys.path.insert(0, 'platform/deployment/tests')
import startup_lifecycle
import qualify_startup

run_id, case = sys.argv[1:]
if case not in ('matrix', 'late-first', 'timely', 'late-next'):
    raise SystemExit('Choose one documented fixed SQL case')
original = startup_lifecycle.cli_db_backend_exec

def fixed_fixture(mode):
    if case == 'matrix':
        return qualify_startup._cli_db_backend_semantic_exec(mode)[0]
    if mode == 'present':
        return original(mode)
    if case == 'late-first':
        return qualify_startup._cli_db_backend_late_zero_exec()
    return qualify_startup._cli_db_backend_transition_exec(case == 'late-next')

output = io.StringIO()
with patch.object(startup_lifecycle, 'cli_db_backend_exec', side_effect=fixed_fixture):
    with contextlib.redirect_stdout(output):
        code = qualify_startup.main([
            '--target', 'platform/deployment/environments/kdg-local.json',
            '--run-id', run_id, '--control', 'pinned-cli-postgres-cli-db-backend'])
result = json.loads(output.getvalue())
result.update(synthetic_activity_rows=True, semantic_case=case,
              semantic_cases_verified=(24 if case == 'matrix' else 1) if code == 0 else 0)
print(json.dumps(result, sort_keys=True))
raise SystemExit(code)
PY
```

These fixtures preserve the production conditions, deadlines and exits. The two
transition cases count exactly two fixed-input observations with a transaction-local
setting, discarded by rollback/exit. On rejection they carry only that ordinal in
server-local exception detail so subtransaction rollback cannot erase the oracle.
No role, table or business data changes. The normal qualifier above independently
observes actual backend lifetime; synthetic SQL results are explicitly labelled.

## Safe Docker failure diagnostics

The bounded [diagnostic capture item](ENV_DOCKER_FAILURE_DIAGNOSTICS_EVIDENCE.md)
is implemented and verified. Existing `dev.py` and startup qualification errors may add a
`docker_failure` object to the original stage/code/runtime_ready=false result:

```json
{"schema_version":1,"operation":"container_create","phase":"receive","elapsed_ms":5000}
```

The object identifies the attempted operation category and transport phase at failure.
elapsed_ms measures that exchange with a monotonic clock; it is a nonnegative integer,
capped at2147483647. Phase is validate, connect, idle_before, send, receive, idle_after
or budget_after. Categorization follows complete request validation; rejected requests
use unvalidated. Only fixed operation categories appear, never routes, resource IDs/
names, socket paths, payloads, credentials, hashes or exception messages.

The formatter validates fields again and omits malformed metadata. When cleanup wraps
an earlier exchange error, the bounded cycle-safe exception-chain walk retains its
earliest valid diagnostic while preserving the outer stage/code. Reuse of a poisoned
session retains its first observation. Ordinary errors without this metadata and
successful output retain their existing shape.

Only failures observed inside DockerSession.exchange carry a new observation.
Owner checks and deadlines outside an exchange may have no docker_failure; no last
successful request is presented as the cause of an unrelated later failure. Excessive
exception ancestry is omitted when the bounded walk cannot establish attribution.

This is selected diagnostic evidence, not proof that a request was sent/completed,
that Docker cancelled a mutation, or that resources are safe to remove. Existing
deadlines, no reconnect/replay, one-shot cleanup and lost-custody preservation remain.
The two historical backend timeouts remain unexplained; a later pass or this code
change does not establish their causes. Source changes require fresh qualification;
preserve previous receipts and uncertain resources. Public runtime remains gated.

## Socket-close error handling

The [close-error preservation increment](ENV_DOCKER_CLOSE_EVIDENCE.md) uses the existing
DockerSession owner. It detaches the stream and permanently invalidates the session
before one close attempt. If close raises OSError while an exchange or context body
is already failing, that active error and its original selected diagnostic remain
authoritative. Active cancellation is preserved. Explicit close or ordinary exit
without a prior error still raises its close error; non-OSError close exceptions
retain propagation. Repeated close/exit does not retry, reconnect or replay.

Invalidated means unusable, not confirmed kernel closure or Docker-resource cleanup.
A close error creates no cleanup/adoption authority and no successful lifecycle claim.
Existing stage/code/diagnostic schema, privacy and deadlines stay unchanged. Fresh
source-bound preparation/qualification is needed before future actual execution;
previous receipts and uncertain resources remain preserved. Runtime stays gated.

## Post-Auth default-privilege request boundary

Existing auth-catalog and cli-db-backend qualification now construct the next
source-derived API default-privilege request and prove the pure transport validator
refuses it. Success includes api_default_privileges_request_refused=true. The
request is never exchanged; the CLI stays terminated and no additional SQL runs.
This is construction/refusal evidence, not observed CLI SQL, ACL semantics or setup
completion. See [scope, tests and source identity](ENV_API_DEFAULT_PRIVILEGES_REQUEST_EVIDENCE.md).
The current absent experimental.webhooks section correctly disables webhooks for
the pinned CLI; adding an explicit false section would be invalid. Existing config,
deadlines and Docker allowlist are unchanged. Fresh actual qualification is required
before runtime claims; prior receipts and uncertain resources stay preserved.

### Rollback-only API default-privilege semantics

After the existing prepare/toolchain/images sequence for a fresh qualified UUID,
run this fixed fixture through the existing auth-catalog control. Use apply for
the positive case, then omitted and extra for negative controls. Both negative
cases must exit2 with execution_sql_failed and no qualified semantic result.
Each invocation uses an independently fresh disposable database and the retained
owner's normal cleanup; preserve failures/resources after lost custody.

```sh
KDG_ACL_CASE=apply
python3 - "$KDG_RUN_ID" "$KDG_ACL_CASE" <<'PY'
import contextlib
import io
import json
import sys
from unittest.mock import patch
sys.path.insert(0, 'platform/deployment')
sys.path.insert(0, 'platform/deployment/tests')
import startup_lifecycle
import qualify_startup
run_id, case = sys.argv[1:]
if case not in ('apply', 'omitted', 'extra'):
    raise SystemExit('Choose one documented fixed ACL case')
def fixed_fixture(mode):
    return qualify_startup._api_default_privileges_semantic_exec(mode, case)[0]
output = io.StringIO()
with patch.object(startup_lifecycle, 'auth_catalog_exec', side_effect=fixed_fixture):
    with contextlib.redirect_stdout(output):
        code = qualify_startup.main([
            '--target', 'platform/deployment/environments/kdg-local.json',
            '--run-id', run_id, '--control', 'pinned-cli-postgres-auth-catalog'])
result = json.loads(output.getvalue())
invariant_count = qualify_startup._api_default_privileges_semantic_exec('post', case)[1]
if code == 0:
    expected = {'ok': True, 'code': 'qualified', 'stage': 'pinned_cli_postgres_auth_catalog',
                'auth_catalog_verified': True, 'api_default_privileges_request_refused': True,
                'cli_terminated_before_dispatch': True, 'cleanup_verified': True,
                'runtime_ready': False, 'fresh_setup_completed': False}
    if case != 'apply' or any(type(result.get(k)) is not type(v) or result.get(k) != v
                              for k, v in expected.items()):
        raise SystemExit('Unexpected successful ACL qualification result')
result.update(synthetic_acl_fixture=True, semantic_case=case,
              semantic_invariants_verified=invariant_count if code == 0 else 0)
print(json.dumps(result, sort_keys=True))
raise SystemExit(code)
PY
```

The fixture seeds21 direct grants, executes the exact source SQL as postgres and
checks the precise normalized ACL delta, unchanged existing objects, new-object
direct grants, PUBLIC function execution preservation and an independent rollback
witness. Five rollback-only corruptions also prove sensitivity of existing-object,
new-object, PUBLIC and both rollback checks. All synthetic defaults, grants, schema and objects roll back inside a
bounded subtransaction. Only the existing test hook admits this fixed request;
production routes/CLI termination are unchanged. Direct grant removal does not
establish effective denial through PUBLIC, global defaults or role inheritance.
See [semantic evidence](ENV_API_DEFAULT_PRIVILEGES_SEMANTICS_EVIDENCE.md).

### Guarded owner API default-privilege execution

The opt-in local control extends the existing retained owner after verified backend
departure and Auth pre/job/disposal/post checks. It applies only the fixed source
SQL in a bounded transaction, then independently checks direct default ACLs before
normal cleanup. The CLI remains terminated. The source-only request remains refused;
only the two bounded typed profiles are admitted. Existing controls retain behavior.
After fresh prepare/toolchain/images qualification:

```sh
python3 platform/deployment/tests/qualify_startup.py --target platform/deployment/environments/kdg-local.json --run-id "$KDG_RUN_ID" --control pinned-cli-postgres-api-default-privileges
```

Successful qualification records api_default_privileges_verified=true only after
both exec proofs and final custody. It leaves runtime_ready/fresh_setup_completed
false. Do not treat direct grant removal as effective denial through PUBLIC/global/
inherited privileges. Preserve failed/uncertain resources under the existing custody
rules; no automatic grant repair or reversal of committed SQL. See
[owner evidence](ENV_API_DEFAULT_PRIVILEGES_OWNER_EVIDENCE.md) for completion status,
exact tests and remaining gates.

The following fixed eleven-case rollback-only matrix exercises the new production
apply/verify predicates: it preserves seeded global, grant-option and unrelated-schema
grants, rejects omitted/extra SQL, grantability-only/unrelated-schema mutations and
reintroduced direct grants, and verifies rollback restoration. It uses the
existing catalog test hook, without adding a public SQL input or changing production
profiles. Run after the same fresh prerequisites:

```sh
python3 - "$KDG_RUN_ID" <<'PY'
import contextlib
import io
import json
import sys
from unittest.mock import patch
sys.path.insert(0, 'platform/deployment')
sys.path.insert(0, 'platform/deployment/tests')
import startup_lifecycle
import qualify_startup
run_id = sys.argv[1]
def fixed_fixture(mode):
    return qualify_startup._api_default_privileges_owner_semantic_exec(mode)[0]
output = io.StringIO()
with patch.object(startup_lifecycle, 'auth_catalog_exec', side_effect=fixed_fixture):
    with contextlib.redirect_stdout(output):
        code = qualify_startup.main([
            '--target', 'platform/deployment/environments/kdg-local.json',
            '--run-id', run_id, '--control', 'pinned-cli-postgres-auth-catalog'])
result = json.loads(output.getvalue())
if code == 0:
    expected = {'ok': True, 'code': 'qualified', 'stage': 'pinned_cli_postgres_auth_catalog',
                'auth_catalog_verified': True, 'cleanup_verified': True,
                'runtime_ready': False, 'fresh_setup_completed': False}
    if any(type(result.get(k)) is not type(v) or result.get(k) != v for k, v in expected.items()):
        raise SystemExit('Unexpected owner ACL semantic result')
count = qualify_startup._api_default_privileges_owner_semantic_exec('post')[1]
result.update(owner_acl_predicates_verified=count if code == 0 else 0)
print(json.dumps(result, sort_keys=True))
raise SystemExit(code)
PY
```

### Owner-check timeout observations

Optional `owner_failure` is separate from the Docker-request `docker_failure`.
It contains only schema_version=1, scope, check and bounded integer elapsed_ms.
Allowed pairs are acquisition/custody, fresh/custody and guard/budget; the last
labels the complete outer current/idle/budget boundary. Each scope also permits
already_expired when the budget was exhausted at observation entry.
The value identifies where an existing timeout was detected, not which custody
read or request caused it. It does not measure the whole operation's duration.

Observation is best effort: existing checks, errors/cancellation, deadlines,
connection and cleanup authority are unchanged. Invalid metadata or failed clock
observation is omitted. Nested/original valid observations use the existing bounded
error-chain formatter; no source/resource/credential/exception text is emitted.
There is no new control, reconnect/replay, recovery deletion or grant repair.
See [owner timeout evidence](ENV_OWNER_TIMEOUT_DIAGNOSTICS_EVIDENCE.md) for synthetic
verification and the limits of earlier actual-Docker receipts on changed source.

The direct acquisition handoff idle/budget pairs and fresh-session pre-constructor
idle/budget pair remain outside this observation coverage. A timeout there may lack
owner_failure; absence of metadata does not identify its cause. Follow-up coverage
is recorded in deferred work.

### Owner post-Auth setup tail

The opt-in `pinned-cli-postgres-post-auth-setup-tail` qualification control extends
verified API default privileges through the selected empty Vault, absent roles.sql,
disabled nonexperimental migrations/seeds and private current-branch initialization.
The existing owner publishes `supabase/.branches/_current_branch`, exactly `main`
without a newline, with requested file mode0644. It retains artifact identity/content
custody through normal cleanup. A preexisting marker is not adopted or overwritten;
ordinary controls still reject this extra workspace artifact.

This is owner execution after the CLI has been terminated. Its separate
`owner_post_auth_setup_tail_verified` fact is published only after normal cleanup;
`fresh_setup_completed` and `runtime_ready` remain false. No additional SQL profile,
repository migration/seed, Vault write, grant repair or CLI continuation is admitted.
The closed generated configuration and invocation are required; experimental schema
execution would invalidate the disabled-migration no-op conclusion.

Isolated process acceptance, using the existing private synthetic Docker daemon:

```sh
PYTHONPATH=platform/deployment/tests python3 -m unittest -v test_resources.ExecutionSupervisor.test_post_auth_setup_tail_process_exact_artifact_and_cleanup
```

See [tail evidence](ENV_POST_AUTH_SETUP_TAIL_EVIDENCE.md) for pinned upstream source,
exact verification and remaining gates. No actual Docker proof is claimed for this
increment. Future actual qualification requires fresh source-bound prerequisites;
retain earlier receipts and uncertain resources unchanged.

The marker is prepared in owner-private staging through retained directory descriptors
and published with Linux no-replace rename semantics. An existing destination is
refused even when empty; failed publication does not overwrite/adopt it. Staging and
mutation parents retain identity across validation. Filesystem deadlines are checked
around operations; hard preemption of a blocked filesystem call is not qualified.

### Actual setup-tail qualification on current source

The actual disposable-Docker control is now qualified on source1bc9837 with fresh
prepare/toolchain/image receipts. See [actual qualification evidence](ENV_POST_AUTH_TAIL_ACTUAL_EVIDENCE.md)
for exact commands, source bindings, results and preservation checks. The earlier
tail implementation record remains historical synthetic evidence. This does not
resume the CLI or qualify running Auth/API services, complete setup or runtime readiness.
Use fresh source-bound prerequisites after subsequent implementation changes; preserve
older receipts and uncertain resources. No recovery cleanup is authorized by success
of a separate fresh operation.

### Source-bound Kong pre-start boundary

The opt-in `pinned-cli-postgres-kong-boundary` control follows the verified owner
post-Auth setup tail. It validates one fixed synthetic Kong create intent and a
separate three-member in-memory transfer (kong.yml, localhost.crt, localhost.key).
The original CLI stays terminated. Kong create must remain rejected by the existing
Docker request classifier; no Kong container, copy, service health or HTTP response
is qualified. The synthetic key markers are not native minted-token conformance.

After normal owned PostgreSQL shutdown/cleanup the separate
`owner_kong_boundary_verified` fact may be published, with `kong_create_refused`
and `kong_three_file_transfer_verified`; runtime_ready/fresh_setup_completed remain
false. Ordinary tail/default controls retain their original behavior. No public
daemon endpoint, arbitrary key/config input or additional Docker route is admitted.
See [boundary evidence](ENV_KONG_BOUNDARY_EVIDENCE.md) for exact tests, source and
remaining lifecycle/scaffold gates. This item uses only isolated private process
fixtures; actual qualification on later changed source needs fresh prerequisites.


### Bounded binary archive transport

The existing persistent canonical PUT
`/v1.48/containers/<64 lowercase hex>/archive?path=%2F` route supports an exact
bytes body up to 65536 bytes, with a separate 1024-byte header limit including the
header terminator. Other requests retain the 16384-byte aggregate limit. Limits
are checked before final request construction and socket access. This resolves
the transport mismatch for the source-derived three-file Kong archive; archive
structure/content validation remains with the existing lifecycle owner.

Connection continuity, exact Content-Length framing and Content-Type: application/x-tar, deadlines,
response bounds, permanent failure invalidation and no replay remain binding.
This adds no Docker route, qualifier control or gateway execution authority. The
Kong create boundary still refuses creation; no copy/start/health/runtime readiness
is claimed. See [archive transport evidence](ENV_ARCHIVE_TRANSPORT_EVIDENCE.md).


### Closed disposable Kong profile before execution

The existing `pinned-cli-postgres-kong-boundary` control now also inspects the
selected Kong image's exact Docker API 1.48 Config. It requires the current image
Id/platform and the closed public [Config authority](fixtures/supabase-kong-image-api-config.md).
Changes to any inherited default, type, missing field or additional field refuse.
Source intent and synthetic three-file input remain independently validated.

A separate `supabase_kong_disposable_<project>` request has restart disabled,
AutoRemove false, private cgroup namespace, no mounts, disabled logging, unprivileged
execution, 2 GiB memory/swap, 2 CPU and 256 PID bounds. It publishes only
127.0.0.1:55481 to 8000. User kong, root working directory, selected health check and
SIGQUIT are explicit; image environment/label defaults and the source/image exposed
port union are closed expectations. This is not an observed container-merge proof.

Both source and disposable create requests must still be rejected by the Docker
classifier. The owner sends neither request. The existing boundary fact is published
only after normal cleanup; there is no new success field or qualifier control.
The original CLI stays terminated; synthetic markers do not qualify Auth routing.
No Kong copy/start/health/disposal or full runtime readiness is claimed. Existing
receipts remain historical; later actual qualification needs fresh source-bound
prerequisites. See [profile evidence](ENV_KONG_DISPOSABLE_PROFILE_EVIDENCE.md).


### Owned disposable Kong lifecycle (synthetic verification)

`pinned-cli-postgres-kong-execution` is the next explicit qualification control.
It extends the existing post-Auth setup tail and Kong boundary, retaining the
terminated original CLI. The existing owner alone supplies an exact per-exchange
fixture operand for disposable Kong name absence/create. Ordinary transport calls
still refuse both Kong profiles; there is no session-wide admission flag.

The owner validates the selected image and effective container Config, safe host
settings, empty mounts, exact network and same instance. It creates once, transfers
the existing three-file in-memory archive once, starts once and observes health.
Create/transfer/start/health share the original120s execution deadline; Kong then PG
shutdown share one15s deadline; cleanup has one10s attempt. Normal cleanup deletes
Kong before PG, database volume and owned bridge, using non-force deletion and404
confirmation. Unknown creation, lost custody or closed transport preserves resources;
labels alone never authorize recovery. An active lifecycle error remains primary if
best-effort cleanup also fails. No reconnect, replay or adoption is admitted.

Only complete normal cleanup/final custody publishes
`owner_kong_execution_verified`, `kong_create_executed`,
`kong_three_file_transfer_verified`, `kong_healthy_verified`,
`kong_shutdown_verified` and `kong_disposal_verified`. This control omits
`kong_create_refused`; the separate boundary control retains that fact.
Both runtime_ready and fresh_setup_completed remain false. Public marker keys do
not qualify native tokens, functional Auth routing or full service setup.

This increment verifies private synthetic peers only. Actual Docker qualification
requires fresh source-bound preparation/toolchain/image receipts and its own evidence;
prior receipts remain historical. Do not treat synthetic health as actual gateway
proof. See [lifecycle evidence](ENV_KONG_EXECUTION_EVIDENCE.md) for test commands,
retained failures and remaining gates. Full ENV/consuming scaffold acceptance precedes
Identity/Access/WRITE and server-backed KDG; production/pilot/deployment remain gated.

Source custody snapshots now reuse securely opened parent directory descriptors
within that one invocation. Every file is still freshly opened/read/checked/hashed;
file evidence retains its before/after signatures. Before a snapshot returns, each
parent pathname is walked again without following symlinks and must match the held
device/inode. Descriptors close on every exit, including rejection/cancellation;
no observations or authority are cached across calls. This reduces repeated path
traversal without changing the existing acquisition/helper or lifecycle deadlines.

The effective inspection also requires the identified nonempty proc masked/readonly
paths. Running NetworkSettings.Ports must match the exact loopback publication and
unbound exposed-port entries; inactive states admit only the explicit safe empty,
unbound or same loopback forms. Endpoint options remain empty/default, with only
known dynamic observation fields accepted. Unhealthy during startup is terminal;
current health is rechecked before normal shutdown. These checks strengthen the
existing inspection policy; the approved create request remains unchanged.


### Actual Kong qualification checkpoint — 2026-10-19

The current-source actual `pinned-cli-postgres-kong-execution` attempt refused
startup/unsafe_create after successful fresh preparation/toolchain/image qualification.
Read-only API1.48 diagnosis identifies omitted null Config.OnBuild and a permutation
of identical MaskedPaths members at the initial created-container check. No policy
was relaxed or execution retried. The running PG, created Kong, volume and bridge were
preserved until separately approved exact-resource cleanup, now completed without force.
The exact failure/cleanup records are in [actual evidence](ENV_KONG_ACTUAL_EVIDENCE.md). A fresh source-bound run is
required after acceptance-tested projection correction. Actual Kong lifecycle,
ordinary compatibility, full ENV/scaffold and dependent runtime work remain gated.


### Observed Kong projection correction — 2026-10-19

The effective-container validator now accepts omitted null Config.OnBuild only and
compares both identified protection lists by exact duplicate-free string membership.
Non-null OnBuild, missing/extra protections and other missing Config keys still refuse.
Pinned image validation/create/transport/deadline rules remain unchanged. Owner and
private-process acceptance RED precede the correction;152 selected methods pass.
A fresh actual control reaches running Kong, then refuses the separate post-start
null OomKillDisable observation. Actual lifecycle acceptance remains open; no OOM
policy change is included. Exact failed-run cleanup was separately approved and
completed with both exits0/no force/four404 checks. Review adds late hostile and offline
selected-projection coverage:154 distinct selected methods pass across retained frames,
with three targeted methods rerun on final48 bindings. See
[correction evidence](ENV_KONG_PROJECTION_EVIDENCE.md) for results, custody and next work.


### Nullable Kong OOM default — 2026-10-20

The existing effective-container validator accepts explicit null OomKillDisable as
the daemon default/unavailable projection in a copied HostConfig. It never requests
disabled OOM killing; true and wrong-type observations still refuse and latch custody
loss without execution/cleanup replay. Create/image/transport/deadlines are unchanged.
Owner acceptance RED,20 owner/133 affected methods and3 process controls pass across
retained source-bound calls. A fresh actual disposable Kong lifecycle now passes:
create, three-file transfer, health, normal shutdown and disposal, with original
Docker identities preserved. Ordinary API-default compatibility also passes with
normal cleanup on the same unchanged receipts. See [OOM evidence](ENV_KONG_OOM_DEFAULT_EVIDENCE.md)
for exact commands, initial harness/registry failures and source/preservation records.
The first image collection's incomplete lock is retained; the successful fresh run
uses two-second request spacing inside unchanged collection limits, without altering
publisher pins or response validation. runtime_ready/fresh_setup_completed remain
false. Native-key/functional Auth routing, remaining ENV services and consuming
scaffold proof still precede dependent Identity/Access/WRITE/server-backed KDG.

Independent one-shot review addresses all six findings, with no new review deferrals.
Three final targeted methods prove the expanded12-form/phase matrix, full-row
preservation, unrelated hostile-field refusal and versioned process-fixture overlay.
Broader selected tests and actual qualification retain their explicit source frames.


### Fixed public Kong native defaults — 2026-10-20

The existing closed Kong fixture now embeds the publisher's public local opaque
keys and exact HS256 anon/service_role defaults. It has no runtime signer or caller
credential input. The no-signing-file/no-override target, Auth secret agreement,
independent HMAC oracle and exact pinned-source signer fragment under verified
Node26.11.1 establish these fixed bytes; complete CLI resolution, custom/asymmetric
keys and functional Auth remain unproved. See
[native-key evidence](ENV_KONG_NATIVE_KEYS_EVIDENCE.md) for exact commands, source
bindings, original test failures, reproduction and five impact decisions.

The earlier actual Kong lifecycle qualification uses placeholder markers and remains
historical on that source frame. This transfer change is tested with synthetic peers
only; fresh source-bound prerequisites are required before future actual startup.
Host Docker is not accessed by this increment. Existing transport/image/create/
custody/deadline rules and all runtime/dependent gates remain unchanged.

ATDD/focused TDD and one-shot review complete:80 distinct selected methods pass across
recorded source frames; final9 targeted methods pass on48 unchanged bindings. All
six review findings are addressed. Hardened standalone proof pins known artifact
hashes, uses verified source buffers, compares the delivered tuple and rechecks bytes.
Both stdout/stderr are tested, including contained positive-control key injection.


### GoTrue closed long-running service profile — 2026-10-20

The existing create-profile owner now distinguishes the complete58-entry GoTrue
service environment from its unchanged six-variable migration job. The selected
public environment and full create argv agree with the exact pinned publisher's
pure builders under verified Node26.11.1; explicit target input and relocated imports
are documented. This is not a whole-CLI config-resolution or Docker API capture.
The intent exposes9999 only on its network, auth alias, no mounts/host publish and
source wget health. The source unless-stopped restart and inherited image command
are not approved as a disposable execution profile. Ordinary classifier refusal is
retained, no Docker admission or owner lifecycle is added. See
[profile evidence](ENV_GOTRUE_PROFILE_EVIDENCE.md) for commands, source hashes,
negative coverage and scaffold/UI/context/documentation/ADR impacts.

Profile scope/shape checks do not prove real image identity/effective container
settings/custody. Add those through retained owners before any actual service start;
prove vendor migration/no-op behavior, safe disposal and functional routing before
readiness. Host Docker, real accounts/access and production remain untouched. Future
startup uses fresh source-bound prerequisites; all dependent gates remain closed.

The repeatable checked-in publisher comparison and fresh-checkout tool prerequisites
are in [the source README](fixtures/supabase-gotrue-source/README.md). Explicit tool
selection is required; the default unittest skip does not count as conformance.
Final81 affected plus2 process methods pass on one58-file frame. All ten review
findings are patched; a prior combined-run timeout remains recorded/unexplained.
No deadline, source inventory or custody protection was relaxed.

### Internal GoTrue owner pre-start boundary — 2026-10-20

FreshGuard.verify_gotrue_service_boundary is a single-use internal prerequisite after
healthy owned Kong. It checks current PG/Kong custody/health, selected GoTrue image
identity and existing exact Auth image defaults, then validates complete service
intent and requires ordinary classifier refusal. Only a private completion flag is
set; it adds no public command/startup path, post-cleanup fact or service execution.
See [evidence](ENV_GOTRUE_BOUNDARY_EVIDENCE.md). Source changes require fresh runtime
prerequisites. Public control wiring, safe disposable GoTrue profile/effective Config,
owned lifecycle and functional Auth remain subsequent work.

ATDD and selected verification pass88 distinct methods across three unchanged-source
calls (13 boundary,73 affected,2 process). Review/evidence and572-file preservation
audit complete; original fixture errors and prior timing investigations remain recorded.
No full-suite or actual Docker claim. The next item is public qualification/process
wiring for this refusal boundary, before safe service execution.

### Access private registry storage —2026-10-21

The Access owner route now supports exact clean/1/2/3 catalogs. Revision3 adds empty
private applications, permissions and matching-application entry mappings; grants and
Identity remain unchanged. New registry rows accept owner fixture INSERT only. Private
statement guards refuse UPDATE/DELETE/TRUNCATE, including noop/empty statements; ordinary
FK checks also refuse parent TRUNCATE without dependent tables. Runtime/browser roles
receive no registry privileges. Later protected registration/mutation/readers require
explicit delivery. No grants, application enablement or effective access is created.

Use the existing coordinated owner migration/release path. Unknown history, object,
constraint, routine, trigger, default or ACL drift refuses without normalization. Failed
migration blocks release; rollback preserves previous state, then explicit controlled
upgrade after disposition/releasing a held lock provides recovery. Do not downgrade or
start migrations independently on service startup. Current v1 remains incompatible and
stopped for real consumers. [Registry evidence](../../services/access/ACCESS_REGISTRY_STORAGE_EVIDENCE.md)
records synthetic-only native preparation/acceptance and retained inspection commands.
Private preparation and --all are single-use; preserve prior frames and resources.
Existing portable bootstrap and historical timing follow-ups remain separate.

Reviewed registry storage requires UTF8 server encoding before Access migration effects;
unsupported source encodings refuse without normalization. Internal FK-trigger enablement
is part of exact catalog verification. See registry evidence for the separate isolated
SQL_ASCII refusal and fresh reviewed acceptance frame; prior frames remain historical.


### Protected Access application availability — 2026-10-21

Access0007 adds bounded `application.set_enabled` with its own current authority, exact
expected revision and atomic mutable-row/outcome/before-after evidence. The existing
controlled migration route recognizes exact clean/1/2/3/4/5/6/7 without normalization.
Only command owner gains UPDATE(enabled); raw writes and missing/forged evidence refuse.
No consumer activation, grant or organization enablement is included. Preserve prior
frames/resources and use fresh synthetic namespaces/custody for native qualification.
[Owner preparation/recovery](../../services/access/APPLICATION-SET-ENABLED.md) and
[evidence](../../services/access/APPLICATION_SET_ENABLED_EVIDENCE.md) retain compatibility
with actual previous6 clients and catalog-only Identity18 verification. Failure blocks
activation; inspect and forward-reconcile without startup migration or automatic reverse.

### Access private organization application storage — 2026-10-21

Access0008 stages empty organization application admission storage with a composite
org/app key and local RESTRICT application FK. Only access_migrator has table privileges;
owner helpers set org context with SET LOCAL and forced RLS compares the current org
setting. The policy cannot distinguish session-level from transaction-local settings;
no runtime/auth guard is added. Private statement guards refuse every UPDATE/DELETE/
TRUNCATE, including empty/noop/UPSERT/MERGE update arms.
Synthetic fixture UUIDs establish no external organization/actor verification.

Use the existing controlled Access owner upgrade; exact clean/1–8 verification refuses
unknown catalog/history/ACL drift before normalization. Preserve failed evidence, resolve
the cause and explicitly retry; no startup migration or automatic reverse. Existing7
enablement remains; Identity18 recognizes8 through verified metadata without Access row
reads. [Owner evidence](../../services/access/ORGANIZATION_APPLICATION_STORAGE_EVIDENCE.md)
records source custody, qualification commands, recovery and limits. Private preparation
and --all are single-use; --verify-retained is read-only and repeatable. Organization
verification/configure execution, readers/grants and coordinated consumer activation
remain gated. Preserve earlier native frames and retained resources.


### Private Identity organization verification — 2026-10-21

Identity0019 adds only the private setup `organization_target(uuid)` point check for
staged Access command execution. Existing target definer/RLS and table grants are reused;
only access_command_owner gains EXECUTE. It returns the exact active organization UUID
without requiring accounts/memberships or exposing metadata. Context settings are trusted
backend assertions, not independent authentication. Access8 configure remains disabled.

Use the existing controlled Identity owner migration route, never startup migration,
stamping, downgrade or automatic reversal. Exact history/catalog/ACL drift refuses;
preserve failed frames, reconcile the cause and explicitly retry. Generate its reference
only through the existing rollback-only recorder on a fresh known-source fixture.
[Owner evidence](../../services/access/ORGANIZATION_TARGET_VERIFICATION_EVIDENCE.md)
records source custody, synthetic qualification commands and recovery. Private preparation
and --all are single-use; --verify-retained is read-only. No real organization/account
changes or deployment authorization follows from this synthetic prerequisite.

### Protected organization application configuration — 2026-10-21

Access0009 delivers the existing owner command through the restricted Access operator
and CLI. Exact command/org/app authority precedes Identity19 private verification;
context is transaction-local and is no substitute for authority. Five-second observations
expire across waits/replay; every execution reobserves. Scoped historical lookup requires
current authority. Expected absence/revision, server attribution and deferred exact
row/outcome/event evidence protect creation/change; unchanged preserves the row.

Use the existing controlled Access owner upgrade. Unknown history/catalog/ACL refuses;
migration failure blocks activation. Preserve diagnostics, reconcile the cause, and
explicitly retry forward; no startup migration, stamping, downgrade or automatic reverse.
[Owner runbook](../../services/access/ORGANIZATION-APPLICATION-CONFIGURE.md) and
[evidence](../../services/access/ORGANIZATION_APPLICATION_CONFIGURE_EVIDENCE.md) record
synthetic-only commands, retention, previous-client compatibility and verification.
Private preparation/--all are single-use; --verify-retained is read-only. Use fresh
namespaces after failure/source changes, preserving prior frames and data. This does not
deliver grants, ACCESS-B, effective admission or PtS/KDG activation. No real target,
production migration, provisioning, deployment, pilot, reset/prune or push is authorized.


### Staged Access grant lifecycle storage — 2026-10-22

Use the existing controlled Access migration owner to stage Access0010; no startup
migration or runtime role elevation. Fresh private synthetic fixture preparation and
qualification are single-use; source changes/failures require fresh namespaces, with
prior frames preserved. Independent --verify-retained performs read-only inspection.
The new fields do not authorize adoption, grants or effective consumer activation.
See [owner evidence](../../services/access/GRANT_LIFECYCLE_STORAGE_EVIDENCE.md) for actual
commands/results, previous9 preservation and source/log custody. Do not reset/prune
resources or treat retained historical proof as qualification of changed source.

### Existing Identity pre-grant target proof — 2026-10-22

The current-head qualification exercises the existing Identity point projection; it
installs no production function, grant or migration. Prepare one fresh isolated database
using the existing protected owner fixture tooling. Synthetic account mappings and
membership lifecycle changes use existing Identity operator commands. Access point reads
run in short read-only transactions with local trusted context; runtime/operator direct
access stays denied. No real account/access operation is authorized by this proof.

See [owner evidence](../../services/access/IDENTITY_PREGRANT_TARGET_EVIDENCE.md) and
[runbook](../../services/access/IDENTITY-PREGRANT-TARGET.md). Preparation and --all are
single-use; --verify-retained is read-only. Preserve failed/source-changed frames and
use fresh namespaces, retain historical resources/data, and stop normally without reset
or prune. Private bootstrap portability remains deferred. Protected grant execution and
consumer activation require their own subsequent delivery evidence.

### Organization grant registry bridge — 2026-10-22

Use the controlled Access owner upgrade for0011; no startup migration or automatic
reversal. The generated discriminator preserves legacy PtS writes while nonlegacy
organization grants gain registry/active-field integrity. It does not adopt historical
rows or activate grant commands/readers. Final legacy cutover needs separate coordinated
evidence. Exact catalog/history/ACL drift refuses without normalization; failed migrations
roll back, require inspection and explicit forward retry.

See [owner evidence](../../services/access/GRANT_REGISTRY_BRIDGE_EVIDENCE.md) and
[runbook](../../services/access/GRANT-REGISTRY-BRIDGE.md). Fresh synthetic preparation and
--all are single-use; independent --verify-retained is read-only. Preserve failed/source-
changed frames and use fresh namespaces, retain historical data/resources, stop normally
without reset/prune. Private bootstrap portability remains deferred. No real-target or
deployment authorization follows from isolated qualification.


### Strict organization grant integrity verified —2026-10-22

PtS is unused and may upgrade to the target platform contract under ADR-0052. Legacy
PtS organization writes are no longer a compatibility goal. Access0012 removes
the temporary0011 discriminator and installs validated direct registry/global active-row
integrity. Use the existing controlled owner route only; incompatible rows must refuse
without adoption, deletion, startup migration or automatic reverse. Preserve exact11 on
failure, inspect diagnostics and explicitly retry forward after authorized resolution.
No production/real-target operation is authorized. Synthetic qualification uses fresh
single-use namespaces and independent read-only retained inspection, keeping prior data,
resources and receipts. Account/PtS/Content adoption remains coordinated subsequent work.


Final reviewed synthetic proof passes15 recorded native stages and independent read-only
retained inspection. See [owner evidence](../../services/access/STRICT_GRANT_INTEGRITY_EVIDENCE.md)
and [runbook](../../services/access/STRICT-GRANT-INTEGRITY.md) for exact commands/custody.
The physical slot14 fingerprint assumes the measured pinned native PostgreSQL catalog
(including collation OID100). Full logical schema dump/recreate loses dropped slots and
is not currently qualified/accepted; no manual catalog repair or backup/restore success
is claimed. Only rollback/controlled forward retry recovery is proven by this item.
No protected grant execution, effective reader or PtS account cutover is delivered.

Final regression1484 PASS48.67s; both composition checks exit0. Native run stopped
normally with data/volumes/receipts retained; concurrent work preserved. No reset/prune.


### Protected organization assignment qualification —2026-10-22

Access0013 adds protected `grant.assign` to the existing controlled migration/operator
route. Use fresh single-use synthetic namespaces and exact account/member recovery
selectors. Preserve failed frames; source changes require fresh custody, not replacement
receipts. [Owner evidence](../../services/access/GRANT_ASSIGN_EVIDENCE.md) records exact
commands/results and [runbook](../../services/access/GRANT-ASSIGN.md) describes bounded
observation, authority, concurrency, rollback/forward recovery and previous-client checks.
Preparation does not activate app access. No production migration, real access, deployment,
reset/prune or resource cleanup follows. Private bootstrap portability and complete logical
restore remain existing limitations. Protected revocation/readers are subsequent items.


Final reviewed assignment evidence:1519 affected tests PASS,13 native stages and separate
read-only retained inspection PASS; both composition checks exit0. Three review lenses
completed with direct verification/doc corrections and no deferral. Root source/log/state
custody audit passed; normal local stop retained data/volumes/receipts and older frames.
Concurrent work and immutable history remain preserved. See owner evidence above.


### Protected organization revocation qualification —2026-10-22

Use existing controlled Access migration/operator tooling for Access0014 grant.revoke.
Qualification uses fresh source-bound synthetic cases, retained previous13 client bytes,
independent read-only retained inspection and explicit failed-frame preservation.
[Owner evidence](../../services/access/GRANT_REVOKE_EVIDENCE.md) records exact commands,
results and custody; [runbook](../../services/access/GRANT-REVOKE.md) describes exact
binding/revision, current revoke authority and historical receipt recovery. No active
Identity target observation is added to removal. Preserve old data/volumes/receipts;
no reset/prune/recovery cleanup, startup migration or automatic reverse. Deployment,
real access, consumers, portable bootstrap and complete logical restore remain outside
this bounded synthetic proof.
