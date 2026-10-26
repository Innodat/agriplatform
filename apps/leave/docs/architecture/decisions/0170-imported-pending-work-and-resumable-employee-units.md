# ADR-0170: Imported Pending Work and Resumable Employee Units

**Status:** Accepted — user approved E8 and both choices on 2026-10-25
**Date:** 2026-10-25
**Complements:** [ADR-0007](./0007-required-approval-and-automatic-decisions.md),
[ADR-0107](./0107-corrected-balances-preserve-decision-evidence.md),
platform [ADR-0012](../../../../../platform/docs/architecture/decisions/0012-operation-identity-idempotency-and-tracing.md)
and [ADR-0020](../../../../../platform/docs/architecture/decisions/0020-safe-schema-changes-and-release-recovery.md)
**Implementation/readiness:** Not authorized

## Context

The accepted consultant migration runbook requires exact-batch email approval,
source/request/balance reconciliation, duplicate prevention and export-to-cutover
reconciliation. It does not decide whether source pending approvals bind new Leave
work, or whether successful units survive a different employee's failure.
The user approved the complete E8 package and both choices on 2026-10-25.

## Decision

1. **Pending imports start a freshly verified Leave approval cycle at controlled
   activation.** Explicitly show old source status/steps, current target route, initial
   employee response and waiting-clock consequences in the client-approved report.
   Preserve source decisions as historical external evidence; they do not become
   binding local approvals. No silent rerouting or proxy acknowledgement. Existing
   authorized automatic-decision rules remain available only when freshly valid.
   Completed source history does not replay old approval/rejection/cancellation or
   adjustment notifications. Pending current response/approval notices are held until
   approved activation, then use the ordinary Leave outbox/current authority/dedup rules.
2. **Apply in atomic employee units, with explicit resumable batch progress.** All Leave
   openings, imported requests and their required local effects for one employee commit
   together. Successful employees remain committed if another fails. Stop/reconcile/
   resume against actual original unit outcomes; never claim the entire batch or several
   service owners are one transaction. No imported selection becomes ordinary actionable
   work until the exact approved selection is reconciled and its activation is authorized.

The activation eligibility is narrow import-source provenance, not a new application
status, universal draft system or background job. Staged imported rows have no ordinary
end-user detail/task/action visibility until eligible; scoped operator reconciliation
uses the explicit import surface. The actual E5 read/finalization and E7 consumers must
respect this eligibility. Deliver supporting consumer compatibility before creating
such rows; if previous-version compatibility cannot be preserved, use P-0020's explicit
maintenance/recovery path. No reader may silently ignore an imported-source hold.

Recheck authority, route/input revisions and required initial-response/gate predicates
at activation. A materially changed target route or approved plan requires a revised
report and renewed client email approval, not silent change or fabricated consent.
No waiting clock or escalation starts while imported work is deliberately unavailable;
record the actual activation instant as the new cycle's actionable origin while retaining
original source submission/wait evidence separately. Imported approved records retain
explicit source approval provenance rather than new invented human decisions.

## Alternatives considered

- Treat old partial approvals as binding current decisions: requires verified compatible
  authority/route/response evidence beyond the selected conservative migration path.
- Replay historical notices or expose pending tasks during partly applied migration:
  produces stale or incomplete actionable work before the client-approved handover.
- One transaction across all employees/owners, or auto-delete successful units on a later
  failure: conflicts with bounded owner transactions and immutable/recoverable evidence.

## Impacts and verification

Features, written UX, migration runbook and the owning import contract adopt this decision.
Existing accepted decisions are unchanged. Client email approval still remains outside
Leave UI; no synthetic accounts, grants, approver identity or direct source-table writes.

Scaffold: reuse actual bounded command/recovery/native fixtures, not a migration engine.
Shared UI: no new client import/approval screen. Agent context: current rules suffice.
Docs: exact batch/provenance/route/unit/activation evidence and owner mapping. ADR:
these two accepted choices bind the import behavior left open by the original runbook. 8.3–14 own
source-net/gross, stale route, missing response, partial-unit failure, lost response,
source duplicate, staged visibility and activation/notification compatibility oracles.
No import, email, migration, grants, activation or runtime test was executed here.
