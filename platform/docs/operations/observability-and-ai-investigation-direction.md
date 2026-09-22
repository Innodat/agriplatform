# Observability and AI Investigation Direction

**Updated:** 2026-09-22  
**Status:** Agreed MVP scope; advanced tooling comparison and AI workflow deferred

## Ownership and scope

Applications expose health/readiness, structured logs and relevant metrics/traces.
External monitoring owns collection, dashboards, alert evaluation, grouping and
routing to technical operations. Business notifications remain separate. Operational
alert delivery must not depend solely on the application notification service it
monitors. Follow [ADR-0023](../architecture/decisions/0023-structured-operational-logs-and-sensitive-data.md)
for privacy and [ADR-0012](../architecture/decisions/0012-operation-identity-idempotency-and-tracing.md)
for distinct operation/event/trace identities.

OpenTelemetry is the agreed foundation for basic backend instrumentation. The user wants browser
requests traceable through backend services and linked worker processing. Grafana,
Faro and Tempo are candidates, with Loki versus OpenSearch to be evaluated against
real investigation tasks. No final product stack, versions or dual-log-store decision
has been made. A comparative product trial is not an MVP requirement. GlitchTip/Sentry remain optional candidates where error investigation
and repair workflow provide demonstrated value. Self-hosted editions must be evaluated
on their actual features, not assumed equivalent to hosted product interfaces.

## MVP delivery boundary

Include safe structured logs with operation identifiers, health checks, a small set
of actionable operational alerts, basic OpenTelemetry tracing across the API and
shared-service calls, and one working monitoring setup verified with a simple failure
scenario. Reuse the privacy and identity rules linked above. Telemetry export must be
bounded and asynchronous; monitoring failure must not prevent business actions.

Browser-to-backend tracing may follow the first working backend instrumentation and
must not block initial implementation. The Loki/OpenSearch comparison, AI diagnosis,
approval-to-PR automation and advanced error-management workflows are deferred. Select
a practical initial setup without a comparative bake-off; keep instrumentation portable
so later operational experience can guide changes. A monitoring setup is still needed
before release, but this does not require deploying every candidate tool.

## Health signals

Report API readiness, worker health and notification delivery separately. API readiness
indicates ability to serve requests with the dependencies required for those requests;
do not make optional/asynchronous email delivery a prerequisite for Leave submission
or approval. Required access verification must still fail closed if unavailable.

Worker health includes recent process/heartbeat evidence and progress when eligible
queued work exists. An idle empty queue is healthy; a running process that makes no
progress on eligible work must be detectable. Track delivery failures and oldest
pending work separately so a provider outage is visible without presenting the entire
application as down. Specific intervals and thresholds belong to operational delivery.

A notification-provider outage should raise a delivery/backlog signal while unrelated
Leave API actions remain available. This is a monitoring contract, not a new employee
screen. Implement and verify the signals through the selected external monitoring setup.

## Shutdown reporting

Follow [platform ADR-0027](../architecture/decisions/0027-bounded-worker-shutdown-and-deployment-reporting.md).
An exceeded shutdown grace period produces a deployment warning and structured event
from the supervisor. Distinguish forced termination, replacement health and verified
processing recovery; label unconfirmed recovery honestly. Occasional recovered stops
need no page by default; repeated stops, unhealthy replacements and stalled eligible
work require attention under agreed thresholds. A dedicated dashboard panel is deferred.

## Future AI investigation-to-PR capability

Use existing telemetry, coding-agent, Git and CI capabilities with modest integration
for incident evidence, approval and task coordination. Detect/group an error; investigate
with read-only access to permitted telemetry and deployed code; report suspected cause,
evidence, uncertainty and proposed fix. After explicit approval, run an isolated coding
task through the existing BMAD/ATDD workflow: reproduce with a failing regression test,
implement the fix, run relevant tests and create a draft PR. Disclose reproduction gaps.
Normal review, merge and deployment remain separate. Monitor recurrence after deployment.

Logs are untrusted evidence, not agent instructions. Preserve privacy/access boundaries,
query limits and explicit truncation/pagination. Capture release/deployed commit context
and correlation information so investigations can identify the code actually executing.
This future target does not authorize autonomous production changes or immediate Leave
implementation. The AI feature is not an additional Leave MVP delivery requirement.

## Deferred comparison for future monitoring improvements

Use the same representative browser/API/worker failure in each candidate setup.
Evaluate ability to retrieve retained operation logs across services in time order,
follow request traces and worker retries, broaden to surrounding service activity,
see readable browser source locations, and export query results with limits visible.
Measure investigation effort, ingestion/privacy behavior, resource use and operational
maintenance. Provide bounded read-only query access suitable for future AI investigation.
Avoid reliance on repeated expansion of tiny surrounding-log windows.

The user's prior Loki experience involved excessive clicks to read surrounding logs;
this is a concrete usability concern to test, not grounds to assume a ten-line storage
limit. Do not deploy two log stores merely to postpone choosing between them.
Trial execution and numerical comparison criteria remain deferred. Initial MVP
product configuration can be selected during operational delivery without this trial.

## Research references checked 22 September 2026

- [Grafana log exploration](https://grafana.com/docs/grafana/latest/visualizations/explore/logs-integration/)
- [OpenSearch observability](https://docs.opensearch.org/platform/observability/)
- [Grafana Assistant deployment distinctions](https://grafana.com/docs/grafana-cloud/platform/grafana-assistant/introduction/)
- [Sentry Seer issue-fix API](https://docs.sentry.io/api/seer/start-seer-issue-fix/)

## Delivery impact

Scaffold: prove telemetry/error defaults before template promotion. Shared UI: no new
application monitoring or AI administration screen authorized. Agent context: existing
privacy and BMAD instructions apply. Documentation: this direction is linked from shared
scaffold guidance and Leave delivery tracking. ADR: no vendor-selection ADR accepted;
existing platform decisions remain binding. No trial or runtime change performed.
