# Organization grant registry compatibility bridge — 2026-10-22

Access0011 replaces the legacy three-permission CHECK with a narrow compatibility
bridge. A stored generated `registry_permission` is NULL for exactly the three legacy
PtS literals and equals `permission` otherwise. Its organization-scope composite FK
requires a registered permission. Nonlegacy active rows additionally require membership
and actor/update provenance; revoked rows can retain unknown provenance while remaining
registry-bound. Existing positive/nonnil/finite safeguards, keys, ACLs and forced RLS stay.

The nullable discriminator is temporary compatibility scaffolding, not a second permission
source. Final direct FK/global active-row integrity and removal of the carveout require
coordinated legacy adoption. A global NOT VALID FK would still reject new/updated legacy
rows before adoption; the bridge avoids that disruption without inventing PtS mappings.
Legacy values/creation history remain untouched. Storage accepts verified external IDs
without an Identity FK; it does not itself verify target/current actor/membership.

Protected grant assignment remains unsupported. Later commands must exclude the legacy
PtS literals while v1 ignores membership/revocation. Existing v1 continues its PtS-only
whitelist; no KDG or membership-safe effective reader is activated. PtS account-grant
adoption, final writer cutover, ACCESS-B and coordinated consumer activation remain gates.

## Acceptance and preservation

Baseline: eda0bbbe09eca7b7908920b1ae0eae060694dbff. Root preservation snapshot
`/tmp/grant-registry-preservation.json` records concurrent files, production sources and
52 immutable historical migrations/references. Existing client/parser/CLI SQL and historical
migrations stay unchanged. Concurrent documents may evolve; they are preserved and excluded
from the scoped commit. All prior synthetic frames, data and Docker resources are retained.

Before production edits, fresh `grant-registry-red-20261022` preparation installed
Identity19/service actor and controlled Access10. Actual restricted Access registration
created the synthetic application and organization `kdg_capture.read.own` permission.
A complete owner grant insert then failed with23514/`grants_permission_check`; exact
before/after Access snapshots matched. Expected acceptance RED exited1. Logs and its
isolated database remain retained under deployment `.local/identity-baseline/`.
Focused missing-feature RED separately failed5 tests (missing11/head10/selector).

## Delivery impacts

Scaffold: extend existing owner migration, exact verifier and qualifier seams; no generator,
service or fixture framework. Shared UI: none. Agent context: none. Documentation: owner
runbook/evidence, mutable substrate/development and KDG handoffs. ADR: existing release
compatibility, structural integrity, ownership, attribution and safe logging decisions;
no accepted ADR changes. Existing owners retain schema/client/generator/test/runbook work.
Dependency baseline including TypeScript7.0.2 is unchanged. Private bootstrap portability
remains an existing follow-up, not a portable CI claim.

All implementation and verification use isolated synthetic local data. No real account/
access operation, production migration, provisioning, deployment, pilot, Leave/editor,
reset/prune, historical cleanup or push is included. Normal native stop retains data.

Adding a STORED generated column can physically rewrite/lock its table. The existing
controlled migration timeouts and rollback/retry route apply; isolated small-fixture
qualification is not production sizing or zero-downtime evidence. No explicit business
DML, backfill or adoption is performed by the migration.

The first five-case preparation (`grant-registry-proof-20261022`) passed source custody
and actual controlled10/11 migrations. Aggregate execution stopped at the first reused
snapshot: an unbound storage helper used super() on a class outside its inheritance
chain. The failed frame/data and exact qualifier remain preserved; correcting its base
class and explicit existing seeding changes no migration or runtime behavior. It is not
counted as passing aggregate acceptance.

A read-only EXPLAIN diagnostic on the first synthetic11 frame showed that the old
privilege probe `INSERT ... SELECT *` now raises428C9 during generated-column rewriting,
before the intended permission check. No statement was executed or data changed. The
existing helper now names its four writable legacy columns explicitly, preserving42501
as the actual privilege expectation on old/new schemas. A second source-bound preparation
is retained without an aggregate claim; fresh proof follows the combined harness fixes.


## Requirement to test evidence

| Requirement | Passing native/focused evidence |
| --- | --- |
| Clean11 and populated10 preserving original columns/IDs/time and five command receipts | `prepare_cases`, `upgrade` |
| All three legacy permissions, absent registry and post11 complete→null UPDATE in both orgs | `functional` |
| Registered organization permission, active required fields, revoked history, wrong/account registry scope, generated override and rollback | `functional` with named SQLSTATE/constraint assertions |
| Actual runtime/org RLS and SELECT-only; operator/definer raw write denial | `privileges`, reused existing restricted helper with writable-column probe |
| Exact schema/history/generated expression/FK/internal-trigger/RLS/ACL drift | `drift`; `test_identity_uses_schema_resolved_generated_metadata_then_full_catalog` |
| Actual restricted Identity19 repeat on10/11 and committed generated/ACL drift refusal | `identity_repeat`, `identity_drift_refusal` |
| Relation/advisory lock and injected postcondition rollback, explicit retry forward | `failure_and_locks` |
| Source/log custody, single-use aggregate, independent read-only exact11 | qualifier main and separate `--verify-retained`; focused optimized/source/log tests |

Fresh proof3 passed all7 aggregate stages and separate retained verification. Source
custody binds 116 inputs and 20 generated logs. Pre-review full affected regression:
1469 passed in47.12s; both composition modes exited0. Latest focused checks:30 passed.
All52 historical sources and73 unchanged production/client files match the baseline;
only the two intended mutable production verifiers change, alongside new0011 DDL.

From repository root:

```sh
P=platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python
F=platform/deployment/.local/identity-baseline/grant-registry-proof3-20261022
D=platform/deployment/.local/identity-baseline/grant-registry-20261022
$P -I -B "$F/bootstrap_run.py" > "$D/root-bootstrap-proof3.log" 2>&1
ACCESS_QUALIFICATION_DIR="$F" $P -I -B "$F/root_qualification_driver.py" > "$D/root-all-proof3.log" 2>&1
ACCESS_QUALIFICATION_DIR="$F" $P -I -B services/access/tests/qualify_grant_registry_bridge.py --verify-retained > "$D/root-retained-proof3.log" 2>&1
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 $P -I -B -m pytest services/access/tests apps/pts/tests/test_release.py platform/deployment/tests/test_migrate_adapter.py -q -p no:cacheprovider
$P -B tools/py/run_compose_supabase.py --check-only
$P -B tools/py/run_compose_supabase.py --identity-authority owned --no-seeds --check-only
```

The root driver calls the qualifier's same main, exposing only selected safe exception
class/SQLSTATE/source location on failure. These preparation/aggregate commands are
single-use; source changes/failures require a new namespace. Root output stays separate
from frozen generated logs. Earlier successful or failed frames are never relabeled as
qualification of changed source. Independent review/final acceptance is recorded below.

## Independent review

Three lenses completed sequentially under agent capacity limits. Verification-gap lens
returned none. Eleven confirmed findings in ten groups concern focused-test isolation,
private-bootstrap prerequisite documentation, retained-state digest custody, exact safe
lock-failure attribution, registered grants in the second organization, permission UPDATE
recomputation, complete multirow FK rollback, partial revoked provenance, referenced-side
FK trigger drift and still-generated expression drift. All route to bounded proof/doc
patches through the same implementation agent; no runtime/DDL intent change or new
public surface. Existing private-bootstrap portability remains deferred. Pre-review
source diff and successful proof3 remain retained, distinct from final reviewed acceptance.

The reviewed `grant-registry-accepted-20261022` aggregate passed the added behavior,
upgrade and runtime cases. Restricted Identity19 correctly refused the deliberately
altered STORED expression, but restoration comparison failed. A separate fresh diagnostic
(`grant-registry-expression-diagnostic-20261022`) measured the cause: the trigger snapshot retained48 rows and differed only in
autogenerated internal RI names; all semantic catalog fields matched and
exact controlled preflight/postcondition passed after restoration. The failed frame
remains untouched. New qualifier snapshots project out only incidental generated RI
name identifiers; counts, definitions/functions/events, enabled state and user trigger
names remain protected, alongside the independent exact catalog verifier. No DB state
is normalized or repaired. Final acceptance uses another fresh namespace.

## Final reviewed native acceptance

Fresh `grant-registry-final-20261022` preparation and all8 native stages pass, followed
by a separate read-only retained invocation. All116 source bindings,21 generated-log/
selected diagnostic digests and the retained-state result digest match. Actual relation
contention records safe55P03 with `access_migration_failed_requires_reconciliation`;
only the owner advisory retry lock records `access_migration_busy` without SQLSTATE.
No production error classification or logging changed. Both FK ends and still-STORED
expression drift refuse; explicit fixture restoration preserves semantic catalog/data.
Second-org registered grants participate in the actual runtime's exact row-set checks.

Use the commands above with F=platform/deployment/.local/identity-baseline/grant-registry-final-20261022
and root bootstrap/all/retained output suffix `-final` in D. Earlier proof3 is pre-review
acceptance; the failed reviewed frame and separate expression diagnostic remain retained.
Final focused bridge checks:13 passed. All11 review findings are addressed, no new
intent/ADR/runtime change or deferral. Final regression/composition/stop and custody
results follow; private bootstrap portability remains the existing follow-up.


Final affected regression:1472 passed in37.69s, no skips. Both composition checks exited0;
outputs are `root-regression-final.log` and `root-compose-{default,owned}-final.log` in D.
Native run99b7231c-0a5b-4bdb-98e8-3329564c526a stopped normally. Exact stop uses P -B
platform/deployment/dev.py stop --target platform/deployment/environments/kdg-local.json
--run-id 99b7231c-0a5b-4bdb-98e8-3329564c526a --supabase followed by the pinned absolute
binary under platform/deployment/.local/kdg-toolchains/
ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/supabase/supabase.
`root-native-stop.log` records completed/runtime_ready=false. No reset/prune occurred;
all data, volumes, receipts, prior preparations and failed frames remain retained.
Final private `root-final-evidence.json` binds owned/source/log/state/frozen inventories,
supplemental bootstrap actor evidence,52 protected sources,73 unchanged production/client
sources and concurrent observed bytes, then records the exact scoped local commit.
Production0011/verifier bytes match pre-review accepted proof; review patches changed
only qualification/docs. No push, real-target adoption or consumer activation occurred.
