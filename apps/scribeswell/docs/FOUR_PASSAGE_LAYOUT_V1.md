# Four-passage public reading layout v1

Status: adopted contract with component implementation in review; executed browser
evidence and remaining qualification are recorded in
[the layout evidence](FOUR_PASSAGE_LAYOUT_EVIDENCE.md). Consumes canonical CAP-6/ST-16/ST-31/ST-34 and the
[reader interaction direction](../../../_bmad-output/specs/spec-scribeswell-studies/reader-interaction.md).
The approved four-pane direction supersedes the two-pane limits, automatic
selection clearing on Compare and fixed keep-pane-1 closure in
[PASSAGE_COMPARISON.md](PASSAGE_COMPARISON.md). Its independent navigation,
public access, scrolling, error isolation and analysis attribution remain binding.

## Bounded outcome

One public workspace supports one to four ordered, stable-keyed reader panes.
Workspace tabs, per-tab private associations, cross-tab edit lanes and durable
same-device restoration follow separately; this slice neither implements nor
removes them. Existing StudiesProvider, StudiesPanel and NoteEditor stay outside
pane-keyed lifecycles. Layout changes never create/delete notes, flush input just
because a pane closes, or replace the current study/note. All public layout work
is independent of sign-in and current Access availability.

The user delegates routine technical decisions and continued implementation.
No new user-intent choice, migration, owner-service change or external side effect
is needed. The limits and geometry below close the bounded technical gates for
this slice, subject to executable qualification.

## Semantic actions and provenance

- Add reader pane duplicates the **complete canonical reference** of the active
  pane, inserts immediately after it, activates the new pane and opens its picker.
  Cancel/Escape keeps that pane at the duplicated reference and returns focus to
  its picker trigger. The accessible name distinguishes this action from Add to study.
- Open here targets the active pane, including when analysis still describes a
  different visible pane. Open beside inserts/activates adjacent to active with
  the supplied reference and no picker. Identical references are permitted.
- At four panes, either action that needs another pane opens an accessible explicit
  replacement dialog naming all four panes and references. Cancel changes nothing.
  Replacement is a fresh navigation of the chosen existing pane; no implicit victim.
  For Add, replace with the captured active reference and open the picker. Do not
  advertise Open in new tab until that separately delivered action exists.
- Close removes only the chosen pane. Closing active selects the nearest surviving
  neighbor (previous if present, otherwise next); survivors keep identity/position.
  Hide the final Close control **and** reject a semantic final-pane close.
- Each pane owns selector and sequential chapter arrows. Merely activating a pane
  changes no reference and creates no passage-history push. There are no independent
  pane-history ledgers/arrows. Numbering is presentation, never identity.
- Selection identifies stable pane key, navigation generation, canonical source,
  chapter/verse and exact word. Navigating/removing its source invalidates selection;
  adding another pane does not. Same word ID in another pane is a different origin.
  Late chapter/morphology/preview completions cannot select a pane, reopen a tool,
  resurrect closed analysis or steal focus. Validate morphology identity in both
  public and Studies analysis rendering. Hidden phone-origin selection clears as
  in the current reader; note ownership/write destination stays unchanged.
- Existing focus-mode anchor/clamp handling and Escape focus return remain. Tool
  toggles, resizing, reader navigation, adding/removing panes and browser replay
  preserve mounted writing, IME composition, pending-operation identity and recovery.
  No private request is caused merely by a public layout transition.

## Single public reference and wire owner

Reuse the pinned catalogue and canonical reference validator in
`web/src/lib/passage-references.ts`; do not create another reference vocabulary.
Full inclusive ranges, catalogue/version/versification and reference-only entries
round-trip without truncation. Reference-only NT passages issue no text/morphology
requests for an invented corpus. Existing Zod is available; no new dependency is
needed. One closed codec owns URL and snapshot parsing and types; parser helpers
are handwritten app code, not hand-edited generated API artifacts.

New URL parameter: `reader=JSON.stringify({v:1,panes:[{ref}],active:0})`, encoded
once with URLSearchParams. `active` is a zero-based index; panes number one to four.
Enforce 4096 characters on the complete serialized public reader query fragment
(`reader=` plus its encoded value); unrelated query/hash fields are outside that
bound and preserved. Reject unknown fields/versions, duplicate reader parameters,
invalid references and invalid active indices. A supplied invalid new parameter
shows a safe Invalid reading link message and one Genesis 1 default; never blend
its fields with legacy input. Missing new format uses the existing legacy
book/chapter/verse/compareBook/compareChapter/compareVerse and range-end parser,
with catalogue-valid references and safe fallback. Preserve valid old links.
Preserve the existing malformed-coordinate protection: a fallback is a public
display location, not a validated user-requested passage. Invalid legacy/new
input must not expose Add current passage for that fallback until an explicit
valid navigation/selection resolves it; opening Studies must not rewrite the
malformed URL. Add passage's ordinary explicit picker remains available. Keep
the existing malformed-coordinate regression assertions.

All deliberate new URL writes emit only `reader`, removing owned legacy fields
including range ends and preserving unrelated query/hash/path/basename. A valid
new format takes precedence over legacy fields. Sharing includes only active public
references/index, never opaque layout keys, private IDs/titles, input, account or
invitation proof. Pane activation alone may update this URL with replace, never push.

### Standalone account confirmation return

The existing fixed-origin/app-root account callback consumes this qualified public
wire when `reader` is supplied: validate with the same closed codec and serialize
only its canonical references/active index. Preserve complete ranges, at most four
panes and existing encoded-size bound. Drop unrelated/private/credential fields and
fragments. Invalid/duplicate/oversize/unknown-field new input returns the safe app
root; never blend legacy into a rejected new layout. When `reader` is absent, retain
the already-qualified legacy account-return allowlist behavior. This is consumer
compatibility for the new reader representation, not provider/mail activation or
private workspace restoration. Intercepted signup requests must prove the exact
`emailRedirectTo`; no live provider change is authorized.

## History, snapshots and anchors

Closed public snapshot:
`{v:1,tabKey,activePaneKey,panes:[{paneKey,ref,anchor?}]}`. One random local tabKey
identifies this workspace without implementing tab UI or private associations.
Local layout keys are nonempty strings of at most128 characters; use random UUIDs,
unique pane keys and valid active membership. At most four panes, at most8192 UTF-8
bytes. No unknown fields, duplicate identities or private data. Match snapshot
references/order to the validated URL before using identities/anchors; invalid or
mismatched snapshots fall back to URL with fresh public identities.

Anchor: closed `{chapter,verse,word?,offset}`. Coordinates are catalogue-valid;
chapter equals the displayed reference's starting chapter. Word is the source API's
**one-based position within verse**, not word ID or match key; optional integer1–4096.
The source enumerates from1 (`corpus_source.py`, `bible_service.py` contiguous-word
validation). Larger positions omit word and fall back to verse, never truncate it.
Offset is an integer CSS-pixel distance from scrollport top, bounded -512…512;
capture clamps offset, parser rejects out-of-bound supplied values. Capture the
first visible intersecting word; omit anchors for ref-only/loading/error/empty views.
Fallback is word → verse → explicit reference/chapter start. This is best-effort
public position recovery, not private-highlight identity or source-retargeting proof.

React Router remains owner of URL navigation. Installed Router6.30.4 stores user
state in native `history.state.usr`, with reserved outer `key` and `idx`.
Namespace the public snapshot at `usr.scribeswellReader`, preserving unrelated user
and outer fields. A same-URL native `replaceState` helper may checkpoint anchors
without triggering Router; omit its URL argument and never forge popstate events.
Read current native state before merging, not stale useLocation state. If existing
`usr` is a non-null non-record (array/primitive), preserve it untouched and skip the
snapshot write; URL plus the bounded public cache still permits safe replay.
Do not silently wrap or replace another consumer's state. Null/missing usr may
become a record. Preserve Router default-key/absent-native-key semantics.
Router pushes/replaces construct only `{usr,key,idx}` themselves: capture unrelated
outer fields before navigation and merge them into the newly created entry afterward,
keeping its **new** key/idx. Own-command acknowledgement must work without a snapshot
(including primitive/array usr), using controller memory and actual resulting entry
identity, not a public command marker or permanent visited-entry set.

Before every deliberate reference navigation, pane addition, closure or explicit
replacement, synchronously capture/checkpoint outgoing anchors, then issue exactly
**one Router push** with the next public URL/snapshot. Fresh identical Open also
issues a new seek generation. Activation, scroll, selection, typing, tool/focus
changes cause no push. A public-only, bounded64-entry in-memory anchor cache may
retain fresh scroll positions by actual browser-entry identity and matching refs;
it is not an independent navigation stack or a durable-restoration promise.
Periodic/deferred checkpoint work verifies captured key/idx/href before writing so
it cannot overwrite an entry reached by Back/Forward. Preserve unrelated state
also when pushing; for non-record usr keep it and omit new snapshot.
Keep the URL's active index current through Router replace on pane activation;
classify this as activation only, transfer matching cached anchors to the resulting
new Router key and do not restore/seek. Pointer/focus activation may precede a
selector/chevron click: synchronously current controller refs and coalescing prevent
stale closure/entry writes. Pane navigation captures its key; Open here/beside resolves
current active at the semantic boundary. Capacity dialog confirmation revalidates
captured layout generation and surviving replacement key.

Ingest initial URL and Router/POP location changes exactly once per entry identity
and URL. A controller's own push acknowledgement must not restore/seek again.
This means once per **incoming navigation occurrence**, not once forever for an
entry: repeated Back/Forward to the same entry must restore each time. Consume
own-command acknowledgements once and distinguish PUSH/REPLACE from POP.
The app runs React StrictMode: effect replay must not create history pushes,
duplicate restores or lose a legitimate one-shot acknowledgement. Keep the existing
BrowserRouter basename/AuthProvider/StudiesProvider ownership in App.tsx.
Replay restores validated public layout/anchors without pushing or changing private
study/note/authorization. Prefer matching cached anchors, then matching snapshot;
without either, use the URL reference. Direct URL uses explicit verse start;
matching history anchors take precedence on replay/refresh. Each restore/explicit
Open seek applies once per navigation generation after pane is visible/data ready.
Later reveal/resize/tool switch cannot rewind it. Requests remain scoped to pane
and navigation generation; do not rely solely on AbortController.
Replay invalidates pending captures/seeks before new rendering. Distinguish
restoration/geometry-generated scrolling from deliberate user movement so a clamp
cannot overwrite an outgoing saved anchor. Existing focus-mode anchor logic and
pane target seeking must cooperate with this controller rather than restore twice.
Preserve not only JSX/editor DOM identity but the current Studies lane object:
NoteEditor redraws on lane changes. Characterize the same contenteditable node,
composition/caret/owned passage atoms and original pending operation across public
add/close/replay; never clone lanes or key the tools subtree by layout.

## Responsive qualification choices

Measure the **available reader container**, after current tool widths, rather than
assuming viewport width. Minimum pane width320px, gap16px: three columns only at
992px available, otherwise two columns at656px, otherwise one visible pane with
an accessible named switcher. Four panes use two-by-two, never four narrow columns.
Two panes use two columns at656px; one pane keeps existing readable maximum.
If a two-row grid cannot provide200px usable height per row, use one visible pane
and the switcher. Qualify desktop, intermediate widths, phone, reduced height and
tool/focus transitions. Keep overflow inside independent reader scrollports; long
labels wrap/truncate accessibly. Preserve visible pane positions through geometry
changes. Existing phone Studies/Analysis use full-width replacement, not squeezed
sidebars. These choices may be refined from measured failing layout tests within
the same approved direction; record any change and its evidence.

## Proof and delivery limits

First characterize current range navigation, independent scroll/error/late-fetch
isolation, focus clamp/Escape and mounted editor/IME/pending-operation behavior.
Observe missing Add/four-pane acceptance failure, then focused codec/controller
failure before implementation. Test every transition above, malformed bounds,
unrelated history state, exact push counts, interleaved Back/Forward, same-reference
different positions, repeated seek, stale checkpoint/response/seek, final close and
capacity Cancel/replace. Legacy-emitted URL/binary Compare expectations may change
only where this approved contract supersedes them; keep behavioral assertions.

Run component/browser/build checks only in this phase. Actual migration/SQL,
Auth/Identity/Access/app integration, live signup/confirmation, physical iOS/Android
selection/IME/keyboard and production release remain final gates. Do not acquire
KDG55481/55482. Preserve all dirty/concurrent README/canonical/other-app work.
Standalone account creation remains required and retained. Sharing/invitation/
Notification owner contracts remain separately gated; no competing Access path.

Impact: app-specific reader/controller/codecs only; no scaffold or shared-UI
promotion before proven neutral reuse, no new agent rule, no ADR amendment,
database/API/provider/deployment change. Record exact requirement-to-test mapping,
observed chronology and all failed attempts in FOUR_PASSAGE_LAYOUT_EVIDENCE.md.
