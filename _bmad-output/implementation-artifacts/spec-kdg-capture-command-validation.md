---
title: 'Validate capture commands against their pinned questionnaire'
type: 'feature'
created: '2026-10-23'
status: 'done'
route: 'oneshot'
baseline_commit: 'ddaea64ba4393c3b97e1959ee54649fe9d89d717'
context:
  - '{project-root}/apps/kdg-capture/AGENTS.md'
---

<frozen-after-approval reason="next authorized bounded KDG persistence/API slice">

## Intent

Implement app-owned strict capture.create/edit v1 command parsing and pinned-definition
answer validation in api/capture_commands.py. This is the missing input boundary for
future atomic capture/history/outcome writes, not their activation. Follow contracts.md
Wire values and validation/Capture commands and existing questionnaire.py definitions.
Given a complete initial response with rating1/false, parsing and fresh-action validation
succeed without changing entered content. Given missing/foreign/wrong-type answers or
hidden false/disabled details, fresh-action validation fails safely. Required text must
contain non-whitespace; optional unanswered text is omitted (reject supplied blank text).

Keep two phases: parse_create(raw)/parse_edit(raw) strictly validate complete bounded
UTF-8 JSON structural shape before outcome lookup. validate_answers(command,definition)
checks completeness/types against the explicitly supplied original published definition
only for fresh actions after confirmed outcome absence. No latest-version lookup,
comparison of retry bodies, callback orchestration, replay or authorization implementation.
Structural parsing can accept missing/foreign questions; their semantic validity belongs
to the second phase. Preserve original command strings, date, device time and answers.

Create exact fields: operation_id, command_version, capture_id, child_id,
questionnaire_version_id, observation_date, answers, captured_at, child_eligibility_ref.
Edit exact fields: operation_id, command_version, expected_revision, observation_date,
answers; capture ID remains a future path parameter. Closed canonical nonnil IDs, strict
v1 positive integer version, decimal positive signed64-bit revision, real YYYY-MM-DD
date, RFC3339 UTC device time, 50-answer/5000-codepoint text bounds and total131072-byte
UTF-8 envelope. Reject coercion, duplicate keys, NUL, invalid Unicode/nonfinite JSON,
unknown fields and browser owner/org/actor/audit assertions. Eligibility reference stays
opaque nonblank text, not UUID or authority proof; no new representation/retention policy.
Valid unknown integer command versions produce unsupported_command_version; malformed
input returns validation_failed. No input, values or chained diagnostics in safe errors.

Use existing approved Pydantic/standard library and local questionnaire/context models.
No dependencies, startup/router/OpenAPI/client changes, migration or DB connection.
ATDD must first show invalid pinned answers accepted; focused TDD must observe parser
strictness failures before fixes. Test initial and explicitly supplied older definitions,
all three question types, scalar/UUID/revision/date/time bounds, exact whitespace,
false/disabled details, optional omission, full-body limits and safe diagnostics.

Synthetic local/CI only. Preserve concurrent work/history/Docker resources and approved
TypeScript7.0.2 baseline. Fingerprints/HMAC deferred, Story1.2 bootstrap contract unchanged.
No Leave/editor, real accounts/access, production, provisioning/deployment/pilot/cleanup.
Capture/parent tables, atomic writes/current authority, native RLS/concurrency and release
migration/recovery remain consuming work; no partial outcome migration or persistence claim.

</frozen-after-approval>

## Implementation Notes

bmad-help [BD] selects bmad-build: prior outcome adapter is complete; actual capture
input validation is absent, and parent version/child/eligibility tables do not yet exist.
The immediate deliverable is one small reversible domain boundary, no irreversible
operation or unresolved user-visible choice. oneshot route. Tests live in
apps/kdg-capture/tests/test_capture_commands.py. Reuse questionnaire.py/context.py
unchanged. Original definition validation remains a separate, fresh-action-only call.

Scaffold: none; capture/questionnaire semantics are KDG-owned, with no new proven neutral
pattern. Shared UI: none. Agent context: existing policy sufficient. Docs: owner contract,
API guide, current handoff and source-bound evidence; preserve all historical tails.
ADRs: no new decision. Synthetic qualification does not complete Story1.6 or persistence.
Dirty-tree preservation authorized; /tmp/kdg-capture-command-before.json records baseline.


ATDD observed incomplete initial answers accepted before implementation (1 failure).
Focused parsing RED observed8 failures including acceptance before correction; later
serialization RED observed2 failures from invented details:null. No expectations relaxed.
Initial109 command cases plus56 existing definition cases passed; initial API regression
244 PASS with one existing Starlette/httpx warning. OpenAPI unchanged and TS7.0.2 PASS.

## Review Triage Log

1. **medium — patch documentation:** frozen model fields leave answers dict mutable.
   Explicitly documented private ownership and immediate fresh-write revalidation rather
   than inventing a new immutable mapping/queue envelope. Constructed nested-answer and
   post-parse foreign-question regressions prove existing revalidation rejects changes.
2. **low — patch:** API guide's literal P was not an executable variable expansion.
   Corrected the new command to "$P", consistent with the existing retained-env guide.
3. **low — patch tests:** missing modified/constructed instance coverage. Added invalid
   nested rating, invalid BooleanQuestion details configuration and foreign inserted
   question cases; all safely fail through the existing instance revalidation.
4. **low — patch tests:** optional omission only covered text. Added independent required/
   optional omission matrix for rating/boolean/text, covering all6 combinations.
5. **low — patch tests:** true/null and empty details not explicit. Added null rejection
   plus exact empty/whitespace preservation when details enabled; no behavior change.
6. **low — patch tests:** whole-envelope unknown value/key validation lacked regression.
   Added NUL/surrogates in unknown values/keys and nested overflow; version2 fixtures
   prove invalid values fail before unsupported-version dispatch, not only extra-field
   validation. Existing implementation passes without another validation layer.
7. **low — patch tests:** parser error privacy covered fewer paths than semantic errors.
   Added traceback checks for oversized answer, hidden false details and invalid Unicode;
   all suppress raw private input through existing safe boundary.

No finding deferred. Tests now cover128 command cases; final regression follows in
owner evidence. Public schemas, migrations and all shared artifacts remain unchanged.


Final API regression263 PASS in1.43s, including128 input cases; one existing approved-
baseline warning.220 existing KDG/template/dependency files unchanged;148 preexisting
paths present; historical handoff exact suffix. Source-bound evidence and staged scope
checks precede the local commit. No native or Docker operation occurred.
