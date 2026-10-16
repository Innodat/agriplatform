# ADR-0141: Assignment Gaps and Resumption Without Duplicate Grants

**Status:** Accepted  
**Date:** 2026-10-15  
**Scope:** Reassigning the same leave type after a coverage gap

## Decision

Preserve previously earned entitlement and original expiry. Do not earn for dates without
assignment coverage. Resume under applicable rules from the new coverage date without
another upfront annual grant merely because of reassignment. Additional intended amounts
use separately authorized adjustment with existing reason/review/request-impact safeguards.

Ending coverage in March and restoring it in June does not refill the annual allowance
or earn for April/May. Retained balance does not itself authorize out-of-coverage requests.
If a gap was an administrative mistake, correct assignment history through authorized
reviewed correction, preserving original evidence and ADR-0128 safeguards. Do not disguise
correction as reassignment. Basis/category/cross-type restrictions remain under ADR-0133–0136.

## Consequences and verification

Exact monthly/upfront gap calculations require explicit examples before implementation.
This decision chooses no monthly proration formula, new availability date or restart grant.
Bind coverage boundaries, retained provenance and duplicate-grant detection across repeated
assignments, with coordination/review evidence. Test no gap earning/duplicate grant,
preserved expiry, independent request coverage, authorized adjustments and corrections,
repeated resumption/concurrency and real E5/E6 integration before activation.

Update features, spine, written UX, relevant earning/projection/assignment story contracts
and tracker/handoff. Reuse scoped interval/review/version/evidence/client scaffold/UI
patterns; Leave owns earning semantics. Existing agent context suffices. Accepted
predecessors unchanged; exact tests, final sizing and readiness remain open. No code,
runtime tests or implementation/readiness authorization.
