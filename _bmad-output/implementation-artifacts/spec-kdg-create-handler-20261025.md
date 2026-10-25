---
title: 'KDG protected create and stored-target retry handler'
type: 'feature'
created: '2026-10-25'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

Implement an unmounted KDG create/retry handler that parses the current create command, verifies current protected Access evidence over HTTP outside transactions, then executes the existing bounded owner transaction. Verify create.all first, selecting create.assigned only after confirmed access_denied; unavailable or malformed evidence never falls back. Both require own-account scope and current account/durable actor/membership evidence. Privately find an existing outcome under its operation lock and authorize its actual stored owner/child, including current same-membership assignment for assigned authority, before returning the original receipt. Fresh commands consume the existing create body. Return no receipt before transaction commit and final deadline checks. Preserve ordinary inactive-child compatibility and no incoming answer/version/eligibility checks on committed replay.

All qualification is synthetic HTTP plus recorded connection behavior. No mounted write API, database migration/data mutation, real access/accounts, deployment, provisioning, cleanup, Leave/editor or production. Preserve concurrent work, historical evidence/resources and dependencies including TypeScript7.0.2; fingerprints/HMAC stay deferred. Native durable commit/lost-response/concurrency and ADR-0020 release gates remain required before activation.

</frozen-after-approval>

## Implementation Notes

- No intent gaps or irreversible work. Small code-only owner boundary: write-candidate/capture_create_handler.py, behavioral write-tests/test_capture_create_handler.py and new evidence/handoff. Context/main HTTP policy, owner create/outcome adapters and contracts are the code map. No new generic runtime framework, route, migration, dependency or permission.
- Reuse strict Context base fields with an exact-create permission override, protected transport validation patterns, shared Budget/VerifiedContext identity from capture_create.write and existing fresh body unchanged. Starlette's existing worker adapter runs synchronous SQL without blocking the event loop or abandoning the worker on ordinary cancellation. Caller provides one exclusive already-open bounded connection with no transaction; connection acquisition/release and HTTP header multiplicity remain embedding responsibilities before mounting.
- One total3-second external authorization window within original10-second request budget; response max16384 bytes, duplicate keys/unsupported encoding/redirects/unknown evidence fail closed. Checked-at must be within the actual check window; local execution starts within1second. No network under local locks. Confirmed all denial permits only the same-org assigned capability check.
- Replay current authority is checked on stored capture owner and child, never received IDs. Current assigned checks active assignment/current membership under the shared child lock; all remains own-author. This follows contracts.md:45,618,665 current authority rule; GET own-read recovery after assignment/create loss stays a separate boundary.
- Existing body reacquires the operation lock/rechecks absence for fresh actions; PostgreSQL transaction advisory locks are reentrant and this avoids risky refactoring. Do not bypass its checks.
- Scaffold/shared UI: domain-specific orchestration stays app-owned; existing generated helper and template remain unchanged, parity checked. Agent context: no generic change. Docs: source-bound qualification and prepend-only handoff. ADR: existing decisions suffice. No active migration or API dependency changes.

- Implemented one owner module and18 focused tests; all75 write tests pass, managed helper/scaffold parity passes. No database/Docker/HTTP service operations occurred; transports are MockTransport and connections record calls only.
- ATDD initial missing-handler import failed. Focused freshness test then failed because cleanup delay refreshed the monotonic observation; capture it at complete evidence validation before response/client close, and retain it through worker dispatch. Regression now refuses before SQL.
- Worker tests stall in restricted sandbox (same environment limitation as previous synthetic ASGI work); interrupted only that session, ran bounded synthetic tests with escalation. No real network or connection. Isolated helper-time patch avoids perturbing asyncio's clock diagnostics.

- Review exposed real direct-task-cancellation and shared worker-limiter deadline gaps. Both focused regressions failed before fixes: canceled caller finished while worker owned the connection; saturated limiter retained request beyond its shortened budget. Use existing AnyIO fail_after for admission and retain/shield/await the worker on repeated direct cancellation. No new public API or framework. Both regressions pass.
- Added combined capability deadline, late-commit/original-receipt retry without duplicate inserts and driver-autocommit preflight coverage. Distinct capture/operation identity remains the already-selected cross-field structural wire requirement, now explicitly tested for an existing outcome too; incoming fresh semantics remain skipped on replay.
- Scaffold assessment: existing transaction template is synchronous; jwt_optional offloads token decode, without exclusive DB ownership. No existing async SQL scaffold consumes this app-specific bridge; its focused fixture remains with the actual consumer instead of introducing unused runtime infrastructure.

- Final verification:80 affected tests PASS (23 handler cases plus57 existing write tests), scaffold/helper parity PASS. Reviewer independently reran both worker regressions:2 PASS, both findings addressed. No native database or Docker operation was run. All105 preexisting dirty/untracked files retained byte-identical; handoff preserves exact historical suffix and resolved TypeScript7.0.2 unchanged.

## Review Triage Log

1. high / patch — Direct and repeated asyncio Task cancellation released the caller while the worker still owned the connection. Reproduced with failing test, fixed by retaining/shielding/awaiting worker completion before propagating cancellation. Reviewer rechecked and independently passed the regression.
2. medium / patch — Shared worker limiter admission was unbounded. Reproduced deadline failure under held limiter, fixed using AnyIO fail_after with original remaining Budget; timeout prevents any later SQL. Reviewer rechecked and independently passed the regression.
3. false / reject — Distinct capture/operation UUIDs are the existing global cross-field wire requirement (contracts.md:336 and explicit frozen Intent notes), so the structural guard precedes lookup for fresh and replay requests. Its location outside CreateCommand does not make it fresh domain authorization. Added explicit existing-outcome regression and documentation; answer/child/version/eligibility semantics still remain after absence.
4. medium / patch — Single-request timeout case did not protect combined fallback duration; added delayed confirmed-all denial plus assigned response whose combined duration exceeds the one window.
5. medium / patch — Commit-failure test did not exercise original receipt recovery; added recorded commit-success/late-ack error then changed-body retry returning original receipt with no new inserts. Native commit/lost-response qualification remains explicitly unclaimed.
6. low / patch — Early driver-autocommit refusal lacked direct coverage; added invalid_write_context before HTTP/business SQL, preserving helper's additional safeguards.
