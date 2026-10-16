---
title: 'ENV guarded CLI volume creation integration'
type: 'feature'
created: '2026-10-16'
status: 'in-review'
baseline_commit: 'd4bdd2fbfb1def85f3875f89970b6355909ba348'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '/home/ck/repos/innodat/agriplatform/AGENTS.md'
  - '/home/ck/repos/innodat/agriplatform/platform/deployment/DEVELOPMENT.md'
  - '/home/ck/repos/innodat/agriplatform/platform/deployment/fixtures/supabase-pg17-lifecycle.md'
  - '/home/ck/repos/innodat/agriplatform/platform/docs/architecture/contracts/scaffold-environment-and-generation.md'
---

<frozen-after-approval reason="standing bounded ENV implementation approval and Next instruction">

## Intent

**Problem:** The pinned CLI fresh fixture acknowledges a two-label volume create without executing the ENV volume owner's six-label checks. The constructor and CLI proofs remain disconnected from guarded execution-time ownership.

**Approach:** Connect the actual pinned CLI ensure-volume boundary to the existing volume owner on the retained guarded resource session, exercised against private synthetic Docker peers. Acknowledge only after validated owner creation/reinspection/use checks; retain refused container execution.

## Boundaries & Constraints

**Always:** Truthful absent CLI probe precedes creation. Keep qualified evidence/run lock, one connection/version, five-second total daemon budget, image/network continuity, current custody and owner postchecks. Fresh owner operation refuses existing volumes, sends the existing exact six-label create profile once, validates acknowledgement/reinspection and current absence of container references. Lost/ambiguous mutation terminates without replay, adoption or cleanup. Keep subprocess waits outside the immediate constructor callback; bound the integrated process by remaining guard time. Preserve existing acquire/invocation/CLI controls and exact baseline including TypeScript7.0.2. Report observed ownership separately from planned metadata, and safe facts only.

**Never:** Treat404/201/labels as immutable identity, exclusive reservation, empty storage or qualified initialization. No real Docker mutations, container execution/SQL, host upgrade/provisioning, credentials/accounts/access changes, production migrations/deployment/pilot, dependent Identity/Access/WRITE/KDG/Leave implementation, another generator/service/readiness engine, accepted ADR edits or concurrent-document loss. `up` stays gated and runtime_ready=false.

## I/O & Edge-Case Matrix

| Scenario | Input/state | Expected behavior | Failure |
| --- | --- | --- | --- |
| Integrated positive | Valid pinned CLI absent probe and exact create; valid synthetic peer | Owner POST six labels, validated observation/use before CLI ACK; strict PG request/copy/refused start | runtime false, no real container |
| Existing/late/foreign | Volume present before guarded create | No adoption or create ACK/PG create | safe reuse/ownership refusal |
| Uncertain mutation | Lost/truncated response, bad201/descriptor, changed reinspection or references | No replay/cleanup/later phase | safe owner refusal |
| Continuity/custody | Changed source/evidence/lock/image/network, EOF, exhausted budget | No unverified ACK or returned proof; release connection/lock | established safe errors |
| Invalid phase/bridge | Wrong/repeated/reordered command, forged/malformed/duplicate private handoff | No arbitrary daemon route or ACK; baseline validated before negative injection | safe fixture refusal |
| Compatibility | Existing acquisition, fresh constructor, old standalone CLI controls | Existing contracts unchanged | exact regression oracles |

</frozen-after-approval>

## Code Map

- `platform/deployment/volumes.py`: distinct fresh-only session operation; reuse create_input/require_absent/volume_descriptor/observe_unused. Existing acquire_session keeps adoption behavior.
- `platform/deployment/resources.py`: retained fresh guard context and final joint checks; characterize extraction; keep constructor callback immediate.
- `platform/deployment/startup.py`: exact fixture-only closed handoff to parent owner; generated private location/custody/bounds, no endpoint selector. Preserve standalone proof; source-bind any private helper.
- Existing deployment `tests/qualify_resources.py`, `tests/qualify_startup.py` and corresponding resource/volume/startup/lifecycle tests: independent oracles and actual pinned-CLI integration.
- `dev.py` SOURCES and `tests/test_dev.py` FILES: update together only for a new owning helper. Existing profile/lifecycle authority documents describe precisely proven limits.

## Tasks & Acceptance

- [x] Add meaningful integrated acceptance RED; send root smallest command and wait before production edits. Add characterization before guard extraction.
- [x] Implement fresh owner operation and retained-context CLI connection with matrix coverage; no fake unconditional success.
- [x] Preserve existing controls, add baseline-valid negative integration controls and safe-output tests; source-bind any helper.
- [x] Record requirement/test evidence and scaffold/UI/context/documentation/ADR impacts; root owns runbook, evidence, KDG handoff/memlog and scoped local commit.

**Acceptance:** Given absent private peer resources and the pinned CLI, when integrated fresh startup reaches ensure-volume, then the real ENV owner algorithm sends one exact request and validates observations before acknowledgement, and execution still terminates before a real container starts. Given uncertainty or changed custody, when that boundary is attempted, then no unverified acknowledgement or readiness claim survives.

## Implementation Notes

No intent gaps or irreversible actions. Root alone runs socket/port/public suites serially outside sandbox; implementer waits for root RED and never escalates. Root owns documentation/qualification/review/commit. Bind any helper to source and test-copy lists. Idempotent creation cannot qualify freshness/initialization.

## Spec Change Log

## Review Triage Log

| Finding | Verdict and verified evidence | Route |
| --- | --- | --- |
| Blind1 executable custody | medium: qualified_evidence inputs cover sources/receipts and image evidence, not the Supabase file; qualify anchors only its directory and repeats tool probes afterward. New retained execution could mutate the volume before that late refusal. | patch verified executable identity/bytes binding before launch and mutation |
| Blind2 pre-ACK joint controls | medium: existing late controls start at58+, after the ACK-side joint45–57. No fault cases directly protect that acknowledgement gate. | patch independent private tests, no new public controls |
| Blind3 post-POST custody failures | medium: source/receipt/lock/config mutations currently happen before POST. Newly uncertain mutation needs explicit no-ACK/no-replay/later-phase evidence. | patch post-POST cases |
| Blind4 peer credentials | medium: current forged-token test still uses a valid direct child; wrong ancestry/UID branches lack negative proof. | patch real grandchild plus safe UID adapter test |
| Blind5 listener custody | medium: new listener inode/type/mode guards lack removal/replacement/permission tests. | patch existing-state tests |
| Blind6 output cap | medium: guarded runner has its own 1MiB accounting; old bounded_command tests execute another function. | patch stdout/stderr/combined overflow and bounded consumption |
| Blind7 process-group cleanup | medium: drip witness protects one wrapper only; malformed/output/pipe-holder terminal paths lack descendant evidence. | patch terminal-path witnesses; no reaping promise |
| Blind8 framing cases | medium: oversized/empty/full-without-EOF are distinct branches not covered by partial drip. | patch no-owner-mutation and total deadline cases |
| Blind9 final evidence | low: final broad/public results remain closure work; record exact successful commands/results after executing them. | root documentation closure |
| Edge | No findings. | none |
| Verification1 output accounting gap | medium: filed pre-verified repository searches show flood tests target images.bounded_command, while guarded code is distinct. | patch with Blind6 |
| Verification2 ancestry gap | medium: filed pre-verified searches show all adversaries retain direct-child ancestry; deleting PPid comparison would preserve tests. | patch with Blind4 |

Every instance classified before grouping. Shared missing output-cap and ancestry
coverage are grouped by identical root causes; other patches stay separate. No
findings deferred. The original implementation agent is re-engaged for narrow
code/tests; root retains final evidence/navigation/qualification/commit ownership.

## Verification

Behavioral RED, focused suites, matrix audit, independent review. Fresh prepare/toolchain/images; public integrated and existing controls, thirteen unchanged retained files/source snapshots; full deployment suite, AST/whitespace/links and read-only up refusal. Exact commands/results and remaining gates in evidence.

Matrix audit: integrated5tests PASS40.069s, public wiring1 PASS4.083s, volumes31 PASS11.566s, lifecycle19 PASS52.183s. Root read complete scoped diff; five impact decisions and exact intermediate results recorded in ENV_GUARDED_CLI_VOLUME_EVIDENCE.md. Public pinned-CLI and final broad regression remain closure checks.
