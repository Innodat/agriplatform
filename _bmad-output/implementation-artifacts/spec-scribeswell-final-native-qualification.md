---
title: 'Complete native Scribeswell data-path qualification'
type: 'bugfix'
created: '2026-10-26'
status: 'done'
route: 'dispatch'
baseline_commit: '7c0e9319c8dc05cd51a3814d7753db0d3048ff81'
review_loop_iteration: 0
context:
  - /home/ck/repos/innodat/agriplatform/AGENTS.md
  - /home/ck/repos/innodat/agriplatform/apps/scribeswell/docs/OWN_HIGHLIGHTS_V1.md
  - /home/ck/repos/innodat/agriplatform/apps/scribeswell/docs/OWN_COPIES_V1.md
  - /home/ck/repos/innodat/agriplatform/apps/scribeswell/docs/STUDY_DETAILS_DISCOVERY_V1.md
  - /home/ck/repos/innodat/agriplatform/_bmad-output/specs/spec-scribeswell-studies/corpus-publication.md
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

Finish the actual database qualification of the completed personal Studies implementation, correcting demonstrated defects and invalid fixtures while preserving the agreed behavior. Establish real migration, permission, content, concurrency and original-operation recovery evidence before the final browser/owner/device/release assessment.

## Boundaries & Constraints

Always preserve original failing evidence, current authority, independent app/service ownership, existing input and previous supported writers. Use observed native failures as ATDD red and focused TDD/qualification for fixes. User authorizes technical choices and continuous implementation without routine stops.

Native execution is now permitted only against fresh uniquely owned disposable PostgreSQL17 fixtures with loopback dynamic ports, exact owned cleanup and explicit source snapshots. Earlier no-native implementation slices are complete. Never touch KDG55481/55482, retained or production databases, live owners, production activation, platform/other apps, accepted ADRs, generated files or byte-frozen historical consumer fixtures. No push or competing Access/Notification implementation. Parent owns combined final regression, canonical derivation and checkpoint.

</frozen-after-approval>

## Code Map

All app paths below under apps/scribeswell/; canonical adopted contracts retain product authority.
- docs/evidence/final-integration/native-full.log, native-results.json, native-failures.json: actual first combined run2233pass37fail68errors390.97s, no skips, source unchanged, owned container stopped/32768 released. Read exact relevant failure sections; never relabel this run green. Summarized roots below are investigation leads, not permission to change expected outcomes.
- tests/test_corpus_publish_native.py closed fixture uses INSERT verse VALUES without column list; actual schema order is id,chapter_id,verse_num,book_id,chapter_num, while fixture supplies id,chapter_id,book_id,chapter_num,verse_num. This explains multiverse duplicate key and may explain corpus_mismatch; verify actual source/rows before changing auditor. tests/test_reader_evidence_native.py consumes this fixture.
- tests/test_personal_notes_storage.py native fixture fails at historical0004 retry (line159), causing68setup errors across copies/highlights/details/private storage. studies-migrations/env.py safely suppresses driver causes; diagnose inside owned fixture with temporary safe class/sqlstate observations, no credential/payload dumps. Do not assume a new schema failure without inspecting it. Reuse real previous-version loaders and controlled transaction semantics.
- tests/test_caller_preparation_rehearsal.py injected SELECT1/0 runs directly in before_cursor_execute callback; psycopg DivisionByZero escapes outside SQLAlchemy wrapping while test expects DBAPIError. Preserve real PostgreSQL failure and complete rollback assertions; correct injector/precise expected driver classification only after explaining it.
- tests/test_owned_migrations.py nonhead rejection includes0003 although dormant/controller historical head is deliberately pinned0003 (migrations/env.py). Preserve accepted versioned profiles and add explicit positive/negative coverage rather than breaking old profile compatibility.
- tests/studies_owner_fixture.py qualification dependency loop now requires rfc8785; parent restored pinned0.1.4 only in isolated /tmp Python using verified RECORD hashes from platform/deployment/.local/python-baseline-qualification/cache/archive-v0/lWPAEJW2owTOrdwO and offline repacked wheel. Shared cache/source unchanged. Six owner-fixture failures need focused rerun, not source relaxation.
- /tmp/scribeswell-final-native-run.py is parent runner: fresh named/labeled postgres:17, dynamic loopback port, explicit test DSNs/opt-ins, sequential pytest, snapshots and exact container stop. Do not overwrite initial evidence. Make a focused variant with a distinct evidence directory and explicit pytest node arguments; no parallel native suites (roles cluster-global). Prepared Python /tmp/scribeswell-implementation-python/bin/python. Docker postgres17 cached. Normal sandbox escalation for isolated native execution, separately from workspace edits.

## Tasks & Acceptance

- [x] Read native failures, classify fixture/environment/runtime causes and retain exact observed red evidence. Correct demonstrated publication fixture column/source mismatch and precise rollback injection/profile expectations without weakening existing behavior assertions. Restore all affected tests to executing their real target paths.
- [x] Diagnose/fix the historical private migration retry failure safely. Preserve controlled rollback, FORCE RLS before commit, bounded migrations and prior writers. Prefer ordinary owner migration semantics and smallest demonstrated fix; do not build a new migration framework or change unrelated owners. Do not edit historical migrations speculatively: any necessary correction to an unreleased owning revision that itself prevents reaching a successor must be justified with actual driver/native evidence and prior-version safety, never applied to retained/production state.
- [x] Execute all newly authored copies/highlight metadata/study details/context/publication/reader native tests after fixtures work. Fix actual runtime/SQL defects minimally with failing-then-passing evidence; verify real permissions, lifecycle, snapshots, concurrency, rollback and original operation replay. No assertion weakening to silence unexplained failures. Add a real API/native NUL text probe (escaped U+0000 currently passes _unicode but PostgreSQL JSONB cannot store it); if it produces generic storage failure, reject impossible-to-store input safely before SQL without stripping newlines/combining marks. Synchronize owning contracts/generated DTOs if changed through generators.
- [x] Qualify contextual SQL with representative volume/deadline evidence and controlled publication with actual checked-in scripts/hebrew.json plus supported capacity/timing. Reuse fixture/import/auditor paths; no fake claimed publication proof, arbitrary scope/data caps or timeout relaxation to hide a failure. Observe performance failures before optimizing; record exact source/manifest counts, bounds and elapsed work. Distinguish deliberate stdout discard from actual network loss.
- [x] Retain focused exact commands/results/source pairs and every failure/process limitation in app FINAL_INTEGRATION_EVIDENCE.md plus owned evidence. Record scaffold/shared-UI/agent-context/docs/ADR impact. No canonical specs/memory, staging or commit. Parent independently reviews and runs final combined browser/owner/release assessment; do not rerun whole2300-test suite or full browser matrix repeatedly.

Acceptance:
- Given fresh owned PostgreSQL17, when native workflows execute, then required migrations, RLS, coherent edits/copies/context reads and original-operation recovery pass without skips or fixture errors for the affected cases.
- Given malformed or impossible-to-store user input, when handled, then safe input failure preserves data and no partial note/receipt commits.
- Given a migration or competing write failure, when retried under original authority, then rollback/forward recovery and lifecycle/attribution invariants remain proved.

## Implementation Notes

Planning uses actual combined failures, not proposed defects. No intent gaps or irreversible external actions; only ephemeral owned DB state is mutable. Cohesive full qualification scope retained under user's continuous delegation. Runtime/publication performance changes require demonstrated evidence, not speculative optimization. App-only impact unless parent later authorizes proven shared promotion; no current platform changes.

## Spec Change Log

## Review Triage Log

All three BMAD lenses launched context-free before triage. Runtime thread limit allowed only one fresh reviewer at a time; subsequent lenses launched after completion, with no patches or finding decisions before all reported.

| ID | Verdict / route | Verified evidence and disposition |
| --- | --- | --- |
| B1 | medium / verification patch | Complete final native run remains pending, exactly as the evidence states; parent will execute the prepared frozen full suite and retain the original2233/37/68 red. |
| B2 | medium / verification patch | Successful28.060s artifact run used diagnostic COPY; supported importer plus final publication must run in parent full native suite. No importer success is inferred from COPY. |
| B3 | medium / verification patch | Actual DB/browser bridge is explicitly pending; parent full native opt-in executes existing create/write/reopen bridge alongside full native lifecycle/metadata tests. No mocked browser result substitutes for it. |
| B4 | medium / verification patch | Final browser matrix is pending and will execute once after review corrections; focused desktop grammar case is not matrix acceptance. |
| B5 | false / reject | Existing canonical corpus-publication contract602-606 bounds each invocation and requires retained original-operation recovery; it does not promise every maximum corpus always completes in one invocation. Test retains original unknown outcome and explicitly reconciles/reuses the same operation, with runtime automatic retry absent. Independent first-window maximum56.748s is separately retained, not inferred from a retry. |
| B6 | low / direct evidence patch | Near-budget maximum is explicitly one observation, not a reliability guarantee. Parent final runner will retain host/fixture resource observations and a second final-source measurement; no redundant benchmark loop or stronger SLA. |
| B7 | false / reject | Actual publication writer corpus_publish.py is byte-identical to prior checkpoint7c0e9319c8dc05cd51a3814d7753db0d3048ff81, SHA2564ded06f8025f6c210823a7d1c9ad88d50db31b3215ac60d3f7cfeaa8c868665d. New0006 native tests run that unchanged prior SQL writer, including acknowledged original-operation replay; the source-qualification cache changes no publication wire. This is actual previous writer execution, not only profile refusal tests. |
| B8 | medium / patch | NUL regression covers create only. Add actual replacement rejection with existing value/revision/metadata/receipt snapshot unchanged and valid same-operation retry. Shared DTO rejects before SQL, but preserve this meaningful existing-data oracle. |
| B9 | medium / patch | NoteEditor inlines currently accepts NUL and sends a doomed save despite the stricter incoming wire guard. Add editor input red, reject impossible scalar input locally with existing Changes not saved/Retry, keep DOM input correctable and prove no save before correction. Preserve newline/combining behavior. |
| B10 | medium / patch | Added schema not-pattern excludes NUL only while runtime also rejects lone surrogates. Synchronize owning JSON-schema Unicode-scalar grammar without excluding valid supplementary characters; exporter/generator only, with real JavaScript pattern oracle. |
| E1 | medium / patch | Batch foreign-key check can hold KEY SHARE on immutable header before statement guard FOR UPDATE; two alternate appends can deadlock on upgrades. Controlled producer already locks header first, but previous alternate-write serialization regresses. Reproduce with actual concurrent lock ordering then use compatible NO KEY UPDATE statement guard while preserving completion serialization/actor checks. |
| V1 | medium / patch | Verified regression gap: capacity completion corruption tests bypass new batch comparison; malformed IDs do not cover valid-but-wrong digest. Add capacity command wrong-digest atomic refusal/no rows/no receipt and unchanged original-operation retry. |
| P1 | medium / patch | New worker reports before0006 on failure, but deployment/migrate.py main failure-envelope allowlist stops at0005, dropping recovery evidence. Synchronize with existing shared REVISIONS and test current-head failure evidence without changing unknown/reconciliation semantics. |
| P2 | medium / defer | Pre-existing studies_migrate.py returns hard-coded after0001 despite upgrading head; outer app wrapper expects same marker. This predates current native fixes and does not stop private migrations, but misstates actual release head. Platform host-release.py:206 also requires that exact marker, so an app-only change would break activation qualification. This requires coordinated owner release-contract adoption before activation; current native proof uses actual Alembic ledger. |

## Verification

Use distinct owned focused runner/evidence, explicit native opt-ins and DSNs confined to new fixture, exact cleanup even on interruption. First isolate shared fixture root then affected cases, preserving expected outcomes. Application-only tests for grammar/adapter changes; owning generator/build checks when affected. Parent owns full final regression after return. Never reuse/stop another session's fixture or overwrite first native-full log.

### Review correction results

Original same-context implementer fixed B8/B9/B10/E1/V1/P1 with smallest changes. Actual native red retained40P01 and before0006 report loss; other assertion-prefix failure explained, never used to weaken storage or atomicity checks. Native green16pass112.66s; concurrency expanded to all3tables3pass27.25s. Editor/schema browser red2fail; first green1fail1pass retained because test incorrectly expected automatic saving after invalid input; unchanged existing explicit Retry semantics explained, corrected2pass13.1s. Schema/export6pass2.10s. Generated artifacts changed only through owners. Parent verified NO KEY UPDATE still conflicts with completion FOR UPDATE, all actor/immutable/digest checks retained, and prior publication writer exact bytes unchanged. B1-B4/B6 await parent final runners; P2 stays external coordinated release-contract adoption. Parent corrected table/index summary to retain both first-green browser outcomes, with raw log/results unchanged.

### Parent final-browser findings — pending correction


The first full desktop/mobile matrix remains running on a frozen source snapshot. Individual observed failures below are recorded before correction; repeated viewport instances will remain in the complete failure inventory. No pass or startup cause is inferred.

| ID | Verdict / route | Observed evidence and smallest intended correction |
| --- | --- | --- |
| F1 | fixture / patch | personal-notes263 context-notes POST is incorrectly intercepted by reviewLibrary as a StudyView, creating an unrelated alert. Exact context-notes fallback preserves the existing valid setup handler and original alert assertion. |
| F2 | unexplained / investigate | personal-notes266 blank startup times out before initial Studies button, without a page snapshot. Retain original context and diagnose safe startup errors; do not claim fixture fixes explain it or increase timeout blindly. |
| F3 | fixture / patch | personal-notes487 Notes button selector now matches reference navigation controls as well as note previews. Select the first direct preview button per note row, preserving all note rows and roundtrip assertions. |
| F4 | fixture / patch | personal-notes561 Bold owned-atom roundtrip has the same independently observed preview-selector ambiguity. Preserve formatting and reload assertions. |
| F5 | fixture / patch | personal-notes561 Italic owned-atom roundtrip has the same independently observed preview-selector ambiguity. Preserve formatting and reload assertions. |
| F6 | fixture / patch | personal-notes561 Bullet list owned-atom roundtrip has the same independently observed preview-selector ambiguity. Preserve formatting and reload assertions. |
| F7 | fixture / patch | personal-notes561 Numbered list owned-atom roundtrip has the same independently observed preview-selector ambiguity. Preserve formatting and reload assertions. |
| F8 | fixture / patch | personal-notes564 passage-only preview matches both preview and reference buttons. Preserve exact preview text, reopen and note-content assertions. |
| F9 | runtime / patch | personal-notes1464 sole conflicted note reentry bypasses exit guard via same-current fastpath, retaining stale conflict lane. This behavior predates the native baseline. Canonical reader-interaction87 requires changing the edited aggregate to use the exit guard; existing test specifies Stay then Switch anyway and latest read. Reuse current guard, retire only consented abandoned definitive-conflict lane and fetch fresh; preserve shared conflicts, clean reveal and unknown operations. |
| F10 | fixture / patch | workspace-restoration145 resource404 never reaches target: successful initial note literal146 omits required visibility:study. Add required field only; retain clearing/isolation assertions. |
| F11 | fixture / patch | workspace-restoration151 late candidate never reaches target: successful literal152 omits visibility:study. Add required field only; retain dirty-lane and privacy assertions. |
| F12 | fixture / patch | workspace-restoration163 admission403 never reaches target: successful literal164 omits visibility:study. Add required field only; retain all-current-lane clearing assertions. |
| F13 | fixture / patch | workspace-restoration190 note404 variant never reaches target: successful literal192 omits visibility:study. Add required field only; retain affected/unrelated association assertions. |
| F14 | fixture / patch | workspace-restoration190 study404 variant independently fails at same initial literal192. Preserve distinct case and existing assertions. |
| F15 | fixture / patch | workspace-restoration196 hydration401 never reaches target: successful literal197 omits visibility:study. Add required field only; retain dirty lane and original command recovery. Complete negative control literal205 likewise so wrong ID/parent/owner is the tested refusal reason. |

First parent full browser run completed1133passed29failed2expected native-only skips34.3min (2058.85s),103selected file hashes unchanged. All29error contexts are preserved before subsequent runners in app evidence/final-integration/browser-first-failure-contexts; browser-failure-inventory.json retains every viewport instance. Mobile repeats F1/F3-F15 except unexplained F2; no additional root was observed. Parent corrections are in focused verification. Live-owner approved ports55481/55482 were occupied at a nonmutating probe, so no new live-owner fixture was started and that environment remains untouched.

| ID | Verdict / route | Observed evidence and disposition |
| --- | --- | --- |
| F16 | medium unverified / investigate | Focused corrected46-case run45passed1failed218.72s, unchanged103sources. Mobile admission403 now fails at initial first-tab Private label1 (Genesis1 instead), while desktop and other corrected targets pass. Missing visibility is corrected; inspect actual candidate/request ordering before any fixture or runtime correction. Preserve focused red/context; do not weaken authorization assertions or infer the earlier blank startup has this cause. |

F16 resolved by controlled actual response inversion: admission-controlled-order-red1failed19.95s with unchanged103sources, safe diagnostics show two study requests/two note requests and saved-0 privateLabel=false while saved-1=true. Holding first study response allows second candidate to own first note response, so the note-arrival counter does not identify a tab. Six uninverted diagnostic passes35.4s are retained but do not establish a fix. Route medium/fixture patch: explicitly sequence fixture study responses/first hydration, retaining original global403 and input/privacy assertions; inspect same existing ambiguous gates for identical fixture cause. No runtime authorization change or timeout relaxation.

## Cross-cutting impact decisions

- Scaffold: no shared scaffold change; migrations and corpus qualification are app-owned. Existing owning OpenAPI/DTO/database-helper generators provide the affected reproducible artifacts.
- Shared UI: no promotion; note aggregate validation and conflict-lane behavior depend on this app's note/operation contracts, with no new reusable UI component.
- Agent context: no change; current AGENTS instructions already cover native proof, short transactions, migration safety and owner boundaries.
- Documentation: app final integration evidence retains commands, source pairs, failures, measured limits and external gates. Parent derives canonical current status through bmad-spec from append-only memory, preserving IDs and accepted intent.
- ADRs: no new or edited accepted decision; this implements existing controlled migration, structural integrity, scalar API contract, saving/recovery and owner-isolation decisions. Coordinated release-report adoption remains an external owner gate.

### Parent corrected full-matrix findings (run still active)

| ID | Verdict / route | Verified observation and disposition |
| --- | --- | --- |
| F17 | medium / interaction test patch | personal-notes222 existing reopen/Review latest test now waits behind the deliberate sole-conflict consent dialog. Retained local-input/no-read assertions still pass; new E1 behavior requires explicit Stay then Analysis before Review latest. Preserve all existing latest-read/Use latest assertions and add that required user flow after matrix freeze release. This is exposed by the new guard, not unexplained storage failure. |
| F18 | medium unverified / investigate | personal-notes391 collected uncertain operation times out waiting initial Studies button with no page snapshot, same observed blank-startup shape as F2 at a different case. No root cause established. Preserve context and instrument safe startup state across the affected fixture owner after freeze release; no blind timeout or runtime patch. |

F17 correction adds explicit Stay then Analysis while preserving original local-text/no-read and Review latest/Use latest/read-count oracles. Final14focused bothviewport29.7s passed on unchanged103sources; prior14pass26.7s precedes a diagnostic frame-parser safety correction and remains distinct. Actual helper JS oracle3assertions proves message URLs excluded, source pathname/line/column retained with query removed and missing-stack handling. Runtime/build/native/backend source unchanged; final complete browser matrix is running separately in browser-complete, no pass inferred. F2/F18 startup cause remains unexplained with bounded safe failure-only observations enabled.

### Parent instrumented matrix findings (still source-frozen)

| ID | Verdict / route | Evidence and intended correction |
| --- | --- | --- |
| F19 | medium unverified / investigate | D3 personal-notes1886 fails initial tab-ready assertion with rootChildren0/documentcomplete. Shared safe diagnostics identify six script transport failures (PassagePane, WordStudy, useBible, StudiesPanel, RelevantNotes, NoteEditor), no renderer exception. This establishes failed module downloads for this occurrence, not their transport cause or equivalence to older blanks. Preserve current run/context and retain a bounded allowlisted net::ERR_* classification on future failures; no runtime retry/timeout patch. |
| F20 | medium / fixture patch | D12 anchored outline seeks word2 but setup supplies only one word (position1) and hard-coded chapter1 even for chapter2. Browser observed history anchor1; transient intended2 can be checkpointed back to the only actual rendered word. Supply a coherent chapter2 response containing actual target word2 before navigation and preserve exact word/history assertions. Current runtime reveal behavior is unchanged by native qualification; no speculative navigation patch. |

| ID | Verdict / route | Evidence and disposition |
| --- | --- | --- |
| F21 | medium unverified / investigate | workspace-restoration181 now fails desktop public-scroll checkpoint, expected anchor verse>3 but remains3. Original gesture/assertions are intact; earlier mobile occurrence had only passing diagnostics and unknown cause. Current desktop instance is preserved separately; instrument actual readiness/scroll/restoration generations and establish a cause before patching runtime or fixture. No assertion/timeout relaxation or claim that earlier cause is fixed. |

Parent ended this instrumented already-failed run by SIGINT to its verified owned Playwright child:569passed3failed4interrupted1skip591unrun14.2min/854.15s,103sources unchanged. Full log/context/interruption in browser-complete retained, despite its directory name this is NOT complete qualification. Root package manifests and observed Vite metadata hashes/mtimes were unchanged between in-progress and after observations; this does not establish the startup transport cause or whole-environment stability.

F21 controlled red establishes a runtime defect independently of bootstrap: same restored pane-0, data-ready/device-ready true and visibleheight587; wheel then top350 at322ms, releasing held initial ResizeObserver writes top76 at322ms, checkpoint445ms restores verse3. Original >3 assertion fails. Route medium/runtime patch: consume pending one-shot restore after actual gesture on measurable ready pane, using existing wheel/touchmove/keydown intent classes; preserve no-gesture restore, resize retention and original scroll assertions. Add controlled regression plus ordinary restoration checks in both viewports. This does not prove the historical desktop/mobile occurrence had the same cause. No bootstrap change justified.

F21 evidence correction: first controlled late-resize harness replayed callbacks even after ResizeObserver.disconnect, unlike the intended browser lifecycle. Candidate handler run22pass2fail55.5s preserves those reds. The earlier top350→76 diagnostic therefore does NOT yet establish a native-reachable runtime defect or the historical cause. Return F21 to medium/unverified investigation until a faithful live-observer control reproduces on unchanged runtime; remove candidate runtime handler if that cannot be established. No original assertion, timeout or failed evidence may be dropped.

F21 faithful control on unchanged pre-candidate runtime reproduced two desktop reds (wheel/primarypointer), runner13.88s, honoring observer disconnect. This supports the narrow gesture-consumption patch independently of older unknown failures. Subsequent candidate run10pass4fail53.5s retains touch/pointer diagnostic artifacts: some control gestures acted on a transient bootstrap pane with no delivered intent/height0; primary-pointer exact offset was sampled before native frame settling. These do not justify additional runtime guards. Correct only controlled fixture postrestore/measurable boundary and realistic pointer release/frame sequence, preserving >3/durable/hide oracles and the original normal test unchanged.


## Final parent disposition — bounded delivery complete

B1/B2: complete frozen native run executed2383passed/1bridge-fixture-failed/1warning1002.49s, no skips; all backend/native cases including supported artifact import/publication and supported maximum passed. The full aggregate remains historical red. B3: actual app API/fresh PostgreSQL17/browser bridge separately passed on corrected real-ID fixture and final reader source,1passed11.31s. B4: final complete desktop/mobile matrix1174passed/2expected native-only skips24.4minutes;103selected source files unchanged. B6: resource observations and supported-capacity assertions retained; pytest captured successful per-case timing, so no invented final-source timing or first-window SLA.

Final build including TypeScript passed2.82s; six owning reproducibility/contract/composition checks passed. Isolated generator still matches five current owning sources. Lint was attempted but no checks ran: system ESLint6.4.0 has no project configuration (exit2); this remains an explicit tooling gap. All exact commands, snapshots, red/green evidence and failure contexts are linked from apps/scribeswell/docs/FINAL_INTEGRATION_EVIDENCE.md. No additional runtime edits followed final verification.

F1/F3–F17/F20/F21 demonstrated fixture/runtime corrections are covered by final matrix; F21 invalid disconnected-observer proof remains withdrawn, faithful control supplies actual red/green. F2/F18/F19 startup cause remains unverified; one occurrence proves script transport failures only. Historical scroll failure identity remains unknown despite separately proved pending-restore correction. These are not relabelled root-caused.

P2 coordinated platform/app migration-report adoption remains a release gate. Fresh live Access-owner integration, standalone live-provider signup/profile, recipient/invitation and Notification owner delivery, and physical-device selection/keyboard qualification remain external gates; no shared capability or production acceptance inferred. All owned disposable fixtures stopped; KDG55481/55482 untouched. Canonical derivation passed both coherence and preservation checks with kernel/36companions/11CAP/38acceptance rows unchanged. Existing canonical/README and all other-owner working-tree edits remain outside the bounded local checkpoint.
