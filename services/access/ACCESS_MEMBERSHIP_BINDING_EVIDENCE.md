# ACCESS-A staged membership storage

Access revision `access_0002` adds nullable bigint `access.grants.membership_id` and
`grants_membership_id_positive CHECK (membership_id > 0)`. Existing opaque grant IDs,
organization/account/permission keys, permission CHECK, text creation attribution,
creation timestamps, forced organization RLS and runtime SELECT remain. There is no
default, backfill, Identity FK, permission inference or grant activation.

Current v1 ignores membership identity and remains incompatible/stopped for real
consumers. This storage increment does not close ACCESS-A/B membership-bound eligibility,
commands, registry/admission, coordinated PtS adoption or KDG activation gates. NULL must
never become a membership match. Future effective organization checks must match the
exact active organization/account/membership instance.

## Controlled route and recovery

Use the existing Access Alembic configuration and `ACCESS_MIGRATION_DATABASE_URL` with
an actual restricted `access_migrator` session. Bootstrap schema/roles separately;
Access migrations do not provision or repair them. The qualified bootstrap gives the
Access owner its schema and grants runtime schema USAGE as that owner. Both Access roles must be login roles without SUPERUSER, CREATEDB, CREATEROLE,
REPLICATION or BYPASSRLS. The owner has no database CREATE, outgoing role memberships
or effective callable authority on Identity SECURITY DEFINER routines
(schema USAGE plus function EXECUTE). Runtime has no outgoing
membership, including an owner-assumption path.

Incoming owner memberships must be absent or match the inspected native Supabase
bootstrap exactly: postgres receives an ADMIN-only edge from supabase_admin
(ADMIN=true, INHERIT=false, SET=false) and a separate SET-only edge from postgres
(ADMIN=false, INHERIT=false, SET=true). The exact administrator profiles are also
required: postgres LOGIN/NOSUPERUSER with CREATEDB/CREATEROLE/REPLICATION/BYPASSRLS/INHERIT;
supabase_admin LOGIN/SUPERUSER with those same flags. Names alone do not suffice.
This target-specific bootstrap authority is retained without global role changes;
every other incoming shape refuses. Unknown bootstrap/ACL/catalog/history is preserved and refused.

The existing environment verifies original revision1 bytes, schema ownership and exact
ACL/defaults, actual session/role, known single version row and fixed semantic catalogs
before Alembic creates history or runs DDL. It verifies final columns/defaults, constraints,
indexes, policies, owner/private ledger, triggers, routines, types and ACLs before commit.
Both grants and ledger must be permanent tables with no inheritance parent/child links.
No normalization or REVOKE-based repair occurs. Runtime table SELECT deliberately covers
the added column; runtime DML, DDL, owner assumption and private-ledger reads remain denied.
Access receives no Identity privileges. The migration has no artificial Identity SQL dependency.

A transaction-scoped owner advisory lock serializes migrations. Transaction-local
search_path is pg_catalog,pg_temp; lock timeout is3s, statement timeout30s and idle
transaction timeout10s. PostgreSQL17 additionally enforces a60s transaction timeout.
The actual selected native PostgreSQL17 target is qualified here; older supported
PostgreSQL versions have the per-statement/lock/idle bounds and require their own target
qualification. Connection attempts are bounded to5s. The qualifier bounds each migration
process to75s. Offline/stamp/downgrade paths, including programmatic stamp, refuse before
migration effects. Safe fixed errors suppress SQL/URL/business exception text.

The existing coordinator orders optional Identity before Access and stops later owners
on failure; completion alone never authorizes activation. A refused/ambiguous upgrade
requires reconciliation of the exact Access history/catalog and preserved data. Remove a
known test contention/failure only through explicit maintenance, then rerun the controlled
upgrade. Applied migrations are retained; do not downgrade, auto-reverse, reset, provision
on startup or activate an old membership-ignoring reader.

## Executed evidence

Frozen interpreter:
`platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python`.
Native run: `99b7231c-0a5b-4bdb-98e8-3329564c526a`, started through existing `dev.py up`
with the absolute pinned Supabase CLI2.120.0. Root finalization stopped it normally (`stop/completed`, runtime_ready=false),
retaining all databases, receipts and resources. No production/real-account/access action
or reset/prune is part of this evidence.

Acceptance RED was observed before implementation in fresh `accessa_red`: the original
Access upgrade exited0 at revision1, then the assertion failed because membership_id
was absent. Private `access-membership-20261021/acceptance-red.json` retains the result.
Focused RED also failed on the missing migration/check module before implementation.
The original Access revision and all Identity migration/reference/source bytes remain.

Current fresh final preparation is explicit private fixture work under
`platform/deployment/.local/identity-baseline/access-membership-final-optimized-20261021/`.
`bootstrap.py` creates only fresh synthetic scratch databases and bounded Access schema
rights, reusing existing restricted shared logins without changing them. Its separately
recorded `bootstrap_identity18.py` prepares one isolated genuine Identity18 case through
the unchanged Identity route. Native Auth-helper definitions are copied into the new
private proof and included in source custody. No earlier mutating qualification is rerun. The thin private bootstrap_run.py records
unchanged before/after source custody while both preparation scripts execute; successful
exit and captured log hashes are mandatory in bootstrap-source-custody.json. Aggregate
acceptance verifies that witness against the current source closure before any stage.
Post-preparation hashes alone do not establish preparation execution custody.
The first new preparation frame remains failed/preserved after an isolated schema-owner
SET ROLE prerequisite refusal; the next successful frame used temporary database-local
CREATE for Identity schema preparation and revoked it afterward. No global memberships
were added. A function-ACL-only guard also refused unchanged Identity18 because legacy
PUBLIC EXECUTE exists without Access-owner schema USAGE; the reviewed guard checks
actual callable authority. Those historical results are not presented as current success. Dedicated
new scratch cases hold external inheritance objects and an Identity definer EXECUTE
fixture; no shared global role flags or memberships change during these refusal tests.
The initial Access role was newly created in the earlier frame; no prior login/password
or historical receipt/resource was replaced. General existing bootstrap portability is
still deferred; this is synthetic local evidence, not portable CI provisioning.

Private input retains the existing native framework's `databases`, Identity-only
`owner_urls` and `runtime_urls`. New `access_owner_urls` are validated separately for
exact case/run database, loopback host, selected port and actual access_migrator username
before any connection; they never replace identity_migrator URLs. Credential/run files
are owner-private. Credentials never enter argv, output, receipts or source witnesses.

Explicit preparation command, already run once for the fresh final frame; do not replay
its single-use mutating scripts:

```sh
platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python -I -B platform/deployment/.local/identity-baseline/access-membership-final-optimized-20261021/bootstrap_run.py
```

The root's final aggregate invocation, from the repository root:

```sh
ACCESS_QUALIFICATION_DIR="$PWD/platform/deployment/.local/identity-baseline/access-membership-final-optimized-20261021" platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python -B services/access/tests/qualify_access_membership_binding.py --all
```

Final root aggregate exited0 with59 PASS records. Its unchanged before/after witness
binds130 executed-source/config/lock/bootstrap files, matching the successful preparation
witness. Restricted-owner contention refused in1.472s and the held DDL lock in4.447s;
explicit recoveries succeeded. Independent --verify-retained exited0 with two additional
PASS records and its own unchanged witness. Earlier candidate and failed frames remain
historical with their original receipts.

Optimized Python raises access_qualification_optimized_python_prohibited at the start
of main, before parsing, fixture validation, network or mutations. An actual isolated
-I -B -O sentinel test observed RED before the guard and GREEN afterward.

The aggregate is single-use on fresh prepared cases. Named stages remain available for
new independent cases. Retained inspection is repeatable after restarting the retained native run through
the existing dev.py up route; do not replay private preparation:

```sh
ACCESS_QUALIFICATION_DIR="$PWD/platform/deployment/.local/identity-baseline/access-membership-final-optimized-20261021" platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python -B services/access/tests/qualify_access_membership_binding.py --verify-retained
```

Retained inspection requires the completed aggregate's unchanged before/after executed-source
witness, verifies all recorded migration log hashes and exact retained Access catalog/data
snapshots, then rechecks the known head with the restricted owner. It cannot silently
replace prior execution custody by capturing only the current source. Each new inspection
gets a separate witness and appends receipts. Earlier frames and their source bindings
remain historical.

| Requirement | Actual aggregate evidence |
| --- | --- |
| Clean schema1→2 atomically, exact known1 populated upgrade | clean-upgrade; populated-upgrade; fixed pre/post catalogs |
| Opaque IDs/text attribution/timestamps preserved; NULL staging | opaque-ids-and-legacy-attribution-preserved |
| NULL,1,max-bigint accepted;0/negative/overflow refuse atomically | nullable-positive-bigint-boundaries-atomic;23514 with named positive CHECK or22003 for overflow |
| Exact repeat with NULL and populated nonnull member ID | populated-repeat; nonnull-membership-repeat |
| Missing bootstrap/wrong login/excess authority | missing-bootstrap; wrong-owner-login; excess-database-authority; identity-definer-execute-refusal; focused role-profile/incoming-edge guards |
| Unknown/multiple/malformed history; column/ACL/default/policy/trigger/persistence/inheritance drift | corresponding refusal stages compare complete before/after catalog/data |
| Offline, stamp and downgrade blocked | prohibit-* stages; focused programmatic-stamp test |
| Failure rollback and explicit recovery | injected-postcondition-rollback; explicit-recovery |
| Concurrent owner migration and held DDL lock bounded refusal | bounded-concurrent; bounded-lock; recovery-* |
| Actual runtime DML/DDL/SET ROLE/ledger denial, scoped SELECT | actual-runtime-read-only-rls-private-ledger; otherwise valid context and exact SQLSTATE42501 |
| Genuine Identity18 catalog/data/history unchanged; cross-owner writes/role denied | real-identity18-catalog-history-data-preserved |
| Executed repository-owned source closure unchanged throughout aggregate | executed-source-custody; source witness includes owner revisions, references, pinned SQL, bootstrap, native framework/config and frozen dependency locks |

Focused verification:

```sh
platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python -m pytest -q services/access/tests/test_access_membership_binding.py
```

36 passed in3.10s after the final optimized-Python guard. The isolated -I -B -O
fixture-sentinel test first failed by reaching fixture before the guard (RED), then
passed after main refused before argument parsing or fixture access (GREEN). Coverage includes both Access roles' restricted
flags, exact incoming/bootstrap profiles, callable Identity definer refusal, permanent and
non-inherited grants/ledger, pre-effect CLI/programmatic route denial, exact clean state,
precise database error classification and execution-custody witness refusal. Global role
authority is simulated only in focused tests, never changed in the native fixture.

Affected regression and migration-adapter verification:

```sh
platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python -m pytest -q services/access/tests apps/pts/tests/test_release.py platform/deployment/tests/test_migrate_adapter.py
python3 tools/py/run_compose_supabase.py --check-only
python3 tools/py/run_compose_supabase.py --identity-authority owned --no-seeds --check-only
```

Final root command:

```sh
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python -I -B -m pytest services/access/tests apps/pts/tests/test_release.py platform/deployment/tests/test_migrate_adapter.py -q -p no:cacheprovider
```

1050 passed in84.93s. Both composition commands exited0. Three independent review
lenses completed; all accepted findings and the final optimized-Python guard were
patched. All39 protected historical files and all130 final executed sources remain
unchanged. Native stop returned completed with runtime_ready=false; databases, volumes,
resources and receipts remain retained. Local commit records only this bounded increment.

Earlier runs recorded subprocess TimeoutExpired failures in existing optimized-Python
qualifier tests. The final pre-correction run had1047 passes and three10s/4s timeouts
(active-membership-index, operator-target and token-hook); unchanged focused reruns
passed the active-index/token cases. The4s operator-target process budget repeatedly
failed. An equivalent no-network probe measured3.249s importing and0.001s for fixture
rejection. Only that test's outer process allowance changed to60s; its assertions,
-I/-B/-O flags and all runtime/database deadlines remain. Its module passed2 tests in4.47s.
No behavior expectation was changed to accept a failed guard. Final full verification
passed after this correction. Original intermittent10s timeout causes remain unproven;
the deferred-work entry requests phase measurements, without attributing them to host
load or treating later passes as explanation. Existing portable CI bootstrap remains
separately open.

## Five impact decisions

- Scaffold: extend the existing owner migration/native fixture route only. No generator,
  generic reference ecosystem, new dependency or release runner. Approved dependency pins,
  including TypeScript7.0.2, remain.
- Shared UI: unchanged; no product or administrative interface.
- Agent context: KDG next-session handoff records staged storage and the still-closed
  exact-membership consumer gate.
- Documentation: this owner evidence, the execution substrate and development runbook
  describe controlled preparation, recovery, commands, results and limits.
- ADR: existing ownership, structural-integrity and safe-release decisions suffice;
  accepted ADRs remain immutable and unchanged.
