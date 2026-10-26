# ADR-0149: Standard Approver Includes Scoped On-Behalf Submission

**Status:** Accepted  
**Date:** 2026-10-21  
**Scope:** Leave default-role capability composition for initial on-behalf submission  
**Complements:** [ADR-0007](./0007-required-approval-and-automatic-decisions.md) and
[ADR-0082](./0082-one-approver-role-with-workflow-steps.md); their separate capabilities,
assigned approval authority and self-approval rules remain binding.
**Platform authority:** [ADR-0011](../../../../../platform/docs/architecture/decisions/0011-application-roles-and-business-permissions.md).

## Decision

Include scoped initial on-behalf submission in the standard Approver role. This is
an explicit application-owned default capability grant, not a rule deriving submission
authority from any approval assignment or a role-name check. Custom approval-only roles
may omit the capability. A temporary appointment grants its specified approval
responsibilities, not on-behalf submission automatically; the actor needs a separate
current grant for that action.

Limit employee selection and the command to authorized organization/employee scope.
Bind exact target-scope resolution before readiness; do not infer organization-wide
submission authority merely from a configured final-step position. Keep required
reason, employee/actor attribution, unchanged employee draft, normal validation and
separate employee-only unpaid acknowledgement. Submission satisfies only the actor's
own otherwise authorized approval step and no other required decision.

This default covers initial submission, not automatic authority for on-behalf approved
cancellation/replacement, administrative corrections, funding grants/overrides or
medical-document access. Where an existing coarse capability spans those actions,
resolve narrower submission/default mappings before activation rather than broadening
the role beyond this decision. Leave Manager and medical-document defaults otherwise
stay unchanged. Existing custom-role grants do not silently expand.

## Impacts and verification

Verify standard default-role composition with scoped targets, custom approval-only
denial, temporary-only denial, separately granted temporary actor success, cross-scope
denial, no unrelated correction/funding/document permissions, required reason, unchanged
employee draft and automatic own-step/employee-response safeguards. Coordinate Leave
catalog, Access contracts/role versions, generated clients and setup examples before
affected readiness; do not change live roles/grants during planning.

Reuse existing role/capability/member scope UI and scaffold patterns; Leave owns catalog
and action checks, Access owns grants. Update features, spine, written UX, story/FLOW
traceability, tracker/handoff and index. Existing agent instructions suffice. Accepted
predecessors unchanged; no implementation/tests, migration, runtime grant, deployment
or readiness permission.
