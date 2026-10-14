# ADR-0127: Default New Automatic Policies to Upfront Entitlement with Calendar-Day Proration

**Status:** Accepted
**Date:** 2026-10-13
**Scope:** Initial configuration of new automatic-entitlement policies
**Complements:** [ADR-0090](./0090-annual-entitlement-availability-options.md),
[ADR-0025](./0025-per-policy-calendar-day-proration.md),
[ADR-0104](./0104-monthly-partial-employment-default.md).
Accepted predecessors remain unchanged.

## Decision

For new automatic-entitlement policies, preselect:

- Availability: Available at the start of the leave year (upfront annual entitlement).
- Joining/leaving partway through a period: Adjust for time employed, using inclusive
  calendar-day proration under ADR-0025 and fixed final minute rounding under ADR-0103.

These are editable initial selections, not enforced organization rules or an automatic
publication/activation. Managers review and explicitly publish under the existing policy
configuration contract. Retain daily earning, monthly instalments and full-period allowance
as supported alternatives where applicable; manual-only grants remain a separate choice.
Monthly policies keep ADR-0104's adjustment default. Daily earning includes eligible dates
in its calculation and has no additional proration selector or second proration.

Apply the defaults to a new automatic configuration whose relevant settings have not
been explicitly chosen. Preserve existing policies, saved selections and explicitly
reviewed example-specific choices. Starter examples use these defaults where no different
reviewed automatic setting is specified; example content still requires manager review.
Do not convert manual-only/untracked concepts into automatic entitlement merely to apply
the defaults. No existing employee assignment, balance, grant or historical evidence changes.

This decision selects neither a universal annual amount nor period basis, cap, carry-over,
expiry or statutory/country allowance. Those remain separate configured choices. Upfront
availability follows the configured calendar-year/anniversary boundary. Joining/leaving
proration does not make entitlement accumulate daily: it determines the upfront amount.

## Rationale and retained safeguards

Upfront availability supports planning leave throughout the year with a clear annual
allowance. Calendar-day proration adjusts for partial-period employment independently
of work schedules. Daily earning remains available for organizations wanting progressive
availability; monthly instalments remain another supported policy choice.

An employee may use more than a later departure-adjusted allowance. Existing departure
recalculation, immutable history, protected-request acknowledgement and authorized deficit
review govern those consequences; approved leave is not automatically converted to unpaid.
The default creates no payroll/debt-recovery behavior or notification exemption.

## Impacts and verification

Update product requirements, written UX, architecture/default references, tracker and
E3 configuration/starter/calculation test traceability. Verify new automatic forms preselect
upfront plus adjustment, explicit alternative choices persist through review/publication,
existing policies remain unchanged, monthly defaults remain, daily mode has no double
proration, manual-only choices stay separate and publishing still needs current authority.
Calculation examples remain governed by existing accepted formulas and boundaries.

Scaffold: Leave-specific policy defaults do not belong in generic application generation.
Shared UI: existing conditional fields and explicit form/review controls suffice.
Agent context: existing instructions suffice. ADR impact: additive configuration default;
accepted predecessors are immutable. Final contracts, test mapping, agent sizing and BMAD
readiness remain open. Planning only; no Leave code, policy data, migration or deployment.
