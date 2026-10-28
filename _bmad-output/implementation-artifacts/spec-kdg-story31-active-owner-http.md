---
title: 'Story 3.1 active owner and KDG administrator HTTP integration'
type: 'feature'
created: '2026-10-28'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'a266f9815c74bf189b560c7e6c8c14c8c3fb47ef'
context:
  - apps/kdg-capture/AGENTS.md
  - services/access/HISTORICAL-ACTOR-DISPLAY.md
  - services/access/ACTOR_DISPLAY_NATIVE_EVIDENCE.md
  - apps/kdg-capture/docs/audit-display-composition.md
  - platform/docs/development/bmad-codex-usage.md
---

<frozen-after-approval reason="user explicitly approves routine checkpoints and continuous necessary Story 3.1 local implementation">

## Intent

Connect the reviewed Identity retained-actor reader and KDG administrator read handlers
to their configured owner factories so Story 3.1 review can use running HTTP owners.
Qualify the complete local path with restricted PostgreSQL roles and synthetic authority,
then continue the remaining story items. Story 3.1 stays incomplete until all AC evidence exists.

## Boundaries & Constraints

Preserve current owner contracts, exact original definitions/attribution, current read.all
on every request, private/no-store, original execution budgets, cancellation ownership and
safe errors. Identity28 is already implemented/reviewed: consume it, do not reimplement.
All configuration is explicit server policy; no database connection or migration at factory
construction, no browser service key, cached authorization or own fallback. Keep existing
unconfigured imports/export safe and context-only compatibility where admin config is absent.
Partial admin/display activation fails construction with safe errors. Display credentials
must remain distinct from other service keys; retain active/previous rotation policy.

The user authorizes fresh isolated local API/Auth/database/browser resources and synthetic
credentials. Use installed pinned tools and controlled upgrades; failure blocks activation,
forward recovery only, retain failed attempts/data/volumes. No production deployment, push,
real account/credential change, dependency upgrade or destructive cleanup. Never access,
run, copy or hash apps/kdg-capture/migrations/tests/schema_fixture.py. Preserve concurrent
work, especially Access main/export/package/People and generated KDG database tooling;
stage only this delivery's changes. Do not touch Leave tracking or accepted ADRs.

## I/O & Edge-Case Matrix

| Scenario | Input/state | Expected behavior | Failure |
| --- | --- | --- | --- |
| Mounted owner | Enabled display policy and restricted native reader | Active owner POST resolves selected retained labels | Existing closed403/422/503 and no-store |
| Configuration | Absent, partial, wrong role, duplicate key | Disabled without I/O, or safe startup refusal | No credential/DSN disclosure |
| KDG review | Explicit admin config, current all-read | Actual history/detail/audit-details routes compose existing handlers | Denied/foreign/malformed never fall back |
| Compatibility | Context-only caller and isolated candidates | Existing behavior/contracts preserved | No startup migration or write route activation |
| Packaging | Frozen owner payload and active OpenAPI | Includes all needed display modules and accurate schema | Missing/stale payload rejected |
| Local qualification | Fresh migrated synthetic target, real HTTP owners | Restricted SQL + TLS owner lookup + KDG exact labels/records | Retain migration failures and bounded normal stop |

</frozen-after-approval>

## Code Map

- `services/access/main.py:create_app` is active Access-hosted Identity owner; current
  concurrent People changes must survive. `actor_display_http.create_router`,
  `actor_display_native.PrivateConnection/NativeActorDisplayReader` supply reviewed behavior.
- `services/access/deployment/verify_runtime.py:SOURCES`, Docker allowlist and
  `runtime.env.example` own runtime inputs; `export_openapi.py` owns active schema.
- `apps/kdg-capture/api/runtime.py` currently configures own-context only; sibling
  `write-candidate/admin_http.py` and `audit_display_http.py` hold existing read routes.
  Their engines, closure state, custom OpenAPI and lifespan need deliberate composition;
  copying routes must not lose engine disposal or active schema.
- `apps/kdg-capture/migrations/policy.py` restricts existing local target to port55482;
  preserve that target and add an explicit fresh synthetic target if necessary. Existing
  native_fixture/capture_commit_fixture are retained-only and must not provision this run.
- `services/access/tests/qualify_actor_display_native.py` has fresh isolated PostgreSQL
  setup and captured27→28 controlled migration; reuse reviewed predecessor sources.
  `apps/kdg-capture/tests/qualify_configured_context.py` supplies TLS/socket/process patterns.

## Tasks & Acceptance

- [x] `services/access/actor_display_runtime.py`, `main.py` — explicit disabled/enabled
  configuration and native mount; safe independent tests, acceptance HTTP RED first.
- [x] Access deployment inputs and active OpenAPI — include display runtime, preserve
  isolated schema and current unrelated owner export; regenerate through owners only.
- [x] `apps/kdg-capture/api/` — explicit admin read configuration and route/lifespan/schema
  composition over existing candidates, without activating administrative writes.
- [x] Focused factory/HTTP/package tests — execute every matrix row, then affected suites
  and generated freshness. Preserve existing candidate contracts and current context.
- [x] Coordinator: fresh isolated native/socket qualification, evidence/readiness/handoff
  AC matrix, independent review, scoped commit; next unblocked item follows immediately.

Given enabled owner and KDG policy, when actual HTTP requests run, then current restricted
authority resolves exactly the authorized organization records and selected retained names.
Given denial/configuration/migration failure, when activation or reads are attempted, then
the path refuses safely and existing context/previous consumers remain compatible.

## Implementation Notes

No unresolved user intent gap. Reversible local source/config work; controlled migrations
affect only fresh synthetic targets. Routine plan checkpoints are already approved.
Baseline custody: `platform/deployment/.local/kdg-story31-20261028/baseline-7eb5f4890f2f4210958c638fd8b321e5`.
Delegate implementation Sol High; coordinator owns fresh resources and native proof.
Escalation failures must be reported to coordinator promptly, never left pending silently.
Scaffold: reuse existing lifecycle/owner/migration primitives; no speculative neutral
promotion. Shared UI unchanged in this HTTP item. Agent context sufficient. Docs/evidence
updated together. Existing release/transaction/logging/error/actor ADRs apply unchanged.
Actual model/usage and model-only time unavailable unless tool reports them.

## Spec Change Log

## Review Triage Log

## Verification

Use installed `services/access/.venv/bin/python` (Python3.15.0) and retained Node26.11.1,
TS7.0.2. Focused new factory/HTTP/package tests precede affected owner/candidate tests;
owner exporters/generator freshness and composition check-only follow. Coordinator
records exact source-bound commands/results, real socket/native and recovery evidence.

Coordinator inspected source changes and real results:70 factory,52+2 HTTP and51 catalogue tests pass; actual fresh GoTrue/TLS/restricted SQL chain9 checks pass with code0 shutdown and no remaining runtime sessions. Frozen bundle verifier and packaged-import smoke pass. Controlled Access repeat retains no Identity schema USAGE. Native/source/recovery details and AC matrix are in apps/kdg-capture/docs/STORY31_ACTIVE_HTTP_EVIDENCE.md. Independent review/commit remain pending; the last task is complete only for preparation and evidence, not the still-pending review outcome.


Review triage (all three independent layers completed before classification):

| Finding | Verdict / route | Evidence |
| --- | --- | --- |
| Edge: explicit display mapping can reuse an ambient host service key | high / patch | main routes still consume os.environ while ActorDisplayPolicy sees only explicit mapping. A caller key omitted from that mapping can therefore also authenticate display reads. Validate conflicts against actual host credentials without merging display authority. |
| Edge: SIGTERM bypasses qualification-parent cleanup in --hold | medium / patch | Only child serve installs a handler; default parent SIGTERM terminates the process without finally, leaving actual listeners alive. Handle controlled interruption and retain bounded child stop evidence. |
| Verification: schema collision guards lack tests | medium / patch | Compatible-schema-only checks would pass with guards removed. Add conflicting components/duplicate paths and factory refusal while preserving identical shared definitions. |
| Parent: new schema test depends on uncommitted People mount | medium / patch | Invoking new test against scoped review-candidate main.py reproduces AssertionError at line197. The delivery must pass independently while current concurrent People code remains preserved. |

Blind layer returned no supported findings. Four direct corrections add no product public surface or policy choice. Parent will rerun affected verification and source-bound native HTTP after patch, then obtain independent patch review. No finding deferred.

Final triage: the independent patch reviewer found a startup child-registration window
(medium / patch). Deferred termination through Popen/registration and actual-child
SIGTERM/SIGINT regressions resolve it. Independent re-review is clear. No deferrals.
Coordinator observed319 affected tests plus7 subtests, then5 final supervisor tests;
actual held-owner SIGTERM cleanup, final source-bound9-check HTTP run, scoped client
freshness and frozen bundle verification pass. A zero-session observation overlapping
the held run refused as expected; its post-shutdown repeat passes. Delivery done;
Story3.1 remains incomplete and the next real local administrator entry item follows.
