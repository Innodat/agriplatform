---
title: Strict Access application enablement command input
type: feature
created: '2026-10-21'
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: 0da77323b948903b4a479c6486c6b919bf9d0fc2
context:
  - /home/ck/repos/innodat/agriplatform/AGENTS.md
  - /home/ck/repos/innodat/agriplatform/platform/docs/architecture/contracts/identity-access-execution-substrate.md
---

<frozen-after-approval reason="standing approval for bounded shared prerequisites">

## Intent

Prepare the next ACCESS-A command, application.set_enabled, with a strict typed input contract in the existing parser. Execution remains closed until mutable registry persistence, revision and evidence guards are delivered. Parsing conveys no authority or access.

## Boundaries & Constraints

Extend services/access/access_operator_input.py:parse_command with frozen repr-redacted SetApplicationEnabledCommand and SetApplicationEnabledPayload. Reuse existing version1 envelope/PlatformScope/decoder and Identity's positive bigint decimal validator without modifying Identity source or creating another parser/framework.

Reuse the closed version1 envelope and scope exactly {kind:platform}. Payload exactly app_id, enabled, expected_revision. App grammar remains ASCII [a-z][a-z0-9_]{1,63}; enabled is an actual bool (true or false); expected_revision is a positive canonical decimal string at most9223372036854775807. Reject numeric/bool revisions, zero, signs, whitespace, leading zeroes, Unicode digits, excessive length and overflow; preserve accepted strings. expected_absent, actors, permission and all other fields reject.

Retain closed reasons/evidence semantics (omitted evidence becomes None; null invalid), UUID spelling and strict decoder: UTF8 bytes max65536, no BOM/duplicates/nonfinite numbers/NUL/surrogates, excessive nesting/integers or nonbytes. Fixed access_operator_input_invalid errors expose no submitted values/context/cause. Preserve all three registration command shapes/semantics and immutable records.

No execution is added: Access adapter execute and CLI execute refuse valid set_enabled as command_unsupported before connection/target/dispatch; outcome keeps existing command_invalid refusal; worker keeps its existing closed preconnection rejection. Identity parser/adapter/CLI/worker reject Access bodies before effects. No runtime/schema/dependency/generated changes, Docker/credentials/accounts/configuration, grants/consumers/Leave/editor, deploy/push/reset/prune or historical source/receipt edits. Prior runtime proofs stay source-bound.

## I/O & Edge-Case Matrix

| Scenario | Expected |
| --- | --- |
| Enabled true/false; revision1/max; app length2/64 | Exact distinct typed frozen redacted records, platform scope and accepted spelling preserved |
| Wrong enabled type, revision shape/overflow, invalid app grammar | Fixed safe rejection, no coercion |
| Missing/extra/duplicate root/scope/payload fields, wrong owner/command/scope | Closed rejection, no actor/authority override |
| Reasons/evidence, decoding/forbidden text, body65536/65537 | Existing strict semantics preserved for the new command |
| Three registration commands and Identity consumers | Existing behavior stays green; valid new Access body rejected by Identity |
| Valid set_enabled at Access adapter/CLI/worker; outcome lookup | Preconnection refusal with existing error families, no target/SQL/dispatch or receipt |

</frozen-after-approval>

## Code Map

- services/access/access_operator_input.py: add one command/payload/union branch and reuse imported _decimal. Keep registration paths closed and unchanged.
- services/access/access_operator.py:execute/outcome and operator_cli.py:_access_main/access_worker already close execution before I/O. Preserve allowlists/error families; no runtime edit required.
- services/access/tests/test_access_operator_input.py: existing typed/closure/decoder/boundary/Identity separation patterns; keep registration absence assertions separate. New tests: tests/test_application_enable_input.py.
- services/access/ACCESS_OPERATOR_INPUT_EVIDENCE.md is historical. Add APPLICATION_ENABLE_INPUT_EVIDENCE.md; update current substrate/KDG handoffs only.

## Tasks & Acceptance

- [x] Add focused acceptance tests and observe rejection of a valid enablement body before parser changes; retain RED and existing parser characterization output. Implement minimal parser branch with focused TDD.
- [x] Cover all matrix rows with executed tests, including strict decimal/bool boundaries, duplicates at each level, safe exceptions, traps for owner/adapter/CLI/worker/outcome and unchanged registrations.
- [x] Record requirement-to-test evidence, exact commands/results/source hashes and scaffold/UI/context/docs/ADR impacts. Update mutable substrate/KDG handoffs without claiming runtime enablement.

Given a valid enablement envelope, when parsed, then immutable typed values return without I/O. Given invalid input or an execution attempt, when checked, then existing safe refusal occurs before effects. Existing registration/Identity behavior remains compatible.

## Implementation Notes

Standing approval covers bounded implementation/dirty-tree preservation. Agent implements/tests/documents sequentially; no nested workflow/subagents/commit/native resources. Root owns review/checks/commit after source-frozen handoff. Preservation: /tmp/enable-input-preservation.json. Logs: platform/deployment/.local/access-enable-input-20261021/.

## Spec Change Log

## Review Triage Log

| Finding | Verdict / route | Evidence |
| --- | --- | --- |
| Blind1 execute error safety | low / patch | Execute asserts code only; add existing safe-error assertion (variable input avoids traceback source fixtures). |
| Blind2 disable refusal | low / patch | Valid False parses but execution traps cover True only. Parameterize both values across Access refusal boundaries. |
| Blind3 app digits/underscore | low / patch | New valid app cases are letters only; add a0_b to prove the independently applied app validator. |
| Blind4 direct decoder proof | low / patch partially | Unchanged Identity test_decoder_itself_rejects_nonfinite_and_oversized_integers directly checks the exact reused decoder and ran in297. No duplicate numeric tests needed. Direct excessive-nesting refusal remains absent; add one bounded decoder test with safe error assertions. |
| Blind5 helper extraction | low / reject | Shared test factories are restored by monkeypatch and saved original factory prevents recursion; existing suites pass together. No current behavior diverges. Broad helper/factory refactoring adds complexity for a speculative future fixture change and is unnecessary for this slice. |
| Blind6 matrix granularity | low / reject | Existing repository tests use the same loops and traceback locates the failing shared assertion. No everyday missing behavior demonstrated; splitting/parameter plumbing adds complexity without closing a contract gap. |

All layers completed before triage. Edge and verification-gap lenses returned no findings. Four small test-only corrections; no intent/runtime change or new deferral.

## Verification

Canonical Python: platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python. Disable ambient pytest plugins/cache; use -I -B -m pytest and -p no:cacheprovider. RED then focused input/Identity/adapter/CLI tests. Root affected regression: services/access/tests apps/pts/tests/test_release.py platform/deployment/tests/test_migrate_adapter.py -q. Both composition dry runs: --check-only; --identity-authority owned --no-seeds --check-only. Scoped whitespace, historical/Identity/concurrent preservation and frozen intent checks; no native startup or new runtime-readiness claim.

Implementation handoff: parser-only branch and focused tests delivered; characterization204, focused297 and registration-adapters84 pass. See `services/access/APPLICATION_ENABLE_INPUT_EVIDENCE.md`. Root review, affected regression, both composers and preservation checks remain pending. No execution or runtime-readiness claim.

Final root verification:1259 affected tests PASS35.57s; both composition checks PASS; full scoped diff/matrix audited, all current review patches verified with no new deferral. All45 historical/Identity source hashes and frozen intent unchanged. Concurrent Leave/Scribeswell planning changes preserved/excluded. No native resources/runtime activation. Evidence: services/access/APPLICATION_ENABLE_INPUT_EVIDENCE.md.
