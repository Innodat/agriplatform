# Disposable KDG target preparation

## Current ENV delivery status

ENV is **partially implemented; the isolated KDG stack is not runnable yet**.
Completed increments qualify selected inputs and refuse unsafe handoff; they do not
close the enclosing ENV acceptance item. See individual evidence records below.

| Boundary | Implemented evidence | Remaining acceptance |
| --- | --- | --- |
| Target/configuration | Protected disposable run preparation, exact source/config binding, deterministic owner names and Docker>=28 gate | Actual isolated stack startup and current readiness |
| Dependency baseline | Six pinned executables including TypeScript7.0.2; Python wheel-lock and frontend compatibility fixtures | Generated consuming application/service proof; target/native compatibility; documented third-party declaration limitations |
| Images/resources | Four immutable image identities, guarded owned bridge/database-volume acquisition, daemon observations, current volume-use refusal and joint same-session handoff | Execution-time enforcement, volume freshness/initialization/reuse and reservation/exclusivity |
| PostgreSQL startup | Exact first-create profile and private synthetic create/file-transfer/refused-start proof | Bootstrap semantic/secret safety, actual create/start, health and bounded stop/reset/recovery |
| Owner integration | Ordered ENV/P1/SERVICE/Identity/Access/WRITE contracts and retained ownership | Existing generator recipe/schema/templates, regeneration/custom preservation, generated install/type/build/start/current-Access proof, coordinated owner migrations/fixtures/recovery |
| Provider/device | Explicit nonproduction origins/callback contracts | LAN HTTPS/DNS/testCA, actual Entra callbacks and installed Android/iPhone proof at consuming gates |

The observed host Docker27.0.3 does not meet the >=28 isolation prerequisite. A
supported daemon would still encounter `runtime_adapter_unqualified`. Upgrading the
shared daemon, provisioning infrastructure and production/pilot actions are outside
this delivery approval. Continue bounded ENV and scaffold work before dependent
Identity/Access/WRITE or the server-backed KDG slice.

ENV now implements the first bounded preparation increment of the
[environment contract](../docs/architecture/contracts/scaffold-environment-and-generation.md).
It validates the selected target and reserves deterministic names in a protected receipt.
`runtime_ready` is always false; no containers, database, Auth configuration, accounts,
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
create result refuses without retry. Existing route/method allowlists, 16KiB request
and 64KiB response bounds, strict Content-Length framing, resource ownership checks,
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
and `runtime_ready=false`. The `resources.invocation` helper delegates argv construction
to `startup.invocation`; neither operation executes startup. Final source/evidence and
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
