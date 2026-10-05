# ADR-0046: Application Availability and Access Scopes

**Status:** Accepted — user agreements consolidated 2026-10-02; implementation contracts/readiness remain pending
**Date:** 2026-10-02
**Scope:** Platform application enablement, current access and launcher discovery
**Supersedes in part:** ADR-0011/0019 only insofar as their organization-membership
wording would otherwise require a tenant for all protected applications. Those requirements apply
where the protected application/action is organization-scoped. Account-scoped access
has no synthetic organization requirement. Accepted predecessor files remain unchanged; organization-scoped protections are
unchanged. Account-scoped protected actions still require current permissions.

## Context

The user requires configurable organization and user access to applications: PtS users
must not see Leave merely because they can sign in. The user also confirms Scribeswell
has no organization concept and its users need not belong to an organization.

Current `services/app-directory/routers/apps.py` returns all enabled catalogue entries
to every authenticated caller; context comes from JWT claims. This is discovery behavior,
not a current entitlement check. `/api/apps` is currently ungated despite its admin
label. Existing Access checks organization membership and explicit PtS grants; the
Leave v2 proposal lacks a distinct organization-application enablement check. These are
implementation gaps, not grounds to treat the existing behavior as the desired policy.

## Decision

Keep identity, application availability, organization membership and capability grants
separate. An account may exist without organization membership or employment.

- Catalogue publication describes deployed/discoverable apps and grants no authority.
  Keep display name, URL and icon with App Directory. Access owns global protected-app
  admission as well as organization enablement, so direct APIs enforce disablement.
- Access owns current organization-application enablement and user capability grants.
  For organization-scoped Leave, require global availability, organization enablement,
  current membership, and an effective required capability scoped to that organization.
  Enabling Leave for an organization does not grant it to every member automatically.
- Scribeswell reading is public without sign-in for now, as explicitly directed by
  the user on 2026-10-02. Sign-in currently adds no reader value and must not gate
  reading. No organization, default membership or fake employment is created.
- Future Scribeswell accounts may be created through public registration when that
  capability has a purpose and is explicitly delivered. Do not enable public signup
  for other applications or grant Leave/PtS access as a consequence.
- The user also wants selected applications, initially PtS, to confer Scribeswell
  access automatically. Model this as an explicit one-way Access-owned rule over
  current source-app access, not duplicated permanent grants, organization membership
  inheritance or a wildcard over future apps. Today this is redundant for public
  reading; implement derived protected capabilities only when defined. The exact
  future Scribeswell account capability remains a contract decision, not a grant of
  all future features. Revoking source access removes that derived entitlement unless
  another valid route grants it, but does not remove public reading.
- App Directory queries the current Access owner for discoverable applications instead
  of creating a second grant store or treating JWT roles as current authority. Include
  explicitly public entries such as Scribeswell for anonymous users; never fall back to
  showing protected entries when Access is unavailable. Globally
  disabled apps remain hidden. The global launcher shows an organization-scoped app
  only if at least one current organization context meets its admission requirements;
  that app then selects/rechecks an eligible organization. Account-scoped apps do not
  inherit the originating application's selected organization as an access prerequisite.
- An app hidden in the launcher must also reject unauthorized direct URLs/API actions.
  Each protected action rechecks its applicable current scope and domain permission;
  launcher results and copied links are never authority. Listing unavailability is not
  a successful empty result or permission revocation.

Use explicit typed scope variants in new contracts (`organization` with required
organization ID; `account` without it), and explicit public capabilities requiring
neither identity nor tenant context. Public reading is not a permission to mutate or
administer the service. Do not weaken all existing tenant tables/RLS by
making `org_id` nullable. Organization-owned business records stay organization-scoped;
account-scoped grants have an appropriately constrained owner model. Exact schemas,
permission catalog, revocation/disabling semantics and compatible migrations require
the owning pre-story contract. Existing v1 callers retain supported behavior during
transition; do not silently reinterpret old permission IDs.

## Administration and delivery scope

Platform administration controls global application availability and which organizations
may use an app. Authorized organization administrators assign reviewed application
roles/capabilities within enabled apps; they cannot enable an unavailable app or grant
across organizations. Future account-scoped grants and app-to-app entitlement rules have an authorized
platform owner; public self-registration is separately controlled. Exact delegated
capabilities and UI belong to shared access design.
No billing, subscriptions or new HR suite is implied.

For E1, owner-controlled fixture/provisioning configuration supplies organization
application enablement and explicit users/grants, plus the discovery/API checks. The
normal administration screens remain E2 shared access work. Do not postpone filtering
or direct-access enforcement until those screens exist. A disabled Leave catalogue
entry alone is insufficient once Leave is exposed to its first authorized users.

Required acceptance: PtS-only user sees no Leave; enabled organization without user
grant grants no Leave access; user grant in a disabled organization grants no access;
multiple organizations reveal only eligible Leave contexts; anonymous users can read
Scribeswell without membership; protected direct URLs still enforce grants; future
PtS-derived Scribeswell capabilities cannot grant reverse PtS/Leave access;
revocation/new execution, service failure and stale listing obey existing safeguards.
Keep read-only PtS/Scribeswell account transition bounded; no user-document migration.

Scaffold: default identity/access clients plus an explicit application scope selection;
organization selector and employment integration only for apps needing them. Shared UI:
current filtered AppLauncher and scoped administration controls, proven before promotion.
Agent context: add scope guidance after acceptance, not yet. Documentation: Access and
Directory contracts, Leave tracker and source mapping. ADR: accepted linked refinement
of [0011](./0011-application-roles-and-business-permissions.md) and
[0019](./0019-current-server-side-authorization.md); preserves
[0039](./0039-organization-neutral-tenancy.md) and
[0042](./0042-person-account-employment-and-legacy-adoption.md).
No implementation, grant changes, migration or production access performed.


## Hostname direction — user agreement, 2026-10-02

The user approved `scribeswell.com` for the public reader, `pts.boabab.com` for PtS
and `leave.boabab.com` for Leave, with no optional `scribeswell.boabab.com` redirect.
These are planned hostnames; domain ownership/DNS feasibility has not been verified
and no deployment is performed by recording this direction.

The current deployment documents place PtS at `scribeswell.com/` and the reader at
`scribeswell.com/scribeswell/`. The user clarified that the applications are not actively
used and existing users need not constrain this separation. Do not require a legacy
user/bookmark migration or old-route redirect project as a prerequisite. Configure and
verify the new canonical routes, catalogue links, provider callbacks, CORS, TLS and
release recovery when implementing the move. Preserve application data; lack of active
use does not require deleting it. This discussion does not authorize production changes.

### Application versus organization hostnames — user agreement, 2026-10-02

The user agreed to one hostname per app with explicit authorized organization selection:
`leave.boabab.com` serves all enabled organizations. Organization context can be part
of a validated route for deep links, resolved to stable `org_id`; exact path syntax
remains a routing contract. A hostname/path is context, never authorization. Check
current app enablement, membership, capability and resource scope on every action.

Organization hostnames such as `acme.boabab.com/leave` make sense if a branded client
portal across several apps becomes a concrete requirement. They add tenant-name
allocation/renaming, routing, certificate and authentication-origin considerations;
wildcard DNS can simplify DNS but does not remove those contracts. They are not an
E1 prerequisite. Keep existing multi-organization switching and generic app endpoints;
Scribeswell remains public and organization-independent under its own domain.

Scaffold impact: configured canonical app origin and safe organization routing; no
wildcard tenant-domain provisioning or branded portal generator for E1. Shared UI:
existing prominent organization selector, no new portal screen. Existing ownership
and current-authorization rules remain; no accepted ADR changed. This hostname agreement does not mark the remaining application-admission schemas
or implementation readiness complete.

[Microsoft's multitenant domain guidance](https://learn.microsoft.com/en-us/azure/architecture/guide/multitenant/considerations/domain-names)
describes tenant naming, wildcard DNS, routing and certificate trade-offs. The choice
of app hostnames here is a recommendation for this platform's current requirements.

Subdomains do not automatically share browser sessions. Use the shared authentication
provider with explicit allowed redirects and per-app session handling; do not spread
session cookies across all subdomains merely to create SSO. The detailed sign-in
contract remains separate from choosing branded URLs. No DNS, deployment, signup or
authorization configuration changed in this planning discussion.

References: [Google site-move guidance](https://developers.google.com/search/docs/crawling-indexing/site-move-with-url-changes)
for permanent URL mapping/redirects and [cookie scoping](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie)
for host/domain boundaries. These inform deployment planning, not domain availability.


## Agreed admission behavior and owning contract

[Application admission and discovery](../contracts/application-admission-and-discovery.md)
provides the wire design. The user agreed that disabling an app suspends access without
deleting drafts or configured grants; re-enabling resumes only still-valid access,
with that consequence disclosed by administration. Current membership, capabilities
and all other checks still apply. Existing bounded in-flight execution rules remain.

The user also agreed that unavailable protected discovery leaves public Scribeswell
available, with an explicit could-not-check state and Retry for protected apps. Never
mislabel that partial result as a complete entitlement list or access revocation.
These behaviors are accepted; exact schemas, migrations and executable compatibility
remain delivery gates. No production settings or application code changed.
