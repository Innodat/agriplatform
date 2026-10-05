# E1 security and business audit ownership proposal

**Status:** Ownership/failure policy approved; own-draft evidence simplified by user agreement 2026-10-02; no implementation
**Date:** 2026-10-02
**Sources:** [ADR-0023](../decisions/0023-structured-operational-logs-and-sensitive-data.md),
[ADR-0025](../decisions/0025-record-attribution-and-audit-provenance.md),
[Leave features §1 and §20](../../../../apps/leave/docs/features.md),
[owning draft contract](../../../../apps/leave/docs/architecture/contracts/e1-draft-persistence-and-recovery.md)

## Ownership and required events

Keep authoritative records with the service performing the action. Diagnostic log
aggregation may correlate them; no central synchronous audit HTTP service is needed
on every save. Platform supplies proven record/context mechanisms through scaffolding,
not a universal runtime credential or database writable by every application.

| Action/evidence | Owner and proposed minimum treatment |
| --- | --- |
| Sign-in success/failure, session revocation | Auth provider is authoritative for authentication events. Verify available export/access/retention before pilot; a frontend callback must not pretend to be a complete sign-in audit. Leave records its own verified session/context establishment, not a duplicate provider claim. |
| Verified account/person linking, membership, application enablement and grant changes | Identity/Access owner; immutable transition evidence atomic with the successful local change, including authorized operator and scope. Applies to E1 provisioning as well as future E2 UI. |
| Explicit organization selection/switch | Leave records the verified target organization/account/actor/membership and action identity before confirming selection. Previous organization is optional context, verified where available; a browser-supplied previous value is not authoritative provenance. |
| Draft creation/update | Leave; server-managed created_by/created_at/updated_by/updated_at fields on the draft, revision and atomic operation outcome records. No additional creation/autosave audit row or full form history required. |
| Draft discard | Leave; minimal immutable consequential transition evidence atomic with payload removal, lifecycle/scope change and outcome recording. No discarded payload in the audit. |
| Ordinary autosave/resume and duplicate retries | Existing atomic operation outcome records plus draft attribution/revision provide the technical evidence. Do not add a second full form history or duplicate audit rows per retry. A same-input new save is allowed under the existing revision contract. |
| Ordinary own-draft read | Leave verifies current access/ownership and returns a consistent snapshot. No separate read-audit event or audit persistence gate. Other people’s access and specifically designated sensitive reads require their own later classification/contract. |
| Denied/failed attempts and service faults | Safe structured security/diagnostic events at the detecting service. Never label attempts as committed changes or copy tokens/raw payloads into failure logs. |

Organization selection does not persist a universal active-organization preference
that makes separate tabs switch each other. Every request still carries its own
validated scope and rechecks current authority. A selection acknowledgement and its
operation identity need a bounded idempotent local contract; do not audit every render
or ordinary scoped request as a fresh organization switch. On a failed switch preserve
the safe original context and use the existing switch recovery UX.

Draft evidence simplification agreed 2026-10-02: created/last-updated values live on
the draft record. They are attribution, not a history of edits. Ordinary own-draft
creation/updates need no duplicate audit event, and reopening one's own draft needs
no read-audit write. Required operation outcomes still commit atomically with writes;
discard still has minimal consequential evidence. This narrows the earlier E1 proposal,
not the platform requirement to audit designated sensitive reads in later workflows.

## Minimal evidence and privacy

Event schema requires event UUID, stable event type/version, server UTC time, owner,
verified actor/account reference where known, organization/membership when applicable,
target identity, action/outcome, operation/decision/trace links as applicable and
allowlisted transition metadata. Public/account-only events have explicit scope kinds;
do not fabricate an organization. Human initiator/service executor remain distinct.
An unauthenticated denial cannot acquire an invented verified actor.

Before/after evidence contains relevant grant/link/lifecycle identifiers and states,
not indiscriminate row snapshots. Record a reason only when the owning action requires
one; do not add a reason prompt to ordinary sign-in, selection or saving. Preserve
immutable attribution after account replacement. No notes, medical contents, secrets,
full signed URLs or sensitive form/query payloads in these E1 records or diagnostics.
Runtime authority permits insert and authorized read, not rewrite/delete of audit.
Retention/purge authority and operational access are explicit owner responsibilities.

## Failure policy — approved 2026-10-02

1. If required local mutation audit/outcome evidence cannot persist, the mutation must
   not commit. Use the same local transaction; an unrelated remote log collector is
   not part of that transaction. If commit outcome is uncertain, use normal operation
   recovery instead of claiming rollback.
2. If required organization-selection evidence cannot persist, do not acknowledge the
   new selection. Preserve a safe prior context and offer retry; no automatic switch
   into another organization and no claim that membership was revoked.
3. Where a later workflow explicitly requires sensitive-read evidence, its contract
   must define recording before release and failure behavior. Ordinary E1 own-draft
   reads have no such audit-write requirement; continue to enforce current authority
   and consistent input/revision reads.
4. Failure to export already-durable evidence or to ship ordinary diagnostics does not
   undo committed work, sign users out or block public Scribeswell reading. Report the
   operational failure through existing monitoring and recover export separately.
   Never claim provider sign-in failed solely because application telemetry failed.
5. Failed/denied authentication or authorization stays failed/denied even if recording
   that attempt also fails; log delivery must not become an access bypass.

No organization audit requirement is imposed on anonymous public reader navigation.
Later protected Scribeswell account actions define their own applicable evidence.
No implementation of generic audit dashboards or cross-service event delivery is an
E1 prerequisite. Before pilot, select actual provider evidence access, owner retention
periods and authorized investigation procedures; do not silently use a diagnostic
log's default retention as the business/security policy.

## Delivery evidence and impacts

E1-ENTRY-10 and E1-AC-01/06/09/10/12/13/15/17/18 require fixtures for atomic audit
failure, commit uncertainty, duplicate retry, selection failure, own-draft reads without audit-write side effects,
diagnostics/export failure without failed business commits, actor spoofing,
scoped investigator access and note/token absence. Use actual restricted roles and
owner persistence where claims depend on them. Formal selection-event schemas,
migration/retention policy and executable evidence remain open.

Scaffold: immutable event structure, verified context, atomic writer hooks and safe
logging fixtures; keep event catalog/retention application-owned. Shared UI: reuse
existing unavailable/retry/context recovery, no new audit field or confirmation screen.
Agent context: existing ADR-0023/0025 rules suffice. Documentation: owning contract,
Leave tracker, acceptance map and epic traceability. ADR: implements existing rules;
no accepted decision changed. No application code, tests or database changes performed.


## E1 selection and read-event wire design — 2026-10-02

The user approved the local-required-evidence versus remote-export failure distinction.
The following supplies a bounded technical design under that agreement.

### Organization selection acknowledgement

Use `POST /api/v1/organizations/{org_id}/context/selection` with exactly
`{operation_id: <UUID>}`. One intentional selection uses one operation UUID; retries
reuse it. The backend verifies account, current membership, organization-app enablement
and an applicable Leave capability. No employment record is required to select an
otherwise accessible organization. Do not request an employee ID or trust a client
claim about its prior organization. E1 omits prior-organization metadata.

Persist one immutable `leave.organization_context_selected` event, event version 1,
with verified organization/account/actor/membership, operation UUID, authorization
decision UUID/time and server creation time. The event records an authorized selection
attempt durably accepted by the server, not proof of browser navigation or sign-in.
HTTP 200 follows commit and contains `{operation_id, status: committed, result:
{command: select_organization, org_id, event_id}}`. A matching retry returns the
original result after fresh authorization; it does not create another event. No
saved draft, active-organization database flag, grant or employee row changes here.

Use `GET /api/v1/organizations/{org_id}/context/operations/{operation_id}` for authorized
selection outcome recovery: the same committed response or `{operation_id, status:
unresolved}`. A missing event is unresolved, not proof another request cannot commit.
This separate endpoint/table contract avoids weakening draft outcome records' mandatory
employment/draft references. Both responses are private/no-store and caller-scoped.

Uniqueness on verified `(org_id, actor_id, operation_id)` and the fixed selection
command suffice: there is no editable payload requiring a fingerprint here. Enforce
organization scope and immutable insert/read permissions; audit investigation access
is separately authorized. Resolve concurrent insert/retry through the unique constraint
and a fresh committed read, never two accepted events. Use current server context,
not browser-supplied actor/time/audit fields. Exact DDL is delivery evidence.

Use the existing 10-second execution deadline, 12-second browser mutation wait and
bounded 15-second recovery cycle (up to three lookups/one identical retry) as the
initial selection transport budget. A lookup/retry checks authority again. A definitive
denial takes the access-loss route; unresolved selection offers Retry/Stay without
exposing target business data as if selection succeeded. A historical acknowledgement
never authorizes a later request or forces navigation after the user has left that
selection attempt. The frontend applies it only to its current pending transition.

Save/resolve the original organization's edits first under the approved switch rules.
Then request target selection; if this step fails, the original acknowledged draft
remains saved. Preserve original context only while still authorized. Deep links and
same-user session return use the same audited context establishment before entering
the target workspace. Ordinary rerenders and requests in an established context do not
produce a fresh selection event. Independent tabs retain independent context.

### Own-draft reads — simplified 2026-10-02

Do not emit `leave.draft_content_release_authorized` for ordinary own-draft reads;
the earlier proposed event is withdrawn before implementation. Read the saved input
and revision consistently after current authorization/ownership checks. No audit insert,
draft revision increment or mutation operation ID is needed for this GET. Never expose
protected content on access/dependency failure. Later sensitive or third-party access
needs explicit assessment; this is not blanket exclusion of draft data from security.

### Required contract checks

Selection: concurrent identical calls produce one event; lost acknowledgement resolves
without duplicate events; access revoked before retry prevents outcome disclosure;
audit failure leaves no acknowledged selection; two tabs do not change one another;
late acknowledgement after Stay does not navigate; prior draft stays saved if the
target selection fails. Read: current authority and input/revision snapshots are
consistent; returned text is absent from diagnostics; repeated ordinary own-draft
reads neither insert audit events nor advance the draft revision. Verify restricted roles and pooled
context reuse. Include both in E1-AC-01/06/09/12/13/15/17/18 as applicable.

Scaffold promotion remains the existing same-item obligation: reusable scoped
acknowledgement/audit writers and transport adapters, not mandatory employment or
universal audit of public page views. Leave event types and transition flow stay
application-owned. No new UI confirmation, accepted ADR change or code implementation.


The [controlled provisioning contract](./e1-controlled-provisioning-and-evidence.md) now defines E1 owner-command envelopes, compact outcomes and allowlisted transition evidence. It preserves the agreed absence of ordinary own-draft read/autosave audit rows. Exact owner schemas and executable verification remain readiness work.
