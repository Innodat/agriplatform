---
title: 'Scribeswell caller custody handoff'
type: 'chore'
created: '2026-10-23'
status: 'done'
route: 'oneshot'
baseline_commit: 'c275df02e28daaffaa07981ad075879260bf59d9'
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

Close the next readiness contract: explain exactly what evidence connects the corpus tool's stable service actor, actual database login and permitted commands, using existing Identity-owner and Scribeswell contracts. Produce a readable app-owned preparation/handoff document with owners, required target/source/command/receipt provenance, ordering, conflict/unknown/rotation rules and acceptance scenarios. Link it from existing operational docs and derive the canonical handoff through bmad-spec.

This is a documentation delivery. Distinguish a specified preparation contract from executed preparation and implemented software. The current six-field custody input is a local expectation, not Identity verification; a copied compact receipt or digest alone cannot prove target/kind/key/provenance. Existing Identity CLI supports disposable KDG targets only. Do not add a verification API, cross-owner imports/table reads, Access implementation, actors, roles, credentials, grants, migrations, enforcement, imports or deployment. Actual live owner evidence, explicit target preparation and rehearsal remain gates. Preserve agreed UX, standalone account creation, separate Access/KDG/Leave/factory ownership and working-tree changes.

</frozen-after-approval>

## Implementation Notes

- BMAD step02 read-only investigation found an implemented registration/recovery owner contract but no general live actor-verification API. The bounded result is documentation, with no unresolved user-visible choice or irreversible action. User's yn authorizes this next contract step; prior instruction preserves the dirty tree.
- Implement `apps/scribeswell/docs/CORPUS_CALLER_PREPARATION.md`; link from `HOST_VALIDATION_PROFILES.md`, `CORPUS_CONTROLLER.md`, `MIGRATIONS.md`. Canonical corpus/brownfield/acceptance derive through bmad-spec without changing IDs or closing D1–D5.
- Sources: `services/access/IDENTITY-MIGRATIONS.md` registration/recovery and disposable target sections; `identity_operator.py` receipt; `identity_operator_input.py` strict command; `identity_operator_target.py` target bounds; `APPLICATION-REGISTER.md` owner preparation precedent; Scribeswell `release_profile.py`, `prepared_controller.py`, controller/operator/host docs; ADR0020/0023/0025/0056. Consume documented owner contracts only, never import their runtime implementation.
- Impact decisions: reuse existing owner handoff/release patterns; no new scaffold/factory/shared UI/agent-context/ADR. Only app documentation and canonical derivation change. No runtime ATDD/TDD red or PostgreSQL acceptance is claimed for documentation; validate source consistency, acceptance scenarios, links, canonical IDs/whitespace and protected source preservation. Independently review the bounded diff before local scoped commit; no push.

- Documentation verification: five scoped files pass local link/heading-anchor/whitespace checks; custody field table exactly matches the six fields in the unchanged release_profile.py AST. Existing Identity receipt/CLI source and immutable actor guards inspected; canonical11CAP/38ST and twenty distinct existing companion paths pass. All recorded source/dirty hashes unchanged. No runtime tests, database, image, provider or production operation run for this documentation change.

## Review Triage Log

Independent oneshot blind review returned five findings (18.251kB floor5), each checked before grouping; five distinct medium patches, no deferrals.

- R1 — medium/patch: owned0003 guard forbids changing actor_key/kind/preparation_evidence_ref; Identity retains unique immutable established keys. Native synthetic UUID rotation is not general live replacement support. Document compatibility limits and require a separate reviewed forward change for incompatible replacement; preserve old references/revisions.
- R2 — medium/patch: owned0003 requires caller-supplied strictly increasing revisions, while timestamps are server-owned. Replace server-revision implication with explicit new revision1 and expected-revision updates/overflow/no-op rules.
- R3 — medium/patch: draft has no atomic local preparation boundary. Specify one short owned transaction, serialization and protected before-state check before all four rows; retain actual concurrency/failure proof as a future qualification requirement.
- R4 — medium/patch: nonnil local attribution is not an execution binding. Require retained owner evidence connecting the real preparer actor, actual session/login/target and preparation run, independent of arbitrary supplied UUIDs.
- R5 — medium/patch: local mapping writes have no operation outcome API. Separate their acknowledgement-loss recovery from Identity operation lookup; require ended original session, intended/before/actual whole-state comparison and fail closed on partial/conflicting/unresolved state.

- Final document corrections resolve all five findings without runtime/source changes: explicit rotation compatibility gate, caller revisions, atomic bounded local mapping, session-bound preparation attribution and distinct local acknowledgement-loss recovery. Final source consistency/link/anchor/whitespace, six-field custody AST, canonical11CAP/38ST/20companions and recorded source/dirty hashes pass. No runtime tests run; earlier944/70 results belong to the previous delivery and are not new evidence here. No deferrals; actual owner preparation, bounded executor and rehearsal remain explicitly unimplemented gates.
