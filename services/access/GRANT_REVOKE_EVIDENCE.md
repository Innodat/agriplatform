# Protected organization grant revocation —2026-10-22

This delivery extends the existing Access owner command path, not an administration
service or effective reader. It removes one exact retained grant binding under current
protected revoke authority, expected revision and atomic server-attributed evidence.
It performs no Identity active-target observation, because removal must remain possible
after retirement/rejoin or organization/profile soft deletion. Assignment retains its
existing bounded observation and safeguards. No effective app access is activated.

Baseline aa223574ccd7289e55f13c47d29dc65c8aecfd4c. Root preservation snapshot
/tmp/grant-revoke-preservation.json binds55 immutable historical/reference/input files,
78 baseline production sources and concurrent starting bytes. Existing owner/dependency
baseline including TypeScript7.0.2 is preserved. Scope excludes production/real accounts,
provisioning/deployment/pilot, Leave/editor, reset/prune/cleanup and push.

## Acceptance ordering

Root resumed only the approved isolated run99b7231c-0a5b-4bdb-98e8-3329564c526a through
existing dev.py up and the pinned Supabase binary; normal up exited0. Fresh single-use
grant-revoke-red-20261022 preparation installed Identity19 then controlled Access13.
The actual restricted access_operator connection confirmed session/current login, parsed
a valid grant.revoke and returned command_unsupported before any business transaction.
Full before/after snapshot matched. Expected RED exit1 is in the ignored root diagnostic
folder grant-revoke-20261022/root-acceptance-red.log; bootstrap and source witness retained.
No production source edits preceded RED. All old frames/resources are preserved.

Implementation uses ATDD outside and focused TDD inside. Root owns native execution,
evidence/current handoffs/review/full checks/final custody/normal stop/scoped commit;
one context-free implementation agent owns the owner code/tests/runbook. Earlier input
validation is already delivered and remains unchanged. Later results follow below;
no current runtime qualification or completion is claimed prematurely.

## Delivery impacts

Scaffold: extend existing controlled owner migration/catalog/operator/CLI and native
qualification seams. No generator, generic fixture engine or runtime service. Shared UI:
none. Agent context: unchanged. Documentation: owner runbook/evidence, bounded delivery
spec and mutable substrate/deployment/KDG handoffs. ADR: existing release safety,
transaction, attribution, structural integrity and logging decisions apply; no accepted
ADR edits. Private bootstrap portability and complete logical restore remain existing
limits, not claims of this delivery. Real access and consumer activation remain gated.


## First frozen-source verification

Affected regression1666 PASS53.92s. First fresh nine-case native proof passed ten
stages: populated12/13→14, exact changed/noop/replay/selector refusal, independent
authority/no Identity observation, historical recovery/regrant conflict, retired/rejoined/
soft-deleted target removal, restricted raw/evidence guards, locks, six prior13 clients,
rollback/forward recovery and drift/Identity19 repeats. It then stopped on the large-ID
CLI execute check; aggregate completion and retained proof are not claimed for that frame.

Root inspected only that failed CLI database in a READ ONLY session:0 revoke outcomes,
grant still active revision1. No replay or failed-frame mutation. Source tracing found
Access4's inherited operation_outcome_result_check bound8192, which cannot hold a valid
large opaque target. The fix is an additive14 command-specific bound with exact catalog
verification; legacy bounds remain. All failed-frame data/inputs/logs remain retained.
Code-only child diagnostics, historical13 injection pin and a two-changed-transition
retire/rejoin race will be qualified together in fresh proof2, not by refreshing custody.

A diagnostic search mistakenly included private fixture files and emitted a default
synthetic database-superuser password plus incomplete owner/operator prefixes. No values
are reproduced here, no production credential was involved, and no credential/account
change was made. Further searches are restricted to explicit source paths; root retains
only safe selected failure fields in delivery diagnostics.


Fresh proof2 passes all12 native stages, including the exact65536-byte UTF-8 CLI input,
65556-byte canonical payload, receipt larger than8192 bytes and exact CLI recovery.
Its two changed-intent race observes competing assignment/revoke waits and proves one
revision/event/outcome with one conflict. Affected regression1668 PASS56.28s. Both
composition modes exit0. Separate retained inspection and formal review follow.


## Verification commands and requirement traceability

Commands run from the repository root. `P` below is the prepared executable
`platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python`.
`F` is `platform/deployment/.local/identity-baseline/grant-revoke-proof2-20261022`;
`D` is `platform/deployment/.local/identity-baseline/grant-revoke-20261022`.
These are retained local custody frames, not portable CI artifacts.

```sh
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$P" -I -B -m pytest services/access/tests apps/pts/tests/test_release.py platform/deployment/tests/test_migrate_adapter.py -q -p no:cacheprovider
"$P" -B tools/py/run_compose_supabase.py --check-only
"$P" -B tools/py/run_compose_supabase.py --identity-authority owned --no-seeds --check-only
"$P" -I -B "$F/bootstrap_run.py"
ACCESS_QUALIFICATION_DIR="$F" "$P" -I -B "$F/root_qualification_driver.py"
ACCESS_QUALIFICATION_DIR="$F" "$P" -I -B services/access/tests/qualify_grant_revoke.py --verify-retained
```

Proof2 results: regression **1668 passed in56.28s**; both compositions exit0;
bootstrap exit0; native driver **12 stages passed**, exit0; separate retained
inspection exit0. Logs: `root-regression-proof2.log`, `root-compose-default.log`,
`root-compose-owned.log`, `root-bootstrap-proof2.log`, `root-all-proof2.log`,
`root-retained-proof2.log` under D. Root independent custody inspection matched
135 source files,40 diagnostic logs, generated bootstrap inputs and retained state digest.

| Acceptance requirement | Native method in tests/qualify_grant_revoke.py and focused tests |
| --- | --- |
| Exact binding, revision, creation preservation, atomic changed/noop, stale/wrong selectors | `functional`; test_grant_revoke_adapter.py exact target/result checks |
| Independent current revoke authority; no active Identity projection | `authority_and_identity` |
| Exact replay/fingerprint/recovery; historical receipt; later regrant | `retry_and_recovery` |
| Retired/rejoined/deleted target removal with original binding | `retired_targets` |
| Malformed SQL, raw owner DML, missing paired event, multirow refusal | `guards` |
| Identical retry, changed-intent assign/revoke serialization, bounded locks and authority recheck | `concurrency` |
| Populated13 upgrade/repeat, all six prior clients, opaque IDs, revision overflow | `upgrade_previous` |
| Migration postcondition failure rollback and controlled forward recovery | `rollback_recovery` |
| Exact catalog, ACL/RLS/trigger/function/constraint drift refusal, Identity19 continuity | `catalog_and_identity`; test_grant_revoke.py |
| Actual CLI execute/recovery, UTF-8 boundary, large receipt, ambient libpq refusal | `cli`; test_grant_revoke_adapter.py |
| Exact current catalog/data/source custody after execution | `retained`, independent --verify-retained |

Formal review and any fresh verification following review corrections are recorded below.


## Formal review

Three context-free BMAD lenses reviewed the same193465-byte scoped diff: blind
returned10 findings, edge returned none, verification returned2 preverified gaps.
The build spec records every finding separately. Forged receipt/event rejection,
non-null persisted audit provenance, recovery size/lock cases, complementary size
boundaries and strict duplicate flags receive focused corrections. Exact command
and traceability documentation is completed here. No deferred work is introduced.

One blind concurrency finding was rejected after tracing the existing authority
trigger: execute holds the operator-authority transaction lock before business/row
waits; supported principal/policy updates take that same lock, so removal cannot
overtake those waits. The reachable retry-wait removal is covered. No trigger
bypass, replica mode or new fault-injection system was added for an unreachable race.
The pending spec checklist finding is a workflow-finalization matter, reconciled
after final verification rather than changing approved intent.


## Corrections and final verification

Focused correction command (exit0, **57 passed in1.09s**):

```sh
"$P" -m pytest -q services/access/tests/test_grant_revoke.py services/access/tests/test_grant_revoke_adapter.py services/access/tests/test_operator_cli.py
```

The affected regression command above was repeated on frozen corrected sources:
**1676 passed in55.73s**, exit0 (`root-regression-final.log`). Both exact composition
commands also exited0 (`root-compose-default-final.log`, `root-compose-owned-final.log`).
Fresh final frame is `platform/deployment/.local/identity-baseline/grant-revoke-final-20261022`.
Only eight bootstrap/template inputs were copied from proof2; no generated credentials,
state, results, source witness or logs were copied. Fresh bootstrap exited0 and established
exact source custody (`root-bootstrap-final.log`). The same native/retained commands above
use this final F, with `root-all-final.log` and `root-retained-final.log` under D.

Additional requirement evidence: `evidence_mutations` rejects wrong receipt target,
executor/disposition and wrong event target/executor/type/before/after transitions in
rollback-only fixture transactions. `forged_unchanged` rejects fabricated revision and
binding; `functional` asserts persisted non-null evidence and submitted reason.
`recovery_waits` witnesses lookup retry/authority waits, checks busy only at retry,
bounded unavailable at authority and current denial after released waits. `cli` isolates
matching-selector/canonical over-size refusal and non-null evidence65536/65537 boundaries.
`upgrade_previous` tests wrong selectors at revoked maximum revision. Focused adapter
tests reject oversized recovery selectors and all duplicate grant-flag forms before I/O,
while retaining valid empty/Unicode/opaque selectors and legacy receipt behavior.


Final native driver: **15 stages PASS**, exit0; independent read-only retained
invocation: **PASS**, exit0. Root recomputed every current source and diagnostic
hash, bootstrap generated-input/log hashes and retained-state hash: **PASS**.
Inventory:135 consumed source files,40 qualification logs,10 bootstrap logs.
All55 protected historical/input files and146 prior receipt/spec files match the
starting snapshot; exactly six approved baseline production files changed,72 remain
unchanged. Concurrent working-tree changes are retained independently of this commit.

Durable SHA-256 receipts (sorted compact JSON for inventory hashes):

- Source inventory: `f921a183b13a48d5766866bb6a8dde4691d977cada7d5d519b458fbf8ff46016`
- Qualification-log inventory: `1d9a4ca9e403be4f5873888188b7637c64be2e392fa6c209f10ac2b1e0e476de`
- Retained state: `6ed5346aff134839f82f82b308ecf1019edce41a851f530f3690a774a7b34038`

The complete private final audit is retained under D/root-final-evidence.json;
its postcommit addendum binds the exact local commit and owned path set. Failed
initial proof and passing proof2 remain historical frames without refreshed custody.
No findings remain deferred. Portable bootstrap/CI and complete logical restore
remain explicit existing limits; no production or consumer activation is claimed.

Normal lifecycle stop exited0 with code `completed` (`root-native-stop.log`):

```sh
"$P" -B platform/deployment/dev.py stop --target platform/deployment/environments/kdg-local.json --run-id 99b7231c-0a5b-4bdb-98e8-3329564c526a --supabase /home/ck/repos/innodat/agriplatform/platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/supabase/supabase
```

No reset, prune, failed-frame replay, resource deletion or production operation.
