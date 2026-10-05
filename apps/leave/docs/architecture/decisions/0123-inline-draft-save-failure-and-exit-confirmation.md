# ADR-0123: Adopt Inline Draft Save Failure and Exit Confirmation

**Status:** Accepted  
**Date:** 2026-10-05  
**Supersedes in part:** [ADR-0121](./0121-simple-draft-save-failure-navigation.md), failure presentation only.

Leave adopts [platform ADR-0050](../../../../../platform/docs/architecture/decisions/0050-inline-draft-save-failure-and-exit-confirmation.md).
D2-B shows inline save failure with Retry while editing, with no Keep editing button.
Close/Escape/in-app mobile Back use Stay / Close anyway only when bounded saving cannot
be confirmed; D3 uses Stay / Switch anyway. Saved forms close without a prompt.

Existing single-draft, input-preservation, deliberate discard and submission rules remain.
Shared UI/scaffold mechanics are proven with D2-B/D3; Leave owns destinations and fields.
Update feature/UX/contract/acceptance references. Existing agent rules apply with the new
platform link; no code or readiness pass. Whether to retain Leave drafts is discussed
separately and is not changed by this failure-presentation decision.
