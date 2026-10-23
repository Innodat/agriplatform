# Personal study notes: first wire contract

This app-owned contract supports the first create/write/reopen milestone. **Implemented now:** strict request/response DTOs, bounded command decoding, generated OpenAPI and pure contract tests. **Not implemented:** HTTP routes, current authorization, storage, migrations, browser editor/autosave or account enrollment. The generated paths are unmounted. This document specifies obligations for those future consumers; passing wire tests does not prove them.

The canonical Studies SPEC, UX and accepted platform ADRs retain authority. This milestone is ordinary owner-only studies and notes. Sharing, private responses, study metadata editing, introduction/source metadata, passage lists, deliberate passage links, highlights, conflict copies, deletion and search retain their agreed requirements for later consuming slices. No product requirement is removed. This is partial D2 contract readiness, not D1–D5 closure.

## Wire source and generation

[personal_notes_contract.py](../backend/personal_notes_contract.py) owns the closed Pydantic DTOs and OpenAPI construction. [personal-notes-v1.openapi.json](../contracts/personal-notes-v1.openapi.json) is generated, never hand-edited. Generate with the backend Python environment:

```sh
python3 -m pip install -r apps/scribeswell/tests/requirements.txt
python3 apps/scribeswell/tools/py/export_personal_notes_contract.py
python3 apps/scribeswell/tools/py/export_personal_notes_contract.py --check
python3 -m pytest apps/scribeswell/tests/test_personal_notes_contract.py -q
```

Backend requirements already include Pydantic 2; test requirements additionally declare pytest and JSON Schema validation for schema/DTO parity. No framework upgrade or shared runtime dependency is introduced. The OpenAPI extension `x-runtime-status: contract-only-unmounted` is intentional. Importing the module performs no network, database, environment, migration or registration action. Do not mount the DTOs through existing generic exception handlers: the current public API validation handler exposes validation input. A private adapter must translate errors to the safe error union below without raw exception/input logging before mounting.

## Create, read and preserve

All paths are relative to the Scribeswell origin. Browser account sessions go to Scribeswell, never an Access service credential. Each protected request requires fresh owner-qualified account/actor/current Studies authority, then local resource ownership and active lifecycle checks. No account/org/actor field is accepted in a command. An owner UUID returned in a resource is attribution, never authority.

| Path | Planned behavior |
| --- | --- |
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

Lists use `(created_at DESC, id DESC)` keyset order, default 20/max 50, after owner/lifecycle filtering. Cursor is unpadded base64url of UTF-8 compact JSON `["scribeswell.list.v1", resource, account_id, study_id_or_null, last_created_at, last_id]`; `resource` is `studies` or `notes`. Decoder must reject unknown versions, extra fields, invalid timestamps/IDs, wrong owner/resource/parent and over-512-character cursors with safe 400. A cursor is position, never authority or a snapshot guarantee. Newly created rows may appear only on a restarted page; concurrent changes must never leak inaccessible rows. Cursor codec/SQL are not implemented by these DTOs. Full-value note pages are a first-milestone choice, max 50; future summary projections must preserve filtering and privacy.

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

Storage failures use `operation_unresolved`/409 if commit outcome is uncertain, `studies_storage_unavailable`/503 for definite non-deadline failure, or `request_deadline_exceeded`/503 only when the deadline actually expired. The generated error union defines possible bodies; a future adapter must enforce this status mapping and safe cache headers on success/exception/streaming paths. No private framework-default 422 input echoes.

Operation identity is `(current account, command, command version 1, operation_id)`. Fingerprint canonical validated JSON (sorted keys, compact UTF-8, preserved Unicode, no normalization), including command/version, path study/note IDs and complete typed payload. Store only server-side digest; exclude digest/body from logs and lookup. Same operation plus same payload returns the compact original outcome after current authority/resource lifecycle checks; a changed payload/path is 409 mismatch. An unresolved operation is never proof of rollback. Receipts have no automatic expiry in this milestone; require a compatible explicit retention plan before pruning. Replay cannot recreate a closed resource or override current authority.

## Required persistence and saving behavior — not implemented

Scribeswell owns private study, note and receipt tables. Identity/Access are HTTP owners: no cross-owner table reads or foreign keys. Local study/note scope uses structural composite owner/study relationships and constraints; note visibility is immutable. Server-owned actor/time/revision fields and consequential audit follow ADR-0025/0056. SQL roles must prevent browser/Data API writes, use restricted runtime roles and force RLS with transaction-local verified scope; connection reset/pooling isolation and alternate write paths need actual database proof. An actor row never grants permission.

Current Access/identity waits occur **before** local write locks. One short transaction locks active parent study before child note, checks expected revision and editability together, replaces the full aggregate and commits attribution plus operation receipt atomically. Identical replacement records an acknowledgement without revision increase or false last-change attribution; changed replacement advances once. Rollback exposes no receipt for an uncommitted change. Cross-owner paths, concurrent create/retry/replace/delete, unknown commit, role bypass, revision overflow and default-title races require native database tests before claiming runtime readiness. No startup migrations or implicit fallback writes.

Use one serialized save lane per note across workspace tabs. Coalesce later input, freeze operation/payload for an in-flight attempt, and block later snapshots while its outcome is unknown. Current acknowledged local generation alone may show **Draft saved**. Delayed success for older text cannot mark newer input saved. Recheck authority on every new request/retry; lookup/retry uses the original operation and payload. Revision conflict pauses saving and preserves input without automatic merge or a fabricated copy endpoint.

For the consuming implementation, a request has a 5-second total budget starting before Access, with at most 3 seconds for external checking and at most remaining time for local work; lock waits at most 1 second, statements at most 2 seconds, shortened to remaining time. Positive DB timeout settings only; zero must never disable the bound. Stop issuing work when the budget expires. Client request timeout is 15 seconds; uncertain response uses at most two lookup requests within a 10-second recovery window, each with fresh authority. Unresolved recovery remains unsaved with explicit Retry, not automatic issuance of a new operation. These are planned execution bounds, not measured guarantees.

Autosave debounce is 500 ms, with a 2-second maximum while typing when no prior save is unresolved. Inline **Changes not saved / Retry** while editing; exit-only **Stay / Close anyway**, switching **Stay / Switch anyway**. Confirmed current input closes immediately. Never automatically submit another consequential action after authentication recovery or promise offline/unsent input survival. The UI/editor adapter and real network failure tests remain outstanding.

## Exact Access-owner handoff

| Dependency | Repository evidence / required closure |
| --- | --- |
| Current verified account and durable actor | Owner-qualified identity/session HTTP evidence, expiry/failure/error semantics and execution bounds; no JWT role/email/locally invented actor shortcut. |
| Account-scoped Studies admission | Implement and test the proposed `scribeswell.studies.use` check with typed account authorization scope and restricted Scribeswell caller. Current `services/access/organization_check.py` accepts **organization-scoped KDG checks only**. Returned `own_account` resource scope is not account authority. |
| Enrollment | Separate owner implements the agreed open eligibility for every verified signed-in reader without org/employment/PtS/admin prerequisites, with current suspension and no revoked-grant resurrection. Registration alone grants nothing and creates no study. |
| Standalone signup | Existing Scribeswell Auth consumer remains; live provider/account-creation activation and verified-account contracts require owner evidence. No competing Auth or Access implementation here. |

[The owner enrollment contract](../../../platform/docs/architecture/contracts/scribeswell-study-enrollment.md) remains a draft, not implemented Access behavior. This document is the app-side handoff, not an instruction to modify that owner. No notification/invitation dependency is required for ordinary own notes; those broader features remain gated separately.

## Activation, recovery and traceability

ADR-0020 requires a controlled additive migration and qualified roles **before** private route activation; migration failure blocks activation. Previous public-reader version must keep working. No migrations on API/worker startup, no automatic reversal of applied migrations. Recovery disables private activation or rolls forward while preserving acknowledged data/receipts. Native migration/previous-version/restore tests and D5 release qualification must precede release; no live migration was run for this contract.

| Existing acceptance scope | Evidence now | Remaining proof |
| --- | --- | --- |
| CAP-1/CAP-3 create/write/reopen | Executable create/read/replace DTO round trip, Unicode and rich-text restrictions | Access, SQL persistence and real UI journey |
| CAP-9 saving and lifecycle | Strict revisions, closed outcomes/errors and malformed/forged input tests | Atomicity, authorization, no-op/replay/concurrency and delayed UI acknowledgement |
| D1 identity/access | Precise app-owned dependency above | Separate owner account contract/implementation/qualification |
| D2 data/save | Versioned first wire and normative transaction obligations | Schema, native DB proofs, catalogue anchors, private responses/copy/delete and richer content contracts |
| D3/D4/D5 | Existing requirements preserved | Existing owner/release/browser evidence gates remain open |

No scaffold, shared UI, agent-context or ADR change is justified by this pure contract. Promote proven saving/editor patterns with a real consuming story. The next productive runtime milestone remains the same complete create/write/reopen flow once the Access-owner handoff is executable; do not queue more operational fixture tooling as a substitute.
