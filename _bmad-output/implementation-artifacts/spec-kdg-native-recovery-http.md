---
title: Native SELECT-only recovery HTTP qualification
type: feature
created: 2026-10-25
status: done
route: oneshot
baseline_commit: 0ce7b1c268eb5b0d995178970b5e87bc761aebc7
---

<frozen-after-approval>
## Intent
Qualify the explicit candidate recovery HTTP API against the exact retained local ledger0002 database using actual restricted runtime connections and the candidate's ordinary read-only pool. Access and ASGI requests stay synthetic. Prove original receipt, verified absence/discrimination/isolation, current denial/closed input before checkout, pool saturation with safe failure/recovery, exclusive overlapping leases and complete release/lifespan disposal. Preserve current evidence, data, Docker resources, concurrent work and approved dependencies including TypeScript7.0.2. No migrations, DML, seeds, provisioning, active API wiring, real accounts/Access, deployment, Leave/editor, pilot, fingerprints/HMAC or cleanup. Append source-bound success/failure receipts and report qualification limits.
</frozen-after-approval>

## Implementation Notes
- bmad-help [BD] Build selected for current handoff. Small qualification executable, focused harness tests and evidence; no intent gaps or persistent database effects, so oneshot route. User already authorized same-run resume/normal stop.
- Reuse capture_commit_fixture custody/provenance, prior qualify_operation_recovery retained identifiers/counts, and unmodified recovery_http.create_candidate. No old ledger-only inspector or prepare/migrate/seed command.
- Warm real pool with read-only identity checks to separate handshake from fresh authorization; never relax one-second observation freshness. ASGITransport requires explicit lifespan context for disposal. Restrict before/after checks to normal revision/counts/sentinel; no custom cluster/schema inventory.
- Scaffold/shared UI/agent context/ADR: no new reusable runtime behavior or decision; existing generated primitives stay unchanged and parity-checked. Documentation and source-bound evidence updated together.
- Preexisting dirty paths snapshotted privately at /tmp/kdg-native-http-before.json; owned paths only for commit.

- ATDD observed four explicit behavioral errors against the qualification stub. The native-failure assertion was tightened to the exact injected error so NotImplementedError cannot satisfy it accidentally. Final7 focused harness tests pass, including no success on preservation/source drift and source-bound safe CLI failure.
- Native initial11-group checkpoint passed; its append-only receipt remains historical. Review improvements then qualified12 groups including actual SELECT1/0 rollback/reuse. Both native runs changed no rows/schema/ledger; counts10/10/10 and sentinel retained.
- Final affected suite148PASS; three scaffold code/test parity checks pass. Original candidate/runtime/helper sources and previous source capsules unchanged. Access and ASGI remain synthetic; actual PostgreSQL runtime connections, pool waits/overlap/context/disposal were exercised.
- Twelve groups pass in final capture-commit-recovery-http-7f67806acf134f63b40ad4ad01ae69f2.json;6 observed physical connections across both candidates closed,2 overlapping physical connections distinct. No native edit receipt, TCP listener, real Access, native cancellation or server-drain claim.

## Review Triage Log
- medium / patch: post-execution-only source hashing could bind unrelated concurrent edits. Snapshot owning/candidate/custody sources before imports; check unchanged before and after execution, reject drift before success. Focused source-drift test passes.
- medium / patch: failed CLI receipts lacked source binding/stage. Record initial source hashes and safe stage with exception class only; CLI failure test proves credential canary absent.
- medium / patch: pooled-context check omitted app.mode. Native checkout now verifies org/account/actor/mode all unset/empty before every lease.
- medium / patch: foreign candidate physical disposal unobserved. Both engines now share physical-connection tracking, runtime/read-only/context checks and close assertions;6/6 closed.
- medium / patch: saturation failure never acquired a request lease, leaving native SQL rollback unproved. Added SELECT-only division-by-zero fault after checkout, safe503, zero outstanding leases and successful cleared-context reuse.
All five findings fixed; none deferred. Blind hunter ran; broader review layers skipped under oneshot.
