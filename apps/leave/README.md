# Leave application

Leave is in planning. Application implementation and migration tooling are not yet
authorized by the Phase 1 readiness gate. Product requirements live in
[features.md](./docs/features.md), delivery tracking in
[implementation-plan.md](./docs/implementation-plan.md), and accepted decisions in
the [ADR index](./docs/architecture/decisions/README.md).

## Architecture guide

The [architecture spine](./docs/architecture/ARCHITECTURE-SPINE.md) consolidates
accepted implementation boundaries, data and calculation rules, recovery targets,
and the contracts required before affected stories can start. It links existing
ADRs rather than replacing them. Story planning and the Phase 1 readiness gate
still govern implementation authorization.

## UX design handoff

The Leave UX contract is in [DESIGN.md](../../_bmad-output/planning-artifacts/ux-designs/ux-leave-2026-09-15/DESIGN.md)
and [EXPERIENCE.md](../../_bmad-output/planning-artifacts/ux-designs/ux-leave-2026-09-15/EXPERIENCE.md).
The [approved reference inventory](../../_bmad-output/planning-artifacts/ux-designs/ux-leave-2026-09-15/mockups/README.md)
separates current compositions from historical studies; the written contracts win
when a prototype simplifies an interaction. Review outcomes and source corrections
are tracked in the [resolution log](../../_bmad-output/planning-artifacts/ux-designs/ux-leave-2026-09-15/review-resolution.md).
Design approval does not establish browser accessibility or implementation readiness.

## Migration and opening-balance imports

MVP imports are consultant-operated. See the
[migration runbook](./docs/operations/migration-runbook.md) for source-balance
interpretation, validation, email approval, reconciliation, and the cutover checklist.
The runbook is a planning draft; executable tooling instructions will be added
when the import tool exists.
