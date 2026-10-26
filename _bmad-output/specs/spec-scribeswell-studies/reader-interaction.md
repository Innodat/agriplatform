# Reader and study interaction — integration contract draft

Derived from the feature decision log, existing ReaderPage/PassagePane/WordStudy
and the illustrative prototype. **Owner:** Scribeswell reader/UX. **Status:** D-4
integration remains open. Four-pane public behavior has component implementation
in review under its adopted app contract; current executed results and remaining
corrections are in [its evidence](../../../apps/scribeswell/docs/FOUR_PASSAGE_LAYOUT_EVIDENCE.md).
The in-memory tab component has completed parent source/matrix audit, three
independent reviews/corrections and final component qualification (event377):782
browser passes/2 expected native-browser skips and build on unchanged163-file source.
Durable
same-device restoration and physical-device qualification remain open. The draft
below is superseded only by the explicitly linked bounded adoptions.

Inherits [UX](ux-behaviour.md), [architecture AD-12](ARCHITECTURE-SPINE.md#ad-12--one-frontend-context-owner-adopted)
and the [whole-note save contract](data-and-saving.md).
Existing [comparison behavior](../../../apps/scribeswell/docs/PASSAGE_COMPARISON.md)
is the baseline, not proof that study state or workspace tabs already exist.

### Bounded four-pane adoption — 2026-10-26

Decision334 adopts the app-owned
[four-passage public contract](../../../apps/scribeswell/docs/FOUR_PASSAGE_LAYOUT_V1.md)
for the bounded component slice. It closes the URL/snapshot/anchor/Router and
responsive geometry choices below for one workspace, while preserving existing
writing and malformed-link collection protection. Router outer-state transfer,
one-shot own-command acknowledgements, active-index replace and stale capture/seek
guards are explicit. Event353 records final component qualification:686 browser
passes/2expected native skips and build, with exact reviewed-source evidence and
historical method/failure limits retained. This closes no wider D-4/device gate.
The in-memory tab adoption below covers tab UI and private per-tab associations;
durable same-device restoration and physical-device proof remain open. It does not mark the entire
D-4 draft delivered or change the approved tab/four-pane direction.

### Bounded in-memory tab adoption — 2026-10-26

Decision345 adopts [WORKSPACE_TABS_V1.md](../../../apps/scribeswell/docs/WORKSPACE_TABS_V1.md)
for the next component delivery after four-pane qualification. It closes12-tab
bounds, tab-scoped presentation/global resource lanes, captured serialized creation,
resource-keyed editor retention, last-context departure and guarded public history
capacity recovery. Events361–377 record implementation, independent reviews and parent corrections.
Final component qualification is782 browser passes/2 expected native-browser skips
13.3min plus build on unchanged163-file source. All failed/focused runs and method
limits remain in the adopted evidence; no live integration/device acceptance follows.
All25 triage rows are resolved for the bounded component:23 patches,1 pre-existing
defer,1 false rejection. The Word/Notes test races were deterministically traced,
and retained malformed-tab callback credentials were reproduced before the shared
Auth-filter correction. Decision357 clarifies cancellation: close the chooser and cancel its victim/
consent, while retaining the exact unmatched-entry marker, suspending held-layout
checkpoints/collection, and allowing explicit retry or ordinary navigation. Cancelling
must not overwrite the incoming public history snapshot. Durable same-device metadata
storage and physical-device qualification remain separate gates.

## One state owner

One workspace controller owns the following distinct values. Components emit semantic
actions; they do not maintain competing copies of the editor or reader navigation.
No new state-management package is selected.

| Value | Meaning and lifetime |
| --- | --- |
| Account generation | Verified account key plus generation invalidating private requests/state on account change. Public reading has no private account requirement. |
| Per-tab active study | Own/shared library context and attribution, independent of which reader passage is open. |
| Per-tab current note | Explicitly selected explanation whose marks appear in that tab’s panes. It may be read-only; it is never made writable by containment. |
| Inspected note | Note being previewed/expanded in analysis. Inspection alone does not select a new current note or replace the write destination. |
| Highlight destination | Current note only when currently writable. Palette names it; otherwise explicitly choose/create an own note or private response before a write. Never silently fall back to a previously writable note while showing another explanation's marks. |
| Workspace collection | Ordered stable tab IDs and active tab; each tab owns up to four stable pane IDs, active pane, references, independent anchors/navigation generations and its study/current-note/tool/selection context. No independent pane history ledgers. |
| Analysis selection | Originating pane/source/revision, canonical passage/word or continuous range, selection generation and request identity. Not merely a word ID. |
| Tool state | Studies/Analysis/collapsed; Studies library/outline/Share view, Analysis tab, local search/expansion/focus-return state. |
| Global edit lane | Keyed by verified account and owned note, shared across all tabs: aggregate, base revision/evidence, local generation, acknowledged generation, pending operation and save/conflict state from D-2. |
| Mobile return | Tool-origin pane/reference/reading anchor and last intentional navigation generation. It does not rewind later passage navigation. |

Keep edit lanes above the existing keyed WordStudy lifecycle. Today WordStudy is
keyed by pane/word, so it can remount when analysis changes: mounting the sole editor
there would discard input. A Notes view attaches to the controller's existing lane;
it does not initialize another local note from whichever word is now selected.

## Action transitions

| Action | Reader/selection effect | Study/editor effect |
| --- | --- | --- |
| Inspect ordinary word | Set pane-origin analysis selection; load that word's morphology with exact request identity. | Current note/marks/write destination unchanged. Existing writing remains mounted. |
| Inspect continuous phrase | Capture ordered source occurrences; do not attribute one word's grammar to the phrase. | Notes/context tools may use it; no note/highlight created by inspection. |
| Preview/expand another note | Read authorized note context without replacing current colours. | Remains inspection. Explicit Open/select note is the transition below. |
| Leave study (study menu) | Keep active-tab pane references/anchors and other tabs unchanged. | Resolve the shared last-context departure guard, then clear this tab’s study/current-note association and marks and show Studies library. Delete no records. Rail collapse does not perform this transition. |
| Open a different study | Preserve all active-tab pane references/anchors; other tabs are unchanged. | Set active-tab study and show its outline; clear the previous study’s current-note/marks rather than implicitly selecting a note. Resolve last-context departure for prior writing before completing the switch. Explicit subsequent note selection activates its marks. |
| Select note from outline or explicit Open | Activate that note's marks; reveal a relevant reference when necessary using the normal reader navigation command. | Set current/inspected note and Notes tab. Changing the edited aggregate uses the exit guard; source-only inspection does not discard it. |
| Follow note passage / Open | Navigate active pane, preserving the other. | Current note and editing branch remain; no new note/ref/highlight is inferred. |
| Open beside reference | Open beside creates a new pane adjacent to active, up to four; at capacity explicitly replace a chosen pane or open a new tab. Activate/reveal the destination on phone. | Keep current note and writing. No passage deduplication across panes. |
| Highlight | Validate current selection generation; show palette near selection with named destination. | Change only the current owned aggregate's highlight set; same save lane/version as text. If source is read-only, explicitly choose/create own destination once. |
| Add note | Carry immutable passage/selection context into Notes and focus the new editor after explicit creation. | Reuse active writable study or explicit own/private-response destination. No silent teacher edit or new study per mark. |
| Add to study | Capture containing verse(s), preserving current reader location. | Update separate collected passage list; do not rewrite note text. |
| Studies/Analysis toggle, collapse, focus mode | Preserve reader anchors and selection provenance appropriate to visible pane. | Retain editor, pending lane and tool context. Hiding is not editor exit. |
| Change private-response destination | Reader/source context unchanged. | Affects future responses only; no move or privacy change to existing notes. |

Explicit current-note selection and merely expanding/inspecting content need distinct
semantic events and accessible states. Final component hit targets must demonstrate
this distinction without adding an unnecessary chooser for each highlight. Selecting
another note's existing mark explicitly opens/selects that note; transient word hover
and morphology responses do not. Full colours belong to the current note only, with a
separate visual treatment for transient text selection/word inspection.

## Workspace navigation and public history

The 2026-10-22 user approval supersedes max-two panes, exclusion of new Close
controls and proposed per-pane history buttons. Existing Previous/Next chapter
chevrons stay sequential chapter navigation. There are no separate pane history
ledgers or added history arrows.

### Tabs, targeting and lifetime

- Workspace-tab + creates a one-pane reading setup at the active passage and
  immediately opens its selector; dismissing retains that passage. Explicit Open
  in new tab from a reference opens it directly without a selector. Both inherit
  the active tab's study/
  current-note associations by identity, subject to current authority. It does not
  create/copy a study or note. Each tab subsequently retains its own context.
- Default tab label derives from the first pane reference and additional pane count;
  changing the active pane alone does not rename it. Custom Rename overrides that
  label without changing study data. Omit the study label when none is selected.
- Add reader pane (+) creates/activates a pane at the active reference, then opens
  its picker. Picker cancellation retains that pane/reference. At four panes, route
  to the existing explicit capacity choices before creating anything. Workspace-tab
  + and Add to study remain distinct actions.
- Each pane keeps its independent book/chapter selector and typed-entry interaction.
  Its navigation is unrestricted by the selected study’s passage list; notes and
  collected references are additional navigation routes, not a reading prerequisite.
- Open here changes the active pane. Open beside inserts and activates a new pane;
  identical chapter/reference is allowed with independent position. At four panes,
  require explicit replacement selection or Open in new tab. Never choose a victim
  implicitly. Open in new tab starts with the specified passage. Repeated Open to
  an identical reference issues a fresh seek generation.
- A single Studies/Analysis surface renders active-tab context and attributes the
  selection to its originating tab/pane/source. Pointer/keyboard intent, not late
  responses, changes the active tab/pane. Tab switch retains tool context/input.
- One controller-owned resource lane per account/note serves all tabs. Multiple
  views subscribe to its latest generation; view unmount never starts a separate
  save or writes an obsolete snapshot back. Caret/expansion state may be per-view.
- The common departure predicate applies to tab closure AND explicit study/note
  replacement: guard only when the action would remove the last live editing
  context for an unresolved lane. Revalidate resource/account/input generation and
  the departure predicate after asynchronous recovery or an open confirmation; a
  stale Close/Switch anyway action cannot discard newer input or another account’s
  work. Acknowledged input or another live context leaves immediately.
- Close pane removes a layout item, never note associations or records. A tab's
  note remains available through its shared panel while the tab exists. Closing a
  sole pane closes its tab when another tab remains, delegating to the same tab
  departure/save guard. Hide pane Close only for the final pane in the final tab.
  Hide tab Close for the final tab; semantic close commands protect these same
  cases. Do not reset passages or create a replacement default tab. Closing an active item selects the nearest surviving
  neighbor and preserves its position.
- Closing a tab drops its context associations. If another tab still references the
  same editing lane, keep it without a prompt. If closure would remove the last
  editing context for unresolved input, use D-2 bounded recovery then Stay / Close
  anyway. Success closes immediately. Switch tabs is retention, not an exit.
  An explicit Close anyway releases only that abandoned local editing context;
  unknown in-flight outcomes still require operation reconciliation, never cancel
  a committed mutation or resurrect a deleted note.
- Proposed initial implementation bounds: at most 12 tabs, four panes each; at the
  tab limit explain Close a tab to open another without closing one automatically.
  These bounds and responsive geometry are qualification choices, not new user
  information architecture. Unmount inactive heavy views while retaining compact
  in-memory anchors/context and global edit lanes. Do not require hidden chapter
  or morphology requests merely to keep tabs. Same-device durable context metadata
  is now in scope as described below; no durable unsent editor content, offline
  promise, saved-layout library or cross-device synchronization.

### One browser history path — proposed wire/snapshot boundary

Preserve valid root/legacy deep links using `book/chapter/verse` and
`compareBook/compareChapter/compareVerse`. Missing new format uses that legacy
one/two-pane parser. New explicit multi-pane links use one versioned `reader`
parameter containing compact JSON `{v:1, panes:[{ref}], active:0}`
percent-encoded by URLSearchParams. The new format contains one to four validated
public canonical references only, never tab/study/note titles or IDs, editor input,
selection, invitation proof or account evidence. Each `ref` uses the single D-2 canonical reference shape: catalogue/version,
versification ID, canonical book ID and closed chapter/verse_range target union.
Chapter-only has no verse bounds; verse_range retains inclusive start/end chapter
and verse, with equal endpoints for one verse. URL, history and passage actions
round-trip that same shape without truncating ranges. Reference-only entries need
no fabricated text source; identifiers come from the catalogue, not UI aliases. New format takes precedence when valid;
invalid supplied new format reports an invalid reading link and seeds one safe
public default rather than mixing untrusted/ambiguous formats. Do not emit both.
Exact generated parser/schema and length constraints must be qualified before code.

Proposed history.state namespace `scribeswellReader` is a closed versioned object:
`{v:1, tabKey, activePaneKey, panes:[{paneKey,ref,anchor?}]}`. Keys are random local
layout identities, never private resource identifiers. Anchor is public verse/word
occurrence plus bounded offset. Snapshot contains only the active public reading
setup, not all open tabs or private associations. Proposed maximums: four panes,
4096 URL characters, 8 KiB snapshot, 128 characters per layout key. Reject unknown
versions, duplicate keys, wrong active membership, invalid refs/anchors and extra
private fields through one shared validator; preserve unrelated history.state keys.

1. Before a deliberate passage navigation, tab activation or pane/tab creation/
   closure, replace the current entry's public anchors, then push exactly one new
   active-setup snapshot/URL. Tool/analysis changes, typing, native selections,
   scrolling and merely activating another pane update current state only, no push.
2. Browser popstate restores public references/anchors without pushing. If its
   tabKey survives, activate it and update its public layout only, preserving its
   current authorized private associations/global note lanes. Removed public panes
   have no private editor lane of their own. History never restores prior note text,
   prior study selection or private authorizations.
3. If that tab was closed, create a public-only Reading tab with the same local
   tabKey and recorded public layout, no inherited private associations/editor.
   Subsequent replay reuses it; never overwrite another live tab. At the tab cap,
   retain the current layout and show an explicit Choose tab to close and restore
   action. This recovery closes the chosen layout under the same save guard, then
   restores the pending public snapshot atomically without a history push. Stay
   cancels that recovery. Validate the pending snapshot/entry and current editing
   generations again after the guard; an intervening ordinary navigation/close
   invalidates it. Never silently replace a tab. This capacity path needs a dedicated
   sequence test.
4. Explicit shared/deep links restore their validated public arrangement and cannot
   select a private study/note. Ordinary refresh/return also uses the separate
   same-device workspace record below to restore other open tabs. Adopted precedence:
   an explicit public link controls the active reading setup; saved other tabs remain
   available without changing that link target. Compatible snapshot anchors apply
   only when references match. Missing/evicted/unknown history seeds references from
   the validated URL, without fabricating prior history or private associations.
5. History restore uses captured anchors. Explicit Open/direct URL uses its explicit
   verse target. Apply each seek once when its tab/pane/data becomes visible and
   ready, gated by generation; later resize/reveal must not re-seek. Corpus/layout
   changes permit best-effort public anchor fallback, never private mark retargeting.

This is a draft shared contract. Browser entry identity/replay, cap retry, byte/length
bounds, legacy parsing and stale seek handling require executable qualification
before implementation readiness. Ordinary browser history can evict entries; the app
does not claim to own or durably preserve the browser's complete history stack.

## Same-device refresh and return

User-approved scope now includes remembering all open tabs/reading positions and
per-tab selected study/note across refresh and return on the same device. This
supersedes the earlier active-public-layout-only reload boundary. Browser navigation
history remains public-only and distinct from this remembered working setup.

Decision380 adopts [WORKSPACE_RESTORATION_V1](../../../apps/scribeswell/docs/WORKSPACE_RESTORATION_V1.md)
as the versioned bounded storage/identity/hydration contract. Events384–390
record loop0 review and loop1 corrections, retaining all original evidence and
method limits. Event392 records current-source full browser qualification:982 passes/2 expected
native integration skips,16.2m, unchanged165-file inventory, plus passing build. The visible Studies
owner loads the current note page/cursor and collected passages on rail/Back/tab
return/inherited entry, preserving selected/dirty lanes. Interrupted reads offer
Retry for the same live account/tab incarnation/resource context; old data never
replaces newer intent. These owner reads do not persist content or auto-enroll.
Events394–398 complete three independent reviews, four patch roots and final
postpatch component qualification:994 browser passes/2 expected native integration
skips,18.1m, passing build and unchanged165-file source. Twelve individual review
verdicts retain one pre-existing shared Notes adapter defect as deferred. The
bounded BMAD component delivery is done at local checkpoint
5c13b28f8a52e5f93741b2bde2a95c67583c57b9 (event400), no push. Final
owner/native/device/session/release acceptance remains open. Earlier failures and chronology limits stay disclosed.
Adopted separation: public reading layout/anchors and opaque layout
keys may restore anonymously; account-bound study/note associations and custom tab
labels remain separate private context metadata. Persist the minimum identifiers
needed to refetch, not note bodies, source snippets, highlights, selection text,
credentials or pending commands. Custom labels may reveal personal study context;
do not expose them as anonymous public labels. This is a narrow context-metadata
exception, not authority for an offline editor cache or arbitrary private storage.

Restore private metadata only after verifying the same account generation, current
Studies admission and current study/note resource authority. Hydrate note content
through the authorized API into the existing single resource lane; never replay a
stored unsent body or auto-confirm an action. A switched account cannot inherit
another account’s associations/labels or in-memory input. Do not blindly overwrite
remembered private associations with null while sign-in/verification is pending.

If identity/access services are unavailable, show public reading with private
context hidden and allow retry; preserve pending metadata without treating an outage
as deletion. Confirmed source denial/deletion clears that inaccessible association
and sensitive labels, retaining public passages and independently owned responses.
Sign-out clears live private state; any retained return metadata must remain bound
to its verified owning account and unusable anonymously or by another account.

Persist layout creation/closure, references, stable reading anchors and explicit
context selection with bounded writes. Qualification must cover storage denied,
quota/eviction, malformed/old versions and competing browser-window writes, with
no claim of recovery when the device record is unavailable. Exact backend/browser
storage, record keys, expiry and concurrent-window policy are now adopted in that
contract; qualification remains open. Native IndexedDB adds no library or API. No cross-device workspace sync or unsent-input
survival promise. Saved note truth still comes from D-2 acknowledgements.

## Native selection, asynchronous work and focus

A selection snapshot identifies tab, pane, navigation generation, source/revision,
canonical verse(s) and exact ordered word occurrences. Store that snapshot before
palette/editor focus changes can collapse native selection. A live DOM Range is
not a durable highlight identity. A stale pane, changed source or superseded
selection requires reselection; never apply it to whichever chapter has now loaded.

Pointer drag/Shift-click and keyboard equivalents create continuous ranges only.
Desktop context menu offers Highlight/Add note/Add to study at the selected words;
context-menu dismissal returns focus without accidentally navigating or saving.
Touch long-press/handles retain native selection and OS Copy. Application selection
actions appear only for a valid current selection and must not hijack every native
menu/scroll or interpret a touch long-press as the desktop custom menu.

Do not intercept global typing inside inputs/contenteditable, composition events or
OS text selection. `/` outside editing remains the proposed discoverable passage-
picker shortcut, pending collision/accessibility checks. Enter confirms and Escape
cancels the picker. Reference clicks while editing position the caret; only explicit
Open passage navigates. Reading-mode reference activation uses Open here, with explicit Open beside / Open in new tab alternatives.

Every chapter/morphology/occurrence/private request has tab/pane/navigation/selection
and account generation as applicable. Check its exact originating context before
rendering. Abort where supported, but do not rely on abort for correctness. A late
response cannot reopen closed tools, replace newer selection, move the active pane
or focus an editor. Protected cache keys include account/resource/version; account
change clears private caches, not merely the visible panel.

Focus follows user intent: Add note focuses its editor; palette/context dismissal
returns to source action/selection; picker cancellation restores its trigger.
Background saves/fetches do not steal typing focus. Save/conflict status is accessible
without announcing each keystroke. Identify each pane and origin reference in analysis;
private/shared/Only you labels and read-only source state remain perceivable.

## Phone and editor exits

Retain compact pane state while switching visible passage/tab; heavy hidden views may
unmount. Hidden DOM must not supply the visible tab/pane’s analysis. Full-width Reader/Studies/
Analysis replaces desktop's one panel/rail, not two squeezed sidebars. Remember each
tool's scroll and reader anchor; return to reader reveals the origin pane unless a
later deliberate navigation superseded it. Virtual keyboard changes usable geometry,
not note ownership or passage history.

Removing the last live editing context through note/study replacement, tab closure
or leaving the app invokes D-2's bounded save/outcome recovery under the common
departure predicate above. Acknowledged input leaves immediately. If still unconfirmed,
Stay / Close anyway or Stay / Switch anyway appears only on that exit, with possible
loss explained. Retry remains inline during editing; there is no Keep editing button.
Word inspection, reader navigation, tab switching and tool hiding preserve the lane and are not exits.
A host/browser unload must never be described as guaranteed asynchronous saving or
unsent-input survival. No unreviewed localStorage/IndexedDB/offline editor cache.

A resource identity is distinct from tool/pane identity: the same note has one lane
when reached through Word Analysis, study outline, highlight or private-response view.
Confirmed source loss removes inaccessible teacher content/caches but preserves the
reader's independently owned response and public links. Reauthentication for the same
account resumes only still-authorized in-memory context; a different account or sign-
out clears private state and cannot inherit the prior user's typing. Dependency outage
is unavailable, not evidence of deletion or revocation. Confirmed access denial stops
protected writes and hides unavailable protected content; retained recovery context
cannot be exposed under another identity or bypass current authority.

## Closure and acceptance evidence

D-4 draft defines semantic ownership/transitions, not implementation/device success.
Before consuming code, qualify the proposed snapshot/URL and resource bounds,
identity-safe same-device context storage/restore, last-pane/tab close protection, tab strip overflow and three/four-pane layouts. Demonstrate
controller/editor remount boundaries and strict note-inspection/selection targets.
D-2 owns common identities/save schemas; components cannot invent competing writes.

Required browser cases ST-04–06/10–16/21–23/28/31–34 include retained typing across
word changes, tab switches/remounts and layout closure; one note in multiple tabs;
current versus inspected note; shared read-only source; same-chapter positions;
legacy/direct multi-pane URLs; interleaved browser Back/Forward and closed-tab replay
at capacity; invalid snapshots; URL verse versus anchor restore; late requests after
tab/pane/account changes; keyboard/focus and actual-exit-only uncertainty guards.

Physical iOS Safari and Android Chrome must prove Hebrew handles/drag, native Copy,
bottom actions/palette, editor IME/caret and visible virtual keyboard/landscape. Browser
viewport emulation alone is insufficient. If the native interaction requires a different
user flow, return that concrete fallback for UX agreement rather than silently changing
this contract. Device and accessibility evidence closes at consuming-story acceptance.

Impact: reader/editor/selection domain stays in Scribeswell; assess proven neutral focus/
save/return patterns for shared UI only with first-consumer tests. No framework upgrade,
new agent rule or accepted ADR amendment. Documentation uses this canonical companion;
D-5 still governs safe activation, and public reading stays independent of Studies.

Event406 records one existing anonymous mobile-scroll assertion failure during the
Notes response-boundary regression: history anchor did not advance after a synthetic
scroll. This does not execute changed Notes guards. Twelve instrumented repeats and
final focused repeats pass; the original cause is still unverified. Original gesture
and assertions remain unchanged. Broader suite qualification stays open and the
medium-if-confirmed investigation retains actual failure context. This observation
does not close native phone/selection or any final integration gate.
