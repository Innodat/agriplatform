# Capture command and pinned-answer validation — 2026-10-23

bmad-help [BD] selected the concrete missing capture input boundary before atomic
capture/history/outcome persistence. `api/capture_commands.py` implements strict
capture.create/edit v1 parsing and fresh-action answer validation using existing
QuestionnaireDefinition models. It performs no HTTP, database, Auth, clock or resource I/O.
This does not complete a create/edit API, schema, offline Save or Story1.6.

## Implemented owner contract

Use `parse_create(raw)` / `parse_edit(raw)` on the complete bounded UTF-8 command body.
They return closed CreateCommand/EditCommand models with redacted string/repr diagnostics.
Create fields are exactly operation_id, command_version, capture_id, child_id,
questionnaire_version_id, observation_date, answers, captured_at, child_eligibility_ref.
Edit fields are exactly operation_id, command_version, expected_revision,
observation_date and answers; capture ID belongs to the eventual protected route path.
Neither accepts browser owner, organization, actor or audit assertions.

Structure enforces canonical nonnil lowercase UUIDs, positive signed64-bit revision
strings, strict integer v1 versions, real YYYY-MM-DD dates, UTC device time, 50 answers,
5000 Unicode codepoints per text/details and 131072 bytes for the entire raw envelope.
UTC timestamps accept Z/z or +00:00, T/t and optional fractional seconds; calendar/time
values are validated and the original string is retained as untrusted device input.
Opaque eligibility references remain nonblank text under the whole-envelope limit;
this slice defines no UUID/issuance/retention/authority policy for that future record.
Duplicate JSON keys, nonfinite numbers, unknown fields, NUL and invalid Unicode fail
closed. False details must be absent; explicit null is rejected, and serialization
never invents an absent details field. Valid Unicode and whitespace are preserved.

`validate_answers(command, definition)` revalidates against the explicitly supplied
original QuestionnaireDefinition. It returns None on success without changing command
input. It refuses missing required/foreign questions, mismatched rating/boolean/text
types, disabled details and blank supplied text. Optional unanswered questions are
omitted, including optional text. Required false and rating1 remain valid. No latest
version substitution or answer migration is performed. The caller must bind the supplied
definition to the referenced create version or the stored edit version.

Keep these phases separate. Structural parsing precedes outcome discovery; fresh-action
answer/version/eligibility checks follow confirmed outcome absence. Currently authorized
committed replay uses the original stored resource/receipt even when the retry body has
different structurally valid answers. This module implements no replay/authority helper.
CommandError exposes only validation_failed or unsupported_command_version. Raw Pydantic
error dictionaries, exception locals and request data must not enter public responses
or diagnostic logs. Future HTTP consumers must bound body receipt and adapt safe errors.

## ATDD, focused TDD and regression evidence

P is retained `platform/deployment/.local/kdg-context-20261022/owner-env/bin/python`.
N is retained `platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node`.
All commands run from repository root with existing approved environments; no install.

- Acceptance RED: incomplete initial answers were accepted (expected CommandError was
  not raised). `/tmp/kdg-command-atdd-red.log`:1 failed,1 passed.
- Focused RED: the same case plus forged owner, boolean version, noncanonical ID,
  impossible date, fractional rating, false hidden details and duplicate key cases.
  `/tmp/kdg-command-focused-red.log`:8 failed,1 passed.
- Serialization RED: default dumps added details:null to omitted boolean answers;
  `/tmp/kdg-command-focused-matrix.log`:2 failed,107 passed. Field exclusion fixes it.
- `env PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 P -I -B -m pytest -q -p no:cacheprovider apps/kdg-capture/tests/test_capture_commands.py apps/kdg-capture/tests/test_questionnaire_definition.py`:
  Initial run:165 PASS (109 capture-command cases plus56 definition cases).
- `timeout 60s env PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 P -I -B -m pytest -q -p no:cacheprovider apps/kdg-capture/tests`:
  Initial run:244 PASS; final review-expanded run:263 PASS, one existing Starlette/httpx
  deprecation warning; retained baseline unchanged.
  Synthetic HTTP regression runs outside the restricted process sandbox.
- `N node_modules/typescript/bin/tsc -p apps/kdg-capture/tests/tsconfig.json`:PASS with7.0.2.
- Offline existing `export_openapi.main()` with --check and owner api directory on
  sys.path:openapi_current. No route/OpenAPI/client contract change.

The matrix covers both exact command shapes, all answer types, old versus newer explicit
definitions, structural/fresh semantic separation, date/time/UUID/revision/version
boundaries, optional omission, codepoint and envelope byte limits, malformed/duplicate/
nonfinite JSON, sensitive input diagnostics and exact content preservation. Source/log
bindings and precise argv are retained in [the receipt](evidence/capture-command-validation-20261023.json).

## Delivery impacts and remaining work

Scaffold: none; these are KDG-specific command/questionnaire semantics, not a reusable
form engine. Existing shared error/transaction scaffolding remains unchanged. Shared UI:
none. Agent context: existing guidance sufficient. Documentation: owner contract/API guide,
current handoff and this source-bound evidence; older handoffs/evidence preserved. ADR:
no new decision; retains ADR-0061 semantics and Story1.2's separate bootstrap contract.

Next deliver the supporting version/child/eligibility records and linked capture/revision/
outcome schema plus concrete current-authorized owner writes. Qualify native constraints,
RLS/immutability, atomicity/concurrency and ADR-0020 release/recovery before activation.
No partial outcome-only schema or synthetic durability claim. No database/Docker lifecycle,
real accounts/access, Leave/editor, production, provisioning/deployment/pilot/cleanup,
dependency/TypeScript baseline or fingerprint/HMAC changes occur in this delivery.

## Final review and preservation

The independent blind review returned7 findings; each is triaged in the
[delivery spec](../../../_bmad-output/implementation-artifacts/spec-kdg-capture-command-validation.md).
Documentation clarifies shallow field freezing and immediate fresh-write revalidation,
and fixes the guide's interpreter variable. Added behavioral coverage proves invalid
constructed/mutated inputs fail, all optional/required omission combinations work,
true/null details fail, blank true details stay exact, whole-envelope invalid unknown
values/keys fail before version dispatch and parser tracebacks hide private input.
No review finding is deferred; no new generic guard or queue framework was introduced.

Final `timeout 60s env PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 P -I -B -m pytest -q -p no:cacheprovider apps/kdg-capture/tests`:
263 PASS in1.43s, including128 capture-command cases and the existing56 definition
cases. `/tmp/kdg-command-api-final.log` retains the exact result and existing warning.
These are pure/synthetic behavior and HTTP checks, not native persistence qualification.

All148 preexisting dirty/untracked paths remain present. Concurrent work outside this
scope is preserved and excluded from the local commit.220 existing KDG/template/dependency
files remain byte-identical, including the prior outcome adapter, questionnaire models,
managed inventories and historical evidence. The previous next-session content is an
exact suffix, and the installed application TypeScript remains7.0.2.
