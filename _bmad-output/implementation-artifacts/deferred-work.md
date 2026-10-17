
- source_spec: `platform/deployment/AUTOMATED_OPERATIONS.md`
  summary: Investigate daemon-level gateway mutation continuing after timed-out Compose client (medium, unverified).
  evidence: Client timeout cannot prove daemon operation stopped; demonstrate overlapping candidate/recovery operations with a fault-injection Docker integration before designing extra serialization. Current checks report failures, retain recovery intent and document operator reconciliation; no guaranteed recovery on daemon/host failure.

- source_spec: `platform/deployment/DUAL_STACK.md`
  summary: Add a durable migration reconciliation gate for interrupted or uncertain migration jobs before later release attempts.
  evidence: The existing coordinator stops timed-out jobs and records safe evidence but only activation/TLS uncertainty has persistent retry gates; operator reconciliation is documented. Include process interruption and orphan network handling.

- source_spec: `_bmad-output/implementation-artifacts/spec-env-postgres-graceful-shutdown.md`
  summary: Investigate intermittent existing guarded-CLI descendant cleanup assertion failure during full deployment regression.
  evidence: First full run failed test_resources.Resources.test_integrated_private_handoff_adversaries_and_drip_deadline after its unchanged 0.5-second stopped-state observation; four focused repeats and a full 465-test rerun passed without production/assertion changes. Cause unobserved. Protected failed log is recorded in ENV_POSTGRES_SHUTDOWN_EVIDENCE.md. Capture failing adversary, PID start identity/process state and process group on recurrence to distinguish observation delay from escaping descendant; do not weaken the assertion on passing reruns.

- source_spec: `_bmad-output/implementation-artifacts/spec-env-postgres-graceful-shutdown.md`
  summary: Investigate intermittent image-negative guarded-CLI matrix timeout in full regression.
  evidence: Pre-review-patch full run466 failed unchanged test_resources.Resources.test_integrated_owner_negative_matrix_never_replays_or_returns_proof with docker_timeout instead of image_identity_mismatch; focused exact test passed in13.012s. Protected deployment-tests-3.log SHA256 edec8b991802b7450ddcafec38d72506b7d88e78555e403383ff5690c096f672. The failing scenario is not retained because the assertion sits outside subTest. Capture scenario and bounded-phase timing on recurrence without relaxing the five-second owner deadline or expected refusal.
