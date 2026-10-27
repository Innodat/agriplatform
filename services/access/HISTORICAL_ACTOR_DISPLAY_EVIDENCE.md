# Historical actor display: isolated synthetic owner evidence

2026-10-27; baseline `29763767fc3bb2895fea2500283759975f826d81`.
Implementation, owner verification and three-layer review complete. The
[owner contract](HISTORICAL-ACTOR-DISPLAY.md) remains authoritative. This candidate
is not mounted by active `main.py` and does not implement a database adapter or KDG
composition. Every projection row below is injected synthetic evidence.

## Executed requirement coverage

| Contract | Executed proof |
| --- | --- |
| HD-1 | Actual missing-route POST404 RED precedes implementation. Synthetic retained/removed-account, System, Migrate and service names resolve; rename changes the label while exact actor IDs/order remain. |
| HD-2 | Missing/wrong/duplicate service key and any Authorization header deny before body/projection reads. Disabled configuration denies; partial/malformed/reused keys fail safely. Active/previous keys share the same organization policy. |
| HD-3 | Omitted projection IDs produce only unavailable. No account/person/member/eligibility input or lookup exists; same-UUID account inference and synthetic replacement identities are unavailable to this boundary. |
| HD-4 | Closed JSON, duplicate members, UTF-8/UUID/order/count/streamed 16 KiB bounds, 203-ID acceptance and invalid projection rows/names execute. Output preserves exact requested IDs/org; lazy iteration is bounded and closed. Legal 256-scalar/four-byte names pass. |
| HD-5 | Slow input/read use one absolute deadline; the actual default three-second timeout executes. Serialization deadline, dependency exception, oversized serialized reply and repeated cancellation execute. Owned read cleanup is awaited; cancellation propagates even if the reader returns after cancellation. Errors are safe, with no partial success; all operation outcomes use private/no-store. |
| Owner HD-7 | Isolated OpenAPI has one operation, header API-key security, closed success/error models and discriminated labels. Existing pinned generation, freshness and strict TS7 accepted/rejected examples pass. |

The reader must cooperate with cancellation and keep its own read/unwind bounded.
The implementation reserves 100 ms inside the original three seconds for unwind,
without restarting the deadline. Synchronous injected iterator/serializer code
must also be bounded: Python cannot preempt arbitrary blocking callback code;
deadline checks reject late success. No native implementation is qualified here.

HD-6 and consuming HD-7 remain outside this increment. These results do not prove
actual actor retention after Auth removal, SQL privileges, live caller authority,
consumer response validation, current KDG authorization, UI/session behavior or
installed-device operation.

## Exact tools and commands

Run from repository root. Existing versions remained pinned; nothing was installed.

```sh
OWNER_PYTHON=platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python
OWNER_NODE=platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node
OWNER_GENERATOR=platform/deployment/.local/scaffold-application/proof-yc4xuk/root/platform/api-client/src/cli.mjs

PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$OWNER_PYTHON" -I -B -m pytest services/access/tests/test_actor_display.py -q -p no:cacheprovider
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 timeout 30s "$OWNER_PYTHON" -I -B -m pytest services/access/tests/test_capability_check.py services/access/tests/test_organization_check.py services/access/tests/test_people_setup_references.py -q -p no:cacheprovider
"$OWNER_PYTHON" -I -B services/access/export_actor_display_openapi.py
"$OWNER_PYTHON" -I -B services/access/export_actor_display_openapi.py --check
"$OWNER_NODE" "$OWNER_GENERATOR" --schema services/access/actor-display.openapi.json --output services/access/contracts/actor-display-generated
"$OWNER_NODE" "$OWNER_GENERATOR" --schema services/access/actor-display.openapi.json --output services/access/contracts/actor-display-generated --check
"$OWNER_NODE" node_modules/typescript/bin/tsc --ignoreConfig --noEmit --strict --skipLibCheck --target ES2022 --module NodeNext --moduleResolution NodeNext services/access/tests/actor_display_types.test.ts
```

Interpreter discovery observed FastAPI0.143.0, Pydantic2.14.1, HTTPX0.28.1 and
pytest9.1.1. Consumer compiler remains TypeScript7.0.2; generator uses its existing
isolated pinned TypeScript6.0.3 recipe and @hey-api/openapi-ts0.99.0.

The focused command first failed **404 versus expected200**, then passed76 tests,
then passed **80 tests in3.77s**. Parent independent final run passed **80 in3.75s**.
Affected unchanged HTTP suites passed **127 tests, one existing Starlette
deprecation warning, in3.24s**, exit0, parent tool session48192. That invocation's
output was observed directly; no saved full regression log or log digest is claimed.
Exporter and generator checks passed; strict TS7 check exited0 without diagnostics.

TestClient stalled within the sandbox; the affected sandbox subprocess was killed
after15s and its failure retained. The required escalated retry initially waited
for approval and was aborted after204.6s, with no executed result claimed. Parent's
bounded approved outside-sandbox command above then completed the existing suites.
No existing test was replaced to obtain a pass. New tests use HTTPX ASGITransport.
The generator subprocess returned sandbox EPERM; generation and freshness passed
outside the sandbox with the same installed tool and schema. No network fetch ran.

## Retained source and result custody

Dedicated retained directory: `/tmp/actor-display-20261027-pmvw6siz/`.

- `acceptance-red-source.py`, `acceptance-red.json` and `acceptance-red.log` bind
  actual POST404 failure to its pre-implementation source and exact argv.
- `focused-initial.log` and `focused-second.log` retain76/80-test observations;
  `affected-sandbox.log` records the bounded failed sandbox attempt.
- `parent-verification.json` records exact final focused/exporter/TS argv and log
  hashes. Parent generator freshness independently returned exit0 and
  `api_client_current` in tool chunk92710c; no saved log/hash is claimed for it.
- `implementation-verification.json` records earlier executed command observations
  and source/log hashes, distinguishing retained logs from tool-only output.
- `source/` and `source-manifest.json` capture final implementation/generated/docs
  bytes and SHA256 values. Later review repairs require a new capsule; preserve this
  one and the original RED evidence.
- `protected-comparison.json` checks the nine original active/runtime/client and
  dependency hashes against `/tmp/actor-display-protected-before.json`. All nine
  match. Parent separately confirmed the same nine hashes.

No native/qualification/resource tools ran. Existing concurrent work and retained
resources remain preserved. The prohibited KDG schema fixture was not accessed.

## Impacts and handoff

Scaffold: no promotion for this owner-only first consumer; revisit proven neutral
patterns with their consuming story. Shared UI: none; localized absent/outage labels
remain KDG-owned. Agent context: existing boundaries suffice, unchanged. Docs: this
evidence, owner status, delivery spec and KDG next-session handoff. ADRs:
0056/0022/0023/0031 apply; no accepted decision changed and no new ADR is needed.

Native adapter/function/role, controlled migration and release compatibility/recovery,
real credential provisioning/rotation, active mount, browser/session/worker adoption,
KDG combined DTO/budget/authorization and deployment remain separate work.

Model observation: delegated implementation selected gpt-6.1-sol/high; actual model,
usage/headroom and model-only elapsed time unavailable. One sandbox retry was required
for generation, and affected TestClient execution required the parent bounded retry;
the approval wait is distinct from model/test execution. Formal review is complete.

## Final reviewed qualification

All three independent review layers completed. Blind and edge reviewers returned
no supported findings. The verification reviewer identified one missing over-reserve
cleanup test; it was added without production-code changes. The new regression
proves the reader receives a second cancellation at the original deadline and is
terminated before response headers. No open finding or new deferral remains.

Final parent checks: **81 focused tests passed in 7.12s**, **127 affected HTTP tests
passed in 14.68s** (one existing Starlette deprecation warning), isolated exporter
and generator freshness pass, strict TS7.0.2 compile passes. Runs overlapped, so
these test times include contention. Exact commands, tool results and final logs
are retained in `final-verification.json`, `focused-final.log`, `affected-final.log`,
`export-final.log`, `generator-final.log` and `types-final.log` beneath the directory
above. `parent-final-verification.json` preserves the initial return before the
regression subprocess completed; `final-verification.json` includes its completion.
The original pre-review capsule stays retained; final source custody is captured
separately in `final-source/` and `final-source-manifest.json`.

Review reports: `review-blind.md`, `review-edge.md`, `review-verification.md`.
The delivery spec records the individual verification finding's medium/patch triage.
Next close the KDG composition contract and combined DTO/byte budget before its
synthetic consuming implementation. No active mount, native or real-authority
readiness follows from this delivery.
