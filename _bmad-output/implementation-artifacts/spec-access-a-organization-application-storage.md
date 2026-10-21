---
title: ACCESS-A private organization application storage
type: feature
created: '2026-10-21'
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: fe2c333b71a6adb4518a13692a0f4bf25b269408
context:
  - AGENTS.md
  - platform/deployment/DEVELOPMENT.md
  - platform/docs/architecture/contracts/identity-access-execution-substrate.md
---

<frozen-after-approval reason="standing bounded shared prerequisite implementation approval">

## Intent

Stage private organization application admission storage through the existing Access owner migration. This structural prerequisite precedes external organization verification and protected configuration execution; it grants no access.

## Boundaries & Constraints

Access0008 adds only empty access.organization_applications: org_id UUID and app_id text composite primary key, application FK RESTRICT, enabled boolean NOT NULL default false, revision positive bigint NOT NULL default1, nonnil UUID created_by/updated_by and required finite timestamptz created_at/updated_at. org_id is nonnil/non-null. No cross-owner FK or claim that fixture organization/actors have been verified.

ENABLE and FORCE RLS. Only access_migrator has table privileges and a policy for exact selected org_id under transaction-local app.org_id; missing/other context sees no rows and cannot insert. No runtime/operator/command-owner policy or privilege. Reuse private statement guard registry_storage_immutable for UPDATE/DELETE/TRUNCATE including empty/noop, UPSERT and MERGE update arms. Later protected mutability requires its own migration. No seed data, command/authority/outcome/event whitelist changes, org verification/HTTP reader or execution support.

Keep exact clean/1–7 migration catalogs and immutable source pins. Extend explicit exact8 verification: structural definitions, ownership, ACLs including columns, policy, trigger scope/enablement, internal FK association/enablement, defaults, indexes, persistence and inheritance. Application inbound FK triggers change only at8. Preserve existing7 enablement behavior at7/8. Identity18 metadata integration may recognize exact8 without reading Access business/history rows; historical Identity migrations/references unchanged. Unknown states refuse before normalization; existing bounded serialization, rollback and controlled recovery remain.

Preserve existing registry/grants/receipts, original attribution, parser/adapter/CLI refusal, all retained resources/evidence and concurrent documents. No dependencies/generated files/generator, account/configuration/grants, consumer activation, production/provider/deployment/pilot, reset/prune, Leave/editor or push. Approved TS7.0.2 unchanged. Synthetic isolated preparation/verification and scoped local commit authorized; previous runtime evidence remains source-bound.

## I/O & Edge-Case Matrix

| Given / when | Then |
| --- | --- |
| Clean or populated exact1–7 / controlled upgrade | Exact8, empty new table, all previous data/receipts preserved |
| Owner inserts with matching org context | Same app across organizations and multiple apps per org accepted; defaults and exact references hold |
| Missing/wrong org context or nil/null IDs, actor/time/revision/FK/duplicate errors | RLS or intended named constraint refusal; complete rollback |
| Update/delete/truncate, empty/noop/UPSERT/MERGE or prior successful write in transaction | Fixed immutable refusal; all effects rolled back |
| Runtime/browser/operator/command owner read/write/DDL/owner assumption | Denied; no effective authority added |
| Populated exact8 / repeat; real Identity18 repeat | Catalog/data/ACL/receipts unchanged; owner boundaries preserved |
| Unknown history/catalog, policy/ACL/default/FK/internal trigger/guard drift | Refusal without repair or data normalization |
| Held migration/DDL lock or injected failure / retry after release | Bounded refusal and rollback, explicit recovery passes |

</frozen-after-approval>

## Code Map

Access root: services/access/.
- New migrations/versions/0008_organization_application_storage.py; existing migrations/access_baseline.py for exact8. Former HEAD comparisons must retain7. access_registration_baseline.py maps8 to unchanged7 SQL/catalog.
- identity-migrations/identity_baseline.py: verified_access_command_extension detects8 by relation metadata before7 routine detection, then fixed Access verification. No business/history reads.
- tests/qualify_application_register.py and qualify_application_set_enabled.py supply fixture/URL/timeouts/migration/snapshot/source custody. New qualify_organization_application_storage.py reuses these, adding complete cross-org snapshots via explicit admin observation. Root owns private preparation/native execution; preserve old frames.
- New tests/test_organization_application_storage.py; historical test_application_set_enabled.py, test_permission_register.py and test_entry_permission_register.py retain explicit historical revision assertions; only the new storage suite checks evolving HEAD.
- New ORGANIZATION_APPLICATION_STORAGE_EVIDENCE.md; mutable DEVELOPMENT/substrate/KDG handoffs. Historical evidence unchanged.

## Tasks & Acceptance

- [x] Characterize existing owners and observe storage acceptance RED before implementation. Root independently observes missing relation on retained exact7 before source edits.
- [x] Add additive schema/exact catalog and metadata compatibility using focused TDD; existing seven revisions remain accepted.
- [x] Add native storage qualification covering every matrix row, source/bootstrap custody, single-use --all and read-only --verify-retained; refuse optimized Python before fixtures/I/O. No new framework.
- [x] Record evidence, actual limitations and scaffold/UI/context/documentation/ADR decisions; root performs fresh native and regression proof before completion.

Given isolated synthetic storage staging, when all acceptance checks pass, then only private structural readiness is delivered. Existing organization input execution remains unsupported; all consumer gates remain.

## Implementation Notes

No intent gap. Standing approval covers dirty-tree continuation. Preservation: /tmp/org-storage-preservation.json. Private proof: platform/deployment/.local/identity-baseline/org-storage-20261021/. Root observed missing-table actual RED before implementation (root-acceptance-red.log), owns native preparation/proof, review/regression and commit. Agent runs no DB/Docker/resource operations, nested workflow/agents or commit; freeze before root proof. Bootstrap portability remains deferred.

## Spec Change Log

## Review Triage Log

| Finding | Verdict and evidence / route |
| --- | --- |
| Blind1: policy cannot attest GUC lifetime | low; current_setting accepts session settings too. Trusted owner helpers use SET LOCAL; the policy compares selected scope and does not authenticate a setting's lifetime. Patch documentation to distinguish caller discipline from RLS enforcement; no new authorization guard. |
| Blind2: final root results pending | low; implementation handoff correctly labels them pending. Root will record exact final fresh native/retained/regression/composition outcomes before completion. Patch documentation only. |
| Blind3: reproducible preparation command absent | low; exclusive private bootstrap_run.py plus copied bootstrap.py/bootstrap_identity18.py are retained and source-bound, but evidence omits their invocation. Patch exact preparation entry point and commands/limits. |
| Blind4: overlapping inserts absent | low; native sequential duplicate/scope checks and exact composite PK are present, but overlapping owner fixtures are not exercised. Patch a bounded same-key conflict and different-org overlap with exact results and retained state. |
| Blind5: negative Identity storage integration absent | medium; source-only unit stubs catalog verification; successful genuine Identity18 repeat proves recognition, while drift cases currently exercise Access only. Patch rollback-only malformed-storage verification under actual Identity role, preserving the snapshot. |
| Blind6: expand every exact-catalog branch mutation | low; representative policy/ACL/default/FK/four internal triggers/guard/persistence/history mutations already exercise native refusal. Exact verifier additionally rejects inheritance/rules/columns/ownership by direct catalog equality. Reject broader uncommon branch-matrix expansion requiring more fixture state and complexity; no demonstrated bypass. |
| Blind7: missing native unsupported configuration check | false; configuration refuses before database access. Current broad1314 passing checks include both input variants at adapter/CLI/public/direct workers with target/connection/dispatch traps. Adapter/parser/CLI sources and command whitelist are unchanged; database state cannot affect those branches. Final broad rerun remains required. |
| Blind8: failure frames overwritten on rerun | medium; second --all hits exclusive marker then overwrites failure-frames.json in outer handler. Patch unique exclusive diagnostic artifacts and preservation proof. |
| Blind9: missing fixture masks safe refusal | medium; handler writes into missing/unwritable fixture path and can raise before safe output. Patch storage-tolerant failure reporting and missing-fixture proof. |
| Edge1: rerun overwrites failure evidence | medium; same verified handler defect as Blind8. Patch with that group; retain a separate verdict row. |
| Verification-gap layer | No verification gaps found. |

Surviving patches: context wording; final results/preparation commands; bounded concurrency;
negative Identity integration; unique storage-tolerant diagnostics. No intent gap, new
public surface or new deferred issue. Existing bootstrap portability remains deferred.

## Verification

P=platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python. PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 P -I -B -m pytest -p no:cacheprovider: characterize impacted tests, focused RED/GREEN; root services/access/tests apps/pts/tests/test_release.py platform/deployment/tests/test_migrate_adapter.py -q. Both tools/py/run_compose_supabase.py --check-only modes (default; --identity-authority owned --no-seeds). Root fresh --all and separate --verify-retained through existing native target/restricted logins; previous adapter compatibility and genuine Identity18. Scoped whitespace/source/log/frozen/preservation audit. No root lint/typecheck claim.

Root audit chronology: native frame1 passed upgrades then exposed NULL-org RLS-before-NOT-NULL fixture mismatch; rollback-only diagnosis and separate constraint proof corrected the fixture. Broad2 HEAD assertions were obsolete; historical suites now retain revision checks while new storage suite owns HEAD. Frame2 passed storage/roles/drift/recovery/previous7/enablement, then exposed schema-name regclass resolution requiring forbidden Access USAGE for Identity. Catalog OID lookup correction preserves privilege boundaries; focused characterization observed RED then GREEN. Failed frames/logs are retained. Final fresh reviewed aggregate remains required.


Review patches completed and independently verified. Final reviewed frame
org-storage-reviewed-20261021:15 native stages plus separate retained inspection,
82 unchanged source bindings;1320 affected tests pass42.11s and both composition dry
runs exit0. Normal native stop retains data and runtime readiness remains false.
47 protected source hashes,85 previous-proof files and approved intent are unchanged;
concurrent files are preserved. Root final manifest records source/log/whitespace and
exact scoped commit custody. No new deferred issue; bootstrap portability remains
pre-existing. External org verification/configure execution remain next work.
