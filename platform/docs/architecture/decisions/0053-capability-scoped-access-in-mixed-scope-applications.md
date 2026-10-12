# ADR-0053: Capability-Scoped Access in Mixed-Scope Applications

**Status:** Accepted — user agreement 2026-10-06; implementation contracts pending
**Date:** 2026-10-06
**Scope:** Shared Access, Directory, application contracts and scaffolding
**Supersedes in part:** [ADR-0052](./0052-pts-account-scoped-access-and-coordinated-adoption.md)
only its whole-app account-scope characterization of PtS; current PtS capabilities remain
account-scoped and its coordinated adoption decision remains binding. Refines
[ADR-0046](./0046-application-availability-and-access-scopes.md)'s application-scope model.
Accepted predecessors remain unchanged.

## Decision

Declare the required scope for each protected capability. One application may offer
both account-scoped and organization-scoped capabilities. Scope is registered policy,
not something a caller can choose to obtain an easier authorization path.

- Account capability: require current authenticated account, global application
  availability and the exact account grant. No organization membership or employment.
- Organization capability: additionally require the exact organization context,
  organization application enablement, current membership and applicable scoped grant.
  An account grant is not an organization grant or an extra prerequisite for every
  organization action. Apply each action's independent domain/resource rules.
- Use explicit typed request/decision variants. Reject missing organization for an
  organization capability and mismatched scope; never fall back to an account check
  after organization denial. An account capability cannot authorize reading an
  organization-owned resource merely because both belong to the same application.
- Global app disable stops new checks for all its protected capabilities. Organization
  disable or membership removal affects that organization's capabilities, not independent
  account grants. Existing current-access/in-flight rules remain binding.
- Current PtS capabilities use individual access. Future PtS organization features
  require their own explicit capabilities and delivery contracts. A user can enter
  individual PtS features without selecting an organization; organization context is
  requested only for a feature that requires it. Do not implement those future features now.
- Scribeswell remains organization-independent: public reading now, account-scoped
  personal features only if separately delivered. Leave remains organization-scoped.
  No synthetic organization, employee or automatic cross-scope grant.

## Discovery and navigation

Directory may list a published protected application when the user has a currently
eligible entry capability through either applicable scope, without duplicating the app
entry. Entry capability rules must be explicit; a random internal/admin permission is
not automatically a navigable app entry. Menu eligibility never authorizes a later action.
An application entry must not force organization selection for an account-only route.
Organization features discover/select only eligible contexts and recheck direct actions.

Current Scribeswell menu eligibility continues to depend on current PtS account access
under ADR-0052, not future unspecified PtS organization permissions. Any expansion of
that presentation rule requires an explicit decision. Public reading is unaffected.

## Contracts, evidence and impacts

Access's capability registry binds each capability to one application and one required
scope. Do not encode one exclusive authorization scope on the application registry.
Keep separately constrained grant variants and current actor/resource evidence; do not
make organization RLS nullable. Capability identifiers cannot be silently reassigned to
a different scope: use explicit versioned adoption or a new identifier with consumer
migration where needed. Exact schema, discovery projection and API variants remain
pre-story design work; this decision is not their implementation.

Required fixtures: a zero-membership PtS account; independent Leave organization access;
an app fixture with account and organization capabilities; account grant cannot satisfy
organization action; organization grant cannot satisfy account action; wrong/missing
scope; organization disable leaves independent account access; global disable denies
both; discovery emits one app entry and returns no inaccessible organization details.
Mixed-scope fixtures prove platform behavior without inventing future PtS product features.

ACCESS-A owns registry/grant constraints and controlled provisioning; ACCESS-B owns
scope-specific current checks and coordinated adoption; DISCOVERY/LAUNCHER own eligible
entry/context presentation. Scaffold generates explicit capability contracts and optional
organization navigation, not a mandatory application-wide organization selector.
Shared UI promotes proven patterns at first use. Agent context and owning docs link this
ADR. Reassess prerequisite sizing after PtS resource/Content transition is concrete.
No new public signup, HR suite, implementation, deployment or readiness approval.
