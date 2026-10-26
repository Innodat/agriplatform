# E1 shared identity, access and employment contract discussion

KDG execution closure, 2026-10-14: [Identity/Access substrate](identity-access-execution-substrate.md)
selects KDG-relevant physical actor/member/registry/grant constraints, current/target
projections, restricted role/command schema and owner CLI/adoption matrix. These refine
earlier unspecified DDL/privilege/command passages below; no objects or grants are applied.
Existing PtS/Leave scope and source-owned migration history remain. Actual target baseline/
rehearsal is later delivery evidence, not presumed equivalence.

KDG refinement, 2026-10-14: the acknowledged sole owner permits coordinated planning.
[KDG shared readiness](kdg-shared-readiness.md) adds exact organization own-account/
all-org check variants with stable actor/current membership and no person/employment
requirement. ID-A/ID-B retain schema, lifecycle/projection/operator ownership; existing
PtS account and Leave own-person designs remain. No runtime adoption is claimed.

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

## Expense scope correction — 2026-10-01

[ADR-0045](../decisions/0045-expense-preproduction-history-scope.md) removes historical
Expense receipt/purchase migration and old receipt-client compatibility from this
adoption path. Earlier consolidation recommendations are qualified accordingly.
Retain shared identity adoption and compatibility for existing PtS/Access/Content
consumers; do not infer that their data or interfaces are disposable.

## Repository evidence

- The existing [identity migration](../../../supabase/migrations/20250815110000_platform_create_identity_schema.sql)
  has `identity.org` with UUID identifiers and `identity.users` tied to `auth.users`.
  It does not yet distinguish an account-independent person from a login profile.
- The [membership migration](../../../supabase/migrations/20250815210000_platform_multitenancy_orgs.sql)
  has `identity.org_member` with bigint identifiers, unique organization/user
  membership and per-membership roles. Its authorization helper reads JWT role
  claims; it is not the current-membership/current-permission HTTP contract required
  by [ADR-0019](../decisions/0019-current-server-side-authorization.md).
- At the original September inspection, shared access/employment services were absent.
  Refresh on 2026-10-01 found `services/access` and `services/content-service`; no
  People service was found. Adopt the existing Access owner rather than creating a
  parallel `services/identity-access` implementation.
- These are working-tree observations, not verification of a deployed database.

## Proposed ownership and identifiers

| Concern | Proposed owner and contract |
| --- | --- |
| Login | Supabase Auth with Entra, as already accepted. An authenticated account establishes identity, not organization access or employment. |
| Person and account link | Identity owner; stable account-independent `person_id`, with an explicit verified link to the existing account/profile. Backfill without changing existing account IDs. Do not merge people merely because email addresses match. |
| Organization, membership and application grants | `services/access`, extending the existing owner and adopting existing `identity` records and preserving organization/membership identifiers. Expose membership IDs as opaque decimal strings on JSON boundaries to avoid JavaScript integer precision loss. Leave must not infer type, order or authority from any ID. |
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


## Technical consolidation — 2026-10-01

Current working-tree evidence supersedes the earlier service-absence observation:
[Access implementation](../../../../services/access/main.py) has `POST /v1/check`,
current identity organization/membership checks and `access.grants`. Its permission
allowlist and migration constraint currently cover three PtS permissions only. It
returns `org_id` and account-based `actor_id`, not the person/membership/employment
contract Leave needs. Caller credentials currently recognize PtS and Content.
[PtS service tests](../../../../apps/pts/tests/test_services.py) include actual-database
membership/grant tests with injected authentication; their existence is not a fresh
run or proof of Leave compatibility. The legacy SQL identity review remains useful
historical evidence, not a statement that this Access implementation is absent.

Select the following as the working technical design for E1, subject to contract
verification and existing readiness gates:

- Keep `/v1/check` and existing PtS/Content behavior supported. Introduce versioned
  `/v2/check` for the new explicit person/membership/grant-scope/error contract,
  including a decision identifier and authorization timestamp. Do not change v1
  semantics by merely replacing its response model.
- Add `/v2/organizations?application=leave` as an authenticated caller-scoped listing,
  returning only currently authorized organizations and their membership references.
  Leave's API proxies the necessary business information; the browser does not call
  the private service directly. Scope listing is separate from authority for an action.
- Authenticate the Leave caller with its own restricted service credential and verify
  the end-user bearer token; authorize the service's allowed application/permission
  namespace as well as the user's current grants. Never reuse a PtS or universal key.
  Propagate no unsigned actor headers as authority. Deployment must preserve private
  service reachability and redact credentials from traces/logs.
- Extend the Access owner's permission catalog and migrations for exact
  `leave.request.own.read` and `leave.request.own.manage` capabilities; no wildcard
  grant. Preserve PtS's explicit grants. Custom roles/default-role upgrade semantics
  remain an Access-owned E2 contract, with an explicit compatible E1 bridge rather
  than duplicate grant authorities.
- People supplies `/v1/organizations/{org_id}/employment/me` through an independently
  authorized service call, deriving person identity from the verified caller. Return
  `employment_id`, `person_id`, `org_id`, integer `revision`, effective `as_of_date`,
  applicable period dates/status and response observation time. No arbitrary
  employment-ID argument is needed for own-draft E1. No employment yields a distinct
  authorized setup-needed result; dependency failure is never an empty employee.
- Account-based existing actor IDs remain mapped until the person/service actor
  migration is defined. Do not reinterpret a current `actor_id` as a person ID or
  silently change historical attribution. Serializing existing bigint membership IDs
  as decimal strings remains the new-contract boundary; legacy payloads are unchanged.

The deployment repository now includes operational preparation and shared service
migrations. Read [deployment status](../../../deployment/PRODUCTION_STATUS.md) and
[the runbook](../../../deployment/README.md) before selecting actual targets. The status
file is dated 29 September and is not a live check. ADR-0043 remains Proposed in the
index; do not infer its acceptance or Leave activation from the implementation package.
No production connection, deployment or migration was performed in this pass.

Still blocking identity readiness: verified person/account/service actor mapping,
identity migration ownership/baseline with existing consumers, account-link rules,
exact v2 schemas and role bridge, employment effective-date timezone, and freshness
of employment input through a Leave draft commit. A bounded read-before-write alone
is not a distributed atomicity guarantee. Later E2 shared changes/E5 submissions
require their own change-impact/confirmation consistency proof.

## Person, actor and employment read baseline — 2026-10-01

Select the following implementation design for validation. These structures are not
implemented by this document and do not rename or rewrite existing production data.
The scope is the minimum E1 consumer; E2 administration still needs its write contracts.

### Person/account/actor distinction

- Introduce an Identity-owned `person` with a stable UUID independent of Auth. Use an
  explicit `account_person` link keyed by the existing Auth account UUID; one active
  person link per account. The schema may represent multiple verified accounts linked
  to one person, but E1 does not add account-management or account-merging UI. Grants
  remain account/membership-specific and never combine implicitly across accounts.
- Introduce an Identity-owned actor registry for people and services. Preserve existing
  account UUIDs as legacy human actor IDs, linked to the new person identity, while
  new service actors receive their own stable IDs. Retain actor records after account
  deactivation/removal so attribution survives. Do not conflate the actor ID with
  employment ID or assume it equals the new person ID. Any existing service/system
  profile must be explicitly classified before migration, not backfilled as a person.
- Backfill through an explicit account-to-person/actor mapping manifest. Preserve
  existing account, organization and membership IDs and existing business actor
  references. Confirm duplicate-person cases individually rather than auto-merging
  by email; unresolved mapping blocks that account's v2 employee actions with a safe
  setup-needed outcome while legacy consumers retain their supported contract.
- Verified link creation records its authorized actor, evidence reference and timestamp.
  Changing/removing a link is not self-profile editing. Preserve link history, prevent
  a client from claiming an employee, and recheck the link on each v2 operation.
- New E1 writes use server-resolved actor UUIDs and separately record the initiating
  human where a service truly executes on their behalf. The calling Leave service's
  credential is not evidence that it may impersonate an arbitrary person. E1 has no
  background user-command execution; later workers need their own restricted identity.

The Access owner adopts new identity objects through a separate identity-owned
migration history/baseline, coordinated with its existing `access` history. Do not
expand the current Access Alembic schema filter to take over legacy objects without
an explicit inspected baseline and cutover. Existing SQL and bootstrap owners must
stop managing the adopted objects at the verified transition point. Foreign keys
already used by consumers stay compatible until deliberately migrated.

### v2 authorization response and grant bridge

`POST /v2/check` accepts `org_id` and one explicit `permission` plus the verified
end-user bearer token and caller-specific service credential. The authorized success
payload contains:

| Field | Contract |
| --- | --- |
| `org_id` | Requested and currently authorized UUID, checked by consumers. |
| `account_id` | Verified Auth account UUID. |
| `person_id` | Mapped person UUID, not derived from an email or request body. |
| `actor_id` | Durable verified actor UUID for attribution. |
| `membership_id` | Existing membership ID serialized as a decimal string. |
| `permission` | Exact checked capability; the consumer verifies it matches the request. |
| `scope` | For E1 own-request capabilities: `{kind: own, person_id: ...}`; no wildcard resource scope. |
| `decision_id` | UUID identifying this authorization observation for audit/correlation. |
| `checked_at` | Server UTC timestamp; evidence of the check, not a reusable authorization token. |

The response is private, `Cache-Control: no-store`, and cannot be replayed as authority
on a subsequent request. It contains no email, employee note or department/location.
Use the shared safe error envelope and versioned compatibility plan. Current profile,
organization, membership and grant state must all allow the action. Missing person
mapping is distinct from access denial and dependency outage after authentication and
service scope have been verified.

For E1 provisioning fixtures, use the existing Access-owned explicit grant mechanism,
expanded by reviewed migration to admit the two Leave capabilities. Grant both own-read
and own-manage deliberately for the E1 Employee fixture; neither is inferred from the
legacy `employee` enum or employment status. `/v2/organizations?application=leave`
returns only organizations having relevant effective Leave grants, with current
membership. It is not proof of permission for a later draft request.

E2 role administration must converge on one Access-owned effective-grant evaluation:
custom/default role grants and retained direct grants combine with their scopes and
provenance. No separate Leave grant authority. Migration may materialize effective
grants only with a verified current-state update/invalidation contract; stale projections
cannot extend revoked authority. Role lifecycle and production provisioning remain
E2 work, not an E1 invitation/administration interface.

### Effective employment dates and draft freshness

People stores date-only employment periods, inclusive start/end dates, with a nullable
open end. Enforce same-relationship nonoverlap and end >= start; preserve period IDs
and history across correction/rehire. There is one enduring `(org_id, person_id)`
employment relationship. Its revision advances for changes affecting its read contract.

For Leave, derive the effective business date from the server clock in the employee's
Leave work timezone under Leave ADR-0023/0094. Do not use the browser timezone or move
work-profile ownership into People. Where dated interpretation is needed, fixtures supply the minimum Leave timezone
configuration. Under Leave ADR-0122, absent/invalid timezone produces a nonblocking
draft notice and undated discovery; it never implies a UTC fallback or blocks safe
preservation by itself.

Read the shared relationship first, then obtain the authorized Leave timezone/settings
revision and request People period interpretation with `as_of_date=YYYY-MM-DD` derived
by Leave. The HTTP caller supplies a business date, not authority; People independently
verifies caller/user/scope and returns the date used with its relationship revision.
If initial identity discovery and effective read resolve different employee/person
identities, abort and refresh; do not compose two people's records. Resolve this bounded
sequence within the existing total request budget; no remote request occurs while a
Leave business row is locked. A direct effective-date read may replace two calls once
an authorized stable reference is already available and verified.

Return the matching current period if any, otherwise the next future period if any,
otherwise an ended relationship. A gap before a known rehire period counts as future
employment for the already-approved draft-preparation rule, provided current Leave
access has been granted. This does not restore permissions automatically or authorize
submission for dates in the employment gap.

Accepted under [platform ADR-0044](../decisions/0044-bounded-shared-input-observations-for-draft-saves.md):
a draft-only mutation that has checked current
access and employment may complete within its 10-second execution budget using that
observed employment revision, even if a remote employment edit occurs during execution.
Record the observation revision/date/time and authorization decision reference with
its committed evidence. The next operation rechecks and sees ended-employment read-only
or revoked access. A queued/delayed/restarted attempt must obtain fresh observations.
For the dated path actually relying on employment interpretation, check local
work-timezone/settings revision and effective date under the local transaction guard; if either changed since the remote read, abort before mutation and
repeat preparation outside locks. Never silently carry a stale date across local midnight.

The user approved this bounded draft-save race policy on 2026-10-01. It is not
proof of distributed atomicity or an extension of draft authority to submission,
approval, reservation, entitlement calculation or shared employment edits. Their
stronger input-change/confirmation coordination remains binding before E2/E3/E5
writers become ready. E1 membership revocation already follows platform ADR-0021.

Before readiness, verify actor mapping and v1/v2 compatibility on disposable copies,
current-link/grant changes, inclusive dates/timezones, future rehire gaps, local midnight,
local settings revision races, remote employment changes during a save and the total
request deadline. Preserve log minimization; observation evidence contains references
and versions, never full profile or draft payloads.

## E1 employment read wire proposal — 2026-10-01

This narrows the existing shared read design for discussion; it does not authorize
implementation or complete identity migration/readiness. The user approved the
setup-needed handling of a relationship with no periods on 2026-10-01: preserve
existing drafts and authorized reading, but block creation/editing until corrected.

### Discovery and effective read

Use `GET /v1/organizations/{org_id}/employment/me` for both reads. Without
`as_of_date`, return discovery only; with `as_of_date=YYYY-MM-DD`, return the effective
interpretation. Never silently substitute today's UTC date when the parameter is
absent. The server derives the person from verified identity and checks the consuming
service and current user's authority, as already required above. No caller-supplied
person ID or arbitrary employee lookup is introduced.

Every successful response is HTTP 200, private and `Cache-Control: no-store`.
Responses are discriminated by `status`; every field listed for a variant is required
unless explicitly nullable. Reject malformed dates/unknown query parameters with the
safe validation envelope. UUIDs are strings, dates are real Gregorian ISO date-only
values, and timestamps are UTC RFC 3339 strings. Serialize relationship `revision`
as a positive bigint decimal string, consistent with Leave revisions; this refines
the earlier shorthand “integer revision” and avoids JavaScript precision loss.

| Variant | Fields in addition to `status` |
| --- | --- |
| `not_found` | `org_id`, `person_id`, `observed_at`; no employment ID or inferred employment status. This means an authorized lookup found no relationship. |
| `found` (discovery only) | `org_id`, `person_id`, `employment_id`, `revision`, `observed_at`, `has_periods` (boolean); no effective status or period dates. |
| `effective` (dated read) | `org_id`, `person_id`, `employment_id`, `revision`, `observed_at`, `as_of_date`, `employment_state`, `period`. |

For `effective`, `employment_state` is exactly one of:

- `current`: `period` is the period containing `as_of_date`, with inclusive endpoints.
- `future`: `period` is the earliest later period, including a gap before known rehire.
- `ended`: `period` is the most recent ended period; there is no current/future period.
- `setup_required`: `period` is null because the relationship has no periods.

A non-null `period` contains only `period_id` (UUID), `start_date` (date) and
`end_date` (nullable date). The shared read interprets employment dates; Leave decides
what each state permits. It must not return `can_submit` or embed Leave policy.
No periods is incomplete setup, not evidence that someone has left employment.
If inconsistent/overlapping data prevents a unique answer, fail safely; never choose
an arbitrary row or report absence. Optional department/location/supervisor assignments
remain shared facts, but are omitted from this minimum response. Null assignments do
not produce `setup_required`.

For discovery followed by effective read, Leave compares organization, person and
employment IDs with the verified authorization observation. Revisions may advance
between calls; the effective response supplies the observation used under ADR-0044.
A changed identity or vanished relationship aborts preparation before any draft write.
The response's observation time is evidence, not a cache lifetime or reusable grant.

### Errors and consuming presentation

Use the [shared error envelope](api-errors-and-operation-recovery.md), with safe typed
details only. Check authentication and caller/organization authority before disclosing
whether an account link or employment relationship exists.

| Condition | HTTP / `error_id` | Leave handling |
| --- | --- | --- |
| Invalid/expired end-user authentication | 401 / `authentication_required` | Existing session recovery. |
| Valid identity/caller without required authority | 403 / `access_denied` | Access-denied presentation; no employment details. |
| Authorized account lacks required person mapping | 409 / `identity.person_link_required` | Setup-needed presentation, no automatic linking. |
| Invalid query/date | 422 / `validation_failed` | Safe field identifier; no raw input echoed. |
| Current authorization cannot be checked | 503 / `authorization_unavailable` | Retryable service problem; never report “no employee”. |
| Required employment storage/dependency unavailable | 503 / `dependency_unavailable` | Retryable service problem; no stale data fallback. |
| Inconsistent stored periods or unexpected failure | 500 / `internal_error` | Safe support reference, no inferred employment status. |

Authorized `not_found` and `effective/setup_required` produce a Leave setup-needed
state, with no automatic employment creation or fresh draft mutation. Existing draft
reading remains governed by current own-read authority and ownership; incomplete
employment setup must not be treated as deletion of a saved draft. `ended` preserves
the previously agreed read-only behavior. `current`/`future` permit draft preparation
with current own-manage authority and required ownership/setup. Valid timezone is
required for dated interpretation, not for otherwise authorized input preservation
under platform ADR-0049 / Leave ADR-0122.

### Minimum structural and fixture contract

People owns relationship uniqueness `(org_id, person_id)` and a stable employment UUID.
Periods have stable UUIDs, a same-owner composite organization/relationship FK, non-null
start, nullable end, `end >= start`, and database-enforced inclusive nonoverlap within
one relationship. Adjacent periods may start the day after the previous period ends;
sharing an endpoint is an overlap. An open-ended period precludes a later period until
its end is corrected. Preserve attribution/history under ADR-0025. Period changes and
relationship revision advancement are atomic. Concrete migration/constraint definitions
and authorized correction semantics still require design; no cross-owner database FK.

Disposable E1 fixtures must include linked/authorized current and future employees,
ended employment, a rehire gap, absent relationship, relationship without periods,
accountless employment, null optional assignments, two organizations (one for-profit),
revoked membership/grant and unavailable dependencies. Provision through owner-controlled
test setup with explicit manifest IDs and grants; never production data or a public
runtime setup endpoint. Missing mapping/period setup is intentional only in negative
fixtures. Include inclusive boundary dates, open-end/overlap rejection, exact large
revision serialization, caller/organization isolation and changed identity between reads.

Traceability: ADR-0040/0041/0042/0044; Leave work-timezone and employment-date ADRs
0023/0094; E1-AC-13/14/15/17 in the Leave acceptance map. Scaffold impact: typed People
client and safe variant/error mapping with disposable consumer fixtures. Shared UI:
reuse setup-needed/unavailable presentation, no employee-directory UI. Agent context:
existing ownership guidance suffices. ADR: no accepted policy changed; this remains a
wire proposal. Documentation only; no runtime or migration verification claimed.

## E1 Access wire proposal — 2026-10-01

This completes the proposed wire shapes for the existing v2 direction. Schema/baseline
adoption and executable compatibility evidence remain separate readiness work. No
change to `/v1/check`, existing consumers or accepted authorization ADRs is authorized
by merely specifying these new endpoints.

### Check one capability

`POST /v2/check` has exactly two required JSON fields: `org_id` (UUID string) and
`permission` (explicit registered capability string). Reject unknown body fields,
malformed JSON and duplicate JSON keys with the safe validation envelope. The E1
Leave caller is restricted to `leave.request.own.read` and
`leave.request.own.manage`; arbitrary registered permissions of other apps are not
available through its credential. Preserve end-user `Authorization: Bearer ...`
and a distinct caller credential in `X-Service-Key`, matching the existing transport
convention but with a Leave-specific credential and allowed namespace. Both are
redacted. A user token alone cannot call the private service as Leave.

HTTP 200 contains exactly the required fields in the earlier v2 authorization table:
`org_id`, `account_id`, `person_id`, `actor_id`, `membership_id`, `permission`,
`scope`, `decision_id`, `checked_at`. UUIDs use string representation;
`membership_id` is a positive decimal bigint string and `checked_at` is a UTC
RFC 3339 timestamp. `scope` is `{ "kind": "own", "person_id": "<UUID>" }`, with
the same person as the top-level field. These are typed schemas to declare in the
owning OpenAPI models, not free-form dictionaries. Clients verify requested
organization/permission and consistent person scope before using a decision.

All conditions must be satisfied before returning success: current account/profile,
organization, membership, explicit capability, verified person link and actor mapping.
No implicit manage-to-read permission expansion is introduced. The E1 fixture grants
both deliberately. A valid grant without person/actor setup does not cause automatic
identity creation. Service actors without people need their own later contract;
this own-employee endpoint must not manufacture a person for them.

### List organizations for selection

`GET /v2/organizations?application=leave` returns the caller's organizations with
current membership and at least one effective registered Leave capability. For E1,
the registered Leave catalog contains the two own-request capabilities above. Expand
the registry deliberately with E2; an administrator need not become an employee to
see an organization for which they have an application capability.

The response shape is `{ "organizations": [...], "next_cursor": null | "..." }`.
Each item contains exactly `org_id` (UUID), `name` (display string) and
`membership_id` (decimal string). Names are display values, never identifiers or
markup. No employee, grant list, role claims or organization-type classification is
required for selection. Missing person/employment setup does not hide an otherwise
authorized organization; explain setup only when the protected employee journey
needs it. The listing does not create employment, membership or grants.

Bound pages to 100 organizations, ordered by organization UUID with an optional
opaque `cursor` for the next page. The cursor represents position only, carries no
credentials and never grants access. Validate its format and recheck current caller
authority on every page; do not promise a transactionally frozen list across pages.
The selector loads further pages when necessary and must not present a truncated
first page as the full set. No cross-request positive authorization cache.

An authorized listing with no results returns HTTP 200 with an empty list and null
cursor. Leave presents “no Leave access” with administrator guidance, not “no employee”.
A dependency failure is an error, never an empty success. Listing and subsequent
selection can race a revocation: the selected organization's protected request must
check current access again. Existing session-return and safe organization-switch
rules still apply; the listing itself does not trigger a draft start.

### Shared error and compatibility fixtures

Both endpoints use private/no-store responses and the shared safe error envelope.
The new v2 transport keeps these outcomes distinct:

| Condition | HTTP / `error_id` |
| --- | --- |
| Missing/invalid calling-service credential or disallowed consumer namespace | 403 / `service_access_denied` |
| Missing/invalid/expired end-user token | 401 / `authentication_required` |
| Valid authenticated caller lacking current required access | 403 / `access_denied` |
| Valid authorized employee operation with no verified person link | 409 / `identity.person_link_required` |
| Person link exists but durable actor mapping is incomplete | 409 / `identity.actor_setup_required` |
| Malformed body/query/cursor or unsupported application selector | 422 / `validation_failed` |
| Authentication provider or current grant/membership source unavailable | 503 / `authorization_unavailable` |
| Unexpected failure | 500 / `internal_error` |

Setup identifiers are emitted only after checking caller and relevant current access.
At the Leave boundary, `service_access_denied` is mapped to HTTP 503
`dependency_unavailable` with safe retry/support presentation; it is an integration
failure, not a claim that the employee lost permission. Keep this origin distinction
in the typed server adapter without exposing credential details to the browser.
Existing v1 `detail.code` responses retain their supported semantics.

E1-AC-01/12/13/15/17 fixtures include an empty authorized listing, inaccessible
organizations omitted, multiple pages, revoke-between-list-and-action, missing mapping
versus missing grant, a valid user token with an invalid service credential, a Leave
credential requesting PtS authority, provider outage, bigint serialization and both
legacy response families. Exercise actual current-state checks under restricted roles;
mocked success alone does not prove isolation or revocation behavior.

Scaffold: typed v2 client and server-side safe adapters, with existing v1 consumer
characterization. Shared UI: authorized organization selector and established
setup/denied/unavailable states. Agent context: no new rule required. Documentation:
owning contract and E1 mapping. ADR: existing 0019/0021/0031/0032/0039/0042 apply;
none amended. No endpoint, migration, UI or test implementation is claimed.

## Identity adoption and small-cohort transition — 2026-10-01

The user approved the proposed organization-selection behavior, then clarified that
PtS has three production users, that these accounts are not critical and that manual
recreation/instructions are feasible if needed. This is user-supplied deployment
context, not a live database count. Select a supervised small-cohort transition instead
of building a general-purpose automated account migration for E1. The user subsequently clarified that PtS and Scribeswell are read-only applications;
there is no user-document ownership/access migration to plan for this cohort.

### Ownership and minimum adoption path

- Keep the existing Access migration history limited to `access`. The identity owner
  maintains a distinct identity migration history/baseline, even if maintained with
  the Access service. People owns its separate `people` history; Leave owns `leave`.
  Reuse controlled deployment coordination under ADR-0016/0020, not startup migrations
  or a second generic runner.
- Inventory identity tables, functions, policies, grants, Auth hooks and dependent
  references against the selected target. Record which legacy migration/bootstrap
  owns each object and its successor owner. Verify the baseline before recording it
  as adopted; never stamp an unknown schema as equivalent. Existing source SQL spans
  concerns, so transfer ownership by explicit object inventory, not by assuming a
  whole legacy file can be removed.
- Add the person, account-link and durable actor structures already proposed. Prefer
  keeping the three existing Auth account UUIDs and adding verified links manually:
  one explicit account-to-person/actor mapping entry per user, with authorized actor,
  verification evidence reference and timestamp. No email-based automatic merge,
  synthetic employment from a role, or implicit new grant.
- Keep existing organization IDs where possible. Provision membership and exact PtS
  grants deliberately, then explicit Leave grants/employment only for the E1 users
  who need them. Recheck any retained Auth hook/profile behavior. A successful login
  alone is not evidence that either application's access is correctly configured.
- At the verified ownership transition, prevent legacy bootstrap/composition from
  reapplying adopted objects independently. Update the owning source/configuration,
  never hand-edit generated composition output. Preserve a reproducible clean bootstrap
  as well as the supported existing-database adoption route. Exact migration locations,
  object inventory and coordinator integration remain delivery design evidence.

### Manual recreation if necessary

Recreation is an allowed transition option, not the default requirement. If an account
UUID changes, record old account/actor → replacement account/person/actor mappings,
recreate the intended membership/grants explicitly. Do not rewrite immutable historical attribution merely to make it equal
new account IDs; retain old actor identities and their mapping. Account replacement
must not combine grants from unrelated identities or preserve unintended old access.

The account-related dependency is current authentication/membership/grants:
`access.grants.user_id` and identity membership reference account IDs. The existence
of Content attribution fields or document endpoints in repository code does not show
that these users have production documents requiring migration. Per the user's
clarification, do not require a PtS/Scribeswell document inventory, ownership transfer
or document-access reconciliation for this transition. Preserve the applications'
read-only content and verify sign-in and intended read access after any account change.

Use a short planned maintenance window if the chosen transition cannot keep the
previous version working, as allowed by ADR-0020. Record the affected users, exact
changes, backup/restore or corrective recovery procedure, old-session treatment and
user instructions before execution. Verify new sign-in and intended read access, and revoked/replaced-account rejection
before reopening. The
user can coordinate the three people; this planning work sends no messages and makes
no production changes. No generic account-import/reconciliation UI or zero-downtime
migration system is an E1 prerequisite.

### Discovery authority and required evidence

The existing `identity_bridge.sql` restricts reads by selected organization and actor;
it does not supply the pre-selection organization listing. Add an identity-owned,
caller-scoped discovery contract exposing only memberships/organization display fields
needed by Access; Access applies current application grants. Do not solve discovery
by granting unrestricted identity-table reads or using a runtime superuser. Set verified
account context transaction-locally, clear it on pooled reuse and test absence/spoofing
of context. Exact SQL authority (including any restricted routine and execution grants)
must be reviewed with the baseline; listing must not weaken existing scoped checks.

Required delivery evidence is bounded to the selected transition: disposable synthetic
three-account rehearsal, unchanged v1 PtS/Content clients, new v2 person/actor resolution,
explicit grants, missing/mismatched mapping, discovery isolation, migration failure
blocking activation, and recovery from each completed step. Include account-recreation
fixtures if that option is selected for execution. Keep a per-account completion record,
not an assumption that all three succeeded because one did. No historical Expense
conversion is required under ADR-0045.

Scaffold: owner histories and controlled release evidence remain reusable; the three-user
mapping is deployment-specific and must not become a generated default or fixture with
real personal data. Shared UI: existing sign-in/setup feedback suffices. Agent context:
existing rules apply. ADR: this uses ADR-0042's preservation where possible and ADR-0020's
planned-maintenance path; no accepted policy is amended. No migration or readiness
verification has run. Full live object inventory is execution preparation, not a reason
to build speculative bulk migration tooling during story planning.


## Application admission scope gap — 2026-10-02

The user requires organization/application and user/application configuration. Existing
v2 check/list proposals must add current organization-app enablement before readiness;
membership plus a capability alone is insufficient when the organization lacks Leave.
[Proposed ADR-0046](../decisions/0046-application-availability-and-access-scopes.md)
also provides account-scoped Scribeswell admission without artificial organization
membership. App Directory remains the catalogue/discovery owner, consuming Access
decisions rather than granting every enabled app to every authenticated account.
Finalize account-app admission choice, typed scope/admission schemas, disable/revoke
behavior, authority and compatibility fixtures before dependent stories become ready.
E1 provisions explicit configuration; shared administration UI remains E2.


Scribeswell clarification, 2026-10-02: public reading needs neither sign-in nor an
organization. Future account registration and explicit PtS-derived Scribeswell
capabilities remain separate from organization-scoped Leave. See proposed ADR-0046;
its earlier selected-account-only reader recommendation is superseded by this user
direction. Do not implement artificial public memberships or broaden Leave grants.


## Repository ownership inventory — 2026-10-04

The [identity migration inventory](./identity-migration-ownership-inventory.md) identifies
legacy identity tables/types/hooks/public routines, Access's separate history, dependent
Expense/content references and the actual composition/coordinator paths. It proposes
an identity-only history under the existing maintainer and a bounded clean/adopt
handover. It does not verify a live baseline or authorize running migrations. This is
the concrete repository evidence for E1-ID/ACCESS; target privilege/compatibility,
source handover and migration rehearsal gates remain open.

## Membership retirement and rejoining — concrete E1 design, 2026-10-04

User approved the membership-bound Access design. Select a **new membership ID on
rejoining**, preserving the retired row for history. This uses the existing membership
identifier and avoids adding a second membership-generation field to every grant and
API decision. It implements the accepted rule that old grants never resume merely
because an account rejoins; employment and app suspension remain separate.

### Identity-owned constraints and transitions

- Keep `identity.org_member.id` as the positive bigint identity primary key and retain
  existing IDs. Organization/account references and historical attribution remain intact.
- Replace unconditional `UNIQUE(org_id,user_id)` with a partial unique index on
  `(org_id,user_id) WHERE deleted_at IS NULL`. This enforces one active membership per
  account/organization while allowing retained retired memberships. Validate the actual
  constraint name/dependencies against the selected baseline before migration.
- Treat `deleted_at` as retirement for this contract. Active → retired records the
  server timestamp and authorized audit atomically in Identity. Once retired, the row
  cannot return to active through an ordinary update, seed or retry. Organization/account
  binding cannot be changed to repurpose a membership ID. Enforce these transitions at
  the owner database boundary as well as its command handler; reject direct protected
  writes rather than relying only on an administration screen.
- An explicit rejoin creates a fresh row/ID with fresh attribution and no inherited
  owner flag or member roles. Authorization to rejoin and authorization to grant access
  remain explicit. Concurrent create attempts must not create two active memberships;
  return a safe already-active/conflict outcome without copying or overwriting roles.
- Retirement/rejoin are retriable owner commands with their own stable operation IDs
  and immutable outcomes. A delayed retirement targets its original membership ID,
  never “whichever membership this account currently has.” A replay of an old join
  resolves that original retired membership, never creates another one or presents a
  later membership as its original result. App/domain grants are separate operations.
- Preserve required membership/role and actor evidence; no cascading hard deletion is
  introduced. Existing physical delete paths and Auth-account cascades need explicit
  retirement/adoption handling before they can erase required references. Manual account
  recreation is still allowed under E1-ID; preserve mappings/history and create intended
  replacement membership/grants deliberately.

### Access and legacy compatibility

Access grants bind `(org_id,user_id,membership_id)` to the exact current membership.
Newly created rejoin membership cannot match old grants. No cross-owner transaction is
needed to make retirement effective: a subsequent Access check rejects a retired
membership even if its grant row still exists. Already-authorized bounded execution
continues to follow ADR-0021; this design promises no instantaneous remote cancellation.

An authorized regrant may update the existing unique `(org_id,user_id,permission)`
grant row to the new membership ID, clear revoked_at and advance revision, with immutable
before/after attribution and operation evidence. It must validate the exact currently
active membership supplied to the command; never silently substitute a newer membership
for a delayed grant. If retirement races that validation, the resulting old-bound grant
is ineffective on subsequent checks. E2's UI displays the resulting current state.

Existing `identity.member_role` rows stay attached to their original membership ID;
new membership gets no copied roles. Auth token hooks must select only active membership
and nonretired organization. The legacy `public.get_user_roles()` needs current account,
organization and active-membership validation, not merely the token's historical
member_id. Existing JWT role claims are never current Access authority. Both Access v1
and v2 must enforce the new binding after activation, alongside app admission.

Update seed/provisioning lookups to select only the intended active membership; existing
unqualified org/account subqueries can become ambiguous once historical rows exist.
Any `ON CONFLICT(org_id,user_id)` writer must be changed deliberately for the partial
unique constraint rather than assuming its previous conflict target remains valid.
Keep identity schema changes in the distinct Identity history, Access grant changes in
Access history, and coordinate their activation. If supported old writers cannot run
against the new constraint, use the already-authorized planned maintenance procedure;
record recovery before removing the old unique constraint. Do not declare compatibility
solely because current rows happen to have no retired duplicates.

### Separation from employment and suspension

Retiring application membership does not end or delete shared employment. Rejoining does
not create another employee: verified person/organization resolution still finds the
one enduring employment relationship, with its existing periods and Leave draft where
currently authorized. Conversely, ending employment does not automatically delete all
application membership. Domain rules and explicit access policy remain separate.

Disabling/re-enabling an app or organization-app entry does not retire membership, change
its ID or revoke configured grants. It resumes only still-valid membership-bound grants,
as already approved. No additional user-facing draft workflow or confirmation is added.

### Required evidence and impacts

E1-ID/ACCESS fixtures: retire → denial → rejoin with new ID → no access until deliberate
regrant; old v1/JWT/member-role references cannot restore access; delayed retirement,
old join replay and delayed grant cannot affect a replacement membership; concurrent
joins preserve one active row; ordinary app suspend/re-enable retains valid access;
rehire/person linkage does not duplicate employment; historical rows preserve evidence.
Test actual owner constraints, restricted credentials and transaction rollback as well
as API outcomes. E2 uses this same contract for administration, not a second lifecycle.

Scaffold: promote proven owner-command identity/constraint/error tests with first
consumers, but membership lifecycle remains Identity-owned. Shared UI: existing access
states; no new screen in E1. Agent guidance and accepted ADRs unchanged. This closes the
membership-ID-versus-generation design choice. Exact DDL/trigger/privilege inventory,
legacy-writer migration, immutable audit schema and clean/adopt rehearsal remain technical
readiness checks. No migration, grant or account change was executed.


Restricted discovery refinement, 2026-10-04: the
[owning admission contract](./application-admission-and-discovery.md#restricted-discovery-database-contract--2026-10-04)
specifies the Identity-owned current-account membership projection, Access-owned filtered
organization/app discovery routines and separate restricted execution roles. Verified
transaction account context is trusted backend input, not an independent database proof
of authentication. No arbitrary account selector, new person requirement or cross-owner
browser/table access is introduced. Actual SQL/grant/compatibility evidence remains open.

## Minimum People persistence contract — 2026-10-04

This makes E1-PEOPLE's relationship/period design concrete under ADR-0040/0041/0042.
Generate `services/people` through E1-SERVICE; keep its `people` schema, migration files,
`people.alembic_version`, runtime identity and migration authority independent. This is
planned structure, not an existing package or permission to implement before readiness.

### Owned records and constraints

| Record | Minimum fields | Invariants |
| --- | --- | --- |
| `people.employment` | `id uuid`, `org_id uuid`, `person_id uuid`, `revision bigint`, server-managed creation/update actor UUIDs and UTC timestamps | PK id; unique `(org_id,id)` for scoped child references; unique `(org_id,person_id)` for one enduring employment relationship; positive revision. Organization/person/actor IDs are verified external references without cross-owner FKs. No Auth account or membership ID is required on this record. |
| `people.employment_period` | `id uuid`, `org_id uuid`, `employment_id uuid`, `start_date date`, nullable `end_date date`, server-managed creation/update actor UUIDs and UTC timestamps | PK id; composite FK `(org_id,employment_id)` to employment; non-null start; end null or >= start; inclusive nonoverlap for the same organization/relationship, enforced in the database. No cascade deletion of retained periods. |
| `people.employment_change` | `id uuid`, `org_id uuid`, `employment_id uuid`, `operation_id uuid`, `revision bigint`, `actor_id uuid`, `created_at timestamptz`, typed change kind and bounded reason/evidence reference, explicit before/after period-date details where applicable | Owner-local immutable change evidence, scoped FK to employment and unique `(org_id,employment_id,revision)`. Creation attribution only. Record relation creation and subsequent accepted changes, not every read; no generic full-row or person/profile snapshots. |

Employment changes and period changes advance the **relationship revision once per
accepted owner command**, atomically with required history and its operation outcome.
The revision identifies the complete observed relationship/period set, not just one
period's last-change timestamp. Period UUIDs remain stable across authorized corrections;
rehire appends another period under the same employment ID. The read obtains relationship
revision and interpreted period in one consistent database statement/snapshot. No
independently maintained current/future/ended column is needed: derive it for as_of_date.

E1 provides controlled owner provisioning and the read contract, not public employment
editing. Reuse the owned command/outcome pattern for retriable provisioning; the change
event itself must not be treated as a sufficient idempotency protocol for an arbitrary
command. Exact provisioning command fields, compact result and canonical-input binding
remain part of its readiness contract. Do not run seeds that rewrite real employment
history on application startup. E2 correction commands still require their accepted
history/impact contract before becoming available to users.

### Inclusive periods without overlap

Use a PostgreSQL GiST exclusion constraint combining organization/relationship UUID
equality with overlap of `daterange(start_date, end_date, '[]')`; verify `btree_gist`
availability and its owner-controlled setup in the selected environment. Start/end
API fields remain inclusive date-only values; PostgreSQL's internal range normalization
must not change the end date returned to clients. Null end is unbounded. Reject special
infinite dates and dates outside the declared API-compatible range; pin concrete bounds
with the wire schema rather than silently mapping infinity to an ordinary date.

PostgreSQL documents this [range exclusion pattern](https://www.postgresql.org/docs/17/rangetypes.html#RANGETYPES-CONSTRAINT).
This is a design choice, not a successfully installed extension or tested constraint.
Use the existing API validation plus database constraint; do not replace the database
invariant with an application-only overlap query.

Required examples:

- 1 January–31 March followed by 1 April–open end is permitted.
- A new period starting 31 March overlaps the previous inclusive end and is rejected.
- An open-ended period must be explicitly ended before a later period can coexist.
- A one-day period has equal start/end and is valid; end before start is invalid.
- Concurrent overlapping inserts cannot both commit; another organization/relationship
  is independent. Missing/cross-org parent references fail structural checks.

The owner command locks/guards the employment row for revisions and history; no remote
service wait occurs under that write lock. Ordinary read requests do not acquire a
business write lock or claim to lock the relationship through a later Leave commit.
Leave's bounded draft observation and local-date/settings guards remain consumer-owned.

### Identity, permissions and least disclosure

An accountless person may have an employment record and periods. Owner provisioning
verifies organization/person references through approved owner contracts before its
local transaction; it does not query Identity tables from People or create Auth accounts.
Do not use employment existence as proof of membership, app enablement or permission.
Leave identifies the person through current verified Access checks; People independently
checks its authorized service/user/scope contract and never trusts a raw person header.
The minimal `/employment/me` route accepts no arbitrary person/employee override.

`people_runtime` has only the required read privileges in E1, no DDL or unrestricted
setup writes. Controlled provisioning uses a separate restricted owner writer, with
migration/bootstrap authority separate again. Force organization RLS on all owned
records and constrain own-read employment by verified person context; child queries
join the scoped parent. Runtime cannot read other employees merely because they share
an organization. Change-evidence reads are not exposed through the employee discovery
endpoint. Public browser roles receive no People table/RPC grants. Prove scope failure,
account/person changes and pooled reuse under actual runtime credentials.

E1's minimal response remains the previously defined found/not_found/effective variants;
no names, emails, employment numbers, reasons or audit contents are added. Future
employee directory/display-name lookup belongs to its authorized owner contract, not a
second editable profile in People. No read audit is invented merely for this schema.

### Department, location and supervisor remain shared and optional

Their approved ownership/nullability is unchanged. E1 neither requires an assignment
nor reads those values, so it does not create unused department/location catalogues or
unconstrained placeholder foreign keys just to populate the schema. E2 adds the scoped
catalogues and effective-dated assignments under People, with nullable references and
same-organization constraints. No assignment is a valid state; unavailable assignment
lookup is not reported as null. This sequencing does not move these fields back to Leave.

Supervisor self/cross-organization checks and historical workflow snapshots remain
binding for their consumers. Shared location does not supply Leave's work timezone or
replace its work profile. Leave uses its own settings linked by `(org_id,employment_id)`
without a cross-owner FK; People does not store Leave policy, balances, approvers or
request/draft state. No organization-chart/import or HR suite is added.

### Provisioning, evidence and remaining readiness

Fixture manifests contain explicit synthetic IDs, two organizations, accountless and
linked people, absent/no-period setup, current/future/ended/rehired periods and multiple
accounts pointing to one person. Deliberate duplicate relationship/overlap inputs must
fail safely without partial changes or revision advancement. New employment gives no
application access; membership rejoin does not duplicate employment or its retained draft.
Test source-date interpretation, exact large revision serialization and no stale snapshot
mixing. History/operation failure must roll back the owner change. RLS and exclusion
checks run on actual PostgreSQL, not SQLite or an administrator-only test connection.

This settles minimum record ownership/keys and the selected overlap mechanism. Remaining
pre-readiness work: exact actor/provisioning and history/result schemas, database-date
bounds, extension/migration privilege verification, own-read service policy, safe typed
constraint errors and runnable isolated evidence. E2's shared write/change-impact and
assignment contracts and E5's stronger consequential consistency remain separate gates.

Scaffold: prove optional People client, scoped constraint/error/attribution fixtures with
this first consumer; do not inject employment into all apps. Shared UI: existing setup/
read-only/unavailable states suffice. Agent instructions and accepted ADRs unchanged.
No application code, tables, extensions, migrations or accounts were created.


Leave-specific draft simplification, 2026-10-04: Leave ADR-0122 replaces the earlier
requirement for valid work timezone before draft preservation. Identity/ownership and
current access remain mandatory; People date-only interpretation and other consumers'
contracts are unchanged. Leave may use discovery without a dated interpretation when
timezone setup is missing, preserving bounded input without claiming eligibility.
Confirmed ended-employment restrictions remain. Reconcile the Leave consumer's optional
dated-observation schema before readiness; do not fabricate UTC or alter People periods.


## Undated employment setup evidence — 2026-10-05

Add required boolean `has_periods` to the planned `found` discovery response. People
returns it from the same statement/snapshot as relationship identity and revision, using
existence of an owned period for that scoped relationship. It means only “at least one
employment period is recorded”, not currently employed, eligible or permitted to submit.
No timezone, date calculation, extra endpoint or exposed period history is needed.
`not_found` remains distinct and has no invented employment ID/has_periods value.

Leave with current authority and established relationship uses `has_periods: false`
for the previously agreed `employment_periods_missing` setup restriction, preserving
read access. With periods present but timezone missing/invalid, it may preserve draft
input under ADR-0122 without inventing a current/ended state. Where a valid dated
interpretation is available and used, the effective response and confirmed restrictions
still apply. A failed People call is not `has_periods: false` or permission to skip
required ownership checks. Same-person linked accounts still need their own current grants.

Update the owning OpenAPI model, typed client and fixture responses together during
implementation; the endpoint is planned, so no deployed response is asserted changed.
Tests: no periods, first period added, period correction/relationship revision in one
snapshot, future-only and ended-only periods both returning true, accountless fixture,
wrong organization and unavailable service. This closes the undated period-presence
schema choice; executable evidence and provisioning/readiness gates remain open.


## Canonical capability-check wire — 2026-10-06

This technical design implements the accepted ADR-0053 scope distinction. It replaces
prior two-field `/v2/check` proposals; none has been implemented. Do not maintain two
ambiguous v2 inputs. ACCESS-B owns models, OpenAPI, consumer adapters and fixtures together.
Legacy PtS adoption follows ADR-0052, not a permanent v1 compatibility requirement.

`POST /v2/check` requires the end-user bearer and distinct service credential. Body:

```json
{"permission":"pts.poetry.read","authorization_scope":{"kind":"account"}}
```

```json
{"permission":"leave.request.own.read","authorization_scope":{"kind":"organization","org_id":"<organization UUID>"}}
```

The authenticated bearer determines the account; no account/person/actor selector is
accepted. Capability registration determines the required scope and application.
Reject unknown fields, duplicate keys, malformed IDs and absent required organization
with `validation_failed`. Reject a well-formed but registry-incompatible scope through
the safe validation outcome after service policy validation; never try another scope.
Service policy still limits exact capabilities/endpoints. No top-level optional org_id.

Success common fields: `account_id`, `actor_id`, `permission`, `authorization_scope`,
`decision_id`, `checked_at`. UUID strings and UTC RFC3339 apply. Variants:

| Variant | Additional required fields | Meaning |
| --- | --- | --- |
| Account capability | No person, membership or organization fields | Exact account grant; actor is verified for attribution. Account does not require employment or a person link merely for PtS reading. Missing actor mapping is a safe setup outcome after authority checks, not invented identity. |
| E1 Leave organization own capability | `person_id`, positive decimal-string `membership_id`, `resource_scope: {kind: own, person_id}` | Current organization authority plus verified person/actor setup. `authorization_scope.org_id` identifies the organization; resource scope identifies whose records, not an alternative access scope. |

Do not include absent-variant fields as null placeholders. These are a closed typed
union for current consumers; future organization capabilities need their own declared
resource scope, not an assumed universal own-person restriction. Client verifies exact
permission, authorization scope and identity/resource consistency. The previous generic
`scope` own-person field is now `resource_scope`; no overloaded meaning of scope.
No-store/private responses, no replayable decision token, current authorization and
safe errors remain binding. Person-link errors apply only to capabilities that require
that link. The actor/account mapping must not force employment or organization membership.

E1 Access account checks cover current profile, global app enablement and exact account
grant. Organization checks retain org enablement, current membership and exact bound
grant, plus the applicable identity/resource requirements. Provider waits stay outside
DB locks. Selected wire changes must propagate to Leave/People/reference consumers and
all examples before executable contract generation; source schemas/tests do not yet exist.


## Account-only actor resolution — 2026-10-07

This refines earlier employee-focused actor/link wording for accepted ADR-0052/0053.
An account can have multiple organization memberships and separate individual app grants;
none requires employment merely to exist. Account-only PtS actions need stable attribution,
not a fabricated person/employment or organization membership.

Identity owns a durable actor registry and an account-to-actor association independent
of account_person. Each account has one stable account actor; each service has a distinct
service actor. A verified person link is additional identity evidence for workflows that
need it, not the source of every account actor. Retain the actor and historical association
after account removal/deactivation; do not cascade-delete attribution or reuse an old
actor for a replacement account. Where verified legacy authorship used the account UUID,
preserve that UUID as the actor ID through explicit adoption; unknown/service legacy
profiles require classification, never assumed human backfill.

Two accounts later linked to the same person keep distinct account actors and independent
grants. The person link permits domain person resolution; it neither merges historical
authorship nor unions permissions. A new account created after deletion receives its own
actor/grants, even if the email or person matches. Linking to an existing enduring employee
may restore historical domain context only after explicit current authorization.

### Resolution and controlled setup

1. Authenticate the bearer and establish current account/profile and capability authority.
2. Resolve the verified account's stable actor through the Identity-owned restricted
   projection. Missing actor returns the declared setup outcome after disclosure checks.
3. For a capability requiring a person (Leave own requests), additionally resolve the
   verified person link and resource scope. Account-only PtS omits person/employment fields.

No login, permission read or Content request creates identity rows. E1 controlled setup
adds Identity `account_actor.ensure`: exact verified account_id, explicit intended actor_id,
expected absence, authorized executor and evidence reference. Absent mapping may be created;
an identical verified mapping may return unchanged; a conflicting mapping fails rather
than relinks. Validate actor kind and uniqueness, preserving legacy identity deliberately.
Reuse existing operation/replay/attribution rules and owner-local transaction. The later
account.link_person command consumes the same actor instead of allocating another one.
Actor bootstrap uses the previously required trusted operator mapping; no self-grant endpoint.

The authoritative current-account projection may expose account_id/actor_id to Access
without organization selection or employee joins. It must still reject missing/deactivated
accounts and arbitrary HTTP account selectors. Exact actor DDL/kind constraints, retained
reference strategy on Auth deletion and projection grants remain ID-B readiness inputs;
no extra identity runtime service is introduced. Account deletion disables access even
though historical actor metadata remains.

### Evidence and impacts

ID-B proves account actor without person/membership/employment; later person linking keeps
actor unchanged; same person/two accounts retain distinct grants/actors; account deletion
preserves old attribution; recreation does not take it over; conflicting setup and spoofed
actor fail; duplicate/concurrent ensure commits once. ACCESS-B consumes the actor without
introducing person_link_required for PtS. CONTENT-READ records its verified service executor
and application-asserted initiator distinctly under ADR-0054; forwarding an actor UUID is
not independent user authentication. PTS-ADOPT covers actual account-only behavior.

Scaffold typed identity fixtures, operator adapter and owner documentation update with
ID-B. No new user-facing profile, HR form or shared UI; existing agent/ADR rules suffice.
This is implementation design, not executed schema/provisioning or a readiness pass.


## Actor registry choice — accepted 2026-10-07

[ADR-0056](../decisions/0056-durable-actor-registry-separate-from-login-accounts.md)
confirms the separate registry instead of broadening identity.users to optional-Auth
system identities. Keep account profiles linked to Auth; actor lifetime is independent.
Preserve named System/Migrate actors and verified existing UUIDs; classify service imports
explicitly. The preceding account-only resolution design remains applicable. There is
no actor per login method/run and no implicit merge for several accounts of one person.

ID-B must bind actual table/kind/link constraints, deletion/history behavior and restricted
projection alongside account_actor.ensure and controlled System/Migrate/service bootstrap.
Inventory all supported writers, including legacy JWT-derived audit triggers and text
service attribution; valid seed identities alone do not supply execution context. No new
UI/service or live account deletion is authorized. This resolves the model choice, not
schema/migration/runtime readiness.


## Minimum actor persistence and lifecycle — 2026-10-07

Technical design implementing ADR-0056, owned by ID-B. No actor-management product,
new identity service, live account cleanup or executable migration is introduced.

| Record | Minimum shape | Structural/lifecycle contract |
| --- | --- | --- |
| `identity.actor` | `id UUID` PK; `kind` account/system/service; `display_name`; optional stable `actor_key`; creation/update actor IDs and UTC times | IDs/kind/assigned non-null key are immutable; unique non-null actor_key for named operational identities. Display text is not authority. No Auth/person/org/employment FK on this record. Retain rows referenced by history; no cascading deletion of actors or business attribution. |
| `identity.account_actor` | `account_id UUID` PK; `actor_id UUID` UNIQUE; fixed account-kind discriminator; creation attribution | One permanent account-to-account-actor mapping. Composite actor reference enforces account kind (actor registry supplies the corresponding unique id/kind key). No mapping to System/Migrate/service actors. Account and actor IDs may be equal where legacy evidence requires it; do not assume equality in consumers. |

The account_id in account_actor is a retained historical Auth identifier, not a live FK
whose deletion would erase it. This exception is deliberate: the controlled Identity
writer verifies the live account/profile on creation, while resolution always checks
current account/profile before using the mapping. No arbitrary account IDs may be
inserted through runtime or a browser API. Account profiles themselves keep their Auth
FK. Actual legacy profile/membership/attribution FKs may still prevent Auth deletion;
this design does not authorize dropping those safeguards or promise deletion works today.

Current account deactivation denies authentication-dependent operations without deleting
actor/mapping. If a later controlled account-removal procedure removes the live account,
its historical UUID remains in the mapping and cannot be reassigned. A recreated account
with a different UUID receives a new actor. No actor relink/merge command in E1. Separate
accounts for one person remain distinct; optional account_person linkage does not mutate
account_actor. Provisioning must reject an attempted reuse of a retained mapping as a
new account identity rather than silently inheriting history or grants.

### System, Migrate and operational identities

Controlled baseline/adoption registers named `system` and `migrate` actors and explicitly
required service keys such as `pts-import`. Preserve verified existing System/Migrate
UUIDs; service text such as service:pts-import maps explicitly to a stable registry UUID.
Do not allocate new actors per deployment/run, copy platform-admin flags onto them, or
require Auth records. Actor keys identify attribution; they contain no credential.

Add an owner-controlled `actor.register_system` command for system/service variants:
explicit actor ID, kind, stable key, display name and expected absence. Same verified
registration may return unchanged; conflicting key/ID/kind mapping fails. Only trusted
Identity setup authority may run it. Reuse owner outcomes/audit and supported writer
privilege boundaries. Human account actors still use account_actor.ensure.

The initial trusted migrator actor is established by the controlled migration bootstrap
before ordinary actor-attributed commands run. A clean baseline may give that bootstrap
actor self-referencing creation attribution with an explicit bootstrap release/command
record. This describes trusted setup, not a runtime default or evidence of a human
initiator. Adoption preserves actual legacy provenance instead of applying this rule
retroactively to historical data. Subsequent registrations name the verified executor.

Missing actor context on a normal write fails safely; never silently substitute System
or Migrate. Support corrections identify the actual support account, or the executing
job plus verified initiator if delegated. Only configured restricted execution identities
may select their established system/service actor; a manifest cannot claim arbitrary
actors. Keep database-login/service-credential authorization separate from actor lookup.

### Read, write and adoption boundaries

A restricted Identity projection resolves only the authenticated current account's actor
for Access, independently of person/employment/org. Service actor resolution uses trusted
service identity configuration, not a user-selectable actor parameter. Actor display
resolution exposes only permitted labels; no general account directory is added.

Within Identity, new actor references use non-cascading local constraints where applicable.
Across owner schemas follow existing external-reference contracts: verify and retain actor
IDs without adding cross-owner table dependencies. Legacy FK conversion, ON DELETE SET NULL
behavior and old UUID/text writers require explicit mapping/migration tests; do not rewrite
original authorship or silently interpret all old system profiles as human accounts.

ID-B tests: constrained actor kinds and uniqueness; missing-context write denied; account
mapping without employee; same account idempotent ensure; conflicting ensure rejected;
System/Migrate without Auth accounts; verified service text adoption; historical mapping
survives simulated live-account removal while current lookup denies; recreated account
new identity; later person link unchanged; restricted runtime cannot register or relink.
Characterize all affected writers/triggers first and retain explicit transaction/recovery
checks. Physical DDL names, exact payload/display-name limits, restricted projection
privileges and coordinated deletion/adoption matrices remain readiness work, not implied
by this minimum design. Scaffold/fixtures/docs update in ID-B; no additional UI or ADR.


## People current identity context — proposed 2026-10-08

The user approved keeping application capability checks in Leave and keeping People
independent of `leave.request.*`. This proposes the missing verified-context wire under
the existing Access/Identity owner integration; no separate identity microservice.

Add a restricted Access endpoint `POST /v2/identity/organization-context`, initially
allowed only for the People service credential. Input is exactly `{org_id: UUID}` plus
the current end-user bearer. No account/person/actor override, app ID or permission
string. Verify the service before disclosing user/setup information, then current
session/account profile, active organization and current account membership through
Identity-owned projections. No provider wait while holding a database transaction.

Success is private/no-store and includes `account_id`, `actor_id`, `org_id`, decimal-string
`membership_id`, nullable `person_id`, `observation_id` and UTC `checked_at`. Resolve the
account actor through the accepted registry; missing actor is a safe setup error after
membership is established. A missing person is null, not an inferred employment or new
person record. Responses are current identity observations, not reusable grants/tokens.
This endpoint performs no application admission or capability decision and must never
replace `/v2/check` for protected application actions. No implicit Access app grant is
created by resolving identity or discovering employment.

People's own-employment request proceeds as follows:

1. Authenticate the incoming consumer service and its explicit permission to call the
   organization-scoped own-employment route; reject unknown consumers. Any configured
   organization restrictions remain binding. A user token alone cannot call People.
2. Use People's own Access credential with the forwarded user bearer and requested org
   to obtain current context. Never accept a caller-provided person as a substitute.
3. Require the returned organization to match, and a verified person link. Enforce that
   exact organization/person in People-owned persistence and restricted-role RLS; return
   only the existing minimum employment response. No other employee selector or manager
   directory capability is included. App admission was checked by the consuming API.
4. On missing current membership, deny; on missing linked person, return the existing
   setup error; on unavailable verification, return unavailable, not not_found or stale
   success. Only an authorized People lookup can establish absent employment.

This keeps ordinary end-user access and the narrow authorized service boundary distinct.
An app service compromised within its permitted People own-read scope is a trusted-caller
risk, not a reason to claim service policy verifies all application business decisions.
Accountless employees remain supported in shared persistence but cannot use `/me` without
an authenticated linked account. Future administrative/history access has separate
contracts; this proposal does not infer it from own-read or organization membership.

ACCESS-B supplies the context endpoint and fixtures before PEOPLE consumes it. ID-B owns
the current projection and actor/person mapping. PEOPLE proves real consumer/context/
scoped-query integration. Test spoofed IDs, wrong/revoked membership, wrong service,
changed person link, missing mapping, provider outage and pooled connection reuse.
No app permission names enter People; no cross-owner table access from People is added.

Scaffold: reuse verified-context HTTP types and safe errors only after the first proven
consumer. Shared UI: existing denied/setup/unavailable states; no new user action.
Agent context/ADRs: existing ownership and authorization rules suffice. Docs: reconcile
Access caller matrix, typed schema and owner projection/privileges with this contract.
Exact bounds, provider revocation semantics and executable proof remain readiness gates;
no endpoint, migration or runtime security evidence exists from this planning change.


## Consequential People change attempts and cancellation fence — E5 candidate, 2026-10-23

**Shared-owner technical proposal within the approved prepare-before-source direction;
not an accepted new ADR, implemented protocol or expansion of E1's read-only slice.**
This binds cancellation safety for later consequential employment/period/supervisor writers
under P-0060 and the [Leave coordination contract](../../../../apps/leave/docs/architecture/contracts/e5-request-command-and-finalization.md#people-change-coordination-direction--approved-2026-10-23).
Leave still owns request consequences; People owns facts and the source commit fence.

### Minimal owner-local attempt identity and state

Register a durable People-owned change attempt after explicit source confirmation and
current authorization, before requesting Leave preparation. Bind its immutable identity
to organization, executor/initiator, original operation ID, typed source command/version,
source relationship/expected revision and canonical submitted input fingerprint. Its
closed state is `registered`, `committed` or `cancelled`. Registration changes no employment
fact/revision and is not the source command's committed-success receipt. Reuse existing
owner operation mechanisms where they represent this state safely; do not create a
platform-wide transaction service or duplicate employee master.

A successful Leave preparation is associated with that exact attempt/source revision and
reviewed change through restricted service calls. Persist the preparation identity/evidence
in People before source commit. Immutable input binding prevents another request from
reusing it for a different employee, effective date, supervisor or reviewed consequence.
Current authorization for a genuinely new/restarted human execution remains mandatory;
reconciliation of an already committed fact has its narrow service authority.

| Current state / operation | Required atomic owner-local behavior |
| --- | --- |
| registered / commit | Lock the attempt and actual source in the declared owner order; require exact registered state, expected source revision and required bound Leave preparation; commit fact/history/revision/source outcome/consequence intent plus `committed` state together |
| registered / cancel | Lock that same attempt; transition to `cancelled` durably without mutating the source fact; return its original identity and definitive cancellation state |
| committed / cancel | Return truthful already-committed source outcome/version; cancellation cannot erase or reverse the fact. Leave must reconcile its actual consequences |
| cancelled / commit, including delayed retries | Refuse execution; never recreate/re-register the same original attempt/operation as fresh. No source effect or committed-success receipt |
| committed or cancelled / matching repeat | Return that original terminal state/outcome through current permitted access; no new mutation |

Commit and cancel must contend on the same actual owner row/conditional transition. The
winner determines a durable terminal state. Expected source revision also prevents a
concurrent different attempt from overwriting changed source facts. This fencing baseline
uses stable attempt identity and retained terminal state; no additional wall-clock lease
or global generation counter is required solely to invalidate a cancelled attempt.
The registration/cancel state is not itself a claim that an absent source outcome failed.

### Safe release and recovery across owners

Leave can release its prepared gate only after either (a) it has authoritative cancelled
state for the exact attempt, or (b) authoritative committed source version and its required
Leave consequences are reconciled. No remote wait occurs while either owner's business
transaction is locked. Cancellation takes effect at People's local transition, not when
Leave starts the HTTP call or a browser stops waiting.

If commit wins, recover/apply consequences; if cancel wins, any delayed commit fails. If
cancellation response is lost or People is unavailable, keep the gate and resolve the
original attempt through bounded recovery. A missing record/read timeout is not cancellation.
Never drop the gate because a timer elapsed while a registered attempt can still commit.
An operational deadline may trigger cancel/reconciliation, but does not independently
make release safe. Concrete exceptional-outage limits and alerts remain open.

A preparation message or response can arrive after People cancelled. Any resulting Leave
gate remains tied to that terminal attempt and is reconciled/released from authoritative
cancelled state; it cannot resurrect source rights. A crash before Leave preparation may
leave a registered source attempt with no fact change; cancel it through the same owner
transition. After source commit, durable consequence intent/reconciliation resumes work;
it does not edit the original immutable success result to pretend all owners committed
atomically. No automatic rollback of another owner's committed employment fact.

Retain terminal attempt evidence while supported delayed retries/messages can use the
identity. No cleanup/TTL can recreate a cancelled operation or make old work fresh.
Service authentication, consumer registration and scope must prevent an arbitrary app
from preparing/cancelling another consumer's change. This candidate defines no public
employee-master endpoints or new end-user cancellation screen.

### Required proof and unresolved shared bindings

Actual People/Leave suites must force both commit/cancel orderings, delayed old commit,
late preparation after cancellation, unknown cancellation response, concurrent different
source attempts, wrong attempt/version/scope, source-commit response loss and failed/resumed
Leave consequence. Inspect real source history/outcome/attempt state and Leave gate/current
approval authority; mock response order is not sufficient. Map this into E5-WRITER-02 and
the real 5.15-K/5.24 producers without duplicate generic test suites.

Exact People attempt storage/API/error schemas, protected owner row order, source-to-Leave
affected subjects, consumer registration, future-effective boundaries, cancellation/service
authority, execution/recovery deadlines and ADR adoption remain open. Shared architecture
acceptance and implementation readiness are not asserted by this technical candidate.
Scaffold impact is proven owner-local outcome/conditional-transition and restricted HTTP
helpers; no shared runtime coordinator, UI surface or new agent rule is introduced.
No code, tests, source edits, migrations or deployment occurred.


## Affected subjects and future-effective observations — E5 candidate, 2026-10-23

**Refines the source-attempt candidate; shared adoption and exact in-flight bounds remain
open.** A People change names exact source employment relationships/items and old/new
source values under its expected revision. The selected batch is not an organization-wide
scope and a reviewed pending-request list is not the permanent affected population.

| Source change | Required affected-subject discovery |
| --- | --- |
| One supervisor edit | Changed employee's unfinished supervisor responsibilities plus old/new supervisor applicability; preserve completed decisions and independently configured final steps |
| Selected/planned replacement | Exact selected employment relationships as independent identified items; per-item source revision/outcome and Leave consequence, not everyone with the previous supervisor |
| Employment end/period correction/rehire | Subject employee's relevant requested-date eligibility and accounting; additionally responsibilities/temporary cover where that person's eligibility is consumed by Leave. End-date treatment stays inclusive under the actual dated employment contract |

People provides authorized source scope/evidence; Leave discovers its own current requests,
responsibilities and appointment applicability. Neither owner reads the other's tables.
Preparation locks/protects the relevant local membership identities and re-enumerates
current work, including requests created since review. A materially changed reviewed
consequence returns for existing renewed confirmation; do not silently broaden a selected
People change or treat an old list of request IDs as permission to omit later work.
Permanent replacement during temporary cover follows L-0160's per-responsibility precedence;
no whole-appointment termination or later return to the superseded supervisor.

### Record schedule now; enforce effective facts at the boundary

Recording a future source change participates in the prepare/commit/reconcile protocol
now. Reconciliation installs sufficient source revision/effective-boundary evidence for
Leave to invalidate stale observations and handle future work. Then release the technical
gate: do not hold a pending-change gate for days until the scheduled date, and do not
apply future supervisor authority early. The installed evidence is a subordinate workflow
observation, not another editable employment master.

A dated/current consequential People observation needs actual source revision, effective
source value, interpretation date/instant and next relevant effective boundary (or explicit
none). Changes to a schedule/amendment/cancellation participate again and invalidate the
old evidence. People owns normalization of supervisor effective instants and the declared
timezone/version for date-only schedules. Do not choose the browser timezone or silently
reuse Leave work timezone for every People fact. Employment eligibility still uses the
requested work dates and inclusive period interpretation from the existing owner contract.
Exact typed source response and date-only timezone rule remain adoption gates.

A Leave execution that reaches a known boundary must obtain/reconcile the now-effective
source observation before a new consequential authorization check. Its protected local
check verifies both the installed source revision and whether the prepared observation's
effective interval still contains the evaluation instant. If not, roll back/reprepare
outside locks; never call People while holding the business transaction. A stale worker or
queue cache cannot authorize the previous supervisor. Queue/transfer recovery may update
stored unfinished assignments later, but an obsolete assignment cannot supply authority
in the meantime. Unverifiable replacement yields pending/retryable attention under existing
rules, not continued former authority or a skipped step.

### Explicit remaining boundary decision

A transaction can perform a valid final authorization check just before an effective
instant and commit just after it. The existing Access bounded-in-flight exception does
not automatically decide this People-domain case. Candidate recommendation: define the
protected final check as the consequential authorization instant, bound the remaining
transaction duration, and permit that already-validated decision to finish; any check at
or after the boundary requires the new effective facts. Exact maximum duration and the
accepted domain rule must be bound before this is claimed resolved. Do not claim a
zero-delay physical commit cutoff or treat a preview/start-time check as final authority.
This candidate is not yet an approved extension of in-flight supervisor authority.

Required cases cover current edit with intervening new request, exact selected batch,
future schedule before/at/after boundary, worker unavailable, amended/cancelled schedule,
old/new/temp actors, employment rehire/date range and old observation crossing the
boundary during execution. Inspect source/item versions, current deciding eligibility,
immutable prior decisions and actual per-owner outcomes. No new universal polling worker,
source duplication or additional end-user transfer confirmation is proposed. Actual
consumer registration/discovery indexes/HTTP schemas, timezone and in-flight rule/budgets,
shared ADR adoption and runtime evidence remain open; no implementation/tests occurred.


### Leave supervisor-boundary rule accepted — 2026-10-23

The user accepted the protected-final-check recommendation for Leave, recorded in
[Leave ADR-0163](../../../../apps/leave/docs/architecture/decisions/0163-protected-authority-check-at-supervisor-boundaries.md).
This resolves only that consumer's permanent-supervisor in-flight semantics: a valid final
protected check before the boundary may finish its short bounded transaction afterward;
checks at/after require the new effective facts, and restarted execution rechecks. Existing
decision evidence retains evaluation instant/source basis. It does not approve the whole
source-attempt protocol, set a numerical duration, extend Access/temp authority or impose
a policy on other apps. Earlier pending language for this specific rule is superseded;
all other source/schema/registration/timezone/budget/adoption/evidence gates remain open.


## Restricted People–Leave coordination callers — E5 candidate, 2026-10-23

**Internal HTTP caller policy proposal under the existing owner boundaries; no new human
role or permission.** People alone writes its employment/period/supervisor facts and
source attempt state. Leave alone writes its requests, assignments, local gates and
consequences. Neither service nor its worker receives the other's database credentials.
An external organization ID, actor ID or operation UUID is never sufficient authority.

| Internal caller -> owner operation | Required bounded authority |
| --- | --- |
| Leave API -> People dated/current facts | Existing authorized consumer/user/domain scope; return only required employment/supervisor/version/boundary facts, not a general employee export |
| People source API -> Leave prepare | Registered People source producer, verified exact registered source attempt/item and current human source-management confirmation context; Leave checks actual requested consequence scope |
| People -> Leave reconcile notification | Restricted source-consequence producer and exact durable committed item/version; notice is a hint, not self-authenticating authority or a replacement for authoritative outcome verification |
| Leave API/reconciler -> People attempt outcome | Registered Leave consumer, exact bound attempt/organization/source relationship; compact state/committed version only, not arbitrary human operation lookup or source input/history enumeration |
| Leave reconciler -> People cancel registered attempt | Explicit consumer-scoped recovery capability for an attempt already bound to that consumer's preparation; People performs the commit-versus-cancel transition. Cannot alter source values, cancel unrelated work, undo committed facts or issue a replacement source command |
| Leave own reconciler -> Leave apply/release | Owner-specific service identity and exact claimed durable causal work; verify source state/version then apply only required local effects. No human Approve, employee response or exceptional funding through service identity |

A person may use the already authorized People source workflow to cancel/recover their
uncommitted change where its owning command permits it; this table introduces no new
browser endpoint or access to internal cancel calls. A user role named Leave Manager or
Approver does not imply employment-management rights or backend service credentials.

### Registration and environment policy

Provision a small deployment-owned allowlist of producer/consumer identities, environments,
exact operation families and supported protocol versions. This is service configuration,
not a customer-managed permission screen, dynamic plugin registry or new runtime service.
Use distinct caller credentials/identities per owner and environment; restricted workers
follow P-0026. Existing E1 Leave own-read/manage caller admission does not automatically
permit these later source/worker operations. Extend caller policy explicitly with the
consuming stories and test denied unrelated calls. Do not reuse a universal platform key.

For relevant organization source edits, preparation participation follows the registered
active consumer's actual dependency scope. Enabling Leave must reconcile current source
versions/schedules before consequential commands activate. Disabling browser access does
not silently abandon an already committed source's consequence intent or an unknown
attempt/gate: narrow registered recovery may finish/cancel that original work without
reviving user access. Retiring a consumer requires resolving/fencing its outstanding
attempts before withdrawing required participation. Exact enable/disable/retirement
handshake and supported-version activation evidence remain to be bound.

### Human execution versus durable recovery

Source creation/commit is a protected human command with current People/Access authority;
caller authentication cannot impersonate an arbitrary employee or manufacture approval.
Queued/restarted human execution rechecks current permission. A recovery identity may
observe/cancel an already registered attempt or complete consequences of an actual commit;
it cannot relabel a delayed unauthorized human source edit as service work. Record actual
executor and original initiator separately. Cancelling uncommitted work is not permission
to commit its proposed employment change after the initiator loses authority.

Derive scope from stored attempt/preparation/work ownership plus verified service policy,
not solely request headers/body IDs. People cancellation is allowed only for the exact
bound consumer; source human authority and consumer scope remain distinct. Confused-deputy
cases (wrong consumer, organization, employee, attempt/version or environment) fail before
protected details are disclosed. Unsupported protocol versions retain work for investigation
and block unsafe activation, rather than dropping required consequences.

Preserve existing machine-readable denied versus unavailable outcomes, redacted credentials
and safe operation/trace links. Credentials and full source change payloads never enter
logs or browser responses. Pin actual authentication transport/credential provisioning to
the owning service integration before delivery; Access's existing X-Service-Key convention
is not automatic authority for every People/Leave endpoint.

### Evidence and completion limits

Actual owner suites exercise valid paired calls, user-only credential rejection, wrong
service/environment/consumer, forged scope, unrelated attempt lookup/cancel, current human
revocation versus legitimate committed recovery, disabled app with pending reconciliation,
protocol mismatch and denied cross-owner DB access. E5-WRITER-02/AUTH-01 reference real
owner cases; no duplicate generic authorization service is introduced.

This candidate allocates callers and least authority, not final route/error/schema/credential
implementation or full protocol adoption. Exact consumer admission lifecycle, HTTP schemas,
source version/effective-time payloads, execution budgets and real rollout evidence remain
open with architecture acceptance and readiness. Scaffold reuses proven restricted HTTP
clients/attribution; no shared UI/agent-context or accepted ADR changes are required.
No credentials, grants, code, migrations, runtime tests or deployment were changed.


## Leave participation across access disable/re-enable — E5 baseline, 2026-10-23

**Clarifies the agreed distinction between organization app access and individual
membership/grants; no new configurator control.** Access alone owns global/organization
Leave admission under P-0046. Source coordination is a separate deployment/owner obligation:
Access's enabled flag is not an instruction to unregister the People–Leave consumer.

| Situation | Required behavior |
| --- | --- |
| Before first Leave adoption | Install supported restricted caller policy and participating People source writers, initialize Leave's source/boundary observations and reconcile adoption work before admitting consequential Leave commands |
| Organization/global Leave access disabled | Enforce Access's existing new-action denial and bounded in-flight rules; retain drafts/grants/data. Do not remove source participation or credentials needed for narrowly authorized recovery |
| People change already prepared/committed at disable | Resolve its original attempt; either authoritative cancel or actual committed consequence reconciliation. Disable cannot be treated as cancellation, rollback or proof no source commit occurred |
| People changes after disable with retained Leave work | Keep required source participation for that retained workflow scope. Current facts and effective boundaries remain correct; no browser access or human approval is granted by recovery |
| Leave access re-enabled | Resume only current valid membership/grants. Independently verify supported owner protocol, current source observations and unresolved relevant gates before consequential commands run; no stale authority or assumed empty backlog |
| Person added/removed or capability changed | Existing Access/People identity, membership and domain rules apply. This is not an organization-app toggle or a reason to erase/change another person's source attempt |

A Leave-specific readiness predicate may block an unsafe consequential API action while
owner reconciliation is unavailable; it does not pretend Access revoked the user's grant.
Use the existing truthful unavailable/pending recovery behavior and preserve independently
permitted draft input. No new onboarding wizard, progress screen, approval queue or
customer-operated integration registry is introduced. Current protected reads retain
actual scope/access checks; this is not authority to show disabled app data to users.

### Adoption ordering and retirement limit

The deployment caller allowlist authenticates services; organization participation says
which source changes require this consumer. Neither can be inferred from a launcher result
or a cached browser access flag. Initial adoption must establish a source-side participation
cutover **before** taking the authoritative source/boundary baseline and opening Leave
consequential admission. Writes after that cutover must use the preparation protocol;
concurrent changes during baseline creation must be reconciled before readiness. No interval
may admit Leave commands while relevant People writes can bypass participation.

Bind and prove the actual cutover mechanism with the People source implementation and
controlled release procedure. The current planned People package is not evidence that a
runtime subscription/registration mechanism exists. Do not silently invent a general
registry service or claim a backfill snapshot alone prevents adoption races. Coordinated
migration/activation evidence remains required under P-0020.

**No automatic consumer retirement is part of MVP disable/re-enable.** Participation
remains while retained Leave workflows or supported delayed work depend on it. Removing a
deployed consumer later is an explicit technical decommission/release operation: resolve
or fence outstanding attempts, reconcile committed consequences and prevent new dependent
commands before removing required policy/handlers. Retained historical data is not blanket
permission to run ongoing business actions, and absence of ready queue items is not proof
that delayed/retryable versions are gone. P-0028 compatibility remains binding. No new
end-user retirement feature or speculative dynamic subscription lifecycle is planned here.

Actual owner acceptance covers disable before prepare, between prepare/source commit,
after commit/before consequence, source changes while disabled, current re-enable with
revoked grants, adoption racing a source writer and attempted unsafe handler removal.
Inspect Access admission separately from source attempt/gate/current assignments and
unchanged stored drafts. Existing Access owner tests cover individual membership changes;
E5 references those rather than reproducing them. No live settings, grants, credentials,
source facts, code, migrations or runtime tests changed.

This binds participation lifetime and activation order at design level. Concrete cutover,
wire/storage schemas, execution limits, shared protocol adoption and real concurrency
proof still gate coverage/sizing/readiness. The user's agreement to the access distinction
does not approve all remaining technical protocol details.


## Consolidated People–Leave protocol navigation — 2026-10-23

[People–Leave change coordination](people-leave-change-coordination.md) now owns the
consolidated v1 internal operations/source variants/state sequence. Earlier E5 candidate
sections here remain rationale and adopted rule references; follow that contract for the
current wire baseline and its explicit remaining gates. E1's read-only slice is unchanged.
No new source role, DB access, whole-protocol acceptance or runtime implementation follows.


## People–Leave protocol adoption — 2026-10-23

User adopted the consolidated [coordination baseline](people-leave-change-coordination.md)
under [P-0062](../decisions/0062-people-leave-prepared-source-change-coordination.md).
Earlier candidate/pending-adoption sections are superseded for that design; E1 remains
its read/controlled foundation scope. Actual later source consumers implement required
attempt/participation/storage/HTTP behavior with delivery proof. C5/C6 and overall readiness
remain open; no runtime grant, source fact, migration or application code changed.

## E5 shared management action catalog binding — 2026-10-25

Select `people.employment.manage` as the exact organization-scoped wire identifier for
E2's already required shared employment-management authority. People owns its action/
target semantics; Access owns effective grants. This names one existing authority, not a
new approval permission or a reason to split supervisor/period maintenance into additional
human permission switches. No default role/grant changes are implied.

The resource predicate is `{kind: organization_employments}`: actual employment records
within the checked organization, including authorized creation of a relationship for a
permitted verified person and addition/end of its actual employment periods. Existing
2.16/17 supervisor management uses that same explicitly granted management authority,
with exact same-org employee/supervisor checks and reviewed selection. An employment
record/person link or application role name is not that authority. A service credential
identifies the calling service, not an authorized human employment administrator.

People verifies the current end-user and exact capability/resource target on each human
source command. Preserve initiating account/actor and actual executor attribution; replay
checks current target/outcome visibility under its owner recovery contract. Prepared source
attempt records bind the authorized source action and exact immutable input. Narrow owner
recovery can reconcile an already committed/prepared attempt under its service policy
without manufacturing a current human approval or allowing a new source change.

Leave's policy/schedule/approval/on-behalf/source-impact permission does not substitute
for People management. Conversely, People management grants no general Leave request,
funding, medical or approval permission. Mandatory Leave impact review uses independently
verified exact consequence-read scope as the prepared-change protocol requires; it cannot
substitute a redacted count for a required authorized review.

**Remaining G4-P registry/admission gate:** Access's current generic catalog binds
permissions to applications and app admission. Before registering this shared-owner
identifier, bind its exact common-service registration/admission/default-adoption contract
without silently making it a Leave-owned capability or adding a customer-facing People
app toggle. This document does not claim the existing Access registry already supports
independent shared-service capability ownership. Inspect/propose the smallest compatible
owner design, with any material platform decision explicitly agreed before adoption.
No new grants or live checks are made here. People source payload/attempt/storage remains
the adopted people-leave-change-coordination contract; exact G6 artifacts remain open.

## G4-P internal People admission proposal — 2026-10-25

Proposed P-0063 and Access owning contract select reuse of existing `people` internal
application registration, org admission and explicit `people.employment.manage` grants.
No launcher, extra customer enablement step or Leave-owned capability alias; no automatic
role-name/default grants. Current consumer-specific /v2/check needs its actual People
adapter, not only registry rows. This is the concrete proposed closure of the preceding
G4-P gate, pending user agreement. If accepted, align adopted status/references and plan
actual Access/People producer-consumer tests before activation. No runtime change.

## G4-P adoption and actual existing substrate — 2026-10-25

User agreed P-0063. The proposed common-service registry/admission gate is closed at design
level by existing internal Access app mechanics. Current KDG work already implements the
shared registry/registration/org-admission primitives; do not plan those twice. Current
organization SQL and KDG HTTP branch are kdg_capture-specific, so People caller/resource/
check support and actual People management consumer/adoption remain. No People registration
or service implementation was found in source; deployed state not inspected. Prior pending
adoption text for this decision is superseded; other readiness gates remain.

## Native-file current-session consumer — technical planning candidate 2026-10-25

E1-ID-B's existing current-authentication boundary supplies the narrow subject/session
check selected in the [Content transport contract](content-ownership-and-authenticated-read.md#concrete-native-file-authentication-adapter--technical-planning-candidate-2026-10-25).
It lives with the actual Identity owner and its migration/privilege inventory, not a
new file-auth service or application-owned Auth-table query. Reuse verified current
account/actor/membership and operator target infrastructure already implemented here;
add only the session-check routine/adapter and exact Leave/People consumer registration
that are absent. The original account/person/employment/access separation is unchanged.

The provider check accepts only authenticated registered services and a verified access
credential, returns safe active/denied/unavailable information and opaque subject/session
binding, and releases no provider session row or administration credential. Generated
client/error/credential policy and native restricted-role tests change together. Actual
selected account, service-actor, grant, membership and People resource rows are protected
operator/release inputs, not fabricated live mappings needed to finish a planning document.
Fixture clean/adopt/mismatch/revoked-session proof and real-provider qualification belong
to ID-B and its first consumer. No runtime implementation or current-session evidence is
claimed by this additional planning allocation.

## Account language preference — source coverage refinement 2026-10-26

Leave ADR-0059–0061 require a user's preference to survive organization switching.
E1-ID-B owns the missing persistence/API boundary with Identity's account profile;
E1-A1 owns the actual immediate personal preference presentation. There is no second
person/employment setting, per-organization copy or application grant from a preference.

Use `GET`/`PUT /v2/me/preferences/language` through the existing restricted service/user
context. Resolve the verified account server-side; accept no body-supplied account/org.
A read returns `{preferred_locale, revision}`; verified absence returns English and zero
revision without inventing an employment/profile mutation. A write takes `operation_id`,
`expected_revision` and an exact registered BCP-47 locale tag, updating the account's
preference/revision/server attribution and compact outcome together. Invalid/unsupported
values fail safely. Replays preserve original input/outcome; wrong account, changed
payload and stale revision cannot overwrite another preference. No per-keystroke business
history or new grant/catalogue permission is needed for authenticated own preference.

Persist desired locale separately from rendered fallback. English is initially delivered;
Portuguese readiness remains, with actual translation delivery deferred. A saved desired
Portuguese locale can render English until its resources exist without rewriting that
preference or changing dates' canonical input-format context. UI selection offers the
registered supported choices and explains fallback; no arbitrary localization catalogue
or new translation workflow is introduced. Normal language state follows the account
across organizations; account switching clears the former account's UI/cache. Network
failure never proves preference absence or a completed write. Immediate personal saving
uses existing safe retry/original-outcome presentation, not a business Save/Cancel form.

The existing approved English-only MVP notification increment is unchanged. When actual
translated templates are introduced, the notification owner consumes the same authorized
Identity preference and English fallback, rather than adding per-organization language
truth. Real translation/template proof belongs to that first actual consumer. ID-B/A1
prove own/other-account, concurrent/retried change, organization switch, unavailable
translation and unchanged timezone/authority/stored values. This is planning only.

## Final onboarding and continuity bindings — planning candidate 2026-10-26

The [invitation/prepared-access protocol](organization-invitation-and-prepared-access.md)
selects verified recipient/account binding, seven-day invitations, rotating resend,
fresh mailbox challenge, thirty-day pending approvals and exact per-stage recovery for
2.6/2.9. The [continuity contract](organization-administrator-continuity.md) selects
last-owner plus protected-organization-administrator floors, ordinary self-removal denial
and a single Identity/Access owner-local guard across membership and role writers.
These resolve previously deferred planning inputs as candidates for one final review;
existing membership identities/rejoin, least privilege and no implicit grants remain.

## Consolidated adoption — accepted 2026-10-26

The user explicitly approved the completed consolidated planning package. The reviewed
choices and bounds in this contract are adopted under [the acceptance decision](../decisions/0064-approved-onboarding-continuity-and-content-contracts.md).
Earlier candidate/pending-review wording is historical and superseded for these choices.
Actual implementation and provider/database/browser/recovery proof remain delivery work.
The user requires a new Codex session before implementation; no runtime action here.
