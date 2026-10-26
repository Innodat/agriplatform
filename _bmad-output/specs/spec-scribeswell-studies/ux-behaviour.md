# Study UX contract

Derived companion to [SPEC.md](SPEC.md). The accepted dialogue governs; prototypes demonstrate it but do not select security, schema or release contracts.

## Terms and relationships

| Item | Meaning |
| --- | --- |
| Study | A titled, private-by-default collection containing notes and a passage list. Optional introductory text/source link is supported. “My studies” is the feature name. |
| Workspace tab | A temporary reading setup with up to four panes and its own study/current-note associations; it is not a study or folder. |
| Note | The reader’s explanation or question; no required title. A preview uses its opening text. It can begin at study, passage or phrase level and later connect several passages. |
| Highlight | An explicitly coloured word/phrase range owned by one note, at its actual text occurrence rather than every instance of a lemma. A note can own several ranges and colours across passages, or none. |
| Current note | The visible destination for further highlights. Choose once; ordinary word inspection and reference navigation do not silently replace it. |
| Passage reference | A chapter, verse or verse range. A note’s reference links and a study’s collected passage list are independently useful. |
| Private response | The reader’s own note beside a teacher’s/shared note or passage. It is not an edit of, or automatically shared addition to, the author’s content. |
| Independent copy | Editable content owned by the copier, with source credit; no synchronization with its source. |

The lecture’s “bar anush” observation is attributed user input, not a verified lexical claim or a request to generate interpretation.

## Entry and first study

- Provide an account entry from the public reader header with Sign in and Create account, accessible without selecting/creating a study. Use the existing shared authentication owner and its verification flow; account creation alone creates no study or invitation acceptance. A reader may finish account creation and continue ordinary reading.
- Bible reading and existing word analysis stay public. My studies, Highlight, Add note and Add to study lead to that same sign-in/account-creation experience when required.
- Return the same authorized account to the prior passage/selection and intended interaction after sign-in. Restore only supported recoverable input; never automatically grant sharing access or confirm a consequential action.
- Study creation is explicit. A title may be supplied immediately or left as an unused default: Untitled study, Untitled study 1, Untitled study 2, and so on within that reader’s own studies. Renaming is available later.
- Once created, the active study is visible and reused; adding another note does not create another study. Choose an existing or new own study when an action has no writable destination.
- Every verified signed-in reader is eligible for personal studies without administrator approval, organization membership, employment or PtS access. Implement that policy explicitly through Q-1’s account admission/capability contract; identity alone still grants no access to another reader’s private content, and current suspension/resource checks apply. No organization or employment selector is introduced.

## Workspace and library

- Desktop: one workspace tab strip above the reading area, up to four readers in the active tab, one adjacent right-side tool panel, then a thin labelled Studies/Analysis rail. The tools replace each other in that panel. Clicking the active tool collapses it and returns room to reading; switching tools preserves editor/input and tool context.
- The accepted prototype’s approximately 350px panel/58px rail are examples, not required pixel constants. Responsive behaviour must leave usable text and controls.
- Studies opens a searchable library or active study. My studies and Shared with me are distinct views; search covers accessible titles, note text and references, including Hebrew input. Search must not reveal a former share after authority is lost.
- Opening a different study changes only the active tab’s study context and Studies outline; preserve every reader pane’s reference and position. Do not automatically open its references or rearrange panes. Explicit note selection activates that note’s highlights; departing the previous editing context follows the common save guard.
- Opening a study shows Notes first, each once with a compact opening-text preview and reference links, followed by a separate Passages list. General notes are supported. No required note-title field or repeated explanation beneath every passage.
- Click a note to open its explanation in Analysis → Notes and activate its highlights. Click a passage to navigate. Follow a note’s reference while retaining the current note. Relevant text should be revealed when opening a phrase-anchored note.
- Keep previews/expansion predictable; do not auto-expand a changing amount of content based on available viewport height. Retain manual expansion/working context while using the study.
- Leave study is an explicit action in the study menu, not an × beside the title. It returns the Studies panel to the library and clears only the active tab’s study/current note/marks, retaining passage references/positions and all saved content. Other tabs are unaffected. Apply the common last-context departure guard to unresolved writing. The Studies rail button only hides/shows its panel and retains context.
- Back to Studies returns to the outline/library without losing recoverable writing or search context. Tags, collection hierarchy and group administration are absent.

## Passage picker and capture

- Extend the existing book/chapter dropdown with one editable reference field. Typing drives the same visible book list and chapter grid that mouse browsing uses; no separate mode or duplicated result/confirmation button.
- Accept supported English names/abbreviations, Hebrew names/shorthands, digits 0–9 and conventional Hebrew numbers, including mixed `תהילים קי:1`. Define the alias/versification catalogue under Q-2; ambiguity requires a choice rather than a guess.
- Typing positions/highlights the matching book/chapter without moving the reader. Enter or clicking that chapter confirms the complete typed reference and closes the picker. The chapter cell retains visible verse/range context when specified.
- No verses means a whole chapter. Clicking a different chapter clears the old verse range rather than reusing it there. Invalid chapter/range input remains editable with an explanation; never treat illustrative `ps 2:10-13` as valid when the selected canon has only 12 verses.
- Reader picker confirmation navigates; Add passage confirmation adds the reference and leaves the reader’s passage/position unchanged. Re-adding an existing reference must not overwrite notes or useful input.
- Add current passage bypasses retyping and permits range adjustment. Select verses in the reader lets the user choose first/last verse numbers, with a one-verse selection immediately valid, then Add to study. This does not replace normal word analysis.
- The keyboard entry shortcut must be discoverable and checked against existing shortcuts/accessibility; `/` outside text editing is the prototype candidate. Enter confirms, Escape cancels and restores focus. No interception of typing inside notes.
- Reference-only entries, such as Matthew 26:63–64, remain linkable and support notes/optional external source links. Clearly say the text is unavailable; no fabricated text, word anchors or word highlights. A reference catalogue is not authority to expand the corpus.

## Notes and writing

- Display and edit notes in the same Notes tab in Word Analysis. Add note creates an editor there; editing is not an inserted form beneath the verse. The study and inspector refer to the same note.
- Support paragraphs, bold, italic, lists, external source links and deliberate passage-reference insertion. Mixed Hebrew/English must have appropriate paragraph direction, readable punctuation and caret behaviour. Exact safe representation/limits belong to Q-2.
- In reading mode a note’s passage link opens its passage with this note’s existing highlights. While editing, clicking positions the cursor and offers a deliberate Open passage action; it must not unexpectedly navigate.
- Inserting a reference does not quote selected text, create a passage-list entry or paint a verse. “Insert selected text” and automatic phrase quotation were explicitly rejected.
- Keep the selected passage/phrase and study context visible when adding a text-attached note. Do not show one word’s morphology as the grammar of a multiword selection; preserve the existing individual-word inspector.
- Relevant notes from accessible studies should remain discoverable with author/study attribution. Full colours belong to the chosen current note; do not superimpose every explanation’s markings. Exact inspected-note/current-note distinction is a Q-4 acceptance detail.

## Highlight interaction

- The highlight control lives near selected text rather than requiring entry into Word Analysis. A small selection toolbar offers Highlight, Add note and Add to study; right-click is an alternative route to the same three actions.
- Highlight opens a small colour palette naming its current note, with Change available. No repeated note-picker click for every mark. Without a writable current note, explicitly choose/create an own note once; never silently write into a teacher’s note.
- Add note attaches a new observation to the selected words and opens Notes. Add to study captures the containing verse(s), reusing an existing passage entry where applicable. The actions have different scopes.
- A note may own colours in any deliberately connected supported passage, including passages not independently listed in the study. Highlighting adds the note’s text connection; it does not silently require every study passage to be marked.
- Anchor the exact occurrence, not screen position or all matching words. If a corpus correction leaves a highlight’s location uncertain, keep the note/reference, mark the affected highlight Needs review and let the reader deliberately reselect the intended words. Do not silently retarget it, insert a quotation or require retention of old full Bible editions for this recovery.
- Choose colour freely; no built-in interpretation of yellow/blue/etc. Removing a colour is a highlight removal, not note deletion.
- Desktop: ordinary click retains word analysis; left-drag selects a continuous phrase; Shift-click can extend the range. Selecting an existing mark can open its note. Disconnected Ctrl-click selections are deferred.
- Phone: tap for ordinary analysis; native long-press/selection handles extend a phrase. Preserve familiar OS selection/copy behaviour. Show the three application actions in a bottom bar only while selection exists; colours open in a reachable bottom palette.
- Phone Add note opens the full-width Notes view with selection/study context; Add to study confirms in place. Reader return restores passage/position. Native iOS/Android selection and keyboard geometry still need real-device proof.

## Workspace tabs, comparison and mobile tools

The user-approved 2026-10-22 workspace direction supersedes the earlier two-pane ceiling, exclusion of new Close controls and separate per-pane Back/Forward histories.

- One tab strip above the whole reading area switches reading setups. Start with one pane; add panes deliberately, up to four per tab. Tabs do not introduce another study hierarchy. Default tab labels use the first pane’s passage, plus the number of additional panes (e.g. Daniel 7:13 +2). Activating another pane does not rename the tab. Optional Rename sets a stable custom label without renaming the study.
- Show the selected study beneath the tab strip only when one is selected; otherwise omit that label and reclaim its space. Studies remains accessible.
- A compact + control adds a reader pane, distinct from the workspace-tab +, with tooltip/accessible name Add reader pane. Below the four-pane limit it opens a new pane at the active passage and immediately opens that pane’s chapter selector; dismissing the selector retains the duplicated passage. At capacity offer explicit replacement/new-tab choices without creating a fifth pane. This is separate from Add to study.
- Each reader pane retains its own book/chapter selector with typed reference entry. Navigate any supported passage freely; note/study references provide additional shortcuts. A passage need not be collected in a study before it can be read.
- Workspace-tab + starts one pane at the active passage and immediately opens its selector; dismissing keeps that passage. Open in new tab from a reference opens the reference directly without showing a selector. New tab inherits the active study/current-note associations, without copying records. Each tab then retains its own context and reader positions; explicitly selecting a different study/note affects that tab. The same note has one shared edit buffer/save lane across every tab and tool view.
- Open here targets the active pane. Open beside creates another pane next to it and activates that destination, even if the passage is already present. At four panes, offer an explicit pane replacement or Open in new tab; never silently choose another pane or add a fifth. Open in new tab starts a one-pane reading setup with the reference and inherited context.
- Identical chapters retain independent reading anchors, e.g. Psalm 119:1 beside :176. The active tab's current note supplies relevant marks in its panes; analysis identifies the actual originating tab/pane/reference. Tool switching or ordinary word inspection does not change that note.
- Hide tab Close on the final workspace tab. A sole reader pane is closable when another tab exists: closing it closes its tab through the same save guard. Hide pane Close only for the final pane in the final tab; protect that case through alternate close commands too. Closing an active item activates its nearest surviving neighbour without resetting passages or positions. Closing layouts never deletes study content. Tab switching retains work rather than treating it as an editor exit. Closing a layout that would drop the last unresolved editing context uses the existing bounded-save/exit guard. Retaining another reference to the same edit lane avoids a needless prompt.
- Prototype geometry: three columns when comfortably readable; four panes in a 2×2 grid. At narrower reader widths, use fewer columns; the shared panel may collapse. Exact breakpoints/minimum sizes require layout qualification, including the panel open. Do not ship four cramped columns simply to meet a number.
- Preserve existing Previous/Next chapter arrows and ordinary browser Back/Forward. Do not add independent pane history buttons or ledgers. History restores public reading arrangements/positions without undoing edits; scrolling, analysis/tool changes and typing create no navigation entries. Detailed snapshots and closed-tab replay are proposed in reader-interaction.md, not yet code-qualified.
- One shared right-side Studies/Analysis panel follows the active tab and pane. Each tab retains tool/selection context. Switching tabs never redirects an in-flight write or stale analysis response to a different tab. The panel remains visibly attributed to the selected study/note and source passage.
- Phone: keep the workspace strip, then a compact passage switcher; show one pane at a time. Reader/Studies/Analysis are full-width views with explicit reader return, independent pane positions and no horizontal page overflow. Return does not rewind later deliberate navigation. No nested tab strips or miniature desktop columns.
- On refresh or a later visit on the same device, restore open tabs, passages and reading positions. Restore each tab’s selected study and note only for the verified same account after current access checks; load the acknowledged saved note through its authorized API. Keep private labels/content hidden until then. Unavailable verification leaves reading usable and permits retry; it is not proof of deletion. This restores working context, not unacknowledged writing or cross-device synchronization.
- More than four panes, arbitrary docking/zones, synchronized scrolling, a saved-layout library and cross-device tab sync are outside this feature. Numeric tab/memory limits and inactive-view lifecycle need qualification before implementation; hidden tabs must not require every reader/editor DOM to stay mounted.

## Sharing, personal extensions and copies

- Private is the default. The owner shares through named email invitations with Can view and Remove; no edit-role matrix, group management or bearer link option.
- Share sits beneath the active study title. It temporarily replaces the outline inside the same Studies panel; Back to study restores the outline without moving the reader. Phone uses that existing full-width tool view, with no extra sidebar or rail item.
- Track invitations in this same Share panel with one row per person and a compact ⋯ menu: Pending offers Send reminder / Cancel invitation; Can view offers Remove access; Expired or Declined offers Invite again. Pending reports awaiting acceptance, not confirmed delivery or reading. Reminders reuse the invitation; Invite again explicitly creates a fresh invitation. No separate invitation-management screen.
- Invitations may wait for account creation. Only the verified intended recipient, with current admission and resource authority, can activate/access. Forwarded links alone grant nothing. Exact recipient verification and delivery are Q-1, not an email-string comparison.
- Before acceptance the recipient verifies the invited address. After acceptance the share follows that account through a verified email change; another/recreated account inherits no access or private work by reusing the address and needs a fresh invitation.
- Deliver invitations through email and an account-scoped in-app notification; both open the same invitation with Accept / Decline. The recipient explicitly accepts before the study joins their accepted Shared with me library. Opening a link or reading/dismissing a notification does not accept or decline.
- At the top of Studies → Shared with me, show Pending invitations above the accepted searchable study list, hidden when empty. Each invitation shows its study title, sender, Can view and Accept / Decline. Acceptance moves the study into the accepted list; notification read-state leaves a pending invitation available here.
- Unaccepted invitations expire after 30 days. Accepted sharing has no invitation-based expiry and remains until removed under current access rules. A reminder does not create duplicate access; an expired invitation shows an expired state, and the owner may explicitly issue a fresh invitation. Expiry never deletes recipient-owned writing or copies and is separate from notification retention/retry policy.
- Use the platform notification capability for delivery and common inbox/read-state mechanics; Scribeswell owns invitation state, permitted recipient/content and acceptance. Account-scoped invitations must not borrow Leave organization membership or introduce a synthetic organization. Both delivery routes reach the same invitation action rather than create separate grants.
- Readers see current author updates, can add clearly labelled private responses, and can make an attributed own copy. Author content remains read-only unless independently copied. Sharing an original does not expose a reader’s private responses.
- On the first Add private note for a shared study, choose an existing own study or explicitly create one with suggested title “My notes on [shared study]”. Reuse that destination for later responses to this shared study, showing its name and Change; changing the default affects future notes rather than silently moving existing ones.
- Show the same response beneath its source in Notes, labelled My private note / Only you and Saved in [own study], and make it accessible in My studies. These are two views, not duplicate notes. Destination selection cannot silently broaden the response’s private visibility. When the original becomes unavailable, the own study and note/passages remain; no automatic copy of author content is created.
- Private responses stay Only you even when their destination study is already shared or is later shared. Ordinary notes follow the study’s sharing. The Share view explains that private notes are excluded; there is no action to include selected private responses in this first version. Duplicating a private response preserves its privacy, and copying/sharing a study must not silently expose it.
- Duplicate note lives in its menu: copy writing, passage connections and all ranges/colours; open the copy as current and editable. Own-note copies default to the same study; shared-note copies choose an own destination and retain credit. No separate Copy highlights action or linked synchronization.
- Losing the original study/note through revocation/deletion keeps the reader’s independently owned private writing and passage references. Show a simple original-unavailable message. Do not retain access to source content merely to explain a private response; see Q-3 for recovery/provenance representation.
- Deliberately created independent copies stay independent; source revocation must not be misrepresented as synchronization. Current access still governs their copier-owned destination.

## Saving and removal

| Situation/action | Required behaviour |
| --- | --- |
| Personal note typing | Autosave; Draft saved only for acknowledged current input. No note submission/publish step. |
| Background saving unconfirmed | Inline Changes not saved with Retry; keep editing available, no Keep editing button or modal merely for typing. |
| Leave with acknowledged input | Close/switch immediately. |
| Leave with pending/unknown save | Bounded flush/recovery, then Stay / Close anyway or Stay / Switch anyway if still unconfirmed. Explain possible loss; no rollback or unsent-input survival promise. |
| Studies/Analysis toggle | Preserve the same editor and input; hiding a tool is not automatically leaving its work. |
| Re-authenticate | Same authorized user returns to validated recoverable context; different account sees no prior private content. Never repeat an unresolved consequential operation automatically. |
| Same note changed elsewhere | Pause the stale editor’s autosave, keep local writing visible while open and show This note changed elsewhere / latest changes not saved with Review latest. After review, offer Use latest with explicit local-discard explanation, or Save mine as a new note preserving this editing branch’s content/highlights and privacy. No automatic merge, overwrite or duplicate. |
| Remove highlight | Keep note and other markings. |
| Delete note | Confirm that its owned highlights are also removed. Prevent stale save/create retries from recreating it. |
| Remove passage-list entry | Keep notes/highlights and their reference navigation. |
| Delete own study | Confirm removal of that study’s owned notes/highlights; never cascade into other readers’ independently owned responses/copies. |
| Remove shared library entry | Keep author content and own private notes. |

## Illustrative artifacts

- [Workspace tabs interactive mockup](../../brainstorming/brainstorm-scribeswell-studies-2026-10-19/workspace-tabs-prototype.html) — focused follow-up for the approved expanded layout; earlier two-pane images below are historical examples, superseded for pane/tab navigation.


- [Combined interactive prototype](../../brainstorming/brainstorm-scribeswell-studies-2026-10-19/study-prototype.html)
- [Desktop outline](../../brainstorming/brainstorm-scribeswell-studies-2026-10-19/study-prototype-desktop.png), [comparison](../../brainstorming/brainstorm-scribeswell-studies-2026-10-19/study-prototype-compare.png)
- [Phone outline](../../brainstorming/brainstorm-scribeswell-studies-2026-10-19/study-prototype-phone.png), [notes](../../brainstorming/brainstorm-scribeswell-studies-2026-10-19/study-prototype-phone-notes.png), [selection actions](../../brainstorming/brainstorm-scribeswell-studies-2026-10-19/study-prototype-phone-selection.png)
- [Private-note destination chooser](../../brainstorming/brainstorm-scribeswell-studies-2026-10-19/private-notes-destination.png), [private note alongside source](../../brainstorming/brainstorm-scribeswell-studies-2026-10-19/private-notes-alongside.png)

The user approved the combined journey. The artifact has sample text and in-memory state, simulated sign-in/sharing/saving, and resets on reload. No invitation is sent. Prototype regexes, token positions, sanitization, save flags and DOM behaviour are not production contracts or security evidence. Earlier mockups with study-owned highlights, passage-first repeated notes or a separate reference-confirmation button are superseded by this contract.

Workspace follow-up: [three-pane desktop](../../brainstorming/brainstorm-scribeswell-studies-2026-10-19/workspace-tabs-three.png), [four-pane desktop with Notes](../../brainstorming/brainstorm-scribeswell-studies-2026-10-19/workspace-tabs-four.png), [phone reader](../../brainstorming/brainstorm-scribeswell-studies-2026-10-19/workspace-tabs-phone-reader.png) and [phone Notes](../../brainstorming/brainstorm-scribeswell-studies-2026-10-19/workspace-tabs-phone-notes.png). The focused mockup uses sample references, one shared plain-text note and simulated saving. It does not demonstrate real word selection, rich text, authentication, storage or browser URL/history restoration. Disabled chapter arrows retain their placement only.

The focused workspace mockup now includes accepted +/picker-cancellation, naming, last-item Close protection and Leave study controls. [Study menu](../../brainstorming/brainstorm-scribeswell-studies-2026-10-19/workspace-tabs-leave-study.png) and [reader after leaving](../../brainstorming/brainstorm-scribeswell-studies-2026-10-19/workspace-tabs-no-study.png) illustrate the distinction between leaving a study and hiding the panel. Same-device return persistence remains a written requirement, not prototype behavior.


## Bounded ordinary-note implementation

The bounded runtime supplies Studies/Analysis ordinary-note editing, Hebrew/direction/paragraphs/lists/marks/safe external links and a shared in-memory save lane. Intercepted desktop/mobile tests and a separate native SQL desktop reload exercise autosave, recovery and context isolation; review corrections and affected acceptance are complete. Physical iOS/Android and live integration remain unqualified. Richer reference/highlight/sharing and expanded workspace requirements above retain their agreed direction. See the [delivery evidence](../../implementation-artifacts/spec-scribeswell-personal-notes-runtime.md) for exact tests and limitations.
