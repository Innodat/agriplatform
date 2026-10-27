# E1-DISCOVERY verification evidence — 2026-10-27

Discovery implementation, verification and all three independent reviews are complete.
The single verification finding was patched; nothing was deferred.
The approved delivery is [current organizations and apps](../../../../_bmad-output/implementation-artifacts/spec-1-9-e1-discovery-current-organizations-and-apps.md).
CONTENT-READ completed its review before this increment began. No commit, production
activation, live adoption or grants are authorized by these local proofs.

[Source-bound results](evidence/e1-discovery-qualification-20261027.json) bind the final
runtime, migrations, helpers, references and qualifier to actual retained proof hashes.
[Native oracles](evidence/e1-discovery-oracles-20261027.json) publish the independently
specified synthetic expectations and restricted SQL roles with credentials removed.
Exact private fixtures, commands, logs and journals remain under ignored
`.local/leave-discovery-20261027/qualified-v3/`.

| Requirement | Executed evidence |
| --- | --- |
| Current app-specific organizations; eligible rows before pagination; bounded bigint strings | Native pages100/7 from107eligible contexts after7ineligible leading contexts; exact names/membership IDs, including values above JS safe integer. Same original cursor returns7/6/7after protected revoke/regrant. |
| Current entry applications and separate scopes | Exact app/scope oracles for4accounts: shared person with independent authority, zero-membership PtS, mixed account/org reference scopes, export-only omission, missing actor/person mappings. |
| Empty vs denial, closed caller/input policy and safe no-store errors | Native401/403/422/503checks plus HTTP acceptance tests, including500safe envelope. Directory cannot check capabilities or list organization contexts. |
| Revocation and membership freshness | Protected account-grant revoke/regrant observed immediately. Retire/rejoin creates a new membership, retains2old-bound grants, and neither discovery route revives their authority. |
| Restricted SQL and pool/context isolation | Native missing/malformed/wrong context, same-connection account reuse, stale-session marker and temp-shadowing checks; runtimeSELECT/DDL/SETROLE/private-function denials.10actual anon/authenticated invocations denied. |
| Current active profile and dependencies | Profile temporarily disabled gives403rather than empty; restored successfully. Guarded Auth pause gives503in2.014s; unpause restores200. |
| Catalogue bounds |128registered apps accepted; protected registration129makes both routes503without truncation. Deliberate invalid fixture retained. |
| Total budgets and lock recovery | Actual EXPLAIN ANALYZE returns3application rows and101organization rows. Exclusive fixture table lock makes both HTTP routes503in1.174s; rollback restores200. |
| Migration/release compatibility | Five fresh empty/prior/populated cases upgrade Identity26thenAccess19; reference pair repeats. Independent rollback reference extraction restores exact prior catalogue. Drift blocks dry activation; explicit forward retry succeeds.71historical migration/reference files preserved byte-for-byte.32previous client command receipts replayed, with durable attribution and explicit retire/rejoin/rebind compatibility. |
| Frozen runtime | Offline pinned Python3.15/uv0.13.1package; actual image nonroot65532, read-only root, dropped capabilities and no-new-privileges. Network-none default/Studies/canonical cold startup; stale-lock, foreign-payload and reinventoried-source refusal. Same8exact HTTP cases passed in image on guarded native network; normal stop exit0. |
| Generated consuming contracts and neutral reuse | Owner OpenAPI and generated DTO drift checks; all4typed suites compiled/executed; neutral API-client actual generation fixture passed. |

The native qualifier passed76steps across17mandatory coverage labels, including36HTTP
requests. Full affected regression passed **2,223 tests** with one existing FastAPI/httpx
deprecation warning in 52.74s. Separate platform release verification passed9tests and
11subtests in0.15s. Both composer check-only modes and deployment manifests passed.

The delegate first observed30HTTP acceptance404failures. Root verification exposed and
repaired cross-owner schema metadata lookups, excessive direct runtime Identity access,
private policy binding, installed schema ACL handling and the legacy Identity PUBLIC RLS
helper interaction. Identity26 now grants legacy authorize EXECUTE only to its private
owner, matching established projection owners; runtime/PUBLIC remain denied. New
reference fingerprints were independently published after explicit repaired-DDL rollback
rehearsal. No historical reference or applied migration was rewritten.

Full regression also exposed historical metadata doubles that implicitly advertised every
new routine as installed. They now explicitly exclude Discovery in prior-stage fixtures;
their original expected revisions remain unchanged. The latest-head test preserves
Identity25 ordinary dispatch, rejects25when latest is required and accepts26.

Two native attempts failed before dynamic transitions: an empty bearer created an invalid
HTTP header, then a grant-table oracle overlooked Access15's explicit SELECT revocation.
The repaired qualifier omits Authorization for a missing token and has an actual API401
transport test. Account-grant empty-RLS and organization-grant42501oracles now match the
existing permission history and actual restricted queries. Both failures, scripts,
fixtures and journals are retained. Resume replayed identical protected operation IDs
and verified the existing128-app/authority state, creating no duplicate setup authorities.

```sh
P=platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 timeout 180 "$P" -I -B -m pytest -p no:cacheprovider services/access/tests apps/pts/tests/test_release.py -q --tb=short
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$P" -I -B -m pytest -p no:cacheprovider platform/deployment/tests/test_release.py -q
"$P" -B services/access/export_openapi.py --check
N=platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node
"$N" .local/leave-discovery-20261027/tooling/api-client/src/cli.mjs --schema services/access/openapi.json --output services/access/contracts/generated --check
python3 tools/py/run_compose_supabase.py --check-only
python3 tools/py/run_compose_supabase.py --check-only --identity-authority owned --no-seeds
"$P" -I -B platform/deployment/release.py check
"$P" -I -B .local/leave-discovery-20261027/qualified-v3/native_discovery_conductor.py --execute
```

The native command is a retained source-bound execution, not an idempotent reset command:
its final129-app fixture intentionally rejects further positive discovery. Preserve it.
The public qualifier accepts a separately prepared guarded private fixture and reserves
new proof/journal files before effects. Local proofs use retained Leave run
88a737dd-ad7b-429a-a83c-5d103716d659(Auth55581/DB55582). KDG and unrelated work are preserved.
Image: `agri-access-discovery-api:cdf8c337a4`; exact content ID is in source-bound results.

Scaffold impact: neutral generated-contract fixture proved with first consumer; no new
runtime framework or authenticated scaffold promotion. Shared UI and agent-context: no
changes required. Documentation: owner runbook, evidence and Leave tracking. ADRs:
accepted decisions unchanged. Selected implementation configuration gpt-6.1-sol/high;
actual exposed model and usage remain unknown. Directory adoption is E1-LAUNCHER.


## Independent review closure

All three context-free reviews completed before triage. Blind and edge reviews found
no supported defects. Verification identified one medium gap: Reference's successful
organization route had only denial coverage. The retained implementation agent added
`test_reference_organizations_are_current_and_app_specific`; it asserts exact successful
fields, fresh subsequent results and the forwarded reference selector. A fresh native
fixture proves the same account sees two Leave organizations and exactly one Reference
organization. Exact HTTP oracles, source/process binding and protected setup receipts
passed; the original 129-app fixture was preserved. Its copied synthetic token expired
before the first supplemental check, so that failed attempt and its refresh are retained.

Full affected regression after the patch: **2,223 passed**, one warning, **52.74s**.
OpenAPI, generated DTO drift, composer and frozen runtime custody checks remain passing.
The patch changes verification only; image/runtime/migration source hashes still match
their completed proofs. Original executed native builder bytes were archived and checked
against the executed plan before adding the new native success helper. No fresh review
loop was required by the patch route; iteration remains zero. No findings deferred.

Both bound host APIs stopped normally via SIGTERM, socket closure confirmed; their exit
codes are unavailable, with no forced termination. The exact Leave acceptance CLI run
stopped normally and retained its databases/volumes/history. All image containers stopped
normally and remain retained. KDG, Content fixture state and unrelated changes preserved.
