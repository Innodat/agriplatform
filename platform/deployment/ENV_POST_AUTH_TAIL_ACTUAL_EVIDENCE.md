# ENV actual post-Auth setup-tail qualification

The actual disposable-Docker setup-tail control passes on source commit
`1bc983770066eeef1a13379d3d67195448ae731b`. This qualifies the existing owner's
selected setup phase; it does not establish a running Supabase stack or completed
ENV/P1/SERVICE foundation. Both runtime_ready and fresh_setup_completed remain false.

## Preparation and execution

Run `6748d60a-5876-4998-9bcc-e2529f510119`, target
`platform/deployment/environments/kdg-local.json`, Docker Engine29.9.1.
Commands run serially from the repository root:

```sh
python3 platform/deployment/dev.py prepare --target platform/deployment/environments/kdg-local.json --run-id 6748d60a-5876-4998-9bcc-e2529f510119
python3 platform/deployment/toolchain.py qualify --target platform/deployment/environments/kdg-local.json --run-id 6748d60a-5876-4998-9bcc-e2529f510119
python3 platform/deployment/images.py qualify --target platform/deployment/environments/kdg-local.json --run-id 6748d60a-5876-4998-9bcc-e2529f510119
python3 platform/deployment/tests/qualify_startup.py --target platform/deployment/environments/kdg-local.json --run-id 6748d60a-5876-4998-9bcc-e2529f510119 --control pinned-cli-postgres-post-auth-setup-tail
python3 platform/deployment/tests/qualify_startup.py --target platform/deployment/environments/kdg-local.json --run-id 6748d60a-5876-4998-9bcc-e2529f510119 --control pinned-cli-postgres-api-default-privileges
```

The five successful commands shown above exit0, as observed in the Codex command
completion responses. Preparation, toolchain and image qualification pass. An earlier
sandboxed preparation attempt
refused ports/port_unavailable before resource creation; the same preparation with
authorized socket access passes. No receipt was repaired. The tail control exits0,
stage pinned_cli_postgres_post_auth_setup_tail, code qualified. The ordinary control
also passes (stage pinned_cli_postgres_api_default_privileges, code qualified). It
is a separate fresh operation after successful tail cleanup, using the same unchanged
preparation/toolchain/image receipts; it does not adopt the preceding resources.

Local evidence directory: `platform/deployment/.local/post-auth-tail-actual/`.
`commands.json` records all six attempts, exact argv, output filenames, observed exit
codes and socket context, including the initial exit2. Its refusal output was
transcribed from the original tool response. Total command wall-clock durations
were not retained and are explicitly null; individual tool chunks are not totals.
The existing supervisor budgets were unchanged, but no independent total-duration
measurement is claimed. `evidence-bindings.json` binds all22 underlying command,
Docker inventory, comparison and preservation evidence files.
`checkpoint.json` binds
the original index,17 concurrent files,39 historical prerequisite files and run ID.
`source-bindings.json` retains the preceding74 source/test bindings. New generated
preparation and qualification receipts remain in their normal run-owned directories.

## Requirement-to-test evidence

| Requirement | Actual control/result |
| --- | --- |
| Selected empty/disabled tail and exact branch-marker custody through cleanup | tail.json: owner_post_auth_setup_tail_verified=true |
| Auth job and catalog plus API defaults verified first | tail.json: auth_job_exit_verified/auth_job_disposal_verified/auth_catalog_verified/api_default_privileges_verified=true |
| Original CLI terminated, normal PostgreSQL shutdown and disposal | tail.json: cli_terminated_before_dispatch/pg_shutdown_verified/shutdown_verified/cleanup_verified=true; forced_shutdown=false |
| Ordinary path retains behavior | api-default.json: api_default_privileges_verified=true, cleanup_verified=true; owner_post_auth_setup_tail_verified absent |
| No complete setup/runtime claim | Both controls: fresh_setup_completed=false, runtime_ready=false |

The preceding [implementation evidence](ENV_POST_AUTH_SETUP_TAIL_EVIDENCE.md)
retains the original acceptance RED, focused TDD,282 final selected tests and review
corrections. This verification-only item changes no runtime behavior and adds no
duplicate implementation tests. No full-suite, deployed or real-data proof is claimed.

## Preservation and impacts

Before/after-tail and final inventories contain the identical182 container IDs,211 volume names
and14 network IDs. Only projected inventory fields are recorded, without environment
or log payloads. Normal verified cleanup removes this operation's disposable resources;
prior uncertain resources are neither adopted nor removed. Identity equality is not a
claim of unchanged internal resource content or uninterrupted unrelated workloads.

Scaffold impact: qualify the existing deployment owner, with no generator/schema/client
change and no consuming scaffold claim. Shared UI: none. Agent context: unchanged;
this adds evidence, not policy. Documentation: this record, development runbook, KDG
handoff and memlog. ADR: no new decision; existing isolation, release and safe logging
contracts remain binding. TypeScript7.0.2, mail15484 and all pins remain unchanged.

Next remains the bounded ENV service lifecycle and consuming scaffold proof. Pinned
CLI start.handler.ts completes database setup before START_SERVICES; Kong precedes
GoTrue in start.services.ts. Check selected gates/exclusions before choosing the next
runtime service. An Auth migration job does not qualify a running Auth service.
Identity/Access/WRITE, server-backed KDG, Leave and production remain outside this item.

Final preservation verification confirms all17 concurrent files, original empty index,
39 historical prerequisite files and74 source/test bindings unchanged. The two controls'
25 reported source hashes match disk. All13 new prerequisite files are bound separately
in new-receipt-bindings.json and retained. These checks do not repeat or reinterpret
the preceding implementation's unexplained timing failures or deferred investigations.

Local evidence digests (SHA256):

| Artifact | SHA256 |
| --- | --- |
| evidence-bindings.json | 44d33ed0d077e26a3b33fc14eac428bec81b61bd283e9c07aef126d7d476826c |
| source-bindings.json | 9254183ecdb3e10b22226f211f28f137f6a3b700e03339658b41b118ac80f8b9 |
| commands.json | f915b3e493aa5cabf90b79c71407744ef6106f242fa6329afc3cf1f0fced8a55 |
| tail.json | 3b2bcbc2a4bb77310cf3e3d00a4c9647c3dd8cf10b01d71dabade8ab98c46354 |
| api-default.json | c3fe2316be8460df91bd27f4690b5333a06ffab05c1129c3220219f76ed9faa8 |
| new-receipt-bindings.json | 6977f0932e3e8cce06189011a804044d2c91ff577fd0164e935b01621344f12b |
| verification-summary.json | 46a9a17c6aebef8513ff33a63577ee8377c79325c35e895e7c8d17841cb39281 |
