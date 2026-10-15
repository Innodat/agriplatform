# Disposable KDG target preparation

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
