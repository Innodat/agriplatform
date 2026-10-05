# E1 controlled provisioning and evidence

**Status:** Command/evidence design; operator adapter, owner DDL and executable verification pending  
**Date:** 2026-10-05  
**Consumers:** E1-ID/ACCESS/PEOPLE/ENV/WRITE/REF/CHOICES

This defines owner-controlled setup within the existing BMAD delivery plan. It is not
an administration UI, a generic workflow engine or permission to change live accounts.
Authority: [identity contract](./identity-access-employment-e1.md),
[admission contract](./application-admission-and-discovery.md),
[audit ownership](./e1-security-audit-ownership.md), and platform ADR-0012/0020/0023/0025.

## Invocation and owner boundary

Use an explicitly targeted operator command/fixture adapter implemented by each owning
service. Normal application credentials cannot invoke provisioning or write its tables.
The operator adapter uses a restricted owner writer, not the migrator or a universal
cross-owner service role. It derives executing actor from the authenticated operator or
approved automation identity; actor fields supplied in a JSON manifest are not authority.
If automation acts for a human, record verified initiator separately from executor.
E1 bootstrap establishes the minimal trusted operator mapping through controlled setup;
do not expose a self-registration or self-grant endpoint to solve bootstrap.

An invocation includes a versioned command document, explicit allowlisted target identity
and a manifest/run reference. Before any writes, validate the target against configured
nonproduction/disposable bounds for tests. Production adoption requires its separate
approved target verification/runbook; no localhost/default URL or missing environment
variable can redirect provisioning to a real target. Credential values, personal data
and arbitrary executable SQL do not belong in checked-in manifests or command logs.
Command names below are contract identifiers, not installed shell commands.

Each owner receives one local command at a time. Shared setup may sequence commands
through existing tooling with a per-step completion record, but there is no distributed
transaction. Never roll back another owner's committed state automatically after failure.
Consumers stay unactivated until their required steps verify successfully.

## Common envelope and outcome

Required input fields: `schema_version: 1`, UUID `operation_id`, registered `command`,
explicit `scope`, typed `payload`, bounded `reason_code`, and optional opaque
`evidence_ref`. Scope is `{kind: platform}` or `{kind: organization, org_id: UUID}`;
only commands listed as platform-scoped accept platform scope. No sentinel org ID.
Reject unknown fields, malformed UUIDs/revisions and unsupported command versions.
Provisioning reason codes initially distinguish `initial_setup`, `synthetic_fixture`,
`identity_adoption`, `access_change`, and `setup_correction`. References are identifiers
for controlled records, not URLs containing tokens or copied verification documents.

For existing mutable targets, include expected positive decimal-string revision; creates
require explicit expected absence. A command must identify its exact target, never
“the latest employee/account/membership” inferred at execution. All stable input values,
expected revisions/absence, scope, command/version, reason and evidence reference bind
to the operation fingerprint. Verified executor is part of the operation's owner-local
scope. Exclude timestamps and freshly obtained authorization observations from stable
input; keep those as execution evidence.

Use the already selected versioned SHA-256/JCS consistency mechanism for these bounded
identifier/date/configuration commands, subject to the recorded confidentiality-risk
assessment; do not copy private verification documents or secrets into fingerprint
input. The same operation with changed input fails; concurrent identical attempts can
commit once. A fresh command uses a new operation ID and current expected state.

Success: `{operation_id, status: committed, result: {command, target, disposition,
revision, event_id}}`. Target carries the command's stable owner identifiers. Disposition
is `created`, `changed` or `unchanged`; revision/event_id are null only when the target
contract genuinely lacks a revision or no transition event was required. Typed owner
result variants constrain those cases; do not expose an unvalidated generic dictionary.
Return only after durable local commit. Receipt lookup requires current operator authority,
returns the original compact result, and is not proof of current target state. Missing
receipt is `unresolved`, not a failed command or permission to issue a fresh duplicate.

## Minimum command catalogue

| Owner / command | Scope and payload | Guard and local effect |
| --- | --- | --- |
| Identity `person.create` | platform; stable person_id, expected absence | Create independent person identity without Auth account, membership or grants. No email matching. |
| Identity `account.link_person` | platform; account_id, person_id, stable actor_id, required verification evidence_ref; expected absence or explicit existing-link revision | Verify the account/person and chosen legacy actor mapping; write link/history and actor association atomically. E1 adoption accepts absent or identical verified mapping; conflicting relink requires separate correction design, not automatic overwrite/merge. |
| Identity `membership.join` | organization; account_id, expected_previous_membership_id (null only for first-ever membership), explicit initial owner flag default false | Serialize the org/account membership scope, validate expected history and absence of active membership, allocate new bigint ID and leave roles/grants empty. Returning after retirement requires naming the retired predecessor. Delayed first-join/rejoin cannot recreate access against a changed history. |
| Identity `membership.retire` | organization; exact membership_id/account_id and expected revision | Mark that membership retired with immutable evidence; never target a replacement membership. No cross-owner deletion or employee termination. Add the required membership revision through Identity's owned migration. |
| Access `application.register` / `permission.register` | platform; explicit app ID/scope or exact permission-to-app association, expected absence | Register immutable identity/mapping; new app disabled. Identical existing registration may report unchanged; conflicting mapping fails. |
| Access `application.set_enabled` | platform; app_id, boolean enabled, expected revision | Change global admission, revision and evidence; no grant deletion or silent provisioning. |
| Access `organization_application.configure` | organization; app_id, boolean enabled, expected absence or revision | Establish/update org enablement, verifying the organization externally before the local write. |
| Access `grant.assign` / `grant.revoke` | organization; exact account_id/membership_id/permission and expected absence or grant revision | Validate registered permission and exact current membership for assignment; persist explicit binding or revocation. Regrant is deliberate, never inferred from employment or app enablement. Revoke identifies its existing binding so a delayed revoke cannot erase a later regrant. |
| People `employment.create` | organization; stable employment_id, verified person_id, expected absence | Create the one enduring relationship with revision 1 and owner change evidence, without creating access or periods implicitly. |
| People `employment.period_add` | organization; employment_id, stable period_id, start_date/end_date, expected relationship revision | Add an inclusive nonoverlapping period, advance relationship revision and record minimal change evidence atomically. No E2 public correction/removal API is introduced. |
| Leave initial configuration fixture | organization; explicit type/version IDs, code, name, modes and declared applicability under the owning choice contract | Publish initial choice metadata/pointer through one Leave-owned command with expected absence and evidence. Exact fixture command/result schema is Leave-owned; no full policy fields or public editor. |

The operator's authority must be checked for the exact owner/command/scope; a runtime
service key is not an operator credential. Reads to validate external references precede
local write locks; later checks still use current references and membership binding.
No command borrows another owner's table-write authority. New People periods affecting
consequential workflows require E2/E5 change-impact contracts before production use;
E1 fixture/provisioning scope does not bypass them.

## Minimal owner-local records

Use an owner-local immutable `operation_outcome` keyed by `(executor_actor_id, operation_id)`
with command/version, explicit scope, fingerprint/version, UTC creation time and compact
typed result. Scope is bound in the fingerprint and checked on lookup, not inferred from
a possibly null organization field. This platform-or-organization shape belongs to
operator evidence only; organization business/grant tables retain non-null org_id.
No full input/credential/verification-document snapshot belongs in an outcome.

Use owner-local immutable `change_event` with event UUID, type/version, scope, executor
actor and optional verified initiator, operation ID, target identifiers, UTC timestamp,
reason/evidence reference and allowlisted before/after transition data. Identity link
evidence contains mapping IDs; membership evidence contains lifecycle/owner transition;
Access contains enablement or exact grant binding/revocation; People contains period IDs
and changed dates plus relationship revision. No unrelated profile, email, medical note
or whole-row dump. People's existing planned employment_change is its domain event;
do not duplicate it into another generic event table for the same change.

Changed business state, required event and operation outcome commit in one local
transaction. Missing required evidence aborts the whole local change. An authorized
unchanged command records a compact outcome but creates no fictitious changed-state
event or revision increment. Duplicate replay creates no second event. Identity's
membership-history guard must share the serialization boundary with joins/retirements;
final lock/constraint implementation is part of its schema validation.

Retain these E1 outcomes/events without automatic cleanup until owner retention and
retry-expiry contracts are approved. Do not add an archive database or pruning worker.
Diagnostics contain safe operation/run references and error identifiers, never command
payload dumps. Remote diagnostic export failure does not undo a durable local commit.
This setup evidence does not introduce audits for ordinary draft reads or every autosave.

## Failure/recovery and required tests

Distinguish validation, unauthorized operator, target mismatch, expected-state conflict,
operation-payload mismatch and unavailable required dependency. Use stable safe error
identifiers; never echo verification material or database constraint text. Exact adapter
transport/exit-code mapping is settled with the owner implementation, not a new public API.
On lost response, resolve the same operation under current authority before retrying.
Per-owner committed steps remain visible after a later owner fails; resume from verified
outcomes, not from a successful exit code assumed for the whole manifest.

Fixtures must demonstrate invalid target refusal before writes, runtime-credential denial,
spoofed manifest actor rejection, same/changed/concurrent retry, stale revision, delayed
membership join/retirement, partial cross-owner setup failure and safe resume, local
history failure rollback, no sensitive artifacts, and revoked operator outcome-access
denial. Test restricted database roles and actual commits. No production users/data are
fixtures. Record exact commands, initial acceptance failure and passing checks in Build.

## Remaining implementation-readiness validation and impacts

Finalize operator authentication/authority adapter, exact command/result models and
size limits, owner migration grants, actor/link schema and membership serialization;
verify clean/adopt rehearsals and align existing legacy writers. The catalogue is the
minimum setup scope, not proof those mechanisms already exist. No new approval ritual
for each draft or grant lookup is introduced.

Scaffold: promote proven command/transaction/evidence fixtures with first owners; no
central provisioning database or generic reconciliation engine. Shared UI: none in E1.
Agent context: existing scope/ATDD/release instructions apply. Documentation: owning
contracts and tracker link this catalogue. Accepted ADRs unchanged. No operator command,
account, grant, schema, environment or application code was executed/changed here.
