
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

- source_spec: `_bmad-output/implementation-artifacts/spec-env-cli-db-backend-lifetime.md`
  summary: Investigate fixture alarm expiry before a verified CLI parent handle is published (medium, unverified).
  evidence: Review B1/B2 identifies alarm armed before imports and parent_identity closing its local pidfd on interruption before fixture_main receives it. The current fix proves the held-handle Auth boundary only. Demonstrate import/acquisition/return-window expiry with exact CLI/helper PID start identities, bounded exit/signal evidence and any later CLI action; distinguish safely rejected CLI failure from continuation. Never signal an unverified parent or relax fixture5s/owner bounds merely to cover the window.

- source_spec: `_bmad-output/implementation-artifacts/spec-env-cli-db-backend-lifetime.md`
  summary: Investigate the departure predicate's elapsed bound during a backward database wall-clock step (medium, unverified).
  evidence: Review B3 notes clock_timestamp deadlines can be affected by clock changes; existing statement5s and host operation bounds remain. No backward step was observed in qualified runs. Settle the inner3s claim with an isolated deterministic clock-source fixture and engine timer authority, without changing the host clock, extending limits or claiming monotonic elapsed proof from ordinary passing runs.

- source_spec: `_bmad-output/implementation-artifacts/spec-env-cli-db-backend-lifetime.md`
  summary: Investigate the uncaptured bounded Docker exchange timeout during backend qualification (medium, unverified).
  evidence: ecc22e64 backend exits2 docker/docker_timeout31.748s; record SHA256f3f54b9e5a3d12cfe4b8f6f8de84301aed20d7b3ccad24005ae0a8dbfe973c8a. Exact original exchange/phase/cause and current-change attribution are unobserved. Volume supabase_db_agriplatform-kdg-7MIuZMsoScaLipFY_pTaQQ and empty bridge39d98fe06a6e9851da4cd5f7bf261b2403390f0e15f097f0f3cefbfe00b10fc6 remain preserved; no PG container or volume references observed. Later source-identical safely observed backend PASS does not explain the failure. Capture only safe method/category/status/elapsed/guard-phase/custody evidence on recurrence; no deadline relaxation, replay/adoption or lost-custody removal.

- source_spec: `_bmad-output/implementation-artifacts/spec-env-cli-db-backend-lifetime.md`
  summary: Investigate the existing private-handoff no-eof case timing out without its request witness (medium, unverified).
  evidence: Reviewed-source full629 fails Resources.test_integrated_private_handoff_adversaries_and_drip_deadline at defect no-eof: timeout code, daemon prefix29, one connection and under4s elapsed assertions pass, then descendant count0 instead of1. Full log SHA256655221e6d8c99bb110c2d67ad54a79cafe39b0413faf199bab2bdeb406e4e741; original scenario admission/child identity/timing and current-change attribution are unobserved. Unchanged focused nine-case diagnostic PASS15.692s, with phase1/witness present and2s deadline enforcement for the final declared no-eof case; safe record SHA2562f9649a6bf0859ea645aed182af69527eeab8791ac0c1b2dd1a0aead4f6f451d. This does not explain the original failure. Capture exact scenario admission and per-phase timestamps plus CLI/helper PID start/group/state on recurrence; retain the witness/stopped-state assertions, deadline2s, external4s bound and event prefix rather than weakening them on a passing repeat.

- source_spec: `_bmad-output/implementation-artifacts/spec-env-docker-failure-diagnostics.md`
  summary: Medium-unverified divergent Docker exception ancestry may select a later observation.
  evidence: A forged wrapper with distinct valid context/cause observations selects the cause last; current owner search finds no such divergent distinct-observation sequence. Establish a reachable lifecycle caller producing that graph before changing attribution semantics.
- source_spec: `_bmad-output/implementation-artifacts/spec-env-docker-failure-diagnostics.md`
  summary: Existing DockerSession.close failure can replace the original transport refusal.
  evidence: Baseline and current close invoke stream.close before timeout/OSError normalization; an OSError there can mask the original error while closed is already true. Characterize injected transport-plus-close failure before an owner-scoped change.

- source_spec: `_bmad-output/implementation-artifacts/spec-env-api-default-privileges-owner.md`
  summary: Investigate the unchanged Auth-job cleanup path's actual catalog-control refusal and preserve its original diagnostic cause.
  evidence: Run4ab63792-4fc4-41f2-b837-51415a6b695b catalog exits2 execution_cleanup_unresolved61.766s, retaining healthy PostgreSQL and exited-zero Auth job before new privilege dispatch; exact selected metadata/references and13 unchanged receipts are retained under platform/deployment/.local/api-default-privileges-owner-qualification. The removal path is unchanged from baseline. Separately approved cleanup does not explain the failure; settle through safe original-cause/phase diagnostics or a reproducible unchanged-path failure.
- source_spec: `_bmad-output/implementation-artifacts/spec-env-api-default-privileges-owner.md`
  summary: Determine the source of the full deployment discovery SIGTERM and whether accumulated process or order effects contributed (medium, unverified).
  evidence: Original full command exits143 after440 passing markers without a summary; isolated interrupted test and remaining231 tests all pass in serial partitions. No sender/cause or assertion failure is recorded. Retained deployment-tests.log, partition-plan.json and regression-coverage.json bind all672 IDs to unchanged source. Signal provenance or a reproducible order/supervisor failure would settle the claim; partitioned coverage alone does not.

- source_spec: `_bmad-output/implementation-artifacts/spec-env-api-default-privileges-owner.md`
  summary: Investigate the initialized malformed-second-create process test's intermittent timeout-versus-invalid-response failure.
  evidence: Final partition37 initially fails docker_timeout != docker_response_invalid in test_initialized_unknown_second_create_is_never_adopted; original artifacts retained under platform/deployment/.local/api-default-privileges-owner-qualification/post-review-tests-37-first-failure. Exact unchanged test then passes reviewed source10.761s and isolated baseline38.150s; eight initialized lifecycle methods are AST-identical to baseline, and the create refusal precedes finish/new SQL. No assertion/deadline/source change is made. Settle through request/phase/deadline observations reproducing the first failure; isolated passes do not explain it.

- source_spec: `_bmad-output/implementation-artifacts/spec-env-api-default-privileges-owner.md`
  summary: Investigate the actual backend-control Docker timeout leaving an unused volume and empty bridge before qualification.
  evidence: Reviewed run2958e313-15c6-4ef6-b607-d9712333e7d7 backend exits2 docker/docker_timeout28.952s after owner/matrix positives; no containers remain, only its run-labelled unused database volume and bridgeb3386f7333f0b6d5d1566be3c96f7744cc5966323ab374fd4476516acc049dc7. Source27/receipt13 hashes unchanged; resource acquisition code unchanged. Exact results/references are retained under platform/deployment/.local/api-default-privileges-owner-qualification; no recovery mutation/adoption/replay. Safe request/phase/deadline observations or reproduction would settle the cause; fresh-run success would not explain it.

- source_spec: `_bmad-output/implementation-artifacts/spec-env-owner-timeout-diagnostics.md`
  summary: Cover the remaining direct acquisition handoff and fresh pre-constructor idle/budget timeout observations.
  evidence: Existing resources.acquire final idle/budget pairs and fresh_session pre-constructor pair remain outside selected current/guard observation boundaries; expiry there can still omit owner_failure. Preserve original order and deadlines with integrated boundary tests.
- source_spec: `_bmad-output/implementation-artifacts/spec-env-owner-timeout-diagnostics.md`
  summary: Investigate unverified medium timing sensitivity in the unchanged two-request network deadline control.
  evidence: Initial test_networks.NetworkAcceptance.test_one_operation_deadline_spans_version_and_network_requests observed one request instead of two; identical isolated current/baseline and complete network repeats pass. Initial failure retained under owner-timeout-diagnostics/initial-network-failure; cause/change contribution requires captured request/clock timing without weakening the expectation.
- source_spec: `_bmad-output/implementation-artifacts/spec-env-owner-timeout-diagnostics.md`
  summary: Investigate unverified medium CLI-liveness departure during the synthetic backend-positive process control.
  evidence: Initial selected process group's fourth test refused invalid_owner_handoff when CLI process.poll became non-None; original return code/signal timing was not captured. Exact unchanged current/baseline repeats pass. Retain initial-process-failure and capture process departure timing/return code to settle cause without relaxing liveness or cleanup checks.

- source_spec: `_bmad-output/implementation-artifacts/spec-env-post-auth-setup-tail.md`
  summary: Investigate unverified medium hard blocking of local filesystem synchronization within cooperative ENV deadlines.
  evidence: Tail fsync and existing filesystem custody operations use deadline checks before/after, without a demonstrated selected-host indefinitely blocked syscall. Capture actual blocked-operation duration and cancellation/cleanup behavior before choosing any bounded execution change; no hard filesystem preemption proof is claimed.
- source_spec: `_bmad-output/implementation-artifacts/spec-env-post-auth-setup-tail.md`
  summary: Investigate unverified medium pre-tail acquisition/process timing failures from the first setup-tail synthetic process attempt.
  evidence: process-tail-initial-failure.log retains positive docker_timeout before tail and a replaced-artifact case that never reached verified defaults; source/unit work overlapped, with no stable single-source binding. One unchanged serial repeat and root five-case group pass without altered limits. Capture stable source and phase/clock observations to identify cause; later passes are not explanation.

- source_spec: `_bmad-output/implementation-artifacts/spec-env-kong-owned-lifecycle.md`
  summary: Medium-unverified pre-Kong Auth handoff timing failures remain unexplained despite unchanged isolated and serial process passes.
  evidence: Retain .local/kong-owned-lifecycle/process-final.log and process-negative-final.log; safe diagnostic runs pass without capturing the original escaping invalid_owner_handoff. The existing5s wrapper alarm covers repeated backend/custody observations; measure safe elapsed/count data and capture an original failing stack before attributing cause or optimizing. Preserve every custody boundary/deadline; no caching across observations or timeout enlargement.

- source_spec: `_bmad-output/implementation-artifacts/spec-id-b-membership-join-command.md`
  summary: Complete separately gated Access admission and exact membership-bound grants before activating join/rejoin with any real consumer.
  evidence: Independent review B1 confirms services/access/main.py currently joins access.grants by org_id/user_id, so retained grants can match a replacement membership. This pre-existing ACCESS-A/B transition is explicitly outside the bounded Identity delivery; current Access is incompatible with cutover and must stay stopped until coordinated migration/consumer verification. New member role/grant rows are not copied, but that alone does not prevent legacy Access reuse.

- source_spec: `_bmad-output/implementation-artifacts/spec-id-b-account-actor-ensure.md`
  summary: Make the existing root-prepared Identity synthetic owner fixture provisioning reproducible for other checkouts/CI through its existing owner tooling.
  evidence: Review B7 identified a pre-existing private bootstrap prerequisite shared by older qualifications; remove the new hardcoded frame dependency now, document explicit protected fixture input, and do not claim portable CI bootstrap is delivered.

- source_spec: `_bmad-output/implementation-artifacts/spec-access-a-staged-membership-binding.md`
  summary: Investigate intermittent existing optimized-Python qualifier subprocess10s timeouts without weakening guard assertions or runtime deadlines.
  evidence: Earlier final regression attempts timed out in unchanged membership-retention, active-membership-index and token-hook subprocess imports/probes; later unchanged focused and final1050-test runs passed. Original failing child phase was not captured, so host-load causality is unproven. Capture bounded import/guard phase observations on an original failure before optimization. Separately, repeated operator-target4s outer-budget failures had a measured equivalent3.249s import and0.001s no-network guard; only that test process allowance became60s, preserving its assertions and all runtime/database deadlines. Final native59-stage/retained evidence remains independently passed.

- source_spec: `_bmad-output/implementation-artifacts/spec-access-a-permission-register.md`
  summary: Make the existing synthetic Identity/Access qualification bootstrap reproducible from a fresh checkout using the established environment owner tooling.
  evidence: Both prior application and current permission qualifiers rely on private native/Auth/role preparation scripts and source witnesses. Current local proof is executed and source-bound, but the published qualification commands alone cannot recreate the fixture in a fresh checkout; bootstrap portability was already an explicit prerequisite before this item.

- source_spec: `_bmad-output/implementation-artifacts/spec-access-b-organization-check.md`
  summary: Qualify and bound established PostgreSQL transport failure, including pool pre-ping, before deployed Access operation.
  evidence: Existing main.py pool_pre_ping precedes transaction-local timeouts; connection establishment and pool acquisition bounds do not bound an already-established unresponsive transport. This synthetic delivery makes no total transport deadline claim.
- source_spec: `_bmad-output/implementation-artifacts/spec-access-b-organization-check.md`
  summary: Bound the existing authentication provider adapter's whole operation before deployed Access operation.
  evidence: Existing httpx timeout bounds individual I/O waits; a slowly trickling provider can exceed a total operation deadline. Provider deployment qualification is not claimed by this synthetic check delivery.

- source_spec: `spec-scribeswell-host-validation-profiles.md`
  summary: Bound migration supervisor stdout buffering before allocation rather than checking wire size after communicate.
  evidence: Blind B2 verified against original7d1cd2b adapter; existing communicate buffers before4096 rejection. New fixed worker shapes remain small and deadlines/activation denials remain, but a hard memory ceiling requires separate supervisor transport work.

- source_spec: `_bmad-output/implementation-artifacts/spec-kdg-own-capture-readback.md`
  summary: Qualify the KDG own-detail joined original questionnaire read against actual PostgreSQL during separately authorized native qualification.
  evidence: Blind B9 and verification VG1 show SQL-string doubles return prepared rows even if the original-version predicate is removed. Use two versions and an older owned capture plus restricted runtime role; current synthetic-only delivery explicitly excludes native/DB qualification and activation.
