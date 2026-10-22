---
title: Staged organization grant lifecycle storage
type: feature
created: '2026-10-22'
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: 7a565562c7b5086f2f7b432358f0048c45a47efc
context:
  - AGENTS.md
  - platform/docs/architecture/contracts/identity-access-execution-substrate.md
---

<frozen-after-approval reason="standing bounded shared prerequisite implementation approval">

## Intent

Stage the organization grant lifecycle fields needed by protected grant assignment,
through the existing Access controlled owner migration. This is compatible additive
storage, not effective access or grant execution.

## Boundaries & Constraints

Add Access0010 after9. Existing grants gain scope_kind text NOT NULL DEFAULT
'organization' with exact organization CHECK; revision bigint NOT NULL DEFAULT1 with
positive CHECK; nullable revoked_at timestamptz, created_actor_id/updated_actor_id UUID
and updated_at timestamptz. Nullable actors reject nil when supplied; new nullable times
reject infinity when supplied. No actor/time/membership inference or backfill. New
fields start organization/1/null; all original columns/rows/IDs/defaults/indexes/PtS
permission CHECK/membership constraint/forced RLS/policy/ACL/old owner writers remain.
No permission/Identity FK, effective-row CHECK, server revision/lifecycle guards or
scope activation yet: existing unverified rows cannot become effective authority.

Preserve exact known1–9 and add exact10 catalog/history recognition. Existing9 command
functions/ACLs/triggers stay byte-identical; Identity19 metadata-only Access verification
selects10 from staged column metadata then verifies exact bundle. No cross-owner row
reads or grants. Runtime remains SELECT-only under organization RLS; no operator/command
owner grant write authority. Original creation attribution/time, including historical
values, remains untouched. No dependency/generated/accepted ADR changes, roles/secrets,
new tooling/bootstrap framework, real data/accounts/access, production/deploy/pilot,
Leave/editor, cleanup/reset/prune or push. Preserve all failed/old proof and concurrent
work. Existing grant.assign execution and all dependent consumers remain gated.

## I/O & Edge-Case Matrix

| Scenario | Required result |
| --- | --- |
| Fresh through10; populated exact9→10 and repeat | Exact history/catalog; original row projection and receipts preserved, defaulted new fields; repeat data/catalog identical |
| Opaque IDs/text creators, all three legacy permissions, null/positive membership | No reinterpretation; supported owner INSERT/UPDATE defaults unchanged |
| Null/valid new fields, revision1/max, nonnil actor UUIDs, finite times | Owner fixture accepts without claiming verified actors or current membership |
| Zero/negative revision, wrong/null scope, nil actors, infinite new times | Named constraint/NOT NULL denial and whole rollback |
| Actual runtime different/missing org, write attempts; operator/definer raw writes | Same RLS visibility and write refusal; no new ACL |
| Held migration lock, injected failure, unknown history/catalog/ACL drift | Bounded failure and unchanged state; explicit forward recovery |
| Existing commands/previous9 receipts, Identity19 repeat | Same command behavior/outcomes and metadata-only verification; exact9 still recognized |
| Source change, repeated --all, retained inspection | Single-use fresh preparation, exact source/log custody; separate read-only retained proof |

</frozen-after-approval>

## Code Map

Under services/access: new migrations/versions/0010_grant_lifecycle_storage.py only DDL;
migrations/access_baseline.py extend verify_table and advance HEAD retaining explicit9
in every tuple/HEAD-sensitive configure branch; access_registration_baseline.py map10
to unchanged9 catalog; identity-migrations/identity_baseline.py detect pg_attribute
revision only after schema lookup. Existing mock selector tests must distinguish9/10;
never edit historical migrations or references. New focused test_grant_lifecycle_storage.py
and qualify_grant_lifecycle_storage.py reuse existing native owner qualification helpers,
snapshots/private four-group fixture protocol and safe failure reporting. Reuse consumed
helper source bindings, explicit baseline previous-source manifest/package and controlled
migration routes, not a second fixture framework. Bootstrap remains private root work.

## Tasks & Acceptance

- [x] Observe actual9 missing-field and focused acceptance RED, add10 and exact catalogs.
- [x] Prove every matrix row in fresh synthetic owner/runtime sessions, populated9/previous
  adapter preservation, rollback/recovery and independent retained inspection.
- [x] Run affected tests/composers/reviews, document requirement-to-test/five impacts,
  preserve custody/concurrent sources, normal stop and scoped local commit.

Given retained9, when controlled upgrade10 runs, then original grant values and effective
access behavior are preserved while exact staged storage appears. Given drift/failure,
when upgrade is attempted, then activation refuses without normalization/data changes.

## Implementation Notes

No intent gap. Synthetic migrations only; real deployment remains excluded. Smallest
coherent storage foundation includes fixed organization scope now to avoid another DDL
for that selected invariant. Shared UI/context/new ADR: none; existing owner scaffold,
runbook/evidence/substrate/KDG handoffs updated. TS7.0.2 baseline unchanged.
Root owns DB/Docker/preparation/old-source package/evidence/handoffs/final verification/
commit. Implementation agent owns code/tests/qualifier/owner runbook only, sequentially;
no DB/Docker/commit/nested agents/workflow. Stop after focused tests and freeze sources.
Private frame grant-storage-20261022 holds actual RED and runtime logs; root copies
organization-configure-accepted-20261021 bootstrap for fresh names, never mutates old
failed frames. /tmp/grant-storage-preservation.json binds51 protected sources/concurrent
bytes. Standing approval covers dirty-tree continuation and this bounded spec.

## Spec Change Log

## Review Triage Log

## Verification

P=platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python.
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 P -I -B -m pytest services/access/tests
apps/pts/tests/test_release.py platform/deployment/tests/test_migrate_adapter.py -q
-p no:cacheprovider; focused first. Both P -B tools/py/run_compose_supabase.py --check-only
modes (default; --identity-authority owned --no-seeds). Fresh native --all then separate
--verify-retained; root source/log/history/frozen checks and normal native stop.


Pre-review root native20 groups and independent retained inspection PASS,164 source
bindings match. Independent actual runtime two-populated-org read-only inspection also
passes. Affected regression1440 passed78.43s; both composition modes exit0.


| Finding | Verdict / route / evidence |
| --- | --- |
| Blind1 raw previous-client subprocess diagnostics | medium / patch / raw stdout/stderr persistence can retain unexpected driver diagnostics; emit selected safe failure fields and approved compact receipts only. |
| Blind2 package label and self-declared hashes | medium / patch / root independently verifies79 Git files, but standalone source_snapshot lacks an immutable inventory anchor; pin canonical inventory digest from exact baseline and test tampering. |
| Blind3 generated qualification logs not bound | medium / patch / only bootstrap logs are checked while runbook promises changed-log refusal; bind aggregate-generated logs and verify before retained reads. |
| Blind4 retained accepts other known revisions | low / patch / shared postcondition intentionally supports explicit older targets; exact10 retained label needs its own explicit head assertion. |
| Blind5 previous grant-writing client absent | false / reject / repository searches find no implemented previous grant writer; main.py only reads grants, operator grant execution remains unsupported. Supported owner SQL INSERT/UPDATE is already exercised before/after; do not invent a new client for a nonexistent path. |
| Blind6 runtime second org empty | medium / patch / root independent populated-two-org read passes but the repeatable qualifier uses an empty second org; populate both and assert exact sets plus context reset. |
| Blind7 Identity rejection of actual drift absent | medium / patch / owner catalog rejects drift but genuine Identity19 only sees valid catalogs; add restricted Identity runs against deliberately staged metadata/constraint/ACL drift, exact refusal-state comparisons and fixture restoration. |
| Blind8 INSERT optional/invalid values absent | medium / patch / UPDATE matrix alone does not prove insert boundary; add supplied-valid and named invalid INSERT cases with earlier-write rollback. |
| Blind9 grant relation lock not held | medium / patch / existing advisory test does not exercise ALTER TABLE lock wait; add bounded table-lock failure, unchanged9 state and explicit forward recovery. |
| Edge layer | No findings. |
| Verification-gap layer | No verification gaps found. |

All surviving findings are bounded verification/diagnostic patches; no intent gap,
new public surface, ADR change or new deferral. Preserve the pre-review passed proof
with its source diff; final native verification must use fresh source-bound preparation.


Final reviewed root acceptance:23 native groups, separate retained and independent
runtime read-only inspections pass;164 source bindings and32 generated-log digests
match. Canonical79-file previous package independently matches baseline Git. Focused12
passed0.96s; affected regression1446 passed46.07s; both composers exit0. All eight
surviving review findings patched; one disproved; edge/gap lenses no findings. No new
deferral. Five impacts and exact commands/custody are in owner evidence. Native normal
stop and scoped local commit conclude this bounded item; no real activation or push.
