# Application admission and discovery contract proposal

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

**Status:** Admission/suspension/discovery behavior approved 2026-10-02; wire design pending validation
**Date:** 2026-10-02
**Authority:** [ADR-0047](../decisions/0047-public-access-and-launcher-visibility.md) refines launcher visibility; [ADR-0046](../decisions/0046-application-availability-and-access-scopes.md),
[ADR-0011](../decisions/0011-application-roles-and-business-permissions.md),
[ADR-0019](../decisions/0019-current-server-side-authorization.md),
[ADR-0021](../decisions/0021-revocation-and-in-flight-operations.md)

## One authority for access

Access owns protected application admission, organization-app enablement, current
memberships and effective capability grants. App Directory owns presentation metadata
(app ID, name, canonical URL, description/icon) and publication of deployed entries.
Its publication flag can hide an app; it cannot grant access or serve as the sole
backend kill switch. For a global protected-app disable, use Access-owned admission
state checked by all protected consumers. Do not make each API synchronously call
Directory in addition to Access, or copy independently editable grants into Directory.

E1 introduces explicit application registry/admission and organization-application
records under Access ownership: unique app ID and unique `(org_id, app_id)` admission,
explicit enabled state, revision and server attribution. Absent registration or
organization enablement fails closed. Current capability grants remain separate.
Scope/migration/foreign-key design stays with the owning Access history; never weaken
existing tenant-scoped grants by making organization IDs nullable for Scribeswell.

For Leave, evaluate:

`app globally admitted AND organization app enabled AND current membership AND exact required capability`

Then apply Leave's employment/resource/domain checks. App admission does not require
employment; employee commands do. In E1 use the two explicit own-request capabilities;
E2 extends the reviewed catalog with administration/approval capabilities. No inference
from JWT role names or membership alone. Listing eligible organizations and selecting
one use this same current state, not a separate entitlement evaluator.

## Disable and re-enable behavior — approved 2026-10-02

Disabling Leave for an organization blocks newly checked protected Leave actions and
removes that organization from Leave selection. The launcher still includes Leave if
the user has valid access through another enabled organization. Follow ADR-0021 for
already-authorized short executions; no claim of instantaneous distributed cancellation.
Global protected-app disable applies across organizations under the same rule.

Disable does not delete employees, drafts, audit or configured grants. It is suspension
of access, not data disposal. Existing saved drafts remain stored; clients must remove
protected content when access loss is confirmed and must not claim unsaved edits saved.
Operation outcome recovery also requires current authority. Use shared `access_denied`
without exposing another organization's configuration. A service failure is still
`authorization_unavailable`, not a confirmed disable/denial.

Re-enable is an explicit authorized administration action. Retained grants become
effective only if membership and all other current conditions still hold. The future
administration review must explain that still-valid configured access will resume;
re-enabling never restores deleted memberships or independently revoked grants. No
fresh invitation, duplicate employee or new draft is created automatically. Record both
disable/re-enable with immutable actor/scope/reason/transition evidence under the owning
audit contract. E1 uses explicit fixture/provisioning steps; the shared admin UI is E2.

## Directory wire proposal

Add versioned `GET /api/v2/me/apps`, consumed by updated shared clients/launcher.
Keep the existing `AppEntry` presentation shape; add no embedded grant tokens. Return
`{apps: [...], protected_access_status: complete | sign_in_required | unavailable}`.
No JWT-derived roles or a universal active organization are returned as authority.
The host application owns its per-tab organization context.

- No bearer: return an empty app list and `sign_in_required`. Scribeswell is publicly
  accessible separately but has no anonymous launcher entry; no forced sign-in for reading.
- Verified identity/current Access discovery succeeds: return admitted published apps
  and Scribeswell only if the result includes current PtS admission; `complete`.
  Directory applies this explicit catalogue visibility rule, not a copied grant. With
  no qualifying entries, return an empty successful list.
- Access/provider unavailable: return an empty list and `unavailable`, with an explicit
  could-not-check state and Retry. Do not add a Scribeswell fallback or infer PtS access
  from a stale list. The independent public reader remains usable.
- Supplied invalid/expired token: return 401 `authentication_required`; do not silently
  reinterpret a failed protected identity as a verified anonymous request. Public reader
  content remains accessible through its separate anonymous path.

Directory authenticates as its own restricted consumer to Access and propagates the
verified end-user token. Its discovery-only service contract returns admitted app IDs
and supported scope kinds, not employee data or arbitrary users' grants. Existence
checks across organizations use the narrow discovery authority from the identity
contract. Bounded dependency deadlines and no positive cross-request grant cache;
unknown/unpublished catalogue IDs are omitted and safely diagnosed. Exact internal
endpoint/Pydantic models and limits remain schema work; no implementation claimed.

A listed app does not promise that every page is authorized. Direct app/API requests
always check admission and capability again. A current PtS grant does not reveal Leave.
Scribeswell public reading is unaffected by PtS revocation; future explicit PtS-derived
protected Scribeswell capabilities are evaluated only when those capabilities exist.
No wildcard app inheritance or permanent copied grants in E1.

## Compatibility, evidence and impacts

Existing v1 `/api/me/apps` must stop advertising all enabled protected apps at Leave
activation. Preserve its supported response shape, but filter its `apps` through the
same admission authority. On unavailable current discovery, return a safe retryable
error rather than a misleading complete list. Update PtS/Scribeswell to the v2 client
with safe visibility/empty/unavailable handling; their low-usage transition does not require a broad
legacy adapter program. A stale cached/old launcher never authorizes a direct API call.

The currently ungated `/api/apps` must not be treated as a production administration
API merely because its summary says admin. Restrict the full unpublished catalogue
behind explicit platform administration authority or remove that endpoint from the
public deployment. Public catalogue discovery may expose only deliberately public
metadata; it is distinct from `/me/apps` access and never includes grants.

Required fixtures: absent organization admission, membership without capability,
capability without admission, one authorized organization among several, global disable,
revocation after listing, direct URL/API checks, account without organizations, anonymous
Scribeswell, unavailable Access with usable public reader, invalid token, disable with
retained draft, re-enable with revoked versus still-valid grants, v1/v2 consumer behavior
and public admin-catalogue denial. Map E1-ENTRY-02/03/05/06 and E1-AC-01/09/13/15/17/18.

Scaffold: one admission client, explicit app scope, safe Directory adapter and reusable
launcher states. Shared UI: no HR dependency or mandatory organization selector for
public/account apps. Agent context: root guidance links accepted ADR-0046.
Documentation: this owning contract, Directory adoption, Leave tracking/traceability.
ADRs: 0046 accepted after user agreement; predecessors unchanged. No billing/licensing system,
public registration, runtime configuration, migrations or application code added.


## Access-to-Directory discovery wire — 2026-10-02 design

Select internal `GET /v2/applications` on Access. Require the end-user bearer and
a separate Directory service credential restricted to discovery; no arbitrary user
parameter, selected organization requirement or browser access to the private endpoint.
The current result is `{applications: [{app_id, eligible_scope_kinds}], checked_at}`
as defined in the canonical discovery refinement below. Return unique apps ordered by
app ID; checked_at is a UTC RFC3339 timestamp. The earlier scalar scope_kind is replaced.
E1 includes organization-scoped Leave and account-scoped PtS; PtS is the first
protected account-capability consumer under ADR-0052. Public Scribeswell does not require a
synthetic Access grant or a call to this endpoint for anonymous discovery.

For organization-scoped admission, Access uses current global/org enablement,
membership and an effective registered application capability in at least one
organization. Use a distinct app registry association for capabilities, not permission
string prefix guessing or a wildcard over future permissions. Return no organization
names, employee data, role lists, access tokens or grant provenance. The consumer joins
these IDs to its published presentation catalogue. No applicable protected app is
HTTP 200 with an empty applications list. That is different from failed discovery.

`checked_at` is evidence, never an expiry or reusable grant. Set private/no-store.
The catalogue is a small bounded configuration set: reject an oversized deployment
configuration at validation rather than silently truncating a discovery result; the
concrete configured limit belongs with deployment/schema validation before readiness.
Avoid an unbounded per-organization HTTP loop: the Access owner evaluates the scoped
existence query under its restricted discovery authority.

Use the shared safe envelope: invalid/expired user bearer → 401
`authentication_required`; invalid service identity/disallowed discovery → 403
`service_access_denied`; unavailable provider or current access store → 503
`authorization_unavailable`; unexpected internal failure → 500 `internal_error`.
Missing employee/person mapping alone cannot suppress an organization's otherwise
valid app admission; protected employee commands still require that mapping later.
No future service credential inherits discovery permission automatically.

Directory uses a 3-second total dependency budget for this call, including connection
and response reading, without automatic internal retries. Its request budget is
5 seconds including catalogue composition; these are technical starting limits for
verification, not performance measurements or new Leave business-action deadlines.
On dependency timeout/service credential rejection/5xx, v2 exposes no app links and
explicit `unavailable` status; log safe origin/error category.
Malformed/inconsistent Access data is also unavailable, never full access. Supplied
invalid user authentication remains 401. If Directory itself cannot respond, the
existing public Scribeswell reader remains usable independently of its launcher.

Public reachability does not imply launcher inclusion. Under ADR-0047, Directory
shows Scribeswell only with current PtS admission; this is presentation metadata,
not future protected-feature entitlement. Public direct access remains unchanged.

Generate or validate Pydantic/OpenAPI and frontend schemas together. Add actual
restricted-role fixtures for the application registry relation and existence query,
Directory credential isolation, missing mapping without missing membership, service
failures versus empty results, global/org toggles and stale launcher/direct-API checks.
Retain source and snapshot labels so audit distinguishes authorization observation
from browser display. No discovery result changes grants or organization selection.

## Concrete E1 Access persistence design — 2026-10-04

This refines approved admission behavior for E1-ACCESS/DISCOVERY/LAUNCHER using the
[identity ownership inventory](./identity-migration-ownership-inventory.md). It is a
schema contract proposal, not executed DDL, a new ADR or implementation readiness.
All four tables belong to the Access migration history. Identity remains the owner
of account/person/actor and physical membership records. Directory stores presentation
metadata, not a second admission authority.

| Table | Key and required domain columns | Meaning / constraints |
| --- | --- | --- |
| `access.applications` (new) | `app_id text` PK, `enabled boolean`, `revision bigint` | Stable registered ID, independent of display name/URL. Scope belongs to registered capabilities under ADR-0053; an app may contain both variants. Validate scope-specific contracts before activation. Global enablement defaults false. |
| `access.permissions` (new) | `permission text` PK, `app_id text` FK to applications, required `scope_kind` (`account` or `organization`) | Explicit immutable capability-to-app mapping. Preserve existing PtS identifiers; register exact Leave own-read/manage capabilities. No prefix matching, wildcard expansion or inferred manage-to-read implication. Do not reassign a used capability to another app. |
| `access.organization_applications` (new) | PK `(org_id uuid, app_id text)`, app FK, `enabled boolean`, `revision bigint` | Organization enablement defaults false. Organization ID is an owner-verified external reference, not a new cross-owner FK. Retain the row when disabled; no synthetic public organization. |
| `access.grants` (existing, extended) | Preserve `(org_id,id)` PK, text `id`, UUID `user_id`, text `permission` and unique `(org_id,user_id,permission)`; add `membership_id bigint`, `revoked_at timestamptz` nullable, `revision bigint` | Existing `user_id` continues to mean Auth account, never person/employment. FK permission to registry. Effective grants require an exact current membership binding and `revoked_at IS NULL`. One row per account/org/capability; deliberate regrant updates it with revision/audit rather than inventing duplicate active grants. |

New mutable admission tables use server-controlled `created_by/created_at/updated_by/
updated_at` under ADR-0025, UUID actor references and UTC instants; positive bigint
revisions are serialized as decimal strings. Permission definitions use creation
attribution and immutable app association. New grant attribution is adapted compatibly:
preserve existing text `created_by` and creation time as legacy evidence, add verified
UUID actor reference fields (`created_actor_id`, `updated_actor_id`) and `updated_at`,
and validate existing actor mappings before populating them. Do not blindly cast old
text or rewrite historical authorship. Generated new-owner tables use the ordinary
ADR-0025 names; this exception is confined to the existing Access table transition.
Exact transition constraints must be verified against the selected baseline.

### Membership-bound grants and explicit provisioning

A grant must match current membership ID **and** its organization/account; membership
IDs are positive bigint, never JavaScript numbers on the wire. They remain external
references without a cross-owner database FK. The Access grant writer validates them
through the identity owner's approved restricted contract. Authorization rechecks the
same binding, so a subsequent membership removal makes the grant ineffective even if
revocation cleanup has not run. Rejoining with a new membership ID cannot reactivate
old grants. The [membership lifecycle contract](./identity-access-employment-e1.md#membership-retirement-and-rejoining--concrete-e1-design-2026-10-04)
selects a new membership ID on explicit rejoin, retaining the retired row and allowing
only one active org/account membership through a partial unique index. Retired IDs
cannot be reactivated; no grant-generation field is needed. Concrete migration,
legacy-writer compatibility and constraint evidence remain readiness checks.

Organization app suspension is different: toggling organization_applications.enabled
retains the same valid membership/grants. Re-enable resumes only those still valid.
Explicit grant revocation sets revoked_at; regrant clears it only through authorized
provisioning with current membership validation, expected revision and immutable audit.
Neither app enablement, a new person link nor employment creates grants automatically.

E1 controlled provisioning registers `pts`, `leave` and a distinct synthetic reference
app when required. Map the existing three PtS capabilities to PtS; Leave uses exact
`leave.request.own.read` and `leave.request.own.manage`. Reference capabilities are
separately named by its fixture contract, never borrowed from PtS. Public Scribeswell
requires no Access app/grant row for anonymous reading. Directory's PtS-based menu rule
remains presentation metadata under ADR-0047. Future protected account-scoped features
get their own constrained grant contract; no nullable-org shortcut is introduced now.

Global/org enablement and grant mutations require an authorized owner-controlled
command, expected revision where updating, reason and atomic minimal audit plus operation
outcome. They are not exposed as generic public CRUD by table generation. E2 supplies
administration screens and delegated role mutation contracts. Membership changes stay
with Identity; do not pretend an Access transaction atomically changes another owner.

### Query and privilege boundaries

- `/v1/check` and `/v2/check` share current admission evaluation for the permission's
  registered app: globally enabled, organization enabled, current account/profile and
  exact active membership-bound grant. V2 employee checks additionally enforce verified
  person/actor setup. Preserve v1 wire fields/error family; global/org disable must not
  be bypassed by using the old endpoint. No automatic permission renaming.
- `/v2/organizations` evaluates the same conditions for at least one explicit capability
  of the requested app, without requiring an employee/person mapping. Its identity
  projection supplies authorized membership ID and display name. `/v2/applications`
  returns distinct app IDs with an eligible organization, not a grant or employee list.
- Keep organization tables under forced org-scoped RLS and restricted runtime SELECT;
  no runtime DDL or grant-administration privileges. Global application/permission
  tables need explicit read-only registry privileges for Access, not fake org scope.
  Provisioning/migrator privileges remain separate.
- Pre-selection discovery needs an Identity-owned caller-scoped projection and an
  Access-owned constrained query/routine for grants and organization enablement across
  that caller's memberships. Never disable tenant RLS or give the ordinary check path
  unrestricted cross-org reads. Before delivery, specify actual routine signatures,
  execution roles, safe search paths and grants, and prove wrong/missing/spoofed context
  cannot expose another user's memberships. The query is not complete from table shape
  alone; the existing selected-org bridge is insufficient.
- Validate registry IDs and capability mappings during deployment/provisioning. The
  existing small-catalogue discovery limit remains an explicit configuration bound to
  choose and test before readiness; no silent result truncation.

### Calling-service policy is separate server configuration

Use a closed, validated service-policy configuration mapping a credential identity to
allowed endpoints, explicit application selectors and exact capability IDs. Secrets
are injected through the existing secret/configuration mechanism and compared without
logging them; policy contains credential references, not plaintext keys committed to
source or stored as grant rows. Reject unknown service identities/operations by default.

Leave may check the two Leave capabilities and request Leave organization discovery;
Directory may request application discovery but cannot check arbitrary employee actions.
People's caller policy is selected with its exact read contract. PtS/Content retain only
the explicit PtS operations their supported consumers need. The synthetic reference app
has a separate fixture identity/capabilities. No service credential replaces an end-user
bearer or allows arbitrary account impersonation, and no service grants itself authority
merely by calling over a private network. No generic service-key administration UI,
credential-rotation subsystem or unused worker permissions is added to E1.

### Compatible adoption and evidence

1. Create the registry/organization admission structures in an additive Access migration.
   Verify and populate known permission mappings; unknown existing rows stop adoption
   for explicit disposition rather than silently receiving a guessed app.
2. Backfill membership bindings only for verified exact current org/account matches.
   Retain unmatched/revoked rows as ineffective evidence or resolve them deliberately;
   do not grant access to make migration pass. Add new columns initially compatibly,
   then enforce final required shape only after supported old/new writer verification.
3. Seed PtS global/org enablement deliberately for the intended read-only cohort before
   activating admission-aware consumers. Leave stays disabled until explicitly provisioned.
   Preserve old account UUIDs where practical; allowed manual recreation follows E1-ID.
4. Replace the fixed PtS-only permission CHECK with the explicit registry FK once known
   rows are mapped. Read compatibility does not prove old provisioning writers remain
   compatible; update and test those commands before stricter binding constraints.
5. Coordinate Access, Directory and protected consumers before declaring disable effective.
   An older running Access binary ignores the new enablement columns: either prove a
   supported compatible rollout or use the already-approved planned maintenance path.
   Do not claim the new controls are enforced during a mixed-version gap.

Required schema/contract fixtures: missing registry/org enablement; enabled org without
grant; grant without membership; changed membership binding/rejoin; revoked grant then
app re-enable; same person with separate account grants; unknown permission mapping;
service credential asking for another app; discovery outage; old/new API and provisioning
compatibility; restricted-role direct reads and connection reuse. Verify mutation/audit/
outcome atomicity and safe recovery. Link E1-ENTRY-02/03/05/06/10 and E1-AC-13/15/17/18.

Scaffold impact: explicit registry/client configuration, safe error contracts and owned
migration fixtures promoted with first consumers. Shared UI remains the already-agreed
selector/launcher; no new screen now. Existing agent instructions/ADRs apply. Membership
lifecycle, concrete discovery privilege design, audit schema and rollout rehearsal remain
readiness inputs. No tables, credentials, grants or runtime services changed here.

## Restricted discovery database contract — 2026-10-04

This specifies E1-DISCOVERY's narrow pre-selection path under ADR-0017/0018. It does
not grant Leave, People, Directory or browsers direct Identity-table access. Access's
existing Identity-owner integration is extended explicitly; this is not a general
cross-owner database access pattern. Physical routines are maintained by their owner
histories, with no imports of another service's runtime implementation.

### Verified caller and transaction scope

Access authenticates its calling service and checks that service's explicit discovery
policy, then verifies the end-user bearer through the supported authentication path.
There is no HTTP user/account/person-ID override. Only that verification supplies the
Auth account UUID. Before issuing discovery SQL, Access starts a short read transaction
and sets `app.account_id` transaction-locally on the same connection. Do not reuse
`app.actor_id` ambiguously: membership is account-specific even when two accounts map
to the same person. No selected organization is required at this stage.

Missing, empty or malformed account context is rejected by the discovery routine; it
is never interpreted as “all accounts.” Set context for every transaction and reject
connection/session defaults. Clear by commit/rollback and prove pool reuse. A valid
account with no active memberships has no organization results, but may still have
account-scoped application results. A missing/deactivated account
profile denies protected discovery under the shared error contract; no profile is
created implicitly. Missing person/employment setup alone does not suppress membership.
Provider verification occurs before the database transaction, not under database locks.

The backend is trusted to set verified identity, as ADR-0018 explicitly states. A
runtime credential capable of supplying arbitrary SQL/context is not independently
authenticated as an end user by a PostgreSQL setting. Do not claim that a caller-set
UUID, a SECURITY DEFINER routine or RLS protects against compromise of Access itself.
Untrusted HTTP input cannot set this context; test spoofing at the HTTP boundary, and
missing/malformed context plus privilege/row restrictions at the database boundary.
No JWT verification scheme inside PostgreSQL or new signed-context service is required.

### Owner-maintained routine interfaces

Proposed SQL interface names (internal, not browser APIs):

| Routine | Parameters | Returned columns / responsibility |
| --- | --- | --- |
| `identity.current_account_memberships()` | None; verified transaction account context only | `org_id uuid`, `org_name text`, `membership_id bigint`; active profile, nonretired organization and active membership belonging to that account. No email, role, person, employee or arbitrary account selector. |
| `access.discover_organizations(app_id text, after_org_id uuid, page_size integer)` | Validated explicit registered app; nullable keyset position; size 1–100 | Same three columns for currently admitted organizations, ordered by org UUID. Evaluate global/org enablement, exact membership-bound nonrevoked grant and permission-to-app registry association before pagination. Determine next-page presence with an internal extra matching row; never paginate raw memberships then silently drop eligible results. |
| `access.discover_applications()` | None; verified transaction account context only | Unique `app_id text`, `eligible_scope_kinds text[]`, ordered by app ID, from qualifying account or organization entry capabilities. Canonical refinement below defines the aggregate; no organization names or membership IDs. |

The Identity projection supplies membership facts only; Access applies admission rules.
Public HTTP wrappers still enforce service policy and validated cursor/selector schemas;
they serialize bigint membership IDs as decimal strings and return private/no-store.
Opaque HTTP cursors encode validated position only, never authority. Each page rechecks
current state; no frozen-list promise or positive authorization cache. Discovering an
app/organization does not authorize a later business action. App-list limits use the
small registered catalogue validation bound; choose its exact deployment value before
readiness and fail configuration rather than truncate successful discovery.

Execute each Access result query as one statement joining the Identity projection to
current Access facts, so a page does not combine separate reads of admission/grants.
No per-organization HTTP call loop and no employment lookup. Normal subsequent changes
can invalidate a displayed result; selection and protected requests recheck authority.

### Privilege layout to implement and verify

- `access_runtime` retains the existing selected-organization check permissions and
  receives EXECUTE only on the two Access discovery routines, not cross-organization
  table SELECT or membership in their owner roles.
- Use dedicated NOLOGIN, nonsuperuser, NOBYPASSRLS routine-owner roles, separate from
  table owners/migrators. The Access discovery owner receives only the required Access
  registry/grant/admission column reads and EXECUTE on the Identity projection.
  The Identity projection owner receives only required Identity profile/member/org
  column reads. Runtime cannot SET ROLE into either owner or redefine the routines.
- Explicit RLS policies for these owners restrict Identity to the current account's
  active membership set; Access grant rows to current account and exact active membership
  binding; organization admission rows to that same authorized membership set. Global
  registry reads contain no people. Preserve the ordinary runtime's selected-org RLS;
  do not add a broad permissive runtime policy or temporarily turn row security off.
  Avoid recursive policy dependencies: Identity projection does not query Access, while
  Access's discovery policies may use the Identity projection.
- Fixed SECURITY DEFINER routines use fully qualified object references and a safe
  `search_path` excluding schemas writable by untrusted callers, with `pg_temp` last.
  No dynamic SQL assembled from selector/cursor values, writes, external calls or
  transaction control inside these read routines. Use bound typed arguments.
- Revoke default PUBLIC EXECUTE in the same migration transaction that creates each
  routine; grant only to the stated consumer role. Remove unintended anon/authenticated
  or inherited grants, and deny CREATE on their owning schemas to runtime consumers.
  Routines must not become callable Data API RPCs merely because a schema is exposed.
- Create/grant each routine in its owning history; coordinated deployment orders Identity
  projection before Access discovery. Verify actual owner-role privileges/RLS on the
  pinned PostgreSQL version rather than relying on table-owner test connections.

PostgreSQL's [CREATE FUNCTION security guidance](https://www.postgresql.org/docs/17/sql-createfunction.html#SQL-CREATEFUNCTION-SECURITY)
requires care with definer search paths and default PUBLIC execution. This informs the
privilege design; it does not verify this repository's future routines.

### Acceptance and outstanding technical evidence

Verify two distinct accounts (including two accounts linked to one person), organizations
with and without app enablement, retired/rejoined memberships, stale grants, disabled
profiles, missing person links, multiple pages and revoke-between-pages. Verify raw
user/account headers/query fields cannot override bearer identity; invalid service keys
and disallowed selectors cannot reach discovery. Missing/malformed DB context must fail,
while legitimate empty membership remains a successful empty result.

With actual restricted roles, test unauthorized direct SELECT, forbidden SET ROLE/DDL,
unauthorized routine execution, temporary-object shadowing and pooled connection reuse
after success/error/rollback. Validate final membership/grant filters and compare app-list
and organization-list admission results. Loss of a dependency yields unavailable, never
an empty success. Record EXPLAIN/query timing at the agreed fixture sizes as delivery
evidence without claiming unmeasured capacity now.

This resolves the interface and intended privilege boundary. Exact SQL policies/role
creation, migration grants, statement timeout, configured catalogue bound, compatibility
and concurrency fixtures still need implementation-readiness validation. Scaffold:
promote proven scoped-read/error fixtures with the owning service, not a universal
cross-tenant query helper. Shared UI and agent instructions unchanged. Link E1-DISCOVERY,
E1-ACCESS, E1-LAUNCHER and E1-AC-13/15/17/18. No runtime code, roles or migrations changed.


## Account-scoped PtS refinement — 2026-10-06

Account admission evaluates global app enablement, current account and exact account
grant, with no organization join. Directory discovery unions independently evaluated
account apps with eligible organization apps; zero memberships must not suppress PtS.
The Scribeswell menu rule consumes this PtS result. `/v2/organizations` remains for
organization apps and must not invent a PtS organization.

Define a separately constrained Access-owned account-grant model and typed check scope;
do not simply remove org_id from the existing organization check or allow ambiguous
nullable fields. Identity/person/actor evidence is selected for actual consumer needs;
PtS requires no employment or fake person setup merely to read. Service caller policy,
revocation, safe errors and no-store/current-authority requirements apply to both scopes.

Controlled provisioning must support exact account grant/revoke with revision, replay
and audit safeguards, separate from membership-bound commands. Explicitly provision
intended PtS users; do not union legacy org grants into global account authority.
The legacy v1 response contract may be replaced through the coordinated transition.
Inventory PtS and Content consumers and define corpus/resource scope before finalizing
schemas, story size or activation steps. Runtime enforcement and safe release gates remain.


## Capability-scope contract refinement — 2026-10-06

ADR-0053 replaces exclusive per-app scope with a registered required scope on each
capability. Earlier `{app_id, scope_kind}` discovery rows and the corresponding SQL
routine result are provisional and insufficient for a mixed-scope application; revise
them together before implementation rather than return duplicate app entries or label
an entire app with whichever scope was found first. Final typed entry/context projection
and explicit eligible entry-capability mapping remain required contracts.

Account grant commands target exact account/capability, with no membership ID;
organization commands retain exact organization/account/membership/capability. Reject
scope/capability mismatch in provisioning and checks. A current user can have either
or both without automatic inheritance. Registry association and scope changes require
explicit adoption; do not reinterpret existing grants silently.

ACCESS-B should prove one synthetic mixed-scope app through both typed variants, using
real owner grants and current checks. This tests platform scope dispatch without adding
future PtS organization features. PtS read/export/Content corpus scope remains a separate
unresolved resource contract; account admission alone is not resource authorization.
Global disable covers both variants; organization disable affects only its organization
capabilities. Public Scribeswell has neither grant nor synthetic organization.


## Canonical discovery refinement — 2026-10-06

`GET /v2/applications` requires Directory's restricted service identity and the current
user bearer. No selected org or arbitrary account selector. It returns:

```json
{"applications":[{"app_id":"pts","eligible_scope_kinds":["account"]}],"checked_at":"<UTC RFC3339>"}
```

`eligible_scope_kinds` is a nonempty unique array in canonical account, organization
order, drawn only from currently eligible entry capabilities. One app row even when
both scopes qualify. An eligible organization variant means at least one authorized
organization, not all organizations. No org IDs/counts, permission lists, person data or
grant evidence leak through this aggregate. The restricted SQL discovery routine returns
the same projection; account eligibility must not depend on the membership query having
rows. No result cap may silently truncate eligible apps; the deployment catalogue bound
remains to set before readiness.

Declare an explicit Access-owned set of entry capabilities for each app, validated
against its capability registry; no inference that any internal/admin capability opens
the app. E1 entry mappings: PtS `pts.poetry.read`; Leave `leave.request.own.read`.
Exact reference-app entry IDs remain part of its fixture contract. Manage/export alone
does not imply read or a launcher entry. Scoped direct actions still check their own
capability even when the app is omitted from the launcher.

Directory intersects eligible apps with published catalogue entries, keeping the
existing public AppEntry presentation format. It adds Scribeswell only when PtS's
eligible scopes include account, per ADR-0053; an organization-only synthetic PtS
fixture must not trigger that rule. Public reading remains independent. No bearer,
invalid bearer and unavailable Access retain the already agreed distinct outcomes.

The app's canonical landing route rechecks current eligibility as needed: account
features require no organization selection; organization features request only their
eligible contexts at entry. Do not encode a grant or forced selected organization in
catalogue links. This contract defines no future PtS organization landing screen.

`GET /v2/organizations?application=leave` retains keyset pagination over organizations
with a current eligible organization entry capability. A registered app with no
organization entry capabilities yields an empty list to an allowed caller; it must not
invent an organization for an account-only app. Unregistered/disallowed selectors retain
safe validation/service-policy errors. Selection never authorizes the later action.

Scaffold: generate both closed check variants and array discovery projection together;
update server adapters, SQL routine models and frontend/client fixtures in their owners.
Do not implement a generic policy expression engine. Tests cover zero memberships,
either/both scopes, duplicate-free discovery, scope mismatch, no cross-scope inheritance,
no unauthorized org details, missing entry capability, revocation and dependency failure.
The existing 3-second Access/5-second Directory budgets remain unchanged.

This is a concrete technical design under accepted decisions, not implemented wire
compatibility. Actor projection, account-grant DDL/commands, bounded catalogue values
and PtS corpus/Content resource transition still require closure before readiness.


## Individual grant persistence and administration — 2026-10-07

Concrete E1 technical design under ADR-0052/0053. Access owns both grant variants;
this adds no second authorization service or account-administration UI.

| Owner table | Purpose / required shape |
| --- | --- |
| `access.account_grants` (new) | One row per `(account_id UUID, permission text)`; stable `id UUID`, `revision bigint > 0`, nullable `revoked_at`, server-managed UTC creation/update times and verified actor references. No org_id, membership_id or employment reference. |
| `access.grants` (existing organization model) | Retains non-null organization and exact account/membership binding, registered organization capability and existing legacy adoption/attribution mapping. No account-grant rows in this table. |
| `access.permissions` | Registered application and immutable required scope. Enforce scope-correct references from both grant tables, not only API validation. |

DDL direction: registry has an appropriate unique `(permission, scope_kind)` key.
Each grant table carries a fixed constrained scope discriminator and a composite FK to
that key (`account` in account_grants; `organization` in grants). Runtime cannot choose
the other discriminator. This permits ordinary database constraints to reject a Leave
organization capability in an account grant. Validate migration against existing rows
before replacing legacy constraints; no silent capability scope reassignment.

Account IDs are Identity/Auth external references, verified through the approved owner
contract; do not add a cross-owner table FK or match by email. Stable account IDs, not
person IDs, own individual grants. Linking two accounts to one person does not union
their grants. Recreating an account with a new ID requires deliberate provisioning.
Account deactivation makes retained grants ineffective; reactivation permits only those
still nonrevoked and otherwise valid. App disable also suspends rather than deletes.

### Commands and evidence

Use Access-owned `account_grant.assign` and `account_grant.revoke`, distinct from the
existing membership-bound `grant.assign/revoke`. They use the existing controlled
operator envelope with **platform** scope and exact account/capability target; the scope
here describes operator authority, not a new application capability. Restricted platform
operators/automation must be authorized for that command/app/account target. Ordinary
users, organization administrators and runtime service keys cannot administer account
grants solely through their existing membership or reader authority.

Assignment creates only on explicit expected absence, or deliberately regrants against
the current row revision; it verifies a current valid target account and account-scoped
registered capability. New grants start at revision 1. Revocation requires the exact
grant ID/account/capability and revision, marks revoked_at and increments revision; it
can revoke an existing grant for a now-inactive account. No row deletion or automatic
regrant from employment, membership, app enablement or sign-in. Identical desired state
may return unchanged after expected-state validation, with no fictitious change event.

All commands bind immutable input/expected state and authenticated executor to the
existing operation identity/fingerprint. Changed-input retry fails. A committed retry
returns its original compact result after current operator authorization; it does not
repeat the mutation. A delayed previously uncommitted revoke at revision 2 cannot erase
a deliberate regrant at revision 4. Revision numbers on the wire are decimal strings.
Change, revision, minimal immutable audit and compact outcome commit together; no new
fingerprint/key-rotation policy or duplicated audit on ordinary permission reads.

### Enforcement and fixtures

Account-grant reads use verified account context and forced account-scoped RLS with
restricted SELECT runtime privilege. Organization-grant checks retain org isolation and
membership binding. Provider verification/external account validation occur outside local
write locks. Operator writes use the explicitly restricted owner writer, not runtime or
migrator credentials. Select actual grants/routine security paths and prove them against
real restricted roles; a setting supplied by a trusted API is not independent end-user
authentication by the database. Pool reuse, missing context and arbitrary HTTP account
selectors cannot expose another account's rows. Discovery unions only eligible entry
capabilities; no broad user-grant listing endpoint is introduced.

Required fixtures: zero-membership PtS grant; independently granted read/export/documents;
organization capability rejected by account table and vice versa; same person/two accounts;
duplicate/concurrent assignment; revoke/regrant/stale revoke/replay; account deactivation
and new-ID recreation; organization removal leaving account grant effective; app disable
and re-enable with a separately revoked grant; runtime write denial and connection reuse.
Use explicit PtS cohort grants, never an automatic union of legacy organization grants.

ACCESS-A owns schema/operator evidence; ACCESS-B owns effective permission decisions;
PTS-ADOPT supplies actual consumer transition. Exact column/constraint names, audited
command models/bounds, operator adapter and baseline mapping remain migration/readiness
inputs. Existing owner-local evidence layout is reused. No app code, DDL, grants or tests
were executed. Scaffold fixtures/typed variants and owner docs change with delivery;
no new shared UI or agent rule, and accepted ADRs remain unchanged.


## Initial service caller matrix — proposed 2026-10-08

Refines the closed service-policy configuration for ACCESS-B; separate from end-user
grants. No service may request arbitrary checks merely because the user has a grant.
All listed user checks also require the current user bearer; a service identity is not
an account selector. Unknown caller/endpoint/application/capability combinations fail.

| Authenticated service | Allowed Access operations in this increment |
| --- | --- |
| Leave API | `/v2/check` for `leave.request.own.read` and `leave.request.own.manage`; `/v2/organizations` for `leave`. |
| PtS API | `/v2/check` for `pts.poetry.read`, `pts.poetry.export`, `pts.poetry.documents`, each account-scoped. No organization selector needed for current PtS. |
| Directory | `/v2/applications` for the authenticated user's eligible app projection. No arbitrary `/v2/check` permission or provisioning rights. |
| Reference API | `/v2/check` only for explicitly registered reference capabilities; `/v2/organizations` only for its own app. No Leave/PtS grant borrowing. |
| People | No Leave capability check proposed. Enforce its own authorized calling-service, verified current user/person and organization-scoped own-employment boundary. Exact identity-context verification wire remains a pre-story contract. |
| Content | No end-user Access call in the new private-read path. The application checks domain/user permission; Content enforces its own restricted calling-service and stored ownership policy under ADR-0054/0055. |

**People correction — 2026-10-08:** the user challenged the proposed Leave-specific
check. Withdraw that recommendation; it was not an accepted ADR. Leave calls Access to
check its own application admission/capability. People authenticates the calling service
and checks that it is allowed to perform this own-employment read, with verified current
user/person and organization context. It returns only that person's permitted employment
fields in that organization; no arbitrary person override or employee-directory access.
People must not contain `leave.request.*` rules or gain new permission names whenever a
consumer such as Travel is introduced. New consumers still need explicit service policy.

This retains the existing identity contract's independent service/user/scope checks;
it does not authorize trusting raw person/org headers, accepting a stale Access decision
as a reusable token, or inferring authority from employment existence. Define the exact
current identity/context verification and allowed service/scope wire before readiness;
no new endpoint or universal service key is selected here. The application owns its
business permission decision; People owns protection of shared employment data. The
corrected boundary was approved by the user on 2026-10-08; its verification wire
is proposed below/in the Identity contract, not an implemented security guarantee.

The reference's exact capability IDs remain a registry contract to settle; the matrix
does not authorize a prefix wildcard. Credentials are separately provisioned per service
and environment, never browser-visible or copied into fixture manifests. The test runner
signs in as test users and calls application routes; it receives no universal service key.

Acceptance: unrelated valid service plus valid user is rejected; Leave cannot check PtS
permissions; Directory cannot perform action checks; People rejects unauthorized service/scope and
other-person requests without querying Leave permissions;
Content's old duplicate end-user check is removed only with its coordinated consumer
adoption. Safe integration errors must not falsely tell a user their grant was revoked.

Impacts: ACCESS-B owns validated caller configuration and typed fixtures; each consuming
story adopts its narrow policy. Shared scaffold promotes proven server-only credential
wiring; shared UI/agent context need no new mechanism. Existing ADRs remain unchanged.
Exact credential binding, reference identifiers, limits and rollout evidence remain
readiness inputs. No credentials, grants, deployment or application code changed.


People context wire proposal — 2026-10-08: [Identity contract](./identity-access-employment-e1.md#people-current-identity-context--proposed-2026-10-08)
adds a proposed People-only `/v2/identity/organization-context` operation to this matrix.
It verifies current account/person/organization membership and grants no application
capability. People retains its own incoming-service/own-data policy; Leave retains its
application checks. This wire is for discussion and is not implemented.


Initial reference IDs selected — 2026-10-08: application `reference`, organization
capabilities `reference.record.read` and `reference.record.create`; entry uses read only.
Reference service caller policy lists these exact IDs and organization discovery for
`reference`, without wildcard authority. See [owning reference contract](./platform-verification-app.md#initial-reference-capability-identifiers--2026-10-08).
This resolves the initial create/read identifier gap in earlier passages; mixed-scope
Access fixture identifiers and the remaining readiness contracts remain separate.
