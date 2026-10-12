# ADR-0057: Invitation Onboarding and Trusted Tenant Enrollment

**Status:** Accepted — user direction 2026-10-11; contracts/readiness pending
**Date:** 2026-10-11
**Scope:** Shared organization admission and initial Microsoft Entra tenant mapping
**Refines:** [ADR-0002](./0002-supabase-auth-and-entra.md), activating its tenant-managed
identity revisit at the bounded tenant-mapping level, and
[ADR-0042](./0042-person-account-employment-and-legacy-adoption.md).
Retain Supabase Auth with Microsoft Entra; accepted originals remain unchanged.

## Decision

Normal organization onboarding uses a recipient-bound invitation unless the organization
has an explicitly verified trusted provider-tenant mapping and automatic onboarding has
been separately enabled. Invitations still use supported provider authentication; they
are organization admission, not a substitute login method. Generic Microsoft sign-in,
email-domain matching and employment existence cannot grant organization membership.

Offer Enable automatic onboarding for this tenant? after verified setup. Default off;
configuration/verification alone cannot enable enrollment. Authorized confirmation must
identify the exact organization, trusted tenant and eligible audience. Automatic admission
creates only the approved current membership, not employment, app grants or administrator/
approver roles. Existing account/person linking and role assignment remain independently
verified under their owning contracts. Users may have several organization memberships;
one organization's enrollment policy grants nothing in another organization.

Turning automatic onboarding off stops new automatic joins, without retiring existing
memberships or deleting historical data. Existing authentication/current membership/app
checks remain binding. Rejoin after prior retirement must follow explicit lifecycle
policy and never silently restore revoked grants; define retired/excluded-account handling
before implementation so login cannot bypass an administrator's removal.

Initial scope is a trusted Microsoft Entra tenant mapping over the retained Supabase
integration. Arbitrary per-organization providers, a new identity broker and Graph/SCIM
role/directory synchronization remain deferred. Define trusted issuer/tenant/subject and
audience verification, admin proof/control, external/guest-account eligibility and any
supported group-filter evidence before delivering automatic joins. Fail unavailable or
ambiguous verification safely; do not pretend a tenant-ID text field proves trust.

Restricted bootstrap/migration/adoption commands remain available under their existing
operator authority/evidence contracts. They are not a normal Add member onboarding UI
or an unprotected invitation bypass. Protected provider configuration and organization
admission are separately authorized; no infrastructure role implies unrestricted app data.

## Delivery and evidence

Separate secure invitation, verified tenant configuration and opt-in automatic admission
into bounded shared-platform stories. Verify provider feasibility and declare each wire/
state/privilege/retention contract before its readiness gate; test actual supported sign-in
and synthetic tenant identities during delivery. Tenant-managed onboarding is an explicit
addition to the earlier deferred product scope, not grounds to skip Phase 1 readiness.

Acceptance includes invitation-only unconfigured/off state, verified setup staying off,
explicit enablement and scoped eligible join, wrong tenant/account refusal, concurrent
join/replay, removed-member/rejoin behavior, no implicit employment/grants, and disabling
without membership deletion. Record configuration/enrollment evidence with verified actors,
UTC times and safe references; no token/claim dumps in logs. External verification occurs
outside write locks; local changes and required evidence commit consistently.

Scaffold/shared UI: promote proven identity/admission clients and reviewed tenant-setting
states; retain ordinary invitation and app-role patterns. Agent context/documentation link
this policy and distinguish enrollment from authentication/authorization. No general HR
or provider administration engine. No code, account, invitation, provider or deployment
changed; exact implementation feasibility, sizing and readiness remain open.
