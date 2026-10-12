# E1 controlled provisioning and evidence

> **Capability-scope refinement — 2026-10-06:** [ADR-0053](../decisions/0053-capability-scoped-access-in-mixed-scope-applications.md)
> makes account/organization scope a property of each capability. Current PtS
> capabilities are account-scoped; future organization features do not change them.
> Earlier exclusive application scope fields require the refinement below/in the
> owning admission contract before readiness. No implicit cross-scope authority.

> **Governing update — 2026-10-06:** [ADR-0052](../decisions/0052-pts-account-scoped-access-and-coordinated-adoption.md)
> makes PtS account-scoped now, with individual grants and no organization/membership
> requirement. Earlier organization-only E1/PtS and mandatory v1-preservation passages
> below are superseded for PtS. Leave organization contracts remain binding. Account
> grant/check/discovery/operator schemas and PtS corpus/Content transition are required
> pre-story inputs, not implemented by this notice.

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
| Identity `actor.register_system` | platform; explicit actor_id, kind system/service, stable actor_key, display_name, expected absence | Controlled Identity authority only; preserve verified System/Migrate identities. Identical registration may be unchanged; conflicting key/ID/kind rejected. No Auth, membership or grant creation. Bootstrap migrator is established through controlled baseline, not this command authenticating itself. |
| Identity `account_actor.ensure` | platform; verified account_id, intended stable actor_id, expected absence, required evidence_ref | Establish account attribution without person/membership/employment. Identical verified mapping may return unchanged; conflicting account/actor kind or binding fails. Preserve classified legacy actor identity; no implicit relink or permission grant. |
| Identity `account.link_person` | platform; account_id, person_id, stable actor_id, required verification evidence_ref; expected absence or explicit existing-link revision | Verify the account/person and existing stable account actor mapping; write person link/history atomically without replacing the actor. E1 adoption accepts absent or identical verified mapping; conflicting relink requires separate correction design, not automatic overwrite/merge. |
| Identity `membership.join` | organization; account_id, expected_previous_membership_id (null only for first-ever membership), explicit initial owner flag default false | Serialize the org/account membership scope, validate expected history and absence of active membership, allocate new bigint ID and leave roles/grants empty. Returning after retirement requires naming the retired predecessor. Delayed first-join/rejoin cannot recreate access against a changed history. |
| Identity `membership.retire` | organization; exact membership_id/account_id and expected revision | Mark that membership retired with immutable evidence; never target a replacement membership. No cross-owner deletion or employee termination. Add the required membership revision through Identity's owned migration. |
| Access `application.register` / `permission.register` | platform; explicit app ID/scope or exact permission-to-app association, expected absence | Register immutable identity/mapping; new app disabled. Identical existing registration may report unchanged; conflicting mapping fails. |
| Access `application.set_enabled` | platform; app_id, boolean enabled, expected revision | Change global admission, revision and evidence; no grant deletion or silent provisioning. |
| Access `organization_application.configure` | organization; app_id, boolean enabled, expected absence or revision | Establish/update org enablement, verifying the organization externally before the local write. |
| Access `grant.assign` / `grant.revoke` | organization; exact account_id/membership_id/permission and expected absence or grant revision | Validate registered permission and exact current membership for assignment; persist explicit binding or revocation. Regrant is deliberate, never inferred from employment or app enablement. Revoke identifies its existing binding so a delayed revoke cannot erase a later regrant. |
| Access `account_grant.assign` / `account_grant.revoke` | platform; exact account_id/permission, existing grant_id for revoke/update, expected absence or grant revision | Validate account-scoped capability; assignment verifies target account, revoke may remove an inactive account's existing grant. No membership needed. Deliberate regrant uses current revision; old retry cannot undo it. Owner command/app/account authority required, not organization-admin status. |
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


Account grants — 2026-10-07: [individual grant design](./application-admission-and-discovery.md#individual-grant-persistence-and-administration--2026-10-07)
adds explicit Access platform-operator commands, using the existing envelope/evidence.
No third operator scope is needed: target account is validated payload, not authenticated
executor. Account grant authority remains separate from organization administration.
Separate constrained account_grants storage replaces any inferred nullable-org approach;
exact typed payload/result bounds and operator adapter remain readiness work.


Account actor setup — 2026-10-07: [account-only actor resolution](./identity-access-employment-e1.md#account-only-actor-resolution--2026-10-07)
adds controlled account_actor.ensure before any optional person link. The account_person
link command consumes that stable actor; it must not replace account attribution. Runtime
permission reads create no actor/person/grant rows. Typed models, deletion/history constraints
and trusted operator bootstrap remain ID-B readiness inputs.


Actor registry adoption — ADR-0056, accepted 2026-10-07: Identity-owned controlled bootstrap
retains System/Migrate and explicitly registers required service actors without new Auth
accounts. Verified operator/service context determines attribution; no arbitrary actor
field is authority. Account profiles remain Auth-linked; account_actor.ensure maps them
to durable actors. Exact system/service setup command schema and trust bootstrap remain
ID-B readiness inputs; no actor per run or generic actor-management UI is introduced.


Actor schema refinement — 2026-10-07: [minimum persistence/lifecycle](./identity-access-employment-e1.md#minimum-actor-persistence-and-lifecycle--2026-10-07)
selects actor plus permanent account_actor association, retained historical account ID
without a deletion cascade and current-live-account checks for runtime resolution.
System/service registration uses the existing platform operator envelope. No missing-actor
fallback to System/Migrate; clean bootstrap provenance is explicit and historical adoption
preserves old evidence. Exact command models/bounds and privileges remain before readiness.


## Operator execution surface — proposed 2026-10-08

**Direction approved by the user, 2026-10-08; concrete identity binding and privileges remain readiness inputs.**

For E1, implement the existing controlled commands as owner-local command-line entry
points, runnable through protected deployment/operator tooling. No public provisioning
HTTP endpoint or new administration dashboard is needed for this initial setup. E2's
user-facing administration remains separate and must use authorized application/service
HTTP contracts; a CLI is not the permanent product administration interface.

Use the owning component's restricted operator writer and registered execution identity.
The execution adapter must establish that identity from authenticated infrastructure
context and a protected mapping; command payloads, a supplied actor ID, a shell username
or knowledge of a target UUID cannot establish authority. Define a concrete supported
credential/identity binding before readiness; no universal cross-owner credential and
no migrator role for routine setup. Infrastructure access alone must not implicitly
allow every owner command or organization scope.

For automation, record its registered service actor as executor. Record a human initiator
only when the invocation system supplies verified identity evidence; do not invent a
human from an unverified command flag. Preserve the existing operation ID, expected-state,
atomic outcome/audit, explicit environment target and safe logging contract.

Example sequence: the operator explicitly targets the test environment, assigns an
existing account the PtS read capability through Access's owned command, and checks the
committed receipt plus a current authorization check. The command cannot write Identity,
People or Content tables. Failed/uncertain steps use the existing outcome lookup and
same-operation retry rules, not a fresh blind assignment.

ID-B owns the first verified execution/attribution adapter; ACCESS-A and PEOPLE reuse
proven domain-neutral envelope/target/evidence handling while retaining owner command
policy and persistence. Negative acceptance proves normal runtime credentials cannot
provision, wrong target/owner/scope fails, actor spoofing fails and revoked operator
credentials cannot execute or retrieve outcomes. Exact invocation syntax, identity
binding and privilege grants are readiness inputs, not installed commands.

Scaffold: promote tested owner-command support with its first consumer, no universal
administration service. Shared UI: none for E1 operator execution. Agent context/ADRs:
existing ownership, attribution and release-safety rules suffice. Documentation: owner
runbooks and command catalogue must carry the selected invocation and recovery evidence.


## Setup verification boundary — proposed 2026-10-08

**Approved by the user, 2026-10-08.** The broader hosted verification-app suggestion
is recorded separately; it does not authorize production fixture execution.

A committed setup receipt proves its owner-local change, not that all consumers are
configured, deployed or usable. Separate command completion from consumer acceptance
in existing test/runbook output; no central readiness database or new status API.

For the integrated nonproduction fixture, use current real authorization and consumer
paths with synthetic accounts. PtS proves an account with no organization can enter and
read; without the documents grant, a private document request is denied; the specifically
granted documents capability permits the associated file; revocation denies the next
request. Leave proves the selected organization's enablement, current membership and
own-request capability plus the established person/employment fixture; employment alone
cannot admit the account. Once the final E1 consumer exists, verify create/resume,
autosave, close and reopen through the actual browser.

Keep evidence staged by delivery owner: ACCESS-A proves committed configuration only;
ACCESS-B proves effective authorization; PTS-ADOPT proves the deployed PtS consumer;
Leave's consuming stories prove their own paths. Earlier stories use their existing
service fixtures and do not depend on later UI stories. Integrated checks run when those
consumers exist and before the corresponding activation. Do not present a configuration
command as an effective access control while an old consumer still ignores it.

Failure reports identify the failing stage and safe run/operation reference. Preserve
already committed setup; use verified outcomes and current-state checks to recover under
the existing contract. Do not automatically grant broader permissions or roll back other
owners. Run mutating grant/revocation tests only with isolated fixtures; production
verification remains governed by the approved target-specific adoption runbook.

This is acceptance/runbook refinement, not another feature or implementation-readiness
pass. Exact test commands are supplied during authorized delivery. Reuse the existing
TypeScript Playwright browser suite and backend/contract checks. Scaffold impact is
proven setup/test fixtures; shared UI and agent context need no new mechanism. Existing
ADR/access/release rules remain authoritative.


Change-history scaffold direction approved — 2026-10-12: share the proven immutable
change envelope, typed bounded event schemas and transaction-aware writer through the
[owning builder pattern](../../../builder-cli/README.md#reusable-owner-local-change-history--approved-2026-10-12).
Each owner retains its local history/transaction. People employment_change is one family
history/audit record, not a second generic event duplicate. First-consuming evidence must
prove actor/scope/immutability/rollback/replay; no automatic payload capture or new runtime
service. Existing controlled command evidence and draft simplifications remain binding.
