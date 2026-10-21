---
title: Strict Access organization application configuration input
type: feature
created: '2026-10-21'
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: 71d2b85172137563f5e426b059f12b403878520a
context:
  - /home/ck/repos/innodat/agriplatform/AGENTS.md
  - /home/ck/repos/innodat/agriplatform/platform/docs/architecture/contracts/identity-access-execution-substrate.md
---

<frozen-after-approval reason="standing bounded prerequisite implementation approval">

## Intent

Prepare organization_application.configure in the existing Access parser. This input-only prerequisite introduces explicit organization scope and exclusive create/update expected state; persistence, external organization verification and execution remain undelivered.

## Boundaries & Constraints

Public parse_command(body:bytes) returns a frozen repr-redacted ConfigureOrganizationApplicationCommand, existing OrganizationScope, and distinct frozen create/update payload variants. Reuse Identity pure helpers without changing Identity bytes or adding a parser framework. Internal variant names are implementation choices; parsed payloads contain only fields supplied by the selected wire variant, not unused nullable fields.

Scope exactly {kind:organization,org_id:nonnil standard hyphenated UUID}; preserve accepted uppercase UUID spelling. No platform/account fallback, inferred organization or payload org_id. Payload exactly app_id, enabled and one of expected_absent=true OR expected_revision. Both/neither reject based on key presence even if null. app_id uses existing ASCII [a-z][a-z0-9_]{1,63}; enabled is actual bool. Expected absence is literally True; revision is canonical positive ASCII decimal string through9223372036854775807, preserving strings above JavaScript safe integers. Reject numeric/bool/null/zero/sign/space/leading-zero/Unicode/overflow revisions and false/nonbool absence.

Preserve the closed version1 envelope, UUID spelling, five reasons, optional opaque evidence (omitted None, explicit null invalid), UTF8 bytes max65536 and strict decoder. Reject BOM/duplicates including escaped aliases/nonfinite numbers/NUL/surrogates/deep nesting/oversized integers/nonbytes safely. Fixed access_operator_input_invalid errors expose no submitted text, context or cause. Preserve all four current platform commands; they reject organization scope.

No execution: Access adapter/CLI execute reject valid new bodies as command_unsupported before connection/target/dispatch; outcome remains command_invalid; worker retains closed preconnection refusal. Identity parser/adapter/CLI/worker reject Access input. Do not extend execution/receipt/outcome/lock/fingerprint helpers (existing Access lock helper is platform-only). Parsing verifies neither existence nor authority. No DB/Docker/roles/credentials, schema/dependencies/generated changes, real access/configuration, grants/consumers/Leave/editor, deploy/push/reset/prune or historical evidence edits. Prior runtime proofs stay source-bound.

## I/O & Edge-Case Matrix

| Scenario | Expected |
| --- | --- |
| Both variants, true/false, UUID spelling, app2/64 plus a0_b, revision1/above-JS-safe/max | Distinct typed frozen redacted records, exact values and supplied fields |
| Both/neither expected keys, null/false/nonbool absence, bad revision/bool/app | Fixed safe rejection without coercion |
| Missing/extra/wrong scope, invalid org UUID, org fields on platform commands | Closed refusal; no scope fallback or inference |
| Missing/extra/ordinary/escaped duplicate fields at every level | Closed safe refusal |
| Envelope/provenance/decoder/forbidden text and exact65536/65537 bytes | Existing strict semantics for both variants |
| New body at Identity/Access execution, lookup and worker boundaries | Existing error families before all I/O; existing platform commands remain green |

</frozen-after-approval>

## Code Map

Under services/access:
- access_operator_input.py: import OrganizationScope, branch on new command before platform scope validation; reuse _uuid/_decimal/_object and current app grammar. Add payload variants and command union member only.
- identity_operator_input.py: reusable pure helpers/scope; unchanged.
- access_operator.py and operator_cli.py: current typed execution/outcome allowlists already close new type; unchanged. Test direct methods/CLI/workers with traps.
- tests/test_organization_application_input.py: new focused matrix; reuse existing input assertions and current test conventions. Preserve existing registration and enablement tests rather than widening expected-absence loops indiscriminately.
- ORGANIZATION_APPLICATION_INPUT_EVIDENCE.md plus mutable substrate and KDG handoff: trace tests/results and five impacts. Existing source/evidence remains historical.

## Tasks & Acceptance

- [x] Characterize current parser, observe valid-input RED, add branch/types with focused TDD.
- [x] Execute every matrix row, pre-I/O/refusal safety and current platform/Identity compatibility tests.
- [x] Record exact commands/results/source hashes and scaffold/UI/context/docs/ADR decisions; update current mutable handoffs without runtime claims.

Given a valid organization command, parsing returns exact immutable values without I/O. Invalid input or unsupported execution refuses safely before effects. Existing platform behavior remains unchanged.

## Implementation Notes

Standing approval covers dirty-tree preservation. Root RED is retained under platform/deployment/.local/access-organization-input-20261021/. Preservation snapshot: /tmp/org-input-preservation.json. Agent implements/tests/documents sequentially, no nested workflow/agents/commit/native resources. Root reviews/final-verifies/commits after source-frozen handoff; no later writes. Existing bootstrap portability remains deferred; no native qualification/readiness is claimed.

## Spec Change Log

## Review Triage Log

| Finding | Verdict, evidence and route |
| --- | --- |
| Blind1: extract shared test support | low; coupling is visible but no present signature/setup defect; existing monkeypatch restores globals and saved builder prevents recursion. Reject speculative support-module refactor and added indirection. |
| Blind2: repeated create revision cases | low; create ignores the revision parameter, producing duplicate inputs. Patch: parameterize only distinct variant/revision pairs. |
| Blind3: negative loops lack case context | low; a failure requires inspecting loop locals; no behavior is hidden, and pytest exposes those locals on demand. Reject added fixture/parameter complexity for occasional debugging. |
| Blind4: public Access worker route absent | low; worker delegates five-element transport directly to access_worker, but new fixtures call only the latter. Patch: exercise both call boundaries under existing traps. |
| Blind5: parser no-I/O proof | false; _parse and reused _decode/_object/_uuid/_decimal perform only pure validation/construction, with no filesystem, connection or external verification call path. Trapping unrelated libraries would not prove absence of arbitrary I/O. |
| Blind6: handoffs await final root checks | low; implementation handoff correctly labels pending root work. Patch: root records final results before completion. |
| Blind7: complete wire examples absent | low; prose specifies all fields, but complete create/update examples directly improve consumer documentation. Patch: add two synthetic envelopes to the mutable contract. |
| Edge layer | No findings. |
| Verification-gap layer | No verification gaps found. |
| Root regression: reloaded Identity class comparison | medium; broad suite produced36 failures/1288 passes because characterization reloads Identity while Access retains its imported class. Patch: assert exact operator.OrganizationScope, preserving the exact class guarantee; do not change production or weaken to name comparison. |

## Verification

Python: platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python. Pytest disables plugins/cache with PYTEST_DISABLE_PLUGIN_AUTOLOAD=1, -I -B -m pytest -p no:cacheprovider. RED then focused parser/Identity/adapter/CLI tests; root services/access/tests plus PtS release/migrate-adapter tests. Both composition dry runs (default; --identity-authority owned --no-seeds). Whitespace, protected46 and frozen-intent checks; preserve concurrent files and prior proof. No native startup.


Final root verification:1312 passed in39.14s (`root-regression-reviewed.log`), both
composition dry runs exit0, both complete contract examples parse,46 protected file
hashes and frozen intent match. Reviewed parser/test bytes are unchanged. First broad
run's36 failures were isolated to intentional Identity reload versus the test's class
reference; exact imported-class assertion corrected. Review patches2/4/6/7 and root
assertion correction completed. No new deferred item; existing bootstrap portability
remains deferred. All pre-existing files retained; concurrent Leave edits preserved and
excluded. Seven-file scoped whitespace/source/log custody audit is recorded privately
in `platform/deployment/.local/access-organization-input-20261021/root-verification.json`.
No DB/native resources, dependencies, migrations, execution or activation changes.
