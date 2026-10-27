---
title: 'Qualify Scribeswell against adopted owner readiness and release reports'
type: 'feature'
created: '2026-10-27'
status: 'done'
route: 'dispatch'
baseline_commit: '37706e274c138b35b95fb33db9dcd3776a543a08'
review_loop_iteration: 0
context:
  - '{project-root}/apps/scribeswell/docs/OWNER_READINESS_HANDOFF.md'
  - '{project-root}/services/access/STUDIES-ENROLLMENT.md'
  - '{project-root}/apps/scribeswell/docs/PRIVATE_MIGRATION_REPORT.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

Qualify existing personal Studies/signup through default Access startup using genuine
v2 Identity0026/Access0019 readiness delivered in37706e2. The old app fixture injects
databases. Consume the published readiness/private-report contracts and retain actual
browser, SQL, signup/privacy and release-refusal evidence.

## Boundaries & Constraints

Always preserve explicit enrollment, current authorization, account isolation, existing
browser/SQL/privacy and real local-mail signup/consumed-link/elapsed-expiry assertions.
Generate a fresh artifact through owner prepare() for each fresh service executor.
Freeze sources; use fresh canonical IDs, immediate port/subnet checks and exact shutdown.
Preserve foreign work, KDG/Leave environments and historical evidence.

Never weaken owner checks, inject default-startup dependencies, fabricate artifacts,
accept later heads, edit generated specs or activate production. Sharing/Notification,
production Python3.15, external SMTP and physical devices remain separate. Native
worker tests and mocked host checks do not establish full environment release/recovery.

## I/O & Edge-Case Matrix

| Scenario | Expected behavior |
| --- | --- |
| Fresh qualified owners | Genuine fresh v2 artifact; default main:app and browser flows pass |
| Missing/stale/partial readiness, wrong role/source | Refuse; no injected fallback |
| Signup/confirmation/enrollment | Real provider/mail/SQL; confirmation grants no Studies access |
| Foreign account, disabled access, reused/expired link, leaked secret | Existing SQL/browser/privacy oracles remain binding |
| Committed private0009 report/repeat | Exact report accepted; ledger/old-consumer compatibility proven |
| Stale/wrong/malformed/failed/unknown report | Success/activation refused; reconciliation and forward retry preserved |

</frozen-after-approval>

## Code Map

- `apps/scribeswell/tests/studies_owner_fixture.py`: lifecycle/SQL/browser checks;
  start_apps injects Access databases. `studies_signup_fixture.py:SignupQualification`
  adds real signup, captured mail, consumed-link and elapsed-expiry cases.
- Qualified sources: `/tmp/studies-current-deb424b`; retained qualification:
  `/tmp/studies-current-native-20261027-review/current/qualification.json`.
  Read-only validation passed190 sources/14 runtime hashes. Leave bound inputs unchanged;
  an external app driver can load that source root and freeze its own new sources.
- `services/access/studies_readiness.py:prepare` produces fresh read-only preparation;
  `main.py` already implements default environment startup.
- `apps/scribeswell/tests/test_studies_migration_report_native.py`: actual report,
  ledger, old-consumer, failure/retry checks require a separate fresh PG17 cluster.
- `apps/scribeswell/tests/test_personal_notes_release.py` and
  `platform/deployment/tests/test_host.py`: coordinated report/refusal checks.

## Tasks & Acceptance

**Execution:**
- [x] New `apps/scribeswell/tests/studies_readiness_integration_fixture.py` and
  `apps/scribeswell/tests/test_studies_readiness_integration.py` -- observe the launch
  gap; add an app-owned SignupQualification subclass with explicit source root and
  independent source freeze. Replace only Access launch with main:app and genuine
  fresh artifact. Preserve inherited scenarios.
- [x] New `apps/scribeswell/tools/py/qualify_studies_readiness_integration.py` -- bounded
  fresh-run/source-root/qualification/proof inputs; execute real provider/browser/mail
  and independent SQL/privacy/disabled-authority checks.
- [x] Existing release/host/native report tests above -- run refusal coverage and
  separate actual PG17 qualification; record skips separately, fix demonstrated defects.
- [x] New `apps/scribeswell/docs/DEFAULT_STARTUP_INTEGRATION_EVIDENCE.md` and sanitized
  JSON; update `OWNER_READINESS_HANDOFF.md` and `FINAL_INTEGRATION_EVIDENCE.md` -- publish
  commands/results/hashes, requirement-to-test mapping and remaining gates.

**Acceptance Criteria:**
- Given fresh prepared owners, when default Access and real browser/signup flows run,
  then existing owner/signup/privacy oracles pass without default-startup injection.
- Given unsafe readiness/report evidence, when consumed, then success/activation refuses.
- Given final inspection/shutdown, then evidence matches executed sources and only new
  owned environments stop; foreign work remains intact.

## Implementation Notes

No human intent gaps. Footprint: app qualifier/tests/docs and demonstrated fixes only.
Fresh synthetic fixtures and isolated PG17 resources only; dispatch route. Existing
permission to preserve/work around the dirty tree persists. Investigation: one Sol High
agent; actual model/usage/compute elapsed unknown. Follow repository BMAD model settings.
Scaffold/shared UI/agent-context/ADR: no changes expected; record final impact decisions.
Keep generated canonical specs and owner contracts unchanged.

## Spec Change Log

## Review Triage Log

## Verification

Run failing launch/readiness acceptance, focused helper/privacy tests, fresh native
owner/browser/signup checks and independent SQL/source inspection. Run report/host
refusals and actual PG17 cases; skipped cases establish no proof. Use actual handoff
Python3.12.3 and pinned Supabase; record versions/attempts. Run composition check-only,
BMAD review and scoped local commit. No push/deployment.

Approval: user approved this spec and continuation through completion, including remaining
routine BMAD checkpoints within the frozen scope. No production gate or sandbox
permission is relaxed. Dispatch Sol High implementation; coordinator handles independent
verification, three review lenses and scoped local commit. Actual usage unknown.

## Independent implementation acceptance audit

All four tasks complete. Relevant ATDD red: historical injected launch failed the
default-module assertion (1failed1.42s). App driver changes only the launch/preparation
qualification path; owner contract and190bound archive inputs unchanged. Parent ran
89helper/signup tests0.78s and47app-report/host refusals3.15s, no skips.

Fresh native run b642ef30-d1f2-4b19-b417-bdf7bf469947 passed original browser, disabled
authority and genuine signup/mail flows.24SQL checkpoints; actual elapsed OTP
122.000347s;31confirmed unforced process stops. Parent independently validated377
source/binary hashes and13proof digests, artifact/fresh actor/retained qualification
bindings, real expiry and exact normal stop. Matrix refusal/startup/source/role cases
executed10separate module imports; inherited foreign-account/disabled/privacy/signup
oracles actually executed. Exact commands/results are in app evidence.

Parent ran separate fresh PG17 report suite:6passed8.25s, runner9.291s,86source
hashes unchanged. Actual committed before/after/repeat/previous-consumer and native
DDL/COMMIT failure/unknown-history cases passed. Loopback32770; only fresh tracked
container61a90bea4f9ddfa76776ef8e492a05da577cbcbfb45281344b54479808f9ab94 stopped;
container/volume retained. Composition dry run passed15migrations/no writes.
Full environment release/recovery, production stack, external SMTP and device gates
remain explicitly open. All implementation/native steps completed on first attempt;
actual model usage/compute elapsed unavailable. Step04 reviews follow.

## Review triage — first pass

All three lenses reported. Blind: no supported findings. Verification-gap: no gaps.

| Finding | Verdict | Evidence and route |
| --- | --- | --- |
| Edge1: late owner module addition omitted by final freeze | medium | Reproduced in a fresh temporary owner directory: after tracking main.py, adding an importable httpx.py shadows the external import but verify_sources still succeeds because it hashes only initially known paths. Compare both source membership and digests for selected-owner module inputs. Direct oracle correction; route patch, no public surface or intent change. |

Preserve bound owner archive, published contracts, all inherited passing browser/SQL/
signup/privacy assertions and historical evidence. Add a negative membership oracle,
then requalify edited app driver using fresh UUID/proof; do not relabel prior run.

## Final review resolution and acceptance

All three review lenses reported; the sole supported finding was patched. No finding
deferred. Three negative module/package membership tests first failed, then the
12-test focused file passed0.77s. Parent final helper/signup suite92passed1.01s.
Parent executed fresh review-fixed native run bbc64030-9df1-4dc2-a7e2-ab35f7874fd6:
exit0, all original/disabled/signup browsers passed,24SQL checkpoints,31confirmed
unforced process stops and exact wrapperstop0. Actual OTP elapsed122.000218s.

Final proof:/tmp/scribeswell-default-integration-review-bbc64030. Parent independently
validated486 hashes (171app/305owner/9qualification-proof/binary), recursive membership
of200owner modules, all original190qualification inputs,13retained proof digests,
fresh executor/artifact binding and real expiry. Final artifact SHA256:
37cf4072456c6784ff104ebe97a5cbebb78deba51d0f4edd27c692f818cb927e.
Prior successful b642ef30 run retained as superseded history; no evidence relabelled.

Unchanged release/report code remains qualified by47independent app/host tests3.15s
and6actual PG17 tests8.25s with no skips. Parent rechecked all86PG sources after
the driver-only patch, confirmed Docker exit0/OOMfalse/runningfalse and no32770
listener. Exact fresh container/volume retained; private connection never exported.
Composition check-only passed15migrations/no writes. Final repository evidence was
checked against10private credential/link/token values; none exported.

Tasks and every matrix/acceptance row complete. Full environment release/recovery,
production runtime, external SMTP/devices and sharing owners remain explicit gates,
not deferred findings. Two successful native runs, one review repair; actual model
usage/compute elapsed unknown. All routine continuation checkpoints were authorized
by the user's approve-and-continue-until-done instruction. Create only the scoped
local commit; no push or production activation.
