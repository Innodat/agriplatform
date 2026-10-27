---
title: 'Qualify standalone Scribeswell signup and confirmation'
type: 'feature'
created: '2026-10-27'
status: 'done'
route: 'dispatch'
baseline_commit: '68f11236b543b599705052ca3b3c83f64859d203'
review_loop_iteration: 0
context:
  - /home/ck/repos/innodat/agriplatform/AGENTS.md
  - /home/ck/repos/innodat/agriplatform/apps/scribeswell/docs/ACCOUNT_ENTRY.md
  - /home/ck/repos/innodat/agriplatform/apps/scribeswell/docs/STUDIES_OWNER_INTEGRATION_EVIDENCE.md
  - /home/ck/repos/innodat/agriplatform/platform/docs/development/bmad-codex-usage.md
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

Qualify required standalone account creation through the existing browser UI and real local Auth, email capture, confirmation and explicit personal Studies enrollment. User authorizes continued implementation without routine stops. Use Scribeswell's dedicated disposable fixture; preserve KDG/Leave settings and environments.

## Boundaries & Constraints

Always use the existing native lifecycle/new canonical run IDs, Auth55491/database55492/mail15494 and exact cleanup. Enable registration, required confirmation and local captured mail only for scribeswell-local. Preserve KDG and Leave generated configuration bytes. No external email or relay, production changes, competing Access/Identity implementation, Content edits or fake sessions/routes. Use only synthetic recipients and private0600 fixture files; never log credentials, mail bodies, signed links, DOM or payloads. Preserve all existing real-owner oracles. Auth account/confirmation alone grants no Studies authority; enrollment remains explicit with durable actor attribution and no organization/employment prerequisites.

## I/O & Edge-Case Matrix

| Scenario | Expected result |
| --- | --- |
| Anonymous signup | Actual UI requests account; neutral confirmation guidance; no session/grant/study |
| Unconfirmed login | Provider denies; no protected authority |
| Valid captured email | Exact matching local recipient and validated own Auth/callback URL; real confirmation/session; no implicit enrollment |
| Explicit enrollment | Current permission and durable account actor established; no study until separate create action |
| Reused confirmation | Fresh context cannot gain session/authority from consumed link; public reading remains |
| Expired confirmation | Actual elapsed local OTP expiry denies in fresh context; no grant or study |
| Missing/ambiguous/wrong mail | Bounded safe failure; no arbitrary-link navigation or false pass |

</frozen-after-approval>

## Code Map

- platform/deployment/dev.py configuration: target-specific Scribeswell global/email signup, enable_confirmations=true, local_smtp=true. Keep existing KDG/Leave bytes exact; do not edit generated run config. Short local-test otp_expiry120s supports actual expiry proof; production policy remains owner-gated.
- platform/deployment/tests/test_native_cli.py: add red profile acceptance before renderer change; update only Scribeswell expectations, retaining old target hashes and Leave tests. Mixed owner files have preserved starting copies under app .local/signup-qualification-20261027/before.
- apps/scribeswell/tests/studies_owner_fixture.py: reuse lifecycle/protected setup. Minimal no-op extra-qualification hook after existing workflow+disable observations, before source verification; default behavior unchanged. New signup subclass can re-enable fixture app explicitly after existing denial proof, then run separate signup scenario/SQL observations without breaking original exactly-two-account oracles.
- New app signup qualification helper/entrypoint, tests and Playwright scenario/config: persistent Python apps/scribeswell/.local/owner-integration-20261027/python/bin/python. Real mailbox read through bounded host-side polling/validation; do not expose provider/service credentials to browser except existing sentinels. Existing safe reporter/privacy guards reused; mailbox link/secret contents private.
- Pinned Gotrue source gotrue.service.ts confirms confirmation inversion and local Mailpit SMTP1025. Official Mailpit API: https://mailpit.axllent.org/docs/api-v1/ and https://raw.githubusercontent.com/axllent/mailpit/master/server/ui/api/v1/swagger.json; inspect actual pinned runtime shapes too. GET messages/message only; no relay/release/send API. Validate recipient, exact loopback Auth endpoint and reader redirect, ambiguity and response/time bounds.

## Tasks & Acceptance

- [x] Observe profile acceptance failure; implement Scribeswell-only reproducible confirmation/mail profile.
- [x] Add isolated real browser signup/valid/reused/expired scenarios, selected stage markers and independent SQL checkpoints. New signup identities must use actual UI signup, never admin creation/generate_link. Existing two owner-fixture users remain separate.
- [x] Prove baseline business rows unchanged outside explicit new account effects; before enrollment no new grants/studies; after enrollment exact durable attribution/current permission and no organization/person/employment prerequisites. Capture Auth confirmation safely without changing its tables.
- [x] Test mailbox/URL/missing/ambiguous/time-bound cases and privacy reporting; run affected unit/browser qualification and existing owner flow without assertion weakening. Parent executes fresh native run after review; agent focused tests only.
- [x] Record exact commands/results/source pairs/failures, local-vs-production limits, and scaffold/shared-UI/agent-context/docs/ADR impact. Preserve foreign edits and prepare scoped checkpoint; no push/deploy.

Acceptance: Given this closed local target, when genuine UI signup and mail confirmation execute, then each matrix behavior passes with real provider/SQL evidence and exact cleanup, while old KDG/Leave profiles remain unchanged. Production SMTP/delivery/default startup/device/release gates remain separate.

## Implementation Notes

No user-visible intent gaps or irreversible state: only fresh owned disposable accounts/mail/databases. Local OTP120s is qualification-only; expiry wait may take122s, with bounded worker timeout240s and parent progress updates. Reuse lifecycle rather than duplicate it. Coordinator settings inherited/actual model unknown; delegated implementation selected gpt-6.1-sol/high; bounded recon gpt-6.1-terra/medium. Usage/compute elapsed unknown; record actual test durations separately. Parent owns canonical derivation and final native execution.

## Spec Change Log

## Review Triage Log

2026-10-27: blind, edge-case and verification-gap reviewers each returned no supported findings against the scoped857-line diff. No triage rows or deferrals. The blind reviewer independently ran65helper tests. Shared mixed-owner files were reviewed as additive changes against preserved starting copies; unrelated owner changes were excluded.

## Verification

Focused pytest with PYTHONPATH=platform/deployment; Node syntax/privacy helper checks; source snapshots around executions. Native parent explicit pinned Supabase2.120.0/newUUID/private persistent proof. Tests must actually run, not merely exist. Native signup command should reuse full owner lifecycle; allow bounded expiry wait without increasing product/API budgets or changing other environments.

Implementation agent completed the renderer, original-lifecycle no-op hook, signup
subclass/CLI, strict host mailbox reader, real browser scenario and focused oracles.
All frontmatter context was loaded before implementation. Profile acceptance red:
`PYTHONPATH=platform/deployment apps/scribeswell/.local/owner-integration-20261027/python/bin/python -m pytest platform/deployment/tests/test_native_cli.py -q -k 'signup_requires_confirmation or signup_change_preserves'`
→1failed/1passed4.55s. First helper+native CLI run→96passed29.42s.
Final affected command:
`PYTHONPATH=platform/deployment apps/scribeswell/.local/owner-integration-20261027/python/bin/python -m pytest apps/scribeswell/tests/test_studies_signup.py apps/scribeswell/tests/test_studies_owner_integration.py platform/deployment/tests/test_native_cli.py -q`
→restricted sandbox179passed/1socket PermissionError45.35s; unchanged host-enabled
rerun180passed56.26s. Smallest failed test independently passed host-enabled1/79deselected2.41s.
Old/new safe reporter oracles and new browser/config Node syntax checks passed.
Safe logs and explicitly after-only10-source hashes are in ignored
`apps/scribeswell/.local/signup-qualification-20261027/implementation-focused/`.
New CLI:`apps/scribeswell/tools/py/qualify_studies_signup.py`. No native run performed
by this agent; parent owns review, fresh native proof, canonical derivation and
scoped checkpoint. No production/default-startup/device/release claim is made.
Impact decisions: existing lifecycle/closed profile only; shared UI, agent context
and accepted ADRs unchanged; account-entry/evidence docs updated. No owner or Content
implementation/migration changed. Model selected Sol High, actual model/usage/compute
elapsed unknown; no implementation retry due to test failure (one environment-only
socket rerun). Original owner assertions remain intact.

Parent native attempt1 stopped before fixture startup: runner resolved the venv executable symlink to systemPython and failed the psycopg dependency preflight. Preserved private run1386bbdc-5f0c-475a-a443-892a97a02097. Runner now retains the absolute venv path; fresh run allocated. No application/fixture-source change or claim of passing native verification.

Parent native prerequisite runs `f0c111fe…` and `11b6827a…` reached the existing
owner browser case's60000ms total limit (60048ms atline135;60071ms atline138
after all five search queries). Both received clean exact stop. The cause of
slower execution remains unknown; the earlier34045ms proof is retained. The local
native Playwright case budget is now bounded at90000ms. Assertions, scenarios,
parent command120s timeout and API/provider budgets are unchanged; this harness
adjustment changes no product behavior. Verification:
`node --check apps/scribeswell/web/playwright.owner-integration.config.cjs`
passed (exit0). Fresh native proof remains with the parent.

Native `cd54d333-3d96-490b-82b4-8c133b53b728` passed the original owner workflow
and disabled-state checks, then genuine UI signup created an unconfirmed Auth
account. Its private `signup-created.json` under
`apps/scribeswell/.local/signup-qualification-20261027/native-cd54d333-3d96-490b-82b4-8c133b53b728/`
showed exactly one new Identity profile and its one audit row; all other table
counts were unchanged. Cleanup passed and no fixture remains active. The initial
profile-only oracle incorrectly excluded the existing owner audit effect:
`platform/supabase/migrations/20250815160000_platform_create_audit_log_tbl.sql`
defines `audit_log_identity_users` and `identity.log_audit()`, which records every
profile INSERT with its full row snapshot, null column changes and the current
request actor (null for this unauthenticated signup).

Characterization preceded the correction:
`PYTHONPATH=platform/deployment apps/scribeswell/.local/owner-integration-20261027/python/bin/python -m pytest apps/scribeswell/tests/test_studies_signup.py -q -k legitimate_owner_profile_insert_audit`
failed as expected (1failed/65deselected1.55s). The oracle now permits exactly
profile1+audit1 and verifies exact table/record/INSERT/diff, null actor/column changes,
a canonical nonnil audit UUID and valid UTC timestamp. Every baseline row and all
other-table no-effect checks remain binding. Focused profile tests, including
foreign-record/wrong-operation/mismatched-diff and malformed/unrelated-effect
negatives, passed with
`PYTHONPATH=platform/deployment apps/scribeswell/.local/owner-integration-20261027/python/bin/python -m pytest apps/scribeswell/tests/test_studies_signup.py -q -k profile`
(20passed/60deselected0.77s).
Mail/URL tests, owner/service code and other qualification behavior are unchanged;
fresh full/native verification remains with the parent.


Final parent native run `ed91e6ec-1e8d-417c-a8c6-a2bd10469cbb` passed exit0 in286.15s.
All289sources remained unchanged. Browser owner56153ms, disabled8933ms and actual
signup129621ms passed. Real expiry122.000384s; no fixture Auth writes, mail credential
leak or implicit enrollment. Parent affected195tests passed31.38s/runner32.65s with
11sources unchanged. Exact command/results, safe logs, SQL count/hash checkpoints,
source pairs, prior failures and cleanup are in
`apps/scribeswell/docs/evidence/real-signup-20261027/`. All9ports released, exact
network removed, no forced termination; KDG55481/2occupied untouched. Canonical
bmad-spec derives event463 with preserved kernel/36companions/11CAP/38acceptance rows.
No review deferrals. Shared platform renderer/tests remain mixed-owner dirty with
exact additive patch; scoped app checkpoint is not a coordinated platform release.
Production mail/registration/default startup, recipients/Notification, devices and
release gates remain. The scoped local checkpoint records this delivery; no push or deployment is authorized.
