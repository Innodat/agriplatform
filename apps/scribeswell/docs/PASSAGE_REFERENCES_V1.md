# Collected passage references — delivery contract

**Implemented as opt-in code with component/contract evidence; final native and owner integration remains pending.** This supplies the
ordinary collection subset of CAP-2/ST-04–06. The existing Studies opt-in remains
required for private writes. Public reading and standalone signup remain independent.
Canonical UX/data requirements and accepted platform ADRs retain authority. Note
links/connections/highlights, workspace expansion and sharing consume this reference
identity later; this slice does not change their saved grammar or claim delivery.

## Versioned reference inventory

The owning generator `tools/py/build_reference_catalogue.py` reads the existing
`backend/corpus_source.py::BOOK_METADATA` and `scripts/hebrew.json`, pinned SHA-256
`c2d8e9e565be4ee69f938b444e5e0dc37fdfd0d9ccb185d1a5f8d95fab91c498`. Derive the39
Tanakh book IDs/names/order and actual per-chapter verse maxima from those inputs.
Use `oshb-hebrew-json-c2d8e9e5` as their numbering identity: an artifact identity,
not an unproved equivalence to another edition's numbering. Do not change the corpus.

`data/reference-catalogue/nt-verse-counts.json` supplies27 reference-only NT books.
Its factual chapter/verse maxima were extracted from CrossWire's primary
[canon.h at SVN3765](https://crosswire.org/svn/sword/!svn/bc/3765/trunk/include/canon.h),
SHA-256 `782e7a603cdfb45ddfd6eed9d31a639929fb928b47c7042d83c8ee9b76af078a`.
It contains no copied implementation or scripture text. Their numbering identity is
`crosswire-kjv-3765`; do not use these NT maxima to reinterpret Hebrew references.
All66 book IDs are OSIS IDs; preserve existing39 numeric corpus IDs separately.

Generate one deterministic JSON inventory under `data/reference-catalogue/` plus
its browser copy through this generator, carrying a generated-file warning/ownership
manifest. The semantic inventory digest is its `catalogue_version` (SHA256 lowercase
hex); version calculation excludes its own version field and uses canonical JSON.
`catalogue_id` is `scribeswell.references.v1`. Backend/browser consume identical
outputs; `--check` detects drift and changed pinned inputs, without network access.
Store provenance and exact numbering labels. No database/network import at runtime.

Each book carries `book_id`, English/Hebrew display names (Hebrew may be absent for
reference-only books), declared aliases, chapter verse maxima, `versification_id`
and `text_support` (`hebrew_corpus` or `reference_only`). Hebrew support means the
reader supports that source family; it does not promise the local text is imported.
Actual reader requests determine availability. NT references never fabricate words.

Aliases include exact OSIS IDs and existing full English/Hebrew names, numeric
variants of Roman-numbered book names, Psalm/Psalms/Ps, Song of Songs, תהלים/תהילים,
and Matthew/Matt/מתי. Other abbreviations require an explicit inventory entry.
Use NFC, English case folding, whitespace collapse, Hebrew-point removal and declared
book punctuation normalization; never fuzzy-guess an ambiguous abbreviation. Alias
collisions produce a typed ambiguous result; keep editable input and offer choices.
Hebrew numbers use the existing gematria convention with optional geresh/gershayim;
accept only canonical positive forms within inventory bounds, including טו/טז.

Canonical reference has exactly `catalogue_id`, `catalogue_version`,
`versification_id`, `book_id`, `target`. Target is `{kind:'chapter',chapter}` or
`{kind:'verse_range',start:{chapter,verse},end:{chapter,verse}}`. Single verses repeat
endpoints. Integers are strict positive bounded catalogue values (no booleans,
coercion, verse0, foreign version or guessed conversion). Same-book cross-chapter
ranges are supported only with parser/picker/renderer tests; cross-book ranges are
separate references. A whole chapter remains a chapter, never expanded into verses.

Typing `Psalm110:1`, `Ps 110:1–3`, `תהילים קי:1`, `Genesis1:31–2:3` and
`Matthew26:63–64` must resolve after normal book/number spacing; reject `Ps2:10–13`,
reversed/missing/out-of-bounds ranges and unknown/ambiguous books without mutation.
Keep reference validity separate from imported text availability and service outages.

## Private collection wire

Reuse strict DTOs, bounded decoder, generated OpenAPI/TypeScript, current owner HTTP
Access, safe machine-readable errors and private no-store responses from
`PERSONAL_NOTES_V1.md`. Add:

- `GET /api/studies/{study_id}/passages` returns exactly
  `{study_id,revision,items}`; item is exactly `{id,reference}`. Order is stable.
- `PUT` at the same path accepts exactly `{operation_id,expected_revision,items}`.
  IDs use existing nonnil UUID rules, revisions positive bigint decimal strings.
  Maximum200 entries; duplicate IDs or duplicate canonical references are invalid.
  Overlapping nonidentical ranges remain distinct. Reference validation uses the
  pinned catalogue and version. No submitted attribution/owner/order override.
- Command `study.passages.replace`, version1;200 existing compact OperationAck with
  matching study ID, null note ID and **passage-list** revision. Add command-correlated
  schemas/lookup and safe409 `passage_revision_conflict` with existing typed
  `{expected_revision,current_revision}`. Existing safe status/depth/node/deadline bounds apply.
  Collection commands alone allow131072 body bytes so200 complete range entries fit;
  note/title/enrollment bodies retain65536. Enforce the same selected bound in the
  HTTP reader and strict decoder; limit+1 fails without authority/storage effects.

An existing/new study with no collection rows has the logical empty list revision1.
No startup backfill or trigger on existing study creation is required. First changed
list persists revision2; first no-op empty replacement receipts revision1 without
creating list state. All later revisions are independent of title and note revisions.

After fresh authority outside DB locks, take operation lock, active owner study lock,
then collection coordination/rows in stable order. Original identical operation
replays original acknowledgement after current ownership/lifecycle checks; changed
payload/path mismatches409. Under the parent lock compare current list revision,
including logical1, before writing. Identical ordered IDs/references receipts without
revision/time changes. A changed list and receipt commit atomically, one revision
advance, current actor/server UTC attribution; bigint overflow refuses. Return errors
without leaking candidate text, private data or caller credentials.

Preserve IDs of retained entries. IDs removed and later deliberately re-added may
receive fresh identity. Client candidate addition reuses an existing exact canonical
reference and its ID; never expand/merge ranges or duplicate entries. Removal changes
only the collection: note content/connections/highlights and corpus stay unchanged.
Do not resurrect removed entries by replaying old committed commands.

Use ordinary new migration0003 for a normalized owner-scoped list header and ordered
entries, with composite parent FKs, positive revisions/positions, unique IDs/order and
canonical reference uniqueness. Enforce structural target shape/order in database
constraints; catalogue/domain validation remains API-owned. All mutable/immutable
rows use server actor/UTC attribution as appropriate. Header rows start at revision2.
Use existing runtime role, FORCE RLS, least-privilege SELECT/INSERT/UPDATE/DELETE only
as needed; immutable scope/creation attribution. Receipt constraints widen compatibly
for this null-note command. Keep0001/0002 immutable and old note/title commands and
public reads working. Controlled failure blocks activation, forward recovery only.

## Picker, outline and navigation

One reusable app-specific picker serves reader navigation and collection. Use the
existing browsing shell/book+chapter grid, with one editable reference input. Typing
positions/highlights book/chapter and visibly retains verse/range context. Enter or
clicking the matching chapter confirms the complete valid reference and closes;
there is no additional Confirm button. Clicking another chapter clears old range.
Escape/click-away cancels without effect and restores initiating focus. Exclude text
editing from any reference shortcut; preserve existing keyboard/reader controls.

Study outline remains notes-first, then separate Passages with Add passage, ordered
labels, explicit Open and Remove. Add current passage pre-fills the active reader
reference and permits range adjustment. Add preserves reader positions, current note,
input and save lane. Duplicate addition explains Already in this study without a
second entry or lost input. Same-book cross-chapter labels retain both endpoints;
Open reveals the first chapter/start verse, retains complete range identity and
supports chapter arrows; it does not silently shorten saved ranges.

Only explicit Open navigates the active reader through its existing controller/URL
path; retain note context and other pane positions. NT Open shows the reference and
Text unavailable without fabricated text or word/highlight actions. Available-family
load failure shows truthful Retry; an outage does not invalidate/remove a reference.
Preserve public URL/back/forward and old one/two-pane behavior. Do not implement the
proposed full workspace URL wire in this slice.

Collection editing has one in-memory operation lane per study, separate from note,
creation and title attempts. Freeze snapshot/operation while executing or uncertain;
explicit Retry resolves the original operation via existing bounded lookup/replay.
No later collection operation overtakes it; closing the picker/tool does not cancel
in-flight work. Warn on unload for unresolved attempts without persistence/rollback
promises. Acknowledged success rereads current list, never applies stale candidate
as current state. If that read fails, retain confirmed success and retry only the read.
Revision conflict retains the intended addition/removal; offer deliberate current-list
reload/review, then require explicit new action with fresh operation/base revision,
never automatic rebase/overwrite. Account/navigation/read generations reject stale
results; account replacement clears private state. Current access loss keeps public
reading usable. Metadata and notes remain independently usable while collection fails.

## Verification and integration boundary

Observe smallest relevant contract/browser acceptance failure before implementation;
focused TDD covers parser, generated inventory parity, strict refs/DTOs, unknown
operations, no-op/conflict and navigation/input safety. Desktop/mobile intercepted
component acceptance and build checks run during implementation. Record requirement
traceability and exact commands/results, including failures without changing expected
business results. Source integrity checks are not runtime proofs.

Per direction266, **final integration is deferred until the agreed implementation
sequence reaches its final test phase**. Do not start/use/stop any shared KDG instance
or ports55481/55482 now. Prepare native tests for controlled0003 rollback/retry,
restricted SQL/RLS/constraints, previous consumers, races and immutable notes/title;
prepare actual-owner browser/UI+independent SQL collection proof. Mark these pending
until actually run in that final phase; neither mocks nor generation closes them.
Production/real signup/device/manual-user gates remain explicit.

Impacts: app-specific reference/picker/storage, existing shared migration helper;
no shared UI/scaffold promotion until proven neutral reuse. Agent context unchanged,
accepted ADRs unchanged. Document owner contracts/canonical memory in the same item;
no competing Access, Notifications, Leave or factory implementation.

## Delivery status — 2026-10-25

The catalogue, strict API/DTOs, independent collection storage/lane, reusable picker,
notes-first outline and explicit reader Open are implemented in this delivery.
[Collected passage evidence](COLLECTED_PASSAGES_EVIDENCE.md) records executed checks,
requirement traceability and failures. Controlled0003/native owner-role proof and the
actual-owner browser plus independent SQL run are prepared, not executed, under
direction266. No KDG instance/ports, providers, activation or deployment were changed.
No native permission or transaction guarantee is inferred from HTTP/component doubles.
