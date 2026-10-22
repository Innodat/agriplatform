---
title: Remove legacy PtS exemption from organization grants
type: feature
created: '2026-10-22'
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: 311ea6d9a7b3bfd761773cdf87c11d69ca912fb6
context:
  - AGENTS.md
  - platform/docs/architecture/contracts/identity-access-execution-substrate.md
  - platform/docs/architecture/decisions/0052-pts-account-scoped-access-and-coordinated-adoption.md
---

<frozen-after-approval reason="standing bounded implementation approval and explicit unused-PtS simplification direction">

## Intent

Remove the unnecessary legacy PtS compatibility bridge from organization-grant storage.
ADR-0052 and the user's clarification permit upgrading unused PtS to the new infrastructure;
legacy organization-grant writes are not a preservation requirement. This item delivers
strict organization storage, not the separately coordinated account/PtS/Content cutover.

## Boundaries & Constraints

New Access0012 replaces the generated registry_permission bridge with a validated direct
(permission,scope_kind) FK to access.permissions ON DELETE RESTRICT and a global active
row CHECK requiring membership_id, created_actor_id, updated_actor_id and updated_at.
Revoked rows may retain partial unknown history but still require registered org permission.
Preserve original columns, IDs, values, existing positive/nonnil/finite constraints, keys,
RLS/ACLs and exact historical revisions. No exemption for any of the three PtS literals.
Incompatible data refuses atomically at11, without adoption/deletion/backfill. No business
DML, legacy-org-to-account reinterpretation or implicit permission registration.

Only isolated synthetic local verification. Preserve concurrent work, old receipts/history,
all data and Docker resources. No production/account/access/provisioning/deploy/pilot,
Leave/editor, dependency changes, new generator/service, reset/prune/cleanup or push.
Protected grant execution and effective readers remain later work. Keep existing denial
until coordinated replacement; no bypass or new writer authority. TS7.0.2 unchanged.

## I/O & Edge-Case Matrix

| Scenario | Expected behavior |
| --- | --- |
| Clean12; compatible populated11 upgrade/repeat | Exact12, original values/receipts preserved; bridge column absent |
| Unknown/account-scoped permission including all3 legacy PtS literals | Named direct FK23503 on complete active/revoked inserts/updates |
| Each active required field missing | Named global CHECK23514; no legacy exemption; existing structural guards retained |
| Revoked partial provenance; revival | Supplied values preserved with registered org permission; incomplete revival refuses |
| Permission updates and dependent/multirow failure | Same direct constraints; entire statement/transaction rollback |
| Incompatible populated11 migration | Exact11 data/catalog/history retained, explicit refusal; no normalization |
| Runtime/operator/definer raw writes | Actual existing restricted reads/RLS and write denials unchanged |
| Exact catalog/history/FK both ends/ACL/tombstone drift | Refuse without mutation; only expected dropped slot14 allowed at12 |
| Identity19 recognition of11/12 | Metadata-only selection plus full verification; no business/ledger reads |
| Bounded locks/failure/retry; source custody | Controlled rollback and forward retry, single-use proof and independent retained check |

</frozen-after-approval>

## Code Map

New migrations/versions/0012_strict_grant_integrity.py; mutable migrations/access_baseline.py
recognizes explicit11 and12 (all HEAD tuples audited). Only11 has generated bridge;
12 has direct constraints and exact expected dropped pg_attribute slot14. PostgreSQL keeps
a tombstone after DROP COLUMN; measure its exact native metadata, never waive arbitrary
columns. Registration metadata for11/12 remains10. Parameterize existing complete four-FK
trigger verifier and permissions-side inventory. Identity identity_baseline.py selects12
using schema-resolved direct FK metadata before generated11 marker, then full verification.
No Identity migration/reference or registration/catalog/client/SQL changes.

Reuse qualify_grant_registry_bridge.py helpers (inherits storage.Qualification; canonical
RI trigger suffix normalization only). Add qualify_strict_grant_integrity.py,
test_strict_grant_integrity.py and STRICT-GRANT-INTEGRITY.md. Existing native custody,
five command receipts and root bootstrap apply. Six cases clean/upgrade/refusal/drift/
failure/locks suffice; refusal intentionally remains11. Historical qualifiers may pin11
instead of current head; preserve their historical expected behavior and evidence.

## Tasks & Acceptance

- [x] Observe native acceptance RED before production edits; implement new controlled
migration, exact verifiers, focused tests/native matrix and owner runbook.
- [x] Execute fresh native matrix and separate retained check, three review lenses,
affected regressions/composers, requirement-to-test/five-impact evidence, normal stop
and scoped local commit, preserving all concurrent and historical work.

Given compatible organization data, controlled12 installs direct integrity without changing
business values. Given legacy unregistered PtS rows, it refuses preserving exact11. This
storage foundation does not claim effective account access or a completed PtS transition.

## Implementation Notes

Agent owns new migration, two mutable baselines, new qualifier/test/runbook and affected
mutable current-head unit tests. Small historical qualifier fixes may pin11 explicitly;
no old migration/reference/evidence edits. No DB/Docker/commit/agents/workflow. Root owns
native RED/bootstrap/evidence/handoffs/reviews/full checks/stop/commit. Agent may write
missing-feature tests first but must WAIT for root native RED before production edits.
Freeze/report bootstrap requirements. Root uses existing native run99b7231c-0a5b-4bdb-98e8-3329564c526a,
new private namespaces and four-group bootstrap templates from grant-registry-final-20261022.
All source/log/state custody remains strict. Standing approval covers spec and dirty tree.
Five impacts: extend existing owner scaffold; no UI/context/ADR change; update owner docs,
mutable substrate/DEVELOPMENT/KDG handoffs. ADR52 supplies existing authority. No intent gap.

## Spec Change Log

## Review Triage Log


| Finding | Verdict / route | Verified evidence |
| --- | --- | --- |
| Blind1 aggregate refusal does not independently prove each later bad row | false / reject | Diff already labels aggregate and explicitly disclaims independent later-row causation; functional separately tests every literal/shape by named constraint. No unsupported per-row claim. |
| Blind2 registered incomplete active migration refusal | medium / patch | Nonlegacy incomplete11 already refuses its CHECK, but explicitly registered legacy literals can bypass11 completeness. Isolate this admissible adversarial fixture and prove12 validation refusal; no production registration/adoption. |
| Blind3 successful registered permission update missing | medium / patch | functional only attempts failing permission changes. Add a second registered organization capability and successful transition with exact unrelated-value preservation. |
| Blind4 successful complete revival missing | medium / patch | All current revival examples are incomplete/refused. Add complete supported revival and exact stored state. |
| Blind5 revoked provenance removal UPDATE missing | low / patch | Inserts cover partial revoked rows, not supported nulling updates. Direct bounded update assertions cover this ordinary lifecycle state. |
| Blind6 heterogeneous compatible preservation missing | low / patch | Upgrade currently has one registered capability. Reuse the second capability from Blind3 in mixed active/revoked preservation proof. |
| Blind7 only first trigger on each FK end disabled | medium / patch | Native drift uses LIMIT1. Iterate all four discovered triggers independently with rollback and unchanged snapshots. |
| Blind8 collation OID100 assumption | low / patch | Exact measured native dropped text metadata includes100; supported pinned-image assumption is implicit. Document it; no new catalog abstraction required. |
| Blind9 full logical schema dump restore loses tombstone | low / reject expansion; direct documentation correction | Dropped slots are physical history and absent after recreation; current verifier intentionally requires exact native history. No dump/restore recovery is delivered/used here. Explicitly document that limitation and tested rollback/forward-retry recovery; adding backup/restore tooling/matrix now is beyond a direct correction and not an everyday supported operation at this stage. Never recommend manual catalog repair. |
| Blind10 concurrent grant writer during migration absent | low / reject | Relation contention, complete transactional rollback and direct native INSERT/UPDATE constraints are tested. No protected runtime grant writer exists yet; another synchronized writer matrix adds machinery for a non-current path. Existing ALTER TABLE lock semantics remain, and no concurrent-release/production sizing claim is made. |

Edge-case and verification-gap lenses returned no findings. Eight direct proof/document
corrections in seven patch groups (Blind3/6 share second-permission fixture) go to the
same implementation agent; no production DDL/verifier intent change or new deferral.

## Verification

Use platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python.
Focused TDD first; root actual native --all then separate --verify-retained, Access tests +
PtS release + migrate adapter with plugin/cache disabled, both composition modes.
Private bootstrap consumes retained registry/org-storage credentials/run/config; record this
existing preparation dependency, never claim portable CI or expose secrets. Retained proof
must bind generated_inputs, source/log/state digests before inspection. No repeated lifecycle.


Pre-review matrix audit: all10 rows map to executed methods in owner evidence. Fresh
strict-grant-proof-20261022 passes all8 native stages. Actual incompatible aggregate
remains11, others12; original13 values and five command receipts survive compatible
upgrade/repeat. Focused55 and1484 affected regression tests pass; both composers exit0.
Independent retained check, review and final stop/commit are tracked below. No production
error classification changed. Source freeze holds until coordinated review correction.


Post-review: same implementation agent patched qualifier/runbook only;12 focused checks
PASS. Fresh strict-grant-final-20261022 passes15 native recorded stages and separate
read-only retained verification, binding120 sources,33 owned logs/transition diagnostics
and retained-state digest. All10 matrix rows have executed passing coverage; global
migration CHECK refusal additionally uses isolated admissible legacy11 shapes. Eight
direct review proof/doc corrections addressed, no new deferral; DDL/verifier bytes equal
pre-review proof. Final regression/composition/stop/commit still pending below.


Final affected regression1484 PASS48.67s; both composition modes exit0. Final audit binds
53 preserved historical files,74 unchanged production/client sources, two intended
mutable verifiers plus new0012,120 proof sources/33 generated diagnostics/state digest,
frozen intent and concurrent observed bytes. Normal stop retains all data/resources;
exact17-file scoped local commit follows. No new deferral, real access/production action
or push. Full logical schema restore remains explicitly unqualified; this item proves
transaction rollback and controlled forward retry only.

Normal native stop completed/runtime_ready=false; data and volumes retained.
