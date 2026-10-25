# Collected passages delivery evidence

Opt-in implementation,2026-10-25. Production activation remains disabled. The adopted
[passage contract](PASSAGE_REFERENCES_V1.md) and repository delivery spec govern this
bounded collection slice. Native and actual-owner final integration is **pending**
under direction266; no shared KDG instance or ports55481/55482 were used.

## Delivered behavior

- A deterministic offline66-book catalogue derives39 Hebrew-source book bounds from
  pinned `hebrew.json` and27 reference-only NT books from the pinned factual inventory.
  Backend/browser consume identical generated inventory and source-numbering identities.
  The generator checks both source hashes, derived output drift and its ownership manifest.
- Strict references preserve whole chapters, single verses and same-book cross-chapter
  ranges. English/declared Hebrew aliases, canonical Hebrew numbers, bounds and exact
  source/version matching reject invalid input without guessed numbering conversion.
- Owner-only collection reads/replacements use independent list revisions and ordinary
  controlled migration0003. Empty logical revision1 needs no backfill. Exact no-ops
  receipt without attribution/revision changes; changed list and compact receipt commit
  together. Retained entry IDs keep source identity/creation attribution. Receipt replay
  checks current owner/lifecycle and cannot restore a removed entry.
- One in-memory collection lane per study freezes original attempts and blocks overtaking.
  Conflict retains the addition/removal for deliberate current-list review and explicit
  new action. Acknowledged success always reads the current list; a failed read retries
  that read alone. Late read/account/navigation replies are rejected by generations.
- Notes remain first, followed by separate Passages with Add passage, Add current passage,
  explicit Open and Remove. Collection changes preserve the independent dirty note/title
  lane and reading positions. The same typed/browsable picker serves navigation and Add;
  Enter/matching chapter preserves a complete range, another chapter clears it, and Cancel
  restores focus without sending. Server input rejection retains editable candidate input.
- Explicit Open navigates only the active existing reader pane and retains range endpoints
  in its URL. Reference-only entries show Text unavailable and no fabricated word actions;
  supported-source failures keep a truthful Retry. Existing public URLs remain accepted.

The collection-specific transport cap is131,072 bytes; all other private commands retain
65,536 bytes. Existing JSON depth/value and DTO bounds stay enforced. This narrowly
implements the agreed200-entry maximum rather than expanding note/document budgets.

## Red evidence and corrections

1. Initial focused parser test failed collection because `passage_references` did not exist.
2. Desktop component acceptance created a study and dirty Hebrew note, then failed waiting
   for the absent Add passage control (`npm run test:browser -- --grep 'collected passage
   keeps' --project desktop --workers 1`,30s). This preceded collection UI implementation.
3. The valid200-distinct-range boundary test failed with the previous65,536-byte cap,
   producing safe `ContractInputError`;131,072 is the approved collection-only correction.
   An earlier draft of that test also exposed an invalid generated Genesis verse; the
   fixture now derives real bounds rather than weakening reference validity.
4. A sandboxed combined Python run stopped progressing near the final HTTP tests and was
   interrupted. The same focused suites completed outside the sandbox. Sandbox-only
   browser startup and ephemeral socket-test EPERM failures were rerun with approved
   local process permissions. No native/integration fixture was enabled by these reruns.
5. An intermediate broad browser run overlapped final edits:157 passed,5 failed,2 native
   skips. Failures were responsive long-name/chapter browsing (both projects), selector
   focus departure (both), and the existing mobile create/write/reopen case. This is not
   frozen-source verification. Selector corrections preserve API display metadata while
   retaining catalogue identity/bounds, prevent programmatic scroll from triggering hover
   changes, and close on Shift+Tab from the first picker field. Original expectations
   remain unchanged. Final affected regression results are recorded below. A later backend-only identity guard correction does not change the intercepted browser runtime.

## Executed checks

Python uses `/tmp/scribeswell-manual-python/bin/python` (`P` below). Browser commands
run from the repository with `--workspace=apps/scribeswell/web`, workers1. Component
fixtures intercept private owner/corpus HTTP and prove consuming behavior, not SQL.

| Command | Result |
| --- | --- |
| `P -m pytest apps/scribeswell/tests/test_passage_references.py apps/scribeswell/tests/test_personal_notes_contract.py apps/scribeswell/tests/test_personal_notes_api.py apps/scribeswell/tests/test_studies_owner_integration.py apps/scribeswell/tests/test_personal_notes_release.py -q` |217 passed,1 existing TestClient deprecation warning,12.55s; `/tmp/scribeswell-passages-python-final.log`. Fixture-control tests mock startup; only the collision test uses an ephemeral port. |
| `npm run test:browser --workspace=apps/scribeswell/web -- --grep collected --workers 1` | Earlier component milestone24 passed34.2s, including2 existing privacy matches. |
| `P -m pytest apps/scribeswell/tests/test_personal_notes_storage.py --collect-only -q` |16 native tests collected,0 executed; `/tmp/scribeswell-passages-native-collection.log`. |
| `node --check apps/scribeswell/web/tests/studies-owner.integration.cjs` | Passed; syntax only, actual-owner scenario not executed. |

Generated OpenAPI and TypeScript were updated with their owning exporter and existing
pinned local `platform/api-client` generator; no generated output was hand-edited.
The generator first reported sandbox `api_client_generation_failed`; an approved local
child-process run returned `api_client_generated`. Final results:

| Command | Result |
| --- | --- |
| `npm run test:browser --workspace=apps/scribeswell/web -- reader.spec.cjs personal-notes.spec.cjs --workers 1` |176 passed,2 native-only cases skipped,4.4m; `/tmp/scribeswell-passages-browser-final.log`. Stable browser runtime before the later review corrections and test-only Python portability change. Skips are deferred native proof, not successes. |
| `SCRIBESWELL_TEST_PYTHON=/tmp/scribeswell-manual-python/bin/python npm run test:browser --workspace=apps/scribeswell/web -- --grep 'collected reference parser Python' --workers 1` |2 passed4.6s; `/tmp/scribeswell-passages-parity-portable.log`. Reusable test defaults to `python3`; `SCRIBESWELL_TEST_PYTHON` selects an installed environment with the declared Python dependencies. |
| `npm run test:browser --workspace=apps/scribeswell/web -- --grep 'collected|typed reference visibly|selector closes when keyboard|long bilingual|explicitly enroll, create' --workers 1` |44 passed1.1m; `/tmp/scribeswell-passages-focused-browser.log`. |
| `npm run build --workspace=apps/scribeswell/web` |Passed; `/tmp/scribeswell-passages-build.log`. Existing chunk-size warning remains. |
| `P apps/scribeswell/tools/py/build_reference_catalogue.py --check` |Passed; pinned inputs and identical generated copies. |
| `P apps/scribeswell/tools/py/export_personal_notes_contract.py --check` |Passed. |
| Existing pinned Node26/tool-owner API-client CLI with `--schema .../personal-notes-v1.openapi.json --output .../generated/personal-notes --check` |`api_client_current`; same local paths/toolchain documented in [rename evidence](STUDY_RENAME_EVIDENCE.md). |
| `node --experimental-strip-types apps/scribeswell/tools/sync_personal_notes_database.mjs --check` |Passed, existing shared helper unchanged. |
| `python3 tools/py/run_compose_supabase.py --check-only` |Passed; dry run, no files changed. |
| `git diff --check -- apps/scribeswell` |Passed. |

A focused actual replacement-method test observed a missing retained-reference identity
guard: assigning a fresh ID to a reference still present in the replacement did not
raise. `/tmp/scribeswell-passages-identity-red.log` records1 failed/1 passed. The owner
method now refuses both source rebinding under an existing ID and ID rebinding of a
retained canonical reference before any write. Both control-flow cases pass in the217
suite above. Their cursor double does not establish SQL permissions/transaction proof;
the corresponding native assertion is prepared for the deferred phase.

## Requirement-to-test traceability

| Matrix row / behavior | Executed component/contract coverage | Prepared final integration evidence |
| --- | --- | --- |
| English/Hebrew chapters/ranges collect/reopen without note/title/reading change | `test_reference_identity`; `collected passages persist chapters Hebrew ranges overlap and duplicate IDs without navigation`; dirty-note collection/Open cases | Native collection independence/attribution; owner UI reload+SQL checkpoints |
| Typing, matching/another chapter, Enter and Cancel/focus | Picker rejection/cancel/different-chapter case; matching-chapter full-range case; typed-reference positioning and existing focus/viewport cases | Real-device/manual keyboard/selection remains unqualified |
| Exact duplicate vs overlap; no false change | Duplicate/overlap browser case; strict duplicate DTO case | Native no-op header/rows/revision/receipt comparison |
| Invalid, ambiguous, foreign-version and forged inputs | Parameterized parser/strict DTO/HTTP safe-rejection tests; typed ambiguous choices; editable server rejection;200-entry bound | Native structural constraint tests |
| Explicit active-pane Open/range/reference-only/outage | Persist/reference-only, dirty-note/other-pane and supported-source Retry cases | Actual-owner stored Matthew Open plus unchanged notes/title SQL |
| Independent revisions and stale-list review | Collection conflict/new operation and dirty-note cases; existing title/note regressions | Native collection CAS races and immutable note/title snapshots |
| Lost reply, original retry, frozen payload and post-ack read failure | Uncertain operation, beforeunload, no-overtaking and read-only retry cases | Native replay/mismatch/no-resurrection; owner one-effect receipt checks |
| Current access, closed/wrong owner and late account/navigation |401/403/404 component cases; late account and late study-read cases; HTTP authority-before-storage tests | Native wrong-owner/closed-parent/lookup; actual-owner denial SQL snapshot |
| Migration failure and old consumer | Existing old note/title HTTP/DTO regressions; owner fixture failure/control tests are wrappers only |0003 failure/rollback/forward retry, restricted SQL/RLS and frozen previous consumer remain pending |

## Prepared but not executed

The native fixture now freezes both0002 and0003 out of the0001 previous-history copy,
qualifies the immediate0002 history, injects failure after actual0003 DDL in a copied
history, and expects transactional rollback before forward retry. Applied0001/0002
files are unchanged. Added native cases cover logical empty/no-op, reference/order
identity, attribution, current lifecycle/ownership, replay/mismatch/no-resurrection,
CAS/same-operation races, overflow, forced RLS/roles, structural shape/order/uniqueness
and unchanged note/title rows. The existing generic later-failure probe now descends
from0003 without creating multiple heads. **These are prepared assertions, not proof.**

The actual-owner fixture inventories the pinned catalogue inputs and new source files,
adds collection rows to protected snapshots, and brackets UI add/duplicate/remove/reload
with independent SQL checks of ordered reference identity, actor/UTC attribution,
independent revisions, exact receipts, unchanged notes/title and denial invariance.
It also prepares protected-disable checks for read/write/outcome lookup. The scenario
has syntax and fixture-control evidence only; no owner HTTP/native/browser integration
was executed. Live signup/provider, production release, migration/backup/recovery and
physical iOS/Android gates remain open. No activation/deployment/provider change occurred.

## Reuse and ownership impact

Application-specific catalogue, picker, collection storage and operation lane; no neutral
shared UI promotion is justified. The existing shared migration helper is consumed
unchanged. Scaffold/generator platform choices and accepted ADRs remain unchanged.
No competing Access/Identity/Notifications owner, Leave change or factory implementation
is introduced. Agent context is unchanged. Owner contracts and this evidence record
are updated in the same delivery; canonical-memory reconciliation is maintained by the
parent BMAD execution.

## Independent review and final component checkpoint

All three same-model independent BMAD reviewers completed before triage. The delivery
spec records all14 findings separately:12 direct corrections/prepared-proof items
addressed, one unreachable alias-collision claim rejected, one final-integration gate
retained under explicit direction266. Corrections preserve punctuation rather than
joining numeric coordinates, align book-period parser parity, qualify reference-only
chapter boundaries without corpus requests, reject malformed current URLs, preserve
Stay/read and removal intent context, reject obsolete focus completion, distinguish
confirmed commits on unload, retain duplicate input and test newer-list conflict recovery.
The maximum200-entry native deadline/competition scenario is prepared only.

| Final parent command | Executed result |
| --- | --- |
| `SCRIBESWELL_TEST_PYTHON=/tmp/scribeswell-manual-python/bin/python npm run test:browser --workspace=apps/scribeswell/web -- reader.spec.cjs personal-notes.spec.cjs --workers=1` |226 passed,2 native-only skips,5.0m; `/tmp/scribeswell-passages-parent-browser.log`. |
| `P -m pytest apps/scribeswell/tests/test_passage_references.py apps/scribeswell/tests/test_personal_notes_contract.py apps/scribeswell/tests/test_personal_notes_api.py apps/scribeswell/tests/test_studies_owner_integration.py apps/scribeswell/tests/test_personal_notes_release.py -q` |226 passed,1 existing TestClient warning,12.52s; `/tmp/scribeswell-passages-parent-python.log`. |
| `npm run build --workspace=apps/scribeswell/web` |Passed; existing chunk-size warning, `/tmp/scribeswell-passages-parent-build.log`. |
| Catalogue/OpenAPI/pinned TypeScript-client/helper checks and composition dry run above |All passed; client `api_client_current`. |
| `P -m pytest apps/scribeswell/tests/test_personal_notes_storage.py --collect-only -q` |17 collected,0 executed,0.67s; `/tmp/scribeswell-passages-parent-native-collection.log`. |
| `node --check apps/scribeswell/web/tests/studies-owner.integration.cjs` |Passed; syntax only. |

The31 runtime/test/generated source hashes stayed identical through parent verification.
Focused review checks also passed52 parser,60 browser and8 strengthened follow-up cases;
logs `/tmp/scribeswell-passages-review-parser.log`, `...-review-browser.log` and
`...-review-browser-final.log`. Earlier failures remain above. Native SQL, real-owner
HTTP/UI/SQL and session integration stay pending for the final phase. The delivery
spec remains in-review; a local component checkpoint is not full delivery/activation.
