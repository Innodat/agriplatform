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

Only `platform/deployment/.local/kdg/<UUID>/inventory.json` is installed for the run.
The `.local/` owner ignore rule already excludes it. New directories are mode 0700;
the inventory and transient exclusive lock/staging file are mode 0600. The inventory
binds exact target bytes, implementation/schema/contract/baseline/fixture/registry
source hashes, target/run IDs and **reserved** project, owner-container, database-volume
and network names. These names are planned identifiers, with `identities_state:
reserved_only`; they are not observations that runtime resources exist. Raw target
input, secret references and secret contents are not copied into the inventory.

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

`up`, `verify`, `stop`, and `reset` deliberately return nonzero
`runtime_adapter_unqualified` after input validation. `reset` first requires
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
