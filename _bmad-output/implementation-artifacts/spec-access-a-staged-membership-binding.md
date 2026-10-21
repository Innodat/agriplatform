---
title: 'ACCESS-A staged grant membership storage'
type: 'feature'
created: '2026-10-21'
status: 'done'
route: 'dispatch'
baseline_commit: 'c450c40d0a1490cfecabc58f8ce97c108b13a651'
review_loop_iteration: 0
context:
  - 'AGENTS.md'
  - 'platform/deployment/DEVELOPMENT.md'
  - 'platform/docs/architecture/contracts/identity-access-execution-substrate.md'
---

<frozen-after-approval reason="standing authorized bounded shared prerequisites">

## Intent

Stage the exact membership reference needed by organization grants, through the existing Access migration route, preserving legacy grants and preventing an unsafe migration from activating a release. This is the first ACCESS-A storage increment after Identity18; it does not clear the membership-binding consumer gate.

## Boundaries & Constraints

Add nullable bigint `access.grants.membership_id` with named `grants_membership_id_positive` CHECK>0. Preserve opaque text IDs, keys, legacy attribution/data, permission CHECK, forced RLS and read-only runtime privileges. No default, automatic backfill, Identity FK, permission inference or grant activation. Future Access-B must require exact active org/account/member equality; NULL cannot be treated as a match. Current v1 ignores the column and remains incompatible/stopped until coordinated consumer delivery.

Use existing Access Alembic/config/coordinator; controlled restricted owner upgrade, bounded transactions and sanitized errors. Preserve access_0001 and all Identity migration/reference/source bytes, previous receipts/resources and concurrent Leave/PtS documents. No new generator, generic migration framework, runtime service, product UI, dependency changes, account-scope transition or Leave/editor implementation. No real-account/access, production migration/provision/deploy/pilot, reset/prune or push. Synthetic local/CI verification and scoped local commit are authorized.

## I/O & Edge-Case Matrix

| Given / when | Then |
| --- | --- |
| Separately prepared clean Access schema / upgrade | Existing1 then2 apply atomically; nullable positive field, exact original ACL/RLS/keys preserved |
| Exact head1 with populated opaque IDs/legacy actor text / upgrade | Existing values unchanged, membership NULL; no inferred binding or extra grant |
| NULL,1,max-bigint / controlled owner maintenance | Stored; zero/negative/overflow refuse atomically |
| Head2 with populated rows / repeat | Exact catalog/data unchanged |
| Missing bootstrap, wrong owner, excess authority, unknown/multiple/malformed history, unexpected schema/ACL/default/policy/trigger drift | Refuse before normalization or business change |
| Concurrent migration, held DDL lock or injected failure | Bounded refusal/rollback, preserved ledger/data; explicit recovery succeeds |
| Runtime raw DML/owner assumption, Access owner touching Identity | Denied; no cross-owner privilege expansion |

</frozen-after-approval>

## Code Map

- `services/access/migrations/versions/0001_initial.py`: immutable one-table baseline; original PK/unique/text attribution and org_scope policy.
- `services/access/migrations/env.py`, `alembic.ini`: existing owner route; currently bare engine/transaction. Add narrowly fixed owner/history/catalog checks, bounds, serialization and postcondition; no parallel runner.
- New `migrations/versions/0002_membership_binding.py`, `migrations/access_baseline.py`: additive field and small fixed Access-local catalog assertions for clean/1/2. Avoid copying Identity's eighteen-reference framework or generating a new reference ecosystem.
- `tools/py/deploy_pts.py`, `apps/pts/tests/test_release.py`: existing failure-blocks-activation/Identity-first coordinator; reuse without new release orchestration.
- `services/access/tests/qualify_identity_baseline.py`: reuse existing native run/private fixture validation and engines; additional Access owner URLs must be explicitly validated, not substituted for identity_migrator owner_urls.
- `apps/pts/tools/prepare_test_database.py` is an older port55439/minimal-Identity fixture, unsuitable for current Supabase/Identity18; do not weaken its guards.

## Tasks & Acceptance

- [x] `services/access/tests/test_access_membership_binding.py` and new actual qualifier — observe current missing-column acceptance failure before implementing; focused TDD for matrix and safe route errors.
- [x] `services/access/migrations/versions/0002_membership_binding.py`, `access_baseline.py`, `env.py`, `alembic.ini` — owner-local additive upgrade, exact known baseline/history checks, bounded controlled route and private ledger; prohibit offline/stamp/downgrade execution before effects.
- [x] `services/access/tests/qualify_access_membership_binding.py` — fresh native scratch cases, actual access_migrator/access_runtime, clean/exact1/populated repeat, boundary/unknown/drift/rollback/concurrency/ACL proof. One documented aggregate invocation, repeatable retained inspection and complete executed-source custody. Reuse current fixture framework; bootstrap remains explicit private test preparation, no new generator.
- [x] `services/access/ACCESS_MEMBERSHIP_BINDING_EVIDENCE.md`, owner contract, deployment runbook, KDG handoff — requirement/test commands/results and five impacts; state exactly what remains gated.

Given existing Identity18 in an isolated integration case, when Access upgrades, then Identity data/catalog and history remain unchanged and Access owner cannot alter them. The column migration itself needs no artificial Identity SQL dependency. Given an old reader, this increment makes no safety or activation claim.

## Implementation Notes

No intent gap: accepted contract explicitly permits additive NULL staging before owner commands/backfill/final enforcement. No production effects authorized. Footprint is existing Access owner migration/testing/docs only. Prefer fixed catalog assertions for this single table over new generation tooling. Existing runtime table SELECT deliberately covers the added column; no writes/role inheritance are granted. Check actual session/owner, known version rows and semantic schema/constraints/indexes/policy/ACL/defaults/ledger before and after upgrade. Preserve unknown state for explicit disposition.

Five impacts: extend owner/tooling fixtures; shared UI unchanged; update next-session context; owner evidence/runbook/contract updated; accepted ADRs unchanged (existing ownership, structural/release decisions suffice). Approved dependency baseline including TypeScript7.0.2 stays.

## Spec Change Log

## Review Triage Log

| Finding | Verdict / route | Evidence |
| --- | --- | --- |
| Blind1: runtime elevated attributes | high / patch | Only migrator flags are checked; runtime BYPASSRLS/superuser can pass despite defeating read-only org isolation. Check both restricted roles. |
| Blind2: incoming owner membership | high / patch | pg_auth_members filters only member; a foreign role granted Access owner can assume it. Also reject incoming owner memberships. |
| Blind3: unlogged relations | medium / patch | relpersistence absent from fixed table tuple; UNLOGGED keeps all tested fields while losing crash durability. Require permanent tables. |
| Blind4: inheritance | medium / patch | relispartition excludes partitions but not pg_inherits ordinary inheritance; reject parent/child links for both owned tables. |
| Blind5: Identity definer execution | high / patch | Relation/schema checks omit executable security-definer routines, which can convey cross-owner authority. Reject callable Access migrator authority (Identity schema USAGE plus definer EXECUTE). |
| Blind6: retained Identity snapshot | false / reject | Integration asserts Identity preservation across the Access upgrade. Retained evidence explicitly promises saved Access catalog/data and source/log checks, not future Identity-data immutability; later independent Identity changes do not invalidate that historical assertion. |
| Blind7: clean aggregate prerequisite | medium / patch | clean_previous explicitly allows already-upgraded clean state, so aggregate can skip initial creation. Require exact empty Access state first. |
| Blind8: unrelated DB errors satisfy denial | medium / patch | Broad DBAPIError catches omit SQLSTATE; make otherwise valid writes with required context and assert42501; constraint refusals assert23514/named CHECK or22003. |
| Blind9: preparation source custody | medium / patch | Aggregate hashes bootstrap only after preparation; no preparation-time witness binds actual executed bytes. Require unchanged before/after source witness for explicit fresh preparation. |
| Edge1: runtime elevated attributes | high / patch | Same independently verified defect as Blind1; grouped with it. |
| Edge2: unlogged tables | medium / patch | Same independently verified defect as Blind3; grouped with it. |
| Edge3: inheritance | medium / patch | Same independently verified defect as Blind4; grouped with it. |

Root final check: medium / patch — qualifier assertion-based fixture/custody checks can be stripped under optimized Python; refuse optimized execution before parsing/fixture/network and prove it with an actual -O subprocess.

Verification-gap lens: no findings. Eight surviving root causes receive direct fixed checks/assertions with no new public surface or framework.

Verification maintenance: existing invalid-private-fixture subprocess timed out repeatedly at its4s outer interpreter/import budget. A separately measured equivalent probe spent3.249s importing and0.001s rejecting the fixture without network. Increase only that test process budget to60s; retain all assertions/interpreter flags and all runtime/database deadlines. Its two-test module passed in4.47s. Other intermittent10s subprocess timeouts remain documented observations; do not infer host-load causality from later passes.

## Verification

Frozen Python: `platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python`. Smallest RED then focused tests, fresh actual aggregate, affected Access/PtS release and deployment migration-adapter tests, both composers and three independent reviews. Record exact commands/results. Root performs final independent checks/stop/commit.

Retained native run99b7231c-0a5b-4bdb-98e8-3329564c526a is normally stopped. Start/stop through existing dev.py and absolute pinned Supabase CLI under `.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/supabase/supabase`. Prior private preparation/evidence: `.local/identity-baseline/account-ensure-j9ial0p1/` under platform/deployment. Reuse its credential/run conventions but create fresh Access cases; never rerun old mutating stages or print credentials. Prepare only bounded synthetic Access owner/schema rights, preserving existing shared roles. One new case should contain real Identity18 for owner-boundary integration proof.

Final root verification: actual fresh --all59 PASS plus --verify-retained2 PASS on access-membership-final-optimized-20261021; preparation and aggregate bind130 unchanged executed sources. Restricted-owner contention1.472s, DDL contention4.447s, both recovery passes. Final affected regression1050 passed in84.93s using `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` and frozen Python `-I -B -m pytest services/access/tests apps/pts/tests/test_release.py platform/deployment/tests/test_migrate_adapter.py -q -p no:cacheprovider`. Both composer modes exit0. All39 historical pins match. Native run stopped normally with data/resources/receipts retained. Three review lenses complete; bounded patches verified. Existing portable bootstrap and unexplained intermittent legacy subprocess timing are deferred; no consumer/activation gate is cleared.
