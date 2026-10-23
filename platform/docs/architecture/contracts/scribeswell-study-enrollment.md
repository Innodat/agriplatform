# Scribeswell study enrollment and recipient verification — owner contract draft

2026-10-22. **Owners:** Access facade/policy; Identity account, actor and recipient evidence;
Scribeswell invitation/share transitions.
**Status:** enrollment/check implemented; recipient/invitation design remains proposed.
This is the owner location for the proposed wire. The
[feature contract](../../../../_bmad-output/specs/spec-scribeswell-studies/SPEC.md)
retains product truth. The delivered scope is qualified below; recipient operations and live registration/grant activation remain undelivered.

Inherits [admission](application-admission-and-discovery.md),
[canonical typed checks](identity-access-employment-e1.md#canonical-capability-check-wire--2026-10-06),
[Identity/Access execution](identity-access-execution-substrate.md), and
[errors/outcomes](api-errors-and-operation-recovery.md). Accepted ADRs stay unchanged.

## Delivered enrollment/check slice — 2026-10-23

The approved enrollment/check slice is now implemented by Access/Identity; see the
[owner runbook](../../../../services/access/STUDIES-ENROLLMENT.md) for current DTOs,
restricted SQL roles, closed errors, deadlines, readiness and recovery. Enrollment
requires no organization, employment, PtS or person link. Valid adopted actors are
preserved, and separate actor-only completion grants no Studies authority.

These implementation notes supersede future-tense enrollment obligations below; recipient sections retain their proposed status. The envelope below is the delivered enrollment shape. Its executing Access budget is
3 seconds including receive/provider/SQL/commit, with provider work at most2 seconds;
Identity retains its5-second observation ceiling. The delivered verification/setup
variants are403 `identity.verification_required` and503 `identity.setup_unavailable`.
Recognized Studies outcomes are private/no-store. Unknown callers on the shared check
route retain the compatible KDG denial envelope, as documented in the runbook.

Recipient resolution, address-key normalization, invitation verification and acceptance
sections below remain proposed and undelivered. Their unresolved qualifications are
not prerequisites added to ordinary personal enrollment, and this slice does not
activate Scribeswell note/editor routes, provision real accounts or deploy anything.

## Fixed policy and caller

Proposed registry identity: application `scribeswell`, permission
`scribeswell.studies.use`, authorization scope `{ "kind": "account" }`.
Controlled owner registration precedes activation. No organization, employment,
PtS grant or person link is required. This capability does not change the
PtS-derived launcher rule or grant access to another account's studies.

Only Scribeswell's separately authenticated service identity may invoke enrollment
for its current end-user bearer. Browser, Directory, Content and other service
credentials cannot invoke it. The endpoint is internal, not a public gateway route.
The user bearer determines the account; no target account, actor, email,
organization, permission or role selector is accepted.

## Proposed wire

`POST /v2/enrollments/scribeswell-studies`

Required transport: current user `Authorization: Bearer ...` and the independently
restricted `X-Service-Key`. Neither is logged. Body is exactly:

```json
{"operation_id":"<nonnil UUID>"}
```

Reject duplicate keys, unknown fields and malformed input through the shared
validation envelope. A completed operation returns HTTP 200, private/no-store:

```json
{
  "operation_id":"<original UUID>",
  "status":"committed",
  "result":{
    "disposition":"created",
    "account_id":"<verified UUID>",
    "actor_id":"<verified account actor UUID>",
    "permission":"scribeswell.studies.use"
  }
}
```

`disposition` is the closed union `created | unchanged`. An identical retry returns
its original acknowledgement, including the original disposition. This receipt
is not an Access decision, grant token or promise of current permission. Clients
must not use it instead of the current check below.

## Execution, concurrency and recovery

1. Validate caller and request. Obtain current live-account/profile, required
   verification and actor evidence through owner-authorized paths outside local
   business locks. Never rely on cached JWT email/role claims or a browser actor ID.
2. If actor setup is needed, use only the separately authorized Identity runtime
   setup contract once delivered. The existing operator `account_actor.ensure`
   implementation is not runtime permission. Actor setup and Access assignment
   are separate commits: a retry may resume after actor-only success, which grants
   no Studies access by itself.
3. In the bounded Access transaction, serialize this account/fixed permission and
   operation identity; recheck global app availability, policy and retained grant
   state. A retained revoked grant or suspended account denies enrollment. An
   active grant remains unchanged; an eligible absent grant is created once.
4. Commit required attribution, initial-assignment evidence and successful compact
   outcome with the local effect. Concurrent distinct operations may each have an
   acknowledgement, but produce at most one initial grant/assignment event. User
   initiator and restricted service executor remain distinguishable.
5. Scope outcome identity to authenticated service, account, command version and
   operation UUID. A new execution, including replay, rechecks current eligibility
   and retained revocation. An old success can never recreate a removed/revoked
   grant. No automatic outcome expiry is proposed for first delivery; no physical
   reuse of the operator-only receipt schema is implied.
6. Timeout/disconnect is unresolved, not rollback. Retry the same operation; do not
   mint a replacement after an unknown outcome. Current denial stops automatic
   retries; dependency failure remains unavailable rather than revoked. Numeric
   observation/execution/recovery limits must close before implementation.

Use shared `error_id` envelopes: 401 `authentication_required`; 403
`service_access_denied` for the wrong caller; 403 `access_denied` for confirmed
ineligibility; 422 `validation_failed`; 503 `authorization_unavailable` for a
failed current check and `dependency_unavailable` for required setup failure.
Verified-address-required and actor-setup outcomes need closed owner-selected
variants; do not disguise them as successful enrollment or expose profile content.

## Subsequent protected actions

Use canonical `POST /v2/check`, not a second Scribeswell authorization engine:

```json
{"permission":"scribeswell.studies.use","authorization_scope":{"kind":"account"}}
```

Scribeswell verifies the canonical account response's exact account, actor,
permission and authorization scope, then enforces current local ownership,
accepted share and private-response rules. No org/person/member null placeholders,
positive cross-request grant cache or fallback to PtS/organization authority.
Enrollment, sign-in and receipt lookup never accept an invitation. Public Bible
reads never depend on enrollment/check readiness.

## Current-account preparation — proposed Identity extension

Preparation runs only for the explicit Studies enrollment operation. Ordinary
login, permission checks and public reading remain read-only. Access reaches
Identity through the existing restricted-owner integration; no new Identity HTTP
service or application access to Identity tables is selected.

- Authenticate the current bearer through the supported live provider adapter;
  combine current account/verification evidence with Identity's current profile.
  A user-supplied email, actor, role claim or stored historical receipt cannot
  replace that evidence. Verification failure and unavailable verification differ.
- The Auth-created profile hook is a release prerequisite to qualify, not something
  presumed from an old migration. Missing/deleted, system/keyed or ambiguous
  profiles cannot be recreated/reclassified by this command. Report safe setup
  unavailable without creating Auth, person, employment or organization records.
- Reuse a valid existing account actor unchanged, including an adopted legacy ID.
  For an eligible absent mapping, Identity derives the intended actor UUID from
  the current account UUID and supplies an approved profile-derived label. Reuse
  the delivered owner collision/binding invariants. Unexpected existing actors or
  unclassified legacy attribution require owner reconciliation before activation;
  they never authorize silently choosing another actor or moving a mapping.
- A separately authorized, current-account-only Identity command may establish the
  missing actor/mapping and compact receipt with required creation attribution and
  immutable evidence in its own transaction. It must freshly verify live account
  eligibility, then recheck local profile/binding after waits and before commit.
  Keep the existing five-second observation bound as the proposed executing
  setup limit. Expiry is unavailable; restarting/replaying observes again.
- Runtime service execution and verified user initiation remain distinguishable.
  Ordinary Access checking roles and Scribeswell have no Identity writes; a
  dedicated restricted setup pool can execute only this current-account command.
  Its policy cannot invoke the general operator CLI, register arbitrary actors,
  set a browser-selected account context or borrow operator provisioning authority.

Actor setup and Access enrollment remain separate commits. Actor-only completion
is harmless attribution setup, not a grant. Retry resolves it and continues only
with fresh current eligibility. A pre-existing actor never authorizes enrollment.
Exact routine/receipt DDL and grants belong to Identity's migration history and
must be qualified against the delivered operator path before consuming code.

## Recipient resolution and proof — proposed Access facade

Both operations require the current user bearer, Scribeswell-only service identity
and current `scribeswell.studies.use` authority. They are internal and private/no-store;
no generic account directory or arbitrary application selector is exposed. Identity
owns the provider-qualified address comparison and current account evidence.
Scribeswell owns the invitation; Access does not read its tables or accept it.

### Issuing an invitation

Proposed `POST /v2/recipients/scribeswell-study-invitations/resolve` accepts exactly
`{operation_id, recipient_address}`: a nonnil UUID and one address supplied through
Scribeswell's authorized Share action. Scribeswell first checks current study-owner
rights; the restricted facade is not a substitute for that domain check.

Return exactly `{operation_id, recipient_address_key, recipient_account_id,
decision_id, checked_at}`. The account ID is explicitly nullable for an address
without an existing account binding; the key is a versioned Identity-produced
canonical comparison value, never a bearer secret. It stays private, like the target
address. No display profile, role, account list or directory result is returned.
Account binding uses an authoritative exact-address lookup, never a user-directory
scan or an application guess. An ambiguous or unavailable lookup fails unavailable. Resolution is an observation,
not an Identity mutation: operation_id correlates the request, not an implied
Identity receipt. Scribeswell resolves uncertain creation through its own operation
outcome and never overwrites an already committed target with a later lookup.

Scribeswell persists the target key and any returned account binding with its new
invitation. A known account is not replaced on later email reuse; deleting that
account does not convert the invitation into an unbound one. An intentionally
unbound invitation can await registration. No Auth account is created by resolution.
The owner's UI does not reveal whether the address has an account; Pending remains
invitation state, not delivery or read confirmation.

### Viewing or accepting a pending invitation

Proposed `POST /v2/recipients/scribeswell-study-invitations/verify` accepts exactly
`{invitation_id, invitation_revision, recipient_address_key, bound_account_id}`.
The ID is a nonnil UUID, revision a positive decimal string and bound account ID
explicitly UUID-or-null. Scribeswell supplies these from its stored invitation,
never from a browser's replacement recipient fields. The bound ID is a comparison
constraint, not a target-account selector or a way to change the current account.

Identity verifies the bearer account is current and controls the exact intended
verified primary address. Pending/unverified address changes and JWT email text
are insufficient. A stored binding additionally requires the same account UUID.
An unbound pre-registration invitation may match the intended newly registered
account; this does not merge accounts or inherit another account's accepted shares.
Existing account-bound invitations and all accepted shares can never transfer by
address reuse. Multiple/conflicting provider identities fail unavailable.

Success contains exactly `{invitation_id, invitation_revision,
recipient_address_key, account_id, actor_id, decision_id, checked_at}`. All identity
fields come from current owner evidence. The response is evidence for the one
executing request, not a signed invitation, session token or reusable grant.
Scribeswell verifies every echoed target field and exact current account.
A mismatch uses safe `access_denied` with an allowlisted `recipient_mismatch`
reason, revealing no alternate address/account. UI may offer Switch account.
Missing verification uses proposed HTTP 403 `identity.verification_required`;
required setup unavailable uses HTTP 503 `identity.setup_unavailable`; an
unavailable current verification uses HTTP 503 `authorization_unavailable`. Use
the shared envelope with no raw provider text or identity details. OpenAPI and
adapters must declare the same closed variants before implementation.

### Local acceptance boundary

The Scribeswell executing attempt records a monotonic start before asking for
current Access/recipient evidence. Its proposed five-second observation budget
includes verification, local waits and commit; server `checked_at` alone is not a
cross-host freshness clock. No external calls occur while holding local write locks.
Expiry or a new/restarted attempt requires fresh checks; none of this promises
instantaneous distributed revocation.

After proof, return only the invitation preview fields authorized for the intended
recipient, never source notes or study contents before acceptance. The explicit
Accept command atomically validates stored target/revision, pending lifecycle,
server 30-day deadline and current local study state, then binds an unbound target
and creates the view share plus operation outcome. Invitation ID and target cannot
change during this boundary. Competing claims/revoke/expiry serialize locally;
no delayed proof or acceptance receipt can resurrect withdrawn access.

An already accepted share thereafter follows its account UUID through verified
email changes and uses ordinary current account/resource checks, not repeated
invited-address matching. A new/recreated account needs a fresh explicit invitation.
Recipient proof, notification reads and successful enrollment never accept for it.

## Provider and delivery qualification still required

The provider adapter must demonstrate exact current verification semantics, pending
email-change behavior, unique account matching and deleted/recreated-account handling.
Identity must select/version canonical address normalization from those demonstrated
semantics. Apps must not independently lowercase local parts, strip plus/dot suffixes,
match aliases or infer verification from an old confirmation timestamp. No new email
normalization package, provider configuration or secondary-address feature is selected.
The draft protocol cannot activate until that representation and privacy-safe lookup
privileges are concrete; this is unresolved implementation evidence, not implemented
provider support.

## Owner closure and acceptance

This draft closes the proposed operation/caller shape, not all D-1 work. Before
consuming implementation, settle and independently verify:

- Qualify the proposed live account/actor preparation and recipient facade against
  provider behavior, profile-hook adoption and exact restricted owner SQL/command
  privileges; retain separate Identity/Access migration owners.
- Restricted account-user enrollment command, receipt identity/privileges, immutable
  attribution/event variants, structural uniqueness and concurrent revoke behavior.
- Exact safe error variants, parser/body limits, total dependency/execution and
  recovery deadlines, receipt compatibility and any future explicit retention.
- Finalize canonical address-key representation/provider adapter and recipient
  error variants; prove stale/wrong-account/duplicate claims and safe invitation previews.
- OpenAPI/Pydantic/client schemas generated together; explicit account registry/caller
  policy; compatible migration/activation/recovery under platform ADR-0020.

Map ST-01/02/17/23/26/29 to owner tests: zero-membership first use; concurrent same
and distinct operation IDs; lost response; active/revoked/suspended/disabled states;
replay after revoke; unavailable verification; actor-only partial completion; wrong
service or target fields; account recreation; unchanged public reading. Exercise
actual restricted roles and pool reuse, not only UI mocks. Add actor-only failure
recovery, missing profile, reused/adopted actor, conflicting legacy actor, pending
email change, registered/unregistered target, email reuse, changed invitation
revision, concurrent bind/accept/revoke, verification deadline and no pre-accept
source-content cases.

Scaffold: prove the fixed caller/scope pattern with its first consumer, no generator
claim. Shared UI: no new component. Agent context: existing ownership rules suffice.
Documentation: this owner draft and canonical feature companions. ADR: existing
scope, attribution, transaction and release decisions apply; none amended. Leave,
PtS migration and notification delivery remain outside this enrollment draft.
