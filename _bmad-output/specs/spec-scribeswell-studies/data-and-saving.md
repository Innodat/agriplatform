# Private-study data and saving — Scribeswell contract draft

Derived from the feature decision log and inspected reader/database contracts.
**Owner:** Scribeswell. **Status:** proposed technical contract under adopted
AD-3–AD-9. Broader schema/runtime readiness remains open; the first ordinary-note
wire subset is executable as described below.
[Architecture](ARCHITECTURE-SPINE.md) and [UX](ux-behaviour.md) retain authority.
No database, API, corpus import or editor package is changed by this document.

## First create/write/reopen wire subset

Decisions231–232 adopt the app-owned [personal-notes v1 contract](../../../apps/scribeswell/docs/PERSONAL_NOTES_V1.md).
Its closed DTOs, bounded decoder and generated OpenAPI now feed opt-in private HTTP,
Access adaptation, restricted SQL persistence and ordinary rich-text autosave/reopen.
The adopted source owns exact limits, error codes, cursor shape and execution bounds;
reference/highlight/privacy/copy/delete extensions below remain proposed. Required
empty connections/highlights and refusal of passage-link nodes protect this first
writer; richer content requires compatible versioning. Decision236 closes the owner
interface dependency; event239 records native and browser evidence while independent
review corrections and parent acceptance are complete (event240). Production activation remains refused. Shared migration
helpers are consumed unchanged; no generic editor/save engine is promoted.

## Identity and relationships

Private entity/operation IDs are nonnil UUID strings. Revisions are positive
bigint decimal strings, never JavaScript numbers; timestamps are server UTC.
Account/actor evidence comes from the [Access owner contract](../../../platform/docs/architecture/contracts/scribeswell-study-enrollment.md).
Client owner/actor/timestamp/visibility overrides are rejected, not ignored.

| Record | Owned identity and invariant |
| --- | --- |
| Study | ID, owner account, title, optional introduction/source link, metadata revision and active/deleted lifecycle. Title is not identity; ordinary duplicate titles remain valid. Explicit untitled creation allocates an unused numbered default atomically per owner without imposing universal title uniqueness. |
| Study passage | Own ID, study, canonical reference and stable list order. Separate list revision. Duplicate canonical references in one study reuse the entry; overlapping ranges are distinct, never merged or expanded silently. |
| Note | ID, own study/owner account, immutable visibility kind `study` or `private_response`, document, explicit connections, highlights and one revision. No required note title. Owner must equal destination study owner. |
| Highlight | ID local to one note, freely selected `#RRGGBB` colour and source anchor. It has no independent write/version authority. |
| Provenance | Server-controlled source study/note/account identifiers and relation kind on a private response or independent copy. No required live source row and no cascade from another account's source. |
| Edit-base evidence | Note/revision/owner, immutable visibility/provenance and validated reference/anchor metadata for that revision. No historical note body, quotation or user-visible version browser. |
| Operation outcome | Owner account, command/version and operation ID, private request fingerprint and compact committed result. It is local to Scribeswell and grants no authority. |

Study metadata, passage-list and note revisions are independent. New note/mark
creation is explicit; selecting a word or inspecting another note changes neither
ownership nor the write destination. Note moves and permission overrides are not
introduced by this contract.

## One note aggregate

The editable value is exactly:

```json
{
  "document":{"version":1,"blocks":[]},
  "connections":[],
  "highlights":[]
}
```

Each connection has an ID and canonical passage reference. Each highlight has an
ID, colour and anchor. Omitted arrays are not a request to preserve old fields:
full aggregate writes require all three fields, strictly validated. Creation may
supply empty arrays/document. Server fields and provenance are separate read data.

A note's discoverable passage context is derived from explicit connections,
structured reference links and highlight segments. The study's collected passage
list is independent. Adding a highlight connects its passage to that note; inserting
a reference link does not collect it into the study or paint scripture. Removing a
collected passage leaves notes and anchors intact. No duplicate note body is stored
for passage/phrase/Word Analysis views.

## Structured document v1 — proposed closed grammar

| Node | Exact fields and allowed children |
| --- | --- |
| Document | Ordinary format1 retains its exact runtime grammar; designed format2 adds passage-link inlines under event277. Both carry `version`, `blocks` array of paragraph or list nodes. |
| Paragraph | `type: paragraph`, `direction: auto/ltr/rtl`, `content` inline array. Empty paragraph allowed. |
| List | `type: list`, `style: bullet/ordered`, `items` array of nonempty paragraph arrays. Nested lists are not introduced in v1. |
| Text inline | `type: text`, `text`, `marks` unique canonical array drawn from `bold/italic`. Plain text has empty marks. |
| External-link inline | `type: external_link`, `url`, `content` array of text inlines only. |
| Passage-link inline | Format2 only: `type: passage_link`, canonical `reference`, `label` plain text. It is not a scripture quotation. |

No arbitrary HTML, style/class/event attributes, images, embedded scripts or unknown
node versions. Nested links and links containing structural nodes are invalid.
External links require parsed absolute http/https URLs without embedded credentials;
unsafe schemes and malformed control characters fail validation. Study/source URL
fields use the same safe URL policy. Reading uses safe
DOM text and declared links, with safe new-tab attributes. Pasted formatting passes
through the same server grammar; browser sanitization alone is insufficient.

Preserve mixed Hebrew/English text; direction is presentation metadata, not a change
to scripture identity. Derive previews/search plain text server-side from this grammar,
not submitted HTML or a client-provided search index. Select byte/node/depth/URL limits
and editor-adapter conformance fixtures before implementation; this draft chooses no
editor library. Rejected or unsupported input is not silently truncated to save.

## Canonical references

Reference identity contains catalogue/version, versification ID, canonical book ID
and the closed target union:

- `{kind: chapter, chapter}` for a whole chapter.
- `{kind: verse_range, start: {chapter, verse}, end: {chapter, verse}}` for ordered
  inclusive endpoints within one book; a single verse repeats its endpoint.

Integers must exist in that catalogue; allow verse zero only if explicitly declared.
Proposed same-book cross-chapter representation requires matching picker/renderer
acceptance before adoption. Cross-book selections use separate references. Store
canonical IDs, not user-typed abbreviations as identity. English/Hebrew aliases and
mixed `תהילים קי:1` resolve through one versioned owner catalogue; ambiguous input
requires choice and invalid bounds fail. Do not guess a versification conversion.

Separate reference validity from text availability. Reference-only Matthew can
remain valid with notes/links; it cannot acquire a fabricated corpus/source or word
anchor. Existing Bible schemas do not supply this full reference catalogue. Events267–268
close the bounded collection design and source inputs in the adopted
[passage contract](../../../apps/scribeswell/docs/PASSAGE_REFERENCES_V1.md):
artifact-specific Hebrew numbering plus pinned CrossWire reference-only NT maxima,
with no conversion/text expansion. The bounded generator/parser/schema and consuming picker now have executed component
coverage (events271–272); native/actual-owner proof and corpus publication remain
unqualified. No richer note grammar or source-anchor support is implied.

## Exact word anchors

Proposed anchor fields: `version: 1`, `source_id`, `source_revision`,
`versification_id`, `tokenization_version`, and ordered `segments`. Each segment
contains its canonical verse, inclusive start/end word positions, observed word IDs
as decimal strings, and a server-validated `verse_token_digest`. Segments describe
one continuous selection, possibly across verses; distinct selections are separate
highlights. Every selected position must exist and belong to that verse/source.

The digest is SHA-256 over a versioned canonical encoding of the verse identity and
entire ordered `(position, surface_he)` token sequence; exact UTF-8 source text is
preserved, not stripped into lemma/match keys. The proposed byte encoding below fixes that comparison; the owning importer must
qualify it and prove revision/manifest integrity before delivery. Current numeric word
IDs and positions alone cannot establish persistence through replacement imports.

Reads derive anchor status without changing note revision:

- `valid`: declared revision AND exact verse/token evidence match, or an owner-verified
  compatible revision preserves the exact verse/tokenization evidence and positions.
- `needs_review`: available source evidence shows an incompatible/uncertain target;
  keep note and reference, suppress misleading precise marks and allow explicit repair.
- `unavailable`: current source evidence cannot be obtained; do not infer change,
  deletion or a new target from an outage.

Cross-revision validation cannot match another occurrence by string or lemma. A
changed verse without proven correspondence needs review even if the selected word
looks the same. Reselecting words explicitly replaces anchor evidence through the
whole-note save. No automatic quotation, old full-edition retention or permission to
change source data is introduced.

Existing unchanged anchors/connections may round-trip in a text edit using trusted
stored/base evidence even when source validation is unavailable. Anchor fields
must match that evidence exactly; reusing an ID cannot bypass new-anchor validation. New or repaired
anchors require current owner validation before private write locks. Failure rejects
the whole save; never silently discard the new mark or partially save only text.
An import racing a save may make the recorded revision need review afterward; it
cannot silently reattach the mark. D-5 must coordinate revision activation/validation.

### Corpus reality and proposed digest encoding

Inspection of the [schema](../../../apps/scribeswell/supabase/migrations/20260614000000_scribeswell_create_schema.sql),
[importer](../../../apps/scribeswell/tools/py/import_bible.py) and
[chapter service](../../../apps/scribeswell/backend/services/bible_service.py) establishes:

- Word IDs are serial database identities, unique by verse and one-based position.
  Import upserts on `verse_id,position` and can change `surface_he` while preserving
  that ID. IDs are observations, not immutable source-word identities.
- Imports verify and commit a chapter at a time. A final printed source-file SHA-256
  is process evidence, not an activated per-verse database manifest. Partial imports
  cannot be presented as one verified complete new edition.
- Current API responses have positions/surface/display text, but no source revision,
  tokenization version or verse digest. Existing completeness checks do not supply
  those new evidence fields. No public API or importer behavior changes here.

The `verse_tokens.v1` encoding contract is the following positional JSON array:

```text
["scribeswell.verse_tokens.v1", source_id, catalogue_version, versification_id,
 tokenization_version, canonical_book_id, chapter, verse,
 [[1, exact_surface_he], [2, exact_surface_he], ...]]
```

Serialize once on the server as compact UTF-8 JSON: no BOM/newline or whitespace
outside strings; retain Unicode scalar values (`ensure_ascii=False`), standard JSON
string escaping, and decimal integers. Reject invalid Unicode/lone surrogates.
Token positions must be the complete strictly contiguous sequence 1…N in source
order; chapter/verse and canonical IDs must validate against the owning catalogue.
The result is lower-case hexadecimal SHA-256 of those exact bytes. Browser-provided
hashes are comparison input, never authority for a new/repaired anchor.

Preserve source slashes, diacritics, punctuation and combining-mark order; do not
normalize Unicode, strip vowels/accents or use `display_he`, a lemma/match key or
Strong's code as the token identity. `display_he` may omit morphological separators;
that rendering difference does not turn a word selection into a morpheme anchor.
Any presentation/token mapping change needs separate source/tokenization evidence.

Database word IDs and source revision are deliberately outside the digest so an
owner-verified unchanged verse can compare across revisions or regenerated row IDs.
They remain part of the stored observation/proof checks. Equal hash alone cannot
cross source, catalogue, versification or tokenization boundaries. A changed verse,
even away from the selected words, needs review; matching selected words alone is
not correspondence proof. Do not rewrite historical observed IDs during a read.
A proven compatible current view may map the recorded positions to current row IDs
for rendering without changing the note; newly selected words require current proof.

[Executable digest fixtures](../../../apps/scribeswell/tests/fixtures/verse-token-digests-v1.json)
contain six explicitly synthetic
vectors: unchanged tokens with regenerated IDs/revision; changed text with reused
IDs; inserted token; and canonically equivalent but differently ordered combining
marks. They specify byte/hash expectations only, not actual scripture/catalogue
validation, server authorization or a delivered source-versioning system. The
unchanged [historical planning vectors](anchor-evidence-fixtures.json) remain as
design evidence; runtime tests consume the app-owned fixture.

The [bounded source-candidate delivery](../../implementation-artifacts/spec-scribeswell-source-evidence-candidate.md)
qualifies this pure encoding and full-artifact comparison prerequisite independently.
Representation checks and the selected source checksum/inventory do not establish a
scholarly catalogue or current database publication. Its candidate is explicitly
non-published; [publication](corpus-publication.md#bounded-source-candidate) retains
audit sealing, fencing and activation gates.
The [database-audit candidate](corpus-publication.md#read-only-database-audit-candidate-contract)
now implements independent source/database comparison in a read-only snapshot;
its successful historical observation is neither a sealed audit nor current proof.
Fencing and activation remain gated.

### Proposed source publication boundary

The [corpus-publication companion](corpus-publication.md) proposes one whole-source
manifest revision and a ready/updating/unavailable gate around the existing chapter
import transactions. It owns source-attempt fencing, full-audit activation, coherent
reader evidence, failure recovery and supported writer transition. It requires no
old full-edition storage and changes no current runtime by documentation.

New/repaired marks require coherent current published proof before private write
locks; unchanged stored anchors may still round-trip in a text-only edit under the
rule above. Source activation/schema/privilege/API qualification remains D-2/D-5
work. Do not substitute a process checksum, stale DOM or reused word ID for proof.

## Command and save protocol

Protected routes remain separate from the public Bible GET allowlist. Proposed
application routes below are relative to the Scribeswell API root; every request
checks current Access and then local ownership/visibility. All response variants
are private/no-store and use the shared safe error envelope.

| Command / proposed route | Required input and result |
| --- | --- |
| `POST /api/studies` | Operation ID and supplied optional title/introduction/source link. Server creates one study, returns ID/revision. |
| `PUT /api/studies/{id}` | Operation ID, expected metadata revision and complete metadata value; does not update notes/passages. |
| `PUT /api/studies/{id}/passages` | Operation ID, expected passage-list revision and complete ordered entries. Validate ownership and references; return new/unchanged list revision. |
| `POST /api/studies/{id}/notes` | Operation ID and complete note aggregate. Server supplies ordinary-note visibility, owner and new note ID. Private-response creation is a distinct authorized command with server-derived source/provenance. |
| `PUT /api/studies/{id}/notes/{note_id}` | Operation ID, expected note revision and complete aggregate. Update only that existing active note in the active own study; never upsert. |
| `GET /api/operations/{operation_id}?command=...` | Exact authenticated owner and closed command selector; return compact committed acknowledgement or unresolved, never note payload/fingerprint. |

Commands `note.duplicate`, `note.conflict_copy`, `note.delete`, `study.copy`,
`study.delete` and private-response creation have distinct command identities and
must receive closed dedicated OpenAPI routes before consuming stories. They are
not disguised generic create/update retries. Sharing commands belong to D-1/D-3.

One serialized client save lane per note covers text, connections and highlights.
Local edits may continue, but a second request waits until the previous operation's
outcome resolves. Coalesce later edits into the next complete snapshot. Save results
carry operation ID, note ID and committed revision; only acknowledgement of the
current local generation shows Draft saved. A delayed older result cannot reset
newer text or mark pending edits saved.

Under one short owner transaction, validate expected revision and active lifecycle
together, replace aggregate/owned relationships, advance revision once if changed,
and commit receipt plus required attribution. Identical no-op input acknowledges
without a revision bump. Lock the common parent lifecycle before child mutation;
study/note deletion and saves must serialize under the same declared lock order.
Access/source/provider waits happen before these locks.

Outcome identity is unique per account/command/version/operation UUID; bind the
canonical private payload through a versioned server-only fingerprint. Reuse with
changed payload fails `operation_payload_mismatch`. Never expose payload digests.
Unknown response or disconnect requires the same operation ID/payload and bounded
lookup/retry; an unresolved prior save blocks the next request. Lookup rechecks
current authority; unresolved is not proof of rollback. Receipts store compact
IDs/revisions only, with no automatic initial expiry.

## Conflict, duplication and privacy

A revision conflict pauses that lane with the local aggregate retained while open.
Review latest never merges it automatically. Use latest explicitly replaces the
local branch; Save mine as a new note submits one coherent local document/connections/
highlights snapshot with its base note/revision and a fresh conflict-copy operation.
Do not combine local text with the newer server's highlight collection.

Minimal edit-base evidence, recorded atomically per committed note revision, proves
original owner/visibility/provenance and previously validated anchors without storing
historical document bodies. Validate new anchors separately. The source note must
still be an active owned note and destination writable; stale evidence cannot revive
a deleted note/study. Current permission always applies. Allocate new highlight IDs
for the new note and preserve private-response visibility. No automatic base-evidence
expiry is selected for first delivery; cleanup requires a supported recovery policy.

Duplicate uses a currently authorized coherent source snapshot and destination
ownership, preserving all colours/references and source credit. Whole-study copy
includes only notes visible to the copier; another reader's private responses are
excluded. Viewers cannot reshare as author or write source content. Copies remain
independent. Copy transaction/snapshot bounds and large-study behavior require a
concrete owner plan before those stories; no partial copy is reported as complete.

## Private provenance, deletion and discovery

A private response is one note in its author's own destination study, always
owner-only even when that study is shared. Its highlights, snippets, counts, search
and copied private-response variants use the same visibility rule. Remembered
per-source destination changes affect future responses only; no implicit move.

Provenance stores opaque source IDs/relation kind, not a source note body or cached
teacher text/title. Resolve source title/author presentation only under current source
authority; otherwise show Original unavailable with the owner's own writing and
public references. Source deletion/revocation has no cascade into this private note.
Independent copies intentionally retain their copied content; preserve minimal source
credit already permitted at copying without fetching inaccessible updates. Exact
permitted copy-credit fields/retention still require privacy qualification.

Delete atomically closes the note/study lifecycle and increments its revision before
any stale update could commit. An active-note predicate includes an active parent
study. Retain minimal deletion/operation evidence to prevent old creates/retries from
resurrecting content. How payload erasure/child cleanup is bounded and retained must
close before deletion stories; this draft promises no undelete or indefinite payload
retention. Removing a passage only changes the independent passage list.

Own/accepted-shared library queries and Word Analysis discovery apply current Access,
study-share and note-visibility predicates before pagination, snippets or counts.
Derive plain text/reference search indexes from saved aggregates within the same
owner boundary; indexes/worker caches cannot bypass current row visibility. Lost
source access removes source results but not independently owned responses/copies.
Exact search normalization, keyset cursor/ordering and query limits remain to select.

## Implementation closure and evidence

This is one owner contract for D-2 shapes; consuming schemas/clients/migrations must
be derived from it rather than inventing a second model. Remaining closure:

- Physical private schema/roles/forced RLS and composite owner/study/note/highlight
  constraints; actor/UTC attribution and safe alternate-write error mapping.
- Closed command-specific OpenAPI, error variants and strict document/array/body
  limits; safe editor adapter, parser catalogue and qualification of the proposed canonical digest encoding.
- Qualify the proposed corpus-publication revision/import transition and exact source-validation evidence;
  no claim that current public schemas already provide it.
- Measured statement/lock/total execution and recovery limits; edit-base/outcome
  retention, bounded copies and deletion erasure/cleanup with migration compatibility.
- Private response provenance/copy credit, safe search ordering/normalization and
  snapshot/concurrency tests. D-1 supplies current identity and D-5 governs activation.

Map ST-03–12/18–28 to real API/database tests: atomic rollback of aggregate validation;
response loss, same/different operation concurrency and stale revisions; source import
change versus outage; private-response filtering across every read/copy/count; source
loss; copy coherence; deletion/save races; pool reuse and alternate write paths. Keep
ST-14/15/31 device/history proof in D-4. Documentation validation is not these tests.

Impact: private domain code stays in Scribeswell; public repository allowlist/roles
unchanged. No shared annotation framework, editor package or new root agent rule.
Promote only proven neutral save/error/recovery patterns with their first consumer.
Accepted ADRs remain unchanged; D-5 supplies controlled migrations, compatible activation
and recovery evidence. This planning item implements neither Notes nor Leave.

## Workspace-tab integration

The [reader interaction contract](reader-interaction.md) owns layout lifetime and
public navigation. All tabs/tool views of one account/note share the same aggregate
edit lane described here; per-tab study/note associations do not duplicate documents,
revisions or commands. Unmounting a view must not enqueue a stale local snapshot.
Tab switching retains the lane; the shared last-context departure rule governs
explicit note replacement and layout closure without deleting saved business data.


## Bounded ordinary-note implementation

Ordinary own-study/note create/write/reopen now uses the adopted [app contract](../../../apps/scribeswell/docs/PERSONAL_NOTES_V1.md): private app-owned schema/history, restricted runtime/forced RLS, atomic values and receipts, revisions/no-op/replay and bounded transactions. Native SQL proof includes permissions, concurrency, failed migration/retry and committed-response loss. Richer aggregates, references/anchors, private responses, copy/delete and wider D-2/D-5 remain proposed or gated as stated above. See the [delivery evidence](../../implementation-artifacts/spec-scribeswell-personal-notes-runtime.md) for exact tests and limitations.

Event247 adds actual local provider/owner HTTP and browser saving qualification with restricted app SQL: exact Hebrew/combining-mark text survives autosave/reload, note attribution matches the Identity account actor, second-account access fails, and discarding real completed enrollment/create acknowledgements before same-operation replay produces one durable effect. This is completed-response discard, not injected transport loss. [Integration evidence](../../../apps/scribeswell/docs/STUDIES_OWNER_INTEGRATION_EVIDENCE.md) preserves earlier failures and remaining gates; event250 records all13 findings addressed without deferral and the final patched-source native pass. Wider aggregate and release requirements remain unchanged.

Events258–260 approve and implement the ordinary title-only metadata extension in the adopted [app contract](../../../apps/scribeswell/docs/PERSONAL_NOTES_V1.md#study-title-rename-extension--opt-in-delivery): independent study revision, study.rename operation/receipt, current authority, parent locking and additive0002 constraints. Native and real-owner SQL/browser tests passed; Save/Cancel and original-operation Retry preserve note lanes/context. Independent review and final regression verification are complete for this bounded opt-in (event263); activation stays disabled.


## Delegated collected-passage delivery

Direction266 moves integration testing to the final phase while component ATDD/TDD
continues. The adopted passage contract owns exact catalogue, parser, collection
wire/migration, independent revision/receipts and recovery rules. Ordinary NoteValue
remains unchanged; richer note-link/highlight consumers follow separately. Native
permission/concurrency/migration and actual-owner integration remain unexecuted until
that phase. No owner grant, shared service, provider or activation change is implied.

Events271–272 implement these collection rules in the opt-in and qualify component
behavior, including strict reference identity, retained entry identity, independent
lanes, explicit navigation and conflict/original-operation recovery. Three reviews
produced14 individual triage rows:12 direct corrections/prepared-proof items addressed,
one unreachable ambiguity claim rejected, one final-integration gate retained.
[Application evidence](../../../apps/scribeswell/docs/COLLECTED_PASSAGES_EVIDENCE.md)
records exact checks and earlier failures. Prepared17 native cases are not SQL proof;
final post-review component regression passed226 browser and226 Python cases (event275).
The local preservation checkpoint keeps its delivery spec in-review for final integration;
production stays gated.

## Designed note-reference format extension

Event277 adopts [NOTE_REFERENCES_V1.md](../../../apps/scribeswell/docs/NOTE_REFERENCES_V1.md)
for the next bounded implementation. DocumentV1 remains exact for ordinary notes;
DocumentV2 adds strict canonical passage links and is retained after link removal.
Current-revision old-editor replacements cannot downgrade a stored2; typed409 refuses
before value/receipt changes, while original committed replay remains historical only.
The app contract owns exact limits, caret/safe DOM, same-tab Read/Edit and existing
reader navigation. No implementation, richer aggregate/highlight, sharing or activation
claim. A read-aware prior release/coordinated adoption is required before enabling
rich writes; isolated baseline DTO/storage proof must not import live widened models.

Event280 records initial implementation of the format2/downgrade fence and first
insertion component checks. Full editor matrix, review and native/actual-owner proof
remain pending; this updates the design-only chronology without broadening acceptance.

Event282 extends this to implemented opt-in editor/read-navigation and executed
component matrix/old-format unit coverage. Full regression after review and actual
native/owner proof remain pending. Source evidence retains intermediate failures
and makes no seamless prior-release or activation claim.

Event284 completes three independent reviews and records individually triaged direct
editor/verification corrections. Undo insertion, final-caret position, interrupted
composition, forbidden nested links, candidate limits and feedback require correction;
final patched-source regression and native/owner proof remain pending.

Event286 adopts [the proposed own-library search contract](../../../apps/scribeswell/docs/LIBRARY_SEARCH_V1.md):
read-only private-body query, literal saved text and canonical reference matching,
owner/active filtering before pagination, query-bound positional cursors and retained
account-safe library context. Existing JSONB/passages suffice without a migration or
duplicate search index. At event286, search code/SQL proof was not implemented or qualified.

Event289 closes note-link independent review corrections and final component checks:
324browser/249Python plus build/reproducibility passed. Prior310/312 failure and native
Backspace correction remain disclosed.18native scenarios are collected only; actual
SQL/owner/session and activation/device qualification remain pending. Search is ready
for implementation planning under event288, not implemented.

Event292 records the first in-progress search implementation and component milestones,
not final SQL or parent acceptance.207affectedPython/build and initial2browser checks
passed after runnable missing-field acceptance red; expanded matrix/review remain
pending. A missing-module collection error is not an API-behavior red; the backend
API chronology gap remains disclosed. Final native/owner integration stays deferred.

Events294–296 implement the bounded own-library search read and report296 browser
passes/two native-browser skips,277 affected Python passes and24 focused search
passes. Literal extraction recognizes guarded visible fields rather than certifying
a whole corrupt aggregate; invalid canonical references cannot match through that
branch.401 masks retained private candidates until fresh same-account verification;
400/503 permit correction. SQL locale/matching/isolation/zero mutation and real-owner
proof remain prepared-only. Parent audit/review and final integration remain open.

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

### Public layout/editor preservation component evidence — event353

The [four-pane evidence](../../../apps/scribeswell/docs/FOUR_PASSAGE_LAYOUT_EVIDENCE.md)
records686 browser passes/2expected native skips and final build on unchanged
160-source inventory. Current note lane/editor/owned atoms, actual caret/range,
composition and original save identity survive public layout transitions. Its
account-return extension contains only validated public references; no note-body,
private-authority, API or migration wire changed. Native/owner/session/device and
release proof remains final-phase. Historical method and failed-run limits remain
explicit; per-tab resource context and durable restoration are not delivered here.

Event402 implements a bounded browser read-response protection: unreadable note
values are rejected by the current Notes HTTP adapter before outline/editor
attachment. Existing server DTOs remain authoritative; this consumer renderability
guard does not validate complete attribution metadata or supply resource authority.
Both current document versions and the editor's unchanged URL predicate are reused.
Malformed responses use existing error/Retry handling and preserve dirty lanes and
original save attempts. Event404 records completed review and five direct corrections, including early
traversal budgets, nested-reference counting and canonical IDs. Event406 records final48 repeated targeted passes/build with unchanged166-source
proof. Broader affected run743passes/2native skips/1existing anonymous scroll-test
failure remains unqualified; cause unverified and deferred, original assertions
unchanged. The malformed-note correction is complete at local checkpoint
a5172ca1677f1638b837b6908c5b07a8c48a41a2 (event408), no push; all wider gates remain.
See NOTE_RESPONSE_BOUNDARY_EVIDENCE.md. No native,
actual-owner/session, provider or release qualification follows.
