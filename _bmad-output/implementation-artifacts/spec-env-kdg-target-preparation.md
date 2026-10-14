---
title: 'ENV: guarded KDG disposable target preparation'
type: feature
created: '2026-10-14'
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: 2c8178679144cfd3e8d91ca0d66d979855c39b0f
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/platform/docs/architecture/contracts/scaffold-environment-and-generation.md'
  - '{project-root}/platform/docs/architecture/contracts/scaffold-dependency-baseline-2026-10-14.md'
---

<frozen-after-approval reason="User explicitly authorized first bounded foundation implementation and synthetic verification, preserving the dirty tree">

## Intent

**Problem:** ENV has no guarded disposable-target command. Existing templates are not an executable generator, and a planning PASS cannot establish runtime readiness.

**Approach:** Deliver target preparation as the first bounded increment of the existing ENV item. Validate the approved closed target input and materialize protected, deterministic run identity/source evidence under the existing deployment owner. Finish and verify this increment before dependent foundations. The enclosing ENV runtime/bootstrap acceptance remains open; P1/SERVICE generation, locks/images and actual Auth/database proof are subsequent work, not claimed here.

## Boundaries & Constraints

**Always:** Preserve current changes including concurrent Leave/PtS documents. Use `python3 platform/deployment/dev.py prepare --target <JSON> --run-id <UUID>`. Use approved selected versions including TypeScript 7.0.2; reference/hash the approved baseline without downgrading it or claiming installed compatibility. Resolve workspace root from command source, never supplied target authority. Only `local_disposable` / `ci_disposable`, exact KDG owner set, approved localhost ports/origins/callbacks and run-owned ignored paths are admitted in this first implementation. Validate schema and semantic safety before writes; safe JSON diagnostics only. Existing ENV owns this implementation; no parallel generator, lifecycle or shared offline service.

**Never:** Implement Leave or KDG domain/editor/auth/Access/WRITE. Run migrations, accounts/grants, infrastructure, deployment, real-data fixtures, shell commands from configuration or secrets generation. Read secret contents or include credentials in metadata/errors. Touch live/root Supabase configuration. Treat a prepare receipt as runtime or provider/device qualification. Other lifecycle commands must fail explicitly until actual guarded runtime adapters exist.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
| --- | --- | --- | --- |
| Synthetic preparation | Valid target + canonical UUID, free ports | Protected run inventory binds project/container/network/volume IDs, target/source/fixture/registry/schema/baseline hashes; runtime_ready false | Safe nonzero stage code on failure |
| Repeat | Identical prepared input | Same inventory, no replacement or new run | Changed source/config refuses reuse |
| Unsafe input | Missing/unknown/duplicate keys, bool-as-int, production endpoint, foreign owner, invalid UUID, bad ports | Refuse before run mutation | No raw input/exception dump |
| Filesystem escape | Traversal, symlink target/source/ancestor, foreign prepared directory | Refuse before writing outside intended run | Safe stage reference |
| Occupied target | A required port is already bound | Refuse without attaching to existing process/database | No fallback ports |
| Missing runtime | up/verify/stop/reset, even prepared | Nonzero unqualified stage; reset requires explicit matching confirmation | No processes, SQL, fixture or data changes |

</frozen-after-approval>

## Code Map

- `platform/deployment/`: existing ENV owner; `.local/` already ignored. Add `dev.py`, closed JSON Schema and checked-in synthetic target/fixture inputs here.
- `platform/deployment/target_contract.py`: production Supabase URL validator; retain unchanged.
- `platform/deployment/release.py:coordinate`: existing migration coordinator for future runtime delivery; do not duplicate/invoke in preparation.
- `platform/deployment/tests/`: existing dependency-free unittest convention, reuse it. Bootstrap command may run on current Python; record it separately from selected runtime qualification.
- `platform/builder-cli/`: templates/README only; no generator CLI yet. Add short navigation to actual ENV command, do not add generation claims.
- `apps/kdg-capture/docs/shared-prerequisites.md`: authoritative owner order; do not overwrite concurrent Leave planning or create duplicate product specifications.

## Tasks & Acceptance

**Execution:**
- [x] `platform/deployment/tests/test_dev.py` — first observe subprocess acceptance failure for prepare; add focused guard tests before implementation and exact red/green evidence.
- [x] `platform/deployment/schema/development-target-v1.json`, `platform/deployment/environments/kdg-local.json`, synthetic fixture — define closed versioned inputs consistent with owning contract. Missing local secrets are references only, not required or read at prepare.
- [x] `platform/deployment/dev.py` — implement preparation, guarded idempotence/source binding and explicit refusal of undelivered lifecycle stages; protect inventory using exclusive creation/locking and atomic file installation; reject unexpected files rather than adopt them.
- [x] `platform/deployment/DEVELOPMENT.md`, builder README and foundation evidence — document commands, requirement/test traceability, actual results, five impacts and remaining enclosing ENV gates.

**Acceptance Criteria:**
- Given a fresh synthetic disposable target, when prepare runs and repeats, then only its ignored UUID run is materialized, stable source/target evidence is verified and readiness remains false.
- Given each matrix adversary, when the public CLI runs, then it refuses safely without mutating unrelated files or running owner commands.
- Given preparation completion, when evidence is read, then implementation scope and exact tests distinguish this completed increment from pending full ENV runtime and P1/SERVICE proof.

## Implementation Notes

User authorization takes precedence over Build's redundant dirty-tree/spec approval checkpoints; the approved current owner contracts remain authority. bmad-help selected ENV before P1/SERVICE and shared runtime dependencies. No new product requirements or owner acknowledgement requested.

Implementation and matrix audit complete. Initial acceptance failed because dev.py did not exist. Focused suite grew from eight to twelve passing tests; review regressions reproduced three failures/one error before fixes, then all sixteen passed. Final existing-owner regression: 135 tests in 15.450s, OK. All matrix rows have executed public CLI coverage; exact commands/results and five impacts are in platform/deployment/ENV_PREPARATION_EVIDENCE.md. Fresh final-source preparation/repeat succeeded for run c0ba3257-bd18-430e-b705-23fbfba59632; verify exited2/runtime_adapter_unqualified as required. KDG current README, next-session, testing navigation and memlog now distinguish approval/completed preparation from open runtime prerequisites. No enclosing ENV or KDG runtime acceptance is marked passed.

## Spec Change Log

## Review Triage Log

| Finding | Verdict | Evidence / disposition |
| --- | --- | --- |
| Blind1: inventory bool/int equality | medium | Python dictionary comparison equates true/1 and false/0 at the repeat guard. Patch exact JSON comparison and tamper cases. |
| Blind2: writable .local ancestor | medium | Only final kdg/run permissions are checked; a writable non-sticky parent permits another user to rename its child. Patch mutable ancestor checks and refusal proof. |
| Blind3: directory durability | medium | mkdir parent entries and lock removal lack directory fsync, so a successful receipt can recover without its reachable run or with a stale lock. Patch fsync sequence. |
| Blind4: malformed schema root | medium | Empty array/string reaches schema.get and raises uncaught AttributeError. Patch object guard and public CLI cases. |
| Blind5: fixture contents not validated | false | Preparation hashes opaque owner source only; it never parses/provisions accounts or claims runtime-fixture validation. DEVELOPMENT explicitly calls the fixture metadata-only and runtime_ready remains false. Owner-source edits require a new run. |
| Blind6: IPv6/additional port coverage | medium | Existing occupied-port proof tests only IPv4 web5188 although the contract probes all eight dual-stack ports. Patch focused port cases. |
| Blind7: lifecycle error-code coverage | medium | Generic failure assertions could pass on unrelated validation failures; reset confirmation branches are not distinguished. Patch exact stage/code assertions. |
| Edge1: inventory bool/int equality | medium | Same demonstrated dictionary equality defect as Blind1; grouped for the same patch and regression proof. |
| Edge2: malformed schema root | medium | Same uncaught schema.get path as Blind4; grouped for safe refusal patch. |
| Verification1: reserved identity values | medium | No test checks the UUID-derived values; a constant project prefix mutation would survive the current suite. Patch exact two-run/disjoint identity proof. |

Resolution: all nine accepted findings fixed in seven patch groups. Parent applied the small review corrections after the implementation agent's follow-up tool execution stalled awaiting escalation; no pending agent edits remain. No defects deferred. Directory creation and lock removal now fsync their parent entries; output ancestors reject group/other writes while allowing owner-controlled .local0755. Inventory comparisons preserve JSON types; malformed schema roots refuse safely. Focused tests cover exact lifecycle stage/code, IPv6/second-port refusal and exact/disjoint reserved names.

## Verification

- `python3 -m unittest discover -s platform/deployment/tests -p test_dev.py -v` — acceptance and focused guards pass after observed red.
- `python3 -m unittest discover -s platform/deployment/tests -v` — existing owner regression results recorded, investigate failures without changing unexplained expectations.
- Scoped `git diff --check` and synthetic CLI run — no whitespace errors; explicit unqualified runtime result.
