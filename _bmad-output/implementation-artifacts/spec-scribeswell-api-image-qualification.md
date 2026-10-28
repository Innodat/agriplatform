---
title: 'Package and qualify the Scribeswell Studies API image'
type: 'bugfix'
created: '2026-10-28'
status: 'done'
baseline_commit: 'c88c753fc46d6d5caf296ef3b2ec87370b7f8dc1'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '/home/ck/repos/innodat/agriplatform/AGENTS.md'
  - '/home/ck/repos/innodat/agriplatform/apps/scribeswell/docs/OWNER_READINESS_HANDOFF.md'
  - '/home/ck/repos/innodat/agriplatform/apps/scribeswell/docs/FROZEN_ACCESS_RUNTIME_EVIDENCE.md'
  - '/home/ck/repos/innodat/agriplatform/platform/docs/development/migration-verification.md'
---

<frozen-after-approval reason="human-owned intent; standing approve-and-continue authorization">

## Intent

**Problem:** Studies imports the offline reference catalogue, but the shipped API Dockerfile omits it. Existing qualified consumers launch Scribeswell on the host, and image health smoke disables Studies, leaving this delivery defect unobserved.

**Approach:** Include the required catalogue and qualify the unchanged default API image on a fresh real-owner fixture alongside frozen Access. Preserve the production opt-in guard and publish truthful image/source/evidence boundaries.

## Boundaries & Constraints

**Always:** Observe the missing-artifact failure before repair. Preserve reviewed Identity0026/Access0019 archive/190 inputs, original bundle/proofs, unrelated working changes and previous evidence. Use fresh synthetic executor/run, default shipped commands, restricted app roles and genuine Access artifact/provider. Keep current TLS/URL validation, nonroot users, loopback-only published ports, bounded hardening and exact confirmed cleanup. Bind complete image inputs and installed dependencies; never expose credential values in argv/logs/repository evidence.

**Never:** Activate production, remove APP_ENV production Studies refusal, adopt Identity0027, relax authorization/TLS, change schemas/ADRs/generated specs, use historical KDG/Leave environments, import another owner's implementation into runtime, push, or claim environment release/recovery, external SMTP/device/sharing acceptance. Do not claim a frozen dependency baseline from the app's currently unpinned requirements.

## I/O & Edge-Case Matrix

| Scenario | State | Expected behavior | Failure handling |
|---|---|---|---|
| Missing catalogue | Current shipped packaging, Studies enabled | Actual import/startup failure observed | Retain safe RED evidence |
| Complete image | Fresh real fixture and included catalogue | Default image passes inherited browser/signup/SQL | Exact cleanup and safe provenance |
| Wrong runtime authority | Migration role or forbidden provider key | Refuse app startup | Assert intended configuration refusal |
| Production opt-in | APP_ENV production plus Studies enabled | Existing activation guard refuses | No bypass |
| Source/artifact drift | Changed/new packaged input or unexpected image file | Qualification refuses | Retain evidence without success claim |
| Cleanup failure | Container stop/kill/log failure | Preserve observed state and attempt remaining cleanup | No false termination claim |

</frozen-after-approval>

## Code Map

- `apps/scribeswell/backend/{main,personal_notes_access,personal_notes_contract,passage_references}.py`: Studies import requires `data/reference-catalogue/catalogue.json`. Keep runtime behavior unchanged.
- `apps/scribeswell/deployment/{Dockerfile,Dockerfile.dockerignore,manifest.json}`: missing catalogue COPY/allowlist/smoke artifact. Existing smoke uses production with Studies disabled.
- `apps/scribeswell/tests/studies_frozen_runtime_fixture.py`: subclass `FrozenRuntimeQualification`; intercept `scribeswell-http`, retain real Access preparation/default image, ten owner refusals, browser/signup/SQL, source freeze and explicit container cleanup.
- `studies_owner_fixture.py`, `studies_signup_fixture.py`, `studies_readiness_integration_fixture.py`: existing fixture network, restricted URLs, synthetic corpus, real Auth/local mail, independent SQL. Extend packaging-input freeze beyond existing inventories.
- `backend/{config,database}.py`: nonloopback database URLs require TLS even in development; production Studies is explicitly refused. Qualify actual fixture TLS with both app roles and `pg_stat_ssl`; provision TLS only on this exact owned disposable DB if needed, without weakening validators.
- Current cached app image `sha256:5cb67acc71d0eea7696a6f12a0cea9cf1e4ebaf582e457f9cf15c757a977efca` and Python3.12.14 base exist; offline rebuild cache is unproven. Try normal shipped build, record actual resolved base/dependencies, retain classified infrastructure failures. No dependency baseline upgrade.
- Existing pinned owner toolchain/cache and `/tmp/studies-current-deb424b`/retained qualification are described in frozen Access evidence. Keep preparation at full archive root.

## Tasks & Acceptance

**Execution:**
- [x] `apps/scribeswell/tests/test_studies_api_image.py` — meaningful RED for missing catalogue, matrix regressions and preserved inheritance.
- [x] `apps/scribeswell/deployment/{Dockerfile,Dockerfile.dockerignore,manifest.json}` — include catalogue and make generic artifact smoke require it.
- [x] `apps/scribeswell/tests/studies_api_image_fixture.py`, `tools/py/qualify_studies_api_image.py` — source-bound create-only app image qualification; freeze packaging/corpus inputs and exact image filesystem; default CMD on fixture bridge, TLS proof, restricted env, retained bounded cleanup; reuse existing full consumer oracles.
- [x] `apps/scribeswell/docs/API_IMAGE_INTEGRATION_EVIDENCE.md`, `docs/evidence/api-image-integration-20261028.json`, owner/final handoffs — actual commands/results/hashes, review fixes and remaining gates.

**Acceptance Criteria:**
- Given the repaired image, when default startup and inherited consumer qualification execute, then real browser/enrollment/account-isolation/disabled-authority/signup/consumed/elapsed-expiry/privacy and24 SQL checkpoints pass without skips.
- Given the running image, when independently probed, then exact packaged code/artifacts, dependency inventory, UID10001/default CMD/read-only restrictions and absence of migration/provider-service authority agree with recorded provenance; both app SQL roles have observed TLS connections.
- Given wrong credentials or production opt-in, when default startup executes, then intended refusal is observed; no successful readiness is claimed.
- Given success or failure, when supervision finishes, then exact app/Access/fixture shutdown is evidenced and original inputs remain unchanged.

## Implementation Notes

Standing user approval covers routine BMAD checkpoints and scoped local commits. No unresolved product intent gaps. Footprint: three packaging files plus app-owned qualification/tests/docs. Native side effects are disposable owned synthetic resources only. Scaffold/shared UI/agent context/ADR: no changes; packaging and evidence documentation updated. Sol High implementation; actual model/usage/timing unknown. Parent owns workflow/review/commit; delegated implementer must not restart skills or commit/push.

## Spec Change Log

## Review Triage Log

| Layer | Finding | Verdict/route | Evidence |
|---|---|---|---|
| Blind | No supported findings | No action | Packaging/lifecycle/probes/cleanup traced;17 API tests passed. |
| Edge | Top-level COPY directory symlink escapes existing symlink refusal | medium / patch | Parent reproduced source-directory link followed by rglob; child files are ordinary paths and accepted as repository sources. Extend existing guard to the COPY source itself, with regression. Current qualified input roots are ordinary directories; prior native success remains historical. |
| Verification | No verification gaps | No action | No additional supported gap. |

## Verification

Run smallest relevant RED before packaging repair, focused image/consumer/signup and affected deployment checks, then fresh actual image consumer qualification. Independently audit source membership/digests, actual container artifact/dependency/TLS/environment/hardening observations and final exact resource shutdown. `python3 tools/py/run_compose_supabase.py --check-only` must remain15 migrations/no writes. No root wrapper verification or production activation.

Parent acceptance/matrix audit: actual pre-repair image import RED verified;145 affected tests passed14.14s/no skips/one existing deprecation warning, unchanged source after final freeze. Final native eff62b26-3430-4ea1-a1c4-f3952d02e896 exit0, browser/privacy/disabled/signup/real expiry122.000334s and24 SQL checkpoints passed. Parent live probe proved actual restricted runtime URLs TLSv1.3, UID10001, required catalogue and absence of migration/provider authority. Parent supplemental final audit11683 hashes/entries plus actual engine/process/port audit509 unique sources190 original owner inputs5622 live-bundle entries60API files2927 dependency entries14Access modules1145 dependencies17 containers21 process groups9 binds/no listeners/no exact fixture containers all passed. All six matrix rows covered by executed tests/native oracles. Earlier failed/interrupted/unknown-privacy outcome retained separately. No product/authorization/TLS/production guard/schema/ADR/generator changes. Delegated Sol High, actual model/usage/compute/wait breakdown unknown.

Review patch: existing source symlink refusal now also checks the COPY source root itself. Regression failed first, then3 focused inventory checks passed. Parent full affected repetition146passed6.87s/no skips/one pre-existing deprecationwarning. Runtime/packaging unchanged. Fresh final review-fixed source run56ec83ff-a9e3-4ad0-a0b2-9374c0d853a7 started with explicit review proof/context paths; pre-review successfuleff62 sources/tests/JSON retained under its private proof as superseded history.

Final review-fixed native56ec83ff-a9e3-4ad0-a0b2-9374c0d853a7 EXIT0 on exact guarded sources. Browser/privacy47.074s, disabled6.839s, signup135.648s; actualOTP122.000329s. Parent current live/final/raw-final-dependency/bundle/source/engine/process/port audits all passed:11683hashes/entries509unique files190original owner5622livebundle60API2927dependency entries14Access modules1145dependencyfiles24SQL17normalcontainers21normalprocessgroups9reusebinds/no listeners/no exactfixturecontainers. Freshartifactb90b4fa7551032cae224611743165b5592a4787a46776a0330a1ea81a608a851; APIimage2f3d23b6a3577c580e5935082b4f31da8089c4ad3d38d89ac66879f5ee89f4e7. One review patch verified, no deferred findings; prior unknown privacy failure remains failed history. All acceptance/matrix tasks verified; final source frozen.

Completion: final safe JSON independently matches all572 private proof digests, current native observations and all packaged/driver sources; credential sentinel scans passed. Source guard patch and146tests fully verified by final native run. Concurrent KDG commit2259592df294cff4293e054f44057476371e1fc9 affects no qualified input and is preserved; original canonical baseline remains unchanged in frontmatter. Ready for scoped local commit, no push/activation.
