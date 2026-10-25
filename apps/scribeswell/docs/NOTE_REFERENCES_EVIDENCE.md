# Note passage links — component delivery, final integration pending

The development/test opt-in implements the [adopted closed note-link contract](NOTE_REFERENCES_V1.md).
Production activation remains disabled. Native restricted PostgreSQL, actual-owner
HTTP/UI plus independent SQL, session/provider integration and physical devices are
not qualified by this delivery. Under direction266 those integration scenarios are
prepared only; no KDG instance/shared ports, migration, activation or provider change
was used.

## Executed checks

`P=/tmp/scribeswell-manual-python/bin/python`. Commands run from the repository root.
Browser commands use the app workspace, its isolated component server on5182 and one
worker. Intercepted owner/corpus responses establish component behavior, not actual
owner or database authority.

| Command | Result / retained log |
| --- | --- |
| `P -m pytest apps/scribeswell/tests/test_note_passage_links.py -q` before implementation | 2 failed/11 passed: missing format2 and locked current-revision downgrade refusal; `/tmp/scribeswell-note-links-contract-red.log`. |
| `P -m pytest apps/scribeswell/tests/test_note_passage_links.py apps/scribeswell/tests/test_personal_notes_contract.py apps/scribeswell/tests/test_passage_references.py -q` | 193 passed; `/tmp/scribeswell-note-links-contract-qualified.log`. Includes isolated actual baseline DTO behavior and real storage-method control flow with cursor doubles. |
| `P -m pytest apps/scribeswell/tests/test_personal_notes_api.py -q` | 9 passed, one existing framework deprecation warning; `/tmp/scribeswell-note-links-api-final.log`. |
| `npm run test:browser --workspace=apps/scribeswell/web -- personal-notes.spec.cjs --grep 'note links:' --workers=1` | Expanded32-case matrix passed; `/tmp/scribeswell-note-links-browser-final-matrix.log`. Final complete affected run recorded below. |
| `P apps/scribeswell/tools/py/export_personal_notes_contract.py --check` | Passed after regeneration through the owning exporter. |
| Pinned API-client CLI with `--check` (exact invocation below) | Owned TypeScript output regenerated, never hand-edited; final check below. |
| `P apps/scribeswell/tools/py/build_reference_catalogue.py --check` | Passed; pinned catalogue unchanged. |
| `node --experimental-strip-types apps/scribeswell/tools/sync_personal_notes_database.mjs --check` | Passed; existing shared helper unchanged. |
| `npm run build --workspace=apps/scribeswell/web` | TypeScript/Vite passed; existing bundle-size warning; `/tmp/scribeswell-note-links-build-final.log`. |
| `node --check apps/scribeswell/web/tests/studies-owner.integration.cjs` and `P -m py_compile apps/scribeswell/tests/studies_owner_fixture.py apps/scribeswell/tests/test_personal_notes_storage.py` | Prepared fixture syntax only, not executed native or actual-owner proof. |

Pinned generation/check:

```sh
platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node platform/deployment/.local/scaffold-application/proof-yc4xuk/root/platform/api-client/src/cli.mjs --schema /home/ck/repos/innodat/agriplatform/apps/scribeswell/contracts/personal-notes-v1.openapi.json --output /home/ck/repos/innodat/agriplatform/apps/scribeswell/web/src/generated/personal-notes --check
```

The first local generator and component server attempts were blocked by process/network
sandbox restrictions; the same commands succeeded with local-process escalation.
An initial combined Python run was interrupted after TestClient hung in the sandbox;
its one observed assertion failure was the expected stale generated OpenAPI before
regeneration. It is not called a passing run. The later focused combined197-case run
passed (`/tmp/scribeswell-note-links-python.log`) before the final baseline/budget/API
cases were added. The isolated baseline loader initially failed future-annotation
resolution because its module was not registered in `sys.modules`; registering its
unique module name fixed the harness without widening baseline DTOs. That intermediate
contract run reported1 failed/189 passed (`/tmp/scribeswell-note-links-contract-final.log`),
then190 passed (`/tmp/scribeswell-note-links-contract-final2.log`); final193 includes
explicit label/reference node/text-budget cases.

Initial insertion browser acceptance reported2 failures; later editor changes overlapped
the second case, so this is intermediate evidence, not a frozen-source red matrix
(`/tmp/scribeswell-note-links-browser-red.log`). A clean source-link caret acceptance
subsequently failed both desktop/mobile before the safe source-anchor split was added
(`/tmp/scribeswell-note-links-source-red.log`). The first expanded18-case matrix had
3 failures/15 passes: composition mutated lane state without rerendering its controls,
and mobile Open navigated while the reader stayed hidden behind the tool. Composition
now rerenders; mobile Open reveals the active reader while retaining the same note.
That unchanged matrix passed18 (`/tmp/scribeswell-note-links-browser-matrix2.log`).

A later30-case expansion reported28 passed/2 failed because the new stale-note scenario
assumed a picker stayed open across hiding the note tool. Actual blur cancellation
closed it before a callback could run. The scenario now uses a genuinely distinct
replacement note and proves picker cancellation with no insertion/save in that note;
stale executing input callbacks are separately refused while retaining editable
reference input. The reference input also survives per-note picker reopen so the
reader can reposition a caret and try again. Account/note replacement clears that
picker state. No business expectation or authority rule was relaxed to resolve a failure.

## Requirement traceability

| Requirement | Executed component / contract evidence |
| --- | --- |
| English/Hebrew/chapter/range/Matthew insertion; preserve surrounding writing; no quote/collection/reader move | `note links: insert at caret…`, canonical insertion parameter cases; DTO exact roundtrip and stored plain labels. |
| Cancel/invalid bounds/IME/stale input/account/note | `cancel invalid IME and stale input…`, account replacement, distinct-note cancellation; no replacement-note write. |
| One lane, coherent pending value, unknown original operation / delayed acknowledgement | `unknown original operation and delayed acknowledgement…`; existing original-operation lane retained. |
| Read/Edit caret/input; editing offers Open; reading opens; active pane/full range/reference-only text | Click and keyboard cases, active comparison URL assertions, ordinary format1 caret restoration. Read/Edit does not write navigation history. |
| Source links/marks/lists/direction/paste/reload and atomic deletion | `links source marks lists direction plain paste and reload roundtrip`, source-anchor start/middle/end cases, Backspace/Delete; deleting final link retains2. |
| Owned atomic identity, corrupt/foreign input refusal, unknown/oversized/versioned grammar | Corrupt/foreign DOM case, strict DTO mutation matrix, semantic text/reference-node budget cases; safe scalar labels/strict catalogue. |
| Legacy current-revision downgrade refusal before mutation/receipt, original committed v1 replay | Actual `execute` method double asserts lock order/no UPDATE/INSERT and receipt replay; API409/no-store fixed envelope. Native proof remains pending. |
| Ordinary serialization and genuine old-format refusal | Hash-verified isolated baseline DTO/storage binding, ordinary JSON serialization parity and old-format refusal; original historical SQL fixture remains byte-identical. Native prior-consumer execution pending. |
| Terminal refusal preserves local input / exit protection | `terminal format refusal…`; no automatic retry/new operation; Reload to continue editing. Existing conflict/exit lanes preserved. |

## Prepared final-integration proof and compatibility gate

`tests/fixtures/note_links_baseline/` contains the exact baseline contract and SQL
consumer from full commit `2a383ffcb5c7e75645cf3c2bc1dab0d30ab8f7ae`.
`manifest.json` records each source path and SHA-256; the loader verifies hashes and
binds the storage module to its own frozen DTO before restoring the live module.
It does not rely on the older historical fixture's live NoteView import. A baseline
refusal is actual prior-format safe failure, not a deployed previous-app or seamless
compatibility claim. Before richer-write activation, qualify/deploy a read-aware
previous server and coordinate browser/server adoption under ADR-0020. Unsupported
previous servers must not be required to read newly rich notes.

`test_native_note_format2_fence_original_v1_receipt_and_actual_baseline` prepares
restricted native format2 create/read/no-op, actual baseline ordinary read/write and
rich refusal, original-v1 receipt replay after upgrade, genuinely current-revision
legacy downgrade with independent full-row/receipt equality, and final-link deletion
retaining2. No migration is necessary. The original frozen SQL fixture is untouched.

The actual-owner browser and `studies_owner_fixture.py` prepare `note-links-before` /
`note-links-after` checkpoints: insert in the real UI, reload, Read/Open full range,
read current format2, attempt a legacy payload at the current revision and receive
fixed409. Independent SQL requires exactly one changed note revision/receipt, unchanged
creation attribution/study/collection rows, exact stored format2, and no extra effect
from the refused downgrade. Final ordinary foreign-owner and disabled-authority
checks continue to use the updated complete note. These scenarios are **unexecuted**.

## Reuse decisions and remaining limits

Scaffold: no generator/configuration changes; consume the existing migration helper
unchanged. Shared UI: retain the app-owned editor/picker/navigation; no neutral
promotion justified. Agent context: unchanged. ADRs: no new or modified accepted
ADR. Documentation: adopted note/personal-note contracts and this evidence updated;
canonical memory is reconciled by the delivery workflow. No competing owner, Leave,
factory, sharing, highlights, quote or production setting was implemented.

Final native/owner/session integration, physical keyboards/selection, live signup,
default owner startup, production activation, coordinated compatibility and manual
acceptance remain open. Component doubles and generation do not close those gates.

## Frozen implementation checks

The complete affected command
`npm run test:browser --workspace=apps/scribeswell/web -- personal-notes.spec.cjs --grep-invert 'native PostgreSQL' --workers=1`
passed **216 tests** on desktop/mobile, exit0, with runtime/tests frozen throughout;
`/tmp/scribeswell-note-links-notes-qualified.log`. This includes prior ordinary-note,
source-link, title/collection, recovery and new passage-link behavior. The focused
anchor-boundary/caret command with `--grep 'note links:.*(source at|caret inside|Read Edit)'`
passed10 (`/tmp/scribeswell-note-links-caret-source.log`) beforehand.

The final focused combined Python command using the four files
`test_note_passage_links.py test_personal_notes_contract.py test_personal_notes_api.py test_passage_references.py`
under `apps/scribeswell/tests/` passed **202**, one existing Starlette deprecation
warning; `/tmp/scribeswell-note-links-python-qualified.log`. The frozen build passed
with only the existing bundle warning (`/tmp/scribeswell-note-links-build-qualified.log`),
and pinned generated TS returned `api_client_current`. No native/owner/session
integration command was run.

## Focused post-audit corrections

After the frozen216-case run, six added acceptance cases failed before correction
(`/tmp/scribeswell-note-links-patch-red.log`): an element-boundary caret targeted the
editor root rather than its explicit paragraph for direction; picker blur and queued
restoration could steal intentional outside focus; owned labels lacked bidi isolation.
The direction handler now considers an HTMLElement anchor itself. Owned atomic spans
use auto direction with `unicode-bidi:isolate`. Blur closes the selector without
restoring its trigger; note cancel/confirm timers restore the saved caret only while
that trigger still owns focus. Explicit Cancel/Escape still restore the note caret.
A queued-success external-focus case was added too. These changes do not add a new
save/navigation lane or widen the stored grammar. The post-patch build passed with
only the existing bundle warning (`/tmp/scribeswell-note-links-build-post-patch.log`).

Final focused command:

```sh
npm run test:browser --workspace=apps/scribeswell/web -- personal-notes.spec.cjs --grep 'note links|editor toolbar actions persist|composition defers' --workers=1
```

**52 passed** on desktop/mobile, exit0, against frozen post-patch runtime/test source;
`/tmp/scribeswell-note-links-patch-qualified.log`. This includes all note-link rows,
all four added patch scenarios, existing toolbar and IME behavior. Since the shared
app picker blur path changed, its existing affected regression was also run:

```sh
npm run test:browser --workspace=apps/scribeswell/web -- personal-notes.spec.cjs reader.spec.cjs --grep 'collected picker|dismissed executing picker|selector closes when keyboard focus leaves|typed reference visibly' --workers=1
```

**10 passed**, exit0; `/tmp/scribeswell-note-links-picker-qualified.log`. The complete
216-case result above belongs to the source before these minimal post-audit changes;
it is not represented as a second complete run of the final source. The final focused
52+10 and build cover their affected behavior. Exporter, pinned TypeScript, catalogue,
shared helper and prepared integration syntax remain current. Native/owner/session
integration and all production/device gates remain pending.

## Parent pre-review follow-ups

Read mode initially left the external source-link form visible outside the hidden
formatting toolbar. Desktop/mobile red2 preceded the one-condition correction;
Read now hides the form and Edit restores its candidate/selection without a write.
New case plus source-fragment cases passed8/8 (`/tmp/scribeswell-note-links-read-form-qualified.log`);
red log `/tmp/scribeswell-note-links-read-form-red.log`.

Replay proof now uses coherent separate histories: a current rich2 row refuses a fresh
legacy replacement at its current revision, while an earlier exact no-op v1 replacement
(expected1/ack1) replays historical acknowledgement without writing. Focused method and
contract suites passed141 (`/tmp/scribeswell-note-links-replay-qualified.log`). The prepared
native scenario creates that replacement through isolated baseline storage before upgrade,
then replays it through old/current storage and compares complete rich row/receipt count.
Native syntax only, no execution. Earlier202 Python and216 component results remain
pre-follow-up milestones; final broad patched-source verification is parent-owned.

## Review corrections — targeted acceptance

The reported B1–B9/V1–V2 corrections preserve the frozen intent. Passage insertion
now stages its complete candidate in a detached copy, validates document and command
budgets before touching live writing/selection, then applies editor-created DOM in
one native `insertHTML` editing transaction. Source-anchor splitting is inside that
same native transaction. The per-editor registry stores immutable reference/label
metadata under random DOM tokens and resets on lane replacement. WeakMap ownership
is rebound only for our controlled native editing commands or genuinely trusted
native `historyUndo`/`historyRedo` input; ordinary copied or foreign metadata remains
unsaved/refused. List formatting was observed to recreate owned atom nodes, so the
same controlled binding also preserves native list operations. No separate Undo
engine or private browser-storage state was introduced.

No-caret insertion resolves the actual final supported block/text position, including
trailing DIV/loose text. Composition mirrors the current lane on replacement while
leaving unresolved old-lane state protected. Source-link submission refuses a
selection intersecting an owned atom before mutation and retains the URL candidate.
Candidate refusal leaves the original note saved/unchanged and the reference input
editable. Retained picker text reopens at its candidate book. Existing insertion
feedback is associated with the input and announced politely; parser errors use an
associated alert. This avoids duplicating the collection surface's existing alert.
The owner SQL checkpoint now compares every non-target note exactly, including notes
in another study; its negative oracle covers changed value/revision, deletion and
unexpected addition without executing owner integration.

Targeted chronology, with the original failures retained:

| Command / scope | Result and retained log |
| --- | --- |
| App browser command with `personal-notes.spec.cjs --grep 'note links review:' --workers=1`, before corrections | 26 failed/4 passed; `/tmp/scribeswell-note-links-review-red.log`. V1 passage-only Notes preview and V2 mixed Unicode/HTML-looking stored labels already passed. Four formatting failures were initially a test helper using `press` for a multi-character string, corrected to `pressSequentially` before qualifying those rows. |
| Same app browser command with `--grep 'note links review:.*across an owned atom'` before runtime correction | 4 passed/4 failed; `/tmp/scribeswell-note-links-formatting-red.log`. Bold/Italic passed; Bullet/Numbered list lost safe ownership and could not report saved on both viewports. |
| First corrected 32-case review matrix | 28 passed/4 failed; `/tmp/scribeswell-note-links-review-green1.log`. Remaining native Undo failures occurred only after end-position typing following Redo. |
| Temporary isolated Chromium DOM probes, `note-undo-probe.spec.cjs --project=desktop --workers=1` | `/tmp/scribeswell-note-links-undo-probe.log` and `/tmp/scribeswell-note-links-undo-caret-probe.log`. Diagnostics showed end-position typing was ignored against the noneditable atom, rather than merged into an incorrect Undo group. Empty native inserts/focus tricks did not repair that caret; an empty editable text-node landing did. The temporary probe file was removed; these diagnostics are not application acceptance. |
| Expanded native-key review attempt | `/tmp/scribeswell-note-links-review-green2.log`, interrupted after observing that the first boundary helper normalized ordinary typing and split its native Undo group. The helper was restricted to owned atomic boundaries; no expectation was weakened. |
| App browser command with `--grep 'note links review: native insertion Undo'` | 8 passed; `/tmp/scribeswell-note-links-undo-qualified.log`. Native key events type and Undo/Redo writing before insertion; insertion Undo/Redo preserves writing/source URLs at start/middle/end; subsequent actual typing is asserted, then independently undone/redone with the atom retained. |
| Initial fresh-atom paste/keyless checks | 4 passed; `/tmp/scribeswell-note-links-input-boundary-red.log` (historical filename). |
| Exact post-Redo paste/keyless boundary reproduction | 4 failed; `/tmp/scribeswell-note-links-input-boundary-redo.log`. |
| Same post-Redo input checks after sharing the boundary helper with native trusted `beforeinput` and paste's native `insertText` | 4 passed; `/tmp/scribeswell-note-links-input-boundary-qualified.log`. The landing has no stored marker/character. Physical-device keyboard/IME qualification remains pending. |
| `P -m pytest apps/scribeswell/tests/test_studies_owner_integration.py -k note_link_checkpoint -q` | Initial5 failed, then5 passed/37 deselected; `/tmp/scribeswell-note-links-oracle-red.log` and `/tmp/scribeswell-note-links-oracle-qualified.log`. Pure negative-oracle/control proof; no owner/native integration. |

Final frozen-source targeted command:

```sh
npm run test:browser --workspace=apps/scribeswell/web -- personal-notes.spec.cjs reader.spec.cjs --grep 'note links review:|note links: insertion inside source at|collected picker|collected passages persist|selector closes when keyboard focus leaves|typed reference visibly' --workers=1
```

**50 passed** on desktop/mobile in1.6min, exit0;
`/tmp/scribeswell-note-links-review-qualified.log`. This includes native editing
history, safe source fragments/marks/URLs, all reported correction rows, bold/italic/
list save/reload across an existing atom, passage-only Notes preview reopening,
noncanonical stored label preservation in Read/Edit and unrelated-save serialization,
and affected existing reader/collection picker behavior. Ordinary copied metadata
is separately refused. No runtime/test source changed during this final targeted run.

The parent delivery workflow owns complete regression/build verification and final
spec/canonical/checkpoint reconciliation. Earlier complete runs above are milestones
for their own source versions. Native/actual-owner/session integration remains
prepared only under direction266; no KDG/shared ports, provider, migration, activation
or deployment action occurred. Read-aware previous-version qualification and
coordinated adoption remain prerequisites to richer-write activation. Production,
live signup, physical devices and manual acceptance remain unqualified.

## Atomic deletion correction after complete regression

The parent's frozen complete312-case browser regression reported310 passed/2 failed:
both unchanged desktop/mobile `note links: Backspace removes atomic inline and retains
version2` cases left the passage-only atom present. `/tmp/scribeswell-note-links-parent-browser.log`
is a failed complete run, not a complete pass. The new editable empty text-node landing
remained necessary for typing/paste/keyless native input and was retained.

The correction handles only native character deletion adjacent to a verified owned
atom: the native `beforeinput` path identifies the atom across the empty caret text,
selects only that atom and issues the existing native `delete` editing command. It
covers backward and forward deletion, including backward deletion when component
keydown propagation is stopped. Reentrant native commands are excluded by the same
native-editing guard. Ordinary text deletion keeps its native default. The existing
per-editor metadata registry supports deletion Undo/Redo; the document remains2 when
its last atom disappears. No separate history engine, stored caret marker, Python,
owner authority or integration behavior changed.

Targeted chronology:

| Exact browser scope, with app workspace and `--workers=1` | Result / retained log |
| --- | --- |
| `personal-notes.spec.cjs --grep 'note links deletion:|note links: (Backspace|Delete) removes'` | 2 failed/8 passed; `/tmp/scribeswell-note-links-deletion-red.log`. Existing Backspace failed unchanged; new cases with preceding writing already passed, isolating the passage-only boundary. |
| `personal-notes.spec.cjs --grep 'note links deletion:.*on empty'` | 4 failed/2 passed; `/tmp/scribeswell-note-links-deletion-empty-red.log`. Both Backspace and keydown-blocked backward deletion failed at the exact empty-caret boundary; forward Delete passed. |

Final frozen-source targeted command:

```sh
npm run test:browser --workspace=apps/scribeswell/web -- personal-notes.spec.cjs --grep 'note links deletion:|note links: (Backspace|Delete) removes|note links review: native insertion Undo|note links review:.*editable caret boundary' --workers=1
```

**28 passed** on desktop/mobile in1.2min, exit0;
`/tmp/scribeswell-note-links-deletion-qualified.log`. Existing deletion expectations
were unchanged. Added empty/nonempty-note cases verify one-step Backspace/Delete,
backward native `beforeinput` without component keydown handling, deletion Undo/Redo,
unchanged surrounding writing and version2 after each acknowledged save. The same
run preserves native insertion/typing/source-anchor Undo/Redo and post-Redo paste /
keyless input. Runtime/tests stayed frozen during that run and were returned to the
parent for complete affected notes/build verification. Python249 remains the parent's
unchanged prior passing result. No native/owner/session integration, KDG/shared ports,
search design, canonical/spec, migration, provider or activation work was performed.

## Parent final component qualification

After P1 correction, the complete affected source-frozen command passed **324**
desktop/mobile checks in8.0min, exit0:

```sh
SCRIBESWELL_TEST_PYTHON=/tmp/scribeswell-manual-python/bin/python npm run test:browser --workspace=apps/scribeswell/web -- reader.spec.cjs personal-notes.spec.cjs --grep-invert 'native PostgreSQL' --workers=1
```

Log: `/tmp/scribeswell-note-links-parent-browser-final.log`. Both native-only browser
cases were explicitly excluded. This supersedes the failed310/312 milestone for
component qualification; the earlier failure remains recorded above. The116-file
runtime/test source inventory stayed unchanged throughout this final run.

The parent affected Python command passed **249**, one existing Starlette TestClient
deprecation warning,11.67s, exit0 (`/tmp/scribeswell-note-links-parent-python.log`):

```sh
/tmp/scribeswell-manual-python/bin/python -m pytest apps/scribeswell/tests/test_note_passage_links.py apps/scribeswell/tests/test_passage_references.py apps/scribeswell/tests/test_personal_notes_contract.py apps/scribeswell/tests/test_personal_notes_api.py apps/scribeswell/tests/test_studies_owner_integration.py apps/scribeswell/tests/test_personal_notes_release.py -q
```

Python remained byte-unchanged through the subsequent frontend-only deletion fix.
Final `npm run build --workspace=apps/scribeswell/web` passed TypeScript/Vite,
with the existing chunk-size warning (`/tmp/scribeswell-note-links-parent-build-final.log`).
Catalogue/OpenAPI exporter checks, pinned TypeScript `api_client_current`, existing
migration-helper check and composition `--check-only` passed. Prepared owner JS syntax
and original baseline/historical fixture preservation passed. Native storage collection
found **18 tests**,0.27s; **none were executed**. No final native/actual-owner/session,
physical-device, live-signup, manual or production qualification is inferred.

Three independent BMAD reviews produced15 individual findings;14 patch rows grouped
only identical roots and were addressed with direct fixes/assertions. The transient-
log claim was refuted against repository-owned commands/results/chronology. Parent P1
then exposed and corrected atomic Backspace, with unchanged expectations and focused
red/green before this complete rerun. A scoped local component checkpoint preserves
this code while the delivery spec remains `in-review` for final integration under
direction266. No push, migration, activation, provider or shared KDG-port action.
