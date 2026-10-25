# Personal study notes: first wire contract

This app-owned contract supports the first create/write/reopen and ordinary study-title rename milestones. **Implemented:** strict DTOs, generated OpenAPI/TypeScript, bounded same-origin private API, explicit Access enrollment/check adapters, app-owned PostgreSQL persistence and receipt recovery, controlled private Alembic history, and Studies/Analysis note editing with autosave. **Activation remains disabled in production.** The runtime is an explicit development/test opt-in pending coordinated startup/release qualification; public reading and standalone signup remain independent. Native SQL/browser proof and actual owner HTTP/domain integration are recorded below; synthetic Access responses alone do not establish live Identity/Access authorization.

The canonical Studies SPEC, UX and accepted platform ADRs retain authority. This milestone is ordinary owner-only studies and notes. Sharing, private responses, introduction/source metadata editing, passage lists, deliberate passage links, highlights, conflict copies, deletion and search retain their agreed requirements for later consuming slices. No product requirement is removed. This is partial D2 contract readiness, not D1–D5 closure.

## Wire source and generation

[personal_notes_contract.py](../backend/personal_notes_contract.py) owns the closed Pydantic DTOs and OpenAPI construction. [personal-notes-v1.openapi.json](../contracts/personal-notes-v1.openapi.json) is generated, never hand-edited. Generate with the backend Python environment:

```sh
python3 -m pip install -r apps/scribeswell/tests/requirements.txt
python3 apps/scribeswell/tools/py/export_personal_notes_contract.py
python3 apps/scribeswell/tools/py/export_personal_notes_contract.py --check
python3 -m pytest apps/scribeswell/tests/test_personal_notes_contract.py -q
```

Backend requirements already include Pydantic 2; test requirements additionally declare pytest and JSON Schema validation for schema/DTO parity. No framework upgrade or shared runtime dependency is introduced. The OpenAPI extension `x-runtime-status: opt-in-development-production-disabled` records the activation boundary. Importing the module performs no network, database, environment, migration or registration action. The private router contains its own safe errors because the current public API validation handler exposes validation input. The private router translates errors to the safe error union below without raw exception/input logging; the opt-in main boundary also contains framework-default private errors.

## Create, read and preserve

All paths are relative to the Scribeswell origin. Browser account sessions go to Scribeswell, never an Access service credential. Each protected request requires fresh owner-qualified account/actor/current Studies authority, then local resource ownership and active lifecycle checks. No account/org/actor field is accepted in a command. An owner UUID returned in a resource is attribution, never authority.

| Path | Behavior |
| --- | --- |
| `POST /api/studies/enrollment` | Explicit same-operation enrollment proxy; accepts only operation ID. No enrollment on registration or reading. |
| `POST /api/studies` | Explicit `study.create`; required nullable title. Null allocates a default. Supplied title is preserved exactly, including surrounding spaces; empty/all-whitespace/control characters are invalid. Returns compact `OperationAck`. |
| `GET /api/studies` | Current owner's active studies, bounded page. |
| `GET /api/studies/{study_id}` | Current authorized study metadata and its independent revision. |
| `POST /api/studies/{study_id}/notes` | Explicit `note.create` with a complete initial value; no required note title. Returns compact outcome. |
| `GET /api/studies/{study_id}/notes` | Current owner's ordinary active notes, bounded full-value page. No previews derived before authorization. |
| `GET /api/studies/{study_id}/notes/{note_id}` | Reopen full current value/revision/attribution. |
| `PUT /api/studies/{study_id}/notes/{note_id}` | `note.replace`, required expected revision and complete value; never upserts. |
| `GET /api/operations/{operation_id}?command=…` | Current-owner committed compact outcome or `unresolved`; no body, fingerprint or historical content. |

Create and replace acknowledge with HTTP 200, matching retry outcomes. IDs are canonical lowercase nonnil UUID strings. Revisions are positive signed-bigint **decimal strings**, max `9223372036854775807`; overflow fails closed. Server attribution uses exact UTC `YYYY-MM-DDTHH:MM:SS.ffffffZ` and durable actor IDs, preserving executor/initiator responsibilities where applicable. Clients cannot supply attribution. Success and all private error responses carry `Cache-Control: private, no-store`; intermediaries/service workers must not cache private bytes. Closed/deleted/wrong-owner resources share `resource_unavailable`/404 without existence disclosure.

Default title allocation is atomic per current owner: select the first unused `Untitled study`, then `Untitled study 1`, `Untitled study 2`, etc. Serialize allocation using an owner-scoped local transaction lock and inspect existing active titles; ordinary supplied duplicate titles remain permitted. No global title uniqueness constraint. Allocation must finish within the total request deadline or commit nothing. No automatic creation on signup, opening Studies, refresh or retry of a different action.

Lists use `(created_at DESC, id DESC)` keyset order, default 20/max 50, after owner/lifecycle filtering. Cursor is unpadded base64url of UTF-8 compact JSON `["scribeswell.list.v1", resource, account_id, study_id_or_null, last_created_at, last_id]`; `resource` is `studies` or `notes`. Decoder must reject unknown versions, extra fields, invalid timestamps/IDs, wrong owner/resource/parent and over-512-character cursors with safe 400. A cursor is position, never authority or a snapshot guarantee. Newly created rows may appear only on a restarted page; concurrent changes must never leak inaccessible rows. `personal_notes_cursor.py` and the private repository implement these positions independently of authority. Full-value note pages are a first-milestone choice, max 50; future summary projections must preserve filtering and privacy.

## Complete note value and limits

Every command requires all three fields: `document`, `connections`, `highlights`. This version accepts only **empty** connections/highlights arrays and ordinary `visibility: study` read models. Unknown fields and unsupported nodes are errors, never stripped. Do not let this restricted writer edit a richer saved value: richer nodes/relationships require a new compatible version/adoption strategy before activation, with old clients refused rather than allowed to erase unsupported content.

Document version is integer 1 (not boolean/float). Blocks are paragraphs or ordered/bullet lists. Paragraphs have explicit auto/ltr/rtl direction and text/external-link inlines. Lists contain nonempty groups of paragraphs, with no nested lists. Text preserves Unicode and combining marks exactly; scalar UTF-8 only. Bold/italic marks are unique and canonically ordered bold then italic. External links contain text nodes only. No HTML, CSS, event attributes, image nodes, nested links or passage links. Render with text nodes, never HTML injection; open external links safely with `noopener noreferrer`. The URL validator permits only absolute HTTP(S), valid host/port, no credentials, whitespace, Unicode Cc controls, backslash or malformed/unsafe percent escapes. Numeric browser hosts must be canonical IPv4; IPv6 must be unscoped. Generated schemas encode representable constraints and property descriptions identify additional semantic checks; JSON Schema alone cannot prove transport framing, Unicode scalar/byte budgets, calendar chronology or browser host/port semantics. Never fetch links server-side.

| Bound | Value |
| --- | --- |
| Command bytes / JSON depth / visited values | 65,536 / 16 / 8,192 (root depth 1; values including containers count) |
| Document model nodes / total text codepoints | 2,048 / 50,000 |
| Blocks / list items / paragraphs per item | 256 / 128 / 1–16 |
| Inlines per paragraph / link text children | 256 / 1–64 |
| Text codepoints per inline / URL UTF-8 bytes | 1–4,096 / 2,048 |
| Title codepoints / page items / cursor characters | 1–200 / 50 / 512 |

`parse_command` enforces body size, valid UTF-8, no BOM, duplicate keys at any level, nonfinite/fractional numbers, trailing input, root shape and depth/node budgets before strict DTO validation. It raises only the fixed `ContractInputError` for invalid commands. Public Pydantic APIs still return rich validation errors and must remain internal; never serialize `.errors()` or log exceptions with sensitive inputs. No payload, rich text, link, full signed URL or canonical fingerprint belongs in diagnostics. Explicit model serialization contains private text by design; `str`/`repr` are redacted conveniences, not a logging policy.

## Safe errors and outcomes

The closed error DTOs carry `error: "Request could not be completed"`, a stable `code`, and `details: null`, except `note_revision_conflict` whose details are only expected/current revision. Presentation branches on code, never English. Do not pass through upstream error payloads.

| HTTP | Codes |
| --- | --- |
| 400 | `scribeswell_personal_notes_input_invalid` |
| 401 | `authentication_required` |
| 403 | `studies_access_denied` |
| 404 | `resource_unavailable` |
| 409 | `note_revision_conflict`, `operation_payload_mismatch`, `operation_unresolved` |
| 503 | `studies_access_unavailable`, `studies_storage_unavailable`, `request_deadline_exceeded` |

Storage failures use `operation_unresolved`/409 if commit outcome is uncertain, `studies_storage_unavailable`/503 for definite non-deadline failure, or `request_deadline_exceeded`/503 only when the deadline actually expired. The generated error union defines possible bodies; the private adapter enforces this status mapping and safe cache headers on success/exception/streaming paths. No private framework-default 422 input echoes.

Operation identity is `(current account, command, command version 1, operation_id)`. Fingerprint canonical validated JSON (sorted keys, compact UTF-8, preserved Unicode, no normalization), including command/version, path study/note IDs and complete typed payload. Store only server-side digest; exclude digest/body from logs and lookup. Same operation plus same payload returns the compact original outcome after current authority/resource lifecycle checks; a changed payload/path is 409 mismatch. An unresolved operation is never proof of rollback. Receipts have no automatic expiry in this milestone; require a compatible explicit retention plan before pruning. Replay cannot recreate a closed resource or override current authority.

## Persistence and saving behavior

Scribeswell owns private study, note and receipt tables. Identity/Access are HTTP owners: no cross-owner table reads or foreign keys. Local study/note scope uses structural composite owner/study relationships and constraints; note visibility is immutable. Server-owned actor/time/revision fields and consequential audit follow ADR-0025/0056. SQL roles must prevent browser/Data API writes, use restricted runtime roles and force RLS with transaction-local verified scope; connection reset/pooling isolation and alternate write paths need actual database proof. An actor row never grants permission.

Current Access/identity waits occur **before** local write locks. One short transaction locks active parent study before child note, checks expected revision and editability together, replaces the full aggregate and commits attribution plus operation receipt atomically. Identical replacement records an acknowledgement without revision increase or false last-change attribution; changed replacement advances once. Rollback exposes no receipt for an uncommitted change. Cross-owner paths, concurrent create/retry/replace/delete, unknown commit, role bypass, revision overflow and default-title races require native database tests before claiming runtime readiness. No startup migrations or implicit fallback writes.

Use one serialized save lane per note across workspace tabs. Coalesce later input, freeze operation/payload for an in-flight attempt, and block later snapshots while its outcome is unknown. Current acknowledged local generation alone may show **Draft saved**. Delayed success for older text cannot mark newer input saved. Recheck authority on every new request/retry; lookup/retry uses the original operation and payload. Revision conflict pauses saving and preserves input without automatic merge or a fabricated copy endpoint.

For the consuming implementation, a request has a 5-second total budget starting before Access, with at most 3 seconds for external checking and at most remaining time for local work; lock waits at most 1 second, statements at most 2 seconds, shortened to remaining time. Positive DB timeout settings only; zero must never disable the bound. Stop issuing work when the budget expires. Client request timeout is 15 seconds; uncertain response uses at most two lookup requests within a 10-second recovery window, each with fresh authority. Unresolved recovery remains unsaved with explicit Retry, not automatic issuance of a new operation. The native qualifier exercises shortened actual lock/total deadlines. These are bounded execution settings, not a promise of upstream availability or physical-device timing.

Autosave debounce is 500 ms, with a 2-second maximum while typing when no prior save is unresolved. Inline **Changes not saved / Retry** while editing; exit-only **Stay / Close anyway**, switching **Stay / Switch anyway**. Confirmed current input closes immediately. Never automatically submit another consequential action after authentication recovery or promise offline/unsent input survival. The UI/editor adapter and synthetic lost-response/late-acknowledgement browser tests now exercise this behavior. Live provider and physical-device qualification remain outstanding.

## Exact Access-owner handoff

| Dependency | Repository evidence / required closure |
| --- | --- |
| Current verified account and durable actor | Owner-qualified identity/session HTTP evidence, expiry/failure/error semantics and execution bounds; no JWT role/email/locally invented actor shortcut. |
| Account-scoped Studies admission | Access implements `scribeswell.studies.use` with typed account scope and a restricted Scribeswell caller on the canonical check route. Its six-field account response has no organization/person/member placeholders. Scribeswell consumes this through its bounded HTTP adapter and local resource checks; existing KDG `own_account` resource scope never supplies account authority. |
| Enrollment | Separate Access/Identity owner implements explicit open eligibility for every verified signed-in reader without org/employment/PtS/admin prerequisites, with current suspension and no revoked-grant resurrection. Registration alone grants nothing and creates no study. |
| Standalone signup | Existing Scribeswell Auth consumer remains; live provider/account-creation activation and verified-account contracts require owner evidence. No competing Auth or Access implementation here. |

[The owner enrollment contract](../../../platform/docs/architecture/contracts/scribeswell-study-enrollment.md) now documents the implemented enrollment/check slice; its recipient/invitation sections remain a draft. The [owner runbook](../../../services/access/STUDIES-ENROLLMENT.md) records the actual caller, errors, deadlines, readiness and recovery. This document is the app-side consuming contract; private routes mount only under the explicit development/test opt-in. No notification/invitation dependency is required for ordinary own notes; those broader features remain gated separately.

## Activation, recovery and traceability

ADR-0020 requires a controlled additive migration and qualified roles **before** private route activation; migration failure blocks activation. Previous public-reader version must keep working. No migrations on API/worker startup, no automatic reversal of applied migrations. Recovery disables private activation or rolls forward while preserving acknowledged data/receipts. Native migration/previous-version/restore tests and D5 release qualification must precede release; no live migration was run for this contract.

| Existing acceptance scope | Evidence now | Remaining proof |
| --- | --- | --- |
| CAP-1/CAP-3 create/write/reopen | Native SQL + browser create/write/reopen and actual formatting toolbar/reload | Default owner startup/readiness and coordinated release qualification |
| CAP-9 saving and lifecycle | Strict revisions, native no-op/replay/concurrency/lifecycle and browser delayed/unknown outcomes | Wider deferred copy/delete/richer-content workflows |
| D1 identity/access | Bounded exact app HTTP binding consumes delivered owner contract | Default owner startup/readiness and activation qualification |
| D2 data/save | Versioned first wire, private schema and native permission/transaction proof | Catalogue anchors, private responses/copy/delete and richer content contracts |
| D3/D4/D5 | Existing requirements preserved | Existing owner/release/browser evidence gates remain open |

The bounded runtime below consumes the shared migration helper through its existing installer. Wider reusable editor/saving promotion needs further consuming evidence; no accepted ADR or agent-context change is introduced.


## Opt-in runtime and qualification — 2026-10-23

`SCRIBESWELL_STUDIES_ENABLED=true` requires separate
`SCRIBESWELL_STUDIES_DATABASE_URL` (restricted `scribeswell_studies_runtime`),
`SCRIBESWELL_STUDIES_ACCESS_URL` and server-only `SCRIBESWELL_STUDIES_SERVICE_KEY`.
The browser build uses `VITE_STUDIES_ENABLED=true` to expose the thin Studies/Analysis
surface. Defaults leave private routes/tools absent. Production settings and host
preflight refuse private activation; no real environment was activated. Credentials
never enter a Vite variable or browser request to Access.

The administrator-owned role preparation SQL refuses existing roles and inherited
database CREATE/TEMP authority; the database owner must prepare those global grants
separately. It does not change other consumers' database permissions. The private
schema/history and three tables are separate from the corpus. Runtime roles have
only scoped reads/inserts and selected mutable-column updates; receipts and creation
attribution are immutable to runtime. FORCE RLS applies to the schema owner too.
Dedicated async connections carry transaction-local account scope and close after
use, with a synchronous socket-close timer at the total deadline. No pool or cross-owner
foreign keys are added.

Generate/check the migration helper through the existing builder installer:

```sh
node --experimental-strip-types apps/scribeswell/tools/sync_personal_notes_database.mjs
node --experimental-strip-types apps/scribeswell/tools/sync_personal_notes_database.mjs --check
```

Controlled release execution optionally selects
`SCRIBESWELL_STUDIES_MIGRATION_ENABLED=true` plus its separate
`SCRIBESWELL_STUDIES_MIGRATION_DATABASE_URL`. The existing supervised Scribeswell
migration entry runs corpus first, private history second, before setting complete.
Both must succeed; failed/unknown migration blocks activation. Retain the separate
`studies-migrations.json` and ordinary migration evidence. Recovery disables private
opt-in or rolls forward; it never downgrades/reverses acknowledged notes/receipts.
This delivery supplies release preparation, not permission to activate production.

The editor uses explicit structured DOM construction and a closed serializer, preserving
Hebrew and combining marks, paragraph direction, bold/italic, ordinary lists and safe
external links. Clipboard HTML and dropped markup are not accepted. Notes remain in
one in-memory account/note lane across Studies/Analysis and word inspection. No private
body, title, cursor or edit buffer is persisted to browser storage. Same-account 401
recovery masks private surfaces while retaining recoverable input, then requires fresh
authorized loading and explicit Retry; sign-out/account replacement clears old state.
The native modal supplies Stay / Close anyway or Stay / Switch anyway on unresolved
exit. Unsupported current DOM input is truthfully unsaved and exit-guarded.

Native qualification uses only a newly owned isolated PostgreSQL17 cluster. It covers
upgrade/repeat, failed-DDL rollback/retry with acknowledged data retained, restricted
DDL/TEMP/ledger/foreign-owner/receipt/attribution denials, forced RLS and composite
scope, owner isolation, title/operation/revision races, no-op attribution, closed-resource
replay refusal, revision overflow and commit-response loss. A browser reload over the
real app HTTP adapter and native SQL is separately run with a synthetic Access HTTP
owner and intercepted public corpus. Desktop/mobile intercepted tests cover formatting
actions/reload, unknown operations, delayed acknowledgements, IME, same-account recovery,
account replacement, conflicts, tool continuity and exit guards. These do not establish
live Access/Identity/provider readiness, physical iOS/Android selection/keyboard behavior,
production integration, backup/restore or deployment qualification. Wider D1–D5 scope
and all deferred features above remain open.

Exact commands, results, log locations and matrix traceability are retained in the
[runtime delivery spec](../../../_bmad-output/implementation-artifacts/spec-scribeswell-personal-notes-runtime.md).
Scaffold impact: installer-owned shared migration helper is consumed unchanged. Shared
UI: no promotion is justified yet for this app-specific editor/lane; no generic engine
was added. Agent context and accepted ADRs: unchanged. Documentation: this contract and
canonical companions now distinguish runtime evidence from activation/readiness.

## Actual owner integration qualification — 2026-10-25

The separate one-run fixture and Playwright configuration now pass through the actual
app, Access/Identity owner SQL, native local Supabase Auth and provider-issued callbacks.
[Owner integration evidence](STUDIES_OWNER_INTEGRATION_EVIDENCE.md) records the complete
source-frozen run, independent SQL/actor/duplicate-effect observations, protected disable,
second-account isolation, earlier failed preparations and exact-run normal stop.
Actual initial checks preserve zero effects before explicit enrollment; the native
owner returns a safe503 while no actor has been explicitly prepared. Both real browser
cases and all independent SQL stages passed. Synthetic owner tests remain consuming
contract evidence; this new result establishes the stated local HTTP/domain chain.
Standalone signup, default Access startup/readiness, production release and physical
devices remain unqualified. Owner implementations and retained runs were preserved.
The separate broad browser regression had three failures that passed unchanged in
isolated reruns. Their cause is not established; this is not a full broad pass.

## Study title rename extension — opt-in delivery

The strict API, independent metadata operation lane and additive migration implement this contract. Qualification is recorded in [the rename evidence](STUDY_RENAME_EVIDENCE.md); production activation remains disabled.
It closes the ordinary-title subset of CAP-1/ST-02; introduction/source metadata,
references, sharing, deletion and broader feature gates remain unchanged.

`PUT /api/studies/{study_id}/title` accepts only required `operation_id`,
`expected_revision` and `title`, with existing nonnil UUID, positive signed-bigint
revision and exact Title rules. Empty/null/blank titles are invalid here; only
explicit creation allocates a default. Preserve supplied Unicode and whitespace
exactly; duplicate titles remain permitted. Its command is `study.rename`, version1.
Success200 uses existing compact OperationAck with matching study ID, null note ID
and metadata revision. Extend command-correlated schemas, lookup and safe409
`study_revision_conflict` details `{expected_revision,current_revision}`; other safe
status/no-store/size/error rules remain. Generated consumers must agree.

After fresh current Access, take the existing operation lock then active owner
study row lock. An identical operation/payload replays its original compact outcome
only after current lifecycle checks; changed payload/path is409 mismatch. For a
new operation, compare metadata revision under that lock. A changed title advances
revision once and changes only title/update actor/server UTC time; preserve study ID,
creation attribution, notes, note revisions and reading context. Identical title
records an acknowledgement/receipt without revision or last-change attribution
change. Commit metadata and receipt atomically; bigint overflow refuses safely.
Racing note writes retain their independent revision/value and existing parent-first
lock order. Replaying an older rename never overwrites a later title. Owner/lifecycle
filtering applies to reads and outcome lookup before disclosure.

The active study offers Rename with a compact Title field and explicit Save / Cancel.
Until saving, candidate text changes no heading/library or server state. Cancel before
Save sends nothing. While executing, freeze candidate/operation and prevent competing
rename submission. Confirmed success refreshes current metadata in heading/library
without resetting note editor/save lanes or moving scripture; do not replace a newer
title using an old acknowledgement's candidate. Identity/study/navigation generations
reject stale responses. Conflict preserves entered text, offers deliberate current-title
reload, and requires a subsequent explicit Save with a new operation/base revision.
An uncertain outcome retains original operation/payload for explicit Retry via bounded
lookup/replay; no later rename overtakes it, no rollback or automatic restart is
promised. Closing the title surface does not cancel an executing/unknown command:
retain its in-memory attempt for resolution, then re-read current metadata before a
new edit. Authentication recovery uses the same account protection; confirmed account
replacement clears old private state. Title controls do not intercept note typing.

A new controlled private Alembic revision widens receipt command and nullable-note
correlation CHECKs to admit study.rename while preserving prior commands/rows. The
existing restricted title UPDATE grant remains sufficient. Keep0001 immutable, forced
RLS, receipt immutability and controlled failure/forward recovery. Old running clients
remain compatible with existing paths/read shapes and their own receipt commands.
Required native migration/permission/concurrency/replay and actual-owner browser proof
must run before claiming this extension implemented. Production remains disabled.
