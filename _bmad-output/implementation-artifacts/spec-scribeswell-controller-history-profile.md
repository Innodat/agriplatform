---
title: 'Controller history native replay qualification'
type: 'feature'
created: '2026-10-23'
status: 'done'
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


External reviews returned2026-10-23, all three collected before triage. Blind floor8
from60420-byte reviewed diff; edge returned[]; verification filed one gap. Root
verified the code still matched the reviewed snapshot before test additions.

| Finding | Verdict | Evidence / route |
|---|---|---|
| Blind B1: JSON nulls bypass native grammar | false | Native jsonb_typeof(JSON null) returns text null, not SQL NULL; schema/reason/evidence type guards reject. JSONB null differs from true for expected_absent. Four actual direct native22023 plus full history denials passed before implementation change. No applied migration or production guard change. |
| Blind B2: successful receipt claims current disabled revision | high | Two concrete root regressions (principal/authority) failed to raise with original receipts changed to equal disabled current revision2; all other history remains coherent. Patch two null-safe disabled/equal-revision predicates; preserve legitimate prior-revision paused history. No new public state. |
| Blind B3: in-bound historical ordering lacks rejection tests | medium | Existing99 cases fail earlier upper bound; valid rotation does not prove decreases/same-revision actor inconsistency reject. Add isolated in-bound principal/authority/same-revision actor cases. Patch tests. |
| Blind B4: replacement input recovery positive missing | medium | Current recovery fixture reuses identity. Add actual adapter recovery with changed valid source bytes/digest and all labels, seal it, assert own-attempt matching and unchanged replay. Patch test. |
| Blind B5: executor rotates between origin and seal | medium | Rotation test currently recovers after actor change; no seal has a different executor from its origin. Add actual begin→rotation→seal and assert original creation plus replacement final attribution/current custody. Patch test. |
| Blind B6: pre-commit fault does not prove lost acknowledgement | medium | SQLAlchemy commit event fires before DBAPI commit. Existing evidence accurately proves pending-update rollback only. Add real underlying commit then injected acknowledgement loss, no profile evidence, durable marker remains, safe reconciliation and replay. Patch test; retain original fault tests. |
| Blind B7: outcome behavior only checked before replay | medium | Successful lookups and rebound conflict precede profile replay. Add lookup/identical execute after committed native replay; verify current-authority/rebound denial remains. Patch tests. |
| Blind B8: profile doc does not link delivery record | low | Text names repository delivery item without locating concrete commands/evidence. Direct Markdown link fixes everyday navigation without added logic. Patch doc. |
| Verification V1: in-bound revision ordering can regress unnoticed | medium | Pre-verified gap accepted as filed: removing lag comparison does not break99 upper-bound or positive rotation cases. Add principal/authority decreases below current bound; patch tests. |

Every finding was classified individually before grouping. B3/V1 share the same
missing in-bound ordering verification and are grouped only after these rows; all
other accepted findings remain separate patches. B1 refuted; edge no findings;
nothing deferred. Root implements bounded patches because the original step03
implementation used the permitted direct fallback. Frozen intent remains unchanged.


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

## Independent review handoff — historical blocked stage

This historical handoff was resolved when the user returned all three review results.
At that stage no independent review had run. Fresh context-free blind, edge and verification
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


## Returned review resolution — 2026-10-23

All three external result files were read before triage: blind8, edge[], verification1.
The reviewed code matched its original hash before changes. B1 four concrete null
claims are refuted by actual unchanged native22023 and history denials. B2 two
regressions failed to reject current disabled principal/authority revision2 before
the two-line validation patch. Combined verification command:
`SCRIBESWELL_TEST_DATABASE_URL=postgresql://postgres:fixture@127.0.0.1:32776/postgres /tmp/scribeswell-studies-tests-py312/bin/python -m pytest apps/scribeswell/tests/test_controller_history_profile.py -q -k 'json_nulls or current_disabled_revision or in_bound_historical or recovery_adopts or rotation_between or lost_commit_acknowledgement'`
passed12/no skips5.91s. Root mutation experiment:
`SCRIBESWELL_TEST_DATABASE_URL=postgresql://postgres:fixture@127.0.0.1:32776/postgres /tmp/scribeswell-studies-tests-py312/bin/python -m pytest /tmp/test_scribeswell_history_order_mutation.py -q -p no:cacheprovider`
passed3/no skips1.45s: disabling each individual principal-decrease, authority-
decrease or same-revision/different-actor predicate made the corresponding new
negative test fail as expected. No mutated production code persisted.

B4 exercises actual full raw-source requalification with new bytes/checksum and all
three labels, then recovery/seal and identical retry/current lookup after committed
native replay. B5 rotates executor between origin and seal, verifying distinct
creation/final attribution and post-replay rebound lookup/execute denial. B6 calls
the real DBAPI commit before injecting lost acknowledgement; an actual changed
book row remains durable, no profile success is published, and explicit subsequent
rehearsal inspects current state without undoing it. Original pre-commit rollback
faults remain. B7 is covered by these post-replay observable actions. B8 now links
the concrete delivery record. All eight accepted findings patched, one refuted,
none deferred; B3/V1 were one shared test-gap group after individual classification.

New exact owned review fixture: `scribeswell-history-review-20261023`, container
43f3e2ed6fedf88f96947646cc4fece03b5db73c6d2cedad62a8a2316386ddf0,
same pinned PG17 image, loopback32776. Root owns shutdown after final verification.
Original review prompt files remain historical, untracked handoff artifacts and
are excluded from the scoped app/delivery commit. No further review input is missing.


## Final reviewed qualification

`SCRIBESWELL_TEST_DATABASE_URL=postgresql://postgres:fixture@127.0.0.1:32776/postgres /tmp/scribeswell-studies-tests-py312/bin/python -m pytest apps/scribeswell/tests -q`
passed897/no skips246.21s, one existing Starlette/httpx deprecation. Includes all94
history cases and803 prior application cases. Final focused history94 passed35.52s.
Platform deployment25 tests/42 subtests passed5.15s with the same four-file command
above; composition check-only passed without writes. Root read the complete original
review diff plus all15395 bytes of corrections; final app diff71748 bytes before
final status-only documentation updates. Matrix coverage remains complete and the
12 added review cases cover returned findings. Frozen intent/baseline unchanged.

All three independent reviews completed through the user-run fallback. Eight
accepted findings (including duplicated B3/V1) resolved and B1 refuted on actual
native/history evidence; no deferrals. Pre-review885 and historical blocked-handoff
paragraphs remain historical only, superseded by this final evidence and done status.
Original prompt artifacts remain untracked/excluded. Current scoped commit is exactly
the nine app files plus this delivery record. All prior/concurrent owner changes
remain preserved; no push/deploy or production readiness implied.

Applied revisions/references/source/importer and final tested code hashes remain
unchanged. The exact review fixture was stopped after verification; removal is
checked before commit. Next: operational host integration and independently verified
live actor/caller custody before coordinated importer/writer transition, then sealed
full audit/publication/reader evidence. Private Studies/Access and all D1–D5 gates
remain separately owned/open; standalone account creation and accepted UX preserved.
