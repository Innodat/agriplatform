# ADR-0148: Simple Retry for Uncertain Submission

**Status:** Accepted  
**Date:** 2026-10-21  
**Scope:** User-facing recovery of uncertain request submission  
**Supersedes in part:** [ADR-0087](./0087-return-to-my-leave-after-submission.md),
only its separate Check status action label.

## Decision

Use Retry for submission recovery, including uncertain outcomes. Internally resolve
the original operation first. Confirmed success returns its existing request; a
definitively uncommitted action may retry the same operation/payload under existing
current-authority and validation rules. While the result remains unknown, do not
issue a new submission or present failure/success as established. Explain We couldn't
confirm your submission. Please try again. Preserve the form while recovery is pending.

Retry is an explicit user action to complete the original submission, not permission
to submit changed input, auto-confirm a changed consequence, use a new operation ID
or bypass exact unpaid acknowledgement. Keep bounded recovery, duplicate protection,
session safeguards and return-to-My-Leave behavior. A failed list refresh is distinct
from failed submission. Exact statuses/wire/result retention remain pre-story contracts.

## Impacts and verification

Verify lost response after success, definitively uncommitted retry, unavailable outcome
lookup, repeated Retry and changed input/current authority without duplicates or false
claims. Reuse existing recovery/button/operation patterns; update Leave UX and affected
story/coverage/tracker/handoff. No new shared action label mandate or technical user
workflow. Existing agent instructions suffice; predecessors remain unchanged. No code,
tests, migration, deployment or implementation/readiness authorization.
