---
title: 'ENV: bind the first startup create to qualified immutable image identity'
type: feature
created: '2026-10-15'
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: 1fbd0073cfebb515379dd339b40554bc97f5b2d3
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/platform/docs/architecture/contracts/scaffold-environment-and-generation.md'
---

<frozen-after-approval reason="Standing bounded shared-foundation implementation and synthetic verification approval; user requested next">

## Intent

**Problem:** The qualified image receipt records immutable manifests, but the actual
pinned CLI's first PostgreSQL create still requests a mutable tag. Inspection success
does not establish immutable selection at that boundary.

**Approach:** Extend the existing image/startup owners with a closed selection plan
derived from verified retained evidence and a reusable no-dispatch first-create
transformation. Prove the actual pinned CLI request becomes the qualified Linux/amd64
digest reference at the private executable boundary, then refuse creation.

## Boundaries & Constraints

**Always:** Preserve exact approved pins, source-bound preparation, owner receipts,
existing startup argument/workdir/process/event guards and all concurrent Leave/PtS
changes. ATDD outer loop and focused TDD precede behavior. Derive exactly four approved
tag-to-repository@sha256 mappings through existing owner verification, binding the
Linux/amd64 child manifest, not its index or config digest. Read protected existing
artifacts and verify identity/bytes before and after use; missing/stale evidence cannot
install, collect, repair or adopt. Validate the original create arguments before
replacing only the single PostgreSQL image operand. Preserve every other argument
exactly in memory; never retain argv, SQL, environment values or daemon payloads.
The transformation is reusable construction only, with no dispatch capability.
Proof uses the existing actual pinned CLI/private docker and podman fixtures; record
safe original/selected references and refusal. Keep runtime_ready=false and
container_executed=false. Report selection proof separately from execution enforcement.

**Never:** Activate dev.py up, mutate real Docker, pull layers, execute a container,
SQL or migrations, alter accounts/access, provision/deploy, or use real data. No new
generator, generic proxy/offline service, full Docker wrapper, native-CLI digest-support
claim, changed dependency pins, accepted ADR edits, or Identity/Access/WRITE/Leave/KDG
domain implementation. Do not infer all service/helper creates from first-create proof.

## I/O & Edge-Case Matrix

| State | Expected behavior |
| --- | --- |
| Current protected owner evidence | Exactly four approved mappings to distinct retained Linux/amd64 child digests |
| Actual pinned CLI's validated tagged PostgreSQL create | Replace only image operand; independently verify selected digest, refuse create, retain safe proof |
| Missing/stale/tampered receipt or manifest, extra/missing/mismatched plan entry | Refuse before CLI; never repair or collect |
| Wrong registry/tag/digest or unsafe/ambiguous create options | Refuse without selection or execution |
| Changed receipt/source/workdir during proof | Reject completion; preserve evidence |
| Unexpected command, old startup negative controls | Exact safe refusal, bounded child cleanup and no real dispatch |

</frozen-after-approval>

## Code Map

- `platform/deployment/images.py:retained,qualify`: existing owner validation of receipts,
  artifacts, platform/index-child and tool/preparation bindings. Add only a narrow
  existing-evidence selection accessor if needed; no second receipt validator.
- `platform/deployment/startup.py:existing_images,create_facts,fixture_command`:
  reuse validated argument parsing for a pure first-create transformation. Existing
  `install_fixture,synthetic_probe,validate_observations,qualify` own actual CLI proof.
  Preserve protected roots, source snapshots, pidfd and bounded fixture process guards.
- `tests/test_images.py`, `tests/test_startup_adapter.py`, `tests/qualify_startup.py`:
  extend owning suites and public controls, using independent distinct digest fixtures.
- `image-pins.json` and retained manifests are authority, not editable selection guesses.
  Source registry rewriting does not establish native digest support; actual inspected
  references must remain precisely those proven by the existing boundary.

## Tasks & Acceptance

- [x] Extend focused owner tests; observe behavioral acceptance failure before code.
- [x] Implement protected existing-evidence mapping and no-dispatch first-create
  transformation within existing image/startup modules; retain old behavior contracts.
- [x] Extend actual CLI qualifier with successful immutable selection and exact negative
  controls; no optional unqualified path in its positive result.
- [x] Update `platform/deployment/DEVELOPMENT.md`, new
  `platform/deployment/ENV_IMMUTABLE_CREATE_EVIDENCE.md`, KDG next-session and memlog;
  record requirement/test and scaffold/UI/context/docs/ADR impacts.
- [x] Focused then affected regression, fresh prepared/tool/image actual CLI proof,
  independent review/fixes, scoped verification and local conventional commit, no push.

**Acceptance:** Given current qualified owner evidence, when the public startup proof
executes the pinned CLI against private fixtures, then the first create is transformed
to the corresponding immutable child reference and refused, with independently checked
safe facts. Given invalid selection/evidence/arguments, when qualification is attempted,
then it fails safely without executing a container or repairing evidence.

## Implementation Notes

No intent gap or irreversible operation. Multi-file existing-owner extension warrants
dispatch. Standing approval covers the dirty concurrent tree and bounded work.
Implementer owns code/tests and new runbook section only; root owns evidence/navigation,
spec finalization and memlog. Preserve all other files.

## Spec Change Log

## Review Triage Log

## Verification

Run `python3 -m unittest discover -s platform/deployment/tests -p test_startup_adapter.py`
and affected image tests, then `-p 'test_*.py'`. Prepare a fresh UUID, qualify tools/images
through their existing commands, run public `tests/qualify_startup.py` controls. Retain
exact safe results and unchanged evidence identities. Actual dev.py up remains gated.
Compilation, scoped whitespace and local documentation links must pass.

Initial verification: startup 32 tests pass (root 3.945s), image 34 tests pass (implementer 4.110s), deployment 274 tests pass (60.422s). Fresh run b46431a1-c11b-45c5-8b7f-e19d8ea03470 prepared/tool/image qualification passes; actual pinned CLI selects PostgreSQL child f2a84af37797675f0b27e27ea1fad2ebcd913ebf7ad60be05d7df0bcbd29e4b5 and refuses create, nine events. Four public negative controls return exact safe codes. All 13 evidence identities/bytes and source bindings unchanged. Independent review follows.

### Independent review triage

All three layers completed before triage; thread limits required sequential launches,
without reacting to findings before every layer was launched. Edge review: no findings.
Each instance below is classified separately before grouping.

| ID | Verdict | Evidence / route |
| --- | --- | --- |
| B1 | medium | Reproduced snapshot associating old read bytes with replacement inode from later path stat. Bind bytes/identity to one open descriptor and verify current entry; patch. |
| B2 | medium | Reproduced transformer mutation of health-timeout to 999s still recording immutable_selection_proven. Compare every original/transformed operand except the selected image before success; patch. |
| B3 | medium | Plan validator is structural; trusted provenance comes from existing_images, but pure constructor docs omit that requirement and public coverage is disconnected. Clarify internal verified-plan precondition and add integrated provenance regression with V1; patch. |
| B4 | low | Ambiguous-create test's local events list is never passed to code. Exercise fixture_command for string argv cases and assert no event; direct test correction, patch. |
| B5 | medium | New malformed/non-string/duplicate-digest validation branches lack focused and pre-CLI coverage. Add invalid-plan cases with exact refusal; patch. |
| B6 | low | Reviewed draft evidence lacked traceability/results. Root has added initial commands, matrix and exact outcomes; complete final evidence before delivery. Patch documentation. |
| V1 | medium | Preverified disconnected owner/probe/full-qualify tests could miss a substituted valid-shape plan. Integrate real startup.qualify with prepared image fixture and synthetic CLI process; independently compare retained child digest. Patch with B3. |

All seven instances have bounded fixes, no new public surface or intent change; none deferred.

Final post-review verification: 36 focused startup tests passed in 12.826s; all 278
deployment tests passed in 59.769s, no skips. Fresh run
a87297ea-1730-47a0-8a4e-d56214041118 passed prepare/tool/image qualification and the
actual pinned CLI positive plus four exact negative controls. All 13 evidence files
and proof sources remain unchanged. Actual up refuses docker_28_required. All seven
review instances fixed, none deferred; scoped compilation/whitespace/links pass.
Protected final record .local/immutable-create/final-a87297ea.json SHA-256:
9bfc7ce3865e158462e9f51c675049144de2239d83a35896a40cc5eea1c8ecec.
Requirement-to-test coverage, command evidence and all five impacts are in
platform/deployment/ENV_IMMUTABLE_CREATE_EVIDENCE.md. Runtime remains unqualified.
