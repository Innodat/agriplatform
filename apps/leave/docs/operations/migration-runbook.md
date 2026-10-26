# Migration runbook

**Status:** Planning draft; tooling is not implemented.

E8 technical planning proposal, 2026-10-25: the
[owning import contract](../architecture/contracts/e8-import-cutover-and-qualification.md)
and [single review package](../../../../_bmad-output/planning-artifacts/e8-planning-review.md)
allocate exact package/plan/report evidence, actual owner adapters, protected apply/
resume, source eligibility and qualification. Accepted ADR-0170 binds pending-
workflow/notice and employee-unit behavior following user approval on 2026-10-25.
The accepted procedure below remains authoritative. No executable tool, email,
import, provider mutation or pilot activation was run by planning.

For consultants preparing and reconciling a client migration. Product requirements
remain in [features.md](../features.md), with delivery work tracked in
[implementation-plan.md](../implementation-plan.md).

MVP migration is consultant-operated. A general self-service import screen and
client-facing confirmation page are not planned for MVP. The procedure below is
the required design for the future import tool, not a claim that it exists today.

Consultant correspondence and client email-approval tracking remain outside the
Leave setup UI. Do not add an Awaiting client confirmation status or a standard
opening-balances checklist row to manage this process. The application shows actual
balances and detected data issues; the consultant retains exact-batch approval
evidence through the operational process below. No new application email flow is
required by this procedure.

## Establish what the source balances mean

Before preparing an import, record:

- The NGO, source system/files, and employees covered.
- The effective date and timezone represented by the opening balances.
- The balance unit and applicable employee schedules/standard-day conversions.
- Whether each source balance already accounts for future approved leave or
  pending reservations; do not assume all source columns use the same convention.
- Which historical, pending, and future approved requests will be transferred,
  including their source identifiers, statuses, dates, and recorded amounts.

Reconcile opening balances and transferred requests together. Future approved
leave or pending reservations must affect available entitlement exactly once.
Historical requests already reflected in opening balances must not be deducted
again merely because their history is imported. Preserve any required entitlement
period and expiry information; a single total may not describe the balance fully.

For example, a source shows **8 days** and **2 days of future approved leave**:

| Source meaning | Expected available balance after reconciliation |
|---|---|
| The 8 days are before accounting for that future leave | 6 days |
| The 8 days already account for that future leave | 8 days |

These examples assume no other transactions or calculation effects. Do not apply
a blanket subtraction or addition: document the source convention and derive the
opening entries and transferred-request effects using the application's ledger
rules. Resolve ambiguous source data with the client before applying the batch.

## Validate, review, and apply

1. Prepare documented input templates and an identified import batch. Validate
   memberships, request mappings, units, dates, and balance/request reconciliation.
2. Generate a preview and report showing the balance date, employee/type amounts,
   transferred requests, missing/rejected rows, and source-to-result differences.
   Report errors by employee and source row. Resolve blocking errors before apply.
3. The consultant sends that report to an authorized client contact. Approval or
   requested corrections may be supplied by email; no separate application sign-in
   or Confirm balances page is required.
4. Record the approving contact, approval evidence, and the exact batch/report
   approved. If the data changes, issue a revised report and obtain approval again.
5. Apply only the approved batch through supported, authorized application import
   contracts. Do not use ad hoc database edits. Prevent duplicate application of
   the same source records/batch and retain actor, batch, and result audit history.
6. Check the applied results against the approved reconciliation report and record
   discrepancies for resolution. Do not hide a mismatch by changing expectations.

## Cutover checklist

- Agree when the old system stops accepting changes and when Leave becomes the
  official record. Record the responsible consultant and authorized client contact.
- Record the source export timestamp and the agreed balance date; these may differ.
- Identify all changes made between the export and cutover, including requests,
  decisions, cancellations, employment changes, and balance adjustments.
- Reconcile those changes before going live. Where the approved batch changes,
  regenerate the report and obtain renewed email approval for the revised batch.
- Verify the final applied records against the approved reconciliation and confirm
  the operational handover with the client before treating Leave as authoritative.

These are consultant checklist items, not additional client application screens.

Manual employee and opening-balance entry remains available through the planned
normal application flows. Detailed cutover execution, rollback, and executable
import contracts still require delivery design and verification before a real migration.

## Accepted pending-work and recovery-unit behavior

[ADR-0170](../architecture/decisions/0170-imported-pending-work-and-resumable-employee-units.md)
was accepted with E8 planning on 2026-10-25. Pending source requests receive freshly
verified Leave approval cycles at controlled activation, with new route/initial
response/wait consequences disclosed in the exact approved report. External partial
decisions remain historical evidence. Do not replay old completed business notices;
release only current actionable pending work after authorized activation.

One employee's Leave opening/request/evidence envelope commits together. Successful
employees remain committed when another fails. Resolve original unit outcomes before
explicit retry; changed data/selection/route needs renewed report/email approval. Staged
records stay outside ordinary user economic/read/task/action scope until the approved
selection reconciles and activation is authorized. Support compatible source eligibility
before storing such records; follow controlled maintenance/recovery if needed.

These are accepted requirements for the future tool, not executable instructions or
permission for actual data import, emails, migration or activation.
