---
title: 'ENV PostgreSQL create-request construction'
type: 'feature'
created: '2026-10-16'
status: 'done'
baseline_commit: '7f6531d318543b8a017adccd9725dd6073ffba79'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '/home/ck/repos/innodat/agriplatform/AGENTS.md'
  - '/home/ck/repos/innodat/agriplatform/platform/deployment/fixtures/supabase-pg17-profile.md'
  - '/home/ck/repos/innodat/agriplatform/platform/docs/architecture/contracts/scaffold-environment-and-generation.md'
---

<frozen-after-approval reason="standing user approval for bounded shared ENV delivery">

## Intent

**Problem:** The exact pinned PostgreSQL CLI profile and immutable image selection are validated, but there is no closed Docker API execution input binding those facts. Future execution must not forward ambient variables or arbitrary Docker options.

**Approach:** Construct and validate one fixed in-memory API1.48 PostgreSQL create request through existing create_profile/startup tooling, exercised at the existing refused-create boundary. Emit only a safe construction fact.

## Boundaries & Constraints

**Always:** Validate original profile, qualified child selection and current network/volume evidence first; preserve caller inputs and owner custody. Request uses selected child digest, exact run database name/network/volume/labels/port, four existing public synthetic container env values, exact bootstrap bytes, health/restart/aliases. Explicit linux/amd64 platform and127.0.0.1 HostIp tighten the constrained ENV profile; do not claim byte-identical CLI serialization. Keep TypeScript7.0.2/all approved pins, runtime_ready=false and existing guards.

**Never:** Dispatch/create/start containers, SQL, image pulls, secret provisioning, infrastructure/deploy/account/access changes; no new generic client/parser/service/generator. Do not expand real Docker POST allowlist. Do not save/hash/emit request body, env or bootstrap as observed runtime evidence. KDG fingerprint keys and bootstrap semantic/secret/freshness/lifecycle qualification remain open. Preserve concurrent Leave/PtS work and accepted ADRs.

## I/O & Edge-Case Matrix

| Scenario | Input/state | Expected behavior | Failure |
| --- | --- | --- | --- |
| Valid selected profile | Exact argv/env and qualified fixtures | Exact detached method/path/body; safe fact; create still refused | none |
| Invalid source | Changed/missing argv/env/routing, image/network/volume | Refuse before construction fact | safe established startup code |
| Ambient canary | Unrelated inherited secret variables | Four approved env names only; no canary in request/output/artifacts | no disclosure |
| Corrupt construction | Extra/missing/changed nested request fields or wrong primitive types | Boundary refuses before proof fact | safe startup refusal |
| Custody | Constructor mutates caller argv/env/fixture; returned tree later mutated | Reject mutation; no shared mutable state | no positive event |
| Dispatch attempt | Constructed create route sent to existing transport | Rejected before socket access | docker_request_invalid |

</frozen-after-approval>

## Code Map

- `platform/deployment/create_profile.py`: exact validate/request/environment authority; add closed request constructor and validator, no generic argv parsing. Private literal body builder may serve constructor/validator; tests use independent full oracle.
- `platform/deployment/startup.py`: immutable_first_create and fixture_command validate source and selected request before safe facts. Integrate constructor after immutable selection; independently validate returned request and original input custody before postgres_create event. No body enters fixture/events.json.
- `platform/deployment/tests/create_profile_fixtures.py`, `test_create_profile.py`, `test_startup_adapter.py`: existing independent inputs/expected facts and process proof; update exact event assertions, retain all refusal/lifecycle checks. Add focused execution-input tests here or adjacent test module.
- `platform/deployment/tests/qualify_startup.py`: existing public private-process qualification entry; add one corrupted-request control that validates baseline before injection and proves rejection; preserve other controls.
- `fixtures/supabase-pg17-profile.md` under deployment: document mapping/limits with pinned primary DockerCLI28 opts.go, Moby28 client/container_create.go and docs/api/v1.48.yaml references. Existing source bindings already include profile/create/startup/qualifier; update SOURCES/FILES only if adding authority source.

## Tasks & Acceptance

- [x] Add acceptance failure for missing create-request proof; send root exact RED command and WAIT before production changes.
- [x] Implement exact closed request and boundary validation; cover every matrix row with independent expected request and nested tamper/type/custody tests.
- [x] Extend existing public qualifier negative control and safe facts; preserve exact prerequisite/lifecycle event sequences and no dispatch.
- [x] Update profile authority mapping; root owns runbook/evidence/next-session/memlog and final scoped local commit.

**Acceptance:** Given the validated selected profile, when the existing boundary runs, then a fully checked execution request is constructed in memory and only safe proof facts are retained. Given malformed construction or inputs, when that boundary runs, then no positive proof is emitted and no daemon operation occurs.

## Implementation Notes

No intent gaps or irreversible actions; standing approval covers this scope. Root runs socket/port tests serially outside sandbox; implementer sends commands, never requests escalation, and waits for RED. Root handles frozen-source qualification, review, evidence and commit; implementer owns code/tests/profile mapping only. Use fixed POST path name plus platform query, flat Config fields beside HostConfig/NetworkingConfig. Exact four Env values; health durations in nanoseconds; named volume Binds; three CLI labels; explicit loopback; network endpoints aliases db/db.supabase.internal. No enclosing Config field or arbitrary overrides.

## Spec Change Log

## Review Triage Log

| ID | Verdict | Evidence / route |
| --- | --- | --- |
| B1 | medium | Coherent fixture/argv changes bypass target-port typing at direct boundary; add integer/range validation and refusal tests (patch). |
| B2 | medium | invalid-create-request treats constructor/first-validation unsafe_create as intended injected rejection; distinguish baseline failure before corruption (patch). |
| B3 | medium | inherited=dict(environment) shares unrelated mutable values, so matching mutation of detached request env and caller can alter snapshot too; deep snapshot and nested custody test (patch). |
| B4 | low | selected_facts/create_facts return new construction claim before request validation; emit actual claim only after validation, build expected attestation explicitly at expected-event callsites (direct patch). |
| B5 | false | Current API and CLI fixed mappings agree and independent complete oracles/pinned CLI proof lock both. No current mapping drift or failing concrete input was identified; hypothetical future version edits do not establish a present defect. No generic profile refactor. |
| B6 | medium | Initial review snapshot evidence had RED/impacts only; root has added focused GREEN/matrix and completes public/regression evidence before closure (documentation patch). |
| E1 | medium | Same port defect as B1: bool/out-of-range fixture plus matching argv can emit invalid binding proof (same patch after individual verdict). |

Verification reviewer returned no gaps. B1/E1 share the port cause; other retained findings are separate patches. No intent gap, public execution surface or new state required.

## Verification

Smallest acceptance RED then focused profile/request/startup suites GREEN; matrix audit and independent review. Fresh source-bound prepare/toolchain/images and focused public startup/profile/new-control/lifecycle proof; retained thirteen files unchanged. Full deployment unittest suite, syntax/whitespace/local links and read-only up refusal. Record requirement-to-test and scaffold/UI/context/docs/ADR impacts. Upstream freshness checks see a pre-acquired volume as existing and may skip fresh setup; this known remaining integration gate is not solved by request construction.

Observed acceptance RED before implementation. Final focused profile17 in14.111s, startup38 in13.046s and lifecycle13 in36.222s PASS outside sandbox. Matrix audit: full independent oracle/detachment (valid); prior operand/env plus selected child/network/volume guards (invalid source); ambient canary exclusion; every-node missing/extra/type/value plus boundary constructor mutation; strict recursive custody; existing transport pre-socket rejection. Root owns final qualification/evidence.

Review fixes: observed four-test/twelve-failure RED before patches; port typing/range, negative-control baseline distinction, deep environment custody and post-validation-only attestation now covered. Final focused profile21 in18.898s/startup38 in7.052s/lifecycle13 in31.503s PASS. Six finding instances fixed, one disproved, none deferred. Sources frozen for fresh 43033cc0-d1af-4231-94db-25bd4b35e09c qualification.

Final qualification: fresh 43033cc0-d1af-4231-94db-25bd4b35e09c prepare/toolchain/images PASS; six focused public CLI checks PASS; thirteen retained files/source snapshots unchanged. Record SHA256612519a4feb7ec41c8198a6bc2105e2f2110d45ed12584e883ea07f473f86de8. Full 397 tests in182.029s PASS; real up exit2 docker_28_required/runtime_ready=false. Syntax/whitespace/local links PASS. Root runbook/evidence/navigation/memlog and five impacts complete. Six finding instances fixed, one disproved, none deferred. No real runtime/dependent owner work or concurrent document edits.
