---
title: Read-only Scribeswell database audit candidate
type: feature
created: 2026-10-22
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: 8b5f37546e1fb2cd4117e5304bc6efa9ffdd1695
context:
  - AGENTS.md
  - _bmad-output/specs/spec-scribeswell-studies/corpus-publication.md
  - apps/scribeswell/docs/CORPUS_EVIDENCE.md
---

<frozen-after-approval reason="User next continues authorized bounded BMAD delivery; preserve working-tree and owner boundaries">

## Intent

Establish exact correspondence between a qualified source artifact and a complete corpus database snapshot, prerequisite to ST-37/ST-38. Implement the canonical companion's read-only database audit candidate contract, recording observed word identities without claiming publication readiness.

## Boundaries & Constraints

Always rebuild source evidence before connecting; compare every owned corpus book/chapter/verse/word in one bounded repeatable-read read-only snapshot using existing runtime authority. Exact surfaces, relationships and observed IDs must match the canonical contract. Output after releasing the snapshot; safe fixed diagnostics and atomic create-only files.

Never mutate source/database/grants/schema, configure production, load dotenv, trust submitted candidate proof, alter importer/public API behavior, activate or seal publication, implement Access/Identity/Leave/factory, or claim full ST-37/ST-38. Existing writers remain unfenced; this is a historical observation only. Preserve other sessions' changes.

## I/O & Edge-Case Matrix

| Scenario | Expected behavior |
| --- | --- |
| Complete qualified source/database match | Closed deterministic audit candidate with exact counts/digests and ordered positive decimal-string word IDs; publication false. |
| Missing/extra chapter/verse/word, malformed ID/position/surface or denormalization | Safe nonzero failure and no destination; do not hide rows behind inner joins or truncate. |
| Reused IDs with changed text / regenerated IDs with identical text | First fails; second passes with changed observed IDs and unchanged digest. |
| Concurrent source write during audit | One coherent old snapshot may pass; fresh audit detects change. Writer is not blocked by audit coordination locks. |
| Wrong authority, DB failure, deadline/row/field/output excess | Safe fixed error, bounded exit, snapshot/connection released, no candidate. |
| Existing/racing output or cleanup failure | Preserve prior files; reuse source tool atomic/error/reconciliation behavior. |

</frozen-after-approval>

## Code Map

- `backend/corpus_evidence.py` under `apps/scribeswell/`: source qualification, exact encoder, safe EvidenceError, deterministic serializer. Reuse without changing its behavior.
- `backend/corpus_source.py`: owning BOOK_METADATA. `backend/database.py`: runtime URL validation, safe errors/pool policy; default transaction isolation is insufficient. Do not broaden generic repository authority.
- New `backend/corpus_database_audit.py`: bounded coherent comparison. New `tools/py/audit_corpus_database.py`: operator CLI, no dotenv. Reuse existing `tools/py/build_source_evidence.py` atomic output/parser helpers locally.
- New `tests/test_corpus_database_audit.py`: focused and real PostgreSQL acceptance; reuse guarded fixtures in `tests/test_postgres_acceptance.py` without weakening them. It creates only a unique database/known absent roles and drops owned resources.
- `docs/CORPUS_EVIDENCE.md`: extend executable owner documentation. Root owns canonical memlog/companions and this delivery item.

## Tasks & Acceptance

- [x] Observe missing audit CLI/library acceptance failure first; use focused TDD for comparison/bounds. Existing PostgreSQL baseline already passed 17 cases.
- [x] Implement canonical contract exactly: complete metadata/inventories, denormalized parent checks, exact streamed token digests, globally unique positive observed IDs, reusable source candidate hash and closed output envelope.
- [x] Enforce explicit environment-only `SCRIBESWELL_AUDIT_DATABASE_URL`, existing runtime URL/TLS validation and actual current_user. One repeatable-read read-only snapshot; 60-second DB workflow including connect, capped SQL waits and batches/rows/bytes/output as companion specifies. No filesystem operations during snapshot or unbounded text transfer.
- [x] Prove every matrix row with tests, including actual concurrent PostgreSQL snapshot, read-only enforcement, cancellation/deadline cleanup, full checked-in source and complete synthetic 39-book corpus. Full-source test may seed tables with fixture-admin COPY for speed; only tests write and no production data is involved.
- [x] Extend app contract documentation; report exact red/green and affected regression commands. Do not change existing expected results to dismiss failures.

Given qualified input and matching database, when CLI runs twice, then candidate bytes match and source/database remain unchanged. Given a malformed/mismatched database or operational failure, when invoked, then it exits safely without creating output. Given concurrent writes, when auditing, then a coherent snapshot is used and no durable ready-proof claim is emitted.

## Implementation Notes

Intent gaps: none. No irreversible external actions; only reversible app-local code and guarded disposable DB tests. Footprint: three new app files plus existing docs and possibly fixture reuse. Scaffold/shared UI/agent-context/ADR impact: none; existing release/owner decisions retained, factory belongs to separate session. Access currently offers organization-scoped /v2/check, not Studies account enrollment; no owner files change here.

Python 3.12 test environment: `/tmp/scribeswell-studies-tests-py312/bin/python`. Root-created isolated PostgreSQL 17 container `scribeswell-corpus-audit-20261022` (ID `316fe6bf8ba76f991ba2c2ec343c4fdc67a80aa618ebeee8870c7ea0b1053991`, image `sha256:212aeeeb8faaef6c46498d86cbec6b9344d8d9492996b174664ff82c562ab685`), localhost-only dynamic port 32768, no persistent volume. Fixture admin URL `postgresql://postgres:fixture@127.0.0.1:32768/postgres` supplied only as `SCRIBESWELL_TEST_DATABASE_URL`. Agent may run guarded tests against that test container outside sandbox as needed; root owns stopping it. Never inspect/use workstation credential files or other containers. Root keeps canonical planning files excluded from scoped commit like preceding slices.

## Verification

Agent initial red: missing `corpus_database_audit` acceptance. Initial real PostgreSQL tests progressed through 33 passes; full fixture COPY hit a test-admin timeout retained by a concurrency case, then fixture setup was corrected without weakening expectations. Pre-worker suite passed 34/34 (12.22s); supervised-worker suite passed 40/40 (28.90s). Existing PostgreSQL baseline/regression passed 17/17 (1.93s), one existing Starlette/httpx warning.

Root supplemental red: `SCRIBESWELL_TEST_DATABASE_URL=postgresql://postgres:fixture@127.0.0.1:32768/postgres timeout 60 /tmp/scribeswell-studies-tests-py312/bin/python -m pytest /tmp/test_scribeswell_audit_visibility.py -q` — one failure, 0.46s: restrictive SELECT policy hid an extra word and audit succeeded. Real gap patched before independent review: require conservative catalogue full-row-visibility qualification, no RLS bypass/new authority/coordination locks; assume controlled schema/policy DDL remains stable while supporting concurrent ordinary corpus DML. Safe pre-IPC Unicode validation and audit URL removal from child environment added alongside. Canonical companion records these refinements.

Agent focused patch tests: 4 passed, 39 deselected (surrogate URL, worker environment, supervised timeout, worker failure); an additional PG tool call was interrupted without result, not counted. Root completed remaining documentation corrections and reran the exact supplemental visibility command: **1 passed, 0.34s**, against the disposable database. Wider post-patch verification follows independent review.

Concrete implementation refinement from owner-library inspection: SQL timeouts cannot bound client transport or DNS. Use a supervised standard-library subprocess for the DB snapshot only, passing qualified internal request and URL via stdin, safe bounded JSON reply, timeout kills/reaps worker, parent-only output. Source qualification precedes subprocess budget; startup/IPC count toward the 60 seconds. Preserve psycopg>=3.2 compatibility. Canonical companion records this mechanism. Agent-owned worker file may be added if needed; no API/runtime/schema change.

## Review Triage Log

Three fresh context-free reviewers launched before handling any result. All reported; edge review returned no findings. Task-only diff excludes all pre-existing and concurrent owner changes. Verdicts below precede grouping.

| Finding | Verdict | Evidence / route |
| --- | --- | --- |
| B1: parent buffers unbounded faulty worker stdout | false | Fixed owning `_worker_main` serializes its controlled observation and checks the 64-MiB cap before any successful write; failures emit only fixed tiny JSON. Command is fixed app-local code, not operator-configurable. No production producer can emit an unbounded stream; post-buffer parent check is defense in depth. A replaced/faulty executable is not a demonstrated current source/DB input. No streaming/thread machinery added. |
| B2: malformed worker JSON shape / recursion escapes safe errors | medium | Parent calls result.get on failed non-object JSON and does not map RecursionError. Existing worker-failure surface promises fixed failures. Patch minimal response-object validation and recursion mapping with real subprocess malformed-response cases. |
| B3: correct role name with SUPERUSER/BYPASSRLS accepted | medium | `_audit_snapshot` checks only current_user; visibility helper accepts inactive RLS under elevated attributes. This violates restricted/no-bypass operator authority. Patch actual role attribute check and real contaminated-role tests, restoring attributes afterward. |
| B4: ambient libpq environment can redirect target | medium | Popen copies PGHOSTADDR and other PG* settings; libpq can consume them beyond validated URL. Patch explicit URL-only worker connection environment by excluding PG*; document it and prove hostile PGHOSTADDR cannot redirect the qualified local test target. No shared runtime repository change. |
| B5: policy/relation guard branches lack tests | medium | Filed evidence identifies missing permissive-only filter, effective inherited-role, irrelevant restrictive-role and replacement-view cases. Guard implements these distinctions and determines full-inventory qualification. Patch bounded real PostgreSQL cases with complete cleanup; no new policy or role outside test fixtures. |
| B6: supervised timeout lacks actual open-transaction cleanup proof | medium | Existing sleeping-worker kill/reap test has no DB connection; SQL cancellation test uses private in-process helper. Patch supervised real open read-only transaction timeout and verify its backend disappears with bounded observation. |
| B7: documentation hardcodes session-only test interpreter | low | Both new and prior command examples rely on uncreated `/tmp` environment, causing fresh checkout failure. Direct documentation correction: reproducible Python 3.12/dependency setup, portable activated-env command, explicit disposable-local test URL prerequisite. |
| V1: no filtering permissive-only RLS regression | medium | Pre-verified: deleting literal-true predicate still passes restrictive-policy test, while filtering permissive policy can hide extra data. Add real test with extra word and replace/restore all applicable permissive policies; require visibility_unproven. |

Survivor groups: safe worker response handling (B2); actual restricted role authority (B3); declared libpq environment (B4); visibility branch evidence (B5/V1); supervised backend cleanup (B6); portable developer commands (B7). All add no public surface and address demonstrated states or verified gaps. No intent gap, spec loopback or deferred findings.

## Final verification and traceability

Same implementation agent patched the review survivors. Focused checks: **9 passed / 48 deselected** for subprocess/error/environment handling, then **8 passed / 49 deselected** for new real PostgreSQL cases (4.30s); its session 95070 completed before root began shared-fixture tests. Root inspected the final changes and rewrote the task-only diff. Documentation now creates its own Python 3.12 environment under the app's ignored `.local` path and names the explicit disposable-local test prerequisite.

Root final command, outside sandbox for localhost PostgreSQL/TestClient access:

```sh
SCRIBESWELL_TEST_DATABASE_URL=postgresql://postgres:fixture@127.0.0.1:32768/postgres timeout 120 /tmp/scribeswell-studies-tests-py312/bin/python -m pytest apps/scribeswell/tests -q
```

**160 passed, no skips, one existing Starlette/httpx deprecation warning, 50.17s.** Includes all 57 audit cases, 17 existing actual PostgreSQL acceptance cases and 86 source/importer/reader/lexicon/database-adapter regressions. No frontend/browser code changed; no browser/build rerun claimed. There is no affected app-wide lint/type-check command. No schema composition or migration file changed, so no migration execution or database-composition claim is needed.

| Requirement / matrix | Actual checks run in final suite |
| --- | --- |
| Complete exact historical correspondence (ST-37/ST-38 subset) | Complete synthetic 39-book candidate determinism and no data mutation; full checked-in source fixture COPY plus audited 39 books / 929 chapters / 23,213 verses / 306,785 exact tokens. Closed envelope/source-candidate hash/ordered IDs. No morpheme/full production-corpus qualification claim. |
| Inventory/relationships and exact anchors | Missing/extra tables' rows, malformed/nonpositive IDs/positions, orphan/denormalized parent data, oversized/changed surfaces; unchanged IDs with changed text fail; regenerated IDs with identical tokens pass with changed observations. |
| Coherent snapshot and no business lock | Actual repeatable-read read-only snapshot; concurrent committed corpus write succeeds while old coherent audit passes, fresh audit fails. Actual read-only DDL rejection; private helper uses same worker implementation. |
| Complete visible inventory | Runtime/PUBLIC restrictive and permissive-only filtering policies, effective inherited and irrelevant role policies, replacement view rejection, ordinary base-table visibility and recovery after fixture cleanup. Supplemental root failing visibility proof became green before independent review. |
| Restricted current authority/config | Actual current login plus SUPERUSER/BYPASSRLS rejection/restoration; invalid/surrogate URL before launch; hostile PGHOSTADDR/PGPORT/PGOPTIONS excluded; audit URL absent from child environment and stdin preserved. |
| Bounded safe failure and cleanup | Expected+1 row limit, batches/projection, count/output bounds; SQL cancellation/connection closure; supervised timeout kill/reap; real open read-only backend readiness and disappearance; malformed/recursive worker responses and arbitrary-output suppression. |
| Atomic output | CLI twice identical and source unchanged, mismatch creates no output, existing/symlink output preserved; source helper's injected destination race/write/cleanup tests also rerun in final full suite. Audit cleanup-after-link case verifies recoverable complete destination. |
| Compatibility | Existing 17 real PostgreSQL importer/runtime/RLS/bootstrap/timeouts and 86 earlier app regressions pass unchanged. No shared-owner, Access or factory tests claimed. |

Root canonical check passes authored-document links/whitespace and stable 11 CAP/38 ST IDs; 19 SPEC companions remain resolvable. Scoped app `git diff --check` passes. Independent review triage has no deferred findings.

Disposable PostgreSQL 17 used fixture-only authority. All DB mutation was confined to guarded tests; the auditor itself performs read-only queries. Root stopped exact owned container ID `316fe6bf8ba76f991ba2c2ec343c4fdc67a80aa618ebeee8870c7ea0b1053991` after verification; stop succeeded and `--rm` removes its memory-backed test state. No other service/container touched, no production database read or change, no migration, activation, push or deploy.

Concurrent Access owner commit `1f7edfe61e314d76fa1f4a4e0a0c6ba768adffcc` remains intact; its organization check is not Studies account enrollment. Canonical updates remain in the pre-existing untracked planning tree and are excluded from this task-only commit, as are pre-existing app README and other sessions' changes. Next corpus delivery must close actual writer fencing/sealed-audit/publication contracts and release recovery before source proof or highlights depend on them.

Baseline: `SCRIBESWELL_TEST_DATABASE_URL=postgresql://postgres:fixture@127.0.0.1:32768/postgres timeout 60 /tmp/scribeswell-studies-tests-py312/bin/python -m pytest apps/scribeswell/tests/test_postgres_acceptance.py -q` — 17 passed, one existing Starlette/httpx warning, 7.01s, outside sandbox. Implementation must record observed acceptance red, focused results, actual PostgreSQL cases and affected app suite; no skipped database checks count as acceptance.
