# Organization membership and administration continuity

**Status:** Technical planning candidate for the consolidated review, 2026-10-26.
**Owner:** services/access, which owns both adopted Identity membership and Access grants.
**Consumers:** 2.2–2.5, 2.9–2.10 and every alternate membership/role writer.

## Selected invariant and self-removal policy

For an ordinarily administered organization, preserve at least one active is_owner
membership AND at least one active exact-membership assignment of the protected built-in
Organization Administrator role. These may be different people. Owner status alone grants
no capability. A custom application role, employment, account linkage, tenant enrollment,
prepared approval or retained retired grant does not count as this administrator. The
built-in role must retain its registered organization administration capabilities and
cannot be edited/deleted through the custom-role editor. Application enablement does not
remove organization administration. Count exact current organization/membership bindings,
not JWT owner claims or role labels. This is a conservative continuity floor; delegations
can still authorize their defined actions without counting toward the floor.

Block self-removal from the organization in the ordinary removal UI/API. Another currently
authorized administrator performs it after a replacement is active. Allow one's own app
role changes through existing review/authority checks, but apply the continuity floor
if a change removes the protected organization administrator assignment. Do not introduce
a Leave organization-exit feature or silently transfer ownership. The reviewed UI says
why removal is blocked and points to existing authorized membership/access administration.

This does not promise that an external identity provider cannot suspend all administrators.
A disabled/unavailable login cannot be repaired by inventing a universal admin. Existing
restricted bootstrap/adoption authority is the recovery lane: independently verify the
organization/account, record explicit owner/role approval and evidence, then establish a
valid current membership and explicitly assign the protected role. No browser operator
credential, email-only recovery or automatic grants. A legacy organization already below
the floor requires controlled repair before ordinary destructive administration.

## Atomic guard across the actual single runtime owner

Identity membership and Access permissions are logical boundaries inside services/access;
People and applications are different owners. Use one owner-local PostgreSQL transaction
for this invariant, with narrow separately owned SQL routines and explicit EXECUTE rights
in controlled migrations. The browser, Leave, People and general runtime SQL roles never
receive cross-schema table access. No HTTP wait or distributed transaction is needed to
count this owner's own membership/grants. If a future deployment separates these into
independent stores, this model must be replaced before that separation; two unrelated
prechecks do not preserve continuity.

Lock the organization administration guard first, then exact membership slots in stable
ID order, then protected role/assignment slots. Guard identity is the real organization's
existing stable owner row, not a generic workflow engine. Every writer which can change
either floor must use that same guard: membership join/retire, protected administrator
assign/revoke, role/admission compatibility changes, account lifecycle changes owned
locally, prepared activation and restricted operator/bootstrap/adoption paths. Ordinary
custom-role edits cannot modify the protected built-in definition. Enforce through narrow
owner command routines/write privileges; a convention in one UI is insufficient.

In the same short transaction, verify reviewed revisions, operation identity, current
actor membership and administration authorization, apply the proposed change, verify both
post-change floors, then commit mutation, immutable audit, operation result and required
outbound intent. Failed floor/audit/constraint rolls back all local effects. Lock wait
<=2 seconds and foreground command <=10 seconds; outside verification <=2 seconds/call
and outside locks. Stale review gives review_changed, self-removal gives self_removal_not_supported,
missing floors give last_owner or last_organization_administrator. Safe authorized details
identify the current remedy, without exposing unauthorized holder lists.

A and B cannot each remove the other using preauthorized forms: the winner changes current
membership/authority; the loser rechecks under the organization guard. Removing B while
B revokes A's protected admin role is likewise serialized. Only the operation preserving
both floors and current actor authority may commit. Provision a replacement first; there
is no implicit swap or queued success. Recovery/timeout returns original scoped operation
outcome, never retries a different membership ID.

Retirement remains immediate for new organization checks without deleting foreign grants.
Rejoin is a new membership with a reviewed predecessor and no old role restoration. Owner
flag changes use the restricted existing owner lane, not a new ordinary transfer screen;
that lane now also enforces continuity and audit. Archived historical membership/actor/
permission records remain immutable evidence under their owning retention. External
provider/session outages deny new protected work; they do not erase the organization floor.

## Planned evidence, size and impacts

2.10 owns retirement integration plus this guard on the existing membership command;
2.2 owns protected assignment/revoke participation and 2.9 its activation participation.
The shared guard is first proved with membership/assignment fixtures rather than a future
Leave workflow. Verify both last-member floors independently, nonowner admin versus owner
without grant, self-removal, current-authority loss, concurrent cross-removal and cross-
revoke, command replay after rejoin, operator alternate writes, real restricted privileges
and complete rollback. E5 later proves actual missing-approver/reroute effects; no forward
E5 dependency is created here. Preserve existing grant scope and resource checks.

Scaffold: reuse only proved scoped local command/guard fixtures. Shared UI: existing
membership review, holder links and typed conflict/remedy handling. Agent context:
existing owner/no-implicit-authority rules suffice. Documentation: owner permissions,
migration inventory and controlled recovery procedure with actual implementation.
ADR: candidate continuity/self-removal selections; accepted decisions unchanged. The
single owner-local delta remains bounded; no generic distributed coordinator is added.
No membership, capability, provider setting, runtime code or live database changed.

## Consolidated adoption — accepted 2026-10-26

The user explicitly approved the completed consolidated planning package. The reviewed
choices and bounds in this contract are adopted under [the acceptance decision](../decisions/0064-approved-onboarding-continuity-and-content-contracts.md).
Earlier candidate/pending-review wording is historical and superseded for these choices.
Actual implementation and provider/database/browser/recovery proof remain delivery work.
The user requires a new Codex session before implementation; no runtime action here.
