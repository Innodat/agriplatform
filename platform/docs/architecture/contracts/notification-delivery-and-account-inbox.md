# Shared notification delivery and account inbox — contract draft

2026-10-22. **Owners:** common notification capability for acceptance, rendering,
channels and inbox state; Scribeswell for invitation intent and resource authority;
Identity/Access for recipient/account evidence. **Status:** proposed technical design,
not implemented runtime or implementation-readiness evidence.

First consumer: [Scribeswell Studies](../../../../_bmad-output/specs/spec-scribeswell-studies/SPEC.md).
Inherits platform [notification ownership](../decisions/0006-common-notification-capability.md),
[short transactions](../decisions/0022-short-transactions-and-external-service-calls.md),
[worker authority](../decisions/0026-worker-service-identity-and-ngo-scope.md),
[shutdown](../decisions/0027-bounded-worker-shutdown-and-deployment-reporting.md),
[event compatibility](../decisions/0028-event-payload-versions-and-queued-work-compatibility.md)
and [retry/retention](../decisions/0029-notification-retry-expiry-and-retention.md).
Accepted ADRs remain unchanged. Leave's organization inbox is not implemented,
redefined or made dependent on this draft.

## Scope and authority

Use a shared authorized HTTP capability, initially modular; it need not have a
separate deployment. Application/worker processes never import another owner's
server implementation or read its tables. Each producer owns its outbox; shared
notification storage/migrations belong to the notification owner.

Scribeswell intents and inbox entries are account-scoped with no synthetic
organization. A pre-registration email target is a delivery address awaiting account
binding, not an account grant or an organization scope. Shared keys may not read
Leave organization notifications/counts. A future organization variant requires its
own typed scope and current membership/capability policy before adoption.

## Application intent and outbox

Creating an invitation atomically commits invitation state, operation outcome,
required consequential evidence and immutable notification intent in Scribeswell's
own schema. The browser receives successful invitation creation only after that
commit. Channel outage does not roll it back or imply delivery success.

An explicit reminder uses its own replay-safe Scribeswell command/operation and
notification event ID, retaining the same invitation ID, pending expiry and root
event reference. Retrying that command reuses its event; another deliberate reminder
is a new communication. Neither grants access nor renews the invitation. Invite again
after expiry/decline explicitly creates a new invitation and new initial intent.

Proposed outbox fields: event UUID/type/version, original created-at, originating
command/operation, authoritative owner account and initiator actor, immutable payload,
not-after deadline, processing state, next-attempt-at, attempt count, claim owner/token/
expiry and confirmed handover receipt. Runtime may update delivery bookkeeping, not
rewrite original payload/time/target to make a retry look new. Physical constraints,
attribution and claim SQL must be selected before delivery code.

Restricted discovery exposes only due item/scope/claim metadata. Each item is processed
under its recorded producer/account context with a bounded lease and fencing token.
A stale holder cannot finalize or extend a newer claim. No stored end-user JWT,
user impersonation, broad cross-app credential or caller-selected organization context.
Before handover, check the local invitation is pending, its source still exists,
its target is unchanged and its server expiry has not passed. A verified null-to-
account binding with the same address key is a compatible refinement, handled by
the continuation below without rewriting the original payload. Obsolete unhanded work
is skipped with reason. Uncertain or accepted handover cannot be labelled unsent;
local skipping cannot recall an email or cancel receiver work.

## Proposed durable acceptance wire

Internal `POST /v1/intents`, with a producer-specific service credential authorized
for exact producer/event/template families. A browser bearer alone cannot submit.
Body is a closed versioned envelope:

```json
{
  "producer":"scribeswell",
  "event_id":"<nonnil UUID>",
  "event_type":"scribeswell.study.invitation.created",
  "event_version":1,
  "origin_created_at":"<server UTC>",
  "not_after":"<invitation expiry UTC>",
  "operation_id":"<source operation UUID>",
  "root_event_id":"<initial invitation event UUID>",
  "recipient":{
    "kind":"study_invitation",
    "invitation_id":"<UUID>",
    "account_id":null,
    "address_key":"<Identity-versioned key>",
    "email_address":"<private delivery address>"
  },
  "channels":["email","in_app"],
  "template":"scribeswell.study_invitation.v1"
}
```

Account ID is explicitly UUID-or-null, supplied from the approved domain/recipient
contract. The key/address are private delivery metadata, not identity or authority
for reading. Initial root event ID equals its event ID. Reminder type is
`scribeswell.study.invitation.reminded`, version 1, same invitation/root identifiers
and original invitation expiry; channels are email-only. In-app keeps the original
invitation entry/read state rather than creating duplicate unread items.

No arbitrary subject, HTML, template parameters, origin host or redirect URL is
accepted. Both templates render fixed minimal invitation wording. Do not include
study titles, author names, note text, highlights or recipient lists in email or
cached shared inbox payloads. Scribeswell's authorized Pending invitations view
resolves the agreed study title/sender/Can view details live. No changes to the
permitted content of Leave's separate event families follow from this template.

Receiver validates registered producer/schema/template/recipient/channel policy,
immutable time metadata and expiry, then atomically records acceptance, dedup and
channel jobs before HTTP acknowledgement. Proposed result is HTTP 202:
`{event_id, acceptance_id, status: accepted}`. Duplicate identical envelope returns
the same receipt without another job. Unique dedup key is `(producer,event_id)`;
a changed canonical payload under that key is HTTP 409 `operation_payload_mismatch`.
Unknown/malformed input is safe validation failure. Unsupported known durable
versions remain retained/flagged at their owning stage, never silently completed.
Producer keeps its item unresolved on rejection until a supported correction or
explicit terminal decision; no success is inferred from a transport timeout.

Mark producer handover complete only after matching durable receipt. Crash after
remote acceptance repeats the same envelope/event and resolves through receiver dedup.
Acceptance means the shared capability owns delivery work, not email sent/received,
notification read or invitation accepted.

## Pre-registration recipient and in-app continuation

With no bound account, email may proceed; in-app is `awaiting_recipient`, not failed
or published to an email-filtered inbox. No synthetic Auth/profile/account is created.
Scribeswell discovers pending invitations for a verified reader only through the
[recipient contract](scribeswell-study-enrollment.md), including current address
proof and stored account constraints. Scope/search/lookup privilege and batching
must be qualified; a shared inbox never searches all accounts' emails.

When that proof permits binding an unbound pending invitation, Scribeswell atomically
records its account binding/revision and a separate in-app continuation intent,
without changing pending state/deadline or accepting the study. The event is
`scribeswell.study.invitation.recipient_bound`, version 1, with a new event ID,
initial root-event reference and channels `[in_app]`. It carries exact invitation,
address-key and verified account constraint but no email address or resend request.
Its closed schema is distinct from the created/reminded variant; do not fill absent
variant fields by guessing current state.

Receiver validates exact producer/root/invitation/target and establishes at most one
inbox item for `(producer,invitation_id,account_id,template_family)`. Continuation can
arrive before original handover: validate its immutable linkage, create only the
in-app work, and reconcile later original acceptance without duplicate email/inbox.
It cannot bind a different account over an existing binding. Account deletion or
email reuse never transfers old records. First sign-in/notification creation is not
invitation acceptance. Producer skips binding work already known expired/withdrawn;
receiver enforces the immutable deadline. A withdrawal racing handover may still
publish a generic historical item, whose app destination rechecks current state;
this protocol promises no remote recall. Cross-message linkage and concurrent
ordering need receiver constraint tests before implementation.

## Channel delivery and truthful status

Shared workers render templates and own attempts, retry scheduling and provider
adapters. Record channel outcomes separately: pending, in-flight, provider-accepted,
published (in-app), retryable failure, correction-required, expired or suppressed.
A network loss after sending is uncertain until provider evidence or a qualified
idempotency mechanism resolves it. Durable receiver dedup does not by itself prove
exactly-once provider effects; do not blindly recreate events to fix an uncertain send.

Only validated provider acknowledgement supports provider-accepted; delivery/read
claims need separately verified provider semantics. In-app publication is not read.
User Share status Pending always means awaiting invitation acceptance, never email
delivery/read confirmation. Keep provider diagnostics outside business status.

No new email attempt starts after the earliest of origin-created-at plus 90 days,
immutable not-after, or an earlier known domain relevance cutoff. Shared receiver
validates expiry itself; retry/handover/recipient binding never extends invitation
validity. Late copies after dedup cleanup are rejected as expired, not fresh work.
Already-started remote effects cannot be assumed recalled at the deadline. Existing
identical accepted receipts may be acknowledged after expiry without creating work.

Follow platform ADR-0029: terminal outbox/attempt details remain 90 days after terminal
state; receiver dedup remains at least 90 days from acceptance and longer while
associated processing is unresolved. Preserve original timestamps across stages.
Expired notification processing does not expire/revoke an already accepted study
share or delete private notes. These durations do not apply to note-save receipts.
Inbox/read-state retention needs an explicit owner policy; it is not implicitly
assigned the same lifetime as notification attempt logs.

## Account inbox and read state — proposed wire

Browsers call Scribeswell API, not notification tables/Supabase. Proposed app routes
`GET /api/notifications` and `POST /api/notifications/{id}/read` proxy the owning
restricted HTTP contract. The shared facade is `GET /v1/account-inbox/scribeswell`
and `POST /v1/account-inbox/scribeswell/{id}/read`, with current bearer plus a
Scribeswell-specific inbox credential. No account/org/email override is accepted.

Shared inbox verifies the current account and app capability through Access using
the approved typed account check; Scribeswell additionally governs its invitation
and destination UI. Scope filtering occurs before rows, counts, cursor or read-state
writes. Denied/unavailable authority is not an empty inbox or a zero unread count.
Notification service caller privileges must be registered narrowly before runtime.

An explicit Studies/invitation entry may run the agreed first-use enrollment before
this scoped inbox read. Background sign-in or cross-app badge polling must not enroll
a reader into unrelated applications. Inbox eligibility is not Directory launcher
visibility and must not require PtS access. A platform-wide bell before Studies
enrollment needs its own approved account-inbox admission/composition contract;
this draft does not invent that authority or claim the shared UI already exists.

List query is `cursor` plus bounded `limit`; proposed default 50, maximum 100. Use
keyset order `(created_at DESC,notification_id DESC)`, with an opaque scope-bound
cursor that grants no authority and current rechecks on every page. Item created-at
is its first durable in-app publication time, never rewritten by later arrival,
linkage or reminders; it is distinct from event origin-created-at. Result:
`{items:[{notification_id,event_type,event_version,created_at,read_at,action}],
next_cursor,unread_count}`. Read-at is UTC-or-null; count uses the same current
account/application/visibility predicates. Action is the closed
`{kind: study_invitation, invitation_id}` value, not a supplied full URL.

The app builds a fixed same-origin, allowlisted invitation destination. No bearer
secret, address, note content or return URL appears in the link. Ordinary GET/opening
never accepts. An explicit idempotent read action marks only that account's item read;
opening UI may invoke it. If dismissal is exposed by shared UI, it uses an equally
scoped separate state action, never deletes/declines the underlying invitation.
Exact dismissal wire/retention belongs to the owning shared UI contract before use.

Pending invitations above Shared with me comes from Scribeswell's current pending
invitation query, not shared unread/dismissal flags. Reading/dismissing notification
cannot hide a pending invitation there; Accept/Decline is explicit, currently checked
and app-owned. A delivered old link opens current authorized state: pending,
accepted, expired or unavailable, with no source content granted by the notification.
Shared inbox placement/components are not chosen by this API draft; reuse proven
shared UI with the consuming story, preserving the agreed Studies surface.

## Operations, compatibility and closure

Application outbox and notification workers have distinct restricted owner identities,
authoritative per-item account/recipient context, bounded claims and external waits
outside database locks. Stop claiming on shutdown, drain only within configured bounds
and recover expired leases after forced stop. Supervisor records forced termination
and replacement/recovery evidence even if the worker cannot log. Healthy API, durable
handover, worker progress and provider health are separate observations; notification
faults must not disable public reading or erase already committed private study work.

Preserve type/version handlers for queued, in-flight and retryable work and active
producers. Receiver/schema/caller migrations precede compatible producer activation.
Select initial worker lease/drain/request/retry/body limits, provider idempotency and
callback validation, privacy/rate policy and inbox-retention rules before delivery.
No broker, universal workflow engine, provider choice or independent service deployment
is selected here. This draft is not readiness for any existing Leave implementation.

Required ST-17/26/29/30 and owner acceptance evidence: atomic invitation/intent rollback;
committed invite during provider outage; crash after remote acceptance; duplicate or
altered payload; unsupported version retained; reminder without new access/expiry;
pre-account delivery/binding and reversed arrival order; concurrent recipient conflict;
read/dismiss versus Accept; account/organization count isolation; expiry/cleanup boundary;
forced shutdown/fenced lease recovery; no payload/address/action URLs in logs. Prove
actual restricted roles, durable receipts and provider adapter semantics; mocks alone
cannot establish delivery. Controlled test recipients only, when implementation is
separately authorized.

Impact: first consumer proves generic outbox/client/error/inbox primitives before
scaffold or shared-UI promotion; domain templates/authority stay app-owned. Existing
root instructions and accepted ADRs suffice. This owner document is referenced from
the canonical Studies spec rather than copied into Leave planning. Runtime, provider
configuration, messages and migrations are unchanged.

## Leave organization-scoped timed-event consumer — 2026-10-25

This is an explicit additional organization variant for the already approved Leave E3
3.22/24 and E5 timed producers. The preceding Scribeswell account design is not silently
reinterpreted, and no implemented shared notification runtime is claimed. Reuse one owner
HTTP acceptance/dedup/channel delivery interface, not a second Leave transport service.
Leave scheduling/business relevance is owned by
[its timed contract](../../../../apps/leave/docs/architecture/contracts/e5-timed-work-and-errors.md).

Select internal POST `/v1/intents` with the existing exact producer credential policy.
Leave envelope fields: `producer: leave`, event UUID, closed event_type, event_version 1,
original UTC origin_created_at, not_after exactly 90 days after that creation, causal
operation/work UUID, actual occurrence UUID, `scope: {kind: organization, org_id}`,
recipient `{kind: organization_member, account_id, membership_id}`, channel array,
allowlisted template and minimal typed payload. UUID identity except membership positive
decimal string. One immutable event per actual recipient/account; event dedup key remains
`(producer,event_id)`, and the canonical scope/recipient/payload is part of comparison.

Initial timed families: `leave.approval.reminder` and `leave.approval.escalated` with
corresponding `.v1` templates. Payload contains authorized employee display name, leave
start/end dates, concise status, request UUID and an application-owned relative destination
constructed from that identity. No caller-provided host/redirect, type, employee note,
medical metadata or internal absence reason. The registered Leave producer policy fixes
allowed email/in-app channels; actual receipt acceptance is not email delivery/read.
Assignment/decision/source-change families keep their actual first-consumer E3/E5 contracts
rather than being incorrectly emitted as reminder events. This extension does not declare
all future Leave event-family artifacts complete.

Leave resolves current permitted recipient/account/membership and event relevance before
first handover through its authorized owner interfaces. Accountless recipient cannot be
replaced by guessed email/login or synthetic membership; keep required intent recoverable
until actual recipient resolution/authorized terminal handling. Receiver verifies producer,
org/recipient binding and allowed schema/content/channel policy; application links never
grant read access. Accepted organization inbox reads recheck current exact account/org/
membership policy under the actual E3 inbox contract. Shared delivery never queries Leave
workflow to decide approval coverage or whether a step is still outstanding.

HTTP 202 remains `{event_id, acceptance_id, status: accepted}` after receiver durable
acceptance/dedup/channel intent commit. An identical replay returns the same receipt;
changed envelope under the same event ID is 409 operation_payload_mismatch, retaining
original. Leave completes handover only after matching receipt. Unknown response remains
unknown; do not reset original time/identity or clear/recreate outbox. Receiver rejects
new acceptance at or after not_after even after dedup cleanup; existing exact accepted
receipt does not mean fresh delivery work. Terminal producer retention is 90 days after
terminal state; receiver dedup is at least 90 days from acceptance and while unresolved,
under existing P-0029/Leave retention decisions. Unsupported versions retained/flagged.

Actual first organization consumer must prove current recipient/org isolation, minimal
payload, duplicate/changed/expired events, lost acceptance response and current inbox
access independently from Leave domain recurrence tests. Preserve the distinct Scribeswell
recipient/scope/expiry branches. Scope/caller/receiver implementation, artifact generation
and real PostgreSQL/HTTP verification remain delivery work; no tests run by this contract.
