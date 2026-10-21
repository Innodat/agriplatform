# ACCESS-A private registry storage evidence

2026-10-21. Revision0003 stages empty applications, permissions and entry_permissions
through the existing Access owner migration. It creates no effective access, registration
command, reader, grant or application activation. Current v1 remains incompatible and
stopped for real consumers; ACCESS-A/B, coordinated PtS adoption, WRITE and server KDG
remain gated.

## Delivered behavior

Application IDs follow ASCII `[a-z][a-z0-9_]{1,63}`; permission IDs are literal ASCII1–200
bytes, including controls/DEL, without prefix or wildcard interpretation. Applications
default disabled/revision1. Revisions are positive signed bigint, required actors non-nil
UUIDs and attribution finite timestamptz. Permission scope/association unique keys and
RESTRICT FKs enforce matching application/permission entry mappings. Actor identifiers
are external references without Identity FKs; fixture attribution is not verified command
execution. Normal migrations seed no rows and preserve existing grants/legacy attribution.

Only the migration owner receives new table/function privileges. No roles, runtime
privileges, organization admission, account grants, grants CHECK/FK replacement, backfill,
generator or dependency changes are introduced. Private invoker statement guards refuse
UPDATE/DELETE/TRUNCATE, including empty/noop and alternate UPSERT/MERGE update paths,
with fixed55000/access_registry_storage_immutable. Parent-only TRUNCATE may instead fail
PostgreSQL's ordinary inbound-FK check (0A000); CASCADE/all-table variants reach the guard.
Later mutable owner commands require an explicit migration.

The existing owner route recognizes exact clean/1/2/3 catalogs and pins historical0001/2
bytes. It checks columns/defaults, constraints/indexes, ownership/ACLs, persistence,
inheritance, trigger definitions and internal FK-trigger associations/counts/enablement,
plus function body/security/settings before effects and commit. UTF8 server encoding is
required before migration effects. Unknown state refuses without normalization. Existing
serialization, bounded waits, sanitized errors and failure-blocks-activation remain;
recovery is an explicit controlled upgrade after disposition, never downgrade or startup
migration. Native PostgreSQL17 is the actual qualified target here.

## Final proof and commands

Fresh reviewed frame:
`platform/deployment/.local/identity-baseline/access-registry-reviewed-20261021/`.
Explicit preparation uses existing private fixture tooling, restricted logins and genuine
Identity18, without changing global roles. The separate internal-FK drift test uses the
existing native true-admin login, not owner-role assumptions or new administrator grants.
Before/after preparation and aggregate witnesses bind132 unchanged source/config/bootstrap
files. Completion rediscovers source inventory; retained data requires the exact validated
fixture case set. Access snapshots use bounded read-only repeatable-read transactions.

From the repository root:

```sh
KDG_PY=platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python
KDG_PROOF="$PWD/platform/deployment/.local/identity-baseline/access-registry-reviewed-20261021"
```

Preparation and aggregate already ran once; do not replay these single-use stages on
this retained frame:

```sh
"$KDG_PY" -I -B "$KDG_PROOF/bootstrap_run.py"
ACCESS_QUALIFICATION_DIR="$KDG_PROOF" "$KDG_PY" -B services/access/tests/qualify_access_registry_storage.py --all
```

Root aggregate:82 PASS records; independent retained inspection:2 additional PASS records.
Advisory contention refused in0.552s and DDL contention in3.641s; explicit recovery passed.
Retained inspection verifies aggregate source/log witnesses, exact case inventory and
Access catalog/data. Initial integration proves Identity unchanged across the upgrade;
it does not impose perpetual Identity-data immutability on later owner work.

The native run99b7231c-0a5b-4bdb-98e8-3329564c526a is normally stopped
(stop/completed, runtime_ready=false), preserving databases, volumes, resources and
receipts. Restart that retained run through existing dev.py up before repeatable inspection:

```sh
ACCESS_QUALIFICATION_DIR="$KDG_PROOF" "$KDG_PY" -B services/access/tests/qualify_access_registry_storage.py --verify-retained
```

Optimized Python refuses before fixtures/network. Fixture URLs bind the exact native
run/namespace/loopback port and owner roles; no credentials enter argv or safe output.

## Requirement-to-test evidence

| Requirement | Executed proof |
| --- | --- |
| Clean, populated exact1/exact2 upgrade; empty registry, unchanged legacy grants | clean_previous, exact1/exact2-grants-preserved-empty-registry |
| Defaults, ASCII grammar/length/control endpoints, both scopes, actor/time/revision and named FK/unique failures | boundaries, intended SQLSTATE/constraint and unchanged-state assertions |
| Existing membership NULL/1/max and invalid bigint boundaries; non-null runtime read | nullable-positive-bigint-boundaries-preserved; permissions |
| Immutable ordinary/noop/empty/multirow/UPSERT/MERGE writes and rollback | boundaries, explicit insert-before-update transaction, writable CTE and multirow CHECK cases |
| Populated repeat preserves registry/grant data, catalog and ACL | populated-registry-repeat |
| Unknown history/object/default/constraint/ACL/user-trigger/internal-FK-trigger drift | inherited refusals and registry_refusals |
| Function body, SECURITY DEFINER and RESET search_path drift | independent registry_function/security/search_path cases |
| Non-UTF8 database refuses before effects | sql-ascii-refusal in aggregate; separate encoding-review2 proof |
| Bounded lock/failure rollback and recovery | inherited recovery and exact before/after snapshots |
| Actual runtime/browser read/write/DDL/EXECUTE and owner denial | permissions; runtime login, browser selected-role SQL, effective membership/function checks |
| Genuine Identity18 catalog/data/history and ownership unchanged | inherited integration |
| Preparation/execution/source inventory and retained case integrity | source witnesses, retained inspection and focused inventory mutation tests |

Final independent regression command:

```sh
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$KDG_PY" -I -B -m pytest services/access/tests apps/pts/tests/test_release.py platform/deployment/tests/test_migrate_adapter.py -q -p no:cacheprovider
"$KDG_PY" -B tools/py/run_compose_supabase.py --check-only
"$KDG_PY" -B tools/py/run_compose_supabase.py --identity-authority owned --no-seeds --check-only
```

1075 passed in36.67s; both composition checks exited0. Focused registry/membership tests
passed61 in2.11s. Three independent review lenses completed; eight technical patch groups
were verified. All40 protected historical migration/reference/pinned-source files remain
unchanged. Existing portable CI bootstrap and intermittent subprocess timing follow-ups
remain separate; no production/provider/real-account/access/deploy/pilot or reset/prune occurred.

## Chronology and preserved attempts

Focused RED first demonstrated unknown revision3 and missing migration. The actual
missing-registry baseline replay then used isolated Access sources from
bd2e6f0156f4993fd5433d40c70249ae371564fc on a fresh database: exact2 succeeded and all
three registry tables were absent. **Draft implementation edits already existed.** Actual
RED preceded the first native0003 application, but not source implementation: strict ATDD
ordering was missed and is recorded as a process limitation, not retroactively repaired.
Baseline hashes/log/chronology remain in access-registry-candidate-20261021/acceptance-red.json.

All earlier candidate/final frames and their receipts remain historical. Candidate1
rolled back a catalog-parenthesization mismatch; candidate2 exposed an admin-session role
assumption error in the test harness. The corrected proof uses a real restricted runtime
login and browser effective-role checks. The pre-review final frame passed74 checks on
its original132-source witness; it is not presented as reviewed-source verification.
The isolated SQL_ASCII proof is retained under access-registry-encoding-review2-20261021
(encoding-proof.json, sql-ascii-isolated-native-refusal.log and access-registry-results.json).
Failed locale/import preparation attempts are preserved separately. No old mutating stage,
receipt, source witness or completed fixture was rewritten.

## Five impacts

- Scaffold: extend the existing Access migration/native qualification route, reusing
  fixture/URL/error/command/recovery/integration helpers; no parallel framework.
- Shared UI: unchanged; no app/admin interface.
- Agent context: KDG next-session records private staging and remaining command/consumer gates.
- Documentation: this evidence, mutable owner contract and runbook; prior evidence remains.
- ADR: existing decisions suffice and remain immutable. Dependency pins, including
  TypeScript7.0.2, remain unchanged.
