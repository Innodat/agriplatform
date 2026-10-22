# KDG organization permission check — delivery evidence

This item delivers one current organization capability check through the existing
Access SQL and HTTP owner. It does not activate KDG business writes, PtS, Leave,
account/person variants, discovery or target APIs. Standing user approval covers
implementation and isolated synthetic verification only. Schemas and ownership stay
with Identity and Access. Production, real-account/access changes, deployment/pilot,
reset/prune/resource cleanup and push remain excluded.

Baseline: `1da72d2a48c6599b47e405094b173b19c407b194`.
`/tmp/access-organization-check-preservation.json` captures218 existing Access files
and concurrent starting files. Existing historical migrations/references/receipts and
concurrent Leave/PtS/Scribeswell work must remain preserved.

## Acceptance before implementation

Normal existing dev.py up resumed isolated run
`99b7231c-0a5b-4bdb-98e8-3329564c526a`, exit0; receipt:
`/tmp/access-organization-check-native-up.log`. No reset or new environment lifecycle.
Root created a private qualification Python environment with the approved baseline
packages using existing uv0.13.1, CPython3.15 and local wheel cache. Lock/sync were
frozen/offline/wheel-only; no published dependency baseline or historical lock changed.
Root preparation inputs/logs are under
`platform/deployment/.local/access-organization-check-20261022`.

Before behavior edits, root observed actual `/v2/check`404 and the absent
`access.check_organization_permission(text)` against retained Identity20/Access14.
The first read-only diagnostic used a schema-qualified routine lookup as Identity
owner; that correctly refused Access schema access. The confirming probe used public
catalog metadata, passed without mutation, and retained both logs separately:
`/tmp/access-organization-check-red.log`,
`/tmp/access-organization-check-red-confirmed.log`.
All218 Access source/receipt hashes matched before implementation dispatch.

The root's native fixture preparation uses exact Git-pinned Identity20 and matching
Access14 catalog-verifier sources. Private owner credentials/inputs and generated
state are bound in its preparation custody record, never reproduced here. Prior
proof frames remain historical; they are not refreshed into new passing receipts.

## Required impacts

Scaffold: reuse existing service/export/runtime patterns and owner qualification
helpers; no second generator or generic service. Shared UI: unchanged. Agent context:
unchanged. Documentation: owner runbook/evidence and mutable current handoffs. ADR:
existing authorization, release safety, short transactions, logging and structural
integrity decisions apply unchanged. Additional application checks remain mandatory
acceptance work for their first consumers; deferral does not make protection optional.

## Verification and review

Complete. The authoritative post-review results, requirement mapping, source/receipt
custody, review decisions and normal stop are recorded in the final closure below.
Earlier candidate results and failed attempts remain historical evidence.


## First qualification feedback

The first source-bound native frame retains successful supported Identity fixture and
KDG registry preparation throughAccess12, then a rolled-back legacy fixture INSERT
with SQLSTATE42P08. One reused actor parameter had implicit text and UUID contexts;
explicit text casting corrects the fixture without changing production behavior. No
reader SET edge or Access15 was applied by that attempt. Failed frame/diagnostics are
retained; the next attempt uses a fresh namespace and preparation custody.

The initial affected regression completed1764 PASS/22 failures. Existing historical
mocks default newly queried routines to present and several tests use moving HEAD as
an unknown revision. Corrections retain exact old revision expectations while marking
the new reader absent in old fixtures and recognizing15 explicitly. Unexpected results
are not dismissed by changing business expectations. The latest preparation source
also refuses unknown reader dependencies/effective privileges before granting its
SET-only edge, matching the approved unchanged-on-drift requirement.


Attempt2 prepared current Access14 successfully, including nine supported KDG grants
and the retained unmapped legacy grant. True-admin preparation added only the approved
global SET-only reader edge. The following metadata observer refused SQLSTATE42809:
PostgreSQL may evaluate sequence privilege functions before filtering relation kind.
The query now CASE-guards sequence evaluation, as the existing Identity guard does.
No Access15 migration ran in that attempt; its state/edge/diagnostics remain retained.
A version-aware effective PUBLIC MAINTAIN check also closes the PostgreSQL17+ right.

The retained global edge exposed a clean-database bootstrap dependency: staged
Identity20 must accept precisely that known SET-only edge while preserving its empty
per-database privilege checks, before granting its two Identity rights. This is fixed
in mutable verifier recognition; historical Identity20 migration/reference stay exact.
Fresh final bootstrap will capture the actual current helper sources and immutable
historical files, rather than claim the old verifier can recognize the new global edge.


## Successful end-to-end candidate

Fresh frame: `platform/deployment/.local/identity-baseline/organization-check-attempt4-20261022`.
Controlled current-source Identity20 preparation preserves every historical migration
and reference, including its immutable20 reference; source/helper inputs and generated
state are bound in baseline-preparation-custody.json. Access15 passed an independent
rollback-only captured-source rehearsal against retained14 before this fresh candidate
(`root-rollback-rehearsal2.log`). Exact14 was restored, without a ledger stamp.

The rehearsal also caught a genuine DDL boundary: SQL function creation as the Access
migrator resolves Identity names. The function is now created after SET LOCAL ROLE to
the private reader, under temporary Access schema CREATE, then role reset and CREATE
revocation. No Identity schema privilege or body-validation bypass was added. A prior
metadata query likewise replaced schema-qualified Identity regprocedure lookups with
catalog-only routine classification. Attempt3 and all rehearsal logs remain preserved.

Final candidate --all exited0 (`root-native-attempt4.log`). Actual restricted runtime
SQL→HTTP checks passed for all nine KDG capabilities/resources, caller/account/org
binding, safe denials and authority-before-actor setup precedence. Protected owner
commands proved disable/re-enable, revocation without resurrection, retirement/rejoin
without old grants, and explicit renewal. Role/table/ledger isolation and rollback-only
PUBLIC MAINTAIN rejection passed. Controlled14→15 preserved complete business data;
injected postcondition failure rolled back, repeat retained state and catalog, and
unsafe-role/function drift refused with explicit forward retry. Both owner verifiers
passed after the migration and at retained inspection.

HTTP native proof uses an explicitly synthetic injected bearer verifier and the actual
restricted PostgreSQL login. It does not claim live provider/Entra sign-in, deployed
network policy, KDG business operation/device qualification or real consumer activation.
The existing approved httpx/TestClient combination emits an upstream deprecation
warning; checks pass and no unapproved dependency is installed to suppress it.


## Pre-review candidate commands and requirement mapping

Final frame: `platform/deployment/.local/identity-baseline/organization-check-final-20261022`.
D denotes `platform/deployment/.local/access-organization-check-20261022`.
P denotes `D/owner-env/bin/python`, installed from the actual services/access/uv.lock
using approved uv0.13.1, explicit CPython3.15.0, existing cache, `sync --frozen --offline
--no-build --no-config --no-python-downloads`. `root-owner-sync.log` exit0 and
owner-environment.json bind the owner lock, interpreter and29 installed distributions.
The earlier acceptance environment's separate private lock remains historical evidence.

- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 P -I -B -m pytest services/access/tests/test_organization_check.py -q -p no:cacheprovider`:43 focused tests passed (agent's final focused run); includes real provider adapter error mapping and bounded pool acquisition.
- Same flags with `services/access/tests apps/pts/tests/test_release.py platform/deployment/tests/test_migrate_adapter.py`:1806 PASS in69.54s (`root-regression-final.log`). This is the accumulated affected regression suite, not1806 new feature tests.
- `IDENTITY_QUALIFICATION_DIR=<final frame> P -I -B <final frame>/root_qualification_driver.py`: exit0 (`root-native-final.log`). The driver calls qualifier --all with selected safe failure diagnostics.
- `IDENTITY_QUALIFICATION_DIR=<final frame> P -I -B services/access/tests/qualify_organization_check.py --verify-retained`: exit0 (`root-retained-final.log`), separate read-only inspection.
- `P -B tools/py/run_compose_supabase.py --check-only`: exit0 (`root-compose-default-final.log`).
- Same command with `--identity-authority owned --no-seeds`: exit0 (`root-compose-owned-final.log`).
- Approved owner `uv lock --check --offline` and `P -B export_openapi.py --check` from services/access: passed; owner OpenAPI references and exact response/input variants are also tested.

| Requirement | Evidence |
| --- | --- |
| Exact current KDG capability/resource, identity/member binding, no replayable authority |43 focused HTTP cases; native all-nine positive reads and fresh decision IDs |
| Denied grant/admission/member state, no resurrection or replacement lookup |native protected disable/re-enable, revoke/regrant, retire/rejoin and explicit renewal |
| Actor setup only after current authority |native retained unmapped legacy grant409; same account without requested grant403; no identity mutation |
| Calling-service/bearer separation, configured org, strict body/scope, source unavailable |focused strict/duplicate/deep/large/unknown-field and real-adapter error cases; native policy, bearer, account and scope denials |
| Private role, selected columns, account/org RLS, no tables/ledger/owner escalation |native actual runtime/reader denials, positive own-account selected-column read, missing/wrong context and rollback-only PUBLIC MAINTAIN refusal |
| Exact controlled upgrade, failure, repeat, drift and forward recovery |native14→15 business preservation, injected postcondition rollback, role/function drift and explicit retry; both owners verify |
| Sources/log/state stay bound |source before/after, complete Access function/policy raw observation, retained inspection and root final audit |

The qualifier's final raw catalog includes every Access function and RLS policy field,
so a refusal cannot silently normalize a drift field omitted by older helper snapshots.
That strengthening uses a fresh final frame; the successful attempt4 receipt remains
separate historical evidence rather than being overwritten. Final review, preservation
closure and normal stop follow below.


## Final reviewed closure — 2026-10-22

The three independent review lenses completed. Every finding has its own verdict and
route in the owning spec's Review Triage Log. Corrected practical gaps are verified:
malformed successful provider responses return canonical 503/no-store without database
work; authenticated body receipt has a three-second deadline; configuration requires
printable ASCII keys; OpenAPI declares bearer AND service-key authentication; and the
nine resource expectations are literal independent test oracles. The new SQL reader
also binds permission registration to `kdg_capture`, so another enabled application
cannot satisfy KDG admission.

True-admin preparation now validates the receiving migrator and its exact assumption
paths before adding authority. Actual rollback-only native cases prove safe preparation
and refusal for unsafe recipient flags/incoming paths, with exact graph restoration.
A separate retained reference case proves wrong-application registration denial and
current profile/organization retirement denial through HTTP while valid grants remain.
Installed column-privilege, RLS-policy, role and function drift are rejected by both
owners without normalization or business/catalog changes, followed by explicit retry.

Two pre-existing transport concerns are recorded in BMAD deferred-work.md: total
provider-operation deadlines and established PostgreSQL connection/pre-ping outage
bounds before deployed Access operation. Current per-I/O/connect/pool/transaction
bounds are not represented as a total network-operation guarantee. No provider/device,
production or portable hosted-CI readiness is claimed.

The first reviewed native attempt expected the extension's Identity refusal identifier,
but Identity correctly refused earlier with `identity_target_role_unsafe`. The second
attempt's added-column fixture likewise reached a dependency guard before the expected
privilege guard. Safe rollback-only diagnostics established the exact identifiers; the
column case now changes an existing selected column's UPDATE privilege and verifies
complete restoration. An exact native drift-stage rehearsal passed before the fresh
final proof. These were qualification expectation/fixture corrections, not relaxed
business outcomes. Both failed frames and diagnostics remain retained.

Authoritative final frame:
`platform/deployment/.local/identity-baseline/organization-check-reviewed3-20261022`.
P and D retain their definitions above; the actual approved owner lock/environment was
used throughout. Final source-bound results:

- Focused HTTP contracts: **60 passed** (implementation agent), including independent
  nine-mapping expectations, provider shape failures and stalled-body timeout.
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 P -I -B -m pytest services/access/tests apps/pts/tests/test_release.py platform/deployment/tests/test_migrate_adapter.py -q -p no:cacheprovider`:
  **1,823 passed**, one upstream TestClient deprecation, 92.50 seconds;
  `D/root-regression-reviewed.log`. This is the accumulated affected suite.
- `IDENTITY_QUALIFICATION_DIR=<final frame> P -I -B <final frame>/root_qualification_driver.py`:
  **exit 0**, ten persisted stages plus retained inspection;
  `D/root-native-reviewed3.log`.
- `IDENTITY_QUALIFICATION_DIR=<final frame> P -I -B services/access/tests/qualify_organization_check.py --verify-retained`:
  **exit 0**, separate read-only verification of both owners and both case states;
  `D/root-retained-reviewed3.log`.
- Both database composition commands above: **exit 0** again;
  `D/root-compose-default-reviewed.log` and `D/root-compose-owned-reviewed.log`.
- Owner `export_openapi.py --check`: **openapi_current**. Approved frozen owner lock
  remains the same; no dependency baseline change. Final scoped diff whitespace check passes.

| Requirement strengthened by review | Final evidence |
| --- | --- |
| Correct own-account/organization resources for each literal capability | Independent nine-entry unit and native tables, all-nine actual SQL→HTTP checks |
| KDG application admission cannot use another registered application | Separate supported reference registration, grants and enablement; denied before and after KDG re-enable |
| Current profile and organization required despite valid grants | Reference HTTP positives before retirement and denials afterward; unchanged state around denied reads |
| Strict safe transport input/provider shape and complete auth contract | Focused stalled stream, malformed provider JSON/IDs, printable-key startup and OpenAPI AND assertions |
| Safe recipient before role preparation | Exact preparation body inside rollback-only safe/unsafe-flags/unsafe-incoming fixtures; graph restoration |
| Refusal preserves altered catalog as well as business state | Both-owner column/policy/function/role refusal; complete snapshots, restoration and forward retry |

Final root audit passed before and after normal stop: **217 bound sources, 15 native
logs, ten persisted stages**, source marker equality, captured two-owner helper/source
custody, generated inputs/bootstrap logs and the actual owner-lock receipt. Of the 218
pre-existing Access files, 206 remain byte-identical; the only twelve changed files are
the three intended mutable production modules and nine historical test fixtures.
Every historical migration/reference and prior evidence receipt remains byte-identical.
Frozen approved intent is unchanged. Supplemental diagnostics, preparation/rehearsal
scripts, RED logs, final regression/composition/native/retained logs and the stop receipt
are hashed in `D/root-audit-reviewed.json`.

Retained receipt SHA-256: `2c341e184cc151eaa017a9c46e96028959165c867e02eed5528cfb43f1f2f48b`.

Source marker SHA-256: `6ad01f865a71989db30749db617831cc625058263aa73ce666939f153009ef9b`.

Preparation custody SHA-256: `85ce93cc78bb52875dc1f771bd11ada1ac0a6778fc429bd4e7383b02accb3ff0`.

Root audit SHA-256: `37ef276d4278e92619654227ad4208d82ef8cc61382169a04c048900f8309744`.

Normal existing `dev.py stop --target platform/deployment/environments/kdg-local.json
--run-id 99b7231c-0a5b-4bdb-98e8-3329564c526a --supabase <pinned CLI>` returned
**exit 0 / completed**, `D/root-native-stop.log`. Retained database inspection preceded
stop; the post-stop audit checks files/receipts without claiming a live database read.
No reset, prune, disposal, real-account operation, production migration, deployment,
pilot or push occurred. Concurrent Leave/PtS/Scribeswell work is excluded from the
scope-only local commit. Scaffold/UI/context/documentation/ADR decisions above remain
unchanged. Next review the remaining WRITE prerequisites for the first KDG business
operation; no speculative Access variants or Leave implementation is included.
