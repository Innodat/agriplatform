# ADR-0164: Initial On-Behalf Employee Scope

**Status:** Accepted  
**Date:** 2026-10-23  
**Scope:** Target employees for initial on-behalf submission  
**Resolves:** The target-scope gate in
[ADR-0149](./0149-standard-approver-includes-scoped-on-behalf-submission.md).

## Decision

The standard Approver role's explicit initial on-behalf capability targets employees for
whom the actor normally holds a configured required approval responsibility in the current
organization: supervisor direct reports and employees actually covered by an explicitly
configured final-approver responsibility. A final-role label alone does not grant all
employees or all policies. Recheck the actual selected employee/policy context at submission.

An explicitly authorized administrative on-behalf grant may target organization employees.
Leave Manager's existing organization-wide resource scope does not supply a missing action
capability. Custom roles may omit on-behalf; a submit-only custom role can hold it without
approval authority and cannot record a decision it lacks.

Temporary appointment alone supplies no on-behalf capability and does not widen its employee
population. Temporary/fallback absence routing and historical reporting relationships are
not the standard role's normal-population predicate. An independent current normal or
administrative on-behalf grant remains usable under its own scope.

Employee lookup and the protected command enforce the same scope. Lookup results grant
no continuing authority; current capability, source relationships and exact target/policy
scope are revalidated before commit. No per-employee allowlist editor or new role is needed.

Retain mandatory reason, employee versus submitter attribution, unchanged ordinary employee
draft, all submission gates, only actual authorized own automatic decisions and employee-only
initial unpaid response. This supplies no funding, document, correction, withdrawal or
approved cancellation right. E6 cancellation defaults remain separate.

## Verification and impacts

Verify current supervisor and actual configured-final populations, unrelated employee/type/
organization denial, current relationship change after lookup, custom omission/submit-only,
temporary-only denial and separate independent grant success. Verify actual target lookup
and command, not role-name mocks or UI-only filtering. No runtime test ran in planning.

Scaffold/shared UI reuse current scoped search/Access/typed error patterns; Leave owns the
population predicate. Agent context and platform policy unchanged. Documentation aligns
Features, spine, C5 typed scope/search/command models and original 5.12 mapping. Accepted
predecessors remain unchanged. No live grant, code, migration or readiness authorization.
