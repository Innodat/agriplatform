---
title: 'Story 3.1 native own provisioning and configured capture APIs'
type: 'feature'
created: '2026-10-28'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '5f995f4'
context:
  - apps/kdg-capture/AGENTS.md
  - apps/kdg-capture/docs/contracts.md
  - apps/kdg-capture/docs/PROVISION_CONTRACT_EVIDENCE.md
  - apps/kdg-capture/docs/NATIVE_CAPTURE_COMMIT_EVIDENCE.md
  - apps/kdg-capture/migrations/README.md
  - platform/docs/development/migration-verification.md
  - platform/docs/development/bmad-codex-usage.md
---

<frozen-after-approval reason="user approves successive necessary Story3.1 local implementation and controlled synthetic qualification">

## Intent

Close the concrete native provisioning privilege gap and expose existing own setup,
create, own edit/context, operation recovery, history and detail through the configured KDG API. These
are prerequisites for Story3.1 AC2/AC4 actual facilitator synchronization and own-PWA
separation. Consume established contracts; no new questionnaire/editor management.

## Boundaries & Constraints

Use current independent Access checks, fixed organization, account/actor/membership,
original questionnaire, immutable eligibility/evidence and first-committed retry
contracts. No all-read fallback or all-record offline authorization. Keep external
checks outside local business locks and original ten-second execution budgets,
cancellation/drain/engine disposal, private no-store and closed safe errors.

Observe actual restricted runtime provision failure before migration. Add a new linked
controlled candidate migration; do not edit0001/0002, stamp, downgrade or re-record
historical evidence. Narrow eligibility INSERT to required columns and own-write scope;
bind org/account/actor and validated membership evidence. Server controls issuance time.
Existing immutable references cannot be updated/deleted; no broad role/table/DDL grants.
Use owner-local context if extra domain binding is needed; do not expand neutral
transaction tools for an unproven domain requirement. Preserve previous running
consumers and seeded data; failure blocks activation, explicit forward recovery only.

Factory configuration stays explicit, safe with absent own settings, no DB or migration
on construction/startup, exact restricted runtime role and server-selected questionnaire.
Preserve context-only/admin-only compatibility. Compose owner schemas without losing
paths, components, route closure/lifespans or duplicate-method protection; GET/POST on
one legitimate captures path must coexist. Expose no admin edit/write API here.
Generate exports/types only through established owners.

Fresh isolated synthetic resources and credentials are authorized. Coordinator owns
native migration/resource/actual-HTTP execution. Preserve retained targets/resources,
concurrent generated database tooling/People/Leave changes and evidence. Never access,
run, copy, hash or traverse into apps/kdg-capture/migrations/tests/schema_fixture.py.
No production deployment, push, real credentials/accounts, dependency upgrade or cleanup.
No physical device/provider/release claims from local tests. Story3.1 remains incomplete.

## I/O & Edge-Case Matrix

| Scenario | Input/state | Expected | Failure |
| --- | --- | --- | --- |
| Native setup | Fresh own-read/current create authority | Commit complete bounded eligibility + latest published definition | Missing privilege RED before controlled upgrade |
| Native isolation | Wrong org/account/actor/membership, read/all mode, caller time, update/delete | Exact RLS/column privilege or immutable refusal | No cross-scope issuance or forged issuance time |
| Atomicity | Later-child failure/oversize/deadline | Entire issuance batch rolls back | No partial returned/committed setup |
| Recovery | Controlled upgrade failure then explicit retry/repeat | Rollback ledger/effects, previous consumer survives, forward retry | No auto downgrade or startup migration |
| Configured own API | Complete explicit config and real current authorization | Actual setup/create/own-edit/context/recovery/history/detail compose existing owners | Denied/foreign/malformed requests fail safely |
| Schema/lifetime | GET+POST same path, component/method collision, shutdown | Both legitimate operations retained; ambiguity refused; all engines dispose | No silent route/schema override |

</frozen-after-approval>

## Code Map

- Existing provision.py INSERTs child_eligibility but candidate0002 grants runtime SELECT
  only. Its ProvisionHandler checks READ/EDIT/CREATE_ALL/CREATE_ASSIGNED independently
  before own_write transaction. Current selected query orders numeric display_version
  descending. Preserve controlled locks, complete-response/1000-child bounds.
- Existing candidate0002 has immutable trigger and force RLS. New candidate0003 can
  extend privileges/policy without changing applied predecessors. Existing app-owned
  migration policy permits explicit fresh Story31 target; neutral generated tooling
  is concurrent work and not ours to edit.
- API runtime.py/admin_runtime.py compose active context/admin handlers. Candidate
  provision_http/create_http/edit_http/edit_context_http/recovery_http/read_http/history_http each own lazy engine,
  lifespan and offline OpenAPI owner; reuse them instead of duplicate route wrappers.
  admin_runtime.compose_schema currently refuses any duplicate path, including a
  legitimate GET+POST own captures collection; deliberate method merge needs tests.
- write-tests/test_provision{,_http,_contract}.py and test_create/read/history/recovery
  protect existing contracts. New focused configured own tests must cover actual
  route composition, safe partial settings, no I/O and lifetimes. Do not discover
  migration tests broadly or run historical native preparers.
- Coordinator's private fresh frame is documented in STORY31_ACTIVE_HTTP_EVIDENCE.md.
  tests/qualify_story31_http.py supplies source-bound actual Auth/TLS owner path;
  adapt through active configured own factory after actual migration, retaining
  all historical attempts. Do not import or rerun preparers on existing targets.

## Tasks & Acceptance

- [x] Coordinator actual restricted native provision RED and custody before upgrade.
- [x] New controlled candidate migration + provision local binding + focused tests;
  least privilege, immutable/time, complete atomicity and previous consumer contract.
- [x] Configured own composition, explicit settings and generated configured export;
  focused route/schema/lifetime/config tests observe acceptance failure first.
- [x] Coordinator actual restricted native and running HTTP proof, controlled failure/
  rollback/forward retry, focused affected checks, independent review and scoped commit.
- [x] Update current AC1–6 evidence/readiness/handoff; choose next actual own UI/PWA item.

Given actual native own provision after controlled upgrade, the restricted runtime
returns complete server-committed setup without unrelated authority. Given explicit
configured own APIs, actual facilitator create appears in own history and current
administrator refresh, preserving original definition, owner and audit on retries.

## Implementation Notes

Local user authorization covers this ready prerequisite; no new intent decision.
Implementation Sol High, coordinator owns synthetic runtime/migration proof. Scaffold:
reuse controlled migration/transaction helpers; no generic promotion unless concrete
neutral defect is demonstrated and fixed through template+consumer. Shared UI unchanged.
Agent context sufficient; documentation/AC matrix updated together. Existing ADRs apply.
Model usage/model-only timing unavailable unless exposed. Do not start until preceding
local-admin-entry item is reviewed and committed.

## Spec Change Log

## Review Triage Log

Three independent reviewers completed blind, edge and verification lenses. No supported
remaining findings. Verification withdrew configured detail/edit wiring coverage after
inspecting the real factory, actual HTTP script and source-bound eleven-check receipt.
This was an evidence split; no finding deferred.

## Verification

Installed Python3.15.0/SQLAlchemy2.1.4/Alembic1.20/Psycopg3.3.6; pinned Node26.11.1,
TS7.0.2 and retained API generator. Focused acceptance RED first, then affected existing
provision/create/recovery/read/history/admin contracts. Coordinator actual restricted
PostgreSQL and Auth/Access/HTTP proof establish permissions and rollback; mocks do not.
Owner exporter/client freshness and composition check-only follow meaningful checks.

Coordinator acceptance RED observed before implementation: actual ProvisionHandler
using restricted kdg_capture_runtime + actual GoTrue/current Access over TLS returns
503 provision_unavailable; SELECT true/INSERT false. Frame:
platform/deployment/.local/kdg-story31-20261028/fresh-8f3e984596bb453a902adb8710b4860d/provision-red-777dfdaa9778454389c5e7fb99f0d3ed.
The first reused Auth session correctly failed401 after the preceding provider
revocation/expiry test; failure retained. Explicit actual synthetic sign-in reacquired
sessions before the native RED, no authorization bypass. Current owner hold:
http-0e310203b40b43b394bfefca4eb1b709. Coordinator owns further native execution.
No new implementation thread is available under actual service thread limit; continue
the existing Sol High implementation thread for the next coherent Story3.1 item.

Native qualification after actual0003 failure/rollback/explicit upgrade/repeat passes.
Applied0003 source bytes remain unchanged. A real1000-child10-second timeout exposed
N+1 SQL. Two semantic characterization cases preceded the app-owned batched lock,
post-lock reread and issuance correction; SQL-count RED observed8011 vs bound20.
No neutral helper, grant, cap or budget changed. PostgreSQL17 SELECT List guarantees
ordered volatile output evaluation when excluded from ORDER/GROUP/DISTINCT keys.
Final source-bound native16 + load3 (1000 in0.446s, real UTF8 response-cap rollback
of1000 inserts,1001 refusal) and coordination3 (actual post-lock child change,
bounded contention/cancellation) pass. Actual configured own/admin HTTP11 checks
pass, including committed edit/no-op/recovery, exact original v1 after v2 publication
and existing foreign-org record404. Foreign row is explicitly trusted native fixture
preparation, not claimed HTTP create authority. Earlier transient503/current-observation
failures and a source-drift refusal remain retained; no expected result was relaxed.
Coordinator final focused60 tests +9 subtests pass. Earlier reported affected320 tests
+76 subtests precede batch correction and require affected recheck after it. Formal
three-lens review and evidence/handoff/commit are pending. Environment interruption
stopped owned resources255; resume observations retained, only owned resources restarted.

Final coordinator affected verification after batching: **420 passed, 81 subtests**
(104.05 seconds), exact selected test paths under tests/ and write-tests/: configured
own/admin/context, context_api; provision/provision_batch/provision_migration/
provision_http/provision_contract; create/read/edit/edit_context/recovery/history/
admin/audit/audit_display HTTP + contract tests. Command: services/access/.venv/bin/python
-I -B -m pytest [those explicit test_*.py paths] -q -p no:cacheprovider. One upstream
Starlette TestClient deprecation warning; no skips or failures. This supersedes the
pre-batch affected report. Both configured exporters --check, retained API generator
--schema configured.openapi.json --output contracts/configured-generated --check,
TS7 strict noEmit generated types, sync-kdg-write/database/native-database --check
and python3 tools/py/run_compose_supabase.py --check-only exit0.
Applied0003 digest matches the actual controlled-upgrade source binding.

Current evidence/matrix: apps/kdg-capture/docs/STORY31_OWN_API_EVIDENCE.md and safe JSON
receipt. Next unblocked work is ordinary own capture/My observations integration with
foreground delivery, then PWA shell/update/cache and invalidation qualification.
Story3.1 remains incomplete. Environment context headroom unknown; continue with
retained current resources, no destructive cleanup. Model/effort implementation
Sol High; reviewers inherit coordinator; model-only usage/timing unavailable.
