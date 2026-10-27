# Default Access startup consumer integration

This app-owned qualification consumes the published version 2 readiness contract for
exactly Identity0026/Access0019. It keeps the historical injected integration and
owner evidence intact. It does not qualify a later owner head or the mixed live
owner worktree. Production Studies stays disabled.

The new `tests/studies_readiness_integration_fixture.py` subclasses the existing
`SignupQualification`. Original owner browser, independent SQL, account isolation,
privacy, disabled-authority and real local-mail signup oracles are inherited.
Access alone starts from the explicit qualified owner source root with ordinary
`python -m uvicorn main:app` and the published environment. The owner migration
helpers and protected operator commands also run from that source root. The app
backend/frontend stay on current frozen application sources.

Every new fixture creates a new service executor, runs the owner's read-only
`studies_readiness.py` preparation and consumes its exact compact JSON. Migration
credentials are supplied only to preparation; runtime receives the three restricted
roles, live provider settings, service key and `STUDIES_READINESS_JSON`. There is no
database/provider injection or fallback. Independent source inventories bind the
application/driver, owner sources, retained native qualification/proof inputs and
pinned Supabase binary. The original 190-input archive and retained proof are unchanged.

## Commands and results — 2026-10-27

`P` is `apps/scribeswell/.local/owner-integration-20261027/python/bin/python`,
Python 3.12.3. Commands set `PYTHONDONTWRITEBYTECODE=1`. The pinned Supabase binary is
version 2.120.0. A direct sandbox version read initially refused writing telemetry
outside the workspace; repeating with an isolated `SUPABASE_HOME` succeeded.

Acceptance red, before implementation:

```sh
P -m pytest apps/scribeswell/tests/test_studies_readiness_integration.py -q
```

**1 failed in 1.42s**: the existing app fixture used `python -c` with injected
`create_app` database adapters where default `uvicorn main:app` was required.
The passing test subsequently targets the new app consumer.

Focused launch/inheritance/source-freeze and existing mail/privacy helper checks:

```sh
P -m pytest apps/scribeswell/tests/test_studies_readiness_integration.py apps/scribeswell/tests/test_studies_signup.py -q
```

The initial implementation passed **89 tests in 1.11s**. Review then demonstrated
that newly importable owner modules/packages escaped the original freeze. Three
negative PathFinder-backed cases initially failed to refuse late `httpx.py`,
`httpx/__init__.py` and an existing package's new submodule. The repaired driver
re-enumerates recursive Python module/package membership and digests, including
bytecode and extension modules. Its focused test file passed **12 tests in 0.77s**;
the parent's final helper/signup repetition passed **92 tests in 1.01s**, no skips.
These host tests do not establish real provider/mail proof.

Fresh actual qualification:

```sh
P -B apps/scribeswell/tools/py/qualify_studies_readiness_integration.py \
  --run-id bbc64030-9df1-4dc2-a7e2-ab35f7874fd6 \
  --supabase /home/ck/repos/innodat/agriplatform/platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/supabase/supabase \
  --proof /tmp/scribeswell-default-integration-review-bbc64030 \
  --source-root /tmp/studies-current-deb424b \
  --qualification /tmp/studies-current-native-20261027-review/current/qualification.json
```

**Exit 0 on review-fixed source.** The original owner browser passed (case 44.952s,
runner 47.131s), disabled-authority browser passed (case 8.026s, runner 8.892s), and
real signup browser passed (case 121.379s, runner 122.432s). All 24 independent SQL
checkpoints passed, including signup/confirmation without implicit authority,
explicit enrollment, consumed-link rejection and actual elapsed-expiry rejection.
The expiry observation was 122.000218s against the unchanged 120s provider OTP limit.
All ten default-module startup refusals passed.

The new artifact binds the freshly created executor and 14 runtime modules.
Post-shutdown inspection revalidated 486 SHA256 values: 171 current app inputs,
305 selected owner inputs, including all original 190 qualification inputs,
nine retained qualification/proof files and the pinned binary. Initial/final
inventories match. All 31 owned process-group stops were normal and confirmed;
exact fixture wrapper stop exited 0. No forced termination, foreign environment
stop, production activation or later-head qualification is claimed.

Recursive owner module membership (200 files) and all digests match the captured
inventory. The artifact SHA256 is
`37cf4072456c6784ff104ebe97a5cbebb78deba51d0f4edd27c692f818cb927e` and binds a
fresh executor distinct from the first successful run. The sanitized evidence
retains all final safe report/log hashes and exact source inventories.

The first successful run, `b642ef30-d1f2-4b19-b417-bdf7bf469947` at
`/tmp/scribeswell-default-integration-20261027-b642ef30`, is retained as superseded
history with its original 377-hash inventory, artifact SHA256
`9d65b89da2af08e01c35b8490ad3cf698567a31636230128b2b62ac413c0f95e`
and browser/SQL results.
It does not certify the review-fixed driver. Its original independent inspection
command was `P -B /tmp/scribeswell-default-integration-inspect-20261027.py`.

Coordinated private report and host refusal coverage:

```sh
P -m pytest apps/scribeswell/tests/test_personal_notes_release.py platform/deployment/tests/test_host.py -q
```

**47 passed in 3.30s**, no skips. This exercises current strict report parsing,
committed-attribute consumption, stale/wrong/malformed/failed/unknown report refusal,
reconciliation/forward retry and host activation ordering. The parent independently
repeated the helper/signup suite (**89 passed in 0.78s**) and app/host suite
(**47 passed in 3.15s**), both without skips.

The parent also executed the separate fresh actual PostgreSQL17 report suite:

```sh
P -B -m pytest apps/scribeswell/tests/test_studies_migration_report_native.py -q --tb=no --no-summary --disable-warnings
```

The private connection was supplied through `SCRIBESWELL_NOTES_TEST_ADMIN_URL`;
its value is not exported. **6 passed in 8.25s**, runner 9.291s, exit 0, no skips.
All 86 report-suite source hashes agree before, after and with current source.
Safe fixture/results/source files and the actual pytest log have retained SHA256
digests in the sanitized evidence; the private connection file is excluded.

This run is `308d0c3c-f9c1-48b8-8614-8de9dafd85ce`, with PostgreSQL version
`170011`, stopped retained container `scribeswell-consumer-report-308d0c3c-f9c`
(`61a90bea4f9ddfa76776ef8e492a05da577cbcbfb45281344b54479808f9ab94`) and retained
volume `scribeswell-consumer-report-308d0c3c-f9c-data`. Loopback port 32770 was released.
The private proof remains at `/tmp/scribeswell-consumer-pg17-20261027`.

The parent independently validated all 486 app/owner/qualification/binary hashes,
13 retained private-proof digests, the fresh service actor against the old artifact,
unchanged owner qualification, actual 122.000218s expiry and normal shutdown.
Docker inspection of the separate PG17 container confirmed exit code 0, OOM false
and running false; `ss` confirmed no listener on released port 32770. Driver-only
review repairs did not touch the 86 report-suite sources; the separate 47-test
host/report and six-test actual PostgreSQL17 results retain their original scope.
`python3 tools/py/run_compose_supabase.py --check-only` passed for 15 migrations,
without writes. Native worker and host tests do not establish full environment
release/recovery.

Retained private inputs, mail links and credentials stay in the 0600 fixture proof;
they are never copied into repository evidence. Safe command/results and full source
hashes are published in [sanitized evidence](evidence/default-startup-integration-20261027.json).

## Requirement-to-test mapping

| Requirement | Executed oracle |
| --- | --- |
| Fresh qualified owners; exact sources and executor | Owner `validate_qualification` and read-only `prepare`, new executor binding, artifact hash, independent initial/final source inventories |
| Default Access startup without injection | Separate `uvicorn main:app` process from the qualified archive, actual app HTTP/browser enrollment and current checks |
| Missing/stale/partial artifact, wrong role/source | Ten fresh module-import refusals: absent/malformed artifact, each missing role URL, old artifact version, later head, stale runtime sources, wrong owner pair and migration role supplied as runtime |
| Explicit enrollment and isolation | Inherited original browser plus independent SQL snapshots; public/protected pre-enrollment unchanged state, cross-account denial, disabled availability without protected writes |
| Signup/confirmation grants no Studies permission | Inherited real UI signup, selected local Mailpit message and validated link, SQL profile-only/confirmation snapshots, explicit attributed enrollment and study creation |
| Consumed and elapsed-expired links; no secrets | Inherited consumed-link rejection and actual provider sent-time expiry wait without Auth writes, unchanged-state comparisons, existing sentinel/browser privacy checks |
| Truthful private report and unsafe report refusal | Independent app/host report checks (47 passed) and separate actual PostgreSQL17 report suite (6 passed), with 86 unchanged source hashes and no skips |
| Fresh ownership and exact shutdown | Existing immediate port check, wrapper subnet/resource ownership checks, fresh canonical run reservation and bounded exact process/run stop |

## Limits and impact decisions

Actual environment release/recovery rehearsal, production Python 3.15, external
SMTP/delivery and physical-device acceptance remain outstanding. Native worker tests
and mocked host checks do not establish a full environment release or recovery.
Sharing, recipient/invitation resolution and Notification remain separate owner work.

Scaffold: no generator/template or schema change. Shared UI: none. Agent context:
unchanged. Documentation: this evidence, sanitized JSON and current handoffs. ADR:
no decision change; existing owner, authorization, migration and release contracts
are consumed unchanged. Generated canonical specs and foreign working changes are
untouched. Selected implementation model/effort follows the approved dispatch;
actual model/usage/compute elapsed is unavailable. No deployment or production activation.
