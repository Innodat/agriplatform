# ADR-0136: Same-Type Policy Replacement and Earned Entitlement

**Status:** Accepted  
**Date:** 2026-10-15  
**Scope:** Replacement of an employee's policy assignment

## Decision

For MVP, replacement changes the assigned policy governing the same leave type.
Assigning a different type is a separate assignment with its own entitlement history,
not a transfer. Cross-type entitlement migration is unsupported.

Preserve already-earned entitlement, original expiry and carry-over history. Apply new
earning rules only from permitted effective dates; do not reset available balance or
grant a second annual allowance. Use accepted daily/monthly/upfront timing and method-
transition rules, including per-employee boundaries. Review existing-request consequences
and apply [ADR-0128](./0128-accountable-request-impacts-of-administrative-changes.md).

Replacement cannot bypass [ADR-0133](./0133-used-policy-leave-year-basis-fixed-for-mvp.md),
[ADR-0134](./0134-used-policy-entitlement-source-fixed-for-mvp.md) or
[ADR-0135](./0135-no-balance-tracking-for-mvp.md): no leave-year-basis migration or
conversion between automatic, manual-only and untracked categories once used for MVP.
Independent types and initial assignments remain supported under their own rules.

## Consequences and verification

Bind exact supported policy identities/versions and assignment representation, date/
overlap/coordination guards and retained portion/provenance references before readiness.
This decision does not invent a new policy catalogue or silently convert the existing
versioned policy model. Existing employee overrides persist until explicitly changed
under ADR-0083; detailed compatibility and ending-assignment treatment remain contracts.

Verify same-type replacement, no cross-type balance transfer, preserved portions/expiry/
carry-over and historical requests, no duplicate annual grant/reset, permitted method/date
changes and denied category/basis migrations. Pair scoped API/database concurrency/review/
audit/notification tests with actual consumer integration before activation. Exact tests
and final sizing remain open; no runtime tests executed here.

Update requirements, spine, written review UX and Story 3.36 obligations. Scaffold/UI
reuse guarded assignment/review/version/notification patterns; Leave owns entitlement
effects. Existing agent context suffices. Accepted predecessors remain unchanged.
No implementation or readiness authorization.
