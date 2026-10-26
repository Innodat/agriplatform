# ADR-0153: Standard Leave Manager Includes Reassignment

**Status:** Accepted  
**Date:** 2026-10-22  
**Scope:** Default role mapping for pending approval reassignment  
**Complements:** [ADR-0065](./0065-leave-manager-home-and-ngo-wide-scope.md),
[ADR-0076](./0076-approval-cover-and-planned-delegation.md),
[ADR-0147](./0147-current-supervisor-routing-and-concise-decision-attribution.md)
and platform [ADR-0011](../../../../../platform/docs/architecture/decisions/0011-application-roles-and-business-permissions.md).

## Decision

The standard Leave Manager role includes explicit approval-reassignment permission
within its organization. Ordinary holders can use Reassign approver without an extra
individual grant. Deliberately restricted custom roles may omit this permission.

Keep reassignment a separately checked capability, supplied by the default role mapping,
not inferred from a role-name string or receipt of an escalation. The current API and
UI check it for the affected organization and work. Preserve required reason, eligible
authorized recipient, selected unfinished steps and completed decisions under Story 5.24.
A target needing temporary authority follows the explicit appointment process. This
mapping does not itself grant request approval, sensitive-document access or other
administrative action capabilities. Disclosed permanent-supervisor transfer and already
authorized scheduled return retain their own rules.

Bind exact capability identifier, standard/custom role versions, existing-grant adoption
and tests before readiness. Do not silently expand existing custom grants or apply live
role changes as part of planning. Accepted predecessors remain unchanged: separate
permission checks coexist with a standard role that supplies the permission.

## Impacts and verification

Verify standard-role in-organization reassignment, cross-organization denial, restricted
custom role omission, current revocation, reason/target validation and no implied approval
or document grant. Reuse Access capability mapping and existing Leave transfer/review/
activity patterns; no new role engine or user approval step. Promote generic gaps with
first consumer. Update features, spine, UX, epics, tracker/handoff and index. Existing
agent instructions suffice. No code, runtime tests, migrations, live grants, deployment
or implementation/readiness authorization.
