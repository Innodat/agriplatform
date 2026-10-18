
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

- source_spec: `_bmad-output/implementation-artifacts/spec-env-cli-poststart-auth-boundary.md`
  summary: Investigate the existing nested toolchain refusal and preserve safe child failure metadata through the image-owner wrapper.
  evidence: Fresh608704a3 original first-start control exits2 images_cli/command_refused59.547s; protected proof.json SHA256 f33d0451c166862a3d3ccb95750840689791d4fbad3c2a432c29fc5d08b1fde0. Existing images.bounded_command discards nested toolchain safe stdout, so failing probe/stage and pre/post-runtime phase are unknown. Exact prerequisite repeat and targeted same-control diagnostic pass with unchanged limits/source/receipts; neither explains the failure. Retain safe nested stage/code/exit status and guard phase/cleanup evidence on recurrence; do not infer cause from duration, weaken assertions/deadlines, or treat passing reruns as resolution.

- source_spec: `_bmad-output/implementation-artifacts/spec-env-auth-migration-job-execution.md`
  summary: Investigate bounded CLI descendant termination beyond the normal two-process oracle (medium, unverified).
  evidence: Review B6 notes production SIGKILLs the proven process group and reaps its leader before Auth dispatch. Root process tests verify both known PIDs stopped first, including a mutation oracle for skipped termination; no actual same-group non-zombie descendant surviving SIGKILL plus leader reap is demonstrated. Settle with PID start identities/group/state and a controlled adverse-scheduling kernel/process fixture, distinguishing dead zombies from live or uninterruptible work; do not infer escaping execution from leader-only wait or relax existing bounds.

- source_spec: `_bmad-output/implementation-artifacts/spec-env-auth-migration-job-execution.md`
  summary: Investigate the existing bootstrap CLI create-response timeout and retained unstarted resource.
  evidence: Current-source ead2be18 bootstrap exits2 images_cli/command_deadline27.565s; bootstrap.json SHA256b1d626127699b8ac7c75d0757625f488ea3b1a067dde026113a889ff4ba2e684. Exact container621adc552f9b181be107986dd6ad3199bb81db06062243c8585ca8bd9cf9bf82 remains created/StartedAt zero, immutable approved PG config, matching run/proof labels, network none, no mounts. Existing run_bootstrap caps commands at10s and cannot adopt/delete after a lost create ID. Separate fresh5a192bdc bootstrap passes42.137s without source/limit changes; this does not explain original timeout or recover its resource. Retain selected command/daemon timing on recurrence and define explicit verified recovery separately; no blind replay/deletion or deadline relaxation.

- source_spec: `_bmad-output/implementation-artifacts/spec-env-auth-migration-job-execution.md`
  summary: Investigate the unchanged guarded metadata-owner drip case stopping before its expected terminal-prefix event (medium, unverified cause).
  evidence: Patched-source full593 run fails Resources.test_integrated_private_handoff_adversaries_and_drip_deadline at defect drip,14.313s, with28 events versus expected29 (last volume GET absent), under its unchanged2s owner setting. Log SHA256058acbebc03ae4e53eb39e4e5bdab8e41d6c451ff5fd859e4dd8b184515098f3. This old non-executing metadata path does not enter Auth-job behavior; a direct unchanged repeat passes10.003s, which does not explain the failure or settle current-change/performance attribution. Capture acquisition/fixture/receive phase and per-request timing, PID start/group/state on recurrence, independently of the separate occupied-port failures; retain exact event and deadline assertions.
