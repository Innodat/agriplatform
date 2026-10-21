# Protected application registration evidence

2026-10-21. Implements the approved bounded
[specification](../../_bmad-output/implementation-artifacts/spec-access-a-application-register.md).
Three independent review lenses completed; confirmed findings were patched and
root verification passed: 1210 affected tests, 18 fresh native groups, separate retained
inspection, real isolated CLI receipt lookup and both composition checks. The disposable
runtime stopped normally with data/resources preserved. ACCESS-A/B consumer activation
remains closed.

## Change and owner boundaries

Access0004 adds local operator principals/authorities and immutable operation/event
storage, exact protected command/lookup routines, and database-enforced linkage from a
new application through its created outcome to its required event. Created applications
are disabled revision1 with original-session executor and server UTC attribution.
Existing applications return unchanged/current revision without mutation or event.
Existing registry UPDATE/DELETE/TRUNCATE refusal remains enforced.

The typed adapter and isolated CLI execute only `application.register` under explicit
`--owner access`. Other parsed registry commands refuse before target/connection access.
Receipts expose `{app_id}`, decimal revision and event UUID/null, never payload or
fingerprint. Lookup requires explicit app and current authority; missing means unresolved.
Complete versioned SHA256/JCS input and the Access-local retry namespace prevent changed
input reuse. Retry-lock timeout alone means busy; authority/app waits are unavailable.

Separate restricted LOGIN/NOLOGIN roles are explicitly prepared, without authority seeds.
The previously staged `access_command_owner` is validated and preserved; Access receives
its own exact migrator SET edge. Identity's mutable metadata helper validates this exact
bundle and local Access0004 catalog before excluding only Access-owned dependencies from
its historical view. It matches `schema access` exactly, preserving `access_evil` refusal.
No Identity raw-table grants, cross-owner FK, historical migration/reference changes,
real accounts, enablement, grants or consumer activation are introduced.

A bounded Access-only synthetic namespace derives a fresh `acop_<actual run UUID>_<8hex>`
database and `access-operator-<8hex>.json` inside the actual retained native run. Existing
canonical debug DB/descriptor and private Access secret are preserved. Identity target
behavior remains unchanged. The qualification fixture itself uses protected file reads,
closed inventories, exact run-derived namespace, approved loopback port/login/database,
and refuses URL query/fragment/options before any connection.

## RED and focused verification

Root observed the initial CLI/native exact3 acceptance RED before source edits. Agent
focused RED then produced five failures for missing adapter/executable Access routing,
and a separate unknown Access0004 history failure. The latter preceded baseline-helper
implementation but followed the initial SQL draft: migration-specific unit RED did not
precede every SQL draft line. Root acceptance RED still preceded all implementation. Existing Identity CLI/target behavior
was characterized while adding Access routing. The old parser test's blanket Access CLI
refusal was intentionally superseded only for selected application registration;
Identity refusal and unsupported Access command refusal remain covered.

A genuine Identity18 controlled repeat in the reviewed isolated integration database
first failed `identity_target_role_unsafe` after explicit Access role preparation. The
mutable exact-bundle extension makes that genuine repeat pass. Historical sources and
reference receipts were preserved.

Canonical interpreter:
`platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python`.
Earlier pre-review focused command (183 passed on that source):

```sh
"$KDG_PY" -I -m pytest -p no:cacheprovider services/access/tests/test_application_register.py services/access/tests/test_access_registry_storage.py services/access/tests/test_operator_cli.py services/access/tests/test_operator_target.py services/access/tests/test_access_operator_input.py -q
```

The final test-file changes add pure fixture-refusal cases after the earlier175-pass
run. Observer/admin connections use bounded connect/statement/lock/idle/transaction
settings on the pinned native PostgreSQL17 target.

## Historical native candidate frame and traceability

Pre-review candidate frame (historical source only): private
`platform/deployment/.local/identity-baseline/application-register-candidate-20261021/`
on actual retained native run `99b7231c-0a5b-4bdb-98e8-3329564c526a`, with13 fresh
synthetic databases. Its bootstrap verifies a stable synthetic `service` actor/key under
Identity ownership before supplying the UUID to Access mappings. It creates no Auth
account, membership, employee or app grant. Access never reads Identity actor tables.

Fresh preparation records the complete70-source inventory before/after execution, owning bootstrap scripts,
Auth-helper definitions, private log hashes and immutable source custody. Qualification
rediscovers the complete executed source inventory at completion. Retained snapshots
include forced-RLS grant rows plus table/column/constraint/index/trigger/function/schema
ACL/default/role state. No prior frame, receipt or resource is reset or pruned.

| Requirement | Native candidate assertion |
| --- | --- |
| Clean/1/2/3 upgrade and preserved legacy data | prepare_cases; nonempty forced-RLS grant assertions; exact known catalog |
| Disabled revision1, executor/time, atomic event/outcome | functional; exact new row/event/receipt assertions |
| Existing current revision | exact3 preexisting revision7 returns unchanged/null event |
| Same retry, changed input and unresolved/wrong-app lookup | functional; same receipt, safe conflict/denial, no effects |
| Exact/wildcard authority and disabled/revoked mappings | functional; current authority guards execute/replay/lookup |
| Concurrent retry/application effects | concurrency; both connections witnessed waiting before lock release |
| Retry/authority/app lock classifications | concurrency; bounded waits and busy only for retry lock |
| Lost acknowledgement and revoke during wait | real commit followed by injected lost response; durable lookup; observed wait then revocation/denial |
| GUC spoof and role/raw DML attacks | response_loss_and_authority_wait and attacks; exact executor and expected SQLSTATEs |
| Required evidence and rollback | event insertion failure and application-without-evidence fail atomically |
| Unknown/default/catalog/ACL drift | drift and catalog_adversaries; complete unchanged snapshots on refusal |
| Inherited named default grantees | rollback-only candidate SQL proof strips new-object ACLs; preserves defaults; controlled route separately refuses defaults |
| Trigger/function/extra role/foreign schema | rollback-only exact metadata adversaries; Identity18 rejects extra edge and access_evil USAGE |
| Isolated CLI and environment resistance | real execute/lookup; exact owner target/receipt; ambient libpq variables ignored |
| Identity ownership integration | genuine Identity18 controlled repeat after Access4, no raw cross-owner grants |
| Retained known head | retained; exact metadata checks without business changes |

Execution commands:

```sh
"$KDG_PY" -I -B platform/deployment/.local/identity-baseline/application-register-candidate-20261021/bootstrap_run.py
ACCESS_QUALIFICATION_DIR="$PWD/platform/deployment/.local/identity-baseline/application-register-candidate-20261021" "$KDG_PY" -I -B services/access/tests/qualify_application_register.py --all
ACCESS_QUALIFICATION_DIR="$PWD/platform/deployment/.local/identity-baseline/application-register-candidate-20261021" "$KDG_PY" -I -B services/access/tests/qualify_application_register.py --verify-retained
```

The pre-review candidate aggregate passed all15 recorded groups against its unchanged
70-source preparation/execution closure; its separate retained invocation also passed.
Review fixes below change that source. Those receipts remain historical and do not
verify the current patch. No new frame was prepared and no aggregate/retained stage
was rerun during this focused follow-up; root owns final fresh native verification.

## Review fixes and focused follow-up

- Restricted roles now reject effective foreign schema/table/column/sequence and
  callable privileged-function authority. The catalog-only guard preserves narrowly
  identified existing public/bootstrap privileges and exact Identity target routines;
  no broad foreign-schema exemption or new business-data grant is introduced.
- The adapter rearms remaining statement time before COMMIT and checks its deadline
  after commit returns. A delayed successful commit becomes an uncertain outcome if
  late; it is not rolled back or acknowledged as an on-time response. An in-process
  clock cannot cancel network COMMIT; the unchanged CLI process bound and authorized
  receipt lookup remain necessary.
- Function verification now compares probin and raw argument type/mode/name arrays.
- Native cases were added for malformed direct SQL arguments/UTF8/duplicate,
  noncanonical/oversize envelopes; witnessed changed-input concurrent reuse; disabled
  principal replay/lookup; exact persisted reason/evidence; and rollback-only foreign
  grants for every restricted role. Root executed these assertions in the fresh final frame below.
- The owner runbook now includes concrete private password preparation, verified
  Identity actor evidence, app-bound operator mapping, read-only investigation and
  controlled resume without reset, automatic privilege repair or new tools/lifecycle.

The delayed-commit unit RED reproduced two failures before the runner fix (33 other
focused cases passed). Focused follow-up passed **83 tests** with plugins/cache disabled:

```sh
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$KDG_PY" -I -B -m pytest -p no:cacheprovider services/access/tests/test_application_register.py services/access/tests/test_access_registry_storage.py -q
```

This includes execute/lookup refusals for busy caller transactions, unsupported isolation
and both autocommit indicators, with zero SQL/commit/rollback and preserved caller work;
late-commit behavior; exact raw function metadata drift; all restricted roles' foreign
privilege refusals and narrow native baseline allowance; and direct-SQL matrix coverage.
It does not substitute for executing the new native assertions. Historical source,
receipts and fixtures remain preserved. Root verification below used a fresh frame.

## Preserved attempts and limits

`application-register-20261021` retains initial role/preparation failures and command
fixture debugging. The existing target-projection command role was discovered and
validated rather than replaced; a failed empty database remains for inspection.
`application-register-final-20261021` passed the earlier narrower matrix but had not yet
verified its arbitrary synthetic actor in Identity; it is not attribution proof.
`application-register-reviewed-20261021` includes corrected actor setup and stronger
matrix, with an explicit test-fixture function-owner assumption failure retained.
`application-register-reviewed2-20261021` passed all15 groups on its original source,
before the later protected-fixture/URL-isolation improvement. These frames are historical
candidate evidence and are not relabeled as current-source proof.
`application-register-reviewed3-20261021` additionally passed all15 groups after
fixture-isolation correction; the final candidate extends its source witness to include
the target-validation schema and imported toolchain module.

No production/provision/deploy/pilot/push, reset/prune, real access, Leave/editor or
additional command activation was performed. The selected synthetic scope proves
owner-local configuration/recovery only; permission/entry registration, enablement,
grants, ACCESS-B and coordinated consumer activation remain later work.

## Final root verification — 2026-10-21

Current-source frame: private
`platform/deployment/.local/identity-baseline/application-register-final-reviewed-20261021/`.
Fresh sequential preparation passed on the same actual authorized disposable run, using
13 new databases and a new bounded CLI namespace. Its stable synthetic service actor was
verified under Identity ownership before Access mapping. The bootstrap witness, aggregate
and retained result inventories match the unchanged **70 executed sources**; prior
witnesses were preserved without rewriting.

Root executed these commands with the canonical interpreter above:

```sh
"$KDG_PY" -I -B platform/deployment/.local/identity-baseline/application-register-final-reviewed-20261021/bootstrap_run.py
ACCESS_QUALIFICATION_DIR="$PWD/platform/deployment/.local/identity-baseline/application-register-final-reviewed-20261021" "$KDG_PY" -I -B services/access/tests/qualify_application_register.py --all
ACCESS_QUALIFICATION_DIR="$PWD/platform/deployment/.local/identity-baseline/application-register-final-reviewed-20261021" "$KDG_PY" -I -B services/access/tests/qualify_application_register.py --verify-retained
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$KDG_PY" -I -B -m pytest services/access/tests apps/pts/tests/test_release.py platform/deployment/tests/test_migrate_adapter.py -q -p no:cacheprovider
"$KDG_PY" -B tools/py/run_compose_supabase.py --check-only
"$KDG_PY" -B tools/py/run_compose_supabase.py --identity-authority owned --no-seeds --check-only
```

All **18 native groups passed**. Separate retained verification passed with unchanged
catalog/data snapshots and exact known-head checks. A further root invocation of the real
isolated `operator_cli.py outcome --owner access` using the final namespace descriptor
returned exactly the aggregate's committed receipt (`root-cli-verification.json`). The
native proof includes 18 malformed direct-SQL cases, a witnessed changed-input race,
disabled-principal execute/replay/lookup, distinctive persisted reason/evidence, and
rollback-only schema/table/column/sequence/privileged-function grants for all three
restricted roles. These extend the requirement matrix above on current source.

The affected regression passed **1210 tests in 34.16s** (`root-regression.log`). Both
composition check-only routes passed without changes (`root-compose-bridge.log`,
`root-compose-owned.log`). Root normally stopped the actual disposable run through
`dev.py stop --target platform/deployment/environments/kdg-local.json --run-id
99b7231c-0a5b-4bdb-98e8-3329564c526a --supabase <pinned absolute CLI>` before broad
regression; result was `completed`, `runtime_ready=false`, project
`agriplatform-kdg-mbcjHApbS9uY6DMpVkxSag`. No reset or resource removal occurred.

All 13 review findings have individual verdicts in the spec: 11 patched findings
(including the duplicate foreign-privilege report), two low findings rejected with
specific evidence, none deferred. The shared CLI process timeout/termination mechanism
is verified by its existing real-process tests; native Access separately verifies real
postcommit response loss and recovery. No new Access-specific termination fixture was
added. Identity's exact Access dependency metadata validation intentionally receives no
cross-owner ledger reads. Scoped whitespace, the frozen intent and preservation checks
for all 41 historical files and 13 snapshotted concurrent files passed.

## Five impacts

- Scaffold: extend existing trusted target, owner migration and native evidence patterns;
  no generic provisioning/catalog framework or new runtime lifecycle.
- Shared UI: no impact; no browser/admin interface.
- Agent context: no instruction changes; existing owner/ATDD/release rules apply.
- Documentation: owner runbook, this evidence, mutable substrate and KDG handoff updated.
- ADR: existing accepted decisions suffice; no accepted ADR edits.
