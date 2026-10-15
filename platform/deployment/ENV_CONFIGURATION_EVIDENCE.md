# ENV run-local configuration — 2026-10-15

This bounded increment completes configuration materialization in existing ENV
`dev.py prepare`, under the [environment contract](../docs/architecture/contracts/scaffold-environment-and-generation.md).
The [Build record](../../_bmad-output/implementation-artifacts/spec-env-kdg-run-configuration.md)
records implementation/review. Runtime/bootstrap and P1/SERVICE remain open.

## Delivered scope

Preparation installs only protected `inventory.json` and `supabase/config.toml` under
its ignored UUID run. The config directory is0700 and file0600; inventory binds its
exact byte hash. Repeat and read-only startup preflight verify exact bytes, private
ownership/modes, no links and exact directory contents. Missing/tampered/extra files
refuse without repair. Config is fsynced before inventory publication; interrupted
multi-file installation remains incomplete evidence and is never adopted.

The config selects approved local ports and desktop callbacks, publisher PostgreSQL17
default, Auth with public/anonymous signup and manual linking off, empty exposed
schemas/search path and no automatic table exposure. Repository migrations and seeds
are explicitly disabled with empty paths. Unused pooler/realtime/Studio/local-SMTP/
Storage/S3/vector/analytics/edge services are disabled. No SQL, role files, secrets,
provider bindings, keys, accounts or device TLS are materialized.

Actual CLI2.120.0 status parsing truncated both the original53-character project name
and49-character hyphenless-UUID alternative to40 characters. ENV now uses the existing
prefix plus unpadded URL-safe base64 of all16 UUID bytes:39 characters, reversible with
no UUID bits discarded. Config and reserved inventory identities share that exact
project ID. Canonical UUIDs remain unchanged in run paths and command arguments.
Actual mixed-case/underscore/hyphen probes preserved these characters. The final
synthetic container lookup retained the complete encoded identity; a two-run regression
uses UUIDs differing only in their final byte. Old source-bound runs are not migrated.

Supabase's [configuration reference](https://supabase.com/docs/guides/local-development/cli/config)
and the actual pinned `init` output support the configuration keys. Selected version
pins remain unchanged, including TypeScript7.0.2. The CLI's default PostgreSQL major is
configuration evidence only, not deployed-target compatibility or image-digest proof.

## Requirement-to-test evidence

| Requirement | test_run_config.py evidence |
| --- | --- |
| Public prepare writes protected deterministic config, safe settings and byte binding; immutable repeat | test_public_prepare_installs_closed_configuration_and_immutable_binding |
| Full UUID identity fits CLI and distinguishes late-byte differences | test_project_identity_preserves_all_uuid_bits_within_cli_limit |
| Changed config refuses repeat/up before daemon contact; evidence unchanged | test_tampered_config_refuses_repeat_and_startup_before_daemon_without_repair |
| Missing/extra roles or migrations, modes, symlink/hardlink/directory-link safety | test_missing_extra_unprotected_and_linked_configuration_refuses |
| Interrupted inventory publication leaves config unadopted | test_interrupted_inventory_publication_leaves_unadopted_config |
| Actual config reverified before publication | test_fresh_config_is_verified_before_inventory_publication |
| Directory/file replacement cannot validate detached evidence | test_directory_or_file_replacement_during_validation_refuses |
| Config write/flush/file/directory fsync failures remain incomplete | test_config_write_flush_and_fsync_failures_leave_no_complete_inventory |
| Config mutation during tool execution refuses without replacing receipt | test_toolchain.py: test_config_changed_during_execution_refuses_without_replacing_receipt |

Before implementation, the new public acceptance failed because no run config existed;
four tests had two failures/nine subcase errors. Existing16 preparation tests passed in
2.546s before extending the output set. After implementation all four passed in0.986s.
The project-length regression then reproduced two failures before the final39-character
encoding. All five focused tests passed in1.717s. Existing inventory-content/name
assertions were updated for the new intentional output/identity contract; no unexplained
failure was dismissed. The pre-review deployment suite passed177 tests in18.073s before
adding the identity case. Final review/regression results are recorded below.

## Actual pinned CLI parser proof

The retained opt-in fixture uses the selected executable, explicit private workdir/state,
clean environment and a temporary Unix Docker endpoint. It permits only metadata ping
reads and the exact expected container inspection, returning a synthetic404. The valid
config must reach that lookup; invalid TOML must fail before any API request. No real
Docker socket, token, profile, credentials or runtime is used. This is a test fixture,
not a reusable runtime service or alternate environment command.

```sh
python3 platform/deployment/tests/qualify_supabase_config.py --supabase platform/deployment/.local/kdg-toolchains/9ea3b977-f414-4414-b05e-444e6305c615/payload/supabase/supabase
```

The existing binary is publisher-verified2.120.0; its version is checked again. This
probe deliberately does not use `services` exit0 as parse proof: actual invalid TOML
still produced exit0 there with an error on stderr. Early exploratory parser probes
also exposed ping negotiation and the project-name truncation; their failed expectations
were corrected using actual observed requests, not bypassed. Parser acceptance does
not establish runtime enforcement of migrations/roles/service settings or network binding.

## Impacts and remaining gates

- **Scaffold:** configuration stays with existing ENV preparation and its owner tests;
  no generator, new schema/API owner, candidate pattern or offline runtime is introduced.
- **Shared UI:** none; no application screen/saving behavior is implemented.
- **Agent context:** existing root instructions suffice. Actual owner commands and
  remaining requirements live in the runbook/handoff; no generated context exists.
- **Documentation:** owner evidence/runbook and KDG next-session/testing/memlog record
  the new config/output identity and qualification limits.
- **ADR:** accepted release/ownership/scaffold decisions remain unchanged; no new
  decision or edit to an accepted ADR is required.

Docker>=28, explicit private backend/state/workdir and run-owned loopback network,
publisher image identities/deployed PostgreSQL compatibility, guarded lifecycle,
owner-filtered migration/role/fixture coordination, actual Auth/provider/device and
full owner lock graphs remain open. Runtime readiness always remains false. No daemon
upgrade, container startup, infrastructure, production migration/account/access change,
deployment, real-data pilot, Leave or KDG domain implementation occurred.

## Final review and execution

All seven independent review findings were fixed without deferral. Fresh installation
is checked before inventory publication; validation binds current directory/file
identities and protection across the read. Tool qualification revalidates config at
every existing input-observation check, including after execution. Added tests prove
required settings, actual encoded punctuation, write/flush/file/directory-fsync failure,
and exact preservation of rejected content/modes/link targets. Review regressions
reproduced two config failures and one toolchain failure before the fixes.

Final commands/results:

- `python3 -m unittest discover -s platform/deployment/tests -p test_run_config.py -v`:
  eight tests pass in1.659s.
- `python3 -m unittest discover -s platform/deployment/tests -p test_toolchain.py -v`:
  24 tests pass in2.799s.
- `python3 -m unittest discover -s platform/deployment/tests -p 'test_*.py'`:
  182 tests pass in19.901s with isolated socket permission.
- Retained actual CLI parser fixture: exit0; ordinary and punctuation-bearing UUID
  configurations each make exactly two expected metadata reads. Invalid TOML makes
  zero requests. All three checks pass; runtime_ready=false.
- Scoped whitespace and relative documentation links pass. No test was skipped.

Fresh final-source actual run:

```sh
python3 platform/deployment/dev.py prepare --target platform/deployment/environments/kdg-local.json --run-id 0cc4bc48-505e-41c1-8876-25b2d49b5694
python3 platform/deployment/dev.py up --target platform/deployment/environments/kdg-local.json --run-id 0cc4bc48-505e-41c1-8876-25b2d49b5694
python3 platform/deployment/toolchain.py qualify --target platform/deployment/environments/kdg-local.json --run-id 0cc4bc48-505e-41c1-8876-25b2d49b5694
```

Prepare and repeat exit0. Config directory0700, config/inventory0600; the actual config
matches inventory SHA256 `1fec9990e0d128043e0b543ebed17d2fe961ef01831fdd322fa43688af3cfa12`.
Up returns expected exit2, docker/docker_28_required, runtime_ready=false. Qualification
executes all six pinned tools/compiler/GIL checks and exits0 with toolchain_ready=true,
runtime_ready=false. New receipt SHA256:
`4efad618046ecda6459da9680b23e9cd47375181a059b33f6838ad8acde6ecc2`.
Old prepared runs and tool receipts remain unchanged; no runtime was started.
