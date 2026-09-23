# Leave architecture consolidation — review resolution

23 September 2026. **Architecture consolidation complete; story planning may proceed.**
This is not an implementation-readiness, runtime-test or production-release approval.

## Deliverable and authority

The canonical [architecture spine](../../../../apps/leave/docs/architecture/ARCHITECTURE-SPINE.md)
contains thirteen adopted implementation rules, service/dependency shape, capability
mapping, operational targets and owned delivery prerequisites. Existing requirements,
UX and immutable ADRs remain authoritative. No duplicate specification was generated.

## Findings and dispositions

| Review | Outcome | Disposition |
| --- | --- | --- |
| [Requirements reconciliation](./reviews/reconcile-requirements.md) | Five stale wording groups and tracking cleanup | Corrected daily mode, removed rounding selection, aligned monthly periods, on-demand calculation and cumulative precision; retained auditable expiry/carry-over evidence |
| [UX reconciliation](./reviews/reconcile-ux.md) | One obsolete rounding-selector sentence | Corrected to fixed precision; checked actual spine against UX/privacy/recovery contracts |
| [Independent rubric](./reviews/review-rubric.md) | Pass; no semantic findings | Accepted; explicit delivery gates remain binding |
| [Independent adversarial review](./reviews/review-adversary.md) | Pass; no critical/high findings; optional cross-employee clarification | Added approval/coverage dependency protection to concurrency delivery gate |
| [Independent technology review](./reviews/review-technology.md) | One medium provider-feasibility prerequisite | Added known two-hour standard Supabase upload URL constraint to Content gate and tracker risks; prove fifteen-minute provider enforcement or obtain superseding decision before attachment story |

The provider prerequisite is explicitly deferred to its owner and affected story;
consolidation does not claim it has been implemented or experimentally resolved.
A browser timeout cannot substitute for provider capability expiry. Accepted ADRs
were not modified. All other unresolved technical mechanisms have owners and deadlines
in the spine; none is silently granted to independently built units to decide incompatibly.

## Verification

- `UV_CACHE_DIR=/tmp/leave-uv-cache uv run .agents/skills/bmad-architecture/scripts/lint_spine.py --workspace apps/leave/docs/architecture --output _bmad-output/planning-artifacts/architecture/architecture-leave-2026-09-20/reviews/lint-spine.json`: zero findings.
- Python local-link verification for the spine and newly added documentation links: passed.
- `git diff --check`: passed.
- Repository and official capability checks are recorded in [technology evidence](./reviews/technology-evidence.md).
- No application tests, provider experiments, migrations, deployments or browser accessibility tests were run for this documentation change.

## Delivery impact

Scaffold: inherited prove-then-promote requirements preserved; no generator changed.
Shared UI: existing design/experience contracts preserved; only stale UX wording fixed.
Agent context: existing root instructions remain sufficient; no new instruction required.
Documentation: canonical spine, source reconciliation, README and tracker synchronized.
ADRs: no new policy decisions or amendments to accepted records during consolidation.
The first authorized slice remains sign-in, NGO selection and draft save/resume, after
stories and the relevant Phase 1 readiness gates are complete.

## Follow-up validation: finalized content identity

The user supplied a separate High-reasoning validation finding and accepted the
recommended invariant on 23 September 2026. Platform ADR-0038 records fixed verified
byte identity, protected finalization and explicit replacement. AD-9, requirements,
Content delivery gate and scaffold guidance now reference it. The invariant is resolved;
provider enforcement remains a prerequisite before the first attachment story, alongside
the existing signed-upload lifetime proof. No runtime protection is claimed.
