---
title: 'ID-B staged membership actor attribution'
type: 'feature'
created: '2026-10-21'
status: 'done'
baseline_commit: 'f885abf5b782af09d845af4eefcd9c170faa7bab'
route: 'dispatch'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="standing approval for bounded shared prerequisites">

## Intent

Stage durable actor references on existing memberships so subsequent authorized owner
commands can record attribution without inventing an Auth account or rewriting legacy
history. Add nullable created_actor_id and updated_actor_id UUID local actor references
with ON DELETE RESTRICT through Identity revision15. Protect new fields from existing
writers; only identity_migrator may explicitly populate/change them during this stage.
Once populated, creation actor is immutable even for that owner. Legacy rows stay null
until verified mapping evidence exists. This is structural preparation, not completed
adoption or a retirement/join command.

## Boundaries & Constraints

Always preserve old fields/times/rows/guards, full uniqueness, partial index, existing
read/seed behavior and historical migration/reference bytes. Owner-attribution changes
use existing revision behavior: one increment for a changed row, none for equal values;
backfill is not invisible to revision checks. No invented actor equality or automatic
System attribution. Normal writes cannot clear/change adopted references or set them
on insert, including via upsert/multirow statements; unrelated supported writes stay.
No new owner privileges, generator/framework/dependencies, actor creation/account/access
change, production migration, deploy, reset/prune, Leave/editor, push or real-data use.
Root alone runs disposable synthetic database tooling; retain all receipts/resources.

## I/O & Edge-Case Matrix

| Given / when | Then |
| --- | --- |
| Existing14 clean/adopt/previous target upgraded | nullable columns, validated named RESTRICT actor FKs, invoker guard; old data unchanged except two null fields |
| service_role insertion/update supplies nonnull/different new attribution | safe23514 identity_membership_actor_owner_required /org_member_actor_owner_required; atomic refusal |
| ordinary writer omits new fields or repeats exact existing values | legacy supported writes/noops/seed work; guard does not clear owner references |
| identity_migrator adopts verified synthetic actor IDs | local FKs enforced; old fields/times retained; changed revision advances once |
| nonnull creation actor cleared/replaced by anyone |23514 identity_membership_creation_actor_immutable /org_member_creation_actor_immutable |
| nonexistent/nil actor under owner update |23503 from named FK, no partial state |
| retirement/history/binding, drift/unknown/DDL failure/retry | existing protections and release reconciliation remain; no activated owner command |

</frozen-after-approval>

## Code Map

- services/access/identity-migrations/versions/0015_membership_actor_attribution.py:
  additive SQL plus invoker guard, fixed search_path and same-transaction ACL stripping.
- services/access/identity-migrations/identity_baseline.py: new head/trusted reference;
  preserve every older accepted catalogue and migration source.
- services/access/tests/qualify_identity_baseline.py: extend existing independently
  recorded rollback-only reference, source custody and no-overwrite checks.
- services/access/tests/qualify_membership_actor_attribution.py: subclass existing
  active-index/retirement/binding fixture protocol; specialize characterization,
  catalogue delta, attribution writes, owner adoption and DDL failure proof.
- services/access/tests/test_membership_actor_attribution.py: focused RED/TDD and recorder
  custody; previous test assertions may add new head to allowed states only with reason.
- Owner runbook, ownership inventory, KDG shared-prerequisites/next-session: record actual
  results, staged limits and remaining commands/seed/adoption gates.

## Tasks & Acceptance

- [x] Observe actual14 missing-column acceptance failure before implementing migration.
- [x] Add revision15 and trusted reference recorder, exact head/history/delta checks.
- [x] Prove matrix through actual restricted login and owner-prepared rollback adoption;
  include nonnull preservation, multirow/upsert, bigint exhaustion and atomicity.
- [x] Verify clean/adopt/exact14/repeat, drift/unknown, DDL failure rollback/recovery;
  run focused then affected regressions and both composition checks.
- [x] Record scaffold/UI/context/docs/ADR decisions and requirement-to-test evidence.

Given approved synthetic fixtures, when the bounded matrix completes, then receipts
bind executed source and reference SHA, old source/data/custody and safe output. Given
no command delivery, when CLI/adapter receives membership command, then it still refuses.

## Implementation Notes

Baseline `f885abf5b782af09d845af4eefcd9c170faa7bab`. bmad-help selects BD under existing
ID-B ownership. Planning PASS remains; this does not claim runtime prerequisite completion.
No intent gaps; irreversible effects limited to authorized isolated synthetic migrations.
Shared-schema/security footprint requires dispatch and three review layers. Standing
approval covers implementation and preserved dirty tree; no repeated acknowledgement.

## Verification

Frozen Python: platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python.
Use existing pytest services/access/tests plus apps/pts/tests/test_release.py, plugin
autoload disabled, -I -B and no cacheprovider. Both tools/py/run_compose_supabase.py
--check-only and --identity-authority owned --check-only must pass. No root npm claim.
Use actual prepared local Supabase databases and existing qualifier/reference recorder;
no new generic environment harness. Record exact commands/results after execution.

- Root owns synthetic DB execution/reference recording/private frame preparation.
  Implementation agent writes owning code/tests/qualifier/docs and runs CPU tests only;
  root independently executes actual14 RED before agent implementation starts.

- Actual14 RED recorded before implementation; no rows changed. New independent
  rollback-only reference SHA2562204a3ca4323bf9693aacc5f4202d2aab1516ac395e71516df2d8f702298a715.
- Host refused the fresh implementation agent with `agent thread limit reached`;
  step03's direct implementation fallback used. No concurrent implementation agent.
- Focused TDD found a missing signal import in synthetic restoration; fixed implementation.
 132 focused tests PASS5.17s; first affected regression915 PASS64.95s.
- Retained initial frame member-actor-jqd3m8q8: first matrix stopped before migration
  on frozen-Python receipt binding, corrected by actual previous-source reexecution
  while archiving original receipts; second stopped before migration on missing
  cross-owner fixture preparation; third upgraded clean then refused incomplete
  catalogue delta expectations. Exact added effective column/function observations
  were independently inspected; checks now derive additions from unchanged table
  rights and owner-only new function execution. No unexplained expected result changed.

- Catalogue delta TDD now verifies exact effective-observation additions and rejects
  missing false entries, new grants/function execution, old privilege changes and
  unrelated catalogue drift. Focused138 PASS5.30s.
- Rollback-only owner-prepared adoption/writer checks passed in reviewed-oqmsfory;
  inherited Auth-truncation checks then exposed an extraneous clean cross-owner fixture:
  its finance FK correctly caused42501 before the intended Identity guard. The clean
  lane now uses its original isolated fixture; legacy/previous cases still verify
  cross-owner preservation. No existing guard expectation or privilege was relaxed.
- Owner-prepared adoption changes effective role within an administrator transaction
  so adopted rows and FK actor fixtures can all roll back. No new role membership is
  granted to identity_migrator. Null-field writer checks use actual access_runtime
  session/SET service_role; adopted-field checks use administrator-prepared SET ROLE.

## Five impact decisions

- Scaffold: existing owner migration, reference and qualification route extended;
  no generator/schema-client template/runtime framework or dependency change.
- Shared UI: no UI consumer or interaction in this structural prerequisite.
- Agent context: existing safeguards suffice; AGENTS.md unchanged.
- Documentation: owning migration runbook, inventory, KDG prerequisites/continuation
  and this source-bound delivery evidence record staged adoption/command limits.
- ADR: existing0020 release compatibility,0025 attribution and0056 durable actors apply;
  no new decision or edit to an accepted ADR. TypeScript7.0.2 baseline unchanged.

## Requirement-to-test evidence

| Requirement | Executed proof |
| --- | --- |
| Actual14 missing fields | root actual14-red.json and source-bound characterize command |
| Exact nullable FKs, owner/invoker/search path, prior catalogue and no new privileges | qualifier.compatibility plus test_catalog_delta_accounts_for_exact_effective_observations |
| Ordinary writer insert/update/upsert/multirow and preservation of existing references | qualifier.attribution_writes; actual restricted login and explicitly identified owner-prepared lanes |
| Verified synthetic adoption preserves old fields/times, revision/noop/overflow, immutable creation actor and FK rejection | same rollback-only adoption lane; actual actor fixtures are local service actors, no Auth accounts manufactured for attribution |
| Legacy reads/seeds/history/binding and one-way retirement stay | inherited unchanged retirement.writes matrix plus adopted-reference seed check |
| Clean/adopt/exact14/repeat, source custody, lock/DDL failure rollback/recovery, drift/unknown | qualifier.upgrades_and_failures; historical31-file previous-owner manifest; recorder mutation/default-grantee/no-overwrite tests |

## Exact commands

```bash
OWNER_PYTHON=platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python
PROOF=platform/deployment/.local/identity-baseline/member-actor-final-4gakx3i_
IDENTITY_QUALIFICATION_DIR="$PROOF" "$OWNER_PYTHON" -I -B services/access/tests/qualify_membership_actor_attribution.py --characterize
"$OWNER_PYTHON" -I -B "$PROOF/run-qualification.py"
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$OWNER_PYTHON" -I -B -m pytest services/access/tests/test_membership_actor_attribution.py services/access/tests/test_active_membership_index.py -q -p no:cacheprovider
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$OWNER_PYTHON" -I -B -m pytest services/access/tests apps/pts/tests/test_release.py -q -p no:cacheprovider
"$OWNER_PYTHON" -B tools/py/run_compose_supabase.py --check-only
"$OWNER_PYTHON" -B tools/py/run_compose_supabase.py --identity-authority owned --check-only
```

Reference recording was executed once with IDENTITY_QUALIFICATION_DIR pointing at the
initial member-actor-jqd3m8q8 frame and the existing qualify_identity_baseline.py
--record-membership-actor-attribution-reference command (exit0). Both composers exit0,
no files changed. Private fixture scripts/previous-source executions/failed diagnostics
remain in all three frames. No real/provider/API/server-KDG runtime proof is claimed.

- Final actual matrix PASS27.931s, exit0, executed source unchanged. Final affected
  regression921 PASS34.29s; both composers PASS. Review pending.


## Historical review status — host capacity block

Fresh reviewer launch failed with `collab spawn failed: agent thread limit reached`.
A launch relay through the existing investigation task received the same exact refusal;
no reviewer ran and no review is claimed. Follow rendered bmad-build step04's standalone
handoff fallback; retain in-review and do not commit/finalize until all findings return
and are triaged. Root direct implementation was the permitted step03 fallback.

Results: actual characterization exit0; final matrix27.931s exit0/source unchanged;
focused138 tests5.30s exit0; affected921 tests34.29s exit0; both composers exit0;
preservation2667 paths, no missing/unexpected edits,32 historical owner files unchanged;
146 selected outputs passed the credential URL/token/password scan. Concurrent source
work remains outside the delivery. Normal stop result is recorded below when returned.

Next continuation resumes this in-review item, not dependent command implementation.
Three complete standalone review prompts accompany this record: blind hunter, edge-case
hunter and verification-gap. Run each in an independent review context and return its
findings for triage. No review layer is waived or reported complete.

- Normal native stop completed, exit0; all data/volumes/resources retained.

## External review receipt

Blind review returned ten findings, retained verbatim in
[blind findings](review-id-b-membership-actor-attribution-blind-findings.md).
Edge-case and verification-gap reviews remain pending. No verdicts or implementation
patches yet: step04 requires all review layers to report before classification.
Keep the reviewed source and standalone handoffs unchanged while reviews complete.

Edge-case review subsequently returned two findings, retained verbatim in
[edge findings](review-id-b-membership-actor-attribution-edge-findings.md).
Blind and edge-case reviews are received; verification-gap review remains pending.
No classification or implementation patches until that final layer reports.

Verification-gap review returned one finding, retained in
[verification findings](review-id-b-membership-actor-attribution-verification-findings.md).
All three independent reviews are now received. Source is still unchanged at triage.

## Review Triage Log

Each submitted finding is classified before grouping. These are bounded qualification
and diagnostic corrections, without changing migration15, its reference or runtime
command scope. Root implemented the original item because fresh children were unavailable;
root applies the step04 patch fallback. No intent gap or specification re-derivation.

| Finding | Verdict and checked evidence | Route |
| --- | --- | --- |
| B1 populated update actor substitution | medium: attribution_writes skips the stored-other_actor to valid-actor transition; no behavioral assertion covers it | patch |
| B2 upsert update arm | medium: nonnull INSERT attribution is rejected before ON CONFLICT UPDATE; omitted-attribution INSERT plus protected DO UPDATE is missing | patch |
| B3 multirow execution order | low: CASE multirow update does not guarantee a successful write precedes refusal; dependent writable CTE will observe that rollback boundary | patch |
| B4 owner insert | low: adoption lane updates only; no assertion covers attributed INSERT revision1/legacy fields or named invalid FK on INSERT | patch |
| B5 adopted retirement | low: populated references roll back before inherited retirement regression; add transitions while still adopted | patch |
| B6 FK names | low: inherited reject helper checks constraint only inside its message branch, and current23503 calls omit both; check metadata independently | patch |
| B7 adversarial default grantee | medium: normal reference proves final ACL but source recorder's defaults do not include an additional grantee; use existing role in rollback-only old14 fixture | patch |
| B8 repeat preservation | low: repeat checks command success without before/after catalogue/data snapshots; verify repetition with a deliberately retained extra synthetic attributed member, preserving all original rows | patch |
| B9 new guard drift | medium: existing drift lane is intentionally previous14 and never exercises changed/disabled attribution guard on15 | patch |
| B10 structural additions | low: trusted full catalogue reference and SQL assertions already constrain actual15, but verify_catalog_delta alone uses counts for structural additions and anonymous unit rows; tighten exact vectors and mutations | patch |
| E1 uncaught diagnostics | medium: __main__ calls main directly; unexpected driver exceptions can escape with SQL/diagnostic values; add a fixed safe failure boundary, not the suggested invalid type(error).name expression | patch |
| E2 unknown-history timeout | medium: final unknown-history transaction omits the local bounds used elsewhere, so a conflicting ledger lock can wait without its own deadline | patch |
| V1 adopted update actor substitution | medium: pre-verified consumer-path gap duplicates B1's skipped transition and mutation demonstration | patch |

Grouping: B1/V1 share one missing transition assertion. Every other finding has its
own root cause. No findings deferred or rejected. Existing migration/reference bytes,
frozen intent and all previously required source/receipts/resources must remain intact.


## Review completion and final verification

All three external independent review layers were returned by the user. All13 findings
were classified individually; B1/V1 share one gap, and all12 groups were patched.
No deferred findings. Migration15 and its independently recorded reference are unchanged.
No fresh review launch or repeated owner acknowledgement is required for these step04
qualification/diagnostic patches; original implementation was root's direct fallback.

Review patch evidence:

| Findings | Verified correction |
| --- | --- |
| B1/V1 | Ordinary writer replaces stored other_actor with existing actor and is denied; complete member/revision/role/audit state rolls back |
| B2/B3 | Omitted-attribution INSERT reaches protected ON CONFLICT UPDATE; dependent writable CTE orders a permitted change before denial and verifies rollback |
| B4/B6 | Valid owner INSERT preserves supplied legacy attribution/times and starts revision1; invalid INSERT/UPDATE references verify exact FK names independently of English messages |
| B5 | Adopted references survive retirement; attempted revival/retiming refuses without changing the adopted row |
| B7 | Rollback-only additional default EXECUTE grantee is proved effective on a sentinel, stripped only from the new guard, with defaults and sentinel ACL preserved |
| B8 | Real CLI repeat preserves exact catalogue/all rows including a newly retained synthetic actor and attributed member; original rows untouched and intent/result receipts retained |
| B9/B10 | Current15 changed/disabled guard refuses preflight without normalization; exact structural vectors and function-definition digest supplement the trusted full reference and reject wrong column/FK/trigger/function metadata |
| E1/E2 | Fixed safe failure code covers actual script entrypoint; ledger mutation installs local5s/2s bounds and actual conflicting-lock proof returns55P03 with state restored |

Focused RED:12 failed/59 passed in3.87s (structural mutations, missing error boundary,
constraint-name omission); timeout test separately RED1 failure0.58s. Focused GREEN:
145 passed8.66s, exit0, command below. Final affected936 tests PASS44.54s, exit0. Actual
patched full matrix PASS47.815s, exit0, executed source unchanged. Both composition
checks exit0. All32 historical owner files other than the planned helper extension remain unchanged; new migration/reference bytes remain exactly qualified.
The existing shared qualification reject helper now checks constraint metadata even
when no English diagnostic message is requested; no public/runtime API changes.

Final actual proof:
platform/deployment/.local/identity-baseline/member-actor-review-fixes-9n3jhlhb/.
This supersedes the earlier27.931s matrix for reviewed acceptance. All old frames,
failed attempts, reference recorder inputs and original handoff snapshots remain.
Retained repeat fixture is synthetic only; it creates no account, mapping or grant and
is not an enabled owner actor/membership command. Other new DDL/adoption/drift lanes
roll back. The full matrix is single-use; preserve its new synthetic actor/member and
use fresh cases for a future full proof. Never reset/delete fixtures to rerun it.

Exact reviewed commands from repository root (same frozen owner Python):

```bash
OWNER_PYTHON=platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python
PROOF=platform/deployment/.local/identity-baseline/member-actor-review-fixes-9n3jhlhb
IDENTITY_QUALIFICATION_DIR="$PROOF" "$OWNER_PYTHON" -I -B services/access/tests/qualify_membership_actor_attribution.py --characterize
"$OWNER_PYTHON" -I -B "$PROOF/run-qualification.py"
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$OWNER_PYTHON" -I -B -m pytest services/access/tests/test_membership_actor_attribution.py services/access/tests/test_membership_binding.py -q -p no:cacheprovider
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$OWNER_PYTHON" -I -B -m pytest services/access/tests apps/pts/tests/test_release.py -q -p no:cacheprovider
"$OWNER_PYTHON" -B tools/py/run_compose_supabase.py --check-only
"$OWNER_PYTHON" -B tools/py/run_compose_supabase.py --identity-authority owned --check-only
```

Five impact decisions remain as above. Review adds only owner qualification coverage,
safer diagnostic output and an internal assertion-helper correction. Existing owners
retain scaffold/client/schema/generator/UI/runbook work. No new dependency or accepted
ADR edit; no production migration, account/provider/access change, deploy or push.


Final custody:2677 protected paths checked, no missing or unexpected changes;32
historical owner files and migration15/reference bytes preserved. All executed source
hashes still match.62 selected proof outputs passed credential URL/token/password checks.
Normal native stop completed, exit0, retaining all data/volumes and every old/new frame.
Original standalone review handoffs are retained locally as untracked review snapshots;
only the concise returned findings and delivery evidence enter the scoped source commit.
No dependent Identity/Access/WRITE or server-backed KDG work started in this increment.
