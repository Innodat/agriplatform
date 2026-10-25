# Own-study library search — bounded contract

**Implemented as development/test opt-in code with contract/component evidence; final native and actual-owner integration remains pending.**
CAP-1/ST-03 own-library subset. Inherits [personal notes](PERSONAL_NOTES_V1.md),
[passage references](PASSAGE_REFERENCES_V1.md) and [note links](NOTE_REFERENCES_V1.md).
Shared libraries remain dependent on their separate invitation/resource contracts.

## Read-only HTTP boundary

Add protected `POST /api/studies/search` with exact JSON fields `query`, `limit`,
`cursor`. Query is a Unicode-scalar string of at most200 codepoints; limit is an
integer1–50 (default20); cursor is null/omitted or the bounded search position below.
Unknown/duplicate fields, malformed Unicode/NUL, booleans as integers and unsupported
cursors fail the existing fixed400/no-store envelope. The request body is bounded
at4096 UTF-8 bytes with the existing strict JSON depth/node protections. This is a
read, with no operation ID, receipt, revision, attribution mutation or implicit enrollment.
Keep existing GET list routes and their v1 cursors unchanged for previous consumers.

Search terms may contain private writing. Send them only in the JSON body, never
browser/request URLs, history, browser storage, diagnostics or error details. Return
only the existing StudyPage metadata; no snippets, private matching bodies, counts
or query echo. Recheck Access before each local transaction/page and apply current
owner/active predicates inside every study, note and collection branch. Existing
5-second total, external-check and SQL deadlines apply; exhaustion is unavailable,
never a partial scan reported as complete. Production activation remains disabled.

## Closed matching semantics

Trim outer query whitespace and normalize Unicode to NFC. Blank means the ordinary
own library. Nonblank text is a literal substring, with PostgreSQL `lower` applied to
both NFC operands under the qualified database UTF-8 locale; English case differs
insignificantly and Hebrew remains exact Unicode. Diacritics, punctuation, internal
spacing and `%`, `_`, backslash and quotes remain literal. No fuzzy/stem/regex search
or ordinary-text diacritic removal. Actual locale/Unicode behavior requires prepared
native tests; a SQL-string unit test alone cannot qualify it. PostgreSQL17 documents
[NFC normalization, locale-based lower and literal position matching](https://www.postgresql.org/docs/17/functions-string.html);
normalization requires UTF8 server encoding.

A study matches its saved title OR visible text of an active owned note OR a canonical
passage match. Extract text only through the declared format1/2 grammar: concatenate
adjacent text and external-link text without inserting gaps at formatting boundaries;
include stored passage-link labels as plain text; separate paragraphs/list paragraphs
with one newline. Exclude URL targets, metadata, IDs, marks and arbitrary JSON values.
Never search raw serialized JSON. Unsaved editor input is not searchable until saved.

Resolve English/Hebrew book aliases through the existing pinned catalogue/parser.
A valid chapter/range query matches references in collected passages and structured
note links when catalogue/version/versification/book agree and inclusive ranges overlap.
Whole chapters cover their valid verses; chapter/range and range/chapter overlap is
symmetric. Cross-chapter endpoints remain complete. An unambiguous complete book alias
may match all references in that book, without fabricating a stored chapter reference.
A failed/ambiguous reference interpretation adds no canonical match; ordinary literal
text search still works. Never guess numbering or perform versification conversion.
Reference matching uses stored identity, independently of a custom display label.
Reference-only Matthew participates without corpus fetching or fabricated text.

Use one database-side filtered study query: explicit owner/active outer scope and
correlated owner/study/active EXISTS predicates, then keyset boundary/order/limit.
Order remains `(created_at DESC,id DESC)` with limit+1 for continuation. Multiple
matching notes/references yield one study. Do not scan a bounded unfiltered page in
Python/browser, concatenate another owner's content, or silently cap eligible results.
Guard JSON traversal/numeric extraction against unknown shapes rather than unsafe
casts or recursive matching of unrelated fields. Existing JSONB and normalized
passage rows suffice; no migration or duplicate search index/model is needed. Use
the [PostgreSQL17 JSON operators](https://www.postgresql.org/docs/17/functions-json.html)
with explicit array/type guards; missing-path NULL behavior is not a full grammar validator.

Search cursors have a distinct closed version/resource, verified account, digest
of the full canonical query/matching-version/reference interpretation and final
created_at/ID position. They carry no plaintext query and stay within the existing
512-character cursor bound. Canonical encoding rejects malformed fields/encoding, wrong resource,
query, account, version and extra fields. They are position hints, not authority or
snapshot promises; constructing another otherwise valid owned position is not an
authority bypass. No signing secret or tamper-proof cursor claim is introduced.
Old list cursors never authorize search continuation.

## Library interaction and concurrency

My studies offers an accessible Search studies field and Search action; Enter submits.
Clear explicitly returns to the unfiltered library. Editing a candidate does not
replace applied results until submit. Show loading, empty, invalid and unavailable
states truthfully; preserve the editable candidate and offer retry of the same read.
The label/help explains that search covers saved titles, notes and references.

Keep query/candidate, applied results/pages/cursor, scroll and stable focus anchor in
account-scoped memory across study open/leave, reader/tool changes and retries. No
saved note is copied into search state. On return, refresh the applied search under
current authority, rebuilding up to the previously loaded result depth with normal
bounded requests, stopping at the end or a superseding action; then restore the stable
anchor/position best-effort if results changed. Do not treat an old cursor/cache as
current resource authority or overwrite refreshed results with older cached metadata.
Account replacement/confirmed denial clears private library state; unavailable checks
hide unverified results and permit retry without claiming deletion. Authentication
failure follows the existing private-surface authority mask: retain candidate/applied
context in account-scoped memory, mask private terms/results during401, and restore
the exact candidate only after fresh successful same-account verification/retry.
Storage/Access503 and input400 retain the editable candidate while hiding unavailable
results; confirmed replacement/denial clears that context.

Library requests have their own account/query/navigation generation and loading/error
state. Guard success, error and finally; deduplicate More for the same applied query
and cursor, including returned study IDs. A late old-query/page success or denial
cannot replace current results, clear current loading or affect note/title/collection
lanes. A changed query resets pagination/position. Opening a result changes only the
study/tool context; reader positions and independent save lanes remain. No browser
navigation entry or consequential action results merely from searching.

## Qualification and impacts

ATDD first demonstrates a matching study beyond the first unfiltered page, then
literal title/note/reference discovery and retained multi-page library return. Focused
TDD covers strict read DTO/body/errors, query-bound cursors, guarded grammar traversal,
reference overlap/book aliases and filtering-before-limit. Browser components prove
English/Hebrew/Unicode, formatted text/custom labels, current query races, More,
retained scroll/focus, account/denial/outage and no private terms in URLs/storage.
Prepare restricted native SQL proof for all matching branches, duplicates/equal-time
pagination, malformed JSON, inactive/cross-owner isolation, changed saved content and
previous GET consumer compatibility. Prepare actual-owner UI plus independent zero-
mutation/receipt SQL proof. **Native/owner/session execution stays at final integration.**

Scaffold/shared UI: reuse current app API/error/list patterns, no promotion or generator
change. Agent context and accepted ADRs: unchanged. Documentation/generated clients
and canonical status update with the slice. No Access/Identity implementation,
sharing/notification grants, Leave/factory work, provider change, migration, deployment
or activation is authorized by this contract. Physical devices and live signup remain
separate qualification gates.

## Delivery status — 2026-10-25

The strict protected search read, separate query-bound cursor, single database-side
filtered study query and account-scoped library interaction are implemented. The
existing GET/list route and v1 cursor remain unchanged. Search sends only the query
and continuation in its JSON body; it returns existing StudyPage metadata. The
local query owns independent generations/loading/error state and preserves loaded
depth plus best-effort stable scroll/focus across an authorized refreshed return.

[Search evidence](LIBRARY_SEARCH_EVIDENCE.md) distinguishes executed DTO/API/storage-
method and intercepted desktop/mobile component checks from prepared native SQL and
actual-owner browser/independent SQL checkpoints. PostgreSQL locale/NFC/JSON matching,
actual restricted database isolation and zero mutation remain pending final integration
under direction266. No migration, provider, activation or deployment ran. Physical
devices, live signup and wider Studies gates remain open.
