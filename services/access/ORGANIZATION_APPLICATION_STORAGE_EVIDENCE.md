# Private organization application storage — 2026-10-21

Access0008 stages empty `access.organization_applications` through the existing controlled
owner route. Its composite organization/application key, local RESTRICT application FK,
positive revision/defaults, nonnil external UUIDs and finite required attribution times
are structural safeguards. Synthetic fixture UUIDs are not verified organizations or
actors. No organization configuration execution, authority, receipt/event variant,
reader, grant, account or consumer activation is delivered.

Only access_migrator has table privileges. Owner helpers set app.org_id with SET LOCAL;
ENABLE/FORCE RLS compares each row to that current org context. Missing or different
context cannot expose a row or insert for another organization. RLS cannot distinguish
a session-level setting from a transaction-local setting; this adds no runtime/auth
guard or claim that the policy attests setting lifetime. The reused private statement
guard refuses UPDATE/DELETE/TRUNCATE, including empty/noop, UPSERT and MERGE update arms.
Protected mutability requires a later explicit migration.

The fixed verifier accepts exact clean and revisions1–8, retaining prior source pins
and revision7 enablement behavior. Exact8 additionally verifies columns/defaults,
ownership/table and column ACLs, RLS/policy, guard binding/scope/enablement, indexes,
persistence/inheritance and both ends of the new FK's four internal triggers.
Identity18 selects8 using relation metadata, then the fixed Access verifier. It gains
no Access business/history reads. Historical Identity migrations/references and all
previous evidence remain unchanged and bound to their original sources.

Use the existing restricted Access Alembic upgrade route. Unknown history/catalog or
unsafe ACLs refuse before normalization. Migration failure blocks activation; preserve
history/data/logs, release a held lock or reconcile the cause, then explicitly retry
controlled upgrade. Do not stamp, downgrade, migrate on service startup, or reverse
applied migrations automatically. No production/provider/deployment/pilot is included.

## Verification and traceability

`tests/test_organization_application_storage.py` covers additive history1–8, unchanged7
registration SQL, private migration structure, metadata-only Identity selection and
optimized-Python refusal before fixture access. Existing enablement characterization
passed5 tests before edits. Storage acceptance then failed2 tests (HEAD7 and missing
migration), before implementation. The final focused invocation passed9 tests:

```sh
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python -I -B -m pytest -p no:cacheprovider services/access/tests/test_organization_application_storage.py services/access/tests/test_application_set_enabled.py -q
```

The root independently observed the actual missing relation on retained exact7 before
source edits; its private `root-acceptance-red.log` remains under
`platform/deployment/.local/identity-baseline/org-storage-20261021/`.

The native qualifier reuses current owner fixture/URL/timeouts/migration/source custody
helpers. Root privately prepares the exact synthetic cases, including genuine Identity18
and pinned previous adapter files. Preparation and `--all` are single-use;
`--verify-retained` is repeatable and read-only. Neither invocation provisions fixtures.
The private bootstrap before/after custody witness must match current sources and logs.
Optimized Python refuses before any fixture/I/O. Explicit administrator observations
snapshot complete business rows across organizations and the policy/index/inheritance
catalog; these are observation privileges, not runtime access claims.

The retained private preparation entrypoint is invoked exactly as follows from the
repository root, before either qualifier invocation. This is the final reviewed frame's
command, not permission to rerun its consumed preparation: preserve existing witnesses,
logs and namespaces. Each subsequent source frame needs root-prepared fresh namespaces
and its own exclusive bootstrap witness/log files. bootstrap_run.py captures sources
before and after sequential bootstrap.py/bootstrap_identity18.py execution; both must
match, with successful logs bound into the passed witness, before --all can proceed.

```sh
platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python -I -B platform/deployment/.local/identity-baseline/org-storage-reviewed-20261021/bootstrap_run.py
```

```sh
ACCESS_QUALIFICATION_DIR="$PWD/platform/deployment/.local/identity-baseline/org-storage-reviewed-20261021" platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python -I -B services/access/tests/qualify_organization_application_storage.py --all
ACCESS_QUALIFICATION_DIR="$PWD/platform/deployment/.local/identity-baseline/org-storage-reviewed-20261021" platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python -I -B services/access/tests/qualify_organization_application_storage.py --verify-retained
```

| Requirement | Native qualifier method |
| --- | --- |
| Clean/populated exact1–7 to empty8; preserve rows/four-command receipts | prepare_cases |
| Composite keys/defaults/RLS/context reuse/constraint refusal/rollback/populated8 repeat | storage_functional |
| Same-key overlap/unique refusal and different-org concurrent inserts, old-state preservation | storage_concurrency |
| Populated/empty/noop/UPSERT/MERGE statement refusal; earlier insert rollback | immutable_storage |
| Operator login and controlled runtime/browser/command-owner role denials | storage_privileges |
| RLS/policy/table+column ACL/default/FK/internal triggers/guard/persistence/history drift | storage_catalog |
| Held serialization/DDL lock and injected postcondition failure; explicit recovery | storage_recovery |
| Actual previous7 adapter replay/new enablement/lookup at8 | previous7 |
| Existing enablement semantics and exact catalog at8 | inherited enablement_functional/enablement_catalog |
| Genuine Identity18 metadata integration, unchanged Access rows/catalog | inherited integration |
| Identity18 safe refusal of malformed organization FK enforcement without new grants | identity_storage_refusal |
| Exclusive per-invocation failure diagnostics; safe failure with missing/unavailable storage | isolated unit subprocess tests |
| Exact known catalogs, retained complete cross-organization snapshots and custody | inherited retained/main |

The first root native aggregate passed all controlled upgrade groups, then exposed a
fixture expectation mismatch for NULL org_id: the restricted owner receives42501 from
WITH CHECK RLS before NOT NULL. Bounded rollback-only diagnostics confirmed42501 for
access_migrator and23502/column_name=org_id for supabase_admin. The first administrator
diagnostic used the wrong credential and failed authentication without effects; both
logs remain retained, including `root-null-org-diagnostic-corrected.log`. The fixture
now asserts the observed owner RLS refusal and separately observes the administrator
NOT NULL refusal with an unchanged complete snapshot. Other NULL-column expectations
remain23502. The failed native frame is preserved; fresh namespaces/source custody are
required for the corrected aggregate. No production implementation changed.

The first root broad regression reported2 failures and1314 passes in34.52s. Both
failures were obsolete current-HEAD assertions in the permission and entry registration
suites. Historical permission, entry and enablement suites now assert their retained
revision guarantees, including explicit7 validation, without pinning the evolving
global HEAD. Their existing revision4/5/6 checks remain. The new storage suite owns
the current HEAD8 assertion. `root-regression.log` is preserved. These test-only
evolution corrections do not change production or native qualification sources.

The next native frame passed upgrades, storage/isolation/privilege/catalog checks,
recovery, previous7 compatibility and enablement, then genuine Identity18 repeat refused.
Root's bounded read-only diagnostic established that direct schema-qualified regclass
input requires Access schema USAGE for the Identity owner, while pg_class/pg_namespace
OID discovery succeeds. The new storage verifier now resolves table OIDs from trusted
catalog subqueries, including internal-FK filters, matching existing verifier practice.
OID-to-regclass text rendering retains exact association assertions without name input
resolution. No schema/role privilege was granted. A focused restricted-catalog
characterization failed before this correction; the original native frame is preserved
and a fresh source-bound frame is required.

Review follow-up adds bounded witnessed same-org/app insert contention with one
committed row and exact primary-key23505, plus overlapping different-org inserts for
the same application that both commit. Earlier rows and catalog state are preserved.
A rollback-only malformed-storage case disables one organization FK trigger, then
actual SET LOCAL ROLE identity_migrator catalog verification must return the safe
Identity BaselineError without Access schema grants; rollback preserves the complete
snapshot. Root's corrected-source genuine Identity18 positive diagnostic passed.

Failure reporting now writes only type and selected stack locations to exclusively
created mode0600 per-invocation files. It preserves prior records and emits the fixed
safe result even when fixture storage is missing/unwritable; exception/SQL/driver
payload text is omitted. Isolated subprocess tests avoid importing the qualifier into
the pytest process and changing historical CASES. The edited storage suite passed8
tests in7.77s. New native cases await the root's fresh source-bound verification.

Native aggregate, retained proof, broader regression and compose results are recorded by
the root after source freeze; until those results are added this document claims only
the focused unit results above. No root lint/typecheck or repository-wide test command
exists. General bootstrap portability remains deferred. No real organization validation
or runtime admission behavior is claimed.

## Impact decisions

Scaffold: reuse the existing Access migration/exact-catalog/qualification seams; no
new generator, generated files, schema input or dependency. Shared UI: no UI change.
Agent context: existing organization ownership, attribution and delivery gates suffice;
no AGENTS.md change belongs to this item. Documentation: this evidence plus mutable
DEVELOPMENT/substrate/KDG handoffs record the bounded increment. ADR: existing ownership,
structural integrity, release safety and attribution decisions suffice; none amended.
Existing ACCESS-A/B, external organization verification, protected configure execution,
PtS/Content adoption and coordinated KDG/consumer activation gates remain closed.


## Final reviewed acceptance

All pending root verification described above is now complete. Final fresh frame:
`platform/deployment/.local/identity-baseline/org-storage-reviewed-20261021/`.
Preparation and the15-stage aggregate passed; separate `--verify-retained` passed one
inspection stage, validating exact complete retained states and aggregate/source custody.
All82 executable/config/bootstrap source bindings match preparation before/after,
aggregate completion and separate retained inspection. Commands are the preparation and
qualifier invocations above; private logs are `root-preparation.log`,
`root-native-all.log` and `root-retained.log`. These consumed mutating stages must not
be replayed. Restart the retained native run through dev.py before read-only inspection.

Final independent regression command from repository root:

```sh
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python -I -B -m pytest services/access/tests apps/pts/tests/test_release.py platform/deployment/tests/test_migrate_adapter.py -q -p no:cacheprovider
```

Exit0, **1320 passed in42.11s**, `root-regression-reviewed.log`; no skips. Current
organization input adapter/CLI/public and direct worker pre-I/O refusals are included.
Both composition dry runs exited0 with no files changed:

```sh
platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python -B tools/py/run_compose_supabase.py --check-only
platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python -B tools/py/run_compose_supabase.py --identity-authority owned --no-seeds --check-only
```

Logs: `root-compose-default.log`, `root-compose-owned.log`. The separate corrected-frame
read-only `root-retained7-compatibility.log` confirms current verifiers still accept the
original retained Access7 and genuine Identity18 catalogs. Corrected-source diagnostic
Identity18 repeat and retained inspection passed before final review; those are labeled
diagnostics and do not substitute for this final fresh aggregate.

Three independent review lenses completed. Verification-gap returned no findings;
confirmed blind/edge findings were patched: bounded overlapping same/different-org
inserts, malformed-storage Identity refusal, unique exclusive safe diagnostics,
context lifetime wording and reproducible preparation instructions. Each finding has
its own verdict/evidence row in the Build spec. No new deferred issue; the existing
bootstrap portability prerequisite remains deferred. Failed original and corrected
frames, their logs and successful partial stages remain source-bound history.

The approved intent and all47 protected historical/Identity/parser hashes match. All85
files from the prior completed enablement proof remain byte-identical. All43 pre-existing
untracked files remain unchanged; concurrent tracked Leave epics/implementation-plan/E3
handoff edits are preserved outside this scope. Final source/log/whitespace and scoped
commit custody are retained in `root-verification.json`. No dependencies, historical
migrations/references, real organization/account/access settings or accepted ADRs changed.

Native run99b7231c-0a5b-4bdb-98e8-3329564c526a is stopped through the existing dev.py
vendor lifecycle with data retained and runtime_ready=false; `root-native-stop.log`
records its result. No reset, prune, deployment or pilot occurred. Five impact decisions
above remain binding. Next: external organization verification and protected configuration
execution; this private storage stage grants no effective access or activation.
