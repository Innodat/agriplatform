---
title: 'KDG bounded online audit metadata'
type: 'feature'
created: '2026-10-26'
status: 'done'
route: 'dispatch'
baseline_commit: 'b3e79e9d9a8d2510c9703b28c311addbcaa940a0'
review_loop_iteration: 0
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/apps/kdg-capture/AGENTS.md'
---

<frozen-after-approval reason="standing authorization to continue ready synthetic persistence/API slices without routine stops">

## Intent

Expose a compact online audit metadata API over existing immutable committed create/changed-edit evidence. This technical Story 3.1 subset supports future audit presentation; it does not complete actor-display closure, portal UX or the full story. Existing detail already exposes durable actor IDs; do not invent names or an Identity directory.

## Boundaries & Constraints

**Always:** New inert `GET /api/v1/admin/captures/{capture_id}/events` requires current fixed-organization `kdg_capture.capture.read.all` on every page, verified account/durable actor/membership and exact organization authorization/resource scope before checkout. Reuse `AdminReadHandler` authorization, read-only engine, all_read transaction, original ten-second budget, three-second Access bound, one-second entry freshness, worker-owned unwind and safe private/no-store errors. No own fallback or offline observation.

Return a closed page: org_id, account_id (verified reader), capture_id, original owner_account_id/owner_actor_id, created_by/created_at, updated_by/updated_at, current_revision, limit, events, next_cursor. Event fields: revision, command_type (capture.create/edit), executor_actor_id, nullable initiator_actor_id, recorded_at. All actor IDs are durable attribution, never permission or finished display names. Capture stamps and revision created_at are distinct server statement times, not exact commit instants; do not force equality.

Use one bounded SELECT over scoped capture and a lateral limit+1 revision selection for coherent header/events within one READ COMMITTED statement. Select metadata only, directly from capture_revision; outcome RLS is executor-private and must not hide other-account events. Independently constrain org/capture. Numeric revision DESC, strict revision < last; immutable per-record revisions avoid timestamp ties. Default30/max100. Closed canonical cursor <=2048 bytes binds version, current account/org/capture/read.all/limit/last revision; navigation confers no authority. Refresh sees newer events; no cross-request snapshot promise. Actual UTF8 page <=64KiB. Validate after transaction, final serialization/release inside original budget. Reject malformed stored attribution/order/command/revision safely; empty continuation is valid. A first page with no revision evidence is unavailable, never invented.

**Never:** Snapshot answers/definitions, receipt/outcome/operation IDs, operational logs, eligibility evidence, new audit tables/services, cross-owner database reads, name resolution, full revision browser/restore/export or offline cache. No changes to existing APIs/helpers, schema, managed scaffold files or accepted ADRs. Synthetic local/CI only; no UI/editor/Leave, active startup/browser/sender/queue/worker integration, real services/accounts, native PostgreSQL/Docker, provisioning/migration execution, installs/dependency changes, activation/deployment/production/pilot/cleanup/push. Preserve concurrent work, historical evidence/resources and TypeScript7.0.2. Fingerprints/HMAC deferred. Never read/run/copy/hash `apps/kdg-capture/migrations/tests/schema_fixture.py`.

## I/O & Edge-Case Matrix

| Given / when | Then |
|---|---|
| Current all-read requests another owner's events | Original/latest attribution and actual create/changed-edit events only; own surface still refuses foreign owner |
| No-op or retry has no new revision | No fictitious event; distinct executor/initiator and statement timestamps retained |
| Wrong/missing account/actor/member/org/resource/permission; revocation on continuation | Existing safe authentication/denial/setup/unavailable errors, no checkout/fallback |
| Foreign/missing record; inactive/unassigned child | Same private404; historical metadata remains readable regardless of eligibility |
| Invalid/duplicate/body/selector/query/cursor; other caller/org/capture/limit | Safe422, no caller authority; every valid page rechecks current access |
| Tied/nonmonotonic timestamps, changing current revision, largest page | Numeric revision navigation, coherent single-statement header, no skipped rows, bounded actual UTF8 |
| Invalid rows/driver/acquisition/release/serialization failure, deadline/cancellation | Safe failure, no partial disclosure/late success; connection remains owned through unwind |

</frozen-after-approval>

## Code Map

- `write-candidate/admin_read.py::AdminReadHandler`, `admin_http.py`, `admin_openapi.py`: reuse exact all-read evidence/authority and owner HTTP patterns without editing them.
- `capture_create.py::HISTORY_INSERT`, `capture_edit.py`, `capture_edit_handler.py`: existing changed-only/no-op/replay behavior; existing focused tests provide oracles.
- Selected `migrations/candidates/0002_capture_storage.py:146,217,274`: immutable revision metadata, independent server stamps and all_read RLS; inspect only. No outcome join or schema change.
- New `write-candidate/audit_read.py`, `audit_http.py`, `audit_openapi.py`, `export_audit_openapi.py`, `audit-openapi.json`; `contracts/audit-generated/`; `write-tests/test_audit_{read,http,contract}.py`; `web/tsconfig.audit.json`, `web/tests/audit.types.ts`.
- Parent owns new selected-source `web/tests/audit-read-http-{fixture.py,proof.mjs}`, docs/contracts/handoff/README and evidence. Existing synthetic fixtures may be imported, never broad-copy migrations.

## Tasks & Acceptance

- [x] Importable non-dispatching route: observe actual cross-owner metadata request404 expected200; retain exact RED source/test/log.
- [x] Implement closed metadata/query/cursor models, scoped single SELECT and owned HTTP/direct handler; focused TDD covers every matrix row.
- [x] Owner-export OpenAPI and generate audit client with retained CLI; strict TS7.0.2 rejects answers, observation, selectors and unsupported fields.
- [x] Parent qualifies real synthetic loopback, focused regressions, exports/types and five adopted scaffold parities; updates contract/handoff/evidence together.

Given current read.all, when metadata is requested, then only scoped original/latest attribution and real revision events return. Given failed authority/execution, when completing, then no metadata or new rights escape.

## Implementation Notes

Parent owns this workflow, integration proof, docs, broad verification and commits. The implementation child must not render skills, commit, edit the spec or parent-owned files. Retained tool paths are recorded in `web/README.md` and the previous machine evidence `docs/evidence/online-admin-read-20261026.json` (inspect command argv selectively).

Two independent investigations agree stable-ID metadata is coherent without a new product choice; actor-name HTTP ownership remains outstanding for the full named audit surface. No irreversibles. Freeform technical API subset, no shared Leave epic/sprint mutation. Scaffold: KDG-specific semantics stay local; promote only a demonstrated neutral defect. Shared UI/context/ADRs unchanged; docs/contracts/generated types updated here. Standing authorization covers routine dirty-tree/checkpoint/size decisions; preserve other owners' files and partial deferred-work hunks.

## Spec Change Log

## Review Triage Log


All three layers launched before classification; temporary thread capacity delayed the final launch until one reviewer completed. No layer skipped. The verification review's broad mutation attempt stalled in the restricted environment and was stopped (exit130; bounded retry124); no broad passing mutation claim is made.

| Finding | Verdict | Route | Evidence |
|---|---|---|---|
| B1 | false | reject | Gapped revision fixtures do not establish a reachable committed history. Existing database stamp_capture permits only revision1 creation and +1 changed updates; deferred capture_snapshot_present checks every changed NEW revision, immutable evidence rejects change/delete, and all_read has no per-author event filter. The scoped single SELECT has no other event filter except the explicit untrusted navigation position. Rely on these existing structural invariants; no custom continuity inventory/guard is warranted. Native execution remains explicitly unqualified. |
| B2 | low | patch | Malformed-header tests use null rather than valid unequal creator/owner IDs, so the semantic predicate lacks a direct regression. Extend the existing corruption cases; no new runtime guard. |
| B3 | low | patch | Revision1 executor/owner mismatch similarly needs valid unequal IDs in the existing event-corruption test. No production change. |
| B4 | low | patch | Latest executor versus updated_by mismatch is not directly asserted with valid IDs. Extend that same focused fixture. |
| B5 | medium | patch | Current real-loopback events legitimately have equal executor/initiator, and ASGI only checks inequality for distinct actors. Add exact non-null loopback initiator assertions and exact distinct/null ASGI assertions using existing fixtures. No new fixture seeding protocol is needed; these together detect loss or conflation through actual response construction/transport. Shared root with VG1. |
| B6 | medium | patch | Serialization ValueError currently fires on the worker's first dump; the real final HTTP dump is separately executed but only its deadline is tested. Fail the second dump and assert release already occurred, with safe503/no payload. |
| B7 | low | reject | A valid100-event canonical metadata page is already tested with maximum bigint revisions and fits64KiB by a large margin. All metadata strings have fixed canonical bounds; no legal input producing a larger final HTTP serialization is demonstrated. Another mocked oversized-output test would mirror the guard rather than establish a missing real behavior. No added guard or test. |
| B8 | low | patch | Add a small aware-offset-to-UTC positive case against the existing timestamp normalizer; preserve the represented instant. No new code path. |
| B9 | low | patch | The direct test only establishes unchanged repeated reads. Rename it accordingly; actual no-op/replay behavior is already proved through actual HTTP writes and executed create/edit tests. |
| B10 | low | patch | Update the new human evidence with completed qualification counts and final review disposition as delivery finishes. Historical evidence remains unchanged. Parent-owned documentation correction. |
| B11 | low | patch | Add the two audit verification commands to the existing retained-tool README convention. Parent-owned documentation correction. |
| VG1 | medium | patch | Preverified gap: returning null for a known initiator still satisfies inequality/schema checks. Exact stored-versus-returned distinct and absent actor assertions close the regression gap. Grouped with B5; no application architecture or DTO change. |

Ten finding corrections, two rejected refinements, no deferred review finding. Existing native SQL/RLS/driver activation prerequisites and the separately owned historical actor-label contract remain outstanding; review does not claim those qualifications.

## Verification

Retained Python `platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python` (do not resolve), Node26.11.1/TS7.0.2 and modules; no installs. Explicit audit modules plus affected existing admin/create/edit no-op/replay tests; no native discovery. Existing api-client CLI in retained `scaffold-application/proof-dI2Gy9/root/platform/api-client/src/cli.mjs`. Source-bound reuse of unchanged prior proofs, actual loopback, owner export/generated checks and five scaffold parities. Private custody `platform/deployment/.local/kdg-online-audit-read-20261026/`;185 protected files. Actual SQL/RLS/driver and Identity label contracts remain unqualified before activation/full story.

Initial qualification passes10 commands on one unchanged292-source map:112 focused backend tests (26 new),41 real synthetic HTTP checks, owner export/generated freshness, strictTS7.0.2 and five scaffold parities. All277 previous implementation sources remain unchanged; prior377-test/33-command evidence and21 browser/store/HTTP proofs remain source-bound and valid. All185 protected files remain unchanged. Every matrix row has executed coverage across focused tests and actual loopback. Standalone import and phase-entry fixtures were characterized/fixed without production changes; negative harness deadline records normal shutdown at10.27seconds. Independent review follows.

Final qualification after review passes10 commands on one unchanged292-source map:115 focused backend tests (29 new audit tests),43 actual HTTP checks, owner export/generated freshness, strictTS7.0.2 and five scaffold parities. Ten findings addressed, two rejected, none deferred. All277 previous implementation sources,185 protected files and the frozen intent are unchanged. Controlled lost-initiator mutation passes the prior assertion and fails the exact assertion; unchanged production passes. Current-source forced stall records expected failure and normal shutdown at10.64seconds. Existing native/actor-label prerequisites remain; no new application architecture, schema or dependency changes.
