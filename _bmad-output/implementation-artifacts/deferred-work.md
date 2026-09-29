
- source_spec: `platform/deployment/AUTOMATED_OPERATIONS.md`
  summary: Investigate daemon-level gateway mutation continuing after timed-out Compose client (medium, unverified).
  evidence: Client timeout cannot prove daemon operation stopped; demonstrate overlapping candidate/recovery operations with a fault-injection Docker integration before designing extra serialization. Current checks report failures, retain recovery intent and document operator reconciliation; no guaranteed recovery on daemon/host failure.

- source_spec: `platform/deployment/DUAL_STACK.md`
  summary: Add a durable migration reconciliation gate for interrupted or uncertain migration jobs before later release attempts.
  evidence: The existing coordinator stops timed-out jobs and records safe evidence but only activation/TLS uncertainty has persistent retry gates; operator reconciliation is documented. Include process interruption and orphan network handling.
