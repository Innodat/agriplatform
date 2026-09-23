# ADR-0034: Atomic Single-Active-Draft Creation

**Status:** Accepted  
**Date:** 2026-09-23  
**Scope:** Workflows whose domain rules permit one active draft per defined scope

## Decision

When an application permits only one active draft for a defined owner/workflow scope,
enforce that invariant in the database, not only through a frontend check or a prior
read. Atomically create an active draft or return the existing authorized active draft
for that scope. Concurrent initial creation must converge on the same draft identity.
The owning implementation selects appropriate database uniqueness/coordination within
its transaction and verifies the conflict path under actual concurrency.

Leave's scope is employee plus NGO for the employee application draft. Other workflows
define their own scope and may permit multiple drafts; this is not a global one-draft
limit, global cross-application draft table or generic workflow engine.

Returning an existing draft must never overwrite its values with a competing creation
payload. Preserve local entered values where practical and use the established review/
revision conflict flow if needed rather than merging automatically. The normal start
application action resumes the existing active draft with no duplicate-draft selector.
Recheck identity, NGO scope and resource permissions before returning its data.

Use stable operation identity for retries of a create operation. Returning an existing
active draft for a genuinely new start action is distinct from replaying an old create
operation after that draft was finalized/discarded: the latter follows its recorded
outcome and ADR-0033 lifecycle safeguards, never resurrecting a draft or attaching stale
payload to an unrelated new one. Subsequent updates carry the draft revision.

## Impact and verification

- Acceptance: two simultaneous initial creates yield one active draft; creation values
  do not overwrite the winner; distinct allowed scopes remain independent; denied
  access does not reveal a draft; retries after finalization cannot resurrect it.
- Scaffold: opt-in single-active-draft scope with database enforcement and conflict
  handling, explicit create/resume result and generated contract tests when implemented.
  Do not impose the pattern on applications allowing multiple drafts.
- Shared UI: reuse ordinary resume and conflict patterns; no extra chooser for Leave.
- Agent context: link the scoped, opt-in nature and database-enforced invariant.
- Documentation: builder/shared experience and Leave requirements/tracker synchronized.
- ADR: complements 0012, 0013 and 0033; accepted originals unchanged.
- Planning only; no database constraint, API or generator implemented.
