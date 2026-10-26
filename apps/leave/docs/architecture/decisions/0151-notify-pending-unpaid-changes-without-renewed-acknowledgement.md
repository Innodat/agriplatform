# ADR-0151: Notify Pending Unpaid Changes Without Renewed Acknowledgement

**Status:** Accepted  
**Date:** 2026-10-21  
**Scope:** Later allocation changes to pending requests, including increased unpaid leave  
**Supersedes in part:** [ADR-0032](./0032-protected-reservations-and-explained-changes.md),
[ADR-0054](./0054-administrative-correction-notifications.md),
[ADR-0069](./0069-submission-summary-and-unpaid-acknowledgement.md),
[ADR-0128](./0128-accountable-request-impacts-of-administrative-changes.md) and
[ADR-0150](./0150-scoped-exceptional-funding-and-combined-confirmation.md), only renewed
employee acknowledgement as a finalization gate for later pending-request changes.
Preserves initial self-service acknowledgement under 0069 and initial on-behalf
employee response under [ADR-0088](./0088-employee-acknowledgement-for-on-behalf-unpaid-leave.md).

## Decision

An authorized later change to a pending request's paid/unpaid allocation requires
reviewed consequences, employee-visible actor/reason and previous/revised amounts,
plus an employee notification linking to authorized details. An increase or decrease
does not require a renewed employee acknowledgement and does not create a new
employee-response finalization blocker. No new optional acknowledgement setting.

The change authorizer handles necessary prior discussion with the employee as an
organizational responsibility. Do not add a checkbox asserting the conversation,
an external-consent tracking workflow or a separate employee acceptance task. A
notification is communication, not proof of agreement; unread/read state never
constitutes consent or an approval decision. Request-specific notification payloads
retain the existing minimal content; amounts/reasons stay in authorized application
details. Keep ordinary withdrawal eligibility and valid earlier approval decisions.

Initial own-request submission still reviews/acknowledges the exact requested unpaid
amount. An initial unpaid on-behalf request still needs the employee's response under
ADR-0088. If that initial response remains outstanding when allocation changes, it
remains outstanding and must use current applicable amount/evidence. Do not invent an
initial-response obligation for a request first submitted fully paid just because a
later authorized change introduces unpaid leave. After a required initial response is
satisfied, later changes do not demand renewal. Zero-unpaid applicability and concurrent
initial response/allocation changes remain explicit contract cases before readiness.

All current authority, request revision/lifecycle, valid funding, employment/date,
documents, coverage and required approval conditions still apply. Preserve atomic
change/accounting/evidence/outcome/notification intent and duplicate-safe retries.
This decision does not permit automatic conversion of already approved paid leave to
unpaid; approved-request impact resolution and necessary factual correction/deficit
safeguards remain. New replacement/resubmitted approval cycles retain their applicable
initial submission rules, not an exemption inferred from an old acknowledgement.

## Impacts and verification

Update Features, spine, UX/revised-allocation preview, E3/E5 consumer/test coverage,
tracker/handoff and index. Replace renewed-response tasks/waiting badges and associated
gate tests for later changes with exact consequences, source actor/reason, minimal
notification, authorized details and no renewed blocker. Verify increases/decreases,
previously fully-paid request, initial on-behalf response outstanding/satisfied,
concurrent changes/retry, all remaining gates, preserved decisions/reservations and
no silent approved-paid conversion. Exact contracts/test paths/final sizing remain open.

Comparison informing the decision (checked 2026-10-21):
[Factorial modification guide](https://help.factorialhr.com/en_US/absences-approvals/how-to-modify-an-absence)
documents authorized edits and balance recalculation;
[Leave Dates notifications](https://help.leavedates.com/article/192-email-notification-settings)
documents update notices. Neither establishes a universal unpaid-change convention;
this is the user's chosen workflow, not a claim of industry-wide or legal consent rules.

Reuse existing review/change-history/notification patterns; Leave owns allocation/
finalization semantics. Existing agent instructions suffice. Accepted predecessors
unchanged. No code, runtime tests, migrations, grants, deployment or implementation/
readiness authorization; the HTML change is a planning preview only.
