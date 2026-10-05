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
