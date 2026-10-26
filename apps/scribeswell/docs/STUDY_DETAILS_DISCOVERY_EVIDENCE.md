# Study details and own-note discovery component evidence

[Adopted app contract](STUDY_DETAILS_DISCOVERY_V1.md) implements optional study
introduction/source, complete explicit metadata saving and bounded own-note passage
discovery. Parent owns independent review, final verification and canonical status.
No native SQL, migration/grant execution, live owner calls, native test collection,
KDG ports, deployment or push occurred.

| Requirement | Evidence |
| --- | --- |
| Compatible create/details, exact null clearing, safe Unicode/URL | `test_study_details_discovery.py`: complete and nullable DTO, unsafe URL/NUL/length refusals, explicit-field, scalar and closed-context cases. D1/D5–D7/D14 cover whole forms, candidate recovery, conflict/current read and original-operation unknown retry. |
| Old create receipts and independent title writer | Synthetic old canonical receipt replay includes old title/null semantics and absent optional fields; explicit null differs. Existing rename desktop/mobile tests pass apart from the captured status collision, whose focused rerun passes. Native prior-writer/title/delete cases are authored only. |
| Revision/no-op/attribution/copy | Component storage locks/no-op/conflict/attribution; whole copy persists exact details and counts metadata in canonical bytes. Dedicated native copy/migration/permission tests are syntax only. |
| Private pre-limit context query | Context SQL uses existing guarded paragraph/reference overlap helpers. Component cursor account/reference binding and projection/bounds pass. Actual SQL privacy, ordering, deduplication and pagination remain unexecuted. |
| Inspection vs current note/Open | D2–D4 keep writing usable, Preview does not change editor/destination/URL, explicit Open uses the departure guard and exactly one navigation. D8/D9/D11 cover late tab reads and authority loss. |
| Outline/reference and source-occurrence reveal | D10 preserves a visible relevant passage and navigates once when absent; D12 carries the source word occurrence in that same history command. D13 confirms independent note autosave during unsaved details editing. |
| Restoration compatibility | Parent-directed fixture correction adds only required `visibility:'study'` to `workspace-restoration.spec.cjs` ownedNote. Exactly eight previously failing held Rename cases pass; all expectations and timing remain unchanged. |

All logs below are in [evidence/study-details-discovery](evidence/study-details-discovery/).

- `atdd-red-escalated.log`: runnable backend acceptance red,2failed/5passed,
  missing details decoder and PUT405, before backend implementation.
- The first sandbox HTTP run stalled at `F.....` and was interrupted. Escalated
  hermetic TestClient runs complete. A combined rewrite+escalated-test command was
  rejected automatically before executing; reviewable workspace patches and separate
  test escalation were the safe authorized alternative. No native mutation was tried.
- `metadata-green.log` and `component-green.log`: new metadata/route/storage/context
  checks pass after implementation. Storage inner tests were authored after the outer
  red; they are not represented as an independently observed preimplementation red.
- `browser-red.log`: selector matched no tests. `browser-red-ui.log`:2failures,
  missing Relevant own notes region and source-link absence. Metadata UI was already
  being implemented, and the source-link failure was an incomplete HTTP fixture; only
  the missing relevant region establishes the frontend behavioral red.
- `browser-initial-green.log`:4desktop/mobile passes. `browser-matrix.log`:
 4passed/10failed. Corrections addressed a real double exit prompt after deliberate
  abandonment, textarea accessible-label instability, and the fixture's wrong tab
  control name. `browser-matrix-corrected.log`:14passed,17.7s.
- `application-python.log/json`:302passed,3.16s, explicit node IDs from nine app-only
  modules; database/native environment and PYTEST_ADDOPTS cleared. The first run was
 301passed/1failed: old StudyPage round-trip gained null optional fields. Nullable
  fields now default to None while absent/null serialized read fields remain omitted,
  preserving compatibility without changing that old assertion. The runner overwrote
  its first raw file; the failing assertion and301/1 result remain in tool history
  and this chronology (raw-log retention gap).
- `browser-navigation.log`:10passed,12.1s; D3/D10–D12 desktop/mobile.
- `browser-affected.log`:59passed/9failed,1.8m. The grep also selected restoration
  tests. Eight failed before their action because ownedNote omitted required study
  visibility; baseline47529be already required it in readableNote. One mobile dirty
  rename case encountered a newly added loading status alongside Draft saved.
  Context loading now uses polite live feedback, retaining unique note save status.
- `browser-affected-focused.log`:6passed/2failed,14.3s; dirty rename and D13/D14 pass,
  two unchanged restoration startup assertions still fail. Parent explicitly directed
  the valid wire-fixture correction. `restoration-fixture-corrected.log`: exactly
 8previously failing held Rename restoration cases pass,12.8s.
- `component-final.log`:18passed/1failed. The new10000supplementary-scalar candidate
  used120KiB escaped JSON, exceeding the existing65KiB framing limit. Encoding that
  candidate as actual UTF-8 preserves the scalar assertion within the body bound;
  `scalar-fixture-corrected.log`: that one node passes. No broader rerun was done
  after parent asked to restrict checks; parent owns final combined qualification.
- `final-checks.json`: Scribeswell build, owning OpenAPI/catalogue, pinned isolated
  TypeScript generator and database-helper reproducibility checks pass. Build retains
  the existing large-chunk advisory. The sandbox generator child spawn failed;
  separate normal escalation succeeded. These checks precede the final feedback-text,
  fixture and authored migration-close compatibility adjustments; parent verifies the
  final source. No root build/test claim is made.

Exact browser commands are retained in each npm/Playwright log. Application argv and
final owning-check argv/results are recorded as JSON. `source-hashes.json` records the
baseline47529be and an intermediate after snapshot; `source-hashes-final.json`
records the final implementation handoff. No unchanged-source claim spans patches.

Seven dedicated native cases and the shared fixture's additive0008 failure/retry
path are authored only. AST syntax parsing does not establish SQL, permissions,
transaction rollback, native device behavior, actual Identity/Access, release safety
or production readiness.0008 is forward-only and includes a compatible BEFORE-close
clear plus closed-row constraint so previous title-only deletion SQL erases additive
private details. Existing migrations/generated ownership remain intact.

Historical anonymous mobile-scroll and startup/return failures remain disclosed in
the prior own-highlight/copy/restoration evidence; no assertion was changed to dismiss
them. Scaffold/shared UI/agent context/ADR impact: none; app-owned documentation and
runtime only. Shared recipients/notifications, sharing and private responses remain
gated. Public reading and existing notes/copies remain independent.

## Independent review corrections

The reviewed implementation now activates a relevant inactive pane when it is hidden
by the single-pane layout, preserving that pane's existing reference/position and
using normal history replacement. Already-visible relevant panes remain unchanged.
Direct Preview retry retains the inspected study/note identity; confirmed unavailability
removes the inaccessible row and offers Close rather than an impossible Retry. Current
note autosave revision is removed from contextual read identity, preserving unrelated
preview and pagination. Account/tab/pane/reference/tool/current-selection guards remain.
Details Save/Cancel restores the Edit study details trigger under the existing origin
conditions. Unknown study creation freezes its complete visible candidate and names
its original-operation retry; definitive input refusal remains correctable.

`review-malformed-red.log` observes the malformed matching sibling poisoning discovery
with ValidationError. `review-malformed-green.log` passes three focused component
cases after the existing DTO validator is reused to skip only invalid candidates in
the bounded raw SQL page. Continuations use the last raw scanned row, including when
no readable items remain; no unbounded refill query is performed. The browser's empty
page wording and More action preserve truthful pagination. Actual SQL proof remains
final-phase. Two native malformed/unsupported neighbor cases plus three metadata
replace races (rename, delete, coherent whole-copy snapshot) are authored; only AST
syntax was checked. There are now twelve dedicated native cases including parameters.

The discovery browser fixture now asserts complete canonical request references and
models one note with both its originating and additional passage. D3 therefore keeps
already-visible Genesis1/no additional history after explicit Open; D10/D12 retain
absent-reference navigation coverage. R6 asserts the complete initial canonical
chapter and the new canonical verse reference after deliberate navigation.
`review-browser.log` passes26desktop/mobile cases,28.7s, selected only from the
changed personal-notes suite: R1–R7, D3, D10 and D14. This covers hidden-pane reveal,
direct Preview retry/unavailable Close, details focus, independent successful autosave,
frozen unknown create, canonical requests and empty-page continuation. The existing
unknown-create test now expects the deliberately readonly original candidate; its
same-operation/payload and one-result assertions are unchanged. Its two viewport
results are in `review-create-existing.log`. No broader verification was run during
these corrections; parent owns full verification and final source qualification.

B1 outline truncation and B5 preview-ID mismatch were refuted by the existing caller
and api.note validation; neither received an unrelated patch. Prior failures and
historical/native/device/release limits above remain unchanged. Final review handoff
hashes are in `source-hashes-review-final.json`.


Parent independent final checks:310application tests passed3.17s;44affected
desktop/mobile cases passed55.8s;18review regressions passed23.5s. These are separate
runs on the same191 selected source hashes, not a fabricated single browser run.
Build/OpenAPI/reference catalogue/pinnedDTO/database-helper checks passed.
Exact commands/results and unchanged source pairs: parent-results.json,
parent-review-results.json, parent-{before,after}.json and parent-review-{before,after}.json;
raw parent-*.log retained. Isolated generator's four source modules and transitive
scaffold-install.ts were byte-identical to repository source.

A later parent suspected abandoned-input race was refuted: editorLanes excludes
abandoned lanes and NoteEditor renders only that list, so the source editor unmounts
before the claimed new interactive input. No runtime change, synthetic event
manufacture or unnecessary test was made. Original trace and correction remain in
review triage. Native tests remain authored/AST-only; actual PostgreSQL, owners,
standalone signup environment, physical devices and release remain final gates.

Final characterization addition: parent independently passed2desktop/mobile R8
normal-UI cases3.9s proving the source editor is unmounted and original unknown
operation/payload remains recoverable while destination read waits. Only R8 was
appended: removing that exact suffix reproduces the previous test-file SHA;
all190other selected hashes (including runtime/contracts) remain identical.
parent-refutation-before/after/results.json and .log retain this distinct snapshot.
No prior test assertion or runtime changed; no repeat of the44/18 matrices.
