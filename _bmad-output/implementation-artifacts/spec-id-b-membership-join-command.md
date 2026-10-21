---
title: 'ID-B protected membership join and seed cutover'
type: 'feature'
created: '2026-10-21'
status: 'done'
baseline_commit: '9cd1672efe54d0ee7e7bc595d8ddad7d73a9f2b5'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/platform/docs/architecture/contracts/identity-access-execution-substrate.md'
  - '{project-root}/platform/docs/architecture/contracts/e1-controlled-provisioning-and-evidence.md'
---

<frozen-after-approval reason="standing approval for bounded shared prerequisites">

## Intent

Deliver membership.join and scoped recovery through existing Identity tooling, including
explicit rejoin with a new membership ID. Coordinate removal of full uniqueness with
protected writers and legacy seed retirement. Preserve history; no old roles/grants
resume. Account mapping/live Auth verification remains a separate command and gate.

## Boundaries & Constraints

Derive executor from original session and protected exact join/org/account authority;
owner=true additionally requires membership.join_owner. Recheck after serialization.
Validate nondeleted Identity profile/org without requiring existing membership or
implicitly creating actors/accounts. Retain profile→Auth FK; claim no live provider check.
Use the delivered retry namespace and shared membership-history lock. First join requires
no history; rejoin names the latest retained retired predecessor, with no active row.
Allocate fresh bigint/revision1, server UTC creation/update times and durable executor
actors; legacy nullable profile-attribution fields must not invent an executor profile.
Outcome/event commit atomically, immutable and currently authorized for recovery/replay.
Replay resolves original membership even after retirement/rejoin. Changed retry conflicts.
Block ordinary membership insertion and owner-flag changes, retaining explicit migrator
maintenance and unrelated supported updates. Keep binding/retirement/history guards.
Drop only the full org/account unique constraint; keep active unique index. Preserve all
historical migrations/references, source seeds, unrelated work, receipts and Docker data.
Retire scripts/seed.py execution before client/Auth side effects; preserve source helpers.
Owned composition requires existing --no-seeds and refuses stale generated seed SQL.
No replacement seed RPC, generator/framework/dependency, Access/grant/People/Leave/editor,
real account/authority/provider changes, production migration/provision/deploy/pilot,
reset/prune or push. Isolated synthetic fixtures only; preserve failed attempts.

## I/O & Edge-Case Matrix

| Given / when | Then |
| --- | --- |
| Eligible profile/org, no history, first join | created typed member receipt, revision1, new ID, executor actors/server times; empty roles/grants |
| Retired latest predecessor named | new greater ID, retained predecessor/evidence/roles, no inherited owner without explicit authority |
| Active member, stale/null/wrong predecessor, missing/deleted profile/org | safe conflict, no business/evidence changes |
| Missing/wrong/disabled/revoked join or required owner authority; spoofed context | denial for execution/recovery, including revocation during actual waits |
| Same/changed retry, same/distinct-operation races, lost commit response | once-only original receipt / conflict / bounded busy/unavailable; safe same-operation recovery |
| Old join replay after retirement/rejoin, delayed old retire | original receipt; replacement untouched |
| Ordinary insert/owner change or legacy demo seed | atomic refusal; no implicit rejoin, attribution or role copying |
| Owned composition with seeds/stale generated SQL | early refusal preserving files; clean --no-seeds lane passes |
| Clean/adopt/head16/repeat, catalog drift/unknown, DDL/event failure | exact trusted catalog, old data/history/other owners retained, atomic rollback and explicit recovery |

</frozen-after-approval>

## Code Map

- services/access/identity-migrations/versions/0016_membership_retire_command.py: reuse
  fixed command/evidence/RLS/authority/history-lock design without editing old revision.
- identity-migrations/versions/0017_membership_join_command.py: new owner SQL, local
  profile/org validation, protected insert/owner transition and constraint cutover.
- identity-migrations/identity_baseline.py and tests/qualify_identity_baseline.py: extend
  head/reference chain and existing independent rollback-only recorder.
- identity_operator_input.py: JoinMembershipCommand/canonical retry input already exists.
- identity_operator.py/operator_cli.py: typed created member receipt, fixed execution
  and explicit command/org/account lookup context; retain actor/retire compatibility.
- tests/qualify_membership_retire_command.py: reuse actual restricted sessions, prepared
  native CLI target, witnessed locks, bounded safe failure and complete source custody.
- scripts/seed.py and tools/py/run_compose_supabase.py: fail before side effects; no
  new seeding engine. Source SQL seeds stay immutable. Preserve stale generated outputs
  with receipts if archiving them for the clean owned composition proof.

## Tasks & Acceptance

- [x] Record actual16 missing join/unsupported acceptance failure; focused RED before code.
- [x] Add17 SQL/reference and baseline recorder; preserve every prior source/reference.
- [x] Extend typed adapter/CLI and prove successful actual CLI execute/replay/lookup.
- [x] Protect direct writers; gate legacy demo seeding/owned composition with focused tests.
- [x] Qualify every matrix row using fresh synthetic cases, actual restricted credentials,
  same/distinct first races, owner policy, revoked lookup, delayed commands and rollback.
- [x] Verify clean/adopt/exact16/repeat, event/DDL failure/drift; actor/retire regressions,
  affected tests/composers, five impacts, docs/evidence and independent BMAD reviews.

Given join→retire→rejoin, when old commands replay, then original receipts/history remain
and no later member changes. Given failure, when state is compared, then memberships,
roles and evidence are unchanged. Given delivery, downstream Access/WRITE/KDG stays gated.

## Implementation Notes

bmad-help selects BD. No intent gap: contracts distinguish join from live Auth ensure.
Footprint spans owner SQL/transport/seed guards; synthetic migrations are authorized.
Standing approval covers preserved dirty tree. Latest predecessor uses ordered retained
IDs; refuse unsafe sequence allocation rather than silently repairing owner state.
Root supplies actual16 RED/private frame. Agent implements sequentially, using existing
private bootstrap and previous-owner snapshot tooling. Never reset committed cases.

## Verification

Frozen Python: platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python.
Run smallest failing test, affected pytest services/access/tests apps/pts/tests/test_release.py
with PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 -I -B -q -p no:cacheprovider. Both legacy composer
--check-only and owned --identity-authority owned --no-seeds --check-only pass in clean
output; stale-output refusal is explicit negative proof. Use existing local synthetic
qualification/reference and prepared native CLI, capture exact sources/results/receipts.

Five impacts: extend existing owner/scaffold tooling only; no shared UI consumer;
AGENTS unchanged; update owner runbook/inventory/KDG handoff and requirement-test evidence;
ADRs0020/0025/0035/0056 and accepted E1 apply, no accepted ADR edit. Dependencies including
TypeScript7.0.2 remain unchanged.

## Spec Change Log

## Runtime preparation

Actual16 RED recorded read-only in
platform/deployment/.local/identity-baseline/member-join-t1zthz6c/actual16-red.json:
join functions absent, full uniqueness retained. protected-before.json captures starting
tracked bytes. Previous committed proof/scripts/private credentials are retained in
platform/deployment/.local/identity-baseline/member-retire-ggl0dn_m/; use its existing
bootstrap.py/previous-setup.py protocol to prepare fresh head16 cases, never rerun old
committed stages. Native run99b7231c-0a5b-4bdb-98e8-3329564c526a is starting normally;
prepared native operator target/owner fixture remains available. Keep all receipts,
including any failed attempts. Native up/stop uses existing deployment/dev.py and pinned
Supabase CLI path from the previous frame's run.json. Root owns independent final review,
verification, normal stop and scoped local commit; agent returns without reviewing or
committing. Exact runtime source captures include imported owner/qualification/target/
deployment dependencies. Include actual CLI success and same/distinct-operation races
before independent review, rather than relying only on adapter tests.

## Build evidence — implementation handoff, 2026-10-21

Implementation is ready for root's independent inspection/reviews; no commit or normal
native stop was performed by the implementation agent. The final passing synthetic frame
is `platform/deployment/.local/identity-baseline/member-join-t1zthz6c-attempt4/`.

Delivered revision17, its independently recorded catalog reference, historical baseline
chain/head validation, typed created-member adapter and protected CLI execution/recovery.
The command validates local nondeleted profile/org under bounded row locks, retains the
profile/Auth FK, serializes retry/history then rechecks exact authority, and creates new
membership/event/outcome atomically. Rejoin retains roles/history without copying them.
Ordinary insert/owner changes are guarded; only full uniqueness is dropped. Legacy demo
execution stops before optional imports/environment/client/Auth work; owned composition
requires no seeds and refuses stale generated SQL before writes.

Initial failures: the retained `actual16-red.json` records no join routines and full
uniqueness; focused `test_join_dispatch_and_created_receipt` failed with
`command_unsupported`. Seed guard tests failed with an optional-import error and missing
composer guard before implementation. Focused adapter GREEN:36 tests. Final focused
transport/guard/history suite:107 passed. Final affected suite:971 passed in47.01s:

```sh
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python -I -B -m pytest services/access/tests apps/pts/tests/test_release.py -q -p no:cacheprovider
```

The exact output is retained as `affected-suite.log` in the final frame. One historical
composer test now isolates generated seed output in its temporary fixture, so its original
legacy-migration refusal assertion is still exercised. Head16 historical postcondition
verification remains tested; only head17 satisfies current require_head.

Runtime commands use that same frozen Python with
`IDENTITY_QUALIFICATION_DIR=platform/deployment/.local/identity-baseline/member-join-t1zthz6c-attempt4`
and `-I -B services/access/tests/qualify_membership_join_command.py`, followed by the
single-use stages `--boundaries`, `--additional`, `--matrix`, and the retained consistency
stage `--verify-retained`. Existing private bootstrap/previous-owner execution prepared
fresh cases from exact commit9cd1672efe54d0ee7e7bc595d8ddad7d73a9f2b5 at head16.
Full before/after source captures bind imported owner, qualification, target and deployment
helpers, pinned migrations/references and dependency manifests. No reference was exported
from a deployed target: the existing independent recorder executed all historical source
stages and17 in a rolled-back clean synthetic case. Its final SHA-256 is
`8e6a0b7f61535e0c541b7e80836e1431331ddb37a5ad57432a800b02e4ebd5df`.

| Requirement | Actual proof / result |
| --- | --- |
| First join, durable executor/server times, empty roles | restricted original identity_operator session, created/revision1 receipt and stored row checks PASS |
| Retire/rejoin retained predecessor/roles; delayed commands | original receipts survive retirement/rejoin; fresh replacement ID; old retire touches no replacement PASS |
| Same/changed retry and first races | witnessed actual outcome/history waits; same operation commits once, distinct operations have one safe conflict; changed fingerprint racer conflicts PASS |
| Current exact join and owner policy | owner execution/replay/lookup denial after join_owner disable; missing/wrong scope/account and disabled principal deny PASS |
| Revocation while waiting; bounded retry; lost response | witnessed execute and committed lookup waits recheck revoked authority; busy is bounded; same operation recovers durable lost response PASS |
| Missing/deleted refs and context spoofing | absent/deleted profile/org conflict without evidence changes; forged canonical input and runtime credential denied; GUC cannot choose executor PASS |
| Direct writers and sequence safety | exact owner-trigger codes verified with rollback-only temporary privileges; ordinary owner update and insert refuse; unsafe high predecessor sequence fixture conflicts without repair PASS |
| Evidence failure | injected event trigger aborts membership/outcome/event atomically PASS |
| Clean/adopt/head16/repeat | exact catalogs; retained rows, ledger and foreign-owner references unchanged PASS |
| Catalog drift/unknown/DDL failure | history/function/ACL drift refused; witnessed DDL failure rolls back; explicit retry recovers PASS |
| Actor/retire compatibility | actual actor execute/replay/lookup; actual join→retire→rejoin and original retire replay PASS |
| Actual prepared native CLI | successful join execute, identical replay and scoped lookup; existing protected target unchanged PASS |
| Retained consistency | all joins' original receipt/event/member target, executor, timestamps, transition and single event verified; six final catalogs exact PASS |

Composer proof: `python3 tools/py/run_compose_supabase.py --check-only` passes.
Owned composition without `--no-seeds` refuses; owned/no-seeds with existing generated SQL
refuses while preserving output. The generated `supabase/seeds/` directory was then moved
byte-for-byte to final-frame `archived-generated-seeds/`, with original names, hashes and
archive path in `generated-seed-archive.json`. Source seed files were unchanged. Clean
`python3 tools/py/run_compose_supabase.py --identity-authority owned --no-seeds --check-only`
passes. Commands, exit codes and log hashes are in `composer-results.json`.
`immutable-preservation.json` verifies starting files remain or have exact archive mappings, and protected historical
migration/reference/source-seed files retain their starting bytes.

Retained attempts are deliberate evidence, never reset:

- `member-join-t1zthz6c/`: actual16 RED; independent reference recording attempts; initial
  migration verifier needed an exact allowed membership sequence USAGE exception; first
  restricted execution found missing schema USAGE for legacy auth.role policy evaluation.
- `member-join-t1zthz6c-attempt2/`: row-lock SELECT initially lacked a matching UPDATE RLS
  policy; PostgreSQL therefore hid the profile and safely returned membership conflict.
- `member-join-t1zthz6c-attempt3/`: core, recovery, native CLI and migration matrix passed;
  an extra committed fixture GRANT/REVOKE left an empty column ACL, correctly failing exact
  catalog comparison. This frame remains retained with that diagnostic drift.
- `member-join-t1zthz6c-attempt4/`: all final stages pass. A rollback-only boundary fixture
  initially used postgres instead of the existing supabase_admin helper and could not SET
  ROLE; the transaction rolled back. Corrected fixture uses the established helper and
  rolls back privilege grants, preventing metadata drift. Failed source-capture receipts
  remain retained alongside passing receipts.

The prepared native operator fixture database now runs head17 and retains synthetic join
receipts/members plus earlier retirement/actor evidence. Native run
`99b7231c-0a5b-4bdb-98e8-3329564c526a` remains running for root inspection/normal stop.
No production/main application migration, real account/authority/provider change,
Docker reset/prune, push or commit was performed.

Five impacts: scaffold extends existing owner command/catalog/qualification patterns;
shared UI has no consumer; AGENTS is unchanged; owner runbook/inventory/KDG handoff and
this requirement-to-test evidence are updated; accepted ADRs0020/0025/0035/0056 and E1
apply unchanged. Dependency manifests including TypeScript7.0.2 are unchanged. Live Auth
verification/account mapping, Access activation, People/Leave/editor/WRITE/KDG readiness
remain separate gated work. Independent BMAD reviews and final scoped commit remain root's
handoff responsibility.

Handoff preservation note: concurrent Leave/planning changes are outside this delivery and
remain untouched. Current HEAD and the exact generated-output path mappings are recorded
in final-frame `immutable-preservation.json`; baseline equality is not claimed for those
unrelated files. Final `git diff --check` passed.


Root pre-review inspection found two qualification safeguards missing from the new
entrypoint/drift transaction: uncaught database exceptions and unbounded ledger locks.
Focused entrypoint RED failed before implementation; fixed canned error boundary and
local5s/2s drift bounds, preserving SQL/reference/runtime behavior. Current continuation
now points to this pending review. No concurrent Leave/planning changes belong to this item.

Root independent retained-state/catalog qualification PASS after handoff safeguards;
51 focused tests PASS0.69s. Scoped diff excludes concurrent Leave/planning changes.
Three independent review lenses now inspect this snapshot; no layer is skipped.

## Review Triage Log

All three independent layers returned before classification: blind10, edge1, verification2.

| Finding | Verdict and checked evidence | Route |
| --- | --- | --- |
| B1 existing Access grants can resume | high: services/access/main.py joins grants by org/user, without member ID; this is the existing separately planned Access transition, expressly excluded from this bounded Identity item. New member copies no rows but legacy Access remains incompatible; forbid consumer activation and record the concrete gate. | defer to ACCESS-A/B; document maintenance limit |
| B2 sequence check is scoped by RLS | low: true visibility limitation; required guarantee is fresh unique ID greater than this account/org predecessor, which is visible under exact authority. PK still refuses an unseen collision safely; global monotonicity across unrelated memberships is not promised. Runbook wording needs scope precision. | patch documentation |
| B3 healthy cross-scope allocation interleaving | false: supported EXECUTE is granted only to identity_operator; join holds identity:operator-authority:v1:<session_user> before allocation until commit, serializing every supported join across scopes. Canonical role/ACL checks reject extra login execution/membership. The described A/B allocation interleaving cannot occur in this delivered caller model; future multi-login support needs its own proof. | reject |
| B4 distinct rejoin race | medium: first-join same/distinct races exist; same retired-predecessor race lacks independent behavior proof | patch |
| B5 revocation at history wait / owner authority | medium: current wait proof targets retry lock; different preceding history lock and owner-policy revocation are not witnessed | patch |
| B6 profile/org retirement races | medium: FOR SHARE and revalidation are implemented but only already-deleted references are tested | patch |
| B7 genuine unrelated writer/maintenance | low: no-op does not establish actual legacy mutation or migrator maintenance/revision preservation | patch |
| B8 guards accepts any exception | medium: connection/privilege/SQL errors can satisfy its record; later boundaries verifies actual codes, so remove the redundant weak proof and retain the exact one | patch |
| B9 adversarial join transport | medium: generic actor/retire checks and typed revision cases do not independently verify the join-specific expanded public response boundary | patch |
| B10 release compatibility/maintenance | medium: runbook names cutover but lacks concrete writer inventory, activation order and recovery limits required by ADR0020 | patch documentation |
| E1 sequence hidden out-of-scope rows | low: same visibility/documentation issue as B2, not a global ID-order invariant. Keep per-scope guarantee and explicit collision/unavailable recovery; no broader reader privilege or new helper is warranted | patch documentation |
| V1 composer entrypoint seed guard | medium, pre-verified: tests call helper; removing its main call leaves them green. Private actual CLI proof exists but regression at owning entrypoint is missing | patch |
| V2 authorized wrong-account recovery | medium, pre-verified: original account only; SQL account predicate is not independently mutation-protected by join behavior checks | patch |

Only after individual classification: B2/E1 share documentation scope; other survivors
have separate roots. Patches add no public surface or runtime SQL change. B1 remains a
previously planned excluded owner implementation/activation gate, with explicit source
evidence and release restrictions; it is not silently accepted as production-safe.


## Review completion and final verification

All13 independent findings were individually classified. B3 rejected against the current
single-login/authority-lock execution model. Ten surviving patch groups completed
(B2/E1 grouped); B1 records the already-planned excluded ACCESS-A/B compatibility gate
in deferred-work.md. This is not a claim that legacy Access is safe after rejoin.
Maintenance/activation/recovery restrictions explicitly prohibit that mixed-version use.
Migration17/reference/runtime SQL are unchanged through review.

Review evidence:

| Findings | Executed correction |
| --- | --- |
| B2/E1 | Runbook states per-org/account predecessor ordering, scoped reads, safe collision/unavailable recovery; no global ID-order claim or new reader |
| B4 | Fresh distinct-operation explicit rejoin race: one replacement/event/outcome, loser unresolved, original member/roles/receipts retained |
| B5 | Witnessed history-lock waits followed by join or join_owner revocation deny without business/evidence effects |
| B6 | Actual profile/org retirement-before-validation refuses join; validation-first holds retirement until join commits, with observed row/transaction waits |
| B7 | Actual legacy updated_by change and migrator owner toggle increment revisions while actors/history stay; rollback restores data and catalog |
| B8 | Removed redundant catch-any-exception guards/no-op records; exact machine-code boundary checks remain |
| B9 | Public CLI adversarial org/account/command/revision/member responses and unresolved/error lookup cases preserve operation identity and safe failure |
| B10/B1 | Concrete incompatible writer/old Access inventory, stop/backup/migrate/verify/coordinated Access/activate sequence and keep-stopped recovery; no live action |
| V1 | Composer main refuses missing --no-seeds/stale SQL before discovery/writers, with exact unchanged output/manifest |
| V2 | Authorized org-wide B-context lookup cannot recover A's operation; A still recovers, no effects |

Review stage1 retained its passed rejoin/history-revocation subcases, then an assertion
exposed the existing profile audit trigger's legitimate effect from the test's deliberate
profile retirement. Correction verifies exactly one expected users UPDATE audit row with
only allowed changed fields, while proving no join/evidence effects; it does not dismiss
unexplained drift. review-gaps-2.log / --review-gaps-remaining passes reference orderings,
maintenance and wrong-account lookup with fresh fixtures. Old attempts/logs remain.
Root independently executed fresh rejoin/history-revocation cases and final retained
verification against the final138-file source capture, all PASS, binding the earlier
prefix checks to final code without reusing any committed fixture. Actual review stage
row waits use5s statement/2s lock bounds and bounded witness/event/future waits.

Focused review27 tests PASS. Root final affected command (same frozen Python/flags in
Verification):984 PASS34.92s. Both legacy --check-only and owned --identity-authority
owned --no-seeds --check-only composition routes PASS, without writes. Root retained
receipt/event/member and six exact-catalog checks PASS. Native prepared-target CLI
replay/scoped recovery returns the same existing receipt; native member/event/catalog
also verified, zero new native business operations,138 source files unchanged. Final
private receipts are root-final-cli-*.json and root-current-review-prefix-*.json under
member-join-t1zthz6c-attempt4. No additional review round is required for these bounded
step04 qualification/doc patches.

Final preservation:2656 starting paths retained in place or exact archive, none missing;
three generated seed artifacts archived byte-for-byte, source seeds/history retained.
Root verifies34 historical migration/reference/source-seed files; implementation's42-file
protected set also covers instructions/dependencies.38 selected proof outputs passed
credential URL/token/password checks. Concurrent Leave/planning/PtS and original unrelated
work stays outside this delivery. Native wrapper stop completed normally, preserving all
Docker data/resources and every old/new fixture/frame. Worker model-capacity interruption
was retried successfully; no runtime command was blamed for that service error.

Five impacts stay as recorded. Local delivery is complete; live account verification/
account_actor.ensure remains the next bounded Identity dependency. ACCESS-A/B exact
membership binding remains mandatory before any real consumer activation, followed by
WRITE/KDG gates. No production migration, real account/access/provider, deployment,
reset/prune, Leave/editor or push occurred.
