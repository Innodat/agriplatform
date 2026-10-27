# Studies readiness on the reviewed Identity0026 / Access0019 pair

The closed v2 readiness contract passed isolated native qualification on
`deb424b0c4d29016917c9df39b540a468ca8e1cf` plus this delivery's changes.
The qualified source tree is `/tmp/studies-current-deb424b`; it is an archive,
not the mixed live working tree. During implementation, unrelated Identity0027,
People setup and packaging changes appeared in the live tree. They were preserved.
They are outside this qualification and make its artifact stale for that live runtime.
No accepted migration, ADR, historical qualification or KDG/Leave fixture was edited.

The [adopted owner interface](../../STUDIES-ENROLLMENT.md#exact-reviewed-current-owner-readiness--2026-10-27)
requires artifact and qualification version2 with exactly Identity0026 / Access0019.
Preparation checks actual owner catalogues, matching enabled service executor rows,
Auth profile hook, app/permission registry and restricted role/table authority.
The source inventory now binds the complete migration/reference chain, pinned legacy
sources and executed fixture dependencies. Runtime hashes cover all14 reviewed
packaged default-app modules. Old/future heads, old artifacts and stale sources refuse.
Duplicate artifact JSON keys now refuse as well.

## Actual verification

The initial acceptance test failed as intended: **1 failed, 2 passed**; the old
policy rejected a v2 artifact for Identity0026 / Access0019. After implementation,
readiness tests passed **6/6**. The original-tree focused Studies/host suite passed
**79 tests** with one Starlette deprecation warning in3.07s; parent independently
observed79 passed/one warning in3.41s, then the final post-patch focused rerun
passed79 tests/one warning in2.96s. The archived Studies, KDG organization check,
capability, Discovery, host and Scribeswell release suite passed **264 tests** with
one warning in10.83s. After review fixes, focused negative-oracle tests passed
**8 tests** in0.21s; parent independently observed8 passed in0.20s. The initial sandbox HTTP-suite attempt hung on local socket
support and was interrupted; the bounded escalated run passed. Root composition
`python3 tools/py/run_compose_supabase.py --check-only` exited0 with no writes.

The final review-fixed native command, run by the parent from the isolated archive, was:

```sh
/home/ck/repos/innodat/agriplatform/apps/scribeswell/.local/owner-integration-20261027/python/bin/python -B services/access/tests/qualify_studies_current.py --run-id c68e27fd-960d-44f1-b773-9493795f7f5a --clean-run-id 5b0441bc-70ac-4e40-9a5c-66daac599d61 --supabase /home/ck/repos/innodat/agriplatform/platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/supabase/supabase --proof /tmp/studies-current-native-20261027-review
```

It exited0 with `studies_current_owner_qualification_passed`. Both new clusters
stopped normally; all retained process termination observations were unforced.
Clean migration asserted no account/actor/grant seeds before fixture provisioning.
The populated fixture retained its prior Identity25 profile while upgrading to26,
then retained Access18 registry/principal data through upgrade to19. Deliberate
postcondition failures wrote exclusive0600 markers only after actual postcondition
verification. Full protected row snapshots matched immediately before/after each
failed migration, before successful retry; explicit retries and repeats succeeded. Access-before-Identity refused. No activation ran on failure.

Eight native proof stages, **190 source hashes**, the qualification digest and the
0600 readiness artifact remain in the private proof directory. The artifact digest
is `200fccce1eef748644daabf22d98642960dc25550027018bc92f120252bf8434`.
The [sanitized retained summary](evidence/studies-current-readiness-20261027.json)
contains exact source/proof hashes, commands/results,13 preparation refusals,
nine startup refusals, SQL counts and actual interpreter/dependency versions.
Private credentials/provider tokens are not copied into this document or summary.
The raw pytest output was observed through the tool session; no raw test logfile
was created. Exact test commands are recorded in the summary.

The unmodified default `create_app()` used environment-created restricted database
connections and real provider checks, with no database/provider injection. An OS
uvicorn process imported `main:app`, returned a six-field200 account decision, then
returned403 after current account verification was removed. Revocation also denied
through the default application after valid preparation. Native authorization stages
retain first-use races, actor-only recovery, adopted/collision/profile denials, SQL
and write-lock deadlines, lost-response same-operation retry, revoked replay and
current Auth changes during observed account/actor locks. The provider/current-Auth
race stage makes a real verified provider call, commits an Auth change, then observes
Identity's current SQL denial in the same native provider database.

Preparation refusal faults cover old/unknown/partial ledgers, disabled/missing/
mismatched principals, non-service/unkeyed actor, missing hook, unsafe role, raw table
privilege and disabled registration. Preparation changed no protected business state;
restoration was explicit fixture work. Independent read-only inspection revalidated
actual heads, executor equality, grant/event attribution and retained source/proof
hashes. Parent independently rechecked all190 source hashes/eight proofs, artifact
qualification digest and both normal-stop results. Final parent inspection also
checked exact0600 marker contents, all six boundary/ten profile refusal classes,
and matching protected-state hashes/counts with the expected `unchanged_from` for
both failed owner migrations. Entire snapshot JSON is intentionally different in
that observation field; protected business values are compared by the native oracle.

## Scope, attempts and limits

The archived baseline contained the Scribeswell target/schema/fixture but its native
wrapper still dispatched only KDG/Leave. The first invocation refused schema matching
before allocating resources. With parent authorization, the snapshot copied exactly
the existing working-tree `platform/deployment/dev.py` and `native_cli.py` fixture
support. Their hashes are retained; original tooling stayed unchanged. Only the
snapshot target's `workspace_root` was adjusted to its archive path.

The first complete native attempt passed clean migration and populated upgrade/
failure/retry/repeat, then its inherited two-account initial observer rejected the
additional retained prior profile. No readiness artifact was emitted. Both runs
stopped; evidence remains at `/tmp/studies-current-native-20261027`. The corrected
populated observer and initial-grant precondition were requalified from scratch with
the successful attempt2 UUIDs (`90f7a893-59c3-4a6e-a487-26b4445a0e6f` and
`725e1355-8cae-4d1c-9cf9-783494b79907`). That successful proof remains retained at
`/tmp/studies-current-native-20261027-attempt2`, superseded by the final review-fixed
run above. No failed observation was relabelled successful.

Review tightened three native oracles: profile/boundary refusals now assert exact
status/error pairs (403 Auth/verification denials versus503 setup/profile refusals);
injected migration failures require a safe private marker proving real postcondition
verification was reached; and full protected row values are compared immediately
before/after each failed migration before retry. The parent reran both new clusters
from scratch with these fixes. The final bundle retains actual refusal classes,
markers and matching before/after protected-state hashes. Earlier private evidence
and resources remain preserved.

The authorized handoff interpreter is **Python3.12.3**, using FastAPI0.136.3,
uvicorn0.49.0, Pydantic2.13.4, SQLAlchemy2.0.52, psycopg3.3.6, Alembic1.19.1,
rfc8785 0.1.4 and httpx0.28.1. This is not the locked production Python3.15 stack.
Production bundle compatibility, coordinated environment release/recovery rehearsal,
and the unrelated Identity0027 delivery remain unqualified here. Native fixture
results do not authorize production activation. Recipient/invitation and Notification
delivery, external SMTP and physical-device acceptance remain separate gates.

Scaffold: no generator change; fixture support remains owner-specific.
Shared UI, agent context and ADRs: unchanged. Documentation: owner interface,
Scribeswell handoff and this evidence. Historical fixtures/evidence: preserved.
