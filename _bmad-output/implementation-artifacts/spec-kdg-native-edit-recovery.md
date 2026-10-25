---
title: Native stored-edit recovery over candidate HTTP
type: feature
created: 2026-10-25
status: done
route: dispatch
baseline_commit: 837e580409494d97a38546924ce850e8cd6c76ff
review_loop_iteration: 0
context:
  - apps/kdg-capture/docs/contracts.md
  - apps/kdg-capture/docs/NATIVE_RECOVERY_HTTP_EVIDENCE.md
  - platform/docs/development/migration-verification.md
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Recovery accepts edit receipts in synthetic tests, but native qualification currently covers only create receipts. There is no implemented edit writer; recovery evidence must not imply one exists.

**Approach:** Extend native qualification with an explicitly test-only, restricted-runtime stored-edit fixture on a fresh synthetic capture, then recover the committed edit through the unchanged candidate HTTP boundary. Prove the original operation's target and revision remain stable after another edit. This qualifies stored-edit recovery, not an edit API or its domain authorization.

## Boundaries & Constraints

**Always:** Reuse exact retained run `99b7231c-0a5b-4bdb-98e8-3329564c526a`, existing custody and applied0002 provenance. Journal fresh identities before writes. Seed fresh KDG parents; create through the actual runtime handler; edit only that new capture under the restricted runtime login. Reuse existing transactions/outcomes and PostgreSQL integrity. Independently verify after writer closure. Preserve historical rows/evidence, concurrent work, resources and TypeScript7.0.2. Retain new synthetic data and append-only attempt receipts. Stop the known run normally afterward if this delivery started it.

**Never:** Claim fixture edits qualify an edit API or authorization. No migration, provisioning, privilege expansion, schema/ledger inventory, cleanup, active startup, queue/editor/UI, Leave, real Auth/Access/accounts, production, deployment or pilot. Fingerprints/HMAC deferred.

## I/O & Edge-Case Matrix

| Scenario | Expected behavior |
|---|---|
| Fresh capture then stored edit revision2 | Runtime commit links capture, edit outcome and immutable revision; independent read agrees |
| Later fixture edit revision3 | Original edit GET still returns its original operation, capture and revision2 |
| Original create GET after edits | Original create receipt remains revision1 |
| Wrong discriminator or foreign account/configured organization | Scoped unresolved, no cross-scope existence disclosure |
| Current own-read denial | Safe403 before checkout; no receipt |
| Native write/read/preservation/source failure | No qualified success; retain safe failure stage, intended IDs and completed evidence |

</frozen-after-approval>

## Code Map

Under `apps/kdg-capture/`:

- `migrations/tests/qualify_capture_commit.py`: reuse Dataset/seed/actual create execution; avoid its complete mutating suite.
- `migrations/tests/capture_commit_fixture.py`: reuse exact custody, provenance, identities, engine, sentinel and receipts; no preparer.
- `migrations/tests/qualify_recovery_http.py`: reuse established pool/ASGI/MockTransport and response checks; preserve historical qualifier semantics.
- `write-candidate/operation_outcomes.py`, `write-tools/transaction_context.py`: scoped outcomes and bounded transactions.
- `migrations/candidates/0002_capture_storage.py`: existing runtime grants, attribution and deferred history links; unchanged.

## Tasks & Acceptance

**Execution** (paths under `apps/kdg-capture/`):

- [x] `write-tests/test_native_edit_recovery.py`: acceptance RED, focused fixture/receipt/journal/preservation/failure tests.
- [x] `migrations/tests/qualify_edit_recovery_http.py`: explicit retained-only CLI, fresh dataset, bounded fixture edits, independent storage oracle and recovery HTTP; safe append-only failure/success receipts.
- [x] `docs/NATIVE_EDIT_RECOVERY_EVIDENCE.md`, `docs/evidence/native-edit-recovery-20261025.json`, `docs/contracts.md`, `docs/next-session.md`: source-bound commands, results, traceability and remaining gates.

**Acceptance Criteria:**

- Given exact custody and already-applied0002, when qualification commits only its fresh dataset, then expected effects are one new capture, three outcomes and three immutable revisions, plus its fresh parents; prior business rows, sentinel and ledger are unchanged.
- Given the runtime writer has closed, when independent reads and candidate HTTP recover the original edit, then capture identity/revision, linked snapshots and compact DTO agree, including after revision3 exists.
- Given current own-read denial or scope mismatch, when recovery executes, then native isolation and safe errors hold with released leases.
- Given any native or evidence failure, when the command exits, then it records a safe failed attempt and never reports qualification success.

## Implementation Notes

User approved and continued on 2026-10-25. They also request skipping routine workflow halts when existing authorization is clear; retain actual permission boundaries and material intent gaps. Native fixture writes and normal resume/stop of the exact retained run are authorized by this approved intent. Preserve existing untracked migrations/tests/schema_fixture.py without reading/running/editing it.

Baseline `837e580409494d97a38546924ce850e8cd6c76ff`. bmad-help selects [BD] Build. Investigation found no edit writer: fixture transactions keep this slice focused on the existing reader. No code, Docker or DB action during planning. Concurrent dirty tree already authorized.

Route: no intent gaps; app-owned harness/tests/docs; native execution commits retained synthetic data, requiring dispatch's specification checkpoint. Scaffold/shared UI/agent-context/ADR impact: none expected; reuse existing primitives and keep fixture/domain assertions local. Reusable fixes must update owning templates/tests alongside the consumer. ADR-0020 activation/compatibility/recovery remains unqualified.

Parent independently verified native report digest/current source hashes, planned deltas and stable original edit identity. All matrix rows are covered by native revision2/revision3 exercises and the focused failure/preservation tests. 12 focused,170 affected and three scaffold parity checks pass. Historical handoff restored as exact suffix under the new current entry. Review and normal run stop remain pending.

## Spec Change Log

## Review Triage Log

- Blind1 medium / patch: the independent oracle compares history/outcome to each other, not journaled edit outcome_id. Check planned IDs explicitly.
- Blind2 medium / patch: original child_eligibility_ref and creator_membership_id are enforced by PostgreSQL but omitted from the independent fixture oracle. Add exact original checks.
- Blind3 medium / patch: creation time baseline starts at revision2, proving only preservation through edit3. Capture revision1 independently before edit2 and compare both transitions.
- Blind4 medium / patch: updated actor IDs are checked but updated_at is unobserved. Record/check server timestamps and compare actual changed edits with the preceding observation.
- Blind5 medium / patch: custody invokes repository dev.py/native_cli.py; current source manifest omits them. Include those executed custody dependencies.
- Blind6 low / patch: edit3 storage is verified, but HTTP checks only edit2/create. Add a latest edit3 GET after its commit; small direct extension.
- Blind7 medium / patch: read_storage rejection logic lacks malformed-row tests; orchestration mocks bypass it. Exercise the existing oracle using controlled rows, including immutable facts, journal IDs, revisions and attribution.
- Blind8 false: pending review/stop fields accurately describe an intermediate record; no stopped/review-complete claim exists. Final evidence will replace these fields with observed results before commit.
- Edge1 medium / patch: initial source reads/imports occur outside CLI error handling; an unreadable source can emit traceback and no safe attempt result. Wrap bootstrap and retain safe failure output/receipt when custody remains available, with a failure regression.
- Verification1 medium / patch (pre-verified gap): both purported target-guard cases fail the preceding object-identity guard. Mutate the actual planned object and assert the specific target failure before checkout.

Review capacity note: the third fresh reviewer spawn hit the thread limit; reused an independent completed reviewer thread for the verification lens with the new scoped diff and instructions. All three layers completed before triage.

## Verification

Use the pinned Python owner environment and Node26.11.1 recorded in NATIVE_RECOVERY_HTTP_EVIDENCE.md. Observe the smallest new unittest failure, run focused TDD and affected write tests, then existing write/database/native-database scaffold parity checks. Run SELECT-only native recovery checkpoints before/after. Verify original business rows, planned deltas, source hashes, sentinel and ordinary ledger revision. Retain all attempts; no cleanup. Blind review with individual triage precedes a scoped local commit. Record exact commands/results; doubles cannot establish native permission or commit visibility.

## Completion evidence

All nine accepted review findings patched and verified; one pending-field finding rejected as an accurate intermediate status. No deferrals. Final focused18/affected176 tests pass; scaffold parity3 remains passing. Reviewed-source native report d58241785ea94f8b9f040771e1acd635 and final SELECT-only report03a0e31a22dc43cba25ba9bc8342f4aa pass. Both native source versions and datasets remain retained: total capture12/outcome16/history16 and four parent rows per table. Each attempt added exactly one capture/three outcomes/three revisions plus five fresh parents. Creation attribution baseline is captured before edit2; both edits preserve it, and original edit receipt2 survives current revision3. The known run stopped normally. No application runtime, dependency or schema change; no edit API qualification. Ordinary workflow halts are skipped under the user's explicit instruction when authorization is clear.
