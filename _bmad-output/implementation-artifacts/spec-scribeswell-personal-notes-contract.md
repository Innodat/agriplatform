---
title: 'Executable personal study notes contract'
type: 'feature'
created: '2026-10-23'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

The next useful Studies milestone is explicit study creation, writing an ordinary personal note and reopening saved text. Its app-owned wire contract is not concrete, while the separate Access owner has not implemented the required account-scoped admission/check path.

Close one cohesive, executable create/read/replace/outcome contract using strict DTOs, safe decoding, reproducibly generated unmounted OpenAPI and acceptance tests. Record transaction, saving and release obligations and exact owner dependencies in one app-owned canonical companion. This is contract readiness, not a usable private API/UI or full D2 closure. Preserve standalone signup, existing UX, dirty work and owner boundaries; implement no Access, Leave, app factory, database migration, mounted endpoint or deployment.

</frozen-after-approval>

## Implementation Notes

- Investigation: current services/access/organization_check.py accepts organization-scoped KDG checks only; own_account is a resource scope. platform/docs/architecture/contracts/scribeswell-study-enrollment.md is an owner draft. Do not infer account authority or create a synthetic organization.
- Canonical data-and-saving.md owns the draft aggregate/revision/operation grammar; account-access.md owns prerequisites. apps/scribeswell/backend/main.py remains public-reader-only. Existing generic validation errors expose input, so private adapters must be qualified before any mounting.
- Six scoped files: backend/personal_notes_contract.py, tests/test_personal_notes_contract.py, tools/py/export_personal_notes_contract.py, generated contracts/personal-notes-v1.openapi.json, docs/PERSONAL_NOTES_V1.md and this delivery record. Canonical untracked spec companions are reconciled through bmad-spec and excluded from commit.
- No human intent gap, irreversible effect or shared runtime interface. Bounds and contract serialization are routine implementation choices. First wire supports paragraphs/lists/bold/italic/external links; passage references/connections/highlights require later versioned compatibility work. Empty arrays are required, never silently dropped.
- ATDD: write whole create/save/reopen wire acceptance before source; observe missing contract failure. Then strict boundary tests, generation checks and independent configured blind review. DB atomicity, Access admission and browser saving remain future consuming evidence, not mocked implementation claims.
- Impact: no scaffold/shared UI/agent-context/ADR change; reusable promotion awaits a proven consuming UI. Docs: new owning contract and derived canonical links. Existing accepted ADRs remain binding.
- ATDD observed: /tmp/scribeswell-host-tests-312/bin/python -m pytest apps/scribeswell/tests/test_personal_notes_contract.py -q failed collection with missing module (1 error/1.94s), then initial 55 passed/2.59s. Expanded 65 passed/2.48s. Storage-unavailable code test observed 1 failure/1.97s before adding its safe variant. URL boundary test caught an incorrect fixture calculation (2049 bytes); corrected construction without changing the required 2048-byte assertion or implementation limit. Current focused 74 passed/2.06s.
- Broader 81-case command stalled when reaching the existing public HTTP TestClient case; interrupted (exit130), no completed broad-suite claim. That case enters the app database lifespan against an inert unavailable URL, but the exact stall cause was not investigated in this contract delivery. That attempt also included the pre-correction URL fixture failure. Re-run excludes exactly that database-lifespan HTTP case, retaining six public reader/morphology service regressions. No DB/container/provider effects or native SQL verification claimed.
- Configured review: context-free same-model blind reviewer inspected six original scope files, floor10 and10 findings. No other review layers configured. Added tests/requirements.txt as a bounded seventh file to make JSON Schema parity checks reproducible; backend dependencies unchanged. Offline jsonschema install was unavailable; ordinary uv install succeeded in the disposable test environment (jsonschema4.26.0). No runtime dependency or public API added by review patches.
- Review red: selected new cases observed21 failed/19 passed/74 deselected2.34s before source/schema fixes. First patched focused run114 passed2.79s. Additional terminal-newline parity cases observed2 failed/11 passed/103 deselected1.94s before rejecting embedded terminal controls in schema constraints. No expected result relaxed.
- Final affected command: `/tmp/scribeswell-host-tests-312/bin/python -m pytest apps/scribeswell/tests/test_personal_notes_contract.py apps/scribeswell/tests/test_reader_integrity.py apps/scribeswell/tests/test_word_inspector.py -q -k 'not empty_stored_verse_is_visible_http_failure'` —129 passed,1 explicitly deselected,3.55s, one existing Starlette/httpx deprecation. Includes123 new contract cases and6 existing reader/morphology regressions; no SQL/Access/browser end-to-end proof. Earlier80/74/65/55 counts are pre-review evidence.
- `/tmp/scribeswell-host-tests-312/bin/python apps/scribeswell/tools/py/export_personal_notes_contract.py --check` passed after regeneration. `python3 tools/py/run_compose_supabase.py --check-only` passed (15 planned migrations, no writes). Python compile, generated-reference/component-schema validation, canonical11CAP/38ST/23companion targets and scoped Markdown links pass. `git diff --check` passed. No root build or repository-wide test claim.

## Review Triage Log

| Finding | Verdict / route | Checked evidence and resolution |
| --- | --- | --- |
| B1 Unicode C1 controls accepted | medium / patch | Actual title rejection test failed for U+0080/U+009F; URL checks were independently present in the added cases. Full Cc range now rejected by semantic and representable schema rules. Positive Hebrew preserved. |
| B2 Browser-invalid numeric/scoped hosts | medium / patch | All four fixtures accepted before fix: 999.999.999.999, scoped IPv6, shorthand IPv4 and hex host. Validate canonical IPv4/unscoped IPv6; five positive host forms remain accepted. |
| B3 Nil UUID allowed by schema | medium / patch | JSON Schema accepted nil while DTO rejects it. Add property-level not-const plus exact length; independent Draft202012Validator case now rejects. |
| B4 Overflow revision allowed by schema | medium / patch | Both max+1 and19-digit999… passed JSON Schema before patch. Generate one bounded positive-decimal pattern for DTO/schema, with maximum/overflow/leading-zero parity fixtures. |
| B5 Noncanonical marks allowed by schema | medium / patch | Duplicate and reversed marks accepted by schema before patch. Schema enum and DTO validator derive from same four allowed mark tuples; all six parity cases pass. |
| B6 Outcome command/resource mismatch | medium / patch | Three mismatched command/note_id cases accepted by schema before patch. Add correlated oneOf schema branches; all six DTO/schema pairs now agree. |
| B7 Wrong code allowed on error status | medium / patch | 401 accepted note_revision_conflict before fix. Restrict each error response with a status-specific code enum intersecting the closed safe union;401/409 cross-status acceptance tests now reject. |
| B8 Title/URL schema too permissive | medium / patch | Independent schema validator accepted blank/control titles, relative/credential/control links. Encode representable rules, document property-specific remaining semantic constraints. Follow-up terminal-newline red2 fixed with negative character constraints/exact identifier length. |
| B9 Depth/node tests not isolated | medium / patch | Old array-root depth case failed before traversal, no node-budget test. Spy DTO records whether parser reached validation; exact16/8192 accepted,17/8193 rejected before DTO. Valid duplicate-key payload also tested. Coverage fix; framing implementation unchanged. |
| B10 Missing response coverage | medium / patch | Inspected missing page/revision-detail/chronology assertions. Add valid max50 pages, required-null cursor/size/characters/extra-detail rejection, reversed chronology and all successful/mismatched outcome forms. Coverage fix; response behavior unchanged apart from already-listed schema patches. |

All10 findings verified/addressed, no rejected findings, deferrals or frozen-intent changes. Runtime owner/SQL/UI/release obligations remain explicitly unimplemented scope, not deferred review bugs. Canonical tree is pre-existing untracked and excluded from the scoped local commit, as are all concurrent KDG/Leave/factory/AGENTS changes and staged index entries.
