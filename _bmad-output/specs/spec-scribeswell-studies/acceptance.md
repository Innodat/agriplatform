# Acceptance and verification

Derived companion to [SPEC.md](SPEC.md). These are required future acceptance cases, not tests claimed to pass in the application. Stable capability IDs map to the kernel. Readiness questions identify dependencies, not permission to omit the case.

## Requirement-to-test cases

| ID | Capabilities | Observable acceptance |
| --- | --- | --- |
| ST-01 | CAP-1, CAP-9 | Anonymous reader navigates/compares and uses existing analysis. A personal action requests sign-in; the same authorized user returns to the intended passage/context without automatically confirming sharing. Protected dependency failure does not disable public reading. |
| ST-02 | CAP-1 | A verified signed-in account with no organization, employment, PtS access or administrator approval can create personal studies through the explicit account policy; current suspension checks still apply. Explicit New study with no title creates Untitled study, then unused numbered defaults. Existing-note actions reuse the active study. Rename persists. |
| ST-03 | CAP-1 | Search own/accessible shared studies by title, note text, English/Hebrew reference. Another account and revoked share have no searchable content/metadata exposure. Library return retains search/position. |
| ST-04 | CAP-2 | Type `תהילים קי:1` or `ps 110:1`; picker moves/highlights without navigating. Enter and chapter-cell click each confirm the exact verse and close; no extra confirmation button. |
| ST-05 | CAP-2 | Typed valid range preserves both endpoints; whole chapter remains whole chapter. Clicking another chapter clears the old range. Invalid/ambiguous alias/range remains editable without guessing. Psalm 2:10–13 is rejected under the corpus’s 12-verse chapter rather than accepted from an illustrative example. |
| ST-06 | CAP-2, CAP-5 | Add passage/adjusted current passage does not move the reader or overwrite existing notes; navigating does. First/last verse selection can add one verse or range without breaking word analysis. |
| ST-07 | CAP-2, CAP-3 | Matthew 26:63–64 is reference-only with notes/source link and clear unavailable-text presentation; there is no fabricated text or word highlight. |
| ST-08 | CAP-3, CAP-5 | Create general, passage and phrase notes without titles; the same note is visible from outline and relevant Notes context. A multi-passage explanation appears once in the notes-first outline. |
| ST-09 | CAP-3 | Format paragraphs/bold/italic/lists and source links; Hebrew/English direction, punctuation and caret remain usable. Malicious paste/link/markup is rejected or rendered safely; server validates the agreed representation. |
| ST-10 | CAP-3, CAP-4 | Insert a passage reference: reading opens it with that note’s existing marks, editing positions cursor and offers explicit Open. No automatic quotation, outline entry or whole-verse paint occurs. |
| ST-11 | CAP-4 | One current note owns multiple colours in Daniel and Psalms. Adding marks does not repeatedly ask for the destination; Change is explicit. Inspecting an unrelated word does not change that destination. |
| ST-12 | CAP-4, CAP-5 | Selecting a note reveals only its relevant full colours; selecting its mark opens its note. Another explanation retains independent marks. Notes with no highlights remain valid and discoverable. A corpus correction making an exact occurrence uncertain keeps the note/reference and marks the highlight Needs review; deliberate word reselection repairs it without silent retargeting, quote insertion or requiring old full editions. |
| ST-13 | CAP-4 | Native drag, Shift-click range and alternative right-click expose equivalent Highlight/Add note/Add to study actions with correct scope. Keyboard-only operation, menu dismissal/focus restoration and status announcements work. Multiword selection never borrows one word’s grammar. |
| ST-14 | CAP-4, CAP-5 | On actual iOS Safari and Android Chrome, long-press/handles select Hebrew text while OS Copy remains usable; bottom actions/palette avoid selection and keyboard controls. Tap retains ordinary analysis. |
| ST-15 | CAP-5, CAP-9 | Studies/Analysis share one panel; toggling retains editor/input and selected context, collapse returns space. Phone uses full-width tools and explicit reader return without horizontal overflow, including short landscape/visible keyboard. |
| ST-16 | CAP-6, CAP-11 | Up to four panes per tab preserve independent positions/source attribution, including Psalm 119:1 beside :176. Add reader pane + duplicates the active reference and immediately opens the new pane’s picker; cancel retains that pane/reference. Its accessible label distinguishes it from workspace-tab + and Add to study. Open here targets active pane; Open beside adds/activates a pane without passage deduplication; at capacity require explicit replacement or new tab. Current-note marks apply across that tab. Phone shows one pane with a passage switcher. Late responses from closed/inactive panes cannot change current context. |
| ST-17 | CAP-7 | Private default. Owner invites an existing or not-yet-registered recipient. Email and account-scoped in-app delivery reach the same Accept / Decline invitation; Pending invitations appears above accepted Shared with me studies and is hidden when empty. Only explicit acceptance by the verified intended account with current admission/resource rights activates view access and moves the study to the accepted list. Opening/reading/dismissing a notification or link alone does not accept or decline. Pending acceptance requires the invited verified address. Wrong account, forwarded link or canceled/expired/replayed invite grants nothing. Changing the same account’s verified email preserves an accepted share under current access rules; changed/recycled email cannot transfer it to another or recreated account, which needs a fresh invitation. |
| ST-18 | CAP-7, CAP-8 | Viewer sees author updates but cannot edit/re-share as owner through a direct API or stale control. First private response selects or explicitly creates an own destination study; later responses reuse it without a repeated chooser, and Change applies to future notes. The same response is accessible beside the source and in My studies, visible only to its owner even when the destination is already/later shared. Share explains private notes are excluded, with no first-version override. Private-note duplicates retain privacy; another reader’s study copy/search/direct API cannot expose private notes or their marks. |
| ST-19 | CAP-8 | Duplicate own note copies text/refs/all colours to same study and opens editable/current; teacher-note copy selects own destination and retains credit. Editing/removing marks in either copy never changes its source. Whole-study copy is likewise independent. |
| ST-20 | CAP-7, CAP-8 | Owner revokes/deletes source or source note changes: subsequent protected requests/search fail current source authorization, while the recipient can still find/read/edit the same private response and passage refs in its chosen own study, with source-unavailable presentation where appropriate. No inaccessible source text is exposed as a recovery shortcut. |
| ST-21 | CAP-9 | Acknowledged current input alone shows Draft saved. Simulate lost response after commit, delayed/out-of-order saves and retries; feedback stays truthful and no duplicate/competing mutation overwrites newer work. |
| ST-28 | CAP-3, CAP-8, CAP-9 | Two editors modify the same note. The stale editor pauses autosave without hiding local writing, shows Review latest, and never silently overwrites. Use latest explicitly discards that editor’s unsaved changes; Save mine as a new note explicitly preserves its branch content/highlights and private visibility. Neither action silently merges, changes the other version or repeats a copy after response loss. |
| ST-29 | CAP-7, CAP-8 | Unaccepted invitation expires 30 days after creation; acceptance checks the deadline atomically with current invitation state. Accepted sharing does not expire on that deadline. Reminders create no duplicate authority; expired/withdrawn invitation cannot reactivate through a late link or retry, and owner-issued fresh invitation is explicit. Recipient-owned notes/copies remain. |
| ST-30 | CAP-7 | Owner Share panel shows one row per person with Pending / Can view / Expired / Declined and a compact action menu: pending reminder/cancel, accepted remove access, expired/declined invite again. Pending does not claim delivery/read confirmation. Reminder reuses the invitation; Invite again creates a fresh invitation without duplicate access or revival of an old acceptance link. No separate invitation-management screen. |
| ST-31 | CAP-6, CAP-9, CAP-11 | Preserve Previous/Next chapter arrows; add no independent pane history controls/ledgers. Browser Back/Forward restores public reading arrangements/anchors without loops, phantom steps, private editor resurrection or edit undo. Deliberate passage/tab/layout actions create one step; scroll, word inspection, editing and tools do not. Legacy public URLs still work; malformed/oversize/unknown-version snapshots fail safely. Closed-tab replay follows the shared D-4 rule. |
| ST-22 | CAP-9 | While typing, bounded failed recovery shows Changes not saved/Retry without a modal. Saved close/switch is immediate. Pending/unconfirmed exit offers Stay/Close anyway or Stay/Switch anyway after bounded recovery; no rollback/offline survival promise. |
| ST-23 | CAP-9 | Same-user renewal/reauth returns authorized context; different account, sign-out, source loss and deleted destination cannot expose prior private data. Return URLs reject external targets and contain no note text/credentials. |
| ST-24 | CAP-10 | Remove highlight keeps note/other marks; confirmed note delete removes its marks; passage-list removal leaves notes/marks navigable. Study deletion removes only its owned content; removing shared library entry preserves author and own private work. |
| ST-25 | CAP-9, CAP-10 | Delete races with autosave, delayed create, duplicate and retry. Revision/editability/operation identity stop resurrection, lost updates and repeated effects; alternate write paths and database constraints enforce structural account/note/anchor ownership. |
| ST-26 | All protected | Cross-account requests, malformed identity/scope, stale JWT role claims, denied/unavailable Access and wrong service identity fail safely. Current global admission/capabilities and resource authority are rechecked; no organization/PtS grant borrowing. Private payloads, invite URLs and credentials are absent from diagnostic/error paths. |
| ST-27 | All writes | Disposable-database upgrade from supported prior schema preserves public corpus and old application compatibility; coordinated migration failure blocks activation and records partial outcomes; verified recovery follows ADR-0020. No startup migration or automatic rollback. |
| ST-32 | CAP-11 | Anonymous readers add/switch workspace tabs without sign-in. Workspace-tab + starts at the active passage with its selector open; dismiss retains that passage. Open in new tab from a reference opens it directly without a selector. Tabs retain independent references/positions; new tabs inherit study/note associations only when authorized and do not copy entities. Explicit study selection changes only that tab’s context/outline, preserving every pane’s references/positions without automatically opening study passages. Departing prior writing follows the last-context save guard; explicit note selection activates its marks. Leave study in the study menu clears only this tab’s study/current note/marks and returns its panel to the library without moving panes or deleting content; unresolved last-context writing uses the common guard. Studies rail hide/show preserves context. With none selected, omit the study label. Default tab name follows first-pane reference plus additional count; active-pane changes do not rename it. Custom Rename is stable and changes no study title. The shared panel follows the active tab/pane with clear attribution and accessible keyboard/focus behavior. |
| ST-33 | CAP-3, CAP-9, CAP-11 | The same note in multiple tabs uses one buffer/revision/save lane; typing/highlight changes propagate without a second stale save. Distinct notes retain independent lanes. Inactive/remounted views cannot overwrite newer state. Switching tabs retains unresolved work without an exit prompt. Account change clears all private contexts/lanes across all tabs. |
| ST-34 | CAP-9, CAP-10, CAP-11 | Closing a tab/pane deletes no content. Saved close is immediate; closing the last unresolved editing context follows bounded recovery and Stay/Close anyway. Other live references keep that same lane without prompting. Tab Close is hidden for the final tab. A sole pane closes its owning tab when another tab remains, applying the same last-context save guard. Pane Close is hidden only for the final pane in the final tab; alternate close commands protect the same final-reader case. Closing an active item activates the nearest surviving neighbour without resetting its passage/position. Three/four-pane layouts with tools open, overflowed tab strips, phone switchers and short/keyboard viewports remain usable. |
| ST-35 | CAP-9, CAP-11 | Refresh/return on the same device restores all open reading layouts/anchors and each tab’s selected study/note only for the verified same account under current admission/resource access. Anonymous/different accounts see no retained private labels/context/content. Outage permits reading/retry without falsely deleting remembered context; confirmed denial removes inaccessible context while preserving own responses. Explicit shared links retain their public target without importing private context. Storage denied/evicted/malformed/old version and concurrent-window cases follow the qualified D-4 contract. Restore loads acknowledged note content and never replays unsent input or consequential commands. |
| ST-36 | CAP-1, CAP-9 | From the anonymous reader header, independently open account creation or sign-in without any selected study or protected action. Complete the owner-supported registration/verification flow and return to ordinary reading, preserving public passage context. Registration alone creates no study, accepts no invite and provisions no Studies grant. The same flow from a Studies action restores only its validated intended context after verification. Existing-account, invalid/expired verification, retry, cancelled registration and safe error/return cases follow the shared authentication contract; public reading stays available. |
| ST-37 | CAP-4, CAP-9 | Anchor evidence distinguishes changed source text with reused database IDs from verified unchanged verse tokens with regenerated IDs. Exact UTF-8 combining-mark order, full verse token order, source/catalogue/versification/tokenization and observed IDs follow the shared D-2 contract. Reject incomplete/mixed publication proof and stale new selections; unavailable proof never retargets marks. Existing unchanged anchor evidence may survive a text-only edit. Synthetic digest fixtures check bytes/hashes only; actual importer/API concurrency and source publication require consuming-story evidence. |
| ST-38 | CAP-4, CAP-9 | Corpus publication closes proof before mutation, fences chapter writes to the current attempt/generation, and activates one complete audited manifest atomically with its outcome. Partial imports, interruption, failed audit and stale/alternate writes cannot publish ready proof. A coherent repeatable reader snapshot returns matching words/manifest or unavailable evidence; cached replies cannot authorize new marks. Explicit recovery fully audits; publication retry cannot reactivate an old revision. Previous public readers and ordinary note text roundtrips remain compatible under D-5 release evidence. |

ST-37 source prerequisite delivered: [source-candidate evidence](../../implementation-artifacts/spec-scribeswell-source-evidence-candidate.md)
records observed acceptance red, characterization, final 86 passing affected tests,
independent byte/hash recomputation, full-source reproducibility and review triage.
This covers encoding and source-artifact comparison only. Full ST-37/ST-38 remain
open: no actual database audit, fencing, activation, coherent API proof or private
highlight validation was implemented or qualified.

ST-37/ST-38 database-comparison prerequisite delivered separately:
[audit evidence](../../implementation-artifacts/spec-scribeswell-database-audit-candidate.md)
records final 160 passing application tests with no skips, including complete
checked-in source on disposable PostgreSQL 17, snapshot concurrency, hidden/malformed
inventory, actual role/policy checks and supervised backend timeout cleanup. This
updates the preceding source-only evidence boundary. Writer fencing, audit sealing,
activation, coherent public proof and private highlight validation remain unqualified;
full ST-37/ST-38 and D-2/D-5 are still open.

## Delivery discipline

ST-27/ST-38 dormant infrastructure prerequisite delivered:
[writer-fence evidence](../../implementation-artifacts/spec-scribeswell-dormant-writer-fence.md)
records final 321 passing application tests with no skips, 25 platform tests/42 subtests
and independently reproduced old/head catalogues. Actual fixture enforcement proves
transaction-bound context, both lock orderings, alternate writes, lifecycle cleanup,
restricted caller denial, structural/drift protection and migration rollback.
Production enforcement/caller grants, actor setup, importer transition, sealing and
publication/reader proof remain unimplemented; full ST-38 is not complete.

Observe the smallest relevant acceptance failure before implementing user-visible behaviour or cross-service contracts, then use focused TDD. Characterize existing reader/session behaviour before risky refactoring. Do not change expected results to dismiss unexplained failures.

For each delivery item, map its capability and ST cases to actual test names, exact commands and results. Cross-account/alternate-path cases need real protected API/database/service evidence; UI mocks cannot prove them. Shared-service owners must prove their contracts before the consuming story is ready. Real-device checks ST-14/ST-15 remain required alongside browser automation.

Existing verification surfaces, inspected 2026-10-20:

- Browser: `npm run test:browser --workspace=apps/scribeswell/web` for the existing reader/lexicon suite; read the package/config and add focused ST coverage before broader regression.
- Frontend: `npm run build --workspace=apps/scribeswell/web` includes TypeScript and Vite. The declared `lint` command is a verification candidate; dependency/config readiness must be checked, not assumed.
- Backend: select the affected tests under `apps/scribeswell/tests/` using an available Python environment and `python3 -m pytest`; requirements do not currently declare a complete test environment. Exact new protected-contract/DB commands remain part of Q-2’s delivery design.
- Shared sessions: existing `apps/scribeswell/web/playwright.session.config.cjs` exercises same-origin interaction with PtS; select its actual installed runner when adopting affected flows.
- Composition: `python3 tools/py/run_compose_supabase.py --check-only`. This is composition validation, not migration/cross-account/feature evidence.
- Do not use root dev/build as repository-wide verification. No root test/lint/type-check/CI command covers this feature.

## Evidence available now

### Standalone account-entry consumer delivery — 2026-10-22

The [bounded BMAD delivery record](../../implementation-artifacts/spec-scribeswell-standalone-account-entry.md)
records the observed acceptance red, focused fixes, exact verification commands,
review triage and test names. The final account-entry suite passed 62 checks across
desktop/mobile, including signup outcomes, public-only return URLs, malformed and
rejected callback cleanup, session continuity/sign-out, cancellation, modal isolation
and accessible progress. This qualifies the standalone consumer portion of ST-36
and relevant public/session aspects of ST-01/ST-23, using intercepted Auth HTTP.

Full ST-36 remains open: current owner configuration disables signup; required
confirmation, exact callback allowlist, real mail and protected Studies return
context need owner qualification. No enrollment, study, note, invitation, corpus
publication, migration or physical-device acceptance follows from these tests.
The wider evidence below remains historical prototype/design evidence.

The combined prototype was browser-checked for outline/navigation, retained editor, Hebrew typed-range/chapter confirmation, two-pane note marks, colour actions, independent duplication, reference insertion without quotation/outline membership, simulated save failure, library search, mock invitation/default-title flows and phone-width tools/actions. The user approved the journey.

This supports UX discussion only. It does not establish real authentication/admission, invitation delivery, persisted note saves, rich-text safety, restricted database isolation, concurrency/release correctness or native physical-phone selection. No feature acceptance suite or migration has been implemented or run in this specification step.

### Workspace-tabs planning verification — 2026-10-22

- `uv run .agents/skills/bmad-architecture/scripts/lint_spine.py --workspace _bmad-output/specs/spec-scribeswell-studies`: PASS, zero findings.
- Three independent architecture reviewers: [rubric](reviews/review-tabs-rubric.md), [technology](reviews/review-tabs-technology.md), [seams](reviews/review-tabs-seams.md). Draft range/replay/exit-predicate/table findings fixed; seam reviewer rechecked all four resolutions. D-1–D-5 remain open.
- `node /tmp/scribeswell-workspace-tabs-check.cjs`: PASS against the focused HTML mockup with Chromium, no page errors. The equivalent portable [check script](../../brainstorming/brainstorm-scribeswell-studies-2026-10-19/workspace-tabs-check.cjs) is retained beside the mockup for reproduction with the existing repository Playwright installation.
- Exercised three/four panes, explicit at-capacity replacement, identical-chapter separate verse panes, shared text across tabs, inherited new-tab context, tab/pane closing and last-pane defaults, Studies → Notes, Analysis passage actions, phone passage switching, last-unresolved-context Stay / Close anyway, and no page overflow at 390×844, 1100×800, 844×390 and 390×500. Four screenshots were visually inspected.
- This is illustrative coverage of ST-15/16/32–34, not application acceptance. The mockup deliberately omits authentication, private API/DB, real rich text/anchors/selection, browser history/replay and native device keyboards. ST-31 and protected save/access correctness are specified future evidence, not passed tests.

Subsequent accepted UX refinement: last-tab/last-pane Close is hidden and semantic removal is blocked. The earlier mockup checks of default-reset/recreation describe the prototype at that time and do not prove this refinement. Tab naming, optional study label and the compact + opening its new pane’s picker are also newer written requirements awaiting mockup/application coverage.

Same-device tab/layout and per-tab study/note return persistence (ST-35) is a subsequent accepted requirement. The focused mockup still resets on reload and provides no persistence or private-restoration evidence.

### Focused controls follow-up

`node _bmad-output/brainstorming/brainstorm-scribeswell-studies-2026-10-19/workspace-tabs-controls-check.cjs`: observed failure on missing Add reader pane control before the mockup change, then PASS after implementation and a Stay/menu-dismissal correction. Covers compact pane/tab + with picker cancellation, default/custom naming, final-item Close protection, Leave study/library with retained passages and cleared marks, explicit note activation, shared note text, four-pane capacity, mobile views and last-context Stay / Switch anyway. No page errors; six screenshots generated and inspected for the relevant layouts. The earlier workspace-tabs-check.cjs entry point delegates to this current suite.

This supersedes the earlier statement that those controls awaited mockup coverage. Same-device persistence (ST-35), real typed picker/native word selection, public history, authentication/access and actual saves remain unimplemented in this mockup; its resets-on-reload notice remains accurate. No live app changes or feature acceptance claimed.

Last-pane refinement: closing a sole pane now delegates to tab closure when another tab exists; only the final pane of the final tab is protected. Updated focused-controls assertion first failed (0 Close controls instead of 1) before the mockup change. Earlier statements protecting every sole pane are superseded.

### Anchor-evidence design verification

- `python3 /tmp/study-anchor-evidence-planning.py`: PASS, six synthetic digest vectors and 37 unique ST IDs, local links/whitespace.
- `node /tmp/scribeswell-anchor-fixtures-check.cjs`: PASS, independent JavaScript compact-JSON/UTF-8/SHA-256 recomputation agrees with all six Python-derived vectors. Checks reused IDs with changed text, regenerated IDs with unchanged tokens, insertion and exact combining-mark order.
- Source/schema/service/importer inspection established the current gap; no importer, schema, API or application test was changed or run. These fixtures qualify a proposed encoding only. ST-12/ST-37 still need actual source-publication, API validation and concurrent-import acceptance before highlights are implemented.

### Corpus-publication proposal verification

`python3 /tmp/scribeswell-publication-contract-check.py`: PASS, 11 capability IDs,
38 unique acceptance IDs, canonical companion discovery and local links/whitespace.
Coherence/preservation check retains chapter transaction boundaries, exact anchors,
source-outage versus change, unchanged-anchor text saves and public/private release
separation. The proposed manifest, update gate, fenced source mutation and repeatable
reader evidence are documentation only: no source data, migrations, grants, API or
importer changed; no publication/DB/release acceptance case has been run.


ST-38 input-qualification prerequisite delivered separately:
[publication command evidence](../../implementation-artifacts/spec-scribeswell-publication-command-input.md)
records strict immutable begin/recover/seal envelopes and full raw-source requalification,
including negative actor/time/ready overrides, exact attempt identity retention,
source candidate/audit rejection, safe errors and dependency/I/O isolation. Preparation
does not execute a command, verify an actor, create a receipt, seal a database or
publish source evidence. Full publication/controller/reader acceptance remains open.


ST-27/ST-38 dormant-controller prerequisite delivered:
[controller evidence](../../implementation-artifacts/spec-scribeswell-dormant-corpus-controller.md)
records actual begin/recover/seal, current-authorized original outcome replay, protected
executor custody/history, new input adoption, all seal identity checks, atomic failure
rollback, both revocation/writer orderings and competing transition qualification.
Final root full614 and focused136 tests pass without skips; the four restored response
shape cases ran in the focused suite after full collection. This is dormant fixture
qualification only: no production actor/caller/enforcement, active migration profile,
sealed full audit, manifest or reader proof. Full ST-38/D-2/D-5 remains open.


Supervised corpus invocation is locally implemented and qualified; see
[the supervisor contract](corpus-publication.md#supervised-invocation-contract--implemented-locally)
and [delivery evidence](../../implementation-artifacts/spec-scribeswell-supervised-corpus-invocation.md).
Root full Python regression passed698/no skips, affected acceptance367/no skips,
and platform deployment25 tests/42 subtests. Eight review findings were resolved;
no deferrals. This closes bounded transport/original-operation reconciliation proof,
including actual committed-response loss. It does not close ST-38 or D1–D5: verified
caller/actor custody, active release profile, coordinated importer adoption, sealed
full audit/publication/reader proof and private Studies contracts remain gates.
Production enforcement remains disabled; Access/Identity and Leave/factory ownership,
standalone account creation and agreed UX remain unchanged. No browser, image,
production/provider or live-adoption verification is implied.


Prepared-controller replay is locally implemented; see
[the contract](corpus-publication.md#prepared-controller-replay-contract--implemented-locally)
and [delivery evidence](../../implementation-artifacts/spec-scribeswell-prepared-controller-profile.md).
Root full803 tests passed/no skips184.47s, including105 prepared-profile cases;
independent105-plus-four-probe run passed109/no skips24.71s. Three BMAD review
lenses corrected seven findings and refuted one using existing structural protection;
nothing deferred. This qualifies explicit native replay of already prepared0003 with
false enforcement and empty history, exact custody/ACLs, safe catalogue inspection,
caller timeout ceilings and commit-only success evidence. It neither prepares a live
actor/caller nor verifies Identity. Default CLI/host remains dormant-only. Active/history
release support, live custody, coordinated importer transition, sealed full audit/
publication/reader proof and private Studies contracts remain open; ST-38/D1–D5
are not closed. Applied references/revisions/source/importer, accepted UX and
standalone account creation are preserved; Access/KDG and Leave/factory stay owned
by their separate sessions. No browser/image/provider/production verification inferred.


Controller-history replay is locally implemented, reviewed and qualified; see
[its contract](corpus-publication.md#controller-history-replay-contract--implemented-locally)
and [delivery evidence](../../implementation-artifacts/spec-scribeswell-controller-history-profile.md).
Final root full897/no skips246.21s and focused94 history tests/no skips35.52s passed,
retaining803 prior cases. Literal10000-attempt/20000-outcome capacity, coherent
active/paused/rotated history and actual transition/writer orderings are qualified.
Three user-run independent reviews resolved eight accepted findings (one duplicate
gap) and refuted one JSON-null claim; no deferrals. Added in-bound ordering tests
detect removal of each individual guard. Current-disabled-revision receipts reject;
changed-input recovery, rotation between origin/seal, post-replay original outcomes
and real-commit/injected-ack-loss reconciliation have actual PostgreSQL evidence.
The initial885 pre-review run/thread-limit handoff is historical, not the final state.
Native validation performs no live preparation, enforcement change, Identity
verification, importer transition or publication. Operational host/live custody and
broader ST-38/D1–D5 gates remain open; agreed UX, standalone signup and separate
Access/KDG/Leave/factory ownership stay unchanged.


Operational host-profile integration is locally implemented, independently reviewed
and verified; decision178/evidence179–183 and the [current contract](corpus-publication.md#operational-host-validation--implemented-locally-reviewed)
record explicit selection, bounded worker and commit/evidence activation gating.
Pre-review full932/no skips236.49s, focused37/18.60s and platform66/42/7.55s passed.
Initial acceptance reds, prepared characterization105, affected runs and931/1 timeout-
race discovery remain historical evidence. Supervisor termination is now isolated
from native lock expiry without changing production bounds; both paths pass.
Actual host-to-worker replay, real-commit/injected-ack-loss and explicit reconciliation
are fixture evidence; no image/live Identity/production qualification is inferred.
All independent reviews returned; seven bounded findings patched, one UTF8 claim
refuted, one pre-existing stdout-buffering issue deferred. Current wire-size limits
do not bound peak buffering memory. Host migration inputs are now privately frozen
and cleaned, with real denied/paused/rotated replay coverage. Final root full944/
no skips294.43s (47new/897retained) and platform70/42/4.20s pass (evidence182–183).
Earlier932 is pre-review evidence; the exact owned fixture is stopped/removed.
This extends earlier native-only host statements; dormant stays default and native
CLI has no selector. Live owner custody/image/target, importer/writer/publication and
broader ST-38/D1–D5 remain open. Separate Access/KDG/Leave/factory ownership and
standalone signup stay.


Caller preparation now has a specified [owner handoff contract](../../../apps/scribeswell/docs/CORPUS_CALLER_PREPARATION.md),
adopted as the twentieth companion (decisions186–187). It requires full private
Identity provenance/target pairing before restricted local preparation and committed
profile qualification; copied compact receipts/digests/local custody alone do not
verify Identity. Registration may create; disposable KDG CLI is not live target
support. New mappings start disabled; existing history and actual preparation actor
attribution are preserved. That delivery was documentation only. A subsequent test-only isolated local
mapping rehearsal exercises a bounded subset; external Identity provenance and
the full live handoff matrix remain required, with no live qualification claimed.
ElevenCAP/thirty-eightST, standalone account creation and separate owner boundaries
remain; actual owner preparation/target rehearsal and D1–D5 stay open.


Caller-handoff review correction (decision188): live actor replacement is limited by
current immutable principal key/reference and Identity unique retained keys; synthetic
UUID-rotation coverage is not live compatibility. Incompatible replacement waits for
a reviewed forward change. The contract now requires explicit revisions, atomic
four-row local preparation, independently bound actual session attribution and
separate local COMMIT reconciliation (no controller operation lookup). All five
review findings were documentation fixes. The later isolated rehearsal covers local
atomicity/concurrency/failure observations only; live owner/session attribution and
complete target qualification remain required.


The isolated local mapping rehearsal now passes29new cases and the affected
prepared/history suites pass228/no skips127.55s after review (evidence194).
It qualifies disabled atomic initial preparation, exact no-op, rollback, real
backend serialization/all three lock timeouts, native replay preservation,
restricted operator execute/lookup denial and ended-session COMMIT reconciliation.
Six review evidence gaps were fixed, none deferred. The first affected run had
223passes/one retained capacity statement-timeout; isolated26 and final228 pass
without changing production deadlines or expected results. Actor/session binding
is synthetic; the helper lives only under tests. Live Identity evidence, target/
image qualification, total execution/COMMIT deadlines and production preparation
remain open. This changes no D1–D5, owner, standalone signup or UX requirement.


The [app-owned preparation tool design](../../../apps/scribeswell/docs/CORPUS_PREPARATION_TOOL.md)
is adopted as companion21 (decisions197–199). Its parser is now implemented locally;
its admission/executor portions remain specified designs.
It closes the nine-field request/immutable parser error boundary, separate private
migrator target and trusted owner admission, proposed total execution/COMMIT bounds
and original-session recovery. References/UUIDs/parser values never prove authority.
Direct connections are required for proposed execution; pooler recovery is outside
this contract. Initial reuse requires the same preparer attribution or conflicts.
The initial parser implementation has no owner/file/network/DB effects;
specified worker result wire, unproved durable evidence capture and actual fixture admission
must close before SQL effects. Live owner channel/server identity/image/target proof,
Access/KDG/Leave/factory ownership, UX, standalone signup and D1–D5 stay unchanged.
No new runtime tests or live operations were run for this documentation delivery.


The preparation request parser is now implemented locally (decision203), consuming
the adopted tool contract's first two acceptance rows. It returns immutable nested
declarations through the app namespace and directly reuses unchanged pure custody
validation. Normal code loading is separate from parse calls; no referenced file,
owner, environment, network or DB is accessed during parsing. Equal preparer/service
UUIDs are permitted declarations, never authority. Repository-only import availability
is qualified separately from future runner packaging. The earlier tool document was
design-only; target/admission/deadline/result-wire/durable-attempt/executor and live
readiness remain specified/gated. UX, standalone signup, owner boundaries and D1–D5
are unchanged. Exact commands/results/review live in the
[parser delivery record](../../implementation-artifacts/spec-scribeswell-preparation-request-parser.md).


Reviewed parser evidence (event205): focused207passes2.23s and affected pure
394passes/11native cases deliberately deselected5.98s, with207new/187retained cases.
Six independent review findings were patched, none deferred; an actual two-case
caller-exception retention red preceded its fix. The safe error clears the real
caller/decoder context; depth/import/environment/command/UUID coverage is explicit.
No DB/image/provider/native/whole-app qualification is claimed. Existing pure
custody, applied revisions and owner implementations are unchanged.


The [worker result/attempt contract](../../../apps/scribeswell/docs/CORPUS_PREPARATION_EVIDENCE.md)
is adopted as companion22 (decisions208–209). Its original documentation delivery
ran no runtime tests; the five contract-review findings were fixed. The consuming
pure codecs are now implemented (decision213/event214), preserving the existing
request parser. They validate immutable values, canonical records/hashes, exact
original request and independently expected target, phase/proof/row/session
bindings, create timestamp equality and unchanged reuse. Partial prefixes are
readable; a worker reply requires matching terminal evidence. Encoders revalidate
manual values; one safe error clears decoder and active caller context. Fixed
independent digest oracles and isolated stdlib/no-I/O checks executed.

Final reviewed codec tests (event215):212focused2.41s; independently recreated
Python3.12/pytest9.1.1-only environment212passed2.20s. Affected pure tests606passed
8.57s with11native cases deliberately deselected. Eight verified blind-review
coverage/setup findings were patched, no deferrals or post-review codec behavior
change. Exact commands/setup and intermediate environment/collection failures are
in the codec delivery record and adopted app contract. Historical207/394 parser
evidence remains historical.
Correct hashes and schemas never prove custody or acknowledged persistence;
admitted-only missing session evidence remains unknown. File journaling is not
atomic database business audit: applicable ADR0022/0025 qualification stays required
before effects. Production storage/SQL/supervision/admission, real target/image/database and
crash qualification remain open. No live operations, UX/signup/owner changes,
Access/KDG/Leave/factory implementation or D1–D5 closure is inferred.11CAP/38ST and
all22companions remain stable. Byte/depth probes with multiple invalidities prove
safe rejection, not independent coverage of redundant guards.


### Local fixture record capture — implemented boundary

Decision218/event219 close the next app-local fixture storage contract in the
adopted [attempt-evidence document](../../../apps/scribeswell/docs/CORPUS_PREPARATION_EVIDENCE.md#fixture-storage-contract--bounded-consuming-slice),
without copying its filesystem/API schema here. Trusted root fd, exclusive run
reservation, owner modes, bounded canonical prefix validation, nonblocking locks
and no-clobber file-sync/publication/directory-sync acknowledgements are implemented
only for synthetic local fixtures. Failed appends poison the writer and retain
all residue. Read-only reopening returns validated retained bytes, including an
empty reservation, never proof of the original acknowledgement or no external
effect. No resume/cleanup/replay/live admission/SQL path exists.

Actual ATDD red preceded implementation. Final72storage tests passed7.80s;
affected pure suite678passed20.15s with11native database cases deliberately
excluded. Seven blind-review timing/coverage findings were addressed, no deferrals.
First and later-record process deaths preserve earlier acknowledged bytes; stalled
sync is terminated by the test harness after readiness, not a delivered supervisor.
Exact commands, intermediate fixture failure, setup and local ext2/ext3 evidence
are in the adopted app contract and delivery record. Existing codecs/request parser
remain unchanged. Physical power-loss, production filesystem, kernel I/O deadlines,
real owner/target/image admission, atomic business audit and supervised SQL effects
remain gated.11CAP38ST22companions, agreed UX/standalone signup and separate
Access/KDG/Leave/factory ownership remain intact; no D1–D5 closure is claimed.


### Synthetic communication supervisor — implemented boundary

Decision222 and events223–224 close the app-local
[fixture supervisor contract](../../../apps/scribeswell/docs/CORPUS_PREPARATION_TOOL.md#fixture-communication-and-supervisor-contract).
It exchanges already supplied synthetic terminal declarations through a fixed
isolated stdlib child. Parent independently validates original request/target/
prefix/reply; no parent storage/owner reads, new persistence acknowledgement or
SQL occurs. Frozen `fixture_reply_validated` observations prove communication only,
including when embedded fixture labels say committed/reused. The private closed
transport and unchanged codecs retain separate ownership and meaning.

All phases charge one58work/60total/2remaining-cleanup budget from public entry;
stdin65536/stdout4096 caps apply during transfer, stderr is discarded, no final
drain/retry or public timeout/command/env/callback override. Reaping after a kill
request requires observed SIGKILL before forced-stop attribution; natural exits
in that race stay child_exited. Final total deadline is rechecked after cleanup;
unverified termination remains explicit. OS/spawn scheduling is charged on return,
not claimed hard realtime preemption.

Actual acceptance red preceded implementation. Seven blind findings were fixed,
none deferred; two behavior regressions observed red2failed1.81s then green2passed
1.81s. Final83focused6.76s and761affected15.01s with11native database cases excluded;
63/741 are pre-review evidence. Real isolated malformed/overflow/live refusal,
well-formed mismatched bindings, byte bounds/backpressure, elapsed stalls and
repeated actual forced reaping/fd stability are exercised; fake clocks verify
shared and shrinking budget arithmetic. Exact commands/setup/intermediate failures
are in the adopted tool/evidence documents and delivery record. Existing codecs,
request parser and fixture store remain unchanged. Actual storage/SQL/owner/image/
server/current authority/atomic-audit and physical crash/deadline integration gates
remain open.11CAP38ST22companions and UX/signup/Access-KDG-Leave-factory boundaries
are preserved; no D1–D5 closure or production executor availability is inferred.


Integrated fixture capture evidence (direction227/event228):152capture+legacy
supervisor checks passed12.98s;830affected pure checks passed20.87s,11native cases
excluded. Six review findings fixed, no deferrals. Real supervised append/close/
readback, first/later interruption, partial/pre-effect/reservation failures, stalled
write/sync/readback, lost acknowledgement, root descriptor lifetime and unresolved
termination are exercised. Existing83supervisor cases protect shared lifecycle
reuse. App evidence holds exact commands; no new ST/CAP acceptance or real SQL/owner/
production-durability qualification is claimed. First useful Studies save/reopen
acceptance still depends on its D1/D2 contracts, not this test count.


First ordinary-note wire acceptance (decisions231–232) is owned by the adopted
[personal-notes contract](../../../apps/scribeswell/docs/PERSONAL_NOTES_V1.md#activation-recovery-and-traceability).
Pure tests exercise create/value-preservation/reopen DTOs, strict malformed/forged
input, bigint revisions, Unicode, node/link/byte bounds and generated-schema agreement.
They are partial CAP-1/CAP-3/CAP-9 evidence; no new ST/CAP IDs or completed protected
save/reopen claim. Native authorization/ownership, atomic aggregate+receipt writes,
no-op/replay/concurrency, pool/RLS and browser-generation/failure behavior must still
be observed in the consuming implementation. D1–D5 remain open.
Final wire evidence (event233):129 affected tests passed3.55s (123 new contract,
6 existing reader/morphology), one database-lifespan HTTP test explicitly excluded
after an interrupted stalled attempt. All10 blind findings addressed, no deferrals;
real red preceded schema/host fixes. Generated OpenAPI/DTO parity uses independent
JSON Schema validation. No database/current Access/browser journey was exercised;
the protected save/reopen acceptance remains open.

Decision236 reconciles Access owner delivery f02bf84b1a3d3281fb06e91aba01f0057216511c:
[owner evidence](../../../services/access/STUDIES_ENROLLMENT_EVIDENCE.md) reports143
focused tests/49subtests plus corrected-source native enrollment/check qualification.
These are owner-run results, not rerun here. Full-regression timeout, initial ATDD
chronology limitation and unexplained seven-request exploratory failure remain disclosed.
Personal account checking is now consumable; recipient/invitation protocols and live
activation remain open. Direction237 plans the complete app persistence/API/UI slice;
no new app runtime, tests, migration execution or release acceptance has happened.


## Ordinary-note runtime evidence

Event239 records the implemented opt-in enrollment/create/write/reopen subset. The [delivery record](../../implementation-artifacts/spec-scribeswell-personal-notes-runtime.md) maps every frozen acceptance row to executed native or browser tests and retains earlier failures and completed review corrections. This supports ordinary owner-note behavior only; full feature stories, production/live-owner and physical-device acceptance remain open.

## Actual local owner integration evidence

Event247 records fresh run41b8351e-bcc4-4128-ac22-d7ef3dc561b3: both actual-provider browser scenarios pass, with independent SQL before enrollment, after a read-only current check, after write/reload/isolation and after protected disable. All six frozen integration rows have executed native or focused coverage; parent reran11 focused controls successfully. The [integration evidence](../../../apps/scribeswell/docs/STUDIES_OWNER_INTEGRATION_EVIDENCE.md) maps rows to commands/results and preserves every earlier preparation/browser failure. Three failures in the broad six-worker browser invocation remain disclosed; unchanged isolated retries passed, so no full broad-regression pass is claimed. Event250 records all13 findings addressed without deferral and the final patched-source native pass. These results extend partial CAP-1/CAP-3/CAP-9 evidence; they do not complete all feature stories, standalone signup, default startup/readiness, production, physical-device or wider D1–D5 acceptance.

Final review qualification (event250) uses fresh run21c6a0b8-957b-4623-9462-fabd63264275:222 unchanged sources, actual enrollment/create controls, complete row equality around foreign/disabled requests, both account bindings and study/note/receipt actors, anonymous post-disable reading and confirmed owned-group termination. All13 findings addressed in12 distinct groups; no deferrals. Parent170 affected tests,56 owner characterization,12 retained session checks20.7s, build/generated/helper/composition pass. The earlier broad203/3 remains disclosed. Default startup, signup, production/release, devices and wider feature acceptance remain open.

Events258–260 qualify the implemented ST-02 title subset with native13 and focused browser26 passes plus real-owner run c948174c: UI rename/reload and independent SQL preserve notes/creation attribution and exactly one receipt; foreign/disabled operations fail safely. The [delivery matrix](../../implementation-artifacts/spec-scribeswell-study-rename.md) retains all seven rows. Broader browser/session timeouts remain disclosed; final browser94/session12/native13 and real-owner proof passed after independent review corrections (event263). No manual, signup, physical-device or production acceptance is claimed.


## Collected passages — component implementation, integration pending

Direction266 authorizes proceeding through agreed slices and defers integration
testing to the end. The [collection delivery matrix](../../implementation-artifacts/spec-scribeswell-collected-passages.md)
covers catalogue/picker, stable collection, explicit Open, notes/reader preservation,
conflicts/retries and access/navigation safety. Events271–272 record implemented
opt-in code, executed component checks and independent review corrections; event275 records final226-browser/226-Python component passes. Prepared17 native cases and actual-owner
UI/SQL tests do not count as executed proof. ST-04–06 and wider requirements remain
partially qualified until final integration and relevant human/device acceptance.

## Passage links — designed next slice

Event277 and the [note-link matrix](../../implementation-artifacts/spec-scribeswell-note-passage-links.md)
define bounded CAP-3/ST-09–10 insertion and Read/Edit navigation, strict format2,
prior-editor downgrade refusal, same-lane/context retention and original-operation
recovery. Event282 adds executed component matrix, frozen216-case note regression before minor
audits, focused corrections and isolated baseline-format checks. Review/final regression
and native-owner proof remain pending. Existing
highlight rendering, private/shared contexts, physical devices and release gates stay
open. Final native/actual-owner testing remains deferred by direction266.

Event284 completes independent note-link reviews; direct editor corrections and
coverage additions are in progress, including native Undo/Redo preservation. Existing
component milestones do not qualify the pending final patched source or integration.

Event286 designs the own-library ST-03 subset only. Beyond-first-page discovery,
English/Hebrew references, saved formatted text, query races, retained pagination/position
and owner isolation require future component/native evidence. Shared search remains
gated. Note-link full312 run passed310 and found two Backspace regressions; correction
and final patched-source verification remain pending, with expectations unchanged.

Event289 supersedes the pending corrected-source milestone with324passing browser
and249Python checks. One-step Backspace expectations were preserved and the earlier
310/312 failure remains evidence. This closes the bounded component checkpoint only;
native18cases, owner/session, prior-release activation and physical devices stay pending.
Event288 makes the next own-library search plan ready, without search runtime evidence.

Event292 adds initial in-progress own-library evidence (first browser red, then2
retained-depth browser and207affectedPython/build passes). Expanded matrix, parent
review/final regression and database/owner semantics remain pending. No full ST-03
closure is inferred; API-red chronology gap is retained in the delivery record.

Event296 records296 passed intercepted desktop/mobile notes tests with2 expected
native-browser skips,277 affected Python passes and24 focused search passes after
tests-only401/400/damaged-reference additions. These qualify component behavior,
not PostgreSQL semantics or real-owner authority/zero mutation. The API-red chronology
gap and interrupted runs remain disclosed. Independent review, native/owner/session
integration, shared search, physical devices and broader ST-03 acceptance remain open.

Events298–300 preserve search review-correction status (36 focused browser/152
contract passes, final source-frozen component run pending) and adopt the next
[own-note deletion design](../../../apps/scribeswell/docs/NOTE_DELETION_V1.md).
Dedicated note.delete uses revision/lifecycle locking, atomic empty-value erasure
and minimal retained evidence; only its original receipt resolves after closure.
Confirmation coordinates the existing save lane and never repeats after sign-in.
Controlled0004 constraints and native/owner proof are preparation only; no deletion
implementation, migration or production mutation is claimed. Whole-study deletion
and all broader ownership, copy/privacy and final-integration requirements remain.

Event302 records the parent full search regression:359passed/1mobile scroll-return
failure/2expected native-browser skips9.6min on unchanged140-file source. Focus
restored but scroll became0; the original assertion remains and P2 correction is
in progress.277 Python/build/repro checks passed. This is not overall component
qualification; search checkpoint and next note-deletion implementation wait for
the correction. Native/owner/session/device/production gates remain unchanged.

Event307 supersedes the pending corrected search component run:368 browser passes/
2expected native-browser skips,277 affected Python passes, build/reproducibility
checks passed on unchanged140-file source. All17 actionable findings corrected,
P5refuted; earlier359/1/2 failure and chronology remain in app evidence. Native20
collected/syntax only, actual matching/permissions/owner/session proof still pending.
The delivery stays in-review for final integration; next own-note deletion is ready
design only. No broader requirement or release/production gate is removed.

Event309 preserves search as localc8a56681ba3eec7d104f4aab951b2e66195bb0e9,
component-verified but in-review for final integration. The next own-note deletion
implementation is dispatched against that baseline and adopted contract; no runtime
or test result for deletion is claimed yet. Other product/owner/qualification
requirements and the deferred final native-owner-session phase remain unchanged.

Event313 records implemented own-note deletion with36 focused desktop/mobile and244 affected Python passes, build/generated checks and parent implementation-audit corrections. Independent reviews are in progress and broad component regression remains pending. Native22 and owner fixture/control42 cases are collected/syntax only; no migration, owner/session execution or final qualification. Earlier runnable failures and intermediate runs remain in app evidence. Whole-study deletion and all broader requirements remain.

Events321–322 qualify own-note deletion component checks:418 desktop/mobile browser passes/2 expected native skips,297 affected Python passes/build/generated checks; local f6b33ac6fb20a433f7b3ed72af82f9b8bc6694be (25 scoped paths). Native23 collected only; actual-owner/session/migration qualification remains final-phase and delivery in-review. All failed intermediate runs, original storage-unit-red chronology gap and13 corrected actionable findings remain in app evidence. Whole-study deletion is next planning, unimplemented; all wider requirements remain.

Event327 records whole-study deletion as partial implementation under the [adopted contract](../../../apps/scribeswell/docs/STUDY_DELETION_V1.md): observed route/DTO/storage/action reds precede initial6backend/2browser passes. Expanded target-lane/account/late-response matrix, parent audit, independent review and final component checks remain pending. Prepared0005 is unexecuted; final native/actual-owner/session qualification remains deferred. All wider requirements and existing component limits remain.

Event329 records implemented whole-study deletion with50 focused desktop/mobile and335 affected Python passes, build/owning checks and parent25-path diff/matrix audit. Three independent BMAD reviews are running; broad notes/reader regression remains pending. Native26 cases are collected/syntax only and actual-owner/session/migration execution stays final-phase. Earlier failures/corrections remain in app evidence; no wider capability or release readiness is inferred.


Events333–334 retain whole-study deletion component335 Python/build passes and13 review findings/11 corrected roots. Full browser488 passed/2 expected native skips/2 host-timing assertions failed; controlled-clock6 passes now prove total deadline/late-result behavior, full rerun pending. Native32 collected only. The adopted [four-pane public contract](../../../apps/scribeswell/docs/FOUR_PASSAGE_LAYOUT_V1.md) closes bounded implementation choices, not runtime qualification: stable1–4panes/publichistory, separate mounted writing, explicit capacity replacement and responsive geometry. Tabs/per-tab metadata/durable restoration and all wider requirements remain; dispatch follows deletion checkpoint. No owner/native/session/device or activation claim.


Event342 records four-pane implementation and parent audit in progress, not final qualification. Genuine missing-Add outer red preceded UI; initial helper-unit-red/wider pre-refactor characterization gaps remain. Intermediate frozen public/matrix runs passed; later78-case selection77passes/1mobile position failure is retained while startup/seek corrections are checked. No independent review or final full-browser result yet. Whole-study deletion checkpoint/event337 remains qualified separately. Tabs/restoration/highlights/copies/sharing/private responses and all wider requirements remain; native-owner-session/device/release stays final-phase.

### Four-pane component qualification — event353

CAP-6/ST-16/ST-31/ST-34 bounded public-layout behavior passed686 component-browser
checks with2 expected native-browser skips across all five suites,13.5min; final
build passed. [Exact evidence](../../../apps/scribeswell/docs/FOUR_PASSAGE_LAYOUT_EVIDENCE.md)
maps transitions, original/repair reds,16 triage rows/12 addressed roots and frozen
160-source manifest. It retains failed/interrupted attempts, the older unexplained
initial-position occurrence and original method-ordering gaps. No complete capability,
native SQL/owner/session, physical-device, live signup or release acceptance follows.
Tabs/private associations and same-device restoration remain subsequent work.
