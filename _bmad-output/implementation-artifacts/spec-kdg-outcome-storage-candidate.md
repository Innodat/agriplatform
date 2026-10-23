---
title: 'Add inert KDG capture outcome storage and recovery candidate'
type: 'feature'
created: '2026-10-23'
status: 'done'
route: 'oneshot'
baseline_commit: 'fbd80f3793f7de589769768b0c581a506506f9af'
context:
  - '{project-root}/apps/kdg-capture/AGENTS.md'
  - '{project-root}/platform/docs/architecture/contracts/owned-write-and-secret-execution.md'
---

<frozen-after-approval reason="user requests the next bounded KDG outcome persistence/recovery step">

## Intent

Add a small inert app-owned capture outcome storage/recovery CODE candidate, using
the promoted verified transaction primitives. Existing ledger has no capture/history
tables, so do not apply a partial schema or claim persisted outcomes. Supply exact
scoped private SELECT and plain INSERT against the selected future operation_outcome
columns plus closed capture.create/edit v1 receipt/stored-row validation. No target_id
column is assumed: stored target comes from typed result.capture_id. Wire receipt is
exact operation_id/command_type/command_version/status/result:{capture_id,revision}.
Incoming/stored unknown versions and malformed rows fail closed, never become absent.

Use exact org/caller/handler-command/operation scope; caller must reuse the verified
transaction context. Missing rows return None only after successful scoped read, not
public unresolved/authority or rollback proof. Lookup is private storage discovery;
current stored-resource authorization precedes disclosure. Current own-read may recover
create outcomes after create permission removal, while POST retry still requires create
authority. This candidate does not implement either HTTP policy or replay orchestration.

Append requires a write mode, matching v1 receipt/key, original nonnil internal outcome
UUID and server/executor attribution. It does not begin/commit or upsert, return a
successful wire acknowledgement, retry a different operation, or replace prior result.
Future domain/evidence writes must share the same transaction and enforce local
constraints/linkage; lock/recheck is the caller's obligation. No generic callback engine.

Behavioral ATDD must observe an existing scoped outcome being missed before implementation;
focused TDD covers strict bounds/versions, exact bindings, attribution, deadline/errors,
duplicate/failed read distinction, no premature acknowledgement and original receipts.
Use only retained approved Python/SQLAlchemy/Pydantic and local managed helper, no
cross-owner runtime imports. No API startup, dependency or OpenAPI/client change.

Synthetic local/CI only; no DB/native/Docker work, migration/schema/role creation,
real accounts/access, Leave/editor, production, deployment/pilot/cleanup or fingerprints/
HMAC. Preserve concurrent work/history/resources and TS7.0.2. Actual DDL, RLS/FKs,
concurrent uniqueness, atomic capture/revision/outcome and release qualification remain
explicit gates. Story1.2 bootstrap retry/fingerprint contract remains unchanged.

</frozen-after-approval>

## Implementation Notes

Small reversible owner-internal candidate with no external surfaces or effects; oneshot.
No unresolved product intent: broader persistence/auth/linkage work is deliberately not
claimed or activated. Candidate lives outside dependency-minimal API startup under
write-candidate/operation_outcomes.py; tests under write-tests/test_operation_outcomes.py.
Keep private row models/SQL app-owned; reuse the existing managed helper unchanged.
Scaffold promotion is unnecessary for capture-specific DTOs/table/policies; shared UI,
agent context and ADRs unchanged. Update owner evidence/current handoff/contracts and
optional-test guidance; preserve prior document tails and all historical qualification.
Dirty-tree preservation already authorized; /tmp/kdg-outcome-candidate-before.json.


ATDD observed two genuine behavioral failures (missed existing outcome and absent INSERT)
before implementation; focused late-fetch TDD observed present/absent deadline failures.
Review regression observed identical internal/caller ID accepted before correction.
Final candidate suite:16 PASS; unchanged managed helper:26 PASS; KDG context:4 PASS;
managed parity PASS. No schema/API/native/dependency activation occurred.

## Review Triage Log

1. **medium — patch:** contract explicitly requires distinct internal and caller IDs;
   append accepted equality. Added rejection plus failing-then-passing regression and
   rejected malformed equal-ID stored rows on private read.
2. **medium — patch:** append docstring incorrectly placed all domain effects before
   outcome. Immediate revision/event FK requires outcome first. Corrected to reserve ID,
   applicable domain state, outcome, linked revision/evidence, one commit.
3. **medium — patch:** tests constructed fresh budgets within transactions, weakening
   deadline evidence. Each case now retains one budget; elapsed-work test proves 500ms
   remaining after9.5s and refusal at10s. Delayed fetch tests share that original budget.
4. **false — reject runtime conflict claim:** the alleged existing owner loader imports
   generated test support solely in test_owner_context.py; no runtime loader/consumer
   exists. Adapter is inert and no mounted owner receives those test classes. Documented
   candidate.write as supported helper identity and added second-import integration proof
   to make future consumption explicit without a custom class/context registry.
5. **low — patch:** generic SQL failure was covered but INSERT IntegrityError wasn't
   exercised concretely. Added duplicate-INSERT failure case with safe error, no following
   owner work/acknowledgement and synthetic enclosing transaction error exit. This is not
   actual database uniqueness/rollback proof.
6. **low — patch:** dense adapter checks impeded review. Expanded imports, loader,
   validators, scope comparisons and append into conventional readable formatting.

No deferred findings. Scaffold, shared UI, context, docs and ADR decisions are recorded
above and in owner evidence. Historical evidence is retained; all preexisting paths
remain present. Concurrent Leave/Scribeswell modifications are excluded from this item.
