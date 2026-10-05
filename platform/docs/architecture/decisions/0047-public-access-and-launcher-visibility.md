# ADR-0047: Public Access and Launcher Visibility

**Status:** Accepted
**Date:** 2026-10-02
**Supersedes in part:** [ADR-0046](./0046-application-availability-and-access-scopes.md),
only automatic inclusion of public Scribeswell in the shared launcher and its public-entry
fallback during protected discovery outages. Other access/admission rules remain.

## Decision

Public reachability and personalized launcher visibility are separate decisions.
Scribeswell remains publicly readable at `scribeswell.com` without sign-in, organization
membership or an app grant. Do not include it automatically in the shared app menu.
Show its published catalogue entry only when a signed-in user currently has PtS access
in at least one qualifying organization. Other apps may confer visibility only through
an explicit future rule; do not infer that Leave access is sufficient.

Directory owns this explicit presentation rule, using the current PtS admission result
from Access. It creates no Scribeswell grant or fake membership. Represent it as narrow
catalogue visibility configuration, not a general cross-app authorization engine.
Access still owns all protected admission/capabilities. A launcher entry grants no
protected authority; omitting a public app does not prohibit its public direct URL.

Anonymous users have no Scribeswell entry in the shared launcher. Signed-in users with
no current PtS access also have none. On discovery failure, do not infer PtS access or
show Scribeswell as a fallback menu entry: preserve the explicit unavailable/Retry
presentation, even if the menu has no links. The separate public reader remains usable.
Revoking PtS hides its Scribeswell menu entry on the next current check but cannot revoke
anonymous reading at the public site. Existing account-cache isolation rules apply.

The rest of the shared launcher story remains agreed. No new signup, domain redirect,
protected Scribeswell feature or application administration screen is introduced.

## Impacts and acceptance

- Directory/client/UI: distinguish admission from catalogue visibility; no automatic
  public-app inclusion. Anonymous and signed-in non-PtS users get no Scribeswell link;
  PtS-authorized users do; expired/unavailable checks do not preserve stale eligibility.
- Direct access: anonymous Scribeswell works independently; Leave/PtS direct APIs still
  enforce their applicable permissions even if a launcher once listed them.
- Scaffold: optional explicit catalogue visibility rules with current Access evidence;
  no organization/employment requirement for public apps. Keep a usable error/Retry
  state when no links are available; an empty launcher must not hide a discovery fault.
- Tests/docs: update E1-LAUNCHER and discovery consumer fixtures; preserve keyboard,
  mobile, account-change and outage coverage. Agent context links this refinement.
- Accepted ADR-0046 remains immutable. No application code, access grant, production
  configuration or deployment changed by this decision.
