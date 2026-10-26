# ADR-0167: Approved and Pending Team Availability

**Status:** Accepted  
**Date:** 2026-10-24  
**Scope:** E5 request-review team availability, Story 5.17  
**Complements:** [ADR-0166](./0166-current-team-for-approval-availability.md),
[ADR-0125](./0125-supervisor-based-teams-for-mvp.md)

## Decision

Include approved absences and distinctly marked pending submitted/in-approval requests
when comparing the requested dates against the current permitted team. Pending requests
represent proposed absence, not confirmed leave. Keep the distinction in the API and
accessible presentation rather than depending only on colour.

Exclude unsent drafts and rejected, withdrawn or cancelled requests. Exclude the request
under review from its own colleague comparison. Current request lifecycle and current
submitted cycle determine inclusion; an earlier rejection or intermediate step acceptance
must not overwrite that classification. Closed/correcting input is not another pending
absence. All included rows still require current scope and actual date intersection.

Preserve ordinary colleague privacy: generic Unavailable/Part-day absence plus pending
status where applicable, without leave type, note, reason, comments or attachment metadata.
Detailed request identity/navigation is exposed only with actual detailed-request access.
This adds neither automatic capacity blocking nor authority from team membership or a
temporary appointment. Existing advisory panel failure behavior remains binding.

## Verification and impacts

5.17-A verifies approved versus both pending lifecycle codes, all excluded states/drafts,
self-exclusion, changed current cycle/state, date intersection and privacy-safe projection.
5.17-B renders approved/pending distinctions with accessible labels and consumes the same
query; no separate eligibility or capacity rule. Existing current-team/authorization and
source failure cases remain under ADR-0166 and their actual owners.

Scaffold: typed discriminated read projections and current authorized collection patterns.
Shared UI: existing availability panel/status labels, no new screen. Agent context: existing
rules suffice. Documentation: Features, read contract, spine and planning checkpoint.
Accepted predecessor ADRs unchanged. No implementation, runtime tests, migrations, grants
or readiness authorization.
