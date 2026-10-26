# ADR-0150: Scoped Exceptional Funding and Combined Confirmation

**Status:** Accepted  
**Date:** 2026-10-21  
**Scope:** Request-specific exceptional allocation authority and confirmation  
**Complements:** [ADR-0007](./0007-required-approval-and-automatic-decisions.md),
[ADR-0032](./0032-protected-reservations-and-explained-changes.md) and
[ADR-0128](./0128-accountable-request-impacts-of-administrative-changes.md).

## Decision

Use one scoped exceptional-funding capability for the organization-permitted funding
options of an in-scope request, not separate permission grants for each allocation
line/source. Approval or on-behalf permission alone does not grant this capability.
Validate each source's permitted type, employee/organization ownership, date eligibility,
available amounts, expiry and protected reservations as business checks. The capability
covers permitted request-specific discretionary paid grants, not unrelated standalone
balance adjustment or recurring entitlement changes. Bind exact limits/source contracts
before readiness; no negative-paid borrowing default is introduced.

Review the complete proposed allocation and paid/requested-unpaid split, with a mandatory
reason for the exception. Funding lines retain source, duration and authorizer with the
exception reason, without requiring a separate reason textbox for every line. Confirmed
funding must account for the requested duration and actual entitlement/reservation/
consumption effects without double counting; reason text is not an accounting event.

Funding authorization and ordinary approval have distinct recorded outcomes. An actor
authorized for both may use one Approve with exception confirmation: review allocation,
provide reason and confirm once. Commit both outcomes and their required local effects,
audit/outcome and notification intent together under the existing protected command.
If combined review is stale or authority fails, do not partially execute that combined
confirmation. Funding-only action remains possible for an actor with only the exception
capability; it must not approve another person's required step.

Record confirmed allocation/sources/actor/reason and actual approval step/actor/time/
comment through existing domain records/activity/audit, not an additional workflow/log
system. A valid funding decision may coexist with pending approval or employee response.
Preserve all independent finalization gates, current exact unpaid-response rules and
previous valid decisions. Increased unpaid amounts retain prior/new amounts, explanation
and employee notice; approval waits where required. No silent grant, cross-type borrowing,
decision substitution or automatic conversion of approved paid leave to unpaid.

## Impacts and verification

Verify one capability over permitted mixed sources, denied exception scope and invalid
source business rules, no unrelated adjustment powers, mandatory reason, exact duration/
funding reconciliation, request-specific grant effects, funding-only versus combined
authorization, combined stale/retry atomicity, recorded distinct outcomes without duplicate
effects, prior decisions and independent finalization/employee response. Actual request
writers and E2/E3 impacts integrate before activation; previews do not prove mutations.

Update features, E3 proposal/E5 consumer mapping, spine, written review UX and relevant
mock explanation, tracker/handoff/index. Reuse proven single-review/reason/operation/
audit controls; Leave owns accounting/authorization. Existing agent instructions suffice.
Accepted predecessors unchanged. No code, tests, migrations, runtime grants, deployment
or implementation/readiness authorization.
