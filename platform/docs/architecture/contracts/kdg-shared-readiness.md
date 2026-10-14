# KDG shared-platform readiness addendum

2026-10-14. Selected engineering planning baseline for review; no implemented API,
generator, privileges or secret provisioning is claimed. The sole owner explicitly
acknowledged the KDG/Leave ownership handoff as all component owners. This addendum
refines the mutable owner contracts; accepted ADRs remain unchanged. Product scope
is the approved KDG plan, not a new shared specification or delivery workflow.

## Ownership and applicability

Identity retains ID-A/ID-B baseline, actor/membership persistence, projections and
operator binding. Access retains ACCESS-A registry/grants and ACCESS-B checks,
target verification, OpenAPI/client/negative fixtures. ENV/P1/SERVICE/WRITE retain
environment, generator, owned-write/client/error and disposable-output tests. KDG
integrates its actual consumer and proves offline helpers; builder/UI owners accept
and maintain proven neutral promotions in that consuming item. Release retains
coordinator/recovery tooling. Leave retains its own-person/People/draft consumer and
first-slice acceptance. No shared schema/client/generator/test ownership transfers.

Keep the canonical [capability-check wire](identity-access-employment-e1.md#canonical-capability-check-wire--2026-10-06),
[admission](application-admission-and-discovery.md),
[controlled commands](e1-controlled-provisioning-and-evidence.md) and
[errors/outcomes](api-errors-and-operation-recovery.md). Their earlier employee-only
examples do not constrain this account-own organization consumer. New KDG endpoints
below are private Access operations reached only through the KDG API/setup adapter.
The browser receives KDG models, never Access credentials or replayable decisions.

## Exact KDG check and registry extension

Application ID is `kdg_capture`. All nine capabilities in
[KDG's role matrix](../../../../apps/kdg-capture/docs/contracts.md#access-integration-and-roles)
have required authorization scope `organization`. The entry set is exactly
`kdg_capture.capture.read.own`. Register each literal, not a prefix wildcard.
Default Capturer has create.assigned/read.own/edit.own; Questionnaire administrator
has those three plus create.all/read.all/edit.all/questionnaire.manage/child.manage/
assignment.manage. Roles are explicit bundles, with no implicit read from edit or
future permissions. App role names never grant platform access administration.

`POST /v2/check` retains exactly `permission` and
`authorization_scope: {kind: organization, org_id: UUID}`; user bearer plus the
distinct KDG `X-Service-Key` determine caller/subject. Success contains exactly
`account_id`, `actor_id`, `permission`, `authorization_scope`, `decision_id`,
`checked_at`, `membership_id`, `resource_scope`. No `person_id`/employment/null
placeholder is required. membership_id is a positive signed-bigint decimal string;
all UUIDs are typed strings and checked_at is UTC RFC3339.

| KDG permission suffix | Exact resource_scope |
| --- | --- |
| capture.create.assigned, capture.create.all, capture.read.own, capture.edit.own | `{kind: own_account, account_id: <same verified account>}` |
| capture.read.all, capture.edit.all, questionnaire.manage, child.manage, assignment.manage | `{kind: organization, org_id: <same authorization organization>}` |

create.all means all eligible children for the caller's **own** capture, not creating
another account's observation. Access returns no child/assignment evidence. KDG
checks its own assignment, original author, child/version and write rules.
The KDG service policy allows only these nine `/v2/check` literals and the target
operations below, constrained to its configured Khula UUID. It does not need
organization discovery or Identity's People-only context endpoint. Directory's
optional later listing uses the same entry capability; it does not gate direct entry.

Access checks current account/profile, active organization/current membership,
global/org app enablement, exact membership-bound grant and durable account actor.
Missing actor after authority checks returns HTTP 409 `identity.actor_setup_required`
without creating identity. Existing common authentication/denied/unavailable errors
apply; a caller-policy denial never becomes a claim that the user's grant was revoked.
KDG verifies every echoed permission/scope/account/resource binding before use.
The closed union retains PtS account and Leave own-person variants unchanged.

## Current membership and own-record continuity

Use Identity's existing new-ID-on-rejoin design, not a new generation field. Retired
memberships remain evidence; replacement grants/assignments require explicit renewal.
Assignments and KDG prior-child eligibility bind the decimal-string membership_id.
Old grant/assignment/eligibility does not authorize a replacement membership. Suspending
and re-enabling an app retains the same membership and restores only still-valid rights.

Capture ownership remains the original account, not the historical membership. A
returning same account with newly approved current read/edit rights may read/edit its
old records; a recreated Auth account cannot claim them through name/person/email.
New creates require current membership and renewed assignment/eligibility. A pending
old-membership create remains protected but cannot sync under its old eligibility.
No new transfer, export/intake or retention policy is introduced to resolve that case.

## Trusted target discovery and verification

Add two bounded operations to ACCESS-B, not an arbitrary-target mode on `/v2/check`:

- `GET /v2/kdg-capture/assignment-targets?org_id=<UUID>&cursor=<opaque>`.
- `POST /v2/kdg-capture/assignment-targets/check` with exactly
  `{org_id, target_account_id, expected_membership_id}`.

Runtime calls require KDG service identity plus acting user bearer with current
`kdg_capture.assignment.manage` in that exact organization. The service principal
alone cannot enumerate targets. List checks active target account/profile, membership,
actor and effective create.assigned **or** create.all, plus current app admission.
Each item is exactly `{account_id, actor_id, membership_id, display_name}`; envelope
is `{targets, next_cursor, checked_at}`. display_name is plain text, at most 200
Unicode code points, never an identifier. No email/provider/person/employment/role
list. Missing required display setup is an owner fixture error, not email fallback.

Pages contain at most 100 items, ordered by account UUID; cursor is a protected opaque
position bound to caller/org/query, maximum 2048 bytes. Every page rechecks authority;
listing is not a reusable eligibility token. The point check binds the exact supplied
membership, and returns exactly `{account_id, actor_id, membership_id, org_id,
capture_permissions, decision_id, checked_at}`. capture_permissions is a nonempty
unique array of the two exact effective create capabilities, in assigned/all order.
Foreign, absent, inactive, ineligible or replaced targets return 404
`resource_not_found` without existence details; dependency failure returns 503
`authorization_unavailable`, not ineligibility. Wrong acting authority returns 403.
Malformed fields/cursor use safe 422 `validation_failed`.

Setup uses the **same point-check model/policy**, with a separate registered KDG
setup credential allowed only that route and the configured org, bound to its verified
service executor and explicit `assignment_target.verify` operator authority. No target
listing or ordinary `/v2/check` impersonation. List, point-check and setup verification use identical target account/profile/actor,
current membership, app admission and effective create-capability predicates. Point-check
also verifies expected_membership_id; setup changes only the acting principal policy,
never relaxes target predicates. Runtime credentials and a user bearer
cannot become setup authority. Access derives the setup executor from its protected
credential mapping, never target/payload actor IDs. This narrow service-principal read
grants no target rights and writes no application assignment. Owner setup CLI supplies
that credential server-side; no public provisioning endpoint is added.

Target check and local assignment commit form one bounded execution: Access call
timeout 3 seconds; KDG total deadline 10 seconds; start local execution within 1 second
of the observation or recheck; local statement timeout 5 seconds, lock wait 2 seconds.
Measure total elapsed execution and the one-second observation-to-start bound with
the KDG server's monotonic clock; Access checked_at remains evidence, not a clock to
trust for deadline arithmetic. Start the total budget on request acceptance, charge
all network waits/rechecks/lock waits to that same budget and cap every sub-timeout
by remaining time. A recheck never resets the ten-second budget. At budget exhaustion,
refuse to begin a new local write; an uncertain already-sent operation follows receipt
recovery. One new/restarted attempt always rechecks. No external call under KDG business locks.
Store exact target/membership/decision timing with the assignment's immutable evidence.
A target retirement racing that short execution may leave an old-bound assignment,
which is ineffective for subsequent creates; this is ADR-0021 ordering, not an assertion
of distributed atomicity. Domain concurrency/revision guards remain local.

## Restricted operator binding and initial setup

For owner-local CLI writes select a dedicated database login per owner/environment,
distinct from runtime/migrator, with a protected mapping keyed by the authenticated
PostgreSQL `session_user`. The mapping identifies durable executor actor, enabled
state and exact allowed command/org or platform scope. Read the original login before
any `SET ROLE`; neither `current_user`, shell username, payload actor nor an arbitrary
session setting can select an executor. Restricted operator login cannot alter that
mapping, grant privileges or assume runtime/migrator/other-owner login roles. Initial
mapping/bootstrap is a controlled release input, not a self-grant command.

Unverified human attribution is absent: automation executes as its registered service
actor; an actual human initiator appears only with independently verified invocation
evidence. Separate per-owner credentials/mappings are required even when one human
administers everything. Cross-owner verification uses restricted HTTP/owner adapters;
an operator writer does not read another owner's tables.

Initial sequence uses existing Identity account_actor.ensure and membership.join,
then Access register/enable/organization configure/explicit grant commands, then KDG
version/child/assignment commands. Current `/v2/check` proves effective user entry;
target check proves assignment input. Receipts alone prove only local completion.
Keep original operation IDs/expected state on partial recovery; no automatic cross-owner
undo. Trusted account evidence identifies the verified Auth UUID/profile; display name
or email alone cannot bind Louwnique. Exact CLI paths/target manifest/owner privileges
and clean/adopt execution rehearsal remain ENV/ID-B delivery inputs.

## Minimum existing scaffold and WRITE substrate

P1/SERVICE own a single version-1 JSON recipe at the consuming app's
`scaffold.json`; schema authority is `platform/builder-cli/schema/scaffold-v1.json`.
These are planned paths, not installed files. Minimum closed input keys are
`schema_version`, `owner_id`, `owner_kind`, `sources`, `contracts`, `patterns`,
`extensions`, `deployment_manifest`. owner_kind is application/service. Values refer
to repository-owned sources and explicit proven pattern IDs, not table/API schemas
or live grants. Reject unknown/unsupported declarations, unsafe/traversing paths and
unproven patterns. Extension paths are app-owned and cannot overlap generated paths;
regeneration refuses to overwrite an undeclared modified generated artifact.

First output is React/Vite/shadcn application plus FastAPI owner/API/migration/client/
test skeleton, or service-only variant. KDG fixed-org account-own and Leave selected-org
own-person are explicit opt-ins; no mandatory selector, draft engine or People/Content/
worker dependency. A pattern is registered only with its proven owner contract/test
reference. Offline patterns enter through their KDG first-consuming stories, not before
proof. No recipe contains copies of questionnaire/DB/OpenAPI definitions.

Frontend uses approved npm workspaces/root package-lock ownership, independent
publication. Owner Python packages use independent pyproject.toml/uv.lock/dev groups;
Access stops installing PtS's requirements in its affected item. Disposable output
receives declared shared sources and its installation root, without hidden root tools.

The [ENV/P1/SERVICE contract](scaffold-environment-and-generation.md) now selects
exact generation/environment command/input/extension boundaries and references the
[newest-stable direct pins](scaffold-dependency-baseline-2026-10-14.md). Current PtS
locks do not constrain that selection; affected compatibility is later delivery proof.

Planned builder commands from repo root: `npm run generate --workspace platform/builder-cli
-- --config <recipe> --output <disposable-root>` and `npm run test:generation --workspace
platform/builder-cli`. ENV supplies a guarded bootstrap/stop/reset command and explicit
synthetic target manifest. Generated web exposes type-check/build/test:unit/test:browser/
test:auth-integration; each Python owner exposes locked unit/contract suites. These
command targets require implementation/verification and must not silently pass absent
suites. Exact direct pins, generation options, bootstrap invocation and selected disposable
callback/device topology are now recorded. Full transitive/container identity and actual
provider/device qualification are delivery evidence; no floating “latest” is used.

WRITE fixes restricted runtime tenant/actor context, owner-local structural constraints,
safe framework errors and atomic outcome/revision/evidence. Access/user checks precede
short business locks. KDG's existing [command/receipt/eligibility contracts](../../../../apps/kdg-capture/docs/contracts.md#kdg-request-and-recovery-contract--engineering-closure)
remain domain authority, not copied into the generator. Compare operation fingerprint
before executing effects; rollback business/evidence/receipt together on failure;
actual roles enforce same-org and owner isolation. Promote only the neutral mechanism.
No outbox/worker/content requirement is added to KDG's first slice.

## Evidence and remaining gates

ACCESS fixtures must cover every registered own/all variant, missing person with valid
account actor, mismatched resource/account/org, stale JWT after revoke, app suspend/
re-enable, retired/replaced membership, setup-vs-runtime caller denial, target replacement,
spoofed actor, cross-org target and unavailable verification. Retain PtS account/Leave
person/mixed-scope tests. ID-B proves session_user binding and real restricted privileges.
KDG A01/A02/A14–16 consume these; A09 consumes WRITE and the
[KDG fingerprint disposition](operation-fingerprint-security-evolution.md#kdg-initial-fingerprint-disposition--2026-10-14).

Planning closure does not establish runtime prerequisites. ENV exact compatibility/
bootstrap/callback evidence, generator implementation, owner DDL/adoption/privilege
inventories and installed-client/device proof remain distinct. The KDG
[minimum owner work packet](../../../../apps/kdg-capture/docs/shared-prerequisites.md)
records timing and acceptance without duplicating shared stories. Review this selected
baseline before code; no claim that Leave planning or KDG readiness has passed.


Identity/Access execution checkpoint, 2026-10-14: the
[owning substrate](identity-access-execution-substrate.md) now selects physical
constraints/role matrix/private projections and operator command/invocation models.
Target metadata/actual DDL/ACL/adoption/release rehearsal remain execution evidence.
Earlier unspecified-schema/privilege passages are superseded for the bounded KDG
foundation; wider Leave/People work is not marked complete. WRITE owns the remaining
outcome/evidence table and fingerprint secret execution contract.


Final WRITE checkpoint, 2026-10-14: the
[owned write/secret contract](owned-write-and-secret-execution.md) closes the formerly
open outcome/evidence/role/recovery and KDG secret-file/library planning choices.
Planning selections are complete for ordered shared foundations/KDG consumption;
actual owner/consumer test, target adoption, provider/device, release/restore and
pre-pilot policy evidence remain mandatory delivery gates. No code is authorized.
