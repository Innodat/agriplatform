---
title: 'KDG protected own-edit context'
type: 'feature'
created: '2026-10-26'
status: 'done'
baseline_commit: '5d3bbbfd10ed3af447d787f7939810a67f3001c9'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '/home/ck/repos/innodat/agriplatform/AGENTS.md'
  - '/home/ck/repos/innodat/agriplatform/apps/kdg-capture/AGENTS.md'
  - '/home/ck/repos/innodat/agriplatform/apps/kdg-capture/docs/OFFLINE_HISTORY_EVIDENCE.md'
---

<frozen-after-approval reason="user authorizes continuing implementation without internal approval stops">

## Intent

The candidate PUT checks own-read/own-edit, but a future editor cannot load current
original-record context with independently verified offline edit evidence. Implement
the missing protected GET `/api/v1/captures/{capture_id}/edit-context`, generated
contract and isolated strict transport/Auth consumer. This completes the read API
needed by approved Story2.2; it does not activate editing or local Save.

## Boundaries & Constraints

Always derive fixed organization/account/actor from current verified Access. Check
own-read then own-edit inside one original bounded execution; verify account, actor,
membership and typed scopes agree before checkout. Preserve both actual decision IDs
and checked_at values. Each closed observation expires exactly seven days after its
own verification; read/create success cannot mint edit or all-record authority.

Return full current original-owner CaptureDetail and its exact original immutable
questionnaire, revision/provenance, permitted editable fields `observation_date` and
`answers`, plus separate exact read/edit observations. Keep owner/child/version and
creation facts immutable; unassignment/inactive child is not a historical-edit filter.
Missing/foreign capture has the same safe404. No received selector authorizes access.

Use short read-only transaction/exclusive worker ownership, private/no-store errors,
one ten-second total budget, existing verified-observation freshness and cancellation
drain. Keep detail512KiB bound and a declared whole-envelope bound. Finish exact
serialization before final budget check. A response never acknowledges a write,
creates a command or overwrites local pending/base state. Client validates complete
closed payloads and both scoped observations, pins account/org/capture and fences
publication/deadline/cancellation/Auth replacement before lease release.

Synthetic local/CI only. No UI/editor/Leave, local edit Save/queue/service-worker or
browser/default-startup activation, real accounts/Auth/Access, actual PostgreSQL/native
driver/Docker qualification, provisioning/migrations, deployment/production/pilot or
cleanup. Preserve dependencies including TypeScript7.0.2, concurrent work, prior
evidence/resources and accepted ADRs. Fingerprints/HMAC stay deferred. Never read/run/
copy `apps/kdg-capture/migrations/tests/schema_fixture.py`.

## I/O & Edge-Case Matrix

| Scenario | Expected behavior |
|---|---|
| Current own original record | Full current detail, exact editable fields and independently checked read/edit observations; no create check |
| Read allowed/edit denied or authority mismatch | Safe denial/unavailable, zero checkout; no manufactured or partial evidence |
| Unassigned/inactive historical child | Read/edit-own suffices; original definition/provenance preserved |
| Missing/foreign target | Same404 without detail/observation disclosure |
| Bad path/query/body/bearer | Safe bounded refusal before Access/checkout |
| Storage/release/serialization/deadline/cancellation failure | Safe no-store failure; exclusive ownership until unwind, no provisional context |
| Client malformed/forged/mismatched/oversized payload | Whole context refused; no local/command effect |
| Auth/session replacement or throwing callbacks | No stale publication or leaked lease; caller input stays unchanged |

</frozen-after-approval>

## Code Map

- `docs/contracts.md` own-edit increment; `docs/epics.md` Story2.2 edit-context paragraph: owner truth.
- `capture_edit_handler.EditHandler._authorize`: already verifies read/edit identity agreement; extract a small pair-returning method, keep PUT wrapper return/behavior unchanged. Existing focused edit-handler tests characterize it before refactoring.
- `capture_read.Lookup`, `DETAIL`, `_snapshot`, `CaptureDetail`: reuse scoped original-detail SELECT/validation and read-only transaction; no new database schema.
- `capture_history.OwnReadObservation`: reuse closed scoped observation shape; own-edit variant uses exact literal edit permission. Both identities/scopes must agree with returned capture owner and fixed org.
- `read_http.py`, `read_openapi.py`, exporters/generated clients: established inert HTTP/owner metadata seams. Add `edit_context*.py`, owner `edit-context-openapi.json`, `contracts/edit-context-generated` through owning generation only.
- `web/src/read-validation.ts`, `history.ts`, `read.ts`, `read-entry.ts`: reuse full-detail validator; extract only local exact read/edit observation validation if useful, no generic HTTP SDK.
- `web/tests/auth-proof.mjs`, `persistence-http-proof.mjs` and fixture: add new candidate source/types/tests to explicit selected-source lists and synthetic loopback route. No whole-silo copies.

## Tasks & Acceptance

- [x] Observe actual-route acceptance RED before implementation, preserving exact test/stub/source hashes and logs; characterize authority-pair behavior before extraction.
- [x] Implement candidate backend, owner-generated contract and focused Python tests for every relevant matrix row; keep both checks before checkout and existing PUT behavior unchanged.
- [x] Implement strict `web/src/edit-context.ts`, Auth consumer, type/runtime tests; prove loopback context after create/edit plus denial, identity, scope, original-version and late-response safety.
- [x] Root runs focused then affected regression/freshness/parity, matrix audit, independent review, final evidence/contracts/handoff and scoped local commit; no unrelated dirty paths.

Given current own-read/own-edit and original stored capture, when context loads, then
the caller gets current validated detail and two exact observations without a write.
Given failed authority, invalid/stale execution or bad stored evidence, when loading
cannot safely finish, then no partial/stale context or storage checkout before Access
is exposed.

## Implementation Notes

No intent gap or irreversible action; DTO names/bound choices are engineering details.
Root owns final docs/evidence/spec status/commit. Implementer records private exact
commands/source/logs under `platform/deployment/.local/kdg-edit-context-20261026` and
returns limits. Do not stage/commit. Existing baseline hashes/history copies saved.
Scaffold: reuse proven generated Auth/transaction/schema owners; domain context stays
KDG. Shared UI/context: none. Docs: append current contracts/prepend handoff, retain
history. ADR: inherited decisions, no accepted edits. Correct the stale history
OpenAPI description claiming no offline observation renewal, regenerate through
owners, preserving the already implemented exact own-read behavior.

## Spec Change Log

## Review Triage Log

## Verification

Retained Node26.11.1/TypeScript7.0.2 approved npm capsule, owner Python and API-client
CLI from offline-history evidence; no installs. Explicit synthetic Python modules,
compiled Auth/client unit proof, loopback proof, strict adapters and all six contract
schema/client owners; five scaffold parities. Existing isolated IndexedDB proof is
required if shared observation validation changes. Preserve failure logs and use unique
run names. No fake claims of native PostgreSQL or physical-device qualification.


All three layers completed before triage; verification reviewer started after a slot freed.

| Finding | Verdict / route | Evidence |
|---|---|---|
| B1 membership schema final newline | low / patch | Pydantic model metadata retains `$`; JS schema consumers can accept a trailing newline that runtime rejects. Reuse strict bigint terminal assertion. |
| B2 observation timestamp metadata | low / patch | Schema date-time alone permits offsets rejected by exact observation consumer. Declare canonical UTC-Z metadata matching emitted evidence. |
| B3 identifier titles overwritten | low / patch | Copying CaptureDetail.org_id also copies Org Id title into account/actor/decision properties. Apply constraints without field titles. |
| B4 actual PostgreSQL qualification | medium / defer | Tests are explicitly doubles/synthetic loopback; user excludes actual PostgreSQL/native qualification. Carry new endpoint's actual permissions/read-only/join qualification as activation prerequisite, without claiming it ran. |
| B5 advertised error-schema families | low / patch | Actual404/409/500/503 wire responses are absent from new schema suite despite declared mappings. Add existing safe failure fixtures to contract validation. |
| B6 client detail byte limit | medium / patch | Envelope whitespace test leaves detail small; deleting detail512KiB guard survives. Add valid compact UTF8 detail at bound/+1 inside544KiB envelope. |
| B7 valid fractional/calendar observations | low / patch | Shared validator uses millisecond arithmetic plus exact fractional suffix; positive whole-second cases do not execute fractional calendar rollover. Add a valid distinct-pair case. |
| B8 generic HTTP orchestration extraction | low / reject | No concrete runtime divergence demonstrated. Critical pool policy/worker ownership/safe-error machinery is already shared; domain response adapters remain explicit. A generalized route orchestration layer adds complexity for a hypothetical future mismatch. |
| B9 inherited write execution | false / reject | EditContextHandler explicitly overrides execute with a read-only signature and calls only its read transaction; direct test verifies no mutation or FOR UPDATE. Sharing protected authority-pair implementation does not expose PUT execution. |
| B10 impact decisions/traceability | low / patch (root) | Root-owned final delivery artifacts are pending; add all five impacts and executed matrix mapping to public evidence, retaining existing spec decisions. |
| B11 exact reproduction instructions | low / patch (root) | Publish exact executed argv/cwd/results and approved retained tool prerequisites alongside evidence. No new package test dispatcher/install is needed. |
| VG1 independent detail limit unverified | medium / patch | Preverified same defect as B6; assert both compact-detail boundaries through real loadEditContext consumer. |
| R1 old edit timeout scheduling | low / patch (root) | Full310 run reproduced old40ms expiry before UPDATE phase enters. Apply already characterized fake-clock phase-start correction without changing expected ownership/timeout outcomes or production code. |

Metadata corrections apply to both history and edit-context through a small local owner
helper, preserving generated-file ownership. No generic HTTP runtime rewrite or new
architecture is required. Root retains the pre-review full-suite failure and exact old
edit-test bytes before its deterministic scheduling correction.

Final verification and traceability: `apps/kdg-capture/docs/OWN_EDIT_CONTEXT_EVIDENCE.md` and `docs/evidence/own-edit-context-20261026.json`. All29 final jobs passed with source hashes unchanged; baseline protected/historical evidence preserved. Scoped local commit only; no push.
