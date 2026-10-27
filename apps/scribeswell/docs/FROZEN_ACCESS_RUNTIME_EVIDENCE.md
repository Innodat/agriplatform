# Frozen Access runtime consumer qualification

The app-owned driver qualifies a separate frozen Access Python 3.15 image against
the reviewed Identity0026/Access0019 archive and the existing real Scribeswell
browser/signup/local-mail/SQL fixture. It consumes the adopted version 2 readiness
contract without changing owner code, runtime dependencies or the default image
command. It does not activate an environment or qualify the complete Scribeswell
production image.

`tests/studies_frozen_runtime_fixture.py` extends the existing default-startup
consumer qualifier. Preparation and protected owner operations run from the full
qualified archive. Packaging uses that archive's unchanged offline packager,
frozen lock, pinned Python 3.15.0 and uv 0.13.1. A create-only context receives the
new bundle; the original archive, its 190 qualified inputs and retained qualification,
and the live runtime bundle remain read-only inputs.

Runtime receives the three restricted owner URLs, real provider settings, service
key and freshly prepared executor-bound artifact. Private 0600 env files carry
single-line settings. Docker `--env STUDIES_READINESS_JSON` passes only the name in
argv and inherits the genuine artifact verbatim from its process environment,
including the owner's trailing newline. No entrypoint or default-command override
is used. Runtime has no migration credentials; the intentional wrong-role negative
case is separate.

The image runs as 65532:65532 with a read-only root, ALL capabilities dropped,
no-new-privileges, bounded tmpfs, 64 PIDs, 256 MiB memory and one CPU. It uses only
the new fixture's Docker network and publishes Access on loopback8193. Separate
default-image containers exercise all ten readiness refusals. Cleanup observes
exact container IDs, retains stopped containers/logs and stops the native fixture
even if container cleanup fails. Killing a client is never treated as container
termination.

## Executed checks — 2026-10-27

`P` is `apps/scribeswell/.local/owner-integration-20261027/python/bin/python`
(Python 3.12.3, the fixture controller only). Access itself runs the frozen
Python 3.15.0 interpreter inside the image. Python commands use `-B`.

Before implementation, the focused acceptance file failed collection because the
new qualifier did not exist: **1 collection error in 0.57s**. Its first implemented
boundary checks passed **12 tests in 0.59s**. The first actual image run then
exposed the genuine readiness artifact's terminal newline, which Docker env-file
format cannot carry. A focused transport test was added first and failed
**1 failed/12 passed in 0.63s**; the repair preserves the complete value through
Docker's name-only environment inheritance. The helper and full launch tests
cover exact value preservation and absence of credentials/artifact values in argv.

```sh
P -B -m pytest apps/scribeswell/tests/test_studies_frozen_runtime.py \
  apps/scribeswell/tests/test_studies_readiness_integration.py \
  apps/scribeswell/tests/test_studies_signup.py -q
```

The pre-review repaired focused suite passed **106 tests in 0.88s**, without skips. These
helper tests alone do not establish real provider, image or browser proof.

```sh
P -B -m pytest /tmp/studies-current-deb424b/services/access/tests/test_deployment_package.py -q
python3 tools/py/run_compose_supabase.py --check-only
```

The archived packager suite passed **10 tests in 0.12s**, without skips. Composition
check-only passed15 migrations, without writes. Root build/test wrappers were not
used.

The initial sandbox attempt `46073a2c-3f48-4dd0-a138-f737bf01d7ef` was refused by
local socket permissions before fixture creation; its safe failure record remains
at `/tmp/scribeswell-frozen-access-46073a2c`. The first authorized native attempt
`d9572886-c18c-4a2c-a4e3-f62188b266e4` built the real image and refused all three
invalid packaging cases, then refused two startup variants before the newline
transport failure. Its two exact containers stopped normally, its 14 owned process
stops were confirmed and the exact fixture stop exited0. That attempt is failed
evidence, not consumer qualification. Its private proof/context remain retained.

Review found three qualification-boundary gaps. Invalid packaging builds now require
the actual `access_runtime_verification_failed` marker from combined stdout/stderr,
so unrelated infrastructure failures refuse qualification. Cleanup records inspected
exit/OOM/forced evidence before optional log retrieval and retains it if logs fail.
Additional cases cover running-after-stop, kill success and still-running-after-kill
with exact IDs, retained resources and serialized unconfirmed shutdown. New tests
first reproduced **4 failures/17 passes in0.65s**; the repaired focused file passed
**21 tests in0.67s**. The parent repeated the affected combined suite: **113 passed
in0.91s**, no skips. No runtime owner code or contract changed.

The final review-fixed native command uses explicit create-only paths and the retained approved
inputs (the long toolchain prefix is shown verbatim):

```sh
P -B apps/scribeswell/tools/py/qualify_studies_frozen_runtime.py \
  --run-id 9d74848b-c1f5-4107-a07f-13bcfc1d9cb7 \
  --supabase /home/ck/repos/innodat/agriplatform/platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/supabase/supabase \
  --proof /tmp/scribeswell-frozen-access-review-9d74848b \
  --source-root /tmp/studies-current-deb424b \
  --qualification /tmp/studies-current-native-20261027-review/current/qualification.json \
  --context /tmp/scribeswell-frozen-context-review-9d74848b \
  --python /home/ck/repos/innodat/agriplatform/platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/python/bin/python3.15 \
  --uv /home/ck/repos/innodat/agriplatform/platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/uv/uv \
  --cache /home/ck/repos/innodat/agriplatform/platform/deployment/.local/python-baseline-qualification/cache
```

**Exit0, without skips.** Original browser passed30.499s (runner32.139s), disabled
authority passed4.123s (runner4.915s), and genuine signup/local-mail passed120.667s
(runner121.298s). All24 independent SQL checkpoints passed. Confirmation granted no
Studies authority; explicit enrollment, consumed-link rejection and elapsed-expired
link rejection passed. Actual OTP elapsed time was122.000231s against the unchanged
120-second provider limit. Ten default-image configuration refusals and three actual
packaging build refusals passed.

The successful image is
`sha256:8e57949ca58d596dd9eb45f1645d0b396e86c76b60d6819ae1a6b751ee23d4bd`;
bundle provenance SHA256 is
`5586e93bc2e0879f3ff5ee855335e97ec4e6d7b9b4ce2e56fa8997efafb5eca9`.
The genuine fresh artifact SHA256 is
`8b84adf4777d53773dde2679d9c84b81ac3aabb2ad87b226bb9f04a087b15fae`.
An independent live-container probe matched those exact artifact bytes, including
the terminal newline. Runtime reported Python3.15.0, UID65532, no pytest or migration
configuration, exactly14 `/srv` modules and all1,145 dependency files matching frozen
provenance. Safe Docker fields confirmed the unchanged default command and declared
runtime restrictions.

Independent final inspection (`P -B /tmp/scribeswell-frozen-final-inspect-9d74848b.py`)
validated495 unique source/proof/tool files, the original190 qualified owner inputs,
all200 recursive owner module paths/digests, all5,622 original live-bundle entries,
the packaged payload and equal initial/final inventories. All11 exact containers
were stopped: ten expected refusal exit1, successful API exit0, no OOM or forced
termination. All21 owned process stops were normal and confirmed; exact fixture stop
exited0. Final inspection found no listeners on the declared fixture ports and all
nine SO_REUSEADDR binds succeeded. Exclusive immediate rebinding is not claimed.

The earlier successful run `4fecf04d-f5c4-4e6e-9286-5063365708eb` remains superseded
pre-review history at `/tmp/scribeswell-frozen-access-4fecf04d`. Its original safe
JSON was retained unchanged as `superseded-safe-evidence.json` there (SHA256
`1141434c97bce167722af334fddefc5bba0c2fdc2120bc646f59b5485e470774`). It passed its original browser/signup/SQL/image scope
but does not certify the review-fixed fixture/tests. Its initial exclusive bind
inspection saw TCP close-state EADDRINUSE before listener absence/reuse binds
were confirmed; that historical observation remains in the retained report.

The parent independently ran `/tmp/scribeswell-frozen-parent-audit-review.py`:11,617
hashes/entries,14 runtime modules,1,145 dependency files,24 SQL checkpoints,
11 containers and21 process groups checked successfully. Its focused repetition
passed113 tests in0.91s. Its separate exact API-container inspection confirmed
exit0/runningfalse/OOMfalse, and its listener inspection agreed. The original owner
qualification SHA256 remains
`7fee233970fd6461c92515dbba1dd44e0c98c8d0533cdbc3c1a262a9e9be1e00`.

[Sanitized evidence](evidence/frozen-access-runtime-20261027.json) retains the exact
command, source/image/artifact hashes, safe runtime and shutdown observations, failed
attempt history and retained private-proof/log digests. Service-key/provider-key and
credential URL sentinels were checked absent before publication. Private credentials,
mail bodies, confirmation links and raw environment values stay in local0600 proofs.

## Requirement-to-test mapping

| Requirement | Oracle |
| --- | --- |
| Frozen source and tool custody | Independent initial/final app, recursive owner, retained qualification/proof, package-input, binary and live-bundle membership/digest inventories; archive owner validation before packaging |
| Offline pinned packaging | Actual archive packager with explicit Python/uv/cache and frozen offline sync; pinned carrier Docker build with network disabled |
| Wrong bundle refuses | Actual verified-stage Docker builds reject stale lock, extra importable owner payload and altered packaged main despite recomputed self-inventory; focused exact14 membership/digest tests |
| Genuine default startup | Fresh owner preparation, exact executor/runtime hashes and verbatim environment; unchanged image CMD and real app consumer |
| Unsafe readiness refuses | Ten actual default-image startups with missing/malformed artifact, each absent role URL, old version, later head, stale sources, wrong pair and migration role; fixed configuration-refusal reason required |
| Runtime provenance/isolation | In-container version/UID/pytest/migration-variable/read-only checks; exact14 `/srv` sources and every installed dependency file compared to package provenance; safe selected Docker restriction fields |
| Consumer and signup behavior | Inherited browser, independent SQL/account-isolation/disabled-authority/privacy and real local-mail signup/confirmation/consumed/elapsed-expired-link oracles |
| Exact shutdown on completion/failure | Independent container ID/state/exit/OOM observations, bounded stop/kill reporting, retained failures and fixture stop even after container-stop failure |

## Remaining gates and impact

Actual coordinated environment release/recovery, production signup/provider and
external SMTP delivery, physical iOS/Android acceptance, sharing/recipient contracts
and Notification remain separate gates. This qualification does not adopt later
Identity0027 work or qualify the mixed live owner worktree. Production stays disabled.

Scaffold, shared UI, agent context and ADR impact: none. Documentation: this report,
sanitized evidence and current owner/final handoffs. No owner contract, accepted
migration, dependency baseline, product behavior or generated artifact changes.
