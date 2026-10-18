# CLI post-start health and refused Auth job evidence

Build: [bounded post-start boundary](../../_bmad-output/implementation-artifacts/spec-env-cli-poststart-auth-boundary.md).
Implementation, three-layer review and final reviewed-source verification pass.
Full environment/runtime readiness remains false.

## Purpose and authority

The preceding [initialized CLI proof](ENV_INITIALIZED_CLI_EVIDENCE.md) ends at each
executed PostgreSQL start. This item retains a fresh actual CLI through its health
requests and exact first Auth migration-job request, then refuses the job before
dispatch. It uses the existing retained ENV owners and disposable synthetic target.

Immutable CLI source commit
[753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4](https://github.com/supabase/cli/tree/753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4):
[health checks](https://github.com/supabase/cli/blob/753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4/apps/cli/src/command-internal/db-bootstrap/health-check.ts),
[database sequence](https://github.com/supabase/cli/blob/753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4/apps/cli/src/command-internal/db-bootstrap/start-database.ts),
[fresh setup](https://github.com/supabase/cli/blob/753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4/apps/cli/src/command-internal/db-bootstrap/db-setup.ts),
[Docker argv](https://github.com/supabase/cli/blob/753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4/apps/cli/src/command-internal/docker-run.args.ts),
[Docker execution layer](https://github.com/supabase/cli/blob/753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4/apps/cli/src/command-internal/docker-run.layer.ts).
The [existing profile authority](fixtures/supabase-pg17-profile.md) records the exact
selected command/environment shape. Root read the immutable serializer through a
direct primary-source fetch after browser cache misses; no guessed argv was adopted.

With PG17, Auth enabled and Realtime/Storage disabled, the CLI connects to host-facing
PostgreSQL before constructing the Auth migration job. Reaching that request is source-
grounded progress evidence, not independent connection identity/authentication proof.
Driver probes may issue SQL. The refused job does not execute its Auth migrations or
the subsequent fresh-setup pipeline; no owner migration/account/grant is authorized.

## Required verification

ATDD acceptance RED before behavior, focused no-socket TDD, affected real private-socket
process fixtures, then full deployment discovery. Root runs process/Docker checks
serially; implementation child runs no-socket tests only. Exact commands:

```sh
python3 -m unittest discover -s platform/deployment/tests -p test_pinned_execution.py
python3 -m unittest discover -s platform/deployment/tests -p test_resources.py
python3 -m unittest discover -s platform/deployment/tests
```

Process fixtures require local sockets and child-process execution outside the
restrictive sandbox. Real proof requires fresh source-bound prepare/toolchain/images,
the new control plus existing initialized/persistence/first-start/bootstrap/guarded
controls, and expected public up refusal. Failures and exact output hashes remain
retained, without repaired receipts or weakened expectations.

## Impact decisions

Scaffold: extend current profile/resource/startup/test owners; existing P1/SERVICE
generator acceptance remains open. Shared UI: no change. Agent context: current root
rules suffice; consuming handoff records actual commands/limits. Documentation: this
evidence, profile, runbook, Build record and KDG handoff/memlog. ADR: accepted records
unchanged; no new decision needed. ADR0020 controlled owner migration/compatibility/
activation/recovery gates remain unfulfilled. ADR0023 selected facts only; no raw job
argv/environment/SQL, health logs or credential-derived output is persisted/reported.

## Preservation and remaining gates

Five concurrent document hashes and index entries matched the prior checkpoint at
baseline `c8e1f65f96c371139aca591c5654fd4b69d78aa7`; a protected checkpoint was written,
fsynced and reread before edits. Only this Build's files enter its scoped local commit.
The existing private verifier gained one explicit poststart mode; its exact previous
bytes remain retained. Prior SHA256
`51f9e0b23f4b7ee2651e48519da0bb10aa64a3cfec2c7ea6671ba48c85a9319a`;
updated SHA256
`393136418f8ce208c952d2cdda8f7494d9e172c208b772b793520c2e4159db1c`.
Its negative-injection branch is unchanged and excludes poststart.

Keep actual Auth job ownership/migration and later fresh/initialized setup, complete
stack readiness, cross-execution admission/reconciliation, public lifecycle/recovery,
owner migrations/fixtures/current authorization, provider/device and existing-owner
P1/SERVICE generation/regeneration/install/build/start gates open. Identity/Access/WRITE
and server-backed KDG remain gated. No Leave/editor or production/pilot work follows.
The two earlier intermittent guard investigations remain open.

## Implementation verification

Acceptance RED observed by the implementation child before production edits:
`python3 -m unittest discover -s platform/deployment/tests -p test_pinned_execution.py -k PoststartAuthBoundary`
runs4 tests with4 errors, missing FreshGuard.enable_auth_boundary. The independent
tests specify truthful health, exact Auth job inputs and phase/identity protections.
Focused GREEN, root process/actual qualification and full regression remain required.

Root focused discovery passes **66 tests,0.817s**. Root read the complete1075-line
unified diff before evaluating implementation. First affected command
`python3 -m unittest discover -s platform/deployment/tests -p test_resources.py -k auth_poststart`
runs **3 tests,154.389s**, with2 failed subcases and1 error. Corrupt/lost health-reply
fixtures leave a descendant holding output pipes after CLI parent exit; the fixture
daemon's short idle timeout closes the connection and owned cleanup cannot complete.
The empty terminal-request fixture exits before the owner reads its `/proc` parent
identity, producing FileNotFoundError. These failures remain evidence, not passes.
The implementation owner is correcting fixture timing and keeping the empty sender
alive to test its intended malformed request. The demonstrated vanished-peer read will
also produce a safe handoff refusal. No production execution deadline is increased.

Root additionally identified an oversized valid JSON reply padded with whitespace
that bypasses the receive-loop limit; a concrete RED case and explicit bound are
required before qualification. Malformed JSON will normalize to the safe private-
handoff refusal, retaining the original strict exception expectations for legacy tests.

Concrete oversized-reply regression RED: the child runs
`python3 -m unittest discover -s platform/deployment/tests -p test_pinned_execution.py -k health_lost_malformed_and_oversized`
and observes1 failure because a513-byte valid JSON value with trailing whitespace is
accepted. The fix explicitly rejects responses beyond512 bytes and normalizes malformed
post-start JSON. A no-socket DepartedPrivatePeer test drives the supervisor through the
vanished `/proc` read, proving safe invalid_owner_handoff and group termination.

Corrected fixtures keep the empty terminal sender alive until refusal, detach only
ACK/lost-health descendants' output pipes, and allow initialized/post-start daemon
connections120s idle. The owner execution deadline remains120s and closes the connection
on exit. Legacy strict dev.Refusal assertions are restored; none is broadened to accept
ValueError. Root smallest failed-method rerun passes **1 test,15.353s**; final focused
discovery passes **67 tests,0.786s**. Full affected process verification follows.

Root affected `-k auth_poststart` process discovery passes **3 tests,43.355s**,
covering all10 scenarios: success, malformed health/job operands, malformed/lost health
reply, lost terminal request, changed start identity, changed wrapper custody, elapsed
deadline and interruption. It checks one recorded PostgreSQL create/start, one owner
cleanup attempt and terminated CLI/descendant processes. Custody loss preserves the
unresolved owned row; other demonstrated failures clean up without a boundary success.
Fresh source-bound UUID `608704a3-5430-402e-82e4-e71e4492fcd3` begins prerequisite
qualification on the stable production/profile source.

Fresh608704a3 prerequisites pass prepare0.075s, toolchain22.340s and images42.580s.
All four approved immutable children/configs match the preceding initialized proof,
including PostgreSQL child
`sha256:e85bc10ac5b141223b289e1e8dc8d448cf3df92501917149db0366b9c5aaf053`
and GoTrue child
`sha256:839f529492d116b4e8b7777c953a27c381d34c15a744b1bcefde5eefaa1f9f9f`.
No publisher-version substitution or receipt repair. Actual new control follows.

Actual new `pinned-cli-postgres-auth-boundary` on608704a3 passes **exit0,70.840s**:
real CLI health observed, exact Auth profile validated/refused, job_dispatched=false,
fresh_setup_completed=false, same-instance clean shutdown and owned cleanup verified.
All13 retained files and running inventory remain unchanged; no injection selector.
Root independently rechecked source/profile bindings and concurrent document/index hashes.
Protected `poststart.json` SHA256
`105aabb6665df7866dd6625ff143216af20b1ebc783417b7e1e345ff9df513cf`;
image receipt SHA256
`60a33947dd8abf4142b7616fe487bebf465694f7fbe1ef4c9793ebc37a83db05`.
Root final focused suite passes **68 tests,0.861s**, including33 independently derived
Auth-profile rejection cases. Added exact process group/deadline assertions will also
execute in full discovery.

Existing initialized control passes **exit0,82.714s**, retaining both CLI boundaries
and persisted predicates. Existing persistence passes **exit0,102.520s**, retaining its
first-CLI/owner-recreation result semantics. Both preserve all13 receipts and running
inventory. Protected result SHA256s respectively
`dc15b1a9ebed876cb87d756f3b09e4efc4b9f97f792910a13c85c5c62339a131` and
`10844320dba1e0c31925c1a9696a5bd8ed94ece811f75224cbedfd094c0fa490`.

The subsequent original first-start control refuses **exit2,59.547s**,
images_cli/command_refused, with unchanged13 receipts/running inventory. The serial
sequence stops there. Protected `proof.json` SHA256
`f33d0451c166862a3d3ccb95750840689791d4fbad3c2a432c29fc5d08b1fde0`.
Source tracing identifies the existing image owner's nested toolchain repeat as the
only uncaught bounded subprocess on that path; its safe child stdout is discarded by
the pre-existing wrapper. This does not identify the failing probe or whether failure
preceded or followed container execution. No initial proof or cleanup claim follows.

Root runs the exact existing image-owner repeat with safe exception-only diagnostics:
**PASS32.651s**, no observed owner failure. Protected owner-repeat-diagnostic.json SHA256
`06cf164a79fd0571deb18fc1515acacbc1f388e82e751cdc651d31e34cca21be`.
This passing diagnostic does not explain the earlier refusal. Production/profile and
receipts remain unchanged. A targeted first-start diagnostic now records only safe
owner status codes and guard phase/cleanup booleans, preserving all original limits.
The existing private helper retains its preceding bytes, adds only proof-diagnostic
and leaves the negative-injection branch unchanged. Current helper SHA256
`bb3b866ec6981615263f880804b2ba677cb7661beaeade6df6bea21913e0c627`.

Targeted same-control first-start diagnostic passes **exit0,85.989s**, with original
first_start_only/health/clean-shutdown/disposal facts, unchanged13 receipts/running
inventory and no observed owner failure. Root verifies one guard reaches phase7 with
cleanup attempted and cleaned=true. Protected `proof-diagnostic.json` SHA256
`b4b1a00dda687029ec4fc41d688fd92ecd617c2278b762f269ff361934b6fad4`.
The earlier refusal remains unexplained; this pass does not close its investigation.

## Pre-review regression and matrix audit

Existing bootstrap passes **exit0,25.614s**, retaining its role/JWT/schema/key and
clean-shutdown/disposal semantics; loopback_password_required remains false.
Existing guarded-fresh passes **exit0,68.218s**, retaining its synthetic first-start
refusal. Each preserves13 receipts and running inventory. Protected result SHA256s:
bootstrap `b2665bbdcd149ce89899feb6ed339be8d74e1da292a148fa41f93bfe42628311`;
controls `268ab528069bb6938f2fb14596036688d03d466000d37db38e333335cc7b0688`.
Public up returns expected **exit2,0.063s**, runtime_adapter_unqualified/runtime_ready=false.

`python3 platform/deployment/.local/pinned-cli-execution-qualification/verify-local.py tests 608704a3-5430-402e-82e4-e71e4492fcd3`
passes **553 tests,498.253s** (wrapper498.441s), exit0, no skips. The retained diagnostic
runner uses the same full discovery command above, adding only selected failure metadata
for the two older intermittent investigations; assertions and deadlines are unchanged.
Protected `deployment-tests.log` SHA256
`25e5804d2879482d91c9010ba917dde5654be481be10027f1159bfaca19679f8`;
`deployment-tests.json` SHA256
`54c0955d884b6ac3ce814d10abfad835a13e521df00bac97f4325b9c65e36910`.

All five matrix rows have executed passing coverage in focused/affected/full discovery.
Exact profile inputs additionally have33 refusal mutations. The final process assertions
verify exactly one group signal/two stopped processes and exact docker_timeout with
unchanged execution deadline at cleanup entry. Public lifecycle and runtime remain gated.
Five impacts are recorded above. Three independent review layers follow; no passing
rerun explains the earlier prerequisite refusal or the two older intermittent failures.

| Requirement row | Executed passing acceptance/contract coverage |
| --- | --- |
| Truthful health to refused Auth boundary | PoststartAuthBoundary.test_real_health_then_exact_refused_auth_without_job_dispatch; integrated process/actual CLI proof |
| Exact phase/private exchange and terminal consumption | PoststartAuthBoundary.test_terminal_job_consumed_once_and_finish_needs_boundary; private parser/process adversaries |
| Current state/resource/fixture/start identity | PoststartAuthBoundary.test_health_only_selects_current_safe_fields_and_keeps_start_identity; shared owner custody cases and post-start process faults |
| Exact job inputs | PoststartAuthBoundary.test_changed_auth_profile_or_early_job_never_dispatches; independent golden profile/envelope/process cases |
| Failure/deadline/interruption | Shared execution/cleanup tests plus affected post-start process cases; no success, no replay, one bounded owned cleanup |


## Reproduction and retained artifacts

Run from the repository root. Use a new UUID for source-changing work; do not reuse or
repair608704a3 receipts. The supported implementation lives in the tracked owners,
not in the ignored verification helper. For a new UUID, run these serially:

```sh
python3 platform/deployment/dev.py prepare --target platform/deployment/environments/kdg-local.json --run-id <new-UUID>
python3 platform/deployment/toolchain.py qualify --target platform/deployment/environments/kdg-local.json --run-id <new-UUID>
python3 platform/deployment/images.py qualify --target platform/deployment/environments/kdg-local.json --run-id <new-UUID>
python3 platform/deployment/tests/qualify_startup.py --target platform/deployment/environments/kdg-local.json --run-id <new-UUID> --control pinned-cli-postgres-auth-boundary
```

Repeat the last command with each existing control, serially:
`pinned-cli-postgres-initialized`, `pinned-cli-postgres-persistence`,
`pinned-cli-postgres`, `postgres-bootstrap`, `guarded-fresh`.
Then run `python3 platform/deployment/dev.py up --target platform/deployment/environments/kdg-local.json --run-id <new-UUID>`;
expect exit2/runtime_adapter_unqualified. Full regression is the direct unittest
discovery command above. Capture each safe JSON result and exit status independently;
record SHA256 of the13 receipt/inventory/config files before/after and Docker running
name/ID/image/state inventory before/after. Qualifiers own their bounded cleanup;
a refusal must not be retried until its evidence is inspected.

Exact executed helper commands for608704a3 were
`python3 platform/deployment/.local/pinned-cli-execution-qualification/verify-local.py <mode> 608704a3-5430-402e-82e4-e71e4492fcd3`,
with modes in execution order `prereqs`, `poststart`, `initialized`, `persistence`,
`proof`, then inspected failure, separate owner-repeat diagnostic, `proof-diagnostic`,
`bootstrap`, `controls`, `up`, `tests`. Each invocation is serial. Private artifacts
are retained under
`platform/deployment/.local/pinned-cli-execution-qualification/608704a3-5430-402e-82e4-e71e4492fcd3/`:
`prerequisites.json`, `poststart.json`, `initialized.json`, `persistence.json`,
`proof.json`, `owner-repeat-diagnostic.json`, `proof-diagnostic.json`, `bootstrap.json`,
`controls.json`, `up.json`, `deployment-tests.log`, `deployment-tests.json`,
`full-diagnostic-runner.py`. The pre-extension helper snapshots and source hashes are
under `platform/deployment/.local/cli-poststart-qualification/`; immutable CLI source
snapshots are in its `primary-source/` subdirectory. These local artifacts are ignored
and are not required to reproduce the supported direct commands above.

The diagnostic is observational and can be reproduced without those private scripts:
import existing `qualify_startup`, `images`, `resources`, `dev`; call unchanged
`qualify_startup.main` with the ordinary `pinned-cli-postgres` argv. Capture its safe
JSON stdout. Temporarily wrap `FreshGuard.__init__`, calling the original unchanged
and retaining only guard references; after return report phase, execution_started,
start_attempted, container_recorded, cleanup_attempted and cleaned booleans. During
that call use `sys.settrace` restricted to `images.bounded_command.__code__`, recording
only a caught dev.Refusal stage/code, nested toolchain process returncode and its JSON
`ok/stage/code/runtime_ready/toolchain_ready` fields. Restore tracing in finally.
Do not emit arguments, environment, raw output or exception text, inject failures,
alter dispatch/limits/assertions, or overwrite the original failed result. The separate
owner-repeat diagnostic calls existing `images.existing_tools` for the same target/UUID
under the same exception-only trace; it performs the ordinary owner prerequisite
repeat. Its successful outcome is separate from original failure evidence. Standard
full unittest discovery reproduces the regression checks without the private runner's
selected failure-only metadata for the two earlier open guard investigations.


## Review corrections and fresh-source verification

All three independent review layers completed; runtime thread limits serialized
reviewer admission after simultaneous attempts. Every finding is individually triaged
in the Build record. Null/non-object Health reproduced AttributeError RED, then
explicit dictionary checks at health and terminal admission return safe
execution_invalid_health. No budget/profile/dispatch behavior changed. Tests now
protect identity before first health, healthy→notready admission reset, current health
at terminal, exited/dead/OOM and malformed Health at both sites, consume-before-invalid-
profile replay, fragmented exact512/513 replies, and repeated real private health
polling with the unchanged original deadline. Root73 focused PASS0.812s; smallest new
process polling test PASS3.726s. Root read source/test patch deltas. Source-changing
fix invalidates preceding current-source qualification, so fresh e0098c0e run follows.
One pre-existing safe prerequisite-diagnostic investigation is newly deferred; earlier
failure evidence and two older intermittent guard investigations remain open.

Root affected post-review `-p test_resources.py -k auth_poststart` passes
**4 tests,54.186s**, including the new repeated-polling private process scenario
and all original post-start success/failure cases. Fresh prerequisites begin only
after these process tests finish.


Fresh e0098c0e prerequisites stop before any image receipt/container execution:
prepare PASS0.080s, toolchain PASS20.561s; images exit2 registry/manifest_response_invalid
16.892s. The existing code uses that refusal for non200 manifest status or nonidentity
content encoding; the safe result does not distinguish them. No cause is inferred.
Protected prerequisites.json SHA256
`197359e9a78cfe94f2dcfcb466b4af0f02dea45da63ad04adab099dd662389d6` in its same-named
private run folder. No receipt is repaired. After inspecting the failure path, fresh
run1a572768-945a-4ba4-9ae8-2a2d71b046a4 repeats unchanged prerequisites with required
external registry access; the failed attempt remains separate.


Fresh reviewed-source run `1a572768-945a-4ba4-9ae8-2a2d71b046a4` passes prepare0.060s,
toolchain21.170s and images33.648s with the same four approved immutable identities.
All six actual/synthetic qualifier controls pass serially; each preserves all13
retained files and the running inventory. No injections or diagnostic variants needed.

| Protected result | Exit / seconds | SHA256 |
| --- | --- | --- |
| poststart.json | 0 / 68.083 | `fa8ba3e05a5d28bc066f24dcea15076df095b7c2a0cb1846b9927d95bb9be206` |
| initialized.json | 0 / 89.418 | `13dfab4a066d8d693499794a90fa153e5c1123a88f42196a8eb26b9ab4db78fa` |
| persistence.json | 0 / 83.794 | `a948855c3e2e39efec4cd09047afe6c70db0148062f184ed2646732033489af7` |
| proof.json | 0 / 71.340 | `83d1ad0ee9507bbd4b9d337369d574bcb310c5f60bc395bfa1500dcfbf99da4c` |
| bootstrap.json | 0 / 31.379 | `81d3a3fdc5ab1e231f5dc836cc44c2ad3056e0a81ac775444c92ffbc46d25d2f` |
| controls.json | 0 / 89.361 | `050da13966872ab70b528d5f3f0f4c725d057668d800c83ef1a384dae94022c8` |
| up.json | 2 / 0.076 | `0ee9196239f69a2a27cd6944b405c92644a06c3e1cdf2240a3c7b1e62da913b7` |

Root independently verifies all selected new-boundary facts and every recorded source/
profile digest against current bytes. Public up remains runtime_adapter_unqualified.
The ordinary first-start PASS does not resolve its earlier nested-prerequisite refusal.

The first post-review full regression ends without a result record/final summary.
Its incomplete400-byte log contains a failure marker but no test identity/traceback;
no exact failure cause or successful completion can be claimed. SHA256
`380f6fc65cf6ffadd9555f5e16c23ebaafb8ffcb519a6e4b044dcd9f1752ead8`. Session continuation lost the tool-cell
handle; independent host process check confirms no runner remains. The log is retained,
not overwritten. Full discovery restarts as deployment-tests-2 with unchanged source,
assertions and diagnostic runner, using authorized host process/socket access.


## Reviewed-source closeout

`python3 platform/deployment/.local/pinned-cli-execution-qualification/verify-local.py tests 1a572768-945a-4ba4-9ae8-2a2d71b046a4`
passes **559 tests,591.285s**, exit0, no skips (wrapper591.494s). Protected
`deployment-tests-2.log` SHA256
`555748ddb7d50d515d9fa214917faafc05600dac939714a9283a278bd1e0fafb`;
`deployment-tests-2.json` SHA256
`53841158a6ee373aab7e562b939fcdf20c03b0db7e365b4ae291468eec9874db`.
Root reads the final log and independently verifies current source/profile bindings,
all13 retained receipt/config/inventory hashes and all five concurrent document/index
entries. The synthetic unit fixture prints staging run42; no deployment was performed.
The passing complete run does not explain the earlier incomplete failure marker.

All five requirement rows and scaffold/UI/context/documentation/ADR impacts are covered.
Three review layers and their patches are complete:73 focused,4 affected process and
559 full deployment tests pass, plus actual fresh reviewed-source boundary and all
existing controls above. One pre-existing nested prerequisite-diagnostic investigation
is newly deferred; two older intermittent guard investigations remain open. Earlier
refused/incomplete records remain retained, never overwritten or counted as passes.
This bounded Build is complete. Actual Auth job ownership/dispatch, independent database
session proof, later fresh/initialized setup, whole-stack/runtime, cross-execution/public
lifecycle/recovery and existing-owner ENV/P1/SERVICE acceptance remain open. No dependent
Identity/Access/WRITE/server KDG, Leave/editor, production or real-data action follows.
