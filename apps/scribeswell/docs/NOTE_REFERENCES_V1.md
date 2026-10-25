# Passage links inside personal notes — bounded contract

**Implemented as development/test opt-in code with contract/component evidence; final native and actual-owner integration remains pending.** CAP-3/ST-09–10 subset, consuming the existing
[passage identity](PASSAGE_REFERENCES_V1.md) and [private notes](PERSONAL_NOTES_V1.md).
Personal-note reading/editing remain in the same Analysis → Notes surface. Full
highlight/phrase-context, sharing and device acceptance retain their canonical gates.

## Closed document extension and old-client safety

Keep DocumentV1 and every ordinary v1 serialization/limit unchanged. Add DocumentV2:
exactly `version:2,blocks`, with the same paragraph/list/text/external-link structure
and one extra inline `{type:'passage_link',reference,label}`. Reference is the strict
pinned PassageReference; label is scalar Unicode plain text,1–200 codepoints. No HTML,
URL, marks, extra fields or nested links. External-link content remains text only.
Passage links are invalid in DocumentV1. Connections/highlights remain exact empty
arrays. No source words, scripture quotation or duplicated passage entry is inferred.

New insertion generates the canonical English reference label with existing formatter;
reading preserves a valid stored plain label. The existing document-node/text budget
also counts passage-link labels and reference models; existing65536-byte body and
JSON depth/node limits remain. Reject malformed, excessive or unsupported content
without truncation, unsafe rendering or candidate/payload diagnostics.

Explicit passage insertion upgrades that note document to2. New edits retain2 even
when the last link is removed; ordinary untouched notes remain1. No blanket backfill,
new SQL migration, command/version or receipt shape. Current JSONB constraints suffice.
Under the existing parent→note locks, after current/lifecycle/revision validation and
before mutation/receipt, reject stored document2 → submitted document1 with safe409
`note_format_unsupported`, null details, existing fixed error envelope/no-store policy.
Fingerprint/replay normalization of existing v1 commands stays byte-equivalent.
An already committed original v1 operation may replay its original acknowledgement
after current lifecycle checks; it must not replace the current v2 value. New attempts
cannot downgrade it even if they submit the current revision. Fresh v1 notes/ordinary
replacements remain supported. Widening NoteView alone is insufficient protection.

Add the machine code consistently to error status/OpenAPI/generated TS and frontend
terminal save handling. It pauses automatic saving, keeps local input and uses the
existing conflict/exit safeguards; never silently retries as a new operation, converts
away links or claims saved. Use plain recovery wording: Reload to continue editing.

## Editor insertion and deliberate navigation

Reuse BookChapterSelector rather than invent another reference parser or dialog.
Add Insert passage reference to the existing formatting toolbar. Capture an in-note
caret/range before picker focus with account/note/lane/input generations. Confirm
inserts one atomic safe inline at that caret; for a selection collapse to its end
and keep selected writing. Without an in-note caret, explicitly invoked insertion
may use the current note's end. Cancel/invalid numbering leaves document unchanged.
Reject stale note/account/input or detached ranges without editing another context;
retain editable reference input so the reader can place the caret and try again.
Do not insert during IME composition. Preserve Hebrew/English, direction, lists,
formatting, adjacent text and useful caret/focus on confirm/cancel.

Represent the atomic inline with editor-owned reference metadata and safe text, not
submitted HTML or URL-derived authority. Recognize it before generic SPAN parsing;
validate identity/label on read. Corrupt or foreign nodes fail the existing unsaved
input path. Pasting stays plain text; dropping arbitrary markup remains rejected.
Backspace/Delete can remove the whole inline; subsequent serialization retains2.
Repeated parser/draw/toolbar cycles must neither duplicate nor lose links or text.
Stage and validate insertion before changing live writing. Use the existing native
editing history so insertion/deletion and surrounding typing Undo/Redo coherently.
Per-editor metadata may rebind reconstructed atoms only during controlled native
commands or trusted native history input; ordinary copied metadata remains refused.
Empty editable caret positions carry no stored marker or character. Native deletion
removes one adjacent owned atom without changing surrounding writing.

The agreed reading/editing distinction uses a compact Read note / Edit note control
within the same Notes tab, defaulting to today's editing behavior. Keep the same note
lane and editing DOM/context while reading; hiding is not exit or a new save lane.
A reading view uses the same safe grammar, plain text and authorized current note.
It may show the coherent local note value with its existing truthful save status;
invalid/composing input cannot switch to a misleading stale reading view. Switching
back retains caret/input. No second copy or title-required note workflow.

In editing, clicking a reference positions the caret and offers Open passage, without
navigating. In reading, activating a reference opens it directly. Both delegate to
ReaderPage's existing active-pane controller with the complete range; retain current
note/lane and other panes. Reference-only Matthew clearly shows unavailable text.
No highlight implementation/paint is implied. Read/Edit switching creates no browser
navigation history. Open uses existing public reference URLs, never private note IDs.

StudiesPanel preview renders link labels as plain text without assuming `content`.
Other document consumers must handle both formats without erasing unknown nodes.
Ordinary source links, existing autosave, original-operation retries, conflicts,
account/navigation guards and public reading remain intact.

## Compatibility and final integration

This is development/test opt-in only; production Studies remains disabled. Before
richer-write activation, deploy/qualify a read-aware previous version and coordinated
browser/server adoption under ADR-0020. A prior server's safe refusal of rich content
is **not** seamless compatibility. Do not enable richer writes while unsupported
previous servers must continue reading those notes; no rollout/activation now.

The historical SQL fixture imports live NoteView, so it alone is not prior-format
proof after widening. Preserve that existing frozen fixture byte-for-byte. Add a
separate actual baseline contract/storage snapshot with a recorded full revision and
hashes, isolated from the widened DTO import, to demonstrate ordinary compatibility
and actual prior-format refusal. Test the current server's locked downgrade fence
with a legacy v1 payload at the genuinely current revision, no mutation or receipt.

ATDD observes missing insertion/format behavior before implementation; focused TDD
covers closed grammar/budgets, v1 unchanged serialization, transition refusal before
writes, replay exception and safe errors. Desktop/mobile component checks cover
insert/cancel, caret/IME/mixed text, list/direction/formatting, reading versus editing
Open, full range/reference-only navigation, same lane/no collection writes, save/reload,
unknown operation/conflict and stale note/account callbacks. Build/reproducibility
checks run now. Prepare native original-receipt/no-downgrade/previous-consumer and
actual-owner UI plus independent SQL scenarios for the final integration phase.
Do not run native/owner/session integration or use shared KDG ports now (direction266).
Actual phone keyboard/selection, live signup and production release remain unqualified.

Impacts: application-specific editor/document/navigation; no neutral shared UI or
scaffold promotion, accepted ADR or agent-context change. Reuse existing migration
helper unchanged; no migration needed. Update this contract, existing app notes,
source evidence and canonical memory together; consume Access HTTP as-is and implement
no competing owner, Leave/factory, notification, grant or production configuration.

## Delivery status — 2026-10-25

The closed format2 DTO, locked downgrade fence, generated wire, atomic editor
insertion, same-DOM Read/Edit and active-pane Open are implemented. Ordinary format1
remains supported. [Delivery evidence](NOTE_REFERENCES_EVIDENCE.md) records exact
commands, requirement traceability and remaining qualification. A byte-frozen actual
baseline contract/storage pair is isolated from the widened DTOs; the earlier
historical SQL fixture is untouched. No migration, activation, provider or shared KDG
port was used. Prepared native and actual-owner UI/SQL scenarios remain unexecuted
until the final integration phase under direction266. Read-aware previous-version
qualification and coordinated browser/server adoption remain activation prerequisites.
