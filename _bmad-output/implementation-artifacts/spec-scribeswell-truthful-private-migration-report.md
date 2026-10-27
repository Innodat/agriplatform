---
title: 'Report the actual private Studies migration revision'
type: 'bugfix'
created: '2026-10-27'
status: 'done'
route: 'dispatch'
baseline_commit: '9aed0860667d25ad7ed8bbe088963ebd93e7a07b'
review_loop_iteration: 0
context:
  - /home/ck/repos/innodat/agriplatform/AGENTS.md
  - /home/ck/repos/innodat/agriplatform/platform/docs/development/bmad-codex-usage.md
  - /home/ck/repos/innodat/agriplatform/platform/docs/development/migration-verification.md
  - /home/ck/repos/innodat/agriplatform/platform/docs/architecture/decisions/0020-safe-schema-changes-and-release-recovery.md
  - /home/ck/repos/innodat/agriplatform/apps/scribeswell/docs/OWNER_READINESS_HANDOFF.md
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

The private migration helper upgrades current Studies head0009 but reports0001, which
its supervisor and host release validator require. Make release evidence truthful and
qualify its coordinated consumers before any release activation can rely on it.
User authorizes continuing Scribeswell/shared integration work without routine stops.

## Boundaries & Constraints

Always preserve controlled migrations, restricted identities, actual commit evidence,
prior running application compatibility, bounded supervision and forward recovery.
Preserve every pre-existing working-tree change, including mixed platform files.
Never implement Access readiness, sharing, Notification, Leave or app-factory features;
change generated migration helpers; run startup migrations; deploy or activate production;
contact external services; expose DB URLs, raw diagnostics or business payloads.
Fresh uniquely owned local PostgreSQL17 fixtures only, with exact cleanup. KDG/Leave
ports/resources remain untouched. Existing corpus report and private opt-in stay compatible.

## I/O & Edge-Case Matrix

| Scenario | Expected result |
| --- | --- |
| Fresh or supported populated history | Actual before, committed after0009, fixed owner/recovery, no activation by helper |
| Repeat | before0009/after0009, preserved records and prior consumer reads |
| Failed/unknown migration or commit | No success artifact; activation refused; retained safe reconciliation evidence |
| Old0001/missing/foreign/duplicate/malformed/oversized report | Supervisor and host refuse before activation |
| Packaged history/expected release mismatch | Refuse success; never manufacture a matching revision |
| Private opt-in disabled | Existing public release contract/behavior unchanged |

</frozen-after-approval>

## Code Map

- New apps/scribeswell/deployment/studies_release_contract.py: pure app-owned build-time
  contract shared by worker, supervisor and host. Keep existing four fields, add observed
  nullable before. Closed success shape: complete, owner, before, after, recovery. Fixed
  owner/recovery; expected after0009, before only declared supported ancestor/current
  revisions or null. Tie pure revision declarations to actual Alembic history in tests.
  No extra runtime service, environment selector or public API.
- apps/scribeswell/studies-migrations/env.py: use ordinary Alembic current heads before
  and after under existing migration_transaction lock; reject multiple/unknown/history
  target mismatch. Publish attributes only after transaction exit/commit. Existing
  upgrade-head-only and restricted role/ledger safeguards remain.
- deployment/studies_migrate.py: consume validated committed attributes after actual
  command.upgrade. Do not call alembic current or return presumed success.
- deployment/migrate.py: reuse existing bounded strict_json parser/supervision; validate
  and persist actual private child report, not an invented expected object.
- platform/deployment/host-release.py: dynamically load pure app private contract as
  existing scribeswell_contract loads corpus release_profile; reuse bounded strict JSON
  parsing, validate actual private evidence. Preserve image SHA/digest/release binding,
  cleanup and all unrelated Leave/Access/Content changes. No generic release rewrite.
- deployment/Migrations.Dockerfile: include new pure contract. platform/deployment/
  registry.json: include new contract and all private revision sources0002–0009 in the
  existing migration compatibility fingerprint (individual file paths only).
- tests/test_personal_notes_release.py and platform/deployment/tests/test_host.py:
  characterize existing public/private supervision before edits, then actual-report
  persistence/refusal and host activation ordering. Preserve foreign tests/hunks.
- Focused app native report tests: use existing PostgreSQL17 fixture patterns, actual
  private worker/Alembic and restricted migrator. New fresh cluster or isolated database
  only; parent owns Docker execution. Reuse prior consumer/native fixtures where useful;
  do not weaken historical compatibility/rollback assertions or run full2500case suite.

## Tasks & Acceptance

- [x] Observe actual reporting acceptance red before behavior/contract changes.
- [x] Implement one pure contract, committed observations and coordinated consumers.
- [x] Synchronize packaging/fingerprint; test missing, stale, wrong-target, unsafe input
  and failure refusal with old public behavior retained.
- [x] Add real native fresh/previous/repeat/rollback/retry/report assertions and preserved
  data/previous-consumer proof. Agent runs focused tests; parent executes fresh native.
- [x] Record exact commands/results/failures and all five impact decisions. Preserve
  mixed-owner snapshots at app .local/private-report-20261027/before. No staging/commits
  by implementer. Parent owns review, canonical reconciliation and scoped checkpoint.

Given successful controlled upgrades, when worker and host consume evidence, then they
observe the actual committed head and reject stale/malformed/wrong-release evidence.
Given failure, no consequential activation is allowed and no automatic reversal occurs.

## Implementation Notes

No human-visible intent choice or irreversible external action remains: this is an
existing false report and coordinated local consumer correction. Private report grows
by one field; old false0001 evidence is stale for the new target, while the prior running
app and database contracts remain unchanged. Existing host SHA/image binding ties the
pure expected head to the release; no new deploy/config activation path is introduced.
Selected implementation/release recon Sol High; actual models/usage/compute elapsed
unknown. Prior dirty-main authorization applies; no routine approval stop.

## Spec Change Log

## Review Triage Log

Three independent context-free review layers completed against the scoped727-line diff: no supported findings, no deferrals. Capacity temporarily limited the third launch; it ran after the first returned, and triage waited for all3. Verification reviewer independently47tests passed13.43s and read actual native results.

## Verification

Persistent interpreter apps/scribeswell/.local/owner-integration-20261027/python/bin/python.
Focused pytest app report/release plus platform host/release/registry checks; exact
native command/environment documented by implementer. Parent retains private real URLs
only in ignored0600 files; safe evidence contains observed revisions, test status and
source hashes. Existing live signup proof remains separate; no default Access startup
or full production release claim. Full browser matrix/build unnecessary without UI change.


### Implementer handoff — 2026-10-27

Sources are implemented and frozen for parent native qualification and BMAD review.
The worker verifies packaged history against the pure release declaration and pins
`scribeswell_studies_expected_head` on Alembic Config. Ordinary head-only Alembic
retains frozen historical package behavior; current heads are observed under the
existing transaction/lock and published only after commit. No generated helper changed.
Supervisor persists the actual validated private object; host strictly parses and
validates it before activation, retaining safe successful `private_detail` only.
Image packaging/fingerprint include the contract and every private revision0001–0009.

Exact commands, requirement mapping, five impact decisions and recovery contract:
`apps/scribeswell/docs/PRIVATE_MIGRATION_REPORT.md`. Initial app/host characterization
23passed8.94s; acceptance red1failed/4passed1.83s; coordinated checks45passed12.36s;
final affected app/platform wrapper/release/registry run92passed/77native-skips30.10s.
Earlier90passed/77skipped38.74s preceded two private timeout/existing-evidence cases.
Native file `tests/test_studies_migration_report_native.py` collected6cases1.12s;
parent executes with private `SCRIBESWELL_NOTES_TEST_ADMIN_URL` on fresh PG17.
No actual native execution, owner readiness, external service contact, staging,
checkpoint, deployment or activation by implementer. Canonical reconciliation and
native results remain parent-owned. Existing shared before snapshots and added app/
release-test/doc snapshots remain under `.local/private-report-20261027/before`.
Selected implementation model/effort Sol High; actual model/usage/compute elapsed
unknown; no subagents. Safe implementation command/result/source hashes are retained
at app `.local/private-report-20261027/implementation-checks.json`.


Parent verification complete: six new native cases passed30.47s (runner39.60s),
historical migration/compatibility/permission case passed11.07s (runner22.12s), on
separate fresh PG17 containers.131checked sources unchanged; exact normal stops,
container/volume removal and ports32768/32769released. Parent affected92passed,
77other-native-skips30.41s; no skipped case claimed as native proof. Safe exact
commands/results/source pairs and initial red/green results are under
apps/scribeswell/docs/evidence/private-migration-report-20261027/. Canonical event471
adopts the load-bearing report contract as37thcompanion while preserving kernel,
11CAP and38acceptance rows. Shared-platform patch passes isolated cached apply;
checkpoint only owned app/evidence/spec plus exact own platform hunks. Existing
README/Access/other-owner working edits preserved. No push/deploy/activation.
Actual model/usage/compute elapsed unavailable; selected Sol High for implementation
and release reconnaissance, inherited reviews. No implementation repair loop or
review deferral; only initial third-review launch capacity retry. Native provider
wait durations are separately measured above. Default Access owner gate remains.
