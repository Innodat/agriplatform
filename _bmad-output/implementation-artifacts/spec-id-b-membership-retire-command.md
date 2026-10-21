---
title: 'ID-B protected membership retirement command'
type: 'feature'
created: '2026-10-21'
status: 'done'
baseline_commit: 'eafb2432251a98f81623d2e287daba576b106451'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/platform/docs/architecture/contracts/identity-access-execution-substrate.md'
  - '{project-root}/platform/docs/architecture/contracts/e1-controlled-provisioning-and-evidence.md'
---

<frozen-after-approval reason="standing approval for bounded shared prerequisites">

## Intent

Deliver the existing membership.retire owner command for one exact organization/account/
membership/revision, with authorized server retirement, durable actor attribution,
immutable audit and scoped retry/outcome recovery. Use the delivered operator adapter,
CLI, protected authority and migration/reference tooling; this completes retirement,
not joining, account verification or downstream Access activation.

## Boundaries & Constraints

Derive executor from original session_user and protected exact command/org/account
mapping; recheck after serialization. Serialize the stable outcome namespace and exact
member before mutation. A changed request under the same operation conflicts; replay
returns its original committed result despite later state, only with current authority.
Use server time and existing revision guard, preserve immutable creation attribution,
legacy fields, roles and all other-owner data. Retirement and its event/outcome commit
atomically; no success before commit, missing outcome remains unresolved. Direct ordinary
retirement writes must refuse at the owner boundary; migrator remains controlled
maintenance authority. Preserve supported active seed/noop/unrelated writes explicitly.
Retain full uniqueness/partial index and all historical migration/reference bytes.
No rejoin, account creation/mapping, real authority/account changes, production migration,
deploy, reset/prune, Leave/editor, new framework/generator/dependency or push. Only
isolated synthetic migrations/fixtures are authorized; retain data/receipts/resources.

## I/O & Edge-Case Matrix

| Given / when | Then |
| --- | --- |
| Exact active member/revision and current retire authority | updated receipt target org/account/member, next decimal revision, event UUID; server deleted_at/updated_at and executor updated_actor_id; creation and legacy history retained |
| Missing/wrong org/account/member, stale revision or already retired under new operation | safe conflict, no membership/role/event/outcome effects |
| Exact replay, changed fingerprint, simultaneous retry, response loss | original receipt / conflict / bounded busy as appropriate; exactly one transition/event; scoped lookup recovers committed original |
| Missing/disabled/wrong command/org/target authority, revocation during wait | denial for execution and outcome, no leakage/effects; GUC/SET ROLE cannot impersonate |
| Ordinary UPDATE/upsert/multirow/INSERT supplies retirement | atomic refusal; equal retired values/noops and supported active seeds stay compatible; revival/retiming still refuse |
| Unknown receipt versions, invalid JSON/direct SQL canonical input, malformed worker response | safe verification/validation failure, no unsafe diagnostics or claimed success |
| Clean/adopt/exact15/repeat upgrade, drift/unknown history or injected DDL failure | trusted exact catalog, preserved original rows/history; refuse or rollback without normalization; recover through existing runbook |

</frozen-after-approval>

## Code Map

- services/access/identity-migrations/versions/0005_operator_authority.py: reuse current_operator_authority exact session binding and authority advisory lock.
- versions/0006_actor_command.py: preserve register_system and system_actor_outcome behavior; extend command evidence/checks/RLS through new0016, never edit old revisions.
- versions/0013_membership_retirement.py and0015_membership_actor_attribution.py: retain binding/history/revision/creation guards; new revision permits narrowly authorized command-owner retirement/update actor.
- services/access/identity_operator_input.py: existing strict RetireMembershipCommand parser; canonical_command and command_outcome_lock_key already cover complete retirement envelope.
- services/access/identity_operator.py and operator_cli.py: extend fixed SQL execution, typed member receipts and scoped outcome transport; keep actor invocation compatible. Outcome adds explicit --org-id/--account-id for membership.retire; reject missing/extraneous context before connection.
- identity-migrations/identity_baseline.py and tests/qualify_identity_baseline.py: extend existing head/reference chain/recorder; no parallel generator or reference bypass.
- tests/qualify_actor_command.py and qualify_membership_actor_attribution.py: reuse owner fixture, actual restricted credentials, lock witnesses, rollback/custody/source capture patterns. Previous head15 snapshot retained.

## Tasks & Acceptance

- [x] Observe actual15 missing retirement function/unsupported execution before implementation; add focused failing command/receipt/transport cases.
- [x] Add0016 protected SQL retirement/outcome, command-aware immutable evidence/RLS, least privileges and direct-writer protection; independent rollback-only reference.
- [x] Extend adapter/CLI with bounded safe typed execution and current-authority scoped lookup, preserving actor bytes/receipts.
- [x] Add focused tests and actual restricted-login qualification covering every matrix row, including concurrent conflict/revocation, rollback/event insertion failure, commit uncertainty, replay and lookup isolation.
- [x] Verify upgrade preservation/DDL failure/drift/repeat and previous actor regressions; affected suite and both composers.
- [x] Update owner runbook/inventory, KDG prerequisites/continuation and requirement-to-test evidence plus five impacts; complete independent BMAD review before local scoped commit.

Given authorized synthetic fixtures, when execution succeeds, then exactly one membership
revision and matching audit/outcome are committed with source-bound proof. Given any
failed transaction, when state is inspected, then memberships, roles and audit/outcomes
are unchanged. Given this delivery, when later joining/Access/WRITE/KDG is considered,
then their remaining gates are still explicit; this is not runtime completion of E1.

## Implementation Notes

bmad-help selects BD for the next ID-B increment. No intent gap: existing contracts
settle behavior; scoped outcome flags are an implementation decision. Irreversibles are
limited to authorized disposable synthetic DB work. Shared-schema/security footprint
requires dispatch and three independent reviews. Preserve dirty tree under standing
approval. Root records actual RED, then dispatches implementation sequentially. If
runtime verification cannot complete, retain in-progress with exact evidence rather
than claiming delivery. The agent may execute the existing synthetic tooling using
private prepared frames; never print credentials or reset/reuse committed fixtures.

## Verification

Use frozen owner Python at platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python. Smallest failing test first, affected suite
services/access/tests plus apps/pts/tests/test_release.py with PYTEST_DISABLE_PLUGIN_AUTOLOAD=1,
-I -B -p no:cacheprovider. Both tools/py/run_compose_supabase.py --check-only and
--identity-authority owned --check-only. Actual isolated local Supabase and owner
qualifier/reference recorder supply runtime proof; no root npm claim.

## Five impact decisions

Scaffold: extend existing owner command/migration/reference/tests, no generic framework.
Shared UI: none consumed. Agent context: existing rules sufficient. Documentation:
owner runbook, inventory, KDG continuation and this evidence. ADR:0020/0025/0035/0056
and accepted retirement contract apply; no accepted ADR edit or new product decision.
Dependencies unchanged, including TypeScript7.0.2.

## Spec Change Log

## Initial runtime preparation

Actual preimplementation RED: read-only head15 check passed; required retirement SQL
functions absent. Receipt and protected source manifest retained in
platform/deployment/.local/identity-baseline/member-retire-ggl0dn_m/actual15-red.json
and protected-before.json. Retained native Supabase is normally up for synthetic proof
(run99b7231c-0a5b-4bdb-98e8-3329564c526a); earlier data remains untouched. Prepare fresh
namespaced DB cases using the existing private bootstrap/previous-source route; do not
rerun the committed revision15 matrix. Previous reviewed frame is
platform/deployment/.local/identity-baseline/member-actor-review-fixes-9n3jhlhb/.


## Implementation evidence — 2026-10-21

Implementation is ready for independent review; status remains in-progress until the
root completes BMAD review and the scoped local commit. No reviewer was launched and
no commit was created by the implementation agent.

The preimplementation actual15 absence evidence above is retained. Focused ATDD RED:
`OWNER_PYTHON -I -B -m pytest -p no:cacheprovider services/access/tests/test_membership_retire_command.py -x`
failed at `test_retirement_uses_fixed_sql_and_returns_typed_receipt_only_after_commit`
with `command_unsupported`. After implementation, adapter/input checks passed44 tests;
adapter/CLI/retirement focused checks passed39, then117 affected focused checks passed.
The first broad run had941 passes and one obsolete head15-as-current expectation. That
expectation now verifies historical head15, with a separate explicit head16 final-head
check; no unexplained expected result changed.

Final affected command:
`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 OWNER_PYTHON -I -B -m pytest -p no:cacheprovider services/access/tests apps/pts/tests/test_release.py -q`
passed947 tests in32.47s. Five subsequently added reference-chain/drift cases were checked
with the focused retirement file:18 passed in0.60s. The broad suite was not repeated
for those test-only additions. Both `python3 tools/py/run_compose_supabase.py --check-only`
and `python3 tools/py/run_compose_supabase.py --identity-authority owned --check-only`
passed without writing composed files. OWNER_PYTHON is the frozen executable selected
in Verification above; no dependency change or root npm verification claim.

Actual proof uses fresh namespace ret16a_ in retained native run
99b7231c-0a5b-4bdb-98e8-3329564c526a. The frame is
`platform/deployment/.local/identity-baseline/member-retire-ggl0dn_m/`.
Fresh scratch DBs were prepared through copied/adapted existing private scripts;
head15 source was captured from eafb2432251a98f81623d2e287daba576b106451 and verified
before execution. Original frames and native data were retained. An initial sandbox
connection attempt failed before DB creation (`connection is bad: no error details
available`); the authorized local-network invocation succeeded. No fixture reset or
reuse of a previously committed matrix occurred.

`IDENTITY_QUALIFICATION_DIR=FRAME OWNER_PYTHON -I -B services/access/tests/qualify_identity_baseline.py --record-membership-retire-command-reference`
passed the existing independent rollback-only recorder, checking each historical catalog
through15. New reference SHA256 is
71bd766de85d53269c7f972851442eacdfea45f4d785589d42abb3d2a38ec488.
Historical revisions/references remain byte-identical; immutable-preservation.json
verifies33 protected historical source/reference/root instruction/dependency files.
The reference recorder retains its captured migration/helper/source hashes. Final runtime
source-capture files bind before/after implementation sources to the retained final proof.

The actual command was
`IDENTITY_QUALIFICATION_DIR=FRAME OWNER_PYTHON -I -B services/access/tests/qualify_membership_retire_command.py`
followed once each by `--additional`, `--matrix`, `--recovery`, `--fresh-race`, and
`--verify-retained`. Every stage passed; logs are actual-qualification.log,
actual-additional.log, actual-matrix.log, actual-recovery.log, actual-fresh-race.log and
final-retained.log. identity-qualification.json retains individual safe stages/results.
These mutating stages are single-use; review may use --verify-retained without rerunning
committed fixture setup. Native Supabase remains running; all resources/data/receipts stay.

| Requirement | Verification evidence |
| --- | --- |
| Exact active member/revision, server actor/time, legacy creation/roles retained | actual restricted-commit/replay case; typed retirement tests |
| Missing/wrong target, stale/already-retired new command; no partial effects | actual deny/state comparisons before/after; wrong account/org lookup denial |
| Same/changed retry and simultaneous first execution | actual lock witnesses for fresh identical first execution and committed identical/changed retries; one revision/event/outcome |
| Scoped recovery, response loss, no success before commit | actual LostConnection commits then drops acknowledgment, safe unavailable, original lookup/retry; unit commit uncertainty |
| Missing/revoked/disabled/exact-target authority and revocation during wait | actual restricted sessions, protected mapping changes only in synthetic DB, real blocked backend witness, recheck denies |
| GUC/SET ROLE/raw DML cannot impersonate | actual scoped outcome under forged GUC/search_path; role/raw table refusal |
| Ordinary retirement UPDATE/upsert/multirow/INSERT; active seed/noop compatibility | actual rollback-only service_role lanes; old one-way guards retained |
| Evidence insertion failure rolls back membership/outcome | actual injected event trigger failure with identical before/after state/catalog |
| Invalid direct canonical input, malformed/unknown receipts | actual IC005 canonical forgery refusal; focused strict typed/worker receipt cases |
| Clean/adopt/exact15/repeat, unknown/drift, injected DDL failure/recovery | actual upgrade matrix, original rows/ledger/other-owner references preserved, catalog chain matches; marker proves DDL failure fired |
| Previous actor registration remains compatible | actual restricted actor registration, replay and outcome lookup plus prior unit regressions |

The new migration does not remove full uniqueness or historical references. No joining,
account verification/mapping, downstream Access/WRITE/KDG implementation, production
migration, deployment, reset, prune or push was performed. Five impact decisions above
remain unchanged; runbook, ownership inventory and KDG continuation now link this proof.

Root diff inspection confirms the declared owner footprint and historical source custody.
The KDG continuation now points to this pending-review item. Review completion/local
commit remain unchecked; no dependent item is authorized by passing these tests alone.

Root independent focused adapter/CLI/retirement verification:85 passed1.94s.
Read-only retained-state/catalog consistency qualification passes. Scoped unified diff
includes every new source/reference/test and excludes concurrent unrelated work;
git diff --check passes. Independent three-lens review starts from this snapshot.


## Review Triage Log

Three fresh context-free reviewers completed: blind ten findings (126.051kB floor10),
edge-case [], verification one pre-verified gap. Each is classified before grouping.

| Finding | Verdict and evidence | Route |
| --- | --- | --- |
| B1 other lock waits should be busy | false: delivered adapter/actor contract intentionally maps only exact retry-namespace wait IC001 to busy; other lock/statement waits are unavailable, preserving uncertainty. Existing test_only_exact_outcome_wait_is_busy_and_no_error_chain asserts that distinction. New SQL follows it. | reject |
| B2 lookup revocation during wait | medium: execution waiter proof exists; no actual committed-outcome lookup waiter is revoked before its post-lock authority check | patch |
| B3 mismatched member under alternative authority | medium: current wrong-scope/account tests deny before exact row binding; later authorized alternative account reuses committed operation and exercises fingerprint conflict | patch |
| B4 distinct first operations race | medium: fresh_race uses identical operation IDs; independent IDs sharing the member revision are not behaviorally qualified | patch |
| B5 exhausted revision | low: SQL explicitly conflicts on maximum revision; current qualification does not execute this boundary | patch |
| B6 expected-target transport validation | medium: validator compares expected target but tests only command variant, leaving wrong org/account/member responses unverified | patch |
| B7 successful native CLI retirement/recovery | medium: qualifier calls adapter directly; actual CLI qualification remains actor-only | patch |
| B8 source capture dependencies | medium: current capture omits executed input parser and inherited qualifier/owner helpers, so it cannot bind the complete executed owner proof; include target tooling with new CLI lane | patch |
| B9 retained audit consistency | medium: final query reads transition without assertion and only initial receipt, while later stages commit more retirements; final consistency claim is incomplete | patch |
| B10 single-use wording | low: runbook includes --verify-retained in single-use stages although implementation and continuation permit repeated reads | patch |
| V1 successful CLI retirement/recovery | medium, pre-verified: removing retirement acceptance/context forwarding in worker breaks advertised CLI while current new checks still pass | patch |

B7/V1 share the missing CLI consumer proof. All other survivors have distinct roots.
Smallest fixes are qualification/test/receipt-custody and direct documentation corrections;
no public surface, SQL/reference change or intent renegotiation is required. No deferrals.


## Review completion and final verification

All three independent review layers completed. Eleven submitted findings were classified
individually: B1 rejected against the established exact-outcome-lock error contract;
B7/V1 share one gap; all nine surviving groups patched. Edge-case review returned [].
No deferred findings and no migration/reference/runtime command change from review.

| Findings | Final executed evidence |
| --- | --- |
| B2 | Actual committed lookup waits, authority revoked, denial before receipt with no business/evidence changes; synthetic authority restored |
| B3 | Fresh operation, currently authorized alternative org/account with original mismatched member: conflict, complete state preserved |
| B4 | Distinct operation IDs held behind shared member-history lock: exactly one revision/event/outcome; loser unresolved without evidence |
| B5 | Owner-prepared maximum revision under original-session operator SQL: safe conflict, membership/roles/evidence unchanged; preparation rolls back |
| B6 | Public CLI rejects well-formed wrong org/account/member worker responses, retaining original operation ID |
| B7/V1 | Existing prepared native target CLI executes, replays and looks up one synthetic retirement with identical receipt; member/event/outcome match |
| B8 | Final review stages capture132 owner/qualification/input/target/deployment/source/dependency files before/after; runtime SQL/reference unchanged |
| B9 | Every committed retirement in clean proof plus native CLI checked for exact transition, target/event identity, executor, revision/time and receipt fields; retained receipt artifacts |
| B10 | Runbook distinguishes read-only repeatable --verify-retained from single-use mutating stages |

Runtime review stages --review-boundaries, --review-remaining and strengthened
--verify-retained PASS. Two maximum-revision fixture preparation attempts failed safely
with42501 before command execution because postgres cannot assume identity_migrator.
Using the established supabase_admin fixture helper corrected preparation. Both failed
attempts, fresh synthetic rows, diagnostics and hashes remain in review-fix-results.json;
no fixture reset or permission relaxation. These were fixture setup corrections, not
retirement-command failures. Targeted review tests27 PASS0.56s.

Root final affected command (same frozen Python and flags above):961 PASS35.33s.
Both composition checks PASS with no writes. Root independently reran --verify-retained
and native CLI replay/scoped lookup for its already committed operation: identical
receipt, zero new business operations,132 captured files unchanged. Initial CLI proof
predates a qualifier-only consistency-check edit; runtime migration/adapter/CLI bytes
are unchanged, and root-final-cli receipt captures the current complete source set.
No new independent review round is required for these bounded step04 test/doc patches.

Final custody:2651 tracked starting paths checked, none missing or unexpectedly changed;
33 historical source/reference/root dependency files unchanged.41 selected proof outputs
passed credential URL/token/password checks. Native Supabase normal stop PASS; all data,
volumes/resources, previous frames, new synthetic fixtures and receipts retained.

Five impact decisions and exclusions remain. Controlled retire is delivered; join/rejoin,
full-constraint/seed cutover, live account verification, Access/WRITE and server KDG are
still gated. No remote push or production/provider/real account/access/deploy work.
