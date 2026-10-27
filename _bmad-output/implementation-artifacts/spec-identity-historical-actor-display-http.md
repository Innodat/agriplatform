---
title: 'Isolated Identity historical actor display HTTP candidate'
type: feature
created: '2026-10-27'
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: 29763767fc3bb2895fea2500283759975f826d81
context:
  - services/access/HISTORICAL-ACTOR-DISPLAY.md
  - platform/docs/development/bmad-codex-usage.md
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** KDG's audit IDs lack the Identity-owned display HTTP boundary needed
for permitted current retained labels.

**Approach:** Implement the agreed isolated synthetic owner candidate from the
[owner contract](../../services/access/HISTORICAL-ACTOR-DISPLAY.md), with explicit
configuration, injected read-only projection and separately generated wire types.
The user's “next” authorizes this selected ready scope and continuation.

## Boundaries & Constraints

**Always:** Follow the complete owner contract, HD-1–HD-5 and owner HD-7. Preserve
executor/initiator attribution and missing-versus-outage semantics. Verify actual
HTTP acceptance RED before implementation, then focused TDD. Three seconds cover
input/read/serialization/unwind; no hidden deadline reset. Dependencies stay pinned.
Preserve concurrent work and all retained evidence/resources.

**Never:** Mount in active `main.py`, change its OpenAPI/generated clients, implement
SQL/DB adapters, migrations/grants, real credentials/accounts, KDG composition/UI,
startup/browser/session/worker integration, deployment/push or resource cleanup.
Never access `apps/kdg-capture/migrations/tests/schema_fixture.py`. HD-6 and consuming
HD-7 remain outside this delivery; synthetic rows cannot prove native retention.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| Retained labels | Valid dedicated key/org and sorted actor IDs | Exact ordered resolved/unavailable results; labels may change after rename, IDs do not | 200 private/no-store |
| Service boundary | Missing/wrong/duplicate key or any Authorization | No body/projection disclosure; active/previous keys share exact org policy | 403 safe error |
| Disabled/configuration | All absent versus partial/reused/invalid config | Disabled denies before reads; invalid construction reveals safe identifier only | No secrets in repr/errors |
| Closed wire | Extra/query fields, malformed UUID/JSON/UTF-8, order/duplicates, count or streamed size excess | No projection invocation | 422 private/no-store |
| Owner integrity | Foreign/duplicate/extra rows, invalid names or iterator bounds | Reject whole batch; never invent absent label | 503 safe unavailable |
| Deadline/failure | Slow input/reader, exception, cancellation, oversized reply | Bounded execution with owned unwind; no partial output | Cancellation propagates; 503 for unavailability |
| Generated contract | Isolated candidate schema/types | Closed success/error unions and header security; freshness checks pass | No manual generated edits |

</frozen-after-approval>

## Code Map

- `services/access/HISTORICAL-ACTOR-DISPLAY.md`: authoritative wire/config/projection details, readiness and impacts; do not duplicate API specifications here.
- `services/access/capability_contract.py`: closed/duplicate-key patterns; existing decoder's 64 KiB/own timer cannot be reused unchanged.
- `services/access/people_setup.py`: nearby isolated caller/read-only conventions, not an authorization source for this operation.
- `services/access/export_openapi.py`: safe offline exporter pattern; preserve active export bytes.
- `platform/api-client/src/cli.mjs` and README: existing local generator, generated-file ownership and TS6 tool isolation; consumers retain TS7.0.2.
- `services/access/CURRENT_ACCOUNT_ACTOR_EVIDENCE.md`: retained owner Python executable, no installations or native operations required.

## Tasks & Acceptance

**Execution:**

- [x] `services/access/tests/test_actor_display.py`: retain missing-route POST404 RED and implement all matrix-row behavior tests with injected synthetic reader.
- [x] `services/access/actor_display_contract.py`: strict closed request/response/error DTOs and bounded decoder/row validation.
- [x] `services/access/actor_display_http.py`: isolated app/router factory, explicit redacted policy and absolute budget; no ambient environment or DB creation.
- [x] `services/access/export_actor_display_openapi.py`, `actor-display.openapi.json`, `contracts/actor-display-generated/`: owner-export/generate/check isolated wire contract.
- [x] `services/access/tests/actor_display_types.test.ts`: compile consuming examples and rejected invalid unions with TS7.0.2.
- [x] `services/access/HISTORICAL_ACTOR_DISPLAY_EVIDENCE.md`, owner contract and KDG handoff: exact commands/results/source custody, scope and impacts.
- [x] Complete formal review, triage and any required repairs; refresh evidence after repairs.

**Acceptance Criteria:**

- Given an unimplemented synthetic route, when the valid POST acceptance runs, then retain an actual 404 failure before implementing behavior.
- Given the implemented candidate, when the HD-1–HD-5/owner HD-7 matrix runs, then every row has executed passing behavioral proof and no native/consumer claim.
- Given original active files and dependencies, when final qualification completes, then their baseline hashes remain unchanged and generated files match their exporter/generator.

## Implementation Notes

Planning: no intent gaps or irreversible operations. New owner contract boundary is
consequential service work, so dispatch uses gpt-6.1-sol/high. Existing dirty main
contains authorized concurrent work; preserve it under prior handoff authorization.
User already approved contract/readiness and requested this implementation; no
repeated approval stop. Model/usage/headroom unavailable unless exposed by tools.

Tool discovery: prior evidence's Python lacks FastAPI. Use
`platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python`.
Node is `platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node`.
Installed generator entrypoint:
`platform/deployment/.local/scaffold-application/proof-yc4xuk/root/platform/api-client/src/cli.mjs`.
Compile with `node_modules/typescript/bin/tsc --ignoreConfig --noEmit --strict --skipLibCheck --target ES2022 --module NodeNext --moduleResolution NodeNext`.
Protected active/source/dependency hashes: `/tmp/actor-display-protected-before.json`.
Keep acceptance RED and final logs/source capsules under a dedicated retained `/tmp`
directory and record that directory in evidence. No test log may expose secrets.

## Spec Change Log

2026-10-27: implementation and documentation complete; formal review pending. Frozen
intent unchanged. Source/log custody: `/tmp/actor-display-20261027-pmvw6siz/`.

## Review Triage Log

2026-10-27: three independent layers completed against the isolated runtime/test/
generated diff. Blind hunter: no supported findings. Edge hunter: no findings.
Verification-gap: **medium, patch** — the second reader cancellation at the original
deadline lacked an exercised test; existing tests unwind within the reserve. Add
the focused over-reserve cleanup regression, proving safe503 and owned termination.
No API or production-code change is required; no new deferral.

## Verification

Retain RED/GREEN command logs and final test names/counts. Use retained owner Python
with `-I -B -m pytest ... -q -p no:cacheprovider` and no plugin autoload. Run new tests
first, then existing `test_capability_check.py`, `test_organization_check.py` and
`test_people_setup_references.py`. Run isolated exporter/client `--check`, strict TS7
consuming type check and protected-file hash comparison. Record actual executable
paths and commands in evidence. Do not run native/qualification/resource tools.

## Reviewed completion

One verification gap was patched with a targeted over-reserve cleanup test; no
production-code change or new deferral. Final parent qualification passes81 focused
and127 affected tests, exporter/generator freshness and strictTS7.0.2. Protected
active/dependency bytes are rechecked before commit. Logs/reports and final source
capsule: `/tmp/actor-display-20261027-pmvw6siz/`; see owner evidence for exact commands.
No service, native DB, real credential or consumer integration was activated.
