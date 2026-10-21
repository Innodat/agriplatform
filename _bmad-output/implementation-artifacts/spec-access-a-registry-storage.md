---
title: 'ACCESS-A global registration storage'
type: 'feature'
created: '2026-10-21'
status: 'done'
route: 'dispatch'
baseline_commit: 'bd2e6f0156f4993fd5433d40c70249ae371564fc'
review_loop_iteration: 0
context:
  - 'AGENTS.md'
  - 'platform/deployment/DEVELOPMENT.md'
  - 'platform/docs/architecture/contracts/identity-access-execution-substrate.md'
---

<frozen-after-approval reason="standing authorization for bounded shared prerequisites">

## Intent

Stage the global application/capability/entry registry through Access owner migration, prerequisite to protected registration and exact-membership checks.

## Boundaries & Constraints

Access0003 adds only empty applications, permissions and entry_permissions per the execution substrate's exact persistence table. Registry IDs use ASCII `[a-z][a-z0-9_]{1,63}`; permission IDs are literal ASCII1–200 bytes, not printable-only or prefix rules. Required actor UUIDs are non-nil; timestamptz attribution is finite. Preserve positive bigint revision/default1 and disabled-default application state, both permission scope/association unique keys and RESTRICT FKs, especially the matching-app composite entry FK. No Identity FKs.

All new objects remain private to access_migrator. No new login/reader/command roles or runtime privileges. For this storage stage refuse UPDATE/DELETE/TRUNCATE of new registry rows, including noops; later mutable commands need an explicit migration. Owner fixture inserts supply attribution, not proof of protected command verification. No application rows, capabilities, entry mappings or grants are seeded by migration.

Preserve historical migrations/pins, grants/ACL/RLS, receipts/resources and concurrent work. PtS scope is account; never reinterpret retained organization grants. No grants FK/CHECK replacement, org admission/account grants, commands/API/UI/client, backfill, generator or dependency changes (TypeScript7.0.2 stays). v1 stays stopped/incompatible; consumer gates stay closed. Synthetic local/CI and scoped local commit only: no real account/access, production/provision/deploy/pilot, reset/prune, Leave/editor or push.

## I/O & Edge-Case Matrix

| Given / when | Then |
| --- | --- |
| Fresh clean, exact1 or populated exact2 / upgrade | Exact3; empty new registry; original grants/history preserved; no Identity dependency |
| Valid application/permission/matching entry / owner fixture insert | Defaults and exact local relationships hold; both scopes per app |
| Invalid IDs/ASCII lengths, scope, missing/wrong app, duplicates, nil actors, nonfinite time, nonpositive revision | Intended named CHECK/FK/unique failure; atomic unchanged state |
| Populated exact3 / repeat | Data/catalog/ACL unchanged |
| Registry update/delete/truncate, including noop and multirow attempts | Fixed refusal; complete rollback, no reassignment/history loss |
| Runtime/browser/PUBLIC access or owner assumption | Registry read/write/DDL/EXECUTE denied; grants unchanged |
| Unknown history, object/constraint/function/trigger/default/ACL drift | Refuse without normalization |
| Held migration/DDL lock or injected failure / retry after release | Bounded refusal/rollback; explicit recovery |

</frozen-after-approval>

## Code Map

Access owner root is `services/access/`.

- `migrations/access_baseline.py`: fixed known1/2/3 catalogs; membership_id remains at2/3. `migrations/env.py` already supplies bounds/serialization/safe errors.
- New `migrations/versions/0003_registry_storage.py`: three tables and private immutable guards; secure search_path/ACL atomically.
- Existing `tests/qualify_access_membership_binding.py`: reuse native fixture/URL/error/custody helpers. New qualifier must also snapshot registry data/routine bodies. Never rewrite old receipts.
- Existing operator input/target/CLI are Identity-bound; Access commands require later infrastructure. Reuse current deployment coordinator; no new framework.

## Tasks & Acceptance

Paths below are relative to services/access unless prefixed otherwise.

- [x] New `tests/test_access_registry_storage.py`, `tests/qualify_access_registry_storage.py`: missing-registry actual RED first; behavioral matrix, intended SQLSTATE/constraint and preserved-state assertions.
- [x] New revision0003 and existing baseline: exact additive catalogs/private guards; characterize affected behavior before refactoring.
- [x] Qualifier: fresh --all and retained inspection, unchanged real Identity18, actual restricted roles, complete before/after source/bootstrap custody; refuse optimized Python before fixture/network.
- [x] New `ACCESS_REGISTRY_STORAGE_EVIDENCE.md`; existing platform owner contract/runbook and KDG next-session: requirement/test commands/results and five impacts.

Given successful storage staging without commands/consumers, then no effective access or activation is claimed. Migration failure still blocks the existing release route.

## Implementation Notes

No intent gap or production effects. Five impacts: extend existing owner/scaffold fixtures; no shared UI; refresh KDG context; update owner/runbook evidence; existing ADRs suffice and stay immutable.

## Spec Change Log

## Review Triage Log

| Finding | Verdict / route | Verified evidence |
| --- | --- | --- |
| Blind1: internal FK enforcement triggers | high / patch | verify_registry excludes internal triggers; a disabled RI trigger retains the same FK definition/convalidated flag. Reject disabled internal enforcement and preserve its state in snapshots. |
| Blind2: atomic snapshot isolation | medium / patch | Multi-query db.begin uses READ COMMITTED. Use bounded repeatable-read/read-only observation for the new complete Access snapshot. |
| Blind3: retained Identity data | false / reject | Retained contract explicitly checks Access snapshots/source/log witnesses. Integration proves Identity unchanged across migration, not perpetual Identity-data immutability after independently owned work. No continued Identity-data freeze is claimed. |
| Blind4: retained case inventory | medium / patch | expected snapshots dictate their own case keys; truncation could silently skip data comparisons. Require exact fixture-derived expected case set. |
| Blind5: source inventory freshness | medium / patch | Final hashes reuse start paths; files added during execution escape closure. Rediscover source inventory at completion and compare keys/hashes. |
| Blind6: inherited membership boundaries | medium / patch | Registry override replaces old boundary stage, leaving actual invalid membership values/non-null runtime read unchecked in the new aggregate. Restore those small behavioral assertions under head3. |
| Blind7: UPSERT/MERGE paths | medium / patch | New statement guards are not exercised by alternate update forms. Add conflicting/noop/multirow variants and preserved-state assertions. |
| Blind8: non-UTF8 ASCII assumption | medium / patch | length(text)=UTF8 octet length assumes character-aware source encoding and does not establish ASCII on SQL_ASCII. Explicitly require selected UTF8 encoding before migration effects and qualify refusal. |
| Blind9: ATDD chronology | medium / reject proposed spec edit | Actual baseline RED followed draft source edits; evidence already says so and does not claim test-first source implementation. This process-order deviation cannot be repaired retroactively. Suggested fix edits this build spec and is rejected by review rules; preserve the explicit limitation in final evidence, without claiming strict ATDD ordering. |
| Edge1: disabled internal FK triggers | high / patch | Same demonstrated exclusion as Blind1; group with it. |
| Gap1: guard security/search_path mutations | medium / patch | Filed verified gap: body drift keeps security/settings unchanged. Add independent SECURITY DEFINER and RESET search_path cases, asserting refusal and preserved state. |

Eight patch groups; no new product choice or public surface. Existing portable-bootstrap/timing follow-ups remain separate. Baseline replay is useful acceptance evidence, not evidence that actual acceptance RED preceded source edits.

## Verification

Use frozen Python `platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python`. Focused RED/GREEN, fresh --all, --verify-retained, affected Access/PtS release/deployment-adapter tests, both composer check-only modes, three reviews; root independently verifies/stops/commits. Preserve /tmp/access-registry-protected-history.json (40 historical files).

Native run99b7231c-0a5b-4bdb-98e8-3329564c526a is stopped. Use existing dev.py and pinned CLI in toolchain ad277eef-a10e-4aac-bb82-5743653fb2e0. Reuse preparation conventions in platform/deployment/.local/identity-baseline/access-membership-final-optimized-20261021, but use fresh cases and no old mutating stages. Preserve credentials/resources; keep portability/timing follow-ups separate.

Final independent verification: reviewed frame access-registry-reviewed-20261021, --all82 PASS plus --verify-retained2 PASS;132 unchanged executed sources,40 historical pins unchanged. Advisory/DDL refusal0.552s/3.641s with recovery. Frozen Python with PYTEST_DISABLE_PLUGIN_AUTOLOAD=1, -I -B pytest over services/access/tests, apps/pts/tests/test_release.py and platform/deployment/tests/test_migrate_adapter.py:1075 passed36.67s. Both composer check-only modes exit0. Three review lenses complete, technical patches verified; native run stopped normally with data/resources/receipts retained. Strict ATDD chronology remains a recorded process limitation: actual baseline RED followed draft source edits. No effective access or consumer activation claim.
