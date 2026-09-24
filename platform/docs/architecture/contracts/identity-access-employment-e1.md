# E1 shared identity, access and employment contract discussion

**Status:** Platform direction accepted under ADR-0042; detailed wire contract and readiness pending  
**Date:** 2026-09-23  
**Owners:** Platform identity/people owner and Leave lead

This is the owning design discussion for the minimum shared capabilities consumed
by Leave's first draft slice. It implements the direction of accepted
[ADR-0039](../decisions/0039-organization-neutral-tenancy.md),
[ADR-0040](../decisions/0040-shared-employment-core-and-application-settings.md) and
[ADR-0041](../decisions/0041-shared-supervisor-department-and-location.md).
New choices below remain proposals. Accepted ADRs and the Leave requirements remain
authoritative; this document does not add an HR product or authorize implementation.

## Repository evidence

- The existing [identity migration](../../../supabase/migrations/20250815110000_platform_create_identity_schema.sql)
  has `identity.org` with UUID identifiers and `identity.users` tied to `auth.users`.
  It does not yet distinguish an account-independent person from a login profile.
- The [membership migration](../../../supabase/migrations/20250815210000_platform_multitenancy_orgs.sql)
  has `identity.org_member` with bigint identifiers, unique organization/user
  membership and per-membership roles. Its authorization helper reads JWT role
  claims; it is not the current-membership/current-permission HTTP contract required
  by [ADR-0019](../decisions/0019-current-server-side-authorization.md).
- Inspection of `services/` found app-directory, not implemented identity/access
  or shared employment services. Service paths below are proposed additions.
- These are working-tree observations, not verification of a deployed database.

## Proposed ownership and identifiers

| Concern | Proposed owner and contract |
| --- | --- |
| Login | Supabase Auth with Entra, as already accepted. An authenticated account establishes identity, not organization access or employment. |
| Person and account link | Identity owner; stable account-independent `person_id`, with an explicit verified link to the existing account/profile. Backfill without changing existing account IDs. Do not merge people merely because email addresses match. |
| Organization, membership and application grants | `services/identity-access`, adopting existing `identity` records and preserving organization/membership identifiers. Expose membership IDs as opaque decimal strings on JSON boundaries to avoid JavaScript integer precision loss. Leave must not infer type, order or authority from any ID. |
| Employment and optional shared assignments | `services/people`, owning a `people` schema and stable `employment_id`, separate from person, account and membership IDs. Own dates/status and the optional department/location/supervisor references already approved in ADR-0041. |
| Leave settings and draft ownership | Leave references `org_id` and `employment_id`; records actor attribution separately. It does not read or write shared tables directly or create an editable copy of shared facts. |

The two runtime owners may share a deployment initially; their HTTP contracts,
restricted database authority and migration ownership remain distinct. Separate
containers are not required by this proposal. No shared server imports are introduced.

The user agreed on 2026-09-23 to one enduring employment relationship per person and organization, with
separate effective-dated employment periods for leaving and rejoining. Preserve
period identity and historical dates rather than overwriting a former period or
creating a new person. This makes one employee draft per organization unambiguous.
Concurrent independent employment relationships in the same organization are outside
this agreed model; concrete period constraints and draft keys remain design work. Existing
Leave historical calculation rules still determine how periods affect entitlement.

Allow a shared person/employment record without a login account under ADR-0042. Such a
record grants no application access. E1 uses linked, authorized employee fixtures;
accountless record administration and verified account linking belong to E2. An
organization administrator or service actor need not have an employment record.
Service attribution must use the identity owner's actor contract rather than a fake
employee; concrete person/service actor mapping remains part of the wire design.

### Platform applicability and accountless-person discussion

Identity/access, organization scope and actor attribution are platform-wide patterns.
Shared employment is the platform-wide pattern for applications that need employment;
it is not mandatory for every application or every authenticated user. Proposed service
names and deployment placement above remain choices, not universal requirements.

Accepted under [ADR-0042](../decisions/0042-person-account-employment-and-legacy-adoption.md): support accountless people in the shared data
model from the start. This allows pre-onboarding records and historical employment
imports without manufacturing login accounts. E1 still tests a linked signed-in
employee; it does not need an accountless administration screen. Creating a person,
recording employment, linking a verified login and granting membership/application
access remain separate authorized operations. Never auto-link by matching email or
let a client claim an existing employee ID. No proxy employee acknowledgement is
implied; Leave actions requiring the employee's own response still require that
employee's authenticated participation.

Receipt/expense consolidation and existing-code review are tracked in the
[platform review and integration plan](../reviews/identity-expense-consolidation-2026-09-23.md).

## Minimum E1 read and authorization behavior

These are contract operations, not approved endpoint paths or payload schemas:

1. Resolve the verified caller and list organizations they can currently access for
   Leave. The browser uses Leave's API for business data; organization selection is
   request context, never an authorization grant. No employee-directory enumeration
   is needed for E1.
2. On every protected request, check the selected organization, current membership
   and required explicit Leave capability through Identity/Access. Return the
   authoritative actor/person/membership/organization references, applicable grant
   scopes and decision reference/time. Never trust caller-supplied person or employee
   IDs as proof of ownership. A permission response does not replace Leave's local
   resource rules. No positive grants cached across requests.
3. Read the caller's employment relationship in that organization through People,
   authorized for this caller and consumer. Return stable identity plus the version
   and effective employment period/status/dates needed by the agreed draft rules.
   Include only necessary fields; E1 does not need optional assignment lookups or
   a full person profile. Employment is not a substitute for membership/permission.
4. Leave validates local draft ownership and lifecycle before reading or mutating it.
   Access to recorded operation outcomes also requires current authorization.
   External checks happen outside local business locks. An employment read is not
   an atomic guarantee against a concurrent remote change; define E1 draft eligibility
   and its freshness boundary before declaring the consuming mutation ready.

For explicit capability names, propose `leave.request.own.read` for own draft reads
and `leave.request.own.manage` for create/edit/discard, within the existing own-request
family. These are business capabilities, not grants per button. They do not grant
on-behalf actions, approval, balances or documents. The concrete catalog must map
all later own-request actions explicitly; no wildcard grants or automatic custom-role
expansion. Default Employee role grants and legacy role compatibility remain part of
the access contract, not assumptions about an `employee` role name in a JWT.

## Failure and acceptance boundaries

| Condition | Required result and planned evidence |
| --- | --- |
| Invalid/expired authentication | Safe sign-in recovery; subsequent actions require renewed authentication and access checks. Browser/API tests cover same-user return and account changes. |
| Missing/suspended/ended membership or missing grant | Deny the next authorization check without waiting for token expiry. API tests revoke access with a still-valid token. |
| Access or required employment lookup unavailable | Retryable unavailable result, not permission denial, missing employee, or null assignment. No fallback to stale positive authority. Preserve recoverable unsaved work within the agreed UX limits. |
| Authorized caller has no employment | Distinct setup-needed state for employee draft actions; no automatic employee creation. This does not deny otherwise authorized nonemployee administration. |
| Multiple organizations | Resolve independent memberships/employment references; cross-organization draft access fails. Include a for-profit organization fixture. |
| Revocation after authorization | Apply ADR-0021's bounded already-executing-operation rule; no claim of distributed cancellation. Test ordering and newly queued/restarted execution separately. |
| Null department/location/supervisor | Valid shared employee state; no draft block. E2/E5 add assignment and route tests when those capabilities are introduced. |
| Rehire/account linking | Keep historical references and periods intact; verified linking changes no grants by itself. Characterize existing identity behavior before migration. |

## Remaining contract work and delivery impacts

Before first affected story readiness, settle payloads/endpoints/versioning, exact
grant scopes and catalog, person/service actor migration, membership lifecycle and
role compatibility, employment-period boundary semantics, draft eligibility before
start/after termination, authenticated service-to-service caller propagation, allowed
references, safe error mapping, request/execution timeouts and authorization audit
fields. Prove compatible migration/recovery under ADR-0020. No new foreign key from
Leave into another owner's tables is implied by the logical references above.

E2 adds shared administration, optional scoped lookup/null/history/retirement and
mutation contracts. Later consequential Leave actions need the stronger shared-input
freshness/change-impact design required by ADR-0040; E1 does not settle it implicitly.

- Scaffold: typed HTTP clients, caller propagation, current-access dependency,
  error mapping and generated-sample tests accompany the first proven implementation.
- Shared UI: authorized organization selection, safe unavailable/denied states and
  session return; shared employee selectors remain E2.
- Agent context: existing ownership and organization instructions suffice for this
  proposal; reassess when service paths and contracts are accepted.
- Documentation: this owning contract is linked from Leave's tracker and epic map.
- ADR: no accepted record changed. Any conflict discovered during contract design
  requires a linked new decision; proposed names/placement are not accepted policy.
- Verification: documentation inspection only; no runtime, schema or test code added.
