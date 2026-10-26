# ADR-0063: Internal People Access Registration

**Status:** Accepted — user agreed; current KDG foundation reused, People-specific delivery remains  
**Date:** 2026-10-25  
**Scope:** Shared People management capability registration and admission in Access  
**Complements:** [ADR-0040](./0040-shared-employment-core-and-application-settings.md),
[ADR-0046](./0046-application-availability-and-access-scopes.md),
[ADR-0053](./0053-capability-scoped-access-in-mixed-scope-applications.md) and
[ADR-0062](./0062-people-leave-prepared-source-change-coordination.md).
Accepted predecessors remain unchanged.

## Context

E2 already requires explicit shared employment-management authority independently of
Leave approval/configuration permissions. G4 names `people.employment.manage`, but its
Access registry/admission owner must be bound. The current KDG/platform work has already implemented the reusable registry, protected
application/permission/entry registration and organization admission owner commands. Access
registry storage has one application owner per capability, independent organization
admission and an explicit entry-permission catalogue. Those foundations are existing
implementation to reuse, not new delivery in this decision. Current KDG organization
checks remain explicitly bound to kdg_capture in HTTP permission/caller policy and SQL. Registering People authority under Leave would couple shared
employment to one consumer. A launcher product or extra customer enablement step is not
required by shared-source management.

## Decision

Register `people` as an internal protected owner in Access's existing application registry.
Register `people.employment.manage` with app_id `people` and organization scope. Use actual
existing global/organization enablement and explicit current grants, not another catalog,
new capability-owner schema or a Leave permission alias. The Access registry's technical
application record need not have a customer-facing application or Directory publication.

Provision required internal People global/organization admission through controlled shared
employment onboarding/adoption before that organization uses People management. This is
part of existing shared-source setup, not an additional customer action or People app
selector. Provisioning alone grants no person authority. New organizations start with no
user grant until explicit authorized role/capability approval. Existing explicitly approved
source administrators may be adopted only through verified authority mappings with owner
review/audit, never because their role name is Leave Manager, Approver or supervisor.

People source API checks the current user, organization membership, People global/org
admission and exact management grant using its restricted Access consumer. Leave API
access/role checks remain separate and its UI may link to the authorized shared-source
surface. A person must satisfy each action's own admission/authority; a Leave grant does
not become a People grant. The same independently authorized People source operation can
be consumed by other applications without importing their server code or gaining their
private domain rights.

Do not publish People in App Directory and do not register a People launcher entry
permission for this internal management capability. Internal app registry presence or a
random admin permission is not app discovery. Directory/launcher continue their explicit
published-entry contracts. No new People application, HR suite or administration screen
is introduced by this decision.

Disabling Leave does not disable People authority or delete People grants/admission.
Disabling internal People global/org admission blocks new interactive People management
checks; its controls are restricted operational administration, not a new customer toggle.
Retain required narrow prepared/committed source recovery under ADR-0062; admission flags
cannot release gates, discard source intent or manufacture human authorization. Existing
consumer participation/activation and current fact-read contracts remain independently
required. No blanket read/worker grant follows from internal registration.

## Implementation and verification boundaries

Existing Access controlled commands/constraints own registration, enablement and grants.
Actual Access check code currently has consumer-specific policies/result variants; registry
rows alone will not activate People. Specifically services/access/organization_check.py
accepts the KDG permission set/current configured organization for its KDG branch, and
Access0015 check_organization_permission SQL requires permissions.app_id = 'kdg_capture'.
Those are real current boundaries, not a generic People check awaiting only configuration.
Source inspection found no services/people package or people.employment.manage registration/
consumer. This states current repository implementation, not an audit of deployed rows. Add the exact People credential/permission/resource
variant, current check and generated owner contract through the already planned Access/
People consumer delivery item, preserving supported KDG/PtS/Scribeswell behavior. Do not
modify historical migrations, run owner commands or seed real grants during planning.

Verify explicit authorized/denied People management, wrong caller/org/member, independent
Leave enable/disable, independent People disable, no launcher entry, no role-name grants,
controlled adoption and required retained recovery. Actual restricted-role database and
real HTTP consumer tests remain delivery requirements; this proposal executes none.

Scaffold: existing owner registration/scoped service-client/check patterns, proven with
first consumers; no new permission runtime. Shared UI: existing source-management entry
and role/capability controls; no app tile or extra enablement screen. Agent context and
shared contracts should link this decision if accepted. Exact delivery order/test artifacts
and single-agent sizing remain C6 gates. No implementation/readiness authorization.

## Reuse evidence and remaining scope

Current repository evidence: services/access/APPLICATION_REGISTER_EVIDENCE.md,
PERMISSION_REGISTER_EVIDENCE.md, ENTRY_PERMISSION_REGISTER_EVIDENCE.md,
ORGANIZATION-APPLICATION-CONFIGURE.md and ORGANIZATION_CHECK_EVIDENCE.md;
services/access/migrations/versions/0003_registry_storage.py and 0015_organization_check.py;
services/access/organization_check.py. Read their recorded qualification limits rather
than claiming fresh PASS or production People enablement. The grant compatibility bridge
and active organization check are implemented pieces; do not infer every planned shared
role/assignment consumer is complete.

Planning acceptance records the internal People registration/admission policy and reuses
those foundations. Remaining actual work is compatible People caller/check/resource support,
People management consumer, deliberate registration/admission/grant adoption and owner tests.
No duplicate registry, operator command suite, lifecycle or new standalone foundation story.
Existing predecessor tracking must credit delivered KDG/platform slices and retain only
unimplemented deltas in sizing/order. No runtime tests rerun for this documentation change.
