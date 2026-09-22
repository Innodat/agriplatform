# ADR-0110: Stable Order for Same-Day Balance Events

**Status:** Accepted  
**Date:** 2026-09-22  
**Complements:** ADR-0109 and existing transaction, idempotency and correction rules

## Decision

Retain an effective date and recorded time for balance changes, plus a stable
server-assigned sequence for otherwise same-effective-day user events. Automatic
start-of-day effects follow the existing boundary rules first. Other changes with
the same effective date follow their recorded sequence, not timestamp precision,
client clocks or arbitrary database row order.

Assign the sequence within the existing serialized employee/NGO balance mutation
transaction so it reflects the accepted order of changes. No global ordering across
unrelated employees or NGOs is required. Retries reuse the original recorded event
and sequence rather than introducing a new effect. Preserve explicit relationships
between the effects of one operation; sequencing does not split an atomic change.

Example: an authorized manager adds two days, then approves a request using them.
Replay applies the addition before the approval even if timestamps are identical.
The sequence is internal. User-facing history shows effective date, actor and
recorded time; existing reasons and context remain available.

A backdated change retains its actual recorded time and sequence while taking effect
on the selected date. Backdating still requires existing impact review and historical
correction safeguards. Sequencing must not rewrite original approval evidence or
silently authorize new request allocations. Corrections retain links to the records
they correct; this rule is a deterministic tie-breaker, not a replacement for domain
correction semantics or effective-dated policy selection.

## Impact and verification

- Acceptance: same-timestamp changes replay consistently; addition-before-approval;
  concurrent mutations follow accepted order; retries do not duplicate/reorder events;
  backdated changes preserve original evidence and follow impact-review rules.
- Scaffold/shared UI: Leave-specific event ordering; no new UI control or shared API.
- Agent context: existing transaction/history requirements suffice.
- Documentation: requirements and implementation tracker synchronized.
- ADR: additive; accepted predecessors unchanged.
- Planning only; no runtime, schema migration or production event changes.
