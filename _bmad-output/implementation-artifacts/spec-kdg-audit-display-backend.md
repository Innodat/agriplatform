---
title: 'Bounded KDG backend audit display composition'
type: feature
created: '2026-10-28'
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: c88c753fc46d6d5caf296ef3b2ec87370b7f8dc1
context:
  - apps/kdg-capture/docs/audit-display-composition.md
  - services/access/HISTORICAL-ACTOR-DISPLAY.md
  - platform/docs/development/bmad-codex-usage.md
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** KDG's authorized audit metadata lacks permitted display labels.
**Approach:** Implement the [defined composition](../../apps/kdg-capture/docs/audit-display-composition.md)
as an isolated backend candidate. The user's “next” selects this bounded delivery;
the Identity diagnostic prerequisite is repaired. No new product choices are needed.

## Boundaries & Constraints

**Always:** Existing audit page/cursor semantics, current fixed-org read.all before
SQL and final matching authorization after label work, exact server-selected actor
IDs, released transaction/connection before external lookup, one original10s Budget.
Follow the complete adopted composition/Identity contracts, privacy and owned unwind.
Retain actual missing-route HTTP404 RED before implementing; focused TDD follows.

**Never:** Modify legacy audit APIs/DTOs/exports or generated managed files by hand;
nest a route/execute that restarts the Budget; import Identity server implementation;
perform cross-owner SQL, cache, UI/browser/session/worker/startup activation, native
DB/Docker/migrations/grants, real credentials/accounts, dependency changes, deployment,
push or cleanup. Never access `apps/kdg-capture/migrations/tests/schema_fixture.py`.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| Permitted cross-owner page | Valid bearer, exact all-read, synthetic rows | Unchanged AuditPage plus exact ordered server-selected labels | Private/no-store JSON |
| Input/access/read failure | Unknown/duplicate selectors, body, invalid cursor, denial or malformed audit | No Identity disclosure or old-page fallback | Existing KDG safe pairs |
| Valid unmapped label | Successful exact Identity batch omits no requested ID | Loaded union preserves per-ID unavailable | Never guess names |
| Bad/unavailable Identity | Invalid org/IDs/order/schema/headers/encoding/size or dependency failure | Whole-label degradation only after final authority succeeds | No raw upstream body |
| Authority changes during lookup | Final check denied/unavailable or binding changes | No aggregate publication | Current safe auth error/observation-expired |
| Budget/cancellation | Slow read/input/lookup/cleanup/serialization | Original deadline and owned connection/transport unwind; no diagnostic leaks | No late or detached success |
| Max bounds/export | 100events/203actors, escaped names/cursor |64/256/321KiB actual limits; isolated schema/types | No trimming/pagination changes |

</frozen-after-approval>

## Code Map

- `write-candidate/audit_http.py`: reuse `_engine`, `_acquired_transaction`, `failure`, and `PrivateResponses`; leave source unchanged.
- `audit_read.py`: exact `AuditPage`, parse_query/position and `_transaction/_page`; original `execute` creates a Budget and must not be nested.
- `capture_create_handler.py`: `_complete_worker` owns cancellation-safe non-raising worker outcome; inherited `_authorize(token,budget)` supports the original Budget.
- `write-tests/test_audit_http.py`: existing fake Pool/Connection/Access fixture and actual ASGI acceptance; `test_audit_read.py` validates released transactions.
- `services/access/actor_display_http.py`: isolated repaired owner, used only over synthetic HTTP in tests, never imported by KDG runtime.

## Tasks & Acceptance

All new app-relative files below live in `apps/kdg-capture/`.

- [x] `write-tests/test_audit_display*.py`: real404 RED; KC-1–KC-9 backend subset, including synthetic Identity HTTP; preserve original tests.
- [x] `write-candidate/audit_display.py`, `audit_display_http.py`: closed aggregate, exact selection and original-budget orchestration/final authorization using existing seams unchanged.
- [x] `write-candidate/identity_actor_display.py`: explicit fixed HTTPS/key policy, strict bounded streaming validation, owned timeout/cancellation and safe whole-label degradation.
- [x] `write-candidate/audit_display_openapi.py`, `export_audit_display_openapi.py`, `audit-display-openapi.json`, `contracts/audit-display-generated/`: owner-export/generated candidate only.
- [x] `write-tests/audit_display_types.test.ts`: strict generated TS7 accepted/rejected consuming shapes.
- [x] `docs/AUDIT_DISPLAY_BACKEND_EVIDENCE.md`, `docs/evidence/`, contracts/composition/readiness/handoff: exact source-bound commands/results and impacts.

Given the isolated candidate, when backend KC cases run, then current selection,
released storage, original Budget and final authority are exercised with passing
runtime tests and matching types. Browser KC-7/9 portions remain explicitly later.
Given prior source/dependencies, when qualified, then protected hashes stay identical.

## Implementation Notes

No intent gaps/irreversibles; consequential HTTP composition warrants Sol High dispatch.
Prior dirty concurrent work is authorized and preserved; do not commit unrelated work.
No existing source extraction is required. If a new extraction proves necessary,
characterize before refactoring and report it. Model/usage/headroom unavailable.

Tool paths: Python `platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python`;
Node `platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node`;
generator `platform/deployment/.local/scaffold-application/proof-yc4xuk/root/platform/api-client/src/cli.mjs`.
Evidence directory and protected hashes are named by `/tmp/kdg-audit-display-evidence-path`.
Retain bounded test logs/capsules there. Production and test diagnostics must redact
ordinary asynchronous cleanup failures, including Python3.15 shield callbacks.

## Spec Change Log

## Review Triage Log

2026-10-28: blind hunter found no supported findings; its independent test attempt
used a root environment without SQLAlchemy, while parent qualification uses the
retained owner interpreter and passed133 cases. Edge hunter returned no findings.
Verification-gap: **medium, patch** — independent header-only actor selection and
empty-continuation assertions were absent. Existing expected IDs reused the helper
or occurred in events. Add exact literal fixture-ID assertions over real HTTP;
no runtime/public API change or new deferral is required.

## Verification

New pytest cases first (`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`, Python `-I -B -m pytest`,
`-q -p no:cacheprovider`), then affected audit HTTP/read/contract suites and Identity85
regressions. Use real synthetic owner HTTP for cross-owner proof, injected Access/SQL;
no native claim. Check new and old audit export/type freshness, strictTS7 and protected
sources. Generator subprocess may need approved escalation after sandbox EPERM.
Existing TestClient regressions may need escalation; bound attempts and preserve logs.
Record actual commands/counts and qualification limits, not merely agent reports.

Parent verification:133 tests and40 subtests pass across19 new cases,29 existing
audit cases and85 Identity cases. New/old exports, strictTS7 and generated freshness
pass;388 protected source/dependency files unchanged. Parent inspected actual RED
and qualification output plus runtime/test/export diff. This was the pre-review result.

Final reviewed completion: the header-only/empty-continuation HTTP regression closes
the verification finding. Parent final qualification passes134 tests and42 subtests
(20 new,29 existing audit,85 Identity), with no runtime repair or new deferral.
All three review reports are retained. Earlier133/40 results remain historical.
Export/type checks are source-bound to unchanged runtime/schema/generated bytes;
only the new independent Python regression changed after those checks. No active,
browser, native or resource qualification is claimed. Selected implementation:
gpt-6.1-sol/high; actual model/usage/headroom unknown. Approval/queue waits were
separate from measured pytest runtime. Evidence: `/tmp/kdg-audit-display-20261028-zt4h9kvv/`.
