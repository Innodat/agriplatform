# ENV rollback-only API default-privilege semantics

This qualifier executes the exact pinned CLI SQL in a rollback-only fixture on an
isolated disposable selected PostgreSQL instance. It adds no production dispatch
route, startup stage or CLI continuation. The existing construction/refusal boundary
is unchanged. Runtime/setup/scaffold readiness remains false.

## Source and semantic scope

The source SQL/profile and417-byte SHA256 are recorded in
[request evidence](ENV_API_DEFAULT_PRIVILEGES_REQUEST_EVIDENCE.md): pinned CLI commit
753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4,
SQL SHA256438b7e8bf360f0d66c629c5ff102a9fb52584758be94be722d6cb490b216dacc.
The apply case embeds that constant unchanged and executes it under postgres.

PostgreSQL17 documents that [default privileges](https://www.postgresql.org/docs/17/sql-alterdefaultprivileges.html)
apply when objects are created, use the current creator's defaults, and add per-schema
grants to global defaults. Per-schema revocation cannot remove global/PUBLIC grants.
The [default-ACL catalog](https://www.postgresql.org/docs/17/catalog-pg-default-acl.html)
distinguishes global/per-schema records; a null object ACL denotes built-in defaults.
This fixture checks direct ACL tuples and uses an explicit controlled PUBLIC EXECUTE
sentinel. It proves preservation of that effective function permission, not denial.
It does not establish effective authorization policy for applications or all inherited
role/global-default combinations.

## Six independent SQL invariants

1. Seed and require21 direct target tuples: three roles × four table privileges,
   two sequence privileges and one function privilege. Avoid vacuous revocation.
2. Snapshot normalized exploded default ACL tuples across the database, including
   grantor/grantee/grantability. The exact after-set must equal before minus only
   those postgres/public tuples. Seed table/sequence/function sentinels for other role/schema/creator, one
   unrelated WITH GRANT OPTION grant, and
   preserved table TRUNCATE/REFERENCES/TRIGGER/MAINTAIN and sequence UPDATE rights.
3. Existing synthetic table/sequence/function ACLs must remain unchanged.
4. New postgres-created objects must lack the21 direct target grants while retaining
   the exact15 seeded table/sequence tuples outside the revoke list, including
   grantor/grantee/grantability.
5. New functions retain explicit PUBLIC EXECUTE and effective anon EXECUTE through
   it. This is a controlled fixture condition, not a claim about all runtime defaults.
6. Roll back the inner subtransaction using one dedicated sentinel; afterward
   independently compare original default ACLs and require all synthetic objects/
   schema absent. The outer transaction also rolls back.

Five nested rollback-only corruptions independently prove sensitivity of the later
existing/new/PUBLIC and both rollback predicates. Catch only designated oracle and
rollback SQLSTATEs; other assertion/syntax/permission errors fail the existing
detached psql exec and qualifier. No log output, data dump or exception-text parsing
is introduced. Existing5s statement/idle,1s lock, owner execution/cleanup and
CLI-termination bounds remain. No sequence values are consumed or accounts created.

## Acceptance and verification

ATDD RED: the acceptance test reports the absent semantic fixture. GREEN follows
implementation. A first local syntax error was corrected before GREEN and actual
execution. Focused145-test owner suite PASS3.045s. Acceptance and logs are retained
under .local/api-default-privileges-qualification/.

| Requirement | Verification |
| --- | --- |
| R1: bounded fixed fixture with source SQL and rollback oracles | test_api_default_privileges_semantic_fixture_acceptance |
| R2: exact case set, source inclusion, preserved catalog predicate/timeouts | test_api_default_privileges_semantic_fixture_preserves_bounds_and_closed_cases |
| R3: internal admission only, detached envelope, production refusal restored | test_api_default_privileges_semantic_fixture_only_admitted_inside_exact_test_hook |
| R4: real SQL semantics and non-vacuous failure detection | actual apply, omitted and extra controls |
| R5: ownership, CLI termination, Auth pre/job/post and normal disposal | existing guarded auth-catalog owner exercised by actual controls |
| R6: preserve receipts/state and unrelated running work |13-file before/after hashes and running-inventory observations |

Commands:

```sh
python3 -m unittest discover -s platform/deployment/tests -p test_pinned_execution.py -k test_api_default_privileges_semantic_fixture_acceptance
python3 -m unittest discover -s platform/deployment/tests -p test_pinned_execution.py
```

Actual verification uses the exact tracked [runbook command](DEVELOPMENT.md#rollback-only-api-default-privilege-semantics)
with only fixed case selection changed, following prepare/toolchain/images for fresh
run e7643c35-6dfa-46a0-abda-9af41234dc43. The semantic source/test bindings and13
retained files are checkpointed before actual execution. The unchanged production
source and prerequisite receipts support the same prepared UUID; every invocation
requires a fresh missing volume and creates a new disposable database. No failed
resource is blindly reused.

Final reviewed helper SHA256:
76ce3068ff562a066605b6ca7a68ff1060fb79add5e8b95ca317d53e1a8126ee;
test SHA2564117d0fd21dbc669698d719fc3ebfbd8ea7cedc07114d8948a2696d77ea28452.
The final exact source comparison independently confirms all417 embedded SQL bytes.

| Final record | Result | SHA256 |
| --- | --- | --- |
| acceptance-red.log | expected missing-helper failure | ea0ff2450c6c77d487bbb6bd2fac92714de8f6c31e01e4595a9c259db6528cb0 |
| acceptance-green.log | acceptance PASS | 2299339565fdc7c4fedeb54e99b181ba53b821f77194926422cc7df3301ba0ee |
| pinned-tests-reviewed.log |146 tests PASS7.870s | f930a1bdd9bcb8b6efe3345028080b30a633022e8db3e44882031746d17d602a |
| reviewed-apply.log | exit0, six invariants and five sensitivity corruptions PASS70.779s | 89e5c0503197f382999d3c43688da925d1f44188be29c32d2a375a0d66d093fa |
| reviewed-omitted.log | expected exit2/execution_sql_failed, zero verified invariants45.816s | f7dd94165854aa3028efad68978c9d990b118fb2b3389cbd785d1a022f8cfcae |
| reviewed-extra.log | expected exit2/execution_sql_failed, zero verified invariants51.046s | 5b8bcfeff7dd8e17132a3fd74d4cfe633996b9d7ac95b6c5c9e3b87ee8678ebb |
| source-comparison.json |417-byte exact source match | 8f81d40e719f12e95049c394fdfaff081c4f2ecf5ee650c9824b098319d3881e |

Reviewed tracked command hashes for apply/omitted/extra are respectively
54961a8d4bde8564dca35044bcad19bf425fa28dc9345ad67ebc0c4c794d8ccd,
8a703fdf5d0dbd8cf1e033f1d9afcfd45279964b88c6e1f937d114dc6518a332,
dc795dedca161a2114f859de602cc20a9b10cbb5a1d4c007856a738e76d42654.
Each record captures the exact command and elapsed time. Only fixed case selection
differs. No unrelated running container was added/removed in any final control.
All13 retained files remain byte-identical. Final read-only exact-run label queries
find no remaining container, volume or bridge; no separate recovery cleanup ran.

Initial pre-review actual results are retained separately: apply73.507s,
omitted41.092s, extra47.200s. They do not substitute for reviewed-source results.
One independent oneshot reviewer returned five coverage/precision findings; all
individually triaged and patched, none newly deferred. Separate review layers were
skipped for this qualification-only oneshot. Review expansion hit the existing16KiB
request bound in focused tests; fixed by reusing fixed predicate text server-locally
and canonical tuple ordering. The limit and all timeouts remain unchanged.

The tracked-command regression additionally verifies helper-derived count metadata,
typed success/cleanup/readiness facts, unexpected negative-case success refusal and
zero verified invariants on failure. No full deployment regression, public runtime,
or complete CLI startup is claimed by these results.

## Impacts and remaining work

- Scaffold: qualification extends the existing ENV test owner; no production
  generator/template/schema/client/runtime route changes.
- Shared UI: no UI surface or pattern impact.
- Agent context: existing isolation/owner instructions suffice; no change.
- Documentation: reproducible fixed-case runbook, evidence, KDG handoff and memlog.
- ADRs: existing release safety, ownership and structured diagnostic decisions apply;
  no new architectural decision and no accepted ADR mutation.

Next: admit bounded execution through the retained runtime owner, then qualify the
remaining setup/CLI continuation and full runtime/scaffold foundation. This rollback
fixture alone grants no production execution authority. ENV/P1/SERVICE and dependent
Identity/Access/WRITE/KDG gates stay open. TS7.0.2/mail15484, concurrent documents,
receipts/state and uncertain prior Docker resources remain protected. No deployment,
real-data use or persistent account/access change is included.
