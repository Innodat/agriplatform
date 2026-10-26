# ADR-0158: One Decision for Consecutive Same-Person Steps

**Status:** Accepted  
**Date:** 2026-10-22  
**Scope:** Same person occupying consecutive required approval positions  
**Clarifies:** [ADR-0007](./0007-required-approval-and-automatic-decisions.md)'s retained
configured duplicate-step handling; no accepted predecessor is edited.

## Decision

One confirmation satisfies consecutive approval steps assigned to the same person
when that person currently has authority for each and applicable configuration allows
same-person satisfaction. Record that the actual decision covers both responsibilities;
do not require the person to perform an identical decision twice.

When organization configuration requires two distinct people, flag the same-person
route as invalid and require a different eligible approver. Do not silently collapse
that independent-person requirement. This is not a blanket authority extension or an
exception to self-approval, assignment scope/dates, current membership, absence policy
or other finalization conditions. At least one valid approval remains required.

Preserve actual decision attribution and completed history. A recorded decision is
not retroactively expanded to a different later responsibility merely because a route
changes. Binding what counts as an identical applicable decision and how configurations
encode distinct-person requirements remains a contract gate; add no arbitrary workflow
builder or new policy UI beyond the approved supported behavior.

## Impacts and verification

Verify supervisor/final same eligible person with one confirmation covering both,
configured distinct-person conflict, missing authority for one position, self-approval
denial, scoped temporary authority, authorized submission decisions, changing assignments
and concurrent/retry effects. Keep existing finalization/accounting and current route
contracts. Bind decision-to-step representation, policy validation/preview, authority
observations and test ownership before readiness.

Reuse proven capability/review/decision/history patterns; promote generic gaps with
first consumer. Leave owns rules; Access owns grants. Update features, spine, UX,
Story 5.1/5.18, FLOW-07, tracker/handoff and index. Existing agent instructions suffice.
Exact contracts, final atomic coverage/order/agent sizing/readiness remain open.
No code, runtime tests, migrations, grants, deployment or implementation authorization.
