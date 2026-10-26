---
title: 'Explicit KDG saved-edit delivery and recovery'
type: 'feature'
created: '2026-10-26'
status: 'done'
route: 'dispatch'
baseline_commit: '29c36462728b527614ab23211ff33aa2e34fe900'
review_loop_iteration: 0
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/apps/kdg-capture/AGENTS.md'
  - '{project-root}/apps/kdg-capture/docs/EDIT_RECONCILIATION_EVIDENCE.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Saved edits and transport/reconciliation primitives exist, but no explicit consumer connects them safely through uncertain delivery.

**Approach:** Add an unmounted, single-action delivery/recovery boundary using existing Auth execution leases, immutable saved commands and validated HTTP adapters. Recover the original outcome before deciding whether to send, then reconcile durable evidence with current own-detail.

## Boundaries & Constraints

**Always:** One original account/organization/action identity, one session fence and one total deadline (default and maximum 30 seconds, each HTTP phase maximum 10 seconds), including storage and publication. At most one PUT per invocation; preserve original bytes and identifiers. Current own-read gates retained work; current own-edit gates preparation and every send. Release the lease exactly once. Return safe typed results; known durable acknowledgement survives readback failure without claiming all local work Synced. Preserve concurrent changes, historical evidence, approved dependencies including TypeScript 7.0.2, and resources.

**Never:** Activate UI, startup, sender, queue, scheduling or service workers. No durable claim/leader-election framework; simultaneous explicit calls rely on existing operation idempotency. No fingerprints/HMAC, Leave/editor, real-account/access, native PostgreSQL/Docker qualification, provisioning, migrations, deployments, production, pilot or cleanup. Never read/run/copy/hash `apps/kdg-capture/migrations/tests/schema_fixture.py`; never copy the whole silo. No new dependencies, installs, remote operations or push.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| New delivery | Saved unprepared edit, current read/edit | Freeze command, recover first; unresolved permits one exact PUT; consume receipt then readback | No replacement IDs |
| Lost response | Retained prepared command, recovered committed receipt | Consume matching receipt and readback without PUT, including edit-only denial/expiry | Own-read remains required |
| Blocked preparation | Unsupported envelope, predecessor, scope mismatch or absent authority | No network mutation, preserve work | Typed blocked/expired/denied |
| Uncertain recovery | Auth, malformed, unavailable or unresolved without edit authority | Preserve exact original command and local input | No acknowledgement or blind send |
| Conflict | Valid exact 409 | Consume conflict; import authorized detail while retaining Needs attention | No invented receipt |
| Denial | Recovery/read 403, or ambiguous PUT 403 | Read denial locks partition; PUT denial probes own-detail: loaded preserves read and denies edit; denied/unverifiable conservatively locks partition | No permission renewal from data |
| Freshness | Session/account changes, abort, total deadline, slow storage/headers/body | Stop dependent work and suppress stale success | Bounded safe failure, release once |
| Local failure/concurrency | Storage failure, duplicate calls or newer Save | No false durable acknowledgement; exact duplicate operation; newer overlay survives readback | Retry retains original identity |

</frozen-after-approval>

## Code Map

- `apps/kdg-capture/web/src/history-store.ts`: reuse prepared-envelope validation, read/edit access, transaction fencing, importBaseline and receipt/conflict reconciliation. Add exact own-read-gated prepared lookup with pinned scope, and current-detail import without renewing observations.
- `web/src/auth-entry.ts` under the same silo: reuse acquireExecution; existing read-entry shows release-error handling. Do not alter generated Auth runtime.
- `web/src/recovery.ts`, `edit.ts`, `read.ts`: call transports directly under one lease, not chained entry wrappers; readCapture returns `snapshot`.
- `web/tests/edit-reconciliation-proof.mjs`, `local-edit-save-proof.mjs`, `history-store-proof.mjs`: real Chromium IndexedDB characterization patterns. `persistence-http-proof.mjs` owns an isolated synthetic Python HTTP fixture lifecycle; reuse selected-source capsules, never broad-copy source.
- `docs/contracts.md`, `docs/next-session.md`: current authority; append contracts and prepend handoff, preserving previous bytes.

## Tasks & Acceptance

**Execution:**
- [x] `apps/kdg-capture/web/tests/` -- add behavioral acceptance proof and focused matrix tests; characterize affected storage before refactoring and observe acceptance RED before implementation.
- [x] `apps/kdg-capture/web/src/history-store.ts` -- add the two narrow read-authorized seams; validate pinned identities before IndexedDB access and returned scope before HTTP.
- [x] `apps/kdg-capture/web/src/edit-delivery.ts` and `edit-delivery-entry.ts` -- implement explicit orchestration and Auth boundary with pinned primitives, combined abort/current/deadline fencing, safe results and no activation.
- [x] `apps/kdg-capture/web/tests/` and proof registrations/configs -- verify the actual consumer against real IndexedDB and existing synthetic HTTP API, plus controlled timing/error cases; compile strict selected sources.
- [x] `apps/kdg-capture/docs/` and `web/README.md` -- return contracts, test traceability, immutable source-bound evidence and next handoff (root owns final documentation/review/commit).

**Acceptance Criteria:**
- Given every matrix case, when its registered proof runs, then asserted behavior passes with exact commands and source hashes recorded.
- Given the synthetic HTTP fixture and real IndexedDB, when a saved edit is delivered and retried, then one original server operation is acknowledged and current readback reconciles without duplicate effects.
- Given existing supported history/Save/reconciliation, when affected regression proofs run, then their established behavior remains valid.

## Implementation Notes

No intent gaps or irreversible effects. Standing user authorization covers routine spec/checkpoint continuation. Workflow already activated; implement directly from this spec without starting another lifecycle. Root captured preservation baseline at `platform/deployment/.local/kdg-explicit-edit-delivery-20261026/baseline.json`.

Impact decisions: scaffold remains unchanged unless a proven domain-neutral defect is found (then update owner template and consumer tests together); shared UI unchanged because unmounted; agent context unchanged; documentation updated here; no new ADR because existing contracts/decisions suffice.

Retained tools: Node `platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node`; Python `platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python`; approved node_modules `platform/deployment/.local/web-baseline-qualification/new-5/root/node_modules`; Chromium `platform/deployment/.local/web-baseline-qualification/browsers/chromium_headless_shell-1248/chrome-headless-shell-linux64/chrome-headless-shell`. Use escalated local proofs when sandbox prevents child compilation/browser/loopback; no installs. Root regression runner reference: `platform/deployment/.local/kdg-edit-reconciliation-20261026/root-verify/run.py`.

Final verification:32 jobs pass,73 delivery/29 integrated HTTP checks plus affected regression suites; machine evidence in `apps/kdg-capture/docs/evidence/edit-delivery-20261026.json`. Actual config compiles with approved retained dependencies, preserving the existing Auth declaration-check exception. Root's initial raw-root SDK compile failure is not behavior RED. Review fixes retain exact latest-test RED against isolated pre-fix source and final GREEN; no shared source substitution. Concurrent Scribeswell commit and scaffold edits preserved. No new deferred work.

## Spec Change Log

## Review Triage Log

| Finding | Verdict / route | Evidence |
|---|---|---|
| Blind 1: PUT denial before slow probe | medium / patch | Confirmed 403 currently waits for probe before latching denial; latch edit denial immediately and cover timeout. Deadline/stale fences still forbid later storage writes. |
| Blind 2: returned command mutation | medium / patch | Injected structural store can mutate returned objects during recovery. Snapshot command and serialized bytes before awaits; no new API required. |
| Blind 3: repeat delivery after retained conflict blocks | low / rejected | Conflict is a retained terminal Needs attention result; current own-detail can already be refreshed through authorized read/history/import. Making deliver a new conflict-refresh API adds outcome surface/branches for an unmounted consumer; keep explicit conflict resolution separate. |
| Blind 4: lost committed PUT response | medium / patch | Existing retry starts after observed success. Add actual fixture response-loss then original receipt recovery with no second PUT. |
| Blind 5: fixture denial/conflict cases | medium / patch | Local fake cases cover these branches, but integrated response contracts need consumer-level qualification. Add actual fixture modes and intervening revision. |
| Blind 6: readback/Save interleavings | medium / patch | Existing test saves during PUT only. Add successor Save during readback and successor delivery ahead of older readback; preserve overlay and latest baseline. |
| Blind 7: retained prerequisites undocumented | false / rejected | Existing web README/evidence document exact approved ignored artifacts and clean-checkout limitation; this delivery appends executable proof commands. No installation or new toolchain provisioning is authorized. |
| Edges 1: denial lost on probe timeout | medium / patch | Same verified path as Blind 1 (review snippet suggests fix, actual reviewed source places denial after probe). Latch edit denial first; no postdeadline writes. |
| Verification 1: returned operation scope negative path | medium / patch | Pre-verified missing mutant-killing coverage; inject foreign command action/scope/bytes and assert invalid_request before HTTP. |


## Verification

Record precise RED/GREEN commands, executed matrix assertions, selected-source hashes and limitations beneath `platform/deployment/.local/kdg-explicit-edit-delivery-20261026/`. Use retained toolchains and existing proof patterns. Run new consumer acceptance, affected storage proofs, strict compilation and affected Auth/HTTP/parity suites. Synthetic doubles do not establish actual database permissions, rollback or release readiness.
