---
title: 'KDG questionnaire definition validation prerequisite'
type: 'feature'
created: '2026-10-23'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

Deliver the small app-owned definition-validation prerequisite for Story1.2, not its
blocked bootstrap/persistence/read implementation. Current Story1.2 requires owner
write/operator/release evidence and a fingerprint-based setup contract; the user keeps
fingerprints/HMAC deferred. Do not bypass those gates or expand into another platform
framework. Reuse approved Pydantic2.14.1 and standard JSON parsing in the existing KDG API.

Given an ordered questionnaire document, when validated, then accept only schema_version1,
1–50 unique nonzero canonical UUID question IDs, the closed rating/boolean/text union,
nonblank labels of at most500 Unicode characters and strict required booleans. Preserve
labels/order exactly; reject U+0000 and invalid Unicode rather than normalizing it.
Rating configuration explicitly declares minimum1/maximum5 and endpoint labels Goed /
Nie goed nie; no rating default or intermediate descriptions. Boolean configuration
uses strict default false, details_enabled and a nonblank details_label only when enabled.
Text has only common question fields; answers/executable expressions are not definitions.
Use explicit typed fields/discriminated unions, no generic form engine.

Given malformed JSON, duplicate keys/IDs, unknown fields/schema/types, coerced scalars,
out-of-range configuration, invalid IDs/text or oversized input, when parsed at the
public domain boundary, then return only a fixed safe domain error identifier with no
input, diagnostic dump or chained exception rendering. Bound incoming UTF-8 JSON to
128KiB (the existing command ceiling); model constraints validate structure independently.
The future HTTP layer owns safe field-path presentation and transport-envelope bounds.

Given exactly four caller-supplied question UUIDs, when constructing the initial
candidate definition, then preserve those IDs and the exact four approved Afrikaans
labels, required flags, integer1–5 endpoint meanings and three default-Nee Ja/Nee
questions with optional Ja-only Besonderhede. Allocate no UUIDs, real target identities,
questionnaire/version IDs, actor authority or database rows. Produce an immutable model
with tuple-ordered questions and ordinary JSON serialization. It is inert definition
content, not a seed/provisioning command, published record or working form.

Observe a behavioral acceptance failure before implementing validation; use focused
TDD for structural and safety cases. App-specific definitions stay in KDG; no speculative
scaffold abstraction. Record scaffold/shared-UI/context/docs/ADR decisions. No DB/Docker,
migration, API route/OpenAPI/generated client change, editor/Leave, real accounts/access,
production, provisioning, deployment/pilot, cleanup or fingerprint/HMAC work. Preserve
concurrent work, historical evidence/resources and approved dependencies including TS7.0.2.

</frozen-after-approval>

## Implementation Notes

- bmad-help [BD] selects Story1.2's typed-definition contract prerequisite from epics.md AC1/4 and contracts.md Questionnaire documents, while its actual writes remain blocked by explicit dependency gates. Freeform prerequisite, no claim of Story1.2 completion or sprint advancement.
- One-shot: no human-only intent gaps or irreversible actions; small owner model/parser/factory plus focused tests/docs. Existing dirty tree authorized for preservation; snapshot /tmp/kdg-definition-before.json. No reset/stash or unrelated edits.
- Code map: new api/questionnaire.py and tests/test_questionnaire_definition.py; existing context.py Identifier/canonical_uuid and Closed conventions; existing Pydantic baseline. main.py, runtime.py, OpenAPI, database/migration/native evidence and managed scaffolds remain unchanged.
- Wire-field choices are owner implementation details: common id/type/label/required; flat minimum/maximum/minimum_label/maximum_label for rating, default/details_enabled/details_label for boolean. Scope is schema-version1 MVP only; no answer validator or future schema engine.
- Impacts: scaffold unchanged because question schemas/content are domain-specific; shared UI unchanged; agent context sufficient; owner contract/API guide/evidence/handoff updated; accepted ADRs unchanged. Ordinary Pydantic/JSON, no new dependency or delivery workflow.

- Behavioral acceptance RED /tmp/kdg-definition-acceptance-red.log: initial model accepts duplicate question IDs; expected DefinitionError not raised. Implemented standard closed Pydantic discriminated models plus standard JSON parsing; no runtime/DB/scaffold changes.
- Focused RED /tmp/kdg-definition-focused-red.log: byte-valued initial IDs were coerced into strings, and JSON Schema omitted false constant. BeforeValidator validates raw ID strings; literal false plus strict pre-validator aligns runtime/schema.56 focused cases pass. Earlier uppercase test fixture had only decimal digits; corrected fixture to uppercase hex, not a changed domain expectation.
- Same API tests/OpenAPI/TS contract checks run; restricted-sandbox broad test stalled and was interrupted130. Final bounded outside-sandbox test result recorded in receipt. No network service, provider, Docker or database operation.

## Review Triage Log

- Independent read-only review /root/review_kdg_definition inspected model/test/spec, ran56 isolated cases and found no confirmed issue. No deferred review defect; full Story1.2 readiness remains independently open by design.

- Final PASS:56 focused definition cases;135 complete KDG API/definition regression cases outside restricted process sandbox (1.41s, existing Starlette/httpx deprecation warning only); current HTTP OpenAPI export check; strict application TypeScript7.0.2 contract check; scoped whitespace check. No dependency change to silence the preexisting warning.
- Current entry/runtime/HTTP contracts, native migration tooling/proofs, manifests/locks and original failed fixture are unchanged. No broad builder/browser/native run was necessary for this app-only model; none claimed. Concurrent dirty/untracked work remains outside the staged item.
