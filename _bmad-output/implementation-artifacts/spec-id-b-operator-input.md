---
title: Strict Identity operator command inputs
type: feature
created: '2026-10-20'
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: 99d68050a54e22427ace9ef99e95c4504aced4cf
context:
  - /home/ck/repos/innodat/agriplatform/AGENTS.md
  - /home/ck/repos/innodat/agriplatform/platform/docs/architecture/contracts/identity-access-execution-substrate.md
  - /home/ck/repos/innodat/agriplatform/platform/docs/architecture/contracts/e1-controlled-provisioning-and-evidence.md
---

<frozen-after-approval reason="standing approval for bounded shared prerequisites">

## Intent

Identity needs a strict input boundary before its selected setup operations gain execution authority. Add a small owner-local parser for the four selected commands, returning immutable typed values and safe validation errors.

## Boundaries & Constraints

**Always:** Stdlib only, existing owner layout and canonical qualification interpreter. Observe acceptance RED before implementation, focused TDD thereafter. Preserve unrelated files and historical evidence. Parsing conveys no execution authority.

**Never:** Database/Docker operations, account/access changes, SQL/migrations, target binding, receipts/fingerprints, CLI, generic framework, dependencies, other applications, deployment or commits by the implementation agent.

The API is `parse_command(body: bytes)` in `services/access/identity_operator_input.py`. Return frozen typed command/payload/scope dataclasses. Error messages/repr must expose no submitted values; a fixed safe error code and code-defined field paths suffice. Avoid payload-bearing dataclass repr.

Common required fields: exact integer `schema_version:1`, nonnil UUID `operation_id`, command, scope, payload, reason_code. Only evidence_ref is optional. Scope is exactly `{kind:platform}` or `{kind:organization,org_id:UUID}`. Reject unknown fields at every level, including authority overrides. Reasons are the closed initial enum initial_setup/synthetic_fixture/identity_adoption/access_change/setup_correction.

Selected payloads:
- actor.register_system, platform: actor_id UUID, kind system|service, actor_key matching `[a-z][a-z0-9_.:-]{0,127}`, display_name, expected_absent exactly true.
- account_actor.ensure, platform: account_id UUID, actor_id UUID, display_name, expected_absent exactly true; envelope evidence_ref required.
- membership.join, organization: account_id UUID, required expected_previous_membership_id null or positive bigint decimal string, optional is_owner exact bool default false. True remains a request requiring later join_owner authority.
- membership.retire, organization: account_id UUID, membership_id and expected_revision positive bigint decimal strings.

Lexical refinements: UUIDs standard hyphenated upper/lower spelling only, preserved as accepted strings; no nil, braces, URN or compact aliases. Decimal strings canonical `[1-9][0-9]{0,18}` bounded by 9223372036854775807. Evidence, when present, is nonempty ASCII `[A-Za-z0-9][A-Za-z0-9_.:/-]{0,255}`, excluding `://`; null is invalid. Reasons bounded at128 ASCII chars. Displays preserve Unicode unchanged, 1–200 codepoints, nonblank under the actor database Unicode White_Space definition; reject NUL and lone surrogates anywhere. No normalization. Maximum65536 UTF-8 bytes, strict JSON, no BOM/duplicate keys/nonfinite numbers. Decoder failures, excessive nesting and oversized integers return the same safe validation error.

## I/O & Edge-Case Matrix

| Scenario | Input | Behavior |
|---|---|---|
| Selected commands | Four valid command variants and join owner true/default | Typed immutable values; no authority inferred |
| Closed structure | Missing/unknown/duplicate fields, wrong scope/command, root array | Safe rejection |
| Scalar types | bool schema, numeric IDs, nonbool flags, malformed/nil UUID | Safe rejection |
| Bounds | bigint max/overflow/leading zero; key128/129; display200/201, Unicode blank | Exact boundaries enforced |
| Evidence | ensure missing; null, URL/query, oversized; optional omitted elsewhere | Only selected opaque identifiers accepted |
| Decoder | Invalid UTF8, BOM, escaped duplicate names, NaN, NUL, surrogates, deep nesting, huge integer | Safe rejection, no leaked sentinel |
| Byte limit | Valid JSON padded to65536 /65537 bytes | Accept / reject |
| Preservation | Unicode display and uppercase UUID | Preserve accepted spelling; no normalization |

</frozen-after-approval>

## Code Map

- `services/access/identity-migrations/versions/0002_actor_registry.py` — existing display constraints; locate actual revision if this name differs.
- `services/access/IDENTITY-MIGRATIONS.md` — owning runbook, add bounded parser-only usage.
- `services/access/tests/` — existing owner test/import conventions.
- `platform/deployment/.local/operator-input-hea3nf0p/` — exclusively retain this delivery's RED/GREEN logs.

## Tasks & Acceptance

- [x] Add parser and meaningful tests covering every matrix row, observing RED before implementation.
- [x] Update owner runbook explaining parser-only scope and lexical choices.
- [x] Root records requirement-to-test evidence, impact decisions, handoff and preservation audit.
- [x] Root runs affected suites, independent review and scoped commit.

Acceptance: no new dependency, DB/runtime/resource change or authorization claim. Existing contracts and owner tests continue passing. Implementation agent owns only parser, its test file and owner runbook; root owns spec, evidence/navigation/inventory. If a named file differs, inspect the existing owner rather than creating another owner.

## Implementation Notes

Implemented four frozen command variants with owner-local frozen scopes/payloads and safe
reprs. No I/O, dependencies or authority checks. Acceptance RED was missing module;
focused66 and affected185 pass. An initial test repr assertion collided with the static
class name and was corrected to check submitted identifiers; both attempts retained.
All eight matrix rows have executed coverage mapped in OPERATOR_INPUT_EVIDENCE.md.
Both composition checks pass. Protected baseline audit reports no unexpected changes.
The Code Map path was corrected to the existing hyphenated owner migration directory.


Final review patches modify tests only. Focused127/root affected246 pass, no skips;
both composer checks and whitespace checks pass. Root final source/log-bound receipt
is retained in the proof directory. Preservation audit confirms all2577 preexisting
files except the four intended documentation changes unchanged. No deferred findings.

## Spec Change Log

## Review Triage Log

| Finding | Verdict | Evidence / route |
| --- | --- | --- |
| Blind1 duplicate fixtures masked | medium | Complete-envelope checks also reject current fixtures; remove _pairs and they still reject. Patch valid commands with duplicates. |
| Blind2 decoder fixtures masked | low | Nonfinite/huge-number fixtures have invalid envelopes, so assertions cannot distinguish decoder behavior. Patch direct decoder coverage, no public surface change. |
| Blind3 returned scope unchecked | medium | Success test checks scope type but not org_id; a swapped ID can pass. Patch equality assertions. |
| Blind4 evidence/org repr coverage | low | Existing repr assertions omit these submitted values. Patch distinguishable-value assertions across variants. |
| Blind5 ensure display boundaries | low | Text boundary test currently covers only registration construction path. Patch ensure coverage too. |
| Blind6 nonbytes boundary | low | Public parser checks bytes, but tests never call it with nonbytes. Patch direct invalid-type calls. |
| Blind7 organization UUID lexical cases | low | Payload UUID tests omit org_id aliases. Patch scoped UUID matrix and uppercase preservation. |
| Gap1 duplicate detection mutation survived | medium | Preverified in-memory removal of detection leaves66 passing; same cause as Blind1. Patch together. |
| Gap2 organization substitution survived | medium | Preverified in-memory replacement leaves66 passing; same cause as Blind3. Patch together. |

Edge hunter returned no findings. All findings route to direct test patches; no
implementation defect, intent gap or deferred work was found. All seven grouped test
patches were applied and root final246-test verification passed.


## Verification

Use `platform/deployment/.local/identity-baseline/qualification-im60qj1l/owner-env-djguxc78/offline-venv/bin/python` with `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`, `-I -B -m pytest`, `-p no:cacheprovider`. First run new acceptance test before module exists, retain RED log; then focused parser suite and full `services/access/tests apps/pts/tests/test_release.py -q`. Root checks composition and file preservation. Do not start Docker.
