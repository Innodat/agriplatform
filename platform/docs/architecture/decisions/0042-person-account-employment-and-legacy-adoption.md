# ADR-0042: Person, Account, Employment and Existing Identity Adoption

**Status:** Accepted  
**Date:** 2026-09-23  
**Scope:** Platform identity/access, shared employment and existing consumers

## Context

The user approved the recommendations from the existing identity and receipt/Expense
review. The existing shared identity schema provides useful organization, membership
and account identifiers, but does not yet implement the accepted shared access and
employment direction. Receipt/Expense is not in production. That permits deliberate
consolidation without authorizing loss of existing development data.

## Decision

Identity, verified account linking, organization membership, business-capability access
and person/service attribution are platform-wide contracts. Applications requiring
employment use the shared employment owner under ADR-0040/0041. Other applications,
administrators and service actors need not have employment records. Application
business settings and workflows remain with their application owners.

Represent a person independently of a login account. Permit shared employment for
people without login accounts, including onboarding and historical imports. Do not
manufacture authentication accounts to satisfy an employment foreign key. Linking an
account requires verified identity evidence and authorized handling; matching email
or a client-supplied employee ID is insufficient. Person creation, employment,
account linking, membership and application grants remain distinct operations.
Employment or account linking alone grants no access. Employee-only actions still
require that employee's authenticated participation; no proxy acknowledgement follows
from accountless support.

Use one enduring employment relationship per person per organization, retaining
separate employment periods across leaving and rejoining. Preserve historical
references and do not restore former access grants merely because someone returns.
A person may have employment in multiple organizations. Exact effective-period
constraints and API representations remain contract work.

Adopt the existing shared identity deliberately. Preserve existing organization,
membership and account identifiers where possible, with explicit mappings to person
and employment identities. Do not create a second Leave person directory. Do not
automatically infer employment from an account or a legacy `employee` role.

Align existing consumers with current authorization (ADR-0019/0021), business roles
(ADR-0011), server-managed attribution (ADR-0025), structural scope (ADR-0035) and
HTTP service boundaries. For Expense, clarify purchase subject versus capturing actor
before mapping authentication references to employment. Preserve provenance and
historical mappings. Migrate affected consumers with a shared change or retain an
explicitly tested compatible interface; the complete Expense transition need not
precede Leave's first draft slice.

Characterize existing behavior and establish verified migration baselines under
ADR-0015/0016/0020. Repair and isolate old test fixtures before relying on them.
No destructive reset, automatic data conversion, new migration runner or completed
runtime verification is authorized by this planning decision.

## Impact and verification

- Contracts: refine ADR-0040's person/account and employment-cardinality questions;
  preserve ADR-0041 optional assignment ownership. Service names and deployment
  packaging remain delivery choices.
- Acceptance: accountless employment; verified linking without new grants; independent
  organization relationships; retained rehire history; current revocation checks;
  preserved Expense subject/actor mappings and compatible supported consumers.
- Scaffold: typed shared clients, actor context, owned migrations and isolated
  compatibility/authorization tests accompany the first consuming implementation.
- Shared UI: E1 needs linked employee access, not an accountless HR console. E2 adds
  authorized shared administration; employee-only responses retain their safeguards.
- Agent context: link these platform-wide identity and employment distinctions.
- Documentation: owning contract, Leave requirements/tracker and epic map retain
  traceability to this decision and the consolidation review.
- ADR: additive refinement; accepted predecessors remain unchanged. No implementation
  readiness gate is closed by this acceptance.

## References

- [Shared employment](./0040-shared-employment-core-and-application-settings.md)
- [Optional shared assignments](./0041-shared-supervisor-department-and-location.md)
- [Existing identity/Expense review](../reviews/identity-expense-consolidation-2026-09-23.md)
- [E1 shared contract](../contracts/identity-access-employment-e1.md)
