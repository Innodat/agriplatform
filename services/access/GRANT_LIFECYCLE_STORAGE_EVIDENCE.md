# Staged organization grant lifecycle storage — 2026-10-22

This bounded ACCESS-A prerequisite adds compatible storage to existing organization
grants. New organization scope/revision defaults and nullable revocation/actor/update
fields support future controlled commands. Null attribution means unadopted history;
no mapping, timestamp, permission association or effective authority is inferred.
Existing IDs, original columns/defaults, nullable membership, three-PtS permission CHECK,
keys, owner writers, forced organization RLS and runtime SELECT remain preserved.

Permission registry FK/effective-row validation, exact pre-grant Identity verification,
protected assignment/revocation, writer cutover and membership-bound consumer activation
remain separate gates. This migration does not satisfy effective access checks. In
particular the old permission CHECK still refuses KDG capabilities until coordinated
adoption is delivered; it is deliberately not removed by additive staging.

## Acceptance and preservation

Before source implementation root restarted the existing authorized disposable native
run99b7231c-0a5b-4bdb-98e8-3329564c526a and used a5-second read-only query against the
retained synthetic Access9 upgrade case. It confirmed exact9 and absence of all six
staged fields. Expected acceptance RED exited1. Root source/logs are retained under
platform/deployment/.local/identity-baseline/grant-storage-20261022. No prior data changed.

The preservation snapshot /tmp/grant-storage-preservation.json records full baseline,
concurrent tracked/untracked sources and51 protected historical/parser/reference files.
All pre-existing resources, receipts, failed frames and data remain preserved. Fresh
native preparation uses the existing owner fixture bootstrap, restricted roles/secrets
and target binding with fresh databases. It creates no global roles or infrastructure.
The explicit previous9 source package is79 exact Git files from baseline
7a565562c7b5086f2f7b432358f0048c45a47efc; no historical package is relabeled as current.

## Requirement to test evidence

The native qualifier is tests/qualify_grant_lifecycle_storage.py. Fresh --all and a
separate read-only --verify-retained bind exact source/log custody. All mapped methods passed in final reviewed verification below; no preparation-only
frame is counted as aggregate acceptance.

| Requirement | Passing qualification/test method |
| --- | --- |
| Fresh10, defaults, all three legacy permissions, null/valid fields, max revision and repeat | grant_functional; prepare_cases |
| Populated9 exact original projection, mixed null/positive membership and five previous9 command receipts | upgrade_previous; previous9 |
| Named constraints/NOT NULL refusals and earlier write rollback | grant_constraints |
| Actual runtime/org/missing context, SELECT-only, operator/definer write refusal | grant_privileges |
| Exact column/constraint/default/RLS/ACL/history drift and Identity19 metadata-only repeat | catalog_and_identity; test_identity_selects_exact_bundle_from_schema_resolved_column_metadata |
| Held migration lock and injected postcondition failure, explicit forward recovery | rollback_recovery |
| Existing configure/retry/context/evidence/concurrency/late-wait behavior unchanged | inherited functional through context_and_login_boundaries matrix |
| Existing isolated CLI and exact current catalogs | cli; retained; independent --verify-retained |
| Fixed10 DDL and historical1–9 recognition; unchanged9 command SQL | test_exact_ten_retains_all_prior_versions_and_command_bytes; test_storage_is_additive_ddl_with_nullable_external_provenance |
| Optimized-Python guard and safe diagnostic preservation | focused test_qualification_* |


## Five delivery impacts

Scaffold: existing owner migration/catalog/qualifier seams extend in place. Private
bootstrap remains root fixture work, not a portable CI claim or new framework. Shared
UI: none. Agent context: unchanged. Documentation: owner runbook, this evidence, mutable
substrate/local runbook and KDG handoffs. ADR: applies existing compatible release,
structural integrity, ownership, attribution and logging decisions; no new or edited
accepted ADR. Existing shared schema/client/generator/test/runbook owners retain ownership.
Dependency baseline including TypeScript7.0.2 remains unchanged.

No production migration, real account/access changes, infrastructure provisioning,
deployment, pilot, Leave/editor, reset/prune or push is authorized or performed. Native
verification uses isolated synthetic databases only. Historical runtime proof remains
source-bound. Existing private-bootstrap portability remains deferred; no activation or
new deferral is implied by this storage prerequisite.


Root readonly runtime credential check rejected the assumption that Access owner and
runtime share a password. The authoritative retained runtime fixture secret then
passed actual read-only login. Root copies only that existing secret into protected
runtime-credential.json before source capture; no password/account/role changes occur.
The original refusal is retained separately from native acceptance.


The first nine-case preparation passed exact source custody, but root found a duplicate
configure-authority setup in the inherited rollback case before running its aggregate.
A one-line fixture correction skips that early authority; the recovery method still
creates it after migration. The original preparation/data remains unqualified and
untouched, with its exact qualifier archived in the root diagnostic frame. Fresh
preparation uses grant-storage-proof-20261022. This correction changes no migration,
catalog, command, account, credential or privilege behavior.

Implementation focused RED reported four failures before edits (old HEAD, absent10,
missing metadata selection), then final focused24 passed. Root affected regression:
1440 passed78.43s; both composition modes exit0. Native and review results are recorded
separately below; a passing unit suite does not substitute for runtime acceptance.


## Root native verification

Fresh frame: platform/deployment/.local/identity-baseline/grant-storage-proof-20261022.
Bootstrap exact source custody passed, then all20 aggregate groups passed. Separate
--verify-retained passed with all164 source bindings matching. An independent actual
runtime login additionally read both populated organizations (three rows each) under
the matching context, no rows without context, and no leaked LOCAL context afterward.
It used read-only transactions; it did not modify the retained snapshots. This supports
actual local behavior, not portable CI bootstrap or any real target readiness claim.

From repository root, exact commands use:

```sh
P=platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python
F=platform/deployment/.local/identity-baseline/grant-storage-proof-20261022
$P -I -B "$F/bootstrap_run.py" > "$F/root-bootstrap-driver.log" 2>&1
ACCESS_QUALIFICATION_DIR="$F" $P -I -B "$F/root_qualification_driver.py" > "$F/root-all.log" 2>&1
ACCESS_QUALIFICATION_DIR="$F" $P -I -B services/access/tests/qualify_grant_lifecycle_storage.py --verify-retained > "$F/root-retained.log" 2>&1
$P -I -B "$F/root_runtime_readonly.py" > "$F/root-runtime-readonly.log" 2>&1
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 $P -I -B -m pytest services/access/tests apps/pts/tests/test_release.py platform/deployment/tests/test_migrate_adapter.py -q -p no:cacheprovider
$P -B tools/py/run_compose_supabase.py --check-only
$P -B tools/py/run_compose_supabase.py --identity-authority owned --no-seeds --check-only
```

All commands exited0. The private root driver calls the qualifier's same main --all,
with safe class/SQLSTATE/source-location diagnostics only. The aggregate is single-use;
retained inspection is read-only. Regression output is retained in the original
preparation's root-regression.log; composition output is in grant-storage-20261022.
Independent review and final source/stop/commit custody are recorded at completion.


## Independent review disposition

Three independent lenses completed. Capacity required sequential launches. Edge and
verification-gap lenses returned no findings. All nine blind findings were individually
checked: eight diagnostic/verification gaps are patched; the claimed previous grant
writer client has no implemented call path (main.py only reads grants, operator assignment
stays unsupported). Supported owner SQL writes and all five delivered previous clients
are covered. The spec records each verdict. No intent gap, new public API, ADR change
or new deferral is introduced. Final reviewed verification uses a fresh accepted frame;
the pre-review passed source diff and all previous preparations remain preserved.


## Final reviewed acceptance

Final frame: platform/deployment/.local/identity-baseline/grant-storage-accepted-20261022.
Fresh preparation passed exact before/after source custody. All23 native groups passed;
a separate read-only retained invocation passed. All164 source bindings and32 generated
log/receipt digests match. The canonical79-file baseline inventory is pinned and every
file was independently checked against the declared Git commit. Actual restricted
Identity19 refused committed marker/constraint/ACL drift without changing drifted state;
only the deliberate fixture changes were explicitly restored by the qualifier. Actual
grant-table lock contention failed within its bounded timeout and recovered forward.
Both INSERT and UPDATE boundary matrices preserve whole-transaction rollback. Runtime
checks compare complete row sets from two populated organizations, then prove LOCAL
context reset. Independent root runtime inspection also passed, read-only.

Final focused storage tests:12 passed0.96s. Full affected regression:1446 passed46.07s,
no skips. Both composition modes exited0 on final sources. Use the exact commands
above with F=platform/deployment/.local/identity-baseline/grant-storage-accepted-20261022;
root-regression.log and root-compose-{default,owned}.log are in that final frame.
The original proof paragraph/commands remain pre-review evidence, preserved with their
exact source diff; they are not relabeled as final reviewed source.

All three review lenses completed. Eight confirmed findings were patched; one claim
was disproved by the absence of a previous grant-client writer implementation. No new
deferral or intent change. Five delivery impacts are recorded above. Final root custody
binds all owned files, current sources, generated logs, supplemental driver/runtime
inspection/verified actor receipt,51 protected historical sources and all concurrent
tracked/untracked bytes. No production/source/schema/client/generator/ADR ownership
boundary was changed by the qualification patches.


The native run99b7231c-0a5b-4bdb-98e8-3329564c526a stopped normally. Exact stop used
P -B platform/deployment/dev.py stop --target platform/deployment/environments/kdg-local.json
--run-id 99b7231c-0a5b-4bdb-98e8-3329564c526a --supabase followed by the existing pinned
absolute binary path under platform/deployment/.local/kdg-toolchains/
ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/supabase/supabase.
root-native-stop.log reports completed/runtime_ready=false. No reset/prune occurred;
data, volumes, receipts and all prior preparations/proof remain retained. Private
root-final-evidence.json records source/log/owned/concurrent/history/frozen audits and
the final scoped local commit. No push or real-target activation occurs.


During final custody audit, concurrent edits were observed in epics.md, Leave
implementation-plan.md/planning-handoff-e3.md and the Scribeswell studies .memlog.md/
account-access.md. Root and its implementation agent did not edit these paths. Their
current contents are preserved and excluded from the scoped commit; the private final
manifest records both starting and observed hashes. All51 protected historical sources
remain byte-identical. Concurrent document evolution is not treated as a failed source
qualification or a reason to revert another owner's work.
