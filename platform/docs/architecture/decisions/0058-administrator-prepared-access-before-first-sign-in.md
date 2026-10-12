# ADR-0058: Administrator-Prepared Access Before First Sign-In

**Status:** Accepted — user direction 2026-10-11; activation contracts/readiness pending
**Date:** 2026-10-11
**Scope:** Shared organization onboarding and explicit pending role assignments
**Refines:** [ADR-0057](./0057-invitation-onboarding-and-trusted-tenant-enrollment.md),
[ADR-0042](./0042-person-account-employment-and-legacy-adoption.md) and
[ADR-0011](./0011-application-roles-and-business-permissions.md).
Accepted predecessors remain unchanged.

## Decision

An authorized administrator may prepare and explicitly approve application roles before
the recipient's first platform sign-in. When current account/membership already exist,
normal assignment applies. Otherwise retain pending intended access, bound to the exact
organization/application, reviewed roles and declared verified recipient/provider identity
contract. Do not create synthetic Auth accounts or grant rights by email/name matching.

Use the approved admission route: invitation acceptance when no verified enabled trusted
tenant enrollment applies, or eligible trusted-tenant enrollment when enabled. Preparing
roles cannot bypass admission. Pending roles grant nothing until the correct verified
account and current membership are established and activation checks pass. Automatic
onboarding alone still creates no role; these rights follow an explicit prior admin
approval, not inference from tenant membership or employment.

Identity owns verified admission/account/person linkage; Access owns intended assignment
and effective grants; People owns employment. Communicate over authorized HTTP contracts,
with owner-local commit/evidence and honest staged recovery. No distributed transaction or
new shared onboarding engine. Interrupted activation must not duplicate memberships,
roles or change evidence. Existing membership may remain while role activation awaits
resolution; never report full application access merely from membership success.

Before activation, verify pending approval/target/onboarding state, current assignment
policy, role definition revisions and applicable app enablement. A revoked invitation,
withdrawn preparation or retired membership cannot resurrect grants. Changed role/target
state follows explicit fresh-review rules; do not silently activate a different capability
set from the reviewed one. Separate accounts for one person retain separate permissions.

Account/person/employment linking remains independently verified. An employee record or
administrator-entered email is not proof the authenticated account belongs to that person.
Preserve both approving human and executing service attribution and immutable access-change
evidence; no credentials, full invite URLs or sensitive payload dumps in diagnostics.

## Delivery and impacts

A bounded advance-preparation story follows completed invitation, tenant-enrollment and
role-assignment foundations. Select exact pending schemas/status, target verification,
review/expiry/revocation, authority, activation/retry and retention contracts before readiness.
Provider-specific lookup, if needed, is an explicit scoped dependency; no Graph/SCIM bulk
sync, permanent role import or universal admin credential is introduced.

Prove wrong-account/org refusal, actual verified recipient activation, missing/changed
role definition, invitation cancellation, retired/rejoined membership, response loss and
cross-owner partial failure with synthetic fixtures and real owner boundaries. UI clearly
shows Pending onboarding, Active or Needs review as applicable; confirmed pending access
is not an unsaved administration draft. Reuse the approved assignment drawer/review controls.
Scaffold promotes proven target/activation clients and fixtures; update agent context,
owner UX/runbooks and requirement-to-test mapping. No code, grants, provider configuration,
invitation delivery, migration or implementation-readiness pass occurs through this ADR.
