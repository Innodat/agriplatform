---
title: 'Isolate the Scribeswell owner integration fixture'
type: 'chore'
created: '2026-10-27'
status: 'done'
route: 'dispatch'
baseline_commit: '02ffd98c7568158be50b8ed3c2f86d0488ef0c52'
review_loop_iteration: 0
context:
  - /home/ck/repos/innodat/agriplatform/AGENTS.md
  - /home/ck/repos/innodat/agriplatform/apps/scribeswell/docs/STUDIES_OWNER_INTEGRATION_EVIDENCE.md
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

Run Scribeswell's actual Access/Identity integration independently of KDG and Leave. The user explicitly selects a dedicated disposable Scribeswell fixture using Auth55491/database55492, with availability checked immediately before startup. Preserve every other owner's running environment and existing working-tree changes. Continue without routine approval stops under the user's existing authorization.

## Boundaries & Constraints

Always use the existing platform native lifecycle, exact target/run markers, fresh canonical UUID and run-owned process/resource cleanup. Ports and all run/network/container identities must be separate from KDG and Leave. No arbitrary runtime port overrides or adoption of retained runs. Keep schemas closed and reject changes to fixed target ports. Preserve the current KDG configuration bytes and Leave behavior. Controlled app and Access migrations operate only in the new disposable database, never another environment.

Never implement Access services, Leave or factory features, change global Auth/signup behavior, mutate existing owner fixtures, alter product contracts or claim signup/sharing/device/release acceptance. No push or deployment. This slice establishes the fixture and fresh owner integration; keeping a manual environment alive is separate. Shared platform files already contain foreign Leave changes: patch additively, preserve their exact prior content and do not include foreign hunks in a local checkpoint.

## I/O & Edge-Case Matrix

| Scenario | State | Expected behavior | Failure handling |
| --- | --- | --- | --- |
| Independent target | Scribeswell target | Dedicated namespace/project, Auth55491/DB55492 and other nonoverlapping ports | Closed target validation |
| Concurrent owners | KDG55481/2 occupied, Scribeswell ports free | Scribeswell port preflight succeeds without touching KDG | No broad stop/reset |
| Collision | Any declared Scribeswell port occupied | Refuse before prepare/start | Existing listener untouched |
| Wrong DB | Status reports KDG DB55482 | Refuse before owner migrations | Safe fixed error |
| Normal integration | Fresh isolated fixture | Existing full real-owner HTTP/browser/SQL assertions execute | Exact-run cleanup even on failure |

</frozen-after-approval>

## Code Map

- platform/deployment/native_cli.py: existing validated target selection, namespace/run_path, network labels/loopback/subnet verification. Extend explicitly for scribeswell-local; preserve Leave additions already dirty.
- platform/deployment/dev.py: shared configuration renderer; ordinary native dispatch bypasses historical KDG interceptor. No generic schema/config rewrite needed; keep KDG bytes unchanged.
- New platform/deployment/environments/scribeswell-local.json and schema/scribeswell-development-target-v1.json: closed target, owner_ids identity/access/scribeswell, short agri-scribeswell project prefix (38characters including UUID), own namespace, explicit distinct subnet10.254.27.0/24 subject to host preflight. Fixture reference may point to the actual app-owned studies_owner_fixture.py, registry stays shared. No secret references to KDG runs.
- apps/scribeswell/tests/studies_owner_fixture.py: currently hardcodes KDG target/run path/ports/adminDB/URLs. Switch to Scribeswell target; prefer derive values from validated target, including extra AccessHTTP port8193. Planned web5192/API8192/owner8193/shadow55490/Auth55491/DB55492/studio55493/mail15494/TLS8447.
- apps/scribeswell/web/playwright.owner-integration.config.cjs and web/tests/studies-owner.integration.cjs: align selected fixture baseURL, keeping original authority/privacy/linkage/retry/deletion assertions unchanged.
- platform/deployment/tests/test_native_cli.py and apps/scribeswell/tests/test_studies_owner_integration.py: existing lifecycle/cleanup/port/SQL oracle tests, extend focused isolation and wrongDB coverage. Do not weaken existing marker/source protections.

## Tasks & Acceptance

- [x] Observe failing acceptance for dedicated target, namespace/ports and wrong database before implementation; preserve exact commands/results in app-owned evidence.
- [x] Add closed Scribeswell target/schema and additive native lifecycle support; preserve existing KDG/Leave targets and configuration behavior.
- [x] Adapt app fixture and browser URL references to dedicated configuration, keeping its actual owner/browser/independent SQL oracles and exact cleanup.
- [x] Run focused platform/app regression. Recheck host ports/subnet, then parent executes actual fresh owner integration with explicit pinned CLI/Python and new UUID/proof directory. Record failures honestly; no fixture bypasses or skipped acceptance claims.
- [x] Record docs, scaffold, shared-UI, agent-context and ADR impact; prepare scoped local checkpoint excluding foreign shared-file hunks.

Acceptance: Given independent available ports, when real-owner qualification runs, then it completes existing browser/HTTP/database assertions with Auth55491/DB55492 and releases only its own resources. Given a collision/wrong DB, then no existing owner state is mutated. Given unchanged KDG/Leave inputs, their selected configuration and lifecycle tests remain passing.

## Implementation Notes

No user-visible intent gaps; target naming/other port choices are ordinary technical decisions. No irreversible external action: fresh owned disposable state only. Shared footprint is bounded to native lifecycle extension plus closed target/schema/tests; preserve pre-existing dirty versions at /tmp/scribeswell-isolated-before. Agent runs focused tests only; parent runs native integration after review. No platform source rewrite or new lifecycle.

## Spec Change Log

## Review Triage Log

## Verification

Use /tmp/scribeswell-implementation-python/bin/python for pytest and explicit existing pinned Supabase2.120.0. Focused tests require host subprocess/socket permissions. Parent integration command uses apps/scribeswell/tools/py/qualify_studies_owner_integration.py --run-id NEW_UUID --supabase ABSOLUTE_CLI --proof NEW_PRIVATE_TMP. Do not emit private status, DSNs, keys or business snapshots. Retain only selected safe evidence in tracked docs. Platform/app shared regression plus native result are separate; no full1176browser repeat for fixture-only change.

### Review dispositions

All three BMAD lenses completed before triage. Host thread cap allowed one new reviewer at a time, so launches were sequential after prior completion; no finding decisions or patches occurred until every lens reported. Edge and verification lenses returned no findings.

| ID | Verdict / route | Evidence and disposition |
| --- | --- | --- |
| B1 | medium / patch | Actual first isolated run started/up/verified then failed local Alembic dependency; exact wrapper stop succeeded but read-only Docker inspection proves its empty network still reserves10.254.27.0/24. Add Scribeswell-only verified-empty exact network removal after stop, keeping legacy KDG/Leave semantics unchanged; verify sequential fresh runs. |
| B2 | medium / patch | select_database accepts target DB paired with arbitrary api_url; subsequent Auth admin calls use it. Validate fixed selected Auth origin before owner writes; mixed DB/provider status test must refuse. |
| B3 | medium / patch | New class disables base permission test because it names KDG paths. Add equivalent Scribeswell-namespace readable/writable ancestor behavior coverage without changing foreign Leave tests. |
| B4 | medium / verification patch | Socket double establishes only selected preflight ports. Parent actual integration and before/after foreign-container identity/target hashes provide separate real coexistence evidence; do not call the double full lifecycle proof. |
| B5 | false / reject | Existing actual browser/HTTP integration exercises selected Auth redirect, real Access admission, application writes and browser roundtrip together; planned parent execution is the covering acceptance, not only new constant tests. No extra duplicate startup-mirroring test needed. Until parent run passes that acceptance remains pending. |

First native attempt exit1/32.32s: wrapper prepare/up/verify all passed on dedicated ports, owner migrations could not start because python -I could not import Alembic from user-site dependencies; no browser pass inferred. Exact stop succeeded/no forced process termination, own empty network retained as B1 red. Prepared /tmp-only venv .pth explicitly references existing local dependency installation; isolated import check now passes. No global Python files changed.

Native second35.45s failed safe generic Identity migration guard. Consume documented preferences bootstrap;1focused red/green passed. Third45.15s reached Identity25 and failed capability_reader_role_unsafe. Owner CURRENT-ACCESS.md requires the private capability reader role and sole restricted migrator edge before Identity25, then Access18. Consumer fixture now prepares it exactly and temporarily revokes/restores the edge around historical exact-two-edge reader preparation;2focused tests passed. No service or migration changed. Session continuation lost /tmp, including third raw evidence; selected first/second failures were already archived in repository. Third observed result remains a clearly labelled parent summary, not recreated raw proof. Restored only /tmp Python using offline RECORD-verified pure psycopg/rfc8785 and explicit existing local dependency path; isolated imports pass.

Resume/environment evidence: temporary Python and private /tmp proofs did not survive session continuation. Native fourth39.33s failed driver import because the restored pure psycopg lacked distribution metadata; RECORD-verified metadata restored and SQLAlchemy engine construction passed. Native fifth52.8s passed owner migrations and started Access but failed Scribeswell import (missing psycopg_pool); its raw /tmp proof was lost on the next continuation, and only the labelled observed summary is retained. These are environment failures, not authorization or product behavior proof.

A Scribeswell-owned persistent ignored environment now lives at apps/scribeswell/.local/owner-integration-20261027, with private evidence also there. Offline packages and metadata copied only after RECORD SHA256 verification; existing local site dependencies remain read-only and global installs unchanged. Full Scribeswell API and Access imports passed before the fresh run. Native sixth currently running; no pass inferred.

Native sixth129.51s passed current owner migrations/Auth callback/enrollment/retry/autosave and private notes GET200; browser timed out60s before rename-before. Safe stages do not identify exact earlier navigation cause. Old reload code reselected a study after restoration; replace with explicit tool activation only when not already pressed, heading/outline confirmation, explicit note reopen and unchanged saved text. Native seventh74.42s confirms reload/tool/study restoration then exposed a newly introduced empty-list visibility assertion: empty ul has zero height before first note. Correct only that new helper check to attachment; retain visible heading, pressed tool, Add note and every original content/receipt check. Linked-note outline also has direct preview plus reference buttons; reuse already demonstrated final-matrix F3-F8 correction (direct first preview per li), preserving passage-link assertions. Syntax checks pass; fresh parent qualification pending.


## Final acceptance and handoff

PASS: fresh actual owner run d32a2c3b-715a-4783-b356-8a46356499a7 exit0/94.52s; workflow34045ms and disabled-denial4927ms pass, independent SQL/privacy/attribution/recovery unchanged,284source hashes unchanged. Parent113focused tests20.59s (runner21.89),10source hashes unchanged; actual safe diagnostic oracle and CJS syntax checks pass. All9Scribeswell ports released, exact network removed/no forced termination; KDG ports remain occupied and both other target files unchanged. Foreign containers changed21to15over a longer window with concurrent owners; no false claim all stayed running.

B1/B2/B3 fixed and focused/native verified. B4 actual isolated startup/qualification/cleanup plus endpoint/resource observations supplement the preflight double; B5 actual full workflow now passes. Supplemental old fixture assumptions were corrected without application runtime changes: explicit restored outline, empty list attachment, direct preview selection and full typed current URL oracle. Native sixth historical navigation cause remains unproved; ninth specifically localizes legacy URL assertion. Raw-loss limitations for third/fifth stay explicit.

All commands/results, prior failures, exact snapshots and scope limits are in apps/scribeswell/docs/STUDIES_OWNER_INTEGRATION_EVIDENCE.md and dated evidence. Canonical bmad-spec derivation passed coherence/preservation, keeping prefix/36companions/11CAP/38acceptance rows. Scaffold impact: reuse existing lifecycle with closed isolated target, no generator/factory work. Shared UI/agent context/ADRs unchanged. Docs updated. Private evidence and fully import-checked Python persist in ignored app-local directory. No owner service, Content runtime, production activation or push.

Local checkpoint excludes foreign shared-file hunks; additive shared platform patch remains reviewable alongside their existing owner changes. Canonical/README edits are preserved outside checkpoint as before.
