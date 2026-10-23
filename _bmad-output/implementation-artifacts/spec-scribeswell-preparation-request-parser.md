---
title: 'Parse the closed Scribeswell preparation request'
type: 'feature'
created: '2026-10-23'
status: 'done'
route: 'oneshot'
baseline_commit: '157c606be3f040f65c09c0e9a2a9f1bbab750396'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The agreed preparation request contract has no executable parser. Later preparation code needs bounded immutable declarations without confusing valid input with authenticated owner evidence.

**Approach:** Implement only `parse_preparation_request(raw)` and frozen named request/custody values in the app-owned backend module. Accept exactly bytes containing the closed nine-field version1 JSON request and unchanged six-field custody, under8192bytes/depth4. Reject invalid UTF-8/BOM, duplicate/missing/extra fields, wrong types, nonfinite numbers, invalid canonical UUIDs or bounded ASCII references with the one fixed safe error and no chained context. Preserve values in immutable nested records with no payload repr. Parsing performs no owner/file/environment/network/database effects or authorization. No runner/target/admission implementation, packaging/deployment, migrations, roles/grants, enforcement, Access/KDG/Leave/factory or UX/signup change.

</frozen-after-approval>

## Implementation Notes

- BMAD step02: no intent gaps or irreversible work; small four-file slice: `backend/caller_preparation_input.py`, `tests/test_caller_preparation_input.py`, `docs/CORPUS_PREPARATION_TOOL.md` evidence/status and this spec. Canonical derivation via bmad-spec records actual evidence; existing dirty tree preservation authorized.
- Code map: exact app-local pure `apps.scribeswell.migrations.release_profile.validate_custody` via namespace import, unchanged. Configure repository import root in caller/tests, never mutate paths/load files dynamically inside parser. Publication-input module supplies patterns for frozen/slotted/repr-suppressed values, exact types and error raised outside handler, not an import dependency. Runtime Docker omits custody module; parser is internal/repository-qualified pending consuming runner packaging, no image availability claim.
- Same preparer/corpus actor UUID is permitted: responsibilities are separate, handoff says preparer need not equal service actor; no inequality rule or proof inferred. Error `.code` and message exactly `scribeswell_preparation_request_invalid`; suppress underlying context entirely by raising outside handler.
- Given valid bytes, parsing returns exact named immutable fields. Given malformed/boundary input, it safely rejects before effects. Given untrusted syntactically valid evidence references or same actor UUIDs, it preserves declarations without verifying authority. Given clean interpreter with repository root only, import/parse require only stdlib+own pure custody and no runtime-owner dependencies/path mutation. Cover size/encoding/UUID/reference/object/numeric/duplicate/depth/error/immutability boundaries first.
- Verification order: new acceptance failure, focused parser cases, affected pure input/release-contract tests, then only further checks justified by failures or changes. No database fixtures needed for pure behavior. Record exact commands/results.
- Impacts: application-specific parser and documentation; no scaffold/shared-UI/agent-context or accepted ADR change/promotion. Reuse existing pure custody semantics; do not refactor guarded migrations or owner code.
- Observed outer acceptance red: `/tmp/scribeswell-host-tests-312/bin/python -m pytest apps/scribeswell/tests/test_caller_preparation_input.py -q` ->1failed2.05s, missing parser module, before implementation. Wrote focused boundary tests before implementation, then same command ->196passed2.37s. Namespace import tested in fresh isolated -I -S subprocess with explicit root/empty environment/unrelated cwd, rejecting runtime imports/env access/I/O during calls.
- First affected regression command `/tmp/scribeswell-host-tests-312/bin/python -m pytest apps/scribeswell/tests/test_caller_preparation_input.py apps/scribeswell/tests/test_corpus_publication_input.py apps/scribeswell/tests/test_host_validation_profiles.py -q -k 'not actual_host'` ->383passed/11skipped6.03s. Eleven retained native fixture cases skipped because no disposable DB was supplied; these are not new acceptance proof and no native replay qualification is claimed. New pure cases all executed.

## Review Triage Log

- R1 medium/patch: reproduced2failed2.13s when parsing inside caller JSONDecodeError/RuntimeError handling; raising outside the internal handler still attached the caller's active exception. Raise/catch the safe error with suppressed cause, clear its real __context__, bare-reraise. Focused2passed1.79s; no hidden property/fake context. Safe code/message and underlying decoder/caller context separation preserved.
- R2 medium/patch: all deep-wire fixtures used0, rejected by integer hook before depth guard. Use admitted1 and add independently counted decoded-container depth4pass/depth5fail focused guard coverage. Closed shape remains mandatory even within depth ceiling.
- R3 medium/patch: dict-subclass environment guard left inherited reads open. Replace with a rejecting non-dict object covering iteration, item/get/contains/length and items/keys/values/copy; isolated interpreter passes.
- R4 medium/patch: import guard denied only two owner prefixes. Restrict to stdlib module roots plus exact app namespace/parser/custody modules; no other owner/application implementation allowed. Isolated import succeeds with explicit trusted root and unchanged sys.path.
- R5 medium/patch: command wrong-type tests missed wrong string values. Add empty/other action/case/spacing/newline literal negatives, preventing removal of exact literal comparison from escaping coverage.
- R6 low/patch: UUID positives used only numeric hex digits. Add lowercase a-f identity success and uppercase spelling of the same identity rejection for both request UUID fields.
- All six findings verified and patched, none deferred. Final focused command after corrections207passed2.23s; affected pure regression pending. Initial context-free review diff26000bytes SHA2561156f9a02f7c3267e2702ed19f5ece692b19c912e3a04bff7840345c9ab4b941. Review first attempt hit model capacity; same reviewer retried successfully, no model substitution.
- Final affected pure command `/tmp/scribeswell-host-tests-312/bin/python -m pytest apps/scribeswell/tests/test_caller_preparation_input.py apps/scribeswell/tests/test_corpus_publication_input.py apps/scribeswell/tests/test_host_validation_profiles.py -q -k 'not real_supervised_replay and not history_supervisor_timeout and not history_never_selects_profile and not actual_commit_ack_loss and not real_host_coordinator'` ->394passed/11deselected5.98s (207new/187retained). This deliberately excludes retained native fixture cases; no DB/native/whole-app/image verification claim. New parser cases have no skips. Exact initial broader filter and11skips remain recorded above.

- Final source/document/canonical checks: frozen tested code hashes match; existing application/Identity/applied migrations/pure custody and original AGENTS/README unchanged except intended tool-doc update; nine request/six custody named fields; canonical11CAP/38ST/21companions; scoped/canonical links/anchors/whitespace/AST all pass. Scoped local commit excludes pre-existing untracked canonical tree and all concurrent owner work. No push/deploy/DB/native/image/provider operation performed.
