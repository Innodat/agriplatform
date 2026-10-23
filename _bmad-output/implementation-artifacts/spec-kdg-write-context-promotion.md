---
title: 'Promote bounded transaction context for KDG persistence'
type: 'feature'
created: '2026-10-23'
status: 'done'
route: 'oneshot'
baseline_commit: 'f02bf84b1a3d3281fb06e91aba01f0057216511c'
context:
  - '{project-root}/apps/kdg-capture/AGENTS.md'
  - '{project-root}/platform/builder-cli/AGENTS.md'
---

<frozen-after-approval reason="user requests the next KDG implementation step within the existing synthetic scope">

## Intent

Promote the already-proved neutral Budget/VerifiedContext/execute/transaction primitives
from the historical atomic_write example into a copyable scaffold template without
fingerprint, lock-key, receipt or domain dependencies. Prove generated behavioral tests
and a KDG-owned synthetic consumer before its first persistence/API implementation.
Use a separate managed write-tools root so existing database/native/Auth inventories
and historical examples remain unchanged. A verified-context shape does not establish
authority: KDG still owns current Access evidence, fixed organization and action modes.

Behavioral ATDD must fail on missing emitted behavior before implementation; focused
tests cover bounded positive settings, observation freshness, exact transaction-local
scope, nested/isolation/autocommit refusal, safe SQL/commit failures and late-commit
uncertainty. Reuse the approved retained Python/SQLAlchemy environment; no API dependency
change or startup integration. Synthetic adapters prove control flow only, not actual
PostgreSQL rollback, RLS, timeout or connection-pool isolation. Historical native proof
remains historical, not rerun evidence for this copy.

Preserve concurrent changes, historical evidence/resources and dependency baseline,
including TypeScript7.0.2. No native operations, provisioning, domain tables/routes,
Leave/editor, real accounts/access, deployment/production/pilot/cleanup or fingerprints/
HMAC. Story1.2 bootstrap retry semantics and full WRITE/release gates stay unchanged.

</frozen-after-approval>

## Implementation Notes

Small reversible promotion of existing primitives and generated tests, with no intent
gaps or external effects; oneshot route. User's existing dirty-tree preservation
authorization applies; snapshot /tmp/kdg-write-context-before.json. Keep historical
atomic_write.py, transaction_context.py and all migration/native inventories unchanged.
Canonical sources: templates/application/write-tools/transaction_context.py and
test_transaction_context.py. Add emission and installer-backed KDG write-tools sync;
extend real rendered/installed tests plus owner synthetic consumption. No generic
transaction engine or new business orchestration. Record scaffold/shared-UI/context/
docs/ADR impacts and exact commands/results in KDG evidence and next-session handoff.


ATDD observed renderApplication omit the helper before implementation. Extracted seven
symbols are AST-identical to the historical qualified example. Initial canonical/emitted
11 and KDG owner3 synthetic tests passed; review adds three explicit owner-SQL/deadline
cases, bringing generated tests to14. Existing database/native/Auth inventories and
historical examples remain byte-identical. Builder75/strict TS7.0.2 pass before review;
final affected verification follows below. No DB/Docker/provider work occurred.

## Review Triage Log

Configured oneshot blind review completed; no configured layers skipped. Every finding
was independently assessed against source/callers and the existing delivery commands.

| Finding | Verdict | Evidence / disposition |
| --- | --- | --- |
| 1. Retained Python hardcoded | low | Focused rendered test inherited an existing local prerequisite, limiting independent execution elsewhere. Direct patch: optional SCAFFOLD_WRITE_TEST_PYTHON interpreter selection and explicit dependency guidance; default approved environment unchanged. Other historical suite prerequisites remain. |
| 2. Generated README lacks guidance | medium | New emitted files had no generated-app command/SQLAlchemy/PostgreSQL17/qualification explanation. Patch owning README template; real renderer tests cover emitted content. |
| 3. execute failure untested | medium | fail_execute raised during transaction setup, so removing execute's error adapter could evade it. Add failure specifically on owner SQL, assert closed error and no COMMIT. |
| 4. shrinking waits untested | medium | Constant-clock tests did not distinguish a refreshed per-statement timeout. Add two owner statements with an advanced clock and assert smaller positive settings under original budget. |
| 5. late SQL response untested | medium | Late commit test did not protect execute's separate post-response check. Add late owner SQL result with execution_timeout and no COMMIT. |
| 6. import guard ignores Import nodes | low | Forbidden plain import statements bypassed the regression guard. Direct patch checks Import aliases and qualified prefixes alongside ImportFrom. |
| 7. KDG suite not in consuming command | false | Both migrations/README.md and this delivery evidence already list P -I -B apps/kdg-capture/write-tests/test_owner_context.py, and the command ran3 tests successfully. There is no requirement to run optional SQLAlchemy owner tests in the dependency-minimal API environment or generic builder suite; reject. |
| 8. evidence omits results | medium | Draft evidence listed commands without completed results. Patch final evidence with exact results/logs and source-bound receipt; do not describe intended checks as passes. |

All surviving findings are direct test/documentation corrections without a new runtime
surface. No review finding deferred. Shared UI/context/accepted ADRs unchanged; scaffold
and generated tests updated in the consuming delivery, rather than deferred to app end.


Final verification: canonical14/emitted14/KDG-owner3 synthetic tests PASS; full builder75
PASS9.586s; explicit interpreter focused2 PASS; strict TS7.0.2 and managed parity PASS.
No failures/skips in final affected suites. Evidence and receipt carry exact commands,
results and source/log bindings. All7 extracted symbol ASTs match the historical native-
qualified example;11 protected source/manifest files unchanged;100 preexisting paths
preserved. Current proof is synthetic only. No review finding deferred. Scoped local
commit only; no push, external operation or native resource change.
