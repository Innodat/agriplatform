---
title: 'Qualify Identity retained-actor projection through a restricted native reader'
type: 'feature'
created: '2026-10-28'
status: 'done'
route: 'dispatch'
baseline_commit: '856ec0eb58df952813098fa4056bce4d7442121a'
review_loop_iteration: 0
context:
  - services/access/HISTORICAL-ACTOR-DISPLAY.md
  - platform/docs/development/migration-verification.md
  - apps/kdg-capture/docs/admin-next-readiness.md
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

Supply the missing Identity retained-actor SQL projection and restricted native reader
for KDG historical attribution. Implement the existing owner contract and prove
ON-1–ON-5 through an isolated synthetic PostgreSQL target and HTTP candidate.
The user explicitly approves synthetic native implementation, controlled migrations,
restricted roles and resources, preserving concurrent changes, and continuing without
slice-boundary approvals. This is a prerequisite; Story 3.1 remains incomplete.

## Boundaries & Constraints

**Always:** Use the existing Identity Alembic lane and actual current predecessor27.
Preserve prior migration/reference bytes and dirty work. Use a fresh isolated local
PostgreSQL17 target with synthetic data/credentials only, private fixture inputs,
source-bound proof, acceptance RED first, real restricted LOGIN allow/deny checks,
failed-upgrade rollback and explicit retry. Retain failed attempts/artifacts/resources;
stop only this delivery's owned processes normally. Keep source truth in the existing
owner contract and ON matrix; record exact commands/results and proof limitations.

**Never:** Access/run/copy/hash `apps/kdg-capture/migrations/tests/schema_fixture.py`;
touch retained targets; mount active `main.py`, package/configure production, provision
real accounts/keys, deploy/push, install dependencies, implement Leave/editor/device
work, automatically downgrade, introduce a second migration system or new global
catalogue whitelist. Native scratch Auth helpers do not prove GoTrue/provider lifecycle.

## I/O & Edge-Case Matrix

| Scenario | Given / when | Then |
|---|---|---|
| ON-1 | Restricted login reads selected retained/renamed/account-removed/System/Migrate/service/unknown IDs | Exact retained names/IDs; no live-account joins, inferred mappings, writes or cache; missing differs from failed read |
| ON-2 | Valid arrays or null/empty/duplicate/nil/oversized/multidimensional input; unauthorized logins and forbidden operations | Only bounded UUID projection succeeds; invalid input fails; actual raw-table/DDL/ledger/operator/foreign-owner access fails42501 |
| ON-3 | Original HTTP deadline, acquisition/statement/lock waits, repeated cancellation or cleanup failure | No late success/private diagnostic; bounded transaction/connection ownership and release; no reset budget |
| ON-4 | Qualified27 predecessor/previous consumer, upgrade/repeat, injected failure and reconciled forward retry | Data/old consumer preserved; failed attempt rolls back schema/ACL/ledger, activation blocked; retry succeeds |
| ON-5 | Native reader injected into existing isolated HTTP factory | Existing exact selected IDs/order/bounds/no-store/error semantics and generated freshness unchanged |

</frozen-after-approval>

## Code Map

- `services/access/identity-migrations/env.py`: existing single-transaction controlled
  migration runner; retain startup separation, safe failure and private ledger.
- `identity-migrations/identity_baseline.py`: currently dirty Identity27 head routing;
  extend minimally for28 without replacing concurrent changes.
- `identity-migrations/versions/0002_actor_registry.py`: migrator-owned actor table,
  retained mapping and deletion guards; persisted labels remain200 characters.
- `identity-migrations/versions/0027_people_setup_references.py`,
  `identity_people_setup_catalog.py`, `people-setup-reference.json`: current predecessor;
  preserve bytes, use existing reference convention rather than another verifier.
  Capture the current complete27 runner/source prerequisites before editing; its
  require-head postcondition prevents using the later28 runner to establish27.
  Use captured27 `upgrade head`, then current28 `upgrade head`. Record28 reference
  by exact source execution rollback-only on independently verified27, verify27 again
  after rollback, and publish exclusively; do not re-record historical references.
- `tests/qualify_studies_enrollment.py:clean_upgrade`: reusable scratch bootstrap SQL
  pattern only; never run its hardcoded retained target/helper unchanged.
- `actor_display_http.py`: injected Reader(selected UUID tuple, absolute deadline),
  private cancellation outcome wrapper, three-second operation; wire/parser unchanged.
- `services/access/.venv/bin/python`: inspected installed Python3.15.0/Psycopg3.3.6/
  SQLAlchemy2.1.4/Alembic1.20.0/pytest9.1.1/httpx0.28.1; no installation needed.
- `platform/deployment/.local/identity-actor-display/f6d496e4-d1eb-4a83-8c67-6bcfb3545fa6/`:
  root-captured baseline72 tracked diffs/992 prior sources and exact handoff suffix.

## Tasks & Acceptance

**Execution:**
- [x] `services/access/tests/qualify_actor_display_native.py` and
  `tests/test_actor_display_native.py`: guarded fresh synthetic fixture/proof and
  focused reader tests; observe actual restricted-login missing-function RED before
  implementation; retain native ON matrix, source hashes and failed attempts.
- [x] `services/access/tools/prepare_identity_actor_display_role.sql`: explicit
  restricted login preparation; no silent repair or embedded credential.
- [x] `services/access/identity-migrations/versions/0028_actor_displays.py`: fixed-path
  SECURITY DEFINER `identity.actor_displays(uuid[])`, established Identity owner,
  selected-ID read only; strip inherited EXECUTE defaults and grant only runtime.
- [x] `identity-migrations/identity_actor_display_catalog.py`,
  `actor-display-reference.json`, `identity_baseline.py`: integrate28 with existing
  controlled head/reference conventions; source-derived independent reference,
  targeted effective role/membership/schema-create/forbidden-access validation.
- [x] `services/access/actor_display_native.py`: explicit private connection dependency,
  bound UUID array, short read-only transaction, original acquisition/query/lock/unwind
  deadline and cancellation ownership; return only closed actor/name rows.
- [x] `services/access/ACTOR_DISPLAY_NATIVE_EVIDENCE.md`, owner runbook/contract and
  KDG readiness/handoff: exact proof, traceability, limits and next active-owner gate;
  append to concurrent docs safely and preserve prior handoff suffix.

**Acceptance Criteria:**
- Given the existing owner contract and source-bound predecessor, when all ON cases
  execute, then each matrix row has passing actual evidence at its stated boundary.
- Given unrelated prior files/diffs, when delivery finishes, then custody comparison
  shows only intended changes and preserves concurrent work and retained resources.

## Implementation Notes

- Final:126 focused reader/qualification/HTTP tests pass in5.18s;198 affected
  Identity/release tests pass in3.76s (one existing Starlette deprecation warning).
  Parent actual final native matrix passes ON-1–ON-5, now including nine unsafe
  authority cases. Strict TS7,109-case KDG aggregate proof, composition check-only,
  owner export and generated freshness pass. Generator sandbox subprocess failed;
  identical installed checker passed outside sandbox. No dependency installation.
- All four review findings fixed, independently patch-reviewed with no remaining
  supported finding or new deferral. Normal stop completed for only owned
  attempts2/3/4; exit0/no OOM and all three retained volumes verified. Initial /tmp
  startup capsule was unavailable on resume; persistent failures and source bindings
  remain, and documentation distinguishes historical observations from retained proof.
- Custody: within992 prior selected source files this delivery edited only the five
  planned existing files. Three generated KDG database-tool files and three builder
  tracked diffs evolved concurrently without this delivery's edits; preserve them.
  Exact prior handoff suffix remains intact. Local commit
  includes unchanged prerequisite27 migration/catalogue/reference/role preparation
  so28 has a complete history; concurrent People API/factory/export/deployment and
  other work stay outside the commit. Stage only this delivery and required DB27
  prerequisite; stage the28 runbook addition separately from its prior dirty notes.

- Resume checkpoint: first implementation agent was interrupted by a new user turn.
  It added only `tests/qualify_actor_display_native.py`; no projection/reader/head
  changes or native RED yet. Failed sandbox Docker start retained under
  `/tmp/identity-actor-native-20261028/`; interrupted approval did not execute.
- Parent now started fresh owned container through approved qualifier prefix, using
  `prepare27 --proof platform/deployment/.local/identity-actor-native/f6d496e4-d1eb-4a83-8c67-6bcfb3545fa6-attempt2`.
  Container startup succeeded. Captured27 `upgrade head` failed transactionally at
  revision20: `identity_catalog_mismatch:relations,role_memberships,roles`.
  Logs/argv/source hashes/private inputs are retained in that frame. Reconcile its
  synthetic bootstrap prerequisites against original qualification setup, then retry
  the captured controlled lane; do not change expected historical fingerprints.
  No retained target was touched. Keep the existing failed frame/resources and use
  safe, explicitly bound follow-on stages rather than rerunning create-only prepare27.
  Parent has not observed native RED or qualified27. Native implementation must follow
  that RED. Approved qualifier command prefix is now persisted for execution.

- Read-only prerequisite investigation identified a concrete inherited-authority
  probe: PUBLIC EXECUTE on legacy SECURITY DEFINER `identity.log_audit()` plus
  database TEMP may permit attaching it to a runtime-owned temporary table and
  writing audit rows. Native evidence must determine this; trigger return type
  alone is not a denial oracle. If confirmed, retain its RED and harden precisely
  the implicated legacy trigger EXECUTE ACLs in28 with existing-trigger compatibility
  proof. Preserve historical source/reference bytes; no global object whitelist.

## Spec Change Log

## Review Triage Log

| Finding | Verdict / route | Evidence |
|---|---|---|
| Edge: raw Psycopg DEBUG acquisition diagnostics | medium / patch | Installed Psycopg connect logs caught OperationalError before the reader can sanitize it; reviewer reproduced a private marker in DEBUG output with mocked acquisition. Suppress only this operation's raw driver diagnostics, preserving unrelated task logging. |
| Edge: omitted conninfo fields inherit process defaults | high / patch | PrivateConnection currently passes incomplete conninfo unchanged; reviewer demonstrated PGHOST supplying an omitted host. Required target/login inputs must be explicit and the selected runtime login fixed. |
| Edge: prepare27 captures28 without predecessor frame | medium / patch | Default source_root is current ROOT, now containing28, yet successful current-head upgrade is unconditionally recorded as27. Refuse unsuitable source before resource creation and verify the actual27 ledger before recording qualification. |
| Gap: foreign-owner SECURITY DEFINER guard untested | medium / patch | Eight native authority cases cover Identity helper execution and a foreign table, but none uniquely exercises foreign definer execution. Add one rollback-only executable foreign-owner definer case and prove verifier refusal. |

- Blind layer: no supported findings. All three lenses completed across two
  independent reviewers: runtime refused a third fresh review thread because its
  thread limit included the retained implementation agent. The blind reviewer
  finished that lens before running the verification lens, without reading claims.
  This is reviewer reuse, not a claim of three context-free reviewers. No lens was
  skipped. User's explicit automatic continuation applied; no extra slice approval.

## Design Notes

The established Identity owner can own this definer directly; no extra login or
account projection owner is required. Prefer an explicit Psycopg async connection
dependency without a new pool/package. Decide routine implementation details from
installed sources. New catalogue evidence follows the existing lane without expanding
it into a platform object policy. Synthetic Auth-stub transitions must be labelled as
such; separately record any unperformed real Auth lifecycle qualification.

## Verification

Run the smallest native acceptance failure, then focused reader tests and native ON
matrix; inspect actual results. Run affected Identity/HTTP/release tests, candidate
export/generated freshness, existing affected KDG aggregate proof and composition
check-only. Resolve exact installed tool commands in evidence. Independent three-layer
BMAD review and fixes follow implementation; no device/release completion claim.

- Planning: no unresolved user intent gaps. The user explicitly authorized automatic
  approval/continuation and working beside the dirty tree; approval checkpoint applied
  without another question. Migration/roles mutate only a new synthetic target.
- Dispatch selection: gpt-6.1-sol / high for migration, concurrency and native
  authorization work; coordinator model/usage/headroom unavailable. Investigation
  used gpt-6.1-sol / high. No implementation retries yet.
