# Studies enrollment delivery evidence

Approved source: `_bmad-output/implementation-artifacts/spec-scribeswell-account-enrollment.md`.
Both frontmatter contexts were read before implementation. This delivery is the
Access/Identity enrollment and canonical check slice; it does not mount Scribeswell
notes/editor/recipient routes, change accepted ADRs, migrate Leave/PtS, provision real
accounts or deploy/activate anything.

The first focused acceptance command failed with eight fixture errors because
`create_app` did not yet accept the Studies owner dependencies. The new route/owner
integration was then implemented. The existing approved Python environment was used;
PATH uv0.12.9 refused the repository's uv0.13.1 requirement, so no resolver/install or
dependency baseline change followed. Existing KDG characterization remained in the
focused suite throughout. Those fixture TypeErrors were not a user-visible behavioral
ATDD failure; this is a chronological verification limitation, not evidence of an
observed initial404.

A retrospective comparison later loaded immutable baseline commit
`4fbbcc39d2eb9749f5987acd61acfef1b0131145` main/organization HTTP sources into a
temporary directory using `git show`, without changing the working sources. Its
supported `create_app(db, authenticate)` received the same enrollment HTTP request
as the final implementation: the acceptance expectation200 observed404 on the
baseline and200 on the final implementation. This is retrospective baseline behavior
proof, not a rewritten first-RED chronology. Command:
`P -I -B /tmp/studies-baseline-http-proof.py`; final result exit0 retained in
`/tmp/studies-baseline-http-proof-final.log`. The earlier harness attempt and its
final-module opt-in readiness refusal are retained in
`/tmp/studies-baseline-http-proof.log`; only the temporary harness import order changed.

## Commands and results

`P` is
`platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python`.
`N` is
`platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node`.
Python commands use `-I -B`, `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` and
`pytest -q -p no:cacheprovider`. Synthetic HTTP tests run outside the process sandbox
because its TestClient event loop stalls; no application network/service was mocked
into a claim of native role/provider proof.

- Final focused Studies/KDG/release tests:117 passed,11 release subtests passed in13.08s
  (`/tmp/studies-final-focused.log`):
  `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 P -I -B -m pytest -q -p no:cacheprovider services/access/tests/test_studies_access.py services/access/tests/test_studies_identity.py services/access/tests/test_organization_check.py platform/deployment/tests/test_release.py`.
  The independent root broad run reached2322passed/4726subtests,2skipped before
  interruption:39 deployment fixture refusals correctly detected the still-running
  approved native stack ports, plus one operator signal test failed its four-second
  worker startup wait. Isolated SIGINT/SIGTERM rerun passed both cases in8.02s; no
  assertions were relaxed. Root owns the subsequent port-free deployment regression.
- The explained18 legacy regression failures were moving-head sentinels and old fake
  metadata treating the newly queried Studies routine as present. Unknown sentinels
  now use9999; old fixtures explicitly report the new routine absent. Exact historical
  revision/source/bundle assertions remain. Independent targeted rerun:18 passed.
- `P -I -B -c "import runpy,sys; sys.path.insert(0,'services/access'); runpy.run_path('services/access/export_openapi.py',run_name='__main__')"`
  generated the owner OpenAPI. The same command with exporter `--check` returned
  `openapi_current` under independent verification.
- The existing `platform/api-client` CLI generated and checked
  `services/access/contracts/generated`. Root tooling lacked its isolated pinned
  TS6 payload; the byte-identical four CLI/tool source files were verified against
  retained `platform/deployment/.local/scaffold-application/proof-yc4xuk/root`, whose
  already installed pinned dependencies were used. No package installation or root
  TypeScript change occurred. Sandbox generation failed; the same local tool outside
  the sandbox succeeded. Derived files were changed only by the installer. Exact
  generation command (append `--check` for verification):
  `N platform/deployment/.local/scaffold-application/proof-yc4xuk/root/platform/api-client/src/cli.mjs --schema /home/ck/repos/innodat/agriplatform/services/access/openapi.json --output /home/ck/repos/innodat/agriplatform/services/access/contracts/generated`.
  Final check returned `api_client_current`; OpenAPI final check returned
  `openapi_current`.
- `N node_modules/typescript/bin/tsc --ignoreConfig --noEmit --strict --skipLibCheck --target ES2022 --module NodeNext --moduleResolution NodeNext services/access/tests/studies_types.test.ts`
  passed under TypeScript7.0.2. Its initial failure exposed optional response defaults;
  Pydantic serialization schemas now mark emitted default fields required, and the
  regenerated consumer proof passes.
- Both database composers passed independently: ordinary
  `python3 tools/py/run_compose_supabase.py --check-only` (15 migrations) and
  `--identity-authority owned --no-seeds --check-only` (9 migrations). No composition
  output was written. Owned mode without `--no-seeds` correctly refused.

## Actual isolated qualification

The normal native wrapper resumed only retained run
`99b7231c-0a5b-4bdb-98e8-3329564c526a`, loopback database55482/API55481. It never touched
unknown54322. Wrapper logs are `/tmp/scribeswell-studies-native-up*.log`; the first
attempts refused missing isolated module path and non-explicit executable path before
successful normal `up`. No reset/prune/cleanup or production action ran.

The initial frame
`platform/deployment/.local/identity-baseline/studies-enrollment-20261023` remains intact.
The final frame is
`platform/deployment/.local/identity-baseline/studies-enrollment-final-20261023`.
Private inputs/logs are0600. Source-bound qualification and read-only retained inspection
use `services/access/tests/qualify_studies_enrollment.py`; the separate parent-authored
SELECT-only oracle is retained as `tests/inspect_studies_enrollment.py`.

Actual provider account creation succeeded. Password sign-in returned422
`email_provider_disabled`; this was retained, without changing provider configuration.
Admin-generated magic link plus local `/auth/v1/verify` issued real provider tokens
without outbound email. Live `/auth/v1/user`, native Auth→Identity hook and the isolated
fixture's actual profile hook were verified. Hook-created profiles had no username
onboarding; zero organization memberships were asserted. All synthetic accounts are
retained. No locally signed JWT, custom HMAC or general account provisioner was added.

Retained KDG SQL fixtures originally had a minimal Auth stub. Only the new isolated
clones received the selected actual-provider column types needed for eligibility;
the actual provider schema/configuration was unchanged. Native legacy profile RLS
required the explicit existing `identity.authorize` helper grant for the new NOLOGIN
owner. The candidate also gives its NOLOGIN Access owner `UPDATE(account_id)` solely
for PostgreSQL row locking; runtime roles have no table privileges and grant triggers
refuse that owner's updates. Earlier failed transactions/logs remain retained.

| Requirement | Executed native evidence |
| --- | --- |
| Verified account, no membership/person/employment/PtS prerequisite | Actual provider/profile hooks; first-use fixtures assert zero memberships |
| First same/distinct-operation enrollment race | Four simultaneous requests across three operations, all200; original acknowledgements retained; exactly1grant,1assignment event,1actor setup event |
| Actor-only partial completion and adopted actors | No permission after setup alone; same actor reused; deliberately adopted different UUID remains unchanged |
| Collision/current eligibility | Conflicting actor, missing/deleted/system/keyed profile, unverified/deleted/banned Auth rows refuse |
| Closed confirmed-denial errors | Still-valid live provider bearer plus local unverified/banned Auth state returns actual API403 with `identity.verification_required` / `access_denied`, using SQLSTATEs only |
| Disabled application/new enrollment/replay | Protected audited disable denies check/new/replay; protected explicit re-enable restores only retained valid authority |
| Deadline and retry | Actual SQL sleep with0.1s budget returned unavailable in~0.10146s; real blocked enrollment times out without persisted grant/outcome, then original operation succeeds after fresh evidence |
| Lost response and revoke replay | Actual committed transport response discarded; original operation resolves unchanged; attributed revocation then denies replay/check without restoring grant |
| Restricted SQL | Three actual LOGIN roles denied raw tables/owner assumptions; FORCE RLS and fresh connection context independently inspected |
| Populated upgrade/failure/repeat | Actual Alembic Access-before-Identity refusal, injected owner failure rollback retaining old ledgers, successful ordered upgrades and repeat; no activation |
| Empty-owner clean upgrade | Separately created empty database with only selected Auth prerequisites, ordinary Identity then Access Alembic through21/16, zero account/grant seeds |
| Final source binding | Fresh normal clean/populated proofs after the SQLSTATE correction, plus final fresh first-use race, retained source/proof/log hashes and separate read-only inspection |
| Release opt-in | Host consumes manifest runtime roles/readiness; default runtime refuses unprepared startup; read-only owner readiness checks exact heads/catalogs, provider/hook qualification, matching durable service executor, role restrictions and fixed registry |

The source-defined Identity21 reference was recorded only from an isolated source-executed
candidate; immutable historical migration/reference files were preserved. Current-source
normal Alembic proofs remain distinct from the reference recorder's Operations context.
Selected safe failure logs and each earlier candidate reference remain private evidence.
The first seven-request exploratory candidate failed its all-success assertion before
individual responses were retained. Its cause is not established and no larger-load
capacity claim is made; the final fresh four-request proof keeps the original all200
expectation. Failed exploratory state is not relabeled as successful qualification.

No cancellation/timeout is described as proof of rollback. Confirmed absence after the
blocked-write test is established by independent subsequent SQL observation. An unknown
commit always requires same-operation recovery with fresh current eligibility.

Required impacts are recorded in the runbook: no speculative scaffold engine/shared UI
or context change; documentation and generated owner wire updated; ADRs unchanged.
Public reading and current KDG behavior stay compatible. Production principal/credential
preparation and any real deployment remain outside this delivery; opt-in readiness
refuses when those prerequisites are absent.

Final retained read-only verification passed (`/tmp/studies-verify-retained.log`).
The owning SELECT-only inspector independently passed4grants/4initialevents/10receipts,
zero memberships and no runtime table writes (`/tmp/studies-independent-inspection.log`).
Root repeated its own SELECT-only inspection with the same results
(`/tmp/scribeswell-root-final-inspection.log`). No native mutation followed. The final
owner sources/proofs remain frozen in the retained `qualification.json`; this mutable
delivery chronology is deliberately outside that source inventory.


## Independent review follow-up

Three review layers completed. Confirmed corrections cover post-lock Auth freshness,
source/case proof validation, direct-startup configuration completeness, safe diagnostic
correlation and the Studies-enabled host preflight test gap. Prior retained proof above
is historical; it must not be relabeled as execution of review-patched sources.

The additional full port-free regression command was:
`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 timeout 900s P -I -B -m pytest services/access/tests platform/deployment/tests -q -p no:cacheprovider --tb=short`.
It reached91% without reported failures before timeout (exit124), retained at
`/tmp/scribeswell-final-port-free-regression.log`. This is incomplete verification,
not a full-suite pass. Collection reported2740 tests. The earlier stack/port conflict
and operator-startup failure remain accurately recorded above.

Before review fixes, the known retained native run stopped normally (completed,
`ok:true`, runtime_ready:false), `/tmp/scribeswell-normal-stop.log`. All resources
remain retained. Review qualification must produce new evidence and stop normally again.


Corrected-source review qualification completed in
`platform/deployment/.local/identity-baseline/studies-enrollment-review-20261023`.
Its eight required stage proofs bind the36 authoritative source files that executed;
missing case fields and stale sources refuse qualification/preparation. All19 retained
log hashes were independently checked. Runtime/host RED had six observed failures
(`/tmp/studies-review-runtime-red.log`) before the corresponding fixes. The actual
lock-contention RED is retained separately in `studies-enrollment-lock-red-20261023`
and `/tmp/studies-review-lock-red.log`. GREEN covered nine observed waits: ban,
deletion and loss of verification after the account lock, after the actor lock, and
on replay. Each denied without new actor/receipt writes.

The corrected sources re-executed provider/profile-hook, clean and populated normal
Alembic/failure/repeat, both four-request races, adopted/colliding actors, current
eligibility/availability, partial completion, lost response, revocation and native
lock/statement deadlines. The CLI stage entrypoints use
`P -I -B services/access/tests/qualify_studies_enrollment.py --<stage>`.
Preparation/provider/lock commands are retained in `/tmp/studies-review-*.log`.
The explicit synthetic HTTP prerequisite enrollment was executed with
`P -I -B /tmp/studies-review-initialize.py`. Then
`P -I -B /tmp/studies-review-stages.py` executed, in order: `--boundaries`,
`--first-use-race`, `--current-denials`, `--confirmed-http-denials`,
`--current-source-upgrades`, `--current-first-use-race`, `--retain-qualification`,
`--readiness-proof`, `--verify-retained`. Finally
`P -I -B /tmp/studies-review-finalize.py` retained the prior attempted records and
reran the last three stages with external completed logs.
Stages use fresh retained files, not rewritten earlier evidence.
The final three passing external logs are
`/tmp/studies-review-final-{retain-qualification,readiness-proof,verify-retained}.log`.
One prior retention attempt hashed its own still-open log; its records remain as
`initial-log-binding-{qualification,readiness,readiness-proof}.json`. The unchanged
stage executions were then retained with completed external logs and verified.

Root independently checked source/proof/log consistency
(`/tmp/scribeswell-root-review-source-proof.json`) and ran the equivalent SELECT-only
review-frame inspector (`P -I -B /tmp/studies-review-independent-inspect.py`), whose
only source differences are the fixed repository root and review-frame path.
Result:4grants,4initialevents,9receipts,zero memberships,no runtime table writes
(`/tmp/scribeswell-root-review-inspection.log`). No native mutation followed.
Normal stop completed successfully, preserving all resources
(`/tmp/scribeswell-review-normal-stop.log`).

Root final focused command:
`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 P -I -B -m pytest -q -p no:cacheprovider --tb=short services/access/tests/test_studies_access.py services/access/tests/test_studies_identity.py services/access/tests/test_studies_readiness.py services/access/tests/test_organization_check.py platform/deployment/tests/test_release.py platform/deployment/tests/test_host.py`.
Result:143passed,49subtests passed in3.15s
(`/tmp/scribeswell-root-review-focused.log`). OpenAPI and generated-client checks again
returned `openapi_current` / `api_client_current`; TypeScript7.0.2 compilation and both
composition dry runs passed. No dependency or historical reference baseline changed.
All confirmed review fixes were applied; optional catalog/target/provisioning hardening
was rejected with evidence in the spec triage log. Fingerprints/HMAC remain deferred.
