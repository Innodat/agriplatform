---
title: 'E1-ID-A: Verify the delivered Identity migration baseline for Leave'
type: chore
created: '2026-10-26'
status: done
route: dispatch
baseline_commit: 7c0e9319c8dc05cd51a3814d7753db0d3048ff81
review_loop_iteration: 0
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/platform/docs/development/migration-verification.md'
---

<frozen-after-approval reason="authorized continuation of the approved Leave handoff">

## Intent

**Problem:** Leave's next dependency is E1-ID-A. Existing KDG delivery already owns the Identity baseline and later privilege fixes, but Leave tracking has not verified or credited that evidence. Historical introductory documentation still describes privileges since tightened.

**Approach:** Reconcile the approved story with actual existing implementation and retained qualification. Verify source/reference/log custody and rerun focused current checks; correct current-state navigation and record honest requirement traceability. Reuse delivered owner work without a second history or unnecessary database setup.

## Boundaries & Constraints

**Always:** Preserve the dirty tree, historical migrations/references/receipts and KDG data. Use actual retained database proof distinctly from new CPU verification. Explain that revision0001 alone retained legacy vulnerabilities and later0008/0009/0010/0020 supply safety. Record the strict independent-of-ID-B acceptance question explicitly; never waive it or mark the story complete without a supported disposition. Keep normal development on shared KDG; destructive checks require the existing disposable Leave target and root-controlled setup.

**Never:** Rewrite applied migration history, change accepted ADRs, invent successful database requalification, rerun retained destructive fixtures, stamp/repair/adopt a live target, create another Identity service, install dependencies, commit or perform remote operations. No ID-B implementation or application activation.


**User-approved disposition — 2026-10-26:** Accept the existing hardened sequential
Identity history as Leave's foundation; no separate pre-ID-B history is required.
This does not complete ID-B or authorize live activation. User: “approve, next”.

</frozen-after-approval>

## Code Map

- `services/access/identity-alembic.ini`, `identity-migrations/env.py`, `identity_baseline.py`: separate Identity owner/history; guarded clean/adopt, source/reference pins, private ledger, bounded transaction and postconditions. Current head0021; preserve it.
- `identity-migrations/versions/0001_baseline.py`: pinned-source adoption plus legacy integration. `0008_profile_fields.py`, `0009_legacy_roles.py`, `0010_token_hook.py`, `0020_check_reader_bridge.py`: existing privilege fixes. No production source change is presently justified.
- `services/access/IDENTITY_BASELINE_EVIDENCE.md`, `PROFILE_FIELDS_EVIDENCE.md`, `LEGACY_ROLE_LOOKUP_EVIDENCE.md`, `TOKEN_HOOK_EVIDENCE.md`, `CHECK_READER_BRIDGE_EVIDENCE.md`: independently executed historical qualification, failures and final receipts. Inspect final source custody; later-source drift is not a historical proof failure or fresh current-head proof.
- `services/access/IDENTITY-MIGRATIONS.md`, `platform/docs/architecture/contracts/identity-migration-ownership-inventory.md`: add concise current-state qualification, preserving historical evidence.
- `tools/py/run_compose_supabase.py`, `tools/py/deploy_pts.py`: existing owned source selection and Identity-first failure gate; owned composer requires `--no-seeds`.
- `apps/leave/docs/implementation-plan.md`, `implementation-handoff.md`, `_bmad-output/implementation-artifacts/leave-sprint-status.yaml`: custom tracking. Leave story key `1-4-e1-id-a-establish-a-verified-identity-migration-baseline`.

## Tasks & Acceptance

**Execution:**
- [x] `apps/leave/docs/testing/e1-identity-baseline-evidence.md` -- map every E1-ID-A criterion to existing code and actual retained proof; separate confirmed coverage, limitations and open acceptance disposition.
- [x] `services/access/IDENTITY-MIGRATIONS.md`, `platform/docs/architecture/contracts/identity-migration-ownership-inventory.md` -- clarify current privileges and route without erasing historical records or changing other owners' docs.
- [x] `apps/leave/docs/testing/evidence/e1-identity-baseline-20261026.json` -- root supplies exact current focused command results and read-only custody audit; implementation agent links these as pending until available.
- [x] `apps/leave/docs/implementation-plan.md`, `implementation-handoff.md`, custom tracker -- record verified credit and remaining independent-ID-B issue accurately; retain in-progress until resolved, with no implied ID-B completion.

**Acceptance Criteria:**
- Given existing owner delivery, when inspecting it, then each story criterion has a precise source/test/evidence mapping and any unmet criterion remains explicit.
- Given historical qualification, when auditing retained files, then declared log/source/reference hashes are checked or drift is reported; historical execution is never presented as fresh current-head database execution.
- Given current source, when focused baseline/composer/profile/role/hook/bridge/release tests and both composer checks run, then exact results and any failures are recorded without weakening expectations.
- Given current docs, when reading their introduction, then privilege safety and supported owned/no-seeds route are clear, while baseline-only insecurity and independent-ID-B qualification are not concealed.

## Implementation Notes

Root owns private artifact auditing, tests and final machine receipt. Agent owns the two concise documentation clarifications and Leave evidence draft only; root updates tracking after review. No new behavior is authorized merely to manufacture a failing test: existing ATDD failures and final actual proofs must be cited.

## Spec Change Log

## Review Triage Log


| Finding | Verdict / route | Evidence and resolution |
| --- | --- | --- |
| Blind1 audit implementation absent | medium / patch | Private-only audit source prevented inspection. Machine receipt now embeds exact executable source, its hash and retained-artifact reproduction requirements. No public runtime surface added. |
| Blind2 dirty-tree test provenance | medium / patch | HEAD alone omitted tested working bytes. Repeated the same focused checks with90 selected file hashes captured before/after and unchanged; no database contact. |
| Blind3 cited frames versus audited frames | medium / patch | Profile/role/hook rows could imply separately checked custody. Each is now labeled historical owner-reported; current byte audit explicitly covers baseline and bridge only. |
| Blind4 baseline input anchors | medium / patch | Baseline source/journal claims lacked recorded input hashes. Receipt now records hashes of all five baseline audit inputs; known source commit/reference remain independently checked. |
| Blind5 resolved log provenance | medium / patch | Label/matched alone concealed which retained directory supplied a log. Receipt now includes each exact resolved path and expected SHA256; all30 actual logs match. |
| Blind6 environment provenance | medium / patch | Plugin environment and interpreter/dependency identity were missing. Source-bound repeat records environment, interpreter bytes/version and installed package versions. |
| Blind7 acceptance decision owner | low / patch | Open disposition lacked a concrete resolution owner. Evidence now assigns acceptance to user and records the pending choice; original criterion is preserved, no dependent work advanced. |
| Blind8 unspecified seed archival route | low / patch | New introduction prescribed an unspecified operation. Removed it and linked existing revision17 maintenance guidance; no new cleanup action or helper introduced. |
| Blind9 prose spacing | low / patch | Count/time concatenations obscured evidence. Corrected new evidence prose. Spec-only style changes are not an implementation finding under review workflow. |
| Root1 profile reference | medium / patch | Draft cited the earlier profile reference despite claiming final source. Replaced it with reviewed-source05ccb6afc5c546d18ea16747a59d4e63c6f8576718d885b43ecc03e676779868 from final owner evidence/current pin. |

Edge reviewer returned `[]`; verification-gap reviewer reported no gaps. All three
context-free same-capability lenses completed. All nine filed findings and root's
additional reference correction are resolved; no findings deferred. Initial slot limit
delayed the other two launches until the first reviewer finished; no review was omitted.

## Verification

Use the prepared Python3.15 owner environment at `platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python` with `-I -B`, `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`, `-p no:cacheprovider`. Run only `test_identity_baseline.py`, `test_identity_composition.py`, `test_profile_fields.py`, `test_legacy_roles.py`, `test_token_hook.py`, `test_check_reader_bridge.py` and `apps/pts/tests/test_release.py`. Run both composer check-only routes, owned with `--no-seeds`. Read-only audit uses fixed retained frame paths from owner evidence; never print private credentials or business rows. Broader repository, live adoption/provider and release activation are not qualified.

Reconciliation verification:300 focused tests PASS30.61s; both composer checks PASS.
Read-only custody:20 original Git files,7 source pins,30 baseline logs,29 hardening
logs,3 receipt anchors and43 historical19 Git files verified.172/178 historical
head20 inputs still match; six later drifts reported. No database contact/current
state requalification. All reconciliation tasks complete; actual story acceptance
remains in-progress pending explicit independent-ID-B disposition.

Final verification: 300 focused tests passed in 7.79 s, both composer checks passed;
90 selected source hashes were unchanged across verification. Audit source, original
audit-input anchors, resolved log paths/digests and Python environment are included
in machine evidence. Local link, JSON assertions and scoped whitespace checks passed.
Reconciliation and internal review are finished; spec remains in-review and story
in-progress pending the user-owned independent-ID-B acceptance disposition already
requested. No commit, database mutation or new runtime behavior.

Closeout —2026-10-26: user approved the concrete acceptance adjustment and next
dependency. ID-A accepted; custom tracker moves to review for the epic checkpoint.
Earlier pending-disposition statements above are historical. No new test execution,
database change, commit or live activation is implied by acceptance.
