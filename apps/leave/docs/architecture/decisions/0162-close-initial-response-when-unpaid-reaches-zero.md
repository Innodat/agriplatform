# ADR-0162: Close the Initial Response When Requested Unpaid Leave Reaches Zero

**Status:** Accepted  
**Date:** 2026-10-23  
**Scope:** Initially unpaid on-behalf requests awaiting the employee's response  
**Resolves:** The zero-unpaid applicability gate in
[ADR-0151](./0151-notify-pending-unpaid-changes-without-renewed-acknowledgement.md)  
**Complements:** [ADR-0088](./0088-employee-acknowledgement-for-on-behalf-unpaid-leave.md)
and [ADR-0154](./0154-reassess-finalization-when-blocking-condition-resolves.md).

## Decision

When an authorized allocation change reduces the current requested unpaid amount to
zero on an initially unpaid on-behalf request, close its outstanding initial employee
response requirement because no unpaid amount remains. Do not ask the employee to
acknowledge zero, record consent they did not give, or erase the initial handoff/history.

The actual resolving writer records the allocation and response-closure consequences
consistently with its required evidence, operation outcome and notification intent.
Reassess finalization using existing valid decisions and all current conditions under
ADR-0154. Approve/consume once only if every condition passes; otherwise remain pending
with its current reason. A closed response is not an approval decision.

If a later authorized change introduces unpaid leave again in that same approval cycle,
follow ADR-0151's explanation/notification rules without reopening the closed response
or creating renewed acknowledgement. A new resubmission or replacement cycle applies
its own initial submission rules. Ordinary own-request initial unpaid acknowledgement
and employee-only acknowledgement of an outstanding positive unpaid amount are unchanged.

Keep response/allocation/withdrawal/decision changes protected by current lifecycle,
revision and consequential-input contracts. A stale positive-amount response cannot
acknowledge a changed allocation or reopen closed work. Preserve actual change actor
and response-closure reason separately from any real employee acknowledgement.
Notification read state remains independent.

## Verification and impacts

Verify outstanding initial response changing from positive to zero, no fabricated
acknowledgement, retained history and employee/approver display, all decisions already
recorded versus another gate blocked, later same-cycle positive amount with notice only,
fresh-cycle initial rules, and concurrent/stale/retried allocation/response/withdrawal
with one-time accounting and truthful outcome. Bind exact evidence/schema/command/error
contracts and owner tests before readiness; no runtime pass is claimed here.

Reuse existing allocation/response/finalization/notification and current detail patterns.
No new permission, employee form, visible request status, manual completion or consent
workflow. Update Features, spine, UX, E5 command contract and actual 5.12/5.13/5.15/5.10-B
consumer/test ownership and planning checkpoints. Existing agent instructions suffice;
accepted predecessor ADRs remain unchanged. No implementation, runtime tests, migrations,
live grants, deployment or readiness authorization.
