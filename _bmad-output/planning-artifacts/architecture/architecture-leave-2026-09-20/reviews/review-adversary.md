# Leave architecture adversarial gate

**Verdict: PASS for architecture consolidation, subject to the document's existing delivery gates.** No critical or high finding. This does not authorize implementation or certify that the deferred contracts are complete.

Reviewed `apps/leave/docs/architecture/ARCHITECTURE-SPINE.md`, its ownership and delivery gates, the requirements' approval/coverage section, and accepted Leave ADRs 0074, 0077–0082 and 0112. Review scope was whether separately built units could follow the binding decisions yet disagree materially about ownership, protected writes or shared data.

## Adversarial constructions

### 1. Approval writer versus coverage writer

Unit A finalizes leave under an employee-specific guard after checking a temporary approver. Unit B approves absence for that temporary approver under another employee's guard. If both assume a per-employee lock is sufficient for every invariant, A can commit against coverage that B concurrently invalidates.

This is a meaningful concurrency scenario, but **not an established gap in the binding contract**: AD-3 requires every related writer to participate and protection of related dependencies through commit, AD-7 independently checks coverage, and the concrete persistence/concurrency gate requires the shared protection mechanism and lock order before the affected mutation story. The requirements also explicitly preserve an existing leave approval if coverage becomes unavailable later and flag replacement rather than silently canceling leave. A compliant implementation must distinguish a concurrent stale validation from a subsequent valid change.

**Nonblocking strengthening:** explicitly include cross-employee approval/coverage dependencies in the concrete concurrency gate's examples. This improves visibility without selecting a new locking mechanism or adding scope. It must not be interpreted as permission to lock unrelated employees or whole NGOs.

### 2. Content cleanup versus Leave association

Unit A finalizes a file and later commits a Leave reference. Unit B's cleanup infers abandonment from missing Content-side confirmation and deletes it in the gap.

This pair would be incompatible but cannot both obey AD-9 and platform ADR-0030. Pending/confirmed association and cleanup coordination are already an explicit prerequisite for the attachment story. The spine deliberately does not choose the wire handshake now; separate teams cannot proceed independently until that gate is satisfied. No additional architecture decision is necessary.

### 3. Retry receiver versus outbox producer

Unit A removes terminal work after retention. Unit B removes duplicate evidence and accepts an old producer retry as new delivery.

AD-11 prevents that construction: original retry expiry is anchored to creation, receiver expiry checks remain after deduplication cleanup, and receiver evidence persists while unresolved. AD-10 separately fixes which owner is responsible before and after durable handover. Wire-level identity and acknowledgement details remain explicitly gated before delivery implementation.

### 4. Workflow snapshot versus live absence execution

Unit A treats the submission snapshot as prohibiting later absence-related routing changes. Unit B silently replaces workflow configuration with the latest policy when an approver goes on leave.

Neither interpretation is compliant. AD-7 inherits the approved appointment/absence rules; ADR-0081 and requirements distinguish preserved policy/completed decisions from execution of authorized absence and return conditions. They specify absence when approval is needed, outstanding-step restoration on return, and explicit temporary authority for the both-absent case. The earlier planning questions in ADR-0080 are not still-open product choices after ADR-0081. No new decision is needed.

### 5. Shared identity versus Leave employee settings

Unit A creates a separate editable person directory inside Leave; Unit B treats shared person identity as also owning Leave-specific schedules, employment rules and approval routing.

AD-1 rules out both ownership interpretations. The shared identity/access gate explicitly requires adoption of existing identity schema, allowed references and ownership before the first draft slice. It is legitimate to defer service placement and identifiers until that contract is completed; it would not be legitimate to begin the slice with competing implementations.

## Findings and disposition

- **Critical/high:** none.
- **Low, optional clarification:** name cross-employee coverage dependencies alongside configuration dependencies in the concurrency delivery gate. Suggested disposition: clarify the existing prerequisite, not create a new ADR or resolve physical locking prematurely.
- No demand for immediate schema, endpoint, provider or version decisions: these are explicitly assigned prerequisites with owners and deadlines.

The attempted divergent pairs either violate an existing binding invariant or cross an explicit readiness gate before its contract is resolved. No pair was found that is both fully compliant with the complete inherited contract and materially incompatible.
