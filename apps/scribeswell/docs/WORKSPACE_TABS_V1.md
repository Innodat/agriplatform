# In-memory workspace tabs v1

Status: adopted bounded technical contract with independently reviewed component
implementation and final782-pass/2-skip browser/build qualification. Final live
integration/device/release gates remain open, as recorded in
[WORKSPACE_TABS_EVIDENCE.md](WORKSPACE_TABS_EVIDENCE.md). Consumes CAP-11/ST-31–34 and
[the canonical reader direction](../../../_bmad-output/specs/spec-scribeswell-studies/reader-interaction.md).
The [four-passage contract](FOUR_PASSAGE_LAYOUT_V1.md) remains authoritative for
public references, closed URL/snapshot parsing, anchor bounds and Router ownership.

## Bounded outcome and ownership

Readers can retain up to12 ordered workspace tabs, each with one to four independent
panes. Public reading remains anonymous-capable. Tabs retain public references,
positions and active pane plus their own currently authorized study/current-note,
tool and analysis context. A single account-owned resource registry retains each
note's actual buffer, revision and pending operation; tab views reference that lane,
never clone its body or save a departing obsolete view. One shared tool surface
follows the active tab. No state-management dependency, API, database or owner-service
change is needed. Same-device durable metadata storage/refresh restoration is a
subsequent contract, not silently omitted or implemented by this item.

Public and private ownership must stay distinct: history contains only the existing
closed active public snapshot. No private resource ID, label, editor state, creation
operation or selection enters URLs/history. Custom tab labels are live private
context and clear/mask with owning account authority. Anonymous custom labels may
remain only in the current anonymous memory generation and cannot migrate into a
signed-in/different-account context. No browser storage is introduced here.

## Tab actions

- New workspace tab inserts adjacent to active, starts at its complete active
  canonical reference, activates it and opens its selector. Cancel retains that
  passage/tab. Explicit Open in new tab uses its supplied full reference without a
  picker. Both inherit authorized study/current-note associations by identity,
  never create/copy records. They do not inherit a pending creation action or native
  selection. New tabs reveal Reader initially; their inherited note remains
  associated and available when Analysis Notes is explicitly opened. Existing
  tabs retain their own tool/subtab state. Preserve malformed-fallback provenance
  until explicit valid navigation.
- At12 tabs, explain Close a tab to open another. Never evict a tab automatically.
  The four-pane replacement dialog may additionally offer Open in new tab only
  once that action exists; its captured reference/generation remains revalidated.
- Activation captures the outgoing public anchor and creates exactly one Router
  history step for the newly active setup. A tab switch retains editing and does
  not call a save/departure guard. Re-selecting the active tab is a no-op.
- Default label derives from first pane/reference plus additional pane count,
  independent of active pane. Explicit Rename edits only the tab label; trim,
  require1–80 Unicode code points, reject controls, support mixed Hebrew/English.
  Cancel preserves it. Returning to the default name is an explicit Reset name.
  No study title is changed. Omit absent study labels.
- Presentation refinement (2026-11-04): default tab reference numbers use Hebrew
  numbering, preserving canonical numeric references and verbatim custom labels.
  New tab stays beside the horizontally scrolling strip. Rename is a compact
  pencil, revealed on mouse hover/keyboard focus and available directly on touch;
  accessible action names remain explicit. Reading actions and Studies/Analysis
  share one responsive toolbar with visible tool selection.
- Close tab removes only that layout and its associations. Closing active selects
  previous neighbor if present, otherwise next, preserving its positions. Closing
  inactive leaves active unchanged. A sole pane delegates to tab closure when
  another tab exists. Hide final-tab/final-reader Close and semantically refuse it.
  Exactly one push for successful closure; Cancel/Stay pushes nothing. Keyboard
  focus displaced by closure moves to the active survivor's tab control without
  stealing unrelated focus.
- Accessible tab strip: named tablist, tab/tabpanel relationships, roving keyboard
  focus and Left/Right/Home/End with manual Enter/Space activation. Native clicks
  and explicit commands choose tabs; late work never does. The strip scrolls
  horizontally within its own bounds and reveals the focused/active tab. Add,
  Rename and Close are separately named controls, not nested interactive targets.
  Phone keeps one pane visible with its named switcher and full-width tools.

## Per-tab context and resource operations

Explicit study/note replacement and Leave study affect only the initiating tab's
association and outline; public references/positions stay unchanged. Study opening
never automatically opens a collected passage. Hiding tools retains their input,
outline/analysis scroll and note context. Switching distinct notes may rebind one
editor view, but retains the authoritative lane, owned reference atoms, usable
caret/range and unfinished text. Completion of native composition belongs to the
originating lane even when an intentional tab switch changes the active view.
Analysis provenance includes tab/pane/navigation/selection generation; late
chapter/morphology/occurrence responses cannot focus or select another tab.

Retain one editor host per live resource lane, keyed by account/note, with an
explicit lane binding for change/composition/retry rather than ambient active note.
Only the active view is exposed/focusable. Reusing the same lane across tabs reuses
that host; different notes retain their own DOM/owned atoms/native undo and bounded
selection ranges. Restore a caret only on explicit editor focus, never a background
acknowledgement. Retain DOM hosts only for currently associated or unresolved
editing lanes; acknowledged last-context departure may release its host. A
recovery-only receipt/attempt does not require a hidden editor. Do not create
hidden editors for every previously visited saved note. Inactive heavy
reader/analysis views may unmount; retain compact
tab-owned analysis filters/page/expansion/scroll, not hidden network requests. An
inactive host may finish composition into its own lane; it cannot redirect input.

Keep creation account-global and serialized, retaining the original attempt,
running promise, acknowledgement, captured origin tab/context generation and
intended parent. Switching tabs never starts a second creation or moves its origin.
A completion materializes shared resource truth; it attaches/selects only in the
still-live unchanged originating context, without activating/focusing it. If that
context changed or closed, retain an account-scoped creation recovery item and
safe original-command retry. A known created resource can be explicitly opened
under current API authority; do not replay creation with a fresh operation ID,
clone its payload into another tab or automatically replace another context.
Acknowledgement followed by failed read retries the read, not a second creation.
An unresolved creation blocks another creation with an actionable original
recovery item; it does not block public tab reading/navigation. Existing deletion
preparation must continue coordinating these account-global creation operations.

All asynchronous view work captures account generation, tab identity and relevant
context/navigation generation. A completion may update its still-live originating
context or its existing resource lane; it cannot attach private data or errors to
whichever tab is now active. Explicit deletion acknowledgements remove matching
note/study associations across all tabs while preserving unrelated contexts and
public reading. Existing deletion, title and collection operation identities and
unknown-outcome recovery remain account/resource-owned and available after a view
closes; view closure is never mutation cancellation. Confirmed denial clears
inaccessible private contexts; outages hide/retry under current authority rather
than treating the resource as deleted. Account change/sign-out clears every live
private association, label, lane, request and focus/selection recovery target.

## Last-live-context departure

A live editing context is an authorized open tab whose current-note association
references the exact account/note lane. Tools hidden and inactive tabs still count;
public history entries and pending closed-tab restores do not. Close/replacement
that leaves another such context proceeds immediately. Removing the last context
for unresolved input uses the existing total five-second bounded save/outcome
recovery, then exit-only Stay / Close anyway or Stay / Switch anyway. Saved input
leaves immediately; tab activation and pane-only closure are retention, not exits.

A pending confirmation captures account/tab/lane/input and action generations.
Before executing after recovery or confirmation, recheck those identities, latest
input, resource lifecycle and whether this remains the last context. Stale consent
must not discard new input, another tab's context or another account's work. Stay
changes nothing. Close anyway releases only the abandoned view context and stops
new autosave for that discarded input; retain original unknown command evidence
until reconciliation. Never promise rollback, unsent-input persistence or automatic
consequential confirmation. Browser unload retains the existing limited warning.

## Public history and closed-tab replay

Reuse the closed active snapshot `{v:1,tabKey,activePaneKey,panes:[...]}` and bounded
64-entry public anchor cache. Checkpoint before deliberate public transitions.
Activation, creation and closure push one entry; scroll, pane activation, typing,
renaming and tools do not push. Replay never pushes and never restores private
associations/text or historical authorization.

A valid snapshot naming a live tab activates it and updates its public arrangement
only, preserving that tab's *current* authorized private associations. A closed
snapshot identity creates a public-only tab with that same key; it inherits no
study, note, custom label, selection or pending action. Repeated replay reuses it.
Missing/invalid snapshot uses validated URL with fresh public identities, no
fabricated prior private context. Preserve initial/StrictMode stable-key semantics.

At12 tabs, hold current layout and expose Choose tab to close and restore with
explicit named target choices and Cancel. Preserve the validated pending snapshot
and exact incoming entry identity; selecting a victim uses the same last-context
guard. Recheck entry/pending/layout/account/input generations after asynchronous
recovery before atomically removing that victim and restoring the public-only tab,
without a push. Stay/Cancel cancels the pending victim/consent and closes the chooser; keep the
exact unmatched-entry marker and suspend held-layout checkpoints/collection until
ordinary navigation commits its actual arrangement. Offer explicit Choose tab to
close and restore retry. Ordinary navigation or intervening layout changes
invalidate the former pending action; cancellation never overwrites the incoming
public snapshot (canonical decision357). Never overwrite a live tab implicitly. Pending
restore UI must explain that the current arrangement remains displayed; it cannot
make unrelated current references collectable under the pending URL. Suspend native
checkpoints for the held arrangement while the actual entry names the pending
restore; retain outgoing anchors only under its captured old entry identity.
Invalid/missing snapshots seed a fresh public-only destination from the validated
URL and follow the same capacity rule, never attach the current private context.

## Proof and impacts

Before any runtime refactor/helper draft, observe characterization passes for
existing note/creation/unknown-operation/delete/account/focus behavior, then a
runnable missing-tab acceptance red. Record focused controller/context/editor reds
before each behavior change; do not reconstruct chronology by removing source.
Test inherited identity versus separate context, same-note single lane, distinct
note caret/IME/atoms, offscreen save/create acknowledgements, current account
masking/deletion across tabs, last-context recovery/changed-input stale consent,
12-tab cap and closed-tab replay through guard cancellation/intervening navigation.
Qualify exact push counts, full canonical refs, malformed links, independent anchor
replay, keyboard focus/overflow and mobile viewports with tools open.

Run component/browser/build checks only. Native SQL/migrations, actual
Auth/Identity/Access/app/session integration, KDG55481/55482, live signup,
physical-device interaction and release remain final-phase gates. No production
activation, provider/deployment change, Access/Notification/Leave implementation.
Preserve dirty/concurrent work. Scaffold/shared UI: app-specific until proven neutral
reuse; agent context: no new rule; docs: this contract/evidence/canonical handoff;
ADRs: no amendment. The component delivery and focused evidence do not close parent review/regression
or any wider integration, physical-device or release gate.
