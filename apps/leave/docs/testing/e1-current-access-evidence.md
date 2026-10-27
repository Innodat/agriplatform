# E1-ACCESS-B current capability enforcement

Current Access decisions now support registered account and organization capabilities,
Leave own-person resources, and People's nullable current organization identity context.
Account authority stays independent of membership, person links and employment. Existing
KDG and Studies contracts and generated Studies exports remain compatible.

Implemented, independently reviewed and verified on 2026-10-27. All 13 findings were fixed;
none deferred. The [machine evidence](evidence/e1-current-access-20261027.json) binds current
source bytes and retained proof files to hashes. Tracker state is review; no commit or
production activation was performed.

## Acceptance traceability

| Requirement | Executed proof |
| --- | --- |
| Exact callers/scopes, disclosure order, closed JSON/errors and deadline cleanup | `test_capability_check.py`, actual native HTTP |
| Account with no memberships; independent accounts sharing a person; exact own resource | Initial 25 native checks and final 27-step retained qualifier |
| Nullable People person; authorized missing person; Reference organization resource |9 supplemental checks and final qualifier |
| Revocation, global/org disable and re-enable, rejoin without grant resurrection | Final qualifier plus7 final boundary checks |
| Concurrent revocation | Held uncommitted revoke permits earlier committed grant; after commit HTTP403 `access_denied`; explicit controlled-race receipt |
| Reused connection; no runtime DDL/DML or Identity-table reads | Final qualifier's scoped SQL and three actual42501 denials |
| Actual provider outage/recovery and SQL unavailability | Bound API/provider/DB process; root-controlled Leave Auth pause/resume with PostgreSQL barriers; separate unavailable SQL endpoint |
| Unexpected private-reader membership | Root rollback-only grant rejected, then exact reader state reverified |
| Complete native custody/oracles | Actual PID/cwd/env/socket binding; secure single-read fixture;17 runtime/source inputs unchanged before/after; exact identity/resource/error assertions |
| Typed consumer recovery and compatibility | Capability adapter executes; foreign People account/org rejected; existing language and Studies type tests compile |
| Clean/previous/failure/retry migration | Genuine empty chains;32 captured prior-client replays; migration failure blocks activation; explicit forward retry |
| Historical integrity |5 current owner-catalog pairs;66 historical migrations/reference files unchanged; source-chain drift tests |
| Frozen runtime and deployment inputs | Nonroot/read-only/no-capability / no-network image; canonical manifest and Studies synthetic cold startup; stale/forged bundles refused |

## Reproducible verification

The final affected suite passed **2,154 tests in 93.42s**, with one existing
Starlette/httpx deprecation warning. Shared release tests ran separately because both
release modules use the same Python basename: **9 passed, 11 subtests**. Both composition
checks, manifest validation, owning OpenAPI export/drift, generated types and executable
consumer checks passed. Generated files were produced through the owning generator.

```sh
P=platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$P" -I -B -m pytest -p no:cacheprovider services/access/tests apps/pts/tests/test_release.py -q
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$P" -I -B -m pytest -p no:cacheprovider platform/deployment/tests/test_release.py -q
"$P" -B services/access/export_openapi.py --check
python3 tools/py/run_compose_supabase.py --check-only
python3 tools/py/run_compose_supabase.py --check-only --identity-authority owned --no-seeds
python3 platform/deployment/release.py check

N=platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node
T=platform/deployment/.local/leave-workspace-adoption-20261026/candidate/root/platform/api-client/node_modules/typescript/bin/tsc
"$N" "$T" --ignoreConfig --strict --target es2022 --module commonjs --moduleResolution node --ignoreDeprecations 6.0 --outDir /tmp/access-b-types-reviewed services/access/tests/capability_types.test.ts services/access/tests/language_types.test.ts services/access/tests/studies_types.test.ts
"$N" /tmp/access-b-types-reviewed/tests/capability_types.test.js
"$N" .local/leave-access-b-20261027/api-client/src/cli.mjs --schema services/access/openapi.json --output services/access/contracts/generated --check
```

The private generator copy contains unchanged platform generator sources and resolves the
pinned 0.99.0 generator / 6.0.3 compiler from existing local installations, avoiding concurrent
workspace dependency changes. The native final command was
`"$P" -I -B .local/leave-access-b-20261027/run_qualifier_final.py`; its guarded conductor
prepares the explicit fixture and invokes the retained owner qualifier. It pauses only
the disposable Leave Auth container and always resumes it. Tokens/credentials remain in
mode0600 private files under the git-ignored `.local/leave-access-b-20261027/` frame.

## Delivery boundaries

Actual Auth 55581 and PostgreSQL 55582 belonged to the retained Leave acceptance run.
Scratch names have explicit `acb_88a737ddad7b_` bindings; actual container/network and original
restricted owner logins were verified. Failed attempts, journals and earlier bundles remain.
An actorless historical-state fixture was prepared explicitly by root with existing user
guards restored before API execution; this is not a runtime provisioning path.

No shared UI, scaffold generator or accepted ADR change was needed. The owner-specific
adapter, deployment configuration and frozen packaging were updated with their tests.
Agent context remains unchanged. Private local artifacts are now ignored by Git.
Owner runbook: [CURRENT-ACCESS.md](../../../../services/access/CURRENT-ACCESS.md).

KDG's 55481/55482 environment remains running and unchanged. PtS cutover, discovery,
People management and application journeys remain separately gated. Release activation
is a dry callback; no production migration, deployment or downstream enforcement claim
is implied. Leave acceptance containers are normally stopped with volumes retained.
