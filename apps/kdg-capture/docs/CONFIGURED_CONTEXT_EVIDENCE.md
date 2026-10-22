# Configured KDG current-context boundary — 2026-10-22

Complete for this bounded API prerequisite; final reviewed closure is below.
This bounded Story1.1 API prerequisite adds explicit startup configuration and actual
KDG→Access HTTP→restricted SQL proof. It does not complete browser entry, persistence,
provider sign-in, release or pilot readiness. Fingerprints/HMAC remain deferred.

## Selection, scope and behavior

bmad-help used the updated next-session handoff, catalog, repository configuration,
Story1.1 and [prior API evidence](CONTEXT_API_EVIDENCE.md). [BD] bmad-build selected the
remaining current-owner API integration prerequisite before browser entry and initial
questionnaire persistence. No generic lifecycle or product spec is duplicated.
The new api/runtime.py factory reads three explicit server-owned environment values
and delegates to the existing validated KDG context factory. Missing policy fails at
construction; no environment fallback when an explicit empty mapping is supplied.
It captures policy once. Caller input cannot choose organization, actor, account or key.

Synthetic local/CI only. No setup, provisioning, grant, account, migration, deployment,
real provider, business persistence, Leave/editor, pilot, reset/prune or cleanup action.
The existing native run was resumed and normally stopped after final proof,
with all databases, roles, data, volumes, old receipts and resources retained.

## Behavioral ATDD and focused TDD

The initial test used the actual existing unconfigured context factory when the new
startup adapter was absent. A complete synthetic valid policy plus current decision
still returned503 authorization_unavailable where200 was expected: **1 failed0.91s**.
This is an HTTP behavior failure, not an import-only RED. It proves missing startup
wiring; the prior deliberately unconfigured refusal was correct for its own contract.

Before implementation, missing/invalid/empty-explicit-policy tests extended that outer
acceptance: **8 failed0.67s**. The adapter then passed8 in0.64s. Test fallback to the
old factory was removed once the adapter existed. Added default-environment/snapshot
coverage and the existing70 API cases passed with Access60: **139 passed3.04s**.
No existing business expectation was weakened. Exact output captures are retained in D
and selected excerpts/digests will be versioned at final closure.

D: platform/deployment/.local/kdg-configured-context-20261022.
P: absolute platform/deployment/.local/kdg-context-20261022/owner-env/bin/python.
A: absolute platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python.
All Python checks use approved existing locked environments, -I -B and disabled
pytest plugin autoload for pytest. No dependency installation or lock edit occurred.
The shell's pinned TypeScript7.0.2 and all published baseline files remain unchanged.

Commands from repository root:

- `timeout 60s env PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 P -I -B -m pytest apps/kdg-capture/tests/test_configured_context.py -q -p no:cacheprovider`: behavioral/policy RED and focused GREEN above.
- Same flags with A and `services/access/tests/test_organization_check.py apps/kdg-capture/tests`:139 PASS; D/affected-pre-review.log.
- `A -I -B apps/kdg-capture/tests/qualify_configured_context.py --run`: separate native proof, described below. Normal unit tests neither skip nor pretend to run it.

## Authoritative retained fixture and actual boundaries

[Access final reviewed evidence](../../../services/access/ORGANIZATION_CHECK_EVIDENCE.md#final-reviewed-closure--2026-10-22)
selects `platform/deployment/.local/identity-baseline/organization-check-reviewed3-20261022`.
Earlier final/attempt frames are historical. Its unchanged retained receipt SHA256 is
2c341e184cc151eaa017a9c46e96028959165c867e02eed5528cfb43f1f2f48b.
The existing current owner verifier checks217 bound sources plus logs, both owners'
catalogs and both retained case states using read-only transactions before/after proof.
It is never called with --all, a preparation route, migration or operator command.

The Access-owned new serve_kdg_context_fixture.py reads the verified private fixture
through the existing guarded loader, derives exactly one positive/mapped, denied/mapped
and actor-setup/unmapped case from retained state, and uses the existing access_runtime
login. It checks actual session/current role and nonsuperuser/no-bypass flags. Its
explicit synthetic bearer mapping authenticates only those test identities; no real
Auth or account mutation. Each /v2/check uses actual current Access code and SQL.
KDG imports no Access/Identity implementation; it communicates with a separate owner
process through verified local TLS and its ordinary /v2/check request.

The KDG test process uses the new default environment factory and an explicit local-CA
transport. No verify=False or production TLS relaxation. Actual outer loopback HTTP
exercises KDG middleware/DTO/error adaptation. A new private test TLS fixture is made
using existing openssl; it is unrelated to deferred operation fingerprints/HMAC.

Cases:200 twice with distinct decisions and exact account/actor/member/org/own scope;
403 access_denied;409 identity.actor_setup_required;401 authentication_required;
422 query-selector refusal. Four actual Access permission SQL reads are required.
After the Access test server stops, the still-running KDG instance returns503
 authorization_unavailable within4s. Business/catalog/identity state remains exactly
the original retained state. No current-grant transition is performed; prior native
owner lifecycle tests stay historical and current KDG unit tests prove no decision cache.

## Native failure investigation and current candidate

First native attempt `native-ae96a63f59a449e68d2217a0f3e69c9c` reached all six live HTTP
checks but Access exceeded the12s process-stop bound and was killed(-9); KDG stopped0.
Second diagnostic attempt `native-fd9467b7f0d545afbb9c80b3ac894c77` reproduced this.
Safe lifecycle/stack diagnostics identify Uvicorn waiting for TLS connections to close;
no busy SQL thread is shown. The underlying idle-TLS close behavior is not claimed fixed.
Both failed results, forced markers, logs and exact source capsules remain. Capsules
were verified against the original execution SHA256 values before later edits.

The test server now sets timeout_graceful_shutdown=3. Candidate
`native-e6d414108c554cd8aaf1ad41308c3e07` passes all seven status cases, source/state
checks and independent before/after retained inspection, with both server processes
exiting0. It records access_shutdown_warning=true: bounded idle-TLS drain timeout.
This is verified bounded fixture shutdown, not evidence of a completely graceful
production drain. The deployed Access timeout/pool/rolling-release envelope remains
unqualified. No dependency update, underlying library fix or new runtime behavior is
claimed to remove that limitation. Final reviewed proof will bind the final source.

## Delivery impacts and remaining gates

Scaffold: reuse current factory/closed DTO/error adapter and existing owner fixture;
no generic startup pattern promotion. Shared UI: unchanged. Agent context: root policy
suffices, actual commands in API README. Documentation: README, this evidence, Build
spec and additive current handoff. ADRs: existing ownership/configuration/access/error/
logging/release decisions; no accepted ADR changes. All fingerprints/HMAC stay deferred.
No current DTO or generated-client change is needed; existing OpenAPI/types remain
source authority. Browser auth/return/navigation/accessibility, domain persistence,
queue/device/backup and deployed release gates remain explicit future consumers.

## Final reviewed closure

Configured one-shot Blind Hunter review completed. All seven findings were assessed
individually in [Build triage](../../../_bmad-output/implementation-artifacts/spec-kdg-configured-context.md#review-triage-log)
and patched. No new product/runtime feature is deferred by review. Remaining browser/
provider/persistence/device and deployed drain/pool/release gates stay explicit; the
observed idle-TLS warning is not claimed repaired by a dependency or production change.

The final harness includes KDG's actual generated safe_errors.py in its executed-source
capsule, unconditionally attempts independent retained-after inspection after child
teardown, and records fixed safe failure/stage identifiers. Arbitrary exception text
is never serialized. SIGTERM/SIGINT route through bounded teardown. Relevant installed
package versions, executable path/hash, Python/OpenSSL and both owner/app lock digests
are persisted. All supplied synthetic bearer tokens plus service key are checked across
responses and all server logs. The native proof also loads the advertised ASGI factory
via Uvicorn's actual --app-dir/--factory CLI in a fresh process, checks401/no-store,
and exits automatically after one request. This smoke exercises factory import and
startup; private-CA authenticated integration remains the separate test transport.

Final source-bound native frame:
`D/native-3502e9ca55d24b1997df5414cb2b13a7`.
`A -I -B apps/kdg-capture/tests/qualify_configured_context.py --run`: **exit0**.
Eight checks pass (seven consumer HTTP cases plus the CLI smoke), four restricted
permission SQL reads are counted, and all three server processes exit0. Independent
retained-before/after inspection passes; result retains access_shutdown_warning=true.
That warning qualifies bounded fixture shutdown only. Exact executed source bytes and
hashes, runtime/lock provenance and safe logs remain alongside result.json.

Interruption control frame:
`D/native-c52dac4237b5406ba8623f0cd49268bd`.
Same command with --interrupt-probe: **expected exit143** after runner SIGTERM.
Receipt correctly says passed:false, failure_identifier:supervisor_termination,
failure_stage:supervisor_interruption_probe and signal15. Both child exits0 and
retained_after.status=passed are verified. This is a successful interruption safeguard
check, not a falsely successful interrupted business qualification. It exercises the
same failure-finally path as assertion errors. Earlier failed/forced frames remain.

Final tests and checks:

- `timeout 60s env PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 P -I -B -m pytest apps/kdg-capture/tests -q -p no:cacheprovider`: **79 passed1.26s**, D/final-kdg-tests.log.
- Same flags with A and `services/access/tests/test_organization_check.py apps/kdg-capture/tests`: **139 passed2.70s**, D/final-affected-tests.log.
- `P -B apps/kdg-capture/api/export_openapi.py --check`: openapi_current; D/final-openapi-check.log. No DTO/generated-client change.
- Selected Node26.11.1 `node_modules/typescript/bin/tsc --project apps/kdg-capture/tests/tsconfig.json`: exit0; D/final-types.log. Application TypeScript7.0.2 is unchanged.
- Existing TestClient upstream deprecation warning remains; no dependency installation or lock edit was made to remove it.
- Scoped whitespace, source capsule/current-byte custody, historical217 source/log bindings, original handoff tail and published baseline preservation pass. Root/whole-repository lint/test/CI and portable fresh native bootstrap are not claimed.

Existing `python3 platform/deployment/dev.py up --target platform/deployment/environments/kdg-local.json
--run-id 99b7231c-0a5b-4bdb-98e8-3329564c526a --supabase <absolute pinned CLI>`
returned completed/exit0; the initial relative-path invocation refused before action.
The same guarded stop command returned completed/exit0 after final database inspection.
All data, roles, volumes, receipts and historical resources remain; no reset/prune,
cleanup, provisioning, grants or migrations. Post-stop custody checks read files only;
no live database read is claimed after stop.

[Durable non-sensitive custody/results](evidence/configured-context-20261022.json)
record the full baseline Git ID, protected/current source hashes, final and interrupted
receipts, failed-frame digests/results and observed test/stop excerpts. The current
handoff prepends this checkpoint and retains every prior byte. Concurrent Leave/
Scribeswell/planning work is excluded and preserved. The scoped local commit is not pushed.
