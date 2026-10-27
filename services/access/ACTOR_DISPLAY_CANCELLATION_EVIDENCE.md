# Identity actor display cancellation-diagnostic repair — 2026-10-27

Baseline: `f116f05a590d7500e3b61b4a6783d441a872e3d4`.
The isolated candidate's shielded reader now returns a private, redacted outcome
for ordinary exceptions. Only an uncancelled owner unwraps it. Cancelled attempts
consume the outcome privately and propagate their original cancellation. No global
logging changes, detached reads, deadline resets or wire changes are introduced.
The service remains unmounted; no native or real-authority qualification follows.

## Actual requirement-to-test evidence

| Trigger | Executed result |
|---|---|
| Caller cancellation, then reader cleanup exception | HTTP request remains cancelled; reader finished; zero asyncio diagnostics |
| Repeated caller cancellation during failing cleanup | Ownership retained until reader finishes; cancellation preserved; zero diagnostics |
| Inner timeout followed by cleanup exception | Safe503/private/no-store; no partial success or diagnostic exception |
| Cleanup fails under the original deadline's second cancellation | Reader terminates before response; safe503; zero diagnostics |
| Ordinary reader error and successful label read | Existing safe503 and original closed successful response stay unchanged |
| Existing original-deadline/cleanup tests | Original budget, second cancellation, awaited cleanup and no late success still pass |

The new parametrized actual-ASGI test is
`test_cleanup_exception_never_reaches_asyncio_diagnostics[caller|repeated|timeout|deadline]`.
All four cases failed against the original runtime, then passed after the repair.
The tests capture and restore the test loop's diagnostic handler; production loop
logging is never suppressed. They also check task/result representations do not
expose the synthetic private error. The outcome repr hides both errors and rows.

## Exact commands and results

From repository root, using retained tools with no installation:

```sh
OWNER_PYTHON=platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python
OWNER_NODE=platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node
OWNER_GENERATOR=platform/deployment/.local/scaffold-application/proof-yc4xuk/root/platform/api-client/src/cli.mjs

PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$OWNER_PYTHON" -I -B -m pytest services/access/tests/test_actor_display.py -q -p no:cacheprovider -k cleanup_exception_never_reaches_asyncio_diagnostics
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$OWNER_PYTHON" -I -B -m pytest services/access/tests/test_actor_display.py -q -p no:cacheprovider
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 timeout 30s "$OWNER_PYTHON" -I -B -m pytest services/access/tests/test_capability_check.py services/access/tests/test_organization_check.py services/access/tests/test_people_setup_references.py -q -p no:cacheprovider
"$OWNER_PYTHON" -I -B services/access/export_actor_display_openapi.py --check
"$OWNER_NODE" "$OWNER_GENERATOR" --schema services/access/actor-display.openapi.json --output services/access/contracts/actor-display-generated --check
"$OWNER_NODE" node_modules/typescript/bin/tsc --ignoreConfig --noEmit --strict --skipLibCheck --target ES2022 --module NodeNext --moduleResolution NodeNext services/access/tests/actor_display_types.test.ts
"$OWNER_PYTHON" -I -B /tmp/kdg-actor-display-cancellation-diagnostic.py
```

Acceptance: four RED failures, then four GREEN passes (81 deselected).
Complete owner suite: **85 passed in5.06s**. Affected suites: **127 passed in3.92s**,
with one existing Starlette deprecation warning. Exporter/generator freshness and
strict TypeScript7.0.2 pass. Existing Python3.15.0 and dependencies stay pinned.
The original disclosure diagnostic now exits0 with caller cancellation preserved,
zero loop events and false for private-message disclosure. Independent BMAD oneshot
review found no supported findings and separately passed85 tests. No new deferral.

Retained custody: `/tmp/actor-display-cleanup-fix-e_ezl9lo/`. RED/GREEN JSON/logs,
pre-repair HTTP source and RED test source bind the failure to actual bytes.
`verification.json` records exact commands/tool results; named logs retain all final
checks. `original-diagnostic-green.json` and log record the exact replay; its fresh
safe result/source is `/tmp/kdg-actor-composition-diagnostic-f7_oc3i0/`.
Original failing planning evidence remains preserved at
`/tmp/kdg-actor-composition-diagnostic-yeqc5h4s/`.
`protected-before.json`/`protected-after.json` show12 unchanged active/schema/
generated/dependency files. `green-source/` retains the tested runtime/test pair;
`final-source/` and `final-source-manifest.json` bind finalized delivery documents.

## Scope and impacts

Runtime change: `actor_display_http.py`; tests: `tests/test_actor_display.py`.
All prior planning/history text remains preserved or explicitly marked historical.
This closes the owner prerequisite discovered during KDG composition planning;
it does not execute the planned KC consumer matrix or complete Story3.1.

Scaffold: owner-local task boundary, no generated/shared behavior changed; no new
promotion. Shared UI: none. Agent context: unchanged. Documentation: owner evidence,
KDG composition/readiness/handoff and BMAD spec. ADR: existing0023/0056 and transaction/
release safeguards suffice; no accepted ADR edits. No active app/client/schema,
credentials, native DB/migrations/grants, dependencies, services/resources, UI/Leave,
deployment/pilot/production/push or cleanup changes. Prohibited fixture not accessed.

Model observation: BMAD oneshot implemented inline on the existing coordinator;
model/usage/headroom unavailable. Review inherited coordinator capability. Test
times above are measured subprocess results; model-only elapsed time unavailable.
