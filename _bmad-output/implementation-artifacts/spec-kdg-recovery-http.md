---
title: KDG candidate recovery HTTP embedding
type: feature
created: 2026-10-25
status: done
route: oneshot
baseline_commit: 711b7f8980ce59349d1506c661938f9180359b91
---

<frozen-after-approval>
## Intent
Implement and qualify the next KDG prerequisite: an explicitly constructed, unmounted candidate GET operation recovery API. Require exactly one closed command discriminator, canonical operation UUID, one bearer header and an empty bounded request body. Use current own-read authorization and the original total budget before ordinary bounded pool/driver acquisition; retain the exclusive connection through transaction and release even under cancellation. Return original committed receipts or verified unresolved, safe allowlisted errors and private/no-store responses. Preserve existing callable behavior, evidence and approved dependencies including TypeScript7.0.2. Synthetic local/CI tests only; no API activation, migrations, data changes, new resources, real Access, fingerprints/HMAC, Leave/editor, provisioning, deployment, pilot or cleanup.
</frozen-after-approval>

## Implementation Notes
- bmad-help [BD] Build selected from current handoff. Single small consuming boundary; no intent gaps or irreversible operations, so oneshot route.
- Read-only investigation confirmed reuse of RecoveryHandler._authorize, Lookup, _transaction and protected._complete_worker; API safe_errors is generated and stays unchanged.
- New candidate HTTP module and focused tests only, plus documentation/evidence. No active API or manifest imports change.
- Ordinary QueuePool/driver bounds; no extra recovery framework. Fixed finite acquisition phases can require bounded unwind after expiry/cancel; never return late success or renew observation during checkout. Candidate accepts a single numeric DB host to exclude DNS/failover waits.
- Scaffold: reuse proven generated error/transaction code; candidate-specific orchestration stays app-owned pending proven shared consumer. Shared UI/agent context/ADR: none. Documentation: contract, evidence and historical-prefix handoff in same item.
- Authorized dirty-tree preservation; preexisting hashes retained at /tmp/kdg-http-before.json.

- ATDD observed13 explicit stub failures before implementation. Focused TDD expanded to24 cases; a new lifecycle test first failed disposal0 vs1 before the lifespan fix.
- Factory-only recovery_http.py borrows ordinary lazy read-only QueuePool connections after current Access, keeping checkout/SQL/release in the existing cancellation-safe worker. Original recovery/create modules and native source capsule unchanged.
- Final affected suite141PASS, focused HTTP24PASS; all three generated code/test parity checks pass. Actual in-memory QueuePool exhaustion and overlapping leases use synthetic drivers, no native database or network.
- No retained fixture resumed, no native receipt rewritten, no data/resource/dependency/TypeScript baseline changes. Active context API remains without the recovery route; new module has no exported app.

## Review Triage Log
- medium / patch: factory owned idle pool without shutdown disposal. Standard FastAPI lifespan now disposes after host drain; normal/error lifespan acceptance passed after observing failure.
- medium / patch: omitted URL port could inherit PGPORT. Explicit connect_args port binds configured port or5432; conflicting environment test verifies default5432 and explicit55482.
- medium / patch: exclusive release test lacked overlapping successful leases. Added actual synthetic QueuePool pair, simultaneous SQL barrier, distinct checked-out connections and zero outstanding leases after completion.
- medium / patch: cancellation coverage lacked pending-worker budget expiry. Added short-budget checkout/SQL/release tests proving task retains ownership until unwind, releases, and returns only execution_timeout.
- medium / patch: broad visible-ASCII bearer syntax admitted comma and invalid punctuation. New HTTP validator uses bearer b64token grammar; commas, punctuation and interior padding refused before Access. Existing historical callables unchanged.
All five findings checked and fixed; none deferred. Oneshot blind-hunter layer ran; broader layers omitted per route.
