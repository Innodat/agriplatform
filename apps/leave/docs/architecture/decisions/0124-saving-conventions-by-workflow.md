# ADR-0124: Adopt Saving Conventions by Workflow

**Status:** Accepted  
**Date:** 2026-10-05

Leave adopts [platform ADR-0051](../../../../../platform/docs/architecture/decisions/0051-saving-conventions-by-workflow.md).
Employee requests retain the agreed autosaved unfinished draft and explicit Submit request.
Use Draft saved for acknowledged current input and Close to leave. E1 supplies preservation;
E5 adds submission. No fake submission control or effects are introduced by E1.

Employee configuration, leave types/policies, schedules and routing use explicit whole-form
Save / Cancel, retaining existing review/confirmation for consequential changes. Do not
autosave a name/description separately within these forms. Simple personal preferences
apply immediately on separate surfaces. E2/E3 detail each form using this convention;
no additional administration draft system is required.

The first delivery slice, single-draft limit and platform ADR-0050 failure UX are unchanged.
Prove/promote shared behavior with the first consumer; Leave owns field and workflow meaning.
Update UX, stories, acceptance and scaffold guidance with existing agent safeguards. No
application code or readiness pass; earlier accepted decisions are unchanged.
