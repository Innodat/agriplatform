Read `
<embedded-file path="/home/ck/repos/innodat/agriplatform/_bmad/render/bmad-build/agriplatform-cc7e2d5786a0/a242468543ca715328cb/review-prompts/edge-case-hunter.md">
# Edge Case Hunter Review

**Goal:** You are a pure path tracer. Never comment on whether code is good or bad; only list missing handling.
When a diff is provided, scan only the diff hunks and list boundaries that are directly reachable from the changed lines and lack an explicit guard in the diff.
When no diff is provided (full file or function), treat the entire provided content as the scope.
Ignore the rest of the codebase unless the provided content explicitly references external functions.
A brief secondary deletion check runs as Step 4 when the diff removes code.
A claims check runs as Step 5.

**Inputs:**
- **content** — Content to review, or a path to read it from: diff, full file, or function
- **also_consider** (optional) — Areas to keep in mind during review alongside normal edge-case analysis
- **claims_file** — Path to the spec this change was built from. Do NOT read it before Step 5: the path tracing in Steps 2–3 must finish before the claims are seen.

**MANDATORY: Execute steps in the Execution section IN EXACT ORDER. DO NOT skip steps or change the sequence. When a halt condition triggers, follow its specific instruction exactly. Each action within a step is a REQUIRED action to complete that step.**

**Your method is exhaustive path enumeration — mechanically walk every branch, not hunt by intuition. Report ONLY paths and conditions that lack handling — discard handled ones silently. Do NOT editorialize or add filler. Do not assign severity labels, rankings, or priority levels.**


## EXECUTION

### Step 1: Receive Content

- Take the content to review from the parent message that launched you — inline, or by reading the file it points to (never from this instruction file)
- If no content is supplied, or it is empty, unreadable, or cannot be decoded as text, return `[{"location":"N/A","trigger_condition":"Input empty or undecodable","guard_snippet":"Provide valid content to review","potential_consequence":"Review skipped — no analysis performed"}]` and stop
- Identify content type (diff, full file, or function) to determine scope rules

### Step 2: Exhaustive Path Analysis

**Walk every branching path and boundary condition within scope — report only unhandled ones.**

- If `also_consider` input was provided, incorporate those areas into the analysis
- Walk all branching paths: control flow (conditionals, loops, error handlers, early returns) and domain boundaries (where values, states, or conditions transition). Derive the relevant edge classes from the content itself — don't rely on a fixed checklist. Examples: missing else/default, unguarded inputs, off-by-one loops, arithmetic overflow, implicit type coercion, race conditions, timeout gaps
- Consider implicit branches: the diff special-cases or changes the handling of one or more members of a fixed set of values — enums, status codes, sentinels, type tags, flags, value ranges. The rest of the set is implicit branches (e.g. the diff changes the `RED` and `YELLOW` cases of a `RED`/`YELLOW`/`GREEN` enum; `GREEN` is the implicit branch)
- Consider handle lifetime: when the changed code re-checks, re-fetches, or re-validates something it already held — a handle, index, id, pointer — the re-check exists because an intervening call can invalidate it. Identify that call, what it does to the thing held, and what the changed code silently skips when the re-check fails
- For each call site the diff adds or changes — in test files as well as production code — read the callee's declaration and check the call against it: argument count, order, types, and defaults. Report any mismatch
- For each path: determine whether the content handles it
- Collect only the unhandled paths as findings — discard handled ones silently

### Step 3: Validate Completeness

- Revisit every edge class from Step 2 — e.g., missing else/default, null/empty inputs, off-by-one loops, arithmetic overflow, implicit type coercion, race conditions, timeout gaps
- Add any newly found unhandled paths to findings; discard confirmed-handled ones

### Step 4: Deletion Check

If the diff removed or replaced meaningful code (ignore pure renames and whitespace): load `references/deletion-check.md` and follow it.

### Step 5: Claims Check

Load `references/claims-check.md` and follow it.

### Step 6: Present Findings

Output all findings as a single JSON array following the Output Format specification exactly.


## OUTPUT FORMAT

Return ONLY a valid JSON array of objects. Each edge-case finding contains exactly these four fields:

```json
[{
  "location": "file:start-end (or file:line when single line, or file:hunk when exact line unavailable)",
  "trigger_condition": "one-line description (max 15 words)",
  "guard_snippet": "minimal code sketch that closes the gap (single-line escaped string, no raw newlines or unescaped quotes)",
  "potential_consequence": "what could actually go wrong (max 15 words)"
}]
```

No extra text, no explanations, no markdown wrapping. An empty array `[]` is valid when nothing is found. Deletion findings from Step 4 and claim findings from Step 5, if any, go in the same array with the extra fields defined in `references/deletion-check.md` and `references/claims-check.md`.


## HALT CONDITIONS

- If no content is supplied, or it is empty, unreadable, or cannot be decoded as text, return `[{"location":"N/A","trigger_condition":"Input empty or undecodable","guard_snippet":"Provide valid content to review","potential_consequence":"Review skipped — no analysis performed"}]` and stop
<reference path="references/deletion-check.md">
# Deletion Check

Secondary pass for the Edge Case Hunter — runs only when the diff removed meaningful code. Subordinate to the edge-case pass; findings are usually few or none.

For each chunk of removed or replaced code (ignore pure renames and whitespace), ask: did it carry behavior or a contract that the change neither re-established nor intentionally retired? Add a finding for any resulting regression, orphaned reference, or newly-dead code. Skip anything already covered by your edge-case findings.

Append each finding to the same JSON array as the edge-case findings, with the four standard fields plus:

- `kind`: `"deletion"`
- `confidence`: `"high"`, `"medium"`, or `"low"` — these are inferences; rate them

For a deletion finding the standard fields read as: `location` = the removed item; `trigger_condition` = the behavior or contract it enforced; `guard_snippet` = where or how to re-establish it; `potential_consequence` = the regression or orphan.

Add nothing if nothing qualifies.
</reference>
<reference path="references/claims-check.md">
# Claims Check

Final pass for the Edge Case Hunter. Read the claims file named in the message that launched you now, for the first time; the path tracing is finished and the claims cannot steer it retroactively.

It is the spec the change was built from. Read only its `## Intent` and `## Tasks & Acceptance` sections — the claims live there; ignore the rest of the file. The spec is the change's own account of itself: testimony, not evidence — a claim repeated in a code comment is still the same claim, not confirmation. Extract each checkable claim — what the change does, what it preserves, ordering, arithmetic, and parity with existing code ("exactly as X does") — then try to falsify each one against the code you have already traced. Where your trace is not enough to decide, read the code that decides it: the compared-to function, the actual callee, the state the claim assumes.

Append one finding per falsified claim to the same JSON array, with the four standard fields plus:

- `kind`: `"claim"`
- `confidence`: `"high"`, `"medium"`, or `"low"`

For a claim finding the standard fields read as: `location` = where the code contradicts the claim; `trigger_condition` = the claim, quoted or tightly paraphrased; `guard_snippet` = what the code actually does; `potential_consequence` = what goes wrong for someone who believed the claim.

Verified claims produce nothing. Add nothing if nothing is falsified.
</reference>

## CONTENT SOURCE

"Review content:" in the message that launched you gives the content itself or a path to read it from. Read the file when it is a path; either way that is the content under review, and this instruction file never is.

</embedded-file>
` completely and follow it as your review instructions.

claims_file (leave unread until your instructions call for it): 
<embedded-file path="/home/ck/repos/innodat/agriplatform/_bmad-output/implementation-artifacts/spec-scribeswell-controller-history-profile.md">
---
title: 'Controller history native replay qualification'
type: 'feature'
created: '2026-10-23'
status: 'in-review'
baseline_commit: 'f3cf330322ca2beb8259f8ba5aab4f76c8dbf69c'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/_bmad-output/specs/spec-scribeswell-studies/corpus-publication.md'
---

<frozen-after-approval reason="bounded continuation authorized by user next and existing implement-and-verify instruction">

## Intent

**Problem:** Prepared replay rejects legitimate controller history, preventing safe native release rehearsal after commands execute.

**Approach:** Explicit controller-history-v1 validates coherent current/historical state and unchanged least privileges at exact0003, preserving existing profiles and commit-only success evidence.

## Boundaries & Constraints

**Always:** Implement canonical Controller-history replay contract (decision168): same closed current custody, exact three ACL cells and full restricted authority/catalogue; either enforcement boolean; disabled mappings preserved. Validate empty or complete singleton expected-source history, contiguous generations, unique originating begin/recover and optional seals, predecessor/input/request/receipt coherence, original attribution and finite epoch times. Historical executors remain historical; positive revision evidence cannot exceed current corresponding revisions. Require empty committed bindings. Cap10000 attempts/20000 outcomes; exceeding bounds rejects without cleanup. Acquire migration then controller(31003,1) advisory lock before seven-table SHARE locks. Caller-owned writableRC, safe catalogue path, statement5s/lock2s ceilings retaining shorter caller bounds. Existing profile selection/transaction evidence rules apply.

**Never:** Modify applied revisions/references/source/importer, provision actors/roles/grants, enable/disable enforcement, repair/delete history, verify Identity from local custody, add CLI/env/host selectors or infer profile from drift. No Access/KDG/Leave/factory, browser/signup/UX, publication or production change. No external wait/source scan under locks. Per-statement bounds are not total transport/COMMIT deadline.

## I/O & Edge-Case Matrix

| Scenario | Input/state | Expected | Failure |
|---|---|---|---|
| Native history replay | explicit profile, matching custody and exact0003, coherent empty/updating/closed/recovered history | unchanged direct/native success after commit | fixed safe code |
| Suspension/rotation | enforcementfalse/disabled mappings, old actors/revisions | preserve original records; current custody still exact | no authority restoration |
| Corrupt history | missing/gapped/orphan/cross-source attempts, invalid command/result/input/attribution/revision, binding debris | reject | no repair |
| Unsafe target/input | earlier ledger, drift/extra privilege, invalid profile/custody/transaction | reject | no adoption or partial evidence |
| Concurrent operations | transition-first or validation-first; bound importer | complete/serialize or bounded safe failure | no deadlock, leaked binding or mutation |
| Fault/cap | postcheck/commit fault, reused Config, count above cap | rollback/no success evidence | no partial validation |

</frozen-after-approval>

## Code Map

- `apps/scribeswell/migrations/prepared_controller.py`: reusable custody/catalogue/operator checks; split local custody from false/empty state only after105-case characterization. Preserve old public behavior/errors.
- `migrations/baseline.py`: common authority/ledger prefix and lazy prepared wrapper; add lazy history entry.
- `migrations/env.py`: explicit Config profile selector; add controller-history-v1 with existing scribeswell_prepared_actor. Clear success before all invocations; publish only after commit.
- `migrations/versions/0003_corpus_controller.py`: immutable native validator/transition semantics and attributed outcomes. Read; never edit. `0002` epoch lacks finite timestamp CHECK, so history must explicitly inspect it.
- `tests/test_corpus_publication.py`: enabled/controller_database, body/operator/execute; actual restricted transitions and fixture cleanup. `test_prepared_controller_profile.py`: staged seeded business/sequence fixture, CUSTODY/state/native helpers and existing105 regressions.
- New `migrations/controller_history.py`: bounded set-based consistency checks using exact native grammar after pinned catalogue validation. No runtime service/owner imports.

## Tasks & Acceptance

**Execution:**
- [x] `apps/scribeswell/tests/test_controller_history_profile.py` — observe acceptance red, then cover every matrix row with actual disposable PostgreSQL.
- [x] `apps/scribeswell/migrations/controller_history.py`, `prepared_controller.py`, `baseline.py` — reuse strict prefix; validate canonical complete history without loading unbounded payloads.
- [x] `apps/scribeswell/migrations/env.py` — add explicit native-only selection, preserving dormant/prepared rejection/evidence.
- [x] `apps/scribeswell/docs/CONTROLLER_HISTORY_PROFILE.md`, `MIGRATIONS.md`, `CORPUS_CONTROLLER.md`, `PREPARED_CONTROLLER_PROFILE.md` — exact limits, native usage and remaining production gates; no readiness overclaim.

**Acceptance Criteria:**
- Given real begin/seal/recover chains and current custody, when direct and native head replay run, then every row, sequence, catalogue and ledger is preserved and original outcome lookup behavior unchanged.
- Given corrupt/unsafe/over-cap state or meaningful postcheck/commit failure, when validation runs, then safe rejection/rollback occurs with no profile success evidence or target repair.
- Given competing transitions/configuration/writers, when either operation holds its protected context first, then actual ordering remains bounded and completed writers clean bindings without false success.

## Implementation Notes

Root owns canonical/delivery evidence, fixture and local commit; agent edits listed app files only. Prior dirty files must remain untouched. No intent gaps, production mutation or irreversible action; footprint is one native profile/helper/test/doc set. Existing user authorization covers this concrete bounded continuation without a repeated approval gate. No scaffold/shared-UI/agent-context/ADR changes; app docs and canonical handoff only. Do not overfit SQL exceptions into data diagnostics.

Use `/tmp/scribeswell-studies-tests-py312/bin/python`; root supplies exact fixture URL in this section before dispatch. Sequential database suites; actual red and prepared105 characterization before helper changes. Root independently verifies final suite after three-lens review. Keep tests meaningful: seed real corpus rows/sequences, assert complete snapshots, isolate negative corruption and restore trigger catalogue before invoking checker. Never alter expected results to dismiss unexplained failure.

## Spec Change Log

## Review Triage Log

## Verification

Run smallest history acceptance red, prepared105 characterization, focused history+prepared, affected migration/controller/operator suites, then full app suite. Record exact commands/results/no skipped acceptance and matrix traceability here. Root runs platform deployment regression and composition check-only; verify eight protected source/importer/revision/reference hashes. Native-only qualification does not close host/live custody/importer/publication/reader or private Studies gates. No image/browser/provider/production test claim.

Fixture: `SCRIBESWELL_TEST_DATABASE_URL=postgresql://postgres:fixture@127.0.0.1:32775/postgres`, owned temporary PG17 container65888e044739ca7a0b8d9f171ba2383ef43fc6d3a063aa977423ac4bcca1aa21. Root owns stop/removal. Agent has exclusive sequential database use until returning.

Implementation dispatch attempted with the prescribed no-history prompt, but agent
creation failed at the host thread limit. Per step03 unavailable-agent fallback,
root implements directly from this spec. Read-only investigator completed first.
No code changes precede prepared105 characterization and actual history red.

Actual prepared characterization105 passed22.76s. First history collection failed
because the new test imported baseline before the existing fixture module sets its
module path; corrected test import order before the valid acceptance red. The
actual history run then produced1 passed/1 failed2.81s: both previous profiles
correctly reject real chain without mutation, new entry is absent AttributeError.
Only afterward were shared custody/prefix helpers extracted and history code added.

Initial green107 focused cases23.33s after the missing-entry red; expanded history
first produced57 passed/3 harness failures15.50s (two snapshots attempted Python
datetime decoding of PostgreSQL infinity; empty-ledger expectation confused invalid
with absent ledger). Corrected snapshots preserve every field as server JSON text;
empty-ledger rejection retains its existing safe ledger_invalid code. Then history65
passed21.76s with real concurrency and fault cases. Expanded focused186 passed60.43s.

Actual fixed10000-attempt/20000-outcome fixture exposed a real statement-timeout
performance defect: initial capacity1 failed/four cardinality cases passed11.91s.
Safe diagnostic probe confirmed SQLSTATE57014 first in the preaggregation query,
then repeated full-payload history joins. Query-only corrections retain statement5s/
lock2s: count per-attempt events before coverage comparison; project event metadata
once and use lag/lead/first_value rather than self-joining full payloads. No target
ANALYZE, index, schema, timeout or contract change. Full-capacity direct plus native
pre/post now passed1 case7.79s total; each individual SQL remained within its original
ceiling. The capacity fixture is synthetic coherent data at the literal bound,
separate from small actual native begin/seal/recover fixtures. Revised focused/full
regression still required after these corrections.

Root platform command `/tmp/scribeswell-studies-tests-py312/bin/python -m pytest platform/deployment/tests/test_release.py platform/deployment/tests/test_host.py platform/deployment/tests/test_migrate_adapter.py platform/deployment/tests/test_target_contract.py -q`
passed25 tests/42 subtests2.75s. Composition `python3 tools/py/run_compose_supabase.py --check-only` passed without writes.

Final pre-review focused command:
`SCRIBESWELL_TEST_DATABASE_URL=postgresql://postgres:fixture@127.0.0.1:32775/postgres /tmp/scribeswell-studies-tests-py312/bin/python -m pytest apps/scribeswell/tests/test_controller_history_profile.py apps/scribeswell/tests/test_prepared_controller_profile.py -q`
passed187/no skips61.22s (82 history +105 retained prepared). Root read the entire
scoped60005-byte nine-app-file diff from baseline; unrelated changes excluded.

Matrix audit: Native replay → test_history_replay_preserves_actual_chain and six
test_supported_lifecycle_states; suspension/rotation → test_suspension_and_original_lookup_preserved
and test_historical_executor_rotation_is_not_rebound_authority; corruption →
test_corrupt_history_rejected_without_mutation, closed-current seal, typed result/
all input fields, cardinality/gap and binding-debris cases; target/transaction →
closed selection, strict target, invalid/earlier ledger and five transaction cases
plus retained105 helper cases; concurrency → actual transition-first/validation-first,
bound writer cleanup and configuration writer-first cases; fault/cap → two native
real pending-row rollback/commit faults, scaled cap boundary, literal fixed-capacity
positive10000/20000 and literal10001/20001 denials. All covering tests ran/passed
in187 output; no skipped acceptance. Three acceptance criteria satisfied by these
real database cases. Full broader regression now running before completion.


Final pre-review broader command:
`SCRIBESWELL_TEST_DATABASE_URL=postgresql://postgres:fixture@127.0.0.1:32775/postgres /tmp/scribeswell-studies-tests-py312/bin/python -m pytest apps/scribeswell/tests -q`
passed885/no skips261.13s, one existing Starlette/httpx deprecation only. Includes
82 new history plus803 retained app cases, including actual migration/controller/
operator/reader/importer/auditor suites. Focused187 passed61.22s. All code/test hashes
remained unchanged during full verification. App/delivery Markdown links/whitespace
and protected8 hashes pass; composition and platform25/42 passed as recorded.

## Independent review handoff — blocked by host agent capacity

No independent review has run. Fresh context-free blind, edge and verification
launches each failed with `agent thread limit reached`. Existing agents have prior
context and cannot substitute for the required fresh reviews. Step04 requires
standalone inline review prompts then HALT; this is the mandatory fallback.
The delivery remains in-review, not done, and no commit/push/deploy is made.
Run these in separate fresh sessions and return their findings for individual
triage, fixes, focused/full re-verification as appropriate, then scoped local commit:

- [Blind hunter prompt](review-scribeswell-controller-history-blind-prompt.md)
- [Edge-case prompt](review-scribeswell-controller-history-edge-prompt.md)
- [Verification-gap prompt](review-scribeswell-controller-history-verification-prompt.md)

Exact proposed commit scope is this delivery record plus nine app files in the
scoped diff. The three fallback prompt files are review handoff artifacts; decide
their retention after review. Preserve pre-existing untracked canonical specs and
all unrelated dirty files. Baseline remains the frontmatter full commit. No request
to reauthorize implementation is needed; missing input is independent findings.

</embedded-file>


Review content: the unified diff at `
<embedded-file path="/tmp/scribeswell-controller-history-review.diff">
diff --git a/apps/scribeswell/docs/CORPUS_CONTROLLER.md b/apps/scribeswell/docs/CORPUS_CONTROLLER.md
index e718f92..dbd526f 100644
--- a/apps/scribeswell/docs/CORPUS_CONTROLLER.md
+++ b/apps/scribeswell/docs/CORPUS_CONTROLLER.md
@@ -99,8 +99,10 @@ references and adds a separately generated `0003` reference. Default and host re
 [prepared-controller profile](PREPARED_CONTROLLER_PROFILE.md) additionally checks a
 prepared operator while enforcement stays false and history empty, matching local
 custody without claiming Identity verification. It changes no grants or state.
-Enabling enforcement or recording history remains outside either replay profile;
-this is not active-state release qualification. Real actor/caller preparation,
+The separate [controller-history native profile](CONTROLLER_HISTORY_PROFILE.md)
+validates coherent active/paused history under the same current-custody and privilege
+gates, preserving original outcomes. Operational host release integration and live
+preparation remain gates. Real actor/caller preparation,
 least-privilege operational release profile, target adoption and writer/importer
 transition remain gates. The [outer supervisor](CORPUS_OPERATOR.md) is fixture-qualified;
 its existence does not prepare a live caller or qualify an active release. Closed
diff --git a/apps/scribeswell/docs/MIGRATIONS.md b/apps/scribeswell/docs/MIGRATIONS.md
index a84ad41..835aadc 100644
--- a/apps/scribeswell/docs/MIGRATIONS.md
+++ b/apps/scribeswell/docs/MIGRATIONS.md
@@ -91,7 +91,18 @@ and matches independently supplied custody against protected local records. It d
 not verify Identity, provision callers, adopt earlier revisions or enable enforcement.
 The host adapter and ordinary CLI remain dormant-only and reject prepared targets;
 there is no ambient environment selector. Native profile evidence is published only
-after both checks and commit. Active/history release support remains a later gate.
+after both checks and commit. The separate history-native profile below extends
+local rehearsal; operational host release support remains a later gate.
+
+## Controller-history native replay
+
+The explicit [controller-history profile](CONTROLLER_HISTORY_PROFILE.md) additionally
+validates empty or coherent committed history at exact0003, including paused states
+and historical executor changes. It preserves the prepared profile's exact custody,
+catalogue and privilege gates. Native Config selection remains deliberate; the
+ordinary CLI/host stays dormant-only. This qualification changes no enforcement,
+actor/grant, importer or publication state. Live custody, operational host integration
+and coordinated production transition remain gates.
 
 ## Failure and recovery
 
@@ -124,6 +135,7 @@ a uniquely named database, and removes only its own database and roles. Run
 database suites sequentially against that cluster.
 
 ```sh
+python -m pytest apps/scribeswell/tests/test_controller_history_profile.py -q
 python -m pytest apps/scribeswell/tests/test_prepared_controller_profile.py -q
 python -m pytest apps/scribeswell/tests/test_owned_migrations.py -q
 python -m pytest apps/scribeswell/tests -q
diff --git a/apps/scribeswell/docs/PREPARED_CONTROLLER_PROFILE.md b/apps/scribeswell/docs/PREPARED_CONTROLLER_PROFILE.md
index 7ebd9f0..105bf8f 100644
--- a/apps/scribeswell/docs/PREPARED_CONTROLLER_PROFILE.md
+++ b/apps/scribeswell/docs/PREPARED_CONTROLLER_PROFILE.md
@@ -4,8 +4,9 @@
 for controlled native rehearsal. It performs no caller preparation, actor registration,
 grant repair, enforcement activation, scripture import or state cleanup. The existing
 host adapter and command line remain strict dormant-only; ambient environment hints
-cannot select this profile. An active enforcement/history release profile and host
-integration remain separate gates.
+cannot select this profile. The separate [controller-history native profile](CONTROLLER_HISTORY_PROFILE.md)
+qualifies coherent history without changing this profile. Operational host integration
+and live preparation remain separate gates.
 
 Use `baseline.preflight_prepared(connection, expected_actor)` on an actual restricted
 migrator connection inside a caller-owned writable `READ COMMITTED` transaction.
diff --git a/apps/scribeswell/migrations/baseline.py b/apps/scribeswell/migrations/baseline.py
index d5e3dc5..8122875 100644
--- a/apps/scribeswell/migrations/baseline.py
+++ b/apps/scribeswell/migrations/baseline.py
@@ -112,3 +112,9 @@ def preflight_prepared(connection, expected_actor):
     """Validate explicit prepared custody without preparing or activating anything."""
     from prepared_controller import preflight_prepared as validate
     return validate(connection, expected_actor)
+
+
+def preflight_controller_history(connection, expected_actor):
+    """Validate explicit committed controller history; never activate or repair."""
+    from controller_history import preflight_controller_history as validate
+    return validate(connection, expected_actor)
diff --git a/apps/scribeswell/migrations/env.py b/apps/scribeswell/migrations/env.py
index 036d19f..75df9de 100644
--- a/apps/scribeswell/migrations/env.py
+++ b/apps/scribeswell/migrations/env.py
@@ -2,7 +2,7 @@
 import os
 from alembic import context
 from sqlalchemy import create_engine, pool
-from baseline import BaselineError, preflight, preflight_prepared, ledger
+from baseline import BaselineError, preflight, preflight_prepared, preflight_controller_history, ledger
 config = context.config
 config.attributes.pop('scribeswell_validated_profile',None)
 if context.is_offline_mode():
@@ -10,15 +10,16 @@ if context.is_offline_mode():
 engine = None
 try:
     profile = config.attributes.get('scribeswell_validation_profile','dormant')
-    if profile not in ('dormant','prepared-controller-v1'):
+    if profile not in ('dormant','prepared-controller-v1','controller-history-v1'):
         raise BaselineError('scribeswell_validation_profile_invalid')
     supplied = 'scribeswell_prepared_actor' in config.attributes
-    if (profile == 'dormant' and supplied) or (profile == 'prepared-controller-v1' and not supplied):
+    if (profile == 'dormant' and supplied) or (profile != 'dormant' and not supplied):
         raise BaselineError('scribeswell_validation_profile_invalid')
-    if profile == 'prepared-controller-v1':
+    if profile != 'dormant':
         from prepared_controller import custody
         expected_actor = custody(config.attributes['scribeswell_prepared_actor'])
-        validate = lambda connection: preflight_prepared(connection,expected_actor)
+        checker = preflight_prepared if profile == 'prepared-controller-v1' else preflight_controller_history
+        validate = lambda connection: checker(connection,expected_actor)
     else:
         validate = preflight
     command = getattr(getattr(config, 'cmd_opts', None), 'cmd', None)
diff --git a/apps/scribeswell/migrations/prepared_controller.py b/apps/scribeswell/migrations/prepared_controller.py
index fe1b38a..bd85648 100644
--- a/apps/scribeswell/migrations/prepared_controller.py
+++ b/apps/scribeswell/migrations/prepared_controller.py
@@ -119,7 +119,7 @@ def operator(connection):
         deny('operator_authority')
 
 
-def local_state(connection, expected):
+def custody_state(connection, expected):
     principal = connection.exec_driver_sql("""SELECT database_login,executor_actor_id::text,actor_kind,actor_key,preparation_evidence_ref,
         revision>0 AND created_by_actor_id<>'00000000-0000-0000-0000-000000000000'::uuid
         AND updated_by_actor_id<>'00000000-0000-0000-0000-000000000000'::uuid AND isfinite(created_at) AND isfinite(updated_at)
@@ -133,6 +133,10 @@ def local_state(connection, expected):
         FROM scribeswell.corpus_operator_authority ORDER BY command LIMIT 4""").fetchall()
     if [tuple(row) for row in authority] != [(OPERATOR,expected['source_id'],'corpus.'+command,True) for command in ('begin','recover','seal')]:
         deny('custody_mismatch')
+
+
+def local_state(connection, expected):
+    custody_state(connection, expected)
     if connection.exec_driver_sql('SELECT singleton,enforcement FROM scribeswell.corpus_fence_control').fetchall() != [(True,False)]:
         deny('dormant_state_required')
     for table in TABLES[3:]:
@@ -140,7 +144,7 @@ def local_state(connection, expected):
             deny('dormant_state_required')
 
 
-def _preflight_prepared(connection, expected_actor):
+def checked_prepared(connection, expected_actor, *, controller_history=False):
     expected = custody(expected_actor)
     if not connection.in_transaction() or connection.connection.dbapi_connection.autocommit or connection.get_isolation_level() != 'READ COMMITTED' or connection.exec_driver_sql('SHOW transaction_read_only').scalar() != 'off':
         deny('transaction_required')
@@ -156,11 +160,18 @@ def _preflight_prepared(connection, expected_actor):
     state = _checked_authority_ledger(connection)
     if state != REVISION:
         deny('revision_required')
+    if controller_history:
+        connection.exec_driver_sql('SELECT pg_catalog.pg_advisory_xact_lock(31003,1)')
     for table in TABLES:
         connection.exec_driver_sql('LOCK TABLE scribeswell.'+table+' IN SHARE MODE')
     catalogue(connection,pinned)
     operator(connection)
-    local_state(connection,expected)
+    return state, expected
+
+
+def _preflight_prepared(connection, expected_actor):
+    state, expected = checked_prepared(connection, expected_actor)
+    local_state(connection, expected)
     return state
 
 
diff --git a/apps/scribeswell/migrations/controller_history.py b/apps/scribeswell/migrations/controller_history.py
new file mode 100644
index 0000000..3752318
--- /dev/null
+++ b/apps/scribeswell/migrations/controller_history.py
@@ -0,0 +1,131 @@
+"""Closed native replay checks for committed controller state, not source publication."""
+from baseline import BaselineError
+from prepared_controller import checked_prepared, custody_state
+
+MAX_ATTEMPTS = 10000
+MAX_OUTCOMES = 20000
+
+
+def deny(code='invalid'):
+    raise BaselineError('scribeswell_history_' + code)
+
+
+def invalid(connection, query, parameters=()):
+    if connection.exec_driver_sql(query, parameters).scalar():
+        deny()
+
+
+def history(connection, expected):
+    custody_state(connection, expected)
+    if connection.exec_driver_sql('SELECT singleton FROM scribeswell.corpus_fence_control LIMIT 2').fetchall() != [(True,)]:
+        deny()
+    if connection.exec_driver_sql('SELECT 1 FROM scribeswell.corpus_write_binding LIMIT 1').first():
+        deny()
+    # Probe only cap+1 rows and retain no history payload in the client.
+    for table, maximum in (('corpus_attempt', MAX_ATTEMPTS), ('corpus_command_outcome', MAX_OUTCOMES)):
+        count = connection.exec_driver_sql('SELECT count(*) FROM (SELECT 1 FROM scribeswell.' + table + ' LIMIT %s) bounded', (maximum + 1,)).scalar()
+        if count > maximum:
+            deny('limit_exceeded')
+    epoch = connection.exec_driver_sql('SELECT generation FROM scribeswell.corpus_epoch LIMIT 2').fetchall()
+    if not epoch:
+        invalid(connection, 'SELECT EXISTS (SELECT 1 FROM scribeswell.corpus_attempt) OR EXISTS (SELECT 1 FROM scribeswell.corpus_command_outcome)')
+        return
+    if len(epoch) != 1:
+        deny()
+    invalid(connection, """SELECT EXISTS (SELECT 1 FROM scribeswell.corpus_epoch e WHERE
+        e.source_id<>%s OR NOT isfinite(e.created_at) OR NOT isfinite(e.updated_at)
+        OR e.generation<>(SELECT count(*) FROM scribeswell.corpus_attempt)
+        OR e.generation<>(SELECT max(generation) FROM scribeswell.corpus_attempt))
+        OR EXISTS (SELECT 1 FROM scribeswell.corpus_attempt a WHERE a.source_id<>%s)
+        OR NOT EXISTS (SELECT 1 FROM scribeswell.corpus_attempt WHERE generation=1)""", (expected['source_id'], expected['source_id']))
+    # Native input validation is owner-only, fixed and pinned before invocation.
+    # Aggregate forces evaluation for every bounded row without returning payloads.
+    connection.exec_driver_sql('SELECT count(scribeswell.validate_corpus_command(semantic_command)) FROM scribeswell.corpus_command_outcome').scalar()
+    invalid(connection, """SELECT EXISTS (
+      SELECT 1 FROM scribeswell.corpus_command_outcome o
+      JOIN scribeswell.corpus_attempt a USING (attempt_id,source_id,generation)
+      JOIN scribeswell.corpus_operator_principal p USING (database_login)
+      LEFT JOIN scribeswell.corpus_operator_authority u ON u.database_login=o.database_login
+        AND u.source_id=o.source_id AND u.command=o.semantic_command->>'command'
+      WHERE o.database_login<>'scribeswell_corpus_operator' OR o.source_id<>%s
+       OR o.semantic_command->>'operation_id' IS DISTINCT FROM o.operation_id::text
+       OR o.semantic_command#>>'{scope,source_id}' IS DISTINCT FROM o.source_id
+       OR o.semantic_command#>'{payload,input}' IS DISTINCT FROM jsonb_build_object(
+          'source_sha256',a.input_sha256,'catalogue_version',a.catalogue_version,
+          'versification_id',a.versification_id,'tokenization_version',a.tokenization_version)
+       OR u.command IS NULL OR o.principal_revision>p.revision OR o.authority_revision>u.revision
+       OR (o.principal_revision=p.revision AND o.executor_actor_id<>p.executor_actor_id)
+       OR o.result IS DISTINCT FROM jsonb_build_object('version',1,'operation_id',o.operation_id::text,
+          'command',o.semantic_command->>'command','source_id',o.source_id,
+          'executor_actor_id',o.executor_actor_id::text,'attempt_id',o.attempt_id::text,
+          'generation',o.generation::text,'state',CASE WHEN o.semantic_command->>'command'='corpus.seal' THEN 'closed' ELSE 'updating' END))""", (expected['source_id'],))
+    # Aggregate outcomes before coverage comparison: the pinned FK establishes
+    # their owning attempt. Joining fresh unanalyzed tables first can force a
+    # quadratic nested-loop plan under EXISTS, even for valid bounded history.
+    invalid(connection, """WITH counts AS MATERIALIZED (
+      SELECT attempt_id,
+        count(*) FILTER (WHERE semantic_command->>'command'<>'corpus.seal') AS origins,
+        count(*) FILTER (WHERE semantic_command->>'command'='corpus.seal') AS seals
+      FROM scribeswell.corpus_command_outcome GROUP BY attempt_id)
+      SELECT EXISTS (SELECT 1 FROM counts WHERE origins<>1 OR seals>1)
+        OR (SELECT count(*) FROM counts)<>(SELECT count(*) FROM scribeswell.corpus_attempt)""")
+    # Project each event once, then derive predecessor/successor facts in one
+    # window pass. Avoid self-joining materialized full request/receipt payloads.
+    invalid(connection, """WITH events AS MATERIALIZED (
+      SELECT attempt_id,source_id,generation,
+        max(executor_actor_id::text) FILTER (WHERE semantic_command->>'command'<>'corpus.seal') AS origin_actor,
+        max(created_at) FILTER (WHERE semantic_command->>'command'<>'corpus.seal') AS origin_at,
+        max(semantic_command->>'command') FILTER (WHERE semantic_command->>'command'<>'corpus.seal') AS command,
+        max(semantic_command#>>'{payload,expected_generation}') FILTER (WHERE semantic_command->>'command'<>'corpus.seal') AS previous_generation,
+        max(semantic_command#>>'{payload,expected_attempt_id}') FILTER (WHERE semantic_command->>'command'<>'corpus.seal') AS previous_attempt,
+        max(executor_actor_id::text) FILTER (WHERE semantic_command->>'command'='corpus.seal') AS seal_actor,
+        max(created_at) FILTER (WHERE semantic_command->>'command'='corpus.seal') AS seal_at,
+        max(semantic_command#>>'{payload,expected_generation}') FILTER (WHERE semantic_command->>'command'='corpus.seal') AS seal_generation,
+        max(semantic_command#>>'{payload,expected_attempt_id}') FILTER (WHERE semantic_command->>'command'='corpus.seal') AS seal_attempt
+      FROM scribeswell.corpus_command_outcome GROUP BY attempt_id,source_id,generation),
+    ordered AS MATERIALIZED (
+      SELECT *,lag(attempt_id::text) OVER w AS predecessor,
+        lead(origin_actor) OVER w AS following_actor,lead(origin_at) OVER w AS following_at,
+        first_value(origin_actor) OVER w AS first_actor,first_value(origin_at) OVER w AS first_at
+      FROM events WINDOW w AS (ORDER BY generation)),
+    epoch AS MATERIALIZED (SELECT * FROM scribeswell.corpus_epoch LIMIT 1)
+    SELECT (SELECT count(*) FROM scribeswell.corpus_attempt a
+      JOIN ordered b USING (attempt_id,source_id,generation) CROSS JOIN epoch e
+      WHERE (a.generation=1 AND b.command<>'corpus.begin')
+       OR (a.generation>1 AND (b.command<>'corpus.recover'
+          OR b.previous_generation IS DISTINCT FROM (a.generation-1)::text
+          OR b.previous_attempt IS DISTINCT FROM b.predecessor))
+       OR (b.seal_actor IS NOT NULL AND (b.seal_generation IS DISTINCT FROM a.generation::text
+          OR b.seal_attempt IS DISTINCT FROM a.attempt_id::text))
+       OR a.created_by_actor_id::text<>b.origin_actor OR a.created_at<>b.origin_at
+       OR (a.generation<e.generation AND a.state<>'retired')
+       OR (a.generation=e.generation AND (
+          a.attempt_id<>e.attempt_id OR a.input_sha256<>e.input_sha256 OR a.state<>e.state
+          OR (a.state='closed') IS DISTINCT FROM (b.seal_actor IS NOT NULL)))
+       OR a.updated_by_actor_id::text IS DISTINCT FROM coalesce(b.following_actor,b.seal_actor,b.origin_actor)
+       OR a.updated_at IS DISTINCT FROM coalesce(b.following_at,b.seal_at,b.origin_at))>0
+    OR EXISTS (SELECT 1 FROM epoch e JOIN ordered b ON b.attempt_id=e.attempt_id
+      WHERE e.created_by_actor_id::text<>b.first_actor OR e.created_at<>b.first_at
+       OR e.updated_by_actor_id::text<>coalesce(b.seal_actor,b.origin_actor)
+       OR e.updated_at<>coalesce(b.seal_at,b.origin_at))""")
+    invalid(connection, """WITH ordered AS (
+      SELECT principal_revision,executor_actor_id,authority_revision,
+        lag(principal_revision) OVER w AS previous_revision,
+        lag(executor_actor_id) OVER w AS previous_actor,
+        lag(authority_revision) OVER (PARTITION BY semantic_command->>'command' ORDER BY generation) AS previous_authority
+      FROM scribeswell.corpus_command_outcome
+      WINDOW w AS (ORDER BY generation,CASE WHEN semantic_command->>'command'='corpus.seal' THEN 1 ELSE 0 END))
+      SELECT EXISTS (SELECT 1 FROM ordered WHERE principal_revision<previous_revision
+        OR (principal_revision=previous_revision AND executor_actor_id<>previous_actor)
+        OR authority_revision<previous_authority)""")
+
+
+def preflight_controller_history(connection, expected_actor):
+    try:
+        state, expected = checked_prepared(connection, expected_actor, controller_history=True)
+        history(connection, expected)
+        return state
+    except BaselineError:
+        raise
+    except Exception:
+        raise BaselineError('scribeswell_history_validation_failed') from None
diff --git a/apps/scribeswell/tests/test_controller_history_profile.py b/apps/scribeswell/tests/test_controller_history_profile.py
new file mode 100644
index 0000000..d2655b8
--- /dev/null
+++ b/apps/scribeswell/tests/test_controller_history_profile.py
@@ -0,0 +1,589 @@
+"""Native controller-history qualification on an exclusively owned disposable PG17."""
+import pytest
+from test_corpus_publication import controller_database, enabled, body, operator, execute
+from test_prepared_controller_profile import staged, CUSTODY, engine_for, native
+from test_owned_migrations import invoke
+import baseline
+
+PROFILE = 'controller-history-v1'
+
+
+def state(admin, url):
+    from catalogue import snapshot
+    from test_owned_migrations import business_state
+    engine = engine_for(url)
+    try:
+        with engine.begin() as connection:
+            catalogue = snapshot(connection, head=True)
+    finally:
+        engine.dispose()
+    # JSON text preserves even PostgreSQL infinity values without the driver's
+    # finite Python datetime conversion; all rows and fields remain compared.
+    records = {table: admin.execute('SELECT row_to_json(t)::text FROM scribeswell.' + table + ' t ORDER BY 1').fetchall()
+               for table in ('alembic_version', 'corpus_operator_principal', 'corpus_operator_authority',
+                             'corpus_fence_control', 'corpus_epoch', 'corpus_attempt',
+                             'corpus_command_outcome', 'corpus_write_binding')}
+    return catalogue, business_state(admin), records
+
+
+def direct(url, expected=CUSTODY):
+    engine = engine_for(url)
+    try:
+        with engine.begin() as connection:
+            return baseline.preflight_controller_history(connection, expected)
+    finally:
+        engine.dispose()
+
+
+def chain(staged):
+    admin, url = staged
+    admin.execute('UPDATE scribeswell.corpus_fence_control SET enforcement=true')
+    with operator(url) as connection:
+        first = body(); began = execute(connection, first)
+        seal = body('seal', began); closed = execute(connection, seal)
+        recovery = body('recover', closed); current = execute(connection, recovery)
+    return [(first, began), (seal, closed), (recovery, current)]
+
+
+def test_existing_profiles_reject_history_without_mutation(staged, monkeypatch):
+    admin, url = staged
+    chain(staged)
+    before = state(admin, url)
+    assert invoke(url).returncode != 0
+    with pytest.raises(baseline.BaselineError, match='dormant_state_required'):
+        native(url, monkeypatch, dict(scribeswell_validation_profile='prepared-controller-v1', scribeswell_prepared_actor=CUSTODY))
+    assert state(admin, url) == before
+
+
+def test_history_replay_preserves_actual_chain(staged, monkeypatch):
+    admin, url = staged
+    chain(staged)
+    before = state(admin, url)
+    assert direct(url) == baseline.REVISION
+    config = native(url, monkeypatch, dict(scribeswell_validation_profile=PROFILE, scribeswell_prepared_actor=CUSTODY))
+    assert config.attributes['scribeswell_validated_profile'] == PROFILE
+    assert config.attributes['scribeswell_before'] == config.attributes['scribeswell_after'] == baseline.REVISION
+    assert state(admin, url) == before
+
+
+@pytest.mark.parametrize('mode', ['empty', 'armed', 'updating', 'closed', 'recover_updating', 'recover_closed'])
+def test_supported_lifecycle_states(staged, monkeypatch, mode):
+    admin, url = staged
+    if mode != 'empty':
+        admin.execute('UPDATE scribeswell.corpus_fence_control SET enforcement=true')
+    if mode not in ('empty', 'armed'):
+        with operator(url) as connection:
+            receipt = execute(connection, body())
+            if mode in ('closed', 'recover_closed'):
+                receipt = execute(connection, body('seal', receipt))
+            if mode.startswith('recover'):
+                receipt = execute(connection, body('recover', receipt))
+    before = state(admin, url)
+    assert direct(url) == baseline.REVISION
+    config = native(url, monkeypatch, dict(scribeswell_validation_profile=PROFILE, scribeswell_prepared_actor=CUSTODY))
+    assert config.attributes['scribeswell_validated_profile'] == PROFILE
+    assert state(admin, url) == before
+
+
+def test_suspension_and_original_lookup_preserved(staged):
+    from corpus_publication import lookup_outcome, PublicationError
+    from test_corpus_publication_input import encode
+    admin, url = staged
+    commands = chain(staged)
+    admin.execute('UPDATE scribeswell.corpus_fence_control SET enforcement=false')
+    # Old receipt lookup is available with current authority even while paused.
+    with operator(url) as connection:
+        for request, receipt in commands:
+            assert lookup_outcome(connection, encode(request)) == receipt
+    admin.execute('UPDATE scribeswell.corpus_operator_principal SET enabled=false,revision=revision+1')
+    admin.execute('UPDATE scribeswell.corpus_operator_authority SET enabled=false,revision=revision+1')
+    before = state(admin, url)
+    assert direct(url) == baseline.REVISION
+    with operator(url) as connection:
+        with pytest.raises(PublicationError, match='access_denied'):
+            lookup_outcome(connection, encode(commands[0][0]))
+    assert state(admin, url) == before
+
+
+def test_historical_executor_rotation_is_not_rebound_authority(staged):
+    from corpus_publication import lookup_outcome, PublicationError
+    from test_corpus_publication_input import encode
+    admin, url = staged
+    commands = chain(staged)
+    replacement = '33333333-3333-4333-8333-333333333333'
+    admin.execute('UPDATE scribeswell.corpus_operator_principal SET executor_actor_id=%s,revision=revision+1,updated_by_actor_id=%s', (replacement, replacement))
+    expected = dict(CUSTODY, executor_actor_id=replacement)
+    with operator(url) as connection:
+        current = execute(connection, body('recover', commands[-1][1]))
+        assert current.executor_actor_id == replacement
+        with pytest.raises(PublicationError, match='conflict'):
+            lookup_outcome(connection, encode(commands[0][0]))
+    before = state(admin, url)
+    assert direct(url, expected) == baseline.REVISION
+    with pytest.raises(baseline.BaselineError, match='custody_mismatch'):
+        direct(url)
+    assert state(admin, url) == before
+
+
+def tamper(admin, query):
+    # Simulate owner-corrupted data, with the exact original trigger catalogue
+    # restored before validation; no structural drift hides the data predicate.
+    tables = ('corpus_attempt', 'corpus_command_outcome')
+    for table in tables:
+        admin.execute('ALTER TABLE scribeswell.' + table + ' DISABLE TRIGGER corpus_record_protection')
+    try:
+        admin.execute(query)
+    finally:
+        for table in tables:
+            admin.execute('ALTER TABLE scribeswell.' + table + ' ENABLE ALWAYS TRIGGER corpus_record_protection')
+
+
+@pytest.mark.parametrize('query', [
+    'DELETE FROM scribeswell.corpus_command_outcome WHERE generation=1 AND semantic_command->>\'command\'=\'corpus.begin\'',
+    'DELETE FROM scribeswell.corpus_epoch',
+    'UPDATE scribeswell.corpus_epoch SET generation=3',
+    "UPDATE scribeswell.corpus_epoch SET source_id='other'",
+    "UPDATE scribeswell.corpus_epoch SET attempt_id='44444444-4444-4444-8444-444444444444'",
+    "UPDATE scribeswell.corpus_epoch SET input_sha256=repeat('b',64)",
+    "UPDATE scribeswell.corpus_epoch SET state='closed'",
+    "UPDATE scribeswell.corpus_epoch SET created_at='infinity'",
+    "UPDATE scribeswell.corpus_epoch SET updated_at='-infinity'",
+    "UPDATE scribeswell.corpus_epoch SET created_by_actor_id='44444444-4444-4444-8444-444444444444'",
+    "UPDATE scribeswell.corpus_epoch SET updated_by_actor_id='44444444-4444-4444-8444-444444444444'",
+    "UPDATE scribeswell.corpus_epoch SET updated_at=updated_at+interval '1 second'",
+    "UPDATE scribeswell.corpus_attempt SET state='closed' WHERE generation=1",
+    "UPDATE scribeswell.corpus_attempt SET state='retired' WHERE generation=2",
+    "UPDATE scribeswell.corpus_attempt SET catalogue_version='other' WHERE generation=1",
+    "UPDATE scribeswell.corpus_attempt SET created_by_actor_id='44444444-4444-4444-8444-444444444444' WHERE generation=1",
+    "UPDATE scribeswell.corpus_attempt SET updated_by_actor_id='44444444-4444-4444-8444-444444444444' WHERE generation=1",
+    "UPDATE scribeswell.corpus_attempt SET created_at=created_at+interval '1 second' WHERE generation=1",
+    "UPDATE scribeswell.corpus_command_outcome SET semantic_command='{}'::jsonb WHERE generation=1",
+    "UPDATE scribeswell.corpus_command_outcome SET semantic_command=jsonb_set(semantic_command,'{operation_id}','\"44444444-4444-4444-8444-444444444444\"') WHERE generation=1",
+    "UPDATE scribeswell.corpus_command_outcome SET semantic_command=jsonb_set(semantic_command,'{scope,source_id}','\"other\"') WHERE generation=1",
+    "UPDATE scribeswell.corpus_command_outcome SET semantic_command=jsonb_set(semantic_command,'{payload,input,source_sha256}',to_jsonb(repeat('b',64))) WHERE generation=1",
+    "UPDATE scribeswell.corpus_command_outcome SET semantic_command=jsonb_set(semantic_command,'{payload,expected_generation}','\"7\"') WHERE generation=2",
+    "UPDATE scribeswell.corpus_command_outcome SET semantic_command=jsonb_set(semantic_command,'{payload,expected_attempt_id}','\"44444444-4444-4444-8444-444444444444\"') WHERE generation=2",
+    "UPDATE scribeswell.corpus_command_outcome SET result=result||'{\"extra\":true}'::jsonb WHERE generation=1",
+    "UPDATE scribeswell.corpus_command_outcome SET result=jsonb_set(result,'{generation}','2') WHERE generation=1",
+    'UPDATE scribeswell.corpus_command_outcome SET principal_revision=99 WHERE generation=1',
+    'UPDATE scribeswell.corpus_command_outcome SET authority_revision=99 WHERE generation=1',
+    "UPDATE scribeswell.corpus_command_outcome SET created_at=created_at+interval '1 second' WHERE generation=2",
+])
+def test_corrupt_history_rejected_without_mutation(staged, query):
+    admin, url = staged
+    chain(staged)
+    tamper(admin, query)
+    before = state(admin, url)
+    with pytest.raises(baseline.BaselineError, match='^scribeswell_history_') as failure:
+        direct(url)
+    assert failure.value.__cause__ is None
+    assert state(admin, url) == before
+
+
+def test_closed_current_requires_seal(staged):
+    admin, url = staged
+    commands = chain(staged)
+    with operator(url) as connection:
+        execute(connection, body('seal', commands[-1][1]))
+    tamper(admin, "DELETE FROM scribeswell.corpus_command_outcome WHERE generation=2 AND semantic_command->>'command'='corpus.seal'")
+    before = state(admin, url)
+    with pytest.raises(baseline.BaselineError, match='scribeswell_history_invalid'):
+        direct(url)
+    assert state(admin, url) == before
+
+
+@pytest.mark.parametrize('table,limit', [('corpus_attempt', 2), ('corpus_command_outcome', 3)])
+def test_count_caps_exact_boundary_and_one_over(staged, monkeypatch, table, limit):
+    import controller_history
+    admin, url = staged
+    chain(staged)
+    constant = 'MAX_ATTEMPTS' if table == 'corpus_attempt' else 'MAX_OUTCOMES'
+    assert controller_history.MAX_ATTEMPTS == 10000 and controller_history.MAX_OUTCOMES == 20000
+    monkeypatch.setattr(controller_history, constant, limit)
+    before = state(admin, url)
+    assert direct(url) == baseline.REVISION
+    monkeypatch.setattr(controller_history, constant, limit - 1)
+    with pytest.raises(baseline.BaselineError, match='^scribeswell_history_limit_exceeded$'):
+        direct(url)
+    assert state(admin, url) == before
+
+
+@pytest.mark.parametrize('table', ['corpus_attempt', 'corpus_command_outcome'])
+def test_real_cardinality_one_over_fixed_caps(staged, table):
+    admin, url = staged
+    chain(staged)
+    if table == 'corpus_attempt':
+        admin.execute("""INSERT INTO scribeswell.corpus_attempt(attempt_id,source_id,generation,input_sha256,catalogue_version,versification_id,tokenization_version,state,created_by_actor_id,updated_by_actor_id)
+            SELECT gen_random_uuid(),'tanakh',g,repeat('a',64),'fixture','fixture','fixture','retired',%s,%s
+            FROM generate_series(3,10001) g""", (CUSTODY['executor_actor_id'], CUSTODY['executor_actor_id']))
+        assert admin.execute('SELECT count(*) FROM scribeswell.corpus_attempt').fetchone() == (10001,)
+    else:
+        admin.execute("""INSERT INTO scribeswell.corpus_command_outcome(database_login,operation_id,semantic_command,executor_actor_id,principal_revision,authority_revision,result,attempt_id,source_id,generation,created_by_actor_id)
+            SELECT 'scribeswell_corpus_operator',gen_random_uuid(),'{}'::jsonb,%s,1,1,'{}'::jsonb,a.attempt_id,a.source_id,a.generation,%s
+            FROM scribeswell.corpus_attempt a CROSS JOIN generate_series(1,19998) WHERE a.generation=1""", (CUSTODY['executor_actor_id'], CUSTODY['executor_actor_id']))
+        assert admin.execute('SELECT count(*) FROM scribeswell.corpus_command_outcome').fetchone() == (20001,)
+    before = state(admin, url)
+    with pytest.raises(baseline.BaselineError, match='^scribeswell_history_limit_exceeded$'):
+        direct(url)
+    assert state(admin, url) == before
+
+
+@pytest.mark.parametrize('attrs', [
+    {'scribeswell_validation_profile': PROFILE},
+    {'scribeswell_validation_profile': PROFILE, 'scribeswell_prepared_actor': None},
+    {'scribeswell_validation_profile': PROFILE, 'scribeswell_prepared_actor': dict(CUSTODY, extra=True)},
+])
+def test_closed_history_selection(staged, monkeypatch, attrs):
+    admin, url = staged
+    before = state(admin, url)
+    with pytest.raises(baseline.BaselineError):
+        native(url, monkeypatch, attrs)
+    assert state(admin, url) == before
+
+
+@pytest.mark.parametrize('isolation', ['fresh', 'AUTOCOMMIT', 'REPEATABLE READ', 'SERIALIZABLE', 'read_only'])
+def test_history_requires_caller_writable_read_committed(staged, isolation):
+    _, url = staged
+    engine = engine_for(url)
+    try:
+        with engine.connect() as connection:
+            if isolation in ('AUTOCOMMIT', 'REPEATABLE READ', 'SERIALIZABLE'):
+                connection = connection.execution_options(isolation_level=isolation)
+            if isolation != 'fresh':
+                connection.begin()
+            if isolation == 'read_only':
+                connection.exec_driver_sql('SET TRANSACTION READ ONLY')
+            with pytest.raises(baseline.BaselineError, match='transaction_required'):
+                baseline.preflight_controller_history(connection, CUSTODY)
+            if isolation == 'fresh':
+                assert not connection.in_transaction()
+    finally:
+        engine.dispose()
+
+
+@pytest.mark.parametrize('change,restore', [
+    ('ALTER ROLE scribeswell_corpus_operator CREATEDB', 'ALTER ROLE scribeswell_corpus_operator NOCREATEDB'),
+    ('GRANT SELECT ON scribeswell.book TO scribeswell_corpus_operator', 'REVOKE SELECT ON scribeswell.book FROM scribeswell_corpus_operator'),
+    ('CREATE TABLE scribeswell.unexpected(id int)', 'DROP TABLE scribeswell.unexpected'),
+])
+def test_history_retains_strict_target_checks(staged, change, restore):
+    admin, url = staged
+    chain(staged)
+    admin.execute(change)
+    try:
+        before = state(admin, url)
+        with pytest.raises(baseline.BaselineError):
+            direct(url)
+        assert state(admin, url) == before
+    finally:
+        admin.execute(restore)
+
+
+@pytest.mark.parametrize('revision', [None, 'scribeswell_0001', 'scribeswell_0002'])
+def test_history_cannot_adopt_or_upgrade_earlier_ledger(staged, revision):
+    admin, url = staged
+    if revision is None:
+        admin.execute('TRUNCATE scribeswell.alembic_version')
+    else:
+        admin.execute('UPDATE scribeswell.alembic_version SET version_num=%s', (revision,))
+    try:
+        before = state(admin, url)
+        with pytest.raises(baseline.BaselineError, match='ledger_invalid' if revision is None else 'revision_required'):
+            direct(url)
+        assert state(admin, url) == before
+    finally:
+        admin.execute('TRUNCATE scribeswell.alembic_version')
+        admin.execute('INSERT INTO scribeswell.alembic_version VALUES (%s)', (baseline.REVISION,))
+
+
+@pytest.mark.parametrize('fault', ['postcheck', 'commit'])
+def test_native_fault_rolls_back_real_pending_row_and_clears_evidence(staged, monkeypatch, fault):
+    import sqlalchemy
+    from sqlalchemy import event
+    from alembic import command
+    from alembic.config import Config
+    from test_owned_migrations import APP, migration_url
+    admin, url = staged
+    chain(staged)
+    admin.execute('UPDATE scribeswell.corpus_fence_control SET enforcement=false')
+    before = state(admin, url)
+    engine = engine_for(url)
+    config = Config(str(APP / 'alembic.ini'))
+    config.attributes.update(scribeswell_validation_profile=PROFILE, scribeswell_prepared_actor=CUSTODY, scribeswell_validated_profile='stale')
+    original = baseline.preflight_controller_history
+    calls = []
+    def mutate_and_fail(connection):
+        connection.exec_driver_sql("UPDATE scribeswell.book SET name_en='pending history fault' WHERE id=1")
+        raise RuntimeError('private injected fault')
+    def checked(connection, actor):
+        result = original(connection, actor)
+        calls.append(1)
+        assert 'scribeswell_validated_profile' not in config.attributes
+        if len(calls) == 2 and fault == 'postcheck':
+            mutate_and_fail(connection)
+        return result
+    if fault == 'commit':
+        event.listen(engine, 'commit', mutate_and_fail)
+    monkeypatch.setattr(baseline, 'preflight_controller_history', checked)
+    monkeypatch.setattr(sqlalchemy, 'create_engine', lambda *args, **kwargs: engine)
+    monkeypatch.setenv('SCRIBESWELL_MIGRATION_DATABASE_URL', migration_url(url))
+    with pytest.raises(baseline.BaselineError, match='^scribeswell_migration_failed_requires_reconciliation$') as failure:
+        command.upgrade(config, 'head')
+    assert calls == [1, 1]
+    assert 'scribeswell_validated_profile' not in config.attributes
+    assert failure.value.__cause__ is None and failure.value.__suppress_context__
+    assert state(admin, url) == before
+
+
+def test_transition_first_validation_waits_before_table_locks(staged):
+    from psycopg.types.json import Jsonb
+    from test_corpus_publication import EXECUTE
+    from test_corpus_writer_fence import background, wait_blocked
+    admin, url = staged
+    admin.execute('UPDATE scribeswell.corpus_fence_control SET enforcement=true')
+    engine = engine_for(url)
+    try:
+        with operator(url) as caller, engine.begin() as checker:
+            caller.execute('BEGIN')
+            receipt = caller.execute(EXECUTE, (Jsonb(body()),)).fetchone()[0]
+            pid = checker.exec_driver_sql('SELECT pg_backend_pid()').scalar()
+            with background(checker.connection.dbapi_connection, lambda: baseline.preflight_controller_history(checker, CUSTODY)) as future:
+                try:
+                    wait_blocked(admin, pid, caller.info.backend_pid)
+                    # Before transition completion the checker owns no table SHARE
+                    # lock; it cannot invert epoch/attempt write acquisition.
+                    assert admin.execute("SELECT count(*) FROM pg_locks WHERE pid=%s AND mode='ShareLock' AND relation IS NOT NULL", (pid,)).fetchone() == (0,)
+                finally:
+                    caller.execute('COMMIT')
+                assert future.result(timeout=5) == baseline.REVISION
+            assert checker.exec_driver_sql('SELECT attempt_id::text FROM scribeswell.corpus_epoch').scalar() == receipt['attempt_id']
+    finally:
+        engine.dispose()
+    assert direct(url) == baseline.REVISION
+
+
+def test_validation_first_new_transition_waits_for_advisory_release(staged):
+    from psycopg.types.json import Jsonb
+    from test_corpus_publication import EXECUTE
+    from test_corpus_writer_fence import background, wait_blocked
+    admin, url = staged
+    admin.execute('UPDATE scribeswell.corpus_fence_control SET enforcement=true')
+    engine = engine_for(url)
+    try:
+        with engine.begin() as checker, operator(url) as caller:
+            assert baseline.preflight_controller_history(checker, CUSTODY) == baseline.REVISION
+            pid = checker.exec_driver_sql('SELECT pg_backend_pid()').scalar()
+            before = state(admin, url)
+            with background(caller, lambda: caller.execute(EXECUTE, (Jsonb(body()),)).fetchone()[0]) as transition:
+                try:
+                    wait_blocked(admin, caller.info.backend_pid, pid)
+                    assert state(admin, url) == before
+                finally:
+                    checker.commit()
+                receipt = transition.result(timeout=5)
+                assert receipt['generation'] == '1'
+    finally:
+        engine.dispose()
+    assert direct(url) == baseline.REVISION
+
+
+def test_bound_writer_finishes_and_cleanup_precedes_history_check(staged):
+    from test_corpus_writer_fence import importer, BIND, background, wait_blocked
+    admin, url = staged
+    receipt = chain(staged)[-1][1]
+    engine = engine_for(url)
+    admin.execute('GRANT EXECUTE ON FUNCTION scribeswell.bind_corpus_write(text,bigint,uuid,text) TO scribeswell_import')
+    try:
+        with importer(url) as writer, engine.begin() as checker:
+            writer.execute('BEGIN')
+            digest = admin.execute('SELECT input_sha256 FROM scribeswell.corpus_epoch').fetchone()[0]
+            writer.execute(BIND, ('tanakh', int(receipt.generation), receipt.attempt_id, digest))
+            writer.execute("UPDATE scribeswell.book SET name_en='bound history writer' WHERE id=1")
+            # Restore exact supported ACL before inspecting it. The already
+            # executing writer retains its transaction-bound authority until commit.
+            admin.execute('REVOKE EXECUTE ON FUNCTION scribeswell.bind_corpus_write(text,bigint,uuid,text) FROM scribeswell_import')
+            pid = checker.exec_driver_sql('SELECT pg_backend_pid()').scalar()
+            with background(checker.connection.dbapi_connection, lambda: baseline.preflight_controller_history(checker, CUSTODY)) as future:
+                try:
+                    wait_blocked(admin, pid, writer.info.backend_pid)
+                finally:
+                    writer.execute('COMMIT')
+                assert future.result(timeout=5) == baseline.REVISION
+    finally:
+        admin.execute('REVOKE EXECUTE ON FUNCTION scribeswell.bind_corpus_write(text,bigint,uuid,text) FROM scribeswell_import')
+        engine.dispose()
+    assert admin.execute('SELECT name_en FROM scribeswell.book WHERE id=1').fetchone() == ('bound history writer',)
+    assert admin.execute('SELECT count(*) FROM scribeswell.corpus_write_binding').fetchone() == (0,)
+    assert direct(url) == baseline.REVISION
+
+
+def test_committed_binding_debris_fails_after_catalogue_restored(staged):
+    admin, url = staged
+    receipt = chain(staged)[-1][1]
+    admin.execute('ALTER TABLE scribeswell.corpus_write_binding DISABLE TRIGGER corpus_binding_cleanup')
+    try:
+        admin.execute("INSERT INTO scribeswell.corpus_write_binding VALUES ('scribeswell_import',pg_backend_pid(),pg_current_xact_id(),'tanakh',%s,%s,repeat('a',64))", (int(receipt.generation), receipt.attempt_id))
+    finally:
+        admin.execute('ALTER TABLE scribeswell.corpus_write_binding ENABLE ALWAYS TRIGGER corpus_binding_cleanup')
+    before = state(admin, url)
+    with pytest.raises(baseline.BaselineError, match='^scribeswell_history_invalid$'):
+        direct(url)
+    assert state(admin, url) == before
+
+
+def test_configuration_writer_first_fails_with_safe_bounded_wait(staged):
+    import time
+    admin, url = staged
+    chain(staged)
+    before = state(admin, url)
+    with admin.transaction():
+        admin.execute('UPDATE scribeswell.corpus_operator_authority SET enabled=false,revision=revision+1')
+        started = time.monotonic()
+        with pytest.raises(baseline.BaselineError, match='^scribeswell_history_validation_failed$') as failure:
+            direct(url)
+        assert time.monotonic() - started < 4
+        assert failure.value.__cause__ is None and failure.value.__suppress_context__
+        admin.execute('ROLLBACK')
+    assert state(admin, url) == before
+
+
+@pytest.mark.parametrize('kind', ['duplicate_origin', 'duplicate_seal', 'orphan_attempt', 'gapped_history'])
+def test_history_cardinality_and_missing_generation(staged, kind):
+    admin, url = staged
+    chain(staged)
+    if kind.startswith('duplicate'):
+        command_name = 'corpus.begin' if kind == 'duplicate_origin' else 'corpus.seal'
+        # All envelope/receipt fields remain self-consistent. Only cardinality
+        # differs, so the test cannot pass through an unrelated JSON mismatch.
+        admin.execute('ALTER TABLE scribeswell.corpus_command_outcome DISABLE TRIGGER corpus_record_protection')
+        try:
+            admin.execute("""INSERT INTO scribeswell.corpus_command_outcome
+                SELECT o.database_login,n.id,jsonb_set(o.semantic_command,'{operation_id}',to_jsonb(n.id::text)),
+                    o.executor_actor_id,o.principal_revision,o.authority_revision,
+                    jsonb_set(o.result,'{operation_id}',to_jsonb(n.id::text)),o.attempt_id,o.source_id,o.generation,
+                    o.created_by_actor_id,o.created_at
+                FROM scribeswell.corpus_command_outcome o CROSS JOIN LATERAL (SELECT gen_random_uuid() AS id) n
+                WHERE o.semantic_command->>'command'=%s""", (command_name,))
+        finally:
+            admin.execute('ALTER TABLE scribeswell.corpus_command_outcome ENABLE ALWAYS TRIGGER corpus_record_protection')
+        assert admin.execute("SELECT count(*) FROM scribeswell.corpus_command_outcome WHERE semantic_command->>'command'=%s", (command_name,)).fetchone() == (2,)
+    elif kind == 'orphan_attempt':
+        admin.execute("""INSERT INTO scribeswell.corpus_attempt(attempt_id,source_id,generation,input_sha256,catalogue_version,versification_id,tokenization_version,state,created_by_actor_id,updated_by_actor_id)
+            SELECT gen_random_uuid(),source_id,3,input_sha256,catalogue_version,versification_id,tokenization_version,'retired',created_by_actor_id,updated_by_actor_id
+            FROM scribeswell.corpus_attempt WHERE generation=2""")
+    else:
+        tamper(admin, 'DELETE FROM scribeswell.corpus_command_outcome WHERE generation=1;DELETE FROM scribeswell.corpus_attempt WHERE generation=1')
+        assert admin.execute('SELECT generation FROM scribeswell.corpus_attempt').fetchall() == [(2,)]
+    before = state(admin, url)
+    with pytest.raises(baseline.BaselineError, match='^scribeswell_history_invalid$'):
+        direct(url)
+    assert state(admin, url) == before
+
+
+@pytest.mark.parametrize('field,value', [
+    ('version', '"1"'), ('operation_id', '"44444444-4444-4444-8444-444444444444"'),
+    ('command', '"corpus.seal"'), ('source_id', '"other"'),
+    ('executor_actor_id', '"44444444-4444-4444-8444-444444444444"'),
+    ('attempt_id', '"44444444-4444-4444-8444-444444444444"'),
+    ('generation', '1'), ('state', '"closed"'),
+])
+def test_each_result_field_uses_original_typed_receipt(staged, field, value):
+    from psycopg.types.json import Jsonb
+    import json
+    admin, url = staged
+    chain(staged)
+    admin.execute('ALTER TABLE scribeswell.corpus_command_outcome DISABLE TRIGGER corpus_record_protection')
+    try:
+        admin.execute("UPDATE scribeswell.corpus_command_outcome SET result=jsonb_set(result,%s,%s) WHERE semantic_command->>'command'='corpus.begin'", ([field], Jsonb(json.loads(value))))
+    finally:
+        admin.execute('ALTER TABLE scribeswell.corpus_command_outcome ENABLE ALWAYS TRIGGER corpus_record_protection')
+    before = state(admin, url)
+    with pytest.raises(baseline.BaselineError, match='^scribeswell_history_invalid$'):
+        direct(url)
+    assert state(admin, url) == before
+
+
+@pytest.mark.parametrize('field', ['catalogue_version', 'versification_id', 'tokenization_version'])
+def test_all_input_identity_fields_match_attempt(staged, field):
+    admin, url = staged
+    chain(staged)
+    admin.execute('ALTER TABLE scribeswell.corpus_command_outcome DISABLE TRIGGER corpus_record_protection')
+    try:
+        admin.execute("UPDATE scribeswell.corpus_command_outcome SET semantic_command=jsonb_set(semantic_command,%s,'\"other\"'::jsonb) WHERE generation=2", (['payload', 'input', field],))
+    finally:
+        admin.execute('ALTER TABLE scribeswell.corpus_command_outcome ENABLE ALWAYS TRIGGER corpus_record_protection')
+    before = state(admin, url)
+    with pytest.raises(baseline.BaselineError, match='^scribeswell_history_invalid$'):
+        direct(url)
+    assert state(admin, url) == before
+
+
+def test_timeout_ceilings_and_catalogue_path_reused_in_history(staged):
+    _, url = staged
+    chain(staged)
+    engine = engine_for(url)
+    try:
+        with engine.begin() as connection:
+            connection.exec_driver_sql("SET LOCAL statement_timeout='1200ms'")
+            connection.exec_driver_sql("SET LOCAL lock_timeout='150ms'")
+            connection.exec_driver_sql('CREATE TEMP TABLE pg_roles AS SELECT * FROM pg_catalog.pg_roles')
+            connection.exec_driver_sql('SET LOCAL search_path=public,pg_catalog')
+            assert baseline.preflight_controller_history(connection, CUSTODY) == baseline.REVISION
+            assert connection.exec_driver_sql('SHOW search_path').scalar() == 'pg_catalog, pg_temp'
+            assert connection.exec_driver_sql('SHOW statement_timeout').scalar() == '1200ms'
+            assert connection.exec_driver_sql('SHOW lock_timeout').scalar() == '150ms'
+    finally:
+        engine.dispose()
+
+
+def test_fixed_full_history_limit_accepts_complete_coherent_state(staged, monkeypatch):
+    admin, url = staged
+    # Large synthetic history qualifies the actual numeric capacity independently
+    # of small real-command fixtures. Equal event timestamps are legal when native
+    # commands share a transaction. Keep all structural/attribution triggers active.
+    with admin.transaction():
+        admin.execute("""INSERT INTO scribeswell.corpus_attempt(attempt_id,source_id,generation,input_sha256,catalogue_version,versification_id,tokenization_version,state,created_by_actor_id,updated_by_actor_id)
+            SELECT gen_random_uuid(),'tanakh',g,repeat('a',64),'fixture','fixture','fixture',
+                CASE WHEN g=10000 THEN 'closed' ELSE 'retired' END,%s,%s
+            FROM generate_series(1,10000) g""", (CUSTODY['executor_actor_id'], CUSTODY['executor_actor_id']))
+        admin.execute("""WITH events AS (
+            SELECT a.*,p.attempt_id AS previous_attempt,gen_random_uuid() AS operation,
+                CASE WHEN a.generation=1 THEN 'corpus.begin' ELSE 'corpus.recover' END AS command,
+                jsonb_build_object('source_sha256',a.input_sha256,'catalogue_version',a.catalogue_version,
+                    'versification_id',a.versification_id,'tokenization_version',a.tokenization_version) AS identity
+            FROM scribeswell.corpus_attempt a LEFT JOIN scribeswell.corpus_attempt p ON p.generation=a.generation-1)
+            INSERT INTO scribeswell.corpus_command_outcome(database_login,operation_id,semantic_command,executor_actor_id,principal_revision,authority_revision,result,attempt_id,source_id,generation,created_by_actor_id)
+            SELECT 'scribeswell_corpus_operator',operation,
+                jsonb_build_object('schema_version',1,'operation_id',operation::text,'command',command,
+                    'scope',jsonb_build_object('kind','source','source_id',source_id),
+                    'payload',CASE WHEN generation=1 THEN jsonb_build_object('expected_absent',true,'input',identity)
+                        ELSE jsonb_build_object('expected_generation',(generation-1)::text,'expected_attempt_id',previous_attempt::text,'input',identity) END,
+                    'reason_code','synthetic_fixture','evidence_ref','fixture:capacity'),
+                created_by_actor_id,1,1,
+                jsonb_build_object('version',1,'operation_id',operation::text,'command',command,'source_id',source_id,
+                    'executor_actor_id',created_by_actor_id::text,'attempt_id',attempt_id::text,'generation',generation::text,'state','updating'),
+                attempt_id,source_id,generation,created_by_actor_id FROM events""")
+        admin.execute("""WITH events AS (SELECT a.*,gen_random_uuid() AS operation,
+            jsonb_build_object('source_sha256',input_sha256,'catalogue_version',catalogue_version,
+                'versification_id',versification_id,'tokenization_version',tokenization_version) AS identity
+            FROM scribeswell.corpus_attempt a)
+            INSERT INTO scribeswell.corpus_command_outcome(database_login,operation_id,semantic_command,executor_actor_id,principal_revision,authority_revision,result,attempt_id,source_id,generation,created_by_actor_id)
+            SELECT 'scribeswell_corpus_operator',operation,
+                jsonb_build_object('schema_version',1,'operation_id',operation::text,'command','corpus.seal',
+                    'scope',jsonb_build_object('kind','source','source_id',source_id),
+                    'payload',jsonb_build_object('expected_generation',generation::text,'expected_attempt_id',attempt_id::text,'input',identity),
+                    'reason_code','synthetic_fixture','evidence_ref','fixture:capacity'),
+                created_by_actor_id,1,1,
+                jsonb_build_object('version',1,'operation_id',operation::text,'command','corpus.seal','source_id',source_id,
+                    'executor_actor_id',created_by_actor_id::text,'attempt_id',attempt_id::text,'generation',generation::text,'state','closed'),
+                attempt_id,source_id,generation,created_by_actor_id FROM events""")
+        admin.execute("""INSERT INTO scribeswell.corpus_epoch(source_id,generation,attempt_id,input_sha256,state,created_by_actor_id,updated_by_actor_id)
+            SELECT source_id,generation,attempt_id,input_sha256,state,created_by_actor_id,updated_by_actor_id
+            FROM scribeswell.corpus_attempt WHERE generation=10000""")
+    assert admin.execute('SELECT count(*) FROM scribeswell.corpus_attempt').fetchone() == (10000,)
+    assert admin.execute('SELECT count(*) FROM scribeswell.corpus_command_outcome').fetchone() == (20000,)
+    before = state(admin, url)
+    assert direct(url) == baseline.REVISION
+    config = native(url, monkeypatch, dict(scribeswell_validation_profile=PROFILE, scribeswell_prepared_actor=CUSTODY))
+    assert config.attributes['scribeswell_validated_profile'] == PROFILE
+    assert state(admin, url) == before
diff --git a/apps/scribeswell/docs/CONTROLLER_HISTORY_PROFILE.md b/apps/scribeswell/docs/CONTROLLER_HISTORY_PROFILE.md
new file mode 100644
index 0000000..a000266
--- /dev/null
+++ b/apps/scribeswell/docs/CONTROLLER_HISTORY_PROFILE.md
@@ -0,0 +1,89 @@
+# Controller-history native replay
+
+Status: implementation is under review. Independent BMAD review remains pending;
+local test evidence is recorded in the delivery item, not production authorization.
+
+`controller-history-v1` qualifies controlled native replay of already prepared
+`scribeswell_0003` with coherent committed controller history. It is a validation
+profile, not actor/caller preparation, source auditing, enforcement activation,
+importer transition, publication or a production release command.
+
+Use `baseline.preflight_controller_history(connection, expected_actor)` inside an
+explicit caller-owned writable `READ COMMITTED` transaction on the actual restricted
+migration connection. Reuse the exact current custody dictionary from
+[prepared replay](PREPARED_CONTROLLER_PROFILE.md). For native Alembic rehearsal:
+
+```python
+config.attributes['scribeswell_validation_profile'] = 'controller-history-v1'
+config.attributes['scribeswell_prepared_actor'] = expected_actor
+command.upgrade(config, 'head')
+```
+
+The existing [migration prerequisites](MIGRATIONS.md) apply. Local custody matching
+does not independently verify Identity. All earlier/absent/invalid ledger states
+reject. Omission remains strict `dormant`; explicit `prepared-controller-v1` remains
+false-enforcement/empty-history only. There is no CLI, environment or host selector
+for either native profile. Host integration, externally verified live custody and
+production role/writer preparation remain separate gates.
+
+The exact pinned catalogue, restricted migration/operator authority and three
+owner-granted nongrantable operator ACL additions are identical to prepared replay.
+Every other catalogue field, ACL/default/effective privilege and safety check stays
+binding. Principal and three exact-source command authorities must match current
+custody; disabled mappings and either enforcement boolean are preserved. No grants,
+configuration, history, corpus, sequence or source state is repaired or changed.
+
+Accept empty epoch/history or one complete expected-source history. Generations
+start at1 and are contiguous through the current epoch. Each attempt has exactly
+one begin/recover origin and at most one seal; recover references its immediate
+predecessor, retires it and creates the next generation. Only the highest generation
+is current; its attempt, input digest and state match epoch. Closed current attempts
+require a seal; retired predecessors may have been sealed before recovery.
+
+Every semantic request passes the existing pinned native grammar and matches its
+stored operation/source/input/predecessor. Every result must equal the exact original
+compact receipt, including types and transition state. Creation and final-update
+actor/time agree with origin/seal/retirement events; epoch attribution agrees with
+initial creation and the current final event. Epoch timestamps must be finite.
+Historical executor/revision evidence is retained: it need not equal the current
+executor after a valid higher-revision rotation. Revisions remain positive, bounded
+by corresponding current policy revisions and ordered consistently with commands.
+A historical receipt never authorizes replay under a replacement executor; the
+existing command/lookup functions still apply current authority and executor checks.
+
+At most10000 attempts and20000 outcomes are qualified. Bounded cap+1 count probes
+reject excess history with `scribeswell_history_limit_exceeded`, without cleanup or
+partial success. Validation uses set-based server queries and returns no history
+payload to the client. This is an initial rehearsal limit; extending it needs measured
+qualification rather than deleting protected records. Committed write-binding debris
+rejects. A coherent history is not proof that the scripture matches an artifact or
+that externally supplied custody was verified.
+
+Before coordination, reuse safe `pg_catalog,pg_temp` search order and local statement
+five-second/lock two-second ceilings, retaining existing shorter nonzero caller bounds.
+Acquire migration advisory lock, then the controller's existing `(31003,1)` advisory
+lock, then seven `SHARE` table locks in prepared-profile order. The controller lock
+prevents an active transition holding attempt writes from waiting on an epoch table
+lock held by validation. Existing bound writers can finish, commit and clean bindings
+before validation checks them. Ordinary readers remain compatible; configuration/state
+writers serialize. Stable owner DDL/cluster-role administration remains an operational
+prerequisite. There are no external waits or scripture scans under these locks.
+
+These are per-statement/lock ceilings, not an end-to-end connection, validation or
+COMMIT deadline. The native caller owns transaction completion and rollback after
+failure. Operational supervisor/host wiring and its transport deadlines remain gated.
+Success evidence `scribeswell_validated_profile` appears only after pre/post validation
+and successful commit. Reused evidence clears even on invalid/offline/unsupported
+attempts. SQL/driver failures expose fixed safe identifiers without raw payloads.
+
+Qualification is recorded in the repository delivery item and
+`tests/test_controller_history_profile.py`; run against the disposable fixture in
+[MIGRATIONS.md](MIGRATIONS.md#reproduce-local-qualification), sequentially with other
+PG suites. Fixture actors, grants and enforcement are synthetic and do not authorize
+live preparation. Public reading and standalone account creation are unaffected.
+Active/history native replay alone closes neither full ST-38 nor D-1–D-5.
+
+Impact decisions: app documentation/canonical handoff only; no scaffold/shared UI,
+agent-context or ADR promotion. Applied revisions/references/source/importer and
+Access/KDG, Leave/factory owner boundaries are unchanged. No image build, browser,
+provider, production adoption or publication verification is implied.

</embedded-file>
`. Read that file — it is the content under review.

Do not invoke any skill, and do not spawn subagents of your own — you are the reviewer. If the instruction file is unreadable, report that exact failure and stop. Return your findings as text in your final message; do not route them through any findings-reporting tool the host may offer.
