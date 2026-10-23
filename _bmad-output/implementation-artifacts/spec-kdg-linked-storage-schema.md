---
title: 'Define linked KDG capture storage schema candidate'
type: 'feature'
created: '2026-10-23'
status: 'done'
route: 'oneshot'
baseline_commit: 'dab8db749c49a29c5a59dc5de60e8df91d82a95c'
context:
  - '{project-root}/apps/kdg-capture/AGENTS.md'
  - '{project-root}/platform/docs/architecture/contracts/owned-write-and-secret-execution.md'
---

<frozen-after-approval reason="next authorized bounded KDG persistence slice">

## Intent

Add one unapplied owner Alembic revision candidate outside active versions, declaring
complete supporting storage parents plus linked capture/revision/outcome. This advances
the actual physical schema without applying a partial outcome-only migration. Use ordinary
SQLAlchemy/Alembic PostgreSQL DDL, not custom schema/ledger inventory checks. Given the
candidate is rendered through Alembic offline Operations, it emits its PostgreSQL DDL
without a connection. Given active migration discovery, head remains0001_kdg_foundation.
Actual PostgreSQL enforcement and authorized atomic writers remain consuming gates.

Storage: questionnaire stable org/id; immutable published questionnaire_version with
same-org questionnaire FK, display version, definition/hash and publication attribution;
child active/name<=200/revision/attribution; account-bound child_assignment with membership
instance/current active/revision; immutable child_eligibility reference recording org/
account/member/child/active observation/assigned-or-all context and issuance attribution.
Assignment unique(org,child,account) supports explicit renewal by changing membership and
revision, not implicit rejoin authority. Eligibility reference is opaque bounded text
(issuance<=200 codepoints); old references retain observed membership/revision, not an FK
to a mutable current membership value. No setup/admin/issuance workflow is implemented.

Capture has immutable org/id/owner account+actor/child/questionnaire/version/eligibility/
creator membership and original device timestamp string, mutable explicit observation
date/answers/positive bigint revision, server-managed actor/time attribution. Keep exact
accepted device string, not timestamptz-only normalization. Multiple child/date captures
remain allowed. Same-org composite FKs bind actual parents and original owner/history.
Operation outcome retains existing adapter columns, canonical scoped uniqueness and
compact JSON. Generated relational capture_id/result_revision derive from result, so
existing adapter INSERT/SELECT stays unchanged; same-org capture FK plus composite unique
linkage binds each immutable capture_revision to its exact outcome/executor/command/
operation/capture/revision. No-op outcomes need no new revision. Capture's current revision
has a deferred FK to history so incomplete capture/history cannot commit. No cross-owner
account/actor FKs or runtime identity registry.

UUIDs nonnil, versions/revisions positive, definition/answer/result object bounds;
server attribution/defaults and immutable-row/fact guards; FORCE RLS and narrow explicit
runtime grants based on verified transaction org/account/actor/mode. Outcome access stays
original-executor scoped even for all modes. Missing context fails closed. Parent creation/
management authority remains ungranted until protected consuming commands exist. No role,
schema or database creation, no seed rows, no delete/cleanup authority. Runtime cannot
mutate published versions, eligibility, outcomes or revisions. Operator bootstrap and its
fingerprint contract remain separate and gated.

Synthetic offline code only: do not register in active history or alter production env.py
command guards. Test actual Alembic offline rendering/no connections, no startup/API or
active-head change, unchanged outcome adapter compatibility and selected FK/policy output;
these are DDL/adapter smoke checks, never native constraint/RLS/durability qualification.
Observe missing linked-storage output first via ATDD and use focused tests before fixes.
No generic introspection verifier or alternate SQLite production/test architecture.

Preserve all concurrent work/history/Docker resources/dependencies including TS7.0.2.
No Leave/editor, real accounts/access, provisioning/deployment/pilot/production/cleanup or
fingerprint/HMAC work. Before promotion require native restricted-role/constraint/rollback/
concurrency/atomic writer/replay/current authority proof and ADR-0020 previous-code/migration
coordination, activation-failure blocking and recovery evidence.

</frozen-after-approval>

## Implementation Notes

bmad-help [BD] selected the physical storage candidate after completed command/receipt
boundaries. One reversible unregistered revision plus offline acceptance and owner docs;
no irreversible operation or user-visible design gap. oneshot route. Tables are app-owned
and parent workflows remain gated; no new shared database service, runtime engine or
generic verification layer. Existing native fixture custody is documented, but this slice
does not resume/mutate it or provision another target.

Scaffold: no change; KDG-specific schema, reusable migration controls already promoted.
Shared UI: none. Agent context: existing instructions sufficient. Docs: schema evidence,
owner contract, current handoff and migration guide; preserve exact historical handoff tail.
ADR: no new decision; adopts existing structure/attribution/release and ADR-0061 contracts.
Dirty-tree preservation authorized; /tmp/kdg-linked-schema-before.json records baseline.


ATDD observed missing linked DDL output before implementation. Focused smoke TDD observed
missing deferred snapshot declaration before correction. A test fixture initially matched
OR inside FOR; word-boundary correction preserves intended no-alternative-caller policy.
Review-focused RED observed4 missing guard/link/policy output cases; all passed after
specific fixes. Native enforcement is intentionally unclaimed throughout.

## Review Triage Log

1. **medium — patch:** own_write outcome INSERT lacked stored capture ownership check;
   FK target checks do not enforce the capture SELECT policy. Added explicit visible,
   same-org target EXISTS with own account or all_write scope. Offline output regression
   failed before correction; actual restricted-role behavior remains a native gate.
2. **medium — patch:** result revision could reference nonexistent history. Added deferred
   FK(org,capture,result_revision) to actual history. Existing revision permits legitimate
   no-op edit receipts; real mutation evidence still binds exact operation/executor.
3. **medium — patch:** history-only INSERT could fabricate an unused future revision
   without running capture-side deferred guard. Added history-side current snapshot/date/
   answers/device/editor check, complementing capture-side completeness for every change.
4. **medium — patch:** history/outcome initiators could disagree under nullable FK
   semantics. Added explicit IS NOT DISTINCT FROM comparison in append guard, preserving
   legitimate nullable initiator support rather than inventing account/actor FKs.
5. **medium — patch:** PostgreSQL accepts 24:00:00 normalization while input rejects it.
   Timestamp regex now bounds hour0–23 and minute/second0–59, alongside calendar cast.
6. **medium — patch:** btrim default spaces differed from Python.strip blankness. Explicit
   PostgreSQL trim-character predicate now uses the exact Python whitespace codepoints;
   focused parity test checks that finite set against retained Python isspace behavior.
   This checks blankness only and never normalizes stored content.
7. **low — patch:** snapshot smoke only checked trigger name/deferred declaration.
   Added assertions for actual snapshot lookup/comparisons on both sides and initiator;
   kept explicit that source rendering is not PostgreSQL enforcement qualification.

Final13 offline schema checks PASS; existing16 outcome and9 migration-foundation tests
PASS. No deferred findings. Active head/managed sources/dependency baseline unchanged;
all existing dirty/untracked paths retained. Five delivery impacts are recorded above.
