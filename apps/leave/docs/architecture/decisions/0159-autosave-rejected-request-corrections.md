# ADR-0159: Autosave Rejected-Request Corrections

**Status:** Accepted  
**Date:** 2026-10-22  
**Scope:** Employee correction of an existing rejected request before resubmission  
**Complements:** [ADR-0009](./0009-resubmit-rejected-request.md),
[ADR-0123](./0123-inline-draft-save-failure-and-exit-confirmation.md) and
[ADR-0124](./0124-saving-conventions-by-workflow.md).

## Decision

Autosave unfinished corrections against the existing rejected request so the employee
can leave and return to saved edits. Preserve original submitted details, rejection and
decisions in history. Leave any separate new-application draft untouched; do not force
its completion or discard before editing a rejection. Start a fresh approval cycle
only on explicit Resubmit after current validation.

This is request-scoped correction input, not a second competing ordinary new-application
draft or a new lifecycle status. Saving edits neither reserves entitlement nor reopens
approval. Continue to show the historical rejected outcome until valid resubmission.
The ordinary new-application draft uniqueness scope remains unchanged.

Reuse current authorization, revision/editability and late-save/lifecycle protections,
lightweight input preservation and established autosave failure UX. A stale save cannot
rewrite submitted history, overwrite another revision or resurrect correction input
after resubmission. Resubmit closes the editable correction revision with its required
local effects; retries recover the original outcome. Preserve attachment association/
cleanup and current document permissions for corrected versus historical records.

## Remaining contracts and impacts

Bind correction payload/revision ownership, one current editable correction revision
per request, historical attachments and current edit associations, preservation/closure,
concurrent ordinary draft access and resubmission consistency. Do not invent a second
Drafts section, administrative draft system or promise survival of unsaved browser input.
Verify close/reopen saved corrections, ordinary draft isolation, immutable previous
submission/rejection, no reservation before Resubmit, current initial validation/new
cycle, stale/concurrent autosave versus resubmit and existing Retry/exit behavior.

Reuse proven request-form/autosave/revision/review/history patterns; promote generic gaps
with first consumer. Leave owns cycle/correction semantics. Update features, UX, spine,
Story 5.20, tracker/handoff and index. Existing agent instructions suffice. Accepted
predecessors unchanged. Contracts, final atomic coverage/order/agent sizing/readiness
remain open. No code, runtime tests, migrations, grants, deployment or implementation.
