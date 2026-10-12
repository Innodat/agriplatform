# ADR-0052: PtS Account-Scoped Access and Coordinated Adoption

**Status:** Accepted — explicit user direction; implementation readiness pending
**Date:** 2026-10-06
**Scope:** Access, PtS, Directory, Content integration and shared scaffolding
**Supersedes in part:** [ADR-0046](./0046-application-availability-and-access-scopes.md)
where its transition requirement would preserve legacy PtS caller contracts, and
[ADR-0047](./0047-public-access-and-launcher-visibility.md) where PtS-derived menu
visibility requires access through a qualifying organization. Accepted originals remain unchanged.

## Decision

PtS is a protected account-scoped application. Access is assigned to individuals;
no organization, membership, employment or organization selector is required. PtS
and its Access integration should adopt the platform being established, rather than
constraining it to the existing organization-based PtS API.

- Require verified current account, globally enabled PtS and the exact effective
  account-scoped capability. Sign-in alone grants nothing. Organization membership,
  organization app enablement and employment are not PtS admission prerequisites.
- Access owns typed account-scoped grants and current decisions. Keep their persistence
  boundary explicit; do not make all organization grant tables or RLS scopes nullable.
  Account grants cannot grant Leave access; Leave still requires enabled organization,
  current membership and the exact organization-scoped capability.
- Directory includes PtS from current account admission without enumerating memberships.
  The existing Scribeswell menu rule uses that current PtS account admission. Scribeswell
  stays public at its separate URL and is not an anonymous or outage menu fallback.
- Update PtS, Access and affected shared consumers together as needed. The legacy
  `/v1/check` shape and organization-based PtS grant semantics are not preservation
  requirements. Do not silently reinterpret an old organization grant as an account
  grant; explicitly provision intended individual capabilities. Existing exact PtS
  capability IDs may be retained if their action meaning remains correct.
- Rehearse a coordinated transition, using a planned maintenance window when required
  by ADR-0020, and remove obsolete callers/endpoints only after their consumers are
  accounted for. No obligation to build a permanent legacy compatibility layer.
  Existing permission checks remain in force until replacement activation; no interim
  bypass. Manual recreation of the small noncritical user cohort remains acceptable.

## Data and content boundary

Current PtS code requires an organization header and uses organization-scoped database
and Content records. That describes the legacy implementation, not the target user model.
Account-scoped admission does not mean that the shared poetry corpus becomes separately
owned by each account. It also does not authorize broadening Content access, removing
RLS, deleting records or introducing a synthetic user organization.

Before affected story readiness, inventory PtS read/export/content callers, define the
application corpus/resource authorization and storage-scope transition, and settle the
account check/grant schemas and current-actor evidence. Any retained internal legacy
partition must be server-controlled, unavailable as user-selected authority, and must
not require a PtS user's membership. Its acceptability and migration remain design
work, not a selected storage solution. No historical user-document migration is added.

## Acceptance and impacts

- Account with explicit PtS grant and zero memberships can use permitted PtS actions
  and sees PtS plus Scribeswell in the launcher. It cannot use Leave without independent
  organization-scoped authority.
- Account without PtS grant, revoked grant or disabled PtS cannot use protected PtS
  actions; service failure is unavailable, not allow or an empty successful discovery.
- Organization changes alone neither grant nor revoke independent PtS account access.
  Current account disable and app/capability revocation remain effective on new checks.
- Direct read/export/content paths enforce their actual resource rules; an old
  organization header, signed-in account or launcher result cannot bypass them.
- ACCESS-A adds account-grant provisioning; ACCESS-B proves account and organization
  scope variants and coordinated PtS adoption. DISCOVERY/LAUNCHER and Identity
  transition fixtures change accordingly. Reassess sizing once consumer inventory and
  corpus boundary are concrete; do not conceal a PtS rewrite inside a check endpoint.
- Scaffold: explicit app scope, optional organization selector/employment integration,
  typed clients and contract fixtures. Shared UI: PtS needs no organization selection.
  Agent context, owning application docs, contracts and Leave tracker link this decision.
  No new HR suite, public signup or Scribeswell protected feature is introduced.

Planning only. No code, live grants, data migration, deployment or readiness pass.
