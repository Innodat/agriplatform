# Own-study library search — component delivery, final integration pending

The development/test opt-in implements the [closed search contract](LIBRARY_SEARCH_V1.md).
Production remains disabled. No native/owner/session execution, migration, provider,
deployment or activation ran; direction266 reserves final integration. Intercepted
browser responses and storage-method doubles do not establish PostgreSQL matching,
locale behavior, actual owner authority, permissions or zero mutation.

## Acceptance chronology

`P=/tmp/scribeswell-manual-python/bin/python`; commands run from repository root.
The root `.venv/bin/python` lacks pytest. Initial collection of
`test_library_search.py` failed because the new module did not exist; that is a
missing-component result, not runnable outer behavior acceptance. The API route
was edited before its runnable acceptance assertion was added: no API-before-code
red is claimed. Before frontend implementation, the runnable desktop acceptance
`library search finds saved results beyond the first page and returns at loaded depth`
failed while waiting for the absent accessible Search studies field (30-second
Playwright timeout). Its exact command was
`npm run test:browser --workspace=apps/scribeswell/web -- personal-notes.spec.cjs --grep 'library search finds' --project desktop --workers=1`;
the tool execution output retains that red result. After implementation the same desktop/mobile case passed2/2.

The first expanded search matrix passed10 and failed2: adding Loading above the
list moved More during a double-click, so the second click opened a result. Moving
the loading feedback below the stable list/More controls corrected the behavior;
the same assertions passed12/12. The completed search matrix later passed20/20.

A focused401 acceptance reproduced loading that remained active after the shared
failure path advanced the account epoch. The401 path now clears library pending and
loading, and a successful current read clears the prior sign-in/read error. The existing authority mask remains during401: private candidate/applied context
stays in account-scoped memory and reappears only after fresh successful same-account
verification/retry.503 and400 keep the editable candidate. The initial assertions
passed on desktop/mobile2/2; `/tmp/scribeswell-library-search-auth-red.log`
and `/tmp/scribeswell-library-search-auth-green.log` retain both results. A just-started
full run was interrupted before that correction (exit130), with no pass claim.

The first complete affected notes run encountered obsolete fixture interception:
`reviewLibrary` treated the new `/search` read as a study-ID detail path. That run
was interrupted (exit130), is not a complete pass and has no frozen-source claim.
Those fixtures now intercept the new read while preserving their original behavior
assertions. The existing delayed-library/rename case also preserves a newer confirmed
metadata revision when an older search response arrives late. Focused and final
complete-run evidence follows below.

## Executed verification

| Command | Result / retained evidence |
| --- | --- |
| `P -m pytest apps/scribeswell/tests/test_library_search.py -q` | 27 passed; strict read/body, canonical query/reference interpretation, closed cursor, router and one-read storage-method behavior. |
| `P -m pytest apps/scribeswell/tests/test_library_search.py apps/scribeswell/tests/test_personal_notes_contract.py apps/scribeswell/tests/test_personal_notes_api.py apps/scribeswell/tests/test_note_passage_links.py apps/scribeswell/tests/test_passage_references.py -q` | Final229 passed, one existing TestClient deprecation; `/tmp/scribeswell-library-search-python-final.log`. |
| `npm run test:browser --workspace=apps/scribeswell/web -- personal-notes.spec.cjs --grep 'library search' --workers=1` | 20 passed (desktop/mobile); `/tmp/scribeswell-library-search-browser.log`. |
| `P apps/scribeswell/tools/py/export_personal_notes_contract.py --check` | Passed; generated through its owning exporter. |
| Pinned API-client generation/check (below) | Passed; generated owned TypeScript, never hand-edited. |
| `P apps/scribeswell/tools/py/build_reference_catalogue.py --check` | Passed; catalogue unchanged. |
| `node --experimental-strip-types apps/scribeswell/tools/sync_personal_notes_database.mjs --check` | Passed; shared migration helper unchanged. |
| `python3 tools/py/run_compose_supabase.py --check-only` | Passed; 15 migrations/2 seeds/5 function directories; no files changed. |
| `npm run build --workspace=apps/scribeswell/web` | Passed TypeScript/Vite; existing large-bundle warning; `/tmp/scribeswell-library-search-build-final.log`. |
| `P -m pytest apps/scribeswell/tests/test_personal_notes_storage.py --collect-only -q` | 19 prepared tests collected; no native fixture executed. |
| `node --check apps/scribeswell/web/tests/studies-owner.integration.cjs`; `P -m py_compile apps/scribeswell/tests/studies_owner_fixture.py apps/scribeswell/tests/test_personal_notes_storage.py` | Passed syntax only; no owner/native execution. |

Browser and TestClient checks use local-process escalation because the sandbox
blocks their local sockets/processes. The first un-escalated generator attempt failed
with `api_client_generation_failed`; the same pinned owning generator passed with
local-process access. The earlier sandbox TestClient attempt was not a passing run.

Pinned owning generation/check (omit `--check` to regenerate):

```sh
platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node platform/deployment/.local/scaffold-application/proof-yc4xuk/root/platform/api-client/src/cli.mjs --schema /home/ck/repos/innodat/agriplatform/apps/scribeswell/contracts/personal-notes-v1.openapi.json --output /home/ck/repos/innodat/agriplatform/apps/scribeswell/web/src/generated/personal-notes --check
```

## Requirement traceability and boundaries

| Requirement | Executed component evidence | Prepared final integration |
| --- | --- | --- |
| Matching beyond first unfiltered page; saved title/note/list/custom label | Browser read/return acceptance, SQL-construction/storage-method assertion that filtering is inside one query before order/limit | Restricted native test creates22 newer nonmatching studies, formatted text across marks/external links, list text/custom labels and checks actual results |
| English/Hebrew chapter/range/book; cross-chapter and reference-only Matthew | Canonical query/parser cases and browser English/Hebrew/Unicode body semantics | Actual collection/note reference matching and symmetric inclusive overlap, book-only Matthew, no corpus fetching |
| Literal punctuation/NFC, invalid reference, strict malformed/blank/oversized read | DTO/transport/cursor cases, browser candidate/Enter/Clear; SQL uses literal POSITION with lower/NFC | Qualified PostgreSQL17 UTF8 locale/lower/NFC, malformed JSON array/object/numeric extraction guards |
| Stable pagination/dedup/current generation | Desktop/mobile duplicate More, stale page/query success/denial and old-finally/current-loading cases | Native duplicate notes/references and equal-timestamp keyset traversal, no dropped/duplicate studies |
| Retained depth/scroll/focus and reader/editor context | Desktop/mobile multi-page refreshed return with stable focus/scroll; dirty composing note preserved across search with unchanged reader URL and no note write | Actual-owner UI search/open/return and independent SQL snapshots |
| Account replacement/current denial/verification outage | Desktop/mobile clears candidate/results on replacement/denial; hides unavailable results, retries applied query while preserving candidate; rejects late old denial | Actual owner second-account and protected-disable search refusal |
| No mutations and old GET/list compatibility | Search-only storage method issues one SELECT; strict read has no operation field; list cursor module/wire unchanged | Native before/after full table/receipt snapshots and old GET cursor continuation; owner search-before/search-after independent full-state equality |
| Private terms absent from URLs/storage | Browser Unicode/literal terms inspected in body only, no query URL/storage; no snippets/echo in StudyPage | Existing owner credential inspection remains; search before/after adds no grant/receipt effects |

The native test `test_native_library_search_filtered_matching_pagination_isolation_and_zero_mutation`
is prepared in `test_personal_notes_storage.py`, collected only. Owner checkpoints
`search-before` / `search-after` snapshot all existing owner/app tables and require
exact equality. The prepared browser searches saved note/title/reference data,
opens/returns a result, checks foreign-account isolation and403 after protected disable.
The search read does not certify or repair an entire corrupt stored aggregate.
Ordinary writes validate that aggregate through the closed DTO. Extraction recognizes
visible paragraph/list/text/link-label fields with key/type/array guards and excludes
arbitrary metadata and serialized JSON. A recognized scalar passage-link label can
contribute literal text even if a corrupt alternate write damaged its reference;
canonical-reference matching independently validates catalogue identity/target bounds.
Prepared malformed rows distinguish those behaviors; no invalid canonical reference
is inferred. This is a technical qualification limit, not additional authority.

Native SQL semantics/permissions and actual-owner zero mutation are pending; none of
the SQL-string or intercepted browser assertions qualify those claims.

## Impact decisions

Scaffold: no generator or migration change; existing app API and restricted transaction
patterns are reused. Shared UI: app-specific search/list state; no promotion. Agent
context: unchanged. Documentation: adopted contract, personal-note contract and this
evidence updated; canonical memory reconciliation remains parent-owned. ADRs: no new
or changed accepted decision. No Access/Identity owner, sharing/notification/grants,
Leave/factory, corpus publication, schema/index/search model or production work added.

## Pre-review frozen affected run and focused follow-ups

Exact complete command:
`npm run test:browser --workspace=apps/scribeswell/web -- personal-notes.spec.cjs --workers=1`.
It exited0 with **296 passed,2 expected native-browser skips** in7.9minutes;
`/tmp/scribeswell-library-search-notes-final.log` retains the full result. This is a
complete affected component pass, not native or actual-owner qualification.

The140-file inventory covers app backend, web source/tests/configuration, Python tests,
owned tools/contracts and pinned reference catalogue. The inventory files
`/tmp/scribeswell-library-search-source-before.json` and
`/tmp/scribeswell-library-search-source-after.json` are byte-identical; `cmp` exited0.
Their SHA256 is `1caf1ea951673b70c4de146bb19dc1303be4593f1f3937d4ec7e6427cab8c27d`.
Only documentation was edited during this complete run. The inventory script is
`/tmp/scribeswell-library-search-hash.py`.

After the complete run, tests-only follow-ups strengthened401 exact-candidate
restoration after fresh successful verification, added400 editable-candidate correction,
and explicitly distinguished corrupted visible label matching from invalid canonical
reference matching in the prepared native fixture. The final focused command
`npm run test:browser --workspace=apps/scribeswell/web -- personal-notes.spec.cjs --grep 'library search' --workers=1`
exited0 with **24 passed**; `/tmp/scribeswell-library-search-focused-final.log`.
The prepared fixture was recompiled and collected:19 tests, no native execution;
`/tmp/scribeswell-library-search-native-collected.log`.

A briefly applied query-schema metadata description/NUL exclusion after this run was
restored at the parent review hold, and the original output was reproduced through
its owning exporter/generator. No behavioral validator change occurred. The final
runtime/DTO/OpenAPI/generated bytes again exactly match the frozen inventory; NUL
schema representation remained a parent review-triage item at that pre-review checkpoint. The final affected Python
suite and OpenAPI/TypeScript checks were rerun after restoration.

The final follow-up inventory is
`/tmp/scribeswell-library-search-source-followup.json`, SHA256
`387c5481b72ddf356d43557b798c4ad13a8833ca73cb9cd23320120d92eb27b6`.
Compared to the frozen inventory, exactly these two test paths changed:

| Path | Frozen SHA256 | Follow-up SHA256 |
| --- | --- | --- |
| `apps/scribeswell/tests/test_personal_notes_storage.py` | `37284e90c09c46ef2b67b1be5f6af32ee6cee34d609d0050e35ea8225d0c9a6f` | `0392cb873a1d71dba98f14b0294ae84782542d52019d541567ca0c9bdecf9070` |
| `apps/scribeswell/web/tests/personal-notes.spec.cjs` | `57a830a36493b25e793e5e3b1e5ab150b5eec2c2ce5b097a7a342e8a01c480aa` | `952191c3e69fd55afbd71cdcc632da85a98035da8e060af6bcdf87b6ab124c1e` |


## Independent review corrections and final parent qualification

Three context-free BMAD layers returned13 findings; parent P1 added the prepared
owner pre-enrollment status correction. All14 were triaged individually before
combining only duplicate roots B1/E2 and B4/E1. All12 roots received direct corrections;
none was deferred. The delivery spec retains each verdict/evidence and route.

The focused desktop red command
`npm run test:browser --workspace=apps/scribeswell/web -- personal-notes.spec.cjs --grep 'library review:' --project desktop --workers=1`
reproduced five failures: composition submitted prematurely; masked input remained
editable; More moved current focus; hidden completion moved Analysis scroll143→676;
and invalid feedback lacked input association. `/tmp/scribeswell-library-review-red.log`
retains those failures. The fixes preserve normal Enter, the exact masked candidate,
visible refreshed-return restoration and other working contexts. Error state follows
the typed machine code rather than English presentation text. Completion status
announces loaded studies without including private terms.

The owning DTO now exports the NUL exclusion and scalar-Unicode description; OpenAPI
and client were regenerated through owning tools. Runtime validation is unchanged.
Prepared native fixtures now include active format1 unique-body matching, otherwise-
valid malformed numeric targets, reversed ranges and mismatched catalogue/version/
versification/document negatives. The initial owner search correctly expects503 for
absent Identity setup, matching its existing initial GET; later disabled403 remains.

Executed focused review checks:

- `npm run test:browser --workspace=apps/scribeswell/web -- personal-notes.spec.cjs --grep 'library search|library review:' --workers=1` —36 passed39.9s;
  `/tmp/scribeswell-library-review-focused-final.log`.
- `P -m pytest apps/scribeswell/tests/test_library_search.py apps/scribeswell/tests/test_personal_notes_contract.py -q` —152 passed, one existing warning2.84s;
  `/tmp/scribeswell-library-review-contract.log`.
- Native test collection —20 collected only; `/tmp/scribeswell-library-review-native-collected.log`.
  Owner/native syntax and owning exporter/pinned-client checks passed; no integration ran.

The final140-file source inventory is
`/tmp/scribeswell-library-search-source-review-final.json`, SHA256
`a30a1d1e5d30e6334342bb567ce2130a9a1cda6fed0d9baac604c0f0f97cce40`.
Parent final complete component regression runs against that new frozen snapshot;
the earlier296-pass result is explicitly the pre-review snapshot.


The parent complete command
`SCRIBESWELL_TEST_PYTHON=/tmp/scribeswell-manual-python/bin/python npm run test:browser --workspace=apps/scribeswell/web -- reader.spec.cjs personal-notes.spec.cjs --workers=1`
finished **359 passed,1 failed,2 expected skips** in9.6minutes, exit1;
`/tmp/scribeswell-library-search-parent-final-browser.log`. The mobile multi-page
return case restored focus but received scroll0 where its unchanged assertion requires
more than1215. This is not a full pass. The140-file source inventory remained identical
after the run (`/tmp/scribeswell-library-search-parent-final-after.json`). Parent P2
tracks the direct scroll/restoration correction; checkpoint and subsequent implementation
wait for a corrected frozen full run.

On this pre-P2 snapshot, the parent affected Python command (search, note links,
passage references, personal-note contract/API, owner fixture-control and release
modules) passed277/1existingwarning14.17s; app TypeScript/Vite build passed with the
existing chunk warning. Exporter/catalogue/pinned-client/helper/composition checks
passed; native20 collected0.79s and fixture syntax passed, without execution.


## Parent restoration and supersession corrections

The original mobile return case passed15 focused repetitions under numeric-only
tracing; that did not resolve or invalidate the failed full run. A deterministic
MutationObserver-triggered layout scroll then reproduced the exact failure: opening
the selected-study DOM collapsed the surface to0 while its old passive scroll listener
could still capture it. The saved1265 anchor became0 before the next refreshed read.

Position capture is now protected from successful selection commit through visible
restoration. An early implementation locked at network-read start; its focused
winning-selection regression caught that this prevented a later selected result from
becoming the return anchor. Moving the lock to successful selection commit corrected
that regression. More explicitly unlocks a superseded restoration; the parent's
subsequent stuck-lock suspicion P5 was refuted by that existing guard and caused no
source/test change or additional rerun.

Parent P3 reproduced a queued old animation frame stealing input focus after a newer
query, and P4 reproduced an unfinished old selection reopening Study A over a newer
search. The frame now checks live account/epoch/query/navigation/selection before
any focus or scroll mutation; selected-study success/error also require the captured
library generation. Library loading remains independent from selection loading.

| Exact focused browser selector (each used `npm run test:browser --workspace=apps/scribeswell/web -- personal-notes.spec.cjs --grep '<selector>' --project mobile --workers=1`) | Observed red evidence |
| --- | --- |
| `queued layout-collapse` |1 failed, scroll0 versus required>1215; `/tmp/scribeswell-p2-collapse-red.log` |
| `winning pending selection` |1 failed after the early-lock attempt; `/tmp/scribeswell-p2-pending-selection-red.log` |
| `superseded queued refresh frame` |1 failed, search input lost focus; `/tmp/scribeswell-p2-queued-frame-red.log` |
| `newer search supersedes` |1 failed, stale Study A heading remained; `/tmp/scribeswell-p2-selection-query-red.log` |

The original return test and its assertion are unchanged. Final focused command
`npm run test:browser --workspace=apps/scribeswell/web -- personal-notes.spec.cjs --grep 'library search|library review:' --workers=2`
passed **44 desktop/mobile cases in30.5s**; `/tmp/scribeswell-p2-focused-final.log`.
Temporary runtime traces were removed. Before/after140-file inventories
`/tmp/scribeswell-library-search-source-p2-final.json` and
`/tmp/scribeswell-library-search-source-p2-after.json` match byte-for-byte, SHA256
`b50a21f024f41d31cb86d0c83e991831115ea5fe37d715be1de33965c70ac9d6`.

The initial13 review findings plus parent P1–P4 total17 actionable individual rows;
all received direct corrections. P5 is a separately recorded refuted finding.
Only B1/E2 and B4/E1 share roots; no actionable finding is deferred. Final parent
complete verification follows against this new frozen snapshot, retaining the failed
359/1/2 run above. Native/owner/session execution remains deferred.


## Final component checkpoint — integration still pending

The corrected source completed the parent command
`SCRIBESWELL_TEST_PYTHON=/tmp/scribeswell-manual-python/bin/python npm run test:browser --workspace=apps/scribeswell/web -- reader.spec.cjs personal-notes.spec.cjs --workers=2`
with **368 passed,2 expected native-browser skips in6.8minutes**, exit0;
`/tmp/scribeswell-library-search-parent-p2-browser.log`. Two isolated browser workers
share the local component server, without native/owner services. The140-file source
inventory stayed byte-identical through that full run:
`/tmp/scribeswell-library-search-parent-p2-before.json` and
`/tmp/scribeswell-library-search-parent-p2-after.json`, matching the b50a21f0 snapshot.
The prior359/1/2 run remains a failed run, not rewritten as a pass.

The exact affected Python command
`P -m pytest apps/scribeswell/tests/test_library_search.py apps/scribeswell/tests/test_note_passage_links.py apps/scribeswell/tests/test_passage_references.py apps/scribeswell/tests/test_personal_notes_contract.py apps/scribeswell/tests/test_personal_notes_api.py apps/scribeswell/tests/test_studies_owner_integration.py apps/scribeswell/tests/test_personal_notes_release.py -q`
passed **277 tests,1 existing TestClient warning in18.02s**;
`/tmp/scribeswell-library-search-parent-p2-python.log`. The owner-integration-named
Python module tests fixture controls; it did not start actual owner services.
`npm run build --workspace=apps/scribeswell/web` passed TypeScript/Vite with the
existing chunk warning; `/tmp/scribeswell-library-search-parent-p2-build.log`.

Final exporter/catalogue/pinned TypeScript (`api_client_current`)/shared migration
helper/composition dry-run checks passed. Composition planned15 migrations/2 seeds/
5 function directories without changing files. Native storage tests were collected
only:20 in0.23s; owner/native fixture syntax passed. No native SQL migration or query,
actual-owner/session integration, KDG shared ports, provider change, deployment or
production activation ran. No root-wide test/lint/CI qualification is claimed.

All17 actionable individual findings are corrected; P5 is refuted, none deferred.
Create a scoped local component preservation checkpoint with the delivery record
remaining **in-review** for user-deferred final native/actual-owner/session integration.
That checkpoint does not qualify real PostgreSQL matching, actual permissions/zero
mutation, live signup, physical devices or full ST-03/shared-study acceptance.
