---
title: 'ENV thin Supabase CLI lifecycle'
type: 'feature'
created: '2026-10-20'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '5e237640471083f71f0ec8e98ce5a4401cf3a849'
context: []
---

<frozen-after-approval reason="user approved normal Supabase CLI and thin practical repository wrapper">

## Intent

Replace the active ENV delivery direction with a small normal-CLI route in existing
dev.py. Supabase CLI2.120.0 owns service lifecycle; our code supplies a validated
explicit disposable target/run, existing rendered config, local Docker/loopback
network and safe summaries. Preserve all historical qualifiers, receipts/resources
and concurrent work. Do not continue individual service interception prerequisites.

## Boundaries & Constraints

Always use existing target schema/validation/project_identity/configuration. Add
native_cli.py as a small adapter reached when --supabase <executable> is supplied to
dev.py; old invocations remain compatible for historical qualifiers. All native
commands require target JSON, canonical run UUID and explicit CLI executable; verify
--version is2.120.0. Fresh native preparation lives at the existing .local/kdg/<UUID>
namespace with native.json marker binding target/config/run. Refuse legacy/unmarked
runs and symlink/changed config before invoking the vendor. Native checks do not
require toolchain/image/per-source qualifier receipts. Never mutate old receipts.

Use a private run-local SUPABASE_HOME and Docker config, forced local Docker socket,
clean explicit child environment with experimental stack off. Keep HOME unmodified.
Use one project-specific bridge with host_binding_ipv4=127.0.0.1; inspect its driver,
option and run labels before use, create it only for up if absent, never prune/remove
networks directly. Pass --workdir and --network-id consistently, including local
reset. Keep Docker>=28 localhost gate and port conflict checks for up. No Docker
request interception, individual container Config validation or custom service order.

prepare writes the existing config and small native marker idempotently. up invokes
start; verify invokes status then checks local DB TCP and Auth /auth/v1/health; report
those as Supabase reachability, never application readiness. stop invokes normal
stop with explicit project and retains data (no --all/--no-backup). reset requires
--confirm-target equal target_id and invokes db reset --local --no-seed --yes, not
remote, not environment disposal and not owner Alembic execution. Implement but do
not run reset against pre-existing data. Capture/discard vendor stdout/stderr because
status emits credentials; only safe stage/code/run/project/exit summaries. Commands
have finite timeouts, no automatic retries or recovery deletion.

No global package/lock/TS baseline changes, new generator/runtime service, app schema,
account/access/provider/production changes, deployment, real data or legacy cleanup.

## I/O & Edge-Case Matrix

| Scenario | Expected behavior |
| --- | --- |
| Fresh prepare/repeat | Private fixed config/marker; repeat unchanged; no vendor startup |
| Up/verify/stop/reset | Exact vendor command/workdir/network/project/local scope |
| Production/foreign/unknown target, invalid run, legacy run, changed config/symlink | Refuse safely before vendor mutation |
| Occupied ports, unsafe bridge, foreign Docker/Supabase ambient settings | Refuse conflict or use explicitly clean local inputs |
| Wrong executable version, vendor error/timeout | Safe nonzero summary; no output secrets/retry/cleanup |
| Reset unconfirmed | Refuse before vendor; confirmed command remains explicitly local |

</frozen-after-approval>

## Code Map

- platform/deployment/dev.py: reuse Parser/validate/decode/read/project_identity/configuration,
  free_ports/directory/check_private; add early explicit --supabase dispatch only.
- platform/deployment/native_cli.py: new thin adapter; do not import resources/startup.
- platform/deployment/tests/test_native_cli.py: isolated temporary run/fake vendor process
  acceptance and focused guard tests. No host Docker in unit tests.
- platform/deployment/DEVELOPMENT.md, ENV_NATIVE_CLI_EVIDENCE.md: root-owned runbook/evidence.
- platform/docs/architecture/contracts/scaffold-environment-and-generation.md and
  apps/kdg-capture/docs/shared-prerequisites.md: root-owned approved correction.

## Tasks & Acceptance

- [x] Add failing acceptance first, then adapter/entry route and focused tests.
- [x] Verify matrix with meaningful negative cases and credential-output sentinel.
- [x] Root updates contract/runbook/handoff and five impact decisions; preserves concurrent work.

Given a prepared native run, normal vendor lifecycle operates only in that project's
workdir/network with no historical qualifier dependency. Given an unsafe input or
vendor failure, no false success/application-readiness or sensitive output appears.

## Implementation Notes

Direction and dirty-tree preservation already approved. No new product decision or
requirements interview. Implementation agent owns dev.py/native_cli.py/test_native_cli.py
only; root owns documentation, serial verification and any actual synthetic startup.
Investigations confirm global --network-id is honored by reset recreation; no native
bind-address flag exists. Existing config disables repository Supabase migrations/seeds;
existing owner migration tooling remains authoritative. Source notices/ADRs unchanged.

## Verification

PYTHONPATH=platform/deployment:platform/deployment/tests python3 -m unittest -v test_native_cli
then affected existing dev/gate suites. Root may use a new synthetic UUID for pinned
CLI up/verify/stop after tests; no reset or cleanup of historical resources.


Implementation/acceptance checkpoint:50 affected methods pass (12 native/38 legacy
entry/gate), source-bound. Fresh native prepare/start/verify/stop succeeds on the
same frame; start27.878s, verify1.511s, stop2.113s. No actual reset/account/app migration.
The initial real prepare finds shared .local0755 was rejected; characterization RED
precedes aligning ancestor checks with existing policy. No existing chmod. Root docs
now record approved direction, five impacts and exact evidence. Review pending.


## Review Triage Log

B1 medium, patch — A healthy running native run occupies its own ports, so repeat up
fails before reaching vendor already-running behavior. Permit the matching running
project path through normal CLI startup while keeping fresh-run port conflict refusal;
add repeat-start coverage. No new public command or per-container Config protocol.
B2 low, rejected — Concurrent same-UUID preparation can observe a partial directory
and fail closed with a generic code. It cannot start services or replace state. Normal
use selects one fresh UUID; atomic staging/another parent-lock protocol adds complexity
for a transient diagnostic distinction, contrary to the approved practical scope.
B3 low, patch — Partial initial preparation needs a documented failure exit. Preserve
it, choose a fresh UUID, never adopt/repair/delete it automatically; characterize an
injected write failure and successful fresh preparation. No recovery engine.
B4 medium, patch — Reset argv was tested with a fake only. Add actual reset of solely
new synthetic sentinel data in this item's new project; verify DB/Auth and localhost
network afterward. Compare unrelated resource identities read-only; do not read or
write other projects' real data to manufacture a cross-project data guarantee.
B5 medium, patch — Actual stop success alone does not prove persistence. Add a
synthetic table/sentinel, normal stop/restart and readback on the same native run.
B6 low, patch — Safe troubleshooting lacked a concrete target-specific inspection
command. Document safe container status metadata with the same local environment;
never dump Config/Env or raw vendor debug output.
B7 low, patch — Later owners need credentials without normal-output leakage. Document
explicit capture of vendor status into a new private secret configuration file,
separate from diagnostics, with same target/workdir/network/private environment.
B8 low, patch — Handoff/evidence still call actual startup in progress. Reconcile
status after completed qualification/review, retaining all initial failure history.
V1 medium, patch — New Docker minimum-version implementation was mocked in its old
version test. Feed27.9.9 through the real parser and assert refusal before any network
creation or lifecycle invocation. Legacy gate tests do not cover the new parser.
Edge-case review returns no findings. All three layers complete. No spec intent gap,
new feature surface or legacy cleanup is required by these patches.


Final verification:52 affected methods pass on reviewed bytes. Actual same-run native
start/repeat-start, SQL sentinel persistence, explicitly local synthetic reset,
post-reset DB/Auth and loopback/network assertions, final normal stop all complete.
Original harness's final ID/name comparison fails on unrelated renamed Deals entries;
read-only raw-snapshot reconciliation confirms no prior IDs disappear. Failed harness
and unobserved-cause delta are retained without changing unrelated resources/data.
All9 tested bindings,609 protected files/index and legacy AST behavior pass audit.
8 review findings patched,1 low rejected, no new deferrals. Runbook/evidence/handoff
complete. Native source-compatible edits require no historical receipt rebuild.
