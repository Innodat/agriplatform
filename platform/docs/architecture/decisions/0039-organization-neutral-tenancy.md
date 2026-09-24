# ADR-0039: Organization-Neutral Tenancy

**Status:** Accepted

**Date:** 2026-09-23

**Scope:** Platform, applications, shared services and scaffolding

## Decision

Use organization as the general tenant concept. The platform serves for-profit
organizations as well as NGOs and other organization types. NGO must not be the
generic entity name in new code, schemas, API contracts, permission scopes,
configuration or generated templates.

Use `Organization`/`organization` for descriptive names and the established `org`
abbreviation where consistent with existing contracts, including `org_id` and
`identity.org`. Use tenant for technical isolation terminology. An NGO is an
organization type or a client description, not a distinct tenancy mechanism.
This does not require an organization-type field or classification system unless
a concrete feature needs one.

Authentication, membership, employment and application permissions remain distinct.
Existing tenant isolation, authorization, audit, content and worker requirements
apply equally to every supported organization type. Do not infer permissions,
jurisdiction, leave rules or business structure from nonprofit/for-profit status.

Historical references to NGO in accepted ADRs retain their original wording and
mean the organization tenant where describing generic platform behavior. This
terminology clarification does not narrow their security requirements. Preserve
accepted ADRs; update active contracts and generated artifacts through their owners.
Any existing wire/schema identifier needing renaming requires compatibility and
migration planning under ADR-0020, not an unreviewed bulk rename.

## Impact and verification

- Scaffold: use organization-neutral models, APIs, examples and test fixtures;
  retain compatible existing `org_id` contracts and update owning templates.
- Acceptance: demonstrate identical tenant isolation and applicable authorization
  for nonprofit and for-profit organization fixtures without organization-type
  branches. No new permissions arise from the label.
- Shared UI: generic tenant controls use Organization; specific client names and
  accurate descriptions may still identify an NGO.
- Agent context: record this naming convention outside the managed AGENTS block.
- Documentation: active Leave planning interprets earlier NGO wording consistently.
- ADR: clarifies terminology across existing decisions; no security or ownership
  invariant is superseded. Accepted historical records remain unchanged.
- Planning only; no runtime identifier, database or deployed API was changed.
