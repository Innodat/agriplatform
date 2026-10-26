---
title: 'KDG online organization capture reads'
type: 'feature'
created: '2026-10-26'
status: 'done'
route: 'dispatch'
baseline_commit: '328049f1ac6e67df74c6a88a2ef139849c25df03'
review_loop_iteration: 0
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/apps/kdg-capture/AGENTS.md'
  - '{project-root}/apps/kdg-capture/docs/contracts.md'
---

<frozen-after-approval reason="continued bounded persistence/API work authorized without routine approval stops">

## Intent

**Problem:** Current capture APIs read only the caller's observations. Approved Story3.1 requires a separate online organization read boundary without granting offline all-record access.

**Approach:** Add an inert administrator history/detail candidate and owner-generated contract. Reuse proven record validation, bounded pagination and execution ownership. Preserve own APIs and caches. This technical API subset excludes actor names, audit events and portal presentation; it does not complete Story3.1.

## Boundaries & Constraints

**Always:** Each request verifies exact configured-Khula `kdg_capture.capture.read.all`, current account, durable actor, membership, organization authorization/resource scope and fresh checked evidence before checkout. Denial has no own fallback. Server-selected `all_read` is not client authority. SQL independently constrains organization; detail also constrains capture ID. Retain original owner/actor, questionnaire definition and creation/update provenance; inactive/unassigned children remain historically readable.

Expose `/api/v1/admin/captures` and `/{capture_id}` only on a separately constructed unmounted candidate. Detail retains `CaptureDetail`. A separate closed page echoes verified account/org, dates/limit, items and nullable continuation; no observation, expiry, offline lease or all-edit authority. Existing own routes/types/defaults stay compatible. All replies, including failures, are private/no-store; no browser/storage/SW integration.

History requires inclusive explicit dates, default limit30/max100, descending immutable `(created_at,id)`, limit+1 selection. Closed canonical base64url cursor max2048 bytes binds verified account/org/read.all/dates/limit; it is untrusted navigation, never authority/HMAC. Own/all cursors are incompatible. Recheck every page; no cross-page snapshot or deletion inference. Preserve actual UTF8 limits:512KiB detail/2MiB page, smaller pages continue after last included row without skipping.

Use existing10-second total execution budget, max3-second Access window, one-second SQL-entry freshness, bounded read-only acquisition, worker unwind, release and final serialization fences. External checks occur outside transactions; no provisional result or raw error/log payload escapes.

**Never:** UI/audit endpoint/editor/Leave, active startup/browser/worker/sender/queue activation, schema changes or migrations, real accounts/Auth/Access, native PostgreSQL/Docker, provisioning/deployment/production/pilot/cleanup, installs/dependency changes or push. Preserve concurrent work, historical evidence/resources and TypeScript7.0.2. Fingerprints/HMAC remain deferred. Never read/run/copy/hash `apps/kdg-capture/migrations/tests/schema_fixture.py`.

## I/O & Edge-Case Matrix

| Scenario | Expected behavior | Failure behavior |
|---|---|---|
| Current all-read, another owner in Khula | Original detail and bounded history permitted | Own API still refuses foreign owner |
| Cross-org/missing record or forged selector | Same protected missing-detail behavior; no leaked rows | Strict query/body/ID validation, no client authority |
| Missing/wrong actor/member/account/org/resource/permission or stale evidence | Reject before checkout | Safe401/403/409/503, denial distinct from outage |
| Multi-page/ties/date changes/byte truncation | Correct immutable keyset and continuation; exact original definitions | Invalid stored row refuses whole response |
| Own/all/other caller/date/limit cursor, malformed JSON/base64/duplicates | Bound closed cursor, current scope enforced independently | Safe422; no signature or cursor registry |
| Revocation between pages/unknown or duplicate query/nonempty body | Recheck every request, no own fallback or offline observation | No provisional page or stronger authority |
| Cancellation/timeout/acquisition/release/serialization failure | Owned connection retained through unwind, no late success | Safe bounded failure, private/no-store |

</frozen-after-approval>

## Code Map

- `write-candidate/capture_create_handler.py`: reuse `_authorize` and `_complete_worker`; extract only narrow resource-binding validation while retaining strict own default and existing create fallback behavior. Characterize existing own callers before refactoring.
- `capture_read.py`: retain own `_snapshot` wrapper and its owner check; share structural/original-definition validation explicitly with new admin wrapper. `capture_history.py`: reuse strict query/cursor/keyset/byte accounting through narrow private helpers, keeping own wrappers/observation unchanged. No generic scope engine.
- New `admin_read.py`, `admin_http.py`, `admin_openapi.py`, `export_admin_openapi.py`, `admin-openapi.json`: fixed all-read evidence/queries/page and two inert routes. Reuse `read_http`/`history_http` engine, safe errors, private responses, worker and schema metadata.
- `migrations/candidates/0002_capture_storage.py` and generated `write-tools/transaction_context.py` already recognize all_read; inspect only, no changes. Access organization_check already emits organization resource scope for read.all; no shared-service change.
- New `write-tests/test_admin_{read,http,contract}.py`, relevant existing read/history/create-handler tests: behavioral ATDD then focused TDD. Parent owns actual synthetic loopback proof, docs/evidence/broad qualification; child owns API/tests/generation/type fixture.

## Tasks & Acceptance

- [x] Add importable non-dispatching admin stub and actual missing foreign-owner-read acceptance RED; retain exact source/log evidence before implementation. Characterize own semantics before shared-helper changes.
- [x] Implement files above and cover every matrix row with synthetic ASGI/Access/connection collaborators. Both HTTP and direct handler paths must agree.
- [x] Owner-export OpenAPI; generate `contracts/admin-generated/` with existing api-client CLI; add strict TS7.0.2 contract fixture proving admin page cannot supply own offline observation. Never hand-edit generated artifacts.
- [x] Parent: separate selected-source real-loopback proof with synthetic Access/storage, bounded owned shutdown; update `docs/ONLINE_ADMIN_READ_EVIDENCE.md`, machine evidence, append contracts, prepend handoff and README.

**Acceptance:** Given verified all-read, when another owner's record/pages are requested, then only configured-org current original-version records return. Given denial, stale authority or failed execution, when requests finish, then safe errors disclose no records and own-only behavior/offline authority remain unchanged.

## Implementation Notes

Parent owns this active BMAD workflow; the implementation child works within it and must not render or start another workflow, commit, or edit parent-owned evidence/docs.

No unresolved product gap or irreversible action. Independent contract/code investigation confirms this API subset closes from accepted choices; actor names/audit/portal gates remain. Standing authorization covers dirty-tree preservation and routine checkpoints. KDG capability/record logic stays local; reassess any demonstrated neutral defect for scaffold promotion. Shared UI/context/accepted ADRs unchanged; docs/contracts/types updated together. Freeform technical subset, no whole-story/sprint completion claim.

## Spec Change Log

## Review Triage Log

All three layers reported before classification. Runtime allowed only one fresh reviewer at a time; none was skipped and no result was acted on before the final layer reported.

| Finding | Verdict | Route | Evidence |
|---|---|---|---|
| B1 | medium | patch | New administrator detail parses/validates/serializes its large stored record inside the transaction. The existing history branch already validates after commit. Move only new admin detail CPU work after the short SELECT transaction; add a real execution-phase assertion. No public surface or new guarded state. |
| B2 | low | reject | The finite limit+1 selection can materialize101 bounded detail candidates before packing2MiB. This is the same deliberately bounded existing history pattern; no2MiB RSS promise or observed capacity failure exists. Extra memory guards/streaming would add complexity without a concrete failure. Actual capacity remains an activation qualification, not an invented application architecture. |
| B3 | medium | patch | New SQL contract asserts only organization and LIMIT; recorded storage independently simulates date/keyset/order. Extend the existing focused business-query assertions for actual date predicates, tuple comparison and descending ordering. This is a limited static regression guard, not native SQL proof. |
| B4 | medium | patch | Parent raw node:http body request has its own10-second timer but no shared proof signal; a request starting late can outlive the total proof deadline. Pass the existing controller signal to this request; parent will inject a pending raw-request deadline to qualify actual abortion/shutdown. |
| B5 | low | reject | The fixture-only control endpoint reads one ASGI chunk. Current consumers send one small buffered Node fetch JSON body; no production endpoint uses it and no current consumer failure is shown. A bounded multipart receive loop/fixture protocol tests add branches for an unlikely development-only case. |
| B6 | medium | patch | New historical all-read tests assert no activity SQL but do not set existing synthetic activity/assignment collaborators to failing states. Add detail/page behavioral characterization under inactive child and removed assignment; no new runtime check. |
| B7 | medium | patch | Status-specific generated error contracts lack actual404/500/observation-expiry/execution-timeout wire samples from the new routes. Extend existing actual-response schema validation for those paths. |
| B8 | low | reject | Exact8192-byte guard coverage is absent, but legal closed fields/canonical cursor are independently bounded well below it even when percent encoded. Proposed oversized boundary requests are invalid regardless, so status/no-checkout assertions would not detect guard removal. A patched-parser branch test would mirror implementation rather than establish missing public behavior. |
| B9 | low | patch | Generated request query should also prove forbidden owner/org selectors fail excess-property checking. Add two direct negative TypeScript fixtures; no runtime complexity. |
| B10 | medium | patch | Current cancellation tests start after worker admission; request-body and Access waits have timeout coverage only. Add gated cancellation at both pre-checkout phases, confirming prompt cancellation/no later checkout or success. |
| VG1 | medium | defer | Preverified actual-SQL gap: both storage doubles sort/filter independently, so native execution with tied timestamps/multiple pages remains required. B3 provides a static clause guard only. Native PostgreSQL/permissions are explicitly excluded by user intent; record the real database qualification as a prerequisite, with no passing native claim. |

Seven independent small patches are implemented; three low suggestions rejected, one native verification item deferred. No intent gap, frozen change, new public method or schema is needed.

## Verification

Use retained Python `platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python` (do not resolve symlink), Node26.11.1/TS7.0.2/modules, no installs. Explicit new/admin and affected create/read/history synthetic modules only; never broad native discovery. Existing owner CLI is retained at `platform/deployment/.local/scaffold-application/proof-dI2Gy9/root/platform/api-client/src/cli.mjs`; `--schema .../admin-openapi.json --output .../contracts/admin-generated [--check]`. Run owner freshness, strict types, loopback, affected API/HTTP regressions and five scaffold parities. Reuse earlier evidence only with unchanged effective source hashes. Private custody `platform/deployment/.local/kdg-online-admin-read-20261026/`;182 protected files. Native privileges, production wiring and full Story3.1 remain unqualified.

Candidate qualification:33 passing commands on one unchanged277-source map,373 synthetic backend tests (342 prior +31 admin),37 actual loopback checks,127 direct client tests, eight affected HTTP regressions, eight owner export checks, eight generated-client checks, strict TS7.0.2 and five scaffold parities. Twelve earlier browser/store proofs retain unchanged complete effective-source hashes. Every matrix row has executed coverage; shared between-page/date-change behavior is exercised by test_history_http.HTTPAcceptance.test_continuation_rechecks_current_dates_and_refresh_finds_newer_insertion using the extracted helpers, alongside new all-mode filter/keyset cases. Deadline injection records normal fixture shutdown after10.43seconds. Independent review follows.

Review patches: new admin detail validates after commit; static query clauses, historical inactive/unassigned reads, wire error samples, negative TS selectors and pre-checkout cancellation are covered. The raw body request now uses the existing shared proof signal; controlled delayed-response RED/GREEN aborts at10.69s instead of16.33s, with normal fixture shutdown. Final broad verification first exposed the preexisting history fixture60ms deadline expiring before its intended SQL phase. A controlled80ms authorization delay reproduced this; expiring the original budget only after selected phase admission passes the same delayed characterization while preserving cancellation, timeout, ownership and exactly-one-release assertions. No application deadline or expected outcome changed. Final qualification passes33 commands on one unchanged277-source map:377 backend tests (342 prior +35 admin),37 actual HTTP checks,127 direct client tests, eight affected HTTP proofs, all eight export/generated checks, strictTS7.0.2 and five scaffold parities. All182 protected files and the frozen intent remain unchanged. Native SQL/permissions remain deferred before activation.
