---
title: Protected organization grant revocation
type: feature
created: '2026-10-22'
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: aa223574ccd7289e55f13c47d29dc65c8aecfd4c
context:
  - AGENTS.md
  - platform/docs/architecture/contracts/identity-access-execution-substrate.md
  - platform/docs/architecture/contracts/e1-controlled-provisioning-and-evidence.md
---

<frozen-after-approval reason="standing bounded prerequisite implementation approval and next instruction">

## Intent

Deliver grant.revoke through existing Access owner tooling. Authorized operators remove
one exact retained organization grant binding/revision without selecting a replacement.
Preserve grant.assign and all six delivered clients; activate no effective reader.

## Boundaries & Constraints

Use controlled Access0014 after immutable13 and the existing strict parser, roles,
canonical fingerprint/outcome/event, locks, RLS, adapter and CLI. Check current original
session principal and exact grant.revoke organization/app/account authority, resolving
app from registered organization permission; assignment/platform authority confers nothing.
Recheck after waits. Null policy app/account explicitly means all; nil IDs refuse.

Match org/grant_id/account/member/permission/revision before noop. Retain opaque grant IDs,
binding and all creation fields. Active→revoked sets server time/executor, increments
revision once and commits immutable transition event/outcome atomically. Already revoked
matching state records unchanged receipt only; stale/mismatched input has no effects.
Overflow conflicts only for a changed write. No fresh Identity observation or active-member
requirement: retired/rejoined/deleted organization/profile targets can still lose retained
authority. Never replace the supplied binding. Assignment retains its current verification,
five-second observation and default-deferred safeguards unchanged.

Use shared grant coordination lock with assignment, command-specific retry namespace,
exact fingerprint and current-authority recovery. Lookup exact org/grant/account/member/
permission, no app selector; returns historical receipt, not current authority. Only retry
lock maps busy. Keep narrow owner DML and row/statement/deferred paired-evidence guards.
No extra Identity privileges/migrations, account grants, ACCESS-B/readers/consumer activation,
Leave/editor, dependency/generator/service/framework, production/real accounts, provisioning,
deploy/pilot, reset/prune/cleanup or push. Preserve concurrent work/history/resources.

## I/O & Edge-Case Matrix

| Scenario | Required behavior |
| --- | --- |
| Active exact binding/current authority | Changed revision and atomic server-attributed revoke evidence |
| Already revoked/current revision; stale or wrong selector | Unchanged/no event; conflict without effects respectively |
| Retired/rejoined/deleted target | Remove original grant only; replacement receives nothing |
| Replay/changed input/lost response | Original receipt/exact recovery; conflicting fingerprint refuses |
| Wrong command/org/app/account, disabled/revoked operator | Deny effects and recovery under current authority |
| Assign/revoke/revision races and lock waits | Serialize exact state, bounded errors, atomic rollback |
| Raw/forged/multirow/retimed evidence, malformed SQL/CLI | Refuse safely with unchanged snapshots |
| Populated13→14/repeat/six prior clients/drift/failure | Preserve history/behavior; refuse normalization, forward recovery |

</frozen-after-approval>

## Code Map

New migrations/versions/0014_grant_revoke.py extends13 guard/evidence functions with
independent revoke authority/command/outcome; old sources unchanged. Current access_baseline,
access_registration_baseline/catalog gain explicit14 and retain13 branches. Identity
identity_baseline selects14 by schema-resolved revoke routine metadata before13 and exact
full Access verification; no business/history reads or new dependency exclusions needed.

Agent owns access_operator.py/operator_cli.py and test_grant_revoke_adapter.py: typed
RevokeGrantResult, canonical account UUID, exact five-key grant target and six lookup
selectors (command/org/grant/account/member/permission), closed owner dispatch. Agent owns
DDL/catalog/baselines/native qualifier/test_grant_revoke.py/GRANT-REVOKE.md and necessary
historical unit/qualifier head pins. Reuse qualify_grant_assign/strict/configure helpers,
root source-bound fresh bootstrap and pinned previous13 adapter; no new fixture framework.

## Tasks & Acceptance

- [x] Observe native restricted Access13 unsupported RED before production edits; focused
TDD then migration/catalog/client/CLI and qualification/runbook through owner seams.
- [x] Given exact authority/binding/revision, revoke commits one transition; given stale,
unauthorized or replacement input, no grant/evidence/Identity state changes.
- [x] Root final native/retained proof, regressions/composers, three reviews, custody,
five impacts/documentation, normal stop and scoped conventional local commit.

## Implementation Notes

No unresolved intent gap. Synthetic migrations only; footprint spans owner SQL/catalog/
client/CLI/tests, so dispatch. Investigation confirms active-only Identity projection
must not be copied into removal. Existing approved dependency baseline unchanged.
Root owns evidence/spec/current handoffs/native/bootstrap/reviews/full checks/commit.
One agent owns all implementation/tests/runbook; no additional implementation agent.
Agent must wait for root native RED before production edits; missing-feature tests allowed.
/tmp/grant-revoke-preservation.json binds starting history/production/concurrent bytes.
Event access.organization_grant_revoked uses compact before/after member/revoked/revision;
revoke private assignment observation columns remain NULL. Existing owner ACLs suffice.
New canonical payload preserves Unicode/empty opaque ID; absent optional evidence_ref adds
only its fixed canonical null-field overhead to the body bound, not a new input ID limit.
Five impacts: existing owner scaffold extended; no shared UI/context/ADR change; owner
runbook/evidence plus mutable substrate/deployment/KDG handoffs. Standing approval covers
spec and dirty tree. Private bootstrap portability/logical-restore limits remain explicit.

## Spec Change Log

## Review Triage Log

All three lenses returned before triage; edge reported no findings. Each finding
is recorded separately before grouping. The verification lens supplied preverified
mutation evidence. No intent or architecture change is needed.

| ID/lens | Verdict / route | Evidence and resolution |
| --- | --- | --- |
| B1 blind — unbounded recovery selector | medium / patch | `valid_opaque_grant` checks UTF-8 but no size, and SQL lookup accepts arbitrary text. Add a conservative byte ceiling that contains every valid bounded command selector, before transport/SQL work; retain empty/Unicode/opaque IDs. |
| B2 blind — oversized canonical test confounded | medium / patch | CLI native changes canonical alone, so exact argument comparison can satisfy the refusal. Change both grant argument and canonical together to isolate the size guard. |
| B3 blind — non-null evidence size boundary absent | medium / patch | Native maximum command omits evidence; the non-null branch has a stricter65536 canonical limit. Add valid boundary and otherwise-consistent next-byte refusal. |
| B4 blind — forged receipts/events absent | medium / patch | Native guards test missing event but do not insert malformed revoke receipt/event fields through command-owner seam. Add rollback-only mutations of target, actor, disposition, event type and transitions. |
| B5 blind — authority changes after later waits absent | false / reject | Access14 acquires the transaction-scoped operator-authority advisory lock before business/row waits. Immutable Access4 guard_operator_authority acquires that same lock for principal/policy updates; removal cannot overtake those waits on the supported path. The existing retry-wait removal test covers the reachable pre-authority-lock race. No trigger bypass or new fault-injection framework is justified. |
| B6 blind — blocked recovery absent | medium / patch | Lookup has its own retry/authority lock implementation; only execution waits have behavioral coverage. Add lookup retry busy, authority timeout and authority removal during wait. |
| B7 blind — selectors at revoked maximum revision absent | low / patch | Max revoked noop is covered separately from mismatch-before-noop. Add wrong binding/revision cases to this existing fixture. |
| B8 blind — duplicate grant flags absent | low / patch | Leading-dash success is covered, duplicate normalized/separated forms are not. Add direct CLI refusal cases before dispatch. |
| B9 blind — exact commands/traceability incomplete | low / patch (root documentation) | Evidence originally contained aggregate counts/stages. Root added exact commands, frame/log locations/results and requirement-to-test mapping; finalize after corrections. |
| B10 blind — spec completion/triage pending | low / reject | These were correctly pending while review ran; the proposed fix edits this build spec and is rejected by step04. Routine step05 completion will reconcile final tasks/status. |
| V1 verification — forged unchanged receipt | medium / patch | Preverified: removing exact NEW.result comparison permits fabricated revision999 unchanged receipt; no grant write/event forces another guard. Add false revision/binding insert with complete rollback proof. Group with B4 only after this separate verdict. |
| V2 verification — persisted reason/evidence unchecked | medium / patch | Preverified: replacing p_evidence with NULL still satisfies existing event-count/replay tests. Assert exact non-null evidence and reason in committed immutable event. |

B4/V1 share missing adversarial revoke-evidence verification. All other surviving
findings have separate root causes and receive bounded patches; no deferred work.

## Verification

Prepared Python: platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python.
Focused tests then isolated native --all/separate --verify-retained, Access tests + PtS
release + migrate adapter and both composition modes. Resume only run99b7231c-0a5b-4bdb-98e8-3329564c526a
through existing lifecycle. Fresh single-use cases preserve all prior frames. Record
requirement-to-test mapping and exact commands/results; no portable CI or restore claim.


Historical qualifier continuity: pin qualify_grant_assign migrations/retained catalog to
13 when HEAD advances; the new revoke qualifier overrides that route for14. Preserve
its existing previous12 fixture dependency and add a pinned previous13 adapter from
baseline HEAD. Include all actually consumed helpers/private bootstrap sources in custody.
Canonical null evidence_ref overhead is20 bytes: permit only the bounded canonical size
representable by a valid <=65536-byte input when that optional field was omitted, while
rejecting genuinely oversized direct SQL. Exercise raw UTF-8/escaping and this boundary.


Caller audit: CLI stdout is currently capped8192 bytes. New valid revoke targets can
carry much larger opaque IDs; size only the new revoke transport for its closed bounded
receipt, including JSON escaping, and prove >8192-byte receipt handling. Preserve legacy
command behavior; body/input bounds stay65536. Lookup --grant-id accepts empty/Unicode
and literal leading-hyphen values through --grant-id=..., with strict duplicate flags.


Final verification:57 focused tests and1676 affected regression tests PASS; both
composition modes exit0; fresh final native15-stage proof and separate retained
inspection PASS. All patches above verified in the fresh final frame; no deferrals.
Owner GRANT_REVOKE_EVIDENCE.md contains exact commands, requirement-to-test mapping,
source/log/state receipts and documented limits. Five impacts are recorded above.

Normal lifecycle stop completed; final custody and scoped local commit close this delivery.
