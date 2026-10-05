# ADR-0045: Expense Preproduction History Scope

**Status:** Accepted

**Date:** 2026-10-01

**Supersedes in part:** [ADR-0042](./0042-person-account-employment-and-legacy-adoption.md),
only its requirement to preserve/migrate historical Expense receipt/purchase mappings.

## Decision

The user confirmed that Expense/Receipts is not in production and that old receipt
records need not be catered for. Do not require a historical Expense receipt/purchase
data conversion, record-mapping reconciliation or old receipt-client compatibility
layer as part of the shared identity/Leave path. Existing Expense code remains useful
design evidence; its future adoption can target the chosen platform contract directly.

Shared identity records and other consumers are separate concerns. Preserve supported
Access/PtS/Content contracts and deliberately adopt existing shared identities where
required. This scope reduction does not authorize dropping a shared database or
removing another application's data. No data deletion or reset is performed here.

The internal operation outcome records previously called operation receipts are
unrelated to the Expense application. Leave has none to migrate before first delivery.
Its implementation still needs duplicate-safe retries and must preserve recognition
of records it creates after delivery, including across key rotation/restarts. Call
these operation outcome records in user-facing planning discussions to avoid confusion.

## Impacts

- Planning/docs: remove historical Expense-data adoption as a Leave prerequisite;
  retain shared identity and supported-consumer compatibility gates.
- Scaffold: no legacy Expense receipt adapters/fixtures required; forward operation
  recovery and compatible shared-client patterns remain.
- Shared UI/agent context: no new components or generic instructions required.
- Acceptance: verify the new Expense model when adopted; no old receipt-history
  conversion test is required. Leave retry evidence remains under ADR-0012/0033.
- Accepted predecessors are unchanged. No application implementation, database change
  or readiness approval is created by this decision.
