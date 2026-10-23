---
title: 'Scribeswell host validation profiles'
type: 'feature'
created: '2026-10-23'
status: 'done'
baseline_commit: '7d1cd2bce506a0ff800defc6b409924e1ed2c7ee'
route: 'dispatch'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The controlled host release passes only a URL to Scribeswell migrations and accepts revision-only evidence. The implemented prepared/history validators cannot yet protect an operational release.

**Approach:** Carry explicit profile and expected custody through the existing bounded worker, require post-commit matching validation evidence, and block activation on missing, inconsistent or uncertain evidence. Qualify this integration on disposable fixtures; live owner preparation remains gated.

## Boundaries & Constraints

**Always:** Preserve dormant default and native profile semantics, restricted target/role checks, create-only evidence, safe errors, bounded supervisor termination, prior-group evidence and cleanup. Custody is an externally verified expectation; local parsing/hash equality does not verify Identity. Bind host success to its selected profile/custody and exact owned head. Retain ADR-0020/0023/0056 and current history bounds.

**Never:** Infer profile from database state; create actors/grants, query Identity tables, change applied revisions/references/enforcement/importer, deploy, implement Access/Leave/factory, or alter agreed UX/standalone account creation.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| Default | No selector/custody | Existing dormant upgrade; explicit committed dormant evidence | Drift rejects |
| Replay | Explicit prepared/history plus closed custody | Exact existing 0003 validated before/after; matching profile/digest after commit | Invalid target state rejects |
| Invalid configuration | Unknown/empty profile, malformed/duplicate/oversize JSON, missing/extra custody | No worker/database work | Fixed safe failure |
| Worker mismatch | Missing/extra/stale profile or digest, revision-only reply | No success/activation | Reconciliation if launched |
| Uncertain outcome | Timeout, failed commit acknowledgement, malformed IPC | No validated evidence; preserve safe known-before | Kill/reap and reconcile actual state |
| Host release | Prior group success then invalid Scribeswell evidence | Prior evidence retained; cleanup completes; no compose | Release failure |

</frozen-after-approval>

## Code Map

- `apps/scribeswell/migrations/env.py` — native selectors and post-commit marker; preserve behavior.
- `apps/scribeswell/migrations/prepared_controller.py:custody` — closed six-field shape; extract pure parsing behind existing error wrapper.
- `apps/scribeswell/deployment/migrate.py` — 180s bounded parent/worker IPC and create-only evidence; extend both ends.
- `platform/deployment/host-release.py:preflight,deploy` — exact environment whitelist, group supervision/cleanup/activation gate; consume app-owned pure build-time contract, no server imports.
- `platform/deployment/registry.json` / `apps/scribeswell/deployment/Migrations.Dockerfile` — fingerprints/image include contract and host safety logic.
- `apps/scribeswell/tests/test_owned_migrations.py`, `test_prepared_controller_profile.py`, `test_controller_history_profile.py` — reusable actual PostgreSQL fixtures and native proof.
- `platform/deployment/tests/test_host.py` — fake executor runs real host coordinator; no real release effects.

## Tasks & Acceptance

**Execution:**
- [x] `apps/scribeswell/tests/test_host_validation_profiles.py`, `platform/deployment/tests/test_host.py` — observe missing integration acceptance red; cover matrix and real supervised replay/timeout.
- [x] `apps/scribeswell/migrations/release_profile.py`, `prepared_controller.py` — pure bounded strict JSON/profile/custody and success-evidence contract; retain existing custody errors and characterize before extraction.
- [x] `apps/scribeswell/deployment/migrate.py` — closed IPC request/response, selected expectation, commit marker check, sanitized child environment and safe evidence.
- [x] `platform/deployment/host-release.py` — allow only named Scribeswell options; validate before effects; compare exact success evidence to selection before activation, preserve other groups.
- [x] `platform/deployment/registry.json`, app deployment/docs and canonical companions — verify packaging/fingerprint, document input/recovery/gates and actual evidence.

**Acceptance Criteria:**
- Given explicit prepared/history fixture custody, when the real bounded worker replays 0003, then unchanged database state and matching committed validation evidence are observed.
- Given malformed selection or mismatched success evidence, when parent/host executes, then it fails closed at its boundary without activation or unsafe payload logging.
- Given a real held controller lock, when supervised replay exceeds its budget, then worker/backend terminate, no success is recorded, state remains intact and a later explicit replay reconciles successfully.
- Given a disposable host harness with prior group success, when Scribeswell succeeds or fails, then only matching committed evidence permits activation and owned network cleanup remains required.

## Implementation Notes

- Investigation and no-history implementation dispatch both failed with `agent thread limit reached`; BMAD's direct implementation fallback used. Existing dirty tree and concurrent KDG commit `80493084e6431f88a82c3914e182fa5f46ef7dd5` preserved; baseline remains the exact original revision above.
- Actual acceptance red: new supervised prepared replay failed before profile propagation (1failed5.75s); host revision-only acceptance test failed because activation was permitted (1failed6.96s). Existing prepared105 passed48.15s before custody extraction. These runs used the prior temporary Python3.12 interpreter/PG17 fixture.
- Implemented pure migration contract, unchanged native custody safe-error wrapper, closed IPC/profile marker checks and explicit host whitelist/evidence gate. Host failure evidence selects safe fields; arbitrary payloads never enter its report. Three payload-disclosure and one duplicate-env failures were observed before those corrections.
- Initial affected127 tests/26subtests passed112.97s; expanded platform54/26 passed6.82s. Focused integration35 passed10.88s, including actual host coordinator → real bounded worker → PG17 replay for both non-dormant profiles, actual timeout/backend disappearance/reconciliation, and real DBAPI commit followed by injected acknowledgement loss. The latter first failed because the test-only durable marker was blocked by active writer enforcement; fixture paused, production checks unchanged. This proves injected acknowledgement loss, not an actual network fault.
- Continuation reset removed the prior temporary interpreter/container. Exact former container `c5d439de0d8732c4d3ea47838e1c1c9d75fcadb7175983e559c7b0ba10328169` was absent. Recreated Python3.12.3 environment at `/tmp/scribeswell-host-tests-312` from repository requirements and pytest, and capped disposable PG17 `a5cb797c27836b90586c4b7309687d69442866f0a2e4fd0caacb64afa695a45b` on loopback32768, image `sha256:212aeeeb8faaef6c46498d86cbec6b9344d8d9492996b174664ff82c562ab685`. Initial Docker image invocation confused local image ID with registry digest and failed before creating a fixture; corrected with `--pull never` and exact local ID.
- Current platform command `/tmp/scribeswell-host-tests-312/bin/python -m pytest platform/deployment/tests/test_release.py platform/deployment/tests/test_host.py platform/deployment/tests/test_host_profiles.py platform/deployment/tests/test_migrate_adapter.py platform/deployment/tests/test_target_contract.py -q`: 66passed/42subtests7.55s. Pure contract runs with `-I -S`; existing directory COPY and fingerprint mutation verified. This is packaging-input evidence, not an image build/run.
- Matrix traceability: Default → `test_real_supervised_worker_records_committed_before_after` plus retained upgrade/denials; Replay → `test_real_supervised_replay_carries_selected_profile` and `test_real_host_coordinator_consumes_actual_supervised_replay`; Invalid configuration → `test_invalid_selection_never_starts_worker` and `test_bad_profile_configuration_stops_host_before_effects`; Worker mismatch → parent mismatch/revision-only/native-marker tests; Uncertain → real supervisor timeout, real-commit/injected-ack-loss and malformed IPC tests; Host release → full profile/fault matrix and retained prior-group/network/activation cases.
- Composition check-only passed with no writes. Canonical9 documents/19companions/11CAP/38ST, markdown links and protected/preserved dirty hashes passed. A first generic link probe mistakenly parsed Python text as Markdown; restricting it to Markdown passed without document changes. Full app regression and independent review remain pending; no production/image/provider/publication or live custody claim.

- Full first current regression: `SCRIBESWELL_TEST_DATABASE_URL=postgresql://postgres:fixture@127.0.0.1:32768/postgres /tmp/scribeswell-host-tests-312/bin/python -m pytest apps/scribeswell/tests -q` yielded931passed/1failed252.65s, one existing Starlette/httpx deprecation. The retained supervisor test observed a native failure before its expected timeout; isolated reproduction passed1/5.20s. Test now SIGSTOPs only its owned child after observing the actual backend lock wait, isolates supervisor expiry from native lock expiry, and still requires SIGKILL/reap, disappearing backend and unchanged state. Separate native expiry/retry retained. Focused37 passed18.60s; full final rerun pending. No production timeout or expected outcome relaxed.

- Final root full app regression on owned PG17: `SCRIBESWELL_TEST_DATABASE_URL=postgresql://postgres:fixture@127.0.0.1:32768/postgres /tmp/scribeswell-host-tests-312/bin/python -m pytest apps/scribeswell/tests -q` → **932passed/no skips236.49s**, one existing Starlette/httpx deprecation. Includes35 new integration cases and897 retained app cases; both actual native timeout/forced supervisor branches passed. Platform66/42 passed7.55s. Matrix and all tasks verified against scoped diff; tested code snapshot unchanged. Independent BMAD review remains outstanding; no completion/commit/production claim.

- Review corrections observed6 failing/5 passing targeted cases before fixes (final-write evidence, missing requested evidence, three overflow decodes, mutable input capture). UTF8 three cases passed unchanged and refute B3. Root probes also reproduced multiline acceptance. Focused24 passed1.93s; affected107/26 passed17.41s; platform70/42 passed4.20s after snapshot cleanup coverage. Added real denied, paused and rotated host replay, exact preservation and no credential snapshot retention. B2 remains the one pre-existing deferred issue, explicitly documented as post-buffer wire validation rather than a hard memory cap. Final full regression pending; prior932 is pre-review evidence.

- Final post-review root full command on owned loopback32768 with `/tmp/scribeswell-host-tests-312/bin/python -m pytest apps/scribeswell/tests -q`: **944passed/no skips294.43s**, one existing Starlette/httpx deprecation. Includes47 new integration cases plus897 retained; current platform70/42/4.20s. Seven review fixes complete, one refuted, one pre-existing defer. All matrix rows passed, tested code unchanged; exact owned PG17 `a5cb797c27836b90586c4b7309687d69442866f0a2e4fd0caacb64afa695a45b` stopped/absence verified. Canonical handoff, links/IDs/whitespace and protected/preserved hashes checked. No image build/live custody/production claim.

## Spec Change Log

## Review Triage Log

All three context-free reviews returned before triage: blind9, edge0, verification0. Each blind finding was checked individually before routing; no deduplication.

| ID | Verdict / route | Evidence |
|---|---|---|
| B1 | high / patch | Final save/fsync occurs after success fields are attached; exception path retains validation despite failed status. Remove validation/after on failure and prove a transient final-write fault. |
| B2 | medium / defer (pre-existing) | Baseline `7d1cd2bce506a0ff800defc6b409924e1ed2c7ee` already buffers stdout through communicate before its4096 check. This change introduces no new stdout producer; actual worker replies are fixed bounded shapes. A hard allocation ceiling needs separate supervisor transport work; document accepted wire-size versus buffering limits. |
| B3 | false / reject | Three actual invalid-UTF8 host cases pass unchanged. Decoding happens in stream.read inside the existing try; UnicodeDecodeError subclasses ValueError, so it already enters safe_failure. Opening the stream does not decode it. No production patch. |
| B4 | low / patch | Direct probe strict_json('1e999') returns infinity; all present closed shapes subsequently reject such fields, so no admission bypass. Reject overflow in the parser to honor its documented nonfinite contract. |
| B5 | medium / patch | Repeated source env reads can change selected migration inputs after preflight. Freeze validated migration values into private create-only attempt files for Docker and compare evidence against the same captured selection. No wire/API surface added. |
| B6 | low / patch | Requested profile evidence is assigned after URL validation; valid profile plus bad URL loses safe diagnostic selection. Assign immediately after closed selection validation. |
| B7 | low / patch | Direct valid multiline custody JSON is accepted despite one-line input contract; shared environment parser must reject CR/LF. |
| B8 | medium / patch | Actual host-to-worker tests currently cover success only; native/parent real denials and fake-host failure exist separately. Add real denied replay through the actual host harness, retaining earlier group, safe detail, cleanup and no activation. |
| B9 | medium / patch | Native tests cover paused/rotated history, but added host-path success uses active fixed custody only. Add paused and rotated-current-custody history through real supervised host replay. |

Seven independent bounded patches, one pre-existing transport issue deferred, one UTF8 claim refuted by unchanged-code tests; frozen intent unchanged. No new API or target provisioning. Implementation was direct-root fallback, so root applies review corrections.

## Design Notes

Use `SCRIBESWELL_MIGRATION_PROFILE` (absent means dormant) and `SCRIBESWELL_MIGRATION_CUSTODY_JSON` (required exactly for non-dormant). Custody JSON is at most 4096 UTF-8 bytes, rejects duplicate keys/nonfinite numbers, and uses the unchanged native six-field schema. IPC carries the parsed expectation; safe evidence carries profile and SHA256 of sorted compact ASCII JSON custody, or null for dormant. Neither raw custody nor URL enters evidence. The pure app-owned migration contract is build-time coordination, not cross-owner runtime authorization. Host preflight captures validated migration inputs; private attempt snapshots bind Docker and evidence comparison, then are removed before activation/on failure. Keep runtime configuration and owner administration stable during release.

Impact: scaffold integration is the existing release coordinator, not a new factory pattern; no shared UI or agent-context change; update operational docs. Existing ADRs cover this delivery; no new architecture decision or immutable ADR edit. No irreversible operation beyond owned disposable test fixtures. No unresolved user-visible intent gaps.

## Verification

- Focused acceptance red, custody characterization, affected app/profile/host suites, then full Scribeswell regression on an owned disposable PG17 fixture with no skips.
- Platform release/host/adapter/target contracts, composition check-only, canonical links/IDs and protected hashes; report exact commands/results and stop/remove owned fixture.
