---
title: KDG recovery request adapter
type: feature
created: 2026-10-25
status: done
route: oneshot
baseline_commit: 43406e846dafe7ec5dbea4a62a9c3c9614dfdff2
---

<frozen-after-approval>
## Intent
Implement the next candidate-only consuming recovery request adapter using generated contracts. Pin account/org/original operation/command and queued edit target, issue one bounded same-origin GET with current bearer, and runtime-validate exact committed/unresolved DTOs and status-specific safe errors. Require a caller-owned execution freshness predicate and cancellation signal to discard stale session/org/generation responses. Keep revisions as strings, original identity intact, and unresolved distinct from failure/rollback. No automatic retry, write, refresh, operation allocation, synchronized-state mutation, browser/editor wiring, API activation, native fixture/data/resource work, dependency change, fingerprints/HMAC, real accounts/Access, production, provisioning, deployment, pilot or cleanup.
</frozen-after-approval>

## Implementation Notes
- bmad-help [BD] Build selected from current handoff. Small app-owned adapter/tests/types plus docs/evidence; no intent gaps or irreversible actions, oneshot route. Authorized dirty-tree snapshot /tmp/kdg-recovery-adapter-before.json.
- Reuse generated recovery types and existing Session type; follow existing entry.ts bounded fetch/read pattern without risky extraction or Auth changes. New recovery.ts stays unimported by active startup.
- Required caller lease {signal,isCurrent} represents existing owner generation plus account/org binding; no second lifecycle. Actual Auth integration remains gated. Server still checks current own-read access on every call.
- Existing contracts explicitly require duplicate-key refusal: JSON.parse remains grammar authority; a bounded lexical key scan detects duplicates, including escaped-equivalent keys. No canonicalization/digest/HMAC is introduced.
- Scaffold: generated contract/runtime patterns consumed unchanged; policy-specific binding stays KDG-owned. Shared UI/agent context/ADR: none. Docs, tests and evidence updated together. No dependency/native resources touched.

- ATDD observed29 failures against an explicit NotImplemented stub before implementation. Focused TDD then observed network TypeError misclassification and missing rejected-body cancellation, corrected without weakening assertions.
- Final39 recovery tests pass; with29 existing entry tests,68 affected frontend cases pass. Existing entry/Auth/server/generated contract source remains unchanged. TypeScript7.0.2 passes adapter, existing web entry and generated recovery fixtures, including5 adapter negative types and12 existing contract negative types.
- Three scaffold code/test parity checks pass. No Python/backend/native tests rerun because only a new unconnected frontend adapter/types/tests changed; previous contract source capsule verified intact. No API activation, browser wiring, native resources/data/dependencies touched.
- Required lease is a future consuming seam, not an implemented Auth bridge or offline permission. Adapter never writes/retries/refreshes/allocates IDs or marks local input Synced.

## Review Triage Log
- medium / patch: immediate empty reads could starve timer and accumulate zero-byte chunks. Controlled monotonic-clock stream test first failed after consuming all30 chunks. Added deadline/cancellation/freshness checks before and after each read; empty chunks discarded; test now stops early and cancels source.
- medium / patch: missing input mutation regression. Held-response create/edit tests now mutate account/token/org/operation/command/target/options after start, proving original transport and acknowledgement remain pinned.
- medium / patch: only header-phase cancellation/freshness covered. Added held-body abort, stale generation and throwing predicate cases with acquired-source cancellation assertions.
- medium / patch: unresolved negative shapes/binding untested. Added create/edit cases refusing command_version/result/extras/wrong operation/wrong discriminator; valid unresolved still succeeds.
- medium / patch: original size test did not prove byte/cumulative boundaries. Added accepted16384-byte ASCII/multibyte JSON, rejected16385-byte cumulative streams, split UTF-8 sequences and cancellation on overflow.
All5 findings fixed; none deferred. Blind hunter ran; broader review layers omitted under oneshot.
