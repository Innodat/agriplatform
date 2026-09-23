# ADR-0120: Initial Operational Alert Thresholds

**Status:** Accepted  
**Date:** 2026-09-23  
**Scope:** Leave initial production monitoring

## Decision

Apply [platform ADR-0037](../../../../../platform/docs/architecture/decisions/0037-operational-alerts-and-incident-grouping.md)
with these initial technical defaults:

| Signal | Threshold |
|---|---|
| Leave API unavailable | Five consecutive minutes |
| Worker heartbeat absent | Five minutes, including when the queue is empty |
| Notification delivery work overdue | Warn after 15 minutes; escalate the same incident after one hour |
| Latest verified usable recovery point too old | Alert immediately once age exceeds the one-hour target in ADR-0119 |
| Confirmed data-integrity failure | Alert immediately |

Measure notification delay from when delivery work first becomes due, excluding future
scheduled delivery. Ordinary retry backoff does not reset that age or hide a delivery
incident. Observe producer handover and downstream delivery separately through their
owners; producer acceptance alone does not prove recipient delivery. Heartbeat monitoring
is independent of whether jobs happen to be available. Missing backup evidence must not
be presented as a verified healthy recovery point.

Group repeated failures into an ongoing incident and record verified recovery. These
thresholds do not establish a staffed 24-hour support SLA. Monitoring implementation
selects probes, sampling intervals and routing before pilot and demonstrates that they
can detect these conditions. No custom Leave monitoring administration screen is needed.

## Impact and verification

- Acceptance: simulated threshold crossings, healthy idle worker, future scheduled work,
  overdue retries, grouped repeated signals, escalation and verified recovery.
- Scaffold: shared monitoring contracts and configurable operational templates under
  platform ADR-0037, promoted when proven.
- Shared UI/agent context: no new screen or agent instruction required.
- Documentation: requirements target gate and delivery tracker synchronized.
- ADR: applies platform ADR-0037 and Leave ADR-0119; originals unchanged.
- Planning only; no alert rules deployed or runtime checks executed.
