# Leave Architecture Decision Records

Leave ADRs record decisions whose primary consequences belong to the Leave domain.
Reusable platform decisions live in the
[platform ADR collection](../../../../../platform/docs/architecture/decisions/README.md)
and are linked rather than duplicated here.

## Rules

- Statuses are `Proposed`, `Accepted`, `Superseded`, or `Deprecated`.
- Accepted ADRs remain as history; a later change is a new ADR that supersedes one.
- Numbering is local to this directory and never reused.
- New user-visible states, balance semantics, or authorization boundaries require a
  new or superseding ADR.

## Index

| ADR | Status | Decision |
|---|---|---|
| [0001](./0001-immutable-balance-ledger.md) | Accepted | Leave balances derive from an immutable ledger |
| [0002](./0002-versioned-leave-policies.md) | Accepted | Leave types and policies are effective-dated and versioned |
| [0003](./0003-working-time-in-minutes.md) | Accepted | Working-time consumption is stored canonically in minutes |
| [0004](./0004-configurable-approval-workflows.md) | Superseded by 0007 | Approval workflows are configurable and snapshotted; original record preserved |
| [0005](./0005-jurisdiction-configured-policies.md) | Accepted | Jurisdiction is configurable metadata, not a statutory rules engine |
| [0006](./0006-sensitive-attachment-access.md) | Accepted | Sensitive attachments require separate, domain-aware authorization |
| [0007](./0007-required-approval-and-automatic-decisions.md) | Superseded in part by 0008, 0078, and 0080 | Later-step ordering, coverage gate, and optional directional absence policy qualify approval rules |
| [0008](./0008-later-step-acceptance-on-submission.md) | Superseded in part by 0078 and 0080 | Immediate later-step acceptance retained; coverage and optional absence policy qualify finalization |
| [0009](./0009-resubmit-rejected-request.md) | Accepted | Correct and resubmit the same rejected request while preserving submission history |
| [0010](./0010-cancel-and-replace-approved-leave.md) | Accepted | Cancel and replace approved leave through renewed approval, with scoped on-behalf rights |
| [0011](./0011-colleague-absence-privacy.md) | Superseded in part by 0074 | Colleague type/detail privacy remains; partial days now show Part-day absence |
| [0012](./0012-assigned-approver-field-visibility.md) | Accepted | Assigned approvers see sensitive leave types and employee notes; medical documents remain separately authorized |
| [0013](./0013-leave-manager-field-visibility.md) | Accepted | Leave Managers see in-scope types, employee notes, and approval history; medical documents remain separately authorized |
| [0014](./0014-email-notification-privacy.md) | Accepted | Emails contain only name, dates, status, and a secure application link as request data |
| [0015](./0015-in-app-notification-privacy.md) | Accepted | In-app notifications use the same minimal content; opening requests rechecks role and resource permissions |
| [0016](./0016-approver-medical-document-metadata.md) | Accepted | Approvers without document permission see only provision and verification status; filenames, previews, and downloads remain separately authorized |
| [0017](./0017-leave-manager-medical-document-metadata.md) | Accepted | Leave Managers use the same medical-document metadata permission boundary as approvers |
| [0018](./0018-approval-history-visibility.md) | Accepted | Employees and assigned approvers see in-scope decision history and comments; no private approver-only comments in MVP |
| [0019](./0019-date-by-date-future-balance.md) | Accepted | Assess future balances on every requested date using earned accrual, expiry, and existing reservations |
| [0020](./0020-earliest-expiry-entitlement-allocation.md) | Accepted | Use eligible entitlement expiring soonest first within the selected balance; non-expiring entitlement last |
| [0021](./0021-inclusive-entitlement-expiry-date.md) | Accepted | Expiry date is the last usable leave date; earlier submission does not extend validity |
| [0022](./0022-accrual-effective-date-availability.md) | Accepted | Accrual is usable from the start of its policy-configured effective date, never for earlier leave |
| [0023](./0023-employee-work-timezone.md) | Accepted | Employee work timezone defines leave dates and accrual/expiry boundaries independently of viewer timezone |
| [0024](./0024-mvp-accrual-schedules.md) | Superseded in part by 0043 and 0045 | Annual/monthly/manual choices remain; annual dates follow periods and monthly dates use start/end of month |
| [0025](./0025-per-policy-calendar-day-proration.md) | Accepted | Policies choose no proration or inclusive calendar-day employment proration; manual grants remain explicit |
| [0026](./0026-prorated-grant-rounding.md) | Accepted | Round final prorated grants once per policy: down, nearest (half up), or up to whole minutes |
| [0027](./0027-accrual-date-calendar-fallback.md) | Superseded in part by 0045 | Historical configured-date fallback; monthly dates now follow start/end of month |
| [0028](./0028-policy-carry-over-options.md) | Accepted | Policies choose no, all-unused, or capped carry-over, with optional configured expiry |
| [0029](./0029-repeated-carry-over.md) | Accepted | Policies choose once-only or repeated carry-over within limits; existing expiry dates never extend |
| [0030](./0030-non-carried-entitlement-expiry.md) | Accepted | Unused amounts excluded from carry-over expire with ledger history and employee explanation; no automatic payout or cross-type transfer |
| [0031](./0031-pending-request-rollover-shortfalls.md) | Accepted | Reservations do not bypass rollover rules; keep shortfalls pending and warn of the exact requested unpaid amount |
| [0032](./0032-protected-reservations-and-explained-changes.md) | Accepted | Protect existing reservations; explain authorized unpaid increases and require employee acknowledgement before final approval |
| [0033](./0033-optional-accumulated-balance-cap.md) | Accepted | Optional balance caps limit scheduled accrual; explain excluded amounts and retain existing entitlement |
| [0034](./0034-accrual-resumption-after-cap.md) | Accepted | Resume accrual on the next scheduled date within the cap, without automatic restoration of excluded amounts |
| [0035](./0035-leave-date-funding-and-booking-horizon.md) | Accepted | Reserve entitlement valid on leave dates and enforce a per-policy advance-booking horizon |
| [0036](./0036-default-twelve-month-booking-horizon.md) | Accepted | Default booking horizon is 12 months, configurable per policy; all requested dates must fit |
| [0037](./0037-earned-reservations-count-toward-cap.md) | Accepted | Already-earned reservations count toward the cap until final approval consumes them; future accrual stays separate |
| [0038](./0038-cancellation-accrual-recalculation.md) | Accepted | Cancellation reverses extra accrual enabled by the booking, with a preview, audit corrections, and deficit review |
| [0039](./0039-cancellation-deficit-review.md) | Accepted | In-scope Leave Managers with balance-adjustment permission review cancellation deficits with reasons and employee explanations |
| [0040](./0040-schedule-based-carry-over-day-limits.md) | Accepted | Convert carry-over day limits with the employee's standard day effective at rollover; preserve the audited conversion |
| [0041](./0041-standard-day-for-variable-schedules.md) | Accepted | Configure a standard day for entitlement conversions; actual leave uses the requested date's scheduled hours |
| [0042](./0042-entitlement-period-basis.md) | Accepted | Policies choose calendar-year or employment-anniversary periods independently of accrual frequency |
| [0043](./0043-annual-grants-at-period-start.md) | Accepted | Annual grants occur at period start, with policy-prorated calendar-year joining grants; supersedes 0024's independent annual date |
| [0044](./0044-leap-day-employment-anniversaries.md) | Accepted | February 29 employment anniversaries use February 28 in non-leap years and return to February 29 in leap years |
| [0045](./0045-monthly-grant-start-or-end.md) | Accepted | Monthly policies choose start or end of month, with agreed partial-month proration |
| [0046](./0046-mid-month-joining-grants.md) | Accepted | Upfront monthly policies grant mid-month joiners at employment start; month-end policies wait until month-end |
| [0047](./0047-month-end-grant-same-day-availability.md) | Accepted | Month-end grants are usable from the start of their grant date in the employee's work timezone |
| [0048](./0048-upfront-grant-departure-recalculation.md) | Accepted | Recalculate upfront grants on departure using policy proration; explain corrections and review spent deficits |
| [0049](./0049-leave-after-employment-end.md) | Accepted | Block submission/final approval beyond employment end; flag existing requests with explanations for authorized correction |
| [0050](./0050-minimum-notice-default-zero.md) | Accepted | Minimum notice defaults to zero calendar days; shorter-notice requests require an explanation and approver flag |
| [0051](./0051-backdated-requests-without-cutoff.md) | Accepted | No fixed backdating cutoff; require a reason, visible lateness, normal approval, and historical calculations |
| [0052](./0052-overlaps-and-administrative-corrections.md) | Superseded in part by 0074 | Correction authority/history remain; interval checks replaced by same-date warnings and daily duration limits |
| [0053](./0053-administrative-correction-authority.md) | Accepted | Administrative corrections require a Leave Manager with scoped on-behalf permission; Organization Administrator alone is insufficient |
| [0054](./0054-administrative-correction-notifications.md) | Accepted | Notify employees of corrections by email and in-app; acknowledgement only for increased requested unpaid leave |
| [0055](./0055-ngo-scoped-notifications-and-badges.md) | Accepted | Active-NGO bell/inbox with count-only badges for each active NGO membership |
| [0056](./0056-notification-read-state.md) | Accepted | Open marks read; bulk read affects only the user's active NGO; neither approves nor acknowledges leave |
| [0057](./0057-approval-reminder-interval.md) | Accepted | Policy reminder interval defaults to three calendar days; remind only currently required approvers without changing decisions or routing |
| [0058](./0058-unanswered-approval-escalation.md) | Accepted | Notify an authorized Leave Manager after seven unanswered calendar days by default; rerouting remains explicit and permissioned |
| [0059](./0059-default-language-and-localization-readiness.md) | Accepted | English default with unambiguous dates; prepare for Portuguese as the next language |
| [0060](./0060-portuguese-mozambique-and-angola.md) | Accepted | Initial Portuguese localization targets Mozambique and Angola, with regional validation for both |
| [0061](./0061-user-language-preference.md) | Accepted | User language preference follows NGO switches and personal notifications, with English fallback |
| [0062](./0062-employee-history-and-balance-views.md) | Superseded in part by 0084 | Employee year calendar and accessible history list accompany per-type balances and explanations |
| [0063](./0063-employee-home-screen.md) | Accepted | Employee home prioritizes applying, balances, pending actions, upcoming approved leave, and history navigation |
| [0064](./0064-approver-home-screen.md) | Accepted | Approver home prioritizes required decisions, exception flags, scoped team availability, and employee-workspace access |
| [0065](./0065-leave-manager-home-and-ngo-wide-scope.md) | Accepted | Leave Manager home prioritizes administrative work; MVP employee scope is NGO-wide with separate action permissions retained |
| [0066](./0066-role-sections-and-action-badges.md) | Accepted | Permission-based My Leave/Approvals/Manage Leave sections share active NGO; action badges are separate from unread counts |
| [0067](./0067-automatic-draft-saving.md) | Superseded in part by 0075 | Truthful autosave, NGO-bound drafts, no reservation, and submission revalidation retained; closing label refined by 0075 |
| [0068](./0068-ngo-switch-while-editing.md) | Accepted | Save drafts in the original NGO before switching; failed saves offer retry/stay/discard-unsaved-and-switch |
| [0069](./0069-submission-summary-and-unpaid-acknowledgement.md) | Superseded in part by 0071 | Exact unpaid acknowledgement and submit behavior remain; summary context simplified by 0071 |
| [0070](./0070-simple-submission-confirmation.md) | Accepted | Confirm submission with dates/status; keep identifiers internal, history accessible, employee actions clear, and retries duplicate-safe |
| [0071](./0071-concise-summary-and-header-ngo-context.md) | Accepted | Keep NGO in header, show switcher only for multiple NGOs, and simplify summary without named approvers |
| [0072](./0072-mobile-employee-and-approver-workflows.md) | Accepted | Complete employee/approver workflows on phones with compact month navigation and accessible history list |
| [0073](./0073-calm-practical-visual-direction.md) | Accepted | Calm, spacious, neutral visual design with a primary-action accent, expandable detail, and familiar accessible platform controls |
| [0074](./0074-duration-only-partial-day-leave.md) | Accepted | Partial days use duration without exact times; warn on same-date requests and block daily totals above scheduled hours |
| [0075](./0075-single-draft-and-safe-close.md) | Accepted | One employee application draft per employee per NGO; Apply resumes it; safe Close and confirmed discard |
| [0076](./0076-approval-cover-and-planned-delegation.md) | Superseded in part by 0077 and 0079 | Dated approval cover; scheduled return and appointment-granted authority refined by later decisions |
| [0077](./0077-scheduled-return-of-temporary-approvals.md) | Accepted | Authorize automatic return at temporary-assignment expiry with eligibility checks, audit, notification, and unresolved-cover fallback |
| [0078](./0078-approval-coverage-before-final-approval.md) | Accepted | Require coverage before final approval, including automatic completion, with authorized explained exceptions; qualifies 0007/0008 |
| [0079](./0079-temporary-appointment-grants-scoped-authority.md) | Accepted | Authorized temporary appointment grants bounded approval authority to active NGO members without a permanent approver role |
| [0080](./0080-directional-absence-approval-policy.md) | Superseded in part by 0081 | Directional absence policy retained; pending-step return/timing resolved in 0081 |
| [0081](./0081-absence-fallback-timing-and-return.md) | Accepted | Allow pending work to await supervisor return; continue reminders, restore outstanding supervisor step before final decision, and retain completed approvals |
| [0082](./0082-one-approver-role-with-workflow-steps.md) | Accepted | One Approver role; supervisor relationships and final-step authority resolved through workflow assignments |
| [0083](./0083-recurring-entitlement-period-boundaries.md) | Accepted | Recurring employee entitlement changes only at leave-period boundaries; default next boundary, immediate changes use separate adjustments |
| [0084](./0084-request-focused-balance-planning.md) | Accepted | Keep projections in Apply; defer standalone calculator/graph and explain actual policy consequences |
| [0085](./0085-period-relative-carry-over-expiry.md) | Accepted | Optional carry-over expiry in months from new period start, showing last usable date; existing expiry is never extended |
| [0086](./0086-archive-markers-and-effective-dated-versions.md) | Accepted | Archive timestamps retire records; effective-dated versions preserve calculation rules; snapshots and audit remain distinct |
