---
title: Bridge organization grant registry integrity without legacy adoption
type: feature
created: '2026-10-22'
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: eda0bbbe09eca7b7908920b1ae0eae060694dbff
context:
  - AGENTS.md
  - platform/docs/architecture/contracts/identity-access-execution-substrate.md
---

<frozen-after-approval reason="standing bounded shared prerequisite implementation approval">

## Intent

Replace the three-PtS-only grant CHECK with compatible registry integrity so later
protected KDG assignment can store registered organization capabilities. Preserve the
three legacy PtS permissions exactly without inventing registry adoption or authority.

## Boundaries & Constraints

Access0011 adds a STORED generated nullable registry_permission text: NULL for exactly
pts.poetry.read/export/documents, otherwise the row's permission. Its composite FK with
scope_kind references access.permissions(permission,scope_kind) ON DELETE RESTRICT.
Replace grants_permission_check; retain all existing staged constraints, keys/defaults,
RLS/ACLs and original values. New nonlegacy active rows require nonnull membership_id,
created_actor_id, updated_actor_id and updated_at. Nonlegacy revoked rows may retain
unknown history, but still require registered organization permission. Existing positive,
nonnil and finite constraints remain. No Identity FK or inferred external verification.

This derived discriminator is temporary compatibility scaffolding: final direct FK/global
active-row integrity and its removal require coordinated legacy adoption. No data rewrite,
PtS account-grant implementation, registry backfill, real-account/access/deployment/pilot,
Leave/editor, dependencies, generator, runtime service, reset/prune, cleanup or push.
Existing command/client SQL stays unchanged; grant.assign execution remains unsupported.
Future protected assignment must exclude the three legacy PtS capabilities while v1
readers ignore membership/revocation. Reader/consumer activation remains independently gated.
Preserve concurrent documents, all historical frames/data and immutable migrations/references.

## I/O & Edge-Case Matrix

| Scenario | Expected behavior |
| --- | --- |
| Clean11; populated10 upgrade/repeat | Exact heads; original rows/IDs/text/time/receipts preserved, legacy discriminator NULL |
| Legacy three permissions, no registry | Existing INSERT/UPDATE/null provenance behavior retained across11 |
| Registered organization capability | Complete active row succeeds; discriminator equals permission |
| Unknown or account-scoped capability | Named FK23503, including revoked rows; no fallback |
| Active nonlegacy missing required fields | Named CHECK23514; positive/nonnil/finite safeguards retained |
| Revoked nonlegacy unknown provenance | Accepted only with valid registered org permission; unrevoking incomplete row refuses |
| Generated value override; alternate/multirow writes | Refused or same constraints; whole transaction rollback |
| Actual runtime/operator/command owner | Existing RLS/read-only boundaries; no new writer authority |
| Catalog/history/generated expression/FK/constraint/ACL drift | Exact preflight refusal without normalization; Identity19 metadata-only10/11 recognition |
| Bounded migration lock/failure/recovery; retained custody | Rollback, explicit forward retry; source/log-bound single-use aggregate and separate read-only verification |

</frozen-after-approval>

## Code Map

Extend services/access/migrations/access_baseline.py exact clean/1–10 recognition to11;
new migrations/versions/0011_grant_registry_bridge.py owns only local DDL. Update mutable
identity-migrations/identity_baseline.py bundle selection using schema-resolved generated
column metadata then full catalog verification, never Access business-row reads. Historical
0–10 SQL/Identity references, access_registration_baseline/catalog and env.py stay unchanged.
Reuse tests/qualify_application_register.py four-group loader/engine/migrate/command;
qualify_organization_application_storage.py privileged snapshots/safe failures, and
qualify_grant_lifecycle_storage.py behavior examples, not its pinned previous9 package.
Add tests/test_grant_registry_bridge.py and qualify_grant_registry_bridge.py, plus
GRANT-REGISTRY-BRIDGE.md. Small CASES clean/upgrade/drift/failure/locks suffices. Native
source custody binds consumed helpers, bootstrap/driver/Auth inputs and protected runtime
secret; no extra fixture framework or previous-source package. Unchanged actual client
bytes and five existing command receipts across10→11 establish compatibility alongside
old owner SQL. Root bootstrap installs Identity19/service actor; qualifier migrates Access.

## Tasks & Acceptance

- [x] Observe meaningful acceptance RED and focused TDD; implement local DDL/catalog/selector
and bounded tests/runbook, preserving all older sources and existing clients.
- [x] Fresh actual synthetic matrix, independent retained verification, three review lenses,
regression/composition, requirement/five-impact records, normal stop and scoped local commit.

Given existing PtS grants without registry entries, when controlled11 installs, then their
values and supported writes survive. Given a registered organization capability, when a
complete new grant is stored, then registry scope and required active fields are enforced.
Storage integrity alone never proves target validity, protected execution or effective access.

## Implementation Notes

No intent gap. Local synthetic migration is reversible by discarding only new disposable
fixtures; real migration is outside approval. This is additive schema plus replacement of
a restrictive CHECK with a narrow compatibility bridge, not final legacy cutover. Five
impacts: existing owner scaffold extended; no UI/context/ADR change; owner evidence and
mutable substrate/development/KDG handoffs updated. TS7.0.2 baseline unchanged.
Agent owns only new migration, two mutable baselines, new qualifier/test/runbook; no
DB/Docker/commit/agents/workflow. Root owns native RED, private fixture/evidence/handoffs,
reviews/full verification/stop/commit. Wait for root native RED before production edits;
focused missing-feature tests may be written first. Freeze/report bootstrap requirements.
Standing approval covers bounded spec and dirty tree; preserve evolving concurrent work.

## Spec Change Log

## Review Triage Log

| Finding | Verdict / route | Evidence |
| --- | --- | --- |
| Blind1 real private run read in unit test | medium / patch | read_bytes is mocked but source_snapshot reads retained run.json with read_text; mock the run document too so focused tests need no private fixture. |
| Blind2 dated bootstrap inputs undocumented | low / patch | Actual bootstrap consumes retained registry/org-storage credentials/run/config; document this existing private preparation dependency, without claiming portable CI. |
| Blind3 retained-state digest | medium / patch | Snapshot was compared with DB but not bound into results; pin its digest and refuse mutation before DB inspection. |
| Blind4 lock failure cause | medium / patch | Exit failure/elapsed alone can accept unrelated migration failure; assert selected safe migration-lock code and relation55P03 without raw errors. |
| Blind5 nonlegacy second-org runtime | medium / patch | ORG2 runtime rows were legacy only; add complete registered org2 row to the existing exact restricted runtime comparison. |
| Blind6 permission UPDATE recomputation | medium / patch | Only INSERT and direct generated override were exercised; cover transitions across legacy/registered/unknown with required-field/FK assertions. |
| Blind7 complete multirow FK failure | medium / patch | Existing multirow example hits active-field CHECK; add complete-provenance unknown permission to reach named FK and prove statement rollback. |
| Blind8 partial revoked provenance | medium / patch | All-null revoked example misses all-or-none regressions; independently omit each field while retaining supplied values and refuse unrevocation. |
| Blind9 referenced trigger side | medium / patch | Only a child-side trigger was disabled; test the permissions-side trigger as well. |
| Blind10 still-generated altered exemption | medium / patch | DROP EXPRESSION tests marker absence only; keep stored generation but change exemption to prove full expression verification through owner/Identity19. |
| Edge1 private run dependency in unit test | medium / patch | Same unmocked read_text as Blind1; fix once while retaining this separate verdict. |

Verification-gap lens returned no findings. Each claim was checked before grouping;
11 confirmed findings in10 patch groups. All are bounded documentation/qualification
corrections with no new public surface, product intent, production DDL change or deferral.
Same implementation agent re-engaged. The source-count mirror test for privilege SQL
will be removed; actual restricted native probes establish the required behavior.

## Verification

Use existing actor-command-zxycfmc4/owner-env/venv/bin/python under deployment .local/
identity-baseline. Focused tests first, then Access tests + PtS release + migrate adapter
pytest with plugins/cache disabled; both composition modes. Root fresh --all and separate
--verify-retained, protected/client/frozen/source/log audit and normal native stop.

Affected mutable current-head tests (including test_grant_lifecycle_storage.py and
other baseline/metadata fixtures discovered by focused regression) are also agent-owned:
retain their historical10 assertions while extending current-head expectations to11.
Do not weaken old-version or metadata-only verification to hide unexplained failures.

No data rewrite means no business-value DML/backfill/adoption. PostgreSQL may physically
rewrite/lock the grants table while adding the STORED generated column; the existing
bounded controlled migration route applies. Synthetic proof makes no production sizing
or zero-downtime claim. Preserve original columns/values, allowing the derived column.

Existing lifecycle qualification helper SQL may be adjusted only to select explicit
writable grant columns for privilege probes now that a generated column exists; preserve
42501 expectations and old-version behavior. No historical migration/reference changes.

Pre-review matrix audit: all rows mapped to executed native methods in owner evidence.
Seven native stages and separate retained inspection pass;30 focused checks,1469 affected
regressions and both composition modes pass. Review/final stop/commit remain.

Final reviewed verification:13 focused bridge checks,1472 affected tests in37.69s,
eight native stages, separate read-only retained inspection and both composition modes
PASS. All116 source/21 generated diagnostic bindings and retained-state digest match.
Post-review expression restoration mismatch was measured as generated RI names only;
diagnostic canonicalization preserves all semantic fields/counts/user names, with focused
adversaries. Production DDL/verifiers stayed byte-identical through review. Eleven
findings patched, no new deferral. Native run stopped normally/data retained;52 protected
historical and73 unchanged production/client sources preserved, plus exactly2 intended
mutable verifiers and new0011. Exact15-file scoped local commit follows final audit.
