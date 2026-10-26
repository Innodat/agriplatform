# Trusted Entra organization enrollment

**Status:** Bounded MVP planning candidate, 2026-10-25. No tenant, provider, membership
or grant was changed. Owners: Identity trust/admission; Access prepared app authority.
**Authority:** Platform ADR-0042/0046/0057/0058, Identity membership lifecycle and
[the Identity/Access/People contract](identity-access-employment-e1.md).

## Verification protocol

Use assisted verification by an authorized platform identity operator for initial
organization tenant setup. The organization administrator requests an exact tenant
connection in the normal settings surface; this request is not verification or enrollment.
Do not build an automated Graph directory proof/sync or a second login broker for MVP.
Normal application sign-in remains Supabase with Entra.

The request stores a random operation/challenge, exact organization, tenant UUID,
expected mapping revision, requesting verified account/actor, creation and expiry.
Expire an uncompleted verification request after 24 hours. Restarting verification
uses a new operation/challenge, not an extension of old proof. Limit pending requests
to one per organization; a retry recovers that request without overwriting its input.

The restricted operator procedure requires all of the following before approval:

1. Confirm the organization and requesting administrator through the existing current
   organization-management authority and trusted customer onboarding record. An email
   suffix or an employee record is insufficient.
2. Obtain a fresh normal Entra-backed Supabase sign-in by the intended tenant controller.
   Resolve the upstream tenant/issuer and immutable provider subject through the trusted
   Identity/provider adapter, not browser-supplied `user_metadata`, a typed tenant UUID,
   login email or an unverified decoded JWT. Compare the exact configured application/
   audience, issuer and tenant. Personal Microsoft accounts are ineligible.
3. In a supervised authenticated Entra administration session, the controller demonstrates
   current tenant administration authority and the exact tenant/application configuration
   against the operation's challenge and target. The operator verifies the tenant overview,
   controller identity/administrative role and configured enterprise application/registration
   needed for the retained Supabase integration. Generic successful tenant sign-in is not
   administrator control. Record the operator's explicit approval and safe evidence reference;
   do not copy access tokens, browser sessions or directory/profile dumps into the record.
4. The owner command rechecks current operator/requester authority, exact organization/
   tenant, challenge expiry and expected mapping revision; verifies no conflicting active
   organization mapping exists for this tenant in the initial MVP; and commits the trusted
   mapping, proof attribution, immutable change event and compact original outcome together.

This is an explicit trusted-human administrative decision, not a claim that screenshots
or an email cryptographically prove tenant control. The operator is authorized for this
exact target and records responsibility for the supervised check. A second unrelated
organization cannot claim an already-mapped tenant through self-service. Supporting a
single tenant across multiple independent organizations needs a separately reviewed
mapping/admission policy; invitations remain available meanwhile.

Use a fixed Microsoft cloud/issuer family and registered Entra application selected by
the platform's retained integration. Arbitrary issuer URLs, arbitrary client credentials
and automatic discovery from untrusted input are refused. The actual two customers'
tenant IDs, registrations, redirect origins and secrets are protected deployment inputs.
They are not guessed, committed or required to exist before the story can be planned.
The actual upstream claim-resolution/control-proof procedure must be rehearsed with
supported Entra accounts in 2.7 delivery; failure blocks verification, never falls back
to matching domains or successful generic login.

## Opt-in enrollment and lifecycle

Verification leaves automatic enrollment off. 2.8 separately shows the exact verified
tenant, organization and eligible audience and requires authorized explicit confirmation.
Initial eligibility is a verified native member of that exact tenant; exclude external/
guest and personal accounts. Unsupported or ambiguous provider evidence is ineligible,
not an assumed native member. No optional group-filter administration is added for MVP.
Invitations can admit otherwise permitted guest accounts with their own recipient checks.

Identity records the verified upstream issuer/tenant/subject binding separately from
login email and person/employment. At each automatic join it obtains fresh supported
provider evidence, checks the current enabled mapping/version and current account state,
then serializes the exact account/organization membership scope. Join creates only a
new membership with no owner flag, employment, role or app grant. Repeated concurrent
joins recover that membership. Existing current membership is reused without alteration.
A prior retired membership or explicit admission exclusion blocks automatic rejoin;
rejoin needs the separate authorized lifecycle action. Old grants never revive.

A prepared Access role approval from 2.9 is a separate staged command. Only its exact
verified account/current membership and current application/capability/authority checks
can activate it; enrollment itself cannot activate a role based solely on email or tenant.
No synthesized Auth account or employment is used to prepare access.

Turning enrollment off commits a new mapping revision and stops subsequent automatic
joins. It leaves existing memberships and grants untouched. Disable and join share the
owner's mapping/membership guards: an already committed join remains recorded; a join
that has not passed the protected current mapping check must observe the disable. Work
that restarts after a wait rechecks, rather than reusing an open settings form as authority.

Replacing tenant details invalidates the old verified mapping and disables enrollment
atomically before a new proof starts. New tenant verification does not inherit opt-in.
Revoking trust also disables new joins. Neither operation retires existing memberships,
changes their provider binding, changes employment or grants authority to another tenant.
Current protected action authorization continues to use actual membership/Access state.
Review displays this effect before commitment; no silent remapping of current accounts.

## Acceptance ownership and recovery

2.7 owns request/expiry/retry, scoped operator proof approval, exact trusted mapping,
wrong-tenant/audience/issuer/actor denial, concurrent mapping conflict, replacement and
verification state UI. Its delivery can finish with verified configuration and enrollment
off; it does not wait for 2.8. 2.8 owns opt-in/disable and fresh eligible native-member
join, removed-member/exclusion and concurrency/replay proof. 2.6 invitations remain usable
when verification is pending/off/unavailable. 2.9 proves independent staged grant activation.

Owner-local changes require immutable evidence and compact outcomes. Failed evidence
rolls back; lost response recovers the exact operation under current authority. Pending,
failed, expired and unavailable proof are distinguished. No provider outage is treated
as verified, a removed mapping or a missing membership. External provider/operator waits
hold no business transaction open; protected commit rechecks the recorded local state.
No client email, tenant mutation or operator action is performed by this document.

Scaffold: prove neutral request/revision/outcome/current-service boundaries with synthetic
native/guest/wrong-tenant fixtures and real-provider qualification at first use. Shared UI:
reuse connection states, explicit Save/Cancel/confirmation and safe return; no provider
secrets in forms. Agent context: existing identity/organization/admission ownership rules
suffice. Documentation: restricted proof procedure, authority/evidence/retention and
recovery runbook, generated contracts and requirement-to-test mapping. Accepted ADRs
remain unchanged; no Graph/SCIM sync or generic provider administration product.

## Consolidated adoption — accepted 2026-10-26

The user explicitly approved the completed consolidated planning package. The reviewed
choices and bounds in this contract are adopted under [the acceptance decision](../decisions/0064-approved-onboarding-continuity-and-content-contracts.md).
Earlier candidate/pending-review wording is historical and superseded for these choices.
Actual implementation and provider/database/browser/recovery proof remain delivery work.
The user requires a new Codex session before implementation; no runtime action here.
