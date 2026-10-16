---
title: 'ENV fresh-start volume admission and CLI branch proof'
type: 'feature'
created: '2026-10-16'
status: 'done'
baseline_commit: '0a7c2054eed50958ab003fb66d0f548c82260bc7'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '/home/ck/repos/innodat/agriplatform/AGENTS.md'
  - '/home/ck/repos/innodat/agriplatform/platform/deployment/DEVELOPMENT.md'
  - '/home/ck/repos/innodat/agriplatform/platform/deployment/fixtures/supabase-pg17-lifecycle.md'
  - '/home/ck/repos/innodat/agriplatform/platform/docs/architecture/contracts/scaffold-environment-and-generation.md'
---

<frozen-after-approval reason="standing user approval for bounded ENV implementation">

## Intent

**Problem:** resources.invocation pre-acquires the database volume. The pinned CLI records its existence before creation, so that ordering selects existing-volume behavior and skips fresh setup.

**Approach:** Make the existing guarded invocation constructor require observed volume absence and leave creation to the later CLI phase. Prove that phase through the existing private pinned-CLI fresh create/copy/refused-start fixture. Keep metadata resource acquisition separate and unchanged.

## Boundaries & Constraints

**Always:** Under existing qualified owner evidence/run lock/one connection/five-second daemon budget: verify version/images, require exact volume404 before resource mutations, acquire bridge, recheck images/bridge and exact volume absence before constructor; keep custody/idle/budget/post-owner checks. Existing volumes refuse as unsupported reuse before mutation; ambiguous inspection is not absence. CLI proof models truthful absent probe then exact synthetic volume creation, validated immutable PG request, in-memory root-key transfer and refused first start. Planned volume profile must be distinct from observed metadata. Preserve current acquisition and existing-volume controls, exact approved pins including TypeScript7.0.2, safe diagnostics and runtime_ready=false.

**Never:** Falsify an existing volume as absent; infer fresh contents from POST attempted/201/labels/no references; reserve resources or claim setup SQL executed. No real daemon/container/SQL/secret/infra/account/access/deployment actions, new generator/client/service/workflow, production migration or dependent Identity/Access/WRITE/KDG/Leave implementation. Accepted ADRs/concurrent documents stay preserved.

## I/O & Edge-Case Matrix

| Scenario | Input/state | Expected behavior | Failure |
| --- | --- | --- | --- |
| Absent constructor |404 initially/finally; valid images/bridge | Construct argv once; no volume POST; same connection | runtime false |
| Existing/ambiguous |200 existing/foreign or non200/non404 inspection | No constructor or earlier mutations | safe reuse/inspection refusal |
| Late appearance |404 then200 before handoff | Refuse, preserve acquired bridge, no cleanup/replay | safe reuse refusal |
| Continuity/custody | Loss, delay, changed source/target/receipt/lock | No unverified handoff/reconnect | established safe errors |
| Fresh CLI | Absent probe, exact synthetic volume ACK/create/copy | Preserve strict sequence; refuse start | safe facts only |
| Invalid fresh phase | Pre-acquired input, existing/racing volume, wrong/duplicate/reordered create/copy/start | Refuse before later phase; baseline validated for negative control | safe startup refusal |

</frozen-after-approval>

## Code Map

- `platform/deployment/resources.py`: change invocation only; reuse qualified_evidence/current/version/images/network algorithms. Keep acquire behavior. Extract private repeated network reobservation only if useful; exact existing tests characterize it.
- `platform/deployment/volumes.py`: narrow require-absence helper on caller session/current, fixed run name; no new daemon routes.
- `platform/deployment/startup.py`: install_fixture/fixture_command/lifecycle_prefix/validate_observations/synthetic_probe: explicit fresh fixture mode and planned volume profile, truthful initial missing result, exact ACK event before create, existing root-key validation and refused start. Preserve existing proof; no synthetic ACK asserts real freshness.
- `platform/deployment/tests/qualify_startup.py`: fresh control must bypass unconditional volumes.acquire and reject supplied pre-acquired input. Existing controls retain owner observation. Add positive fresh lifecycle and expected existing-volume refusal.
- `platform/deployment/tests/qualify_resources.py`: extend existing private peer/control oracle for fresh invocation constructor and absence/existing/error/late controls; no endpoint selector.
- `platform/deployment/tests/test_resources.py`, `test_volumes.py`, `test_startup_adapter.py`, `test_startup_lifecycle.py`: independent exact event/state oracles, source/transport and wrong-order tests. Extend current authorities profile/lifecycle docs, update SOURCES/FILES only for any new source authority.
- Pinned source753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4: start-database.ts134 volumeExists before create and189 fresh setup; container-lifecycle.ts ensureVolume/create/copy/start sequence.

## Tasks & Acceptance

- [x] Add outer acceptance failures for pre-acquisition/unsupported fresh CLI path; send root exact commands and WAIT for observed RED before production changes.
- [x] Implement fresh invocation admission and independent private fixture/public control coverage for every matrix row; preserve acquire and old exact proof.
- [x] Add pinned-CLI fresh branch create/copy/refused-start and negative baseline/order proof; no raw env/archive/body evidence.
- [x] Update existing profile/lifecycle authority docs; root owns runbook/evidence/navigation/memlog, five impacts and scoped local commit.

**Acceptance:** Given an absent target volume, when guarded initial invocation is constructed, then it remains absent for the CLI's own probe. Given an existing/ambiguous/late volume, when admission runs, then handoff refuses. Given the pinned CLI fresh fixture, when it runs, then exact volume-create ordering precedes immutable PG create/copy and refused start, without executing setup.

## Implementation Notes

No human intent gaps or irreversible actions. Root runs socket/port/public tests serially outside sandbox; implementer sends RED commands and waits, never requests escalation. Implementer owns code/tests/authority docs only. Root owns BMAD/evidence/runbook/qualification. Absence is a bounded observation, not reservation; execution-time rechecks, fresh DB setup/secret semantics, initialized reuse, real lifecycle and P1/SERVICE remain open.

## Spec Change Log

## Review Triage Log

| Finding | Verdict and evidence | Route |
| --- | --- | --- |
| Blind1 planned metadata extra keys | medium: volume_descriptor filters Mountpoint/Status/unknown fields before planned-profile equality, undermining strict planned/observed distinction. | patch exact original profile |
| Blind2 invalid workdir before bridge creation | medium: local check_workdir runs only inside final constructor, after bridge POST; early validation avoids a needless mutation on known-invalid input. | patch early existing check, retain final check |
| Blind3 combined constructor/CLI integration proof | false: neither implementation nor evidence claims continuous execution or integrated live startup. Separate constructor and pinned-CLI synthetic proofs are the bounded scope; live execution-time enforcement stays explicitly open. | reject; no runtime claim |
| Blind4 fresh negative matrix | medium: existing acquire coverage cannot protect independent fresh version/image/network path; add applicable cases with exact sequence/no construction. | patch focused tests |
| Blind5 fresh existing/conflict bridge | medium: fresh ordering differs and existing/conflict winner paths lack direct fresh coverage. | patch focused tests |
| Blind6 qualifier reconstructs expected result | medium: fabricated result equality cannot independently detect wrong target/run/network constructor input, although argv checks cover network ID. | patch capture actual constructor inputs |
| Blind7 common orchestration extraction | false: no diverging safety behavior demonstrated; intentionally distinct volume acquisition/absence policies already share owner algorithms. A generic pipeline/refactor is unnecessary to fix a concrete defect. | reject |
| Blind8 complete-suite record missing | low: record was pending final regression; execution restart lost that run. Complete passing final suite evidence must replace the incomplete closure record. | patch evidence after rerun |
| Blind9 stale create-request runbook | low: old paragraph says branch integration remains wholly open despite the new bounded proof. | patch precise historical limits |
| Edge layer | No findings. | none |
| Verification1 late bridge replacement coverage | medium: independently verified gap: deleting the fresh final ID comparison preserves current tests. Original acquire replacement test exercises a separate implementation. | patch each final fresh observation |

Each finding classified before grouping. Blind4/5 and Verification1 share missing
fresh-path coverage and are implemented together; other patches remain distinct.
No findings deferred. Original implementation agent re-engaged for code/test patches;
root owns documentation and final verification.

## Verification

Smallest acceptance RED then focused resource/volume/startup/lifecycle GREEN; matrix audit and independent review. Fresh source-bound prepare/toolchain/images; public fresh constructor/CLI controls plus existing positives; thirteen retained files unchanged. Full deployment unittest suite, syntax/whitespace/links and read-only up refusal. Exact commands/results and requirement/test/scaffold/UI/context/docs/ADR evidence required.

Focused matrix coverage ran: resource23tests (legacy dispatch correction then1test GREEN), volumes29 GREEN10.644s, startup40 GREEN5.341s, lifecycle18 GREEN57.979s. All fresh matrix rows executed and passed; broader/public qualification remains a closure check.

Final verification: complete resource suite28tests PASS76.952s; lifecycle19tests
PASS63.664s; full deployment416tests PASS333.443s. Fourteen public CLI checks pass
on fresh d824e14c-5e70-408b-844d-490146e313c2, preserving thirteen retained files and
both source snapshots. Protected record SHA256
d9a1409d4633b4c8b021cd7f675fca564fba2d1732f4532340b4abf77fecfcd2.
Real up refuses docker_28_required, exit2/runtime_ready=false. Eight finding instances
fixed, two disproved, none deferred. Requirement/test commands and five impacts:
[delivery evidence](../../platform/deployment/ENV_FRESH_START_EVIDENCE.md).
The interrupted pre-patch broad run supplies no passing result; final full run above
is the closure evidence. Source parsing, whitespace and local link checks pass.
