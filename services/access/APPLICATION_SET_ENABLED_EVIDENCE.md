# Protected application enablement evidence

This item implements the [approved specification](../../_bmad-output/implementation-artifacts/spec-access-a-application-set-enabled.md).
Access0007 adds `application.set_enabled`; no consumer activation, organization admission,
grants, infrastructure deployment, real-target execution or broader readiness is claimed.
Historical migrations/references and historical evidence remain source-bound and unchanged.

The protected adapter reuses strict parser/JCS/SHA256, the idle READ COMMITTED runner,
bounded isolated CLI, original-session authority and durable compact recovery. SQL checks
typed arguments against exact canonical bytes, including reason/evidence. Row/evidence
triggers prove transitions, actor/time and required event; they make no hash inversion claim.

## RED and focused checks

Root retained `set-enabled-red-20261021`: unsupported CLI/native42883. The implementation
agent then ran the new `services/access/tests/test_application_set_enabled.py` before
implementation: 3 failed for missing execute dispatch, changed receipt and7 catalog.
After implementation those3 passed. The affected input suite intentionally evolves its
closed Access execution assertions while retaining strict parser and Identity refusals.

Owner Python: `platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python`.
Final pytest commands explicitly set `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` and use
`-I -B -m pytest -p no:cacheprovider`. `services/access/tests -q`: **1255 passed in50.55s** during
implementation. Final source checks and native result references are recorded below.

## Native proof and traceability

`services/access/tests/qualify_application_set_enabled.py` inherits the application,
permission and entry matrices and adds the following. Bootstrap uses the existing
reviewed scripts, fresh namespaces and source custody in the approved disposable run;
old secrets/resources/witnesses are preserved. `--all` is single use; retained verification
checks matching aggregate source, state and exact catalogs before recording success.

| Requirement / matrix rows | Test or native method |
| --- | --- |
| Typed changed/unchanged receipt, strict revision/event/target closure, dispatch | `test_application_set_enabled.py`; input and CLI suites |
| Enable/disable/re-enable, stale including unchanged, missing, attribution, exact transition, original replay, all four namespaces | `enablement_functional` |
| Different legacy creation/update actors, max unchanged/overflow, populated6 upgrade, genuine previous6 adapter, populated7 repeat | `prepare_cases`, `enablement_legacy_max_previous` |
| Narrow/wildcard/wrong command/app/original login, disabled/revoked principal/authority | `enablement_authority`, `enablement_concurrency_recovery` |
| Duplicate/distinct/changed concurrent retry, same expected revision, register contention, busy only retry, lost COMMIT, witnessed revocation after wait | `enablement_concurrency_recovery` plus inherited matrices |
| Strict SQL/JCS/boolean/revision/isolation/lookup, raw DML/GUC, independent row/outcome/event attacks, exact guards, rollback | `enablement_attacks` plus inherited matrices |
| Exact clean1..7 upgrade/repeat, unknown/default/role/catalog/source refusal, Identity18 catalog-only selection | `prepare_cases`, `enablement_catalog`, inherited adversaries, `integration`, `retained` |
| Real isolated CLI typed execute and exact-target recovery | `enablement_cli` and inherited CLI matrices |

The actual6 fixture is migrated explicitly to6, populated with all three previous
commands and retained receipts, then upgraded to7. It is not a default-head fixture
relabeled6. Legacy/max rows are inserted at3 and upgraded with guards enabled at7.
Previous6 adapter bytes are captured independently in
`set-enabled-previous-20261021/bootstrap_previous_entry_adapter.py` and hash-pinned by
qualification; production dependencies do not import prior clients.

Failed development attempts remain in `set-enabled-dev-20261021` (sandbox local socket
refusal), `set-enabled-dev2-20261021` (Access7 trigger attachment after premature function
EXECUTE revocation; corrected ordering). A rollback-only exact-upgrade/catalog probe
confirmed the correction. `set-enabled-dev3-20261021` passed inherited checks and new
functional/legacy/authority/concurrency recovery, then its missing-event injection met
the deferred row guard before the event guard. The test now forces only the event
constraint before COMMIT to prove its exact refusal independently; a separate valid
owner update without evidence proves the row guard. No expected behavior was relaxed.
`set-enabled-dev4-20261021` then passed every enablement stage and CLI; its final
Identity18 repeat found the new column-level UPDATE dependency was missing from the
post-validation dependency exclusion. The verifier now excludes exactly `column enabled
of table access.applications` only after full Access metadata/ACL verification. A focused
test retains other column dependencies; no Access table/history reads or grants were
added. No old proof database or failure evidence was reset or pruned.

## Delivery impacts

- Scaffold: the existing owner command/receipt/catalog qualification fixtures now prove
  the mutable application pattern. No generic generator/configuration engine is added.
- Shared UI: no browser/UI surface changes; no reusable UI promotion is warranted.
- Agent context: existing owner isolation, release safety and attribution instructions
  remain sufficient; no AGENTS change is required by this feature.
- Documentation: owner runbook/evidence, registration guidance, Identity metadata notes,
  execution substrate, KDG checkpoint and deployment guidance updated in this item.
- ADR: no accepted decision changes; this implements existing protected mutation,
  availability, attribution, transaction and release contracts. No superseding ADR needed.

## Limits

The delivered single-event subset is retained. This proof does not establish effective
access, organization enablement, grant commands, consuming application behavior or a
real release. The existing bootstrap portability follow-up remains deferred. A client
clock cannot cancel a blocked network COMMIT; isolated process bounds and authorized
same-operation lookup remain the recovery contract. Final review/normal stop/commit
belong to root after source-frozen handoff.

## Executed implementation frame before review extensions

`set-enabled-dev5-20261021` is the fresh implementation acceptance frame in approved
synthetic run `99b7231c-0a5b-4bdb-98e8-3329564c526a`. Sequential bootstrap custody
passed with **79 unchanged executed sources**. Native `--all` passed **39 stages**;
`--verify-retained` then passed with matching aggregate source and complete retained
catalog/data snapshots. All actual databases, private targets/secrets, native resources,
failed attempts and source witnesses remain preserved for root review. Runtime readiness
remains false. Root normal stop and scoped commit are intentionally pending handoff.
Some inherited stage labels retain their historical Access4/5 delivery names; the
current installed catalog is exact Access7, while actual populated6/pre-upgrade behavior
is separately asserted before its7 migration.

Exact commands from the repository root (owner Python path above):

```sh
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python -I -B -m pytest -p no:cacheprovider services/access/tests -q
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python -I -B -m pytest -p no:cacheprovider -o pythonpath=. apps/pts/tests/test_release.py platform/deployment/tests/test_migrate_adapter.py -q
ACCESS_QUALIFICATION_DIR=/home/ck/repos/innodat/agriplatform/platform/deployment/.local/identity-baseline/set-enabled-dev5-20261021 platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python -I -B services/access/tests/qualify_application_set_enabled.py --all
ACCESS_QUALIFICATION_DIR=/home/ck/repos/innodat/agriplatform/platform/deployment/.local/identity-baseline/set-enabled-dev5-20261021 platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python -I -B services/access/tests/qualify_application_set_enabled.py --verify-retained
python3 tools/py/run_compose_supabase.py --check-only
python3 tools/py/run_compose_supabase.py --check-only --identity-authority owned --no-seeds
```

Results: **1257 Access tests passed in50.59s**; **7 PtS release/migrate-adapter tests
passed in0.24s**; both composition dry runs exited0 without changing files. The initial
isolated PtS invocation without `-o pythonpath=.` failed collection because `tools` was
not importable under `-I`; the corrected command above passed. No dependency or import
path implementation was changed to dismiss that collection issue.

All **46 historical hashes** from `/tmp/set-enabled-preservation.json` remain unchanged.
Pre-existing tracked/untracked work is preserved; concurrent Scribeswell artifact edits
were observed and left alone. `git diff --check` passed. This is no repository-wide
build/CI/readiness claim.

Source and result SHA256 custody:

| Artifact | SHA256 |
| --- | --- |
| `services/access/migrations/versions/0007_application_set_enabled.py` | `ae0d5d993be92146fe19af2e335ce25fc440ea8b10c3689281bfde19c3ba8839` |
| `services/access/access_operator.py` | `e68a079128ed9631b75dac9925a798441934b90e0b98e90c6802d32a2d7955b6` |
| `services/access/operator_cli.py` | `78f591ab115e22d34d9f91b5591c55bb7ae06c5fd31efc8e4d94d0078c97e0cb` |
| `services/access/identity-migrations/identity_baseline.py` | `9df484e7e8ab034ad2e0011c52a8c8724f45e401bd1b73b5de3bcc25cea9a486` |
| `services/access/tests/qualify_application_set_enabled.py` | `3b7349896ca318176aba8c68bdea00bbebe2d17f16d713fc8394243c622f2da1` |
| `platform/deployment/.local/identity-baseline/set-enabled-dev5-20261021/bootstrap-source-custody.json` | `440584dddb1732480f8da0896da6bec5fa8f233f4210a3c17f602f19bf65e238` |
| `platform/deployment/.local/identity-baseline/set-enabled-dev5-20261021/results.json` | `c7e024a810c32ffbcef44662427621fe011d9c7ff60ca72146cffd469a5918a8` |
| `platform/deployment/.local/identity-baseline/set-enabled-dev5-20261021/retained-results.json` | `0acd070df73c9a40fc004f90397580ff364e857db927387e20cfbe680e88e2a9` |

## Review extensions and focused handoff — 2026-10-21

The implementation frame above remains historical evidence for its captured source.
The following review changes extend the qualification source; their new native execution
has **not** been claimed against that old frame or witness:

- An existing `access_migrator` original session uses its controlled command-owner SET
  edge and explicit app-bound fixture principal/authority, alongside `access_operator`.
  The exact advisory-key observer requires both original logins waiting on the held
  application lock. Same expected revision must yield one changed receipt, one revision
  conflict and one event; all mappings remain local to the synthetic fixture database.
  No new roles or credentials are prepared.
- Pending principal/authority revocation holds the original login's authority lock;
  execute and lookup are witnessed waiting there before revocation commits. They must
  deny after release with unchanged business/outcome/event snapshots. Retry-wait tests
  remain. No application-wait revocation is claimed: the command already owns the
  authority lock, preventing committed revocation during that wait.
- Functional availability transitions start with one structurally valid synthetic legacy
  grant, including its existing staged membership reference. Disable/re-enable/replay
  compare that retained row rather than proving preservation of an empty grant set.
  This adds no grant feature or storage.
- Matching-state concurrency compares complete application and event snapshots.
  Register/enable contention now witnesses independent logins blocked on the held app
  lock before release, establishing overlap.
- Independent event mutations now additionally cover after.enabled, a wrong string
  after.revision, operation_id, scope kind/id and a different existing outcome link.
  Each must reach `access_event_invalid` and roll back the snapshot. Existing outcome
  insertion attacks remain the proof for outcome-insertion rollback.
- The existing pinned actual previous5 client creates/replays/looks up permission at7
  and retains that receipt across availability toggles and head repeat, alongside the
  previous6 client proofs. The actual6 fixture is reused without duplicate seeding.
- Malformed worker tests again distinguish the fixed safe parser error from exact empty
  ValueError, checking args, rendering/redaction, context and cause through variable
  inputs before any target connection.
- The runbook now includes concrete bounded narrow enablement-authority preparation and
  exact captured-identity/revision revocation transactions, after principal/actor/app
  verification. These examples were documented, not executed on a real target.

Focused checks only, as requested by root:

```sh
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python -I -B -m pytest -p no:cacheprovider services/access/tests/test_application_enable_input.py services/access/tests/test_application_set_enabled.py -q
```

**28 passed in0.43s.** A separate owner-Python import/helper check passed without database
connections: the advisory waiter rejects one-login overlap, requires both login counts,
and splits signed-bigint -1 into its exact unsigned high/low advisory-key components.
Scoped whitespace checks passed. No new native frame/database, aggregate/retained run,
bootstrap or old-witness refresh was performed for these review changes. Root owns the
fresh final native frame, aggregate, separate retained check, broader verification,
normal stop and commit after this source-frozen handoff.

Reviewed qualifier SHA256: `ff21f7fb23cfe7292bbf0be603e0b13a0573d847b3c680520f6e2c331140a8d6`.
Reviewed worker/input test SHA256: `f1044abc69a3d689fef790da6830befb4991f228d5d27c69b53c2382dc34c32c`.

## Final reviewed root verification

Root audited the complete scoped diff and all six acceptance matrix rows. Three independent
review lenses completed; edge and verification-gap returned no findings. Confirmed blind
findings were patched through bounded test/runbook additions. Outcome-insertion rollback
already had exact guard/snapshot proof. Committed revocation during an application-lock
wait is unreachable while the command owns the authority serialization lock; the reachable
authority-wait revocation now has native proof. Per-finding triage is retained in the Build
spec. No new work was deferred; existing bootstrap portability remains deferred.

Fresh final frame: `set-enabled-reviewed-20261021`. Only existing bootstrap scripts,
helper definitions and pinned previous adapters were copied before preparation; no old
credentials, database state, receipts or witnesses were copied. Exact final commands:

```sh
"$KDG_PY" -I -B platform/deployment/.local/identity-baseline/set-enabled-reviewed-20261021/bootstrap_run.py
ACCESS_QUALIFICATION_DIR="$PWD/platform/deployment/.local/identity-baseline/set-enabled-reviewed-20261021" "$KDG_PY" -I -B services/access/tests/qualify_application_set_enabled.py --all
ACCESS_QUALIFICATION_DIR="$PWD/platform/deployment/.local/identity-baseline/set-enabled-reviewed-20261021" "$KDG_PY" -I -B services/access/tests/qualify_application_set_enabled.py --verify-retained
"$KDG_PY" -I -B /tmp/set-enabled-root-cli.py
"$KDG_PY" -B platform/deployment/dev.py stop --target platform/deployment/environments/kdg-local.json --run-id 99b7231c-0a5b-4bdb-98e8-3329564c526a --supabase "$KDG_SUPABASE"
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$KDG_PY" -I -B -m pytest services/access/tests apps/pts/tests/test_release.py platform/deployment/tests/test_migrate_adapter.py -q -p no:cacheprovider
"$KDG_PY" -B tools/py/run_compose_supabase.py --check-only
"$KDG_PY" -B tools/py/run_compose_supabase.py --identity-authority owned --no-seeds --check-only
```

`KDG_PY` is the exact owner interpreter above. `KDG_SUPABASE` is the absolute pinned
`platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/supabase/supabase`.
The independent CLI script is retained as `root-cli-check.py` in the final frame.

Results: fresh preparation PASS; **39 native stages PASS**; separate retained inspection
PASS, with complete catalog/data snapshots unchanged and **79 executed sources** matching
bootstrap before/after, aggregate and retained inventories. Independent real CLI lookup
matched the original saved enablement receipt. Normal stop returned `completed`,
`runtime_ready=false`, preserving all data and Docker resources. Final affected regression:
**1264 passed in 35.67s**, no skips. Both composition dry runs passed and changed no files.

Scoped tracked/untracked whitespace and frozen-intent checks pass. All **46** protected
historical/Identity/parser source hashes match the starting snapshot; all13 preexisting
tracked concurrent files remain unchanged. Concurrent untracked Scribeswell updates are
retained and excluded. Final `root-verification.json` records source/log hashes and the
preservation inventory. This proves the protected configuration command, not effective
authorization, hosted-CI readiness, consumer activation or any real-target change.
