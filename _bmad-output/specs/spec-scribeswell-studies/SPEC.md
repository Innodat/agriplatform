---
id: SPEC-scribeswell-studies
companions:
  - ux-behaviour.md
  - acceptance.md
  - brownfield.md
  - ARCHITECTURE-SPINE.md
  - account-access.md
  - data-and-saving.md
  - ../../../apps/scribeswell/docs/PERSONAL_NOTES_V1.md
  - ../../../apps/scribeswell/docs/PASSAGE_REFERENCES_V1.md
  - ../../../apps/scribeswell/docs/NOTE_REFERENCES_V1.md
  - ../../../apps/scribeswell/docs/LIBRARY_SEARCH_V1.md
  - ../../../apps/scribeswell/docs/NOTE_DELETION_V1.md
  - ../../../apps/scribeswell/docs/STUDY_DELETION_V1.md
  - ../../../apps/scribeswell/docs/FOUR_PASSAGE_LAYOUT_V1.md
  - ../../../apps/scribeswell/docs/WORKSPACE_TABS_V1.md
  - ../../../apps/scribeswell/docs/WORKSPACE_RESTORATION_V1.md
  - ../../../services/access/STUDIES-ENROLLMENT.md
  - corpus-publication.md
  - reader-interaction.md
  - ../../../apps/scribeswell/docs/CORPUS_CALLER_PREPARATION.md
  - ../../../apps/scribeswell/docs/CORPUS_PREPARATION_TOOL.md
  - ../../../apps/scribeswell/docs/CORPUS_PREPARATION_EVIDENCE.md
  - ../../../platform/docs/architecture/contracts/scribeswell-study-enrollment.md
  - ../../../platform/docs/architecture/contracts/notification-delivery-and-account-inbox.md
  - ../../../platform/docs/architecture/decisions/0006-common-notification-capability.md
  - ../../../platform/docs/architecture/decisions/0001-fastapi-openapi-api-boundary.md
  - ../../../platform/docs/architecture/decisions/0019-current-server-side-authorization.md
  - ../../../platform/docs/architecture/decisions/0020-safe-schema-changes-and-release-recovery.md
  - ../../../platform/docs/architecture/decisions/0032-session-recovery-and-return-navigation.md
  - ../../../platform/docs/architecture/decisions/0047-public-access-and-launcher-visibility.md
  - ../../../platform/docs/architecture/decisions/0050-inline-draft-save-failure-and-exit-confirmation.md
  - ../../../platform/docs/architecture/decisions/0051-saving-conventions-by-workflow.md
  - ../../../platform/docs/architecture/decisions/0053-capability-scoped-access-in-mixed-scope-applications.md
sources: []
---

> Derived by bmad-spec from its append-only decision log and cited source material. Update through bmad-spec and re-derive. This SPEC and its companions are the feature contract; existing platform decisions retain their authority. The UX direction is agreed. The implementation gates below remain open.

# Scribeswell studies

## Why

Scribeswell readers need to preserve their own explanations, questions and connections across biblical passages, then rediscover the exact text behind them. Add personal and shared studies to the public Hebrew/Aramaic reader without turning ordinary reading into a login-required activity. Self-study is primary; capturing and revisiting a lecture is a supporting journey.

## Capabilities

- **CAP-1**
  - **intent:** Readers can create, name, find and reopen personal studies and discover studies shared with them.
  - **success:** Every verified signed-in reader can reach personal study creation without administrator approval, organization membership or PtS access. Explicit creation allows a supplied title or an unused numbered “Untitled study”; authorized search finds studies by title, note text and passage reference in My studies or Shared with me.
- **CAP-2**
  - **intent:** Readers can collect and revisit passage references without interrupting the text they are examining.
  - **success:** Chapter, verse and range references work through English/Hebrew entry or browsing; adding preserves the reader, opening navigates, and unsupported text remains a usable reference with notes. The exact picker contract is in the UX companion.
- **CAP-3**
  - **intent:** Readers can write and revisit explanations at study, passage or selected-phrase level.
  - **success:** One note is accessible from its study and relevant text context, supports the agreed lightweight writing tools and reference links, and requires no title. Inserting a reference does not quote text, add a passage-list entry or highlight scripture.
- **CAP-4**
  - **intent:** Readers can illustrate one explanation with several coloured highlights across chosen passages.
  - **success:** A visibly current note owns its highlights and colours across passages; ordinary word inspection does not change that destination. Selecting a note reveals its marks and selecting a mark opens its note; notes may have no highlights.
- **CAP-5**
  - **intent:** Readers can move between scripture, study organization and analysis without losing working context.
  - **success:** The notes-first outline shows each note once; switching the shared Studies/Analysis tool preserves editing context. The desktop and phone arrangements in the UX companion keep reader and tools usable without competing sidebars.
- **CAP-6**
  - **intent:** Readers can compare up to four passages while keeping explanations and analysis attached to their actual source text.
  - **success:** Up to four independently navigable passages per workspace tab retain positions, show the current note’s relevant marks and correctly identify selection origin; phones switch passages instead of squeezing them into columns.
- **CAP-7**
  - **intent:** Owners can give named recipients view access to a private study and remove that access.
  - **success:** Email and account-scoped in-app notifications reach the same invitation with Accept / Decline; pending invitations appear above accepted Shared with me studies, hidden when empty. Invitations can await first sign-in but activate only after explicit acceptance by the verified intended account under current admission/resource rules; forwarding a link or opening/reading/dismissing a notification grants nothing. Acceptance adds the study to the accepted list. Viewers follow the author’s updates without gaining edit rights.
- **CAP-8**
  - **intent:** Readers can develop private responses to shared work and make independent, attributed copies.
  - **success:** Private responses remain separate from author content, shown alongside it and in an own study chosen once per shared study; the reader may create “My notes on [study]” or select an existing destination. Study copies and Duplicate note retain source credit and do not synchronize. A duplicated note includes text, passage connections and all highlight colours. Own responses remain accessible in their own study after the original becomes unavailable.
- **CAP-9**
  - **intent:** Readers can preserve unfinished writing and recover from interruptions with truthful feedback.
  - **success:** Acknowledged input shows Draft saved; unconfirmed saving uses inline Retry and exit-only confirmation. Current identity, permission, revision, lifecycle and retry checks prevent cross-user disclosure, stale overwrite, duplicate effects and deleted-note resurrection.
- **CAP-10**
  - **intent:** Readers can remove their own content without unexpectedly destroying other work.
  - **success:** Highlight removal keeps the note; confirmed note/study deletion removes its owned content; passage-list removal keeps notes and marks; removing a shared library entry deletes neither author content nor private responses.

- **CAP-11**
  - **intent:** Readers can keep several reading setups open without losing their place or writing.
  - **success:** Public workspace tabs each retain up to four independent panes and their own study/note associations. New tabs inherit current associations without copying records; one shared tool surface follows the active tab/pane. Closing a layout never deletes studies or notes, and one per-note edit lane serves all tabs. Same-device refresh/return restores open layouts and positions, plus each tab’s selected study/note only after verifying the same account and current resource access.

## Constraints

- Public reading and existing analysis remain anonymous-capable and independent of protected discovery outages. The public reader exposes standalone sign-in/account creation without requiring a Studies action; registration does not create a study or accept an invitation. Personal study eligibility is open to every verified signed-in reader without administrator approval, organization, employment or PtS prerequisites; Consume Access’s delivered account-scoped enrollment/current-check policy; its release opt-in remains separately qualified. Current admission/capability, suspension and application resource checks remain mandatory. Launcher eligibility is unchanged.
- Scribeswell owns the study domain and FastAPI/OpenAPI boundary. Browser Supabase access remains authentication-only unless realtime is separately approved; shared runtime capabilities are consumed through their owners’ HTTP contracts. Preserve the corpus, lexical source identities and existing reader/session behaviours.
- Notes own optional highlights; studies organize notes and references. Reference links, passage-list entries and word highlights are distinct relationships. A colour does not carry a prescribed theological or semantic meaning.
- Private responses remain owner-only even inside an already/later shared destination study. Ordinary notes follow study sharing; first-version private responses have no sharing override, and copying must not silently change their privacy.
- Personal working notes autosave without a submission/publish workflow. Sharing and deletion are separate authorized actions. Follow the adopted saving, session-recovery and lifecycle decisions; do not promise offline persistence, rollback or survival of unsent input.
- Protect rich text, stable text anchoring, account/resource isolation, current authorization, actor attribution, safe errors and sensitive diagnostic fields. Exact write/identity contracts must resolve Q-1–Q-3 before their consuming implementation.
- Keyboard, mixed Hebrew/English and touch interaction must meet the UX/acceptance companion. Desktop-width emulation is not evidence that native phone selection or its keyboard works.
- Controlled migration, previous-version compatibility, activation-on-success and recovery evidence are required before release. Existing ADRs are immutable; this spec changes no grant, schema or release state.

## Non-goals

- Tags, collections, folders, named-group administration, collaborative editing or discussions.
- Public/bearer sharing links, more than four panes per tab, arbitrary docking/nested tabs, saved layout libraries, cross-device workspace synchronization or disconnected Ctrl-click word selections.
- A separate Copy highlights action; use Duplicate note instead.
- Insert selected text, automatic phrase quotations or automatically painting verses merely mentioned in a note.
- Attachments, full offline editing, New Testament/translation corpus expansion or a new authentication provider.
- Changed launcher eligibility, a generic annotation/workflow runtime, a universal draft system, or implementation/deployment through this planning item.

## Success signal

A reader creates “Kissing the Son,” writes one explanation and highlights evidence across Daniel 7:13 and Psalm 110:1 without repeatedly choosing a destination note. They collect Psalm 2:11 and reference-only Matthew 26:63–64, compare passages across a workspace, reopen the study through reference/text search, and share it with a verified invitee who can make private notes or an independent copy. Losing the original shared source does not erase the invitee’s own writing.

## Open Questions

- **Q-1 — Access and invitations:** Access/Identity now deliver ordinary personal enrollment, verified account/actor evidence and bounded current checks (decision236). Recipient/invitation lifecycle, notification delivery and live activation remain D-1/D-3 work. Channels, acceptance and placement are settled; this broader gate does not prevent the bounded ordinary-note consumer.
- **Q-2 — Data and writes:** Ordinary own-note create/write/reopen now has closed generated contracts, restricted native persistence, revision/lifecycle/retry protection and an opt-in rich-text editor. D-2 remains open for corpus anchors/versification/aliases, richer aggregates, private responses/copy/delete and coordinated release qualification; the data-and-saving companion and adopted app contract distinguish implemented scope from proposals.
- **Q-3 — Private-response recovery:** D-2 must define durable provenance, retention and deletion representation implementing independent ownership and the chosen own-study destination, without inaccessible source content, privacy broadening or silent highlight retargeting.
- **Q-4 — Interaction proof:** The reader-interaction companion defines the approved workspace-tab direction and proposed state/navigation details. D-4 must qualify bounded public URL/history snapshots and separate identity-safe same-device workspace restoration, tab/pane closure, shared edit lanes and responsive three/four-pane layouts, then prove native Hebrew selection, OS copy, virtual keyboard and accessible tool switching on actual iOS/Android. Preserve sequential chapter arrows and browser Back/Forward; separate per-pane passage histories are superseded.

The [implementation contract map](brownfield.md#gates-before-implementation) assigns D-1–D-5 owners, required outputs, acceptance evidence and dependency order. The architecture companion remains draft until these readiness gates close; its adopted rules record settled decisions rather than implementation availability. The [standalone Auth consumer contract](account-access.md#standalone-auth-consumer-contract--bounded-delivery) defines a bounded ST-36 entry slice that does not depend on Studies enrollment; live signup activation remains owner-gated.


## Bounded runtime status

The development/test opt-in implements standalone account entry, explicit personal
enrollment, ordinary own-study/note creation, autosave/reopen and saved-study rename.
The [app contract](../../../apps/scribeswell/docs/PERSONAL_NOTES_V1.md) and
[integration evidence](../../../apps/scribeswell/docs/STUDIES_OWNER_INTEGRATION_EVIDENCE.md)
retain bounded native SQL and actual Auth/Identity/Access/app qualification, including
original-operation recovery, isolation and disable denial. Events247/250 qualify
the original runtime and its13 review corrections; event263 qualifies rename.
Standalone account-entry code does not qualify live signup/confirmation activation,
default Access startup/readiness, physical devices or production release.

Collected passages and format2 note passage links are implemented, independently
reviewed and component-verified: collection226 browser/226 Python (event275), note
links324 browser/249 Python and local404f0956f58661cc90d87fdfdbb9142ee4048bc1
(events289–291). Their [passage](../../../apps/scribeswell/docs/PASSAGE_REFERENCES_V1.md)
and [note-reference](../../../apps/scribeswell/docs/NOTE_REFERENCES_V1.md) contracts
retain exact boundaries. Native migration/permissions/concurrency, actual-owner
proof and compatible rich-write activation remain pending final integration.
These component checkpoints stay in-review and do not fulfill the wider capabilities.

Own-library [search](../../../apps/scribeswell/docs/LIBRARY_SEARCH_V1.md) is
implemented with private read-body terms, filtered keyset pagination and account-safe
retained library context. Event307 completes independent review corrections and
final component qualification:368 browser passes/2expected native-browser skips,
277 Python passes/build/reproducibility checks. Its [evidence](../../../apps/scribeswell/docs/LIBRARY_SEARCH_EVIDENCE.md)
retains the API-red chronology gap, interrupted attempts, failed359/1/2 full run and
subsequent deterministic scroll/queued-callback/query corrections. Native SQL matching,
locale, actual isolation/zero mutation and owner/session proof are prepared only;
the checkpoint stays in-review. Shared search remains owner-gated.

The bounded [own-note deletion contract](../../../apps/scribeswell/docs/NOTE_DELETION_V1.md)
is implemented, independently reviewed and component-qualified:418 browser passes/
2expected native-browser skips,297 Python passes/build/generated checks (event321).
Event322 records local checkpoint f6b33ac6fb20a433f7b3ed72af82f9b8bc6694be.
Its [evidence](../../../apps/scribeswell/docs/NOTE_DELETION_EVIDENCE.md) retains all
failed intermediate runs, corrections and the original storage-unit-red chronology
gap. Native23 cases are collected only; the delivery stays in-review for final
migration/actual-owner/session qualification, with no activation inferred.
The [whole-study deletion contract](../../../apps/scribeswell/docs/STUDY_DELETION_V1.md)
is implemented, independently reviewed and component-qualified:490 browser passes/
2expected native skips,335 Python passes/build/owning checks (event337). Local
checkpoint fe3fb611f5d8f40be3e6954d768228726373e6f6 preserves all unrelated work.
Its [evidence](../../../apps/scribeswell/docs/STUDY_DELETION_EVIDENCE.md) retains the
failed488/2/2 host-timing run and controlled-clock6pass correction;13 review rows/
11 roots addressed. Native32 cases are collected only; delivery remains in-review
for final migration/actual-owner/session qualification.
The [four-pane contract](../../../apps/scribeswell/docs/FOUR_PASSAGE_LAYOUT_V1.md)
is implemented, independently reviewed and component-qualified:686 browser passes/
2expected native skips,13.5min, final build passed (event353). The160-source
inventory stayed unchanged. Local checkpoint 05e4b70e70ef88833f38adacf5e4d20015faa3ca (event354).
Its [evidence](../../../apps/scribeswell/docs/FOUR_PASSAGE_LAYOUT_EVIDENCE.md)
retains16 individual review/audit rows/12 addressed roots,1low rejection, interrupted
680 attempt and failed686 run. Latest-position resize and inactive-gesture races
were reproduced and fixed; the earlier initial-position cause and original method-
ordering gaps remain disclosed. No native/owner/session/device/signup/default Access/
release gate is closed; this remains in-review for final integration.
The [in-memory tab contract](../../../apps/scribeswell/docs/WORKSPACE_TABS_V1.md)
is implemented, independently reviewed and component-qualified (event377):782
browser passes/2 expected native-browser skips13.3min and build, on unchanged163-file
source. Its [evidence](../../../apps/scribeswell/docs/WORKSPACE_TABS_EVIDENCE.md)
retains25 individual review/audit rows,23 addressed patch roots,1 pre-existing defer,
1 rejection, all failed broad attempts and method limits. Word/Notes fixture action
and readiness races were traced; malformed-tab Auth callback resurrection had a
genuine registered red before the shared-filter correction. Decision357 protects
cancelled capacity replay. Wider live integration/device/release gates remain open;
durable same-device metadata restoration follows separately. All11 capabilities/38 acceptance requirements
remain: highlights, workspace tabs/four panes/restoration, copies, sharing, private
responses and wider D1–D5 gates are not removed or implicitly delivered. Integration
stays at the end under direction266; no production activation, provider change,
deployment or production-data mutation is inferred.

Decision380 adopts [same-device restoration v1](../../../apps/scribeswell/docs/WORKSPACE_RESTORATION_V1.md)
for CAP-11/ST-35: closed separate public/account metadata, incarnation binding,
nonmutating Auth identity verification, current resource checks and bounded IDB/
hydration policy. Events384–390 retain loop0 focused evidence, independent
review and loop1 corrections for staged-victim input loss, denial targeting,
Retry/queue/null-response and restored-panel consumption. The current visible
Studies owner loads current notes/cursor and collected passages without replacing
selected or dirty lanes; rail/Back/tab return/inherited context share it. Recovery
uses stable tab lifetime and truthful Retry after newer intent. Focused passes,
all failures and chronology limits remain separate from broad qualification.
Event392 records the completed full984-case browser run:982 passed and2 expected
native integration skips,16.2m, on unchanged165-file source
SHA8c320388b65c3b7e4543769aac06e56abda2887eee4bf1278882f889ec877df7.
Parent build passes. The original caret/IME case passes unchanged in both projects;
its earlier failure remains unexplained.
Earlier broad attempts were interrupted after demonstrated gaps, not qualified.
Events394–398 complete all three independent reviews and four patch roots after
12 individual verdicts; one pre-existing shared Notes response-validation defect
is deferred. Two genuine provider-ordering reds led to the recovery correction.
Final postpatch component qualification:994 passes/2 expected native integration
skips,18.1m, passing build and unchanged165-file source
SHAa4002d1be4fae051a4565dc18b5f955464173b7aa5f85209128446a30c47c070.
BMAD marks this bounded component delivery done; local checkpoint
5c13b28f8a52e5f93741b2bde2a95c67583c57b9 (event400), no push. Final integration
acceptance remains separate. See [restoration evidence](../../../apps/scribeswell/docs/WORKSPACE_RESTORATION_EVIDENCE.md).
Actual-owner/native-device/release qualification remains deferred to final integration.

Event402 starts the bounded Notes response-boundary correction for restoration
review defer L1-E1. Current api.note/api.notes reject unreadable documents before
ordinary/restored outline or editor attachment, preserving the existing recovery,
account and dirty-lane owners. Genuine acceptance/guard reds, focused passes and
build are recorded in [response-boundary evidence](../../../apps/scribeswell/docs/NOTE_RESPONSE_BOUNDARY_EVIDENCE.md).
Events404–406 complete the independent review and bounded correction: five patches,
one false claim,48 repeated focused browser passes/build and unchanged166-source
proof. The wider affected run records743passes/2expected native skips/1anonymous
mobile-scroll failure, not a clean suite. Its cause remains unverified despite
12 diagnostic and final focused passing repeats; original assertions stay intact.
Local checkpoint a5172ca1677f1638b837b6908c5b07a8c48a41a2 (event408), no push.
The new Notes behavior is component-verified; the public-scroll investigation,
broader suite and all final integration/release gates remain open.
