---
title: 'Promote scoped operation locking for KDG writes'
type: 'feature'
created: '2026-10-23'
status: 'done'
route: 'oneshot'
baseline_commit: 'a0436ea675145f2449645eeb2849d90c837e8882'
context:
  - '{project-root}/apps/kdg-capture/AGENTS.md'
  - '{project-root}/platform/builder-cli/AGENTS.md'
---

<frozen-after-approval reason="user requests the next bounded KDG write/outcome prerequisite">

## Intent

Extend the managed bounded transaction-context prerequisite with the existing
organization/account OutcomeKey, stable lock-v1 key and transaction advisory-lock
adapter. Preserve exact historical lock compatibility without importing fingerprint
code or adding dependencies. The fixed validated ASCII tuple can use standard JSON
serialization with sorted keys; it is not a general canonical-JSON implementation.
Only scope/operation identity is hashed for lock selection, never command payloads.

Prove emitted behavior first with an observed acceptance failure, then focused tests
for all key dimensions, strict IDs/schema/command/context, exact bound advisory SQL,
remaining-budget caps, late/expired refusal and safe SQLSTATE errors. Only lock
acquisition55P03 is operation_busy; other SQL/configuration errors remain internal_error.
KDG owns handler command identity, verified authority and fixed organization policy.
The helper grants nothing and does not implement first-committed replay or receipts.

Keep source/tests synchronized through the existing preservation installer in the same
item, with a KDG-owned synthetic consumer and real rendered/installed tests. Preserve
the seven existing runtime primitives and historical examples/migration/native/Auth
inventories. Existing source-bound WRITE-context receipts remain historical when the
managed file inventory hashes change. No API startup/dependency/ADR change.

Synthetic local/CI only: no native connection/Docker/SQL execution or database/schema/
role preparation, no business table/API/editor, Leave, real accounts/access, production,
deployment/pilot/cleanup or fingerprints/HMAC. TypeScript7.0.2 and approved dependencies
remain. Full outcome atomicity, unique constraints, RLS, real lock timing/release and
Story1.2/operator/release readiness remain consuming gates; do not relabel old native
proof as new evidence. Bootstrap retry semantics are unchanged.

</frozen-after-approval>

## Implementation Notes

Small reversible extension of the proven helper/adoption; no intent gaps or external
effects, oneshot route. Dirty-tree preservation is already authorized. Baseline and
preexisting paths captured in /tmp/kdg-operation-lock-before.json. Change canonical
write-tools/transaction_context.py and test_transaction_context.py; sync KDG through
sync-kdg-write.mjs. Extend actual renderer acceptance and owner synthetic consumer.
Existing OutcomeKey/outcome_lock implementations and literal native lock vector supply
the compatibility reference. Record all five delivery impacts and exact evidence.


## Review Triage Log

Configured oneshot blind review completed; no configured layers skipped. Findings
were verified separately before grouping or correction.

| Finding | Verdict | Evidence / route |
| --- | --- | --- |
| 1. Late limit setup still dispatches lock | medium | Code checks budget before _limits and after advisory SQL, with no check between their responses. A late configuration response can therefore dispatch more work after expiry. Direct patch plus behavioral RED/GREEN. |
| 2. Missing enclosing transaction guard | medium | Calling a valid lock with an inactive or autocommit connection reaches SQL; this violates the adapter's documented enclosing-transaction requirement. Direct fail-before-SQL guard, demonstrated by synthetic calls. |
| 3. Supplied context may differ from installed context | low | The helper validates trusted input shape and key matching, not actual connection GUC identity; it is not an authority checker. Owner must reuse the same verified transaction context. Document that obligation explicitly and test KDG key/scope consistency; do not add a custom context registry or per-lock authorization query. |
| 4. SQL errors tested outside owner transaction | medium | Existing cases classify errors but cannot catch accidental success/continued work after a failure within the owner scope. Direct integration-test patch arms the failure after transaction entry and proves no COMMIT or later owner work. |
| 5. Key repr exposes identifiers | low | Default dataclass repr prints account/org/operation IDs while the neighboring context is redacted. Direct redacted repr and test; no runtime authority change. |
| 6. Compatibility program not retained | medium | The100-case stdin experiment passed but did not yet have a durable executable/input record. Retain the deterministic optional test program, run it, and record exact command/results. |
| 7. Final evidence/receipt incomplete | medium | Draft document promises completion records not yet present. Complete final results/source/log receipt and link it before final presentation. |

All survivors are direct local corrections or caller/test documentation. No new runtime
API, authorization mechanism or database operation is needed; no review finding deferred.


Final verification: canonical26/emitted26/owner4 synthetic tests PASS, builder75 PASS
16.245s with no failures/skips, strict TS7.0.2 and managed parity PASS. Reproducible
100-tuple JCS compatibility oracle PASS; historical lock literal unchanged. Review
REDs observed late limit dispatch and inactive/autocommit SQL before fixes; final
transaction integration tests prove no COMMIT/later owner work on error. Seven prior
runtime symbol ASTs and14 historical sources/inventories unchanged;101 preexisting
paths and original handoff suffix preserved. Documentation/receipt carry exact commands
and source/log bindings. Shared UI/context/ADRs unchanged; scaffold/tests and consuming
KDG updated together. No review finding deferred. No DB/native/external operation;
full outcome/replay/Story1.2/release gates remain. Scoped local commit only, no push.
