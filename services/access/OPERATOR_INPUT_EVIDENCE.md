# ID-B operator input validation evidence

2026-10-20; baseline 99d68050a54e22427ace9ef99e95c4504aced4cf.
This increment implements only strict JSON input validation for the four selected
Identity setup commands. Parsed requests convey no execution authority. Account/provider
verification, executor/initiator binding, current authority and expected-state checks,
target binding, durable outcomes and protected writes remain subsequent delivery.

## Requirement-to-test evidence

The parser test suite covers the selected actor.register_system, account_actor.ensure,
membership.join and membership.retire shapes. The delivery spec records the full
acceptance matrix and review disposition; the table below maps it to executable tests.

All tests below are in `tests/test_identity_operator_input.py` and execute in the
full affected suite (no skips). Acceptance RED is retained in `acceptance-red.log`:
collection fails because the parser module does not yet exist. GREEN follows implementation.

| Requirement / matrix row | Test functions (prefix `test_`) |
| --- | --- |
| Four typed commands and requested owner flag | selected_commands_are_typed_frozen_and_redacted; owner_is_only_typed_requested_input |
| Closed fields and required structure | closed_fields_and_required_fields_at_every_level; envelope_scalar_and_scope_rejection; payload_types_uuid_and_exact_scope |
| Exact scalar/UUID/flag types | envelope_scalar_and_scope_rejection; payload_types_uuid_and_exact_scope; all_payload_uuids_reject_aliases_and_nil; organization_scope_rejects_uuid_aliases_malformed_and_nonstring; owner_requires_boolean |
| Bigint and actor/display limits | bigint_decimal_boundaries; actor_text_boundaries_and_unicode_preservation |
| Closed reason and evidence rules | closed_reasons; evidence_lexical_rejection; evidence_required_only_for_ensure_and_max_identifier |
| Strict decoder / duplicate / forbidden codepoints | decoder_failures_are_safe; forbidden_codepoints_anywhere; duplicate_fields_rejected_in_otherwise_complete_commands; decoder_itself_rejects_nonfinite_and_oversized_integers |
| 65536-byte exact limit | exact_utf8_body_byte_boundary; public_boundary_rejects_nonbytes_without_encoding |
| Accepted Unicode/UUID spelling | selected_commands_are_typed_frozen_and_redacted; actor_text_boundaries_and_unicode_preservation |
| Safe diagnostics | error_repr_and_command_repr_do_not_expose_submitted_values; invalid_decoding_does_not_chain_unsafe_decoder_exception |

The initial GREEN attempt exposed a test assertion colliding with the static class
name RegisterSystemPayload. Its repr check now asserts submitted UUID/actor-key secrecy;
no required parser outcome was relaxed. Both attempts remain retained.

## Commands and retained artifacts

Canonical OWNER_PYTHON:
`platform/deployment/.local/identity-baseline/qualification-im60qj1l/owner-env-djguxc78/offline-venv/bin/python`.
No dependency changes or installation: existing Python3.15.0, pytest9.1.1 and owner lock
are reused; the approved TypeScript7.0.2 baseline is untouched. Local RED/GREEN evidence
is retained in `platform/deployment/.local/operator-input-hea3nf0p/`.

- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 OWNER_PYTHON -I -B -m pytest services/access/tests apps/pts/tests/test_release.py -q -p no:cacheprovider`.
- `OWNER_PYTHON tools/py/run_compose_supabase.py --check-only`: PASS; legacy 15 migrations.
- `OWNER_PYTHON tools/py/run_compose_supabase.py --identity-authority owned --check-only`: PASS; owned 9 migrations.

No Docker command, database connection/mutation, credentials, target preparation,
migration or account/access change was needed or performed. Existing synthetic resource
state, receipts and source references remain retained; runtime was not requalified here.

## Impact decisions

- Scaffold: owner-local parser supports the selected future operator adapter. No generator,
  app scaffold input or reusable pattern promotion is warranted before that consumer.
- Shared UI: none; no user-facing surface.
- Agent context: existing repository instructions suffice, no new agent rules.
- Documentation: owner runbook, this traceability record, delivery spec and KDG/owner navigation.
- ADR: existing Identity ownership, release safety, sensitive logging and durable actor decisions
  govern this work. No accepted ADR changes or new architecture decision.

The parser's restricted lexical choices are documented in the owner runbook. Strict parsing
is a prerequisite, never proof of successful provisioning or a substitute for authorization.

## Executed verification result

Initial focused/full suites: **66/185 passed** (`focused-green.log`, `owner-green.log`).
After review test fixes, focused suite: **127 passed** (`review-focused-green.log`); root
final full affected suite: **246 passed**, no skips (`root-final-green.log`).
`root-final-receipt.json` binds the exact command, parser/test source hashes and log hash. Both composition checks pass; diff whitespace
check passes. Preservation audit covers 2577 preexisting nonignored files, with only the
four intended existing documentation files changed; no unexpected changes. Independent
review disposition and scoped commit are recorded in the delivery spec and Git history.

Independent BMAD blind/edge/verification reviews completed. No parser implementation
failure was found. Reviews identified masked duplicate-key/decoder fixtures and missing
scope/redaction/type/ensure-display assertions; focused test patches close those gaps.
No work is deferred. The delivery spec preserves each finding and its triage.
