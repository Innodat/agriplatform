---
title: 'Qualify Scribeswell Studies against frozen Access Python 3.15 runtime'
type: 'chore'
created: '2026-10-27'
status: 'done'
baseline_commit: 'fee50adb53fbd8c02402f0476e18f58e1af1b6ad'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '/home/ck/repos/innodat/agriplatform/AGENTS.md'
  - '/home/ck/repos/innodat/agriplatform/services/access/STUDIES-ENROLLMENT.md'
  - '/home/ck/repos/innodat/agriplatform/apps/scribeswell/docs/OWNER_READINESS_HANDOFF.md'
  - '/home/ck/repos/innodat/agriplatform/platform/docs/development/migration-verification.md'
---

<frozen-after-approval reason="human-owned intent — standing approve-and-continue instruction">

## Intent

**Problem:** Exact Identity0026/Access0019 readiness and the app consumer are qualified using Python3.12.3. The retained frozen production bundle contains older readiness code; it does not qualify the adopted v2 contract on Python3.15.

**Approach:** Package a separate exact-source frozen Access runtime and qualify its unchanged default Docker command using the existing isolated real-owner Scribeswell consumer fixture. Return source-bound safe evidence and update the handoff without production activation.

## Boundaries & Constraints

**Always:** Preserve the original qualified archive `/tmp/studies-current-deb424b`, its190 inputs and retained qualification, existing runtime bundle, unrelated dirty/staged work and owner boundaries. Use reviewed26/19 only, fresh synthetic executor/run and fixture-owned resources. Preparation runs from the complete qualified archive. Runtime uses restricted credentials, real provider, genuine fresh v2 artifact and default `main:app`. Retain private local proofs and bounded verified shutdown. Keep credentials out of logs, argv and public evidence. Use ATDD before implementation.

**Never:** Adopt live Identity0027/People changes, inject runtime databases/providers, fabricate artifacts, run historical KDG/Leave helpers, mutate accepted migrations/ADRs, push, deploy or claim environment release/recovery, external SMTP, physical-device or whole Scribeswell production-image qualification.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| Frozen current runtime | Exact reviewed source, offline pins, fresh artifact | Python3.15 default image passes inherited browser/signup/SQL cases | Retain safe source-bound result |
| Wrong bundle | Stale lock/source, extra importable owner module or altered payload | Refuse before claiming qualification | Preserve originals and failed evidence |
| Unsafe startup | Existing ten readiness refusal variants | Default frozen runtime refuses each | No injected shortcut |
| Lifecycle failure | Startup/probe/browser failure or timeout | Stop exact owned container and native fixture; inspect outcome | Report forced/unknown termination truthfully |
| Source drift | Input/module membership changes during run | Refuse successful result | Retain digests without secrets |

</frozen-after-approval>

## Code Map

- `apps/scribeswell/tests/studies_readiness_integration_fixture.py`: reuse `ReadinessIntegrationQualification`, fresh artifact preparation, recursive owner module freezing and ten startup refusals.
- `apps/scribeswell/tests/studies_owner_fixture.py`, `studies_signup_fixture.py`: real controlled owners, network, process lifecycle, provider/mail, browser and independent SQL oracles. Container handles need explicit cleanup; killing docker client alone is insufficient.
- Archive `services/access/deployment/{package_runtime,verify_runtime}.py`, `Dockerfile`, `.dockerignore`, `pyproject.toml`, `uv.lock`: frozen offline packager,14 owner modules, default nonroot65532 image. Preserve existing live bundle. Preparation needs full repository closure; `/srv` hashes resolve locally.
- `.local/leave-discovery-20261027/qualified-v3/{prove_image,prove_image_http}.py`: read mechanics only; never execute historical fixtures. Docker URLs use fresh fixture DB/Kong container DNS, not host loopback. Avoid raw inspect/environment dumps.
- Toolchain `platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/{python/bin/python3.15,uv/uv}`; offline cache `platform/deployment/.local/python-baseline-qualification/cache`.
- Retained qualification `/tmp/studies-current-native-20261027-review/current/qualification.json`, SHA256 `7fee233970fd6461c92515dbba1dd44e0c98c8d0533cdbc3c1a262a9e9be1e00`.

## Tasks & Acceptance

**Execution:**
- [x] `apps/scribeswell/tests/test_studies_frozen_runtime.py` — observe relevant acceptance failures; cover matrix, exact membership, secret handling and owned container lifecycle.
- [x] `apps/scribeswell/tests/studies_frozen_runtime_fixture.py` — subclass existing qualifier; freeze inputs, package separate exact-source context, build pinned image, start unchanged default command with real restricted owner environment and explicit container cleanup. Require exact14 `/srv` module membership/digests. Preserve native inherited checks.
- [x] `apps/scribeswell/tools/py/qualify_studies_frozen_runtime.py` — explicit create-only paths/toolchain/qualification, safe run result and failed-run retention. Harden with read-only, nonroot, cap-drop ALL, no-new-privileges, bounded resources.
- [x] `apps/scribeswell/docs/FROZEN_ACCESS_RUNTIME_EVIDENCE.md`, `docs/evidence/frozen-access-runtime-20261027.json`, `OWNER_READINESS_HANDOFF.md`, `FINAL_INTEGRATION_EVIDENCE.md` — record actual commands, source/image/artifact hashes, oracles, shutdown and remaining gates.

**Acceptance Criteria:**
- Given the reviewed archive, when the new driver runs, then actual Python3.15.0/uv0.13.1 offline packaging and hardened default image pass real inherited consumer, disabled authority, signup/mail/OTP expiry, SQL and privacy checks without skips.
- Given a packaged image, when independently probed, then Python version, UID, dependency provenance, exact owner source hashes and runtime restrictions are evidenced; migration credentials and pytest are absent from runtime.
- Given stale/altered packaging or unsafe readiness, when tested, then actual validation/startup refuses and no successful qualification is published.
- Given completion or failure, when cleanup finishes, then exact container/fixture termination is independently observed and original archive/live bundle remain unchanged.

## Implementation Notes

Baseline `fee50adb53fbd8c02402f0476e18f58e1af1b6ad`. No unresolved intent gaps. Footprint is app-owned qualification tooling/tests/docs; native mutations are synthetic isolated fixtures with retained recovery evidence. Standing user approval covers routine BMAD checkpoints and local commits. Shared UI/scaffold/agent-context/ADR impact: none; no new runtime contract or product behavior expected. Model: delegated Sol High; actual/usage unknown. Investigation completed without effects.

## Spec Change Log

## Review Triage Log

| Reviewer | Finding | Verdict and route | Evidence |
|---|---|---|---|
| Blind | No supported findings | No action | Traced packaging, startup, provenance, consumer and cleanup. |
| Edge | Non-validation Docker failure can count as packaging refusal | medium / patch | Lines196–204 accept arbitrary nonzero builds. Actual retained run contains verifier markers, but future infrastructure failure would falsely count; require marker and negative coverage. |
| Edge | Final log failure loses known forced termination | medium / patch | Line337 logs before record construction; a logs failure reaches generic unconfirmed record with aggregate forcedfalse. Preserve inspected record first. |
| Verification | Running-after-stop and running-after-kill untested | medium / patch | Existing mocks always stopped or fail before inspection; deleting final Running guard survives tests/native normal cases. Add focused state-transition/refusal coverage. |

## Verification

Run smallest relevant RED then focused helper tests using retained handoff Python with `PYTHONPATH=apps/scribeswell/tests`. Run new native qualifier against explicit archive/qualification and pinned binaries/cache; independently inspect safe evidence and actual stopped container, source custody, image provenance. Run affected existing consumer/deployment tests and composition `python3 tools/py/run_compose_supabase.py --check-only`. Record exact commands/results and limitations. Do not run root build/test wrappers.

Parent verification: 106 focused tests passed in0.85s. Independent `/tmp/scribeswell-frozen-parent-audit.py` passed11617 source/bundle/proof entries,14 modules1145 dependency files24 SQL checkpoints,11 containers21 processes confirmed normal. Selected Docker state confirms stopped exit0/OOMfalse; escalated ss confirms no fixture listeners. All five matrix rows covered by focused tests and actual native oracles. Native source files unchanged after success.

All three surviving findings are direct oracle/record-order/test corrections with no new public surface. Same implementation agent re-engaged; fresh native proof required because hashed qualifier sources change.

Review repairs: all three findings patched by same Sol High implementation agent. New regression tests reproduced four failures before repair;21 focused tests passed in0.67s. Parent affected suites passed113 tests in0.91s; composition15 migrations/no writes passed. Fresh final run9d74848b-c1f5-4107-a07f-13bcfc1d9cb7 uses review-fixed frozen sources;4fec pre-review success retained separately. Parent live-container independent observation matched genuine artifact bytes8b84adf4777d53773dde2679d9c84b81ac3aabb2ad87b226bb9f04a087b15fae, with migration credentials absent. No new public surface or owner contract change.

Final review-fixed native command exited0, run9d74848b-c1f5-4107-a07f-13bcfc1d9cb7, proof `/tmp/scribeswell-frozen-access-review-9d74848b`. Parent independent live/final inspectors and `/tmp/scribeswell-frozen-parent-audit-review.py` passed495 unique source/proof/tool files, original190 qualified inputs200 recursive modules5622 live-bundle entries,14 runtime modules1145 dependency files24 SQL checkpoints,11 containers21 process groups normal, all9 declared ports available with reuseaddr and no listeners. Parent audit rechecked11617 hashes/entries; artifact8b84adf4777d53773dde2679d9c84b81ac3aabb2ad87b226bb9f04a087b15fae;image8e57949ca58d596dd9eb45f1645d0b396e86c76b60d6819ae1a6b751ee23d4bd;expiry122.000231s. Each matrix row has executed focused/native coverage. Review repairs verified; no remaining findings. Actual model/usage and separated compute/build wait timing unknown; two native retries before pre-review success, one final fresh run for review-fixed sources.

Completion: all task/matrix acceptance and three review repairs verified on final source; final sanitized evidence and19 proof/322 private-log digests independently rechecked with credential sentinels absent. No deferred findings; external release/device/SMTP/sharing gates retain prior scope. Ready for scoped local conventional commit; no push.
