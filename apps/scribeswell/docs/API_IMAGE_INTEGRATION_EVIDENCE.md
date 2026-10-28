# Scribeswell Studies API image qualification

The app-owned `tests/studies_api_image_fixture.py` extends the frozen Access
consumer qualifier. It builds the shipped Scribeswell Dockerfile in a new private
context containing every shipped COPY input and the three packaging files. Access
preparation still uses the complete reviewed Identity0026/Access0019 archive, its
original qualification and pinned offline toolchain. Original owner archives,
proofs and the live runtime bundle remain read-only inputs.

The repair adds `data/reference-catalogue` to the API Dockerfile and context
allowlist, and its required JSON to the generic deployment artifact smoke. The
parser requires that file at import time when Studies is enabled. Application
behavior, production opt-in refusal, authorization and TLS validation are unchanged.

## Observed failure and focused checks — 2026-10-28

Before repair, the focused COPY replay really imported `passage_references` and
failed with `FileNotFoundError` for the missing catalogue. The smoke-artifact check
also failed: **2 failed in 0.74s**. The first diagnostic against retained historical
image `sha256:5cb67acc71d0eea7696a6f12a0cea9cf1e4ebaf582e457f9cf15c757a977efca`
found the module itself absent; that old image was insufficient to establish the
current packaging defect.

A normal build of the unchanged current Dockerfile succeeded as
`sha256:4b8f71209932056aca160516f1b83c79334739eb3be237f59cda778a06722fe1`.
An actual read-only, network-disabled import from that image then failed with
`FileNotFoundError` for
`/app/apps/scribeswell/data/reference-catalogue/catalogue.json`, exit1. The build
resolved the existing Python3.12 base and unpinned requirements normally; it did not
establish a frozen application dependency baseline.

```sh
docker build --pull=false -t scribeswell-api-red-20261028 \
  -f apps/scribeswell/deployment/Dockerfile .
docker run --rm --read-only --network none --cap-drop ALL \
  --security-opt no-new-privileges --entrypoint python \
  scribeswell-api-red-20261028 -B -c \
  "import sys; sys.path.insert(0,'apps/scribeswell/backend'); import passage_references"
```

`P` below is `apps/scribeswell/.local/owner-integration-20261027/python/bin/python`
(Python3.12.3 controller). The repaired initial focused suite passed **115 tests in
1.20s**. Expanded API boundary checks passed **8 tests in0.88s**, without skips.

```sh
P -B -m pytest apps/scribeswell/tests/test_studies_api_image.py \
  apps/scribeswell/tests/test_studies_frozen_runtime.py \
  apps/scribeswell/tests/test_studies_readiness_integration.py \
  apps/scribeswell/tests/test_studies_signup.py -q
python3 tools/py/run_compose_supabase.py --check-only
```

The expanded affected suite, including `platform/deployment/tests/test_docker_gate.py`,
passed **139 tests in2.01s**, without skips. Its first sandbox attempt passed132
and failed seven deployment socket-reservation cases with `PermissionError`; the
same suite passed with authorized local socket access. Image extra-file, new/changed/
removed packaging input, symlink, context-membership and installed-dependency drift
checks refuse qualification.

Composition check-only passed15 migrations without writes. Root wrappers were not
used. Unit checks establish fixture control flow and packaging membership; actual
image, provider, TLS, browser and SQL acceptance requires the native run below.

## Retained execution attempts

Fresh run `e1a7593b-a8e6-4ad0-8017-5b168426c74e` built the repaired app image and
frozen Access image and passed all three inherited invalid packaging builds. It
then failed during safe base metadata inspection because the Python image omits
the optional Docker `Config.User` key. This is failed qualification evidence, not a
consumer pass. Inspection now uses Docker's optional map lookup. No app/Access
runtime containers had launched; native fixture stop exited0. Private proof and
context remain at `/tmp/scribeswell-api-image-e1a7593b` and
`/tmp/scribeswell-api-context-e1a7593b`. The unchanged-image RED record is retained
at `/tmp/scribeswell-api-image-red-20261028.json`.

Fresh run `cac010b6-8925-4077-9f6f-5ef2d91f7055` was deliberately interrupted
through the controller's SIGTERM cleanup handler after inspection identified that
runtime `/tmp` tmpfs hides the build-stage requirements copy. Controller exit130,
all launched exact containers and the native fixture stopped normally. The probe
now hashes the identical packaged requirements under `/app`, preserving tmpfs and
the shipped command. The actual probe has a semantic regression for hidden staging
files. Its private proof/context remain under the corresponding `cac010b6` paths.

Fresh run `3cb78e23-568b-42ad-bef2-2d3301977151` passed the real browser44.811s
(runner46.933s), disabled authority4.712s (runner5.723s), all15 default-image startup
refusals and exact image filesystem/hardening checks. It then failed before signup
because the qualification helper incorrectly required a resident private SQL pool.
Studies uses short-lived connections and closes them after each transaction. Both
roles had independently established TLS during preparation. The repaired image
probe now uses each actual restricted runtime URL for a bounded read-only connection
and own-session TLS observation, retaining resident sessions separately. A regression
models an absent private resident connection and still requires both observed runtime
roles. **17 API boundary tests passed in0.99s**. All17 exact containers in the failed
run stopped normally (Access/API exit0, no OOM), and exact fixture stop exited0.
Private proof/context remain under the corresponding `3cb78e23` paths.

Fresh run `78519465-705e-4c22-8af4-e0bca6fb4c8c` completed all original browser
business/SQL stages through study deletion but timed out at90.044s in the inherited
privacy completion observer (`studies-owner-privacy.cjs:16`), runner91.611s. Its
safe reporter does not distinguish leaked/incomplete/pending-response causes; none
is claimed. No privacy success, disabled-authority or signup pass is inferred.
All17 exact containers stopped normally, exact fixture stop exited0. The independent
parent live probe in this failed run did establish UID10001, exact main/config/
catalogue hashes, no migration/provider-service authority and actual TLSv1.3 for
both restricted runtime URLs. That partial proof is retained without relabelling the
run as successful. The next attempt uses unchanged source, assertions and timeouts.

Before review, the parent's affected API/frozen/readiness/signup/direct-database/registry-auth
suite passed **145 tests in14.14s**, no skips, with one existing Starlette deprecation
warning. Its initial sandbox-only attempt stalled in direct-database TestClient;
the exact parent process was interrupted and then terminated (exit143), followed
by the authorized unchanged successful repeat. That did not interrupt the native
fixture. No broader suite pass is claimed.

Superseded pre-review success `eff62b26-3430-4ea1-a1c4-f3952d02e896` passed its
original browser/privacy, disabled authority, signup/expiry and24 SQL checkpoints.
It does not qualify the subsequent COPY-directory-symlink fix. Its original safe
JSON, fixture, tests and parent helper remain under
`/tmp/scribeswell-api-image-eff62b26` as `superseded-safe-evidence.json` and the three
`pre-review-*` files. The current safe JSON records their exact paths and hashes;
it does not duplicate the old JSON.

## Review fix and final focused verification

All three reviews completed: blind and verification found no issues; edge review
found one boundary defect. `packaged_sources` followed a top-level COPY directory
symlink before inspecting children, allowing external directory contents into its
source inventory. The qualifier now rejects the source symlink before `is_dir()`/
`rglob()`. Runtime code, image packaging and all privacy assertions/timeouts are
unchanged.

The top-level `backend -> external directory` regression first failed **1 test,
17 deselected in0.60s**. After the one-line guard, focused inventory checks passed
**3 tests,15 deselected in0.61s**. The parent then passed **146 affected tests in6.87s**,
without skips, with one existing Starlette deprecation warning. It repeated the
complete native qualification on the fixed source below.

## Successful current default-image qualification

Final review-fixed run `56ec83ff-a9e3-4ad0-a0b2-9374c0d853a7` completed **exit0,
without skips**. Original browser/enrollment/account-isolation/autosave/privacy
passed47.074s (runner49.35967s), disabled authority6.839s (runner7.884503s), and genuine
signup/local-mail/confirmation/enrollment/consumed-link/elapsed-expired-link
passed135.648s (runner136.827379s). All24 independent SQL checkpoints passed. Actual
OTP elapsed122.000329s against the unchanged120-second provider limit. The preceding
privacy failure remains unexplained. Privacy assertions/timeouts remain unchanged;
this final success does not diagnose that earlier failure or erase its evidence.

```sh
P -B apps/scribeswell/tools/py/qualify_studies_api_image.py \
  --run-id 56ec83ff-a9e3-4ad0-a0b2-9374c0d853a7 \
  --supabase /home/ck/repos/innodat/agriplatform/platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/supabase/supabase \
  --proof /tmp/scribeswell-api-image-review-56ec83ff \
  --source-root /tmp/studies-current-deb424b \
  --qualification /tmp/studies-current-native-20261027-review/current/qualification.json \
  --context /tmp/scribeswell-api-context-review-56ec83ff \
  --python /home/ck/repos/innodat/agriplatform/platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/python/bin/python3.15 \
  --uv /home/ck/repos/innodat/agriplatform/platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/uv/uv \
  --cache /home/ck/repos/innodat/agriplatform/platform/deployment/.local/python-baseline-qualification/cache
```

The qualified API image is
`sha256:2f3d23b6a3577c580e5935082b4f31da8089c4ad3d38d89ac66879f5ee89f4e7`;
resolved Python3.12.14 base is
`sha256:febd0be41adb897a0ab8f1f1c693d8912669ea60c4940e076e9946b60e210ef0`.
Its base rootfs layers match the image prefix. The exact60 packaged app files,
36 installed distributions and2,514 dependency files (2,927 site-packages entries)
were recorded. A final independent image probe matched every initial app/dependency
observation after signup. These installed dependencies qualify this image only;
requirements remain unpinned.

The separately built frozen Access image is
`sha256:792933a8b3678b78657588e230e4f14dbbfe0e44909e616b56e1f9cf25448eba`.
Its14 runtime modules and1,145 dependency files match frozen package provenance.
The fresh owner-prepared artifact SHA256 is
`b90b4fa7551032cae224611743165b5592a4787a46776a0330a1ea81a608a851`.
All three invalid Access packaging builds, ten Access startup refusals and five
app authority/production refusals passed. No existing readiness artifact was reused.

The current parent audit `parent-independent-container-inspection.json`
revalidated509 unique source/proof/tool files, all190 original
owner qualification inputs and all5,622 retained live-bundle entries. Initial/final
source inventories agree. All17 exact app/Access containers stopped normally:
15 intended refusal exit1, successful Access/API exit0, no OOM or forced termination.
All21 owned process groups stopped normally, exact native fixture stop exited0,
no exact fixture containers or declared-port listeners remained, and all nine
SO_REUSEADDR binds succeeded. Exclusive immediate rebinding is not claimed.

The parent independently probed the live final image's UID10001, main/config/
catalogue bytes, absent migration/provider-service authority and both actual
restricted runtime URLs over TLSv1.3/TLS_AES_256_GCM_SHA384. Its current `parent-final-api-inspection.json`
audit checked11,683 entries, all200 recursive owner modules,60 app files/2,927
dependency entries,24 SQL checkpoints,17 stops and the fresh artifact binding.
The retained original owner qualification SHA256 remains
`7fee233970fd6461c92515dbba1dd44e0c98c8d0533cdbc3c1a262a9e9be1e00`.

[Sanitized evidence](evidence/api-image-integration-20261028.json) records exact
commands, source/image/base/dependency/proof hashes, safe TLS/runtime/shutdown
observations and every failed/interrupted attempt. Private service/provider keys,
credential URLs, mail and confirmation links remain excluded; sentinel and credential
URL scans passed across current, superseded and failed-attempt proofs (15 distinct
private sentinels/status values checked). Private proofs, raw logs and contexts remain retained at their
explicit create-only paths.

## Qualification boundaries

App startup uses the unchanged shipped CMD as UID10001, a read-only root, dropped
capabilities, no-new-privileges, bounded tmpfs/PIDs/memory/CPU, the fresh fixture
bridge and a loopback published API port. Only restricted app URLs and the genuine
Access service capability reach the app. Migration credentials and provider service
keys are absent from successful runtime. Negative default-image startup cases
exercise both wrong database roles, both forbidden provider keys and the preserved
production Studies guard. The ten inherited Access readiness refusals remain.

The independent live probe compares every `/app` file and directory against
packaged inputs, checks the copied requirements digest, records installed dependency
versions and every site-packages entry, and verifies installed bytes again after
signup/expiry. These observations bind one immutable image ID; the application's
unpinned requirements do **not** qualify a frozen dependency baseline. The exact
base image ID, rootfs layers, default command and runtime restrictions are retained.

Both restricted app SQL roles must connect with `sslmode=require` and prove their
own connection in `pg_stat_ssl`; the independent running-image probe uses both actual runtime environment URLs,
opens bounded read-only connections and observes each own session in `pg_stat_ssl`.
Resident sessions are recorded separately; Studies deliberately closes each private
transaction connection, so no persistent private pool is required.
If the exact newly owned disposable database lacks TLS, the fixture installs a
one-day synthetic certificate there and reloads PostgreSQL. No validator, shared
host configuration, historical database or production environment is changed.

Success and failure retain exact container identities, safe exit/OOM/forced
observations and private log digests. App and Access containers are stopped before
the exact native fixture; fixture cleanup is attempted even after container cleanup
failure. A stopped Docker client is never termination evidence.

## Requirement-to-test mapping

| Requirement | Evidence |
| --- | --- |
| Missing catalogue observed before repair | Actual parser import in replayed shipped COPY inputs and the unchanged current Docker image; retained RED image/digest |
| Default shipped API includes catalogue | COPY replay plus generic smoke-artifact/context assertions; independent live exact `/app` inventory |
| Preserve owner contract and consumer coverage | Inheritance identity test; fresh complete archived owner preparation, three invalid builds, ten startup refusals and inherited browser/signup/privacy/24 SQL checkpoints |
| Restricted roles and production guard | Both app migration-role negatives, both forbidden provider-key negatives and production opt-in negative; intended configuration markers required |
| Source/artifact drift refuses | New/changed/removed file, top-level/nested symlink, context extra-file, unexpected image file and dependency-drift checks; initial/final complete packaged input inventories |
| Actual runtime isolation and provenance | Independent UID/default command/image ID, filesystem/dependency byte inventories and selected safe Docker hardening/network/loopback/tmpfs observations |
| TLS remains mandatory | Both restricted app roles independently query their own `pg_stat_ssl`; separate in-image read-only observations use both actual runtime URLs; resident sessions are recorded without assuming a private pool |
| Exact shutdown and failure evidence | Inherited stop/kill/log-failure regressions; exact container state/exit/OOM and process-group observations plus native fixture stop on completion/interruption/failure |

## Remaining gates and impact

Actual environment release/recovery, production signup/provider and external SMTP,
physical-device acceptance, sharing/recipient contracts and Notification remain
separate gates. Studies remains refused under `APP_ENV=production`. Identity0027
and concurrent owner work are not adopted. This task changes packaging and app-owned
qualification/documentation only; no scaffold, shared UI, agent-context, schema,
accepted ADR, generated spec or dependency baseline changes.

## Bounded production-capable candidate — 2026-10-28

The production-capable follow-up changes the API image identity. Parent built and
inspected `sha256:71a599b4054c7b1e3b193369f87c4f24b719eafdbfb2a335ac3f99a49ea8f43c`;
[exact independent image observations](evidence/bounded-studies-rollout-20261028/parent-image.json)
retain all60 packaged app-file hashes, actual default-command production-enabled
startup (health200, anonymous private401, enrollment403 and unavailable Access503),
and production-disabled startup (health200 and private404). Both exact local
containers ran as UID10001 with read-only root/network-none/cap-drop/no-new-privileges,
stopped normally with exit0/no OOM and were removed. Earlier harness failures remain
retained in the private proof directory.

These network-isolated checks establish candidate startup and packaging only. They
exercise no live Access/provider request or DB connection and therefore establish
no TLS/write/owner-readiness proof. The old development-mode integration cannot be
relabeled as this new production image's end-to-end qualification. There is no
published RepoDigest; the rollout inspector/gate refuses a local config image ID
as a production registry binding. See [the runbook](BOUNDED_STUDIES_ROLLOUT.md) for
remaining target inventory, current owner preparation, controlled migration and
separately approved activation/recovery verification.
