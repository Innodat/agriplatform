# ADR-0129: Allocate Equal-Expiry Entitlement by Oldest Source Period

**Status:** Accepted
**Date:** 2026-10-14
**Scope:** Deterministic entitlement allocation within a selected balance
**Complements:** [ADR-0020](./0020-earliest-expiry-entitlement-allocation.md).
Accepted predecessors remain unchanged.

## Decision

Keep earliest-expiry allocation for eligible entitlement, with non-expiring portions
last. Within equal expiry priority, use the oldest source leave period first, then a
stable deterministic portion-identity tie-break. The source period is the original
entitlement period, not the date of its latest carry-over. Preserve it through rollover.
Apply the same source-period ordering among eligible non-expiring portions.

This resolves the open equal-expiry business ordering agreed during Story 3.18.
It does not prioritize older entitlement ahead of earlier-expiring newer entitlement,
extend validity, restore excluded earning or make expired/not-yet-earned/already-reserved
portions usable. Annual allowance/carry-over limits remain separate. No automatic
cross-type borrowing or displacement of existing protected reservations.

Bind the concrete stable portion identity and historical reconstruction/source-period
representation before readiness. Equivalent calculations/retries must produce the same
allocation without relying on row arrival order, client clocks or regenerated unstable
identities. Exact API/schema design stays in the owning allocation contract.

## Impacts and verification

Update requirements/allocation contracts, architecture, written UX and Story 3.18's
source/test mapping. Verify equal expiry across original source periods, repeated
carry-over preserving origin, equal source-period stable final ties, non-expiring portions,
earlier-expiry priority over source age, invalid/reserved portions excluded and repeated
projection equality. E5 actual reservation/consumption writers consume the same ordering
with current inputs and atomicity; previews reserve nothing.

Scaffold: no generic entitlement-allocation engine. Shared UI: existing calculation
disclosures explain source portions; no new user choice/control. Agent context: existing
instructions suffice. ADR impact: additive resolution; immutable ADR-0020 unchanged.
No code, data, migrations or readiness permission; final contracts/tests/sizing remain open.
