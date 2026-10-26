# Study details and relevant own notes v1

App-owned opt-in contract adopted before behavior. Study metadata uses the independent
study revision: title plus nullable introduction (at most 10000 Unicode scalars,
line breaks retained, no NUL) and nullable source_url (the existing safe HTTP(S)
policy, at most 2048 UTF-8 bytes). Create accepts absent optional fields; absent new
fields are omitted from create receipt hashing, preserving original title/null
fingerprints. Explicit nulls remain bound. PUT /api/studies/{id} is
study.details.replace with operation_id, expected_revision and complete title,
introduction, source_url. Rename changes only title. Details use whole-form Save /
Cancel; unknown writes retain the original frozen operation and Cancel only hides
that recovery. Conflict requires an explicit current read, retaining the candidate.
Copy retains details and includes their canonical bytes in the existing 2MiB bound.
Deletion erases details together with the title. Nullable additive0008 requires
controlled migration before activation and forward recovery; no migration runs here.

POST /api/studies/context-notes is an authenticated bounded read with exactly one
canonical reference, optional cursor, and limit default20/max50. It returns each
matching active own study-visible supported note once, newest created_at/id first,
with current study title/owner, note identity/revision, bounded saved preview (120
scalars) and at most256 canonical references. Connections, structured document links
and highlight segments use the existing guarded SQL canonical overlap rules.
Account, parent/note lifecycle and supported visibility/kind filter before limit
and preview; no shared fallback or inaccessible counts. Cursor is canonical keyset,
bound to account and full reference query; invalid/reused context is rejected.

Notes exposes relevant own notes for the exact current account/tab/pane/reference.
Late reads cannot replace newer context. Pagination retains authorized items on
recoverable failure with Retry; access denial masks private results. Preview reads a
separate authorized aggregate, labelled saved writing, and never changes study,
current note, colours or shared edit lane. An in-memory dirty current lane is labelled
as local unsaved writing separately. Explicit Open uses the existing save guard to
select the own study/note. It reveals the first anchored/reference passage only if
none of the note references is already visible; use normal reader navigation once,
including source occurrence targeting where available. Opening only a study or a
preview never navigates. Current visible relevant panes and positions survive.

All current Access, receipt, lifecycle, revision, attribution, single note lane,
account/tab generation and departure protections remain. No recipient/notification
owner, sharing/private responses, other app or platform changes. No scaffold/shared
UI promotion, agent-context or ADR changes. Native SQL/privacy/pagination/copy and
migration tests are authored only; actual owner/device/release qualification remains
final-phase. Canonical specifications remain parent-owned.

Review correction: context discovery validates each already owner/lifecycle-filtered
SQL candidate with the existing NoteValue/ContextNote DTOs. A malformed or unsupported
stored sibling skips that candidate only. Each request still scans at most limit+1
raw matches; its continuation uses the last raw row in the bounded page rather than
the last readable item. Empty readable pages with a continuation say No readable
notes on this page and retain More. No unbounded search for a readable page or second
schema-validation framework is introduced.

Relevant matching panes that are hidden in the single-pane layout are activated by
the normal pane command without replacing their reference/position or adding a
navigation step. Preview recovery retains its own inspected identity; recoverable
reads offer direct Retry Preview and confirmed unavailable resources offer Close.
Successful current-note autosaves do not discard another note's preview/pagination.
Details completion/Cancel returns focus to its own trigger under the existing origin
guards. An unresolved study create freezes all visible original form values and its
retry identifies the original creation; definitive validation refusal permits correction.
