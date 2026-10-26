# Organization invitation and prepared-access protocol

**Status:** Technical planning candidate for the single consolidated review, 2026-10-26.
**Owners:** Identity/Access in services/access; existing Supabase/Entra sign-in and approved
mail delivery adapter. Implements 2.6 and 2.9, not a new authentication service.

## Recipient and sign-in binding

Issue an organization invitation, not a Supabase authentication invitation or a fake Auth
account. Existing configured provider sign-in remains unchanged. A known recipient uses
an exact Identity account UUID selected through authorized lookup. A not-yet-known
recipient uses an immutable invitation target UUID and intended delivery mailbox; no
account/person merge, employment or grant follows from that mailbox.

After provider sign-in, Identity verifies the live session and its existing server-owned
provider-identity/account binding. An invitation for a known account must match that
account. For a new recipient, require a fresh mailbox challenge sent to the invitation's
stored address after sign-in. Bind the challenge to invitation generation, authenticated
account, session and acceptance attempt. Successful verification binds the target once
to that exact account/provider identity; concurrent different-account acceptance loses.
Possessing the original invitation URL, a display email, or a matching unverified email
claim cannot bypass this step. A challenge cannot change the invited address. Address
correction means replacement plus renewed administrator review of any prepared access.
Show the organization and signed-in account before explicit Accept. Wrong-account exit
uses the existing session isolation/re-authentication flow. Do not put tokens in return URLs.

Use 256 random bits for invitation link secrets; store only a keyed digest in invitation
state. The mail outbox may retain an encrypted delivery envelope with restricted key
access until terminal delivery, then erase the secret. No bearer secret in audit/logs.
Use an eight-digit cryptographically random challenge, keyed digest, ten-minute expiry,
maximum five failed attempts, one issue per minute and five issues per hour per
invitation/account and recipient digest. Exhaustion invalidates the challenge, not the
membership. Challenges are single-use and only the latest is valid. Use trusted server
UTC time with exclusive expiry; no mailbox polling, Graph, account linking or new broker.

This deliberately verifies mailbox control separately from stable account identity.
Microsoft warns against email/username as enduring authorization keys; Supabase documents
the Azure provider's optional verified-email claim. Neither substitutes for this binding.
Provider configuration and real callback evidence remain delivery acceptance, without
assuming raw upstream tokens are available in browser metadata.
[Microsoft claim validation](https://learn.microsoft.com/en-us/entra/identity-platform/claims-validation),
[Supabase Azure sign-in](https://supabase.com/docs/guides/auth/social-sign-in/auth-azure).

## Lifetime, resend and local atomic acceptance

An invitation lasts seven days from issue. A deliberate resend rotates the secret and
increments its generation, starts a new seven-day validity, invalidates older links and
challenges, and records one new outbound intent. Rate limit resends to one per minute
and five per hour per invitation; same-operation replay returns the prior generation
without another rotation. A delivery retry uses that generation's original intent and
never extends expiry. A worker checks current generation/state before sending; a mail
already handed to the provider cannot be recalled, but its old link is invalid.
Replacing organization/recipient cancels the old invitation and creates a new target;
prepared roles do not transfer. Cancellation and acceptance contend on the same row.

Owner-local invitation fields: UUID id/target/operation IDs, org UUID, nullable intended
account UUID, expected predecessor membership ID (nullable opaque decimal string), exact
mailbox protected as personal data, generation/revision, keyed secret digest, state
pending/accepted/cancelled/superseded, issued/expires instants, bound account/provider
reference, resulting membership ID and attribution. Expired is a computed presentation of
pending with expires_at <= now; expired acceptance cannot win a concurrent resend.
Unique current target/generation and existing unique active membership constraints apply.

POST /v2/organizations/{org}/invitations creates; POST /{id}/resend and /cancel require
operation_id and expected_revision. Authenticated POST /v2/invitations/inspect accepts a
secret in the request body, returning only the valid invited organization/account context;
POST /{id}/challenge issues the bound challenge and POST /{id}/accept includes the secret,
challenge, generation and operation_id. GET organization-scoped outcomes requires current
administrator authority; recipient outcome recovery is restricted to that bound account.
All paths are relative to the owning service, not public account-enumeration endpoints.

Acceptance locks the invitation and exact membership slot in fixed owner order, verifies
current generation, expiry, target/session/challenge and expected predecessor, then
atomically commits challenge consumption, accepted state, existing/new exact membership,
required audit and compact outcome. Existing active membership is recognized unchanged.
A retired predecessor needs a newly reviewed deliberate invitation; a stale invitation
cannot re-admit after retirement. A new membership has a new ID, owner=false and no copied
grants. Same acceptance outcome remains the original membership after a later retirement;
replaying it cannot recreate membership or falsely report current access.

## Prepared roles and honest stages

Access preparation stores its own UUID, org/application, invitation target or separately
verified trusted-tenant target, exact role IDs/definition revisions, approver, approved
assignment authority evidence, expected membership predecessor, approval revision, state
pending/active/withdrawn/needs_review/expired, operation outcome and attribution. Select
30 days as the pending approval lifetime. Resending the same recipient invitation does
not extend that lifetime; replacement target, changed/deleted role, changed approval
scope/authority, retirement, disabled admission or expiry prevents automatic activation.
Transient verification failure stays pending; a persistent review-dependent change is
needs_review. Trusted-tenant admission uses its separate verified stable target contract,
not mailbox/domain matching. Normal unchanged verified onboarding needs no second review.

Identity's committed admission publishes durable bounded activation intent. Access binds
it to the exact current account/membership and locks preparation/roles/assignment slots,
rechecks current approver authorization, role versions, app admission and target evidence,
then atomically commits assignments, active state, actual human initiator/service executor,
audit and outcome. Withdrawal competes on the same preparation row: it either wins before
activation or reports already active and directs an authorized revocation action. No
rollback of committed membership and no separate People dependency. Rejoin never consumes
an old approval. Pending onboarding / Member, access pending / Active refer to actual
committed owner stages. No Leave access claim follows from membership alone.

Use existing owner request deadlines: each verification HTTP call <=2 seconds, total
foreground action <=10 seconds, local lock wait <=2 seconds; no external waits under
write locks. Retry durable mail/activation work at 1, 5, 15 and 60 minutes, then hourly
until the invitation/approval deadline; terminal failures have an administrator Retry
with current checks. Lost responses use original operation status before issuing a new
command. Stable errors: invitation_invalid, invitation_expired, recipient_mismatch,
challenge_required, challenge_invalid, rate_limited, review_changed, already_active,
verification_unavailable; safe typed retry_after/current_revision where authorized.

Retain compact terminal operation/acceptance/withdrawal identities and membership binding
with membership history; never re-execute old operation IDs after detailed data expires.
Erase challenge digests on terminal state/expiry and undelivered secret envelopes on
cancellation/expiry. Retain invitation operational delivery attempts ninety days after
terminal state, separate from required business audit and approved retention of recipient
history. No unlimited payload dumps or independent copy of Auth credential material.

## Delivery witnesses and impact decisions

2.6 proves known/new/wrong account, forwarded link without fresh challenge, concurrent
account binding, challenge exhaustion, exact expiry, resend versus delayed delivery,
cancel versus accept, existing membership, deliberate rejoin versus old replay, audit
rollback and actual isolated provider/mail delivery. 2.9 separately proves unchanged
activation, changed role/approval/app, withdrawal race, lost handoff and no old-grant
resurrection. Exercise actual restricted database roles and alternate writers.

Retain two bounded leaves: invitation lifecycle/provider mail adapter in 2.6; prepared
roles/current assignment activation in 2.9. Reuse existing membership/operation primitives;
do not wait for future E3 notifications. Scaffold: promote only proven provider/outbox/
retry fixtures. Shared UI: invite/status/challenge/account-switch and existing role drawer.
Agent context: existing ownership rules suffice. Documentation: this contract and actual
owner setup/recovery runbook. ADR: candidate technical selections under accepted P-0057/
0058; no accepted ADR edited. Any broader authentication policy needs its own decision.
No email, grant, account, runtime code or migration is authorized by this document.

## Consolidated adoption — accepted 2026-10-26

The user explicitly approved the completed consolidated planning package. The reviewed
choices and bounds in this contract are adopted under [the acceptance decision](../decisions/0064-approved-onboarding-continuity-and-content-contracts.md).
Earlier candidate/pending-review wording is historical and superseded for these choices.
Actual implementation and provider/database/browser/recovery proof remain delivery work.
The user requires a new Codex session before implementation; no runtime action here.
