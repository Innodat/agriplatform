---
title: Copyable owner-local atomic write and outcome prerequisite
type: feature
created: '2026-10-22'
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: 10b7c7fbf57eaf7c3160212f9b08dedf1bf65114
context:
  - AGENTS.md
  - platform/docs/architecture/contracts/owned-write-and-secret-execution.md
  - platform/builder-cli/WRITE_FINGERPRINT_EVIDENCE.md
---

<frozen-after-approval reason="user explicitly approves continued bounded WRITE atomic-write/outcome implementation and synthetic local/CI proof">

## Intent

Supply the bounded owner-local atomic-write/context/outcome prerequisite before KDG business APIs. Add a small copyable candidate beside the completed fingerprint example, with executable PostgreSQL proof of atomic effects/evidence/outcomes, concurrent retries and isolated transaction context. Keep application models and authority app-owned; no shared runtime service or speculative framework.

## Boundaries & Constraints

Follow the existing WRITE contract: exact organization/account/command/operation outcome identity, stable JCS SHA256 signed64 transaction advisory lock, current pre-lock authorization, ten-second monotonic total execution budget, one-second observation-to-local-start gap, capped two-second lock/five-second statement waits. No network under business locks. Context is verified backend input, transaction-local org/account/actor/mode, cleared on commit/rollback. Return compact acknowledgement only after durable commit; stored unsupported fingerprint/result metadata refuses without rewrite or fresh execution. Reuse completed HMAC helper and existing scaffold installer. Owner validates normalized command and command-specific compact receipt.

Synthetic fixture demonstrates account-command variant using neutral sample records, immutable local revision/evidence linked to outcome and exact executor/org/operation, FORCE RLS and restricted runtime/migrator separation. No-op records outcome without new business revision. Preserve all pre-existing sources, concurrent work, historical receipts and Docker resources. Keep dependency pins including TypeScript7.0.2. No production migrations, real-account/access, provisioning/deployment/pilot, resource cleanup, Leave/editor, public scaffold activation, secret-file lifecycle or first KDG API. Fresh synthetic database/roles are test fixtures only; retain them and proof outputs.

## I/O & Edge-Case Matrix

| Scenario | Expected behavior |
| --- | --- |
| Fresh valid operation | Effects, attribution, evidence and outcome commit together; return compact original result |
| Same key/input; lost response; later domain changes | Fresh authority then original receipt; no duplicate effect |
| Same key/changed payload or unavailable original key | Conflict or verification unavailable; preserve original outcome |
| Concurrent same key; different keys/stale revision | At most one effect per operation; revision arbitrates different operations |
| No-op or evidence/outcome insert failure | No fake revision; failure rolls back all local effects |
| Missing/wrong org/account/mode, pooled commit/rollback | No foreign access; transaction context does not survive reuse |
| Alternate immutable writes/linkage | UPDATE/DELETE/TRUNCATE and mismatched org/executor/outcome refuse |
| Lock wait, expired budget/observation, denial | Bounded safe refusal; only outcome-lock timeout maps operation_busy; no external wait under lock |
| Actual scaffold import/replay | Copied candidate executes; provenance and owner edits survive installer replay |

</frozen-after-approval>

## Code Map

- `platform/builder-cli/examples/owned-service/command_fingerprint.py`: copy sibling import; preserve bytes. Preserve older `transaction_context.py`.
- `platform/builder-cli/src/scaffold-install.ts`, `tests/test_command_fingerprint.py`: reuse real extension copy/provenance/preservation.
- `services/access/access_operator.py`: bounded execution and exact JCS lock tuple precedent; no runtime imports.
- `services/access/tests/qualify_application_register.py`: synthetic SQLAlchemy/psycopg pattern.
- Native run `99b7231c-0a5b-4bdb-98e8-3329564c526a`; root owns dev.py up/stop. Private admin_url: `platform/deployment/.local/identity-baseline/access-registry-reviewed-20261021/credentials.json`; use supabase_admin for exclusive test database preparation, never print credentials.

## Tasks & Acceptance

- [x] Add `platform/builder-cli/examples/owned-service/atomic_write.py`: lean bounded transaction/context/lock/outcome candidate with explicit owner-local orchestration, no configurable runtime engine. Keep domain SQL/result validation in owning sample. Bounded safe errors omit payload/SQL/credential exception chains.
- [x] Add `platform/builder-cli/tests/test_atomic_write.py` and focused SQL/qualification fixture beside tests as needed: observe missing-module acceptance RED before implementation; focused TDD, actual PostgreSQL role/RLS/race/rollback/pool/timeout matrix and installer copy proof. Fixture fails if native dependencies absent, no silent skips. Retain fresh test resources; don't clean up.
- [x] Update `examples/owned-service/README.md`, add `WRITE_ATOMIC_EVIDENCE.md`, update current `apps/kdg-capture/docs/next-session.md` section. Record exact commands/results, requirement-to-test mapping and five impact decisions. Root handles final evidence/audit/handoff.

Given a copied owner candidate, when a concurrent retry or failed evidence write occurs, then actual restricted PostgreSQL sessions prove one atomic committed result or complete rollback. Given permission loss before retry/lookup, when recovering an original operation, then no receipt is disclosed. Given a different operation uses the same UUID under another account/org/command, then exact keys remain isolated.

## Implementation Notes

Standing approval covers scope/dirty-tree preservation; no intent gaps. Python:
`platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python`.
Node: `platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node`.
Proof: `platform/builder-cli/.local/write-atomic-20261022`; exclusive attempt subdirectories.
Root owns lifecycle/evidence/audit/handoff; implementation agent owns example/tests/README.
Private fixture configuration stays under proof; no DSNs, keys or payload in output.
Existing environment supplies dependencies. Root observed missing-module RED and resumed
native run before implementation. Internal API choices are delegated. No agent commits/staging; root records only the completed scope as required by Build.

Review corrections add actual short-budget idle expiry, controlled-clock freshness,
late commit acknowledgement, active-key rollback and existing-record linkage cases.
Root also adds `platform/builder-cli/.gitignore` with the existing deployment `.local/`
convention: private synthetic credentials/proof must be ignored, preserving their bytes.

## Spec Change Log

## Review Triage Log

| Finding | Verdict | Evidence and route |
| --- | --- | --- |
| Blind1: revision FK omits target | medium | Real alternate write can link an existing same-scope record B to outcome A; patch composite unique/FK and actual two-record negative test. |
| Blind2: revision insert omits original-owner context | medium | Executor checks alone permit evidence for a known foreign-owned record through FK visibility; patch original owner check plus actual foreign-owned record case. |
| Blind3: stored target mismatch does not reauthorize/restart | low | Sample conservatively refuses before disclosure; candidate explicitly leaves stored-resource authority/restart to owner. Reject added restart orchestration complexity for changed-target sample retries; document this sample limitation and mandatory consuming behavior. |
| Blind4: missing/bad active key leaks KeyError/FingerprintError | medium | Direct keys[active] occurs after tentative mutation; transaction rolls back but errors bypass safe owner contract. Patch safe fingerprint creation translation and rollback tests. |
| Blind5: typed IDs checked after authority callback | medium | Invalid org/account/operation reaches sample callback; move existing typed validation before callback and test callback remains untouched. |
| Blind6: malformed doc/payload containers raise raw errors | medium | set(payload=None) raises TypeError; add exact dict guards and focused malformed-container cases. |
| Blind7: server deadlines cannot bound socket/commit response waits | medium | Real transport limitation; patch documentation to distinguish monotonic checks/server bounds from transport wall-clock guarantees. No new transport framework in this candidate. |
| Blind8: server transaction timeout lacks actual idle proof | medium | Existing pg_sleep test exercises statement timeout after entry; add idle-lock server-expiry rollback/release test. |
| Blind9: random lock vector lacks historical literal | low | Independent oracle is correct but no fixed retained vector; direct test correction to literal tuple and expected signed integer. |
| Verification1: no server transaction deadline behavioral test | medium | Pre-verified; same root as Blind8. Patch actual idle transaction expiry independently of Python deadline checks. |
| Verification2: observation-age test only checks pre-execution input | medium | Existing started_at-2 fails separate boundary; patch controlled-clock in-budget stale/fresh cases. |
| Edge1: no deadline check after COMMIT acknowledgement | medium | Final check precedes commit; patch postcommit remaining check and late acknowledgement test, preserving truthful uncertainty. |
| Edge2: revision FK permits different target record | medium | Same demonstrated linkage defect as Blind1/2; patch exact target and owner bindings with native alternate-write tests. |
| Root: synthetic private proof directory unignored | medium | Builder lacked deployment's `.local/` exclusion; add the same one-line ignore rule and verify fixture.json excluded with git check-ignore. Historical evidence bytes stay intact. |
| Root: new linkage negative hits existing unique outcome constraint | medium | Copying an existing revision reuses an already-linked outcome, masking target-FK removal. Use an actual no-op outcome and verify FK23503 versus foreign-owner RLS42501 independently. |


## Verification

Run focused pytest using prepared Python with explicit prepared Node and private native fixture path; run existing fingerprint tests and Node builder suite. Root audits scoped diff and baseline hashes. No historical migration edits or Access behavior changes; no full owner regression claim. Scaffold impact: copied candidate/import proof only; shared UI unchanged; agent context unchanged; docs example/evidence/handoff; ADR unchanged. This increment does not qualify complete WRITE, secret loading/backup/restore or consumer release readiness.


## Completion

Root observed missing-module acceptance RED before production edits. Final reviewed
native/fingerprint matrix100 PASS (37 atomic/63 fingerprint), existing builder62 PASS;
all matrix rows execute without skips. Three review lenses complete; individual
triage above, corrections verified and no new deferrals. Independent read-only retained
inspection PASS; normal dev.py stop completed with all data/volumes/resources retained.
Eight final execution-source hashes match;28 proof inputs/logs bound.450 of454 protected
owner/dependency files unchanged; four concurrent Scribeswell release-tool edits excluded
and preserved, as are ongoing Leave/Scribeswell planning changes. All approved dependency
pins including TypeScript7.0.2 and historical Access/Identity/builder bytes remain intact.
Root added ignored proof hygiene and unresolved/foreign-lookup acceptance. Full WRITE,
secret-file/data recovery, consumer and release gates remain. See owner evidence for
exact commands, traceability, limits and final audit. Scope-only local Build commit;
no push or excluded work.
