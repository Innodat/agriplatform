---
title: 'ENV run-volume use admission'
type: 'feature'
created: '2026-10-16'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '8830d111dc7ac53f8dfc4baf68cae3cbcc62a251'
context:
  - '/home/ck/repos/innodat/agriplatform/AGENTS.md'
  - '/home/ck/repos/innodat/agriplatform/platform/deployment/DEVELOPMENT.md'
  - '/home/ck/repos/innodat/agriplatform/platform/docs/architecture/contracts/scaffold-environment-and-generation.md'
---

<frozen-after-approval reason="standing user approval for bounded ENV implementation">

## Intent

**Problem:** Matching run-owned database-volume metadata does not establish whether a running or stopped container already references it. Existing acquisition can hand such a volume to a startup constructor.

**Approach:** Observe current container references through one narrow Docker API query on the existing guarded connection. Refuse any nonempty result before standalone and combined acquisition handoff.

## Boundaries & Constraints

**Always:** Preserve owner algorithms, run lock, evidence custody, one connection, absolute deadline, safe errors, no reconnect/replay, exact approved dependency baseline including TypeScript7.0.2. Use ATDD/focused TDD. All verification is isolated synthetic; runtime_ready remains false. A matching existing unused volume remains metadata-admissible. Query all containers, with only the exact run-owned volume-name filter, and accept only an empty JSON array. Docker API1.48 container listing supports all=true and volume=name; a destination-name match may conservatively refuse too.

**Never:** Real Docker mutations, pulls, containers, SQL, production/account/access/infra/deploy actions; new generator/service/workflow; dependent Identity/Access/WRITE/KDG/Leave work; generic daemon proxy/listing route. No claim of reservation, exclusive access, fresh/empty/initialized storage, immutable volume identity or execution readiness. No container details in reports/errors. Do not edit accepted ADRs or concurrent documents.

## I/O & Edge-Case Matrix

| Scenario | Input/state | Expected behavior | Error handling |
| --- | --- | --- | --- |
| Unused | Exact owned volume; empty reference array | Existing/new acquisition succeeds; constructor once | runtime false |
| Referenced | Running, stopped, or same-owner reference | Refuse before constructor; no cleanup | safe volume-use code |
| Late reference | Empty initial use check; nonempty final combined check | Refuse joint handoff | same safe refusal |
| Invalid observation | Object/null/scalar, non200, malformed/oversized framing | No handoff or replay | existing safe transport or volume-use error |
| Continuity | EOF, truncation, timeout, source/preparation/lock drift around query | Refuse; one connection | established safe error |
| Route safety | Missing all, extra/changed filters, injected name, arbitrary query | Reject before socket access | docker_request_invalid |
| Response typing | Array from version/image/network/volume route | Still refused | docker_response_invalid |

</frozen-after-approval>

## Code Map

- `platform/deployment/volumes.py`: reuse acquire_session; shared bounded use helper after final selected volume observation, no second adapter.
- `platform/deployment/resources.py`: repeat helper after final joint volume descriptor check, before constructor.
- `platform/deployment/dev.py`: _docker_request closed routes; DockerSession.exchange and _docker_response keep existing object typing except this canonical list route. Do not expose caller-controlled response type bypass.
- `platform/deployment/tests/qualify_volumes.py`, `qualify_resources.py`: independent literal query/event oracles; existing private Unix fixture transport accepts JSON arrays. Extend existing public synthetic controls, no endpoint selector. Source binding already includes these files.
- `platform/deployment/tests/test_volumes.py`, `test_resources.py`, `test_docker_session.py` (verify actual session test filename): adjust exact event counts carefully; preserve existing custody/transport/recovery assertions. Characterize affected behavior before risky parser changes.
- Primary API authority: https://raw.githubusercontent.com/moby/moby/v28.0.0/docs/api/v1.48.yaml ContainerList; https://raw.githubusercontent.com/moby/moby/v28.0.0/daemon/list.go volume filter exact map lookup.

## Tasks & Acceptance

**Execution:**
- [x] Add failing acceptance coverage for referenced volume and late combined reference; report exact command to root and WAIT for observed RED before production implementation.
- [x] Implement narrow observation in existing transport/volume/combined owners with focused tests for every matrix row. Reuse existing fixture/test tooling, update affected independent event oracles rather than weakening assertions.
- [x] Extend existing synthetic public controls for running/stopped/late references and malformed/error use observations; verify safe CLI status/output and constructor suppression.
- [x] Update DEVELOPMENT.md with bounded behavior/commands/limits. Root owns evidence file, status summary, next-session/memlog, verification results and scoped local commit.

**Acceptance Criteria:**
- Standalone and joint success require an empty current-use observation on their own existing connection and budget; late joint reference suppresses constructor.
- Existing object response contracts, loss/recovery behavior, ownership guards and unrelated owner documents remain protected.
- Root records requirement-to-test evidence and scaffold/UI/context/documentation/ADR impacts; all affected tests and full deployment suite pass before completion.

## Implementation Notes

Root runs socket/port/public qualification tests serially outside sandbox. Implementer must not launch tests requiring escalation: send root exact commands for RED/GREEN; wait for RED before production code. Implementer owns code/tests and new runbook subsection only, no evidence/navigation/spec edits except append notes/tasks. Root handles tool/image qualification and final evidence after source freeze. Standing authorization settles scope: no intent gaps or irreversible runtime actions. Baseline full hash will be captured before dispatch.

## Spec Change Log

## Review Triage Log

| ID | Verdict | Evidence and route |
| --- | --- | --- |
| B1 | medium | GREEN/public/full results absent from initial evidence draft; root completes verified results before closure (patch). |
| B2 | medium | Every-exchange loss tests cover final transport loss, but final use wrong-type/status/oversized outcomes lack targeted coverage; add cases at existing final boundary (patch). |
| B3 | medium | All standalone use controls initialize existing volumes; fresh-created referenced path lacks direct no-cleanup/no-replay test (patch). |
| B4 | medium | Existing deadline hook covers query delay internally, but safe public query-timeout result lacks direct coverage; add private fixture delay test through public main (patch). |
| B5 | low | Real transport rejects non-list first, so volume_use_invalid is unreachable; remove redundant branch directly (patch). |
| B6 | medium | Standalone executes evidence after final exchange before constructor without immediate idle/budget checks; reproduce observable EOF during this interval, then mirror existing combined boundary guards (patch for demonstrated state). |
| B7 | low | Destination match is documented but fixtures only use generic references; add an explicit nonempty destination-match response assertion (patch). |

Edge reviewer returned no findings; verification reviewer returned no gaps. Its tentative non200 parser concern was retracted after following the existing early status return and is not a filed finding.

## Verification

- Smallest new acceptance test RED, then focused volume/resources/session suites GREEN.
- Existing source-bound prepare/toolchain/images qualification under fresh UUID; existing public synthetic controls including new cases, retained evidence unchanged.
- `python3 -m unittest discover -s platform/deployment/tests -p 'test_*.py'` serial regression.
- Compile, scoped whitespace/link checks; real up remains refusal (read-only prerequisites only).

Observed RED: both requested acceptance tests failed Refusal not raised before production edits. Focused volume25, resources17, session17 pass. Matrix audit maps unused to constructor-once/exact-order tests; references/invalid/late to control matrices; continuity to every-exchange loss and custody/deadline tests; routes/response typing to session tests. Final root qualification and regression pending.

Review patches closed B1–B7: final evidence added; private tests cover final response shapes/status/oversize, references after create, destination matches and safe public query timeout; unreachable branch removed. Standalone handoff EOF regression observed RED (two subcases) before mirroring existing idle/budget guards. Final focused volume28 and resources18 pass; session17 passed. All matrix rows executed; source freeze precedes fresh qualification. No finding deferred.

Final verification: fresh 70727ea5-e47d-4753-8b41-33086f7ce76a prepare/toolchain/images PASS;54 public checks PASS, thirteen retained files and source snapshots unchanged, record SHA2567be0366459c733c21801b7bc8d81df6c771ae549b8b81c14b5434b1c18821dc6. Registry-refused earlier run preserved. Full deployment suite 386 in 186.462s PASS. Real up exit2 docker_28_required/runtime_ready=false. Evidence and all five impacts in platform/deployment/ENV_VOLUME_USE_EVIDENCE.md; navigation/memlog and consolidated runbook status updated. No deferred findings, runtime activation or dependent owner work.
