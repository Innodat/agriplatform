# ADR-0103: Fixed Minute Rounding and Plain Policy Language

**Status:** Accepted  
**Date:** 2026-09-22  
**Scope:** Entitlement rounding and policy-editor explanations  
**Supersedes:** ADR-0026's selectable down/nearest/up rounding

## Decision

Remove user-selectable prorated-grant rounding. Use full calculation precision,
then round usable entitlement down to whole minutes at the defined final boundary.
Preserve fractional remainders across related cumulative accrual portions; never
truncate individual daily portions or repeatedly round an intermediate result.
For a standalone prorated grant, round once at the final amount: 240.7 calculated
minutes gives 240 usable minutes. Do not add an advanced setting or planned
minute-rounding customization without an actual requirement.

Retain the established daily/monthly cumulative rules and cap-before-rounding
behavior; this does not change request increments or schedule-based half days.
Existing historical calculation snapshots retain their recorded rule. The new
convention does not authorize rewriting historical grants.

Policy editing uses plain-language labels and concise contextual examples. Prefer
'Leave per year' with an explanation that this is the full-year allowance, not the
current balance. Explain upfront availability as 'Available at the start of the
leave year'. Explain proration through the decision the administrator is making:
'If someone joins or leaves partway through a period', with choices to adjust for
time employed or give the full period allowance.

Show a short example beside unfamiliar consequential settings, with more detail
expandable. Core explanations must not require hover, a glossary or an external
search. Examples explain the selected policy, are illustrative rather than legal
or client defaults, and do not imply that daily earning allows disabling its
eligible-day calculation. Keep the rounding convention out of the normal form.

## Consequences

- Acceptance: final 240.5/240.7-minute prorated amounts both yield 240; cumulative
  precision remains; no selectable rounding field or nearest/up execution path.
- Scaffold/shared UI: use existing help text and disclosure primitives; no runtime
  component promotion. Apply the plain-language pattern where proven useful.
- Agent context: existing plain-language UX and deterministic calculation rules suffice.
- Documentation: requirements/tracker/UX and policy-editor preview updated.
- ADR impact: supersedes ADR-0026's choice; accepted original remains unchanged.
- Planning only; no actual grants or production calculations changed.
