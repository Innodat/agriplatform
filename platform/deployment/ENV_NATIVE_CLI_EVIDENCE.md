# Thin Supabase CLI route — requirement and verification evidence

Status: thin route complete; reviewed tests and actual native lifecycle behavior verified.
Baseline: `5e237640471083f71f0ec8e98ce5a4401cf3a849` plus explicit owned changes.

## Approved correction and bounded outcome

The user explicitly approved normal Supabase local lifecycle and proportional tooling.
The active path is now dev.py with --supabase <CLI2.120.0 executable>. Its small
native_cli.py adapter reuses existing target validation, project identity and config
rendering. It delegates ordinary start/status/stop and confirmed local DB reset to
the vendor. Historical no-executable qualifier invocations remain compatible; they
are not new-route prerequisites. No new generator or service orchestration framework.

A native run has a private config plus small target/config marker, not a binding to
every repository source/qualifier receipt. Ordinary CLI .temp files are allowed.
The adapter forces the local Docker socket and private Docker/CLI state, preserves
HOME, strips ambient remote credentials/context/proxies and disables experimental
stack routing. A project-specific localhost-bound bridge is inspected/created via
normal Docker CLI. The same network is explicit on every Supabase operation,
including reset recreation. Docker>=28 remains the localhost compatibility gate.
Vendor output is suppressed because normal start/status can contain credentials;
only safe stage/code/exit/project/run summaries are emitted. No retries/pruning or
manual service order/per-container Config validation. stop retains data.

reset means explicitly confirmed local Supabase DB reset with --local/--no-seed,
not remote reset, environment disposal or owner migration execution. It is covered by fake-vendor tests; final qualification additionally resets only
new synthetic sentinel data created for this item, never historical/real data. Existing owner Alembic/fixture/access work stays
separate; Supabase reachability is not application readiness or SQL authentication.
The wider dependency baseline including TS7.0.2 is unchanged.

## Requirement-to-test matrix

Tests are test_native_cli.NativeAcceptance and LifecycleAcceptance:

| Requirement | Method |
| --- | --- |
| Private idempotent preparation without historical receipts | test_prepare_is_private_idempotent_without_qualifier_receipts |
| Reject unsafe/unknown target and invalid run before preparation | test_unsafe_targets_and_run_refused |
| Legacy/changed/symlink config refusal | test_legacy_and_changed_or_symlink_config_refused |
| Reset confirmation and wrong CLI version | test_reset_confirmation_and_wrong_version |
| Exact lifecycle argv/workdir/network, preserved HOME, scrubbed remote environment | test_exact_lifecycle_and_clean_environment |
| Foreign/absent bridge and no unexpected vendor start | test_unsafe_bridge_and_absent_network_never_start_vendor |
| Occupied ports and old Docker prevent start | test_port_conflict_and_old_docker_refuse_before_start |
| Vendor exit/timeout safe; no reset without confirmation/recovery deletion | test_vendor_error_timeout_and_reset_confirmation_are_safe |
| Docker process local/bounded; stderr sentinel suppressed | test_docker_process_boundary_is_local_bounded_and_silent |
| Private state symlink/marker refusal | test_private_state_symlink_and_marker_changes_refuse_before_vendor |
| DB TCP plus Auth HTTP health required; no broader readiness | test_reachability_requires_db_and_auth |
| Shared ancestor0755 allowed; writable ancestor refused; run stays private | test_shared_local_readable_parent_allowed_writable_parent_refused |

All unit fixtures use temporary synthetic roots/fake executable processes. They do
not contact host Docker. Existing test_dev/test_docker_gate compatibility checks use
isolated copies and authorized local test sockets. No root npm build/full-repo claim.

## Recorded tests and retained failures

Unittest prefix: `PYTHONPATH=platform/deployment:platform/deployment/tests python3 -m unittest -v`.
Raw logs and safe JSON result/source manifests are under `.local/lean-supabase/`.
The original acceptance RED (`native-red.txt`) runs4 methods with2 expected failures:
legacy entry rejects the missing --supabase route before implementation. Initial
focused GREEN and later parent-permission characterization RED/GREEN are retained.

First real prepare refuses inventory/unprotected_directory before creating the run:
shared .local is owned0755, while kdg/run state is0700. The new adapter had mistakenly
required0700 for the shared parent. A new failing characterization precedes correction
to the existing dev.prepare policy (owner/current UID, no group/world write). Existing
permissions were not changed; the original actual-prepare.json remains preserved.
Corrected preparation uses that same UUID because no run/resources had been created.

A preliminary unisolated CLI --help probe attempted telemetry under the user's home
and was refused by the read-only sandbox. Subsequent help probes use fresh temporary
SUPABASE_HOME, and the adapter always uses private run-local state. No HOME override
or real home-state mutation is claimed. All vendor command output stays suppressed.

## Five impact decisions and remaining gates

Scaffold: existing ENV entry/config/schema owners retained; one thin CLI adapter,
no parallel generator or service engine. Shared UI: none. Agent context: existing
root safeguards suffice, no AGENTS change. Documentation: approved course correction,
mutable ENV contract, active runbook and KDG handoff/memlog updated; old qualifiers
remain historical and do not drive further per-service work. ADR: accepted Auth,
logging/release/ownership decisions stay; no accepted ADR edits or new decision needed.

Preserve historical sources, receipts/tool payloads, failed runs/locks and uncertain
Docker resources, plus concurrent Leave/PtS/Expense/brainstorming work. No historical
cleanup, production/account/provider changes, infrastructure/deployment/push or real
pilot data. Supabase stack availability does not close Identity/Access/WRITE/P1/SERVICE,
synthetic sign-in, Entra/device or server-backed KDG acceptance. Retained operational
investigations stay historical; they do not gate the simpler vendor-managed path.

## Exact source-bound verification

- `affected`: `test_native_cli test_dev test_docker_gate`; exit0, 6.012s; source manifest SHA256 `d8a8fa55a264878ea4c36b63f9b1e8f71f86cf76afb21629dfb7c0c57f7c7dff`; log SHA256 `188c0cfd3dc9b4f734216796fe12912588729a0d48aebe42b42b07237b20bf7e`; source bytes unchanged within call.
- `affected-corrected`: `test_native_cli test_dev test_docker_gate`; exit0, 6.489s; source manifest SHA256 `f08f7b49c4da47fedb08d0583e43cf3617dbc979c2c52a052f20a2870c35c351`; log SHA256 `7c9b15eb54c7b64bc1064167cedbfea38108876fc1f60a3685ffe0ae87c85072`; source bytes unchanged within call.
- `native-red.txt` SHA256 `0fac80ccea002d9b71cf99efeb0fa2bf873468b3852373002f231f2592cf97d3`.
- `native-green.txt` SHA256 `dd48d05d1c7f3a97157afad8409ddfc66f9b7e7c694251bbb07bbf1c211ab987`.
- `native-parent-red.txt` SHA256 `28de6f3336ee465f8c32f200a4a95bf9845e80892b497ff29aadb97f399c5189`.
- `native-parent-green.txt` SHA256 `7dbcd7b1e22ea3e41aaa00219d0a9d90c304c335196a476313d032afa0c3d282`.

`affected` passes49 methods on the pre-parent-correction frame. `affected-corrected`
passes50 (12 native,38 existing dev/gate) on the corrected frame. Earlier results
remain tied to their own source manifests. No broad historical-orchestrator suite
claim is transferred to the new route.

## Actual native CLI qualification

Only fresh synthetic run71e25ca2-2f0b-4c19-ac48-0a7afa4eda36 is used. The executable is
`platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/supabase/supabase`
resolved to an absolute path. Its pinned --version is verified by the wrapper; this
does not requalify historical receipts against new sources. Base command:

```sh
python3 platform/deployment/dev.py <command> --target platform/deployment/environments/kdg-local.json --run-id 71e25ca2-2f0b-4c19-ac48-0a7afa4eda36 --supabase /home/ck/repos/innodat/agriplatform/platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/supabase/supabase
```

- `actual-prepare.json`: exit2, 0.058s; stage/code `inventory/unprotected_directory`; stderr 0 bytes; receipt SHA256 `559b0ddb1e2445a1ca85f4ba904fa9b2eae45b3a98b7f933dde16c7935131a7e`.
- `actual-prepare-corrected.json`: exit0, 0.443s; stage/code `prepare/completed`; stderr 0 bytes; receipt SHA256 `a59a4e38c0a409dc042d928fb40ef347943324aef5205276ffec7d6573037365`.
- `actual-up.json`: exit0, 27.878s; stage/code `up/completed`; stderr 0 bytes; receipt SHA256 `00c7181c0252dea8ec20a5a2c9309bfe6fe0571f27ba1fb704d235f2b0fb7570`.
- `actual-verify.json`: exit0, 1.511s; stage/code `verify/completed`; stderr 0 bytes; receipt SHA256 `1e11bac3fd2d1a6fa48e8a37231668b7a9dcde05c108bf10a4fd3ba87914d6a5`.
- `actual-stop.json`: exit0, 2.113s; stage/code `stop/completed`; stderr 0 bytes; receipt SHA256 `653aeb6285e09067997a82d9a4969f19800b1758d781966e1ffb9e81ec952881`.


## Review follow-up

All three layers complete. The edge-case layer finds no issue. Blind review reports
8 findings and verification review1. Private spec triage records every verdict.
Repeat-start behavior, real Docker27.9.9 parsing and partial-preparation failure tests
are patched. Concurrent same-UUID preparation's fail-closed generic diagnostic is
rated low and rejected: another lock/staging protocol is unnecessary for present use.
The documented failure exit preserves partial preparation and selects a fresh UUID.

The runbook adds safe target-specific Docker status metadata and explicit private
credential capture, never normal output/logging. Actual integration will use only a
new synthetic sentinel in this item's new database to test stop/restart persistence
and local reset/network behavior. Unrelated project data is never accessed; comparison
of unrelated resource identities is read-only and is not a data-content guarantee.

## Reviewed-source closeout

`review-final`: `test_native_cli test_dev test_docker_gate`; exit0, 13.513s;52 methods (14 native/38 existing dev/gate), no skips. Source manifest SHA256 `02f1e81f5faaa7beb4c3f64d8be255c8ff69d73cd80c5ce7a8a816156b0724dd`; log SHA256 `2ad94dabb0300d279f6538ea253f033645db8c6c6c686da7f5ee0ab1d714a749`; all9 bound files unchanged.

`native-repeat-up-red.txt` SHA256 `408694efb5193b1e18884ae6cc3792f0ccd2053b68f907b60d3b40930f1042c5`.

`native-repeat-up-green.txt` SHA256 `7f0a5008667a0e1f75e611066e835ad661623c4be2eee61236e4453b33e09389`.


The repeat-start characterization observes own-port refusal before the patch. Normal
same-workdir/network vendor status now permits already-running startup; fresh-run
port conflicts still refuse. Docker27.9.9 is fed through the actual native parser,
not a mocked prerequisite. Injected partial-write failure is preserved/refused;
fresh UUID preparation succeeds. No staging/repair/cleanup framework was added.

Actual reviewed-source behavior uses the same native run, without rebuilding old
qualification receipts. Each step receipt records exact argv, exit and duration:

- `integration-start.json`: exit0, 26.662s; SHA256 `088d3e3a2e0fa019efe8d628609681f3d03d781d816031bca8676ef5a4886e6e`.
- `integration-already-running.json`: exit0, 5.608s; SHA256 `6e001cb140fad12c31b82e93935ee138ea1a68773decd4dafb615c667a85846a`.
- `integration-retaining-stop.json`: exit0, 4.686s; SHA256 `2fac27922cc6bea5ca5cee812c23923e75049645fd061b44c8673f7198308cb2`.
- `integration-restart.json`: exit0, 28.249s; SHA256 `e7051326bd22d5760a1b7201707691a5b948bc5ab15ffbe541271097ee3cd141`.
- `integration-local-reset.json`: exit0, 21.56s; SHA256 `a0ab9ae16e18e1a3bd1e3e292a64f3db87331d46f981be711109560795cbc4f6`.
- `integration-post-reset-verify.json`: exit0, 3.267s; SHA256 `4679094782b5d07eae79f4a5f325954aa4f6477999a440a22f8788022fb8d84f`.
- `integration-final-stop.json`: exit0, 4.459s; SHA256 `89ccd6eb608459276bcf8cdf5a41eb1019f322d7eeb1dae624b8fc8d75d84c1e`.

The test creates only env_native_smoke.marker in this item's own synthetic PostgreSQL.
Its UUID sentinel survives normal stop/restart. Explicit local reset clears that new
schema; subsequent database SQL and Auth reachability succeed. Before final normal
stop the script asserts the reset database is on the selected bridge and every
published port for the project is loopback (at least database/gateway). No existing
project's database/account/business data is accessed or reset. The final project is
stopped in the vendor's data-retaining mode; no historical cleanup or prune ran.

The original integration process then exits1 at its final metadata comparison: it
incorrectly treated complete ID/name pairs as immutable identities. Two unrelated
Deals containers retain their original IDs under changed names; one container and
one volume are added. All original unrelated container IDs, volume names and network
IDs remain. These changes' cause was not observed and no restoration/interference
was attempted. Original script, failed assertion and before/after snapshots remain.
Read-only integration-reconciliation.json verifies IDs from those same snapshots;
this does not claim the original whole harness exited0, unchanged unrelated names,
or unchanged business data. All preceding functional assertions/commands completed.

Review triage:8 findings patched,1 low complexity-expanding concurrency diagnostic
rejected, no new deferrals. All three layers finished.609 protected prior/concurrent
files and original index pass audit;32 legacy functions and the legacy main body
remain AST-identical after the new explicit dispatch. Scope uses one small adapter
and existing owners. No root/full historical-suite or full KDG readiness claim.

Next: existing owner migration/fixture/Identity/Access and scaffold integration using
this normal local stack. Synthetic sign-in and later provider/device/application
acceptance remain explicit; do not return to per-service vendor interception work.
