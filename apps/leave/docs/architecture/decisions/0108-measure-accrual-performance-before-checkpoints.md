# ADR-0108: Measure Accrual Performance Before Adding Checkpoints

**Status:** Accepted  
**Date:** 2026-09-22  
**Complements:** ADR-0106 and ADR-0107

## Decision

Start with direct authoritative backend calculation from efficiently queried history.
Do not introduce a balance cache, accrual checkpoint mechanism or additional worker
for this purpose in the initial implementation. Test calculation performance against
realistic employee counts and several years of history before release. Define the
representative workload and acceptable response targets before the affected stories
are ready; this decision does not invent numerical targets or claim measured results.

If measurements show unacceptable cost, introduce rebuildable checkpoints to avoid
replaying all prior history. They remain derived intermediate results, never another
source of truth. Historical corrections invalidate affected checkpoints, including
later results dependent on the corrected history. Rebuild from authoritative inputs;
never use an invalid checkpoint to confirm a consequential change.

Existing fresh-data, transaction and historical-evidence requirements remain binding.
Decision snapshots are retained evidence, distinct from disposable performance
checkpoints. Notifications and other existing worker responsibilities are unaffected.

## Impact and verification

- Acceptance: direct calculation meets agreed representative workload targets before
  release; if checkpoints become necessary, verify equivalence with full replay and
  invalidation after historical corrections before relying on them.
- Scaffold/shared UI: Leave-specific calculation strategy; no new shared primitive.
- Agent context: no additional instruction needed.
- Documentation: requirements and implementation tracker synchronized.
- ADR: additive performance direction; accepted predecessors unchanged.
- Planning only; no performance benchmark or runtime implementation performed.
