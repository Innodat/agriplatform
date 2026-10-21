---
title: 'ID-B protected account actor setup'
type: 'feature'
created: '2026-10-21'
status: 'done'
baseline_commit: 'e0d116eb083cba00367a1757e373a15fdaa39340'
route: 'dispatch'
review_loop_iteration: 0
context:
  - 'AGENTS.md'
  - 'platform/deployment/DEVELOPMENT.md'
  - 'platform/docs/architecture/contracts/identity-access-execution-substrate.md'
---

<frozen-after-approval reason="standing authorized bounded Identity implementation">

## Intent

**Problem:** The accepted `account_actor.ensure` input still refuses execution. Account-only applications need durable authorship without employment or organization setup.

**Approach:** Complete the existing protected Identity command, verifying the selected live Auth account/profile before local coordination, then atomically creating its permanent actor mapping and immutable command evidence.

## Boundaries & Constraints

**Always:** ADR-0056 and owner contracts govern. Explicit account/actor UUIDs, current account-targeted platform authority, required classification provenance, server executor/time, bounded transactions, safe errors and scoped recovery. Preserve historical migration/reference bytes, source files, receipts and concurrent work. Synthetic local/CI verification only; preserve Docker resources and committed fixtures.

**Never:** Auth creation/mutation, person/employment/membership/grant creation, actor reassignment/merge, login-time setup, new service/generator/receipt framework, production deployment, Leave/editor or push. Existing ACCESS-A/B membership-binding activation gate remains.

## I/O & Edge-Case Matrix

| Scenario | Input/state | Expected behavior | Error |
|---|---|---|---|
| New | Live Auth and nondeleted ordinary profile, unused explicit actor | Account actor, mapping, outcome and event commit together | None |
| Legacy | Classified human profile, actor UUID equals account UUID, unbound account-kind actor or absent actor | Preserve UUID/history; create mapping only when eligible | Conflict for foreign/system/keyed actor |
| Identical | Same verified mapping and label | Unchanged outcome, no new event | None |
| Conflict | Other binding, occupied foreign UUID, changed kind/label, system/keyed profile | Preserve all state | Conflict |
| Ineligible | Missing/deleted Auth/profile | No setup despite retained mapping | Conflict/refusal |
| Unavailable | Auth reader missing/unsafe, SQL dependency or lock failure | No partial writes; bounded safe failure | Unavailable, never absence |
| Unauthorized | Wrong login/account/authority, spoofed GUC or raw write | No setup or disclosed lookup | Denied |
| Retry | Same operation/input, changed input, concurrent requests, response loss | One committed change; replay or scoped recovery; mismatch conflicts | Busy only retry lock |
| Lifecycle | Deleted account then new account UUID | Retain historical actor/map; new account cannot take old actor | Conflict on reuse |

</frozen-after-approval>

## Code Map

- `services/access/identity_operator_input.py`, `identity_operator.py`, `operator_cli.py`: reuse strict EnsureAccountActorCommand, JCS/retry identity, bounded execution, typed receipts and CLI; add account-targeted platform outcome lookup.
- `services/access/identity-migrations/versions/0002_actor_registry.py`, `0005_operator_authority.py`, `0006_actor_command.py`, `0017_membership_join_command.py`: existing immutable history and protected writer/evidence patterns; add revision18, never edit predecessors.
- `services/access/identity-migrations/identity_baseline.py` and `tests/qualify_identity_baseline.py`: staged role validation, exact catalog references, rollback-only independent recorder; preserve heads1–17 and add head18.
- `platform/deployment/DEVELOPMENT.md`, `apps/kdg-capture/docs/next-session.md`, owner evidence/contracts: exact delivery and remaining gates.

## Tasks & Acceptance

**Execution:**
- [x] `services/access/tests/test_identity_operator.py`, CLI/baseline tests and new `qualify_account_actor_ensure.py` — observe acceptance failure before implementation, then focused TDD and actual matrix coverage.
- [x] `services/access/identity-migrations/versions/0018_account_actor_ensure.py` — protected SQL command, evidence guards, immutable mapping writer and authorization-scoped lookup; extend existing actor registration without regressions.
- [x] `services/access/identity-migrations/identity_baseline.py`, reference recorder and new reference — exact staged verifier preparation and head18 catalog; reject drift before mutation.
- [x] `services/access/identity_operator.py`, `operator_cli.py` — strict account receipt and lookup context through existing target/tooling, no extra credential.
- [x] `platform/deployment/DEVELOPMENT.md`, owner evidence/contracts, KDG tracker/handoff — requirement-to-test commands/results, five impacts, coordinated preparation/recovery and exclusions.

**Acceptance Criteria:**
- Given each matrix state, when the restricted command/CLI executes, then actual PostgreSQL evidence demonstrates its expected result and unchanged unrelated data, audit, roles and permissions on refusal.
- Given clean and known head17 databases, when controlled upgrade/repeat/drift checks execute, then head18 is exact, data preserved and unknown/drifted history refuses without normalization.
- Given interruption, lock contention, authority revocation or delayed execution, when command/recovery runs, then total deadlines and exact target authorization hold, and no receipt precedes commit.
- Given successful setup, when inspected, then no person, membership, employment or access grant exists because of it.

## Implementation Notes

Technical decision: prepare `identity_account_verification_owner` as NOLOGIN, noninheriting/nonbypass with exact migrator SET-only membership. Separate restricted Auth-owner bootstrap grants only auth schema USAGE and SELECT(id,deleted_at) on auth.users plus its exact SELECT RLS policy. Identity migration grants selected profile reads and an authority-scoped profile policy, then a fixed pinned-search-path verifier executable only by command owner. It independently checks account-targeted current authority; no caller verification flag/GUC. Verify before advisory/business locks; retain evidence for this bounded execution and recheck local profile/current authority after waits. Auth banning remains Supabase authentication policy.

Staged validation permits only that exact Auth preparation, no Identity objects; normalize expected staged membership before every historical comparison, including early returns. No broad rights or old reference regeneration.

Explicit operator evidence records human classification; it cannot itself prove live Auth. Existing unbound actor adoption is limited to the verified account UUID, account kind, null key, non-system/non-keyed profile. Arbitrary unbound actors refuse. New differing UUID must be unused in actor/mapping and legacy profile identity space; existing own legacy actor must not be bypassed. No cross-owner authorship backfill or automatic classification.

Five impacts: scaffold fixtures/tooling and documentation update; no product/shared UI; refresh handoff context; implement ADR-0056 without changing accepted ADRs. Dependencies unchanged. Preserve existing Access activation gate.

## Spec Change Log

## Review Triage Log

| Finding | Verdict / route | Evidence |
| --- | --- | --- |
| B1 Auth RLS prerequisite | medium / patch | Staged/head checks accept disabled Auth RLS, while runtime refuses; validate enabled RLS before activation and exercise refusal. |
| B2 Replay freshness expiry | medium / patch | Saved-result branch combines expiry with ineligibility (IC003); elapsed observation must report IC004, as the new-operation branch does. |
| B3 Observation start | medium / patch | Timestamp is assigned after both reads, excluding their elapsed time; anchor before observations and prove a delayed observation expires. |
| B4 Auth UUID creation overlap | low / reject | An overlapping explicit/random Auth allocation can collide with an observed proposed UUID, but bounded observation never reserves Auth's future UUID namespace. No authority is inherited; conflicting subsequent mapping refuses. Exact independent UUID coincidence is negligible in ordinary use; cross-owner creation coordination adds substantial scope/complexity. Retain declared bounded observation, no instant global reservation claim. |
| B5 Inherited Auth policy | medium / patch | Runtime checks direct/public policy names but not unexpected memberships; an inherited restrictive policy can disguise absence. Reject unexpected verifier membership before reads and qualify it. |
| B6 Aggregate qualification | low / patch | Current main omits named stages by default. Add a documented aggregate fresh-case invocation using existing methods; no product API or new provisioning framework. |
| B7 Private fixture dependency | medium / patch + pre-existing defer | New CLI qualifier hardcodes an old private frame; replace with explicitly supplied protected fixture input and validate exact target URL/binding. General root-prepared bootstrap portability predates this change; document that prerequisite and defer its delivery rather than add another generator. |
| B8 Alternate executor | medium / patch | New qualifier hardcodes one login; reuse existing controlled second-executor fixture pattern for scoped execution/recovery, restore ACLs and retain evidence. |
| B9 Physical Auth deletion | medium / patch | Soft deletion does not prove physical account removal preserves durable mapping/evidence. Add an isolated account-only deletion/recreation case without dropping safeguards. |
| B10 Fingerprint/actor audit closure | medium / patch | Current closure checks fingerprint length and mapping audit, omitting independent canonical digest/new actor audit comparison. Add selected known-command proof. |
| E1 Concurrent local profile change | low / reject | An overlapping profile change can commit after the last check; setup is a bounded eligibility observation followed by permanent attribution, not an access grant or commit-time profile-liveness promise. Current profile is checked after waits and again in the mapping trigger. Additional row-lock/write privileges are unjustified for this rare overlap; current access still rechecks separately. |
| V1 Deleted unmapped UUID | medium / patch | Pre-verified gap: existing soft-deletion case is independently protected by a mapping. Add deleted foreign Auth UUID with no actor/map and prove conflict plus unchanged state. |

## Verification

Frozen Python: `platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python`. Run smallest RED, focused tests, fresh synthetic actual matrix/CLI, affected Access plus PtS release suite, both composition checks (owned requires --no-seeds), and independent three-lens review. Record exact results in this spec/evidence.

Native run `99b7231c-0a5b-4bdb-98e8-3329564c526a` is up. Reuse private bootstrap from `platform/deployment/.local/identity-baseline/member-join-t1zthz6c-attempt4/`, previous sources from baseline HEAD, new proof/cases only. Preserve old single-use stages; never print credentials. Root handles independent checks, stop and commit.


### Implementation handoff —2026-10-21

Implemented protected revision18, exact staged role/Auth preparation and historical
normalization, independent rollback-only reference, account-targeted adapter/CLI receipts
and recovery, actual matrix/closure/regression fixtures and owner/runbook/handoff docs.
[Owner evidence](../../services/access/ACCOUNT_ACTOR_ENSURE_EVIDENCE.md) contains
requirement-to-stage traceability, exact commands/results, retained failed witnesses,
known-candidate synthetic CLI forward reconciliation, five impacts and release recovery.

RED: frozen Python `-m pytest services/access/tests/test_identity_operator.py -k account_actor_ensure_dispatch -q`
failed1 with command_unsupported. Final focused four-file suite passed152 in1.13s.
Actual clean/exact17/repeat and matrix stages passed as individually recorded; initial
final-source full run stopped at a witness-harness limitation, subsequently closed by
`--remaining` with an actual authority/business advisory wait-chain witness. Additional
stages passed revocation/unsafe Auth policy, response-loss recovery, injected migration
rollback/recovery and retained register/join/retire branches. Final public CLI, physical
missing-profile/evidence/immutability closure, populated repeat and read-only retained
verification passed. No aggregate initial-run success is claimed.

Final proof frame: `platform/deployment/.local/identity-baseline/account-ensure-00zi4tlq`.
New head18 reference SHA256: `98bb572d298fec7ec6825d7f2928a6830eaee31aa16fef063b61b77c7fccc595`.
All historical source/reference files and prior fixture directories stay intact.
Implementation tasks complete; enclosing root independently checks the diff, affected
suite/composers, three review lenses, preservation and normal native stop/commit.
Status remains in-progress until those enclosing Build steps finish. Existing ACCESS-A/B
membership-binding activation gate and all authorized exclusions remain.


### Review patch handoff —2026-10-21

Resolved B1/B2/B3/B5/B6/B7/B8/B9/B10/V1 with targeted changes. Staged/head checks
now require enabled Auth RLS; both Auth-reading verifiers reject unexpected memberships
before reads; the observation budget starts before both observations, and replay expiry
returns IC004. No rejected global UUID reservation/profile-lock proposal was implemented.

The qualifier now provides `--all`, preserves individual flags, accepts an explicit
protected CLI owner fixture through current private input and validates core/operator
URLs before connections. New actual proofs cover bounded disabled-RLS refusal, replay
expiry, delayed observations, inherited policy, existing alternate executor namespaces/
foreign recovery/ACL restoration, physical deletion/recreation, deleted-unmapped foreign
UUID refusal and independent digest/new-actor audit evidence. The edited parent qualifier
accepts explicit required-case sets while retaining its existing default validation.

Only18 was regenerated through its independent rollback-only recorder; final reference
SHA256 is `9502c7183ed38c6f81a3de6f578e04e6feb81059c56fdbbc44045b6f6054eb50`.
Fresh frame `account-ensure-j9ial0p1`: one `--all` invocation exited0 with26 PASS labels
and complete unchanged-source custody. Exact known-candidate routine-only forward
reconciliation retained existing CLI data/receipts/history and required final catalog;
old frames/source evidence were preserved. Focused baseline/new qualifier tests71 passed
in0.35s; edited parent qualification tests21 passed in0.42s. No wider tests were run by
the implementation agent for this review patch. Root owns final independent checks.

See the [reviewed owner evidence](../../services/access/ACCOUNT_ACTOR_ENSURE_EVIDENCE.md)
for exact aggregate command, private bootstrap prerequisite, outcomes and limitations.


### Enclosing Build completion —2026-10-21

All three independent lenses completed. Each of12 findings has an individual triage row:
9 blind findings and1 verification gap resolved,2 low proposals rejected under the
bounded-observation/no-access-grant contract. The new hardcoded private fixture dependency
was removed; pre-existing owner bootstrap portability is explicitly deferred. Root also
required operator URL validation before connections (R1, medium/patch); inherited validator
now accepts an explicit case set while preserving prior defaults. No new generator or
product surface was introduced.

Independent final commands/results:

- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python -I -B -m pytest services/access/tests apps/pts/tests/test_release.py -q -p no:cacheprovider`:1012 passed in38.63s. The earlier1-failed/995-passed run exposed a test fixture missing the new historical-normalization seam; its6 cases passed after explicitly preserving/asserting the guard→snapshot→normalization→comparison order. Runtime code was unchanged by that correction.
- Frozen Python `-B tools/py/run_compose_supabase.py --check-only` and `--identity-authority owned --no-seeds --check-only`: both PASS, no generated writes.
- `IDENTITY_QUALIFICATION_DIR=platform/deployment/.local/identity-baseline/account-ensure-j9ial0p1` with frozen Python `-B services/access/tests/qualify_account_actor_ensure.py --verify-retained`: PASS.
- Independent public CLI execute replay and exact-account outcome lookup returned the original stored final receipt; `root-cli-replay-recovery.json` records both results. No new business operation was created.
- Fresh reviewed `--all`:26 PASS stages; final143-source captures match current executable sources.35 historical migration/reference/source-pin hashes unchanged.
- `git diff --check`: PASS. Native run99b7231c-0a5b-4bdb-98e8-3329564c526a normally stopped through existing `dev.py stop`, preserving data/receipts and prior frames. An initial relative executable argument refused before execution; the required absolute pinned executable succeeded.

Scaffold/tooling, UI, context, documentation and ADR decisions are recorded in owner
evidence. Dependencies including TypeScript7.0.2 remain unchanged. All unrelated working
tree changes are excluded from the local delivery commit. No production/provider/real
account/access/provision/deploy/pilot, Leave/editor, reset/prune or push occurred. The
ACCESS-A/B membership-binding activation gate remains mandatory.
