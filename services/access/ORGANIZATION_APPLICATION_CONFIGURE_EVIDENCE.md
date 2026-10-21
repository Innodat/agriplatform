# Protected organization application configuration — 2026-10-21

This bounded ACCESS-A delivery extends the existing owner migration/operator/CLI route
for organization availability configuration. It creates no effective admission, grant,
reader or consumer activation. Exact organization/command/app authority precedes the
Identity19 private point observation; every new execution reobserves, while historical
receipt lookup requires current exact authority. Five seconds from observation start
bounds reuse through locks/replay, following the existing Identity ensure pattern.

## Acceptance and preservation

Before implementation root observed retained exact Access8 without the protected
configuration routine using a bounded read-only query. Its safe expected-failure log is
`platform/deployment/.local/identity-baseline/organization-configure-20261021/root-acceptance-red.log`.
The implementation agent also observed adapter dispatch/result acceptance RED before
its first implementation. Independent root verification and final results are recorded below.

The root preservation snapshot is `/tmp/org-config-preservation.json`:14 concurrent
tracked files,43 untracked files and50 protected historical migration/reference sources.
Root's previous-source package contains78 exact Git files from full baseline
`fd8248f43a3355b9494e031128d2ffdafd0a8fb0`, including genuine Access8/Identity19 migration
helpers and previous adapter/parser dependencies. No historical source is relabeled as
current code. Native preparation reuses existing restricted roles/secrets and target
binding; it provisions only synthetic local databases, not new runtime identities.
Existing original proof frames, receipts, data and Docker resources stay retained.

## Requirement traceability

| Requirement | Native qualification methods (all must pass) |
| --- | --- |
| Exact current command/org/app authority before Identity; recheck after waits | authority_and_identity; context_and_login_boundaries; freshness_and_revocation |
| Active account-free organization, local setup context, bounded observation | authority_and_identity; freshness_and_revocation; late_wait_expiry |
| Expected absence/revision; creation/change/unchanged attribution | functional; deferred_evidence_and_overflow; upgrade_previous |
| Scope-aware idempotency, fingerprint conflict, current scoped recovery | retry_and_recovery; functional; concurrency |
| Atomic required row/outcome/event; deny raw writes | guards; deferred_evidence_and_overflow; forged_evidence_and_merge |
| Concurrent writes, revocation, response loss, lock classifications | concurrency; freshness_and_revocation; late_wait_expiry; retry_and_recovery |
| Genuine populated8 to9/repeat; old adapters/receipts remain | upgrade_previous; retained; separate --verify-retained |
| Drift/failure blocks activation; controlled forward recovery | catalog_and_identity; rollback_recovery |
| Safe existing CLI/worker transport and target verification | cli; test_organization_application_configure.py; affected regression |

## Five delivery impacts

Scaffold: extend existing owner migration/adapter/CLI and qualification fixtures; no
parallel bootstrap framework, generator or runtime service. Shared UI: none for private
owner commands. Agent context: no change. Documentation: owner runbook, contract,
local-development runbook, evidence and KDG continuation. ADR: applies accepted release
recovery, short transactions, scope/attribution/logging rules; no new ADR or accepted
ADR modification. Shared clients/generators remain with their current owners. Dependency
baseline, including TypeScript7.0.2, stays unchanged.

No real account/access changes, production migration, infrastructure, deployment, pilot,
Leave/editor, reset/prune or push follows from this synthetic proof. ACCESS-B, grants,
effective admission and coordinated PtS/KDG activation remain separately gated.

## Preserved provisional verification

The provisional migration smoke exposed two corrected implementation issues before the
full matrix: explicit8 history was omitted after moving HEAD to9, then constraint-trigger
creation followed removal of its needed function EXECUTE privilege. Exact8 recognition
was restored and transaction-local construction reordered with unchanged final ACLs.
Controlled8 then9 passed exact catalog verification; failed transactions/logs remain.

The first nine-case preparation witness correctly refused a qualifier polling-source
edit during preparation. That frame remains unqualified. The next frame refused a
missing actor-bootstrap receipt: actual actor inserts existed, but root omitted the
existing required receipt. Fresh preparation now reads/verifies each synthetic actor
before recording the receipt. No failed receipt/witness was rewritten as successful.

The next aggregate passed preparation/functional checks, then a fixture attempted an
immutable authority tuple update. It now disables the prior authority and inserts a new
exact app authority, preserving history. Automatic approval review rejected further
mutating diagnostics in that retained failed frame to protect evidence; that action did
not execute. Root continued using fresh synthetic fixtures without requesting broader
permissions. The later aggregate passed functional/authority/replay/guards/deferred
proof/concurrency, then its wait-observation polling could not see the new restricted
backend. Existing owner qualification clears PostgreSQL statistics snapshots while
polling; the correction retains required expiry/revocation expectations.

All provisional/failed frames remain separate from final acceptance. Read-only inspection
reported synthetic revision3 unchanged after the wait-observation failure. No failed
aggregate is replayed, and no old evidence/data is removed or silently normalized.


## Review resolution

Three independent lenses completed: blind, edge cases and verification gaps. All
confirmed findings were patched; none changes approved intent and none is deferred.
The spec records individual triage. The resulting coverage includes identical concurrent
retries, exact two-organization recovery, raw MERGE and forged evidence refusals,
context/login spoofing, direct SQL encoding/shape/isolation boundaries and all four
actual previous8 commands populated before upgrade and exercised again after9.

Freshness is checked after blocking reads and writes, before conflict/replay returns,
with current-authority refusal taking priority. Seven deliberate5.1-second waits cover
business/row coordination, outcome replay/fingerprint reads, missing-app reads, a late
FK and late event write. Each requires AC004 and identical full state. Only the retry
lock remains busy. Standalone source custody now includes all consumed inherited helpers.
The pre-review passed frame retains its exact source diff; it is historical evidence,
not the final reviewed source qualification.


## Final reviewed verification

Final frame: `platform/deployment/.local/identity-baseline/organization-configure-accepted-20261021`.
Fresh bootstrap and exact before/after preparation source witness passed. The native
matrix passed all16 groups; a separate official read-only retained inspection passed.
All160 source bindings match, including four inherited helpers and78 independently
Git-verified baseline files. Supplemental root custody binds the diagnostic driver and
verified actor receipt. Source changes invalidate preparation; --all is single-use.

Exact commands below use `P=platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python`
and `F=platform/deployment/.local/identity-baseline/organization-configure-accepted-20261021`:

```sh
$P -I -B "$F/bootstrap_run.py" > "$F/root-bootstrap-driver.log" 2>&1
ACCESS_QUALIFICATION_DIR="$F" $P -I -B "$F/root_qualification_driver.py" > "$F/root-all.log" 2>&1
ACCESS_QUALIFICATION_DIR="$F" $P -I -B services/access/tests/qualify_organization_application_configure.py --verify-retained > "$F/root-retained.log" 2>&1
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 $P -I -B -m pytest services/access/tests apps/pts/tests/test_release.py platform/deployment/tests/test_migrate_adapter.py -q -p no:cacheprovider > "$F/root-regression.log" 2>&1
$P -B tools/py/run_compose_supabase.py --check-only > "$F/root-compose-default.log" 2>&1
$P -B tools/py/run_compose_supabase.py --identity-authority owned --no-seeds --check-only > "$F/root-compose-owned.log" 2>&1
```

Every command exited0. The root diagnostic driver calls the same qualifier main with
--all and emits only safe exception class/SQLSTATE/source locations on failure.
Affected regression: **1348 passed in59.61s**. Agent final focused configure/storage:
18 passed. Both composition modes passed. Preparation logs, source witness, aggregate
and retained results, snapshots, old-client receipts and CLI artifacts remain private.
This proves isolated synthetic local behavior, not portable CI bootstrap or real-target
readiness. Existing bootstrap portability remains deferred; no new review deferral.


The authorized native run99b7231c-0a5b-4bdb-98e8-3329564c526a stopped normally with
`dev.py stop --target platform/deployment/environments/kdg-local.json --run-id
99b7231c-0a5b-4bdb-98e8-3329564c526a --supabase` followed by the existing pinned binary
at `platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/supabase/supabase`.
The command used P -B (without -I); root-native-stop.log reports completed, runtime_ready
false. No reset/prune occurred. Final root custody records protected50 historical hashes,
all14 concurrent tracked and43 pre-existing untracked bytes, frozen spec, owned paths,
source/results/log digests and the scoped local commit. No source claim is derived from
a failed preparation or mutable run receipt. Private root-final-evidence.json records
that audit without credentials or business payloads.
