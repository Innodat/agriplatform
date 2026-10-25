# Candidate recovery with current Auth admission — 2026-10-25

`web/src/recovery-entry.ts:createRecoveryEntry` combines the existing KDG Auth entry with
`recoverOperation`. It is separately imported candidate code, unconnected to startup,
UI/editor, operation queue or saved-state feedback. No HTTP route or API dependency
activation is included. Server authorization remains current on each recovery request.

The generated lifecycle exposes a trusted-owner `acquireExecution()` only after current
admission. Its frozen lease contains the pinned session/context, AbortSignal, current
predicate and idempotent release. Bearers stay outside state/publications. The existing
epoch invalidates leases before abort callbacks on refresh, account replacement, retry,
sign-in, logout, password recovery and disposal. Admission cannot be reacquired during
reset. Reentrant disposal/retry cannot strand promises or share replacement epochs.
Consumers release in finally; a released lease has no further authority.

The KDG wrapper hides this generic lease API, pins configuration and pending input,
and checks admitted account/org before its one bounded read. Existing response validation,
original operation/edit target, 16 KiB body limit and maximum 10-second deadline remain
owned by recovery.ts. A superseded read returns only `superseded`, including late headers,
late body errors and A→B→A. Unadmitted execution sends nothing. Current receipts/unresolved/
safe errors release only their own execution, with no retry, Auth refresh, sign-in,
write, new operation, queue update or automatic Synced feedback. Changing organization
requires disposal/replacement of the existing fixed-organization entry owner. Results
are observations at completion, never cached authorization for later consequential work.

| Requirement | Evidence |
|---|---|
| Admitted pinned session/account/org | Current receipt, mismatch refusal, refreshed bearer and disposed organization tests |
| Invalidation and cancellation | Seven lifecycle transitions, late headers/body and A→B→A tests |
| Ordinary completion/deadline | Concurrent requests, ignored transport deadline and lease independence |
| Safe input/results | Malformed input/accessors; committed/unresolved; 401/403/503 with sensitive text stripped; malformed errors |
| Edit contract | Admitted original target success and wrong target refusal |
| Scaffold propagation | Canonical template tests, KDG managed parity, actual fresh renderer/installer proof |
| Reentrant callbacks | Disposal and nested-retry regressions observed failing before fix |

Final consuming capsule: **199 tests** (19 new consumer, 118 generated lifecycle,
62 prior Auth/config); strict TypeScript 7.0.2, three expected typing failures and the
existing compiler negative control. Fresh generated application: **118 tests** plus
owner-customization preservation. Affected recovery/entry/scaffold regressions: **74**.
Blind review: five findings fixed, none deferred. Acceptance stub had ten failures;
two focused reentrancy regressions failed before correction. Initial empty nested-process
logs under sandbox EPERM are excluded; proof runners now check native spawn errors.

Scaffold/runtime/test changes are same-item updates through the owning templates and
managed regeneration. No shared UI or agent-context change; no new ADR. Dependencies,
Docker resources/data and historical evidence preserved; fingerprints/HMAC deferred.
Synthetic local/CI only. Backend/native, browser/editor, actual Auth/Access, deployment,
release compatibility and API activation are unqualified. See the source-bound
[receipt](evidence/recovery-entry-20261025.json) and
[delivery record](../../../_bmad-output/implementation-artifacts/spec-kdg-recovery-entry.md).
