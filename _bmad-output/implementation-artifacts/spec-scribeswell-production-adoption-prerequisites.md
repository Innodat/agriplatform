---
title: 'Studies production adoption prerequisites'
type: 'chore'
created: '2026-10-28'
status: 'draft'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '7eb27133a887b481e84b0c2f2ce2de5c5c112e55'
context:
  - 'apps/scribeswell/docs/STUDIES_TARGET_READINESS.md'
  - 'apps/scribeswell/docs/BOUNDED_STUDIES_ROLLOUT.md'
  - 'platform/docs/architecture/decisions/0052-pts-account-scoped-access-and-coordinated-adoption.md'
---

<frozen-after-approval reason="scope decision pending; existing routine BMAD checkpoint approval retained">

## Intent

Prepare a safe bounded private Studies release against the actual restored production target. Preserve public reading and saved data; stop activation on migration/readiness failure. A short maintenance window is acceptable, and a broad upgrade rehearsal is excluded.

## Boundaries & Constraints

**Always:** preserve unrelated staged/working changes. Keep existing production protections effective until coordinated replacement. Use owner-reviewed migration/permission contracts and explicit grants; preserve authenticated Expense helper behavior and existing corpus data/identities. Derive any new adoption reference from pinned synthetic bootstrap sources, never the production target. Keep rollback data-preserving and prefer verified forward recovery. Separate local/isolated qualification from production execution approval.

**Never:** infer account grants from legacy organization grants, fabricate readiness, bypass strict owner catalogues, temporarily reopen PUBLIC helper execution, silently add a legacy authorization facade, adopt the mixed Identity0027 worktree, publish or mutate production without concrete execution approval, or treat previous native success as target compatibility proof.

## I/O & Edge-Case Matrix

| State | Required behavior |
|---|---|
| Supported source-bound owner pair and compatible consumers | Eligible for concrete maintenance proposal after focused evidence |
| Actual legacy Identity/Access plus v1 PtS caller | Refuse release; resolve owner adoption and consumer scope first |
| Missing managed-role authority or qualification material | Refuse preparation; obtain explicit supported recipe/proof |
| Failed/unknown migration or readiness | No activation; preserve evidence/data and reconcile actual state |

</frozen-after-approval>

## Open Questions

- Should the Studies release work include the coordinated Identity/Access/PtS prerequisite? Include it: plan and implement the scoped owner adoption, explicit grants and compatible typed consumers, resolving corpus/Content boundaries under ADR-0052 before implementation. Keep Studies-only: complete this operational handoff and leave activation blocked on the separate owners. No production permission is granted by either scope choice. This was asked asynchronously; no answer has arrived.

## Code Map

- `apps/scribeswell/docs/STUDIES_TARGET_READINESS.md` and `docs/evidence/bounded-studies-rollout-20261028/target-readiness.json` — actual current target, source/image comparisons and blocked activation evidence.
- `services/access/IDENTITY-MIGRATIONS.md`, `identity-migrations/identity_baseline.py` — existing exact adoption excludes postgres-owned profile/PUBLIC-helper correction. New support needs an independently qualified profile and exact convergence, not comparator normalization.
- `services/access/migrations/versions/0012_strict_grant_integrity.py` — requires registered permissions and complete active grant provenance; no backfill for the three actual legacy PtS grants.
- `services/access/main.py` at reviewed `deb424b0c4d29016917c9df39b540a468ca8e1cf` and frozen image792933 — v1 deliberately returns503; do not alter the qualified runtime/archive to hide the mismatch.
- `apps/pts/backend/clients.py` at actual deployed `2480de173149cc646e8c1c55d088a93c4b196f47` — real image byte hash79eded confirms v1 dependency. Current PtS/Content adoption must follow accepted application/resource contracts.
- `services/access/tools/prepare_studies_runtime_roles.sql` — requires superuser; actual managed postgres is NOSUPERUSER/CREATEROLE. Needs specifically qualified capability-based preparation, not unconditional removal of guard.
- `apps/scribeswell/docs/MIGRATIONS.md` — public corpus already has an explicit ownership/role preparation contract; preserve legitimate defaults, importer and reader.

## Tasks & Acceptance

**Execution:**
- [x] `apps/scribeswell/docs/evidence/bounded-studies-rollout-20261028/target-readiness.json` — retain credential-free actual host/database and deployed/frozen consumer evidence.
- [x] `apps/scribeswell/docs/STUDIES_TARGET_READINESS.md`, `OWNER_READINESS_HANDOFF.md` — record exact blockers, current unchanged public availability and bounded next delivery.
- [ ] `apps/scribeswell/docs/STUDIES_TARGET_READINESS.md` — record human scope choice and applicable owner delivery order before changing cross-application behavior.
- [ ] `services/access/IDENTITY-MIGRATIONS.md`, owning PtS/Content application contracts — investigate and settle precise source-derived adoption and resource boundary if expanded scope is selected; then regenerate actionable implementation tasks in this draft.

**Acceptance Criteria:**
- Given live target metadata, when considering the existing candidate, then known consumer and owner mismatches prevent approval/activation.
- Given supported source-derived fixtures, when authorizing later implementation, then exact owner/consumer contracts and focused failure/recovery acceptance are recorded first.
- Given this investigation, when complete, then production data/configuration/runtime and unrelated local changes are preserved.

## Implementation Notes

BMAD investigation only; status remains draft pending the explicit cross-application scope question. Routine checkpoint approval does not choose a new application scope. No implementation/deployment or production SQL mutation occurred. Selected investigation model/effort Sol High; usage/elapsed unavailable. Temporary original current-head qualification/archive paths are unavailable; recover/reissue exact owner proof into durable protected storage, without relabelling older evidence. One rejected full-Compose export was replaced by an approved metadata allowlist, with no secret/configuration export.

## Spec Change Log

## Review Triage Log

## Verification

Executed read-only SQL with transaction_read_only=on; actual host image/public HTTP inspection; network-isolated frozen-image source hash comparison. Host books200/39; Studies404; no pending activation. Private raw records live in the ignored `apps/scribeswell/.local/release-preparation-20261028/` directory. No broad test/rehearsal or new production readiness claim.
