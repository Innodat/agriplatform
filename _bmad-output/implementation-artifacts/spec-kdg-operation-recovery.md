---
status: done
route: oneshot
baseline_commit: 093161ca975149001d86e05665dac3649105c51f
---

## Intent
<frozen-after-approval>
Implement the next authorized KDG persistence/API prerequisite: an unmounted own-read operation recovery callable. Require current verified account, durable actor and organization admission through Access read.own; look up the exact account/org/command/operation key. Disclose only an authorized stored target's original compact committed receipt. Successful absence returns unresolved; failed verification never does. Preserve total deadlines and exclusive connection ownership through cancellation. Qualify with behavioral ATDD, focused TDD and SELECT-only retained-fixture evidence. No migrations, seeds, mounting, fingerprint/HMAC, provisioning, release or cleanup.
</frozen-after-approval>

## Implementation Notes
- bmad-help selected Build for the next handoff prerequisite; bounded oneshot route with no new architecture decision.
- Dirty tree authorized; preexisting file hashes captured privately at /tmp/kdg-recovery-before.json.
- Existing create handler characterization: 23 tests passed before protected transport/worker reuse.
- Scaffold: app-owned recovery policy; reuse proven generated transaction primitives unchanged. UI: none. Agent context: none. ADR: existing decisions sufficient. Documentation and source-bound evidence updated in this item.

- ATDD: missing module first failed; explicit recovery stub then failed all 11 initial acceptance scenarios with NotImplementedError before behavior was implemented.
- Inner loop: reuse private Access evidence/worker handling through class policy attributes and optional private transaction callable; 23 existing create characterization tests protected that refactoring. Recovery performs scoped SELECTs under own_read without create checks or locks.
- Final verification: 117 affected write tests pass (16 new recovery cases), all three generated code/test parity checks pass; six SELECT-only native cases pass on retained ledger0002. Native edit receipt remains unavailable in this fixture and is not claimed.
- Initial native qualifier receipt failed safely before SQL because its preliminary Budget was instantiated after observation. Fixed ordering; failed receipt retained. No schema or persistent rows changed.
- Dependencies, TypeScript7.0.2, migration candidates, shared generators, prior evidence and concurrent work preserved. Normal stop retains the known Docker run/data.

## Review Triage Log
- medium / patch: qualifier observation preceded Budget; confirmed by safe stack and authorization_observation_expired. Budget now precedes observation; native rerun passes.
- low / patch: saturated limiter test cleanup could hang on a regression. Release admission token before awaiting cleanup, then reacquire for scope exit.
- medium / patch: missing committed-result late-completion coverage. Added test proving execution_timeout after late commit; no receipt escapes.
- medium / patch: missing transaction-exit failure after absence. Added commit failure test proving 503 operation_verification_unavailable and connection unwind; no unresolved escapes.
- low / patch: native custody helper omitted from source binding. Added native_fixture.py digest; successful native receipt includes it.
All five findings addressed; none deferred. Blind hunter used; broader review layers skipped under the oneshot route.
