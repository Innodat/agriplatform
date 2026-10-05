# ADR-0121: Adopt Simple Draft Save-Failure Navigation

**Status:** Accepted  
**Date:** 2026-10-04  
**Supersedes in part:** [ADR-0075](./0075-single-draft-and-safe-close.md), only
save-failure exit presentation; single-draft scope and deliberate discard remain unchanged.

Leave adopts [platform ADR-0048](../../../../../platform/docs/architecture/decisions/0048-simple-draft-save-failure-navigation.md)
for Close, Escape/mobile Back and organization switching in employee draft editing.
Use the shared simple warning and Try again / Keep editing / Close anyway choices;
organization switching uses Stay / Switch anyway and still checks target access.
This replaces the failure-exit label Discard unsaved changes (and its switching variant).
Deliberate Discard draft remains a separate confirmed command. Submission safeguards,
autosave revision/lifecycle rules and the first delivery slice remain unchanged.

Scaffold/shared UI: prove shared handling in E1-D2/D3 and promote with the consumer.
Agent context: existing platform guidance applies. Documentation: feature, UX, draft
contract, acceptance mapping and planning references follow platform ADR-0048.
No application code or readiness gate completion is implied.
