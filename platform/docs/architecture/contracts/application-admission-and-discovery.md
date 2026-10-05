# Application admission and discovery contract proposal

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
For E1 it returns HTTP 200 `{applications: [{app_id, scope_kind}], checked_at}`.
Application IDs are registered strings, `scope_kind` is `organization` or `account`,
and `checked_at` is a UTC RFC 3339 timestamp. Return unique entries ordered by app ID.
E1 protected apps use organization scope; account-scope evaluation is introduced only
with an actual protected account capability. Public Scribeswell does not require a
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
| `access.applications` (new) | `app_id text` PK, `scope_kind text`, `enabled boolean`, `revision bigint` | Stable registered ID, independent of display name/URL. E1 supports `organization` protected admission; reject unsupported account-scope configuration rather than half-implementing it. Global enablement defaults false. |
| `access.permissions` (new) | `permission text` PK, `app_id text` FK to applications | Explicit immutable capability-to-app mapping. Preserve existing PtS identifiers; register exact Leave own-read/manage capabilities. No prefix matching, wildcard expansion or inferred manage-to-read implication. Do not reassign a used capability to another app. |
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
account with no active memberships returns an empty list. A missing/deactivated account
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
| `access.discover_applications()` | None; verified transaction account context only | Unique `app_id text`, `scope_kind text`, ordered by app ID, where at least one current membership-bound grant qualifies. No organization names or membership IDs in this response. |

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
