# ADR-0037: Operational Alerts and Incident Grouping

**Status:** Accepted  
**Date:** 2026-09-23  
**Scope:** Shared operational monitoring; application-specific thresholds

## Decision

Monitor API availability, worker health, overdue delivery, recovery-point freshness and
confirmed integrity failures through shared operational monitoring. Thresholds are
technical configuration per application, not business administration settings. Group
repeated signals from the same ongoing failure into an incident, escalate that incident
when appropriate and record recovery only when supported by fresh evidence. Retain
safe diagnostic context under ADR-0023. Routine validation failures are not integrity
incidents; an empty queue is not evidence that a worker is healthy or unhealthy.

Each owner selects and verifies its thresholds. A notification-provider failure remains
distinct from Leave API availability; independently available operations remain usable.
Do not add a dedicated application monitoring screen or require a particular monitoring
vendor. Technical alerts are separate from employee notifications and approval escalation.

## Impact and verification

- Scaffold: promote proven health/heartbeat, queue-age and recovery-point signals,
  configurable alert rules and incident grouping through shared operational templates.
  These are implementation requirements, not existing builder functionality.
- Acceptance: simulate sustained failure, healthy idle workers, overdue work, repeated
  signals, escalation and recovery; verify one ongoing incident instead of alert floods.
- Shared UI: no additional business screen.
- Agent context: existing operational privacy and evidence conventions suffice.
- Documentation: operational direction and application requirements link this decision.
- ADR: complements 0023, 0024 and 0027; accepted predecessors unchanged.
- Planning only; no monitoring rules deployed or incident delivery tested.
