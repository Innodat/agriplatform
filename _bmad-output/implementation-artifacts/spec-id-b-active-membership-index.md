---
title: Stage active membership uniqueness compatibly
type: feature
created: '2026-10-20'
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: 0e460f65afd8e92c32b974412d0ea648f915eced
context:
  - /home/ck/repos/innodat/agriplatform/AGENTS.md
  - /home/ck/repos/innodat/agriplatform/platform/docs/architecture/contracts/identity-access-execution-substrate.md
---

<frozen-after-approval reason="standing bounded shared implementation approval">

## Intent

Prepare accepted E1 active-membership uniqueness through compatible expansion. Add14
with named UNIQUE btree index org_member_active_org_user_uidx on identity.org_member
(org_id,user_id) WHERE deleted_at IS NULL. Keep the original full unique constraint,
all rows, seeds, guards/readers and existing writer behavior. This stages the required
index; it does not permit historical duplicates or implement rejoin on canonical14.

## Boundaries & Constraints

Use only CREATE UNIQUE INDEX in14, no IF NOT EXISTS, concurrent DDL, row changes, grants,
new function/trigger/service/framework/generator or historical source/pin edits. Existing
canonical13 preflight validates shape before upgrade. Preserve original
org_member_org_id_user_id_key/backing index and record exact definition/dependencies.
Do not drop it outside explicitly rolled-back synthetic isolation. Its later removal
requires coordinated owner commands/seeds and ADR-0020 compatibility/recovery: installed
PostgREST upsert supports column conflict target only; read-then-insert could implicitly
rejoin. No seed rewrite or runtime/app/access readiness claim here. Production migrations,
accounts/access/provider, infrastructure/deploy/pilot, reset/prune, Leave/editor and push
remain excluded. Dependencies including TypeScript7.0.2 stay.

## I/O & Edge-Case Matrix

| Scenario | Expected |
| --- | --- |
| Actual13 canonical inventory | New index absent; full unique present, retired duplicates refused; legacy active seed works |
| Canonical14 upgrade | Exact single-index catalog addition, no other changes/data rewrites; full uniqueness retained |
| Rolled-back owner-prepared isolation dropping only full unique | Partial index rejects two active same-org/account, permits retained retired histories, isolates other org/account and preserves old membership roles; exact catalog/data restored |
| Canonical14 concurrent legacy inserts | Independent restricted logins/SET service_role contend; exactly one committed active member and safe23505 for loser, original rows/roles retained; winner is explicitly retained synthetic fixture data |
| Clean/adopt/exact13/repeat, drift/unknown/injected index-DDL failure | Verified14 or exact old catalog/history/data preserved; marker proves injection fired, fixtures restored then recovery |

</frozen-after-approval>

## Code Map

Add services/access/identity-migrations/versions/0014_active_membership_index.py,
ACTIVE_MEMBERSHIP_INDEX_SQL, revision identity_0014/down identity_0013, destructive downgrade
refused. Extend identity_baseline.py head/trusted chain and existing
qualify_identity_baseline.py --record-active-membership-index-reference branch; new
active-membership-index-reference.json recorded/pinned only by root, verifying13 first.
Previous canonical 0e460f65afd8e92c32b974412d0ea648f915eced has29 owner py/json files; capture/verify against Git.
Reuse qualify_membership_retirement.py/binding/Profile fixtures and function/seed/read
proof. Add small qualify_active_membership_index.py subclass, reference-case name
active_membership_index_reference; keep other nine-case protocol and member-retention-
fixtures.json. Override compatibility/index behavior, characteristic witness and migration
matrix for13/14. Reuse unchanged retirement writes() and CPU tests where appropriate.
Failure fixture adapts existing sequence-backed event witness to CREATE INDEX/new index
existence; all temporary objects restored. Index isolation uses administrator rollback
transaction, drops full constraint without CASCADE, SET LOCAL ROLE service_role, compares
rows/catalog after rollback; never claims restricted-login DDL authority. Concurrent proof
retains both unique protections, labels constraint attribution honestly and commits only
one new spare-org/spare-account synthetic member; join/audit/receipt safety is not claimed.

## Tasks & Acceptance

- [x] Child: focused test_active_membership_index.py observes missing14/head RED; add
migration, baseline/reference recorder and13 historical-head adjustment. Test source/ref
custody and exact additive shape. Do not run DB/Docker or pin/reference generation.
- [x] Child: qualifier covers every matrix row, actual partial-index named23505, full
constraint still present, explicit bounded concurrency with observed blocking (no sleeps
as ordering proof), cleanup/witnesses and source-bound old13 comparison. Root alone
supplies fresh fixtures/reference/pin. Do not mutate docs/spec; report CPU verification.
- [x] Root: record actual13/reference14/complete matrix, full affected tests/both composers,
three independent reviews, source/custody/safe-output checks, retained-data normal stop,
requirement-test evidence/five impacts in owner runbook/evidence/KDG docs/inventory,
scoped local commit. Preserve concurrent Scribeswell/Expense/BMAD documents.

Given canonical13, when14 upgrades, then only the new index appears and legacy writers
stay compatible. Given isolated full-constraint removal, when membership rows are written,
then only one active per org/account is accepted. Given failure, old state stays.

## Implementation Notes

No intent gap. Additive staging follows ADR-0020; final E1 replacement stays gated rather
than inventing an unaudited seed RPC. Only isolated synthetic DDL/data is authorized.
Standing approval covers preserved dirty concurrent tree and bounded implementation.
Root has already rendered Build and orchestrates steps/reviews/commit. The single step03
child implements both Child tasks, code/tests only; no additional workflow/subagents.

## Spec Change Log

## Review Triage Log

| Finding | Verdict | Evidence and route |
| --- | --- | --- |
| Blind1 resume after committed winner | low | Fresh-fixture precondition intentionally refuses replay; durable precommit/result witnesses retain the winning row and no automatic adoption/reset is authorized. Direct documentation patch states matrix is single-use after the committed fixture; reject adding a recovery/adoption subsystem. |
| Blind2 concurrency startup/block/commit failure coverage | medium | New coordinator owns rollback/worker lifetime around a deliberate commit; only happy-path actual evidence currently covers it. Patch focused failure-path tests proving rollback, bounded completion and enclosing fixture cleanup. |
| Blind3 busy polling | low | Three-second observer loop issues queries without yielding on no block. Add bounded polling interval while continuing to require actual pg_blocking_pids evidence; patch. |
| Blind4 multirow partial-index rollback | low | Named new-index refusals currently cover one row. Add one valid-plus-duplicate statement and reuse full-state comparison; patch. |
| Blind5 replacement leaves partial index | low | Isolation retires the original row but not its replacement. Add replacement retirement/new active insertion with retained history/roles checks in existing rollback transaction; patch. |
| Blind6 blocked CREATE INDEX | medium | New CREATE INDEX can wait behind ordinary writers; injected post-DDL failure does not prove timeout behavior. Patch old13 failure case holding ROW EXCLUSIVE, bounded safe refusal/unchanged state, release before subsequent rollback/recovery. |
| Blind7 actual index drift | medium | Actual drift cases mutate function/ACL; index drift itself has only snapshot tests. Patch rollback-only direct-owner preflight for missing/wrong-predicate index on canonical14, no target normalization. Do not manufacture invalid pg_index state. |
| Blind8 upgrade invocation unit test | false | Required actual clean/adopt/exact13 migration routes execute upgrade and verify independently pinned index/relation postconditions. Empty upgrade would refuse and fail the matrix. The SQL-constant unit test is not the sole evidence; a mirror implementation-call test adds no missing acceptance verification. |
| Blind9 new catalog guard branch | medium | New branch's role/privilege guard order is not directly exercised; head test replaces it entirely. Patch focused success and individual guard-refusal-before-comparison tests. |
| Blind10 pending final receipts | low | Reviews/custody/stop really were pending in reviewed snapshot. Root completes exact receipts and navigation before completion; direct documentation patch. |

Edge-case review returned no findings; verification-gap review found no gaps. Host thread
capacity required sequential children; all three completed before individual triage, none
skipped. Nine findings route to private-test/documentation patches; one is disproved.
No production SQL/reference/pin changes and no deferrals.

## Verification

Frozen OWNER_PYTHON=platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python.
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$OWNER_PYTHON" -I -B -m pytest services/access/tests
apps/pts/tests/test_release.py -q -p no:cacheprovider; smallest RED/focused first.
Both composer --check-only routes, source-bound matrix,29 previous files, restoration/
credential-safe logs, normal stop and scoped commit. No root npm claim. Five impacts:
existing owner pattern extends scaffold; no UI consumer; context sufficient; owner/
continuation docs updated; accepted ADRs unchanged.

Initial verification: missing14/head RED; focused68 tests PASS. Actual13 characterization
PASS after SQLAlchemy Row serialization correction. First root pin assertion omitted the
new pg_class relation; unpinned first upgrade refused/rolled back (old13/no index verified).
All failures/source/partial witnesses retained. Corrected independent14 pin
b710b943ecb95e4b7cbce9eb77debad8f1ad181c40a2532ff87cd85be317033b. Actual full matrix
PASS42.258s source unchanged,834 affected tests PASS41.56s no skips, both composers exit0.
Each frozen matrix row ran/passed; canonical concurrency retained one synthetic winner.
Three review layers and final custody/normal stop follow.


Final reviewed verification: child80 focused tests PASS; fresh reviewed frame
platform/deployment/.local/identity-baseline/active-member-index-reviewed-_dfnt87r/.
Actual13 characterization PASS; full matrix PASS46.265s source unchanged,846 affected
tests PASS38.42s no skips, both composers exit0. Blocking writer refusal7.746s preserved
old13; injection marker/rollback/restoration/recovery and actual missing/wrong-predicate
index drift PASS. Multirow/replacement history isolation and canonical concurrency PASS,
one synthetic winner retained with old full-constraint23505. Every frozen matrix row
ran/passed. Three reviews complete: nine findings addressed, one disproved, none deferred.
Production14 migration/reference/pin unchanged through review; all initial failures/source/
winners retained. Five impacts and exact commands/requirements are in owner evidence.
Final custody/normal-stop/scoped local commit receipts are recorded in reviewed frame.

Final custody:2659 protected paths, none missing/unexpected; seven intended existing
paths changed and original concurrent work retained. Executed source matches current
source. Normal wrapper stop completed for99b7231c-0a5b-4bdb-98e8-3329564c526a, retaining
all data/resources and both initial/reviewed synthetic winners; runtime_ready=false.
