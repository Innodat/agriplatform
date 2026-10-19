# Safe Docker failure diagnostic evidence

Build: [ENV safe Docker failure diagnostics](../../_bmad-output/implementation-artifacts/spec-env-docker-failure-diagnostics.md).
Status: diagnostic increment implemented, verified and reviewed; runtime_ready=false.

## Purpose and authority

The previous backend-lifetime item retained two Docker timeouts without the failing
exchange/phase. This item implements the diagnostic-capture portion of that existing
investigation through the existing transport and qualification output. It does not
explain the historical failures, authorize recovery or complete runtime readiness.

The approved [environment contract](../docs/architecture/contracts/scaffold-environment-and-generation.md)
and [ADR0023](../docs/architecture/decisions/0023-structured-operational-logs-and-sensitive-data.md)
govern. Existing transport/resource/startup/qualification owners retain all work.
Source baseline is `6ccd126894fa5a029c043285d068bf40103423ce`.

An optional `docker_failure` contains exactly schema_version=1, a closed operation
category, a closed transport phase and bounded monotonic elapsed_ms. Request validation
precedes categorization. Invalid requests use unvalidated; no raw resource/route/input
or exception text becomes a diagnostic. A validated copy is emitted, not an object
dump. The existing outer stage/code and exit remain authoritative. The selected
diagnostic can describe an earlier exchange when cleanup wraps the original failure;
it is not proof of daemon cancellation, mutation outcome or recovery.

Only failures inside DockerSession.exchange produce an observation. A caller/owner
deadline outside an exchange can still omit docker_failure. No last successful
exchange is substituted as its cause. Excessive ancestry is omitted rather than
reporting a newer wrapper as the original failure. This is bounded transport
diagnostic capture, not completion of all existing diagnostic investigations.

## Requirement-to-test ledger

| Requirement | Required executed evidence | Status |
| --- | --- | --- |
| D1: connect/send/receive attribution | DockerSessionTests.test_failure_diagnostics_acceptance_connect_and_qualifier_json; test_failure_phases_elapsed_and_permanent_closure; test_elapsed_observation_is_nonnegative_and_capped | PASS |
| D2: framing/final-budget attribution | DockerSessionTests.test_framing_idle_and_processing_budget_phases; existing decode/final-idle/total-deadline and bad-response tests | PASS |
| D3: safe rejected-input/error output | DockerSessionTests.test_invalid_sensitive_request_never_acquires_socket; connect/body/exception canaries; existing public-up transport-failure test | PASS |
| D4: first failure through cleanup/reuse | Resources.test_execution_uncertain_archive_start_preserves_closed_peer_without_replay; session permanent-closure test | PASS |
| D5: hostile metadata/chain | DockerSessionTests.test_formatter_exact_validation_chain_cycles_and_ordinary_shape; test_observation_clock_failure_preserves_refusal_and_closes | PASS |
| D6: compatibility and actual runtime gate | Affected/full suites, source-qualified actual backend/prior controls and expected public refusal | PASS |

## Verification artifacts

Protected ignored qualification records live under
`platform/deployment/.local/docker-failure-diagnostics-qualification/` and the existing
`platform/deployment/.local/pinned-cli-execution-qualification/<run UUID>/` owner
verification directories. The former retains concurrent file/index identities and
the exact approved frozen spec. Existing source-bound preparation/tool/image receipts
require a fresh UUID after source changes; older records remain unchanged.

Root independently ran the following on the frozen source:

| Command suffix after `python3 -m unittest discover -s platform/deployment/tests` | Result | Log SHA256 |
| --- | --- | --- |
| `-p test_docker_session.py` | 25 PASS0.480s | `7d49e8b7107391578d88270b947fba04e062ee693648dbcb4d9d0916c8392d0f` |
| `-p test_docker_gate.py` | 15 PASS1.191s | `1b8b2ea4a5295e03652e2f365cb44673a4036824088b0433a72cd4ca13914044` |
| `-p test_resources.py -k test_execution_uncertain_archive_start_preserves_closed_peer_without_replay` | 1 test/four scenarios PASS15.191s | `ec7002ae0493d1dd8292a5b173054762df3d540f09c3586f3211cc8ac1b76664` |

These commands retain root-session/root-gate/root-cleanup .json/.log files under
the first protected artifact directory. root-cleanup-summary.json supplements the
original metadata record's plural-only test-count parser; its unchanged log explicitly
records one test. No result is inferred from an unexecuted test.

The outer acceptance test
`DockerSessionTests.test_failure_diagnostics_acceptance_connect_and_qualifier_json`
first fails for missing Refusal.docker_failure, then passes with exact safe fields,
original exit2 and no injected SECRET string. Inner tests cover connect/send/receive,
idle_before/idle_after/final budget, rejected sensitive routes/oversized bodies,
elapsed clipping, exact metadata types/keys/enums, hostile dict/key subclasses,
cycles, excessive ancestry and diagnostic-clock failure. Ordinary shape remains.
The existing real private-handoff process test executes lost/malformed copy and start
responses and automatic finally cleanup: outer cleanup_unresolved is unchanged,
original container_archive/container_start receive diagnostics survive, the peer is
closed and no delete/replay occurs.

The old Docker-gate timeout test used a finite clock-call list. Its clock fixture now
sets the same6s elapsed value during recv and returns that state for every clock read;
the same5s deadline and original docker_timeout assertion remain. This ties expiry
to receive rather than incidental clock-call count, including added observation calls.
No expected rejection or production deadline was changed.

## Pre-review source actual qualification

Existing commands use this form; modes and run IDs below identify each immutable record:

```sh
python3 platform/deployment/.local/pinned-cli-execution-qualification/verify-local.py MODE RUN_ID
```

The retained local wrapper SHA256 is
`1c5d32b7f6c3253f6aee2eefc57896daa50eab65ee12e857ccda01473a6a88dc`.
It records timing, source receipts and selected running inventory around existing
tracked owners. The direct clean-checkout commands do not require that ignored file:

```sh
KDG_RUN_ID='<fresh-canonical-lowercase-UUID>'
python3 platform/deployment/dev.py prepare --target platform/deployment/environments/kdg-local.json --run-id "$KDG_RUN_ID"
python3 platform/deployment/toolchain.py qualify --target platform/deployment/environments/kdg-local.json --run-id "$KDG_RUN_ID"
python3 platform/deployment/images.py qualify --target platform/deployment/environments/kdg-local.json --run-id "$KDG_RUN_ID"
python3 platform/deployment/tests/qualify_startup.py --target platform/deployment/environments/kdg-local.json --run-id "$KDG_RUN_ID" --control CONTROL
python3 platform/deployment/dev.py up --target platform/deployment/environments/kdg-local.json --run-id "$KDG_RUN_ID"
```

Replace CONTROL with the tracked qualifier argument corresponding to each mode:

| Wrapper mode | CONTROL |
| --- | --- |
| backend | pinned-cli-postgres-cli-db-backend |
| catalog | pinned-cli-postgres-auth-catalog |
| auth-job | pinned-cli-postgres-auth-migration |
| poststart | pinned-cli-postgres-auth-boundary |
| initialized | pinned-cli-postgres-initialized |
| persistence | pinned-cli-postgres-persistence |
| proof | pinned-cli-postgres |
| bootstrap | postgres-bootstrap |
| controls | guarded-fresh |

Use the existing [runbook](DEVELOPMENT.md) for prerequisites, retained-resource custody
and expected refusal meanings. Exact selected tools/images and synthetic-only scope
remain binding.

Run A = `28a98246-e095-4c4e-8f3f-f837143d9bd9`.
Run B = `567e8619-cb2d-4b7c-9a1e-71ef023193a8`.
Both bind the same25 source files, approved target and5 implementation/test file hashes.
Preparation/toolchain/images pass on A0.079/28.835/78.801s and B0.064/17.975/83.290s.
The existing image qualifier uses fixed2s request spacing within its original180s
budget; exact publisher identities and pins remain. No floating replacement is used.

| Run | Mode | Result/seconds | Record SHA256 |
| --- | --- | --- | --- |
| A | `backend` | PASS 72.695s | `e78cdb33f73a994fb9de24627f6d182c33a8c4a6597d785fef8739e30437a4bc` |
| A | `catalog` | PASS 92.538s | `69e0a557ae02aa6be0ce0ba3176752204d376829c52b1015c96759fea18cd441` |
| A | `auth-job` | PASS 102.125s | `b429bfdd13b9690835d86f13c74e2e811ec960d05b2aaf38ae331884f9bcd9e7` |
| A | `poststart` | PASS 88.793s | `300b42ea778f5302c2d93a80e6303d5084c0f776a99841a394936f499be0b85b` |
| A | `initialized` | PASS 103.692s | `7d3cc6f9a47c3c67517d968945253770bf6858cf5d90e91848b2375b792b05d5` |
| B | `persistence` | PASS 90.896s | `ffe762b0bddc871246374ba29c49a8ebe0399cb6d7ec9ff22a694bcbf5e55c7a` |
| B | `proof` | PASS 100.956s | `a14028868b5302990ca81a05731736a51a16be909ca50501a20de977ee261945` |
| B | `bootstrap` | PASS 32.944s | `bd578d1b73456b92fa7c01a6dc17a219ae971da04d82e4160e9ab0eb2dd0ad87` |
| B | `controls` | PASS 110.701s | `72717a53c211ad42c621c15e494b8fa2c8f518b48097e82c21b3bf68ef181a31` |
| B | `up` | Expected refusal 0.049s | `47871d50fd065c3cdc47abf5d688f3aa22a0f38468582e0f1741b560e37d6e17` |

All controls preserve13 receipts/config files. Successful output has no docker_failure;
full runtime/setup remain false. Backend observes actual backend presence/departure and
Auth catalog/job; persistence proves owner recreation, same cluster/run marker and
both shutdowns; first-start/bootstrap prove existing health/catalog/shutdown/cleanup.
Guarded control proves the synthetic boundary and deliberately refuses first start.

Running inventories match except selected concurrent Deals changes: A/catalog records
benchmark replacement; A/poststart four service additions; B/controls adds bench/db/
redis, no removals. Selected records concurrent-docker-deltas-current.json and
resume-controls-inventory-delta.json retain identities. ENV does not act on these
resources or establish the initiator/cause of those concurrent changes.

## Preserved failure and approval interruptions

A/persistence refuses docker/docker_timeout44.997s, exit2; record SHA256
`44a8ec5999997b14d1a9131abc4e9d5259b54731e10e1ee9589f04594f203ceb`.
All13 receipts and running inventory match. No docker_failure is attached; the record
cannot identify a failed exchange or owner check. This is not a PASS or proof of the
same cause as older timeouts. B's later pass does not explain or overwrite it.

Exact read-only inspection finds no matching database container or volume references;
the labeled database volume and empty bridge
`aa642e43c489f140d27ff3bb265618d44877b5dff4ee46ed4972106673d541fe` remain.
Selected resource-state record SHA256
`5ce613151c91796695f818fa7872a3e64640301bb3e01451009541cfab77bc18`.
Both resources remain preserved. Labels/inspection do not restore custody or authorize
removal, replay or adoption. All older failures/diagnostic resources remain untouched.

Several requests fail before execution because automatic approval review reports model
capacity or exceeds its deadline. Exact attempts are retained in ignored qualification
records and append-only memlog. Later standalone bootstrap/controls/up requests gain
approval in approximately2–5s; request size causing earlier failures is unproven.
Distinguish approval wait from test runtime; do not bypass approval or loosen runtime
deadlines. No new user permission is needed for the existing authorized scope.

## Pre-review regression and review

The existing unchanged diagnostic runner attempted the full deployment suite for B:

```sh
python3 platform/deployment/.local/pinned-cli-execution-qualification/verify-local.py tests 567e8619-cb2d-4b7c-9a1e-71ef023193a8
```

The runner reaches its900s outer limit before final summary. Retained log SHA256
`6e7a1110caf899b654c6bfb4c661192c77fc98c13c5a68fccdfff77b5dd8a4ab` contains
exactly581 pass marks plus two expected synthetic-command messages, no other output.
Frozen discovery identifies579 completed tests before the two final modules, then two
completed test_volumes tests. No pass is claimed for the interrupted test.

```sh
PYTHONPATH=platform/deployment/tests python3 -m unittest test_volumes test_wireguard
```

Both final modules PASS58 tests14.692s, including the interrupted test. Thus all637
unique discovered tests pass across partitions (579+58); two tests repeat. This is not
a completed single-process run. Original timeout/log and exact discovery/test hashes
remain in full-regression-outer-timeout.json and regression-partition-manifest.json;
regression-tail-result.json records the standard unittest result. No assertion or
runtime deadline changes. Independent review remains pending; no completion commit.

## Impact decisions

- Scaffold: existing development Docker transport/error output and startup qualifier
  tests enhanced. No new generator, runtime service, logger or runner.
- Shared UI: none; operator JSON from existing local tooling only.
- Agent context: existing privacy, ATDD, custody and owner instructions suffice.
- Documentation: this evidence, DEVELOPMENT.md and KDG handoff/memlog updated.
- ADR: apply ADR0023 and existing lifecycle/release decisions; accepted ADRs unchanged.

## Preserved boundaries

TypeScript7.0.2, mail15484, approved target, routes, lifecycle deadlines and ownership
remain. Concurrent Leave/PtS/Expense/brainstorming changes and index are preserved.
Full Auth/setup, public lifecycle/runtime, ENV/P1/SERVICE consuming scaffold and
Identity/Access/WRITE/server KDG gates stay open. No Leave/editor, production migration,
account/access/grant change, provisioning, deployment, push or real-data pilot use.

## Reviewed-source verification

All three independent review layers complete. Blind8 and edge1 findings are individually
triaged in the Build; verification-gap layer finds none. The initial observation-clock
read moves inside exchange's existing try/close handler, with a RED-then-GREEN regression
that preserves original exception, closes existing stream and refuses reuse without
invented metadata. Root session26 PASS0.551s and gate15 PASS1.412s. The first root attempt
inside the restricted sandbox cannot bind private Unix sockets; its permission errors
are not a source failure, and the same tests pass with normal authorized permissions.

Reviewed-source run C = `aa31b4ab-0a8d-4aaf-a119-52a3c24ddde1`.
Prepare0.068s/toolchain30.121s/images79.352s PASS. Actual backend PASS96.723s,
13 receipts unchanged; record SHA256
`d63919362396f8fcb17814be80973fbe9758b3f23985c03983c0bb18ee30ef9f`.
Selected concurrent inventory deltas (Deals benchmark replacement/regional HTTP removal)
are retained in reviewed-backend-inventory-delta.json; ENV does not act on them or
establish their initiator. Public up expected exit2/runtime_adapter_unqualified0.052s,
runtime_ready=false. A/B controls remain pre-review evidence, not relabelled C results.

Reviewed-source full638 completes666.470s with one existing no-eof witness failure:
len(descendant)=0 instead of1, after expected timeout/prefix/connection/elapsed checks.
Log SHA256`90438f7acca156a18796611496303f60775f924ecafe98790f3a94819b1b049b`;
record SHA256`68ea0061ab4600e8fee4e3c3d2cee97e2cd3c784a39dfa11e590b8a80825860f`.
The exact unchanged nine-case test then PASS10.422s:

```sh
python3 -m unittest discover -s platform/deployment/tests -p test_resources.py -k test_integrated_private_handoff_adversaries_and_drip_deadline
```

One unchanged full638 rerun PASS638.108s, no skips. Existing command:

```sh
python3 platform/deployment/.local/pinned-cli-execution-qualification/verify-local.py tests aa31b4ab-0a8d-4aaf-a119-52a3c24ddde1
```

Retained deployment-tests-2.log SHA256
`4140987ffc772fc32b47e922dea958b4ca4cd898eeacfbd8244ee46784531946`;
result record SHA256`f6a538f4ea2e9c41eae1d0dacccc16735c40f1c0abaa071111723862ba0f25ab`.
This does not explain the earlier failure or establish change attribution. No test
assertion, runtime deadline or900s wrapper limit changed. All prior diagnostics,
failed logs, uncertain resources and investigations remain preserved.

Two findings are deferred: a pre-existing close failure can mask a transport error;
and medium-unverified divergent explicit/implicit exception ancestry needs a reachable
owner sequence before attribution changes. Other low/speculative findings are rejected
with individual reasons. Direct tracked command mappings above fix reproducibility
without introducing a runner or changing runtime behavior. This bounded diagnostic
increment is accepted; enclosing ENV/runtime/dependent work remains incomplete.
