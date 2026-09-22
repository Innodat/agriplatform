# ADR-0112: Revalidate Calculation Inputs at Confirmation

**Status:** Accepted  
**Date:** 2026-09-22  
**Complements:** Existing fresh-data, transaction and reviewed-version safeguards

## Decision

At consequential confirmation, verify the relevant policy, calendar, employment and
other calculation inputs as well as the employee balance and reviewed record.
A version check on the request alone does not establish that related inputs remain
valid. Apply the existing rules for selecting the applicable policy version; do not
silently replace a submitted request's snapshotted policy with the latest policy.

If applicable inputs changed since preview, recalculate. Require renewed confirmation
when duration, paid/unpaid allocation or another consequential reviewed detail changes.
Return an updated review while preserving entered information; do not commit the
outdated action. If the change has no consequential effect and authorization and
other validation still pass, proceed without an unnecessary extra confirmation.

Protect the final verification/calculation and commit against concurrent relevant
configuration changes. All writers of relevant configuration must participate in
the selected consistency mechanism; an employee balance lock alone is insufficient.
The concrete dependency revision/locking scheme belongs in affected technical stories,
which must demonstrate that inputs cannot change unnoticed between validation and
commit. Do not implement a broad lock of unrelated NGOs or employees.

Example: a calendar change makes a five-day draft consume four days. Show the revised
four-day result and ask the employee to confirm again. A calendar change outside the
request dates with no other effect does not require another confirmation.

## Impact and verification

- Acceptance: changed calendar or applicable policy between preview and submission;
  changes racing final validation; changed and unchanged outcomes; preserved form
  input; no stale allocation committed; existing policy snapshot semantics retained.
- Scaffold/shared UI: reuse current review/conflict patterns; calculation dependency
  selection remains Leave-specific, with no new administrator control.
- Agent context: existing transaction and current-data guidance suffices.
- Documentation: requirements, tracker and UX synchronized.
- ADR: additive; accepted predecessors unchanged.
- Planning only; no transaction code, locks or runtime UI implemented.
