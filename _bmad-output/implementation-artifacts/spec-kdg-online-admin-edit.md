---
title: 'KDG online administrator conditional edit and original-operation recovery'
type: 'feature'
created: '2026-10-27'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '3db852ec451982fcc7edd6895c8f867598c0bb6e'
context: []
---

<frozen-after-approval reason="standing user authorization for ready synthetic KDG persistence/API work">

## Intent

Implement the API portion of the approved administrator Save goal: correct another owner's original observation with current authority, conditional revision protection and recoverable original operation receipts. Consume current administrator context and existing E2 commands/outcomes; preserve original ownership and attribute the actual administrator. This is an inert synthetic candidate, not full Story 3.2 or a mounted portal.

## Boundaries & Constraints

PUT `/api/v1/admin/captures/{capture_id}` consumes unchanged EditCommand: operation_id, command_version=1, expected_revision, observation_date, answers. No selectors or extra fields. Require current organization read.all then edit.all, matching verified account/actor/membership/scopes, before checkout. No own fallback. First read observation remains one-second fresh at SQL entry; pair has one three-second cap and original execution ten seconds, including final serialization/release.

Use all_write with actual verified executor, organization/target SQL, original immutable questionnaire/version and stored owner/creation/child/captured provenance. PostgreSQL date/JSONB equality determines no-op. Changed capture, one executor-private capture.edit receipt and immutable revision evidence commit atomically. No-op stores receipt only. Matching shown revision is required even for no-op. Conflict is existing safe409 error_id/current_revision only; rejected input produces no outcome/history. Standard row locking and conditional update arbitrate fresh operations; no force overwrite. Validation uses original definition without current child activity/assignment/new-create eligibility.

GET `/api/v1/admin/operations/{operation_id}?command_type=capture.edit` requires exactly that discriminator, current read.all and all_read; no body/other selectors. Existing compact committed receipt or unresolved union. Outcomes remain organization/current-executor/command/operation private. Found receipts authorize the actual stored org/target, never incoming path/payload; original receipt survives changed retry bytes/path and later revisions. Invalid/missing/foreign stored target yields safe503 operation_verification_unavailable. Verified absence is unresolved, not proof that in-flight work cannot later commit. Recovery needs no edit.all and never executes an edit. Existing receipt storage cannot distinguish original own/admin save surface; do not invent provenance.

All HTTP responses/errors private/no-store, closed safe typed details; unknown/SQL/commit/release/serialization faults cannot publish timely success. Own API/PWA behavior remains unchanged. Reuse controlled migration/release rules; no schema/promotion/activation. Synthetic local/CI only; preserve concurrent changes and historical evidence/resources/dependencies including TypeScript 7.0.2. No UI/editor/Leave, real Auth/Access/accounts/services, native PostgreSQL/Docker, provisioning/migration execution, startup/cache/sender/queue/worker activation, installs/dependency edits, deployment/production/pilot/push or cleanup. Fingerprints/HMAC deferred. Never read/run/copy/hash the prohibited untracked migration fixture.

## I/O & Edge-Case Matrix

| Given / when | Then |
|---|---|
| Foreign-owner capture, current all pair, valid original answers and matching revision | Actual administrator updates only date/answers/revision; original facts preserved; linked receipt/event atomically committed |
| No-op or stale unchanged values | No-op receipt without fictitious event; stale409 before effects |
| Facilitator/admin saves in either order; intervening reviewed save | Winner retained, stale loser/repeated review conflict; fresh reviewed revision/new operation may succeed |
| Lost response, changed-body/path retry, later edit | Exact original private receipt; no duplicate write; recovery after edit loss uses read.all only |
| Wrong account/org/scopes/actors, denial/outage/session/setup | Safe current-authority error, no own fallback or precheck checkout; private absence unresolved |
| Invalid original answers or missing/foreign target | Safe422/404; malformed stored receipt/target safe503; no leaked proposal |
| Body/header/selectors/bytes, first freshness, deadlines/cancellation/driver faults | Reject safely with original budgets and owned unwind; no late success |

</frozen-after-approval>

## Code Map

- Add `write-candidate/admin_edit.py`: specialized all-edit body/handler and read recovery; reuse capture_edit validation/constants/RevisionConflict, capture_edit_handler.EditProposal, operation_outcomes storage, transaction_context and AdminEditContextHandler._authorize_pair. Existing source owners remain unchanged; all-edit SQL uses org/id, not owner impersonation. Separate fixed own/all boundaries keep prior qualified sources stable.
- Add `admin_edit_http.py`, `admin_edit_openapi.py`, `export_admin_edit_openapi.py`, `admin-edit-openapi.json`: two inert routes, lazy bounded write/read engines, safe errors and final serialization; reuse existing owner command/receipt/error schemas. No exported app or mounted routes.
- Add `write-tests/test_admin_edit{,_http,_contract}.py`, `contracts/admin-edit-generated/`, `web/tsconfig.admin-edit.json`, `web/tests/admin-edit.types.ts`.
- Parent owns `web/tests/admin-edit-http-{fixture.py,proof.mjs}`, contract append, handoff prepend, web README and `docs/ONLINE_ADMIN_EDIT_EVIDENCE.md`/machine evidence. Reuse selected recorded loopback fixtures; no broad fixture copying.

## Tasks & Acceptance

- [x] Preserve actual missing-route PUT405 expected200 RED with owned shutdown; focused failing tests before behavior.
- [x] Implement/test every matrix row including SQL projections, rollback/noop, stored-target replay, pair evidence and read-only recovery.
- [x] Owner-export/generate exact client; strict TS proves command/receipt/conflict/recovery shapes and absence of authority/proposal extras.
- [x] Parent qualifies both write orderings, repeated conflicts, lost response/recovery, isolation, source preservation and scaffold parity; review and record evidence.

Given authorized cross-author Save, when qualified, then only its original conditional action is committed/recovered and current authority remains necessary. Given failed access/execution, when completing, then no unauthorized effect or success claim escapes.

## Implementation Notes

No intent gap or irreversible action. Technical route/discriminator follow current API patterns; approved Story3.2 and contracts settle replay, absence, original-version correction and role loss. One cohesive Save goal includes required recovery. Standing approval covers dirty tree, routine checkpoints and cohesive spec size; no new confirmation needed. Scaffold/shared UI/context/ADR unchanged unless a concrete neutral defect is demonstrated; KDG permission/record semantics stay local. Update documentation/types/tests together. Do not edit Leave trackers/global cached epic context.

## Spec Change Log

## Review Triage Log

| Finding | Verdict | Route | Verified evidence |
|---|---|---|---|
| B1 | medium | patch | Write-pool disposal failure skips distinct recovery-pool disposal; directly attempt both with finally and test failed first disposal. |
| B2 | low | patch | Different operation/executor concurrency covers revision arbitration only; add same-executor/operation competing retries and one-effect/original-receipt assertions. |
| B3 | low | patch | Release failure proves uncertainty, not dropped response; add post-commit wire interruption and read-only recovery. |
| B4 | low | patch | Foreign capture/invalid authority does not cover foreign-org stored outcome; seed same-executor/operation under another org and prove private absence. |
| B5 | low | patch | New GET needs its SQL/commit/release failure-specific no-disclosure assertions. |
| B6 | low | patch | Add GET stale checkout rejection before outcome/target SQL; PUT expiry is a distinct caller. |
| B7 | low | patch | Loopback negatives accept any error_id; assert exact target/access/validation IDs. |
| B8 | false | rejected | Inherited persistence-http-fixture.Connection.execute already returns active=False for create.CHILD and no assignment for create.ASSIGNMENT under inactive_removed; new fixture forwards these unchanged. The claimed absence of mode behavior is false; inherited body tests also remove child/assignment. |
| B9 | low | patch | Replace Python bool/int-equal dictionary comparison with canonical JSON equality in the recorded substitute and qualify type distinction. |
| B10 | low | patch | Refresh final evidence/handoff wording to match recorded qualification. |
| E1 | medium | patch | Stored-target SQL error becomes WriteError internal_error and PUT500; map this target verification fault to503 without changing deadline errors. |
| E2 | medium | patch | Same disposal defect as B1; retain individual finding, group correction under shared root cause. |
| V1 | medium | patch | Pre-verified gap: new PUT stream deadline untested by GET/own-PUT tests; add bounded-consumption/no-Access/no-checkout test sensitive to removing its chunk check. |

All three layers reported before triage. Thirteen individual findings: twelve direct corrections (B1/E2 share disposal root cause), one false mode claim rejected, no deferral.

## Verification

Retained owner-env Python (no symlink resolution), Node26.11.1/TS7.0.2. Explicit new modules and existing own edit/recovery/admin authority suites; actual loopback plus bounded negative; owner export/generated client/strict types; five adopted scaffold code/test parity checks. Reuse old evidence only by complete source equality:307 implementation sources and191 protected files. Private custody `platform/deployment/.local/kdg-online-admin-edit-20261027/`. Native SQL/RLS/rollback and full browser/device/UI/release activation remain unqualified.

Parent owns workflow, parent integration/evidence/docs and commits. Implementation child owns only the new candidate modules/export/generated contract/focused Python tests/type fixture/project; do not render skills, edit this spec/parent files or commit. Retained tools and generation commands are in web/README.md and previous machine evidence. Keep the child available for review patches.

Candidate qualification: ten commands,180 focused backend tests (42 new),53 actual loopback checks, owner export/client freshness, strict TypeScript7.0.2 and five scaffold parities on one unchanged322-source map. All307 prior sources/191 protected files and23 prior effective-source-bound proofs remain unchanged. Every matrix row has executed coverage. Actual missing-route405 RED, bounded expected watchdog failure and normal owned shutdown are retained. Independent review follows.

Final review qualification: ten commands on unchanged322-source map,185 focused tests
(47 new),60 actual loopback checks, generated export/client/strict types and five scaffold
parities. All307 prior sources/191 protected files and23 reused proofs remain unchanged.
Two production regression failures were observed before direct error/disposal corrections.
New stream caller test uses nonempty immediate chunks because Starlette filters empty
messages before yielding them; an in-memory removal of exactly its per-chunk deadline
check fails bounded consumption25 vs10, while unchanged code passes. Private source/log
refs are in review-qualification.json. Controlled post-commit body truncation and concurrent
same-executor/operation retries now pass. Twelve review findings addressed, one false
mode claim rejected, none deferred. Full Story3.2/native/browser/UI/release remains open.
