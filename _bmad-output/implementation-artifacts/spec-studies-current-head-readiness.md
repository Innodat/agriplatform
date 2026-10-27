---
title: 'Studies readiness on reviewed current Identity and Access owners'
type: 'bugfix'
created: '2026-10-27'
status: 'done'
route: 'dispatch'
baseline_commit: 'deb424b0c4d29016917c9df39b540a468ca8e1cf'
review_loop_iteration: 0
context:
  - '{project-root}/services/access/STUDIES-ENROLLMENT.md'
  - '{project-root}/platform/docs/development/migration-verification.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

Studies readiness still requires Identity0021/Access0016, blocking default Access startup
on the reviewed current owners. Implement and natively qualify preparation and startup
against the exact Identity0026/Access0019 pair now delivered in deb424b; the handoff's
0025/0018 pair predates that reviewed Discovery baseline.

Publish the adopted owner contract, exact environment/artifact interface and source-bound
evidence. Retain all unrelated working changes and historical fixtures. The private
migration-report correction in e2b3445 is complete and is not reopened.

## Boundaries & Constraints

Always preserve current provider/Auth/profile evidence, exact matching service-executor
principals, restricted roles, source/catalogue verification, Identity-before-Access
migration ordering, revocation, bounded deadlines and refusal of stale/partial/unsafe
evidence. Default create_app must construct its own Studies connections from environment
settings. Preparation remains read-only and writes only a new private artifact.

Never accept arbitrary later heads, fabricate positive proof fields, rewrite accepted
migrations/ADRs, modify historical evidence, use injected databases as default-startup
proof, or activate production. Recipient/invitation and Notification delivery remain
undelivered. Keep KDG and Leave fixtures untouched; native mutations use a fresh isolated
synthetic fixture with a canonical run UUID and immediate port/subnet checks.

## I/O & Edge-Case Matrix

| State | Expected behavior |
| --- | --- |
| Qualified exact current heads, safe roles, matching enabled principals, profile hook and registry | Read-only preparation emits a source-bound private artifact; unmodified default startup and real provider-backed Studies requests succeed |
| Old, unknown, partial or mismatched owner revisions | Preparation refuses; no activation |
| Missing, disabled, mismatched or non-service executor principal; unsafe role/raw privileges; missing hook/registration | Preparation refuses without repair |
| Missing/partial environment, old or malformed artifact, changed runtime or qualification sources/proofs | Preparation/startup refuses at its owning boundary |
| Current account denial or revoked grant after valid preparation | Runtime denies; artifact grants no authority |
| Migration failure or unknown result | Activation remains blocked; explicit recovery/retry preserves existing state |

</frozen-after-approval>

## Code Map

- `services/access/studies_readiness.py`: exact heads in prepare/validate_artifact;
  authoritative source inventory, proof-stage validation, read-only catalogue/principal
  and role checks. Extend provenance to current migration/catalogue dependencies.
- `services/access/main.py:create_app`: environment opt-in already validates readiness;
  preserve its default path and KDG/capability/Discovery dispatch.
- `services/access/identity-migrations/identity_baseline.py`: require_head now means0026;
  `services/access/migrations/access_baseline.py` verifies0019. Reuse these owners.
- `apps/scribeswell/tests/studies_owner_fixture.py`: fresh isolated real-provider fixture,
  current migration preparation and browser/SQL proofs; start_apps currently injects
  databases. Extend/reuse it for current-owner readiness without weakening old evidence.
- `apps/scribeswell/tools/py/qualify_studies_owner_integration.py`: existing single-use
  fixture CLI. Historical `services/access/tests/qualify_studies_enrollment.py` is
  reference-only: fixed retained KDG run, old revisions and reference-writing stages.
- `services/access/tests/test_studies_readiness.py` and
  `platform/deployment/tests/test_host.py`: focused refusal and host-consumer coverage.

## Tasks & Acceptance

**Execution:**
- [x] `services/access/tests/test_studies_readiness.py` -- observe current-head failure,
  then cover exact pair/artifact compatibility and source/proof refusal cases.
- [x] `services/access/studies_readiness.py` -- adopt a closed current-head artifact
  policy and genuine qualification inputs, retaining all owner safety checks.
- [x] `apps/scribeswell/tests/studies_owner_fixture.py` and bounded owner qualification
  helper under `services/access/tests/` -- qualify fresh current owners, clean/populated
  upgrade/repeat/failure, restricted runtime execution, preparation refusals and default
  startup; retain actual stage observations and independent read-only inspection.
- [x] `platform/deployment/tests/test_host.py` -- synchronize artifact examples if
  needed and verify host refusal behavior without deployment.
- [x] `services/access/STUDIES-ENROLLMENT.md`, owner evidence and
  `apps/scribeswell/docs/OWNER_READINESS_HANDOFF.md` -- publish adopted interface,
  exact commands/results/hashes and remaining gates.

**Acceptance Criteria:**
- Given the current reviewed owners, when qualification and preparation execute, then
  default startup succeeds using real restricted credentials and live provider checks.
- Given each matrix refusal state, when its owning boundary executes, then it refuses
  with no fabricated evidence or runtime authority.
- Given existing KDG and public consumers, when focused regressions execute, then their
  contracts remain compatible and retained fixtures are preserved.

## Implementation Notes

Planning investigation found no unresolved human intent choices. Artifact version policy
is an owner implementation decision. No production side effects are authorized; native
effects are limited to new synthetic resources. Footprint spans readiness, qualification,
consumer tests and documentation; no business API change is intended. Hence dispatch.

Impacts: no scaffold/shared UI/agent-context/ADR changes expected; document the final
decisions and any proven reusable qualification support. Existing service ownership and
release-safety decisions apply. Coordinator model/effort inherited; actual usage and
compute elapsed unavailable. Investigation used one inherited-capability subagent.

## Spec Change Log

## Review Triage Log

## Verification

Run the smallest new failing readiness acceptance first, then focused Studies Identity/
Access/startup and host tests with the existing locked owner interpreter. Execute fresh
native qualification through the isolated fixture with a new run UUID and private proof
directory; inspect source hashes and native allow/deny/migration/provider results
independently. Run `python3 tools/py/run_compose_supabase.py --check-only` for composition.
Record exact commands/results and requirement-to-test traceability in owner evidence.
No root build/test claim, production activation, external SMTP or physical-device claim.

## Execution checkpoint — native permission pending

Approved by user to implement and continue. Delegated implementation selected
`gpt-6.1-sol` / `high`; actual provider usage unavailable. ATDD observed the new
current-head artifact acceptance fail against the previous v1 implementation.
Focused readiness/Studies/host regression: 79 passed, one Starlette warning, 3.07s
(child-reported; parent final independent verification/review remains pending).

Foreign concurrent work added uncommitted Identity0027 and changed main/baseline.
It is preserved. Approved baseline qualification therefore uses isolated source
`/tmp/studies-current-deb424b`, archived from the canonical baseline above with this
delivery applied. Exact adopted policy under implementation: artifact v2 for
Identity0026/Access0019 only; foreign0027 is not adopted or qualified. Snapshot artifact
will intentionally fail if applied against changed live runtime sources.

Native helper: services/access/tests/qualify_studies_current.py. Planned proof root:
`/tmp/studies-current-native-20261027`; clean run
`0e28eca3-a17b-42d4-a9ed-660df25eec4f`; populated run
`428063a3-9f50-407f-83c8-f0b043dee3e3`. Read-only inspection found all new proof/run
directories absent before retrying required Docker/socket escalation. First pending
approval call never launched and was interrupted by coordinator after prolonged
waiting; retry permission is pending. No native success or readiness artifact claimed.

Implementation agent remains available for completion and review repairs. Next: receive
the pending native execution permission, execute and inspect native evidence, reconcile
snapshot changes into the original tree without foreign edits, complete task/matrix
audit, then run BMAD step04 review and finalization. Do not restart the workflow or
rerun historical fixed-KDG qualifier stages. No production activation.

## Independent implementation acceptance audit

Parent read the scoped qualified-source diff at /tmp/studies-current-readiness-qualified.diff.
All five implementation tasks complete. Native matrix coverage: eight authorization/
migration/provider stages,13 preparation refusal faults, nine default-startup refusals,
unmodified OS process200 then current403 and revoked denial; changed-source/proof and
closed-schema refusals covered by executed readiness tests. Parent independently reran
focused suite79passed/one warning3.41s; validated190 source/eight proof hashes and
artifact digest plus both unforced normal stops. Composition dry run passed15migrations.
Archived compatibility suite264passed/one warning10.83s; exact commands/results and
actual interpreter versions are in owner evidence. Native retry and support-source
reconciliation preserved; historical failed attempt retained. Step04 review now starts.

## Review triage — first pass

All three review lenses reported before triage. Blind review: no supported findings.

| Finding | Verdict | Evidence and route |
| --- | --- | --- |
| Edge1: profile-denial oracle accepts any StudiesFailure | medium | Confirmed broad catches in current_denials (and boundary cases); expected status/error identifiers distinguish current ineligibility403, unverified403 and deliberately unavailable profile/setup503. Patch to require each contract-specific result; reviewer suggested blanket403 is not correct for missing/deleted/system/keyed profile cases. |
| Edge2: postcondition injection need not be reached | medium | Confirmed exit status alone can accept an unrelated failure. Owner env deliberately suppresses exception contents, so searching logs for the injected message is invalid; add a safe private marker emitted only after actual postcondition verification reaches the injection, then require it for the failed stage. Patch. |
| Edge3: failed migration asserts ledger only | medium | Confirmed failure comparison checks ledger only and later asserts prior profile existence, leaving row-value corruption undetected. Patch with immediate before/after protected data equality before retry. |
| Verification1: populated failure data gap | medium | Filed verification evidence confirms the same missing row-value comparison as Edge3. Group with Edge3 for a single direct oracle correction. |

All survivors are trivial qualification-oracle corrections within the existing approved
behavior. No new public surface or intent change; route patch. Keep exact26/19 policy,
all successful authorization/startup/refusal stages, historical attempts and foreign
source isolation. Requalify edited helper under fresh IDs; never relabel old evidence.

## Final review resolution and acceptance

All three supported review root causes are patched; no review finding deferred.
Eight negative-oracle tests passed (parent0.20s). Parent executed the complete revised
native helper from the qualified snapshot: exit0, both new clusters passed/stopped
normally, no forced termination. Final populated run c68e27fd-960d-44f1-b773-9493795f7f5a;
clean5b0441bc-70ac-4e40-9a5c-66daac599d61. Private proof root:
/tmp/studies-current-native-20261027-review. Parent independently revalidated190 source
hashes/eight stage proofs, artifact qualification digest,20 retained artifact/proof
digests in public summary, strict denial observations, both0600 postcondition markers,
and matching failed-migration protected-data digests/counts. Final artifact SHA256:
200fccce1eef748644daabf22d98642960dc25550027018bc92f120252bf8434.

Final focused readiness/Studies/host rerun:79passed/one warning2.96s. Archived264-test
compatibility run remains valid for unchanged production code; subsequent changes
only tightened qualifier oracles, independently tested and rerun natively. Composition
dry run passed with15migrations/no writes. Full commands/results/source boundaries
are in services/access/docs/testing/studies-current-readiness-20261027.md and its
sanitized JSON. Previous attempt2 evidence is superseded, retained unchanged.

Three complete native attempts (one failed fixture oracle, two successful), plus one
pre-allocation dispatch refusal. Actual Python3.12.3 handoff stack recorded; production
Python3.15/bundle/release rehearsal remains unqualified. Concurrent Identity0027 remains
unqualified and untouched; this delivery adopts only reviewed26/19. No deployment.
Selected delegated implementation Sol High; reviewers inherited coordinator capability.
Actual model/usage/compute time unavailable; test durations above measured separately.
BMAD complete; create only the scoped local commit, with shared host-test artifact hunk
alone staged from that otherwise foreign-modified file. Never stage foreign changes.
