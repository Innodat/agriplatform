# ADR-0122: Lightweight Draft Compatibility and Setup

**Status:** Accepted  
**Date:** 2026-10-04  
**Scope:** Non-consequential employee draft preservation

## Decision

The user approved simplifying drafts: prevent invalid configuration at its owning
editor, allow unfinished input to be saved despite missing/invalid work timezone, and
permit obsolete draft choices to be cleared rather than maintaining elaborate draft
compatibility through releases. A saved draft is not an eligibility or submission result.

Validate timezone configuration at its source and prevent ordinary profile edits from
leaving affected employees without usable settings. Initial setup, import defects or
migration errors can still leave incomplete configuration. In that case, allow authorized
create/edit/save/reopen of bounded draft input and show a small setup notice where useful;
do not force a Contact your administrator step or make timezone setup a draft-save gate.
Block timezone-dependent calculation and submission until their required setup is valid.
The timezone is a Leave setting, not a value to erase from the employee's draft.

When current configuration definitively makes a saved selection unusable, clear only
that obsolete selection in the form and briefly explain that it needs choosing again.
For example, clear a retired/unavailable-for-new-use type or a no-longer-permitted mode;
do not guess a replacement or convert hours into days. Preserve independent entered
dates, notes and still-usable mode values. A dependency outage is not proof that a
selection is obsolete and must not trigger clearing. Incomplete/reversed typed dates
remain normal unfinished input, not a migration defect to erase. No whole-draft deletion
or clearing of submitted records follows from this decision.

Reads remain read-only. Clearing a selection becomes a normal bounded draft input
change, persisted only through the current revision/lifecycle/operation safeguards; do
not silently rewrite a record during GET or replay an old receipt as a new mutation.
Only show Saved after the cleared form state is acknowledged. Existing saved null/explicit
choices are not backfilled with initial defaults. A later explicit user type choice
follows normal mode rules; repair is not a new request and does not reset defaults.

Current account/app/membership/capability checks, correct employee ownership, structural
bounds, attribution and revision/lifecycle protection remain mandatory. This decision
does not grant access, invent an employee or relax confirmed ended-employment read-only
behavior. If effective employment cannot be established solely because timezone setup
is unavailable, do not fabricate current/ended eligibility or use it to block simple
preservation; eligibility remains unknown and consequential actions stay blocked.
Missing employment/identity is still a scope/setup problem, distinct from a missing
calculation setting. Required authorization/identity-service outages do not fail open.

## Consequences

- Replaces earlier planning-contract requirements that missing/invalid timezone block
  draft mutations, and that obsolete type/mode selections must always be retained.
  ADR-0067's no-reservation, truthful persistence and submission revalidation remain.
  Accepted earlier ADR files are unchanged.
- E1 need not implement complete work-profile version selection or configuration-to-save
  locking merely to preserve draft values. Resolve those contracts before dependent
  calculations, employment eligibility interpretation and consequential workflows.
- E1 still reads enough shared identity/employment context to establish ownership and
  honors definite lifecycle/access restrictions. Reconcile optional dated interpretation
  with the minimal response schema before readiness; do not invent an implicit UTC date.
- Tests: missing/invalid timezone with successful authorized save/reopen; blocked previews/
  submission; obsolete selection clearing with notice and revision-safe save; dependency
  outage preserves selection; independent dates/notes survive; no cross-user writes.
- Scaffold/shared UI: reuse simple draft status/field-reset notice where proven; Leave
  owns what is obsolete and which fields can be cleared. No generic migration engine.
- Agent guidance: existing authority, scope and no-resurrection rules apply.
- Documentation: product, UX, draft/configuration contracts and tracker follow this rule.
- No code, data clearing, migration or readiness approval is performed by this ADR.
