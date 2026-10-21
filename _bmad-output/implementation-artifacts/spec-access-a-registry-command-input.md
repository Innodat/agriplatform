---
title: Strict Access registry command inputs
type: feature
created: '2026-10-21'
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: f42d3f73a9b51cde0125898daaafc5bec7fc77c7
context:
  - /home/ck/repos/innodat/agriplatform/AGENTS.md
  - /home/ck/repos/innodat/agriplatform/platform/docs/architecture/contracts/identity-access-execution-substrate.md
  - /home/ck/repos/innodat/agriplatform/platform/docs/architecture/contracts/e1-controlled-provisioning-and-evidence.md
---

<frozen-after-approval reason="standing approval for bounded shared prerequisites">

## Intent

Access has private registry storage but lacks typed registration inputs. Prepare its three approved registry commands using the existing strict version1 envelope mechanics, without enabling execution or effective access.

## Boundaries & Constraints

**Always:** Existing Access owner layout; stdlib-only pure parsing; immutable, payload-redacted command/payload/scope records. Public API `services/access/access_operator_input.py:parse_command(body: bytes)`. Reuse pure helpers/types from `identity_operator_input.py`; preserve its public API, union, errors and bytes. Keep this small: no new parser framework or shared package. Errors use fixed `access_operator_input_invalid` with no submitted values, decoder text or chained submitted-input exception.

Common envelope has exactly schema_version (integer1, never bool), operation_id (nonnil standard hyphenated UUID), command, scope, payload, reason_code; only evidence_ref optional. Preserve accepted spelling. Reuse Identity's five closed reasons and opaque evidence grammar/length. Optional evidence omission becomes None; explicit null invalid. Body max65536 UTF8 bytes, strict JSON, no BOM, duplicate keys, nonfinite numbers, NUL or lone surrogates anywhere. Excessive nesting/integers and nonbytes reject safely. Scope exactly `{kind:platform}`.

Payloads, all requiring `expected_absent is True`:
- application.register: app_id, expected_absent.
- permission.register: app_id, permission, scope_kind account|organization, expected_absent.
- entry_permission.register: app_id, permission, expected_absent.

app_id exactly ASCII `[a-z][a-z0-9_]{1,63}`. Permission is literal ASCII1–200 bytes, including whitespace, controls and DEL except globally forbidden NUL. Preserve bytes; no prefix/wildcard expansion or normalization. Parsing verifies no authority/association.

**Never:** SQL/migrations/roles/authority/receipts/fingerprints, CLI/target routing, DB/Docker startup or resource changes, deps, generated artifacts, Leave/editor/other apps, production/pilot/deploy/push. Preserve historical source/reference/receipt bytes and concurrent work. Identity parser/adapter/CLI must continue refusing these Access commands. ACCESS-A/B activation stays closed.

## I/O & Edge-Case Matrix

| Scenario | Input/state | Expected behavior |
|---|---|---|
| Registration | Three valid exact payloads; both permission scopes | Frozen distinct typed records; fields preserved, safe repr |
| Closure | Missing/extra/duplicate fields at root/scope/payload; wrong command/scope | Fixed safe rejection |
| Scalars | bool version; nil/malformed UUID; nonbool/false expected_absent | Rejection; uppercase UUID preserved when valid |
| App IDs | Length2/64; length1/65, uppercase, Unicode, newline | Exact ASCII grammar boundaries |
| Permissions | Length1/200, controls/DEL/spaces/punctuation; empty/201/nonASCII/NUL | Preserve accepted bytes, refuse invalid values |
| Provenance | Closed reasons; optional/valid evidence; null/URL/oversize | Existing envelope semantics preserved |
| Decoder | Bad UTF8/BOM, escaped duplicates, NaN/overflow, surrogates, deep JSON, oversized int, wrong body type | Sanitized error without submitted sentinel/context leak |
| Body bound | Otherwise valid body padded to65536/65537 bytes | Accept/refuse |
| Owner separation | Valid registry bodies sent to Identity parser/adapter/CLI | Refuse before SQL/target/connection; Identity regressions pass |

</frozen-after-approval>

## Code Map

- `services/access/identity_operator_input.py` — reuse pure decoder, field/UUID checks, reason/evidence constants, envelope and PlatformScope; do not edit.
- `services/access/identity_operator.py`, `operator_cli.py` — existing execution remains Identity-only; fake connection/target/dispatch traps prove rejection.
- `services/access/tests/test_identity_operator_input.py`, `test_operator_cli.py`, `test_identity_operator.py` — import/test conventions.
- `platform/deployment/.local/access-registry-input-20261021/` — retain this delivery's exact RED/GREEN logs and source evidence only, no credentials.

## Tasks & Acceptance

- [x] Run acceptance before creating module; retain missing-module RED. Characterize existing Identity parser before reuse; then focused TDD.
- [x] Add `access_operator_input.py` and `tests/test_access_operator_input.py`; cover every matrix row, safe exceptions and Identity separation with executed tests.
- [x] Add `ACCESS_OPERATOR_INPUT_EVIDENCE.md` mapping requirements to exact tests/commands/results and source hashes; record five impacts: owner scaffold fixture reusable here, no UI/context/ADR change, docs updated.
- [x] Update mutable delivery notes in substrate contract and prepend current checkpoint to KDG next-session; preserve all historical text. Agent completes all tasks sequentially, no commit. Root reviews/verifies/commits.

Given valid input, when parsed, then frozen Access values return without I/O. Given invalid input/wrong owner, when parsed, then safe refusal precedes execution. Given existing Identity tests, when rerun, then behavior stays unchanged.

## Implementation Notes

Root read the complete scoped product diff (26903 bytes). All nine matrix rows map to executed focused tests; focused combined277 PASS. Missing-module RED and Identity127 characterization preceded implementation, independently witnessed by root. No existing Identity source was edited. Technical footprint is one112-line parser and its tests, plus evidence/navigation. Broad verification and review follow.

Root final reviewed verification:1152 affected tests PASS47.06s, no skips; both composers exit0. All three test-only patches verified, none deferred. Root preservation audit matches41 historical files and13 concurrent changes; frozen intent unchanged. Native resources untouched. This Build is complete, with Access execution/activation still gated.

## Spec Change Log

## Review Triage Log

| Finding | Verdict | Evidence and route |
|---|---|---|
| Blind1 broad checks pending | false | Checkpoint explicitly says pending and makes no final claim; root performs required checks before completion. |
| Blind2 forbidden recursive text fixtures masked by closure/ASCII | low | New tests cannot distinguish the recursive decoder check from later field rejection. Add direct reused-decoder recursive characterization; patch. |
| Blind3 numeric decoder fixtures masked | false | Existing test_identity_operator_input.py:test_decoder_itself_rejects_nonfinite_and_oversized_integers directly tests the exact reused decoder for six numeric cases and ran in277 passing tests. |
| Blind4 ASCII-only byte fixture | false | Existing test_exact_utf8_body_byte_boundary uses a valid Unicode display and exact65536/65537 bytes through the same reused decoder; it ran in277. Accepted Access fields are all ASCII. Proposed invalid multibyte envelope would still reject after removal of byte bound and cannot distinguish it. |
| Blind5 incomplete allowed ASCII range fixture | low | Selected controls leave accidental filtering of other accepted bytes undetected. Exercise all127 allowed bytes on both permission variants; patch. |
| Blind6 owner-boundary error safety unchecked | low | Direct owner traps assert class but not fixed message/context; CLI checks code only. Assert exact safe errors/output with valid submitted sentinel provenance; patch. |

Edge returned no findings; verification-gap returned no gaps. Three independent reviews completed before triage; three test-only patch groups go to the existing implementation agent. No deferrals or contract changes.

## Verification

Canonical interpreter `platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python`, `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`, `-I -B -m pytest`, `-p no:cacheprovider`. First acceptance RED, focused suite GREEN; then root `services/access/tests apps/pts/tests/test_release.py platform/deployment/tests/test_migrate_adapter.py -q` and both composers (`--check-only`; `--identity-authority owned --no-seeds --check-only`). Retain logs and `git diff --check`. No native startup. Historical runtime proofs stay source-bound; input-only evidence here.
