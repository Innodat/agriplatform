---
title: 'Inert KDG audit review state'
type: 'feature'
created: '2026-10-28'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
baseline_commit: 'f1fd78025ad7bdad0e06db7129f5435a8d7c8fe5'
---

<frozen-after-approval reason="user requests continuous ready Story 3.1 work; existing activation exclusions retained">

## Intent

Add one inert in-memory audit review coordinator over the existing auditDetails adapter
and auditPresentation projection. This advances the selected AC-3/5 client publication
and retry behavior without mounting a portal or inferring current administrator authority.
Existing composition contract requires clearing page/name memory on invalidation,
account/org/capture/page/session/access fences, and explicit Retry of the complete
current-authorized aggregate. These are sufficient owner rules for this bounded state
consumer; no new service contract is needed.

A caller supplies an explicit pinned session/request, cancellation signal and current-
generation predicate. Each coordinator owns exactly one account/org/capture/page/session/
access context; switching requires invalidating/closing it and creating a new instance.
Explicit load or retry clears previous content before starting one aggregate request.
Overlapping loads cancel owned earlier work and prevent stale success or errors from
changing state. Every snapshot rechecks the caller predicate; explicit invalidation,
external abort or close removes held presentation/error state and aborts in-flight work.
Invalidated/closed instances never revive. Error/denial/unavailable remains distinct
from empty successful metadata and never retains prior names. Retry is explicit and
repeats the whole authorized GET, never just a name lookup. No automatic retry.

Given a loaded model, when invalidated or closed, then snapshots expose no model and
late responses cannot revive it. Given overlapping reads, when the old one finishes,
then it returns superseded and cannot overwrite the newer result. Given names outage,
when Retry is explicitly called, then the complete adapter request runs again and its
new current result replaces old content. Given account/org/capture/page/session/access
change signaled by the caller, when snapshot/read occurs, then old content locks.
Given failure, denied access, cancellation or timeout, when a request finishes, then
only the safe typed result remains, never a false empty audit. Caller changes to input
objects after construction do not retarget requests.

Never infer all-read from own-read, role strings or possession of a model. This is a
synthetic consumer, not actual administrator admission or integrated rendering proof.
Previously returned immutable snapshots cannot be revoked; the future renderer must
subscribe to its actual owner invalidation and reread current state. No persistent
storage, subscriptions to Auth/browser, offline authority, UI/portal/editor/Leave,
startup/worker/queue activation, real services/accounts/keys, native DB/Docker/migrations/
grants, dependencies, deployment/production/pilot/push or resource lifecycle/cleanup.
Preserve concurrent work, old evidence/resources and TS7.0.2. Never access/run/copy/hash
apps/kdg-capture/migrations/tests/schema_fixture.py.

</frozen-after-approval>

## Implementation Notes

Ready reassessment after pure presentation: composition contract already fixes caller
invalidation/full-read Retry/no-store; public state mechanics are routine app-local
design choices. No load-bearing intent gap or irreversible action. Oneshot inline;
user explicitly requests successive ready slices without routine confirmation.
Code map: new web/src/audit-review.ts with createAuditReview; new
web/tests/audit-review.test.mjs, audit-review.types.ts, audit-review-proof.mjs and
web/tsconfig.audit-review.json. Reuse unchanged audit-display.ts/audit-presentation.ts
and existing strict helpers. No global Leave tracking or full Story 3.1 done mutation.

State API: snapshot, load, retry, invalidate, close. State is idle/loading, a safe
presentation result, terminal locked or closed. Each explicit request has the adapter's
own original maximum ten-second budget. Abort only owned work; preserve independent
own-PWA data. Coordinator does not execute registration, credential setup or startup.
ATDD: retain actual missing-state acceptance RED, then focused race/cancellation/retry/
identity-switch proof and existing adapter/presentation regressions with strict TS7.

Scaffold: domain-local composition, existing transport/immutability reused, no new neutral
promotion. Shared UI/context unchanged. Docs: combined consumer evidence and final Story
3.1 gate checkpoint. ADR0022/0023/0031/0056, no ADR/release change. Model/effort, tokens
and model-only elapsed unknown; test/tool timing recorded separately where observable.

Acceptance RED run-009f5062-e691-48ff-abdc-544d302c4970 compiled successfully and
failed idle != loaded before implementation. Initial GREEN
run-0d3ed64e-9b02-4eb2-9dee-e49a35a15168 passes16 cases and strict TypeScript7.0.2.
Existing aggregate109/original73 also pass with unchanged production sources.
Documentation scope: apps/kdg-capture/docs/AUDIT_REVIEW_CONSUMER_EVIDENCE.md,
docs/evidence/audit-review-consumers-20261028.json, admin-next-readiness.md,
implementation-readiness.md, audit-display-composition.md, testing.md and next-session.md.
These reconcile the preceding assessment already present in the workspace. No global
tracking changes. All preexisting KDG runtime, generated, dependency and schema files
remain unchanged; concurrent non-KDG work is excluded from delivery ownership.

Final independent review completed with zero supported findings; no triage rows or new
deferrals. State reviewer independently passed16 cases and strict TS7 via direct
captured-source commands after wrapper EPERM. All six RED/GREEN/regression capsules
were verified against exact results and source hashes. All620 protected KDG files remain
unchanged. Concurrent Scribeswell changes arrived and were left untouched; only the
explicit KDG/spec delivery paths are committed. Story3.1 remains incomplete at the
recorded portal/all-read/session/browser/accessibility/device boundary. Continue-to-done
is not plausible within retained activation exclusions, so no speculative inert layers
or excluded actions follow. Model/context headroom and usage unknown.
