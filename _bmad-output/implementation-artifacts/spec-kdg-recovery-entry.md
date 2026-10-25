---
title: KDG candidate recovery with current Auth admission
type: feature
created: 2026-10-25
status: done
route: oneshot
---

<frozen-after-approval reason="human-owned intent">

## Intent

The recovery adapter requires a current execution signal and freshness predicate. Bind it to the existing Auth/entry lifecycle so replacement, logout and disposal suppress stale results without introducing another lifecycle. Keep this a separately imported candidate consumer; no browser/editor activation or operation-state mutation.

| Scenario | Expected behavior |
|---|---|
| Current admitted account and organization | One bounded original-operation GET using the captured session |
| Checking, denied, disposed or mismatched scope | No recovery request |
| Session refresh, account replacement, retry, sign-in, logout, recovery or disposal | Invalidate and abort existing reads before replacement admission |
| Late response or account A→B→A | Suppress stale receipt and error |
| Completed read | Release its execution without revoking other work or admission |

Synthetic local/CI only. Preserve concurrent changes, historical evidence, Docker resources and TypeScript 7.0.2. Fingerprints/HMAC remain deferred. No Leave/editor, provisioning, real account/access, deployment, cleanup or API startup adoption.

</frozen-after-approval>

## Implementation Notes

bmad-help selects the next consuming integration from next-session.md. Small reversible oneshot; no intent gap or irreversible step. Use the existing lifecycle epoch, add a narrow execution lease, propagate through the owning scaffold template and its tests. No shared UI or agent-context change; no new architecture decision (existing admission/session/error/release contracts apply). Baseline HEAD 7b3fa6afca1ff566885d9ab82c510d046961cc27; unrelated dirty files preserved.

## Verification

Characterize existing lifecycle, observe candidate acceptance failure, then run focused lifecycle and consuming tests, actual fresh scaffold proof, parity, TypeScript 7.0.2 and existing recovery/entry regressions. Blind review and individual triage before scoped commit.

## Implementation Notes (completion)

Added a narrow trusted-owner ExecutionLease to the existing generated Auth lifecycle. It captures the existing epoch, exact admitted state and pinned session; reset invalidates before abort callbacks. Completion releases only its own lease. No second lifecycle, storage, permission cache or domain runtime was introduced. The KDG candidate wrapper hides the lease API, snapshots configuration and pending input, checks account/org, invokes the unchanged recovery adapter and suppresses stale completion. Owning lifecycle/test templates were regenerated into KDG with the managed installer. Shared UI and agent-context impact: none; no ADR required. Documentation/contracts and scaffold maintenance record updated in the same item.

Concrete sandbox EPERM exposed native spawn errors with misleading exit status: proof runners now assert native spawn errors as well as status. No dependency change. Current tests execute without Node process isolation for individual diagnostics; elevated synthetic runner execution is needed for nested processes in this sandbox. Initial sandbox-only empty child logs are not counted as evidence.

## Review Triage Log

- medium, patch — Abort listener disposal could leave retry pending, and nested retry could share outer epoch. Both failures reproduced in template tests. reset now returns its own execution, cleans old timer/finish before callbacks, and callers recheck that execution. 118 generated lifecycle tests pass.
- medium, patch — New error fixture omitted required error text. Corrected to contract-valid sensitive text and separately retained malformed-body refusal. Existing parser expectation was unchanged.
- medium, patch — Null/throwing pending values bypassed safe validator. Snapshot input inside a protected block; malformed runtime cases return invalid_request without transport.
- medium, patch — Missing edit consuming coverage. Added original edited target success and mismatched target refusal.
- medium, patch — Missing current 401/503 consuming evidence. Added valid 401/403/503 cases proving safe identifier, own lease release, no SDK refresh/interactive side effects or admission publication. All five findings fixed; none deferred.

## Verification results

Pinned Node 26.11.1; TypeScript 7.0.2, Supabase SDK 2.117.3, React 19.3.0 unchanged. Acceptance stub replay: 10 failures/1 pass, including admitted recovery returning superseded instead of committed. Reentrant focused TDD: 2 failures before fix, 118 template tests after fix. Final auth-proof --unit-only: 199 tests (19 recovery-entry, 118 generated lifecycle, 62 prior Auth/config), strict own-source compile and three new expected typing failures plus existing negative control. Fresh actual renderer/installer scaffold: 118 generated tests plus owner-customization preservation. Affected recovery/entry/auth-pattern regression: 74 tests. Managed Auth parity passes. See RECOVERY_ENTRY_EVIDENCE.md and durable receipt for exact commands, source hashes and retained local proof paths. No backend/native/browser execution or release claim in this slice.
